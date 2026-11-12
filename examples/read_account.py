"""Read a disposable MT5 demo account without placing trades.

Run: python examples/read_account.py
Set MRPC_API_KEY, MT5_LOGIN, MT5_PASSWORD and MT5_SERVER in the environment.
Connection usage is billed; check the portal after cleanup, especially on errors.
"""
import asyncio
import os


def create_account(account_factory=None):
    required = ("MRPC_API_KEY", "MT5_LOGIN", "MT5_PASSWORD", "MT5_SERVER")
    missing = [key for key in required if not os.environ.get(key, "").strip()]
    if missing:
        raise ValueError("Set these environment variables: " + ", ".join(missing))
    login = int(os.environ["MT5_LOGIN"])
    if login <= 0:
        raise ValueError("MT5_LOGIN must be a positive account number")
    if account_factory is None:
        from MetaRpcMT5 import MT5Account
        account_factory = MT5Account
    return account_factory(user=login, password=os.environ["MT5_PASSWORD"],
                           grpc_server="mt5.mrpc.pro:443", api_key=os.environ["MRPC_API_KEY"])


async def read_account(account_factory=None):
    account = create_account(account_factory)
    try:
        await account.connect_by_server_name(os.environ["MT5_SERVER"], timeout_seconds=30)
        summary = await account.account_summary()
        print(f"Balance: {summary.account_balance}; equity: {summary.account_equity}; "
              f"free margin: {summary.account_margin_free} (account currency)")
    finally:
        await account.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(read_account())
    except Exception as exc:
        # API errors may contain connection details. Do not print credentials in a shared log.
        print(f"Read failed ({type(exc).__name__}). Inspect locally; redact details before sharing.")
        raise SystemExit(1) from None
