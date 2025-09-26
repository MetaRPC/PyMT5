# examples/market_book.py
import asyncio
import os
from datetime import datetime, timedelta

from .common.env import connect, shutdown, SYMBOL
from .common.utils import title
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI

try:
    from grpc.aio import AioRpcError
except Exception:
    AioRpcError = Exception  # fallback

# ---- tunables ----
BUDGET_SEC = int(os.getenv("ORDERBOOK_BUDGET_SEC", "15"))
PREPARE_SLEEP = float(os.getenv("ORDERBOOK_PREPARE_SLEEP", "0.8"))
ATTEMPTS = tuple(int(x) for x in os.getenv("ORDERBOOK_ATTEMPTS", "3,5").split(","))
CANDIDATES = [s.strip() for s in os.getenv("ORDERBOOK_SYMBOLS", "EURUSD,GBPUSD,USDJPY").split(",") if s.strip()]
MAX_CANDIDATES = int(os.getenv("ORDERBOOK_MAX_CANDIDATES", "2"))
# make connect faster for this example
os.environ.setdefault("TIMEOUT_SECONDS", "20")
os.environ.setdefault("CONNECT_RETRIES", "1")
# -------------------

def _fmt_side(entry_type: int) -> str:
    return {1: "BID", 2: "ASK"}.get(int(entry_type), str(entry_type))

def _compact_print_book(reply, depth: int = 5) -> None:
    levels = (getattr(reply, "entries", None)
              or getattr(reply, "book", None)
              or getattr(reply, "levels", None))
    if not levels:
        s = str(reply)
        print("order_book:\n" + (s if len(s) < 800 else s[:800] + " …"))
        return
    bids, asks = [], []
    for e in levels:
        etype  = getattr(e, "type", getattr(e, "entry_type", None))
        price  = getattr(e, "price", None)
        volume = getattr(e, "volume", getattr(e, "size", None))
        side = _fmt_side(etype)
        (bids if side == "BID" else asks).append((float(price or 0.0), float(volume or 0.0)))
    bids.sort(key=lambda x: x[0], reverse=True)
    asks.sort(key=lambda x: x[0])
    print(f"order_book (top {depth}):")
    print("  BID:")
    for p, v in bids[:depth]:
        print(f"    {p:.6f}  x {v:g}")
    print("  ASK:")
    for p, v in asks[:depth]:
        print(f"    {p:.6f}  x {v:g}")

def _to_float(x):
    try:
        return float(x)
    except Exception:
        for attr in ("value", "data", "requestedValue", "double", "price", "bid", "ask"):
            v = getattr(x, attr, None)
            if v is None:
                continue
            try:
                return float(v)
            except Exception:
                pass
        return None

async def _ticks_bookdepth(acc, symbol: str) -> int:
    try:
        resp = await acc.symbol_info_integer(symbol, MI.SymbolInfoIntegerProperty.SYMBOL_TICKS_BOOKDEPTH)
        if isinstance(resp, (int, float)):
            return int(resp)
        return int(getattr(resp, "value", 0) or 0)
    except Exception:
        return 0

async def _try_snapshot(acc, symbol: str, timeout_s: int):
    deadline = datetime.utcnow() + timedelta(seconds=timeout_s)
    try:
        return await asyncio.wait_for(
            acc.market_book_get(symbol, deadline=deadline),
            timeout=timeout_s + 1.0,
        )
    except (asyncio.TimeoutError, AioRpcError):
        return None
    except Exception:
        return None

async def _ensure_release(acc, symbol: str):
    try:
        dl = datetime.utcnow() + timedelta(seconds=4)
        await asyncio.wait_for(acc.market_book_release(symbol, deadline=dl), timeout=5.0)
    except (asyncio.TimeoutError, asyncio.CancelledError, Exception):
        pass

