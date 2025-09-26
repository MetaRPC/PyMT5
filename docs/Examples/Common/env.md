# ⚙️ `examples/common/env.py`

Helpers for **loading environment**, auto‑patching protobuf shims, and creating a ready‑to‑use **MT5 account** (with graceful shutdown). No code changes required in your examples — just `await connect()` / `await shutdown(acc)`

---

## 🧭 What this module does

* **Applies pb2 shim** on import (`pb2_shim.apply_patch()`), so you can import enums/messages from `MetaRpcMT5.*` consistently.
* **Loads environment** via `python-dotenv` if available (`.env` is optional).
* **Picks the best adapter**: prefers `MetaRpcMT5Ex.MT5AccountEx`, falls back to `MetaRpcMT5.mt5_account.MT5Account`.
* **Connects with retries**: tries

  1. `connect_by_server_name(server_name, …)`
  2. `connect_by_host_port(host, port, …)`
  3. `connect(host=…, port=…, timeout_seconds=…)` (or `deadline` variant)
* **Shuts down nicely**: attempts `disconnect()` → `close()` → `shutdown()` (awaits if coroutine).

---

## 🔌 Public API

```python
async def connect() -> MT5Account:
    """Returns a connected MT5 account using env vars and small backoff between retries."""

async def shutdown(acc) -> None:
    """Best‑effort graceful disconnect. Safe to call multiple times; ignores errors."""
```

---

## 🌍 Environment variables

These are read at import / connect time (with defaults where noted):

```ini
# credentials & routing
MT5_LOGIN=12345678
MT5_PASSWORD=secret
MT5_SERVER=MetaQuotes-Demo
GRPC_SERVER=mt5.mrpc.pro:443

# connection behavior
TIMEOUT_SECONDS=90
CONNECT_RETRIES=3

# app behavior
MT5_ENABLE_TRADING=0     # 1 = allow trading examples
MT5_SYMBOL=EURUSD        # default symbol
MT5_VOLUME=0.10          # default lot size
```

> Tip: If `.env` exists, it will be auto‑loaded by `python-dotenv` (if installed). Otherwise use your shell to export variables.

---

## 🧪 Minimal usage example

```python
# comments intentionally in English
import asyncio
from examples.common.env import connect, shutdown

async def main():
    acc = await connect()
    try:
        print("[OK] connected as:", getattr(acc, "user", None))
        # ... do your calls here ...
    finally:
        await shutdown(acc)
        print("[OK] shutdown")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🧯 Troubleshooting

* **Wrong creds / server** → adapter raises on `connect_*`; check `MT5_LOGIN/MT5_PASSWORD/MT5_SERVER`.
* **gRPC unreachable** → verify `GRPC_SERVER` (host:port), firewall/VPN, and run `diag_connect.py` first.
* **Timeouts** → increase `TIMEOUT_SECONDS` or `CONNECT_RETRIES`.
* **Trading examples skip actions** → you likely have `MT5_ENABLE_TRADING=0`.

---

## Adapter preference

```python
try:
    from MetaRpcMT5Ex import MT5AccountEx as MT5Account
except Exception:
    from MetaRpcMT5.mt5_account import MT5Account
```

If the extended adapter is present, you’ll get extra capabilities for free — the rest of your code doesn’t change.

---

## 📝 Notes

* Adds project roots to `sys.path` (`ROOT`, `package`, `ext`) so that imports work in example runs.
* Uses a small incremental sleep between retries (0.5s, 1.0s, …) for friendlier backoff.
* `shutdown()` is idempotent-ish: safe even if the connection partially failed.

 That’s it. Keep calm and `await connect()`.

