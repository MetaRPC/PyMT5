"""
MT5Service - Mid-Level API Wrapper

A convenient wrapper over MT5Account with dataclasses, automatic time conversion,
and simplified list handling.

ARCHITECTURE LAYERS:
    LOW  -> MT5Account  (protobuf Request/Data, direct gRPC)
    MID  -> MT5Service  (Python types, removes Data wrappers) <- THIS FILE
    HIGH -> MT5Sugar    (business logic, ready-made patterns)

KEY ADVANTAGES:
    - Returns clean Python types (float, int, str, datetime)
    - Automatically unpacks protobuf .data wrappers
    - Converts Timestamp -> datetime
    - 30-70% less code for common operations
    - Direct value returns (no .requested_value extraction)

AVAILABLE METHODS (36 total):

ACCOUNT METHODS (4):
    - get_account_summary()     Get all account data in one call
    - get_account_double()      Get account double property (Balance, Equity, etc.)
    - get_account_integer()     Get account integer property (Leverage, Login, etc.)
    - get_account_string()      Get account string property (Currency, Company, etc.)

SYMBOL METHODS (13):
    - get_symbols_total()       Get count of available symbols
    - symbol_exist()            Check if symbol exists
    - get_symbol_name()         Get symbol name by index
    - symbol_select()           Add/remove symbol from Market Watch
    - is_symbol_synchronized()  Check if symbol data is synced
    - get_symbol_double()       Get symbol double property (Bid, Ask, Point, etc.)
    - get_symbol_integer()      Get symbol integer property (Digits, Spread, etc.)
    - get_symbol_string()       Get symbol string property (Description, Currency, etc.)
    - get_symbol_margin_rate()  Get margin requirements for symbol
    - get_symbol_tick()         Get last tick data
    - get_symbol_session_quote() Get quote session times
    - get_symbol_session_trade() Get trade session times
    - get_symbol_params_many()  Get comprehensive parameters for multiple symbols

POSITION & ORDERS METHODS (5):
    - get_positions_total()     Get count of open positions
    - get_opened_orders()       Get all opened orders and positions
    - get_opened_tickets()      Get ticket numbers only (lightweight)
    - get_order_history()       Get historical orders
    - get_positions_history()   Get historical positions with P&L

MARKET DEPTH METHODS (3):
    - subscribe_market_depth()   Subscribe to DOM (Depth of Market)
    - unsubscribe_market_depth() Unsubscribe from DOM
    - get_market_depth()         Get market depth snapshot

TRADING METHODS (6):
    - place_order()             Place new order
    - modify_order()            Modify existing order
    - close_order()             Close position by ticket
    - check_order()             Validate order before sending
    - calculate_margin()        Calculate required margin
    - calculate_profit()        Calculate potential profit

STREAMING METHODS (5):
    - stream_ticks()            Stream real-time tick data
    - stream_trade_updates()    Stream trade execution events
    - stream_position_profits() Stream position P&L updates
    - stream_opened_tickets()   Stream ticket number changes
    - stream_transactions()     Stream trade transaction events
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple, AsyncIterator, Any
from google.protobuf.timestamp_pb2 import Timestamp

# Import MT5Account and protobuf
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_functions_pb2
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_helper_pb2
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2


# ══════════════════════════════════════════════════════════════════════════════
# region DATA TRANSFER OBJECTS (DTOs)
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class AccountSummary:
    """
    Complete account information in one convenient structure.

    ADVANTAGE: Clean Python dataclass with native types instead of protobuf.
    All important account information in one place with datetime instead of Timestamp.
    """
    login: int                                      # Account login number
    balance: float                                  # Account balance in deposit currency
    equity: float                                   # Account equity (Balance + Floating P&L)
    user_name: str                                  # Client name
    leverage: int                                   # Account leverage (e.g., 100 for 1:100)
    trade_mode: Any                                 # Account trade mode (demo/real/contest)
    company_name: str                               # Broker company name
    currency: str                                   # Deposit currency (USD, EUR, etc.)
    server_time: Optional[datetime]                 # Server time (already converted from protobuf)
    utc_timezone_shift_minutes: int                 # UTC timezone shift in minutes
    credit: float                                   # Credit facility amount
    margin: float                                   # Margin used for open positions
    free_margin: float                              # Free margin available for trading
    margin_level: float                             # Margin level percentage (equity/margin * 100)
    profit: float                                   # Current floating profit/loss


@dataclass
class SymbolMarginRate:
    """Margin rate information for a symbol."""
    initial_margin_rate: float                      # Initial margin rate
    maintenance_margin_rate: float                  # Maintenance margin rate


@dataclass
class SymbolTick:
    """
    Current tick information for a symbol.

    ADVANTAGE: Time is already converted from Unix timestamp to datetime.
    """
    time: datetime                                  # Tick time (converted from Unix timestamp)
    bid: float                                      # Current Bid price
    ask: float                                      # Current Ask price
    last: float                                     # Last deal price
    volume: int                                     # Tick volume
    time_ms: int                                    # Tick time in milliseconds
    flags: int                                      # Tick flags
    volume_real: float                              # Tick volume with decimal precision


@dataclass
class SessionTime:
    """Trading session time range."""
    from_time: datetime                             # Session start time
    to_time: datetime                               # Session end time


@dataclass
class SymbolParams:
    """
    Comprehensive symbol information.

    ADVANTAGE: All important symbol parameters in one structure.
    Much more convenient than making multiple calls to SymbolInfoDouble/Integer/String.
    """
    name: str                                       # Symbol name
    bid: float                                      # Current Bid price
    ask: float                                      # Current Ask price
    last: float                                     # Last deal price
    point: float                                    # Point size (minimal price change)
    digits: int                                     # Number of decimal places
    spread: int                                     # Current spread in points
    volume_min: float                               # Minimum volume for trading
    volume_max: float                               # Maximum volume for trading
    volume_step: float                              # Volume step
    trade_tick_size: float                          # Trade tick size
    trade_tick_value: float                         # Trade tick value
    trade_contract_size: float                      # Contract size
    swap_long: float                                # Swap for long positions
    swap_short: float                               # Swap for short positions
    margin_initial: float                           # Initial margin requirement
    margin_maintenance: float                       # Maintenance margin requirement


@dataclass
class BookInfo:
    """Single Depth of Market (DOM) price level entry."""
    type: Any                                       # SELL (ask) or BUY (bid)
    price: float                                    # Price level
    volume: int                                     # Volume in lots (integer)
    volume_real: float                              # Volume with decimal precision


@dataclass
class OrderResult:
    """
    Result of a trading operation.

    ADVANTAGE: Clean dataclass instead of protobuf OrderSendData/OrderModifyData.
    """
    returned_code: int                              # Operation return code (10009 = TRADE_RETCODE_DONE)
    deal: int                                       # Deal ticket number (if executed)
    order: int                                      # Order ticket number (if placed)
    volume: float                                   # Executed volume confirmed by broker
    price: float                                    # Execution price confirmed by broker
    bid: float                                      # Current Bid price
    ask: float                                      # Current Ask price
    comment: str                                    # Broker comment or error description
    request_id: int                                 # Request ID set by terminal
    ret_code_external: int                          # External return code


@dataclass
class OrderCheckResult:
    """Result of order validation."""
    returned_code: int                              # Validation code (0 = success)
    balance: float                                  # Balance after deal
    equity: float                                   # Equity after deal
    profit: float                                   # Profit
    margin: float                                   # Required margin
    margin_free: float                              # Free margin after
    margin_level: float                             # Margin level after (%)
    comment: str                                    # Error description


# endregion

# ══════════════════════════════════════════════════════════════════════════════
# region MT5SERVICE CLASS
# ══════════════════════════════════════════════════════════════════════════════


class MT5Service:
    """
    Mid-level API wrapper over MT5Account.

    Provides cleaner Python API by:
        - Returning native Python types instead of protobuf
        - Automatically unpacking .data wrappers
        - Converting Timestamp → datetime
        - Simplifying request creation

    """

    def __init__(self, account: MT5Account):
        """
        Create MT5Service wrapper.

        Args:
            account: MT5Account instance (low-level gRPC client)
        """
        self._account = account

    def get_account(self) -> MT5Account:
        """Return the underlying MT5Account for direct low-level access."""
        return self._account

    #endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region ACCOUNT METHODS (4 methods)
    # ══════════════════════════════════════════════════════════════════════════

    async def get_account_summary(
        self,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> AccountSummary:
        """
        Get complete account information in ONE method call.

        Returns:
            AccountSummary with all account data in native Python types (14 fields).

        Technical: Internally makes 5 RPC calls:
            1. account_summary() - gets 11 basic fields (login, balance, equity, username, etc.)
            2-5. account_info_double() × 4 - gets margin, free_margin, margin_level, profit
        Result: AccountSummary dataclass with 14 fields in native Python types.
        ADVANTAGE: Single method call vs 14 separate AccountInfo* calls (93% code reduction).
        """
        data = await self._account.account_summary(deadline, cancellation_event)

        server_time = None
        if data.server_time:
            server_time = data.server_time.ToDatetime()

        # Get additional margin and profit data
        margin = await self._account.account_info_double(
            account_info_pb2.ACCOUNT_MARGIN, deadline, cancellation_event
        )
        free_margin = await self._account.account_info_double(
            account_info_pb2.ACCOUNT_MARGIN_FREE, deadline, cancellation_event
        )
        margin_level = await self._account.account_info_double(
            account_info_pb2.ACCOUNT_MARGIN_LEVEL, deadline, cancellation_event
        )
        profit = await self._account.account_info_double(
            account_info_pb2.ACCOUNT_PROFIT, deadline, cancellation_event
        )

        return AccountSummary(
            login=data.account_login,
            balance=data.account_balance,
            equity=data.account_equity,
            user_name=data.account_user_name,
            leverage=data.account_leverage,
            trade_mode=data.account_trade_mode,
            company_name=data.account_company_name,
            currency=data.account_currency,
            server_time=server_time,
            utc_timezone_shift_minutes=data.utc_timezone_server_time_shift_minutes,
            credit=data.account_credit,
            margin=margin,
            free_margin=free_margin,
            margin_level=margin_level,
            profit=profit,
        )

    async def get_account_double(
        self,
        property_id: account_info_pb2.AccountInfoDoublePropertyType,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> float:
        """
        Get individual account double property.

        Args:
            property_id: Property to retrieve (ACCOUNT_BALANCE, ACCOUNT_EQUITY, etc.)

        Returns:
            float value directly (no Data struct extraction)

        Technical: Low-level method returns AccountInfoDoubleResponse with res.data.requested_value.
        This wrapper auto-extracts the float, eliminating the .data.requested_value access.
        Supports automatic reconnection on gRPC errors via execute_with_reconnect.
        """
        return await self._account.account_info_double(property_id, deadline, cancellation_event)

    async def get_account_integer(
        self,
        property_id: account_info_pb2.AccountInfoIntegerPropertyType,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> int:
        """
        Get individual account integer property.

        Args:
            property_id: Property to retrieve (ACCOUNT_LEVERAGE, ACCOUNT_LOGIN, etc.)

        Returns:
            int value directly (no Data struct extraction)

        Technical: Low-level returns AccountInfoIntegerResponse with res.data.requested_value.
        This wrapper auto-extracts the int. Used for properties like leverage (1:100), login number.
        """
        return await self._account.account_info_integer(property_id, deadline, cancellation_event)

    async def get_account_string(
        self,
        property_id: account_info_pb2.AccountInfoStringPropertyType,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> str:
        """
        Get individual account string property.

        Args:
            property_id: Property to retrieve (ACCOUNT_CURRENCY, ACCOUNT_COMPANY, etc.)

        Returns:
            str value directly (no Data struct extraction)

        Technical: Low-level returns AccountInfoStringResponse with res.data.requested_value.
        This wrapper auto-extracts the string. Used for properties like currency ("USD"), company name.
        """
        return await self._account.account_info_string(property_id, deadline, cancellation_event)

    #endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region SYMBOL METHODS (13 methods)
    # ══════════════════════════════════════════════════════════════════════════

    async def get_symbols_total(
        self,
        selected_only: bool,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> int:
        """
        Get count of available symbols.

        Args:
            selected_only: True to count only Market Watch symbols, False for all

        Returns:
            int count directly (no Data struct)

        Technical: Low-level returns SymbolsTotalData with data.total wrapper.
        This auto-extracts the count. selected_only=True counts Market Watch, False counts all available symbols in terminal.
        """
        data = await self._account.symbols_total(selected_only, deadline, cancellation_event)
        return data.total

    async def symbol_exist(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> Tuple[bool, bool]:
        """
        Check if symbol exists in terminal.

        Args:
            symbol: Symbol name to check

        Returns:
            Tuple of (exists, is_custom)
        """
        data = await self._account.symbol_exist(symbol, deadline, cancellation_event)
        return (data.exists, data.is_custom)

    async def get_symbol_name(
        self,
        index: int,
        selected_only: bool,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> str:
        """
        Get symbol name by index position.

        Args:
            index: Symbol index (starting at 0)
            selected_only: True to use only Market Watch symbols

        Returns:
            Symbol name string directly
        """
        data = await self._account.symbol_name(index, selected_only, deadline, cancellation_event)
        return data.name

    async def symbol_select(
        self,
        symbol: str,
        select: bool,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> bool:
        """
        Add/remove symbol from Market Watch.

        Args:
            symbol: Symbol name
            select: True to add, False to remove

        Returns:
            Success status directly
        """
        data = await self._account.symbol_select(symbol, select, deadline, cancellation_event)
        return data.success

    async def is_symbol_synchronized(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> bool:
        """
        Check if symbol data is synchronized.

        Args:
            symbol: Symbol name to check

        Returns:
            True if synchronized, False otherwise
        """
        data = await self._account.symbol_is_synchronized(symbol, deadline, cancellation_event)
        return data.synchronized

    async def get_symbol_double(
        self,
        symbol: str,
        property: market_info_pb2.SymbolInfoDoubleProperty,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> float:
        """
        Get individual symbol double property.

        Args:
            symbol: Symbol name
            property: Property to retrieve (SYMBOL_BID, SYMBOL_ASK, etc.)

        Returns:
            float value directly

        Technical: Low-level returns SymbolInfoDoubleResponse with data.value wrapper.
        This extracts the float from nested structure. Common properties: SYMBOL_BID, SYMBOL_ASK, SYMBOL_POINT.
        """
        data = await self._account.symbol_info_double(symbol, property, deadline, cancellation_event)
        return data.value

    async def get_symbol_integer(
        self,
        symbol: str,
        property: market_info_pb2.SymbolInfoIntegerProperty,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> int:
        """
        Get individual symbol integer property.

        Args:
            symbol: Symbol name
            property: Property to retrieve (SYMBOL_DIGITS, SYMBOL_SPREAD, etc.)

        Returns:
            int value directly
        """
        data = await self._account.symbol_info_integer(symbol, property, deadline, cancellation_event)
        return data.value

    async def get_symbol_string(
        self,
        symbol: str,
        property: market_info_pb2.SymbolInfoStringProperty,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> str:
        """
        Get individual symbol string property.

        Args:
            symbol: Symbol name
            property: Property to retrieve (SYMBOL_DESCRIPTION, etc.)

        Returns:
            str value directly
        """
        data = await self._account.symbol_info_string(symbol, property, deadline, cancellation_event)
        return data.value

    async def get_symbol_margin_rate(
        self,
        symbol: str,
        order_type: market_info_pb2.ENUM_ORDER_TYPE,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> SymbolMarginRate:
        """
        Get margin rates for a symbol and order type.

        Args:
            symbol: Symbol name
            order_type: Order type (BUY, SELL, etc.)

        Returns:
            SymbolMarginRate with initial and maintenance rates
        """
        data = await self._account.symbol_info_margin_rate(symbol, order_type, deadline, cancellation_event)
        return SymbolMarginRate(
            initial_margin_rate=data.initial_margin_rate,
            maintenance_margin_rate=data.maintenance_margin_rate,
        )

    async def get_symbol_tick(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> SymbolTick:
        """
        Get current market prices for a symbol.

        Args:
            symbol: Symbol name

        Returns:
            SymbolTick with time already converted to datetime

        Technical: Low-level returns SymbolInfoTickData with Unix timestamp (data.time).
        This wrapper converts time field from Unix seconds to Python datetime via fromtimestamp().
        Also provides time_msc (milliseconds) for sub-second precision and tick flags for tick type detection.
        """
        data = await self._account.symbol_info_tick(symbol, deadline, cancellation_event)

        tick_time = datetime.fromtimestamp(data.time)

        return SymbolTick(
            time=tick_time,
            bid=data.bid,
            ask=data.ask,
            last=data.last,
            volume=data.volume,
            time_ms=data.time_msc,
            flags=data.flags,
            volume_real=data.volume_real,
        )

    async def get_symbol_session_quote(
        self,
        symbol: str,
        day_of_week: market_info_pb2.DayOfWeek,
        session_index: int,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> SessionTime:
        """
        Get quote session times.

        Args:
            symbol: Symbol name
            day_of_week: Day of the week
            session_index: Session index (starting at 0)

        Returns:
            SessionTime with start/end times as datetime

        Technical: Low-level returns SymbolInfoSessionQuoteData with 'from' and 'to' Timestamp fields.
        This wrapper converts both protobuf Timestamps to Python datetimes via ToDatetime().
        Shows when quotes (prices) are available for symbol on specified day. Most symbols have 1 session (0).
        """
        data = await self._account.symbol_info_session_quote(symbol, day_of_week, session_index, deadline, cancellation_event)

        # Field names are 'from' and 'to' (Python keywords, access via getattr)
        from_timestamp = getattr(data, 'from')
        to_timestamp = getattr(data, 'to')

        from_time = from_timestamp.ToDatetime()
        to_time = to_timestamp.ToDatetime()

        return SessionTime(from_time=from_time, to_time=to_time)

    async def get_symbol_session_trade(
        self,
        symbol: str,
        day_of_week: market_info_pb2.DayOfWeek,
        session_index: int,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> SessionTime:
        """
        Get trading session times.

        Args:
            symbol: Symbol name
            day_of_week: Day of the week
            session_index: Session index (starting at 0)

        Returns:
            SessionTime with start/end times as datetime
        """
        data = await self._account.symbol_info_session_trade(symbol, day_of_week, session_index, deadline, cancellation_event)

        # Field names are 'from' and 'to' (Python keywords, access via getattr)
        from_timestamp = getattr(data, 'from')
        to_timestamp = getattr(data, 'to')

        from_time = from_timestamp.ToDatetime()
        to_time = to_timestamp.ToDatetime()

        return SessionTime(from_time=from_time, to_time=to_time)

    async def get_symbol_params_many(
        self,
        name_filter: Optional[str] = None,
        sort_mode: Optional[int] = None,
        page_number: Optional[int] = None,
        items_per_page: Optional[int] = None,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> Tuple[List[SymbolParams], int]:
        """
        Get parameters of multiple symbols at once.

        Args:
            name_filter: Optional symbol name filter
            sort_mode: Optional sort mode
            page_number: Optional page number for pagination
            items_per_page: Optional items per page

        Returns:
            Tuple of (list of SymbolParams, total count)

        Technical: Low-level returns SymbolParamsManyResponse with data.symbol_infos (protobuf repeated field).
        This wrapper unpacks each SymbolInfo protobuf into SymbolParams dataclass with 17 fields.
        Much faster than 17 separate SymbolInfoDouble/Integer/String calls per symbol.
        """
        # Build request
        request = account_helper_pb2.SymbolParamsManyRequest()
        if name_filter:
            request.symbol_name = name_filter
        if sort_mode is not None:
            request.sort_type = sort_mode
        if page_number is not None:
            request.page_number = page_number
        if items_per_page is not None:
            request.items_per_page = items_per_page

        data = await self._account.symbol_params_many(request, deadline, cancellation_event)

        # Convert to SymbolParams list
        symbols = []
        for s in data.symbol_infos:
            symbols.append(SymbolParams(
                name=s.name,
                bid=s.bid,
                ask=s.ask,
                last=s.last,
                point=s.point,
                digits=s.digits,
                spread=s.spread,
                volume_min=s.volume_min,
                volume_max=s.volume_max,
                volume_step=s.volume_step,
                trade_tick_size=s.trade_tick_size,
                trade_tick_value=s.trade_tick_value,
                trade_contract_size=s.trade_contract_size,
                swap_long=s.swap_long,
                swap_short=s.swap_short,
                margin_initial=s.margin_initial,
                margin_maintenance=s.margin_maintenance,
            ))

        return (symbols, data.symbols_total)

    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region POSITION & ORDERS METHODS (5 methods)
    # ══════════════════════════════════════════════════════════════════════════

    async def get_positions_total(
        self,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> int:
        """
        Get total number of open positions.

        Returns:
            int count directly (no Data struct)
        """
        data = await self._account.positions_total(deadline, cancellation_event)
        return data.total_positions

    async def get_opened_orders(
        self,
        sort_mode: account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE = account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> Any:
        """
        Get all open positions and pending orders.

        Args:
            sort_mode: Sort mode for results

        Returns:
            OpenedOrdersData with separate lists for positions and orders

        Technical: Returns protobuf OpenedOrdersData with data.position_infos and data.order_infos.
        Each contains full position/order details (ticket, symbol, volume, profit, SL/TP, etc.).
        For tickets only (faster), use get_opened_tickets() which skips detailed field parsing.
        """
        return await self._account.opened_orders(sort_mode, deadline, cancellation_event)

    async def get_opened_tickets(
        self,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> Tuple[List[int], List[int]]:
        """
        Get only ticket numbers (lightweight).

        Returns:
            Tuple of (position_tickets, order_tickets)

        Technical: Low-level returns OpenedOrdersTicketsData with two repeated int64 fields.
        This extracts position_tickets and order_tickets lists without parsing full position/order details.
        10-20x faster than get_opened_orders() when you only need ticket IDs for existence checks or counting.
        """
        data = await self._account.opened_orders_tickets(deadline, cancellation_event)
        return (list(data.opened_position_tickets), list(data.opened_orders_tickets))

    async def get_order_history(
        self,
        from_dt: datetime,
        to_dt: datetime,
        sort_mode: account_helper_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE = account_helper_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_CLOSE_TIME_DESC,
        page_number: int = 0,
        items_per_page: int = 50,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> Any:
        """
        Get historical orders and deals for a time period.

        Args:
            from_dt: Start time
            to_dt: End time
            sort_mode: Sort mode
            page_number: Page number for pagination
            items_per_page: Items per page

        Returns:
            OrdersHistoryData with orders and deals

        Technical: Returns protobuf OrdersHistoryData with data.order_history_infos (repeated field).
        Includes both orders and their related deals. Supports pagination for large result sets.
        For closed positions with P&L, use get_positions_history() instead (more detailed profit tracking).
        """
        return await self._account.order_history(from_dt, to_dt, sort_mode, page_number, items_per_page, deadline, cancellation_event)

    async def get_positions_history(
        self,
        sort_type: account_helper_pb2.AH_ENUM_POSITIONS_HISTORY_SORT_TYPE,
        open_from: Optional[datetime] = None,
        open_to: Optional[datetime] = None,
        page: int = 0,
        size: int = 10,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> Any:
        """
        Get closed positions history with P&L.

        Args:
            sort_type: Sort type
            open_from: Start of open time filter
            open_to: End of open time filter
            page: Page number
            size: Items per page

        Returns:
            PositionsHistoryData with closed positions

        Technical: Returns protobuf PositionsHistoryData with data.history_positions (repeated field).
        Each PositionHistoryInfo includes profit, commission, swap, open/close times and prices.
        Filters by position open time (not close time). Better than order_history for profit calculations.
        """
        return await self._account.positions_history(sort_type, open_from, open_to, page, size, deadline, cancellation_event)

    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region MARKET DEPTH METHODS (3 methods)
    # ══════════════════════════════════════════════════════════════════════════

    async def subscribe_market_depth(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> bool:
        """
        Subscribe to Depth of Market (DOM) updates.

        Args:
            symbol: Symbol name to subscribe

        Returns:
            Success status

        Technical: Low-level returns MarketBookAddData with data.success wrapper.
        This auto-extracts bool. Required before calling get_market_depth() to receive DOM snapshots.
        Terminal maintains subscription - call unsubscribe_market_depth() when done to free resources.
        """
        data = await self._account.market_book_add(symbol, deadline, cancellation_event)
        return data.success

    async def unsubscribe_market_depth(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> bool:
        """
        Unsubscribe from DOM updates.

        Args:
            symbol: Symbol name to unsubscribe

        Returns:
            Success status

        Technical: Low-level returns MarketBookReleaseData with data.success wrapper.
        This auto-extracts bool. Releases DOM subscription to free terminal resources.
        Always unsubscribe when done - brokers may limit concurrent DOM subscriptions.
        """
        data = await self._account.market_book_release(symbol, deadline, cancellation_event)
        return data.success

    async def get_market_depth(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> List[BookInfo]:
        """
        Get current DOM snapshot.

        Args:
            symbol: Symbol name

        Returns:
            List of BookInfo entries

        Technical: Low-level returns MarketBookGetData with data.books (repeated BookRecord protobuf).
        This wrapper unpacks each BookRecord into BookInfo dataclass (type, price, volume, volume_real).
        Requires prior market_book_add subscription. BookRecord.type: 1=BUY (bid), 2=SELL (ask) levels.
        """
        data = await self._account.market_book_get(symbol, deadline, cancellation_event)

        books = []
        for book in data.books:
            books.append(BookInfo(
                type=book.type,
                price=book.price,
                volume=book.volume,
                volume_real=book.volume_real,
            ))

        return books

    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region TRADING METHODS (6 methods)
    # ══════════════════════════════════════════════════════════════════════════

    async def place_order(
        self,
        request: Any,  # trading_helper_pb2.OrderSendRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> OrderResult:
        """
        Send market/pending order to broker.

        Args:
            request: OrderSendRequest

        Returns:
            OrderResult with deal/order tickets

        Technical: Low-level returns OrderSendData protobuf with nested broker response fields.
        This wrapper flattens protobuf into OrderResult dataclass with 10 fields (returned_code, deal, order, etc.).
        Check returned_code == 10009 (TRADE_RETCODE_DONE) for successful execution.
        """
        data = await self._account.order_send(request, deadline, cancellation_event)

        return OrderResult(
            returned_code=data.returned_code,
            deal=data.deal,
            order=data.order,
            volume=data.volume,
            price=data.price,
            bid=data.bid,
            ask=data.ask,
            comment=data.comment,
            request_id=data.request_id,
            ret_code_external=data.ret_code_external,
        )

    async def modify_order(
        self,
        request: Any,  # trading_helper_pb2.OrderModifyRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> OrderResult:
        """
        Modify existing order or position (SL/TP).

        Args:
            request: OrderModifyRequest

        Returns:
            OrderResult with modification details

        Technical: Low-level returns OrderModifyData protobuf (same structure as OrderSendData).
        This wrapper flattens into OrderResult. Used to change SL/TP on positions or modify pending order price/SL/TP.
        """
        data = await self._account.order_modify(request, deadline, cancellation_event)

        return OrderResult(
            returned_code=data.returned_code,
            deal=data.deal,
            order=data.order,
            volume=data.volume,
            price=data.price,
            bid=data.bid,
            ask=data.ask,
            comment=data.comment,
            request_id=data.request_id,
            ret_code_external=data.ret_code_external,
        )

    async def close_order(
        self,
        request: Any,  # trading_helper_pb2.OrderCloseRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> int:
        """
        Close position or delete pending order.

        Args:
            request: OrderCloseRequest

        Returns:
            Return code directly (10009 = success)

        Technical: Low-level returns OrderCloseData with data.returned_code wrapper.
        This auto-extracts the int return code (10009=TRADE_RETCODE_DONE means successful close/delete).
        For positions, creates opposite market order. For pending orders, sends delete request.
        """
        data = await self._account.order_close(request, deadline, cancellation_event)
        return data.returned_code

    async def check_order(
        self,
        request: Any,  # trade_functions_pb2.OrderCheckRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> OrderCheckResult:
        """
        Validate order before sending to broker.

        Args:
            request: OrderCheckRequest

        Returns:
            OrderCheckResult with validation details

        Technical: Low-level returns OrderCheckResponse with deeply nested mrpc_mql_trade_check_result.
        This wrapper extracts 8 validation fields (returned_code=0 means valid, balance_after_deal, margin, etc.).
        Use this before place_order() to pre-validate margin requirements without sending to broker.
        """
        data = await self._account.order_check(request, deadline, cancellation_event)

        # Extract nested result structure
        result = data.mrpc_mql_trade_check_result

        return OrderCheckResult(
            returned_code=result.returned_code,
            balance=result.balance_after_deal,
            equity=result.equity_after_deal,
            profit=result.profit,
            margin=result.margin,
            margin_free=result.free_margin,
            margin_level=result.margin_level,
            comment=result.comment,
        )

    async def calculate_margin(
        self,
        request: Any,  # trade_functions_pb2.OrderCalcMarginRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> float:
        """
        Calculate required margin for an order.

        Args:
            request: OrderCalcMarginRequest

        Returns:
            Margin value directly (no Data struct)

        Technical: Low-level returns OrderCalcMarginResponse with data.margin wrapper.
        This auto-extracts margin float from protobuf response. Use to check margin requirements before placing order.
        """
        data = await self._account.order_calc_margin(request, deadline, cancellation_event)
        return data.margin

    async def calculate_profit(
        self,
        request: Any,  # trade_functions_pb2.OrderCalcProfitRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[Any] = None,
    ) -> float:
        """
        Calculate potential profit for a trade.

        Args:
            request: OrderCalcProfitRequest

        Returns:
            Profit value directly (no Data struct)

        Technical: Low-level returns OrderCalcProfitResponse with data.profit wrapper.
        This auto-extracts profit float. Calculates P&L for hypothetical trade given entry/exit prices and volume.
        """
        data = await self._account.order_calc_profit(request, deadline, cancellation_event)
        return data.profit

    # endregion

    # ══════════════════════════════════════════════════════════════════════════
    # region STREAMING METHODS (5 methods)
    # ══════════════════════════════════════════════════════════════════════════

    async def stream_ticks(
        self,
        symbols: List[str],
        cancellation_event: Optional[Any] = None,
    ) -> AsyncIterator[SymbolTick]:
        """
        Real-time tick data stream.

        Args:
            symbols: List of symbol names to stream
            cancellation_event: Optional cancellation event

        Yields:
            SymbolTick with time already converted to datetime

        Technical: Low-level streams OnSymbolTickData with symbol_tick.time as protobuf Timestamp.
        This wrapper converts each Timestamp to Python datetime via ToDatetime() for every tick.
        Stream continues until cancellation_event.set() or connection loss (auto-reconnects via execute_stream_with_reconnect).
        """
        async for data in self._account.on_symbol_tick(symbols, cancellation_event):
            # Convert protobuf Timestamp to datetime
            tick_time = data.symbol_tick.time.ToDatetime()

            yield SymbolTick(
                time=tick_time,
                bid=data.symbol_tick.bid,
                ask=data.symbol_tick.ask,
                last=data.symbol_tick.last,
                volume=data.symbol_tick.volume,
                time_ms=data.symbol_tick.time_msc,
                flags=data.symbol_tick.flags,
                volume_real=data.symbol_tick.volume_real,
            )

    async def stream_trade_updates(
        self,
        cancellation_event: Optional[Any] = None,
    ) -> AsyncIterator[Any]:
        """
        Real-time trade events stream (new/closed positions).

        Args:
            cancellation_event: Optional cancellation event

        Yields:
            OnTradeData events

        Technical: Server pushes OnTradeData when position opens/closes or pending order placed/deleted.
        Each event contains position_info or order_info with full details (ticket, symbol, volume, type, etc.).
        Thin wrapper - passes through protobuf OnTradeData without conversion (minimal overhead).
        """
        async for data in self._account.on_trade(cancellation_event):
            yield data

    async def stream_position_profits(
        self,
        interval_ms: int = 1000,
        ignore_empty: bool = True,
        cancellation_event: Optional[Any] = None,
    ) -> AsyncIterator[Any]:
        """
        Real-time position profit updates stream.

        Args:
            interval_ms: Polling interval in milliseconds
            ignore_empty: Skip frames with no changes
            cancellation_event: Optional cancellation event

        Yields:
            OnPositionProfitData with P&L updates

        Technical: Server polls positions every interval_ms and pushes updates when profit changes.
        ignore_empty=True filters out frames where no position P&L changed, reducing bandwidth.
        Each OnPositionProfitData contains position_profits repeated field with ticket→profit mapping.
        """
        async for data in self._account.on_position_profit(interval_ms, ignore_empty, cancellation_event):
            yield data

    async def stream_opened_tickets(
        self,
        interval_ms: int = 1000,
        cancellation_event: Optional[Any] = None,
    ) -> AsyncIterator[Any]:
        """
        Real-time position/order ticket updates stream (lightweight).

        Args:
            interval_ms: Polling interval in milliseconds
            cancellation_event: Optional cancellation event

        Yields:
            OnPositionsAndPendingOrdersTicketsData with ticket IDs

        Technical: Server polls every interval_ms and pushes OnPositionsAndPendingOrdersTicketsData.
        Contains opened_position_tickets and opened_orders_tickets repeated int64 fields.
        10-20x less bandwidth than stream_trade_updates() - use when you only need to track ticket changes.
        """
        async for data in self._account.on_positions_and_pending_orders_tickets(interval_ms, cancellation_event):
            yield data

    async def stream_transactions(
        self,
        cancellation_event: Optional[Any] = None,
    ) -> AsyncIterator[Any]:
        """
        Real-time trade transaction stream (detailed).

        Args:
            cancellation_event: Optional cancellation event

        Yields:
            OnTradeTransactionData events

        Technical: Server pushes OnTradeTransactionData for every trade operation step (request→broker→result).
        More detailed than on_trade: includes transaction_type (DEAL_ADD, ORDER_DELETE, etc.) and request details.
        Thin wrapper - passes through protobuf OnTradeTransactionData without conversion.
        """
        async for data in self._account.on_trade_transaction(cancellation_event):
            yield data

    # endregion