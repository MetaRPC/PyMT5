# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE app/compat/mt5_patch.py — Compatibility utilities for MT5Service builds ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose:                                                                     ║
║   Provide a thin, version-tolerant layer that hides MT5Service/pb2 diffs.    ║
║   Contains safe imports, enum fallbacks, and polyfilled helper APIs.         ║
║                                                                              ║
║ Exposes:                                                                     ║
║   • ORDER_MAP (BUY/SELL/LIMIT/STOP/STOP_LIMIT → int)                          ║
║   • Sorting constants: POSITION_SORT_*, ORDER_SORT_*, DEAL_SORT_*            ║
║   • Async helpers (build-agnostic):                                          ║
║       - order_calc_profit(svc, ...)                                          ║
║       - order_calc_margin(svc, ...)                                          ║
║       - market_book_get(svc, symbol)  # DOM/Order Book                        ║
║       - symbol_info_session_quote(svc, symbol, ...)                           ║
║                                                                              ║
║ Strategy (per helper):                                                       ║
║   1) Try the server RPC variant (different arg names/locations supported).   ║
║   2) If not available/0.0 → compute locally using symbol metadata.           ║
║   3) As a last resort → simple FX formulae with safe defaults.               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import asyncio
import logging
import importlib
from inspect import isawaitable

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# ───────────────────────── helpers ─────────────────────────
def _get_attr_safe(obj, *names):
    """Return the first present attribute from *names, or None."""
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return None

def _import_tf():
    """
    Try to import a module that contains order-type enums:
      1) Official pb2 (account_helper_pb2) if present in the build
      2) A user-supplied fallback module named `tf`
    """
    try:
        from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as mod
        return mod
    except Exception:
        pass
    try:
        return importlib.import_module("tf")
    except Exception:
        return None

_tf = _import_tf()

# ───────────────────── sorting (fallback constants) ─────────────────────
POSITION_SORT_OPEN_ASC  = 0
POSITION_SORT_OPEN_DESC = 1
POSITION_SORT_CLOSE_ASC = 2
POSITION_SORT_CLOSE_DESC= 3
ORDER_SORT_OPEN_ASC     = 4
ORDER_SORT_OPEN_DESC    = 5
ORDER_SORT_CLOSE_ASC    = 6
ORDER_SORT_CLOSE_DESC   = 7
ORDER_SORT_EXP_ASC      = 8
ORDER_SORT_EXP_DESC     = 9
DEAL_SORT_ASC           = 10
DEAL_SORT_DESC          = 11

# ───────────────────────── ORDER_MAP ─────────────────────────
# Prefer pb2 enum if available; otherwise use stable numeric fallbacks.
OrderType = _get_attr_safe(_tf, "OrderType", "ORDERTYPE", "OrderTypes") if _tf else None

def _or_default(name, default):
    """Fetch enum value `name` from OrderType if present; else `default`."""
    if OrderType is not None and hasattr(OrderType, name):
        return getattr(OrderType, name)
    return default

ORDER_MAP = {
    "BUY":            _or_default("ORDER_TYPE_BUY",            0),
    "SELL":           _or_default("ORDER_TYPE_SELL",           1),
    "BUY_LIMIT":      _or_default("ORDER_TYPE_BUY_LIMIT",      2),
    "SELL_LIMIT":     _or_default("ORDER_TYPE_SELL_LIMIT",     3),
    "BUY_STOP":       _or_default("ORDER_TYPE_BUY_STOP",       4),
    "SELL_STOP":      _or_default("ORDER_TYPE_SELL_STOP",      5),
    "BUY_STOP_LIMIT": _or_default("ORDER_TYPE_BUY_STOP_LIMIT", 6),
    "SELL_STOP_LIMIT":_or_default("ORDER_TYPE_SELL_STOP_LIMIT",7),
}

def _resolve_order_type(order_type):
    """Accept str/enum/int and return a normalized int order type."""
    if isinstance(order_type, int):
        return order_type
    if hasattr(order_type, "value"):
        try:
            return int(order_type.value)
        except Exception:
            pass
    if isinstance(order_type, str):
        key = order_type.strip().upper()
        if key in ORDER_MAP:
            return ORDER_MAP[key]
    return ORDER_MAP["BUY"]

def _is_awaitable(x):
    """True for coroutines/futures/awaitables (compatible check)."""
    return asyncio.iscoroutine(x) or isawaitable(x)

async def _first_ok_async(calls):
    """
    Try a sequence of callables (sync or async) and return the first successful
    result as (result, None). If all fail, return (None, last_exception).
    """
    last_err = None
    for fn in calls:
        if fn is None:
            continue
        try:
            res = fn()
            if _is_awaitable(res):
                res = await res
            return res, None
        except Exception as e:
            last_err = e
    return None, last_err

