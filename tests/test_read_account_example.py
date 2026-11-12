import contextlib
import importlib.util
import io
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("read_account_example", Path(__file__).parents[1] / "examples/read_account.py")
example = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)


class ReadAccountExampleTests(unittest.IsolatedAsyncioTestCase):
    async def test_read_only_lifecycle_and_no_key_in_output(self):
        calls = []
        class Account:
            def __init__(self, **kwargs):
                assert kwargs["api_key"] == "test-secret"
            async def connect_by_server_name(self, server, **kwargs): calls.append("connect")
            async def account_summary(self):
                calls.append("read")
                return SimpleNamespace(account_balance=10, account_equity=10, account_margin_free=10)
            async def disconnect(self): calls.append("disconnect")
        with patch.dict(os.environ, {"MRPC_API_KEY":"test-secret", "MT5_LOGIN":"123", "MT5_PASSWORD":"test-password", "MT5_SERVER":"Demo"}, clear=True):
            output=io.StringIO()
            with contextlib.redirect_stdout(output): await example.read_account(Account)
        self.assertEqual(calls,["connect","read","disconnect"])
        self.assertNotIn("test-secret",output.getvalue())
        self.assertNotIn("test-password",output.getvalue())

    async def test_disconnect_attempted_after_failed_connect_or_read(self):
        for stage in ("connect", "read"):
            calls=[]
            class Account:
                def __init__(self, **kwargs): pass
                async def connect_by_server_name(self,*args,**kwargs):
                    if stage=="connect": raise RuntimeError("failed")
                async def account_summary(self): raise RuntimeError("failed")
                async def disconnect(self): calls.append("disconnect")
            with patch.dict(os.environ, {"MRPC_API_KEY":"test-secret", "MT5_LOGIN":"123", "MT5_PASSWORD":"test-password", "MT5_SERVER":"Demo"}, clear=True):
                with self.assertRaises(RuntimeError): await example.read_account(Account)
            self.assertEqual(calls,["disconnect"])

    async def test_missing_credentials_do_not_create_connection(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError): await example.read_account(lambda **k: self.fail("Unexpected connection"))
