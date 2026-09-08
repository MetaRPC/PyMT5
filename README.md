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

## 🆔 Account ID Generation (`GetId`)

> ⚠️ **Important**: You must generate your deterministic account ID with `GetId` **firstly** before connecting or streaming.

MetaRPC uses deterministic terminal identifiers derived from your MT account login number and password:
- The same `user` and `password` combination always produces the exact same deterministic GUID.
- This GUID must be supplied as the `id` routing parameter / metadata header on all subsequent calls (`ConnectEx`, `AccountSummary`, `OrderSend`, `OnSymbolTick`, etc.) along with your `APIKey` header.
- **REST Endpoint**:
  ```bash
  curl -X GET "https://mt5.mrpc.pro/GetId?user=YOUR_LOGIN&password=YOUR_PASSWORD" \
       -H "APIKey: YOUR_API_KEY"
  ```
  Returns:
  ```json
  {
    "data": {
      "id": "e8d91060-c3d3-4f4d-8d2a-9e1b2c3d4e5f"
    }
  }
  ```
- **gRPC Call**:
  Call `GetId` via the connection service stub (`GetIdRequest { User = "...", Password = "..." }`) before establishing a session.

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
