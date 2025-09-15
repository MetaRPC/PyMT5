"""
╔══════════════════════════════════════════════════════════════════╗
║ app/history_service.py — unified history helpers & MT5 patches   ║
╠══════════════════════════════════════════════════════════════════╣
║ Purpose  One API over pb2 variants for orders/positions history. ║
║ Exports  (bound onto MT5Service):                                ║
║          order_history, positions_history, orders_history,       ║
║          history_order_by_ticket, history_deal_by_ticket,        ║
║          history_deals_get, history_deals_total, opened_orders.  ║
║ Behavior Tries snake/camel fields, enum fallbacks, pagination.   ║
║ Safety   Read-only, ~5s gRPC timeouts, tolerant to missing pb2.  ║
╚══════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import asyncio
from typing import Any, Optional, Iterable, List
from datetime import datetime, timezone, timedelta

# Proto & exceptions (soft stubs if SDK is missing)
try:
    import MetaRpcMT5.mt5_term_api_account_helper_pb2 as ah_pb2  # type: ignore
    from MetaRpcMT5 import ConnectExceptionMT5  # type: ignore
except Exception:
    ah_pb2 = None
    class ConnectExceptionMT5(RuntimeError):  # soft fallback
        pass


# ───────────────────────────── helpers ─────────────────────────────

def _to_dt(x: datetime | int | float | None) -> datetime:
    """Normalize user input (datetime/epoch/None) to aware-UTC datetime."""
    if x is None:
        return datetime.now(timezone.utc)
    if isinstance(x, datetime):
        return x if x.tzinfo else x.replace(tzinfo=timezone.utc)
    return datetime.fromtimestamp(int(x), tz=timezone.utc)

def _ts(x: datetime | int | float | None) -> int:
    """UTC epoch seconds from any supported time input."""
    return int(_to_dt(x).timestamp())

def _oh_default_sort() -> int:
    """Safe default sort_mode for OrderHistory; falls back to 1 if enum absent."""
    if ah_pb2 and hasattr(ah_pb2, "BMT5_ENUM_ORDER_HISTORY_SORT_TYPE"):
        E = ah_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE
        for cand in ("BMT5_SORT_BY_CLOSE_TIME_ASC", "BMT5_SORT_BY_CLOSE_TIME", "BMT5_SORT_NONE"):
            if hasattr(E, cand):
                return int(getattr(E, cand))
    return 1

def _first_container(page: Any) -> Optional[Iterable]:
    """Return the first iterable container with records inside a page-like object."""
    if page is None:
        return None
    for name in ("items", "orders", "positions", "deals", "records"):
        arr = getattr(page, name, None)
        if isinstance(arr, (list, tuple)):
            return arr
    return None

def _first_container_len(page: Any) -> Optional[int]:
    arr = _first_container(page)
    return len(arr) if arr is not None else None

def _extract_history_items(page: Any) -> List[Any]:
    """Materialize list of items from a page; empty list if absent."""
    arr = _first_container(page)
    return list(arr) if arr is not None else []

def _iter_history_items(page: Any):
    """Iterator over items in a page; no raise if nothing inside."""
    arr = _first_container(page)
    if arr:
        for it in arr:
            yield it

def _find_any_by_ticket(page: Any, ticket: int) -> Optional[Any]:
    """Search record by ticket across common ticket-like fields."""
    for it in _iter_history_items(page):
        for fld in ("ticket", "order", "order_ticket", "id", "position"):
            v = getattr(it, fld, None)
            if v is not None and int(v) == int(ticket):
                return it
    return None

def _dir_from(item: Any) -> Optional[str]:
    """Infer BUY/SELL from typical direction fields (best-effort)."""
    for name in ("type", "order_type", "deal_type", "action", "side"):
        v = getattr(item, name, None)
        if v is None:
            continue
        s = str(v).upper()
        if "BUY" in s:
            return "BUY"
        if "SELL" in s:
            return "SELL"
    return None

def _is_deal_like(_: Any) -> bool:
    """Placeholder: accepts any record as 'deal-like' (customize if needed)."""
    return True


# ───────────────────── low-level history methods ─────────────────────
# Note: exposed as MT5Service instance methods (not svc.acc.*)

async def order_history(
    self,
    *,
    from_dt: datetime | int | None,
    to_dt: datetime | int | None,
    sort_mode: Optional[int] = None,
    page_number: int = 0,
    items_per_page: int = 50,
) -> Any:
    """Unified order history call (returns proto page or None)."""
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")

    client = getattr(acc, "account_helper_client", None) or getattr(acc, "account_client", None)
    if client is None or ah_pb2 is None:
        return None

    f = _ts(from_dt)
    t = _ts(to_dt)
    sort_val = sort_mode if sort_mode is not None else _oh_default_sort()
    headers = getattr(acc, "get_headers", lambda: [])()

    # snake_case
    try:
        req = ah_pb2.OrderHistoryRequest(
            from_time=f, to_time=t,
            sort_mode=sort_val,
            page_number=page_number, items_per_page=items_per_page,
        )
        return await client.OrderHistory(req, metadata=headers, timeout=5.0)
    except Exception:
        pass
    # camelCase
    try:
        req = ah_pb2.OrderHistoryRequest(
            fromTime=f, toTime=t,
            sortMode=sort_val,
            pageNumber=page_number, itemsPerPage=items_per_page,
        )
        return await client.OrderHistory(req, metadata=headers, timeout=5.0)
    except Exception:
        pass
    # alternative field set
    try:
        req = ah_pb2.OrderHistoryRequest(
            time_from=f, time_to=t,
            sort=sort_val,
            page=page_number, size=items_per_page,
        )
        return await client.OrderHistory(req, metadata=headers, timeout=5.0)
    except Exception:
        return None

async def history_deals_total(
    self,
    from_dt: datetime | int,
    to_dt: datetime | int,
    *,
    page_size: int = 500,
    max_pages: int = 100,
) -> Optional[int]:
    """
    Count 'deal-like' records in the interval.
    Returns int or None when history API is unavailable in the build.
    """
    if not getattr(self, "acc", None):
        raise RuntimeError("Not connected")

    f = _to_dt(from_dt)
    t = _to_dt(to_dt)
    sort = _oh_default_sort()

    total = 0
    any_pages = False

    for page_num in range(max_pages):
        page = await order_history(
            self,
            from_dt=f,
            to_dt=t,
            sort_mode=sort,
            page_number=page_num,
            items_per_page=page_size,
        )
        if page is None:
            break

        any_pages = True
        for _ in _iter_history_items(page):
            if _is_deal_like(_):
                total += 1

        n = _first_container_len(page)
        if n is None or n < page_size:
            break

    return total if any_pages else None



async def positions_history(
    self,
    *,
    sort_type: Optional[int] = None,
    open_from: datetime | int | None = None,
    open_to: datetime | int | None = None,
    page: int = 0,
    size: int = 50,
) -> Any:
    """Unified positions history call (handles enum/field variants)."""
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")

    client = getattr(acc, "account_helper_client", None) or getattr(acc, "account_client", None)
    if client is None or ah_pb2 is None:
        return None

    f = _ts(open_from)
    t = _ts(open_to)

    if sort_type is None and hasattr(ah_pb2, "AH_ENUM_POSITIONS_HISTORY_SORT_TYPE"):
        E = ah_pb2.AH_ENUM_POSITIONS_HISTORY_SORT_TYPE
        for cand in ("AH_SORT_BY_OPEN_TIME_ASC", "AH_SORT_BY_OPEN_TIME", "AH_SORT_NONE"):
            if hasattr(E, cand):
                sort_type = int(getattr(E, cand))
                break
    if sort_type is None:
        sort_type = 0

    headers = getattr(acc, "get_headers", lambda: [])()

    # snake_case
    try:
        req = ah_pb2.PositionsHistoryRequest(
            sort_type=sort_type,
            open_from=f, open_to=t,
            page=page, size=size,
        )
        return await client.PositionsHistory(req, metadata=headers, timeout=5.0)
    except Exception:
        pass
    # camelCase
    try:
        req = ah_pb2.PositionsHistoryRequest(
            sortType=sort_type,
            openFrom=f, openTo=t,
            pageNumber=page, itemsPerPage=size,
        )
        return await client.PositionsHistory(req, metadata=headers, timeout=5.0)
    except Exception:
        return None


# ───────────────────── convenience wrappers over history ─────────────────────

async def orders_history(
    self,
    *,
    from_dt: datetime | int | None = None,
    to_dt: datetime | int | None = None,
    days_back: int = 7,
    page: int = 0,
    size: int = 800,
    sort_mode: Optional[int] = None,
    fetch_all: bool = False,
    return_raw: bool = False,
) -> Any:
    """
    Orders history.
    - return_raw=False → flat list of items (with pagination if fetch_all=True)
    - return_raw=True  → page object(s)
    """
    if not getattr(self, "acc", None):
        raise RuntimeError("Not connected")

    to_dt_ = _to_dt(to_dt)
    from_dt_ = _to_dt(from_dt) if from_dt is not None else (to_dt_ - timedelta(days=days_back))
    sort = sort_mode if sort_mode is not None else _oh_default_sort()

    raw_pages: List[Any] = []
    flat_items: List[Any] = []
    p = int(page)

    while True:
        reply = await order_history(
            self,
            from_dt=from_dt_,
            to_dt=to_dt_,
            sort_mode=sort,
            page_number=p,
            items_per_page=size,
        )
        if reply is None:
            break

        if return_raw:
            raw_pages.append(reply)
        else:
            flat_items.extend(_extract_history_items(reply))

        if not fetch_all:
            break

        n = len(_extract_history_items(reply))
        if n < size or n == 0:
            break
        p += 1

    return raw_pages[0] if (return_raw and not fetch_all) else (raw_pages if return_raw else flat_items)


async def history_order_by_ticket(
    self,
    ticket: int,
    *,
    days_back: int = 30,
    items_per_page: int = 800,
) -> Optional[Any]:
    """Find a record by ticket: search opened snapshot, then first history page."""
    if not getattr(self, "acc", None):
        raise RuntimeError("Not connected")

    # Search among currently opened
    try:
        snap_fn = getattr(self, "opened_orders", None)
        if callable(snap_fn):
            snap = await snap_fn()
            for name in ("orders", "pending", "opened_orders", "positions"):
                arr = getattr(snap, name, None)
                if isinstance(arr, (list, tuple)):
                    for item in arr:
                        for fld in ("ticket", "order", "order_ticket", "id"):
                            v = getattr(item, fld, None)
                            if v is not None and int(v) == int(ticket):
                                return item
        else:
            snapd = await self.opened_snapshot()
            for arr in (snapd.get("positions", []), snapd.get("pending", [])):
                for item in arr:
                    v = item.get("ticket")
                    if v is not None and int(v) == int(ticket):
                        return item
    except Exception:
        pass

    # One page of history (fallback)
    to_dt_ = datetime.now(timezone.utc)
    from_dt_ = to_dt_ - timedelta(days=days_back)
    page = await order_history(
        self,
        from_dt=from_dt_,
        to_dt=to_dt_,
        page_number=0,
        items_per_page=items_per_page,
    )
    for it in _extract_history_items(page):
        for fld in ("ticket", "order", "order_ticket", "id"):
            v = getattr(it, fld, None)
            if v is not None and int(v) == int(ticket):
                return it
    return None


async def history_deal_by_ticket(
    self,
    ticket: int,
    *,
    days_back: int = 30,
    page_size: int = 500,
    max_pages: int = 40,
) -> Optional[Any]:
    """Scan multiple pages to find a 'deal-like' record by ticket."""
    if not getattr(self, "acc", None):
        raise RuntimeError("Not connected")

    to_dt_ = datetime.now(timezone.utc)
    from_dt_ = to_dt_ - timedelta(days=days_back)
    sort = _oh_default_sort()

    for page_num in range(max_pages):
        page = await order_history(
            self,
            from_dt=from_dt_,
            to_dt=to_dt_,
            sort_mode=sort,
            page_number=page_num,
            items_per_page=page_size,
        )
        if page is None:
            break
        found = _find_any_by_ticket(page, ticket)
        if found is not None:
            return found
        n = _first_container_len(page)
        if n is None or n < page_size:
            break
    return None


async def history_deals_get(
    self,
    from_dt: datetime | int,
    to_dt: datetime | int,
    *,
    symbol: str | None = None,
    direction: str | None = None,  # 'BUY'/'SELL'
    magic: int | None = None,
    limit: int | None = None,
    page_size: int = 500,
    max_pages: int = 100,
) -> List[Any]:
    """Return 'deal-like' records in interval with optional filters."""
    if not getattr(self, "acc", None):
        raise RuntimeError("Not connected")

    f = _to_dt(from_dt)
    t = _to_dt(to_dt)
    want_sym = symbol.upper() if symbol else None
    want_dir = direction.upper() if direction else None
    sort = _oh_default_sort()

    out: List[Any] = []
    for page_num in range(max_pages):
        page = await order_history(
            self,
            from_dt=f,
            to_dt=t,
            sort_mode=sort,
            page_number=page_num,
            items_per_page=page_size,
        )
        if page is None:
            break

        for item in _iter_history_items(page):
            if not _is_deal_like(item):
                continue
            if want_sym:
                sym = (getattr(item, "symbol", "") or getattr(item, "symbol_name", "")).upper()
                if sym != want_sym:
                    continue
            if magic is not None:
                mg = getattr(item, "magic", getattr(item, "magic_number", None))
                if mg is None or int(mg) != int(magic):
                    continue
            if want_dir:
                side = _dir_from(item)
                if side and side != want_dir:
                    continue
            out.append(item)
            if limit is not None and len(out) >= limit:
                return out

        n = _first_container_len(page)
        if n is None or n < page_size:
            break

    return out


async def opened_orders(
    self,
    *,
    sort_mode: int | None = 0,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
):
    """
    OpenedOrders via AccountHelper (bypasses package-level self.account_client.OpenedOrders).
    Returns proto reply (or .data if the build wraps it).
    """
    if not getattr(self, "id", None):
        raise ConnectExceptionMT5("Please call connect method first")
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")
    if ah_pb2 is None or not getattr(acc, "account_helper_client", None):
        raise RuntimeError("AccountHelper client not available in this build")

    # Request with tolerant field naming
    try:
        req = ah_pb2.OpenedOrdersRequest(inputSortMode=int(sort_mode or 0))
    except Exception:
        req = ah_pb2.OpenedOrdersRequest()
        try:
            setattr(req, "sortMode", int(sort_mode or 0))
        except Exception:
            pass

    headers = acc.get_headers() if hasattr(acc, "get_headers") else []
    timeout = None
    if deadline is not None:
        try:
            timeout = max((deadline - datetime.now(timezone.utc)).total_seconds(), 0.0)
        except Exception:
            timeout = None

    async def _call():
        return await acc.account_helper_client.OpenedOrders(
            req, metadata=headers, timeout=timeout
        )

    if cancellation_event is None:
        res = await _call()
    else:
        t_call = asyncio.create_task(_call())
        t_cancel = asyncio.create_task(cancellation_event.wait())
        done, pending = await asyncio.wait({t_call, t_cancel}, return_when=asyncio.FIRST_COMPLETED)
        for t in pending:
            t.cancel()
        if t_call in done:
            res = await t_call
        else:
            raise asyncio.CancelledError("opened_orders cancelled")

    return getattr(res, "data", res)


# --- bind helpers onto MT5Service ---
def _register_history_patches() -> None:
    """Monkey-patch all exported helpers onto MT5Service."""
    try:
        from app.core.mt5_service import MT5Service  # type: ignore
    except Exception:
        return

    to_patch = {
        "order_history":           globals().get("order_history"),
        "positions_history":       globals().get("positions_history"),
        "orders_history":          globals().get("orders_history"),
        "history_order_by_ticket": globals().get("history_order_by_ticket"),
        "history_deal_by_ticket":  globals().get("history_deal_by_ticket"),
        "history_deals_get":       globals().get("history_deals_get"),
        "history_deals_total":     globals().get("history_deals_total"),
        "opened_orders":           globals().get("opened_orders"),
    }
    for name, fn in to_patch.items():
        if callable(fn):
            setattr(MT5Service, name, fn)

_register_history_patches()
