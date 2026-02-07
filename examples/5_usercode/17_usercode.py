"""==============================================================================
FILE: 17_usercode.py - USER CODE SANDBOX
==============================================================================

WHAT IS THIS?
  Your personal sandbox for writing and testing MT5 trading code.
  Write once, run instantly with: python main.py usercode


THREE API LEVELS AVAILABLE:
  - account (MT5Account) - Low-level gRPC protobuf (full control)
  - service (MT5Service) - Mid-level native Python types (recommended)
  - sugar   (MT5Sugar)   - High-level convenience (62+ methods)

  You can mix all 3 levels in the same code!

HOW TO RUN THIS DEMO:
  cd examples
  python main.py usercode       (or select [18] from interactive menu)

=============================================================================="""

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

# Import all three API levels
from MetaRpcMT5 import MT5Account
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar

# Import protobuf types (for low-level examples)
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb_account
import MetaRpcMT5.mt5_term_api_market_info_pb2 as pb_market
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as pb_trading
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as pb_subscriptions


async def run_user_code():
    """Your sandbox function - write your code here!"""

    print()
    print("=" * 60)
    print("       USER CODE SANDBOX - Ready to Code!")
    print("=" * 60)
    print()

    # =================================================================
    # INITIALIZATION - All 3 API levels ready
    # =================================================================
    try:
        config = load_settings()
    except Exception as e:
        fatal(e, "Failed to load configuration")
        return

    try:
        account = await create_and_connect_mt5(config)
    except Exception as e:
        fatal(e, "Failed to create and connect MT5Account")
        return

    # Create mid-level service wrapper
    service = MT5Service(account)

    # Create high-level sugar API
    sugar = MT5Sugar(service, default_symbol=config.get('test_symbol', 'EURUSD'))

    print("[OK] Connected! All 3 API levels initialized:")
    print("   - account (MT5Account) - Low-level gRPC")
    print("   - service (MT5Service) - Mid-level Python types")
    print("   - sugar   (MT5Sugar)   - High-level convenience")
    print()
    print("=" * 60)
    print("YOUR CODE STARTS HERE")
    print("=" * 60)
    print()

    # =================================================================
    # QUICK START EXAMPLES (Uncomment to try)
    # =================================================================

    # Example 1: Get account balance (Sugar - easiest)
    # -----------------------------------------------------------------
    print("\nExample 1: Get account balance (Sugar API)")
    print("-" * 60)
    balance = await sugar.get_balance()
    print(f"Balance: {balance:.2f}")

    # Example 2: Get account info (Service - more control)
    # -----------------------------------------------------------------
    print("\nExample 2: Get account info (Service API)")
    print("-" * 60)
    account_info = await service.get_account_summary()
    print(f"Balance: {account_info.balance:.2f} {account_info.currency}")
    print(f"Equity:  {account_info.equity:.2f}")

    # Example 3: Get account via protobuf (Account - full control)
    # -----------------------------------------------------------------
    print("\nExample 3: Get account via protobuf (Account API)")
    print("-" * 60)
    reply = await account.account_summary()
    print(f"Balance (protobuf): {reply.account_balance:.2f}")

    # Example 4: Get current price (Sugar)
    # -----------------------------------------------------------------
    print("\nExample 4: Get current price (Sugar API)")
    print("-" * 60)
    bid = await sugar.get_bid()
    ask = await sugar.get_ask()
    spread = await sugar.get_spread()
    print(f"EURUSD: Bid={bid:.5f} Ask={ask:.5f} Spread={spread:.1f} pips")

    # Example 5: Get open positions (Sugar)
    # -----------------------------------------------------------------
    print("\nExample 5: Get open positions (Sugar API)")
    print("-" * 60)
    positions = await sugar.get_open_positions()
    print(f"Open positions: {len(positions)}")
    for pos in positions:
        # Note: Use SUB_ENUM_ORDER_TYPE from subscriptions_pb2 for position type
        pos_type = "BUY" if pos.type == pb_subscriptions.SUB_ORDER_TYPE_BUY else "SELL"
        print(f"  #{pos.ticket}: {pos.symbol} {pos_type} Vol={pos.volume:.2f} "
              f"Profit={pos.profit:.2f}")

    # =================================================================
    # YOUR CODE HERE
    # =================================================================

    # TODO: Write your trading logic here
    # - Use account.* for low-level protobuf access
    # - Use service.* for mid-level Python types
    # - Use sugar.* for high-level one-liners

    print("\n" + "=" * 60)
    print("User code completed!")
    print("=" * 60 + "\n")


