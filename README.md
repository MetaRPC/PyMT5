# PyMT5 SDK — Cloud Python SDK for MetaTrader 5 (MT5)

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://img.shields.io/badge/docs-PyMT5-0083ff.svg)](https://metarpc.github.io/PyMT5/)
[![Cloud](https://img.shields.io/badge/VPS-Not_Required-success.svg)](https://mrpc.pro)
[![Platform](https://img.shields.io/badge/OS-Linux%20|%20macOS%20|%20Windows%20|%20Docker-brightgreen.svg)](https://mrpc.pro)

> **Official Python SDK for MetaTrader 5 Cloud API via gRPC & REST.**  
> Connect, stream live ticks, and execute trades on any MT5 broker or prop firm from Linux, macOS, Docker, or AWS Lambda — **without running a Windows VPS or desktop terminal.**

---

## ⚡ Why MetaRPC PyMT5?

- **Zero Windows VPS**: Stop paying $20–$80/month for buggy Windows servers. Run trading bots in lightweight Linux containers or serverless workers.
- **Ultra-Low Latency**: High-speed gRPC streaming and execution co-located with London (LD4) and New York (NY4) broker data centers (<20ms execution).
- **Universal Broker & Prop Firm Support**: Connects to 500+ brokers and prop firms including **FTMO, IC Markets, Pepperstone, Exness, FundedNext, Tickmill, XM, FXCM**.
- **Automatic Session Management**: Session GUID (`id`) is generated automatically by the server upon connection and attached to all subsequent requests.
- **Asyncio Native**: Modern asynchronous Python design with automatic reconnection, heartbeat monitoring, and resilience.

---

## 📦 Installation

```bash
pip install MetaRpcMT5
```

---

## 🚀 30-Second Quick Start

```python
import asyncio
from pymt5 import MT5Account

async def main():
    # 1. Initialize account with your credentials
    # Sign up at https://mrpc.pro/signup to get your free API key
    account = MT5Account(
        user=12345678,                      # Your MT5 Login
        password="your_mt5_password",        # Your MT5 Password
        grpc_server="mt5.mrpc.pro:443",      # Cloud gRPC Endpoint
        api_key="your_mrpc_api_key"          # From https://mrpc.pro/my
    )

    # 2. Connect by broker server name
    print("Connecting to MetaTrader 5 Cloud...")
    await account.connect_by_server_name("MetaQuotes-Demo", base_chart_symbol="EURUSD", timeout_seconds=30)
    print("Connected successfully!")

    # 3. Get real-time account summary
    summary = await account.account_summary()
    print(f"Balance: ${summary.account_balance:,.2f}")
    print(f"Equity:  ${summary.account_equity:,.2f}")
    print(f"Free Margin: ${summary.account_margin_free:,.2f}")

    # 4. Fetch live quotes
    quote = await account.get_quote("EURUSD")
    print(f"EURUSD Bid: {quote.bid} | Ask: {quote.ask}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔑 Getting Your API Key & Free Trial

1. **Sign Up**: Create your free account at [https://mrpc.pro/signup](https://mrpc.pro/signup).
2. **Copy API Key**: Open your portal dashboard at [https://mrpc.pro/my](https://mrpc.pro/my) and grab your personal API token.
3. **Connect**: Pass your key in code or set the `MRPC_API_KEY` environment variable:
   ```bash
   export MRPC_API_KEY="your_api_token_here"
   ```

---

## 🌐 Production Endpoints

| Environment | Host / URL | Port | Protocol | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **MT5 Production gRPC** | `mt5.mrpc.pro` | `443` | TLS / gRPC | High-throughput trading & streaming |
| **Interactive API UI (Swagger)** | [https://mt5.mrpc.pro/apiui](https://mt5.mrpc.pro/apiui) | `443` | HTTPS / REST | Interactive REST endpoints & testing |
| **Portal Dashboard** | [https://mrpc.pro/my](https://mrpc.pro/my) | `443` | HTTPS | Manage terminals, copiers & keys |
| **Account Registration** | [https://mrpc.pro/signup](https://mrpc.pro/signup) | `443` | HTTPS | Instant free trial registration |

---

## 🏢 Compatible Brokers & Prop Firms

Tested and verified with over 500+ MetaTrader server environments:
- **Prop Firms**: FTMO, FundedNext, The Funded Trader, E8 Funding, Alpha Capital, SurgeTrader.
- **Brokers**: IC Markets, Pepperstone, Exness, Tickmill, XM, FXCM, FP Markets, Eightcap, AvaTrade.

---

## 📚 Complete Documentation & Code Examples

- 📖 [Comprehensive Documentation](https://metarpc.github.io/PyMT5/)
- 🚀 [10-Minute First Project Guide](https://metarpc.github.io/PyMT5/All_Guides/Your_First_Project/)
- 📡 [Live Tick & Bar gRPC Streaming](https://metarpc.github.io/PyMT5/All_Guides/GRPC_STREAM_MANAGEMENT/)
- 💼 [Order Execution & Position Management](https://metarpc.github.io/PyMT5/API_Reference/MT5Account/)
- 💡 [Example Scripts & Strategies](https://github.com/MetaRPC/PyMT5/tree/main/examples)

---

## 📄 License

This SDK is open-sourced under the [MIT License](LICENSE).  
Cloud infrastructure and API services are operated by [MetaRPC](https://mrpc.pro).
