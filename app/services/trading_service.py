"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE app/trading_service.py — high-level trading API & MT5Service patch      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║ • Provide a unified, high-level trading surface on top of various builds     ║
║   (market & pending ops, order/position mgmt).                               ║
║ • Prefer native MT5Account helpers when available; otherwise delegate        ║
║   to TradingHelper.OrderSend.                                                ║
║                                                                              ║
║ Exposed methods (patched onto MT5Service)                                    ║
║ • Market:  buy_market, sell_market                                           ║
║ • Pending: place_buy_limit/sell_limit/buy_stop/sell_stop/stop_limit          ║
║ • Low-level universal sender: order_send_ex                                  ║
║ • Mgmt:   cancel_order, pending_modify, position_modify,                     ║
║           position_close, close_all_positions                                ║
║                                                                              ║
║ Behavior                                                                     ║
║ • Best-effort symbol pre-selection (symbol_select) before actions.           ║
║ • If acc has a direct helper (e.g., buy_market) → use it; else fallback      ║
║   to order_send_ex → TradingHelper.OrderSend.                                ║
║ • Optional preflight OrderCheck via TradeFunctions when present.             ║
║ • Field presence is probed safely for proto messages (set only if exists).   ║
║                                                                              ║
║ Safety                                                                       ║
║ • Read/write (trading) but resilient to missing features across builds.      ║
║ • No hard dependency on specific proto variants; gracefully degrades.        ║
║ • Timeouts are short and headers are passed if available.                    ║
║                                                                              ║
║ Deps (optional)                                                              ║
║ • mt5_term_api_trading_helper_pb2[_grpc]  — OrderSend / OrderModify / Close  ║
║ • mt5_term_api_trade_functions_pb2[_grpc] — OrderCheck / calc helpers        ║
║                                                                              ║
║ Registration                                                                 ║
║ • On import, methods are monkey-patched onto MT5Service (idempotent).        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import inspect
from typing import Any, Optional

# TradingHelper pb2/pb2_grpc (present in your build)
try:
    from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2  # type: ignore
    from MetaRpcMT5 import mt5_term_api_trading_helper_pb2_grpc as th_grpc  # type: ignore
except Exception:
    th_pb2 = None
    th_grpc = None

# TradeFunctions pb2 (for OrderCheck/Calc*)
try:
    from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf_pb2  # type: ignore
    from MetaRpcMT5 import mt5_term_api_trade_functions_pb2_grpc as tf_grpc  # type: ignore
except Exception:
    tf_pb2 = None
    tf_grpc = None


# ────────────────────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────────────────────

def _headers(acc) -> list[tuple[str, str]] | list:
    """Return metadata headers if the account exposes get_headers()."""
    return acc.get_headers() if hasattr(acc, "get_headers") else []

async def _ensure_symbol(acc, symbol: str) -> None:
    """Best-effort symbol pre-selection to reduce first-call latency."""
    fn = getattr(acc, "symbol_select", None)
    if callable(fn):
        try:
            res = fn(symbol, True)
            if inspect.iscoroutine(res):
                await res
        except Exception:
            pass

def _has(obj, name: str) -> bool:
    """Convenience callable check."""
    return callable(getattr(obj, name, None))

def _enum(pb_mod, name: str, default: int = 0) -> int:
    """Safely fetch enum value from a pb2 module (fallback to default)."""
    try:
        return int(getattr(pb_mod, name))
    except Exception:
        return default

def _set_if_has(obj, field: str, value) -> None:
    """Set a proto field only if present in this build (no exceptions)."""
    try:
        if hasattr(obj, field):
            setattr(obj, field, value)
    except Exception:
        pass

