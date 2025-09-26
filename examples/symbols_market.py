# examples/symbols_market.py
import asyncio
import os

from .common.env import connect, shutdown, SYMBOL
from .common.utils import title, pprint
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI  # enums

# gRPC error type (optional)
try:
    from grpc.aio import AioRpcError
except Exception:
    AioRpcError = Exception  # fallback

# --- Fast profile (can be overridden via env) ---
os.environ.setdefault("TIMEOUT_SECONDS", "15")   # connect timeout (env.py respects this)
os.environ.setdefault("CONNECT_RETRIES", "1")    # fewer retries to avoid hangs
EX_BUDGET = int(os.getenv("EXAMPLE_BUDGET_SEC", "20"))  # global cap for the whole example

SCAN_LIMIT_ALL = int(os.getenv("SYMBOLS_SCAN_LIMIT_ALL", "30"))
SCAN_LIMIT_WATCH = int(os.getenv("SYMBOLS_SCAN_LIMIT_WATCH", "30"))

# ---------- helpers ----------

def _to_float(x):
    try:
        return float(x)
    except Exception:
        for attr in ("value", "data", "requestedValue", "double", "price", "bid", "ask", "point"):
            v = getattr(x, attr, None)
            if v is None:
                continue
            try:
                return float(v)
            except Exception:
                pass
        return None

def _to_int(x):
    try:
        return int(x)
    except Exception:
        v = getattr(x, "value", None)
        try:
            return int(v)
        except Exception:
            return None

def _to_str(x):
    if isinstance(x, str):
        return x
    for attr in ("value", "data", "name", "string"):
        v = getattr(x, attr, None)
        if isinstance(v, str):
            return v
    return str(x)

async def _symbols_total(acc, selected: bool) -> int:
    try:
        r = await acc.symbols_total(selected)
        return _to_int(r) or 0
    except Exception:
        return 0

async def _symbol_name(acc, index: int, selected: bool) -> str | None:
    try:
        r = await acc.symbol_name(index, selected)
        return r if isinstance(r, str) else getattr(r, "name", None)
    except Exception:
        return None

async def _ensure_selected(acc, symbol: str):
    try:
        await acc.symbol_select(symbol, True)
    except Exception:
        pass

async def _print_symbol_snapshot(acc, symbol: str):
    # exist
    try:
        ex = await acc.symbol_exist(symbol)
        print(f"{symbol}: exist =", bool(ex if isinstance(ex, (int, float, bool)) else getattr(ex, 'exist', True)))
    except Exception:
        print(f"{symbol}: exist = ?")

    # tick
    try:
        t = await acc.symbol_info_tick(symbol)
        b = _to_float(getattr(t, "bid", None))
        a = _to_float(getattr(t, "ask", None))
        print(f"  tick: BID={b}  ASK={a}  spread={None if (b is None or a is None) else (a-b)}")
    except Exception:
        print("  tick: <error>")

    # doubles
    try:
        bid = await acc.symbol_info_double(symbol, MI.SymbolInfoDoubleProperty.SYMBOL_BID)
        ask = await acc.symbol_info_double(symbol, MI.SymbolInfoDoubleProperty.SYMBOL_ASK)
        point = await acc.symbol_info_double(symbol, MI.SymbolInfoDoubleProperty.SYMBOL_POINT)
        print(f"  doubles: BID={_to_float(bid)}  ASK={_to_float(ask)}  POINT={_to_float(point)}")
    except Exception:
        print("  doubles: <error>")

    # integers
    try:
        digits = await acc.symbol_info_integer(symbol, MI.SymbolInfoIntegerProperty.SYMBOL_DIGITS)
        trade_mode = await acc.symbol_info_integer(symbol, MI.SymbolInfoIntegerProperty.SYMBOL_TRADE_MODE)
        print(f"  integers: DIGITS={_to_int(digits)}  TRADE_MODE={_to_int(trade_mode)}")
    except Exception:
        print("  integers: <error>")

    # strings (best effort)
    try:
        desc = await acc.symbol_info_string(symbol, MI.SymbolInfoStringProperty.SYMBOL_DESCRIPTION)
        s = _to_str(desc)
        if s and s != "None":
            print(f"  description: {s}")
    except Exception:
        pass

# ---------- main ----------

async def main():
    acc = None
    try:
        title("Symbols & Market Info (fast-safe)")
        # Hard global budget for the whole example
        async with asyncio.timeout(EX_BUDGET):
            acc = await connect()

            # Ensure base symbol is visible
            await _ensure_selected(acc, SYMBOL)

            # Totals
            total_all = await _symbols_total(acc, selected=False)
            total_watch = await _symbols_total(acc, selected=True)
            print(f"Symbols total: all={total_all}  market_watch={total_watch}")

            # List a few names (all)
            if total_all:
                n = min(SCAN_LIMIT_ALL, total_all)
                names_all = []
                for i in range(n):
                    nm = await _symbol_name(acc, i, selected=False)
                    if nm:
                        names_all.append(nm)
                if names_all:
                    print("All symbols (sample):", ", ".join(names_all[:10]) + (" ..." if len(names_all) > 10 else ""))

            # List a few names (watchlist)
            if total_watch:
                n = min(SCAN_LIMIT_WATCH, total_watch)
                names_w = []
                for i in range(n):
                    nm = await _symbol_name(acc, i, selected=True)
                    if nm:
                        names_w.append(nm)
                if names_w:
                    print("Market Watch (sample):", ", ".join(names_w[:10]) + (" ..." if len(names_w) > 10 else ""))

            # Snapshots: base + up to 2 from Watchlist
            sample = [SYMBOL]
            if total_watch:
                n = min(2, total_watch)
                for i in range(n):
                    nm = await _symbol_name(acc, i, selected=True)
                    if nm and nm not in sample:
                        sample.append(nm)

            print("\nSnapshots:")
            for s in sample:
                await _ensure_selected(acc, s)
                await _print_symbol_snapshot(acc, s)

    except TimeoutError:
        print(f"Stopped after global budget of {EX_BUDGET}s. Server/provider is too slow right now.")
    except AioRpcError as e:
        # Typical: DEADLINE_EXCEEDED on slow/muted servers
        detail = getattr(e, "details", lambda: "")()
        print(f"gRPC error during symbols demo: {detail or 'AioRpcError'}. "
              f"Likely provider timeout. Try increasing TIMEOUT_SECONDS or switch server.")
    finally:
        if acc:
            try:
                await shutdown(acc)
            except Exception:
                pass

