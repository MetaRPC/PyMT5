"""Quick start: connect by server name and fetch a simple string property."""
import asyncio
import uuid

from MetaRpcMT5 import ConnectExceptionMT5, ApiExceptionMT5
from MetaRpcMT5Ex import MT5AccountEx as MT5Account 

# Put your real credentials and server here
USER = 12345678
PASSWORD = "replace_me"
GRPC_SERVER = "mt5.mrpc.pro:443"   # your endpoint if different
SERVER_NAME = "MetaQuotes-Demo"    # example; replace with your cluster/server name

async def main() -> None:
    print("▶ start")
    acc = MT5Account(
        user=USER,
        password=PASSWORD,
        grpc_server=GRPC_SERVER,
        id_=str(uuid.uuid4()),
    )
    try:
        print("→ connecting by server name…")
        await acc.connect_by_server_name(
            server_name=SERVER_NAME,
            base_chart_symbol="EURUSD",
            wait_for_terminal_is_alive=True,
            timeout_seconds=30,
        )
        print("✅ Connected by server name")

        
        value = await acc.account_info_string(property_id=0)
        print("Account string property:", value)

    except ConnectExceptionMT5 as e:
        print("❌ ConnectExceptionMT5:", e)
    except ApiExceptionMT5 as e:
        print("❌ ApiExceptionMT5:", e)
    finally:
        try:
            await acc.disconnect()
            print("↩ disconnected")
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())
