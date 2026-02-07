"""==============================================================================
FILE: 09_sugar_history.py - HIGH-LEVEL SUGAR API HISTORY & PROFITS DEMO

🎯 PURPOSE:
  Demonstrates MT5Sugar historical data methods: deals and profit calculations.
  QUICK access to trading history with pre-defined time ranges!

WHO SHOULD USE THIS:
  - Daily/weekly/monthly performance tracking
  - Building trading statistics and reports
  - Analyzing historical performance
  - Quick profit/loss calculations

📚 WHAT THIS DEMO COVERS (2 Categories):

  1. HISTORICAL DEALS METHODS (5 methods)
     - get_deals_today() - All deals from today
     - get_deals_yesterday() - Yesterday's deals
     - get_deals_this_week() - Current week deals
     - get_deals_this_month() - Current month deals
     - get_deals_date_range(from, to) - Custom date range

  2. PROFIT CALCULATION METHODS (3 methods)
     - get_profit_today() - Today's total profit
     - get_profit_this_week() - This week's profit
     - get_profit_this_month() - This month's profit

BONUS FEATURES DEMONSTRATED:
  - Win/Loss ratio calculation
  - Trade statistics (count, volume, profitability)
  - Sample deals display with formatting

API LEVELS:
    HIGH-LEVEL (Sugar) - THIS FILE: Pre-defined time ranges, automatic calculations
    MID-LEVEL (Service): Custom time ranges, manual filtering
    LOW-LEVEL (Account): Full control, protobuf timestamps

🚀 HOW TO RUN:
  cd examples
  python main.py sugar09              (or select [9] from menu)

⚠️ WARNING: This demo CREATES TEST HISTORY!
  - Opens and closes 2 test positions (BUY/SELL)
  - Generates sample deals for demonstration
  - Recommended to run on DEMO account first
=============================================================================="""

import asyncio
import sys
import os
from datetime import date, timedelta

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
    fatal,
)

# Import MT5Sugar
from pymt5.mt5_sugar import MT5Sugar
from pymt5.mt5_service import MT5Service



