import asyncio
import os
from datetime import datetime, timedelta

from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown, SYMBOL
from .common.utils import title, safe_async
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI


# --- utilities ---------------------------------------------------------------

def _fmt_side(entry_type: int) -> str:
    return {1: "BID", 2: "ASK"}.get(int(entry_type), str(entry_type))

def _compact_print_book(reply, depth: int = 5) -> None:
    levels = (
        getattr(reply, "entries", None)
        or getattr(reply, "book", None)
        or getattr(reply, "levels", None)
    )
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


async def _get_ticks_bookdepth(acc, symbol: str) -> int:
    resp = await safe_async(
        f"symbol_info_integer(TICKS_BOOKDEPTH)('{symbol}')",
        acc.symbol_info_integer, symbol,
        MI.SymbolInfoIntegerProperty.SYMBOL_TICKS_BOOKDEPTH
    )
    return int(getattr(resp, "value", 0) or 0)


async def _try_get_book_once(acc, symbol: str, secs: int):
    deadline = datetime.utcnow() + timedelta(seconds=secs)
    return await safe_async(
        f"market_book_get({symbol},{secs}s)",
        acc.market_book_get, symbol,
        deadline=deadline
    )


async def _ensure_release(acc, symbol: str, secs: int = 8):
    try:
        deadline = datetime.utcnow() + timedelta(seconds=secs)
        await safe_async("market_book_release", acc.market_book_release, symbol, deadline=deadline)
    except Exception:
        
        pass


async def _scan_symbols_with_dom(acc, limit: int = 200, show_top: int = 10):
    """Returns a list of symbols with depth>0 among the first `limit` instruments."""
    
    total_resp = await safe_async("symbols_total(False)", acc.symbols_total, False)
    total = int(getattr(total_resp, "total", 0) or 0)
    if not total:
        print("Failed to get character count.")
        return []

    count = min(limit, total)
    names = []
    for i in range(count):
        name_resp = await safe_async(f"symbol_name({i}, False)", acc.symbol_name, i, False)
        name = getattr(name_resp, "name", None)
        if name:
            names.append(name)

    # Checking the depth
    found = []
    for nm in names:
        d = await _get_ticks_bookdepth(acc, nm)
        if d > 0:
            found.append((nm, d))
            if len(found) >= show_top:
                break

    if found:
        print("Found symbols from the DOM:", ", ".join(f"{s}({d})" for s, d in found))
    else:
        print(f"Didn't find any DOM in the first {count} characters. Increase the scanner limit.")

    return [s for s, _ in found]


# --- Main scenario -----------------------------------------------------

async def main():
    acc = await connect()
    try:
        title("Market Book (L2)")

        # 0) base symbol from .env
        symbol = SYMBOL
        await safe_async("symbol_select", acc.symbol_select, symbol, True)

        depth_val = await _get_ticks_bookdepth(acc, symbol)
        print(f"TICKS_BOOKDEPTH[{symbol}] =", depth_val)

        # If the base symbol doesn't have a DOM, we immediately look for another one.
        if depth_val <= 0:
            print(f"The symbol {symbol} doesn't have a glass. I'm looking for an alternative…")
            alts = await _scan_symbols_with_dom(acc, limit=int(os.getenv("ORDERBOOK_SCAN_LIMIT", "200")))
            if not alts:
                return
            symbol = alts[0]
            print(f"Switching to {symbol}")
            await safe_async("symbol_select", acc.symbol_select, symbol, True)

        # 1) subscription
        await safe_async("market_book_add", acc.market_book_add, symbol)
        await asyncio.sleep(1.5)  # let the server prepare

        # 2) three attempts with an increasing deadline
        got = False
        for secs in (6, 10, 15):
            reply = await _try_get_book_once(acc, symbol, secs)
            if reply:
                _compact_print_book(reply, depth=5)
                got = True
                break

        # 3) Didn't work? Let's look for another symbol in the DOM and try again.
        if not got:
            print("The snapshot didn't arrive. I'm looking for another symbol with DOM…")
            alts = await _scan_symbols_with_dom(acc, limit=int(os.getenv("ORDERBOOK_SCAN_LIMIT", "200")))
            # remove the current symbol from the candidates if it is there
            alts = [s for s in alts if s != symbol]
            if alts:
                symbol2 = alts[0]
                print(f"I'm trying {symbol2}")
                await _ensure_release(acc, symbol) 
                await safe_async("market_book_add", acc.market_book_add, symbol2)
                await asyncio.sleep(1.5)
                for secs in (6, 10, 15):
                    reply = await _try_get_book_once(acc, symbol2, secs)
                    if reply:
                        _compact_print_book(reply, depth=5)
                        symbol = symbol2
                        got = True
                        break

        if not got:
            print("DOM never returned the snapshot. It looks like the provider is limiting L2 for this account/instruments..")

    finally:
        await _ensure_release(acc, symbol, secs=8)
        await shutdown(acc)


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

