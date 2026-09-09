# PyMT5 SDK

> Official MetaTrader 5 Python SDK for algorithmic trading, backtesting, and market data streaming via gRPC.

[![Docs](https://img.shields.io/badge/docs-PyMT5-blue.svg)](https://metarpc.github.io/PyMT5/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

📄 **Full Documentation**: [https://metarpc.github.io/PyMT5/](https://metarpc.github.io/PyMT5/)

---

## 📦 Installation

```bash
pip install MetaRpcMT5
```

---

## 🔑 API Key & Authentication

Connecting to MetaRPC production endpoints (`mt5.mrpc.pro:443`) requires an API key:

1. **Sign Up**: Create an account for free at [https://mrpc.pro/signup](https://mrpc.pro/signup).
2. **Generate API Key**: In your MetaRPC Portal dashboard at [https://mrpc.pro/my](https://mrpc.pro/my), go to **API Keys** to generate and copy your personal API token.
3. **Configure Connection**: Pass your API key / token along with the server address (`mt5.mrpc.pro:443`) in your connection settings.

---


---

## 🆔 Automatic Account ID & Authentication

MetaRPC uses deterministic terminal identifiers derived from your account login number and password:
- The SDK automatically derives and attaches your deterministic account GUID (`id`) and `APIKey` headers on all calls (`ConnectEx`, `AccountSummary`, `OrderSend`, streaming, etc.).
- Account ID derivation is completely automatic inside the library constructor/client initialization — no manual `GetId` or `curl` calls required.
- Pass your API key directly to the Account/Client constructor or via the `MRPC_API_KEY` environment variable.

## 🌐 Production Endpoints

| Environment | Host | Port | Protocol |
| :--- | :--- | :--- | :--- |
| **Production** | `mt5.mrpc.pro` | `443` | TLS / gRPC |
| **Direct API UI (Swagger)** | `https://mt5.mrpc.pro/apiui` | `443` | HTTPS |
| **Portal Dashboard** | `https://mrpc.pro/my` | `443` | HTTPS |
| **Registration / API Key** | `https://mrpc.pro/signup` | `443` | HTTPS |

---

## 📄 Documentation & Guides

Explore comprehensive documentation at [https://metarpc.github.io/PyMT5/](https://metarpc.github.io/PyMT5/):
- 🚀 **Quick Start & First Project**
- 🔑 **Authentication & API Keys**
- 📡 **Live Market Data & gRPC Streaming**
- 💼 **Account Management & Order Execution**
- 📊 **Return Codes & Error Handling Reference**
