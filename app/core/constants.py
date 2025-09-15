# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE app/constants.py — MT5 order type constants & resolvers                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose: Provide consistent mapping between human-readable order names       ║
║          ("BUY", "SELL_LIMIT") and MT5 gRPC enum ints.                       ║
║ Export:  ORDER_MAP, ORDER_NAMES, resolve_order_type, order_name              ║
║ Safety:  Works even if pb2 module is missing (falls back to defaults).       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from typing import Optional

try:
    # Try to import MT5 pb2 helper with enum definitions
    from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as tf  # type: ignore
except Exception:  # fallback if pb2 is missing
    tf = None  # type: ignore

# Default numeric codes (used in MT5 platform)
_DEFAULTS = {
    "ORDER_TYPE_BUY": 0,
    "ORDER_TYPE_SELL": 1,
    "ORDER_TYPE_BUY_LIMIT": 2,
    "ORDER_TYPE_SELL_LIMIT": 3,
    "ORDER_TYPE_BUY_STOP": 4,
    "ORDER_TYPE_SELL_STOP": 5,
    "ORDER_TYPE_BUY_STOP_LIMIT": 6,
    "ORDER_TYPE_SELL_STOP_LIMIT": 7,
}


def _resolve(name: str, *, container: Optional[str] = "OrderType", default: Optional[int] = None) -> int:
    """
    Resolve enum constant `name` into int.
    Lookup order:
      1) tf.<container>.<name>
      2) tf.<name>
      3) _DEFAULTS[name] or 0
    """
    if default is None:
        default = _DEFAULTS.get(name, 0)
    if tf is None:
        return default

    # Try nested enum container
    if container and hasattr(tf, container):
        obj = getattr(tf, container)
        if hasattr(obj, name):
            val = getattr(obj, name)
            if isinstance(val, int):
                return val

    # Try top-level constant
    if hasattr(tf, name):
        val = getattr(tf, name)
        if isinstance(val, int):
            return val

    # Fallback
    return default


# Primary mapping: str → int
ORDER_MAP = {
    "BUY": _resolve("ORDER_TYPE_BUY"),
    "SELL": _resolve("ORDER_TYPE_SELL"),
    "BUY_LIMIT": _resolve("ORDER_TYPE_BUY_LIMIT"),
    "SELL_LIMIT": _resolve("ORDER_TYPE_SELL_LIMIT"),
    "BUY_STOP": _resolve("ORDER_TYPE_BUY_STOP"),
    "SELL_STOP": _resolve("ORDER_TYPE_SELL_STOP"),
    "BUY_STOP_LIMIT": _resolve("ORDER_TYPE_BUY_STOP_LIMIT"),
    "SELL_STOP_LIMIT": _resolve("ORDER_TYPE_SELL_STOP_LIMIT"),
}

# Reverse mapping: int → str
ORDER_NAMES = {v: k for k, v in ORDER_MAP.items()}


def resolve_order_type(order_type) -> int:
    """Accepts str/int/enum-like and returns normalized int code."""
    # Already int
    if isinstance(order_type, int):
        return order_type
    # Enum-like (has .value)
    if hasattr(order_type, "value"):
        try:
            return int(order_type.value)  # type: ignore[arg-type]
        except Exception:
            pass
    # String → normalize
    if isinstance(order_type, str):
        key = order_type.strip().upper()
        if key in ORDER_MAP:
            return ORDER_MAP[key]
    # Fallback: default to BUY
    return ORDER_MAP["BUY"]


def order_name(code: int) -> str:
    """Return human-readable order name for a given int code."""
    return ORDER_NAMES.get(int(code), "BUY")


__all__ = ["ORDER_MAP", "ORDER_NAMES", "resolve_order_type", "order_name"]
