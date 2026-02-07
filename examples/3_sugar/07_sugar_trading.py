"""==============================================================================
FILE: 07_sugar_trading.py - HIGH-LEVEL SUGAR API TRADING DEMO

🎯 PURPOSE:
  Demonstrates MT5Sugar trading operations: market and pending orders.
  ULTRA-SIMPLE one-liner trading methods for quick order execution!

WHO SHOULD USE THIS:
  - Quick trading scripts and bots
  - Simple order execution without complexity
  - Learning basic trading operations
  - Prototyping trading strategies

📚 WHAT THIS DEMO COVERS (3 Categories):

  1. SIMPLE MARKET TRADING (2 methods)
     - buy_market(symbol, volume) - Instant BUY
     - sell_market(symbol, volume) - Instant SELL

  2. PENDING ORDERS (4 methods)
     - buy_limit(symbol, volume, price) - BUY when price drops
     - sell_limit(symbol, volume, price) - SELL when price rises
     - buy_stop(symbol, volume, price) - BUY when price rises
     - sell_stop(symbol, volume, price) - SELL when price drops

  3. TRADING WITH SL/TP (4 methods)
     - buy_market_with_sltp() - Market BUY with Stop Loss & Take Profit
     - sell_market_with_sltp() - Market SELL with SL/TP
     - buy_limit_with_sltp() - Limit BUY with SL/TP
     - sell_limit_with_sltp() - Limit SELL with SL/TP

API LEVELS:
    HIGH-LEVEL (Sugar) - THIS FILE: One-liner trading, automatic defaults
    MID-LEVEL (Service): More parameters, custom settings
    LOW-LEVEL (Account): Full control, manual order construction

🚀 HOW TO RUN:
  cd examples
  python main.py sugar07              (or select [7] from menu)

⚠️ WARNING: This demo EXECUTES REAL TRADES on your account!
  - Uses minimum lot size from config (test_volume)
  - Opens positions and places pending orders for demonstration
  - Closes all positions and cancels pending orders at the end
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



async def run_sugar_trading_demo():
    """Run the Sugar trading demonstration."""

    print("\n" + "=" * 80)
    print("MT5 SUGAR API - TRADING DEMO (Market & Pending Orders)")
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

# IMPORTANT: Pause to stabilize the connection with the trading server
# The trading server requires more time than the quotation server
    print_info("Waiting for trade server synchronization (20 seconds)...")
    await asyncio.sleep(20)
    print_success("Trade server ready!")

    test_symbol = config['test_symbol']
    min_volume = config['test_volume']  # Minimum lot size

    # Lists to track opened positions and orders for cleanup
    opened_positions = []  # Market positions to close at the end

    # Get current price
    try:
        bid = await sugar.get_bid(test_symbol)
        ask = await sugar.get_ask(test_symbol)
        print(f"\nCurrent {test_symbol} prices: BID={bid:.5f}, ASK={ask:.5f}")
    except Exception as e:
        fatal(e, "Failed to get current price")
        return


    # ══════════════════════════════════════════════════════════════════════════════
    # region SIMPLE MARKET TRADING
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("1. SIMPLE MARKET TRADING")
    print("=" * 80)

    # ══════════════════════════════════════════════════════════════
    # 1.1. buy_market()
    #      Open BUY position at current market ASK price.
    #      Chain: Sugar → Service.send_order() → Account.order_send() → gRPC
    #      Returns: ticket number (int) of opened position.
    #      DANGEROUS operation - executes real trade!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    print(f"\n1.1. buy_market() - Open BUY position {min_volume:.2f} lots on {test_symbol}")

    try:
        buy_ticket = await sugar.buy_market(test_symbol, min_volume)
        print_success(f"BUY order opened! Ticket: {buy_ticket}")
        opened_positions.append(buy_ticket)
    except Exception as e:
        print_if_error(e, "buy_market failed")

    # Wait for server to process
    await asyncio.sleep(5)

    # ══════════════════════════════════════════════════════════════
    # 1.2. sell_market()
    #      Open SELL position at current market BID price.
    #      Chain: Sugar → Service.send_order() → Account.order_send() → gRPC
    #      Returns: ticket number (int) of opened position.
    #      DANGEROUS operation - executes real trade!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    print(f"\n1.2. sell_market() - Open SELL position {min_volume:.2f} lots on {test_symbol}")

    try:
        sell_ticket = await sugar.sell_market(test_symbol, min_volume)
        print_success(f"SELL order opened! Ticket: {sell_ticket}")
        opened_positions.append(sell_ticket)
    except Exception as e:
        print_if_error(e, "sell_market failed")

    # Wait for server to process
    await asyncio.sleep(5)

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region PENDING ORDERS
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("2. PENDING ORDERS (Limit & Stop)")
    print("=" * 80)

    # Get fresh prices
    bid = await sugar.get_bid(test_symbol)
    ask = await sugar.get_ask(test_symbol)

    # ══════════════════════════════════════════════════════════════
    # 2.1. buy_limit()
    #      Place BUY LIMIT pending order (executes when price drops).
    #      Chain: Sugar → Service.send_order() → Account.order_send() → gRPC
    #      Returns: ticket number (int) of pending order.
    #      DANGEROUS operation - places real pending order!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    buy_limit_price = bid - 0.0020  # 20 pips below current bid
    print(f"\n2.1. buy_limit() - Place BUY LIMIT at {buy_limit_price:.5f}")

    try:
        buy_limit_ticket = await sugar.buy_limit(test_symbol, min_volume, buy_limit_price)
        print_success(f"BUY LIMIT placed! Ticket: {buy_limit_ticket}")
        print(f"  Will execute if price drops to {buy_limit_price:.5f}")
    except Exception as e:
        print_if_error(e, "buy_limit failed")

    # Wait for server to process
    await asyncio.sleep(5)

    # ══════════════════════════════════════════════════════════════
    # 2.2. sell_limit()
    #      Place SELL LIMIT pending order (executes when price rises).
    #      Chain: Sugar → Service.send_order() → Account.order_send() → gRPC
    #      Returns: ticket number (int) of pending order.
    #      DANGEROUS operation - places real pending order!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    sell_limit_price = ask + 0.0020  # 20 pips above current ask
    print(f"\n2.2. sell_limit() - Place SELL LIMIT at {sell_limit_price:.5f}")

    try:
        sell_limit_ticket = await sugar.sell_limit(test_symbol, min_volume, sell_limit_price)
        print_success(f"SELL LIMIT placed! Ticket: {sell_limit_ticket}")
        print(f"  Will execute if price rises to {sell_limit_price:.5f}")
    except Exception as e:
        print_if_error(e, "sell_limit failed")

    await asyncio.sleep(5)

    # ══════════════════════════════════════════════════════════════
    # 2.3. buy_stop()
    #      Place BUY STOP pending order (executes when price rises).
    #      Chain: Sugar → Service.send_order() → Account.order_send() → gRPC
    #      Returns: ticket number (int) of pending order.
    #      DANGEROUS operation - places real pending order!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    buy_stop_price = ask + 0.0020  # 20 pips above current ask
    print(f"\n2.3. buy_stop() - Place BUY STOP at {buy_stop_price:.5f}")

    try:
        buy_stop_ticket = await sugar.buy_stop(test_symbol, min_volume, buy_stop_price)
        print_success(f"BUY STOP placed! Ticket: {buy_stop_ticket}")
        print(f"  Will execute if price rises to {buy_stop_price:.5f}")
    except Exception as e:
        print_if_error(e, "buy_stop failed")

    await asyncio.sleep(5)

    # ══════════════════════════════════════════════════════════════
    # 2.4. sell_stop()
    #      Place SELL STOP pending order (executes when price drops).
    #      Chain: Sugar → Service.send_order() → Account.order_send() → gRPC
    #      Returns: ticket number (int) of pending order.
    #      DANGEROUS operation - places real pending order!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    sell_stop_price = bid - 0.0020  # 20 pips below current bid
    print(f"\n2.4. sell_stop() - Place SELL STOP at {sell_stop_price:.5f}")

    try:
        sell_stop_ticket = await sugar.sell_stop(test_symbol, min_volume, sell_stop_price)
        print_success(f"SELL STOP placed! Ticket: {sell_stop_ticket}")
        print(f"  Will execute if price drops to {sell_stop_price:.5f}")
    except Exception as e:
        print_if_error(e, "sell_stop failed")

    await asyncio.sleep(5)

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region TRADING WITH SL/TP
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("3. TRADING WITH SL/TP (Stop Loss & Take Profit)")
    print("=" * 80)

    # Get fresh prices
    bid = await sugar.get_bid(test_symbol)
    ask = await sugar.get_ask(test_symbol)

    # ══════════════════════════════════════════════════════════════
    # 3.1. buy_market_with_sltp()
    #      Open BUY position with Stop Loss and Take Profit.
    #      Chain: Sugar → Service.send_order() → Account.order_send() → gRPC
    #      Returns: ticket number (int) of opened position.
    #      DANGEROUS operation - executes real trade with SL/TP!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    stop_loss = bid - 0.0030     # 30 pips SL
    take_profit = bid + 0.0050   # 50 pips TP
    print(f"\n3.1. buy_market_with_sltp() - BUY with SL/TP")
    print(f"  Entry: {ask:.5f}, SL: {stop_loss:.5f} (-30 pips), TP: {take_profit:.5f} (+50 pips)")

    try:
        buy_sltp_ticket = await sugar.buy_market_with_sltp(
            test_symbol,
            min_volume,
            sl=stop_loss,
            tp=take_profit
        )
        print_success(f"BUY with SL/TP opened! Ticket: {buy_sltp_ticket}")
        opened_positions.append(buy_sltp_ticket)
    except Exception as e:
        print_if_error(e, "buy_market_with_sltp failed")

    # Wait for server to process
    await asyncio.sleep(5)

    # ══════════════════════════════════════════════════════════════
    # 3.2. sell_market_with_sltp()
    #      Open SELL position with Stop Loss and Take Profit.
    #      Chain: Sugar → Service.send_order() → Account.order_send() → gRPC
    #      Returns: ticket number (int) of opened position.
    #      DANGEROUS operation - executes real trade with SL/TP!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    stop_loss_sell = ask + 0.0030     # 30 pips SL
    take_profit_sell = ask - 0.0050   # 50 pips TP
    print(f"\n3.2. sell_market_with_sltp() - SELL with SL/TP")
    print(f"  Entry: {bid:.5f}, SL: {stop_loss_sell:.5f} (+30 pips), TP: {take_profit_sell:.5f} (-50 pips)")

    try:
        sell_sltp_ticket = await sugar.sell_market_with_sltp(
            test_symbol,
            min_volume,
            sl=stop_loss_sell,
            tp=take_profit_sell
        )
        print_success(f"SELL with SL/TP opened! Ticket: {sell_sltp_ticket}")
        opened_positions.append(sell_sltp_ticket)
    except Exception as e:
        print_if_error(e, "sell_market_with_sltp failed")

    await asyncio.sleep(5)

    # ══════════════════════════════════════════════════════════════
    # 3.3. buy_limit_with_sltp()
    #      Place BUY LIMIT pending order with SL/TP.
    #      Chain: Sugar → Service.send_order() → Account.order_send() → gRPC
    #      Returns: ticket number (int) of pending order.
    #      DANGEROUS operation - places real pending order with SL/TP!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    buy_limit_sltp_price = bid - 0.0020
    stop_loss_buy_limit = buy_limit_sltp_price - 0.0030
    take_profit_buy_limit = buy_limit_sltp_price + 0.0050
    print(f"\n3.3. buy_limit_with_sltp() - BUY LIMIT with SL/TP")
    print(f"  Entry: {buy_limit_sltp_price:.5f}, SL: {stop_loss_buy_limit:.5f}, TP: {take_profit_buy_limit:.5f}")

    try:
        buy_limit_sltp_ticket = await sugar.buy_limit_with_sltp(
            test_symbol,
            min_volume,
            buy_limit_sltp_price,
            sl=stop_loss_buy_limit,
            tp=take_profit_buy_limit
        )
        print_success(f"BUY LIMIT with SL/TP placed! Ticket: {buy_limit_sltp_ticket}")
    except Exception as e:
        print_if_error(e, "buy_limit_with_sltp failed")

    await asyncio.sleep(5)

    # ══════════════════════════════════════════════════════════════
    # 3.4. sell_limit_with_sltp()
    #      Place SELL LIMIT pending order with SL/TP.
    #      Chain: Sugar → Service.send_order() → Account.order_send() → gRPC
    #      Returns: ticket number (int) of pending order.
    #      DANGEROUS operation - places real pending order with SL/TP!
    #      Timeout: 10 seconds
    # ══════════════════════════════════════════════════════════════
    sell_limit_sltp_price = ask + 0.0020
    stop_loss_sell_limit = sell_limit_sltp_price + 0.0030
    take_profit_sell_limit = sell_limit_sltp_price - 0.0050
    print(f"\n3.4. sell_limit_with_sltp() - SELL LIMIT with SL/TP")
    print(f"  Entry: {sell_limit_sltp_price:.5f}, SL: {stop_loss_sell_limit:.5f}, TP: {take_profit_sell_limit:.5f}")

    try:
        sell_limit_sltp_ticket = await sugar.sell_limit_with_sltp(
            test_symbol,
            min_volume,
            sell_limit_sltp_price,
            sl=stop_loss_sell_limit,
            tp=take_profit_sell_limit
        )
        print_success(f"SELL LIMIT with SL/TP placed! Ticket: {sell_limit_sltp_ticket}")
    except Exception as e:
        print_if_error(e, "sell_limit_with_sltp failed")

    await asyncio.sleep(5)

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region CLEANUP - CLOSE ALL POSITIONS AND PENDING ORDERS
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "-" * 80)
    print("4. CLEANUP - Closing positions and canceling pending orders")
    print("-" * 80)

    # 4.1. Close market positions
    if opened_positions:
        print(f"\n  Closing {len(opened_positions)} market position(s)...")
        closed_count = 0
        for ticket in opened_positions:
            print(f"  Closing position #{ticket}...")
            try:
                success = await sugar.close_position(ticket)
                if success:
                    print("    [+] Closed")
                    closed_count += 1
                else:
                    print("    [!] Failed")
            except Exception as e:
                print_if_error(e, "Failed to close position")
            await asyncio.sleep(1)  # Small delay between closes

        if closed_count > 0:
            print(f"\n  [+] Closed {closed_count} position(s)")
    else:
        print_info("No market positions to close")

    # Wait for server to process closes
    await asyncio.sleep(2)

    # 4.2. Cancel pending orders
    try:
        # Get all opened orders (should be only pending now)
        opened_data = await service.get_opened_orders(sort_mode=0)

        if opened_data.opened_orders:
            print(f"\n  Canceling {len(opened_data.opened_orders)} pending order(s)...")
            cancel_count = 0
            for pending in opened_data.opened_orders:
                ticket = pending.ticket
                print(f"  Canceling pending order #{ticket}...")

                try:
                    # Use Service's close_order to delete pending order
                    from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as trading_helper_pb2
                    close_req = trading_helper_pb2.OrderCloseRequest(ticket=ticket)
                    ret_code = await service.close_order(close_req)

                    if ret_code == 10009:
                        print("    [+] Canceled")
                        cancel_count += 1
                    else:
                        print(f"    [!] Return code: {ret_code}")
                except Exception as e:
                    print_if_error(e, "Failed to cancel order")
                await asyncio.sleep(1)  # Small delay between cancels

            if cancel_count > 0:
                print(f"\n  [+] Canceled {cancel_count} pending order(s)")
        else:
            print_info("No pending orders to cancel")

    except Exception as e:
        print_if_error(e, "Failed to get opened orders")

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # CLEANUP: DISCONNECT
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("CLEANUP: Disconnecting...")
    print("=" * 80)

    try:
        await account.channel.close()
        print("[OK] Disconnected successfully")
    except Exception as e:
        print(f"[WARN] Disconnect warning: {e}")


    # ══════════════════════════════════════════════════════════════════════════════
    # DEMO SUMMARY
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)

    print("\nMETHODS DEMONSTRATED (10 total):")
    print("   SIMPLE MARKET TRADING (2):  buy_market, sell_market")
    print("   PENDING ORDERS (4):         buy_limit, sell_limit, buy_stop, sell_stop")
    print("   TRADING WITH SL/TP (4):     buy_market_with_sltp, sell_market_with_sltp,")
    print("                               buy_limit_with_sltp, sell_limit_with_sltp")

    print("\nMT5Sugar Trading Features:")
    print("  - Simple market orders: buy_market/sell_market (2 params: symbol, volume)")
    print("  - Pending orders: buy_limit/sell_limit/buy_stop/sell_stop (3 params: symbol, volume, price)")
    print("  - Direct ticket returns: ticket = await sugar.buy_market(...)")
    print("  - Automatic SL/TP handling in *_with_sltp methods")

    print("\nWHAT'S NEXT:")
    print("   [8]  Position Management  → python main.py sugar08")
    print("   [9]  History & Profits    → python main.py sugar09")
    print("   [10] Advanced Features    → python main.py sugar10")

    print("\n" + "=" * 80)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    asyncio.run(run_sugar_trading_demo())
