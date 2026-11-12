# PyMT5 SDK — Cloud Python SDK for MetaTrader 5 (MT5)

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://img.shields.io/badge/docs-PyMT5-0083ff.svg)](https://metarpc.github.io/PyMT5/)
[![Cloud](https://img.shields.io/badge/VPS-Not_Required-success.svg)](https://mrpc.pro)
[![Platform](https://img.shields.io/badge/OS-Linux%20|%20macOS%20|%20Windows%20|%20Docker-brightgreen.svg)](https://mrpc.pro)

Python client for managed MetaTrader 5 terminals. Run your Python application on Linux, macOS or Windows; the remote MetaTrader terminal still runs on Windows. Broker access, account permissions and API service availability apply.

## Start with a read-only demo

The smallest example connects, reads the account summary and attempts to disconnect in `finally`. It does not submit orders. Hosted connection usage is billed: see [current pricing](https://mrpc.pro/#pricing) and the [cost calculator](https://mrpc.pro/tools/terminal-cost?lang=en).

```bash
git clone https://github.com/MetaRPC/PyMT5.git
cd PyMT5
python -m pip install ./package
# Set MRPC_API_KEY, MT5_LOGIN, MT5_PASSWORD and MT5_SERVER
# in your private process environment, using a disposable demo account.
python examples/read_account.py
```

Get your API key from [the portal](https://mrpc.pro/my). Do not paste passwords or API keys into issues, screenshots, source files or command-line arguments. The SDK supplies authentication metadata and uses the connection identifier returned by the server. Keep that identifier private too.

The example displays amounts in the account currency, not necessarily USD. A network failure can leave connection status uncertain; check the portal and stop an unused terminal. The SDK's disconnect method suppresses server errors, so returning from cleanup alone is not proof of remote shutdown.

## Choose your next example

- [Read-only account example](examples/read_account.py): the starting point above.
- [Interactive examples](examples/main.py): configure `examples/0_common/settings.json` locally and run `python examples/main.py`. A positional argument selects an example; it is **not** an API key. Some examples place trades. Review each before running and use disposable demo accounts.
- [Python walkthrough](https://mrpc.pro/tutorials/console/python?lang=en): the existing recorded workflow.
- [Quote streaming](https://mrpc.pro/tutorials/console/websocket?lang=en): subscriptions, events and cleanup.
- [Local Python versus a hosted API](https://mrpc.pro/guides/local-python-vs-cloud-api?lang=en): deployment and operational tradeoffs.
- [Copier sizing calculator](https://mrpc.pro/tools/copier-sizing?lang=en): inspect requested volume before broker rounding. Copy trading uses the separate [PyCopier SDK](https://metarpc.github.io/PyCopier/).

The example menu includes trading and strategy demonstrations. They are examples, not investment recommendations or production reliability guarantees. Check actual order/history state before retrying a timed-out trade request.

## Endpoints and deployment

| Service | Address |
| --- | --- |
| MT5 gRPC over TLS | `mt5.mrpc.pro:443` |
| MT5 REST/API console | [mt5.mrpc.pro/apiui](https://mt5.mrpc.pro/apiui) |
| Terminals and API key | [mrpc.pro/my](https://mrpc.pro/my) |
| Product and pricing | [mrpc.pro](https://mrpc.pro/) |

This package's low-level client is gRPC; the REST console is a separate interface. Do not mix REST header examples with gRPC method signatures. Broker support must be checked against the actual server and demo account. No universal broker coverage, execution-latency guarantee or free hosted usage is implied.

## Development checks

```bash
python -m unittest discover -s tests -p test_read_account_example.py
```

These offline tests verify the example's lifecycle, failure cleanup and credential handling. They do not prove broker connectivity or order execution.

## 📚 Complete Documentation & Code Examples

- 📖 [Comprehensive Documentation](https://metarpc.github.io/PyMT5/)
- 🚀 [10-Minute First Project Guide](https://metarpc.github.io/PyMT5/All_Guides/Your_First_Project/)
- 📡 [Live Tick & Bar gRPC Streaming](https://metarpc.github.io/PyMT5/All_Guides/GRPC_STREAM_MANAGEMENT/)
- 💼 [Order Execution & Position Management](https://metarpc.github.io/PyMT5/MT5Account/MT5Account.Master.Overview/)
- 💡 [Example Scripts & Strategies](https://github.com/MetaRPC/PyMT5/tree/main/examples)

## 📄 License

This SDK is open-sourced under the [MIT License](LICENSE).  
Cloud infrastructure and API services are operated by [MetaRPC](https://mrpc.pro).

