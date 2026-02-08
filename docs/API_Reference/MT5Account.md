# 🎯 MT5Account API Reference

!!! info "Documentation Status"
    **Auto-generated from source code** (`package/MetaRpcMT5/helpers/mt5_account.py`) and enhanced for readability.
    Complete API reference with enhanced navigation. Single-page format for easy browsing.

---

## 📌 Overview

MT5Account represents a low-level async Python client for MetaTrader 5 terminal via gRPC protocol. API methods accept typed parameters and return either protobuf Data objects or native Python types (float, int, str). This is the foundation layer that directly communicates with the MT5 gRPC server, providing automatic reconnection, error handling, and streaming capabilities.

!!! success "Key Features"
    - ✅ Async/await API for most operations (42 async methods + 4 sync constructors/utilities)
    - ✅ Automatic reconnection on transient errors (UNAVAILABLE, TERMINAL_INSTANCE_NOT_FOUND)
    - ✅ Built-in error handling and retry logic via execute_with_reconnect wrappers
    - ✅ Streaming support for real-time data (5 async generators: ticks, trades, positions, profit, transactions)
    - ✅ Complete trading operations (market/pending orders, modifications, closures)
    - ✅ Comprehensive account, symbol, and position information retrieval (40+ methods)

!!! tip "Detailed Guides Available"
    For in-depth understanding of each method group with examples and best practices, see:

    - 📖 [MT5Account Master Overview](../MT5Account/MT5Account.Master.Overview.md) - Complete low-level API guide
    - 👤 [Account Information](../MT5Account/1.%20Account_Information/Account_Information.Overview.md) - Balance, equity, margin methods
    - 📊 [Symbol Information](../MT5Account/2.%20Symbol_Information/Symbol_Information.Overview.md) - Symbol properties, ticks, sessions
    - 📈 [Positions & Orders](../MT5Account/3.%20Positions_Orders/Positions_Orders.Overview.md) - Position/order snapshots and history
    - 📖 [Market Depth](../MT5Account/4.%20Market_Depth/Market_Depth.Overview.md) - Level II quotes (DOM)
    - 💰 [Trading Operations](../MT5Account/5.%20Trading_Operations/Trading_Operations.Overview.md) - Order execution and validation
    - 📡 [Streaming Methods](../MT5Account/6.%20Streaming_Methods/Streaming_Methods.Overview.md) - Real-time data streams

---

## 📑 Table of Contents