# ==============================================================================
# QUICK REFERENCE
# ==============================================================================
#
# LEVEL 1: MT5Account (Low-level protobuf)
# ------------------------------------------------------------------------------
#   await account.account_summary()  # Get account info
#   await account.opened_orders()    # Get positions and orders
#
#   # Get symbol tick price
#   tick_reply = await account.symbol_info_tick(symbol="EURUSD")
#   print(f"Bid: {tick_reply.tick.bid}, Ask: {tick_reply.tick.ask}")
#
#   # Place order (use Sugar for easier trading - see Pattern 1)
#
# LEVEL 2: MT5Service (Mid-level Python types) - RECOMMENDED
# ------------------------------------------------------------------------------
#   await service.get_account_summary()
#   await service.get_opened_orders()
#   await service.get_symbol_tick(symbol="EURUSD")
#   # Note: Use service methods or sugar for easier trading
#   # For low-level protobuf trading, see Pattern 1 below
#
# LEVEL 3: MT5Sugar (High-level one-liners) - SIMPLEST
# ------------------------------------------------------------------------------
#   # Account queries
#   await sugar.get_balance()
#   await sugar.get_equity()
#   await sugar.get_margin()
#   await sugar.get_free_margin()
#   await sugar.get_floating_profit()
#
#   # Price queries
#   await sugar.get_bid(symbol="EURUSD")
#   await sugar.get_ask(symbol="EURUSD")
#   await sugar.get_spread(symbol="EURUSD")
#   await sugar.get_price_info(symbol="EURUSD")
#
#   # Trading (market orders)
#   await sugar.buy_market(symbol="EURUSD", volume=0.01)
#   await sugar.sell_market(symbol="EURUSD", volume=0.01)
#   await sugar.buy_market_with_pips(symbol="EURUSD", volume=0.01,
#                                     sl_pips=20, tp_pips=40)
#   await sugar.sell_market_with_pips(symbol="EURUSD", volume=0.01,
#                                      sl_pips=20, tp_pips=40)
#
#   # Trading (pending orders)
#   await sugar.buy_limit(symbol="EURUSD", volume=0.01, price=1.0500)
#   await sugar.sell_limit(symbol="EURUSD", volume=0.01, price=1.0700)
#   await sugar.buy_stop(symbol="EURUSD", volume=0.01, price=1.0700)
#   await sugar.sell_stop(symbol="EURUSD", volume=0.01, price=1.0500)
#
#   # Position management
#   await sugar.get_open_positions()
#   await sugar.count_open_positions()
#   await sugar.close_position(ticket=123456)
#   await sugar.close_all_positions()
#   await sugar.modify_position_sltp(ticket=123456, sl=1.0500, tp=1.0700)
#
#   # Risk calculations
#   await sugar.calculate_position_size(
#       symbol="EURUSD",
#       risk_percent=1.0,
#       sl_pips=20
#   )
#
#   # Profit tracking
#   await sugar.get_total_profit()
#   await sugar.get_profit_by_symbol(symbol="EURUSD")
#   await sugar.get_profit_today()
#   await sugar.get_profit_this_week()
#   await sugar.get_profit_this_month()
#
# ==============================================================================
# USEFUL PATTERNS
# ==============================================================================
#
# Pattern 1: Safe order placement with validation
# ------------------------------------------------------------------------------
#   # Check account balance first
#   balance = await sugar.get_balance()
#   if balance < 100:
#       print("Insufficient balance")
#       return
#
#   # Calculate position size based on risk
#   volume = await sugar.calculate_position_size(
#       symbol="EURUSD",
#       risk_percent=1.0,  # Risk 1% of account
#       sl_pips=20         # Stop loss at 20 pips
#   )
#
#   # Place order with risk management
#   ticket = await sugar.buy_market_with_pips(
#       symbol="EURUSD",
#       volume=volume,
#       sl_pips=20,
#       tp_pips=40  # 1:2 risk/reward ratio
#   )
#   print(f"Order placed: {ticket}")
#
# Pattern 2: Monitor open positions
# ------------------------------------------------------------------------------
#   positions = await sugar.get_open_positions()
#   total_profit = sum(pos.profit for pos in positions)
#   print(f"Total floating profit: {total_profit:.2f}")
#
#   for pos in positions:
#       # Close positions in profit > 50
#       if pos.profit > 50:
#           await sugar.close_position(pos.ticket)
#           print(f"Closed profitable position #{pos.ticket}")
#
# Pattern 3: Get market data
# ------------------------------------------------------------------------------
#   price_info = await sugar.get_price_info("EURUSD")
#   print(f"Symbol: {price_info.symbol}")
#   print(f"Bid: {price_info.bid:.5f}")
#   print(f"Ask: {price_info.ask:.5f}")
#   print(f"Spread: {price_info.spread:.5f}")
#   print(f"Time: {price_info.time}")
#
# Pattern 4: Check connection health
# ------------------------------------------------------------------------------
#   if sugar.is_connected():
#       is_alive = await sugar.ping()
#       if is_alive:
#           print("Connection OK")
#       else:
#           print("Server not responding")
#   else:
#       print("Not connected")
#
# Pattern 5: Mix API levels for flexibility
# ------------------------------------------------------------------------------
#   # Use Sugar for simple operations
#   balance = await sugar.get_balance()
#
#   # Use Service for more control
#   account_info = await service.get_account_summary()
#
#   # Use Account for direct protobuf access
#   summary = await account.account_summary()
#   balance_pb = summary.account_balance
#   equity_pb = summary.account_equity
#
# ==============================================================================
# COMMON ORDER TYPES (for reference)
# ==============================================================================
#
# from MetaRpcMT5.mt5_term_api_trade_functions_pb2 import (
#     ORDER_TYPE_TF_BUY,           # Market buy
#     ORDER_TYPE_TF_SELL,          # Market sell
#     ORDER_TYPE_TF_BUY_LIMIT,     # Buy limit (below current price)
#     ORDER_TYPE_TF_SELL_LIMIT,    # Sell limit (above current price)
#     ORDER_TYPE_TF_BUY_STOP,      # Buy stop (above current price)
#     ORDER_TYPE_TF_SELL_STOP,     # Sell stop (below current price)
# )
#
# ==============================================================================


if __name__ == "__main__":
    """Direct execution (for testing)"""
    try:
        asyncio.run(run_user_code())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
