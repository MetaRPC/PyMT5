"""══════════════════════════════════════════════════════════════════════════════
FILE: 01_general_operations.py - LOW-LEVEL MT5 API INFORMATION DEMO

PURPOSE:
  Comprehensive demonstration of MT5 information retrieval methods via MT5Account.
  This is a REFERENCE GUIDE for account, symbol, position, and market data queries
  WITHOUT trading operations (see 02_trading_operations.py for trading examples).


📚 WHAT THIS DEMO COVERS (6 Steps):

  STEP 1: CREATE MT5ACCOUNT INSTANCE
     • MT5Account() - Initialize MT5 account object with credentials

  STEP 2: CONNECTION TO MT5 SERVER
     • connect_by_server_name() - Connect to MT5 cluster via gRPC proxy (RECOMMENDED)
     • check_connect() - Verify connection status

  STEP 3: ACCOUNT INFORMATION METHODS
     • account_summary() - Get all account data in one call (RECOMMENDED)
     • account_info_double() - Individual double properties (Balance, Equity, Margin, etc.)
     • account_info_integer() - Integer properties (Login, Leverage, etc.)
     • account_info_string() - String properties (Currency, Company, etc.)

  STEP 4: SYMBOL INFORMATION & OPERATIONS
     • symbols_total() - Count total/selected symbols
     • symbol_exist() - Check if symbol exists
     • symbol_name() - Get symbol name by index from Market Watch
     • symbol_select() - Add/remove symbol from Market Watch
     • symbol_is_synchronized() - Check sync status with server
     • symbol_info_double() - Bid, Ask, Point, Volume Min/Max/Step
     • symbol_info_integer() - Digits, Spread, Stops Level
     • symbol_info_string() - Description, Base/Profit Currency
     • symbol_info_margin_rate() - Get margin requirements
     • symbol_info_tick() - Get last tick data with timestamp
     • symbol_info_session_quote() - Quote session times
     • symbol_info_session_trade() - Trade session times
     • symbol_params_many() - Detailed parameters for multiple symbols

  STEP 5: POSITIONS & ORDERS INFORMATION
     • positions_total() - Count open positions
     • opened_orders() - Get all opened orders & positions
     • opened_orders_tickets() - Get only ticket numbers (lightweight)
     • order_history() - Historical orders with pagination
     • positions_history() - Historical positions with P&L
     • tick_value_with_size() - Get tick value/size data for symbols

  STEP 6: MARKET DEPTH (DOM - Depth of Market)
     • market_book_add() - Subscribe to DOM updates
     • market_book_get() - Get current market depth snapshot
     • market_book_release() - Unsubscribe from DOM
     ⚠️  Note: DOM typically NOT available for forex pairs on demo accounts

🔄 API LEVELS COMPARISON:

  LOW-LEVEL (MT5Account) - THIS FILE:
  ✓ Direct gRPC/protobuf calls
  ✓ Maximum control and flexibility
  ✓ See exactly what MT5 API returns
  ✗ More verbose code
  ✗ Manual protobuf structure handling

  MID-LEVEL (MT5Service):
  ✓ Wrapper with native Python types (datetime, float)
  ✓ 30-50% code reduction
  ✓ Cleaner error handling
  ✗ Less control over exact API calls

  HIGH-LEVEL (MT5Sugar):
  ✓ One-liner operations with smart defaults
  ✓ Ultra-simple API for common tasks
  ✓ Best for quick prototyping
  ✗ Least flexibility

🚀 HOW TO RUN THIS DEMO:
  cd examples
  python main.py lowlevel01     (or select [1] from interactive menu)

══════════════════════════════════════════════════════════════════════════════"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Fix Windows console encoding for Unicode characters (only if running standalone)
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'package'))

from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import MetaRpcMT5.mt5_term_api_connection_pb2 as connection_pb2

# Import common utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '0_common'))
from demo_helpers import (
    load_settings,
    create_and_connect_mt5,
    print_separator,
    print_step,
    print_method,
    print_success,
    print_info,
    fatal,
)


async def run_general_demo():
    """
    Run comprehensive low-level MT5Account demonstration.

    This function demonstrates ALL information retrieval methods using
    direct protobuf calls through MT5Account API.
    """

    print("═" * 59)
    print("MT5 LOWLEVEL DEMO 01: GENERAL OPERATIONS")
    print("═" * 59)
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # LOAD CONFIGURATION & CONNECT
    # ═══════════════════════════════════════════════════════════════════════
    config = load_settings()
    TEST_SYMBOL = config['test_symbol']

    # Create MT5Account and connect using helper function
    # This handles: creating account, connecting, verifying connection
    account = await create_and_connect_mt5(config)

    try:

        # region Account Info


        # ═══════════════════════════════════════════════════════════════════════
        # STEP 3: ACCOUNT INFORMATION METHODS
        # ═══════════════════════════════════════════════════════════════════════
        print_step(3, "Account Information Methods")

        # ══════════════════════════════════════════════════════════════
        # 3.1. account_summary()
        #      Get complete account information in ONE call.
        #      Call: account.account_summary() → gRPC → MT5 Server
        #      Returns: AccountSummaryResponse (protobuf message)
        #      RECOMMENDED method for retrieving account data.
        # ══════════════════════════════════════════════════════════════
        print_method("3.1", "account_summary()", "Get all account data in one call")

        # Direct protobuf call - no request object needed for this method
        summary_data = await account.account_summary()

        print("\nAccount Summary (direct protobuf field access):")
        print_separator()
        print(f"  Login:               {summary_data.account_login}")
        print(f"  UserName:            {summary_data.account_user_name}")
        print(f"  Company:             {summary_data.account_company_name}")
        print(f"  Currency:            {summary_data.account_currency}")
        print(f"  Balance:             {summary_data.account_balance:.2f}")
        print(f"  Equity:              {summary_data.account_equity:.2f}")
        print(f"  Credit:              {summary_data.account_credit:.2f}")
        print(f"  Leverage:            1:{summary_data.account_leverage}")
        print(f"  Trade Mode:          {summary_data.account_trade_mode}")

        # ServerTime is a protobuf Timestamp - need to convert
        if summary_data.server_time:
            server_time = summary_data.server_time.ToDatetime()
            print(f"  Server Time:         {server_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # UTC Timezone Shift: server time offset from UTC in minutes
        # For example: 120 minutes = UTC+2 (the server is 2 hours ahead of UTC)
        utc_shift = summary_data.utc_timezone_server_time_shift_minutes
        print(f"  UTC Timezone Shift:  {utc_shift} minutes (UTC{utc_shift/60:+.1f})")

        # ══════════════════════════════════════════════════════════════
        # 3.2. account_info_double()
        #      Get individual DOUBLE properties from account.
        #      Call: account.account_info_double(property_id) → gRPC → MT5 Server
        #      Returns: double (float value for specified property)
        #      Examples: Balance, Equity, Margin, Profit, Credit.
        # ══════════════════════════════════════════════════════════════
        print_method("3.2", "account_info_double()", "Get specific double property")

        # Request Balance property
        balance_value = await account.account_info_double(
            property_id=account_info_pb2.ACCOUNT_BALANCE
        )
        print(f"  Balance:                       {balance_value:.2f}")

        # Request Equity property
        equity_value = await account.account_info_double(
            property_id=account_info_pb2.ACCOUNT_EQUITY
        )
        print(f"  Equity:                        {equity_value:.2f}")

        # ══════════════════════════════════════════════════════════════
        # 3.3. account_info_integer()
        #      Get individual INTEGER properties from account.
        #      Call: account.account_info_integer(property_id) → gRPC → MT5 Server
        #      Returns: int64 (integer value for specified property)
        #      Examples: Login, Leverage, Trade Mode, Limit Orders.
        # ══════════════════════════════════════════════════════════════
        print_method("3.3", "account_info_integer()", "Get specific integer property")

        # Request Leverage property
        leverage_value = await account.account_info_integer(
            property_id=account_info_pb2.ACCOUNT_LEVERAGE
        )
        print(f"  Leverage:                 1:{leverage_value}")

        # ══════════════════════════════════════════════════════════════
        # 3.4. account_info_string()
        #      Get individual STRING properties from account.
        #      Call: account.account_info_string(property_id) → gRPC → MT5 Server
        #      Returns: string (string value for specified property)
        #      Examples: Name, Company, Server, Currency.
        #      ══════════════════════════════════════════════════════════════
        print_method("3.4", "account_info_string()", "Get specific string property")

        # Request Company property
        company_value = await account.account_info_string(
            property_id=account_info_pb2.ACCOUNT_COMPANY
        )
        print(f"  Company:                  {company_value}")

        # endregion Account Info
        # region Symbol Info


        # ═══════════════════════════════════════════════════════════════════════
        # STEP 4: SYMBOL INFORMATION & OPERATIONS
        # ═══════════════════════════════════════════════════════════════════════
        print_step(4, "Symbol Information & Operations")

        # ══════════════════════════════════════════════════════════════
        # 4.1. symbols_total()
        #      Count available symbols or symbols in Market Watch.
        #      Call: account.symbols_total(selected_only) → gRPC → MT5 Server
        #      Returns: SymbolsTotalResponse (protobuf with .total field)
        #      Mode: False = all symbols, True = Market Watch only.
        # ══════════════════════════════════════════════════════════════
        print_method("4.1", "symbols_total()", "Count symbols")

        # Count all available symbols
        all_symbols_data = await account.symbols_total(selected_only=False)
        print(f"  Total available symbols:       {all_symbols_data.total}")

        # Count symbols in Market Watch only
        selected_symbols_data = await account.symbols_total(selected_only=True)
        print(f"  Symbols in Market Watch:       {selected_symbols_data.total}")

        # ══════════════════════════════════════════════════════════════
        # 4.2. symbol_exist()
        #      Check if a symbol exists in terminal.
        #      Call: account.symbol_exist(symbol) → gRPC → MT5 Server
        #      Returns: SymbolExistResponse (.exists, .is_custom fields)
        #      Useful before querying symbol properties.
        # ══════════════════════════════════════════════════════════════
        print_method("4.2", "symbol_exist()", "Check if symbol exists")

        exist_data = await account.symbol_exist(symbol=TEST_SYMBOL)
        print(f"  Symbol '{TEST_SYMBOL}' exists:      {exist_data.exists}")
        print(f"  Is custom symbol:         {exist_data.is_custom}")

        # ══════════════════════════════════════════════════════════════
        # 4.3. symbol_name()
        #      Get symbol name by index from Market Watch.
        #      Call: account.symbol_name(index, selected) → gRPC → MT5 Server
        #      Returns: SymbolNameResponse (.name field)
        #      Index starts at 0. Use with symbols_total().
        # ══════════════════════════════════════════════════════════════
        print_method("4.3", "symbol_name()", "Get symbol name by index")

        # Show first 3 symbols from Market Watch
        symbols_to_show = min(3, selected_symbols_data.total)

        if symbols_to_show == 0:
            print("  No symbols in Market Watch")
        else:
            print(f"  Showing first {symbols_to_show} symbols from Market Watch:")
            for i in range(symbols_to_show):
                name_data = await account.symbol_name(index=i, selected=True)
                if name_data.name:
                    print(f"    [{i}] {name_data.name}")
                else:
                    print(f"    [{i}] (empty - no symbol at this position)")

        # ══════════════════════════════════════════════════════════════
        # 4.4. symbol_select()
        #      Add or remove symbol from Market Watch.
        #      Call: account.symbol_select(symbol, select) → gRPC → MT5 Server
        #      Returns: SymbolSelectResponse (.success field)
        #      Mode: select=True adds, select=False removes symbol.
        # ══════════════════════════════════════════════════════════════
        print_method("4.4", "symbol_select()", "Add/remove symbol from Market Watch")

        select_data = await account.symbol_select(symbol=TEST_SYMBOL, select=True)
        print(f"  Symbol '{TEST_SYMBOL}' added to Market Watch: {select_data.success}")

        # ══════════════════════════════════════════════════════════════
        # 4.5. symbol_is_synchronized()
        #      Check if symbol data is synchronized with server.
        #      Call: account.symbol_is_synchronized(symbol) → gRPC → MT5 Server
        #      Returns: SymbolIsSynchronizedResponse (.synchronized field)
        #      Ensures symbol has latest quotes before trading.
        # ══════════════════════════════════════════════════════════════
        print_method("4.5", "symbol_is_synchronized()", "Check sync status")

        sync_data = await account.symbol_is_synchronized(symbol=TEST_SYMBOL)
        print(f"  Symbol '{TEST_SYMBOL}' synchronized:  {sync_data.synchronized}")

        # ══════════════════════════════════════════════════════════════
        # 4.6. symbol_info_double()
        #      Get individual DOUBLE properties of symbol.
        #      Call: account.symbol_info_double(symbol, property) → gRPC → MT5 Server
        #      Returns: SymbolInfoDoubleResponse (.value field)
        #      Examples: Bid, Ask, Point, Volume Min/Max/Step, Spread.
        # ══════════════════════════════════════════════════════════════
        print_method("4.6", "symbol_info_double()", "Get double properties")

        # Get BID price
        bid_data = await account.symbol_info_double(
            symbol=TEST_SYMBOL,
            property=market_info_pb2.SYMBOL_BID
        )
        print(f"  Bid price (SYMBOL_BID):        {bid_data.value:.5f}")

        # Get ASK price
        ask_data = await account.symbol_info_double(
            symbol=TEST_SYMBOL,
            property=market_info_pb2.SYMBOL_ASK
        )
        print(f"  Ask price (SYMBOL_ASK):        {ask_data.value:.5f}")

        # Get POINT size
        point_data = await account.symbol_info_double(
            symbol=TEST_SYMBOL,
            property=market_info_pb2.SYMBOL_POINT
        )
        print(f"  Point size (SYMBOL_POINT):     {point_data.value:.5f}")

        # Get VOLUME_MIN
        volume_min_data = await account.symbol_info_double(
            symbol=TEST_SYMBOL,
            property=market_info_pb2.SYMBOL_VOLUME_MIN
        )
        print(f"  Min volume (VOLUME_MIN):       {volume_min_data.value:.2f}")

        # ══════════════════════════════════════════════════════════════
        # 4.7. symbol_info_integer()
        #      Get individual INTEGER properties of symbol.
        #      Call: account.symbol_info_integer(symbol, property) → gRPC → MT5 Server
        #      Returns: SymbolInfoIntegerResponse (.value field)
        #      Examples: Digits, Spread, Stops Level, Trade Mode.
        # ══════════════════════════════════════════════════════════════
        print_method("4.7", "symbol_info_integer()", "Get integer properties")

        # Get DIGITS
        digits_data = await account.symbol_info_integer(
            symbol=TEST_SYMBOL,
            property=market_info_pb2.SYMBOL_DIGITS
        )
        print(f"  Digits (SYMBOL_DIGITS):        {digits_data.value}")

        # Get SPREAD
        spread_data = await account.symbol_info_integer(
            symbol=TEST_SYMBOL,
            property=market_info_pb2.SYMBOL_SPREAD
        )
        print(f"  Spread (SYMBOL_SPREAD):        {spread_data.value} points")

        # Get STOPS_LEVEL
        stops_data = await account.symbol_info_integer(
            symbol=TEST_SYMBOL,
            property=market_info_pb2.SYMBOL_TRADE_STOPS_LEVEL
        )
        print(f"  Stops level (STOPS_LEVEL):     {stops_data.value} points")

        # ══════════════════════════════════════════════════════════════
        # 4.8. symbol_info_string()
        #      Get individual STRING properties of symbol.
        #      Call: account.symbol_info_string(symbol, property) → gRPC → MT5 Server
        #      Returns: SymbolInfoStringResponse (.value field)
        #      Examples: Description, Base Currency, Profit Currency.
        # ══════════════════════════════════════════════════════════════
        print_method("4.8", "symbol_info_string()", "Get string properties")

        # Get DESCRIPTION
        desc_data = await account.symbol_info_string(
            symbol=TEST_SYMBOL,
            property=market_info_pb2.SYMBOL_DESCRIPTION
        )
        print(f"  Description:                   {desc_data.value}")

        # Get BASE CURRENCY
        base_data = await account.symbol_info_string(
            symbol=TEST_SYMBOL,
            property=market_info_pb2.SYMBOL_CURRENCY_BASE
        )
        print(f"  Base currency:                 {base_data.value}")

        # Get PROFIT CURRENCY
        profit_curr_data = await account.symbol_info_string(
            symbol=TEST_SYMBOL,
            property=market_info_pb2.SYMBOL_CURRENCY_PROFIT
        )
        print(f"  Profit currency:               {profit_curr_data.value}")

        # ══════════════════════════════════════════════════════════════
        # 4.9. symbol_info_margin_rate()
        #      Get margin requirements for symbol.
        #      Call: account.symbol_info_margin_rate(symbol, order_type) → gRPC → MT5 Server
        #      Returns: SymbolMarginRateResponse (.initial/maintenance_margin_rate)
        #      Used for calculating required margin.
        # ══════════════════════════════════════════════════════════════
        print_method("4.9", "symbol_info_margin_rate()", "Get margin requirements")

        # Call with direct parameters (no request object needed)
        margin_rate_data = await account.symbol_info_margin_rate(
            symbol=TEST_SYMBOL,
            order_type=market_info_pb2.ORDER_TYPE_BUY
        )

        print(f"  Initial margin rate (BUY):     {margin_rate_data.initial_margin_rate:.2f}")
        print(f"  Maintenance margin rate (BUY): {margin_rate_data.maintenance_margin_rate:.2f}")

        # ══════════════════════════════════════════════════════════════
        # 4.10. symbol_info_tick()
        #      Get last tick (price update) for symbol.
        #      Call: account.symbol_info_tick(symbol) → gRPC → MT5 Server
        #      Returns: MqlTick (.time, .bid, .ask, .last, .volume, .flags)
        #      Most recent price data from server.
        # ══════════════════════════════════════════════════════════════
        print_method("4.10", "symbol_info_tick()", "Get last tick data")

        tick_data = await account.symbol_info_tick(symbol=TEST_SYMBOL)

        print(f"  Last tick for {TEST_SYMBOL}:")
        print(f"    Bid:                         {tick_data.bid:.5f}")
        print(f"    Ask:                         {tick_data.ask:.5f}")
        print(f"    Last:                        {tick_data.last:.5f}")
        print(f"    Volume:                      {tick_data.volume}")

        # Time is Unix timestamp
        tick_time = datetime.fromtimestamp(tick_data.time)
        print(f"    Time:                        {tick_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # ══════════════════════════════════════════════════════════════
        # 4.11. symbol_info_session_quote()
        #      Get quote session trading hours.
        #      Call: account.symbol_info_session_quote(symbol, day, session_index) → gRPC → MT5 Server
        #      Returns: SessionTimeResponse (.from, .to as Timestamp)
        #      When symbol quotes are available.
        # ══════════════════════════════════════════════════════════════
        print_method("4.11", "symbol_info_session_quote()", "Get quote session times")

        # Call with direct parameters (no request object needed)
        quote_session_data = await account.symbol_info_session_quote(
            symbol=TEST_SYMBOL,
            day_of_week=market_info_pb2.MONDAY,
            session_index=0
        )

        print(f"  Monday quote session #0:")

        # Note: protobuf fields are named 'from' and 'to' (not 'from_time'/'to_time')
        if hasattr(quote_session_data, 'from') and getattr(quote_session_data, 'from'):
            from_time = getattr(quote_session_data, 'from').ToDatetime()
            from_seconds = from_time.hour * 3600 + from_time.minute * 60 + from_time.second
            print(f"    From (seconds from day start): {from_seconds}")
            
        if hasattr(quote_session_data, 'to') and getattr(quote_session_data, 'to'):
            to_time = getattr(quote_session_data, 'to').ToDatetime()
            to_seconds = to_time.hour * 3600 + to_time.minute * 60 + to_time.second
            print(f"    To (seconds from day start):   {to_seconds}")

        # ══════════════════════════════════════════════════════════════
        # 4.12. symbol_info_session_trade()
        #      Get trading session hours.
        #      Call: account.symbol_info_session_trade(symbol, day, session_index) → gRPC → MT5 Server
        #      Returns: SessionTimeResponse (.from, .to as Timestamp)
        #      When symbol can be traded (buy/sell).
        # ══════════════════════════════════════════════════════════════
        print_method("4.12", "symbol_info_session_trade()", "Get trade session times")

        # Call with direct parameters (no request object needed)
        trade_session_data = await account.symbol_info_session_trade(
            symbol=TEST_SYMBOL,
            day_of_week=market_info_pb2.MONDAY,
            session_index=0
        )

        print(f"  Monday trade session #0:")

        # Note: protobuf fields are named 'from' and 'to' (not 'from_time'/'to_time')
        if hasattr(trade_session_data, 'from') and getattr(trade_session_data, 'from'):
            from_time = getattr(trade_session_data, 'from').ToDatetime()
            from_seconds = from_time.hour * 3600 + from_time.minute * 60 + from_time.second
            print(f"    From (seconds from day start): {from_seconds}")

        if hasattr(trade_session_data, 'to') and getattr(trade_session_data, 'to'):
            to_time = getattr(trade_session_data, 'to').ToDatetime()
            to_seconds = to_time.hour * 3600 + to_time.minute * 60 + to_time.second
            print(f"    To (seconds from day start):   {to_seconds}")

        # ══════════════════════════════════════════════════════════════
        # 4.13. symbol_params_many()
        #      Get comprehensive parameters for multiple symbols at once.
        #      Call: account.symbol_params_many(request) → gRPC → MT5 Server
        #      Returns: SymbolParamsManyResponse (.symbol_infos array)
        #      RECOMMENDED for getting complete symbol data efficiently.
        # ══════════════════════════════════════════════════════════════
        print_method("4.13", "symbol_params_many()", "Get detailed parameters")

        # Create request with symbol filter (this method takes request object as positional arg)
        params_many_req = account_helper_pb2.SymbolParamsManyRequest(
            symbol_name=TEST_SYMBOL
        )
        params_many_data = await account.symbol_params_many(params_many_req)

        print(f"  Retrieved parameters for {len(params_many_data.symbol_infos)} symbols matching '{TEST_SYMBOL}':")

        # Show first 3 symbols
        max_show = min(3, len(params_many_data.symbol_infos))
        for i in range(max_show):
            info = params_many_data.symbol_infos[i]
            print(f"\n  Symbol #{i+1}: {info.name}")
            print(f"    Bid:                         {info.bid:.5f}")
            print(f"    Ask:                         {info.ask:.5f}")
            print(f"    Digits:                      {info.digits}")
            print(f"    Spread:                      {info.spread} points")
            print(f"    Volume Min:                  {info.volume_min:.2f}")
            print(f"    Volume Max:                  {info.volume_max:.2f}")
            print(f"    Volume Step:                 {info.volume_step:.2f}")
            print(f"    Contract Size:               {info.trade_contract_size:.2f}")
            print(f"    Point:                       {info.point:.5f}")

        # endregion Symbol Info
        # region Positions Info


        # ═══════════════════════════════════════════════════════════════════════
        # STEP 5: POSITIONS & ORDERS INFORMATION
        # ═══════════════════════════════════════════════════════════════════════
        print_step(5, "Positions & Orders Information")

        # ══════════════════════════════════════════════════════════════
        # 5.1. positions_total()
        #      Count currently open positions.
        #      Call: account.positions_total() → gRPC → MT5 Server
        #      Returns: PositionsTotalResponse (.total_positions field)
        #      Lightweight check for open trades.
        # ══════════════════════════════════════════════════════════════
        print_method("5.1", "positions_total()", "Count open positions")

        positions_total_data = await account.positions_total()
        print(f"  Total open positions:          {positions_total_data.total_positions}")

        # ══════════════════════════════════════════════════════════════
        # 5.2. opened_orders()
        #      Get all currently opened orders and positions with details.
        #      Call: account.opened_orders() → gRPC → MT5 Server
        #      Returns: OpenedOrdersResponse (.opened_orders, .position_infos)
        #      Complete snapshot of open trades.
        # ══════════════════════════════════════════════════════════════
        print_method("5.2", "opened_orders()", "Get all opened orders & positions")

        # Call with default sort_mode (no request object needed)
        opened_orders_data = await account.opened_orders()

        total_orders = len(opened_orders_data.opened_orders) + len(opened_orders_data.position_infos)
        print(f"  Total opened orders/positions: {total_orders}")
        print(f"    Pending orders:              {len(opened_orders_data.opened_orders)}")
        print(f"    Open positions:              {len(opened_orders_data.position_infos)}")

        # Show first 2 positions if any exist
        max_show = min(2, len(opened_orders_data.position_infos))
        for i in range(max_show):
            pos = opened_orders_data.position_infos[i]
            print(f"\n  Position #{i+1}:")
            print(f"    Ticket:                      {pos.ticket}")
            print(f"    Symbol:                      {pos.symbol}")
            print(f"    Type:                        {pos.type}")
            print(f"    Volume:                      {pos.volume:.2f}")
            print(f"    Price Open:                  {pos.price_open:.5f}")
            print(f"    Current Price:               {pos.price_current:.5f}")
            print(f"    Profit:                      {pos.profit:.2f}")

        # ══════════════════════════════════════════════════════════════
        # 5.3. opened_orders_tickets()
        #      Get only ticket numbers of opened orders (lightweight).
        #      Call: account.opened_orders_tickets() → gRPC → MT5 Server
        #      Returns: OpenedOrdersTicketsResponse (.opened_orders_tickets, .opened_position_tickets)
        #      Fast check without full position details.
        # ══════════════════════════════════════════════════════════════
        print_method("5.3", "opened_orders_tickets()", "Get ticket numbers only")

        tickets_data = await account.opened_orders_tickets()

        total_tickets = len(tickets_data.opened_orders_tickets) + len(tickets_data.opened_position_tickets)
        print(f"  Total tickets:                 {total_tickets}")
        print(f"    Pending order tickets:       {len(tickets_data.opened_orders_tickets)}")
        print(f"    Position tickets:            {len(tickets_data.opened_position_tickets)}")

        # Show first few position tickets if any exist
        if len(tickets_data.opened_position_tickets) > 0:
            max_show = min(5, len(tickets_data.opened_position_tickets))
            tickets_str = " ".join(str(t) for t in tickets_data.opened_position_tickets[:max_show])
            print(f"  First position tickets:        {tickets_str}")

        # ══════════════════════════════════════════════════════════════
        # 5.4. order_history()
        #      Get historical orders with time range and pagination.
        #      Call: account.order_history(from_dt, to_dt) → gRPC → MT5 Server
        #      Returns: OrderHistoryResponse (.history_data array)
        #      Use for analyzing past trading activity.
        # ══════════════════════════════════════════════════════════════
        print_method("5.4", "order_history()", "Get historical orders")

        # Set time range (last 365 days) - trying wider range
        now = datetime.now()
        from_time = now - timedelta(days=365)

        try:
            # Call with direct parameters (no request object needed)
            order_history_data = await account.order_history(
                from_dt=from_time,
                to_dt=now
            )

            print(f"  Historical orders (last 365d): {len(order_history_data.history_data)}")

            # Show first 2 orders if any exist
            max_show = min(2, len(order_history_data.history_data))
            for i in range(max_show):
                item = order_history_data.history_data[i]
                if item.history_order:
                    order = item.history_order
                    print(f"\n  Order #{i+1}:")
                    print(f"    Ticket:                      {order.ticket}")
                    print(f"    Symbol:                      {order.symbol}")
                    print(f"    Type:                        {order.type}")
                    print(f"    Volume:                      {order.volume_initial:.2f}")
                    print(f"    Price Open:                  {order.price_open:.5f}")
        except Exception as e:
            print(f"  ⚠️  Server error retrieving order history: {e}")
            print("     → This is a server-side error, not a client issue")

        # ══════════════════════════════════════════════════════════════
        # 5.5. positions_history()
        #      Get historical positions with P&L and details.
        #      Call: account.positions_history(sort_type, open_from, open_to) → gRPC → MT5 Server
        #      Returns: PositionsHistoryResponse (.history_positions array)
        #      Analyze trading performance and results.
        # ══════════════════════════════════════════════════════════════
        print_method("5.5", "positions_history()", "Get historical positions with P&L")

        try:
            # Call with direct parameters (no request object needed)
            positions_history_data = await account.positions_history(
                sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
                open_from=from_time,
                open_to=now
            )

            print(f"  Historical positions (last 365d): {len(positions_history_data.history_positions)}")

            # Show first 2 positions if any exist
            max_show = min(2, len(positions_history_data.history_positions))
            for i in range(max_show):
                pos = positions_history_data.history_positions[i]
                print(f"\n  Position #{i+1}:")
                print(f"    Position Ticket:             {pos.position_ticket}")
                print(f"    Symbol:                      {pos.symbol}")
                print(f"    Order Type:                  {pos.order_type}")
                print(f"    Volume:                      {pos.volume:.2f}")
                print(f"    Profit:                      {pos.profit:.2f}")
        except Exception as e:
            print(f"  ⚠️  Server error retrieving positions history: {e}")
            print("     → This is a server-side error, not a client issue")

        # ══════════════════════════════════════════════════════════════
        # 5.6. tick_value_with_size()
        #      Get tick value and contract size for symbols.
        #      Call: account.tick_value_with_size(symbols) → gRPC → MT5 Server
        #      Returns: TickValueSizeResponse (.symbol_tick_size_infos array)
        #      Essential for position sizing and risk calculations.
        # ══════════════════════════════════════════════════════════════
        print_method("5.6", "tick_value_with_size()", "Get tick value/size data")

        try:
            # Use only TEST_SYMBOL to avoid zero values for unselected symbols
            tick_value_data = await account.tick_value_with_size([TEST_SYMBOL])

            print(f"  Tick value data retrieved for {TEST_SYMBOL}:")

            # Show data for the symbol
            symbol_data = tick_value_data.symbol_tick_size_infos[0]
            print(f"    Tick value (profit):               ${symbol_data.TradeTickValueProfit:.5f}")
            print(f"    Tick value (loss):                 ${symbol_data.TradeTickValueLoss:.5f}")
            print(f"    Tick value (avg):                  ${symbol_data.TradeTickValue:.5f}")
            print(f"    Tick size (min price change):      {symbol_data.TradeTickSize:.5f}")
            print(f"    Contract size:                     {symbol_data.TradeContractSize:.0f}")
            print()
            print(f"  [i] What this means:")
            print(f"      • For 1 standard lot ({symbol_data.TradeContractSize:.0f} units)")
            print(f"      • Each {symbol_data.TradeTickSize:.5f} price change")
            print(f"      • Equals ${symbol_data.TradeTickValue:.5f} profit/loss")
            print(f"      • Values are in your account currency")

        except Exception as e:
            print(f"  ⚠️  Error retrieving tick value data: {e}")
            print("     → This may occur if symbol is not available")
            print("     → Make sure TEST_SYMBOL exists on your broker's server")

        # endregion Positions Info
        # region Market Book (DOM)


        # ═══════════════════════════════════════════════════════════════════════
        # STEP 6: MARKET DEPTH / DOM (Depth of Market)
        # ═══════════════════════════════════════════════════════════════════════
        print_step(6, "Market Depth / DOM (Level 2 Data)")
        print()

        # IMPORTANT: DOM Availability Warning
        print("[!] IMPORTANT: DOM (Market Book) Availability")
        print_separator()
        print()
        print("DOM is typically NOT available for:")
        print("  [X] Forex pairs (EURUSD, GBPUSD, etc.)")
        print("  [X] Demo accounts")
        print()
        print("DOM IS available for:")
        print("  [OK] Exchange-traded instruments (Stocks, Futures, Options)")
        print("  [OK] Some brokers on LIVE accounts")
        print()
        print("Why Forex has NO DOM?")
        print("  Forex = Decentralized market (no central exchange)")
        print("  -> No unified order book")
        print("  -> Each broker sees only their own orders")
        print()
        print("Expected behavior in this demo:")
        print("  1. Subscription succeeds   (market_book_add)")
        print("  2. Data retrieval FAILS    (market_book_get - timeout)")
        print("  3. This is NORMAL for Forex demo accounts")
        print()
        print_separator()
        print()

        # ══════════════════════════════════════════════════════════════
        # 6.1. market_book_add()
        #      Subscribe to market depth (Level 2) data stream.
        #      Call: account.market_book_add(symbol, deadline) → gRPC → MT5 Server
        #      Returns: MarketBookAddResponse (.opened_successfully field)
        #      Required before calling market_book_get().
        # ══════════════════════════════════════════════════════════════
        print_method("6.1", "market_book_add()", "Subscribe to DOM")

        # Short timeout for DOM operations (5 seconds)
        dom_deadline = datetime.now() + timedelta(seconds=5)

        try:
            book_add_data = await account.market_book_add(
                symbol=TEST_SYMBOL,
                deadline=dom_deadline
            )
        except Exception as e:
            # Compact error output
            print("  [X] Subscription failed (timeout or not supported)")
        else:
            if book_add_data.opened_successfully:
                print(f"  [+] Subscription accepted for '{TEST_SYMBOL}'")
            else:
                print("  [X] Subscription rejected by broker")

        # ══════════════════════════════════════════════════════════════
        # 6.2. market_book_get()
        #      Retrieve current market depth snapshot.
        #      Call: account.market_book_get(symbol, deadline) → gRPC → MT5 Server
        #      Returns: MarketBookGetResponse (.mql_book_infos array)
        #      Shows buy/sell order book levels.
        # ══════════════════════════════════════════════════════════════
        print_method("6.2", "market_book_get()", "Get DOM snapshot")

        dom_deadline = datetime.now() + timedelta(seconds=2)

        try:
            book_get_data = await account.market_book_get(
                symbol=TEST_SYMBOL,
                deadline=dom_deadline
            )
        except Exception as e:
            # Compact error output for DOM (expected to fail on Forex)
            print("  [X] No DOM data available")
            print("      (Timeout - expected for Forex demo)")
        else:
            if len(book_get_data.mql_book_infos) > 0:
                print(f"  [OK] Received {len(book_get_data.mql_book_infos)} price levels")
                print("       (UNUSUAL for Forex - broker provides limited DOM)")
                print()

                # Show first 5 levels
                max_show = min(5, len(book_get_data.mql_book_infos))
                for i in range(max_show):
                    level = book_get_data.mql_book_infos[i]
                    book_type = "SELL" if level.type == market_info_pb2.BOOK_TYPE_SELL else "BUY"
                    print(f"       [{i+1}] {book_type:4s}  {level.price:.5f}  Vol: {level.volume}")
            else:
                print("  [i] No data returned (broker has no DOM)")

        # ══════════════════════════════════════════════════════════════
        # 6.3. market_book_release()
        #      Unsubscribe from market depth data stream.
        #      Call: account.market_book_release(symbol, deadline) → gRPC → MT5 Server
        #      Returns: MarketBookReleaseResponse (.closed_successfully field)
        #      Cleanup after finishing with DOM data.
        # ══════════════════════════════════════════════════════════════
        print_method("6.3", "market_book_release()", "Unsubscribe")

        dom_deadline = datetime.now() + timedelta(seconds=5)

        try:
            book_release_data = await account.market_book_release(
                symbol=TEST_SYMBOL,
                deadline=dom_deadline
            )
        except Exception as e:
            # Compact error output (not critical)
            print("  [!] Unsubscribe timeout (not critical)")
        else:
            if book_release_data.closed_successfully:
                print("  [+] Unsubscribed successfully")
            else:
                print("  [!] Unsubscribe reported unsuccessful")

        # endregion Market Book (DOM)


    finally:
        # Clean disconnection
        print("\n\nFINAL: Disconnect")
        print("─" * 59)
        try:
            await account.channel.close()
            print("✓ Disconnected successfully")
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")
        print("\n✓ Demo finished")

    # ══════════════════════════════════════════════════════════════════════════════
    # DEMO SUMMARY
    # ══════════════════════════════════════════════════════════════════════════════
    print("\n" + "═" * 80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("═" * 80)

    print("\nMETHODS DEMONSTRATED (29 total):")
    print("   INITIALIZATION (1):       MT5Account()")
    print("   CONNECTION (2):           connect_by_server_name, check_connect")
    print("   ACCOUNT INFO (4):         account_summary, account_info_double,")
    print("                             account_info_integer, account_info_string")
    print("   SYMBOL INFO (13):         symbols_total, symbol_exist, symbol_name,")
    print("                             symbol_select, symbol_is_synchronized,")
    print("                             symbol_info_double, symbol_info_integer,")
    print("                             symbol_info_string, symbol_info_margin_rate,")
    print("                             symbol_info_tick, symbol_info_session_quote,")
    print("                             symbol_info_session_trade, symbol_params_many")
    print("   POSITIONS & ORDERS (6):   positions_total, opened_orders,")
    print("                             opened_orders_tickets, order_history,")
    print("                             positions_history, tick_value_with_size")
    print("   MARKET DEPTH (3):         market_book_add, market_book_get,")
    print("                             market_book_release")

    print("\nLowLevel API Features:")
    print("  • Direct gRPC/protobuf calls - maximum control and transparency")
    print("  • Returns protobuf messages - see exact MT5 API structure")
    print("  • All methods use: account.method() → gRPC → MT5 Server")
    print("  • No wrapper overhead - pure MT5 Terminal API")

    print("\nWHAT'S NEXT:")
    print("   [2] Trading Operations    → python main.py lowlevel02")

    print("\n" + "═" * 80)


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(run_general_demo())