### 🔧 Initialization
- [__init__](#__init__) — Initialize MT5Account instance
- [create](#create) — Factory method with UUID generation

### 🔌 Connection
- [connect_by_server_name](#connect_by_server_name) — Connect using MT5 server name
- [connect_by_host_port](#connect_by_host_port) — Connect using host:port

### 👤 Account Info
- [account_summary](#account_summary) — Full account information
- [account_info_double](#account_info_double) — Account float property
- [account_info_integer](#account_info_integer) — Account integer property
- [account_info_string](#account_info_string) — Account string property

### 📊 Symbol Info
- [symbols_total](#symbols_total) — Total symbols count
- [symbol_exist](#symbol_exist) — Check symbol existence
- [symbol_name](#symbol_name) — Get symbol name by index
- [symbol_select](#symbol_select) — Select/deselect symbol
- [symbol_is_synchronized](#symbol_is_synchronized) — Check symbol sync status
- [symbol_info_double](#symbol_info_double) — Symbol float property
- [symbol_info_integer](#symbol_info_integer) — Symbol integer property
- [symbol_info_string](#symbol_info_string) — Symbol string property
- [symbol_info_margin_rate](#symbol_info_margin_rate) — Margin rate for order type
- [symbol_info_tick](#symbol_info_tick) — Latest tick data
- [symbol_info_session_quote](#symbol_info_session_quote) — Quote session times
- [symbol_info_session_trade](#symbol_info_session_trade) — Trade session times
- [symbol_params_many](#symbol_params_many) — Batch symbol parameters

### 📈 Positions & Orders
- [positions_total](#positions_total) — Total open positions count
- [opened_orders](#opened_orders) — All opened orders and positions
- [opened_orders_tickets](#opened_orders_tickets) — Tickets snapshot
- [order_history](#order_history) — Historical orders
- [positions_history](#positions_history) — Historical positions
- [tick_value_with_size](#tick_value_with_size) — Tick value calculations

### 📖 Market Depth
- [market_book_add](#market_book_add) — Subscribe to DOM
- [market_book_get](#market_book_get) — Get current DOM
- [market_book_release](#market_book_release) — Unsubscribe from DOM

### 💰 Trading
- [order_send](#order_send) — Send trading order
- [order_modify](#order_modify) — Modify existing order
- [order_close](#order_close) — Close position
- [order_check](#order_check) — Check order validity
- [order_calc_margin](#order_calc_margin) — Calculate required margin
- [order_calc_profit](#order_calc_profit) — Calculate profit/loss

### 📡 Streaming
- [on_symbol_tick](#on_symbol_tick) — Real-time tick stream
- [on_trade](#on_trade) — Trade event stream
- [on_position_profit](#on_position_profit) — Position profit updates
- [on_positions_and_pending_orders_tickets](#on_positions_and_pending_orders_tickets) — Tickets stream
- [on_trade_transaction](#on_trade_transaction) — Transaction event stream

### 🔧 Internal
- [get_headers](#get_headers) — Get gRPC headers
- [reconnect](#reconnect) — Reconnect to MT5
- [execute_with_reconnect](#execute_with_reconnect) — Execute with auto-reconnect
- [execute_stream_with_reconnect](#execute_stream_with_reconnect) — Stream with auto-reconnect

---

## 🏗️ Class: MT5Account

*Source: Line 122*

Low-level gRPC client for MetaTrader 5 terminal operations.

MT5Account provides direct protobuf-based interface to MT5 terminal operations including account management, symbol queries, position tracking, market depth, trading operations, and real-time streaming. Most methods use async/await patterns and include automatic reconnection on transient errors.

!!! tip "Recommended Usage"
    1. Use `MT5Account.create()` to create instance with auto-generated UUID
    2. Connect using `connect_by_server_name()` (recommended) or `connect_by_host_port()`
    3. Call async methods to interact with MT5
    4. Close connection with `await account.channel.close()`

!!! note "Constructor Requirements"
    - Requires MT5 credentials (user, password) and gRPC server address
    - Optional terminal instance UUID (if None, must use factory method `create()`)
    - Establishes secure gRPC channel with TLS, keepalive, and 100MB message limits

---

## 🔧 Initialization & Factory Methods

### __init__

**Signature:** `def __init__(self, user, password, grpc_server, id_)`

*Source: Line 123*

Initialize MT5Account with gRPC connection.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `user` | int | MT5 account login |
| `password` | str | MT5 account password |
| `grpc_server` | str | gRPC server address (default: "mt5.mrpc.pro:443") |
| `id_` | UUID | Terminal instance UUID (auto-generated if not provided) |

---

### create

**Signature:** `def create(cls, user, password, grpc_server, id_) -> MT5Account`

*Source: Line 200*

Create MT5Account instance with explicit UUID.

Factory method that creates a new MT5Account with gRPC connection.
The connection is established with TLS, keepalive, and automatic reconnect configured.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `user` | int | MT5 account login number |
| `password` | str | MT5 account password |
| `grpc_server` | str | gRPC server address (default: "mt5.mrpc.pro:443" if empty) |
| `id_` | UUID | Terminal instance UUID (optional, will be generated if not provided) |

**Returns:** `MT5Account` - Initialized account instance (not yet connected to MT5 server)

!!! example "Usage Example"
    ```python
    from uuid import uuid4
    account = MT5Account.create(
        user=12345678,
        password="mypassword",
        grpc_server="mt5.mrpc.pro:443",
        id_=uuid4()
    )
    await account.connect_by_server_name("MetaQuotes-Demo", "EURUSD")
    ```

---

## 🔌 Connection Methods

### connect_by_server_name

**Signature:** `async def connect_by_server_name(self, server_name, base_chart_symbol, wait_for_terminal_is_alive, timeout_seconds, deadline)`

*Source: Line 463*

!!! success "Recommended Method"
    This is the **RECOMMENDED** connection method - simpler than connect_by_host_port.
    Used in all demonstration examples via create_and_connect_mt5() helper.

Connects to MT5 server by broker server name (cluster name).

The method establishes connection to MT5 terminal, waits for terminal readiness,
and updates the instance GUID (self.id) from server response.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `server_name` | str | - | MT5 broker server/cluster name (e.g., "MetaQuotes-Demo") |
| `base_chart_symbol` | str | "EURUSD" | Base symbol for chart initialization |
| `wait_for_terminal_is_alive` | bool | True | Wait for terminal readiness before returning |
| `timeout_seconds` | int | 30 | Timeout in seconds for terminal readiness waiting |
| `deadline` | datetime | None | Deadline for gRPC call completion |

**Raises:**

- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails due to communication errors

!!! example "Usage Example"
    ```python
    account = MT5Account(user=12345, password="pass", grpc_server="localhost:9999")
    await account.connect_by_server_name("MetaQuotes-Demo", "EURUSD")
    print(f"Connected! Terminal GUID: {account.id}")
    ```

---

### connect_by_host_port

**Signature:** `async def connect_by_host_port(self, host, port, base_chart_symbol, wait_for_terminal_is_alive, timeout_seconds, deadline)`

*Source: Line 394*

Connects to MT5 server by IP address or hostname and port.

Alternative connection method when you know the exact server address.
For most cases, use connect_by_server_name() instead (simpler and recommended).

The method establishes connection to MT5 terminal, waits for terminal readiness,
and updates the instance GUID (self.id) from server response.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | str | - | Server IP address or hostname (e.g., "mt5.broker.com") |
| `port` | int | 443 | Server port number |
| `base_chart_symbol` | str | "EURUSD" | Base symbol for chart initialization |
| `wait_for_terminal_is_alive` | bool | True | Wait for terminal readiness before returning |
| `timeout_seconds` | int | 30 | Timeout in seconds for terminal readiness waiting |
| `deadline` | datetime | None | Deadline for gRPC call completion |

**Raises:**

- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails due to communication errors

!!! example "Usage Example"
    ```python
    account = MT5Account(user=12345, password="pass", grpc_server="localhost:9999")
    await account.connect_by_host_port("mt5.broker.com", 443, "EURUSD")
    print(f"Connected! Terminal GUID: {account.id}")
    ```

---

## 👤 Account Information Methods

### account_summary

**Signature:** `async def account_summary(self, deadline, cancellation_event)`

*Source: Line 532*

Gets the summary information for a trading account asynchronously.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deadline` | datetime | Deadline after which the request will be canceled if not completed |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `AccountSummaryData` - The server's response containing account summary data

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected before calling this method
- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails due to communication or protocol errors

---

### account_info_double

**Signature:** `async def account_info_double(self, property_id, deadline, cancellation_event) -> float`

*Source: Line 579*

Retrieves a double-precision account property (e.g. balance, equity, margin).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `property_id` | AccountInfoDoublePropertyType | The account double property to retrieve |
| `deadline` | datetime | Deadline after which the call will be cancelled |
| `cancellation_event` | asyncio.Event | Event to cancel the operation |

**Returns:** `float` - The double value of the requested account property

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### account_info_integer

**Signature:** `async def account_info_integer(self, property_id, deadline, cancellation_event) -> int`

*Source: Line 622*

Retrieves an integer account property (e.g. login, leverage, trade mode).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `property_id` | AccountInfoIntegerPropertyType | The account integer property to retrieve |
| `deadline` | datetime | Deadline after which the call will be cancelled |
| `cancellation_event` | asyncio.Event | Event to cancel the operation |

**Returns:** `int` - The integer value of the requested account property

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### account_info_string

**Signature:** `async def account_info_string(self, property_id, deadline, cancellation_event) -> str`

*Source: Line 665*

Retrieves a string account property (e.g. account name, currency, server).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `property_id` | AccountInfoStringPropertyType | The account string property to retrieve |
| `deadline` | datetime | Deadline after which the call will be cancelled |
| `cancellation_event` | asyncio.Event | Event to cancel the operation |

**Returns:** `str` - The string value of the requested account property

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

## 📊 Symbol Information Methods

### symbols_total

**Signature:** `async def symbols_total(self, selected_only, deadline, cancellation_event)`

*Source: Line 714*

Returns the total number of symbols available on the platform.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `selected_only` | bool | True to count only Market Watch symbols, false to count all |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolsTotalData` - Total symbol count data

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### symbol_exist

**Signature:** `async def symbol_exist(self, symbol, deadline, cancellation_event)`

*Source: Line 757*

Checks if a symbol with the specified name exists (standard or custom).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | The symbol name to check |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolExistData` - Information about symbol existence and type

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### symbol_name

**Signature:** `async def symbol_name(self, index, selected, deadline, cancellation_event)`

*Source: Line 800*

Returns the name of a symbol by index.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `index` | int | Symbol index (starting at 0) |
| `selected` | bool | True to use only Market Watch symbols |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolNameData` - The symbol name at the specified index

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### symbol_select

**Signature:** `async def symbol_select(self, symbol, select, deadline, cancellation_event)`

*Source: Line 845*

Adds or removes a symbol from Market Watch.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `select` | bool | True to add, false to remove |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolSelectData` - Success status of the operation

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### symbol_is_synchronized

**Signature:** `async def symbol_is_synchronized(self, symbol, deadline, cancellation_event)`

*Source: Line 890*

Checks if the symbol's data is synchronized with the server.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name to check |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolIsSynchronizedData` - True if synchronized, false otherwise

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### symbol_info_double

**Signature:** `async def symbol_info_double(self, symbol, property, deadline, cancellation_event)`

*Source: Line 933*

Retrieves a double-precision property value of a symbol.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `property` | SymbolInfoDoubleProperty | The double-type property to retrieve |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolInfoDoubleData` - The double property value

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### symbol_info_integer

**Signature:** `async def symbol_info_integer(self, symbol, property, deadline, cancellation_event)`

*Source: Line 978*

Retrieves an integer-type property value of a symbol.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `property` | SymbolInfoIntegerProperty | The integer property to query |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolInfoIntegerData` - The integer property value

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### symbol_info_string

**Signature:** `async def symbol_info_string(self, symbol, property, deadline, cancellation_event)`

*Source: Line 1023*

Retrieves a string-type property value of a symbol.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `property` | SymbolInfoStringProperty | The string property to retrieve |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolInfoStringData` - The string property value

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### symbol_info_margin_rate

**Signature:** `async def symbol_info_margin_rate(self, symbol, order_type, deadline, cancellation_event)`

*Source: Line 1068*

Retrieves the margin rates for a given symbol and order type.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `order_type` | ENUM_ORDER_TYPE | The order type (buy/sell/etc) |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolInfoMarginRateData` - The initial and maintenance margin rates

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### symbol_info_tick

**Signature:** `async def symbol_info_tick(self, symbol, deadline, cancellation_event)`

*Source: Line 1113*

Retrieves the current tick data (bid, ask, last, volume) for a given symbol.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name to fetch tick info for |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `MrpcMqlTick` - The latest tick information

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected
- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### symbol_info_session_quote

**Signature:** `async def symbol_info_session_quote(self, symbol, day_of_week, session_index, deadline, cancellation_event)`

*Source: Line 1156*

Gets the quoting session start and end time for a symbol on a specific day and session index.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | The symbol name |
| `day_of_week` | DayOfWeek | The day of the week |
| `session_index` | int | Index of the quoting session (starting at 0) |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolInfoSessionQuoteData` - The session quote start and end time

---

### symbol_info_session_trade

**Signature:** `async def symbol_info_session_trade(self, symbol, day_of_week, session_index, deadline, cancellation_event)`

*Source: Line 1202*

Gets the trading session start and end time for a symbol on a specific day and session index.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | The symbol name |
| `day_of_week` | DayOfWeek | The day of the week |
| `session_index` | int | Index of the trading session (starting at 0) |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolInfoSessionTradeData` - The trading session start and end time

---

### symbol_params_many

**Signature:** `async def symbol_params_many(self, request, deadline, cancellation_event)`

*Source: Line 1248*

Retrieves symbol parameters for multiple instruments asynchronously.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | SymbolParamsManyRequest | The request containing filters and pagination |
| `deadline` | datetime | Deadline after which the request will be canceled |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `SymbolParamsManyData` - Symbol parameter details

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected before calling this method
- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails due to communication or protocol errors

---

## 📈 Positions & Orders Methods

### positions_total

**Signature:** `async def positions_total(self, deadline, cancellation_event)`

*Source: Line 1299*

Returns the total number of open positions on the current account.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `PositionsTotalData` - The total number of open positions

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If gRPC fails to connect or respond

---

### opened_orders

**Signature:** `async def opened_orders(self, sort_mode, deadline, cancellation_event)`

*Source: Line 1343*

Gets the currently opened orders and positions for the connected account asynchronously.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `sort_mode` | BMT5_ENUM_OPENED_ORDER_SORT_TYPE | The sort mode for the opened orders (0 - open time, 1 - close time, 2 - ticket ID) |
| `deadline` | datetime | Deadline after which the request will be canceled if not completed |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `OpenedOrdersData` - The result containing opened orders and positions

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected before calling this method
- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails due to communication or protocol errors

---

### opened_orders_tickets

**Signature:** `async def opened_orders_tickets(self, deadline, cancellation_event)`

*Source: Line 1392*

Gets ticket IDs of all currently opened orders and positions asynchronously.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deadline` | datetime | Deadline after which the request will be canceled |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `OpenedOrdersTicketsData` - Collection of opened order and position tickets

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected before calling this method
- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails due to communication or protocol errors

---

### order_history

**Signature:** `async def order_history(self, from_dt, to_dt, sort_mode, page_number, items_per_page, deadline, cancellation_event)`

*Source: Line 1437*

Gets the historical orders for the connected trading account within the specified
time range asynchronously.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `from_dt` | datetime | The start time for the history query (server time) |
| `to_dt` | datetime | The end time for the history query (server time) |
| `sort_mode` | BMT5_ENUM_ORDER_HISTORY_SORT_TYPE | The sort mode (0 - by open time, 1 - by close time, 2 - by ticket ID) |
| `page_number` | int | Page number for paginated results (default 0) |
| `items_per_page` | int | Number of items per page (default 0 = all) |
| `deadline` | datetime | Deadline after which the request will be canceled |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `OrdersHistoryData` - The server's response containing paged historical order data

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected before calling this method
- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails due to communication or protocol errors

---

### positions_history

**Signature:** `async def positions_history(self, sort_type, open_from, open_to, page, size, deadline, cancellation_event)`

*Source: Line 1502*

Retrieves historical positions based on filter and time range asynchronously.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `sort_type` | AH_ENUM_POSITIONS_HISTORY_SORT_TYPE | Sorting type for historical positions |
| `open_from` | datetime | Start of open time filter (UTC) |
| `open_to` | datetime | End of open time filter (UTC) |
| `page` | int | Page number for paginated results (default 0) |
| `size` | int | Number of items per page (default 0 = all) |
| `deadline` | datetime | Deadline after which the request will be canceled |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `PositionsHistoryData` - Historical position records

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected before calling this method
- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails due to communication or protocol errors

---

### tick_value_with_size

**Signature:** `async def tick_value_with_size(self, symbols, deadline, cancellation_event)`

*Source: Line 1566*

Gets tick value and tick size data for the given symbols asynchronously.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbols` | list[str] | List of symbol names |
| `deadline` | datetime | Deadline after which the request will be canceled |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `TickValueWithSizeData` - Tick value and contract size info per symbol

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected before calling this method
- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails due to communication or protocol errors

---

## 📖 Market Depth (DOM) Methods

### market_book_add

**Signature:** `async def market_book_add(self, symbol, deadline, cancellation_event)`

*Source: Line 1620*

Opens the Depth of Market (DOM) for a symbol and subscribes to updates.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name to subscribe |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `MarketBookAddData` - True if DOM subscription was successful

---

### market_book_release

**Signature:** `async def market_book_release(self, symbol, deadline, cancellation_event)`

*Source: Line 1658*

Releases the Depth of Market (DOM) for a symbol and stops receiving updates.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name to unsubscribe |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `MarketBookReleaseData` - True if DOM release was successful

---

### market_book_get

**Signature:** `async def market_book_get(self, symbol, deadline, cancellation_event)`

*Source: Line 1696*

Gets the current Depth of Market (DOM) data for a symbol.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `MarketBookGetData` - A list of book entries for the symbol's DOM

---

## 💰 Trading Operations Methods

### order_send

**Signature:** `async def order_send(self, request, deadline, cancellation_event) -> trading_helper_pb2.OrderSendData`

*Source: Line 1740*

Sends a market or pending order to the trading server asynchronously.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderSendRequest | The order request to send |
| `deadline` | datetime | Deadline for the operation |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `OrderSendData` - Response with deal/order confirmation data

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected
- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### order_modify

**Signature:** `async def order_modify(self, request, deadline, cancellation_event)`

*Source: Line 1785*

Modifies an existing order or position asynchronously.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderModifyRequest | The modification request (SL, TP, price, expiration, etc.) |
| `deadline` | datetime | Deadline for the operation |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `OrderModifyData` - Response containing updated order/deal info

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected
- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### order_close

**Signature:** `async def order_close(self, request, deadline, cancellation_event)`

*Source: Line 1830*

Closes a market or pending order asynchronously.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderCloseRequest | The close request including ticket, volume, and slippage |
| `deadline` | datetime | Deadline for the operation |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `OrderCloseData` - The close result and return codes

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected
- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails

---

### order_check

**Signature:** `async def order_check(self, request, deadline, cancellation_event)`

*Source: Line 1875*

Checks whether a trade request can be successfully executed under current market conditions.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderCheckRequest | The trade request to validate |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `OrderCheckData` - Result of the trade request check, including margin and balance details

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If gRPC fails to connect or respond

---

### order_calc_margin

**Signature:** `async def order_calc_margin(self, request, deadline, cancellation_event)`

*Source: Line 1919*

Calculates the margin required for a planned trade operation.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderCalcMarginRequest | The request containing symbol, order type, volume, and price |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `OrderCalcMarginData` - The required margin in account currency

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If gRPC fails to connect or respond

---

### order_calc_profit

**Signature:** `async def order_calc_profit(self, request, deadline, cancellation_event)`

*Source: Line 1963*

Calculates potential profit/loss for a planned trade operation.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderCalcProfitRequest | The request containing symbol, order type, volume, open price, and close price |
| `deadline` | datetime | Deadline for the gRPC call |
| `cancellation_event` | asyncio.Event | Event to cancel the request |

**Returns:** `OrderCalcProfitData` - The potential profit/loss in account currency

**Raises:**

- `ConnectExceptionMT5` - If the client is not connected
- `ApiExceptionMT5` - If the server returns a business error
- `grpc.aio.AioRpcError` - If gRPC fails to connect or respond

---

## 📡 Streaming Methods

### on_symbol_tick

**Signature:** `async def on_symbol_tick(self, symbols, cancellation_event)`

*Source: Line 2013*

Subscribes to real-time tick data for specified symbols.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbols` | list[str] | The symbol names to subscribe to |
| `cancellation_event` | asyncio.Event | Event to cancel streaming |

**Yields:** `OnSymbolTickData` - Async stream of tick data responses

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected before calling this method
- `ApiExceptionMT5` - If the server returns an error in the stream
- `grpc.aio.AioRpcError` - If the stream fails due to communication or protocol errors

---

### on_trade

**Signature:** `async def on_trade(self, cancellation_event)`

*Source: Line 2048*

Subscribes to all trade-related events: orders, deals, positions.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cancellation_event` | asyncio.Event | Event to cancel streaming |

**Yields:** `OnTradeData` - Trade event data

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected
- `ApiExceptionMT5` - If the server returns a known API error
- `grpc.aio.AioRpcError` - If the stream fails due to communication or protocol errors

---

### on_position_profit

**Signature:** `async def on_position_profit(self, interval_ms, ignore_empty, cancellation_event)`

*Source: Line 2080*

Subscribes to real-time profit updates for open positions.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `interval_ms` | int | Interval in milliseconds to poll the server |
| `ignore_empty` | bool | Skip frames with no change |
| `cancellation_event` | asyncio.Event | Event to cancel streaming |

**Yields:** `OnPositionProfitData` - Profit update data

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected
- `ApiExceptionMT5` - If the server returns a known API error
- `grpc.aio.AioRpcError` - If the stream fails due to communication or protocol errors

---

### on_positions_and_pending_orders_tickets

**Signature:** `async def on_positions_and_pending_orders_tickets(self, interval_ms, cancellation_event)`

*Source: Line 2119*

Subscribes to updates of position and pending order ticket IDs.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `interval_ms` | int | Polling interval in milliseconds |
| `cancellation_event` | asyncio.Event | Event to cancel streaming |

**Yields:** `OnPositionsAndPendingOrdersTicketsData` - Snapshot of tickets

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected
- `ApiExceptionMT5` - If the server returns a known API error
- `grpc.aio.AioRpcError` - If the stream fails due to communication or protocol errors

---

### on_trade_transaction

**Signature:** `async def on_trade_transaction(self, cancellation_event)`

*Source: Line 2155*

Subscribes to real-time trade transaction events such as order creation, update, or execution.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cancellation_event` | asyncio.Event | Event to cancel streaming |

**Yields:** `OnTradeTransactionData` - Trade transaction replies

**Raises:**

- `ConnectExceptionMT5` - If the account is not connected
- `ApiExceptionMT5` - If the server returns a known API error
- `grpc.aio.AioRpcError` - If the stream fails due to communication or protocol errors

---

## 🔧 Internal/Low-level Methods

!!! warning "Internal Methods"
    These methods are used internally by the MT5Account class. Regular users don't need to call them directly.
    All public API methods already include proper usage of these internal helpers.

### get_headers

**Signature:** `def get_headers(self)`

*Source: Line 277*

Returns gRPC metadata headers for API requests.

Internal helper method that constructs gRPC metadata headers containing
the terminal instance UUID. Used automatically by execute_with_reconnect
and execute_stream_with_reconnect wrappers.

**Returns:** `list[tuple[str, str]]` - List of metadata tuples containing ("id", terminal_uuid)

!!! note
    This is an internal method. Regular users don't need to call it directly.
    All public API methods already include proper headers automatically.

---

### reconnect

**Signature:** `async def reconnect(self, deadline)`

*Source: Line 280*

Reconnects to MT5 terminal using previously saved connection parameters.

Internal method that re-establishes connection to MT5 terminal using the
connection parameters from the last successful connect_by_server_name() or
connect_by_host_port() call. Automatically called by execute_with_reconnect
wrappers on transient connection errors.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `deadline` | datetime | Deadline for gRPC call completion |

**Raises:**

- `ApiExceptionMT5` - If the server returns an error in the response
- `grpc.aio.AioRpcError` - If the gRPC call fails due to communication errors

!!! note
    This is an internal method used by automatic reconnection logic.
    Regular users don't need to call it manually - reconnection happens
    automatically when needed.

---

### execute_with_reconnect

**Signature:** `async def execute_with_reconnect(self, grpc_call, error_selector, deadline, cancellation_event)`

*Source: Line 289*

Executes a gRPC unary call with automatic reconnection on transient errors.

Internal wrapper method that executes a gRPC unary (request-response) call
with built-in resilience against transient network errors and terminal restarts.
Automatically reconnects on UNAVAILABLE errors and TERMINAL_INSTANCE_NOT_FOUND errors,
then retries the operation.

All public API methods (account_info_double, symbol_info_tick, order_send, etc.)
use this wrapper internally to provide automatic reconnection.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `grpc_call` | Callable | A function that performs the gRPC call. Takes headers as parameter and returns the response |
| `error_selector` | Callable | A function that extracts error object from response. Return object with .error_code to check for reconnection-triggering errors |
| `deadline` | datetime | Deadline for gRPC call completion |
| `cancellation_event` | asyncio.Event | Event to cancel the operation |

**Returns:** `Any` - The response from the successful gRPC call

**Raises:**

- `ConnectExceptionMT5` - If reconnection fails due to missing connection context
- `ApiExceptionMT5` - If the server returns a business logic error
- `grpc.aio.AioRpcError` - If a non-recoverable gRPC error occurs
- `asyncio.CancelledError` - If operation was cancelled via cancellation_event

!!! note
    This is an internal method. Regular users don't need to call it directly.
    It's used as a wrapper by all public API methods for automatic resilience.

---

### execute_stream_with_reconnect

**Signature:** `async def execute_stream_with_reconnect(self, request, stream_invoker, get_error, get_data, cancellation_event)`

*Source: Line 320*

Executes a gRPC server-streaming call with automatic reconnection logic on recoverable errors.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | - | The request object to initiate the stream with |
| `stream_invoker` | Callable | A function that opens the stream. It receives the request and metadata headers, and returns an async streaming call |
| `get_error` | Callable | A function that extracts the error object (if any) from a reply. Return an object with .error_code == "TERMINAL_INSTANCE_NOT_FOUND" to trigger reconnect, or any non-null error to raise ApiExceptionMT5 |
| `get_data` | Callable | A function that extracts the data object from a reply. If it returns None, the message is skipped |
| `cancellation_event` | asyncio.Event | Event to cancel streaming and reconnection attempts |

**Yields:** Extracted data items streamed from the server

**Raises:**

- `ConnectExceptionMT5` - If reconnection logic fails due to missing account context
- `ApiExceptionMT5` - When the stream response contains a known API error
- `grpc.aio.AioRpcError` - If a non-recoverable gRPC error occurs

---
