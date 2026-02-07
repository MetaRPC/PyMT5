"""
MT5Sugar - High-level convenience API for MT5 trading.

Architecture layers:
    LOW  → MT5Account (protobuf Request/Data, direct gRPC)
    MID  → MT5Service (Python types, removes Data wrappers)
    HIGH → MT5Sugar (business logic, ready-made patterns)

This is the HIGHEST-LEVEL API layer designed for maximum simplicity:
  - Properties for instant access (await sugar.balance)
  - Context managers (async with sugar.connect(...))
  - Enums instead of magic numbers (Period.TODAY, OrderType.BUY)
  - Unified methods with smart defaults
  - Type hints everywhere

Methods (62 methods + 7 properties = 69 total):
  - 61 async methods
  - 1 sync method (is_connected)
  - 6 async properties (balance, equity, margin, free_margin, margin_level, profit)
  - 1 sync property (service)

1. CONNECTION (4 methods):
    - connect() - connect to MT5 server
    - ping() - verify connection health
    - quick_connect() - quick connection helper
    - is_connected() - check connection status

2. QUICK BALANCE (6 methods):
    - get_balance() - current balance
    - get_equity() - current equity
    - get_margin() - used margin
    - get_free_margin() - available margin
    - get_margin_level() - margin level %
    - get_floating_profit() - current floating P&L

3. PRICES & QUOTES (5 methods):
    - get_bid() - current BID price
    - get_ask() - current ASK price
    - get_spread() - current spread in points
    - get_price_info() - complete price info (Bid/Ask/Spread/Time)
    - wait_for_price() - wait for price update

4. SIMPLE TRADING (6 methods):
    - buy_market() - instant BUY at market
    - sell_market() - instant SELL at market
    - buy_limit() - BUY limit order
    - sell_limit() - SELL limit order
    - buy_stop() - BUY stop order
    - sell_stop() - SELL stop order

5. TRADING WITH SL/TP (10 methods):
    - buy_market_with_sltp() - BUY with SL/TP prices
    - sell_market_with_sltp() - SELL with SL/TP prices
    - buy_limit_with_sltp() - BUY limit with SL/TP
    - sell_limit_with_sltp() - SELL limit with SL/TP
    - buy_market_with_pips() - BUY with SL/TP in pips (alias)
    - sell_market_with_pips() - SELL with SL/TP in pips (alias)
    - modify_position_sltp() - modify both SL and TP
    - modify_position_sl() - modify only SL
    - modify_position_tp() - modify only TP
    - calculate_sltp() - convert pips to prices

6. POSITION MANAGEMENT (8 methods):
    - close_position() - close position by ticket
    - close_position_partial() - partially close position
    - close_all_positions() - close all open positions
    - get_open_positions() - get all open positions
    - get_position_by_ticket() - get position by ticket
    - get_positions_by_symbol() - filter positions by symbol
    - count_open_positions() - count open positions
    - has_open_position() - check if positions exist

7. POSITION INFORMATION (2 methods):
    - get_total_profit() - total floating P&L
    - get_profit_by_symbol() - floating P&L for symbol

8. HISTORY & STATISTICS (11 methods):
    - get_deals() - flexible history query with Period enum
    - get_profit() - total profit for period
    - get_deals_today() - today's deals
    - get_deals_yesterday() - yesterday's deals
    - get_deals_this_week() - this week's deals
    - get_deals_this_month() - this month's deals
    - get_deals_date_range() - custom date range
    - get_profit_today() - today's profit
    - get_profit_this_week() - this week's profit
    - get_profit_this_month() - this month's profit
    - get_daily_stats() - comprehensive daily statistics

9. SYMBOL INFORMATION (5 methods):
    - get_symbol_info() - complete symbol parameters
    - get_all_symbols() - list all available symbols
    - is_symbol_available() - check if symbol exists
    - get_min_stop_level() - minimum SL/TP distance
    - get_symbol_digits() - decimal places for symbol

10. RISK MANAGEMENT (4 methods):
    - calculate_position_size() - lot size by risk %
    - can_open_position() - validate before trading
    - get_max_lot_size() - maximum allowed volume
    - calculate_required_margin() - margin for planned trade

11. ACCOUNT & GENERAL (1 method):
    - get_account_info() - structured account data

12. PROPERTIES (7 Python properties for convenient access):
    - balance - Account balance (async property)
    - equity - Current equity (async property)
    - margin - Used margin (async property)
    - free_margin - Free margin (async property)
    - margin_level - Margin level % (async property)
    - profit - Total floating profit/loss (async property)
    - service - Access to MT5Service instance (sync property)
"""

from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Optional, List, Union, Tuple
from enum import Enum
import asyncio

from .mt5_service import (
    MT5Service,
    AccountSummary,
    SymbolTick,
    SymbolParams,
    OrderResult,
    OrderCheckResult,
)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'package'))
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as trade_functions_pb2
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as trading_helper_pb2


# ══════════════════════════════════════════════════════════════════════════════
# region ENUMS & CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

class Period(Enum):
    """Time period for history queries"""
    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    THIS_MONTH = "this_month"
    CUSTOM = "custom"


class OrderType(Enum):
    """Order types for trading"""
    BUY = 0
    SELL = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP = 5

# endregion


# ══════════════════════════════════════════════════════════════════════════════
# region DATA TRANSFER OBJECTS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class PriceInfo:
    """Complete price information for a symbol"""
    symbol: str
    bid: float
    ask: float
    spread: float
    time: datetime


@dataclass
class SymbolInfo:
    """Complete symbol information"""
    name: str
    bid: float
    ask: float
    spread: int
    digits: int
    point: float
    volume_min: float
    volume_max: float
    volume_step: float
    contract_size: float


@dataclass
class AccountInfo:
    """Complete account information"""
    login: int
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    profit: float
    currency: str
    leverage: int
    company: str


@dataclass
class DailyStats:
    """Daily trading statistics"""
    date: date
    deals_count: int
    profit: float
    commission: float
    swap: float
    volume: float

# endregion


# ══════════════════════════════════════════════════════════════════════════════
# region MT5SUGAR CLASS
# ══════════════════════════════════════════════════════════════════════════════