# ───────────── helpers that may call async service APIs ─────────────
async def _try_symbol_meta(svc, symbol):
    """
    Try to read contract_size / tick_size / tick_value using any of the
    commonly-seen method names and field spellings across builds.
    """
    try:
        si = None
        for nm in ("symbol_info", "get_symbol_info", "symbol_info_get"):
            fn = getattr(svc, nm, None)
            if callable(fn):
                si = fn(symbol)
                if _is_awaitable(si):
                    si = await si
                break
        if si is None:
            return {}

        def gx(obj, *keys):
            for k in keys:
                if isinstance(obj, dict) and k in obj:
                    return obj[k]
                if hasattr(obj, k):
                    return getattr(obj, k)
            return None

        return {
            "contract_size": gx(si, "TradeContractSize", "trade_contract_size", "ContractSize", "contract_size", "volume_min_lots"),
            "tick_size":     gx(si, "TradeTickSize", "trade_tick_size", "TickSize", "tick_size"),
            "tick_value":    gx(si, "TradeTickValue", "trade_tick_value", "TickValue", "tick_value"),
        }
    except Exception:
        return {}

async def _try_initial_margin_rate(svc, symbol):
    """
    Try to retrieve initial_margin_rate from several service methods/fields.
    Returns float or None.
    """
    try:
        m = None
        for name in ("symbol_info_margin_rate", "symbol_info_margin", "get_symbol_info_margin_rate"):
            fn = getattr(svc, name, None)
            if callable(fn):
                m = fn(symbol)
                if _is_awaitable(m):
                    m = await m
                break
        if not m:
            return None
        for k in ("initial_margin_rate", "InitialMarginRate", "margin_rate", "MarginRate", "rate"):
            if isinstance(m, dict) and k in m:
                return float(m[k])
            if hasattr(m, k):
                return float(getattr(m, k))
        return float(m)  # if the build already returns a plain number
    except Exception:
        return None

# ───────────────────────── public async APIs ─────────────────────────
async def order_calc_profit(svc, symbol, volume, order_type, **prices):
    """
    Build-agnostic profit calculator (account currency).
    Accepts any combination of: price_open, price_close, price (alias for open).
    Tries service variants first; if they fail or return 0.0 with prices given,
    falls back to local FX formula using contract_size.
    """
    otype = _resolve_order_type(order_type)
    price_open  = prices.get("price_open") or prices.get("open") or prices.get("price")
    price_close = prices.get("price_close") or prices.get("close")

    calls = []
    if price_open is not None and price_close is not None:
        calls += [
            lambda: svc.order_calc_profit(symbol, volume, otype, price_open,  price_close),
            lambda: svc.order_calc_profit(symbol=symbol, volume=volume, order_type=otype,
                                          price_open=price_open, price_close=price_close),
        ]
    if price_open is not None and price_close is None:
        calls += [
            lambda: svc.order_calc_profit(symbol, volume, otype, price_open),
            lambda: svc.order_calc_profit(symbol=symbol, volume=volume, order_type=otype, price_open=price_open),
        ]
    calls += [
        lambda: svc.order_calc_profit(symbol, volume, otype),
        lambda: svc.order_calc_profit(symbol=symbol, volume=volume, order_type=otype),
    ]

    res, err = await _first_ok_async(calls)
    if err is None:
        # Accept server result if non-zero OR if we don't have both prices.
        try:
            if price_open is None or price_close is None:
                return res
            if res is not None and float(res) != 0.0:
                return res
        except Exception:
            # If cannot cast to float, still return whatever the server gave us.
            if res is not None:
                return res

    # Local FX fallback (requires both prices)
    meta = await _try_symbol_meta(svc, symbol)
    contract_size = float(meta.get("contract_size") or 100000.0)
    if price_open is None or price_close is None:
        raise RuntimeError(
            f"order_calc_profit failed and local calc needs price_open/price_close; last server error: {err!r}"
        )
    sign = 1.0 if otype == ORDER_MAP["BUY"] else -1.0
    return (float(price_close) - float(price_open)) * contract_size * float(volume) * sign

async def order_calc_margin(
    svc, symbol, volume, order_type, price=None, leverage=None, initial_margin_rate=None
):
    """
    Build-agnostic margin calculator (account currency).
    Tries service variants first; if not available or returns 0.0/None,
    uses local approximation:
        margin ≈ price * lots * contract_size / leverage * initial_margin_rate
    """
    otype = _resolve_order_type(order_type)

    calls = []
    if price is not None:
        calls += [
            lambda: svc.order_calc_margin(symbol, volume, otype, price),
            lambda: svc.order_calc_margin(symbol=symbol, volume=volume, order_type=otype, price=price),
        ]
    calls += [
        lambda: svc.order_calc_margin(symbol, volume, otype),
        lambda: svc.order_calc_margin(symbol=symbol, volume=volume, order_type=otype),
    ]

    res, err = await _first_ok_async(calls)
    if err is None:
        # Accept non-zero server result; otherwise compute locally.
        try:
            if res is not None and float(res) != 0.0:
                return res
        except Exception:
            if res is not None:
                return res

    # Local approximation
    meta = await _try_symbol_meta(svc, symbol)
    contract_size = float(meta.get("contract_size") or 100000.0)

    if leverage is None:
        lev = None
        for nm in ("account_info", "get_account_info", "account"):
            fn = getattr(svc, nm, None)
            if callable(fn):
                acc = fn()
                if _is_awaitable(acc):
                    acc = await acc
                for k in ("leverage", "Leverage", "margin_leverage"):
                    if isinstance(acc, dict) and k in acc:
                        lev = acc[k]; break
                    if hasattr(acc, k):
                        lev = getattr(acc, k); break
                if lev:
                    break
        leverage = float(lev or 100.0)

    if initial_margin_rate is None:
        initial_margin_rate = await _try_initial_margin_rate(svc, symbol) or 1.0

    if price is None:
        for nm in ("symbol_info_tick", "symbol_tick", "symbol_price"):
            fn = getattr(svc, nm, None)
            if callable(fn):
                tick = fn(symbol)
                if _is_awaitable(tick):
                    tick = await tick
                for k in ("bid", "Bid", "ask", "Ask", "last", "Last"):
                    if isinstance(tick, dict) and k in tick:
                        price = float(tick[k]); break
                    if hasattr(tick, k):
                        price = float(getattr(tick, k)); break
                if price is not None:
                    break
        if price is None:
            price = 1.0  # safe placeholder

    return float(price) * float(volume) * contract_size / float(leverage) * float(initial_margin_rate)

