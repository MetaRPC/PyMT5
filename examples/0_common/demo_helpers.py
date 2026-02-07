"""
Helper functions for low-level MT5 demonstrations.

This module provides common utilities for:
  - Loading configuration from settings.json
  - Connecting to MT5 server
  - Error handling and formatting
  - Output formatting
"""

import os
import sys
import json
from uuid import uuid4
from typing import Dict, Any

# Add package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'package'))

from MetaRpcMT5 import MT5Account

# Import error handling utilities directly from centralized location
from MetaRpcMT5.helpers.errors import (
    fatal,
    print_if_error,
    print_short_error,
    format_api_error,
    check_retcode,
    print_retcode_warning,
    print_success,
    print_warning,
    print_info,
)

# Re-export for convenience
__all__ = [
    'load_settings',
    'create_and_connect_mt5',
    'print_separator',
    'print_step',
    'print_method',
    'print_error',
    'fatal',
    'print_if_error',
    'print_short_error',
    'format_api_error',
    'check_retcode',
    'print_retcode_warning',
    'print_success',
    'print_warning',
    'print_info',
]


def load_settings() -> Dict[str, Any]:
    """
    Load settings from settings.json file.

    Returns:
        Dictionary with configuration:
        - user: MT5 login
        - password: MT5 password
        - grpc_server: gRPC server address
        - mt_cluster: MT5 broker server name
        - test_symbol: Test symbol for demonstrations

    Raises:
        FileNotFoundError: If settings.json doesn't exist
        ValueError: If required fields are missing
    """
    settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')

    if not os.path.exists(settings_path):
        raise FileNotFoundError(
            f"Settings file not found: {settings_path}\n"
            "Please create settings.json with your MT5 credentials.\n"
            "Example:\n"
            "{\n"
            '  "user": 12345678,\n'
            '  "password": "your_password",\n'
            '  "grpc_server": "127.0.0.1:9999",\n'
            '  "mt_cluster": "MetaQuotes-Demo",\n'
            '  "test_symbol": "EURUSD"\n'
            "}"
        )

    with open(settings_path, 'r', encoding='utf-8') as f:
        settings = json.load(f)

    # Validate required fields
    required_fields = ['user', 'password', 'grpc_server', 'mt_cluster', 'test_symbol']
    missing_fields = [field for field in required_fields if field not in settings]

    if missing_fields:
        raise ValueError(f"Missing required fields in settings.json: {', '.join(missing_fields)}")

    return settings


async def create_and_connect_mt5(config: Dict[str, Any]) -> MT5Account:
    """
    Create MT5Account instance and connect to MT5 server.

    This is a convenience function that:
    1. Creates MT5Account with unique GUID
    2. Connects using connect_by_server_name (RECOMMENDED method)
    3. Updates account GUID from server response

    Parameters:
        config: Configuration dictionary from load_settings()

    Returns:
        Connected MT5Account instance

    Raises:
        Exception: If connection fails
    """
    print("Creating MT5Account instance...")

    # Create unique GUID for this terminal instance
    terminal_guid = uuid4()

    # Initialize MT5Account with credentials
    account = MT5Account(
        user=config['user'],
        password=config['password'],
        grpc_server=config['grpc_server'],
        id_=terminal_guid
    )

    print(f"[OK] MT5Account created (UUID: {terminal_guid})")
    print()
    print("Connecting to MT5 server...")
    print(f"  User:          {config['user']}")
    print(f"  gRPC Server:   {config['grpc_server']}")
    print(f"  MT Cluster:    {config['mt_cluster']}")
    print(f"  Base Symbol:   {config['test_symbol']}")
    print(f"  Timeout:       120 seconds")
    print()

    # Connect to MT5 server using server name
    # This is RECOMMENDED method - simpler than ConnectEx
    await account.connect_by_server_name(
        server_name=config['mt_cluster'],
        base_chart_symbol=config['test_symbol'],
        timeout_seconds=120
    )

    # Method automatically updates account.id internally
    print(f"[OK] Connected successfully")
    print(f"  Terminal GUID: {account.id}")
    print()

    return account


def print_separator(title: str = "", char: str = "─"):
    """Print formatted section separator"""
    if title:
        print(f"\n{title}")
        print(char * 59)
    else:
        print(char * 59)


def print_step(step_num: int, title: str):
    """Print formatted step header"""
    print(f"\n\nSTEP {step_num}: {title}")
    print("═" * 59)


def print_method(method_num: str, method_name: str, description: str):
    """Print formatted method header"""
    print(f"\n{method_num}. {method_name} - {description}")


def print_error(error: Exception, context: str = ""):
    """
    Print error message in formatted style.

    Parameters:
        error: Exception that occurred
        context: Optional context description
    """
    if context:
        print(f"  [ERROR] {context}: {error}")
    else:
        print(f"  [ERROR] Error: {error}")


def fatal(error: Exception, message: str):
    """
    Print fatal error and raise exception.

    Parameters:
        error: Exception that occurred
        message: Error message to display

    Raises:
        The original exception
    """
    if error:
        print(f"[FAIL] FATAL: {message}")
        print(f"   Error: {error}")
        raise error
    else:
        print(f"[FAIL] FATAL: {message}")
        raise RuntimeError(message)