class MT5Sugar:
    """
    High-level convenience API for MT5 trading using Python best practices.

    Example usage:
        # Create instance
        sugar = MT5Sugar(service)

        # Use properties
        balance = await sugar.balance
        equity = await sugar.equity

        # Simple trading
        ticket = await sugar.buy_market("EURUSD", 0.1)

        # With context manager
        async with MT5Sugar.connect("ICMarkets-Demo") as sugar:
            await sugar.buy_market("EURUSD", 0.1)
    """

    def __init__(
        self,
        service: MT5Service,
        default_timeout: float = 10.0,
        default_symbol: Optional[str] = None
    ):
        """
        Initialize MT5Sugar with a service instance.

        Args:
            service: MT5Service instance
            default_timeout: Default timeout for operations in seconds
            default_symbol: Default trading symbol (e.g., "EURUSD")
        """
        self._service = service
        self._default_timeout = default_timeout
        self._default_symbol = default_symbol

    @classmethod
    async def connect(
        cls,
        host: str,
        port: int = 443,
        login: int = 0,
        password: str = "",
        **kwargs
    ) -> 'MT5Sugar':
        """
        Create and connect MT5Sugar instance (use as context manager).

        """
        # This is a placeholder - actual implementation needs MT5Account connection
        raise NotImplementedError("Direct connection not yet implemented. Use MT5Sugar(service)")

    @property
    def service(self) -> MT5Service:
        """Get underlying MT5Service for advanced operations"""
        return self._service
     
     # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 1. CONNECTION - Methods of connecting and checking the connection
    # ══════════════════════════════════════════════════════════════════════════

    def is_connected(self) -> bool:
        """
        Check if connection to MT5 server is active.

        Returns:
            True if gRPC channel is ready or idle, False otherwise

        Example:
            if sugar.is_connected():
                balance = await sugar.get_balance()
            else:
                print("Not connected to MT5 server")
        """
        try:
            import grpc
            # Get underlying MT5Account from service
            account = self._service.get_account()
            if not hasattr(account, 'channel'):
                return False

            # Check channel state
            # READY or IDLE states mean we can make calls
            state = account.channel.get_state(try_to_connect=False)
            return state in (grpc.ChannelConnectivity.READY, grpc.ChannelConnectivity.IDLE)
        except Exception:
            return False

    async def ping(self, timeout: float = 5.0) -> bool:
        """
        Ping MT5 server to check connection health.

        Attempts a quick request to verify the server responds.

        Args:
            timeout: Timeout in seconds for ping attempt

        Returns:
            True if server responds successfully, False otherwise

        """
        try:

            # Try a lightweight operation with short timeout
            async with asyncio.timeout(timeout):
                _ = await self._service.get_symbols_total(selected_only=True)
            return True
        except (asyncio.TimeoutError, Exception):
            return False

    async def quick_connect(self, cluster_name: str, base_symbol: str = "EURUSD") -> None:
        """
        Quick connect (or reconnect) to MT5 cluster by name.

        This is the easiest connection method - just provide your broker's cluster name.
        Uses the credentials already stored in MT5Account. Perfect for switching between
        demo/live accounts or reconnecting after disconnection.

        Args:
            cluster_name: MT5 cluster identifier (e.g., "ICMarkets-Demo", "FxPro-Live01")
            base_symbol: Base chart symbol for connection (default: "EURUSD")

        Raises:
            RuntimeError: If credentials are not accessible in MT5Account
            Exception: If connection to cluster fails

        Note:
            This method uses connect_by_server_name() which automatically:
            - Validates credentials with the MT5 server
            - Waits for terminal to be ready (default 30 seconds)
            - Updates the session GUID from server
        """
        # Get underlying MT5Account
        account = self._service.get_account()

        # Verify credentials are available
        if not hasattr(account, 'user') or not hasattr(account, 'password'):
            raise RuntimeError(
                "Cannot connect: credentials not accessible in MT5Account. "
                "Please ensure MT5Account was created with valid user and password."
            )

        # Connect using server name (ConnectEx in protobuf)
        await account.connect_by_server_name(
            server_name=cluster_name,
            base_chart_symbol=base_symbol,
            wait_for_terminal_is_alive=True,
            timeout_seconds=30
        )
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 2 QUICK BALANCE & ACCOUNT
    # ══════════════════════════════════════════════════════════════════════════

    async def get_balance(self) -> float:
        """
        Get account balance (realized profit only).

        Technical: Calls service.get_account_summary() and extracts balance field.
        Returns only closed position profits - use get_equity() for balance + floating P&L.
        """
        summary = await self._service.get_account_summary()
        return summary.balance

    async def get_equity(self) -> float:
        """
        Get current equity (balance + floating P/L).

        Technical: Calls service.get_account_summary() and extracts equity field.
        Equity = balance + floating profit from all open positions. Used for margin level calculation.
        """
        summary = await self._service.get_account_summary()
        return summary.equity

    async def get_margin(self) -> float:
        """
        Get used margin.

        Technical: Calls service.get_account_double(ACCOUNT_MARGIN).
        Sum of margin locked by all open positions. Check against free_margin before opening new positions.
        """
        return await self._service.get_account_double(
            account_info_pb2.ACCOUNT_MARGIN
        )

    async def get_free_margin(self) -> float:
        """
        Get available margin for new positions.

        Technical: Calls service.get_account_double(ACCOUNT_MARGIN_FREE).
        Free margin = equity - used margin. Must be sufficient for new position's required margin.
        """
        return await self._service.get_account_double(
            account_info_pb2.ACCOUNT_MARGIN_FREE
        )

    async def get_margin_level(self) -> float:
        """
        Get margin level % (Equity/Margin × 100).

        Technical: Calls service.get_account_double(ACCOUNT_MARGIN_LEVEL).
        Brokers trigger margin call/stop out when level drops below threshold (typically 100%/50%).
        """
        return await self._service.get_account_double(
            account_info_pb2.ACCOUNT_MARGIN_LEVEL
        )

    async def get_floating_profit(self) -> float:
        """
        Get total floating profit/loss from open positions.

        Technical: Calls service.get_account_double(ACCOUNT_PROFIT).
        Sum of unrealized P&L across all open positions. Updates with every price tick.
        """
        return await self._service.get_account_double(
            account_info_pb2.ACCOUNT_PROFIT
        )

    # Python properties for convenient access
    @property
    async def balance(self) -> float:
        """Property: Account balance"""
        return await self.get_balance()

    @property
    async def equity(self) -> float:
        """Property: Current equity"""
        return await self.get_equity()

    @property
    async def margin(self) -> float:
        """Property: Used margin"""
        return await self.get_margin()

    @property
    async def free_margin(self) -> float:
        """Property: Free margin"""
        return await self.get_free_margin()

    @property
    async def margin_level(self) -> float:
        """Property: Margin level %"""
        return await self.get_margin_level()

    @property
    async def profit(self) -> float:
        """Property: Total floating profit/loss"""
        return await self.get_floating_profit()
    
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 3 PRICES & QUOTES
    # ══════════════════════════════════════════════════════════════════════════

    async def get_bid(self, symbol: Optional[str] = None) -> float:
        """
        Get current BID price.

        Technical: Calls service.get_symbol_tick() and extracts bid field.
        Uses default_symbol if symbol=None. BID = sell price for closing long/opening short.
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        tick = await self._service.get_symbol_tick(symbol)
        return tick.bid

    async def get_ask(self, symbol: Optional[str] = None) -> float:
        """
        Get current ASK price.

        Technical: Calls service.get_symbol_tick() and extracts ask field.
        Uses default_symbol if symbol=None. ASK = buy price for opening long/closing short.
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        tick = await self._service.get_symbol_tick(symbol)
        return tick.ask

    async def get_spread(self, symbol: Optional[str] = None) -> float:
        """
        Get current spread in points.

        Technical: Calls service.get_symbol_tick() and calculates ask - bid.
        Spread = broker's cost per trade. Lower spread = better execution. Varies with market volatility.
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        tick = await self._service.get_symbol_tick(symbol)
        return tick.ask - tick.bid

    async def get_price_info(self, symbol: Optional[str] = None) -> PriceInfo:
        """Get complete price information"""
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        tick = await self._service.get_symbol_tick(symbol)
        return PriceInfo(
            symbol=symbol,
            bid=tick.bid,
            ask=tick.ask,
            spread=tick.ask - tick.bid,
            time=tick.time
        )

    async def wait_for_price(
        self,
        symbol: Optional[str] = None,
        timeout: float = 5.0
    ) -> PriceInfo:
        """Wait for valid price update with timeout"""
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        try:
            async with asyncio.timeout(timeout):
                return await self.get_price_info(symbol)
        except asyncio.TimeoutError:
            raise TimeoutError(f"No price received for {symbol} within {timeout}s")
        
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 4 SIMPLE TRADING METHODS
    # ══════════════════════════════════════════════════════════════════════════

    async def buy_market(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Open BUY position at market price.

        Returns:
            Position ticket number

        Technical: Fetches current ASK price via get_symbol_tick(), builds OrderSendRequest with TMT5_ORDER_TYPE_BUY.
        Uses slippage=10 points as default tolerance. Raises RuntimeError if returned_code != 10009 (TRADE_RETCODE_DONE).
        Returns result.order (ticket ID) on success. Uses default_symbol if symbol=None.
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        # Get current price
        tick = await self._service.get_symbol_tick(symbol)

        # Create OrderSendRequest
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=symbol,
            operation=trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY,
            volume=volume,
            price=tick.ask,
            slippage=10,  # Default slippage in points
            comment=comment,
            expert_id=magic
        )

        # Send order
        result = await self._service.place_order(order_req)

        if result.returned_code != 10009:  # TRADE_RETCODE_DONE
            raise RuntimeError(
                f"Order failed: code={result.returned_code}, comment={result.comment}"
            )

        return result.order

    async def sell_market(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Open SELL position at market price.

        Returns:
            Position ticket number

        Technical: Fetches current BID price via get_symbol_tick(), builds OrderSendRequest with TMT5_ORDER_TYPE_SELL.
        Uses slippage=10 points as default tolerance. Raises RuntimeError if returned_code != 10009.
        Returns result.order (ticket ID) on success. SELL = profit from price falling.
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        # Get current price
        tick = await self._service.get_symbol_tick(symbol)

        # Create OrderSendRequest
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=symbol,
            operation=trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_SELL,
            volume=volume,
            price=tick.bid,
            slippage=10,  # Default slippage in points
            comment=comment,
            expert_id=magic
        )

        # Send order
        result = await self._service.place_order(order_req)

        if result.returned_code != 10009:  # TRADE_RETCODE_DONE
            raise RuntimeError(
                f"Order failed: code={result.returned_code}, comment={result.comment}"
            )

        return result.order

    async def buy_limit(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        price: float = 0.0,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Place BUY LIMIT pending order (buy below current price).

        Returns:
            Order ticket number

        Example:
            ticket = await sugar.buy_limit("EURUSD", 0.1, price=1.0850)
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        # Create OrderSendRequest
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=symbol,
            operation=trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY_LIMIT,
            volume=volume,
            price=price,
            comment=comment,
            expert_id=magic
        )

        result = await self._service.place_order(order_req)

        if result.returned_code != 10009:
            raise RuntimeError(
                f"Order failed: code={result.returned_code}, comment={result.comment}"
            )

        return result.order

    async def sell_limit(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        price: float = 0.0,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Place SELL LIMIT pending order (sell above current price).

        Returns:
            Order ticket number

        Example:
            ticket = await sugar.sell_limit("EURUSD", 0.1, price=1.0950)
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        # Create OrderSendRequest
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=symbol,
            operation=trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_SELL_LIMIT,
            volume=volume,
            price=price,
            comment=comment,
            expert_id=magic
        )

        result = await self._service.place_order(order_req)

        if result.returned_code != 10009:
            raise RuntimeError(
                f"Order failed: code={result.returned_code}, comment={result.comment}"
            )

        return result.order

    async def buy_stop(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        price: float = 0.0,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Place BUY STOP pending order (buy above current price).

        Returns:
            Order ticket number

        Example:
            ticket = await sugar.buy_stop("EURUSD", 0.1, price=1.0950)
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        # Create OrderSendRequest
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=symbol,
            operation=trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY_STOP,
            volume=volume,
            price=price,
            comment=comment,
            expert_id=magic
        )

        result = await self._service.place_order(order_req)

        if result.returned_code != 10009:
            raise RuntimeError(
                f"Order failed: code={result.returned_code}, comment={result.comment}"
            )

        return result.order

    async def sell_stop(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        price: float = 0.0,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Place SELL STOP pending order (sell below current price).

        Returns:
            Order ticket number

        Example:
            ticket = await sugar.sell_stop("EURUSD", 0.1, price=1.0850)
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        # Create OrderSendRequest
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=symbol,
            operation=trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_SELL_STOP,
            volume=volume,
            price=price,
            comment=comment,
            expert_id=magic
        )

        result = await self._service.place_order(order_req)

        if result.returned_code != 10009:
            raise RuntimeError(
                f"Order failed: code={result.returned_code}, comment={result.comment}"
            )

        return result.order
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 5 TRADING WITH SL/TP 
    # ══════════════════════════════════════════════════════════════════════════

    async def buy_market_with_sltp(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        sl_pips: Optional[float] = None,
        tp_pips: Optional[float] = None,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Open BUY position with Stop Loss and Take Profit.

        Args:
            symbol: Trading symbol
            volume: Volume in lots
            sl: Stop Loss price (absolute)
            tp: Take Profit price (absolute)
            sl_pips: Stop Loss in pips (alternative to sl)
            tp_pips: Take Profit in pips (alternative to tp)
            comment: Order comment
            magic: Magic number

        Returns:
            Position ticket number

        Technical: Converts sl_pips/tp_pips to prices via symbol.point × 10. For BUY: SL = ask - (pips × point × 10), TP = ask + (pips × point × 10).
        Fetches symbol_info for point value if pips specified. Sets stop_loss/take_profit fields in OrderSendRequest.
        Raises RuntimeError if returned_code != 10009.
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        # Get current price and symbol info
        tick = await self._service.get_symbol_tick(symbol)

        # Calculate SL/TP from pips if needed
        sl_price = sl
        tp_price = tp

        if sl_pips is not None or tp_pips is not None:
            # Get symbol info for point value
            symbol_info = await self.get_symbol_info(symbol)
            point = symbol_info.point

            if sl_pips is not None:
                sl_price = tick.ask - (sl_pips * point * 10)  # For BUY, SL is below entry
            if tp_pips is not None:
                tp_price = tick.ask + (tp_pips * point * 10)  # For BUY, TP is above entry

        # Create OrderSendRequest
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=symbol,
            operation=trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY,
            volume=volume,
            price=tick.ask,
            slippage=10,
            comment=comment,
            expert_id=magic
        )

        # Set SL/TP if provided
        if sl_price is not None:
            order_req.stop_loss = sl_price
        if tp_price is not None:
            order_req.take_profit = tp_price

        # Send order
        result = await self._service.place_order(order_req)

        if result.returned_code != 10009:  # TRADE_RETCODE_DONE
            raise RuntimeError(
                f"Order failed: code={result.returned_code}, comment={result.comment}"
            )

        return result.order

    async def sell_market_with_sltp(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        sl_pips: Optional[float] = None,
        tp_pips: Optional[float] = None,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Open SELL position with Stop Loss and Take Profit.

        Args:
            symbol: Trading symbol
            volume: Volume in lots
            sl: Stop Loss price (absolute)
            tp: Take Profit price (absolute)
            sl_pips: Stop Loss in pips (alternative to sl)
            tp_pips: Take Profit in pips (alternative to tp)
            comment: Order comment
            magic: Magic number

        Returns:
            Position ticket number

        Example:
            # Using absolute prices
            ticket = await sugar.sell_market_with_sltp("EURUSD", 0.1, sl=1.1000, tp=1.0900)

            # Using pips
            ticket = await sugar.sell_market_with_sltp("EURUSD", 0.1, sl_pips=50, tp_pips=100)
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        # Get current price
        tick = await self._service.get_symbol_tick(symbol)

        # Calculate SL/TP from pips if needed
        sl_price = sl
        tp_price = tp

        if sl_pips is not None or tp_pips is not None:
            symbol_info = await self.get_symbol_info(symbol)
            point = symbol_info.point

            if sl_pips is not None:
                sl_price = tick.bid + (sl_pips * point * 10)  # For SELL, SL is above entry
            if tp_pips is not None:
                tp_price = tick.bid - (tp_pips * point * 10)  # For SELL, TP is below entry

        # Create OrderSendRequest
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=symbol,
            operation=trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_SELL,
            volume=volume,
            price=tick.bid,
            slippage=10,
            comment=comment,
            expert_id=magic
        )

        # Set SL/TP if provided
        if sl_price is not None:
            order_req.stop_loss = sl_price
        if tp_price is not None:
            order_req.take_profit = tp_price

        # Send order
        result = await self._service.place_order(order_req)

        if result.returned_code != 10009:
            raise RuntimeError(
                f"Order failed: code={result.returned_code}, comment={result.comment}"
            )

        return result.order

    async def buy_limit_with_sltp(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        price: float = 0.0,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        sl_pips: Optional[float] = None,
        tp_pips: Optional[float] = None,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Place BUY LIMIT pending order with Stop Loss and Take Profit.

        Args:
            symbol: Trading symbol
            volume: Volume in lots
            price: Limit order price
            sl: Stop Loss price (absolute)
            tp: Take Profit price (absolute)
            sl_pips: Stop Loss in pips (alternative to sl)
            tp_pips: Take Profit in pips (alternative to tp)
            comment: Order comment
            magic: Magic number

        Returns:
            Order ticket number

        Example:
            ticket = await sugar.buy_limit_with_sltp("EURUSD", 0.1, price=1.0850, sl_pips=50, tp_pips=100)
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        # Calculate SL/TP from pips if needed
        sl_price = sl
        tp_price = tp

        if sl_pips is not None or tp_pips is not None:
            symbol_info = await self.get_symbol_info(symbol)
            point = symbol_info.point

            if sl_pips is not None:
                sl_price = price - (sl_pips * point * 10)  # For BUY, SL is below entry
            if tp_pips is not None:
                tp_price = price + (tp_pips * point * 10)  # For BUY, TP is above entry

        # Create OrderSendRequest
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=symbol,
            operation=trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY_LIMIT,
            volume=volume,
            price=price,
            comment=comment,
            expert_id=magic
        )

        # Set SL/TP if provided
        if sl_price is not None:
            order_req.stop_loss = sl_price
        if tp_price is not None:
            order_req.take_profit = tp_price

        # Send order
        result = await self._service.place_order(order_req)

        if result.returned_code != 10009:
            raise RuntimeError(
                f"Order failed: code={result.returned_code}, comment={result.comment}"
            )

        return result.order

    async def sell_limit_with_sltp(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        price: float = 0.0,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        sl_pips: Optional[float] = None,
        tp_pips: Optional[float] = None,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Place SELL LIMIT pending order with Stop Loss and Take Profit.

        Args:
            symbol: Trading symbol
            volume: Volume in lots
            price: Limit order price
            sl: Stop Loss price (absolute)
            tp: Take Profit price (absolute)
            sl_pips: Stop Loss in pips (alternative to sl)
            tp_pips: Take Profit in pips (alternative to tp)
            comment: Order comment
            magic: Magic number

        Returns:
            Order ticket number

        Example:
            ticket = await sugar.sell_limit_with_sltp("EURUSD", 0.1, price=1.0950, sl_pips=50, tp_pips=100)
        """
        symbol = symbol or self._default_symbol
        if not symbol:
            raise ValueError("Symbol must be specified or set as default")

        # Calculate SL/TP from pips if needed
        sl_price = sl
        tp_price = tp

        if sl_pips is not None or tp_pips is not None:
            symbol_info = await self.get_symbol_info(symbol)
            point = symbol_info.point

            if sl_pips is not None:
                sl_price = price + (sl_pips * point * 10)  # For SELL, SL is above entry
            if tp_pips is not None:
                tp_price = price - (tp_pips * point * 10)  # For SELL, TP is below entry

        # Create OrderSendRequest
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=symbol,
            operation=trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_SELL_LIMIT,
            volume=volume,
            price=price,
            comment=comment,
            expert_id=magic
        )

        # Set SL/TP if provided
        if sl_price is not None:
            order_req.stop_loss = sl_price
        if tp_price is not None:
            order_req.take_profit = tp_price

        # Send order
        result = await self._service.place_order(order_req)

        if result.returned_code != 10009:
            raise RuntimeError(
                f"Order failed: code={result.returned_code}, comment={result.comment}"
            )

        return result.order
    
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 6 POSITION MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════════

    async def close_position(self, ticket: int) -> bool:
        """
        Close position completely by ticket.

        Args:
            ticket: Position ticket number

        Returns:
            True if position closed successfully

        Technical: Creates OrderCloseRequest with ticket, calls service.close_order().
        Returns True only if return_code == 10009 (TRADE_RETCODE_DONE).
        Server creates opposite market order to close position (BUY→SELL, SELL→BUY).
        """
        # Create OrderCloseRequest
        close_req = trading_helper_pb2.OrderCloseRequest(
            ticket=ticket
        )

        # Send close order - returns int (return code)
        return_code = await self._service.close_order(close_req)

        return return_code == 10009  # TRADE_RETCODE_DONE

    async def close_all_positions(self, symbol: Optional[str] = None) -> int:
        """
        Close all open positions.

        Args:
            symbol: If specified, close only positions for this symbol

        Returns:
            Number of positions closed

        Technical: Calls service.get_opened_orders() to fetch position_infos, iterates and calls close_position() for each.
        Filters by symbol if specified. Continues closing remaining positions even if individual close fails.
        Returns count of successfully closed positions (where close_position returned True).
        """
        positions_data = await self._service.get_opened_orders(sort_mode=0)
        closed_count = 0

        for position in positions_data.position_infos:
            # Filter by symbol if specified
            if symbol and position.symbol != symbol:
                continue

            try:
                if await self.close_position(position.ticket):
                    closed_count += 1
            except Exception as e:
                # Log error but continue closing other positions
                print(f"Failed to close position {position.ticket}: {e}")

        return closed_count

    async def modify_position_sltp(
        self,
        ticket: int,
        sl: Optional[float] = None,
        tp: Optional[float] = None
    ) -> bool:
        """
        Modify position SL/TP.

        Args:
            ticket: Position ticket number
            sl: New Stop Loss price (None to keep current)
            tp: New Take Profit price (None to keep current)

        Returns:
            True if modification successful

        Technical: Fetches position via get_opened_orders() to get current SL/TP, preserves unmodified values.
        Creates OrderModifyRequest with ticket + stop_loss + take_profit. Returns True if returned_code == 10009.
        Raises ValueError if position not found. SL/TP must respect broker's minimum stop level.
        """
        # Get position info
        positions_data = await self._service.get_opened_orders(sort_mode=0)

        position = None
        for pos in positions_data.position_infos:
            if pos.ticket == ticket:
                position = pos
                break

        if not position:
            raise ValueError(f"Position {ticket} not found")

        # Create OrderModifyRequest with direct fields
        modify_req = trading_helper_pb2.OrderModifyRequest(
            ticket=ticket,
            stop_loss=sl if sl is not None else position.stop_loss,
            take_profit=tp if tp is not None else position.take_profit
        )

        # Send modify order
        result = await self._service.modify_order(modify_req)

        return result.returned_code == 10009  # TRADE_RETCODE_DONE

    async def close_position_partial(self, ticket: int, volume: float) -> bool:
        """
        Partially close position by specified volume.

        Args:
            ticket: Position ticket number
            volume: Volume to close (must be less than position volume)

        Returns:
            True if partial close successful

        Example:
            # Close half of the position volume
            success = await sugar.close_position_partial(123456, 0.05)
        """
        # Get position info
        positions_data = await self._service.get_opened_orders(sort_mode=0)

        position = None
        for pos in positions_data.position_infos:
            if pos.ticket == ticket:
                position = pos
                break

        if not position:
            raise ValueError(f"Position {ticket} not found")

        if volume >= position.volume:
            raise ValueError(f"Partial volume {volume} must be less than position volume {position.volume}")

        # Determine opposite order type and price
        if position.type == trade_functions_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY:
            # Position is BUY, close with SELL
            operation = trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_SELL
            tick = await self._service.get_symbol_tick(position.symbol)
            price = tick.bid
        else:
            # Position is SELL, close with BUY
            operation = trading_helper_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY
            tick = await self._service.get_symbol_tick(position.symbol)
            price = tick.ask

        # Create OrderSendRequest with direct fields for partial close
        order_req = trading_helper_pb2.OrderSendRequest(
            symbol=position.symbol,
            operation=operation,
            volume=volume,
            price=price,
            slippage=10,  # Default slippage in points
            stop_loss=0.0,
            take_profit=0.0,
            comment=f"Partial close #{ticket}"
        )

        result = await self._service.place_order(order_req)

        return result.returned_code == 10009

    async def modify_position_sl(self, ticket: int, sl: float) -> bool:
        """
        Modify position Stop Loss only.

        Args:
            ticket: Position ticket number
            sl: New Stop Loss price

        Returns:
            True if modification successful

        Example:
            success = await sugar.modify_position_sl(123456, 1.0900)
        """
        return await self.modify_position_sltp(ticket, sl=sl, tp=None)

    async def modify_position_tp(self, ticket: int, tp: float) -> bool:
        """
        Modify position Take Profit only.

        Args:
            ticket: Position ticket number
            tp: New Take Profit price

        Returns:
            True if modification successful

        Example:
            success = await sugar.modify_position_tp(123456, 1.1000)
        """
        return await self.modify_position_sltp(ticket, sl=None, tp=tp)
    
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 7. POSITION INFORMATION
    # ══════════════════════════════════════════════════════════════════════════

    async def get_open_positions(self):
        """Get all open positions."""
        positions_data = await self._service.get_opened_orders(sort_mode=0)
        return list(positions_data.position_infos)

    async def get_position_by_ticket(self, ticket: int):
        """Get position by ticket number."""
        positions_data = await self._service.get_opened_orders(sort_mode=0)

        for pos in positions_data.position_infos:
            if pos.ticket == ticket:
                return pos

        return None

    async def get_positions_by_symbol(self, symbol: str):
        """Get all positions for specified symbol."""
        positions_data = await self._service.get_opened_orders(sort_mode=0)

        return [pos for pos in positions_data.position_infos if pos.symbol == symbol]

    async def has_open_position(self, symbol: Optional[str] = None) -> bool:
        """Check if there are open positions (optionally filtered by symbol)."""
        positions_data = await self._service.get_opened_orders(sort_mode=0)

        if symbol is None:
            return len(positions_data.position_infos) > 0

        return any(pos.symbol == symbol for pos in positions_data.position_infos)

    async def count_open_positions(self, symbol: Optional[str] = None) -> int:
        """Count open positions (optionally filtered by symbol)."""
        positions_data = await self._service.get_opened_orders(sort_mode=0)

        if symbol is None:
            return len(positions_data.position_infos)

        return sum(1 for pos in positions_data.position_infos if pos.symbol == symbol)

    async def get_total_profit(self) -> float:
        """Get total profit/loss across all open positions."""
        positions_data = await self._service.get_opened_orders(sort_mode=0)

        return sum(pos.profit for pos in positions_data.position_infos)

    async def get_profit_by_symbol(self, symbol: str) -> float:
        """Get total profit/loss for positions of specified symbol."""
        positions_data = await self._service.get_opened_orders(sort_mode=0)

        return sum(pos.profit for pos in positions_data.position_infos if pos.symbol == symbol)
    
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 8. HISTORY & STATISTICS
    # ══════════════════════════════════════════════════════════════════════════

    def _get_period_range(
        self,
        period: Period,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Tuple[datetime, datetime]:
        """Helper to convert Period enum to datetime range."""
        today = date.today()

        if period == Period.TODAY:
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today, datetime.max.time())

        elif period == Period.YESTERDAY:
            yesterday = today - timedelta(days=1)
            start = datetime.combine(yesterday, datetime.min.time())
            end = datetime.combine(yesterday, datetime.max.time())

        elif period == Period.THIS_WEEK:
            # Start of week (Monday)
            start_of_week = today - timedelta(days=today.weekday())
            start = datetime.combine(start_of_week, datetime.min.time())
            end = datetime.combine(today, datetime.max.time())

        elif period == Period.THIS_MONTH:
            # Start of month
            start_of_month = today.replace(day=1)
            start = datetime.combine(start_of_month, datetime.min.time())
            end = datetime.combine(today, datetime.max.time())

        elif period == Period.CUSTOM:
            if from_date is None or to_date is None:
                raise ValueError("from_date and to_date required for CUSTOM period")
            start = datetime.combine(from_date, datetime.min.time())
            end = datetime.combine(to_date, datetime.max.time())

        else:
            raise ValueError(f"Unknown period: {period}")

        return (start, end)

    async def get_deals(
        self,
        period: Period = Period.TODAY,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List:
        """
        Get deals for specified period.

        Args:
            period: Predefined period (TODAY, YESTERDAY, THIS_WEEK, THIS_MONTH, CUSTOM)
            from_date: Custom start date (required if period=CUSTOM)
            to_date: Custom end date (required if period=CUSTOM)

        Returns:
            List of orders (deals) for the specified period

        Technical: Converts Period enum to datetime range via _get_period_range(), calls service.get_positions_history().
        Uses positions_history (not order_history) to get profit/commission/swap for each closed position.
        Sets size=10000 to fetch all positions. Returns history_positions list with full position details.
        """
        from_dt, to_dt = self._get_period_range(period, from_date, to_date)

        # Use positions_history instead of order_history to get profit data
        from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as account_helper_pb2

        history_data = await self._service.get_positions_history(
            sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
            open_from=from_dt,
            open_to=to_dt,
            page=0,
            size=10000  # Large number to get all positions
        )

        return list(history_data.history_positions)

    async def get_profit(
        self,
        period: Period = Period.TODAY,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> float:
        """
        Get total profit for specified period.

        Args:
            period: Predefined period (TODAY, YESTERDAY, THIS_WEEK, THIS_MONTH, CUSTOM)
            from_date: Custom start date (required if period=CUSTOM)
            to_date: Custom end date (required if period=CUSTOM)

        Returns:
            Total profit for the period

        Technical: Calls get_deals() to fetch positions, sums order.profit field across all positions.
        Includes both gross profit and losses. Does not subtract commission/swap (use get_daily_stats for that).
        Returns net realized P&L for closed positions only.
        """
        deals = await self.get_deals(period, from_date, to_date)
        return sum(order.profit for order in deals)

    async def get_deals_today(self) -> List:
        """
        Get all deals made today.

        Returns:
            List of today's orders

        Example:
            deals = await sugar.get_deals_today()
            print(f"Today's deals: {len(deals)}")
        """
        return await self.get_deals(Period.TODAY)

    async def get_deals_yesterday(self) -> List:
        """
        Get all deals made yesterday.

        Returns:
            List of yesterday's orders

        Example:
            deals = await sugar.get_deals_yesterday()
        """
        return await self.get_deals(Period.YESTERDAY)

    async def get_deals_this_week(self) -> List:
        """
        Get all deals made this week (from Monday to today).

        Returns:
            List of this week's orders

        Example:
            deals = await sugar.get_deals_this_week()
            print(f"This week: {len(deals)} deals")
        """
        return await self.get_deals(Period.THIS_WEEK)

    async def get_deals_this_month(self) -> List:
        """
        Get all deals made this month.

        Returns:
            List of this month's orders

        Example:
            deals = await sugar.get_deals_this_month()
            total_volume = sum(d.volume for d in deals)
        """
        return await self.get_deals(Period.THIS_MONTH)

    async def get_deals_date_range(self, from_date: date, to_date: date) -> List:
        """
        Get all deals within a specific date range.

        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)

        Returns:
            List of orders in the date range

        Example:
            # Get January 2024 deals
            deals = await sugar.get_deals_date_range(
                date(2024, 1, 1),
                date(2024, 1, 31)
            )
        """
        return await self.get_deals(Period.CUSTOM, from_date, to_date)

    async def get_profit_today(self) -> float:
        """
        Get total profit made today.

        Returns:
            Today's profit/loss

        Example:
            profit = await sugar.get_profit_today()
            print(f"Today's P/L: {profit:.2f}")
        """
        return await self.get_profit(Period.TODAY)

    async def get_profit_this_week(self) -> float:
        """
        Get total profit made this week.

        Returns:
            This week's profit/loss

        Example:
            profit = await sugar.get_profit_this_week()
        """
        return await self.get_profit(Period.THIS_WEEK)

    async def get_profit_this_month(self) -> float:
        """
        Get total profit made this month.

        Returns:
            This month's profit/loss

        Example:
            profit = await sugar.get_profit_this_month()
            balance = await sugar.get_balance()
            monthly_return = (profit / balance) * 100
            print(f"Monthly return: {monthly_return:.2f}%")
        """
        return await self.get_profit(Period.THIS_MONTH)
    
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 9. SYMBOL INFORMATION
    # ══════════════════════════════════════════════════════════════════════════

    async def get_symbol_info(self, symbol: str) -> SymbolInfo:
        """
        Get complete symbol information.

        Technical: Calls service.get_symbol_params_many(name_filter=symbol) to fetch SymbolParams.
        Extracts 10 key fields (name, bid, ask, spread, digits, point, volume limits, contract_size) into SymbolInfo.
        Raises ValueError if symbol not found. Faster than 10 separate SymbolInfoDouble/Integer calls.
        """
        params_list, _ = await self._service.get_symbol_params_many(name_filter=symbol)

        if not params_list:
            raise ValueError(f"Symbol {symbol} not found")

        params = params_list[0]
        return SymbolInfo(
            name=params.name,
            bid=params.bid,
            ask=params.ask,
            spread=params.spread,
            digits=params.digits,
            point=params.point,
            volume_min=params.volume_min,
            volume_max=params.volume_max,
            volume_step=params.volume_step,
            contract_size=params.trade_contract_size
        )

    async def get_all_symbols(self) -> List[str]:
        """
        Get list of all available symbols.

        Uses optimized batch fetching (symbol_params_many) to retrieve all symbols
        efficiently in pages instead of individual calls.
        """
        symbols = []
        page = 1
        page_size = 100  # Fetch 100 symbols per request

        while True:
            symbol_params, total = await self._service.get_symbol_params_many(
                name_filter=None,
                sort_mode=None,
                page_number=page,
                items_per_page=page_size
            )

            # Extract symbol names
            symbols.extend([s.name for s in symbol_params])

            # Check if we got all symbols
            if len(symbols) >= total or len(symbol_params) < page_size:
                break

            page += 1

        return symbols

    async def is_symbol_available(self, symbol: str) -> bool:
        """Check if symbol exists and is tradable"""
        exists, _ = await self._service.symbol_exist(symbol)
        return exists

    async def get_min_stop_level(self, symbol: str) -> int:
        """
        Get minimum stop level (minimum distance for SL/TP) in points.

        Args:
            symbol: Trading symbol

        Returns:
            Minimum stop level in points

        Example:
            min_level = await sugar.get_min_stop_level("EURUSD")
            print(f"Minimum SL/TP distance: {min_level} points")
        """
        from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2
        return await self._service.get_symbol_integer(
            symbol,
            market_info_pb2.SYMBOL_TRADE_STOPS_LEVEL
        )

    async def get_symbol_digits(self, symbol: str) -> int:
        """
        Get number of decimal places in symbol price.

        Args:
            symbol: Trading symbol

        Returns:
            Number of digits after decimal point

        Example:
            digits = await sugar.get_symbol_digits("EURUSD")
            print(f"EURUSD has {digits} digits")  # Usually 5 for EURUSD
        """
        from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2
        return await self._service.get_symbol_integer(
            symbol,
            market_info_pb2.SYMBOL_DIGITS
        )
    
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 10. RISK MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════════

    async def calculate_position_size(
        self,
        symbol: str,
        risk_percent: float,
        sl_pips: float
    ) -> float:
        """
        Calculate position size based on risk percentage.

        Args:
            symbol: Trading symbol
            risk_percent: Risk as percentage of balance (e.g., 2.0 for 2%)
            sl_pips: Stop Loss distance in pips

        Returns:
            Optimal position size in lots

        Technical: Calculates risk_amount = balance × (risk_percent / 100), pip_value = point × 10 × contract_size.
        Formula: volume = risk_amount / (sl_pips × pip_value). Rounds to volume_step, clamps to volume_min/max.
        Fetches symbol_info for point, contract_size, volume constraints. Standard forex risk management formula.
        """
        # Get account balance
        balance = await self.get_balance()

        # Get symbol information
        symbol_info = await self.get_symbol_info(symbol)

        # Calculate risk amount in account currency
        risk_amount = balance * (risk_percent / 100.0)

        # Calculate pip value for 1 lot
        # For most forex pairs: pip_value = point * contract_size
        pip_value = symbol_info.point * 10 * symbol_info.contract_size

        # Calculate position size
        # risk_amount = sl_pips * pip_value * volume
        # volume = risk_amount / (sl_pips * pip_value)
        volume = risk_amount / (sl_pips * pip_value)

        # Round to symbol's volume step
        volume = round(volume / symbol_info.volume_step) * symbol_info.volume_step

        # Ensure volume is within limits
        if volume < symbol_info.volume_min:
            volume = symbol_info.volume_min
        elif volume > symbol_info.volume_max:
            volume = symbol_info.volume_max

        return volume

    async def can_open_position(
        self,
        symbol: str,
        volume: float
    ) -> Tuple[bool, str]:
        """
        Validate if position can be opened.

        Args:
            symbol: Trading symbol
            volume: Position volume in lots

        Returns:
            (can_open, reason) tuple

        """
        # Get current price
        tick = await self._service.get_symbol_tick(symbol)

        # Create MQL trade request for BUY
        mql_trade_req = trade_functions_pb2.MrpcMqlTradeRequest(
            action=trade_functions_pb2.TRADE_ACTION_DEAL,
            symbol=symbol,
            volume=volume,
            price=tick.ask,
            order_type=trade_functions_pb2.ORDER_TYPE_TF_BUY,
            type_filling=trade_functions_pb2.ORDER_FILLING_IOC,
            type_time=trade_functions_pb2.ORDER_TIME_GTC
        )

        # Wrap in OrderCheckRequest
        check_request = trade_functions_pb2.OrderCheckRequest(
            mql_trade_request=mql_trade_req
        )

        # Check order
        try:
            result = await self._service.check_order(check_request)

            if result.returned_code == 0:  # CHECK_OK
                return (True, "OK")
            else:
                return (False, f"Check failed: code={result.returned_code}")

        except Exception as e:
            return (False, f"Check error: {str(e)}")

    async def get_max_lot_size(self, symbol: str) -> float:
        """
        Get maximum lot size allowed for this symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Maximum volume in lots

        Example:
            max_lots = await sugar.get_max_lot_size("EURUSD")
            print(f"Maximum lot size: {max_lots}")
        """
        from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2
        return await self._service.get_symbol_double(
            symbol,
            market_info_pb2.SYMBOL_VOLUME_MAX
        )

    async def calculate_required_margin(
        self,
        symbol: str,
        volume: float,
        order_type: Optional[int] = None
    ) -> float:
        """
        Calculate margin required to open a position.

        Args:
            symbol: Trading symbol
            volume: Position volume in lots
            order_type: Order type enum value (default: BUY)

        Returns:
            Required margin in account currency

        Technical: Fetches current tick, selects price (ASK for BUY, BID for SELL), creates OrderCalcMarginRequest.
        Calls account.order_calc_margin() directly (bypasses service layer). Returns result.margin float.
        Use to verify sufficient free_margin before placing order. Margin = volume × contract_size × price / leverage.
        """
        # Get current price
        tick = await self._service.get_symbol_tick(symbol)

        # Default to BUY if not specified
        if order_type is None:
            order_type = trade_functions_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY

        # Determine price based on order type
        if order_type == trade_functions_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY:
            price = tick.ask
        else:
            price = tick.bid

        # Create calc margin request
        request = trade_functions_pb2.OrderCalcMarginRequest(
            symbol=symbol,
            order_type=order_type,
            volume=volume,
            open_price=price
        )

        # Calculate margin using proper accessor
        account = self._service.get_account()
        result = await account.order_calc_margin(request)

        return result.margin
    
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 11. TRADING HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    async def calculate_sltp(
        self,
        symbol: str,
        is_buy: bool,
        sl_pips: Optional[float] = None,
        tp_pips: Optional[float] = None
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert SL/TP from pips to absolute prices.

        Args:
            symbol: Trading symbol
            is_buy: True for BUY, False for SELL
            sl_pips: Stop Loss in pips (None to skip)
            tp_pips: Take Profit in pips (None to skip)

        Returns:
            Tuple (sl_price, tp_price). Returns None for values not specified.

        Example:
            # For BUY position
            sl_price, tp_price = await sugar.calculate_sltp("EURUSD", True, 50, 100)
            print(f"SL: {sl_price}, TP: {tp_price}")

            # For SELL position
            sl_price, tp_price = await sugar.calculate_sltp("EURUSD", False, 50, 100)
        """
        # Get current price and symbol info
        tick = await self._service.get_symbol_tick(symbol)
        symbol_info = await self.get_symbol_info(symbol)
        point = symbol_info.point

        sl_price = None
        tp_price = None

        if is_buy:
            # For BUY: SL below entry, TP above entry
            entry_price = tick.ask
            if sl_pips is not None:
                sl_price = entry_price - (sl_pips * point * 10)
            if tp_pips is not None:
                tp_price = entry_price + (tp_pips * point * 10)
        else:
            # For SELL: SL above entry, TP below entry
            entry_price = tick.bid
            if sl_pips is not None:
                sl_price = entry_price + (sl_pips * point * 10)
            if tp_pips is not None:
                tp_price = entry_price - (tp_pips * point * 10)

        return (sl_price, tp_price)

    async def buy_market_with_pips(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        sl_pips: Optional[float] = None,
        tp_pips: Optional[float] = None,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Open BUY position at market with SL/TP specified in pips.

        This is an alias for buy_market_with_sltp() with pips parameters.

        Args:
            symbol: Trading symbol
            volume: Volume in lots
            sl_pips: Stop Loss in pips
            tp_pips: Take Profit in pips
            comment: Order comment
            magic: Magic number

        Returns:
            Position ticket number

        Example:
            # Buy 0.1 lot with 50 pip SL and 100 pip TP
            ticket = await sugar.buy_market_with_pips("EURUSD", 0.1, 50, 100)
        """
        return await self.buy_market_with_sltp(
            symbol=symbol,
            volume=volume,
            sl_pips=sl_pips,
            tp_pips=tp_pips,
            comment=comment,
            magic=magic
        )

    async def sell_market_with_pips(
        self,
        symbol: Optional[str] = None,
        volume: float = 0.01,
        sl_pips: Optional[float] = None,
        tp_pips: Optional[float] = None,
        comment: str = "",
        magic: int = 0
    ) -> int:
        """
        Open SELL position at market with SL/TP specified in pips.

        This is an alias for sell_market_with_sltp() with pips parameters.

        Args:
            symbol: Trading symbol
            volume: Volume in lots
            sl_pips: Stop Loss in pips
            tp_pips: Take Profit in pips
            comment: Order comment
            magic: Magic number

        Returns:
            Position ticket number

        Example:
            # Sell 0.1 lot with 50 pip SL and 100 pip TP
            ticket = await sugar.sell_market_with_pips("EURUSD", 0.1, 50, 100)
        """
        return await self.sell_market_with_sltp(
            symbol=symbol,
            volume=volume,
            sl_pips=sl_pips,
            tp_pips=tp_pips,
            comment=comment,
            magic=magic
        )
    
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # region 12. ACCOUNT INFORMATION
    # ══════════════════════════════════════════════════════════════════════════
    
    async def get_account_info(self) -> AccountInfo:
        """
        Get complete account information in a structured dataclass.

        Returns:
            AccountInfo dataclass with all account details

        Example:
            account = await sugar.get_account_info()
            print(f"Account: {account.login}")
            print(f"Balance: {account.balance}")
            print(f"Equity: {account.equity}")
            print(f"Free Margin: {account.free_margin}")
            print(f"Margin Level: {account.margin_level}%")
        """
        summary = await self._service.get_account_summary()

        return AccountInfo(
            login=summary.login,
            balance=summary.balance,
            equity=summary.equity,
            margin=summary.margin,
            free_margin=summary.free_margin,
            margin_level=summary.margin_level,
            profit=summary.profit,
            currency=summary.currency,
            leverage=summary.leverage,
            company=summary.company_name
        )

    async def get_daily_stats(self, target_date: Optional[date] = None) -> DailyStats:
        """
        Get daily trading statistics.

        Args:
            target_date: Date to get stats for (default: today)

        Returns:
            DailyStats dataclass with trading statistics for the day

        Example:
            # Today's stats
            stats = await sugar.get_daily_stats()
            print(f"Deals: {stats.deals_count}")
            print(f"Profit: {stats.profit}")
            print(f"Volume: {stats.volume} lots")

            # Specific date
            stats = await sugar.get_daily_stats(date(2024, 1, 15))
        """
        if target_date is None:
            target_date = date.today()

        # Convert date to datetime range (start of day to end of day)
        from_dt = datetime.combine(target_date, datetime.min.time())
        to_dt = datetime.combine(target_date, datetime.max.time())

        # Get positions history for the day (includes profit data)
        from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as account_helper_pb2
        history_data = await self._service.get_positions_history(
            sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
            open_from=from_dt,
            open_to=to_dt,
            page=0,
            size=10000
        )

        # Calculate statistics
        deals_count = 0
        total_profit = 0.0
        total_commission = 0.0
        total_swap = 0.0
        total_volume = 0.0

        for position in history_data.history_positions:
            deals_count += 1
            total_profit += position.profit
            total_commission += position.commission
            total_swap += position.swap
            total_volume += position.volume

        return DailyStats(
            date=target_date,
            deals_count=deals_count,
            profit=total_profit,
            commission=total_commission,
            swap=total_swap,
            volume=total_volume
        )
    
    # endregion


    # ══════════════════════════════════════════════════════════════════════════
    # CONTEXT MANAGER SUPPORT
    # ══════════════════════════════════════════════════════════════════════════

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Cleanup if needed
        pass