# ───────────────────────── Market book (DOM) ─────────────────────────
async def market_book_get(svc, symbol: str):
    """
    Retrieve market depth (DOM). Try high-level service methods first; if absent,
    call the lower-level gRPC MarketInfo.MarketBookGet with auto-reconnect.
    """
    last_err = None

    # 1) High-level service helpers (sync/async)
    for nm in ("market_book_get", "book_get", "get_market_book"):
        fn = getattr(svc, nm, None)
        if not callable(fn):
            continue
        try:
            r = fn(symbol)
            if hasattr(r, "__await__"):
                r = await r
            return r
        except Exception as e:
            last_err = e

    # 2) Fallback via market_info_client (pb2 required)
    try:
        from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
    except Exception as e:
        raise RuntimeError(f"market_book_get failed: no pb2 ({e!r})") from e

    acc = getattr(svc, "acc", None)
    client = getattr(acc, "market_info_client", None)
    if client is None:
        raise RuntimeError(f"market_book_get failed: {last_err!r}")

    req = mi_pb2.MarketBookGetRequest(symbol=symbol)
    exec_fn = getattr(acc, "execute_with_reconnect", None)

    try:
        if callable(exec_fn):
            async def grpc_call(headers):
                return await client.MarketBookGet(req, metadata=headers, timeout=None)
            res = await exec_fn(grpc_call, lambda r: getattr(r, "error", None))
        else:
            headers = acc.get_headers() if hasattr(acc, "get_headers") else []
            res = await client.MarketBookGet(req, metadata=headers, timeout=None)
        return getattr(res, "data", res)
    except Exception as e:
        raise RuntimeError(f"market_book_get failed: {e!r}") from e

# ───────────────────── Quote session info (trading hours) ────────────────────
async def symbol_info_session_quote(svc, symbol, day_of_week=None, session_index=None):
    """
    Return quote-session info for `symbol`. Tries several API shapes:
      - svc.symbol_info_session_quote(symbol)
      - svc.symbol_info_session(symbol)
      - svc.symbol_info_session_quote(symbol, day_of_week, session_index) loop
    """
    calls = []
    if hasattr(svc, "symbol_info_session_quote"):
        calls.append(lambda: svc.symbol_info_session_quote(symbol))
    if hasattr(svc, "symbol_info_session"):
        calls.append(lambda: svc.symbol_info_session(symbol))

    if day_of_week is None:
        for dow in (0, 1, 2, 3, 4, 5, 6):
            calls.append(lambda dow=dow: svc.symbol_info_session_quote(symbol, dow, 0))
            calls.append(lambda dow=dow: svc.symbol_info_session_quote(symbol=symbol, day_of_week=dow, session_index=0))
    else:
        if session_index is None:
            session_index = 0
        calls += [
            lambda: svc.symbol_info_session_quote(symbol, day_of_week, session_index),
            lambda: svc.symbol_info_session_quote(symbol=symbol, day_of_week=day_of_week, session_index=session_index),
        ]

    res, err = await _first_ok_async(calls)
    if err is None:
        return res
    log.warning("symbol_info_session_quote: no API variant worked; continuing. Last error: %r", err)
    return None

__all__ = [
    "ORDER_MAP",
    "POSITION_SORT_OPEN_ASC", "POSITION_SORT_OPEN_DESC",
    "POSITION_SORT_CLOSE_ASC", "POSITION_SORT_CLOSE_DESC",
    "ORDER_SORT_OPEN_ASC", "ORDER_SORT_OPEN_DESC",
    "ORDER_SORT_CLOSE_ASC", "ORDER_SORT_CLOSE_DESC",
    "ORDER_SORT_EXP_ASC", "ORDER_SORT_EXP_DESC",
    "DEAL_SORT_ASC", "DEAL_SORT_DESC",
    "order_calc_profit", "order_calc_margin",
    "market_book_get", "symbol_info_session_quote",
]
