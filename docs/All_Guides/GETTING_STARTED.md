# Getting Started with PyMT5

> **Quick Setup & Overview** - Start automating your trading with PyMT5 (Python for MetaTrader 5) in minutes.

---

## 🎯 What is PyMT5?

**PyMT5** is an industrial-grade, type-safe Python client library for interacting with **MetaTrader 5** terminals via high-performance **gRPC**. It eliminates complex C++ DLL wrappers and provides direct, reliable programmatic trading.

### 🌟 Key Advantages
- 🚀 **High Throughput**: Native gRPC streaming for sub-millisecond price ticks and trade execution.
- 🛡️ **Three-Layer Architecture**: Low-level gRPC (`MT5Account`), typed wrapper methods (`MT5Service`), and high-level convenience (`MT5Sugar`).
- 🔄 **Resilient Connection**: Auto-reconnect, exponential backoff, and transparent channel healing.
- 💼 **Production Ready**: Fully verified across institutional accounts, hedge fund systems, and automated retail bots.

---

## 📦 Installation

Install PyMT5 via your standard Python package manager:

```bash
pip install metarpc-mt5
```

---

## 🔑 API Key & Authentication

Connecting to MetaRPC production endpoints (`mt5.mrpc.pro:443`) requires an API key:

1. **Sign Up**: Create an account for free at [https://mrpc.pro/signup](https://mrpc.pro/signup).
2. **Generate API Key**: In your MetaRPC Portal dashboard at [https://mrpc.pro/my](https://mrpc.pro/my), go to **API Keys** to generate and copy your personal API token.
3. **Configure Connection**: Pass your API key / token along with the server address (`mt5.mrpc.pro:443`) in your connection settings.

---

## 🔌 Minimal Connection Example

Here is how easy it is to initialize `MT5Account`, connect to your MetaTrader terminal, and retrieve your account balance:

```
account = MT5Account(user=user, password=password, host=grpc_server)
await account.connect_by_server_name(server_name, "EURUSD", timeout=30)
summary = await account.account_summary()
print(f"Balance: {summary.account_balance}, Equity: {summary.account_equity}")
```

---

## 🗺️ Documentation Road Map

To get the most out of PyMT5, follow this suggested reading order:

1. 🚀 **[Your First Project](Your_First_Project.md)** - Build and run a working project in 10 minutes.
2. 🗺️ **[Project Map](PROJECT_MAP.md)** - Understand the 3 architectural layers and interaction flow.
3. 📖 **[Glossary](GLOSSARY.md)** - Essential MetaTrader 5 and algorithmic trading terminology.
4. 🐣 **[MT5 for Beginners](MT5_For_Beginners.md)** - Step-by-step terminal setup and demo account guide.
5. 📡 **[gRPC Streaming](GRPC_STREAM_MANAGEMENT.md)** - Subscribe to ticks, trades, DOM, and position updates.
6. 📊 **[Return Codes](RETURN_CODES_REFERENCE.md)** - Complete reference of broker and gateway return codes.
