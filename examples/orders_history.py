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
    Example: Orders / Deals / Positions History (paged, robust to schema variants)
    =============================================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Opens async session to the MT5 bridge; must be closed with `shutdown()`. |
    | Monkey-patch | Attach `_order_history` and `_positions_history` to `acc` | Provides portable wrappers that tolerate field/enum name differences across builds. |
    | Interval | `from_dt = now - HISTORY_DAYS`, `to_dt = now` (UTC) | Uses UTC consistently; printable ISO interval banner. |
    | Orders | `acc.order_history(from_dt, to_dt, page=0, size=PAGE_SIZE)` | Requests historical orders with optional sort mode and pagination; prints up to 50 items. |
    | Positions/Deals | `acc.positions_history(sort_type, open_from, open_to, page=0, size=PAGE_SIZE)` | Requests historical positions (and/or deals) and prints up to 50 items. |
    | Print | `_print_orders(...)`, `_print_positions(...)` | Friendly, compact lines with ticket, symbol, volume, price/time fields. Skips missing fields silently. |
    | Cleanup | `await shutdown(acc)` | Always close the session even on errors. |

    RPCs used (AccountHelper gRPC)
    ------------------------------
    - `AccountClient.OrderHistory(OrderHistoryRequest)` →
      - Supported field names (auto-detected): `input_from|inputFrom|from_|from`, `input_to|inputTo|to_|to`
      - Sort field (optional): `input_sort_mode|inputSortMode|sort_mode`
      - Pagination: `page_number|pageNumber`, `items_per_page|itemsPerPage`
    - `AccountClient.PositionsHistory(PositionsHistoryRequest)` →
      - Sort enum (optional): `AH_ENUM_POSITIONS_HISTORY_SORT_TYPE|AH_SORT_BY_OPEN_TIME_ASC`
      - Time range fields (auto-detected): `position_open_time_from|positionOpenTimeFrom|open_time_from|openFrom` and `..._to`
      - Pagination: `page_number|pageNumber`, `items_per_page|itemsPerPage`

    Portability helpers
    -------------------
    - `_enum_or(default, *path)` — resolves enum by path (e.g., `("BMT5_ENUM_ORDER_HISTORY_SORT_TYPE", "BMT5_SORT_BY_CLOSE_TIME_ASC")`) or falls back to `default`.
    - `_set_ts_any(msg, names, dt)` — finds a Timestamp field by any of the candidate names and calls `FromDatetime(UTC(dt))`.
    - `_set_any(msg, names, value)` — assigns to the first matching scalar field name.
    - `_safe_get(obj, *names, default=None)` — returns the first present attribute among candidates.
    - Time handling: `_utc(dt)` ensures everything is in UTC; `_fmt_ts(ts)` prints `YYYY-MM-DD HH:MM:SS` (UTC).

    Output fields (best-effort; optional fields are skipped)
    -------------------------------------------------------
    - Orders: `ticket|order_ticket`, `symbol`, `type|order_type`, `volume_initial|volume`, `price_open|price`,
      `time_setup|time_setup_msc`, `time_done|time_done_msc`.
    - Positions/Deals: `ticket|deal_ticket`, `symbol`, `volume`, `price_open|price`, `profit`,
      `open_time`, `close_time`.

    Pagination & limits
    -------------------
    - Page size comes from `HISTORY_PAGE_SIZE` (default 200).
    - Printers show up to 50 items per section to keep logs readable (rest is summarized).

    Environment knobs
    -----------------
    - `HISTORY_DAYS` (int, default `7`) — lookback window size.
    - `HISTORY_PAGE_SIZE` (int, default `200`) — page size for both queries.

    Timeouts & deadlines
    --------------------
    - If `deadline` is passed to the wrappers, a gRPC `timeout` is computed from it on the client side.
    - If your server has incorrect time/offset, prefer **client-side timeouts** (omit `deadline`) to avoid `DEADLINE_EXCEEDED`.

    Edge cases
    ----------
    - Different builds may rename fields; this example auto-detects snake_case/camelCase.
    - If the server envelopes payload in `data`, it is unwrapped.
    - Any missing pb2 fields/enums fall back gracefully; errors are caught and printed as `[...]: Error: <type>: <msg>`.

    How to run
    ----------
    From project root (module path):
      `python -m examples.<this_file_name_without_.py>`
    Examples:
      `python -m examples.history`  or  `python -m examples.orders_positions_history`
    (Use your actual filename under `examples/`.)

    Requirements
    ------------
    - Valid connection settings (`.env` / `connect()`).
    - `MetaRpcMT5.mt5_term_api_account_helper_pb2` must be importable in this build (already handled at module import).
    """