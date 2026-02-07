# 🎯 MT5Service API Reference

!!! info "Documentation Status"
    **Auto-generated from source code** (`src/pymt5/mt5_service.py`) and enhanced for readability.
    Complete API reference with enhanced navigation. Single-page format for easy browsing.

---

## 📌 Overview

MT5Service represents a mid-level Python wrapper over MT5Account (low-level gRPC client). It provides clean Python API with native types (float, int, str, datetime) instead of protobuf structures, automatically unpacks .data wrappers, converts timestamps, and reduces boilerplate code by 30-70% for common operations.

!!! success "Key Features"
    - ✅ Native Python types instead of protobuf (float, int, str, datetime)
    - ✅ Automatic .data wrapper extraction (no manual `.data.requested_value` access)
    - ✅ Timestamp datetime conversion for all time fields
    - ✅ 36 methods covering all MT5 operations (account, symbols, trading, streaming)
    - ✅ Cleaner API with dataclasses (AccountSummary, SymbolTick, OrderResult, etc.)
    - ✅ Built on top of MT5Account with automatic reconnection and error handling

---

## ⚠️ Important: Understanding MT5Service Role

!!! warning "This is a Middleware Layer - Not for Most Users"
    **MT5Service exists primarily for MT5Sugar's architectural needs.**

    - 🎯 **For most users**: Use [MT5Sugar](./MT5Sugar.md) instead (high-level, ready patterns)
    - 🔧 **For advanced users**: This layer is useful when you need specific mid-level operations
    - 📦 **Architectural purpose**: Bridges protobuf (MT5Account) and business logic (MT5Sugar)

!!! info "Value Reality Check"
    **Not all 36 methods add equal value:**

    - ✅ **HIGH value** (8 methods): Complex protobuf unpacking + dataclass conversion
        - Worth using directly: `get_account_summary()`, `get_symbol_params_many()`, `check_order()`, `place_order()`, `modify_order()`, etc.

    - ⚪ **MEDIUM/LOW value** (10 methods): Simple field extraction
        - Consider using if convenient, or call MT5Account directly

    - ⚪ **NONE value** (18 methods!): Direct pass-through to MT5Account
        - Just proxy calls like `return await account.method()` or `yield data`
        - **For these, consider calling MT5Account directly** to avoid extra layer

!!! tip "Detailed Guides Available"
    For in-depth understanding of each method group, see:

    - 📖 [Complete MT5Service Overview](../MT5Service/MT5Service.Overview.md) - Value analysis of all 36 methods
    - 👤 [Account Information](../MT5Service/1.%20Account_Information.md) - 4 methods (1 HIGH, 3 NONE)
    - 📊 [Symbol Information](../MT5Service/2.%20Symbol_Information.md) - 13 methods (4 HIGH, 5 LOW, 4 NONE)
    - 📈 [Positions & Orders](../MT5Service/3.%20Positions_Orders.md) - 5 methods (1 MEDIUM, 1 LOW, 3 NONE)
    - 📖 [Market Depth](../MT5Service/4.%20Market_Depth.md) - 3 methods (1 HIGH, 2 MEDIUM)
    - 💰 [Trading Operations](../MT5Service/5.%20Trading_Operations.md) - 6 methods (3 HIGH, 3 LOW)
    - 📡 [Streaming Methods](../MT5Service/6.%20Streaming_Methods.md) - 5 methods (1 HIGH, 4 NONE)

---

## 📑 Table of Contents