if __name__ == "__main__":
    asyncio.run(main())


# python -m examples.cli run symbols_market


"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/symbols_market.py — symbols overview (fast-safe)               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   A quick, fault-tolerant demo that:                                         ║
║   • connects with short timeouts,                                            ║
║   • counts available symbols (all vs. Market Watch),                         ║
║   • prints small samples of names,                                           ║
║   • shows compact “snapshots” per symbol (exist, tick, BID/ASK/POINT,        ║
║     DIGITS/TRADE_MODE, DESCRIPTION).                                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Execution flow                                                               ║
║   1) Sets a “fast profile” via env:                                          ║
║      TIMEOUT_SECONDS=15, CONNECT_RETRIES=1, EXAMPLE_BUDGET_SEC=20.           ║
║   2) Creates a global deadline using `asyncio.timeout(...)`.                 ║
║   3) `connect()` → ensures base `SYMBOL` is visible in Market Watch.         ║
║   4) Requests totals:                                                        ║
║        • `symbols_total(False)` — all symbols,                               ║
║        • `symbols_total(True)`  — Market Watch.                              ║
║   5) Prints a sampled list of names (limited by SCAN_LIMIT_*).               ║
║   6) Builds a snapshot list: base SYMBOL + up to 2 from Watchlist.           ║
║   7) For each symbol prints:                                                 ║
║        • exist,                                                              ║
║        • tick (BID/ASK + spread),                                            ║
║        • doubles: BID/ASK/POINT,                                             ║
║        • integers: DIGITS/TRADE_MODE,                                        ║
║        • string DESCRIPTION (best-effort).                                   ║
║   8) Gracefully closes the session via `shutdown()`.                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Key RPCs & enums                                                             ║
║   • `symbols_total(selected: bool)`                                          ║
║   • `symbol_name(index: int, selected: bool)`                                ║
║   • `symbol_select(symbol, True)`                                            ║
║   • `symbol_exist(symbol)`                                                   ║
║   • `symbol_info_tick(symbol)` → fields `bid/ask`                            ║
║   • `symbol_info_double(symbol, MI.SymbolInfoDoubleProperty.…)`              ║
║       – `SYMBOL_BID`, `SYMBOL_ASK`, `SYMBOL_POINT`                           ║
║   • `symbol_info_integer(symbol, MI.SymbolInfoIntegerProperty.…)`            ║
║       – `SYMBOL_DIGITS`, `SYMBOL_TRADE_MODE`                                 ║
║   • `symbol_info_string                                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Helper utilities                                                             ║
║   • `_to_float/_to_int/_to_str` — robust extraction from varied pb2 shapes   ║
║     (`.value/.data/...`).                                                    ║
║   • `_symbols_total`, `_symbol_name` — wrappers with try/except.             ║
║   • `_ensure_selected` — ensures symbol is in Market Watch.                  ║
║   • `_print_symbol_snapshot` — unified, compact per-symbol printout.         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Environment / tunables                                                       ║
║   • `EXAMPLE_BUDGET_SEC` (default 20) — hard time cap for the whole demo.    ║
║   • `TIMEOUT_SECONDS` (15) — connect timeout (respected by env.py).          ║
║   • `CONNECT_RETRIES` (1) — fewer retries to avoid hangs.                    ║
║   • `SYMBOLS_SCAN_LIMIT_ALL` (30) — how many “all” names to scan.            ║
║   • `SYMBOLS_SCAN_LIMIT_WATCH` (30) — how many Watchlist names to scan.      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Error handling                                                               ║
║   • Global `asyncio.timeout` → clear message on `TimeoutError`.              ║
║   • Catches `AioRpcError` (e.g., DEADLINE_EXCEEDED) with a hint to increase  ║
║     `TIMEOUT_SECONDS` or switch server.                                      ║
║   • Value converters tolerate non-standard response shapes.                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Output                                                                       ║
║   • Totals line: `Symbols total: all=N  market_watch=M`.                     ║
║   • Sampled name lists (ellipsis if truncated).                              ║
║   • `Snapshots:` block (1–3 symbols) with tick/doubles/integers/description. ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Dependencies                                                                 ║
║   • `connect`, `shutdown`, `SYMBOL` — `examples/common/env.py`               ║
║   • `title` — `examples/common/utils.py`                                     ║
║   • pb2 enums: `MetaRpcMT5.mt5_term_api_market_info_pb2 as MI`               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ How to run                                                                   ║
║   • `python -m examples.cli run symbols_market`                              ║
║     (or run the module directly).                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""



