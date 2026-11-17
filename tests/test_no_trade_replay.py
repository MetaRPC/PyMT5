"""
Trade calls must never be re-sent automatically after a transport failure whose outcome
is unknown. Uses a real in-process grpc.aio server on 127.0.0.1 with fake servicers.
"""
import os
import sys
import unittest

import grpc
import grpc.aio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'package'))

from MetaRpcMT5 import MT5Account, TradeOutcomeUnknownError, ApiExceptionMT5
from MetaRpcMT5.helpers import errors
from MetaRpcMT5 import mrpc_mt5_error_pb2 as error_pb2
from MetaRpcMT5 import mt5_term_api_connection_pb2 as conn_pb2
from MetaRpcMT5 import mt5_term_api_connection_pb2_grpc as conn_grpc
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as acc_pb2
from MetaRpcMT5 import mt5_term_api_account_helper_pb2_grpc as acc_grpc
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as trade_pb2
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2_grpc as trade_grpc


class Script:
    """Per-method list of planned failures, consumed one per call; afterwards: success."""

    def __init__(self):
        self.calls = {}
        self.plan = {}

    def take(self, method):
        self.calls[method] = self.calls.get(method, 0) + 1
        steps = self.plan.get(method) or []
        return steps.pop(0) if steps else None


async def _answer(script, method, context, reply_cls, data):
    step = script.take(method)
    if step is None:
        return reply_cls(data=data)
    kind, value = step
    if kind == "status":
        code, details = value
        await context.abort(code, details)
    return reply_cls(error=error_pb2.Error(error_code=value, error_message=f"{value} (fake)"))


class FakeConnection(conn_grpc.ConnectionServicer):
    def __init__(self, script):
        self.script = script

    async def ConnectEx(self, request, context):
        return await _answer(self.script, "ConnectEx", context, conn_pb2.ConnectExReply,
                             conn_pb2.ConnectData(terminal_instance_guid="11111111-2222-3333-4444-555555555555"))


class FakeAccount(acc_grpc.AccountHelperServicer):
    def __init__(self, script):
        self.script = script

    async def AccountSummary(self, request, context):
        return await _answer(self.script, "AccountSummary", context, acc_pb2.AccountSummaryReply,
                             acc_pb2.AccountSummaryData(account_login=42))


class FakeTrading(trade_grpc.TradingHelperServicer):
    def __init__(self, script):
        self.script = script

    async def OrderSend(self, request, context):
        return await _answer(self.script, "OrderSend", context, trade_pb2.OrderSendReply,
                             trade_pb2.OrderSendData(returned_code=10009, order=7))

    async def OrderModify(self, request, context):
        return await _answer(self.script, "OrderModify", context, trade_pb2.OrderModifyReply,
                             trade_pb2.OrderModifyData(returned_code=10009))

    async def OrderClose(self, request, context):
        return await _answer(self.script, "OrderClose", context, trade_pb2.OrderCloseReply,
                             trade_pb2.OrderCloseData(returned_code=10009))


class NoTradeReplayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.script = Script()
        self.server = grpc.aio.server()
        conn_grpc.add_ConnectionServicer_to_server(FakeConnection(self.script), self.server)
        acc_grpc.add_AccountHelperServicer_to_server(FakeAccount(self.script), self.server)
        trade_grpc.add_TradingHelperServicer_to_server(FakeTrading(self.script), self.server)
        port = self.server.add_insecure_port("127.0.0.1:0")
        await self.server.start()

        self.account = MT5Account(user=1, password="x", api_key="test-key",
                                  id_="11111111-2222-3333-4444-555555555555")
        await self.account.channel.close()
        channel = grpc.aio.insecure_channel(f"127.0.0.1:{port}")
        self.account.channel = channel
        self.account.connection_client = conn_grpc.ConnectionStub(channel)
        self.account.account_client = acc_grpc.AccountHelperStub(channel)
        self.account.trade_client = trade_grpc.TradingHelperStub(channel)
        self.account.server_name = "Fake-Demo"  # as after connect_by_server_name

    async def asyncTearDown(self):
        await self.account.channel.close()
        await self.server.stop(None)

    def calls(self, method):
        return self.script.calls.get(method, 0)

    async def test_trade_transport_failure_is_not_resent(self):
        cases = [
            ("OrderSend", lambda: self.account.order_send(trade_pb2.OrderSendRequest(symbol="EURUSD", volume=0.01))),
            ("OrderModify", lambda: self.account.order_modify(trade_pb2.OrderModifyRequest(ticket=7))),
            ("OrderClose", lambda: self.account.order_close(trade_pb2.OrderCloseRequest(ticket=7, volume=0.01))),
        ]
        codes = [grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED,
                 grpc.StatusCode.UNKNOWN, grpc.StatusCode.INTERNAL]
        for method, call in cases:
            for code in codes:
                with self.subTest(method=method, code=code.name):
                    before = self.calls(method)
                    self.script.plan[method] = [("status", (code, "transport broke"))]
                    with self.assertRaises(TradeOutcomeUnknownError) as cm:
                        await call()
                    ex = cm.exception
                    self.assertEqual(self.calls(method) - before, 1)
                    self.assertEqual(self.calls("ConnectEx"), 0)
                    self.assertEqual(ex.error_code, "TRADE_OUTCOME_UNKNOWN")
                    self.assertEqual(ex.error_code(), "TRADE_OUTCOME_UNKNOWN")
                    self.assertEqual(ex.error.error_code, "TRADE_OUTCOME_UNKNOWN")
                    self.assertEqual(ex.operation, method)
                    self.assertEqual(ex.code(), code)
                    self.assertEqual(ex.details(), "transport broke")
                    self.assertIsInstance(ex.transport_error, grpc.aio.AioRpcError)
                    self.assertIs(ex.__cause__, ex.transport_error)
                    self.assertIsInstance(ex, grpc.RpcError)
                    self.assertIsInstance(ex, grpc.aio.AioRpcError)
                    self.assertIsInstance(ex, ApiExceptionMT5)
                    self.assertTrue(str(ex).startswith(f"TRADE_OUTCOME_UNKNOWN: {method} failed with gRPC {code.name}"))
                    self.assertIn("NOT re-sent", str(ex))

    async def test_trade_terminal_instance_not_found_reconnects_and_resends(self):
        self.script.plan["OrderSend"] = [("inband", "TERMINAL_INSTANCE_NOT_FOUND")]
        data = await self.account.order_send(trade_pb2.OrderSendRequest(symbol="EURUSD", volume=0.01))
        self.assertEqual(data.returned_code, 10009)
        self.assertEqual(self.calls("OrderSend"), 2)
        self.assertEqual(self.calls("ConnectEx"), 1)

    async def test_read_unavailable_is_retried(self):
        self.script.plan["AccountSummary"] = [("status", (grpc.StatusCode.UNAVAILABLE, "transport broke"))]
        data = await self.account.account_summary()
        self.assertEqual(data.account_login, 42)
        self.assertEqual(self.calls("AccountSummary"), 2)
        self.assertEqual(self.calls("ConnectEx"), 1)

    async def test_api_key_invalid_in_band_fails_fast(self):
        for method, call in [
            ("AccountSummary", lambda: self.account.account_summary()),
            ("OrderSend", lambda: self.account.order_send(trade_pb2.OrderSendRequest(symbol="EURUSD", volume=0.01))),
        ]:
            with self.subTest(method=method):
                self.script.plan[method] = [("inband", "API_KEY_INVALID")]
                with self.assertRaises(ApiExceptionMT5) as cm:
                    await call()
                self.assertEqual(cm.exception.error_code(), "API_KEY_INVALID")
                self.assertEqual(self.calls(method), 1)
                self.assertEqual(self.calls("ConnectEx"), 0)

    async def test_api_key_refusal_in_status_does_not_reconnect(self):
        for code_text in ("API_KEY_INVALID", "API_KEY_REQUIRED"):
            for method, call in [
                ("AccountSummary", lambda: self.account.account_summary()),
                ("OrderSend", lambda: self.account.order_send(trade_pb2.OrderSendRequest(symbol="EURUSD", volume=0.01))),
            ]:
                with self.subTest(code=code_text, method=method):
                    before = self.calls(method)
                    self.script.plan[method] = [("status", (grpc.StatusCode.UNAVAILABLE, f"{code_text}: refused"))]
                    with self.assertRaises(grpc.aio.AioRpcError) as cm:
                        await call()
                    self.assertNotIsInstance(cm.exception, TradeOutcomeUnknownError)
                    self.assertIn(code_text, cm.exception.details())
                    self.assertEqual(self.calls(method) - before, 1)
                    self.assertEqual(self.calls("ConnectEx"), 0)

    async def test_connect_does_not_loop_on_api_key_refusal(self):
        self.script.plan["ConnectEx"] = [("status", (grpc.StatusCode.UNAVAILABLE, "API_KEY_INVALID"))] * 5
        with self.assertRaises(grpc.aio.AioRpcError) as cm:
            await self.account.connect_by_server_name("Fake-Demo", timeout_seconds=30)
        self.assertIn("API_KEY_INVALID", cm.exception.details())
        self.assertEqual(self.calls("ConnectEx"), 1)

    async def test_execute_with_reconnect_positional_signature_unchanged(self):
        async def grpc_call(headers):
            return await self.account.account_client.AccountSummary(acc_pb2.AccountSummaryRequest(), metadata=headers)
        res = await self.account.execute_with_reconnect(grpc_call, lambda r: getattr(r, "error", None), None, None)
        self.assertEqual(res.data.account_login, 42)


class RetryableRetcodeTests(unittest.TestCase):
    def test_unknown_outcome_retcodes_are_not_retryable(self):
        for code in (10012, 10028, 10031):
            self.assertFalse(errors.is_retcode_retryable(code), code)
        self.assertTrue(errors.is_retcode_retryable(errors.TRADE_RETCODE_TOO_MANY_REQUESTS))
        self.assertTrue(errors.is_retcode_requote(errors.TRADE_RETCODE_REQUOTE))


if __name__ == "__main__":
    unittest.main()
