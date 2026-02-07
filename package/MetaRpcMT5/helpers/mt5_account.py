"""
══════════════════════════════════════════════════════════════════════════════
MT5Account - Low-Level MetaTrader 5 gRPC Client
══════════════════════════════════════════════════════════════════════════════

This file implements the low-level MT5 API client with direct protobuf message
handling. All methods accept protobuf Request objects and return protobuf Data.

FACTORY METHOD (RECOMMENDED):
   • create()           - Create instance with auto-generated or explicit UUID

CONNECTION FEATURES:
   • TLS/SSL encryption enabled
   • Automatic keepalive (ping every 20 seconds)
   • Smart reconnection with backoff (200ms to 3 seconds)
   • Message size limits: 100 MB for large responses

TOTAL METHODS: 40 (35 unary RPCs + 5 streaming RPCs)

METHOD GROUPS:
──────────────────────────────────────────────────────────────────────────────

1. CONNECTION (2 methods)
   • connect_by_host_port       - Connect to MT5 by IP/host
   • connect_by_server_name     - Connect to MT5 by server name

2. ACCOUNT INFORMATION (4 methods)
   • account_summary            - Get all account data (RECOMMENDED)
   • account_info_double        - Get double properties (Balance, Equity, Margin)
   • account_info_integer       - Get integer properties (Login, Leverage)
   • account_info_string        - Get string properties (Currency, Company)

3. SYMBOL INFORMATION & OPERATIONS (13 methods)
   • symbols_total              - Count total/selected symbols
   • symbol_exist               - Check if symbol exists
   • symbol_name                - Get symbol name by index
   • symbol_select              - Add/remove symbol from Market Watch
   • symbol_is_synchronized     - Check sync status with server
   • symbol_info_double         - Get double properties (Bid, Ask, Point)
   • symbol_info_integer        - Get integer properties (Digits, Spread)
   • symbol_info_string         - Get string properties (Description)
   • symbol_info_margin_rate    - Get margin requirements
   • symbol_info_tick           - Get last tick data
   • symbol_info_session_quote  - Get quote session times
   • symbol_info_session_trade  - Get trade session times
   • symbol_params_many         - Get detailed parameters for multiple symbols

4. POSITIONS & ORDERS INFORMATION (6 methods)
   • positions_total            - Count open positions
   • opened_orders              - Get all opened orders & positions
   • opened_orders_tickets      - Get ticket numbers only
   • order_history              - Get historical orders
   • positions_history          - Get historical positions
   • tick_value_with_size       - Get tick value/size data

5. MARKET DEPTH / DOM (3 methods)
   • market_book_add            - Subscribe to Depth of Market
   • market_book_release        - Unsubscribe from DOM
   • market_book_get            - Get current market depth snapshot

6. TRADING OPERATIONS (6 methods)
   • order_send                 - Send market or pending order
   • order_modify               - Modify existing order
   • order_close                - Close market or pending order
   • order_check                - Validate order before sending
   • order_calc_margin          - Calculate required margin
   • order_calc_profit          - Calculate potential profit/loss

7. STREAMING METHODS (5 methods) - Real-time data streams
   • on_symbol_tick                        - Stream tick data (Bid/Ask updates)
   • on_trade                              - Stream trade events
   • on_position_profit                    - Stream position P&L updates
   • on_positions_and_pending_orders_tickets - Stream ticket changes
   • on_trade_transaction                  - Stream trade transaction events

UTILITIES:
   • get_headers                    - Generate request headers
   • reconnect                      - Reconnect helper
   • execute_with_reconnect         - Generic wrapper for unary RPCs
   • execute_stream_with_reconnect  - Generic wrapper for streaming RPCs

══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import grpc
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Callable, Awaitable, AsyncGenerator, Any
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.empty_pb2 import Empty

# import your generated stubs
import MetaRpcMT5.mt5_term_api_connection_pb2 as connection_pb2
import MetaRpcMT5.mt5_term_api_connection_pb2_grpc as connection_pb2_grpc
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2_grpc as account_helper_pb2_grpc
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_helper_pb2
import MetaRpcMT5.mt5_term_api_trading_helper_pb2_grpc as trading_helper_pb2_grpc
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2_grpc as market_info_pb2_grpc
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_functions_pb2
import MetaRpcMT5.mt5_term_api_trade_functions_pb2_grpc as trade_functions_pb2_grpc
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_information_pb2
import MetaRpcMT5.mt5_term_api_account_information_pb2_grpc as account_information_pb2_grpc
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
import MetaRpcMT5.mt5_term_api_subscriptions_pb2_grpc as subscriptions_pb2_grpc
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2_grpc as market_info_pb2_grpc
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2
import MetaRpcMT5.mt5_term_api_account_information_pb2_grpc as account_info_pb2_grpc

# Import centralized error classes from errors module (same package)
from .errors import (
    ApiError as ApiExceptionMT5,
    NotConnectedError as ConnectExceptionMT5,
)


# === MT5Account Class ===
class MT5Account:
    def __init__(self, user: int, password: str, grpc_server: Optional[str] = None, id_: Optional[UUID] = None):
        """
        Initialize MT5Account with gRPC connection.

        Args:
            user: MT5 account login
            password: MT5 account password
            grpc_server: gRPC server address (default: "mt5.mrpc.pro:443")
            id_: Terminal instance UUID (auto-generated if not provided)
        """
        self.user = user
        self.password = password
        self.grpc_server = grpc_server or "mt5.mrpc.pro:443"   # default server
        self.id = str(id_) if id_ else None

        # Configure TLS credentials
        credentials = grpc.ssl_channel_credentials()

        # Configure channel options for reliability and performance
        options = [
            # Keepalive: Send ping every 20 seconds to keep connection alive
            ('grpc.keepalive_time_ms', 20000),

            # Keepalive timeout: Wait 5 seconds for ping response
            ('grpc.keepalive_timeout_ms', 5000),

            # Allow keepalive pings even when no RPCs are active
            ('grpc.keepalive_permit_without_calls', 1),

            # Enable keepalive enforcement
            ('grpc.http2.max_pings_without_data', 0),

            # Initial backoff on connection failure: 200ms
            ('grpc.initial_reconnect_backoff_ms', 200),

            # Maximum backoff: 3 seconds
            ('grpc.max_reconnect_backoff_ms', 3000),

            # Minimum time to wait before attempting reconnect: 5 seconds
            ('grpc.min_reconnect_backoff_ms', 5000),

            # Maximum connection age: disable (0 = infinite)
            ('grpc.max_connection_age_ms', 0),

            # Message size limits (100 MB for large responses)
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),
        ]

        # Create async gRPC secure channel with advanced options
        self.channel = grpc.aio.secure_channel(
            self.grpc_server,
            credentials,
            options=options
        )

        # Init stubs directly
        self.connection_client = connection_pb2_grpc.ConnectionStub(self.channel)
        self.subscription_client = subscriptions_pb2_grpc.SubscriptionServiceStub(self.channel)
        self.account_client = account_helper_pb2_grpc.AccountHelperStub(self.channel)
        self.trade_client = trading_helper_pb2_grpc.TradingHelperStub(self.channel)
        self.market_info_client = market_info_pb2_grpc.MarketInfoStub(self.channel)
        self.trade_functions_client = trade_functions_pb2_grpc.TradeFunctionsStub(self.channel)
        self.account_information_client = account_information_pb2_grpc.AccountInformationStub(self.channel)

        # Connection state
        self.host = None
        self.port = None
        self.server_name = None
        self.base_chart_symbol = None
        self.connect_timeout_seconds = 30

    # ══════════════════════════════════════════════════════════════════════════
    # region FACTORY METHODS
    # ══════════════════════════════════════════════════════════════════════════

    @classmethod
    def create(
        cls,
        user: int,
        password: str,
        grpc_server: str = "",
        id_: Optional[UUID] = None
    ) -> "MT5Account":
        """
        Create MT5Account instance with auto-generated or explicit UUID.

        RECOMMENDED factory method that creates a new MT5Account with gRPC connection.
        The connection is established with TLS, keepalive, and automatic reconnect configured.
        If id_ is not provided, a random UUID is automatically generated.

        Args:
            user: MT5 account login number
            password: MT5 account password
            grpc_server: gRPC server address (default: "mt5.mrpc.pro:443" if empty)
            id_: Terminal instance UUID (optional, auto-generated if not provided)

        Returns:
            MT5Account: Initialized account instance (not yet connected to MT5 server)

        Examples:
            >>> # Auto-generated UUID (RECOMMENDED for most cases)
            >>> account = MT5Account.create(
            ...     user=12345678,
            ...     password="mypassword",
            ...     grpc_server="mt5.mrpc.pro:443"
            ... )
            >>>
            >>> # Explicit UUID (for advanced use cases)
            >>> from uuid import uuid4
            >>> account = MT5Account.create(
            ...     user=12345678,
            ...     password="mypassword",
            ...     grpc_server="mt5.mrpc.pro:443",
            ...     id_=uuid4()
            ... )
            >>> await account.connect_by_server_name("MetaQuotes-Demo", "EURUSD")
        """
        server = grpc_server if grpc_server else "mt5.mrpc.pro:443"
        terminal_id = id_ if id_ else uuid4()
        return cls(user=user, password=password, grpc_server=server, id_=terminal_id)

    # endregion

    # ══════════════════════════════════════════════════════════════════════════
    # region UTILITIES
    # ══════════════════════════════════════════════════════════════════════════

    def get_headers(self):
        return [("id", self.id)]

    async def reconnect(self, deadline: Optional[datetime] = None):
        if self.server_name:
            await self.connect_by_server_name(self.server_name, self.base_chart_symbol or "EURUSD",
                                              True, self.connect_timeout_seconds, deadline)
        elif self.host:
            await self.connect_by_host_port(self.host, self.port or 443,
                                            self.base_chart_symbol or "EURUSD", True,
                                            self.connect_timeout_seconds, deadline)

    async def execute_with_reconnect(
        self,
        grpc_call: Callable[[list[tuple[str, str]]], Awaitable[Any]],
        error_selector: Callable[[Any], Optional[Any]],
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        while cancellation_event is None or not cancellation_event.is_set():
            headers = self.get_headers()
            try:
                res = await grpc_call(headers)
            except grpc.aio.AioRpcError as ex:
                if ex.code() == grpc.StatusCode.UNAVAILABLE:
                    await asyncio.sleep(0.5)
                    await self.reconnect(deadline)
                    continue
                raise

            error = error_selector(res)
            if error and error.error_code in ("TERMINAL_INSTANCE_NOT_FOUND", "TERMINAL_REGISTRY_TERMINAL_NOT_FOUND"):
                await asyncio.sleep(0.5)
                await self.reconnect(deadline)
                continue

            if res.HasField("error") and res.error.error_message:
                raise ApiExceptionMT5(res.error)

            return res

        raise asyncio.CancelledError("The operation was canceled by the caller.")

    async def execute_stream_with_reconnect(
        self,
        request: Any,
        stream_invoker: Callable[[Any, list[tuple[str, str]]], grpc.aio.StreamStreamCall],
        get_error: Callable[[Any], Optional[Any]],
        get_data: Callable[[Any], Any],
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> AsyncGenerator[Any, None]:
        """
        Executes a gRPC server-streaming call with automatic reconnection logic on recoverable errors.

        Args:
            request: The request object to initiate the stream with.
            stream_invoker (Callable): A function that opens the stream. It receives the request and metadata headers,
                and returns an async streaming call.
            get_error (Callable): A function that extracts the error object (if any) from a reply.
                Return an object with .error_code == "TERMINAL_INSTANCE_NOT_FOUND" to trigger reconnect,
                or any non-null error to raise ApiExceptionMT5.
            get_data (Callable): A function that extracts the data object from a reply. If it returns None, the
                message is skipped.
            cancellation_event (asyncio.Event, optional): Event to cancel streaming and reconnection attempts.

        Yields:
            Extracted data items streamed from the server.

        Raises:
            ConnectExceptionMT5: If reconnection logic fails due to missing account context.
            ApiExceptionMT5: When the stream response contains a known API error.
            grpc.aio.AioRpcError: If a non-recoverable gRPC error occurs.
        """
        while cancellation_event is None or not cancellation_event.is_set():
            reconnect_required = False
            stream = None
            try:
                stream = stream_invoker(request, self.get_headers())
                async for reply in stream:
                    error = get_error(reply)

                    if error and error.error_code in (
                        "TERMINAL_INSTANCE_NOT_FOUND",
                        "TERMINAL_REGISTRY_TERMINAL_NOT_FOUND",
                    ):
                        reconnect_required = True
                        break

                    if error and getattr(error, "message", None):
                        raise ApiExceptionMT5(error)

                    data = get_data(reply)
                    if data is not None:
                        yield data

            except grpc.aio.AioRpcError as ex:
                if ex.code() == grpc.StatusCode.UNAVAILABLE:
                    reconnect_required = True
                else:
                    raise

            finally:
                if stream:
                    stream.cancel()  # close stream properly

            if reconnect_required:
                await asyncio.sleep(0.5)
                await self.reconnect()
            else:
                break

    # endregion

    # ══════════════════════════════════════════════════════════════════════════
    # region CONNECTION
    # ══════════════════════════════════════════════════════════════════════════

    async def connect_by_host_port(
        self,
        host: str,
        port: int = 443,
        base_chart_symbol: str = "EURUSD",
        wait_for_terminal_is_alive: bool = True,
        timeout_seconds: int = 30,
        deadline: Optional[datetime] = None,
    ):
        """
        Connects to MT5 server by IP address or hostname and port.

        Alternative connection method when you know the exact server address.
        For most cases, use connect_by_server_name() instead (simpler and recommended).

        The method establishes connection to MT5 terminal, waits for terminal readiness,
        and updates the instance GUID (self.id) from server response.

        Args:
            host (str): Server IP address or hostname (e.g., "mt5.broker.com").
            port (int, optional): Server port number. Defaults to 443.
            base_chart_symbol (str, optional): Base symbol for chart initialization.
                Defaults to "EURUSD".
            wait_for_terminal_is_alive (bool, optional): Wait for terminal readiness
                before returning. Defaults to True.
            timeout_seconds (int, optional): Timeout in seconds for terminal readiness
                waiting. Defaults to 30 seconds.
            deadline (datetime, optional): Deadline for gRPC call completion.

        Raises:
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails due to communication errors.

        Example:
            >>> account = MT5Account(user=12345, password="pass", grpc_server="localhost:9999")
            >>> await account.connect_by_host_port("mt5.broker.com", 443, "EURUSD")
            >>> print(f"Connected! Terminal GUID: {account.id}")
        """
        #Build connect request
        request = connection_pb2.ConnectRequest(
            user=self.user,
            password=self.password,
            host=host,
            port=port,
            base_chart_symbol=base_chart_symbol,
            wait_for_terminal_is_alive=wait_for_terminal_is_alive,
            terminal_readiness_waiting_timeout_seconds=timeout_seconds,
        )

        headers = []
        if self.id:
            headers.append(("id", str(self.id)))

        res = await self.connection_client.Connect(
            request,
            metadata=headers,
            timeout=30.0 if deadline is None else (deadline - datetime.utcnow()).total_seconds(),
        )

        if res.HasField("error") and res.error.error_message:
            raise ApiExceptionMT5(res.error)

        # Save state
        self.host = host
        self.port = port
        self.base_chart_symbol = base_chart_symbol
        self.connect_timeout_seconds = timeout_seconds
        self.id = res.data.terminalInstanceGuid

    async def connect_by_server_name(
        self,
        server_name: str,
        base_chart_symbol: str = "EURUSD",
        wait_for_terminal_is_alive: bool = True,
        timeout_seconds: int = 30,
        deadline: Optional[datetime] = None,
    ):
        """
        Connects to MT5 server by broker server name (cluster name).

        This is the RECOMMENDED connection method - simpler than connect_by_host_port.
        Used in all demonstration examples via create_and_connect_mt5() helper.

        The method establishes connection to MT5 terminal, waits for terminal readiness,
        and updates the instance GUID (self.id) from server response.

        Args:
            server_name (str): MT5 broker server/cluster name (e.g., "MetaQuotes-Demo").
            base_chart_symbol (str, optional): Base symbol for chart initialization.
                Defaults to "EURUSD".
            wait_for_terminal_is_alive (bool, optional): Wait for terminal readiness
                before returning. Defaults to True.
            timeout_seconds (int, optional): Timeout in seconds for terminal readiness
                waiting. Defaults to 30 seconds.
            deadline (datetime, optional): Deadline for gRPC call completion.

        Raises:
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails due to communication errors.

        Example:
            >>> account = MT5Account(user=12345, password="pass", grpc_server="localhost:9999")
            >>> await account.connect_by_server_name("MetaQuotes-Demo", "EURUSD")
            >>> print(f"Connected! Terminal GUID: {account.id}")
        """
        # Build connect request 
        request = connection_pb2.ConnectExRequest(
            user=self.user,
            password=self.password,
            mt_cluster_name=server_name,
            base_chart_symbol=base_chart_symbol,
            terminal_readiness_waiting_timeout_seconds=timeout_seconds,
        )

        headers = []
        if self.id:
            headers.append(("id", str(self.id)))
        res = await self.connection_client.ConnectEx(
            request,
            metadata=headers,
            timeout=30.0 if deadline is None else (deadline - datetime.utcnow()).total_seconds(),
        )

        if res.HasField("error") and res.error.error_message:
            raise ApiExceptionMT5(res.error)

        # Save state
        self.server_name = server_name
        self.base_chart_symbol = base_chart_symbol
        self.connect_timeout_seconds = timeout_seconds
        self.id = res.data.terminal_instance_guid

    # endregion

    # ══════════════════════════════════════════════════════════════════════════
    # region ACCOUNT INFORMATION
    # ══════════════════════════════════════════════════════════════════════════

    async def account_summary(
        self,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Gets the summary information for a trading account asynchronously.

        Args:
            deadline (datetime, optional): Deadline after which the request will be canceled
                if not completed.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            AccountSummaryData: The server's response containing account summary data.

        Raises:
            ConnectExceptionMT5: If the account is not connected before calling this method.
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails due to communication or protocol errors.
        """
        if not (self.host or self.server_name):
            raise ConnectExceptionMT5("Please call connect method first")

        request = account_helper_pb2.AccountSummaryRequest()

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                if timeout < 0:
                    timeout = 0
            return await self.account_client.AccountSummary(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )

        return res.data

    async def account_info_double(
        self,
        property_id: account_info_pb2.AccountInfoDoublePropertyType,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> float:
        """
        Retrieves a double-precision account property (e.g. balance, equity, margin).

        Args:
            property_id (AccountInfoDoublePropertyType): The account double property to retrieve.
            deadline (datetime, optional): Deadline after which the call will be cancelled.
            cancellation_event (asyncio.Event, optional): Event to cancel the operation.

        Returns:
            float: The double value of the requested account property.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = account_information_pb2.AccountInfoDoubleRequest(property_id=property_id)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.account_information_client.AccountInfoDouble(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda _: None,  # no error field
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data.requested_value

    async def account_info_integer(
        self,
        property_id: account_info_pb2.AccountInfoIntegerPropertyType,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> int:
        """
        Retrieves an integer account property (e.g. login, leverage, trade mode).

        Args:
            property_id (AccountInfoIntegerPropertyType): The account integer property to retrieve.
            deadline (datetime, optional): Deadline after which the call will be cancelled.
            cancellation_event (asyncio.Event, optional): Event to cancel the operation.

        Returns:
            int: The integer value of the requested account property.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = account_information_pb2.AccountInfoIntegerRequest(property_id=property_id)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.account_information_client.AccountInfoInteger(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda _: None,  # no error field
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data.requested_value

    async def account_info_string(
        self,
        property_id: account_info_pb2.AccountInfoStringPropertyType,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> str:
        """
        Retrieves a string account property (e.g. account name, currency, server).

        Args:
            property_id (AccountInfoStringPropertyType): The account string property to retrieve.
            deadline (datetime, optional): Deadline after which the call will be cancelled.
            cancellation_event (asyncio.Event, optional): Event to cancel the operation.

        Returns:
            str: The string value of the requested account property.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = account_information_pb2.AccountInfoStringRequest(property_id=property_id)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.account_information_client.AccountInfoString(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda _: None,  # no error field
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data.requested_value

    # endregion

    # ══════════════════════════════════════════════════════════════════════════
    # region SYMBOL INFORMATION & OPERATIONS
    # ══════════════════════════════════════════════════════════════════════════

    async def symbols_total(
        self,
        selected_only: bool,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Returns the total number of symbols available on the platform.

        Args:
            selected_only (bool): True to count only Market Watch symbols, false to count all.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolsTotalData: Total symbol count data.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolsTotalRequest(mode=selected_only)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolsTotal(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_exist(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Checks if a symbol with the specified name exists (standard or custom).

        Args:
            symbol (str): The symbol name to check.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolExistData: Information about symbol existence and type.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolExistRequest(name=symbol)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolExist(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_name(
        self,
        index: int,
        selected: bool,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Returns the name of a symbol by index.

        Args:
            index (int): Symbol index (starting at 0).
            selected (bool): True to use only Market Watch symbols.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolNameData: The symbol name at the specified index.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolNameRequest(index=index, selected=selected)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolName(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_select(
        self,
        symbol: str,
        select: bool,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Adds or removes a symbol from Market Watch.

        Args:
            symbol (str): Symbol name.
            select (bool): True to add, false to remove.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolSelectData: Success status of the operation.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolSelectRequest(symbol=symbol, select=select)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolSelect(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_is_synchronized(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Checks if the symbol's data is synchronized with the server.

        Args:
            symbol (str): Symbol name to check.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolIsSynchronizedData: True if synchronized, false otherwise.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolIsSynchronizedRequest(symbol=symbol)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolIsSynchronized(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_info_double(
        self,
        symbol: str,
        property: market_info_pb2.SymbolInfoDoubleProperty,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Retrieves a double-precision property value of a symbol.

        Args:
            symbol (str): Symbol name.
            property (SymbolInfoDoubleProperty): The double-type property to retrieve.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolInfoDoubleData: The double property value.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolInfoDoubleRequest(symbol=symbol, type=property)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolInfoDouble(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_info_integer(
        self,
        symbol: str,
        property: market_info_pb2.SymbolInfoIntegerProperty,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Retrieves an integer-type property value of a symbol.

        Args:
            symbol (str): Symbol name.
            property (SymbolInfoIntegerProperty): The integer property to query.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolInfoIntegerData: The integer property value.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolInfoIntegerRequest(symbol=symbol, type=property)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolInfoInteger(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_info_string(
        self,
        symbol: str,
        property: market_info_pb2.SymbolInfoStringProperty,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Retrieves a string-type property value of a symbol.

        Args:
            symbol (str): Symbol name.
            property (SymbolInfoStringProperty): The string property to retrieve.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolInfoStringData: The string property value.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolInfoStringRequest(symbol=symbol, type=property)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolInfoString(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_info_margin_rate(
        self,
        symbol: str,
        order_type: market_info_pb2.ENUM_ORDER_TYPE,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Retrieves the margin rates for a given symbol and order type.

        Args:
            symbol (str): Symbol name.
            order_type (ENUM_ORDER_TYPE): The order type (buy/sell/etc).
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolInfoMarginRateData: The initial and maintenance margin rates.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolInfoMarginRateRequest(symbol=symbol, order_type=order_type)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolInfoMarginRate(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_info_tick(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Retrieves the current tick data (bid, ask, last, volume) for a given symbol.

        Args:
            symbol (str): Symbol name to fetch tick info for.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            MrpcMqlTick: The latest tick information.

        Raises:
            ConnectExceptionMT5: If the account is not connected.
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolInfoTickRequest(symbol=symbol)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolInfoTick(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_info_session_quote(
        self,
        symbol: str,
        day_of_week: market_info_pb2.DayOfWeek,
        session_index: int,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Gets the quoting session start and end time for a symbol on a specific day and session index.

        Args:
            symbol (str): The symbol name.
            day_of_week (DayOfWeek): The day of the week.
            session_index (int): Index of the quoting session (starting at 0).
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolInfoSessionQuoteData: The session quote start and end time.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolInfoSessionQuoteRequest(
            symbol=symbol,
            day_of_week=day_of_week,
            session_index=session_index,
        )

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolInfoSessionQuote(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_info_session_trade(
        self,
        symbol: str,
        day_of_week: market_info_pb2.DayOfWeek,
        session_index: int,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Gets the trading session start and end time for a symbol on a specific day and session index.

        Args:
            symbol (str): The symbol name.
            day_of_week (DayOfWeek): The day of the week.
            session_index (int): Index of the trading session (starting at 0).
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolInfoSessionTradeData: The trading session start and end time.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.SymbolInfoSessionTradeRequest(
            symbol=symbol,
            day_of_week=day_of_week,
            session_index=session_index,
        )

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolInfoSessionTrade(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def symbol_params_many(
        self,
        request: account_helper_pb2.SymbolParamsManyRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Retrieves symbol parameters for multiple instruments asynchronously.

        Args:
            request (SymbolParamsManyRequest): The request containing filters and pagination.
            deadline (datetime, optional): Deadline after which the request will be canceled.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            SymbolParamsManyData: Symbol parameter details.

        Raises:
            ConnectExceptionMT5: If the account is not connected before calling this method.
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails due to communication or protocol errors.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                if timeout < 0:
                    timeout = 0
            return await self.account_client.SymbolParamsMany(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    # endregion

    # ══════════════════════════════════════════════════════════════════════════
    # region POSITIONS & ORDERS INFORMATION
    # ══════════════════════════════════════════════════════════════════════════

    async def positions_total(
        self,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Returns the total number of open positions on the current account.

        Args:
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            PositionsTotalData: The total number of open positions.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If gRPC fails to connect or respond.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = Empty()

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                timeout = max(timeout, 0)
            return await self.trade_functions_client.PositionsTotal(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def opened_orders(
        self,
        sort_mode: account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE = account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Gets the currently opened orders and positions for the connected account asynchronously.

        Args:
            sort_mode (BMT5_ENUM_OPENED_ORDER_SORT_TYPE): The sort mode for the opened orders
                (0 - open time, 1 - close time, 2 - ticket ID).
            deadline (datetime, optional): Deadline after which the request will be canceled
                if not completed.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            OpenedOrdersData: The result containing opened orders and positions.

        Raises:
            ConnectExceptionMT5: If the account is not connected before calling this method.
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails due to communication or protocol errors.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = account_helper_pb2.OpenedOrdersRequest(inputSortMode=sort_mode)

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                if timeout < 0:
                    timeout = 0
            return await self.account_client.OpenedOrders(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def opened_orders_tickets(
        self,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Gets ticket IDs of all currently opened orders and positions asynchronously.

        Args:
            deadline (datetime, optional): Deadline after which the request will be canceled.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            OpenedOrdersTicketsData: Collection of opened order and position tickets.

        Raises:
            ConnectExceptionMT5: If the account is not connected before calling this method.
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails due to communication or protocol errors.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = account_helper_pb2.OpenedOrdersTicketsRequest()

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                if timeout < 0:
                    timeout = 0
            return await self.account_client.OpenedOrdersTickets(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def order_history(
        self,
        from_dt: datetime,
        to_dt: datetime,
        sort_mode: account_helper_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE = account_helper_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_CLOSE_TIME_ASC,
        page_number: int = 0,
        items_per_page: int = 0,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Gets the historical orders for the connected trading account within the specified
        time range asynchronously.

        Args:
            from_dt (datetime): The start time for the history query (server time).
            to_dt (datetime): The end time for the history query (server time).
            sort_mode (BMT5_ENUM_ORDER_HISTORY_SORT_TYPE, optional):
                The sort mode (0 - by open time, 1 - by close time, 2 - by ticket ID).
            page_number (int, optional): Page number for paginated results (default 0).
            items_per_page (int, optional): Number of items per page (default 0 = all).
            deadline (datetime, optional): Deadline after which the request will be canceled.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            OrdersHistoryData: The server's response containing paged historical order data.

        Raises:
            ConnectExceptionMT5: If the account is not connected before calling this method.
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails due to communication or protocol errors.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = account_helper_pb2.OrderHistoryRequest(
            inputSortMode=sort_mode,
            pageNumber=page_number,
            itemsPerPage=items_per_page,
        )

        # Set timestamp fields (must be set separately - FromDatetime modifies in-place)
        request.inputFrom.FromDatetime(from_dt)
        request.inputTo.FromDatetime(to_dt)

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                if timeout < 0:
                    timeout = 0
            return await self.account_client.OrderHistory(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def positions_history(
    self,
    sort_type: account_helper_pb2.AH_ENUM_POSITIONS_HISTORY_SORT_TYPE,
    open_from: Optional[datetime] = None,
    open_to: Optional[datetime] = None,
    page: int = 0,
    size: int = 0,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Retrieves historical positions based on filter and time range asynchronously.

        Args:
            sort_type (AH_ENUM_POSITIONS_HISTORY_SORT_TYPE): Sorting type for historical positions.
            open_from (datetime, optional): Start of open time filter (UTC).
            open_to (datetime, optional): End of open time filter (UTC).
            page (int, optional): Page number for paginated results (default 0).
            size (int, optional): Number of items per page (default 0 = all).
            deadline (datetime, optional): Deadline after which the request will be canceled.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            PositionsHistoryData: Historical position records.

        Raises:
            ConnectExceptionMT5: If the account is not connected before calling this method.
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails due to communication or protocol errors.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = account_helper_pb2.PositionsHistoryRequest(
            sort_type=sort_type,
            page_number=page,
            items_per_page=size,
        )

        if open_from:
            request.position_open_time_from.FromDatetime(open_from)
        if open_to:
            request.position_open_time_to.FromDatetime(open_to)

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                if timeout < 0:
                    timeout = 0
            return await self.account_client.PositionsHistory(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def tick_value_with_size(
        self,
        symbols: list[str],
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Gets tick value and tick size data for the given symbols asynchronously.

        Args:
            symbols (list[str]): List of symbol names.
            deadline (datetime, optional): Deadline after which the request will be canceled.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            TickValueWithSizeData: Tick value and contract size info per symbol.

        Raises:
            ConnectExceptionMT5: If the account is not connected before calling this method.
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails due to communication or protocol errors.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = account_helper_pb2.TickValueWithSizeRequest()
        request.symbol_names.extend(symbols)

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                if timeout < 0:
                    timeout = 0
            return await self.account_client.TickValueWithSize(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    # endregion

    # ══════════════════════════════════════════════════════════════════════════
    # region MARKET DEPTH / DOM
    # ══════════════════════════════════════════════════════════════════════════

    async def market_book_add(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Opens the Depth of Market (DOM) for a symbol and subscribes to updates.

        Args:
            symbol (str): Symbol name to subscribe.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            MarketBookAddData: True if DOM subscription was successful.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.MarketBookAddRequest(symbol=symbol)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.MarketBookAdd(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def market_book_release(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Releases the Depth of Market (DOM) for a symbol and stops receiving updates.

        Args:
            symbol (str): Symbol name to unsubscribe.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            MarketBookReleaseData: True if DOM release was successful.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.MarketBookReleaseRequest(symbol=symbol)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.MarketBookRelease(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def market_book_get(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Gets the current Depth of Market (DOM) data for a symbol.

        Args:
            symbol (str): Symbol name.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            MarketBookGetData: A list of book entries for the symbol's DOM.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = market_info_pb2.MarketBookGetRequest(symbol=symbol)

        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.MarketBookGet(
                request,
                metadata=headers,
                timeout=max(timeout, 0) if timeout else None,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    # endregion

    # ══════════════════════════════════════════════════════════════════════════
    # region TRADING OPERATIONS
    # ══════════════════════════════════════════════════════════════════════════

    async def order_send(
        self,
        request: Any,  # trading_helper_pb2.OrderSendRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> "trading_helper_pb2.OrderSendData":
        """
        Sends a market or pending order to the trading server asynchronously.

        Args:
            request (OrderSendRequest): The order request to send.
            deadline (datetime, optional): Deadline for the operation.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            OrderSendData: Response with deal/order confirmation data.

        Raises:
            ConnectExceptionMT5: If the account is not connected.
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                if timeout < 0:
                    timeout = 0
            return await self.trade_client.OrderSend(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def order_modify(
        self,
        request: Any,  # OrderModifyRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Modifies an existing order or position asynchronously.

        Args:
            request (OrderModifyRequest): The modification request (SL, TP, price, expiration, etc.).
            deadline (datetime, optional): Deadline for the operation.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            OrderModifyData: Response containing updated order/deal info.

        Raises:
            ConnectExceptionMT5: If the account is not connected.
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                if timeout < 0:
                    timeout = 0
            return await self.trade_client.OrderModify(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def order_close(
        self,
        request: Any,  # OrderCloseRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Closes a market or pending order asynchronously.

        Args:
            request (OrderCloseRequest): The close request including ticket, volume, and slippage.
            deadline (datetime, optional): Deadline for the operation.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            OrderCloseData: The close result and return codes.

        Raises:
            ConnectExceptionMT5: If the account is not connected.
            ApiExceptionMT5: If the server returns an error in the response.
            grpc.aio.AioRpcError: If the gRPC call fails.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                if timeout < 0:
                    timeout = 0
            return await self.trade_client.OrderClose(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def order_check(
        self,
        request: Any,  # OrderCheckRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trade_functions_pb2.OrderCheckData:
        """
        Checks whether a trade request can be successfully executed under current market conditions.

        Args:
            request (OrderCheckRequest): The trade request to validate.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            OrderCheckData: Result of the trade request check, including margin and balance details.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If gRPC fails to connect or respond.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                timeout = max(timeout, 0)
            return await self.trade_functions_client.OrderCheck(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def order_calc_margin(
        self,
        request: Any,  # OrderCalcMarginRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trade_functions_pb2.OrderCalcMarginData:
        """
        Calculates the margin required for a planned trade operation.

        Args:
            request (OrderCalcMarginRequest): The request containing symbol, order type, volume, and price.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            OrderCalcMarginData: The required margin in account currency.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If gRPC fails to connect or respond.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                timeout = max(timeout, 0)
            return await self.trade_functions_client.OrderCalcMargin(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    async def order_calc_profit(
        self,
        request: Any,  # OrderCalcProfitRequest
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Calculates potential profit/loss for a planned trade operation.

        Args:
            request (OrderCalcProfitRequest): The request containing symbol, order type, volume, open price, and close price.
            deadline (datetime, optional): Deadline for the gRPC call.
            cancellation_event (asyncio.Event, optional): Event to cancel the request.

        Returns:
            OrderCalcProfitData: The potential profit/loss in account currency.

        Raises:
            ConnectExceptionMT5: If the client is not connected.
            ApiExceptionMT5: If the server returns a business error.
            grpc.aio.AioRpcError: If gRPC fails to connect or respond.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        async def grpc_call(headers):
            timeout = None
            if deadline:
                timeout = (deadline - datetime.utcnow()).total_seconds()
                timeout = max(timeout, 0)
            return await self.trade_functions_client.OrderCalcProfit(
                request,
                metadata=headers,
                timeout=timeout,
            )

        res = await self.execute_with_reconnect(
            grpc_call=grpc_call,
            error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline,
            cancellation_event=cancellation_event,
        )
        return res.data

    # endregion

    # ══════════════════════════════════════════════════════════════════════════
    # region STREAMING METHODS
    # ══════════════════════════════════════════════════════════════════════════

    async def on_symbol_tick(
        self,
        symbols: list[str],
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to real-time tick data for specified symbols.

        Args:
            symbols (list[str]): The symbol names to subscribe to.
            cancellation_event (asyncio.Event, optional): Event to cancel streaming.

        Yields:
            OnSymbolTickData: Async stream of tick data responses.

        Raises:
            ConnectExceptionMT5: If the account is not connected before calling this method.
            ApiExceptionMT5: If the server returns an error in the stream.
            grpc.aio.AioRpcError: If the stream fails due to communication or protocol errors.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = subscriptions_pb2.OnSymbolTickRequest()
        request.symbol_names.extend(symbols)

        async for data in self.execute_stream_with_reconnect(
            request=request,
            stream_invoker=lambda req, headers: self.subscription_client.OnSymbolTick(req, metadata=headers),
            get_error=lambda reply: reply.error,
            get_data=lambda reply: reply.data,
            cancellation_event=cancellation_event,
        ):
            yield data

    async def on_trade(
        self,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to all trade-related events: orders, deals, positions.

        Args:
            cancellation_event (asyncio.Event, optional): Event to cancel streaming.

        Yields:
            OnTradeData: Trade event data.

        Raises:
            ConnectExceptionMT5: If the account is not connected.
            ApiExceptionMT5: If the server returns a known API error.
            grpc.aio.AioRpcError: If the stream fails due to communication or protocol errors.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = subscriptions_pb2.OnTradeRequest()

        async for data in self.execute_stream_with_reconnect(
            request=request,
            stream_invoker=lambda req, headers: self.subscription_client.OnTrade(req, metadata=headers),
            get_error=lambda reply: reply.error,
            get_data=lambda reply: reply.data,
            cancellation_event=cancellation_event,
        ):
            yield data

    async def on_position_profit(
        self,
        interval_ms: int,
        ignore_empty: bool = True,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to real-time profit updates for open positions.

        Args:
            interval_ms (int): Interval in milliseconds to poll the server.
            ignore_empty (bool, optional): Skip frames with no change.
            cancellation_event (asyncio.Event, optional): Event to cancel streaming.

        Yields:
            OnPositionProfitData: Profit update data.

        Raises:
            ConnectExceptionMT5: If the account is not connected.
            ApiExceptionMT5: If the server returns a known API error.
            grpc.aio.AioRpcError: If the stream fails due to communication or protocol errors.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = subscriptions_pb2.OnPositionProfitRequest(
            timer_period_milliseconds=interval_ms,
            ignore_empty_data=ignore_empty,
        )

        async for data in self.execute_stream_with_reconnect(
            request=request,
            stream_invoker=lambda req, headers: self.subscription_client.OnPositionProfit(req, metadata=headers),
            get_error=lambda reply: reply.error,
            get_data=lambda reply: reply.data,
            cancellation_event=cancellation_event,
        ):
            yield data

    async def on_positions_and_pending_orders_tickets(
        self,
        interval_ms: int,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to updates of position and pending order ticket IDs.

        Args:
            interval_ms (int): Polling interval in milliseconds.
            cancellation_event (asyncio.Event, optional): Event to cancel streaming.

        Yields:
            OnPositionsAndPendingOrdersTicketsData: Snapshot of tickets.

        Raises:
            ConnectExceptionMT5: If the account is not connected.
            ApiExceptionMT5: If the server returns a known API error.
            grpc.aio.AioRpcError: If the stream fails due to communication or protocol errors.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = subscriptions_pb2.OnPositionsAndPendingOrdersTicketsRequest(
            timer_period_milliseconds=interval_ms,
        )

        async for data in self.execute_stream_with_reconnect(
            request=request,
            stream_invoker=lambda req, headers: self.subscription_client.OnPositionsAndPendingOrdersTickets(req, metadata=headers),
            get_error=lambda reply: reply.error,
            get_data=lambda reply: reply.data,
            cancellation_event=cancellation_event,
        ):
            yield data

    async def on_trade_transaction(
        self,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to real-time trade transaction events such as order creation, update, or execution.

        Args:
            cancellation_event (asyncio.Event, optional): Event to cancel streaming.

        Yields:
            OnTradeTransactionData: Trade transaction replies.

        Raises:
            ConnectExceptionMT5: If the account is not connected.
            ApiExceptionMT5: If the server returns a known API error.
            grpc.aio.AioRpcError: If the stream fails due to communication or protocol errors.
        """
        if not self.id:
            raise ConnectExceptionMT5("Please call connect method first")

        request = subscriptions_pb2.OnTradeTransactionRequest()

        async for data in self.execute_stream_with_reconnect(
            request=request,
            stream_invoker=lambda req, headers: self.subscription_client.OnTradeTransaction(req, metadata=headers),
            get_error=lambda reply: reply.error,
            get_data=lambda reply: reply.data,
            cancellation_event=cancellation_event,
        ):
            yield data

    # endregion
