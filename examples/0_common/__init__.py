"""
Common utilities and configuration for low-level examples.

This package contains:
  - settings.json - MT5 account credentials and configuration
  - helpers.py - Connection utilities, error handling, formatting
"""

from .helpers import (
    load_settings,
    create_and_connect_mt5,
    print_separator,
    print_step,
    print_method,
    print_error,
    fatal
)

__all__ = [
    'load_settings',
    'create_and_connect_mt5',
    'print_separator',
    'print_step',
    'print_method',
    'print_error',
    'fatal'
]