### 👤 Account Information
- [get_account_summary](#get_account_summary) — Complete account data in one call
- [get_account_double](#get_account_double) — Account float property
- [get_account_integer](#get_account_integer) — Account integer property
- [get_account_string](#get_account_string) — Account string property

### 📊 Symbol Information
- [get_symbols_total](#get_symbols_total) — Total symbols count
- [symbol_exist](#symbol_exist) — Check symbol existence
- [get_symbol_name](#get_symbol_name) — Get symbol name by index
- [symbol_select](#symbol_select) — Add/remove symbol from Market Watch
- [is_symbol_synchronized](#is_symbol_synchronized) — Check symbol sync status
- [get_symbol_double](#get_symbol_double) — Symbol float property
- [get_symbol_integer](#get_symbol_integer) — Symbol integer property
- [get_symbol_string](#get_symbol_string) — Symbol string property
- [get_symbol_margin_rate](#get_symbol_margin_rate) — Margin rates for symbol
- [get_symbol_tick](#get_symbol_tick) — Current market prices
- [get_symbol_session_quote](#get_symbol_session_quote) — Quote session times
- [get_symbol_session_trade](#get_symbol_session_trade) — Trade session times
- [get_symbol_params_many](#get_symbol_params_many) — Batch symbol parameters

### 📈 Positions & Orders
- [get_positions_total](#get_positions_total) — Total open positions count
- [get_opened_orders](#get_opened_orders) — All opened orders and positions
- [get_opened_tickets](#get_opened_tickets) — Tickets snapshot (lightweight)
- [get_order_history](#get_order_history) — Historical orders
- [get_positions_history](#get_positions_history) — Closed positions with P&L

### 📖 Market Depth (DOM)
- [subscribe_market_depth](#subscribe_market_depth) — Subscribe to DOM updates
- [unsubscribe_market_depth](#unsubscribe_market_depth) — Unsubscribe from DOM
- [get_market_depth](#get_market_depth) — Current DOM snapshot

### 💰 Trading Operations
- [place_order](#place_order) — Send market/pending order
- [modify_order](#modify_order) — Modify order or position
- [close_order](#close_order) — Close position or delete order
- [check_order](#check_order) — Validate order before sending
- [calculate_margin](#calculate_margin) — Calculate required margin
- [calculate_profit](#calculate_profit) — Calculate potential profit

### 📡 Streaming Methods
- [stream_ticks](#stream_ticks) — Real-time tick data stream
- [stream_trade_updates](#stream_trade_updates) — Trade events stream
- [stream_position_profits](#stream_position_profits) — Position profit updates
- [stream_opened_tickets](#stream_opened_tickets) — Tickets stream (lightweight)
- [stream_transactions](#stream_transactions) — Transaction event stream

---

## 🏗️ Class: MT5Service

*Source: Line 222*

Mid-level wrapper over MT5Account providing clean Python API with native types.

MT5Service sits between the low-level MT5Account (protobuf gRPC client) and high-level business logic layers. It simplifies common operations by automatically unpacking protobuf wrappers, converting timestamps to datetime objects, and returning native Python types instead of protobuf structures. This reduces boilerplate code by 30-70% compared to using MT5Account directly.

!!! tip "Architecture Position"
    - **LOW** MT5Account (protobuf Request/Data, direct gRPC)
    - **MID** MT5Service (Python types, removes Data wrappers) **← THIS CLASS**
    - **HIGH** MT5Sugar (business logic, ready-made patterns)

!!! note "Constructor Requirements"
    - Requires MT5Account instance (already connected low-level client)
    - No direct connection logic - uses wrapped account's channel
    - Lightweight wrapper - minimal overhead over MT5Account

!!! tip "Usage Pattern"
    1. Create and connect MT5Account instance
    2. Wrap it with `service = MT5Service(account)`
    3. Call methods with cleaner API (returns native types)
    4. Close underlying account connection when done

!!! success "Key Advantages"
    - **Native types**: Returns `float`/`int`/`str`/`datetime` instead of protobuf wrappers
    - **Auto-unpacking**: No manual `.data.requested_value` extraction needed
    - **Time conversion**: Timestamps automatically converted to Python datetime
    - **Dataclasses**: Clean DTOs (AccountSummary, SymbolTick, OrderResult, etc.)
    - **Code reduction**: 30-70% less boilerplate for common operations

---

## 🔧 Methods

### __init__

**Signature:** `def __init__(self, account)`

*Source: Line 234*

Create MT5Service wrapper.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account` | MT5Account | Low-level gRPC client instance |

---

### get_account

**Signature:** `def get_account(self) -> MT5Account`

*Source: Line 243*

Return the underlying MT5Account for direct low-level access.

**Returns:** MT5Account instance for advanced operations

---

## 👤 Account Information Methods

### get_account_summary

**Signature:** `async def get_account_summary(self, deadline, cancellation_event) -> AccountSummary`

*Source: Line 254*

Get complete account information in ONE method call.

**Returns:** `AccountSummary` with all account data in native Python types (14 fields)

!!! note "Technical Details"
    Internally makes 5 RPC calls:

    1. `account_summary()` - gets 11 basic fields (login, balance, equity, username, etc.)
    2-5. `account_info_double()` × 4 - gets margin, free_margin, margin_level, profit

    Result: AccountSummary dataclass with 14 fields in native Python types.

!!! success "Advantage"
    **93% code reduction**: Single method call vs 14 separate `AccountInfo*` calls

---

### get_account_double

**Signature:** `async def get_account_double(self, property_id, deadline, cancellation_event) -> float`

*Source: Line 309*

Get individual account double property.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `property_id` | int | Property to retrieve (ACCOUNT_BALANCE, ACCOUNT_EQUITY, etc.) |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `float` value directly (no Data struct extraction)

!!! note "Technical Details"
    Low-level method returns `AccountInfoDoubleResponse` with `res.data.requested_value`.
    This wrapper auto-extracts the float, eliminating the `.data.requested_value` access.
    Supports automatic reconnection on gRPC errors via `execute_with_reconnect`.

---

### get_account_integer

**Signature:** `async def get_account_integer(self, property_id, deadline, cancellation_event) -> int`

*Source: Line 330*

Get individual account integer property.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `property_id` | int | Property to retrieve (ACCOUNT_LEVERAGE, ACCOUNT_LOGIN, etc.) |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `int` value directly (no Data struct extraction)

!!! note "Technical Details"
    Low-level returns `AccountInfoIntegerResponse` with `res.data.requested_value`.
    This wrapper auto-extracts the int. Used for properties like leverage (1:100), login number.

---

### get_account_string

**Signature:** `async def get_account_string(self, property_id, deadline, cancellation_event) -> str`

*Source: Line 350*

Get individual account string property.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `property_id` | int | Property to retrieve (ACCOUNT_CURRENCY, ACCOUNT_COMPANY, etc.) |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `str` value directly (no Data struct extraction)

!!! note "Technical Details"
    Low-level returns `AccountInfoStringResponse` with `res.data.requested_value`.
    This wrapper auto-extracts the string. Used for properties like currency ("USD"), company name.

---

## 📊 Symbol Information Methods

### get_symbols_total

**Signature:** `async def get_symbols_total(self, selected_only, deadline, cancellation_event) -> int`

*Source: Line 377*

Get count of available symbols.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `selected_only` | bool | True to count only Market Watch symbols, False for all |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `int` count directly (no Data struct)

!!! note "Technical Details"
    Low-level returns `SymbolsTotalData` with `data.total` wrapper.
    This auto-extracts the count. `selected_only=True` counts Market Watch, `False` counts all available symbols in terminal.

---

### symbol_exist

**Signature:** `async def symbol_exist(self, symbol, deadline, cancellation_event)`

*Source: Line 398*

Check if symbol exists in terminal.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name to check |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** Tuple of `(exists, is_custom)`

---

### get_symbol_name

**Signature:** `async def get_symbol_name(self, index, selected_only, deadline, cancellation_event) -> str`

*Source: Line 416*

Get symbol name by index position.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `index` | int | Symbol index (starting at 0) |
| `selected_only` | bool | True to use only Market Watch symbols |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** Symbol name string directly

---

### symbol_select

**Signature:** `async def symbol_select(self, symbol, select, deadline, cancellation_event) -> bool`

*Source: Line 436*

Add/remove symbol from Market Watch.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `select` | bool | True to add, False to remove |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** Success status directly

---

### is_symbol_synchronized

**Signature:** `async def is_symbol_synchronized(self, symbol, deadline, cancellation_event) -> bool`

*Source: Line 456*

Check if symbol data is synchronized.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name to check |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `True` if synchronized, `False` otherwise

---

### get_symbol_double

**Signature:** `async def get_symbol_double(self, symbol, property, deadline, cancellation_event) -> float`

*Source: Line 474*

Get individual symbol double property.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `property` | int | Property to retrieve (SYMBOL_BID, SYMBOL_ASK, etc.) |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `float` value directly

!!! note "Technical Details"
    Low-level returns `SymbolInfoDoubleResponse` with `data.value` wrapper.
    This extracts the float from nested structure. Common properties: SYMBOL_BID, SYMBOL_ASK, SYMBOL_POINT.

---

### get_symbol_integer

**Signature:** `async def get_symbol_integer(self, symbol, property, deadline, cancellation_event) -> int`

*Source: Line 497*

Get individual symbol integer property.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `property` | int | Property to retrieve (SYMBOL_DIGITS, SYMBOL_SPREAD, etc.) |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `int` value directly

---

### get_symbol_string

**Signature:** `async def get_symbol_string(self, symbol, property, deadline, cancellation_event) -> str`

*Source: Line 517*

Get individual symbol string property.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `property` | int | Property to retrieve (SYMBOL_DESCRIPTION, etc.) |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `str` value directly

---

### get_symbol_margin_rate

**Signature:** `async def get_symbol_margin_rate(self, symbol, order_type, deadline, cancellation_event) -> SymbolMarginRate`

*Source: Line 537*

Get margin rates for a symbol and order type.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `order_type` | int | Order type (BUY, SELL, etc.) |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `SymbolMarginRate` with initial and maintenance rates

---

### get_symbol_tick

**Signature:** `async def get_symbol_tick(self, symbol, deadline, cancellation_event) -> SymbolTick`

*Source: Line 560*

Get current market prices for a symbol.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `SymbolTick` with time already converted to datetime

!!! note "Technical Details"
    Low-level returns `SymbolInfoTickData` with Unix timestamp (`data.time`).
    This wrapper converts time field from Unix seconds to Python datetime via `fromtimestamp()`.
    Also provides `time_msc` (milliseconds) for sub-second precision and tick flags for tick type detection.

---

### get_symbol_session_quote

**Signature:** `async def get_symbol_session_quote(self, symbol, day_of_week, session_index, deadline, cancellation_event) -> SessionTime`

*Source: Line 594*

Get quote session times.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `day_of_week` | int | Day of the week |
| `session_index` | int | Session index (starting at 0) |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `SessionTime` with start/end times as datetime

!!! note "Technical Details"
    Low-level returns `SymbolInfoSessionQuoteData` with 'from' and 'to' Timestamp fields.
    This wrapper converts both protobuf Timestamps to Python datetimes via `ToDatetime()`.
    Shows when quotes (prices) are available for symbol on specified day. Most symbols have 1 session (0).

---

### get_symbol_session_trade

**Signature:** `async def get_symbol_session_trade(self, symbol, day_of_week, session_index, deadline, cancellation_event) -> SessionTime`

*Source: Line 628*

Get trading session times.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `day_of_week` | int | Day of the week |
| `session_index` | int | Session index (starting at 0) |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `SessionTime` with start/end times as datetime

---

### get_symbol_params_many

**Signature:** `async def get_symbol_params_many(self, name_filter, sort_mode, page_number, items_per_page, deadline, cancellation_event)`

*Source: Line 658*

Get parameters of multiple symbols at once.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name_filter` | str | Optional symbol name filter |
| `sort_mode` | int | Optional sort mode |
| `page_number` | int | Optional page number for pagination |
| `items_per_page` | int | Optional items per page |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** Tuple of `(list of SymbolParams, total count)`

!!! note "Technical Details"
    Low-level returns `SymbolParamsManyResponse` with `data.symbol_infos` (protobuf repeated field).
    This wrapper unpacks each `SymbolInfo` protobuf into `SymbolParams` dataclass with 17 fields.
    Much faster than 17 separate `SymbolInfoDouble/Integer/String` calls per symbol.

---

## 📈 Positions & Orders Methods

### get_positions_total

**Signature:** `async def get_positions_total(self, deadline, cancellation_event) -> int`

*Source: Line 728*

Get total number of open positions.

**Returns:** `int` count directly (no Data struct)

---

### get_opened_orders

**Signature:** `async def get_opened_orders(self, sort_mode, deadline, cancellation_event) -> Any`

*Source: Line 742*

Get all open positions and pending orders.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `sort_mode` | int | Sort mode for results |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `OpenedOrdersData` with separate lists for positions and orders

!!! note "Technical Details"
    Returns protobuf `OpenedOrdersData` with `data.position_infos` and `data.order_infos`.
    Each contains full position/order details (ticket, symbol, volume, profit, SL/TP, etc.).
    For tickets only (faster), use `get_opened_tickets()` which skips detailed field parsing.

---

### get_opened_tickets

**Signature:** `async def get_opened_tickets(self, deadline, cancellation_event)`

*Source: Line 763*

Get only ticket numbers (lightweight).

**Returns:** Tuple of `(position_tickets, order_tickets)`

!!! success "Performance"
    10-20x faster than `get_opened_orders()` when you only need ticket IDs for existence checks or counting.

!!! note "Technical Details"
    Low-level returns `OpenedOrdersTicketsData` with two repeated int64 fields.
    This extracts `position_tickets` and `order_tickets` lists without parsing full position/order details.

---

### get_order_history

**Signature:** `async def get_order_history(self, from_dt, to_dt, sort_mode, page_number, items_per_page, deadline, cancellation_event) -> Any`

*Source: Line 781*

Get historical orders and deals for a time period.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `from_dt` | datetime | Start time |
| `to_dt` | datetime | End time |
| `sort_mode` | int | Sort mode |
| `page_number` | int | Page number for pagination |
| `items_per_page` | int | Items per page |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `OrdersHistoryData` with orders and deals

!!! note "Technical Details"
    Returns protobuf `OrdersHistoryData` with `data.order_history_infos` (repeated field).
    Includes both orders and their related deals. Supports pagination for large result sets.
    For closed positions with P&L, use `get_positions_history()` instead (more detailed profit tracking).

---

### get_positions_history

**Signature:** `async def get_positions_history(self, sort_type, open_from, open_to, page, size, deadline, cancellation_event) -> Any`

*Source: Line 810*

Get closed positions history with P&L.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `sort_type` | int | Sort type |
| `open_from` | datetime | Start of open time filter |
| `open_to` | datetime | End of open time filter |
| `page` | int | Page number |
| `size` | int | Items per page |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `PositionsHistoryData` with closed positions

!!! note "Technical Details"
    Returns protobuf `PositionsHistoryData` with `data.history_positions` (repeated field).
    Each `PositionHistoryInfo` includes profit, commission, swap, open/close times and prices.
    Filters by position open time (not close time). Better than `order_history` for profit calculations.

---

## 📖 Market Depth (DOM) Methods

### subscribe_market_depth

**Signature:** `async def subscribe_market_depth(self, symbol, deadline, cancellation_event) -> bool`

*Source: Line 846*

Subscribe to Depth of Market (DOM) updates.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name to subscribe |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** Success status

!!! note "Technical Details"
    Low-level returns `MarketBookAddData` with `data.success` wrapper.
    This auto-extracts bool. Required before calling `get_market_depth()` to receive DOM snapshots.
    Terminal maintains subscription - call `unsubscribe_market_depth()` when done to free resources.

---

### unsubscribe_market_depth

**Signature:** `async def unsubscribe_market_depth(self, symbol, deadline, cancellation_event) -> bool`

*Source: Line 868*

Unsubscribe from DOM updates.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name to unsubscribe |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** Success status

!!! warning "Important"
    Always unsubscribe when done - brokers may limit concurrent DOM subscriptions.

!!! note "Technical Details"
    Low-level returns `MarketBookReleaseData` with `data.success` wrapper.
    This auto-extracts bool. Releases DOM subscription to free terminal resources.

---

### get_market_depth

**Signature:** `async def get_market_depth(self, symbol, deadline, cancellation_event)`

*Source: Line 890*

Get current DOM snapshot.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** List of `BookInfo` entries

!!! note "Technical Details"
    Low-level returns `MarketBookGetData` with `data.books` (repeated `BookRecord` protobuf).
    This wrapper unpacks each `BookRecord` into `BookInfo` dataclass (type, price, volume, volume_real).
    Requires prior `market_book_add` subscription. `BookRecord.type`: 1=BUY (bid), 2=SELL (ask) levels.

---

## 💰 Trading Operations Methods

### place_order

**Signature:** `async def place_order(self, request, deadline, cancellation_event) -> OrderResult`

*Source: Line 929*

Send market/pending order to broker.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderSendRequest | Order request details |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `OrderResult` with deal/order tickets

!!! tip "Success Check"
    Check `returned_code == 10009` (TRADE_RETCODE_DONE) for successful execution.

!!! note "Technical Details"
    Low-level returns `OrderSendData` protobuf with nested broker response fields.
    This wrapper flattens protobuf into `OrderResult` dataclass with 10 fields (returned_code, deal, order, etc.).

---

### modify_order

**Signature:** `async def modify_order(self, request, deadline, cancellation_event) -> OrderResult`

*Source: Line 963*

Modify existing order or position (SL/TP).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderModifyRequest | Modification request details |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `OrderResult` with modification details

!!! note "Technical Details"
    Low-level returns `OrderModifyData` protobuf (same structure as `OrderSendData`).
    This wrapper flattens into `OrderResult`. Used to change SL/TP on positions or modify pending order price/SL/TP.

---

### close_order

**Signature:** `async def close_order(self, request, deadline, cancellation_event) -> int`

*Source: Line 996*

Close position or delete pending order.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderCloseRequest | Close request details |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** Return code directly (10009 = success)

!!! note "Technical Details"
    Low-level returns `OrderCloseData` with `data.returned_code` wrapper.
    This auto-extracts the int return code (10009=TRADE_RETCODE_DONE means successful close/delete).
    For positions, creates opposite market order. For pending orders, sends delete request.

---

### check_order

**Signature:** `async def check_order(self, request, deadline, cancellation_event) -> OrderCheckResult`

*Source: Line 1018*

Validate order before sending to broker.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderCheckRequest | Order to validate |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** `OrderCheckResult` with validation details

!!! tip "Use Case"
    Use this before `place_order()` to pre-validate margin requirements without sending to broker.

!!! note "Technical Details"
    Low-level returns `OrderCheckResponse` with deeply nested `mrpc_mql_trade_check_result`.
    This wrapper extracts 8 validation fields (`returned_code=0` means valid, balance_after_deal, margin, etc.).

---

### calculate_margin

**Signature:** `async def calculate_margin(self, request, deadline, cancellation_event) -> float`

*Source: Line 1053*

Calculate required margin for an order.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderCalcMarginRequest | Margin calculation request |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** Margin value directly (no Data struct)

!!! note "Technical Details"
    Low-level returns `OrderCalcMarginResponse` with `data.margin` wrapper.
    This auto-extracts margin float from protobuf response. Use to check margin requirements before placing order.

---

### calculate_profit

**Signature:** `async def calculate_profit(self, request, deadline, cancellation_event) -> float`

*Source: Line 1074*

Calculate potential profit for a trade.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | OrderCalcProfitRequest | Profit calculation request |
| `deadline` | datetime | Optional deadline for the operation |
| `cancellation_event` | Event | Optional cancellation event |

**Returns:** Profit value directly (no Data struct)

!!! note "Technical Details"
    Low-level returns `OrderCalcProfitResponse` with `data.profit` wrapper.
    This auto-extracts profit float. Calculates P&L for hypothetical trade given entry/exit prices and volume.

---

## 📡 Streaming Methods

### stream_ticks

**Signature:** `async def stream_ticks(self, symbols, cancellation_event)`

*Source: Line 1101*

Real-time tick data stream.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbols` | List[str] | List of symbol names to stream |
| `cancellation_event` | Event | Optional cancellation event |

**Yields:** `SymbolTick` with time already converted to datetime

!!! note "Technical Details"
    Low-level streams `OnSymbolTickData` with `symbol_tick.time` as protobuf Timestamp.
    This wrapper converts each Timestamp to Python datetime via `ToDatetime()` for every tick.
    Stream continues until `cancellation_event.set()` or connection loss (auto-reconnects via `execute_stream_with_reconnect`).

---

### stream_trade_updates

**Signature:** `async def stream_trade_updates(self, cancellation_event)`

*Source: Line 1135*

Real-time trade events stream (new/closed positions).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cancellation_event` | Event | Optional cancellation event |

**Yields:** `OnTradeData` events

!!! note "Technical Details"
    Server pushes `OnTradeData` when position opens/closes or pending order placed/deleted.
    Each event contains `position_info` or `order_info` with full details (ticket, symbol, volume, type, etc.).
    Thin wrapper - passes through protobuf `OnTradeData` without conversion (minimal overhead).

---

### stream_position_profits

**Signature:** `async def stream_position_profits(self, interval_ms, ignore_empty, cancellation_event)`

*Source: Line 1155*

Real-time position profit updates stream.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `interval_ms` | int | Polling interval in milliseconds |
| `ignore_empty` | bool | Skip frames with no changes |
| `cancellation_event` | Event | Optional cancellation event |

**Yields:** `OnPositionProfitData` with P&L updates

!!! note "Technical Details"
    Server polls positions every `interval_ms` and pushes updates when profit changes.
    `ignore_empty=True` filters out frames where no position P&L changed, reducing bandwidth.
    Each `OnPositionProfitData` contains `position_profits` repeated field with ticket→profit mapping.

---

### stream_opened_tickets

**Signature:** `async def stream_opened_tickets(self, interval_ms, cancellation_event)`

*Source: Line 1179*

Real-time position/order ticket updates stream (lightweight).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `interval_ms` | int | Polling interval in milliseconds |
| `cancellation_event` | Event | Optional cancellation event |

**Yields:** `OnPositionsAndPendingOrdersTicketsData` with ticket IDs

!!! success "Performance"
    10-20x less bandwidth than `stream_trade_updates()` - use when you only need to track ticket changes.

!!! note "Technical Details"
    Server polls every `interval_ms` and pushes `OnPositionsAndPendingOrdersTicketsData`.
    Contains `opened_position_tickets` and `opened_orders_tickets` repeated int64 fields.

---

### stream_transactions

**Signature:** `async def stream_transactions(self, cancellation_event)`

*Source: Line 1201*

Real-time trade transaction stream (detailed).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cancellation_event` | Event | Optional cancellation event |

**Yields:** `OnTradeTransactionData` events

!!! note "Technical Details"
    Server pushes `OnTradeTransactionData` for every trade operation step (request→broker→result).
    More detailed than `on_trade`: includes `transaction_type` (DEAL_ADD, ORDER_DELETE, etc.) and request details.
    Thin wrapper - passes through protobuf `OnTradeTransactionData` without conversion.

---
