"""
══════════════════════════════════════════════════════════════════════════════
 FILE: 04_service_demo.py - MID-LEVEL SERVICE API DEMO

 PURPOSE:
   Demonstrates MT5Service mid-level API wrapper for cleaner, more Pythonic code.
   Shows how to use MT5Service methods that return native Python types instead of protobuf.
   This is the RECOMMENDED layer for most trading applications.


 📚 WHAT THIS DEMO COVERS (30 Methods in 8 Steps):

   STEP 1: CREATE MT5SERVICE & CONNECT
      • MT5Service() - Create service wrapper
      • connect_by_server_name() - Connect to MT5 cluster

   STEP 2: ACCOUNT INFORMATION (4 methods)
      • get_account_summary() - All account data in one dataclass
      • get_account_double() - Individual double properties
      • get_account_integer() - Individual integer properties
      • get_account_string() - Individual string properties

   STEP 3: SYMBOL INFORMATION (13 methods)
      • get_symbol_tick() - Current market prices
      • get_symbol_params_many() - Multiple symbols at once
      • get_symbols_total() - Count available symbols
      • get_symbol_integer() - Individual integer properties
      • get_symbol_string() - Individual string properties
      • symbol_exist() - Check if symbol exists (returns bool directly)
      • get_symbol_name() - Get symbol name by index
      • get_symbol_double() - Get double property (Bid, Ask, Point, etc.)
      • symbol_select() - Add/remove symbol from Market Watch
      • is_symbol_synchronized() - Check symbol data sync status
      • get_symbol_margin_rate() - Get margin rates for order types
      • get_symbol_session_quote() - Get quote session times
      • get_symbol_session_trade() - Get trading session times

   STEP 4: POSITIONS & ORDERS (4 methods)
      • get_opened_orders() - Full position/order details
      • get_opened_tickets() - Lightweight ticket numbers only
      • get_positions_total() - Count of open positions
      • get_positions_history() - Historical closed positions

   STEP 5: PRE-TRADE CALCULATIONS (2 methods)
      • calculate_margin() - Required margin for order
      • calculate_profit() - Potential profit calculation

   STEP 6: ORDER HISTORY (1 method)
      • get_order_history() - Historical orders/deals with separation

   STEP 7: TRADING OPERATIONS (4 methods)
      • check_order() - Pre-validate order before sending
      • place_order() - Send order to broker (structure demo)
      • modify_order() - Modify order SL/TP (structure demo)
      • close_order() - Close position (structure demo)

   STEP 8: MARKET DEPTH (3 methods)
      • subscribe_market_depth() - Subscribe to DOM updates
      • get_market_depth() - Get current DOM snapshot
      • unsubscribe_market_depth() - Unsubscribe from DOM

   FINAL: DISCONNECT
      • disconnect() - Close connection

 ⚡ API LEVELS COMPARISON:

   LOW-LEVEL (MT5Account):
      • Direct protobuf Request/Data structures
      • account.account_summary()
      • Returns: protobuf AccountSummaryData
      • Manual time conversions: data.server_time.ToDatetime()

   MID-LEVEL (MT5Service) - THIS DEMO:
      • Wrapper over MT5Account
      • service.get_account_summary()
      • Returns: AccountSummary (clean dataclass)
      • Auto-converted times: summary.server_time (datetime)

   HIGH-LEVEL (MT5Sugar) - Coming Soon:
      • Business logic and ready patterns
      • One-liner operations with smart defaults

 💡 WHY USE MT5SERVICE?
      Less code (30-80% reduction)
      Native Python types (datetime, float, etc)
      No manual protobuf Request building
      Direct value returns (no .requested_value)
      Better separation (positions/orders in separate lists)
      Type safety (better IDE support)

 ⚠️  IMPORTANT:
   • MT5Service wraps MT5Account (low-level)
   • You still have access to account.* methods if needed

 🚀 HOW TO RUN THIS DEMO:
   cd examples
   python main.py 4          (or select [4] from interactive menu)

══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'package'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '0_common'))

# Import helpers
from demo_helpers import (
    load_settings,
    create_and_connect_mt5,
    print_step,
    print_method,
    print_if_error,
    print_success,
    print_info,
    fatal,
    check_retcode,
)

# Import MT5Service
from pymt5.mt5_service import MT5Service

# Import protobuf types
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_functions_pb2
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_helper_pb2


async def main():
    """Main demonstration function."""

    print("═══════════════════════════════════════════════════════════")
    print("MT5 SERVICE DEMO: Mid-Level API (Recommended)")
    print("═══════════════════════════════════════════════════════════")
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # LOAD CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════

    config = load_settings()

    # ═══════════════════════════════════════════════════════════════════════
    # region CREATE MT5SERVICE & CONNECT
    # ═══════════════════════════════════════════════════════════════════════

    print_step(1, "Create MT5Service and Connect")

    # Create low-level MT5Account first
    account = await create_and_connect_mt5(config)

    print("⏳ Waiting for trade server synchronization (20 seconds)...")
    await asyncio.sleep(20)
    print("✓ Trade server ready!\n")

    # Create MT5Service wrapper
    service = MT5Service(account)
    print("✓ MT5Service created (mid-level wrapper)")
    print()

    # endregion


    try:

        # ═══════════════════════════════════════════════════════════════════════
        # region ACCOUNT INFORMATION
        # ═══════════════════════════════════════════════════════════════════════
        print_step(2, "Account Information Methods")

        # ══════════════════════════════════════════════════════════════
        # 2.1. GET ACCOUNT SUMMARY
        #      Get complete account information in ONE method call.
        #      Returns: Clean AccountSummary dataclass with 14 fields.
        #      All times already converted to datetime.
        #      RECOMMENDED for retrieving account data (vs 14 separate calls).
        # ══════════════════════════════════════════════════════════════
        print_method("2.1", "get_account_summary()", "Get all account data")

        summary = await service.get_account_summary()

        print(f"  Login:         {summary.login}")
        print(f"  User Name:     {summary.user_name}")
        print(f"  Balance:       {summary.balance:.2f} {summary.currency}")
        print(f"  Equity:        {summary.equity:.2f}")
        print(f"  Profit:        {summary.profit:.2f}")
        print(f"  Credit:        {summary.credit:.2f}")
        print(f"  Margin:        {summary.margin:.2f}")
        print(f"  Free Margin:   {summary.free_margin:.2f}")
        print(f"  Margin Level:  {summary.margin_level:.2f}%")
        print(f"  Leverage:      1:{summary.leverage}")
        print(f"  Company:       {summary.company_name}")
        if summary.server_time:
            print(f"  Server Time:   {summary.server_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC{summary.utc_timezone_shift_minutes/60:+.1f})")
        print(f"  Trade Mode:    {summary.trade_mode}")

        # ══════════════════════════════════════════════════════════════
        # 2.2. GET ACCOUNT DOUBLE
        #      Get individual account property by ID.
        #      Returns: float directly (no Data struct extraction).
        #      Use when you need just one specific value.
        # ══════════════════════════════════════════════════════════════
        print_method("2.2", "get_account_double()", "Get individual property")

        balance = await service.get_account_double(
            account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
        )

        print(f"  Balance:       {balance:.2f} (same as above, direct return)")

        # ══════════════════════════════════════════════════════════════
        # 2.3. GET ACCOUNT INTEGER
        #      Get individual account integer property by ID.
        #      Returns: int directly (no Data struct extraction).
        #      Use for Leverage, Login, TradeMode, etc.
        # ══════════════════════════════════════════════════════════════
        print_method("2.3", "get_account_integer()", "Get integer property")

        leverage = await service.get_account_integer(
            account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE
        )

        login = await service.get_account_integer(
            account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LOGIN
        )

        print(f"  Leverage:      1:{leverage} (direct int return)")
        print(f"  Login:         {login}")

        # ══════════════════════════════════════════════════════════════
        # 2.4. GET ACCOUNT STRING
        #      Get individual account string property by ID.
        #      Returns: str directly (no Data struct extraction).
        #      Use for Currency, Company, Name, etc.
        # ══════════════════════════════════════════════════════════════
        print_method("2.4", "get_account_string()", "Get string property")

        currency = await service.get_account_string(
            account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY
        )

        company = await service.get_account_string(
            account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY
        )

        print(f"  Currency:      {currency} (direct string return)")
        print(f"  Company:       {company}")

        # endregion


        # ═══════════════════════════════════════════════════════════════════════
        # region SYMBOL INFORMATION
        # ═══════════════════════════════════════════════════════════════════════
        print_step(3, "Symbol Information Methods")

        # ══════════════════════════════════════════════════════════════
        # 3.1. GET SYMBOL TICK
        #      Get current market prices for a symbol.
        #      Returns: Clean SymbolTick dataclass.
        #      Time field is datetime (not Unix timestamp).
        #      Easy access to Bid, Ask, Spread.
        # ══════════════════════════════════════════════════════════════
        print_method("3.1", "get_symbol_tick()", "Get current market prices")

        tick = await service.get_symbol_tick(config['test_symbol'])

        spread = tick.ask - tick.bid
        print(f"  Symbol:        {config['test_symbol']}")
        print(f"  Bid:           {tick.bid:.5f}")
        print(f"  Ask:           {tick.ask:.5f}")
        print(f"  Spread:        {spread:.5f} ({spread*10000:.1f} points)")
        print(f"  Last:          {tick.last:.5f}")
        print(f"  Volume:        {tick.volume}")
        print(f"  Time:          {tick.time.strftime('%Y-%m-%d %H:%M:%S')}")

        # ══════════════════════════════════════════════════════════════
        # 3.2. GET SYMBOL PARAMS MANY
        #      Get multiple symbols' parameters at once.
        #      Supports pagination (page, perPage).
        #      Returns: List of clean SymbolParams dataclasses.
        #      Efficient batch operation.
        #      RECOMMENDED for retrieving symbol parameters.
        # ══════════════════════════════════════════════════════════════
        print_method("3.2", "get_symbol_params_many()", "Get multiple symbols (first 5 alphabetically)")

        symbols, total = await service.get_symbol_params_many(
            name_filter=None,
            sort_mode=None,
            page_number=1,
            items_per_page=5
        )

        print(f"  Retrieved {len(symbols)} symbols (total available: {total}):")
        for i, sym in enumerate(symbols[:3]):
            print(f"    {i+1}. {sym.name:10}  Bid: {sym.bid:.5f}  Ask: {sym.ask:.5f}  Digits: {sym.digits}  Spread: {sym.spread} pts")
        if len(symbols) > 3:
            print(f"  ... and {len(symbols)-3} more")

        # ══════════════════════════════════════════════════════════════
        # 3.3. GET SYMBOLS TOTAL
        #      Get count of available symbols.
        #      Returns: int directly (no Data struct).
        #      selected_only=True for Market Watch count only.
        # ══════════════════════════════════════════════════════════════
        print_method("3.3", "get_symbols_total()", "Count available symbols")

        all_symbols_count = await service.get_symbols_total(False)
        watch_symbols_count = await service.get_symbols_total(True)

        print(f"  All Symbols:       {all_symbols_count} (total in terminal)")
        print(f"  Market Watch Only: {watch_symbols_count} (selected symbols)")

        # ══════════════════════════════════════════════════════════════
        # 3.4. GET SYMBOL INTEGER
        #      Get individual symbol integer property.
        #      Returns: int directly (no Data struct).
        #      Use for Digits, Spread, TradeMode, etc.
        # ══════════════════════════════════════════════════════════════
        print_method("3.4", "get_symbol_integer()", "Get integer property")

        digits = await service.get_symbol_integer(
            config['test_symbol'],
            market_info_pb2.SymbolInfoIntegerProperty.SYMBOL_DIGITS
        )

        spread_points = await service.get_symbol_integer(
            config['test_symbol'],
            market_info_pb2.SymbolInfoIntegerProperty.SYMBOL_SPREAD
        )

        print(f"  Symbol:        {config['test_symbol']}")
        print(f"  Digits:        {digits} (decimal places)")
        print(f"  Spread:        {spread_points} points")

        # ══════════════════════════════════════════════════════════════
        # 3.5. GET SYMBOL STRING
        #      Get individual symbol string property.
        #      Returns: str directly (no Data struct).
        #      Use for Description, Path, Currency, etc.
        # ══════════════════════════════════════════════════════════════
        print_method("3.5", "get_symbol_string()", "Get string property")

        description = await service.get_symbol_string(
            config['test_symbol'],
            market_info_pb2.SymbolInfoStringProperty.SYMBOL_DESCRIPTION
        )

        base_currency = await service.get_symbol_string(
            config['test_symbol'],
            market_info_pb2.SymbolInfoStringProperty.SYMBOL_CURRENCY_BASE
        )

        profit_currency = await service.get_symbol_string(
            config['test_symbol'],
            market_info_pb2.SymbolInfoStringProperty.SYMBOL_CURRENCY_PROFIT
        )

        print(f"  Symbol:        {config['test_symbol']}")
        print(f"  Description:   {description}")
        print(f"  Base Currency: {base_currency}")
        print(f"  Profit Currency: {profit_currency}")

        # ══════════════════════════════════════════════════════════════
        # 3.6. SYMBOL EXIST
        #      Check if symbol exists in terminal.
        #      Returns: bool directly (no Data struct).
        #      Fast check before working with symbol.
        # ══════════════════════════════════════════════════════════════
        print_method("3.6", "symbol_exist()", "Check if symbol exists")

        exists_eur, selected_eur = await service.symbol_exist("EURUSD")
        exists_fake, selected_fake = await service.symbol_exist("FAKESYMBOL123")

        print(f"  EURUSD exists:      {exists_eur} (selected: {selected_eur})")
        print(f"  FAKESYMBOL123:      {exists_fake} (selected: {selected_fake})")

        # ══════════════════════════════════════════════════════════════
        # 3.7. GET SYMBOL NAME
        #      Get symbol name by index position.
        #      Returns: str directly (no Data struct).
        #      Useful for iterating all symbols.
        # ══════════════════════════════════════════════════════════════
        print_method("3.7", "get_symbol_name()", "Get symbol name by index")

        try:
            symbol_name = await service.get_symbol_name(0, False)  # First symbol, all symbols
            print(f"  First symbol (index 0): {symbol_name}")
        except Exception as e:
            print_if_error(e, "get_symbol_name failed")

        # ══════════════════════════════════════════════════════════════
        # 3.8. GET SYMBOL DOUBLE
        #      Get individual symbol double property.
        #      Returns: float directly (no Data struct).
        #      Use for Bid, Ask, Point, etc.
        # ══════════════════════════════════════════════════════════════
        print_method("3.8", "get_symbol_double()", "Get double property")

        bid_price = await service.get_symbol_double(
            config['test_symbol'],
            market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_BID
        )

        ask_price = await service.get_symbol_double(
            config['test_symbol'],
            market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_ASK
        )

        print(f"  Symbol:        {config['test_symbol']}")
        print(f"  Bid:           {bid_price:.5f} (direct double return)")
        print(f"  Ask:           {ask_price:.5f}")
        print(f"  Spread:        {ask_price-bid_price:.5f} points")

        # ══════════════════════════════════════════════════════════════
        # 3.9. SYMBOL SELECT
        #      Add/remove symbol from Market Watch.
        #      Returns: bool directly (success/failure).
        #      Useful for managing visible symbols.
        # ══════════════════════════════════════════════════════════════
        print_method("3.9", "symbol_select()", "Add/remove from Market Watch")

        try:
            selected = await service.symbol_select(config['test_symbol'], True)
            print(f"  Symbol {config['test_symbol']} in Market Watch: {selected}")
        except Exception as e:
            print_if_error(e, "symbol_select failed")

        # ══════════════════════════════════════════════════════════════
        # 3.10. IS SYMBOL SYNCHRONIZED
        #       Check if symbol data is synchronized.
        #       Returns: bool directly (no Data struct).
        #       Ensures symbol is ready for trading.
        # ══════════════════════════════════════════════════════════════
        print_method("3.10", "is_symbol_synchronized()", "Check sync status")

        try:
            is_synced = await service.is_symbol_synchronized(config['test_symbol'])
            print(f"  Symbol {config['test_symbol']} synchronized: {is_synced}")
        except Exception as e:
            print_if_error(e, "is_symbol_synchronized failed")

        # ══════════════════════════════════════════════════════════════
        # 3.11. GET SYMBOL MARGIN RATE
        #       Get margin rates for order types.
        #       Returns: SymbolMarginRate dataclass with direct values.
        #       Shows margin requirements per order type.
        # ══════════════════════════════════════════════════════════════
        print_method("3.11", "get_symbol_margin_rate()", "Get margin rates")

        try:
            margin_rate = await service.get_symbol_margin_rate(
                config['test_symbol'],
                market_info_pb2.ENUM_ORDER_TYPE.ORDER_TYPE_BUY
            )
            print(f"  Symbol:        {config['test_symbol']}")
            print(f"  Order Type:    BUY")
            print(f"  Initial:       {margin_rate.initial_margin_rate*100:.2f}%")
            print(f"  Maintenance:   {margin_rate.maintenance_margin_rate*100:.2f}%")
        except Exception as e:
            print_if_error(e, "get_symbol_margin_rate failed")

        # ══════════════════════════════════════════════════════════════
        # 3.12. GET SYMBOL SESSION QUOTE
        #       Get quote session times.
        #       Returns: SessionTime with start/end times.
        #       Shows when quotes are available.
        #       Note: For forex, 00:00-00:00 means 24-hour session (normal)
        # ══════════════════════════════════════════════════════════════
        print_method("3.12", "get_symbol_session_quote()", "Get quote session")

        try:
            quote_session = await service.get_symbol_session_quote(
                config['test_symbol'],
                market_info_pb2.DayOfWeek.MONDAY,
                0
            )
            print(f"  Symbol:        {config['test_symbol']}")
            print(f"  Day:           Monday, Session 0")
            print(f"  From:          {quote_session.from_time.strftime('%H:%M')}")
            print(f"  To:            {quote_session.to_time.strftime('%H:%M')}")
            print(f"  (00:00-00:00 = 24-hour forex trading)")
        except Exception as e:
            print_if_error(e, "get_symbol_session_quote failed")

        # ══════════════════════════════════════════════════════════════
        # 3.13. GET SYMBOL SESSION TRADE
        #       Get trading session times.
        #       Returns: SessionTime with start/end times.
        #       Shows when trading is allowed.
        #       Note: For forex, 00:00-00:00 means 24-hour session (normal)
        # ══════════════════════════════════════════════════════════════
        print_method("3.13", "get_symbol_session_trade()", "Get trade session")

        try:
            trade_session = await service.get_symbol_session_trade(
                config['test_symbol'],
                market_info_pb2.DayOfWeek.MONDAY,
                0
            )
            print(f"  Symbol:        {config['test_symbol']}")
            print(f"  Day:           Monday, Session 0")
            print(f"  From:          {trade_session.from_time.strftime('%H:%M')}")
            print(f"  To:            {trade_session.to_time.strftime('%H:%M')}")
            print(f"  (00:00-00:00 = 24-hour forex trading)")
        except Exception as e:
            print_if_error(e, "get_symbol_session_trade failed")

        # endregion
        

        # ═══════════════════════════════════════════════════════════════════════
        # region POSITIONS & ORDERS
        # ═══════════════════════════════════════════════════════════════════════
        print_step(4, "Positions & Orders Methods")

        # ══════════════════════════════════════════════════════════════
        # 4.1. GET OPENED ORDERS
        #      Get all open positions and pending orders.
        #      Returns: protobuf OpenedOrdersData with separate lists.
        #      All time fields are Timestamp (convert with .ToDatetime()).
        # ══════════════════════════════════════════════════════════════
        print_method("4.1", "get_opened_orders()", "Get positions and pending orders")

        opened_data = await service.get_opened_orders(
            account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
        )

        print(f"  Open Positions: {len(opened_data.position_infos)}")
        if len(opened_data.position_infos) > 0:
            for i, pos in enumerate(opened_data.position_infos[:3]):
                open_time = pos.open_time.ToDatetime()
                print(f"    Position #{i+1}: Ticket={pos.ticket} Symbol={pos.symbol} Type={pos.type} Volume={pos.volume:.2f} Profit={pos.profit:.2f} OpenTime={open_time.strftime('%Y-%m-%d %H:%M')}")
            if len(opened_data.position_infos) > 3:
                print(f"    ... and {len(opened_data.position_infos)-3} more positions")
        else:
            print("    (No open positions)")

        print(f"\n  Pending Orders: {len(opened_data.opened_orders)}")
        if len(opened_data.opened_orders) > 0:
            for i, ord in enumerate(opened_data.opened_orders[:3]):
                setup_time = ord.time_setup.ToDatetime()
                print(f"    Order #{i+1}: Ticket={ord.ticket} Symbol={ord.symbol} Type={ord.type} Volume={ord.volume_initial:.2f} Price={ord.price_open:.5f} SetupTime={setup_time.strftime('%Y-%m-%d %H:%M')}")
            if len(opened_data.opened_orders) > 3:
                print(f"    ... and {len(opened_data.opened_orders)-3} more orders")
        else:
            print("    (No pending orders)")

        # ══════════════════════════════════════════════════════════════
        # 4.2. GET OPENED TICKETS
        #      Get only ticket numbers (lightweight).
        #      Returns: Two lists of ticket IDs (position_tickets, order_tickets).
        #      Much faster when you only need ticket numbers.
        #      Use for quick "what's open?" checks.
        # ══════════════════════════════════════════════════════════════
        print_method("4.2", "get_opened_tickets()", "Get ticket numbers only (lightweight)")

        pos_tickets, order_tickets = await service.get_opened_tickets()

        print(f"  Position Tickets: {pos_tickets}")
        print(f"  Order Tickets:    {order_tickets}")

        # ══════════════════════════════════════════════════════════════
        # 4.3. GET POSITIONS TOTAL
        #      Get total number of open positions.
        #      Returns: int directly (no Data struct).
        #      Fast count without loading full position data.
        #      Note: 0 is normal if account has no open positions
        # ══════════════════════════════════════════════════════════════
        print_method("4.3", "get_positions_total()", "Get count of open positions")

        try:
            total_positions = await service.get_positions_total()
            print(f"  Total Open Positions: {total_positions}", end="")
            if total_positions == 0:
                print(" (no positions currently open)")
            else:
                print()
        except Exception as e:
            print_if_error(e, "get_positions_total failed")

        # ══════════════════════════════════════════════════════════════
        # 4.4. GET POSITIONS HISTORY
        #      Get historical positions (closed positions).
        #      Returns: protobuf PositionsHistoryData with all details.
        #      Supports pagination and time filtering.
        #      All time fields are Timestamp (convert with .ToDatetime()).
        # ══════════════════════════════════════════════════════════════
        print_method("4.4", "get_positions_history()", "Get closed positions")

        try:
            # Get last 24 hours of history (first 10 positions)
            now = datetime.now()
            yesterday = now - timedelta(hours=24)

            pos_hist_data = await service.get_positions_history(
                sort_type=account_helper_pb2.AH_ENUM_POSITIONS_HISTORY_SORT_TYPE.AH_POSITION_OPEN_TIME_DESC,
                open_from=yesterday,
                open_to=now,
                page=0,
                size=10
            )

            print(f"  History Positions (last 24h): {len(pos_hist_data.history_positions)}")
            if len(pos_hist_data.history_positions) > 0:
                for i, hp in enumerate(pos_hist_data.history_positions[:3]):
                    open_time = hp.open_time.ToDatetime()
                    close_time = hp.close_time.ToDatetime()
                    duration = close_time - open_time
                    print(f"    Position #{i+1}: Ticket={hp.position_ticket} Symbol={hp.symbol} Volume={hp.volume:.2f} Profit={hp.profit:.2f} Duration={duration}")
                if len(pos_hist_data.history_positions) > 3:
                    print(f"    ... and {len(pos_hist_data.history_positions)-3} more positions")
            else:
                print("    (No closed positions in last 24 hours)")
        except Exception as e:
            print_if_error(e, "get_positions_history failed")

        # endregion
        

        # ═══════════════════════════════════════════════════════════════════════
        # region PRE-TRADE CALCULATIONS
        # ═══════════════════════════════════════════════════════════════════════
        print_step(5, "Pre-Trade Calculation Methods")

        # ══════════════════════════════════════════════════════════════
        # 5.1. CALCULATE MARGIN
        #      Calculate required margin for an order.
        #      Returns: float directly (no Data struct).
        #      Use before placing orders to check margin requirements.
        # ══════════════════════════════════════════════════════════════
        print_method("5.1", "calculate_margin()", "Required margin for order")

        try:
            margin_req = trade_functions_pb2.OrderCalcMarginRequest(
                order_type=trade_functions_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY,
                symbol=config['test_symbol'],
                volume=config['test_volume'],
                open_price=tick.ask
            )

            margin = await service.calculate_margin(margin_req)
            print(f"  Symbol:        {config['test_symbol']}")
            print(f"  Volume:        {config['test_volume']:.2f} lots")
            print(f"  Required Margin: {margin:.2f} {summary.currency}")
        except Exception as e:
            print_if_error(e, "calculate_margin failed")

        # ══════════════════════════════════════════════════════════════
        # 5.2. CALCULATE PROFIT
        #      Calculate potential profit for a trade.
        #      Returns: float directly.
        #      Use to estimate P&L before trading.
        # ══════════════════════════════════════════════════════════════
        print_method("5.2", "calculate_profit()", "Potential profit calculation")

        try:
            # Calculate profit for +10 pips target
            pip_size = 0.0001  # For EURUSD
            target_price = tick.ask + (10 * pip_size)

            profit_req = trade_functions_pb2.OrderCalcProfitRequest(
                order_type=trade_functions_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY,
                symbol=config['test_symbol'],
                volume=config['test_volume'],
                open_price=tick.ask,
                close_price=target_price
            )

            profit = await service.calculate_profit(profit_req)
            print(f"  Symbol:        {config['test_symbol']}")
            print(f"  Volume:        {config['test_volume']:.2f} lots")
            print(f"  Entry:         {tick.ask:.5f} (Ask)")
            print(f"  Target:        {target_price:.5f} (+10 pips)")
            print(f"  Potential Profit: {profit:.2f} {summary.currency}")
        except Exception as e:
            print_if_error(e, "calculate_profit failed")

        # endregion
        

        # ═══════════════════════════════════════════════════════════════════════
        # region ORDER HISTORY
        # ═══════════════════════════════════════════════════════════════════════
        print_step(6, "Order History Methods")

        # ══════════════════════════════════════════════════════════════
        # 6.1. GET ORDER HISTORY
        #      Get historical orders and deals for a time period.
        #      Returns: protobuf OrdersHistoryData.
        #      ADVANTAGE: Orders and Deals in one response (not separated).
        #      All time fields are Timestamp (convert with .ToDatetime()).
        #      Supports pagination for large histories.
        # ══════════════════════════════════════════════════════════════
        print_method("6.1", "get_order_history()", "Historical orders & deals with separation")

        try:
            # Get last 7 days of history
            history_from = datetime.now() - timedelta(days=7)
            history_to = datetime.now()

            hist_data = await service.get_order_history(
                from_dt=history_from,
                to_dt=history_to,
                sort_mode=account_helper_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_CLOSE_TIME_DESC,
                page_number=1,
                items_per_page=50
            )

            # Separate orders and deals
            hist_orders = [item.history_order for item in hist_data.history_data if item.HasField('history_order')]
            hist_deals = [item.history_deal for item in hist_data.history_data if item.HasField('history_deal')]

            print(f"  Time Period:   {history_from.strftime('%Y-%m-%d')} to {history_to.strftime('%Y-%m-%d')}")
            print(f"  Total Records: {hist_data.arrayTotal}")
            print(f"  Orders:        {len(hist_orders)} (pending/limit/stop orders)")
            print(f"  Deals:         {len(hist_deals)} (actual executions with P&L)")

            if len(hist_orders) > 0:
                print("\n  Recent Orders (first 3):")
                for i, ord in enumerate(hist_orders[:3]):
                    print(f"    Order #{i+1}: Ticket={ord.ticket} Symbol={ord.symbol} Type={ord.type} Volume={ord.volume_initial:.2f} Price={ord.price_open:.5f} State={ord.state}")

            if len(hist_deals) > 0:
                print("\n  Recent Deals (first 3):")
                for i, deal in enumerate(hist_deals[:3]):
                    print(f"    Deal #{i+1}: Ticket={deal.ticket} Symbol={deal.symbol} Type={deal.type} Volume={deal.volume:.2f} Price={deal.price:.5f} Profit={deal.profit:.2f}")

            if len(hist_orders) == 0 and len(hist_deals) == 0:
                print("  (No history in the last 7 days)")
        except Exception as e:
            print_if_error(e, "get_order_history failed")

        # endregion
        

        # Add 2-3 second delay before trading operations
        print("\n\n⏳ Waiting 3 seconds before trading operations...")
        await asyncio.sleep(3)

        # ═══════════════════════════════════════════════════════════════════════
        # region TRADING OPERATIONS (Advanced)
        # ═══════════════════════════════════════════════════════════════════════
        print_step(7, "Trading Operations Methods (Advanced)")
        print("NOTE: These methods show API structure.")
        print("      check_order runs validation, others show structure only.")

        # ══════════════════════════════════════════════════════════════
        # 7.1. CHECK ORDER (Pre-validation)
        #      Validate an order BEFORE sending to broker.
        #      Returns: Clean OrderCheckResult dataclass.
        #      ADVANTAGE: Auto-extracts nested MqlTradeCheckResult fields.
        #      Shows what account state will be after execution.
        # ══════════════════════════════════════════════════════════════
        print_method("7.1", "check_order()", "Pre-validate order")

        sl = tick.ask - (50 * 0.0001)  # 50 pips SL
        tp = tick.ask + (100 * 0.0001)  # 100 pips TP

        check_req = trade_functions_pb2.OrderCheckRequest(
            mql_trade_request=trade_functions_pb2.MrpcMqlTradeRequest(
                action=trade_functions_pb2.MRPC_ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_DEAL,
                symbol=config['test_symbol'],
                order_type=trade_functions_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY,
                volume=config['test_volume'],
                price=tick.ask,
                stop_loss=sl,
                take_profit=tp
            )
        )

        try:
            check_result = await service.check_order(check_req)

            print(f"  Symbol:        {config['test_symbol']}")
            print(f"  Type:          BUY")
            print(f"  Volume:        {config['test_volume']:.2f} lots")
            print(f"  Price:         {tick.ask:.5f}")
            print(f"  Return Code:   {check_result.returned_code}")

            if check_result.returned_code == 0:
                print(f"  ✓ Order Valid:")
                print(f"    Required Margin:  {check_result.margin:.2f} {summary.currency}")
                print(f"    Balance After:    {check_result.balance:.2f} {summary.currency}")
                print(f"    Equity After:     {check_result.equity:.2f} {summary.currency}")
                print(f"    Free Margin:      {check_result.margin_free:.2f} {summary.currency}")
                print(f"    Margin Level:     {check_result.margin_level:.2f}%")
            else:
                print(f"  ✗ Order Invalid: {check_result.comment}")
        except Exception as e:

            # CheckOrder often fails on DEMO accounts (broker limitation)
            print("  ℹ️  OrderCheck not available (common on demo accounts)")
            print()

            err_msg = str(e)
            if len(err_msg) > 150:
                err_msg = err_msg[:150] + "... [truncated]"
            print(f"     Server response: {err_msg}")

            print()
            print("  ℹ️  This is expected on many demo brokers:")
            print("     • OrderCheck RPC not implemented by broker's demo server")
            print("     • Use calculate_margin()/calculate_profit() for validation instead")
            print("     • place_order() will work normally despite this limitation")
            print()

        # ══════════════════════════════════════════════════════════════
        # 7.2. PLACE ORDER
        #      Send market BUY order to broker.
        #      Returns: Clean OrderResult dataclass with order/deal numbers.
        #      ADVANTAGE: Automatic type conversions for result fields.
        # ══════════════════════════════════════════════════════════════
        print_method("7.2", "place_order()", "Send market BUY order")

        # Get fresh tick for order
        tick = await service.get_symbol_tick(config['test_symbol'])

        # Build order request with minimal volume
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=config['test_symbol'],
            operation=trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY,
            volume=config['test_volume'],  # Minimal volume from config
            price=tick.ask,
            stop_loss=tick.ask - (50 * 0.0001),   # 50 pips SL
            take_profit=tick.ask + (100 * 0.0001) # 100 pips TP
        )

        order_ticket = None
        try:
            order_result = await service.place_order(order_req)

            print(f"  Symbol:        {config['test_symbol']}")
            print(f"  Type:          BUY")
            print(f"  Volume:        {config['test_volume']:.2f} lots")
            print(f"  Price:         {tick.ask:.5f}")
            print(f"  SL:            {tick.ask - (50 * 0.0001):.5f}")
            print(f"  TP:            {tick.ask + (100 * 0.0001):.5f}")
            print()

            # Check result using helper function
            if check_retcode(order_result.returned_code, "Order placement"):
                order_ticket = order_result.order
                print(f"  Order Ticket:  {order_result.order}")
                print(f"  Deal Ticket:   {order_result.deal}")
                print(f"  Volume:        {order_result.volume:.2f}")
                print(f"  Price:         {order_result.price:.5f}")
            else:
                print("  ⚠️  Order was not placed")

        except Exception as e:
            print_if_error(e, "place_order failed")

        print()
        await asyncio.sleep(1)  # Brief pause

        # ══════════════════════════════════════════════════════════════
        # 7.3. MODIFY ORDER
        #      Modify position SL/TP levels.
        #      Returns: Clean OrderResult dataclass.
        #      ADVANTAGE: Simple API for modifying open positions.
        # ══════════════════════════════════════════════════════════════
        if order_ticket:
            print_method("7.3", "modify_order()", "Modify position SL/TP")

            # Get fresh tick
            tick = await service.get_symbol_tick(config['test_symbol'])

            # Build modify request - tighter SL, wider TP
            modify_req = trading_helper_pb2.OrderModifyRequest(
                ticket=order_ticket,
                stop_loss=tick.ask - (30 * 0.0001),   # Tighter: 30 pips SL
                take_profit=tick.ask + (150 * 0.0001) # Wider: 150 pips TP
            )

            try:
                modify_result = await service.modify_order(modify_req)

                print(f"  Position:      {order_ticket}")
                print(f"  New SL:        {tick.ask - (30 * 0.0001):.5f}")
                print(f"  New TP:        {tick.ask + (150 * 0.0001):.5f}")
                print()

                if check_retcode(modify_result.returned_code, "Order modification"):
                    print(f"  ✓ Position modified successfully")
                else:
                    print("  ⚠️  Position was not modified")

            except Exception as e:
                print_if_error(e, "modify_order failed")

            print()
            await asyncio.sleep(1)  # Brief pause

        # ══════════════════════════════════════════════════════════════
        # 7.4. CLOSE ORDER
        #      Close opened position.
        #      Returns: Return code (int).
        #      ADVANTAGE: Simple close by position ticket.
        # ══════════════════════════════════════════════════════════════
        if order_ticket:
            print_method("7.4", "close_order()", "Close position")

            # Build close request
            close_req = trading_helper_pb2.OrderCloseRequest(
                ticket=order_ticket
            )

            try:
                close_code = await service.close_order(close_req)

                print(f"  Position:      {order_ticket}")
                print()

                if check_retcode(close_code, "Position close"):
                    print(f"  ✓ Position closed successfully")
                    order_ticket = None  # Clear ticket
                else:
                    print("  ⚠️  Position was not closed")

            except Exception as e:
                print_if_error(e, "close_order failed")

            print()
        else:
            print_method("7.3-7.4", "modify/close", "Skipped (no open position)")
            print("  ⚠️  No position to modify/close")
            print()

        # endregion
       

        # ═══════════════════════════════════════════════════════════════════════
        # region MARKET DEPTH (DOM)
        # ═══════════════════════════════════════════════════════════════════════
        print_step(8, "Market Depth (DOM) Methods")
        print("\nℹ️  IMPORTANT: Market Depth (Order Book) is only available for exchange-traded instruments")
        print("   • Works for: Stocks, Futures, Options (exchange symbols)")
        print("   • NOT available for: Forex pairs (OTC trading, no centralized order book)")
        print("   • Testing with EURUSD will result in timeout/empty data - this is expected!")

        # ══════════════════════════════════════════════════════════════
        # 8.1. SUBSCRIBE MARKET DEPTH
        #      Subscribe to Depth of Market updates.
        #      ADVANTAGE: Takes symbol string (not Request object).
        #      Must call before get_market_depth.
        # ══════════════════════════════════════════════════════════════
        print_method("8.1", "subscribe_market_depth()", "Subscribe to DOM updates")

        try:
            subscribed = await service.subscribe_market_depth(config['test_symbol'])
            if subscribed:
                print(f"  ✓ Subscribed to Market Depth for {config['test_symbol']}")

                # ══════════════════════════════════════════════════════════════
                # 8.2. GET MARKET DEPTH
                #      Get current DOM snapshot.
                #      ADVANTAGE: Returns clean List[BookInfo].
                #      Requires prior subscribe_market_depth call.
                # ══════════════════════════════════════════════════════════════
                print_method("8.2", "get_market_depth()", "Get current DOM snapshot")

                try:
                    dom_books = await service.get_market_depth(config['test_symbol'])
                    print(f"  Symbol:        {config['test_symbol']}")
                    print(f"  Depth Levels:  {len(dom_books)}")

                    if len(dom_books) > 0:
                        # Show top 3 bids and top 3 asks
                        bid_count = 0
                        ask_count = 0

                        print("\n  Top Bid Levels:")
                        for i, book in enumerate(dom_books[:20]):
                            if book.type == market_info_pb2.BookType.BOOK_TYPE_BUY:
                                bid_count += 1
                                print(f"    Bid #{bid_count}: Price={book.price:.5f} Volume={book.volume_real:.2f}")
                                if bid_count >= 3:
                                    break

                        print("\n  Top Ask Levels:")
                        for i, book in enumerate(dom_books[:20]):
                            if book.type == market_info_pb2.BookType.BOOK_TYPE_SELL:
                                ask_count += 1
                                print(f"    Ask #{ask_count}: Price={book.price:.5f} Volume={book.volume_real:.2f}")
                                if ask_count >= 3:
                                    break

                        if bid_count == 0 and ask_count == 0:
                            print("  (No market depth data available)")
                    else:
                        print("  (Market depth not available for this symbol)")
                except Exception as e:
                    print_if_error(e, "get_market_depth failed")

                # ══════════════════════════════════════════════════════════════
                # 8.3. UNSUBSCRIBE MARKET DEPTH
                #      Unsubscribe from DOM updates.
                #      ADVANTAGE: Takes symbol string (not Request object).
                #      Always clean up subscriptions.
                # ══════════════════════════════════════════════════════════════
                print_method("8.3", "unsubscribe_market_depth()", "Unsubscribe from DOM")

                try:
                    unsubscribed = await service.unsubscribe_market_depth(config['test_symbol'])
                    if unsubscribed:
                        print(f"  ✓ Unsubscribed from Market Depth for {config['test_symbol']}")
                except Exception as e:
                    print_if_error(e, "unsubscribe_market_depth failed")
            else:
                print(f"  ⚠️  Could not subscribe to Market Depth for {config['test_symbol']}")
        except Exception as e:
            print_if_error(e, "subscribe_market_depth failed")

        # endregion

    finally:

        # ═══════════════════════════════════════════════════════════════════════
        # FINAL: DISCONNECT
        # ═══════════════════════════════════════════════════════════════════════
        print("\n\nFINAL: Disconnect")
        print("─" * 59)

        try:
            await account.channel.close()
            print("✓ Disconnected successfully")
        except Exception as e:
            print_if_error(e, "Disconnect failed")

    print("\n═══════════════════════════════════════════════════════════")
    print("✓ DEMO COMPLETED")
    print("═══════════════════════════════════════════════════════════")

if __name__ == "__main__":
    asyncio.run(main())
