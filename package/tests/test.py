import asyncio
from MetaRpcMT5.mt5_account import MT5Account


async def test_account_summary():
    user = 5036292718
    password = "_0AeXaFk"
    host = "78.140.180.198"
    port = 443
    server_name = "MetaQuotes-Demo"

    account = MT5Account(user=user, password=password)
    #await account.connect_by_host_port(host=host, port=port, base_chart_symbol="EURUSD")
    await account.connect_by_server_name(server_name=server_name, base_chart_symbol="EURUSD")

    summary = await account.account_summary()
    print("✅ Account summary:")
    print(summary)

    async for tick in account.on_symbol_tick(["EURUSD", "GBPUSD"]):
        print(tick)


if __name__ == "__main__":
    asyncio.run(test_account_summary())