async def main():
    acc = None
    symbol_in_use = SYMBOL
    try:
        title("Market Book (L2) — quick check")
        
        with_budget = asyncio.timeout(BUDGET_SEC)

        async with with_budget:
            acc = await connect()

            # short candidate list: base first
            candidates = [SYMBOL] + [s for s in CANDIDATES if s != SYMBOL]
            candidates = candidates[:MAX_CANDIDATES]

            # keep only those with declared DOM
            filtered = []
            for sym in candidates:
                try:
                    await acc.symbol_select(sym, True)
                except Exception:
                    continue
                d = await _ticks_bookdepth(acc, sym)
                print(f"TICKS_BOOKDEPTH[{sym}] = {d}")
                if d > 0:
                    filtered.append(sym)

            if not filtered:
                tick = await acc.symbol_info_tick(SYMBOL)
                b = _to_float(getattr(tick, "bid", None))
                a = _to_float(getattr(tick, "ask", None))
                print("Provider does not return DOM (L2) on this account/server. Showing 1-level from tick:")
                print(f"  BID: {b}  ASK: {a}  spread: {None if (b is None or a is None) else (a-b)}")
                return

            # try each candidate quickly
            for sym in filtered:
                symbol_in_use = sym
                print(f"[{sym}] subscribing…")
                try:
                    await acc.market_book_add(sym)
                except Exception:
                    continue
                await asyncio.sleep(PREPARE_SLEEP)

                got = False
                for i, t in enumerate(ATTEMPTS, start=1):
                    print(f"[{sym}] attempt {i}/{len(ATTEMPTS)} with {t}s…")
                    snap = await _try_snapshot(acc, sym, t)
                    if snap:
                        _compact_print_book(snap, depth=5)
                        got = True
                        break

                # unsubscribe, but without blocking the main script
                try:
                    await asyncio.shield(_ensure_release(acc, sym))
                except Exception:
                    pass

                if got:
                    return

            # no L2 → 1-level
            tick = await acc.symbol_info_tick(symbol_in_use)
            b = _to_float(getattr(tick, "bid", None))
            a = _to_float(getattr(tick, "ask", None))
            print("Provider does not return DOM (L2) within short timeout. 1-level from tick:")
            print(f"  BID: {b}  ASK: {a}  spread: {None if (b is None or a is None) else (a-b)}")

    except TimeoutError:
        # The total budget is exhausted - we display a clear message and make a fallback
        print(f"Stopped after global budget of {BUDGET_SEC}s. Provider likely limits L2; showing 1-level…")
        if acc:
            try:
                tick = await acc.symbol_info_tick(symbol_in_use)
                b = _to_float(getattr(tick, "bid", None))
                a = _to_float(getattr(tick, "ask", None))
                print(f"  BID: {b}  ASK: {a}  spread: {None if (b is None or a is None) else (a-b)}")
            except Exception:
                pass
    finally:
        if acc:
            try:
                await asyncio.shield(_ensure_release(acc, symbol_in_use))
            except Exception:
                pass
            try:
                await asyncio.shield(shutdown(acc))
            except Exception:
                pass

if __name__ == "__main__":
    asyncio.run(main())


# You can start it immediately as before.:
# python -m examples.cli run market_book
#--------------------------------------------------

# To expand scanning by tools:
# $env:ORDERBOOK_SCAN_LIMIT=500
# python -m examples.cli run market_book

#--------------------------------------------------
# If you know any "live" ticker from the DOM, just insert it.:
# $env:MT5_SYMBOL="SGDM"   
# python -m examples.cli run market_book

# Less waiting time between subscribing and trying
# $env:ORDERBOOK_PREPARE_SLEEP="1.0"

# aggressive timeouts on market_book_get
# $env:ORDERBOOK_T1="4"
# $env:ORDERBOOK_T2="6"
# $env:ORDERBOOK_T3="8"

# We scan less (and found suitable ones anyway)
# $env:ORDERBOOK_SCAN_LIMIT="60"

# let's limit the candidates to a clear list
# $env:ORDERBOOK_SYMBOLS="EURUSD,GBPUSD,USDJPY,XAUUSD,US500,US30"


