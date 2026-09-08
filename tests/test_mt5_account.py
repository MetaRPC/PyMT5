import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'package'))

from MetaRpcMT5.mt5_account import MT5Account, ConnectExceptionMT5, ApiExceptionMT5
from MetaRpcMT5 import mt5_term_api_connection_pb2 as conn_pb
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as helper_pb


class TestMT5Account(unittest.TestCase):
    def test_account_initialization(self):
        account = MT5Account(user=12345678, password="test_password", grpc_server="custom.server:443")
        self.assertEqual(account.user, 12345678)
        self.assertEqual(account.password, "test_password")
        self.assertEqual(account.grpc_server, "custom.server:443")

    def test_default_grpc_server(self):
        account = MT5Account(user=12345678, password="test_password")
        self.assertEqual(account.grpc_server, "mt5.mrpc.pro:443")

    def test_connect_request_proto(self):
        req = conn_pb.ConnectRequest(
            user=12345678,
            password="test_password",
            host="127.0.0.1",
            port=443
        )
        self.assertEqual(req.user, 12345678)
        self.assertEqual(req.password, "test_password")
        self.assertEqual(req.host, "127.0.0.1")
        self.assertEqual(req.port, 443)

    def test_account_summary_data_proto(self):
        data = helper_pb.AccountSummaryData(
            account_login=12345678,
            account_balance=10000.50,
            account_equity=10250.75,
            account_currency="USD",
            account_leverage=100
        )
        self.assertEqual(data.account_login, 12345678)
        self.assertAlmostEqual(data.account_balance, 10000.50)
        self.assertAlmostEqual(data.account_equity, 10250.75)
        self.assertEqual(data.account_currency, "USD")
        self.assertEqual(data.account_leverage, 100)

    def test_exceptions(self):
        exc = ConnectExceptionMT5("connection failed")
        self.assertIn("connection failed", str(exc))

        api_exc = ApiExceptionMT5("invalid order volume")
        self.assertIn("invalid order volume", str(api_exc))


if __name__ == "__main__":
    unittest.main()
