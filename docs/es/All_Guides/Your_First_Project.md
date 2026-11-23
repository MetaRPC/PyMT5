# Your First Project in 10 Minutes (Python)

> **Hands-on Quick Start** - Create a working trading project with MetaTrader 5 and PyMT5 from scratch.

---

## Step 0: Obtain Your API Key

To connect to MetaRPC endpoints (`mt5.mrpc.pro:443`), obtain your API key:

1. Register for free at [https://mrpc.pro/signup](https://mrpc.pro/signup).
2. Generate your API token in your dashboard at [https://mrpc.pro/my](https://mrpc.pro/my).
3. Keep the token handy — supply it via the `MRPC_API_KEY` environment variable (defaults to `TRIAL` for trying things out).

---

## Step 1: Create Your Project

Create a new directory for your trading bot and install the package:

```bash
mkdir my_pymt5_bot
cd my_pymt5_bot
pip install MetaRpcMT5
```

---

## Step 2: Write Your Trading Code

Create `main.py` and paste the following. Every call is asynchronous, so the whole thing runs inside `asyncio.run(...)`:

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def main():
    # Build the client (session id is generated and attached automatically).
    # The constructor takes: user, password, grpc_server, id_
    account = MT5Account(
        user=591129415,                  # your MT5 login
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",  # the MetaRPC gateway address
    )

    # Connect by broker server name (recommended)
    await account.connect_by_server_name(
        "MetaQuotes-Demo",               # your broker/cluster server name
        base_chart_symbol="EURUSD",
        timeout_seconds=30,
    )

    # Read the account summary
    summary = await account.account_summary()
    print(f"Balance: {summary.account_balance}, Equity: {summary.account_equity}")

    await account.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

> Fill in your own `user`, `password` and server name from your MT5 demo account (see [MT5 for Beginners](MT5_For_Beginners.md) to create one).

---

## Step 3: Run the Program

```bash
python main.py
```

You should see your account balance and equity, e.g.:

```
Balance: 10000.0, Equity: 10000.0
```

---

## 🚀 Next Steps

Congratulations! You have successfully established a direct gRPC connection to MetaTrader 5. Next:

- Explore **[gRPC Streaming](GRPC_STREAM_MANAGEMENT.md)** to listen to live ticks.
- Check the **[API Reference](../MT5Account/MT5Account.Master.Overview.md)** for all 43 available terminal methods.
- Learn about high-level risk management and auto-normalization in **[MT5Sugar](../MT5Sugar/MT5Sugar.Master.Overview.md)**.