"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/market_book.py — fast L2 (DOM) with timeouts and fallback      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   Quickly and safely probe for order book depth (L2/DOM) on a small set of   ║
║   symbols. Uses short per-step timeouts, a global time budget, clear logs,   ║
║   graceful unsubscribe, and automatic fallback to 1-level (tick) display.    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ What it does (main flow)                                                     ║
║   1) Sets a global time budget via asyncio.timeout().                        ║
║   2) Connects to MT5 (connect()).                                            ║
║   3) Builds a candidate list: base SYMBOL + ORDERBOOK_SYMBOLS.               ║
║   4) Filters to symbols that declare DOM depth > 0                           ║
║      (symbol_info_integer: SYMBOL_TICKS_BOOKDEPTH).                          ║
║   5) For each eligible symbol:                                               ║
║        • market_book_add(sym) → short preparatory sleep;                     ║
║        • several quick market_book_get(deadline=…) attempts;                 ║
║        • on first successful snapshot, prints top levels and exits.          ║
║   6) Always tries to unsubscribe (market_book_release) without blocking.     ║
║   7) If DOM never arrives / budget expires — prints 1-level from tick.       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Tunables (env)                                                               ║
║   ORDERBOOK_BUDGET_SEC     (int, default 15) — global time budget.           ║
║   ORDERBOOK_PREPARE_SLEEP  (float, 0.8) — pause after subscription.          ║
║   ORDERBOOK_ATTEMPTS       (str, "3,5") — per-attempt seconds, CSV.          ║
║   ORDERBOOK_SYMBOLS        ("EURUSD,GBPUSD,USDJPY") — DOM candidates.        ║
║   ORDERBOOK_MAX_CANDIDATES (int, 2) — limit number of symbols to probe.      ║
║   TIMEOUT_SECONDS          (setdefault→20) — speeds up connect() timeouts.   ║
║   CONNECT_RETRIES          (setdefault→1)  — fewer connect() retries.        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Timeouts & budget                                                            ║
║   • Global: asyncio.timeout(BUDGET_SEC) bounds the ENTIRE scenario.          ║
║   • Snapshot: market_book_get(deadline=UTC+X) wrapped in asyncio.wait_for.   ║
║   • Unsubscribe: market_book_release(deadline=UTC+4) under wait_for(5s).     ║
║   • Network timeouts are handled; gRPC errors map to AioRpcError.            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Fallbacks                                                                    ║
║   • No DOM for candidates / all attempts used → print 1-level (BID/ASK).     ║
║   • Global budget exceeded → clear message + 1-level tick output.            ║
║   • Any release errors are swallowed (graceful).                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Direct API calls                                                             ║
║   symbol_select(sym, True)                                                   ║
║   symbol_info_integer(sym, SYMBOL_TICKS_BOOKDEPTH)                           ║
║   market_book_add(sym) / market_book_get(sym, deadline=…) /                  ║
║   market_book_release(sym, deadline=…)                                       ║
║   symbol_info_tick(sym) → (bid/ask)                                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Helpers in this file                                                         ║
║   _compact_print_book(reply, depth) — pretty-prints top BID/ASK levels.      ║
║   _ticks_bookdepth(acc, sym)        — reads DOM depth (int).                 ║
║   _try_snapshot(acc, sym, t)        — obtains a snapshot with a hard timeout.║
║   _ensure_release(acc, sym)         — safe unsubscribe from DOM.             ║
║   _to_float(x)                      — robustly extracts a float from various ║
║                                       protobuf response shapes.              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Dependencies                                                                 ║
║   connect(), shutdown(), SYMBOL — from examples/common/env.py                ║
║   MI.SymbolInfoIntegerProperty   — pb2 enum for TICKS_BOOKDEPTH              ║
║   grpc.aio.AioRpcError (if grpc is installed; else falls back to Exception)  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ How to run                                                                   ║
║   python -m examples.cli run market_book                                     ║
║   (see env variables above / .env for tuning)                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Notes                                                                        ║
║   • DOM candidates are filtered by declared depth (TICKS_BOOKDEPTH > 0).     ║
║   • finally: uses shield() so release/shutdown can’t be cancelled mid-exit.  ║
║   • Logs are concise and informative: attempts, timings, and fallback path.  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""