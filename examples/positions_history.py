# examples/positions_history.py
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as AH

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ---------------- utils: tolerant field setters ----------------

def _set_any(obj, names, value) -> bool:
    for n in names:
        try:
            setattr(obj, n, value)
            return True
        except Exception:
            continue
    return False

def _set_ts_any(req, names, dt) -> bool:
    if dt is None:
        return False
    if isinstance(dt, (int, float)):
        sec = int(dt)
    elif isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        sec = int(dt.timestamp())
    else:
        return False

    for n in names:
        try:
            fld = getattr(req, n)
        except Exception:
            continue
        # protobuf Timestamp?
        try:
            if hasattr(fld, "FromDatetime"):
                dtu = datetime.fromtimestamp(sec, tz=timezone.utc)
                fld.FromDatetime(dtu)
                return True
        except Exception:
            pass
        # generic {seconds,nanos}
        try:
            setattr(fld, "seconds", sec)
            return True
        except Exception:
            pass
    return False

def _fmt_ts(ts) -> str:
    try:
        sec = getattr(ts, "seconds", None)
        if sec is None:
            return "-"
        return datetime.fromtimestamp(int(sec), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "-"

def _fmt_num(x, nd=5) -> str:
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return "-"

# ---------------- main ----------------

async def main():
    acc = await connect()

    # ---- patch: robust positions_history over varying proto fields ----
    async def _positions_history(self, sort_type, open_from, open_to, page, size,
                                 deadline=None, cancellation_event=None):
        # enum tolerant
        try:
            sort_type = int(sort_type) if sort_type is not None else 0
        except Exception:
            sort_type = 0

        req = AH.PositionsHistoryRequest()

        # sort
        _set_any(req, ["sort_type", "sortType"], sort_type)

        # time window (try all known field names)
        _set_ts_any(req, ["position_open_time_from", "open_time_from", "openFrom", "positionOpenTimeFrom"], open_from)
        _set_ts_any(req, ["position_open_time_to",   "open_time_to",   "openTo",   "positionOpenTimeTo"  ], open_to)

        # pagination (snake → camel fallback)
        if not _set_any(req, ["page", "page_index", "page_number"], int(page)):
            _set_any(req, ["pageNumber"], int(page))
        if not _set_any(req, ["size", "items_per_page"],   int(size)):
            _set_any(req, ["itemsPerPage"], int(size))

        async def grpc_call(headers):
            client = getattr(self, "account_helper_client", None) or getattr(self, "account_client", None)
            if client is None:
                raise RuntimeError("AccountHelper client is not available in this build")
            timeout = None
            if deadline is not None:
                dt = (deadline - datetime.utcnow()).total_seconds()
                timeout = max(dt, 0.0)
            return await client.PositionsHistory(req, metadata=headers, timeout=timeout)

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return getattr(res, "data", res)

    acc.positions_history = _positions_history.__get__(acc, type(acc))
    # -------------------------------------------------------------------

    try:
        print("\n==================== Positions History (paged) ====================\n")

        # period: last 30 days (UTC)
        now = datetime.now(timezone.utc)
        open_from = now - timedelta(days=30)
        open_to   = now

        # sort: attempt to extract from enum, otherwise 0
        sort_val = 0
        try:
            E = getattr(AH, "AH_ENUM_POSITIONS_HISTORY_SORT_TYPE", None)
            if E is not None:
                for cand in ("OPEN_TIME_DESC", "OPEN_TIME_ASC", "TICKET_DESC", "TICKET_ASC"):
                    if hasattr(E, cand):
                        sort_val = int(getattr(E, cand))
                        break
        except Exception:
            sort_val = 0

        page = 1
        size = 50
        total_shown = 0

        # table header
        header = f"{'Ticket':>12}  {'Symbol':<10} {'Vol':>7} {'Open Time (UTC)':<20} {'Close Time (UTC)':<20} {'Open':>12} {'Close':>12} {'Profit':>10}"
        sep = "-" * len(header)
        print(header)
        print(sep)

        while True:
            # without safe_async - to avoid printing raw dumps
            resp = await acc.positions_history(sort_val, open_from, open_to, page, size)

            items = (
                getattr(resp, "positions_data", None)
                or getattr(resp, "items", None)
                or getattr(resp, "positions", None)
                or getattr(resp, "history_positions", None)
                or []
            )

            if not items:
                # If it's completely empty, we go out.
                if page == 1 and total_shown == 0:
                    print("⚠️  The server returned a response without an array of positions.")
                break

            
            for it in items:
                ticket = getattr(it, "position_ticket", None) or getattr(it, "ticket", None) or "-"
                symbol = getattr(it, "symbol", "") or "-"
                volume = getattr(it, "volume", None)
                open_t = _fmt_ts(getattr(it, "open_time", None))
                close_t= _fmt_ts(getattr(it, "close_time", None))
                p_open = getattr(it, "open_price", getattr(it, "price_open", None))
                p_close= getattr(it, "close_price", getattr(it, "price_close", None))
                profit = getattr(it, "profit", None)

                print(f"{str(ticket):>12}  {symbol:<10} {_fmt_num(volume,2):>7} {open_t:<20} {close_t:<20} {_fmt_num(p_open):>12} {_fmt_num(p_close):>12} {_fmt_num(profit,2):>10}")
                total_shown += 1

            # Pagination: If the page is shorter than size, it is the last one.
            if len(items) < size:
                break
            page += 1

        print(sep)
        print(f"Total number of lines shown: {total_shown}")

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())

