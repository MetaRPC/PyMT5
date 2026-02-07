"""==============================================================================
FILE: 10_sugar_advanced.py - ADVANCED SUGAR API DEMO (RISK MANAGEMENT & MORE)

🎯 PURPOSE:
  Demonstrates NEW advanced MT5Sugar methods for risk management, symbol info,
  trading helpers, and account analytics. Professional risk management made EASY!

WHO SHOULD USE THIS:
  - Professional traders using proper risk management
  - Anyone wanting automated position sizing
  - Traders working with multiple symbols
  - Performance tracking and account monitoring

📚 WHAT THIS DEMO COVERS (4 Categories, 10 methods total):

  1. ACCOUNT INFORMATION (2 methods)
     - get_account_info() - Complete account snapshot
     - get_daily_stats() - Today's trading statistics

  2. SYMBOL INFORMATION (3 methods)
     - get_symbol_info(symbol) - Complete symbol data
     - is_symbol_available(symbol) - Check symbol tradability
     - get_all_symbols() - List all available symbols

  3. RISK MANAGEMENT (4 methods)
     - calculate_position_size(symbol, risk%, SL_pips) - Auto position sizing
     - get_max_lot_size(symbol) - Maximum tradeable volume
     - can_open_position(symbol, volume) - Pre-trade validation
     - calculate_required_margin(symbol, volume) - Margin calculation

  4. TRADING HELPERS (1 method)
     - calculate_sltp(symbol, is_buy, sl_pips, tp_pips) - SL/TP from pips

💡 KEY FEATURES DEMONSTRATED:
  - Professional risk management (risk 2% per trade)
  - Automated position sizing based on account balance
  - Pre-trade validation to prevent errors
  - Working with pips instead of raw prices
  - Comprehensive account analytics

API LEVELS:
    HIGH-LEVEL (Sugar) - THIS FILE: One-liners, smart defaults, automatic calculations
    MID-LEVEL (Service): More control, native Python types
    LOW-LEVEL (Account): Full control, protobuf structures

🚀 HOW TO RUN:
  cd examples
  python main.py sugar10              (or select [10] from menu)

⚠️  TRADING DEMO WARNING:
  - This demo performs MOSTLY READ-ONLY operations
  - EXCEPTION: Opens 1 REAL minimal test position (0.01 lots) at the end
  - The test trade uses proper risk management (SL/TP included)
  - Recommended for DEMO accounts
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
    print_warning,
    print_info,
    fatal,
)

# Import MT5Sugar
from pymt5.mt5_sugar import MT5Sugar
from pymt5.mt5_service import MT5Service



def print_section(title: str):
    """Print section header"""
    print("\n" + "-" * 80)
    print(title)
    print("-" * 80)


async def run_sugar_advanced_demo():
    """Run the Sugar advanced features demonstration."""

    print("\n" + "=" * 80)
    print("MT5 SUGAR API - ADVANCED FEATURES DEMO (Risk Management)")
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
    print_success("Connected successfully!")

    # IMPORTANT: Pause to stabilize the connection with the trading server
    print_info("Waiting for trade server synchronization (20 seconds)...")
    await asyncio.sleep(20)
    print_success("Trade server ready!")

    symbol = config['test_symbol']


    # ══════════════════════════════════════════════════════════════════════════════
    # region ACCOUNT INFORMATION
    # ══════════════════════════════════════════════════════════════════════════════
    print_section("1. ACCOUNT INFORMATION - Complete Snapshot")

    # ══════════════════════════════════════════════════════════════
    # 1.1. get_account_info()
    #      Get complete account snapshot with all account properties.
    #      Chain: Sugar → Service.get_account_summary() → Account → gRPC
    #      Returns: AccountInfo dataclass with all account data.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    try:
        account_info = await sugar.get_account_info()
        print_success("get_account_info()", "Complete account data retrieved")
        print(f"    Account Login:    {account_info.login}")
        print(f"    Balance:          {account_info.balance:.2f} {account_info.currency}")
        print(f"    Equity:           {account_info.equity:.2f} {account_info.currency}")
        print(f"    Margin Used:      {account_info.margin:.2f} {account_info.currency}")
        print(f"    Free Margin:      {account_info.free_margin:.2f} {account_info.currency}")
        print(f"    Margin Level:     {account_info.margin_level:.2f}%")
        print(f"    Floating P/L:     {account_info.profit:.2f} {account_info.currency}")
        print(f"    Leverage:         1:{account_info.leverage}")
        print(f"    Broker:           {account_info.company}")
        print()
    except Exception as e:
        print_if_error(e, "get_account_info failed")
        return


    # ══════════════════════════════════════════════════════════════
    # 1.2. get_daily_stats()
    #      Calculate today's trading statistics (profit, deals, volume).
    #      Chain: Sugar → get_deals_today() → Service.get_order_history() → Account → gRPC
    #      Returns: DailyStats dataclass with aggregated statistics.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    print_section("2. DAILY STATISTICS - Today's Performance")

    try:
        stats = await sugar.get_daily_stats()
        print_success("get_daily_stats()", "Today's statistics calculated")
        print(f"    Total Deals:      {stats.deals_count}")
        print(f"    Total Profit:     {stats.profit:.2f} {account_info.currency}")
        print(f"    Commission:       {stats.commission:.2f} {account_info.currency}")
        print(f"    Swap:             {stats.swap:.2f} {account_info.currency}")
        print(f"    Total Volume:     {stats.volume:.2f} lots")
        print()
    except Exception as e:
        print_if_error(e, "get_daily_stats failed")


    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region SYMBOL INFORMATION
    # ══════════════════════════════════════════════════════════════════════════════
    print_section("3. SYMBOL INFORMATION - Comprehensive Symbol Data")

    # ══════════════════════════════════════════════════════════════
    # 2.1. get_symbol_info()
    #      Get complete symbol information (prices, limits, specs).
    #      Chain: Sugar → Service.get_symbol_params() → Account → gRPC
    #      Returns: SymbolInfo dataclass with all symbol properties.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    try:
        symbol_info = await sugar.get_symbol_info(symbol)
        print_success(f"get_symbol_info(\"{symbol}\")", "Complete symbol data retrieved")
        print(f"    Symbol:           {symbol_info.name}")
        print(f"    BID:              {symbol_info.bid:.5f}")
        print(f"    ASK:              {symbol_info.ask:.5f}")
        print(f"    Spread:           {symbol_info.spread} points")
        print(f"    Digits:           {symbol_info.digits}")
        print(f"    Point:            {symbol_info.point:.5f}")
        print(f"    Volume Min:       {symbol_info.volume_min:.2f}")
        print(f"    Volume Max:       {symbol_info.volume_max:.2f}")
        print(f"    Volume Step:      {symbol_info.volume_step:.2f}")
        print(f"    Contract Size:    {symbol_info.contract_size:.0f}")
        print()
    except Exception as e:
        print_if_error(e, "get_symbol_info failed")
        return

    # ══════════════════════════════════════════════════════════════
    # 2.2. is_symbol_available()
    #      Check if symbol is available for trading.
    #      Chain: Sugar → Service.symbol_exist() → Account → gRPC
    #      Returns: bool - True if symbol is available.
    #      SAFE operation - read-only query.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    try:
        available = await sugar.is_symbol_available(symbol)
        if available:
            print_success(f"is_symbol_available(\"{symbol}\")", "Symbol is available for trading")
        else:
            print_warning(f"is_symbol_available(\"{symbol}\")", "Symbol is NOT available")
    except Exception as e:
        print_if_error(e, "is_symbol_available failed")

    # ══════════════════════════════════════════════════════════════
    # 2.3. get_all_symbols()
    #      Get list of all available symbols on the server.
    #      Chain: Sugar → Service.get_symbols_total() + symbol_name() → Account → gRPC
    #      Returns: List[str] - list of all symbol names.
    #      SAFE operation - read-only query.
    #      Timeout: 60 seconds (may take time for large symbol lists)
    # ══════════════════════════════════════════════════════════════
    print("    Loading all symbols (may take 10-60 seconds)...", end='', flush=True)
    try:
        all_symbols = await sugar.get_all_symbols()
        print(" Done!")
        print_success("get_all_symbols()", f"Found {len(all_symbols)} symbols")
        print(f"   First 10 symbols: {' '.join(all_symbols[:10])}...")
        print()
    except Exception as e:
        print_if_error(e, "get_all_symbols failed")


    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region RISK MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════════════
    print_section("4. RISK MANAGEMENT - Professional Position Sizing")

    # ══════════════════════════════════════════════════════════════
    # 3.1. calculate_position_size()
    #      Calculate optimal position size based on risk percentage and stop loss.
    #      Chain: Sugar → Service (get_account_summary + get_symbol_params + calc) → Account → gRPC
    #      Returns: float - recommended lot size for specified risk.
    #      SAFE operation - calculation only, no trades.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    risk_percent = 2.0
    stop_loss_pips = 50.0

    try:
        lot_size = await sugar.calculate_position_size(symbol, risk_percent, stop_loss_pips)
        print_success(
            f"calculate_position_size(\"{symbol}\", {risk_percent:.1f}%, {stop_loss_pips:.0f} pips)",
            f"Recommended lot size: {lot_size:.2f}"
        )

        risk_amount = account_info.balance * risk_percent / 100.0
        print(f"    Balance:          {account_info.balance:.2f} {account_info.currency}")
        print(f"    Risk Amount:      {risk_amount:.2f} {account_info.currency} ({risk_percent:.1f}%)")
        print(f"    Stop Loss:        {stop_loss_pips:.0f} pips")
        print(f"    Position Size:    {lot_size:.2f} lots")
        print(f"    If SL hits, you lose exactly {risk_amount:.2f} {account_info.currency} ({risk_percent:.1f}% of balance)")
        print()
    except Exception as e:
        print_if_error(e, "calculate_position_size failed")

    # ══════════════════════════════════════════════════════════════
    # 3.2. get_max_lot_size()
    #      Calculate maximum tradeable lot size based on free margin.
    #      Chain: Sugar → Service (get_account_summary + order_calc_margin) → Account → gRPC
    #      Returns: float - maximum lot size account can afford.
    #      SAFE operation - calculation only, no trades.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    try:
        max_lots = await sugar.get_max_lot_size(symbol)
        print_success(f"get_max_lot_size(\"{symbol}\")", f"Max lots: {max_lots:.2f}")
        print(f"    Free Margin:      {account_info.free_margin:.2f} {account_info.currency}")
        print(f"    Maximum Lots:     {max_lots:.2f}")
        print()
    except Exception as e:
        print_if_error(e, "get_max_lot_size failed")

    # ══════════════════════════════════════════════════════════════
    # 3.3. can_open_position()
    #      Pre-trade validation: checks margin, symbol availability, volume limits.
    #      Chain: Sugar → Service (multiple checks) → Account → gRPC
    #      Returns: (bool, str) - (can_open, reason_if_not).
    #      SAFE operation - validation only, no trades.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    test_volume = 0.1
    try:
        can_open, reason = await sugar.can_open_position(symbol, test_volume)
        if can_open:
            print_success(
                f"can_open_position(\"{symbol}\", {test_volume:.2f})",
                "[OK] Position CAN be opened - all checks passed"
            )

        else:
            print_warning(
                f"can_open_position(\"{symbol}\", {test_volume:.2f})",
                f"[X] Position CANNOT be opened: {reason}"
            )
            
    except Exception as e:
        print_if_error(e, "can_open_position failed")

    # ══════════════════════════════════════════════════════════════
    # 3.4. calculate_required_margin()
    #      Calculate margin required to open position with given volume.
    #      Chain: Sugar → Service.order_calc_margin() → Account → gRPC
    #      Returns: float - required margin in account currency.
    #      SAFE operation - calculation only, no trades.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    try:
        required_margin = await sugar.calculate_required_margin(symbol, test_volume)
        print_success(
            f"calculate_required_margin(\"{symbol}\", {test_volume:.2f})",
            f"Required margin: {required_margin:.2f} {account_info.currency}"
        )
        print()
    except Exception as e:
        print_if_error(e, "calculate_required_margin failed")


    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region TRADING HELPERS
    # ══════════════════════════════════════════════════════════════════════════════
    print_section("5. TRADING HELPERS - Pip-Based SL/TP Calculation")

    # ══════════════════════════════════════════════════════════════
    # 4.1. calculate_sltp()
    #      Calculate exact SL/TP prices from pip values.
    #      Chain: Sugar → Service.get_symbol_tick() + get_symbol_params() → Account → gRPC
    #      Returns: (float, float) - (stop_loss_price, take_profit_price).
    #      SAFE operation - calculation only, no trades.
    #      Timeout: 5 seconds
    # ══════════════════════════════════════════════════════════════
    is_buy = True  # BUY direction
    sl_pips = 50.0
    tp_pips = 100.0

    try:
        sl, tp = await sugar.calculate_sltp(symbol, is_buy, sl_pips, tp_pips)
        current_ask = await sugar.get_ask(symbol)
        print_success(
            f"calculate_sltp(\"{symbol}\", BUY, {sl_pips:.0f}, {tp_pips:.0f})",
            "SL/TP prices calculated from pips"
        )
        print(f"    Current ASK:      {current_ask:.5f}")
        print(f"    Stop Loss:        {sl:.5f} ({sl_pips:.0f} pips below entry)")
        print(f"    Take Profit:      {tp:.5f} ({tp_pips:.0f} pips above entry)")
        print(f"    Risk/Reward:      1:{tp_pips/sl_pips:.1f}")
        print()
    except Exception as e:
        print_if_error(e, "calculate_sltp failed")

    # Demonstrate BuyMarketWithPips and SellMarketWithPips
    print_info("OPTIONAL TRADING DEMO", "You can test pip-based trading methods:")
    print(f"   Example 1: sugar.buy_market_with_pips(\"{symbol}\", 0.01, 50, 100)")
    print(f"              Opens BUY 0.01 lots, SL=50 pips, TP=100 pips")
    print()
    print(f"   Example 2: sugar.sell_market_with_pips(\"{symbol}\", 0.01, 50, 100)")
    print(f"              Opens SELL 0.01 lots, SL=50 pips, TP=100 pips")
    print()
    print(f"   (!) These methods automatically calculate exact SL/TP prices!")
    print()

    # endregion


    # ══════════════════════════════════════════════════════════════════════════════
    # region PRACTICAL EXAMPLE
    # ══════════════════════════════════════════════════════════════════════════════
    print_section("6. PRACTICAL EXAMPLE - Complete Risk-Managed Trade")

    print("This is how a professional trader would setup a trade:")
    print()
    print("Step 1: Decide on risk parameters")
    print(f"  - Risk per trade: {risk_percent}%")
    print(f"  - Stop Loss: {stop_loss_pips} pips")
    print(f"  - Take Profit: {tp_pips} pips (R:R = 1:{tp_pips/sl_pips:.1f})")
    print()
    print("Step 2: Calculate position size (AUTOMATED)")
    try:
        safe_lot_size = await sugar.calculate_position_size(symbol, risk_percent, stop_loss_pips)
        print(f"  [+] Calculated lot size: {safe_lot_size:.2f} lots")
    except Exception as e:
        print(f"  [X] Failed to calculate: {e}")
        safe_lot_size = 0.01

    print()
    print("Step 3: Validate trade (AUTOMATED)")
    try:
        can_open, reason = await sugar.can_open_position(symbol, safe_lot_size)
        if can_open:
            print(f"  [+] Trade validation passed")
        else:
            print(f"  [X] Validation failed: {reason}")
    except Exception as e:
        print(f"  [X] Validation error: {e}")

    print()
    print("Step 4: Calculate SL/TP prices (AUTOMATED)")
    try:
        sl_price, tp_price = await sugar.calculate_sltp(symbol, is_buy, sl_pips, tp_pips)
        print(f"  [+] SL price: {sl_price:.5f}")
        print(f"  [+] TP price: {tp_price:.5f}")
    except Exception as e:
        print(f"  [X] Calculation failed: {e}")

    print()
    print("Step 5: Execute trade (REAL EXAMPLE with minimal volume)")
    # Use minimal safe volume for demo (0.01 lots = micro lot)
    demo_volume = 0.01
    try:
        # Recalculate SL/TP for the demo volume
        demo_sl, demo_tp = await sugar.calculate_sltp(symbol, is_buy, sl_pips, tp_pips)

        # Execute the trade
        ticket = await sugar.buy_market_with_sltp(
            symbol,
            volume=demo_volume,
            sl=demo_sl,
            tp=demo_tp
        )

        if ticket > 0:
            print(f"  [+] Trade executed successfully!")
            print(f"      Ticket: {ticket}")
            print(f"      Volume: {demo_volume:.2f} lots (minimal demo)")
            print(f"      SL: {demo_sl:.5f} ({sl_pips:.0f} pips)")
            print(f"      TP: {demo_tp:.5f} ({tp_pips:.0f} pips)")
            print()
            print("  [INFO] This is a REAL trade with minimal volume for demonstration.")
            print(f"  [INFO] You can close it manually or wait for SL/TP to trigger.")
        else:
            print(f"  [X] Trade failed (ticket={ticket})")
    except Exception as e:
        print(f"  [X] Trade execution failed: {e}")
        print()
        print("  [INFO] Demo trade failed - showing what code would look like:")
        print(f"  ticket = await sugar.buy_market_with_sltp(")
        print(f"      \"{symbol}\",")
        print(f"      volume={demo_volume:.2f},")
        print(f"      sl=<calculated>,")
        print(f"      tp=<calculated>")
        print(f"  )")

    print()
    print("(!) With Sugar API, professional risk management is THIS EASY!")
    print()

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


    # ══════════════════════════════════════════════════════════════
    # DEMO SUMMARY
    # ══════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)

    print("\nMETHODS DEMONSTRATED (10 total):")
    print("   ACCOUNT INFORMATION (2):  get_account_info, get_daily_stats")
    print("   SYMBOL INFORMATION (3):   get_symbol_info, is_symbol_available,")
    print("                             get_all_symbols")
    print("   RISK MANAGEMENT (4):      calculate_position_size, get_max_lot_size,")
    print("                             can_open_position, calculate_required_margin")
    print("   TRADING HELPERS (1):      calculate_sltp")

    print("\nMT5Sugar Advanced Features:")
    print("  • Professional risk management: auto position sizing based on risk %")
    print("  • Pre-trade validation: check margin, volume, symbol availability")
    print("  • Symbol information: complete specs, availability checks")
    print("  • Pip-based trading: calculate SL/TP from pip values, not prices")
    print("  • Account analytics: complete snapshot and daily statistics")

    print("\n[OK] SUGAR API MASTERY COMPLETE!")
    print("   You now know ALL Sugar API methods across 5 demos:")
    print("   • 06_sugar_basics.py - Connection, Balance, Prices")
    print("   • 07_sugar_trading.py - Market & Pending Orders")
    print("   • 08_sugar_positions.py - Position Management")
    print("   • 09_sugar_history.py - Historical Data & Profits")
    print("   • 10_sugar_advanced.py - Risk Management & Analytics [DONE]")

    print("\n" + "=" * 80)


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    asyncio.run(run_sugar_advanced_demo())