def _map_operation(side: str, order_type: Optional[str]) -> int:
    """
    Map high-level (BUY/SELL + MARKET/LIMIT/STOP/STOP_LIMIT) → TradingHelper enum.
    Defaults to MARKET flavor when unknown.
    """
    if th_pb2 is None:
        return 0
    s = (side or "BUY").upper()
    ot = (order_type or "MARKET").upper()

    if ot == "MARKET":
        return _enum(th_pb2, f"TMT5_ENUM_ORDER_TYPE_{'BUY' if s=='BUY' else 'SELL'}")
    if ot == "LIMIT":
        return _enum(th_pb2, f"TMT5_ENUM_ORDER_TYPE_{'BUY_LIMIT' if s=='BUY' else 'SELL_LIMIT'}")
    if ot == "STOP":
        return _enum(th_pb2, f"TMT5_ENUM_ORDER_TYPE_{'BUY_STOP' if s=='BUY' else 'SELL_STOP'}")
    if ot in ("STOP_LIMIT", "STOPLIMIT", "STOP-LIMIT"):
        return _enum(th_pb2, f"TMT5_ENUM_ORDER_TYPE_{'BUY_STOP_LIMIT' if s=='BUY' else 'SELL_STOP_LIMIT'}")
    return _enum(th_pb2, f"TMT5_ENUM_ORDER_TYPE_{'BUY' if s=='BUY' else 'SELL'}")


async def _find_position_ticket_by_symbol(self, symbol: str) -> int | None:
    """
    Resolve a position ticket by symbol via opened_snapshot() as a fallback
    for builds without a direct position_close(symbol=...) helper.
    """
    try:
        snap = await self.opened_snapshot()
        for p in snap.get("positions", []):
            if str(p.get("symbol", "")).upper() == symbol.upper():
                t = p.get("ticket")
                return int(t) if t is not None else None
    except Exception:
        pass
    return None


# ────────────────────────────────────────────────────────────────────────────
# HIGH-LEVEL: MARKET
# ────────────────────────────────────────────────────────────────────────────

async def buy_market(self, symbol: str, volume: float,
                     sl: float | None = None, tp: float | None = None, **opts) -> Any:
    """
    BUY at market. Prefer acc.buy_market/market_buy/buy → else fallback to order_send_ex.
    """
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")
    await _ensure_symbol(acc, symbol)

    # Prefer account-level helper if present (with permissive signature handling)
    for cand in ("buy_market", "market_buy", "buy"):
        fn = getattr(acc, cand, None)
        if callable(fn):
            try:
                sig = inspect.signature(fn)
                res = fn(symbol, volume, **({"sl": sl, "tp": tp} if {"sl","tp"} <= set(sig.parameters) else {}))
                return await res if inspect.iscoroutine(res) else res
            except Exception:
                pass

    # Fallback: universal sender
    return await order_send_ex(self, action="MARKET", side="BUY",
                               symbol=symbol, volume=volume, sl=sl, tp=tp, **opts)

async def sell_market(self, symbol: str, volume: float,
                      sl: float | None = None, tp: float | None = None, **opts) -> Any:
    """
    SELL at market. Prefer acc.sell_market/market_sell/sell → else fallback to order_send_ex.
    """
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")
    await _ensure_symbol(acc, symbol)
    for cand in ("sell_market", "market_sell", "sell"):
        fn = getattr(acc, cand, None)
        if callable(fn):
            try:
                sig = inspect.signature(fn)
                res = fn(symbol, volume, **({"sl": sl, "tp": tp} if {"sl","tp"} <= set(sig.parameters) else {}))
                return await res if inspect.iscoroutine(res) else res
            except Exception:
                pass
    return await order_send_ex(self, action="MARKET", side="SELL",
                               symbol=symbol, volume=volume, sl=sl, tp=tp, **opts)


# ────────────────────────────────────────────────────────────────────────────
# UNIVERSAL SENDER → TradingHelper.OrderSend
# ────────────────────────────────────────────────────────────────────────────

