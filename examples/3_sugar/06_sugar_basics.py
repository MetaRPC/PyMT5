"""══════════════════════════════════════════════════════════════════════════════
FILE: 06_sugar_basics.py - HIGH-LEVEL SUGAR API BASICS DEMO

🎯 PURPOSE:
  Demonstrates MT5Sugar basics: connection, account balance, and price queries.
  This is the SIMPLEST way to interact with MT5 - perfect for quick scripts!

WHO SHOULD USE THIS:
  - Beginners learning MT5 API
  - Quick prototyping and testing
  - Simple monitoring scripts
  - Educational purposes

📚 WHAT THIS DEMO COVERS (3 Categories):

  1. CONNECTION METHODS (2 methods)
     - is_connected() - Check connection status
     - ping() - Verify connection health

  2. QUICK BALANCE METHODS (6 methods)
     - get_balance() - Account balance
     - get_equity() - Current equity
     - get_margin() - Used margin
     - get_free_margin() - Available margin
     - get_margin_level() - Margin level %
     - get_floating_profit() - Floating P/L

  3. PRICES & QUOTES (5 methods)
     - get_bid() - Current BID price
     - get_ask() - Current ASK price
     - get_spread() - Spread in pips
     - get_price_info() - Complete price info
     - wait_for_price() - Wait for price update

API LEVELS:
    HIGH-LEVEL (Sugar) - THIS FILE: One-liner operations, smart defaults
    MID-LEVEL (Service): More control, native Python types
    LOW-LEVEL (Account): Maximum flexibility, protobuf structures

🚀 HOW TO RUN:
  cd examples
  python main.py sugar06              (or select [6] from menu)

 NOTE: This demo is READ-ONLY and safe to run on live accounts!
══════════════════════════════════════════════════════════════════════════════"""

import asyncio
import sys
import os

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'package'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '0_common'))

# Import helpers
from demo_helpers import (
    load_settings,
    create_and_connect_mt5,
    print_if_error,
    print_success,
    print_info,
    fatal,
)

# Import MT5Sugar
from pymt5.mt5_sugar import MT5Sugar
from pymt5.mt5_service import MT5Service