async def run_sugar_history_demo():
    """Run the Sugar history & profits demonstration."""

    print("\n" + "=" * 80)
    print("MT5 SUGAR API - HISTORY DEMO (Historical Deals & Profits)")
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

    test_symbol = config['test_symbol']
    min_volume = config.get('test_volume', 0.01)


    # ══════════════════════════════════════════════════════════════════════════════
    # region PREPARATION: Create history
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "-" * 80)
    print("PREPARATION: Creating test trade history")
    print("-" * 80)

    print("\nExecuting test trades to generate history...")

    # Trade 1: Quick BUY/CLOSE
    try:
        ticket1 = await sugar.buy_market(test_symbol, min_volume)
        print_success(f"Opened BUY #{ticket1}")
        await asyncio.sleep(2)

        success = await sugar.close_position(ticket1)
        if success:
            print_success(f"Closed BUY #{ticket1}")
    except Exception as e:
        print_if_error(e, "Failed to open/close BUY")

    await asyncio.sleep(1)

    # Trade 2: Quick SELL/CLOSE
    try:
        ticket2 = await sugar.sell_market(test_symbol, min_volume)
        print_success(f"Opened SELL #{ticket2}")
        await asyncio.sleep(2)

        success = await sugar.close_position(ticket2)
        if success:
            print_success(f"Closed SELL #{ticket2}")
    except Exception as e:
        print_if_error(e, "Failed to open/close SELL")

    print_success("Test history created!")
    await asyncio.sleep(2)  # Let server register deals

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region HISTORICAL DEALS METHODS
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "-" * 80)
    print("1. HISTORICAL DEALS METHODS")
    print("-" * 80)

    # ══════════════════════════════════════════════════════════════
    # 1.1. get_deals_today()
    #      Get all closed positions (deals) executed today (from midnight).
    #      Chain: Sugar -> Service.get_order_history() -> Account -> gRPC
    #      Returns: List[Order] - list of today's deals.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n1.1. get_deals_today() - All deals from today")

    try:
        deals_today = await sugar.get_deals_today()
        print(f"  Found {len(deals_today)} deal(s) today:")
        for i, deal in enumerate(deals_today[:5], 1):  # Show first 5
            print(f"    {i}. Position #{deal.position_ticket}: {deal.volume:.2f} lots, Profit: {deal.profit:.2f}")
        if len(deals_today) > 5:
            print(f"  ... and {len(deals_today) - 5} more")
    except Exception as e:
        print_if_error(e, "get_deals_today failed")

    # ══════════════════════════════════════════════════════════════
    # 1.2. get_deals_yesterday()
    #      Get all closed positions from yesterday (full day: 00:00 to 23:59:59).
    #      Chain: Sugar -> Service.get_order_history() -> Account -> gRPC
    #      Returns: List[Order] - list of yesterday's deals.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n1.2. get_deals_yesterday() - All deals from yesterday")

    try:
        deals_yesterday = await sugar.get_deals_yesterday()
        if len(deals_yesterday) == 0:
            print("  No deals yesterday")
        else:
            print(f"  Found {len(deals_yesterday)} deal(s) yesterday")
    except Exception as e:
        print_if_error(e, "get_deals_yesterday failed")

    # ══════════════════════════════════════════════════════════════
    # 1.3. get_deals_this_week()
    #      Get all closed positions from this week (Monday 00:00 to now).
    #      Chain: Sugar -> Service.get_order_history() -> Account -> gRPC
    #      Returns: List[Order] - list of this week's deals.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n1.3. get_deals_this_week() - All deals from this week")

    try:
        deals_week = await sugar.get_deals_this_week()
        print(f"  Found {len(deals_week)} deal(s) this week")
    except Exception as e:
        print_if_error(e, "get_deals_this_week failed")

    # ══════════════════════════════════════════════════════════════
    # 1.4. get_deals_this_month()
    #      Get all closed positions from this month (1st day 00:00 to now).
    #      Chain: Sugar -> Service.get_order_history() -> Account -> gRPC
    #      Returns: List[Order] - list of this month's deals.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n1.4. get_deals_this_month() - All deals from this month")

    try:
        deals_month = await sugar.get_deals_this_month()
        print(f"  Found {len(deals_month)} deal(s) this month")
    except Exception as e:
        print_if_error(e, "get_deals_this_month failed")

    # ══════════════════════════════════════════════════════════════
    # 1.5. get_deals_date_range()
    #      Get all closed positions within custom date range (from - to).
    #      Chain: Sugar -> Service.get_order_history() -> Account -> gRPC
    #      Returns: List[Order] - list of deals in date range.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n1.5. get_deals_date_range() - Custom date range (last 7 days)")

    try:
        today = date.today()
        week_ago = today - timedelta(days=7)
        deals_range = await sugar.get_deals_date_range(week_ago, today)
        print(f"  Found {len(deals_range)} deal(s) in last 7 days")
        print(f"  Date range: {week_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")
    except Exception as e:
        print_if_error(e, "get_deals_date_range failed")

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region PROFIT CALCULATION METHODS
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "-" * 80)
    print("2. PROFIT CALCULATION METHODS")
    print("-" * 80)

    # ══════════════════════════════════════════════════════════════
    # 2.1. get_profit_today()
    #      Calculate total profit/loss from all deals closed today.
    #      Chain: Sugar -> get_deals_today() -> Service -> Account -> gRPC
    #      Returns: float - sum of profit from today's deals.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n2.1. get_profit_today() - Total profit from today's deals")

    try:
        profit_today = await sugar.get_profit_today()
        if profit_today >= 0:
            print(f"  Today's profit: +{profit_today:.2f}")
        else:
            print(f"  Today's profit: {profit_today:.2f}")
    except Exception as e:
        print_if_error(e, "get_profit_today failed")

    # ══════════════════════════════════════════════════════════════
    # 2.2. get_profit_this_week()
    #      Calculate total profit/loss from all deals closed this week.
    #      Chain: Sugar -> get_deals_this_week() -> Service -> Account -> gRPC
    #      Returns: float - sum of profit from this week's deals.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n2.2. get_profit_this_week() - Total profit from this week")

    try:
        profit_week = await sugar.get_profit_this_week()
        if profit_week >= 0:
            print(f"  This week's profit: +{profit_week:.2f}")
        else:
            print(f"  This week's profit: {profit_week:.2f}")
    except Exception as e:
        print_if_error(e, "get_profit_this_week failed")

    # ══════════════════════════════════════════════════════════════
    # 2.3. get_profit_this_month()
    #      Calculate total profit/loss from all deals closed this month.
    #      Chain: Sugar -> get_deals_this_month() -> Service -> Account -> gRPC
    #      Returns: float - sum of profit from this month's deals.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print("\n2.3. get_profit_this_month() - Total profit from this month")

    try:
        profit_month = await sugar.get_profit_this_month()
        if profit_month >= 0:
            print(f"  This month's profit: +{profit_month:.2f}")
        else:
            print(f"  This month's profit: {profit_month:.2f}")
    except Exception as e:
        print_if_error(e, "get_profit_this_month failed")

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region DETAILED DEALS ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "-" * 80)
    print("3. DETAILED DEALS ANALYSIS (Today)")
    print("-" * 80)

    try:
        deals_today = await sugar.get_deals_today()

        if len(deals_today) > 0:
            print(f"\nAnalyzing {len(deals_today)} deal(s) from today:")

            total_profit = 0.0
            total_volume = 0.0
            win_count = 0
            loss_count = 0

            for deal in deals_today:
                total_profit += deal.profit
                total_volume += deal.volume

                if deal.profit > 0:
                    win_count += 1
                elif deal.profit < 0:
                    loss_count += 1

            print("\n=== Statistics ===")
            print(f"  Total deals:  {len(deals_today)}")
            print(f"  Winning:      {win_count} ({win_count/len(deals_today)*100:.1f}%)")
            print(f"  Losing:       {loss_count} ({loss_count/len(deals_today)*100:.1f}%)")
            print(f"  Total volume: {total_volume:.2f} lots")

            if total_profit >= 0:
                print(f"  Net profit:   +{total_profit:.2f} ")
            else:
                print(f"  Net profit:   {total_profit:.2f} [X]")

            # Show sample deals
            print("\n  Sample deals (max 10):")
            for i, deal in enumerate(deals_today[:10], 1):
                profit_str = f"{deal.profit:.2f}"
                if deal.profit > 0:
                    profit_str = "+" + profit_str

                print(f"  {i:2d}. Position #{deal.position_ticket} | {deal.volume:.2f} lots | {profit_str}")

            if len(deals_today) > 10:
                print(f"  ... and {len(deals_today) - 10} more")
        else:
            print("\n  No deals found today to analyze")
            print("   (The test trades may take a few seconds to appear in history)")

    except Exception as e:
        print_if_error(e, "Failed to analyze deals")

    # endregion


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

    print("\nMETHODS DEMONSTRATED (8 total):")
    print("   HISTORICAL DEALS (5):     get_deals_today, get_deals_yesterday,")
    print("                             get_deals_this_week, get_deals_this_month,")
    print("                             get_deals_date_range")
    print("   PROFIT CALCULATION (3):   get_profit_today, get_profit_this_week,")
    print("                             get_profit_this_month")

    print("\nMT5Sugar History Features:")
    print("  • Time-based queries: pre-defined ranges (today, yesterday, week, month)")
    print("  • Custom date ranges: get_deals_date_range(from, to)")
    print("  • Automatic profit calculation: sum profit from deals in time range")
    print("  • Returns: List[Order] with detailed deal information")

    print("\nWHAT'S NEXT:")
    print("   [10] Advanced Features    → python main.py sugar10")

    print("\n[OK] SUGAR API COMPLETE!")
    print("   You've now seen all demo categories:")
    print("   • 06_sugar_basics.py - Connection, Balance, Prices (read-only)")
    print("   • 07_sugar_trading.py - Market & Pending Orders")
    print("   • 08_sugar_positions.py - Position Management & Info")
    print("   • 09_sugar_history.py - Historical Deals & Profits")

    print("\n" + "=" * 80)


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    asyncio.run(run_sugar_history_demo())