async def order_send_ex(
    self,
    *,
    action: str,             # "MARKET" | "PENDING"
    side: str,               # "BUY" | "SELL"
    symbol: str,
    volume: float,
    price: float | None = None,
    sl: float | None = None,
    tp: float | None = None,
    expiration: int | None = None,     # unix sec
    order_type: str | None = None,     # "MARKET"|"LIMIT"|"STOP"|"STOP_LIMIT"
    # fine options:
    filling: str | None = None,        # "FOK"|"IOC"|"RETURN"
    deviation_points: int | None = None,
    comment: str | None = None,
    magic: int | None = None,
    **extra
) -> Any:
    """
    Build-agnostic sender. If MT5Account exposes its own order_send_ex → use it.
    Otherwise build TradingHelper.OrderSend request. Best-effort OrderCheck first.
    """
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")
    await _ensure_symbol(acc, symbol)

    # 1) Delegate to MT5Account.order_send_ex if available (passes only non-None args)
    fn = getattr(acc, "order_send_ex", None)
    if callable(fn):
        kw = dict(action=action, side=side, symbol=symbol, volume=volume,
                  price=price, sl=sl, tp=tp, expiration=expiration,
                  order_type=order_type, filling=filling,
                  deviation_points=deviation_points, comment=comment, magic=magic)
        kw = {k: v for k, v in kw.items() if v is not None}  # strip Nones
        kw.update(extra)
        res = fn(**kw)
        return await res if inspect.iscoroutine(res) else res

    # 2) Pure helper path
    if th_pb2 is None or not getattr(acc, "trade_client", None):
        raise RuntimeError("order_send_ex is not available in this build")

    operation = _map_operation(side, order_type)
    req = th_pb2.OrderSendRequest(symbol=symbol, volume=float(volume), operation=operation)
    # optional fields guarded (vary across builds)
    _set_if_has(req, "price", float(price) if price is not None else None)
    _set_if_has(req, "sl",    float(sl)    if sl    is not None else None)
    _set_if_has(req, "tp",    float(tp)    if tp    is not None else None)
    if expiration is not None:
        _set_if_has(req, "expiration_time", int(expiration))
        # different time enums across builds
        if hasattr(th_pb2, "TMT5_ENUM_ORDER_TYPE_TIMEH"):
            _set_if_has(req, "expiration_time_type", getattr(th_pb2, "TMT5_ENUM_ORDER_TYPE_TIMEH"))
        elif hasattr(th_pb2, "TMT5_ORDER_TIME_GTC"):
            _set_if_has(req, "type_time", getattr(th_pb2, "TMT5_ORDER_TIME_GTC"))

    if filling:
        f = filling.upper()
        if hasattr(th_pb2, f"TMT5_ORDER_FILLING_{f}"):
            _set_if_has(req, "type_filling", getattr(th_pb2, f"TMT5_ORDER_FILLING_{f}"))

    if deviation_points is not None:
        _set_if_has(req, "deviation", int(deviation_points))
    if comment is not None:
        _set_if_has(req, "comment", str(comment))
    if magic is not None:
        _set_if_has(req, "magic", int(magic))

    # arbitrary extras (set only when present)
    for k, v in extra.items():
        _set_if_has(req, k, v)

    # Optional preflight: TradeFunctions.OrderCheck (best-effort)
    if tf_pb2 and getattr(acc, "trade_functions_client", None) and hasattr(tf_pb2, "OrderCheckRequest"):
        try:
            chk = tf_pb2.OrderCheckRequest(symbol=symbol, volume=float(volume), operation=operation)
            _set_if_has(chk, "price", float(price) if price is not None else None)
            _set_if_has(chk, "sl",    float(sl)    if sl    is not None else None)
            _set_if_has(chk, "tp",    float(tp)    if tp    is not None else None)
            await acc.trade_functions_client.OrderCheck(chk, metadata=_headers(acc), timeout=5.0)
        except Exception:
            pass  # preflight is advisory

    return await acc.trade_client.OrderSend(req, metadata=_headers(acc), timeout=7.0)


# ────────────────────────────────────────────────────────────────────────────
# PENDING
# ────────────────────────────────────────────────────────────────────────────

async def place_buy_limit(self, symbol: str, volume: float, price: float,
                          sl: float | None = None, tp: float | None = None,
                          expiration: int | None = None, **opts) -> Any:
    """BUY LIMIT wrapper → order_send_ex(action=PENDING, order_type=LIMIT)."""
    return await order_send_ex(self, action="PENDING", side="BUY", symbol=symbol, volume=volume,
                               price=price, sl=sl, tp=tp, expiration=expiration, order_type="LIMIT", **opts)

async def place_sell_limit(self, symbol: str, volume: float, price: float,
                           sl: float | None = None, tp: float | None = None,
                           expiration: int | None = None, **opts) -> Any:
    """SELL LIMIT wrapper → order_send_ex(action=PENDING, order_type=LIMIT)."""
    return await order_send_ex(self, action="PENDING", side="SELL", symbol=symbol, volume=volume,
                               price=price, sl=sl, tp=tp, expiration=expiration, order_type="LIMIT", **opts)

