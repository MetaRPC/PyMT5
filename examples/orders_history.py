import asyncio
from datetime import datetime, timedelta, timezone
import os

from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown
from .common.utils import title
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as AH

HISTORY_DAYS = int(os.getenv("HISTORY_DAYS", "7"))
PAGE_SIZE    = int(os.getenv("HISTORY_PAGE_SIZE", "200"))

# ── utilities ─────────────────────────────────────────────────────────────────
def _utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def _fmt_ts(ts) -> str:
    sec = getattr(ts, "seconds", None)
    if sec is None:
        return ""
    return datetime.fromtimestamp(sec, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def _safe_get(obj, *names, default=None):
    for n in names:
        v = getattr(obj, n, None)
        if v is not None:
            return v
    return default

def _enum_or(default_val, *path):
    cur = AH
    try:
        for p in path:
            cur = getattr(cur, p)
        return cur
    except Exception:
        return default_val

def _set_ts_any(msg, name_candidates, dt: datetime) -> bool:
    """Find a Timestamp field by any name and call FromDatetime."""
    for name in name_candidates:
        field = getattr(msg, name, None)
        if field is not None and hasattr(field, "FromDatetime"):
            field.FromDatetime(_utc(dt))
            return True
    return False

def _set_any(msg, name_candidates, value) -> bool:
    """Find a scalar field by any name and assign a value."""
    for name in name_candidates:
        if hasattr(msg, name):
            setattr(msg, name, value)
            return True
    return False

# ── Monkey patches taking into account different field names ──────────────────────────────────
async def _order_history(self, from_dt, to_dt, *,
                         sort_mode=None, page_number=0, items_per_page=PAGE_SIZE,
                         deadline=None, cancellation_event=None):
    sort_mode = sort_mode or _enum_or(0, "BMT5_ENUM_ORDER_HISTORY_SORT_TYPE", "BMT5_SORT_BY_CLOSE_TIME_ASC")

    req = AH.OrderHistoryRequest()

    # from/to: We support both snake and camel, as well as reserved names.
    ok_from = _set_ts_any(req, ["input_from", "inputFrom", "from_", "from"], from_dt)
    ok_to   = _set_ts_any(req, ["input_to", "inputTo", "to_", "to"], to_dt)
    _set_any(req, ["input_sort_mode", "inputSortMode", "sort_mode"], sort_mode)
    _set_any(req, ["page_number", "pageNumber"], int(page_number))
    _set_any(req, ["items_per_page", "itemsPerPage"], int(items_per_page))

    if not (ok_from and ok_to):
        
        pass

    async def grpc_call(headers):
        timeout = None
        if deadline:
            timeout = max(0, (deadline - datetime.utcnow()).total_seconds())
        return await self.account_client.OrderHistory(req, metadata=headers, timeout=timeout)

    res = await self.execute_with_reconnect(
        grpc_call=grpc_call,
        error_selector=lambda r: getattr(r, "error", None),
        deadline=deadline,
        cancellation_event=cancellation_event,
    )
    return res.data

async def _positions_history(self, sort_type, *, open_from, open_to,
                             page=0, size=PAGE_SIZE,
                             deadline=None, cancellation_event=None):
    if sort_type is None:
        sort_type = _enum_or(0, "AH_ENUM_POSITIONS_HISTORY_SORT_TYPE", "AH_SORT_BY_OPEN_TIME_ASC")

    req = AH.PositionsHistoryRequest(sort_type=sort_type)

    _set_ts_any(req,
        ["position_open_time_from", "positionOpenTimeFrom", "open_time_from", "openFrom"],
        open_from
    )
    _set_ts_any(req,
        ["position_open_time_to", "positionOpenTimeTo", "open_time_to", "openTo"],
        open_to
    )
    _set_any(req, ["page_number", "pageNumber"], int(page))
    _set_any(req, ["items_per_page", "itemsPerPage"], int(size))

    async def grpc_call(headers):
        timeout = None
        if deadline:
            timeout = max(0, (deadline - datetime.utcnow()).total_seconds())
        return await self.account_client.PositionsHistory(req, metadata=headers, timeout=timeout)

    res = await self.execute_with_reconnect(
        grpc_call=grpc_call,
        error_selector=lambda r: getattr(r, "error", None),
        deadline=deadline,
        cancellation_event=cancellation_event,
    )
    return res.data

# ── printing results ──────────────────────────────────────────────────────
def _print_orders(res):
    items = _safe_get(res, "orders", "orders_history", default=[]) or []
    print(f"orders: {len(items)}")
    for i, o in enumerate(items[:50], start=1):
        ticket = _safe_get(o, "ticket", "order_ticket")
        symbol = getattr(o, "symbol", "")
        type_  = _safe_get(o, "type", "order_type")
        vol    = _safe_get(o, "volume_initial", "volume")
        price  = _safe_get(o, "price_open", "price")
        tsetup = _fmt_ts(_safe_get(o, "time_setup", "time_setup_msc"))
        tdone  = _fmt_ts(_safe_get(o, "time_done",  "time_done_msc"))
        print(f"  #{i}: order={ticket} {symbol} type={type_} vol={vol} price={price} setup={tsetup} done={tdone}")
    if len(items) > 50:
        print(f"  … more {len(items)-50}")

def _print_positions(res):
    items = _safe_get(res, "position_infos", "deals", "positions", default=[]) or []
    print(f"positions/deals: {len(items)}")
    for i, p in enumerate(items[:50], start=1):
        ticket = _safe_get(p, "ticket", "deal_ticket")
        symbol = getattr(p, "symbol", "")
        vol    = getattr(p, "volume", None)
        price  = _safe_get(p, "price_open", "price")
        profit = getattr(p, "profit", None)
        topen  = _fmt_ts(getattr(p, "open_time", None))
        tclose = _fmt_ts(getattr(p, "close_time", None))
        print(f"  #{i}: ticket={ticket} {symbol} vol={vol} price={price} profit={profit} open={topen} close={tclose}")
    if len(items) > 50:
        print(f"  … more {len(items)-50}")


async def main():
    acc = await connect()


    acc.order_history     = _order_history.__get__(acc, type(acc))
    acc.positions_history = _positions_history.__get__(acc, type(acc))

    try:
        title("Orders / Deals / Positions History")

        to_dt   = datetime.utcnow().replace(tzinfo=timezone.utc)
        from_dt = to_dt - timedelta(days=HISTORY_DAYS)
        print(f"interval: {from_dt.isoformat()} → {to_dt.isoformat()}")

        try:
            orders = await acc.order_history(from_dt, to_dt, page_number=0, items_per_page=PAGE_SIZE)
            if orders:
                _print_orders(orders)
            else:
                print("orders: 0")
        except Exception as e:
            print(f"[order_history] Error: {type(e).__name__}: {e}")

        try:
            sort_type = _enum_or(0, "AH_ENUM_POSITIONS_HISTORY_SORT_TYPE", "AH_SORT_BY_OPEN_TIME_ASC")
            deals = await acc.positions_history(sort_type, open_from=from_dt, open_to=to_dt, page=0, size=PAGE_SIZE)
            if deals:
                _print_positions(deals)
        except Exception as e:
            print(f"[positions_history] Error: {type(e).__name__}: {e}")

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())


