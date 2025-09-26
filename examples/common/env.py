from __future__ import annotations

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

# 1) Ensure project paths are on sys.path (ROOT, package/, ext/)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for p in (ROOT, os.path.join(ROOT, "package"), os.path.join(ROOT, "ext")):
    if p not in sys.path:
        sys.path.append(p)

# 2) Apply pb2 shim NOW (MetaRpcMT5 is importable because sys.path is ready)
try:
    from .pb2_shim import apply_patch as _pb2_apply_patch
    _pb2_apply_patch()
except Exception:
    # soft-fail: we'll try again after imports
    pass

# 3) Prefer extended adapter if available, otherwise base
try:
    from MetaRpcMT5Ex import MT5AccountEx as MT5Account
except Exception:
    from MetaRpcMT5.mt5_account import MT5Account  # fallback

# 4) Re-apply shim AFTER imports (idempotent safety)
try:
    _pb2_apply_patch()
except Exception:
    pass

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
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/common/env.py — environment bootstrap & resilient MT5 connect  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose:                                                                     ║
║   Prepare PYTHONPATH, load .env, apply the pb2 shim, pick the account        ║
║   adapter (extended/base), and establish a gRPC connection to an MT5         ║
║   terminal with retries and timeouts. Also provides a gentle shutdown.       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ What it does (happy path):                                                   ║
║   1) Appends project paths to sys.path: repo root, ./package, ./ext.         ║
║   2) Applies pb2_shim.apply_patch() early to expose pb2 modules/aliases      ║
║      (important across different MetaRpcMT5 builds).                         ║
║   3) Imports MT5AccountEx from MetaRpcMT5Ex if available; otherwise falls    ║
║      back to MetaRpcMT5.mt5_account.MT5Account.                              ║
║   4) Re-applies the pb2 shim (idempotent) after imports for safety.          ║
║   5) Reads settings from environment and optional .env.                      ║
║   6) connect():                                                              ║
║      • collects credentials & endpoints (login/password/server/host:port),   ║
║      • tries connect_by_server_name(...),                                    ║
║      • if not available/failed — tries connect_by_host_port(...),            ║
║      • else falls back to a generic connect(...),                            ║
║      • between attempts: small backoff; respects retry/timeout limits.       ║
║   7) Returns a ready-to-use MT5Account instance.                             ║
║   8) shutdown(): performs best-effort graceful disconnect (disconnect/close/ ║
║      shutdown — whichever exists), awaiting coroutines when needed.          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Environment variables (inputs):                                              ║
║   MT5_LOGIN            (int, default 0)                                      ║
║   MT5_PASSWORD         (str, "")                                             ║
║   MT5_SERVER           (str, "MetaQuotes-Demo")                              ║
║   GRPC_SERVER          (str, "mt5.mrpc.pro:443") → parsed into host/port     ║
║   TIMEOUT_SECONDS      (int, 90)                                             ║
║   CONNECT_RETRIES      (int, 3)                                              ║
║   MT5_ENABLE_TRADING   ("1"/"0", default "0")                                ║
║   MT5_SYMBOL           (str, "EURUSD")                                       ║
║   MT5_VOLUME           (float, "0.10")                                       ║
║  * .env is loaded automatically via dotenv.load_dotenv().                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Connection behavior (details):                                               ║
║   • For connect_by_server_name / connect_by_host_port the code sets          ║
║     base_chart_symbol=SYMBOL and wait_for_terminal_is_alive=True.            ║
║   • Generic connect(...) tries two signatures:                               ║
║       - with timeout_seconds, or                                             ║
║       - with deadline = utcnow + timeout_s (fallback signature).             ║
║   • Retries: up to CONNECT_RETRIES with small exponential-ish backoff.       ║
║   • The last exception is re-raised for clear diagnostics.                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Exported constants (used by examples):                                       ║
║   ENABLE_TRADING: bool  — toggles live trading via env.                      ║
║   SYMBOL: str          — default symbol (ensured in Market Watch).           ║
║   VOLUME: float        — default lot size.                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Helpers / utilities used:                                                    ║
║   • dotenv.load_dotenv() — loads .env if present.                            ║
║   • pb2_shim.apply_patch() — exposes pb2 modules/classes and smooths build   ║
║     differences (aliases, AccountHelper*Stub name variants, request classes).║
║   • grpc.aio.AioRpcError — gRPC error type (soft fallback to Exception if    ║
║     grpc isn't available during static checks).                              ║
║   • Adapter methods from MT5Account/MT5AccountEx:                            ║
║       connect_by_server_name / connect_by_host_port / connect,               ║
║       and disconnect/close/shutdown for teardown.                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Public API of this file:                                                     ║
║   async def connect() -> MT5Account                                          ║
║       Establishes a connection and returns the ready account object.         ║
║                                                                              ║
║   async def shutdown(acc) -> None                                            ║
║       Gracefully closes the connection (best effort), awaiting coroutines.   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""