async def run_sugar_basics_demo():
    """Run the Sugar basics demonstration."""

    print("\n" + "=" * 80)
    print("MT5 SUGAR API - BASICS DEMO (Read-Only Operations)")
    print("=" * 80)

    # Load configuration
    try:
        config = load_settings()
    except Exception as e:
        fatal(e, "Failed to load configuration")
        return

    # Create MT5Account and connect
    try:
        account = await create_and_connect_mt5(config)
    except Exception as e:
        fatal(e, "Failed to create and connect MT5Account")
        return

    # Create MT5Service
    service = MT5Service(account)

    # Create MT5Sugar with default symbol
    sugar = MT5Sugar(service, default_symbol=config['test_symbol'])


    # ══════════════════════════════════════════════════════════════════════════════
    # region CONNECTION
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("1. CONNECTION METHODS")
    print("=" * 80)

    # ══════════════════════════════════════════════════════════════
    # 1.1. is_connected()
    #      Check if gRPC channel is ready or idle.
    #      Returns: bool - True if connected.
    #      SAFE operation - local check only.
    # ══════════════════════════════════════════════════════════════
    print("\n1.1. is_connected() - Check connection status")

    if sugar.is_connected():
        print_success("Status: CONNECTED")
    else:
        print("  [X] Status: NOT CONNECTED")

    # ══════════════════════════════════════════════════════════════
    # 1.2. ping()
    #      Verify connection health with lightweight request.
    #      Chain: Sugar → Service.get_symbols_total() → Account → gRPC
    #      Returns: bool - True if server responds.
    #      SAFE operation - quick test query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n1.2. ping() - Verify connection health")

    try:
        if await sugar.ping(timeout=5.0):
            print_success("Ping successful - connection is healthy")
        else:
            print("  [X] Ping failed - server not responding")
    except Exception as e:
        print_if_error(e, "Ping failed")

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region QUICK BALANCE METHODS
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("2. QUICK BALANCE METHODS")
    print("=" * 80)

    # ══════════════════════════════════════════════════════════════
    # 2.1. get_balance()
    #      Get current account balance (deposit amount).
    #      Chain: Sugar → Service.get_account_summary() → Account → gRPC
    #      Returns: float balance in account currency.
    #      SAFE operation - read-only query.
    # ══════════════════════════════════════════════════════════════
    print("\n2.1. get_balance() - Account balance")

    try:
        balance = await sugar.get_balance()
        print(f"  Balance: {balance:.2f}")
    except Exception as e:
        print_if_error(e, "get_balance failed")

    # ══════════════════════════════════════════════════════════════
    # 2.2. get_equity()
    #      Get current account equity (balance + floating profit).
    #      Chain: Sugar → Service.get_account_summary() → Account → gRPC
    #      Returns: float equity = balance + open positions P/L.
    #      SAFE operation - read-only query.
    # ══════════════════════════════════════════════════════════════
    print("\n2.2. get_equity() - Account equity")

    try:
        equity = await sugar.get_equity()
        print(f"  Equity: {equity:.2f}")
    except Exception as e:
        print_if_error(e, "get_equity failed")

    # ══════════════════════════════════════════════════════════════
    # 2.3. get_margin()
    #      Get amount of margin currently used by open positions.
    #      Chain: Sugar → Service.get_account_double() → Account → gRPC
    #      Returns: float used margin (collateral locked).
    #      SAFE operation - read-only query.
    # ══════════════════════════════════════════════════════════════
    print("\n2.3. get_margin() - Used margin")

    try:
        margin = await sugar.get_margin()
        print(f"  Used Margin: {margin:.2f}")
    except Exception as e:
        print_if_error(e, "get_margin failed")

    # ══════════════════════════════════════════════════════════════
    # 2.4. get_free_margin()
    #      Get amount of margin available for new positions.
    #      Chain: Sugar → Service.get_account_double() → Account → gRPC
    #      Returns: float free margin = equity - used margin.
    #      SAFE operation - read-only query.
    # ══════════════════════════════════════════════════════════════
    print("\n2.4. get_free_margin() - Free margin")

    try:
        free_margin = await sugar.get_free_margin()
        print(f"  Free Margin: {free_margin:.2f}")
    except Exception as e:
        print_if_error(e, "get_free_margin failed")

    # ══════════════════════════════════════════════════════════════
    # 2.5. get_margin_level()
    #      Get margin level percentage (equity / margin * 100).
    #      Chain: Sugar → Service.get_account_double() → Account → gRPC
    #      Returns: float margin level %. 0 = no positions.
    #      SAFE operation - read-only query.
    # ══════════════════════════════════════════════════════════════
    print("\n2.5. get_margin_level() - Margin level %")

    try:
        margin_level = await sugar.get_margin_level()
        if margin_level == 0:
            print("  Margin Level: INFINITY (no open positions)")
        else:
            print(f"  Margin Level: {margin_level:.2f}%")
    except Exception as e:
        print_if_error(e, "get_margin_level failed")

    # ══════════════════════════════════════════════════════════════
    # 2.6. get_floating_profit()
    #      Get total floating profit/loss from all open positions.
    #      Chain: Sugar → Service.get_account_double() → Account → gRPC
    #      Returns: float unrealized P/L. Positive = profit.
    #      SAFE operation - read-only query.
    # ══════════════════════════════════════════════════════════════
    print("\n2.6. get_floating_profit() - Current floating profit/loss")

    try:
        profit = await sugar.get_floating_profit()
        if profit >= 0:
            print(f"  Profit: +{profit:.2f}")
        else:
            print(f"  Profit: {profit:.2f}")
    except Exception as e:
        print_if_error(e, "get_floating_profit failed")

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region PRICES & QUOTES METHODS
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("3. PRICES & QUOTES METHODS")
    print("=" * 80)

    test_symbol = config['test_symbol']

    # ══════════════════════════════════════════════════════════════
    # 3.1. get_bid()
    #      Get current BID price (SELL price) for symbol.
    #      Chain: Sugar → Service.get_symbol_tick() → Account → gRPC
    #      Returns: float current BID price.
    #      SAFE operation - read-only query.
    # ══════════════════════════════════════════════════════════════
    print(f"\n3.1. get_bid() - Current BID price for {test_symbol}")

    try:
        bid = await sugar.get_bid(test_symbol)
        print(f"  BID: {bid:.5f}")
    except Exception as e:
        print_if_error(e, "get_bid failed")

    # ══════════════════════════════════════════════════════════════
    # 3.2. get_ask()
    #      Get current ASK price (BUY price) for symbol.
    #      Chain: Sugar → Service.get_symbol_tick() → Account → gRPC
    #      Returns: float current ASK price.
    #      SAFE operation - read-only query.
    # ══════════════════════════════════════════════════════════════
    print(f"\n3.2. get_ask() - Current ASK price for {test_symbol}")

    try:
        ask = await sugar.get_ask(test_symbol)
        print(f"  ASK: {ask:.5f}")
    except Exception as e:
        print_if_error(e, "get_ask failed")

    # ══════════════════════════════════════════════════════════════
    # 3.3. get_spread()
    #      Get current spread in points (ASK - BID).
    #      Chain: Sugar → Service.get_symbol_tick() → Account → gRPC
    #      Returns: float spread = ask - bid.
    #      SAFE operation - read-only query.
    # ══════════════════════════════════════════════════════════════
    print(f"\n3.3. get_spread() - Current spread for {test_symbol}")

    try:
        spread = await sugar.get_spread(test_symbol)
        print(f"  Spread: {spread:.5f}")
    except Exception as e:
        print_if_error(e, "get_spread failed")

    # ══════════════════════════════════════════════════════════════
    # 3.4. get_price_info()
    #      Get complete price information (BID, ASK, spread, time).
    #      Chain: Sugar → Service.get_symbol_tick() → Account → gRPC
    #      Returns: PriceInfo dataclass with all price data.
    #      SAFE operation - read-only query.
    # ══════════════════════════════════════════════════════════════
    print(f"\n3.4. get_price_info() - Complete price info for {test_symbol}")

    try:
        price_info = await sugar.get_price_info(test_symbol)
        print(f"  Symbol:     {test_symbol}")
        print(f"  BID:        {price_info.bid:.5f}")
        print(f"  ASK:        {price_info.ask:.5f}")
        print(f"  Spread:     {price_info.spread:.5f}")
        print(f"  Time:       {price_info.time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print_if_error(e, "get_price_info failed")

    # ══════════════════════════════════════════════════════════════
    # 3.5. wait_for_price()
    #      Wait for price with timeout (single request, NOT polling).
    #      Chain: Sugar → Service.get_symbol_tick() → Account → gRPC
    #      Returns: PriceInfo when valid price received.
    #      SAFE operation - read-only query with timeout.
    #      Timeout: Custom (here 3 seconds)
    # ══════════════════════════════════════════════════════════════
    print(f"\n3.5. wait_for_price() - Wait for price update (3 sec timeout)")
    print(f"  Waiting for {test_symbol} price change...")

    try:
        tick = await sugar.wait_for_price(test_symbol, timeout=3.0)
        print_success("Price received!")
        print(f"    BID: {tick.bid:.5f}, ASK: {tick.ask:.5f}")
    except TimeoutError:
        print_info("This is normal if price doesn't change within timeout")
    except Exception as e:
        print_if_error(e, "wait_for_price error")

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # CLEANUP: DISCONNECT
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("CLEANUP: Disconnecting...")
    print("=" * 80)

    try:
        await sugar.disconnect()
        print("✓ Disconnected successfully")
    except Exception as e:
        print(f"⚠️  Disconnect warning: {e}")


    # ══════════════════════════════════════════════════════════════════════════════
    # DEMO SUMMARY
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("[OK] DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)

    print("\nMETHODS DEMONSTRATED (13 total):")
    print("   CONNECTION METHODS (2):  is_connected, ping")
    print("   QUICK BALANCE (6):       get_balance, get_equity, get_margin, get_free_margin,")
    print("                            get_margin_level, get_floating_profit")
    print("   PRICES & QUOTES (5):     get_bid, get_ask, get_spread, get_price_info, wait_for_price")

    print("\nMT5Sugar API ADVANTAGES:")
    print("   [+] One-liner operations:   await sugar.get_balance() - simple!")
    print("   [+] Direct value returns:   float, not wrapped in structs")
    print("   [+] No protobuf knowledge:  All native Python types")
    print("   [+] Auto timeouts:          Built-in timeout handling")
    print("   [+] Smart defaults:         Default symbol, standard parameters")

    print("\nWHAT'S NEXT:")
    print("   [7]  Trading Operations   → python main.py sugar07")
    print("   [8]  Position Management  → python main.py sugar08")
    print("   [9]  History & Profits    → python main.py sugar09")
    print("   [10] Advanced Features    → python main.py sugar10")

    print("\n" + "=" * 80)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    asyncio.run(run_sugar_basics_demo())