# python -m examples.cli run orders_history

# or, for example, in 30 days
# $env:HISTORY_DAYS=30
# python -m examples.cli run orders_history


"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/orders_history.py — orders / deals / positions history         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   Query order and position/deal history for a given period directly via      ║
║   gRPC (AccountHelper), tolerate varying pb2 field names across builds,      ║
║   and print a concise, readable summary.                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ What it does (main flow)                                                     ║
║   1) Applies pb2 shim (apply_patch), connects to MT5 (connect()).            ║
║   2) Monkey-patches two methods onto `acc`:                                  ║
║        • acc.order_history(from_dt, to_dt, …)                                ║
║        • acc.positions_history(sort_type, open_from, open_to, …)             ║
║      These build requests tolerant to field-name differences and invoke      ║
║      low-level RPC via `execute_with_reconnect()`.                           ║
║   3) Computes the date interval: last `HISTORY_DAYS`.                        ║
║   4) Fetches:                                                                ║
║        • OrderHistory → prints up to 50 lines (ticket, symbol, type, volume, ║
║          price, setup/done times).                                           ║
║        • PositionsHistory → prints up to 50 lines (ticket, symbol, volume,   ║
║          price, profit, open/close times).                                   ║
║   5) Gracefully shuts down the session (shutdown()).                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Time range                                                                   ║
║   • `to_dt` = now (UTC); `from_dt` = `to_dt − HISTORY_DAYS`.                 ║
║   • Timestamp fields are filled into whichever matching names exist          ║
║     (snake/camel/alternates).                                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Pagination & sorting                                                         ║
║   • `items_per_page` = `HISTORY_PAGE_SIZE`, `page_number/page` = 0.          ║
║   • Sorting:                                                                 ║
║       - OrderHistory: `BMT5_SORT_BY_CLOSE_TIME_ASC` (if enum exists).        ║
║       - PositionsHistory: `AH_SORT_BY_OPEN_TIME_ASC` (if enum exists).       ║
║   • If enum names/paths are absent, falls back to safe `0`.                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Build robustness                                                             ║
║   • Date fields: `input_from/inputFrom/from_/from` and                       ║
║                  `input_to/inputTo/to_/to`.                                  ║
║   • Sort/page fields: `input_sort_mode/inputSortMode/sort_mode`,             ║
║     `page_number/pageNumber`, `items_per_page/itemsPerPage`.                 ║
║   • Enums resolved via `_enum_or(AH, …)`; if path not found → default `0`.   ║
║   • Responses read “softly” via `_safe_get()` across keys like               ║
║     `orders/orders_history` and `positions/deals/position_infos`.            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Output                                                                       ║
║   • Orders: `orders: <N>` plus up to 50 entries with ticket, symbol, type,   ║
║     volume, price, setup/done (UTC).                                         ║
║   • Positions/Deals: `positions/deals: <N>` plus up to 50 entries with       ║
║     ticket, symbol, volume, price, profit, open/close (UTC).                 ║
║   • If N > 50, prints `… more <N-50>`.                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Environment variables                                                        ║
║   HISTORY_DAYS       — history window length (default 7).                    ║
║   HISTORY_PAGE_SIZE  — page size (default 200).                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Direct RPCs (via acc.execute_with_reconnect)                                 ║
║   • `account_client.OrderHistory(AH.OrderHistoryRequest)`                    ║
║   • `account_client.PositionsHistory(AH.PositionsHistoryRequest)`            ║
║     (timeout derived from deadline; `error_selector` → `r.error`)            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Helpers in this file                                                         ║
║   `_utc(dt)`               — normalize datetime to UTC.                      ║
║   `_fmt_ts(ts)`            — `Timestamp.seconds` → UTC string.               ║
║   `_safe_get(obj, *names)` — safely extract a field from multiple names.     ║
║   `_enum_or(default, …)`   — resolve enum from AH by path, else default.     ║
║   `_set_ts_any(msg, names, dt)` — write `Timestamp` into the first matching. ║
║   `_set_any(msg, names, val)`  — write scalar into the first matching field. ║
║   `_print_orders(res)` / `_print_positions(res)` — formatted output.         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Caveats / limitations                                                        ║
║   • If `from/to` fields can’t be set (rare build), the request goes without  ║
║     them; server-side defaults may return empty results.                     ║
║   • Time printing uses only `seconds`; if absent, prints empty string.       ║
║   • No `safe_async` wrapper here — exceptions are handled locally around     ║
║     the calls.                                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ How to run                                                                   ║
║   `python -m examples.cli run orders_history`                                ║
║   (connection settings via `.env` / environment vars).                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""