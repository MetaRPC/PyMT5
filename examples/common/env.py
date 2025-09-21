"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/env_config.py — Environment configuration and account setup        ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ Purpose:                                                                         ║
║   Apply pb2 shim, load env/.env, prepare imports, and set up an MT5 account      ║
║   connection (preferring the extended adapter if available).                     ║
║                                                                                  ║
║ Exposes:                                                                         ║
║   1) connect()  → returns MT5Account/MT5AccountEx connected using env vars.      ║
║   2) shutdown(acc) → best-effort graceful disconnect (disconnect/close/shutdown).║
║                                                                                  ║
║ Key Variables (from env/.env):                                                   ║
║   - MT5_LOGIN, MT5_PASSWORD, MT5_SERVER                                          ║
║   - GRPC_SERVER (e.g., "mt5.mrpc.pro:443")                                       ║
║   - TIMEOUT_SECONDS (default 90), CONNECT_RETRIES (default 3)                    ║
║   - ENABLE_TRADING, SYMBOL, VOLUME                                               ║
║                                                                                  ║
║ Strategy (connect):                                                              ║
║   1) Try connect_by_server_name(server_name, …).                                 ║
║   2) Fallback connect_by_host_port(host, port, …).                               ║
║   3) Fallback connect(host, port, timeout_seconds=…) or with deadline.           ║
║   Uses small backoff between retries.                                            ║
║                                                                                  ║
║ Adapter preference:                                                              ║
║   Use MetaRpcMT5Ex.MT5AccountEx if present; otherwise MetaRpcMT5.MT5Account.     ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

# --- auto-apply pb2 shim for all examples ---
try:
    from .pb2_shim import apply_patch as _pb2_apply_patch
    _pb2_apply_patch()
except Exception:
    pass
# --------------------------------------------

import os, sys, asyncio
from datetime import datetime, timedelta

# optional: .env support
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# gRPC error type
try:
    from grpc.aio import AioRpcError
except Exception: 
    AioRpcError = Exception

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for p in (ROOT, os.path.join(ROOT, "package"), os.path.join(ROOT, "ext")):
    if p not in sys.path:
        sys.path.append(p)

# prefer the extended adapter if available
try:
    from MetaRpcMT5Ex import MT5AccountEx as MT5Account
except Exception:
    from MetaRpcMT5.mt5_account import MT5Account  # fallback


ENABLE_TRADING = os.getenv("MT5_ENABLE_TRADING", "0") == "1"
SYMBOL = os.getenv("MT5_SYMBOL", "EURUSD")
VOLUME = float(os.getenv("MT5_VOLUME", "0.10"))

async def connect() -> MT5Account:
    """
    First, try server_name (ConnectEx), if that doesn't work, try host:port.
    Timeout and retries are configurable: TIMEOUT_SECONDS (default 90), CONNECT_RETRIES (default 3)
    """
    from datetime import datetime, timedelta
    import asyncio

    user        = int(os.getenv("MT5_LOGIN", "0") or 0)
    password    = os.getenv("MT5_PASSWORD", "")
    server_name = os.getenv("MT5_SERVER", "MetaQuotes-Demo")
    grpc_server = os.getenv("GRPC_SERVER", "mt5.mrpc.pro:443")

    timeout_s = int(os.getenv("TIMEOUT_SECONDS", "90"))
    retries   = int(os.getenv("CONNECT_RETRIES", "3"))

    acc = MT5Account(user=user, password=password, grpc_server=grpc_server, id_=None)

    host = grpc_server.split(":")[0]
    try:
        port = int(grpc_server.split(":")[1])
    except Exception:
        port = 443

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            # 1) server_name / ConnectEx
            if hasattr(acc, "connect_by_server_name"):
                await acc.connect_by_server_name(
                    server_name,
                    base_chart_symbol=SYMBOL,
                    wait_for_terminal_is_alive=True,
                    timeout_seconds=timeout_s,
                )
                return acc
        except Exception as e:
            last_err = e
            # small backoff and fallback on host:port
            await asyncio.sleep(0.5 * attempt)

        try:
            # 2) host:port (If there is a special method, use it)
            if hasattr(acc, "connect_by_host_port"):
                await acc.connect_by_host_port(
                    host, port,
                    base_chart_symbol=SYMBOL,
                    wait_for_terminal_is_alive=True,
                    timeout_seconds=timeout_s,
                )
                return acc
            # 3) fallback connect(...)
            if hasattr(acc, "connect"):
                try:
                    await acc.connect(host=host, port=port, timeout_seconds=timeout_s)
                except TypeError:
                    # alternative signature - via deadline
                    deadline = datetime.utcnow() + timedelta(seconds=timeout_s)
                    await acc.connect(host=host, port=port, deadline=deadline)
                return acc
        except Exception as e:
            last_err = e
            if attempt < retries:
                await asyncio.sleep(1.0 * attempt)
                continue
            raise

    if last_err:
        raise last_err
    return acc


async def shutdown(acc) -> None:
    """Gentle shutdown (best-effort)."""
    if acc is None:
        return
    for name in ("disconnect", "close", "shutdown"):
        fn = getattr(acc, name, None)
        if callable(fn):
            try:
                res = fn()
                if asyncio.iscoroutine(res):
                    await res
                break
            except Exception:
                
                pass