async def place_buy_stop(self, symbol: str, volume: float, price: float,
                         sl: float | None = None, tp: float | None = None,
                         expiration: int | None = None, **opts) -> Any:
    """BUY STOP wrapper → order_send_ex(action=PENDING, order_type=STOP)."""
    return await order_send_ex(self, action="PENDING", side="BUY", symbol=symbol, volume=volume,
                               price=price, sl=sl, tp=tp, expiration=expiration, order_type="STOP", **opts)

async def place_sell_stop(self, symbol: str, volume: float, price: float,
                          sl: float | None = None, tp: float | None = None,
                          expiration: int | None = None, **opts) -> Any:
    """SELL STOP wrapper → order_send_ex(action=PENDING, order_type=STOP)."""
    return await order_send_ex(self, action="PENDING", side="SELL", symbol=symbol, volume=volume,
                               price=price, sl=sl, tp=tp, expiration=expiration, order_type="STOP", **opts)

async def place_stop_limit(self, symbol: str, is_buy: bool, volume: float,
                           stop_price: float, limit_price: float,
                           sl: float | None = None, tp: float | None = None,
                           expiration: int | None = None, **opts) -> Any:
    """
    STOP-LIMIT wrapper. TradingHelper uses limit_price as the 'price' field;
    stop_price is attached as an extra field only if the proto supports it.
    """
    side = "BUY" if is_buy else "SELL"
    return await order_send_ex(self, action="PENDING", side=side, symbol=symbol, volume=volume,
                               price=limit_price, sl=sl, tp=tp, expiration=expiration,
                               order_type="STOP_LIMIT", stop_price=stop_price, **opts)


# ────────────────────────────────────────────────────────────────────────────
# ORDER / POSITION MANAGEMENT
# ────────────────────────────────────────────────────────────────────────────

async def cancel_order(self, ticket: int) -> Any:
    """
    Cancel pending (or close by ticket where helper supports it).
    Prefer acc.cancel_order/order_delete/pending_delete → else TradingHelper.OrderClose.
    """
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")

    for cand in ("cancel_order", "order_delete", "pending_delete"):
        fn = getattr(acc, cand, None)
        if callable(fn):
            res = fn(ticket=ticket) if "ticket" in inspect.signature(fn).parameters else fn(ticket)
            return await res if inspect.iscoroutine(res) else res

    if th_pb2 and getattr(acc, "trade_client", None):
        req = th_pb2.OrderCloseRequest(ticket=int(ticket))
        return await acc.trade_client.OrderClose(req, metadata=_headers(acc), timeout=5.0)

    raise RuntimeError("cancel_order is not available in this build")

async def pending_modify(self, ticket: int, *,
                         price: float | None = None,
                         sl: float | None = None,
                         tp: float | None = None,
                         expiration: int | None = None) -> Any:
    """
    Modify a pending order. Prefer acc.pending_modify/order_modify → else TradingHelper.OrderModify.
    """
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")

    for cand in ("pending_modify", "order_modify"):
        fn = getattr(acc, cand, None)
        if callable(fn):
            kw = {"ticket": ticket}
            if price is not None:      kw["price"] = price
            if sl is not None:         kw["sl"] = sl
            if tp is not None:         kw["tp"] = tp
            if expiration is not None: kw["expiration"] = expiration
            res = fn(**kw)
            return await res if inspect.iscoroutine(res) else res

    if th_pb2 and getattr(acc, "trade_client", None):
        req = th_pb2.OrderModifyRequest(ticket=int(ticket))
        _set_if_has(req, "price", float(price) if price is not None else None)
        _set_if_has(req, "sl",    float(sl)    if sl    is not None else None)
        _set_if_has(req, "tp",    float(tp)    if tp    is not None else None)
        _set_if_has(req, "expiration_time", int(expiration) if expiration is not None else None)
        return await acc.trade_client.OrderModify(req, metadata=_headers(acc), timeout=5.0)

    raise RuntimeError("pending_modify is not available in this build")

