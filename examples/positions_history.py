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


"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/positions_history.py — paged positions (deals) history             ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                          ║
║   Fetch position/deal history for a time window (with pagination) and print      ║
║   it as a table. The code is resilient to heterogeneous pb2 builds: it           ║
║   supports alternate field names and multiple response container shapes.         ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ What it does (main flow)                                                         ║
║   1) Applies the pb2 shim (apply_patch) and connects to MT5 (connect()).         ║
║   2) Monkey-patches a universal method `positions_history(...)` onto `acc`:      ║
║        • Builds `AH.PositionsHistoryRequest`, tolerating field name variants;    ║
║        • Calls low-level RPC via `execute_with_reconnect()`.                     ║
║   3) Sets the period to the last 30 days (UTC).                                  ║
║   4) Tries to infer `sort_type` from enum                                        ║
║      otherwise uses 0.                                                           ║
║   5) Paginates with `size=50`, starting from `page=1`, until a short page.       ║
║   6) Prints a formatted table (header + rows) and a final total counter.         ║
║   7) Gracefully shuts down (shutdown()).                                         ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ Request fields (tolerant setters)                                                ║
║   • sort_type | sortType                                                         ║
║   • time window (any of):                                                        ║
║       position_open_time_from | open_time_from | openFrom | positionOpenTimeFrom ║
║       position_open_time_to   | open_time_to   | openTo   | positionOpenTimeTo   ║
║   • pagination (any of): page | page_index | page_number | pageNumber            ║
║                       and: size | items_per_page | itemsPerPage                  ║
║   • Timestamps are set via `FromDatetime` or `{seconds}`, always in UTC.         ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ Response extraction                                                              ║
║   • Tries containers in order: `positions_data` | `items` | `positions` |        ║
║     `history_positions`.                                                         ║
║   • For each entry it prints user-friendly fields:                               ║
║       ticket: position_ticket | ticket                                           ║
║       symbol: symbol                                                             ║
║       volume: volume                                                             ║
║       open/close time: open_time | close_time  (formatted via `seconds→UTC`)     ║
║       prices: open_price | price_open, close_price | price_close                 ║
║       profit: profit                                                             ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ Output                                                                           ║
║   Table columns:                                                                 ║
║     Ticket | Symbol | Vol | Open Time (UTC) | Close Time (UTC) | Open | Close    ║
║     | Profit                                                                     ║
║   • Numbers are formatted robustly (`_fmt_num`); times via `_fmt_ts` (UTC).      ║
║   • If the first page is empty, prints a warning.                                ║
║   • Ends with a separator and “Total number of lines shown: N”.                  ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ Direct calls                                                                     ║
║   • `client.PositionsHistory(AH.PositionsHistoryRequest, metadata, timeout)`     ║
║     where `client = acc.account_helper_client` or `acc.account_client`.          ║
║   • Uses `acc.execute_with_reconnect(..., error_selector=lambda r: r.error)`.    ║
║   • No `safe_async` wrapper in this example.                                     ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ Local helpers                                                                    ║
║   `_set_any` / `_set_ts_any` — safe setters for scalars and Timestamps.          ║
║   `_fmt_ts` / `_fmt_num` — formatting for times and numbers.                     ║
║   Logging is configured at INFO (logging.basicConfig).                           ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ Error handling & timeouts                                                        ║
║   • Timeout is derived from `deadline` inside `execute_with_reconnect`.          ║
║   • If no client is present (account_helper_client/account_client) →             ║
║     RuntimeError.                                                                ║
║   • Empty/Unexpected container shapes are handled gracefully.                    ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ How to run                                                                       ║
║   `python -m examples.cli run positions_history`                                 ║
║   (connection settings via `.env` / environment variables).                      ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""
