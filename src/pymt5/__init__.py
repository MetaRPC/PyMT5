"""
══════════════════════════════════════════════════════════════════════════════
PyMT5 - MetaTrader 5 gRPC Client Library

This package provides three levels of abstraction for MT5 trading:

  LOW-LEVEL (MT5Account):
    - Direct gRPC/protobuf interface
    - Full control and flexibility
    - Located in: package/MetaRpcMT5/mt5_account.py

  MID-LEVEL (MT5Service):
    - Pythonic wrapper over MT5Account
    - Clean return types (dataclasses, datetime, etc.)
    - Recommended for most applications
    - Located in: src/pymt5/mt5_service.py

  HIGH-LEVEL (MT5Sugar):
    - One-liner operations with smart defaults
    - Risk-based calculations
    - Business logic patterns
    - Located in: src/pymt5/mt5_sugar.py

ERROR HANDLING:
  - ApiError: Wraps protobuf errors with convenient methods
  - NotConnectedError: Raised when not connected
  - Trade RetCode constants and helpers
  - Located in: package/MetaRpcMT5/helpers/errors.py (centralized for entire project)

══════════════════════════════════════════════════════════════════════════════
"""

# Import error classes and constants from centralized MetaRpcMT5.helpers.errors module
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'package'))
from MetaRpcMT5.helpers.errors import (
    # Exception classes
    ApiError,
    NotConnectedError,

    # RetCode constants
    TRADE_RETCODE_SUCCESS,
    TRADE_RETCODE_DONE,
    TRADE_RETCODE_DONE_PARTIAL,
    TRADE_RETCODE_PLACED,
    TRADE_RETCODE_REQUOTE,
    TRADE_RETCODE_REJECT,
    TRADE_RETCODE_CANCEL,
    TRADE_RETCODE_ERROR,
    TRADE_RETCODE_TIMEOUT,
    TRADE_RETCODE_INVALID,
    TRADE_RETCODE_INVALID_VOLUME,
    TRADE_RETCODE_INVALID_PRICE,
    TRADE_RETCODE_INVALID_STOPS,
    TRADE_RETCODE_TRADE_DISABLED,
    TRADE_RETCODE_MARKET_CLOSED,
    TRADE_RETCODE_NO_MONEY,
    TRADE_RETCODE_PRICE_CHANGED,
    TRADE_RETCODE_PRICE_OFF,
    TRADE_RETCODE_INVALID_EXPIRATION,
    TRADE_RETCODE_ORDER_CHANGED,
    TRADE_RETCODE_TOO_MANY_REQUESTS,
    TRADE_RETCODE_NO_CHANGES,
    TRADE_RETCODE_LOCKED,
    TRADE_RETCODE_FROZEN,
    TRADE_RETCODE_INVALID_FILL,
    TRADE_RETCODE_CONNECTION,
    TRADE_RETCODE_ONLY_REAL,
    TRADE_RETCODE_LIMIT_ORDERS,
    TRADE_RETCODE_LIMIT_VOLUME,
    TRADE_RETCODE_INVALID_ORDER,
    TRADE_RETCODE_POSITION_CLOSED,
    TRADE_RETCODE_LONG_ONLY,
    TRADE_RETCODE_SHORT_ONLY,
    TRADE_RETCODE_CLOSE_ONLY,

    # Helper functions
    is_retcode_success,
    is_retcode_partial_success,
    is_retcode_error,
    get_retcode_message,
)

# Import service layer (mid-level)
from .mt5_service import MT5Service

# Import sugar layer (high-level) - when ready
# from .mt5_sugar import MT5Sugar

__version__ = '1.0.0'

__all__ = [
    # Service classes
    'MT5Service',
    # 'MT5Sugar',  # Coming soon

    # Error classes
    'ApiError',
    'NotConnectedError',

    # RetCode constants
    'TRADE_RETCODE_SUCCESS',
    'TRADE_RETCODE_DONE',
    'TRADE_RETCODE_DONE_PARTIAL',
    'TRADE_RETCODE_PLACED',
    'TRADE_RETCODE_REQUOTE',
    'TRADE_RETCODE_REJECT',
    'TRADE_RETCODE_CANCEL',
    'TRADE_RETCODE_ERROR',
    'TRADE_RETCODE_TIMEOUT',
    'TRADE_RETCODE_INVALID',
    'TRADE_RETCODE_INVALID_VOLUME',
    'TRADE_RETCODE_INVALID_PRICE',
    'TRADE_RETCODE_INVALID_STOPS',
    'TRADE_RETCODE_TRADE_DISABLED',
    'TRADE_RETCODE_MARKET_CLOSED',
    'TRADE_RETCODE_NO_MONEY',
    'TRADE_RETCODE_PRICE_CHANGED',
    'TRADE_RETCODE_PRICE_OFF',
    'TRADE_RETCODE_INVALID_EXPIRATION',
    'TRADE_RETCODE_ORDER_CHANGED',
    'TRADE_RETCODE_TOO_MANY_REQUESTS',
    'TRADE_RETCODE_NO_CHANGES',
    'TRADE_RETCODE_LOCKED',
    'TRADE_RETCODE_FROZEN',
    'TRADE_RETCODE_INVALID_FILL',
    'TRADE_RETCODE_CONNECTION',
    'TRADE_RETCODE_ONLY_REAL',
    'TRADE_RETCODE_LIMIT_ORDERS',
    'TRADE_RETCODE_LIMIT_VOLUME',
    'TRADE_RETCODE_INVALID_ORDER',
    'TRADE_RETCODE_POSITION_CLOSED',
    'TRADE_RETCODE_LONG_ONLY',
    'TRADE_RETCODE_SHORT_ONLY',
    'TRADE_RETCODE_CLOSE_ONLY',

    # Helper functions
    'is_retcode_success',
    'is_retcode_partial_success',
    'is_retcode_error',
    'get_retcode_message',
]
