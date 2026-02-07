"""
══════════════════════════════════════════════════════════════════════════════
Helpers Package - Low-Level Components for PyMT5
══════════════════════════════════════════════════════════════════════════════

This package contains core components used across the PyMT5 project:
  • mt5_account.py - Low-level gRPC client (MT5Account class)
  • errors.py - Error handling (ApiError, NotConnectedError, RetCodes, helpers)

USAGE:
  from helpers.mt5_account import MT5Account
  from helpers.errors import ApiError, NotConnectedError, TRADE_RETCODE_DONE

══════════════════════════════════════════════════════════════════════════════
"""

# Re-export MT5Account for convenience
from .mt5_account import MT5Account

# Re-export all error classes and utilities
from .errors import (
    # Exception classes
    NotConnectedError,
    ApiError,

    # Backward compatibility aliases
    ConnectExceptionMT5,
    ApiExceptionMT5,

    # All RetCode constants
    TRADE_RETCODE_DONE,
    TRADE_RETCODE_DONE_PARTIAL,
    TRADE_RETCODE_PLACED,
    TRADE_RETCODE_REQUOTE,
    TRADE_RETCODE_PRICE_CHANGED,
    TRADE_RETCODE_REJECT,
    TRADE_RETCODE_CANCEL,
    TRADE_RETCODE_INVALID_REQUEST,
    TRADE_RETCODE_INVALID_VOLUME,
    TRADE_RETCODE_INVALID_PRICE,
    TRADE_RETCODE_INVALID_STOPS,
    TRADE_RETCODE_INVALID_EXPIRATION,
    TRADE_RETCODE_INVALID_FILL,
    TRADE_RETCODE_INVALID_ORDER,
    TRADE_RETCODE_INVALID_CLOSE_VOLUME,
    TRADE_RETCODE_INVALID,
    TRADE_RETCODE_TRADE_DISABLED,
    TRADE_RETCODE_MARKET_CLOSED,
    TRADE_RETCODE_SERVER_DISABLES_AT,
    TRADE_RETCODE_CLIENT_DISABLES_AT,
    TRADE_RETCODE_ONLY_REAL,
    TRADE_RETCODE_LONG_ONLY,
    TRADE_RETCODE_SHORT_ONLY,
    TRADE_RETCODE_CLOSE_ONLY,
    TRADE_RETCODE_FIFO_CLOSE,
    TRADE_RETCODE_HEDGE_PROHIBITED,
    TRADE_RETCODE_NO_MONEY,
    TRADE_RETCODE_LIMIT_ORDERS,
    TRADE_RETCODE_LIMIT_VOLUME,
    TRADE_RETCODE_LIMIT_POSITIONS,
    TRADE_RETCODE_ERROR,
    TRADE_RETCODE_TIMEOUT,
    TRADE_RETCODE_NO_QUOTES,
    TRADE_RETCODE_TOO_MANY_REQUESTS,
    TRADE_RETCODE_LOCKED,
    TRADE_RETCODE_FROZEN,
    TRADE_RETCODE_NO_CONNECTION,
    TRADE_RETCODE_PRICE_OFF,
    TRADE_RETCODE_CONNECTION,
    TRADE_RETCODE_ORDER_CHANGED,
    TRADE_RETCODE_NO_CHANGES,
    TRADE_RETCODE_POSITION_CLOSED,
    TRADE_RETCODE_CLOSE_ORDER_EXIST,
    TRADE_RETCODE_REJECT_CANCEL,

    # Helper functions
    is_retcode_success,
    is_retcode_partial_success,
    is_retcode_error,
    is_retcode_requote,
    is_retcode_retryable,
    get_retcode_message,

    # Error handling utilities
    fatal,
    print_if_error,
    print_short_error,
    format_api_error,
    check_retcode,
    print_retcode_warning,

    # Convenience functions
    print_success,
    print_warning,
    print_info,
)

__all__ = [
    # Core classes
    'MT5Account',

    # Exception classes
    'NotConnectedError',
    'ApiError',
    'ConnectExceptionMT5',
    'ApiExceptionMT5',

    # RetCode constants
    'TRADE_RETCODE_DONE',
    'TRADE_RETCODE_DONE_PARTIAL',
    'TRADE_RETCODE_PLACED',
    'TRADE_RETCODE_REQUOTE',
    'TRADE_RETCODE_PRICE_CHANGED',
    'TRADE_RETCODE_REJECT',
    'TRADE_RETCODE_CANCEL',
    'TRADE_RETCODE_INVALID_REQUEST',
    'TRADE_RETCODE_INVALID_VOLUME',
    'TRADE_RETCODE_INVALID_PRICE',
    'TRADE_RETCODE_INVALID_STOPS',
    'TRADE_RETCODE_INVALID_EXPIRATION',
    'TRADE_RETCODE_INVALID_FILL',
    'TRADE_RETCODE_INVALID_ORDER',
    'TRADE_RETCODE_INVALID_CLOSE_VOLUME',
    'TRADE_RETCODE_INVALID',
    'TRADE_RETCODE_TRADE_DISABLED',
    'TRADE_RETCODE_MARKET_CLOSED',
    'TRADE_RETCODE_SERVER_DISABLES_AT',
    'TRADE_RETCODE_CLIENT_DISABLES_AT',
    'TRADE_RETCODE_ONLY_REAL',
    'TRADE_RETCODE_LONG_ONLY',
    'TRADE_RETCODE_SHORT_ONLY',
    'TRADE_RETCODE_CLOSE_ONLY',
    'TRADE_RETCODE_FIFO_CLOSE',
    'TRADE_RETCODE_HEDGE_PROHIBITED',
    'TRADE_RETCODE_NO_MONEY',
    'TRADE_RETCODE_LIMIT_ORDERS',
    'TRADE_RETCODE_LIMIT_VOLUME',
    'TRADE_RETCODE_LIMIT_POSITIONS',
    'TRADE_RETCODE_ERROR',
    'TRADE_RETCODE_TIMEOUT',
    'TRADE_RETCODE_NO_QUOTES',
    'TRADE_RETCODE_TOO_MANY_REQUESTS',
    'TRADE_RETCODE_LOCKED',
    'TRADE_RETCODE_FROZEN',
    'TRADE_RETCODE_NO_CONNECTION',
    'TRADE_RETCODE_PRICE_OFF',
    'TRADE_RETCODE_CONNECTION',
    'TRADE_RETCODE_ORDER_CHANGED',
    'TRADE_RETCODE_NO_CHANGES',
    'TRADE_RETCODE_POSITION_CLOSED',
    'TRADE_RETCODE_CLOSE_ORDER_EXIST',
    'TRADE_RETCODE_REJECT_CANCEL',

    # Helper functions
    'is_retcode_success',
    'is_retcode_partial_success',
    'is_retcode_error',
    'is_retcode_requote',
    'is_retcode_retryable',
    'get_retcode_message',

    # Error handling utilities
    'fatal',
    'print_if_error',
    'print_short_error',
    'format_api_error',
    'check_retcode',
    'print_retcode_warning',

    # Convenience functions
    'print_success',
    'print_warning',
    'print_info',
]
