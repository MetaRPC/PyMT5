"""
╔════════════════════════════════════════════════════════════════╗
║ FILE app/market_info_patch.py                                  ║
╠════════════════════════════════════════════════════════════════╣
║ Purpose: Attach market-info helpers to MT5Service that work    ║
║          across different pb2 layouts/names.                   ║
║ Adds:   MT5Service.tick_value_with_size(symbol, volume=None)   ║
║         MT5Service.symbol_info_margin_rate(symbol, order_type) ║
║ Notes:  Best-effort: try modern gRPC → older SDK fallbacks.    ║
╚════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations
from types import SimpleNamespace as _NS
from typing import Any, Optional

# Try to import pb2 modules (names differ across builds).
try:
    from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as account_helper_pb2  # type: ignore
except Exception:
    try:
        import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2  # type: ignore
    except Exception:
        account_helper_pb2 = None  # type: ignore

try:
    from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2  # type: ignore
except Exception:
    try:
        import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2  # type: ignore
    except Exception:
        market_info_pb2 = None  # type: ignore


def _unbox_num(v: Any) -> Optional[float]:
    """Return float from various numeric wrappers/fields, else None."""
    try:
        if hasattr(v, "value"):
            v = getattr(v, "value")
        return None if v is None else float(v)
    except Exception:
        pass
    for k in ("double", "number", "val", "Value"):
        try:
            if hasattr(v, k):
                return float(getattr(v, k))
        except Exception:
            pass
    try:
        return float(v) if isinstance(v, (int, float, str)) else None
    except Exception:
        return None

def _gx(o: Any, *names: str):
    """Get attribute/key by any of the provided names."""
    for n in names:
        if o is None:
            continue
        if isinstance(o, dict) and n in o:
            return o[n]
        if hasattr(o, n):
            return getattr(o, n)
    return None

def _first_item(payload: Any):
    """Pick the first item from common container fields (data/items/…)."""
    for name in ("data", "items", "symbols", "infos"):
        seq = getattr(payload, name, None)
        if isinstance(seq, (list, tuple)) and seq:
            return seq[0]
    if isinstance(payload, (list, tuple)) and payload:
        return payload[0]
    return None


async def tick_value_with_size(self, symbol: str, volume: float | None = None) -> dict:
    """
    Return {'name','tick_value','tick_size','contract_size'} for a symbol.

    Strategy:
      1) Prefer acc.tick_value_with_size([symbol]) → read fields via aliases.
      2) Fallback to symbol_info_double/symbol_info_integer keys.

    Note: `volume` is accepted for signature compatibility but not used here.
    """
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")

    # 1) Modern path via account's method.
    try:
        resp = await acc.tick_value_with_size([symbol])  # low-level helper
        it = _first_item(resp)
        tv = _unbox_num(_gx(it, "tick_value", "TickValue", "tickValue", "value"))
        ts = _unbox_num(_gx(it, "tick_size",  "TickSize",  "tickSize",  "size"))
        cs = _unbox_num(_gx(it, "contract_size", "ContractSize", "contractSize"))
        if tv is not None or ts is not None or cs is not None:
            return {"name": symbol, "tick_value": tv, "tick_size": ts, "contract_size": cs}
    except Exception:
        pass

    # 2) SDK fallback: query individual fields.
    tv = ts = cs = None
    try: tv = await acc.symbol_info_double(symbol, "SYMBOL_TRADE_TICK_VALUE")
    except Exception: pass
    try: ts = await acc.symbol_info_double(symbol, "SYMBOL_TRADE_TICK_SIZE")
    except Exception: pass
    try:
        try: cs = await acc.symbol_info_double(symbol, "SYMBOL_TRADE_CONTRACT_SIZE")
        except Exception: cs = await acc.symbol_info_integer(symbol, "SYMBOL_TRADE_CONTRACT_SIZE")
    except Exception:
        pass
    return {"name": symbol, "tick_value": tv, "tick_size": ts, "contract_size": cs}


async def symbol_info_margin_rate(self, symbol: str, order_type: int = 0):
    """
    Unified wrapper for margin parameters.

    Returns:
      SimpleNamespace(
        initial_margin_rate: float (defaults to 1.0),
        maintenance_margin_rate: Optional[float],
        leverage: Optional[float],
      )

    Strategy:
      1) Use MarketInfo gRPC (SymbolInfoMarginRate) if available.
      2) Fallback to older SDK method acc.symbol_info_margin_rate.
    """
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")

    # 1) gRPC MarketInfo service.
    if market_info_pb2 is not None and getattr(acc, "market_info_client", None):
        try:
            req = market_info_pb2.SymbolInfoMarginRateRequest(symbol=symbol, order_type=order_type)
            res = await acc.market_info_client.SymbolInfoMarginRate(
                req, metadata=getattr(acc, "get_headers", lambda: [])(), timeout=None
            )
            init = _unbox_num(_gx(res, "initial_margin_rate", "initial", "initialRate", "initial_margin"))
            maint = _unbox_num(_gx(res, "maintenance_margin_rate", "maintenance", "maintenanceRate", "maintenance_margin"))
            lev  = _unbox_num(_gx(res, "leverage", "leverage_rate", "leverageRate"))
            return _NS(initial_margin_rate=init or 1.0, maintenance_margin_rate=maint, leverage=lev)
        except Exception:
            pass

    # 2) Legacy SDK fallback.
    try:
        r = await acc.symbol_info_margin_rate(symbol, order_type)
        init = _unbox_num(_gx(r, "initial_margin_rate", "initial", "initialRate", "initial_margin")) or 1.0
        maint = _unbox_num(_gx(r, "maintenance_margin_rate", "maintenance", "maintenanceRate", "maintenance_margin"))
        lev  = _unbox_num(_gx(r, "leverage", "leverage_rate", "leverageRate"))
        return _NS(initial_margin_rate=init, maintenance_margin_rate=maint, leverage=lev)
    except Exception:
        return _NS(initial_margin_rate=1.0, maintenance_margin_rate=None, leverage=None)


# Attach to MT5Service (no hard fail if import is unavailable).
try:
    from app.core.mt5_service import MT5Service  # type: ignore
    setattr(MT5Service, "tick_value_with_size", tick_value_with_size)
    setattr(MT5Service, "symbol_info_margin_rate", symbol_info_margin_rate)
except Exception:
    pass