async def position_modify(self, ticket: int, *, sl: float | None = None, tp: float | None = None) -> Any:
    """
    Modify an open position SL/TP. Prefer acc.position_modify/modify_position/position_set_sl_tp.
    Else use TradingHelper.OrderModify(ticket).
    """
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")

    for cand in ("position_modify", "modify_position", "position_set_sl_tp"):
        fn = getattr(acc, cand, None)
        if callable(fn):
            sig = inspect.signature(fn)
            if {"ticket", "sl", "tp"} <= set(sig.parameters.keys()):
                res = fn(ticket=ticket, sl=sl, tp=tp)
            else:
                try:
                    res = fn(ticket, sl, tp)
                except TypeError:
                    res = fn(ticket=ticket, sl=sl, tp=tp)
            return await res if inspect.iscoroutine(res) else res

    if th_pb2 and getattr(acc, "trade_client", None):
        req = th_pb2.OrderModifyRequest(ticket=int(ticket))
        _set_if_has(req, "sl", float(sl) if sl is not None else None)
        _set_if_has(req, "tp", float(tp) if tp is not None else None)
        return await acc.trade_client.OrderModify(req, metadata=_headers(acc), timeout=5.0)

    raise RuntimeError("position_modify is not available in this build")

async def position_close(self, ticket: Optional[int] = None,
                         symbol: Optional[str] = None,
                         volume: Optional[float] = None) -> Any:
    """
    Close a position. Prefer acc.position_close (ticket/symbol aware).
    Else use TradingHelper.OrderClose with resolved ticket (by symbol if needed).
    """
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")

    fn = getattr(acc, "position_close", None)
    if callable(fn):
        try:
            sig = inspect.signature(fn)
            if "ticket" in sig.parameters and ticket is not None:
                res = fn(ticket=ticket)
            elif "symbol" in sig.parameters and symbol:
                res = fn(symbol=symbol, volume=volume) if "volume" in sig.parameters else fn(symbol=symbol)
            else:
                # fallback: try to fetch object and pass it in
                if ticket is None and symbol:
                    getter = getattr(acc, "positions", None) or getattr(acc, "positions_get", None)
                    if callable(getter):
                        items = getter()
                        items = await items if inspect.iscoroutine(items) else items
                        for p in items or []:
                            if getattr(p, "symbol", "").upper() == symbol.upper():
                                res = fn(p); return await res if inspect.iscoroutine(res) else res
                res = fn()
            return await res if inspect.iscoroutine(res) else res
        except Exception:
            pass

    # Fallback via helper requires a ticket
    if ticket is None and symbol:
        ticket = await _find_position_ticket_by_symbol(self, symbol)

    if ticket is not None and th_pb2 and getattr(acc, "trade_client", None):
        req = th_pb2.OrderCloseRequest(ticket=int(ticket))
        return await acc.trade_client.OrderClose(req, metadata=_headers(acc), timeout=5.0)

    raise RuntimeError("position_close is not available in this build")

async def close_all_positions(self, *, symbol: Optional[str] = None) -> dict:
    """
    Close all (or symbol-filtered) positions. Prefer acc.close_all_positions when present.
    Else enumerate positions and close one by one.
    """
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")

    fn = getattr(acc, "close_all_positions", None)
    if callable(fn):
        res = fn(symbol=symbol) if "symbol" in inspect.signature(fn).parameters else fn()
        return await res if inspect.iscoroutine(res) else res

    getter = getattr(acc, "positions", None) or getattr(acc, "positions_get", None)
    if not callable(getter):
        raise RuntimeError("no way to enumerate positions in this build")

    items = getter()
    items = await items if inspect.iscoroutine(items) else items
    attempted = 0
    errors: list[str] = []
    for p in items or []:
        if symbol and getattr(p, "symbol", "").upper() != symbol.upper():
            continue
        attempted += 1
        try:
            await position_close(self, ticket=getattr(p, "ticket", None))
        except Exception as e:
            errors.append(str(e))
    return {"attempted": attempted, "closed": attempted - len(errors), "errors": errors}


# ────────────────────────────────────────────────────────────────────────────
# REGISTRATION
# ────────────────────────────────────────────────────────────────────────────
try:
    from app.core.mt5_service import MT5Service  # type: ignore
except Exception:
    MT5Service = None

if MT5Service:
    patch = {
        "buy_market": buy_market,
        "sell_market": sell_market,
        "order_send_ex": order_send_ex,
        "place_buy_limit": place_buy_limit,
        "place_sell_limit": place_sell_limit,
        "place_buy_stop": place_buy_stop,
        "place_sell_stop": place_sell_stop,
        "place_stop_limit": place_stop_limit,
        "cancel_order": cancel_order,
        "pending_modify": pending_modify,
        "position_modify": position_modify,
        "position_close": position_close,
        "close_all_positions": close_all_positions,
    }
    for k, v in patch.items():
        setattr(MT5Service, k, v)