"""
    Example: Market Book (L2) snapshot with fallback scan
    =====================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Open async session to MT5 bridge; must be closed with `shutdown()`. |
    | Base symbol | `symbol = SYMBOL` from env, then `symbol_select(symbol, True)` | Use configured symbol; ensure it is selected/visible in the terminal. |
    | Depth check | `_get_ticks_bookdepth()` via `symbol_info_integer(SYMBOL_TICKS_BOOKDEPTH)` | Quickly detects whether DOM (L2) is even available for the symbol. |
    | Subscribe | `market_book_add(symbol)` then short `sleep(1.5)` | Ask server to start feeding order book events; small delay gives the server time to prepare a snapshot. |
    | Try snapshot | Up to 3 attempts: `market_book_get(symbol, deadline=now+{6,10,15}s)` | Progressive deadlines improve odds in slow environments. Stops at the first success. |
    | Print book | `_compact_print_book(reply, depth=5)` | Prints top N (BID first, then ASK). Entry type mapping: 1→BID, 2→ASK. |
    | Fallback scan | If no snapshot: `_scan_symbols_with_dom(limit, show_top)` | Scans first `limit` instruments, checks `TICKS_BOOKDEPTH`, switches to a symbol with DOM and retries once. |
    | Cleanup | `_ensure_release()` + `shutdown()` | Always release the book (best-effort) and close the session even on errors. |

    RPCs used (with params)
    -----------------------
    - `symbol_select(symbol: str, enable: bool)`                           → ensure symbol availability
    - `symbol_info_integer(symbol: str, property=SYMBOL_TICKS_BOOKDEPTH)`  → DOM depth (0 = no L2)
    - `market_book_add(symbol: str)`                                       → subscribe to order book
    - `market_book_get(symbol: str, deadline: datetime)`                   → request current snapshot
    - `market_book_release(symbol: str, deadline: datetime)`               → release subscription (polite cleanup)
    - `symbols_total(visible_only: bool)`                                  → total instruments
    - `symbol_name(index: int, selected: bool)`                            → instrument name by index

    Helper behavior
    ---------------
    - `_compact_print_book(reply, depth=5)` tolerates different payload shapes:
      it looks for `entries` or `book` or `levels`. For each level it extracts `type/entry_type`, `price`, `volume/size`.
      Output format (examples):
        order_book (top 5):
          BID:
            1.234560  x 100
          ASK:
            1.234700  x 90
    - `_ensure_release()` swallows exceptions on release to avoid hangs on shutdown.
    - All RPCs are wrapped with `safe_async(label, func, *args)` for labeled logging and exception safety.

    Environment / knobs
    -------------------
    - `MT5_SYMBOL` (string) — base symbol for the first attempt (imported as `SYMBOL`).
    - `ORDERBOOK_SCAN_LIMIT` (int, default 200) — how many instruments to scan while searching for DOM.
    - Retry sequence for snapshot deadlines: 6s → 10s → 15s (tweak in code if needed).
    - Print depth for the compact view: 5 levels each side (tweak via `_compact_print_book(..., depth=5)`).

    Typical flows
    -------------
    1) DOM available on the base symbol:
       - subscribe → get snapshot within first/second deadline → print top 5 → release.
    2) No DOM on the base symbol:
       - scan `limit` instruments → pick first with `TICKS_BOOKDEPTH>0` → subscribe & retry → print → release.
    3) Provider limits DOM:
       - after all attempts prints: "DOM did not deliver a snapshot..." and exits gracefully.

    Edge cases & safety
    -------------------
    - If `symbols_total()` returns 0 or names cannot be fetched, scan path aborts with a clear message.
    - If snapshot `reply` is not structured (no levels), it prints a trimmed `str(reply)` instead of crashing.
    - Deadlines use UTC; server/terminal latency is tolerated by progressive timeouts.

    How to run
    ----------
    From project root (module path):
      `python -m examples.market_book`

    If you use the CLI runner:
      `python -m examples.cli run market_book`

    Optional environment:
      Windows PowerShell
        `$env:ORDERBOOK_SCAN_LIMIT=500`
        `$env:MT5_SYMBOL="SGDM"`
      Bash
        `export ORDERBOOK_SCAN_LIMIT=500`
        `export MT5_SYMBOL=SGDM`
    """