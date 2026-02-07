"""==============================================================================
FILE: 08_sugar_positions.py - HIGH-LEVEL SUGAR API POSITION MANAGEMENT DEMO

🎯 PURPOSE:
  Demonstrates MT5Sugar position management: querying, modifying, and closing.
  SIMPLIFIED position operations without complex parameter handling!

WHO SHOULD USE THIS:
  - Managing open positions programmatically
  - Building position monitoring tools
  - Learning position modification (SL/TP)
  - Quick position closing operations

📚 WHAT THIS DEMO COVERS (3 Categories):

  1. POSITION INFO METHODS (7 methods)
     - get_open_positions() - All open positions
     - get_position_by_ticket(ticket) - Specific position
     - get_positions_by_symbol(symbol) - Positions for symbol
     - has_open_position(symbol) - Check if positions exist
     - count_open_positions() - Count total positions
     - get_total_profit() - Total floating P&L
     - get_profit_by_symbol(symbol) - Profit for symbol

  2. POSITION MODIFICATION (3 methods)
     - modify_position_sl(ticket, sl) - Change Stop Loss
     - modify_position_tp(ticket, tp) - Change Take Profit
     - modify_position_sltp(ticket, sl, tp) - Change both SL/TP

  3. POSITION CLOSING (3 methods)
     - close_position(ticket) - Close full position
     - close_position_partial(ticket, volume) - Partial close
     - close_all_positions(symbol=None) - Close all (or by symbol)

API LEVELS:
    HIGH-LEVEL (Sugar) - THIS FILE: Simple position operations
    MID-LEVEL (Service): More control, custom close parameters
    LOW-LEVEL (Account): Full control, manual request construction

🚀 HOW TO RUN:
  cd examples
  python main.py sugar08              (or select [8] from menu)

⚠️ WARNING: This demo OPENS and CLOSES test positions!
  - Opens 2 test positions (BUY/SELL)
  - Demonstrates modification operations
  - Closes all positions at the end
  - Recommended to run on DEMO account first
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

# Import MT5Sugar
from pymt5.mt5_sugar import MT5Sugar
from pymt5.mt5_service import MT5Service

# Import protobuf for type checking
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as trade_functions_pb2


async def run_sugar_positions_demo():
    """Run the Sugar position management demonstration."""

    print("\n" + "=" * 80)
    print("MT5 SUGAR API - POSITION MANAGEMENT DEMO")
    print("=" * 80)

    # Load configuration
    try:
        config = load_settings()
    except Exception as e:
        fatal(e, "Failed to load configuration")
        return

    # Create MT5Account and connect
    print("\nConnecting to MT5...")
    try:
        account = await create_and_connect_mt5(config)
    except Exception as e:
        fatal(e, "Failed to create and connect MT5Account")
        return

    # Create MT5Service
    service = MT5Service(account)

    # Create MT5Sugar with default symbol
    sugar = MT5Sugar(service, default_symbol=config['test_symbol'])
    print_success("Connected!")

    print_info("Waiting for trade server synchronization (20 seconds)...")
    await asyncio.sleep(20)
    print_success("Trade server ready!")

    test_symbol = config['test_symbol']
    min_volume = config.get('test_volume', 0.01)


    # PREPARATION: Open test positions
    print("\n" + "-" * 80)
    print("PREPARATION: Opening test positions")
    print("-" * 80)

    # Get current prices
    try:
        bid = await sugar.get_bid(test_symbol)
        ask = await sugar.get_ask(test_symbol)
        print(f"\nCurrent {test_symbol} prices: BID={bid:.5f}, ASK={ask:.5f}")
    except Exception as e:
        fatal(e, "Failed to get current price")
        return

    # Open 2 positions for testing
    ticket1 = None
    ticket2 = None

    try:
        ticket1 = await sugar.buy_market(test_symbol, min_volume)
        print_success(f"Opened BUY position: #{ticket1}")
    except Exception as e:
        print_if_error(e, "BUY error")
        return

    try:
        ticket2 = await sugar.sell_market(test_symbol, min_volume)
        print_success(f"Opened SELL position: #{ticket2}")
    except Exception as e:
        print_if_error(e, "SELL error")
        return

    # Let positions register
    await asyncio.sleep(1)


    # ══════════════════════════════════════════════════════════════════════════════
    # region POSITION INFO METHODS
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("1. POSITION INFO METHODS")
    print("=" * 80)

    # ══════════════════════════════════════════════════════════════
    # 1.1. has_open_position()
    #      Check if any open positions exist for symbol.
    #      Chain: Sugar -> Service.get_opened_orders() -> Account -> gRPC
    #      Returns: bool - true if positions exist.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print(f"\n1.1. has_open_position() - Check if {test_symbol} positions exist")

    try:
        has_pos = await sugar.has_open_position(test_symbol)
        print(f"  Has open {test_symbol} positions: {has_pos}")
    except Exception as e:
        print_if_error(e, "has_open_position failed")

    # ══════════════════════════════════════════════════════════════
    # 1.2. count_open_positions()
    #      Count total number of open positions.
    #      Chain: Sugar -> Service.get_opened_orders() -> Account -> gRPC
    #      Returns: int - total count of open positions.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n1.2. count_open_positions() - Count total open positions")

    try:
        count = await sugar.count_open_positions()
        print(f"  Total open positions: {count}")
    except Exception as e:
        print_if_error(e, "count_open_positions failed")

    # ══════════════════════════════════════════════════════════════
    # 1.3. get_open_positions()
    #      Get all open positions with full details.
    #      Chain: Sugar -> Service.get_opened_orders() -> Account -> gRPC
    #      Returns: List[Position] - list of all open positions.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n1.3. get_open_positions() - Get all open positions")

    try:
        positions = await sugar.get_open_positions()
        print(f"  Found {len(positions)} position(s):")
        for i, pos in enumerate(positions, 1):
            pos_type = "BUY" if pos.type == trade_functions_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY else "SELL"
            print(f"    {i}. Ticket #{pos.ticket}: {pos_type} {pos.volume:.2f} lots, Profit: {pos.profit:.2f}")
    except Exception as e:
        print_if_error(e, "get_open_positions failed")

    # ══════════════════════════════════════════════════════════════
    # 1.4. get_position_by_ticket()
    #      Get specific position by ticket number.
    #      Chain: Sugar -> Service.get_opened_orders() -> Account -> gRPC
    #      Returns: Position - position details or None if not found.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print(f"\n1.4. get_position_by_ticket() - Get specific position #{ticket1}")

    try:
        pos = await sugar.get_position_by_ticket(ticket1)
        if pos is None:
            print("  [X] Position not found")
        else:
            print(f"    Found position:")
            print(f"    Symbol: {pos.symbol}")
            print(f"    Volume: {pos.volume:.2f}")
            print(f"    Price:  {pos.price_open:.5f}")
            print(f"    Profit: {pos.profit:.2f}")
    except Exception as e:
        print_if_error(e, "get_position_by_ticket failed")

    # ══════════════════════════════════════════════════════════════
    # 1.5. get_positions_by_symbol()
    #      Get all positions for specific symbol.
    #      Chain: Sugar -> Service.get_opened_orders() -> Account -> gRPC
    #      Returns: List[Position] - positions for the symbol.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print(f"\n1.5. get_positions_by_symbol() - Get positions for {test_symbol}")

    try:
        symbol_positions = await sugar.get_positions_by_symbol(test_symbol)
        print(f"  Found {len(symbol_positions)} position(s) for {test_symbol}")
    except Exception as e:
        print_if_error(e, "get_positions_by_symbol failed")

    # ══════════════════════════════════════════════════════════════
    # 1.6. get_total_profit()
    #      Get total floating P/L from all positions.
    #      Chain: Sugar -> Service.get_opened_orders() -> Account -> gRPC
    #      Returns: float - sum of all position profits.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n1.6. get_total_profit() - Total floating P&L")

    try:
        total_profit = await sugar.get_total_profit()
        if total_profit >= 0:
            print(f"  Total profit: +{total_profit:.2f}")
        else:
            print(f"  Total profit: {total_profit:.2f}")
    except Exception as e:
        print_if_error(e, "get_total_profit failed")

    # ══════════════════════════════════════════════════════════════
    # 1.7. get_profit_by_symbol()
    #      Get floating P/L for specific symbol.
    #      Chain: Sugar -> Service.get_opened_orders() -> Account -> gRPC
    #      Returns: float - sum of profits for the symbol.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print(f"\n1.7. get_profit_by_symbol() - Profit for {test_symbol}")

    try:
        symbol_profit = await sugar.get_profit_by_symbol(test_symbol)
        if symbol_profit >= 0:
            print(f"  {test_symbol} profit: +{symbol_profit:.2f}")
        else:
            print(f"  {test_symbol} profit: {symbol_profit:.2f}")
    except Exception as e:
        print_if_error(e, "get_profit_by_symbol failed")

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region POSITION MODIFICATION
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("2. POSITION MODIFICATION METHODS")
    print("=" * 80)

    # Refresh prices
    bid = await sugar.get_bid(test_symbol)
    ask = await sugar.get_ask(test_symbol)

    # ══════════════════════════════════════════════════════════════
    # 2.1. modify_position_sl()
    #      Modify Stop Loss level for existing position.
    #      Chain: Sugar -> Service.modify_order() -> Account.order_send() -> gRPC
    #      Returns: bool - True if modification successful.
    #      DANGEROUS operation - modifies real position!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    new_sl = bid - 0.0030  # 30 pips below
    print(f"\n2.1. modify_position_sl() - Set Stop Loss to {new_sl:.5f}")

    try:
        success = await sugar.modify_position_sl(ticket1, new_sl)
        if success:
            print_success(f"Stop Loss updated for position #{ticket1}")
        else:
            print("  [X] Failed to update Stop Loss")
    except Exception as e:
        print_if_error(e, "modify_position_sl failed")

    await asyncio.sleep(0.5)

    # ══════════════════════════════════════════════════════════════
    # 2.2. modify_position_tp()
    #      Modify Take Profit level for existing position.
    #      Chain: Sugar -> Service.modify_order() -> Account.order_send() -> gRPC
    #      Returns: bool - True if modification successful.
    #      DANGEROUS operation - modifies real position!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    new_tp = bid + 0.0050  # 50 pips above
    print(f"\n2.2. modify_position_tp() - Set Take Profit to {new_tp:.5f}")

    try:
        success = await sugar.modify_position_tp(ticket1, new_tp)
        if success:
            print_success(f"Take Profit updated for position #{ticket1}")
        else:
            print("  [X] Failed to update Take Profit")
    except Exception as e:
        print_if_error(e, "modify_position_tp failed")

    await asyncio.sleep(0.5)

    # ══════════════════════════════════════════════════════════════
    # 2.3. modify_position_sltp()
    #      Modify both Stop Loss and Take Profit in one call.
    #      Chain: Sugar -> Service.modify_order() -> Account.order_send() -> gRPC
    #      Returns: bool - True if modification successful.
    #      DANGEROUS operation - modifies real position!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    new_sl2 = ask + 0.0030  # For SELL position
    new_tp2 = ask - 0.0050
    print(f"\n2.3. modify_position_sltp() - Set both SL and TP")
    print(f"  SL: {new_sl2:.5f}, TP: {new_tp2:.5f}")

    try:
        success = await sugar.modify_position_sltp(ticket2, new_sl2, new_tp2)
        if success:
            print_success(f"SL/TP updated for position #{ticket2}")
        else:
            print("  [X] Failed to update SL/TP")
    except Exception as e:
        print_if_error(e, "modify_position_sltp failed")

    await asyncio.sleep(0.5)

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region POSITION CLOSING
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("3. POSITION CLOSING METHODS")
    print("=" * 80)

    # ══════════════════════════════════════════════════════════════
    # 3.1. close_position_partial()
    #      Close part of position volume (partial close).
    #      Chain: Sugar -> Service.close_order() -> Account.order_send() -> gRPC
    #      Returns: bool - True if close successful.
    #      DANGEROUS operation - closes real position partially!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    print(f"\n3.1. close_position_partial() - Close 50% of position #{ticket1}")

    partial_volume = min_volume / 2
    try:
        success = await sugar.close_position_partial(ticket1, partial_volume)
        if success:
            print_success(f"Closed {partial_volume:.3f} lots from position #{ticket1}")
        else:
            print("  [INFO] Partial close may not be supported on all brokers")
    except Exception as e:
        print_if_error(e, "close_position_partial failed")
        print("  [INFO] Partial close may not be supported on all brokers")

    await asyncio.sleep(1)

    # ══════════════════════════════════════════════════════════════
    # 3.2. close_position()
    #      Close entire position completely.
    #      Chain: Sugar -> Service.close_order() -> Account.order_send() -> gRPC
    #      Returns: bool - True if close successful.
    #      DANGEROUS operation - closes real position!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    print(f"\n3.2. close_position() - Close entire position #{ticket1}")

    try:
        success = await sugar.close_position(ticket1)
        if success:
            print_success(f"Position #{ticket1} closed completely")
        else:
            print("  [X] Failed to close position")
    except Exception as e:
        print_if_error(e, "close_position failed")

    await asyncio.sleep(1)

    # Open a new position for symbol-specific close test
    ticket3 = None
    try:
        ticket3 = await sugar.buy_market(test_symbol, min_volume)
        print(f"\n  Opened test position #{ticket3} for close_all_positions(symbol) demo")
        await asyncio.sleep(1)

        # ══════════════════════════════════════════════════════════════
        # 3.3. close_all_positions(symbol)
        #      Close all positions for specific symbol.
        #      Chain: Sugar -> Service (get_opened_orders + close_order loop) -> Account
        #      Returns: int - number of closed positions.
        #      DANGEROUS operation - closes all symbol positions!
        #      Timeout: 30 seconds
        # ══════════════════════════════════════════════════════════════
        print(f"\n3.3. close_all_positions(symbol) - Close all {test_symbol} positions")

        closed_count = await sugar.close_all_positions(test_symbol)
        print_success(f"Closed {closed_count} position(s) for {test_symbol}")
    except Exception as e:
        print_if_error(e, "close_all_positions(symbol) failed")

    await asyncio.sleep(1)

    # ══════════════════════════════════════════════════════════════
    # 3.4. close_all_positions()
    #      Close ALL open positions (all symbols).
    #      Chain: Sugar -> Service (get_opened_orders + close_order loop) -> Account
    #      Returns: int - number of closed positions.
    #      DANGEROUS operation - closes ALL positions!
    #      Timeout: 30 seconds
    # ══════════════════════════════════════════════════════════════
    # First, check if any positions remain
    remaining_count = await sugar.count_open_positions()
    if remaining_count > 0:
        print(f"\n3.4. close_all_positions() - Close all remaining positions")
        try:
            closed_total = await sugar.close_all_positions()
            print_success(f"Closed {closed_total} position(s)")
        except Exception as e:
            print_if_error(e, "close_all_positions failed")
    else:
        print("\n3.4. close_all_positions() - No positions to close")
        print_info("All positions already closed")

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # FINAL CHECK
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "-" * 80)
    print("FINAL STATUS CHECK")
    print("-" * 80)

    await asyncio.sleep(1)
    final_count = await sugar.count_open_positions()
    print(f"\nFinal open positions count: {final_count}")

    if final_count == 0:
        print(" All test positions successfully closed!")
    else:
        print(f"  [WARN] {final_count} position(s) still open")


    # ══════════════════════════════════════════════════════════════════════════════
    # CLEANUP: DISCONNECT
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("CLEANUP: Disconnecting...")
    print("=" * 80)

    try:
        await account.channel.close()
        print("✓ Disconnected successfully")
    except Exception as e:
        print(f"⚠️  Disconnect warning: {e}")


    # ══════════════════════════════════════════════════════════════════════════════
    # DEMO SUMMARY
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)

    print("\nMETHODS DEMONSTRATED (13 total):")
    print("   POSITION INFO (7):        has_open_position, count_open_positions,")
    print("                             get_open_positions, get_position_by_ticket,")
    print("                             get_positions_by_symbol, get_total_profit,")
    print("                             get_profit_by_symbol")
    print("   POSITION MODIFICATION (3): modify_position_sl, modify_position_tp,")
    print("                             modify_position_sltp")
    print("   POSITION CLOSING (3):     close_position, close_position_partial,")
    print("                             close_all_positions")

    print("\nMT5Sugar Position Management Features:")
    print("  • Position info: query, count, filter by ticket/symbol")
    print("  • Profit tracking: total and per-symbol floating P/L")
    print("  • SL/TP modification: modify_position_sl/tp/sltp methods")
    print("  • Flexible closing: full, partial, all, or by symbol")

    print("\nWHAT'S NEXT:")
    print("   [9]  History & Profits    → python main.py sugar09")
    print("   [10] Advanced Features    → python main.py sugar10")

    print("\n" + "=" * 80)


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    asyncio.run(run_sugar_positions_demo())