# python -m examples.positions_history

async def main():
    """
    Example: Positions History (paged, schema-tolerant)
    ===================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Opens async session to the MT5 bridge; must be closed with `shutdown()`. |
    | Patch | Attach `acc.positions_history = _positions_history(...)` | Provides a robust wrapper over `AccountHelper.PositionsHistory` that survives field/enum differences across builds. |
    | Time window | `open_from = now-30d`, `open_to = now` (UTC) | Consistent UTC handling; printed as a header row. |
    | Sort | Detect sort enum (OPEN_TIME_* or TICKET_*) else `0` | Works even if enum names differ or are absent. |
    | Paging loop | Request pages until a short page (< size) arrives | Streams results in deterministic chunks; prints a header once. |
    | Print rows | Aligned table with ticket, symbol, vol, open/close time, open/close price, profit | Missing fields are rendered as “-”; numbers formatted safely. |
    | Cleanup | `await shutdown(acc)` | Ensures clean disconnect on any path. |

    RPCs used
    ---------
    - `AccountHelper.PositionsHistory(PositionsHistoryRequest)` (or `account_client` equivalent)
      - Sort type: `sort_type|sortType`
      - Open time range (any of): `position_open_time_from|open_time_from|openFrom|positionOpenTimeFrom`
                                  `position_open_time_to|open_time_to|openTo|positionOpenTimeTo`
      - Pagination: `page|page_index|page_number|pageNumber`, `size|items_per_page|itemsPerPage`

    Portability helpers
    -------------------
    - `_set_any(obj, names, value)` — assigns the first existing field among candidates (snake/camel tolerant).
    - `_set_ts_any(req, names, dt)` — writes protobuf `Timestamp` (`FromDatetime`) or `seconds` fallback.
    - `_fmt_ts(ts)` — prints `YYYY-MM-DD HH:MM:SS` (UTC) from `ts.seconds`.
    - `_fmt_num(x, nd)` — safe float formatter (fallback “-”).

    Data sources (where rows come from)
    -----------------------------------
    - The page payload may use different containers; code checks, in order:
      `positions_data` → `items` → `positions` → `history_positions`.
    - Per-row fields (best-effort):
      - ticket: `position_ticket | ticket`
      - symbol: `symbol`
      - volume: `volume`
      - times:  `open_time`, `close_time`
      - prices: `open_price | price_open`, `close_price | price_close`
      - P/L:    `profit`

    Output format (example)
    -----------------------
    Ticket        Symbol        Vol  Open Time (UTC)       Close Time (UTC)         Open        Close     Profit
    ---------------------------------------------------------------------------------------------------------------
       12345678   EURUSD       0.10  2025-09-01 10:30:00   2025-09-01 12:05:07     1.08350     1.08510       15.20
       12345679   XAUUSD       0.02  2025-09-03 09:00:00   2025-09-03 09:45:55  2350.00000  2351.10000        2.20
    ---------------------------------------------------------------------------------------------------------------
    Total rows shown: N

    Pagination & limits
    -------------------
    - Starts with `page=1`, `size=50`. If a page returns fewer than `size` rows, iteration stops.
    - Adjust `page/size` in code as needed; prints at most what the server returns.

    Timeouts & deadlines
    --------------------
    - If `deadline` is provided to the wrapper, a client-side gRPC `timeout` is derived from it.
    - If your server time is skewed, prefer omitting `deadline` and rely on client timeouts.

    Edge cases
    ----------
    - Empty/unknown containers → prints a warning on the first page and exits gracefully.
    - Mixed field naming (snake/camel) is handled automatically.
    - If `account_helper_client` is absent, the code falls back to `account_client`.

    How to run
    ----------
    From project root:
      `python -m examples.positions_history`
    Or via your CLI (if present):
      `python -m examples.cli run positions_history`
    """
