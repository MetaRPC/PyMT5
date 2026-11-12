import asyncio
import contextlib
import io
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "examples"))
from account_dashboard import dashboard
from stream_quotes import stream_quotes

ENV = {"MRPC_API_KEY": "secret-key", "MT5_PASSWORD": "secret-password",
       "MT5_LOGIN": "123", "MT5_SERVER": "Demo"}


class BoundedExamplesTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.calls = []
        calls = self.calls
        class Account:
            def __init__(self, **kwargs): pass
            async def connect_by_server_name(self, *args, **kwargs): calls.append("connect")
            async def disconnect(self): calls.append("disconnect")
            async def account_summary(self):
                calls.append("read")
                return SimpleNamespace(account_balance=10, account_equity=11, account_margin_free=9)
            async def on_symbol_tick(self, symbols, cancellation_event):
                try:
                    while True:
                        calls.append("tick")
                        yield SimpleNamespace(symbol_tick=SimpleNamespace(symbol=symbols[0], bid=1, ask=2))
                finally: calls.append("stream-closed")
        self.Account = Account
        self.env = patch.dict(os.environ, ENV, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    async def test_dashboard_reads_only_requested_samples(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            await dashboard(1, 1, self.Account)
        self.assertEqual(self.calls, ["connect", "read", "disconnect"])
        self.assertIn("account currency", output.getvalue())
        self.assertNotIn("secret", output.getvalue())

    async def test_stream_stops_at_event_limit_and_closes_before_disconnect(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(await stream_quotes(events=2, account_factory=self.Account), 2)
        self.assertEqual(self.calls, ["connect", "tick", "tick", "stream-closed", "disconnect"])

    async def test_quiet_stream_is_cancelled_by_deadline(self):
        calls = self.calls
        class Quiet(self.Account):
            async def on_symbol_tick(self, **kwargs):
                try:
                    await asyncio.Event().wait()
                    yield None
                finally: calls.append("stream-closed")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(await asyncio.wait_for(stream_quotes(seconds=.02, account_factory=Quiet), 1), 0)
        self.assertEqual(self.calls, ["connect", "stream-closed", "disconnect"])

    async def test_read_failure_still_disconnects(self):
        class Broken(self.Account):
            async def account_summary(self): raise RuntimeError("private server detail")
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(RuntimeError): await dashboard(account_factory=Broken)
        self.assertEqual(self.calls, ["connect", "disconnect"])

    async def test_invalid_limits_never_connect(self):
        for request in (dashboard(samples=0, account_factory=self.Account),
                        stream_quotes(seconds=0, account_factory=self.Account),
                        stream_quotes(events=1001, account_factory=self.Account)):
            with self.assertRaises(ValueError): await request
        self.assertEqual(self.calls, [])
