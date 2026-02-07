# 🎯 MT5Sugar API Reference

!!! info "Documentation Status"
    **Auto-generated from source code** (`src/pymt5/mt5_sugar.py`) and enhanced for readability.
    Complete API reference with enhanced navigation. Single-page format for easy browsing.

---

## 📌 Overview

MT5Sugar represents a high-level convenience API for MT5 trading using Python best practices. It sits at the top of the architecture stack, providing maximum simplicity with properties for instant access, context managers, enums instead of magic numbers, unified methods with smart defaults, and comprehensive type hints. This is the recommended layer for most trading applications.

!!! success "Key Features"
    - ✅ Python properties for instant access (`await sugar.balance`, `await sugar.equity`)
    - ✅ Context managers for automatic connection handling (`async with MT5Sugar.connect(...)`)
    - ✅ Enums instead of magic numbers (Period.TODAY, OrderType.BUY)
    - ✅ Smart defaults and unified method signatures
    - ✅ 62 async methods + 7 properties covering all trading scenarios
    - ✅ Built-in risk management and position sizing calculators
    - ✅ Comprehensive type hints for IDE autocomplete

!!! tip "Detailed Guide Available"
    📖 [MT5Sugar Master Overview](../MT5Sugar/MT5Sugar.Master.Overview.md) - Complete high-level API guide with examples, best practices, and usage patterns for all 62 methods

---

## 📑 Table of Contents

### 👤 Account Information
- [get_balance](#get_balance) — Get account balance
- [get_equity](#get_equity) — Get current equity
- [get_margin](#get_margin) — Get used margin
- [get_free_margin](#get_free_margin) — Get available margin
- [get_margin_level](#get_margin_level) — Get margin level %
- [get_floating_profit](#get_floating_profit) — Get floating profit/loss
- [get_account_info](#get_account_info) — Complete account info

### 🔑 Account Properties (async)
- [balance](#balance) — Property: Account balance
- [equity](#equity) — Property: Current equity
- [margin](#margin) — Property: Used margin
- [free_margin](#free_margin) — Property: Free margin
- [margin_level](#margin_level) — Property: Margin level %
- [profit](#profit) — Property: Total floating profit/loss

### 💹 Prices & Quotes
- [get_bid](#get_bid) — Get BID price
- [get_ask](#get_ask) — Get ASK price
- [get_spread](#get_spread) — Get spread in points
- [get_price_info](#get_price_info) — Complete price info
- [wait_for_price](#wait_for_price) — Wait for valid price

### 📊 Simple Trading (Market & Pending)
- [buy_market](#buy_market) — Open BUY at market
- [sell_market](#sell_market) — Open SELL at market
- [buy_limit](#buy_limit) — Place BUY LIMIT
- [sell_limit](#sell_limit) — Place SELL LIMIT
- [buy_stop](#buy_stop) — Place BUY STOP
- [sell_stop](#sell_stop) — Place SELL STOP

### 🎯 Trading with SL/TP
- [buy_market_with_sltp](#buy_market_with_sltp) — BUY with stop loss/take profit
- [sell_market_with_sltp](#sell_market_with_sltp) — SELL with stop loss/take profit
- [buy_limit_with_sltp](#buy_limit_with_sltp) — BUY LIMIT with SL/TP
- [sell_limit_with_sltp](#sell_limit_with_sltp) — SELL LIMIT with SL/TP
- [buy_market_with_pips](#buy_market_with_pips) — BUY with SL/TP in pips
- [sell_market_with_pips](#sell_market_with_pips) — SELL with SL/TP in pips
- [calculate_sltp](#calculate_sltp) — Convert pips to prices

### 📈 Position Management
- [close_position](#close_position) — Close position by ticket
- [close_position_partial](#close_position_partial) — Partial close
- [close_all_positions](#close_all_positions) — Close all positions
- [modify_position_sltp](#modify_position_sltp) — Modify SL/TP
- [modify_position_sl](#modify_position_sl) — Modify stop loss only
- [modify_position_tp](#modify_position_tp) — Modify take profit only
- [get_open_positions](#get_open_positions) — Get all open positions
- [get_position_by_ticket](#get_position_by_ticket) — Get position by ticket
- [get_positions_by_symbol](#get_positions_by_symbol) — Get positions for symbol
- [has_open_position](#has_open_position) — Check if positions exist
- [count_open_positions](#count_open_positions) — Count open positions
- [get_total_profit](#get_total_profit) — Total P&L across positions
- [get_profit_by_symbol](#get_profit_by_symbol) — P&L for symbol

### 📜 History & Statistics
- [get_deals](#get_deals) — Get deals for period
- [get_profit](#get_profit) — Get profit for period
- [get_deals_today](#get_deals_today) — Today's deals
- [get_deals_yesterday](#get_deals_yesterday) — Yesterday's deals
- [get_deals_this_week](#get_deals_this_week) — This week's deals
- [get_deals_this_month](#get_deals_this_month) — This month's deals
- [get_deals_date_range](#get_deals_date_range) — Deals in date range
- [get_profit_today](#get_profit_today) — Today's profit
- [get_profit_this_week](#get_profit_this_week) — This week's profit
- [get_profit_this_month](#get_profit_this_month) — This month's profit
- [get_daily_stats](#get_daily_stats) — Daily trading statistics

### 🔍 Symbol Information
- [get_symbol_info](#get_symbol_info) — Complete symbol info
- [get_all_symbols](#get_all_symbols) — List all symbols
- [is_symbol_available](#is_symbol_available) — Check symbol availability
- [get_min_stop_level](#get_min_stop_level) — Minimum SL/TP distance
- [get_symbol_digits](#get_symbol_digits) — Decimal places

### 🛡️ Risk Management
- [calculate_position_size](#calculate_position_size) — Calculate lot size by risk
- [can_open_position](#can_open_position) — Validate position opening
- [get_max_lot_size](#get_max_lot_size) — Maximum allowed lot size
- [calculate_required_margin](#calculate_required_margin) — Calculate required margin

---

## 🏗️ Class: MT5Sugar

*Source: Line 225*

High-level convenience API for MT5 trading using Python best practices.

MT5Sugar represents the highest-level API layer in the PyMT5 architecture, designed for maximum simplicity and developer productivity. It wraps MT5Service with intuitive Pythonic patterns including async properties (`await sugar.balance`), context managers (`async with sugar.connect()`), enums instead of magic numbers, smart method defaults, and comprehensive risk management tools. This is the recommended layer for building trading applications, bots, and analysis tools.

!!! tip "Architecture Position"
    - **LOW** MT5Account (protobuf Request/Data, direct gRPC)
    - **MID** MT5Service (Python types, removes Data wrappers)
    - **HIGH** MT5Sugar (business logic, ready-made patterns) **← THIS CLASS**

!!! note "Constructor Requirements"
    - Requires MT5Service instance (mid-level wrapper)
    - Optional `default_timeout` (seconds for operations, default 10.0)
    - Optional `default_symbol` (default trading symbol like "EURUSD")
    - **Recommended**: Use `MT5Sugar.connect()` class method instead of direct construction

!!! tip "Usage Patterns"
    **Pattern 1: Context Manager (Recommended)**
    ```python
    async with MT5Sugar.connect("ICMarkets-Demo") as sugar:
        balance = await sugar.balance
        ticket = await sugar.buy_market("EURUSD", 0.1)
    ```

    **Pattern 2: Manual Connection**
    ```python
    account = MT5Account.create(user=12345, password="pass", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name("ICMarkets-Demo", "EURUSD")
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    balance = await sugar.balance
    ticket = await sugar.buy_market("EURUSD", 0.1)
    ```

    **Pattern 3: Properties for Quick Access**
    ```python
    balance = await sugar.balance  # Instead of await sugar.get_balance()
    equity = await sugar.equity
    margin_level = await sugar.margin_level
    ```

!!! success "Key Advantages"
    - **Pythonic API**: Properties, context managers, enums, type hints
    - **Smart defaults**: Default symbol, automatic price fetching, sensible timeouts
    - **Risk management**: Position sizing by risk %, margin validation, lot size limits
    - **Convenience methods**: Today's profit, this week's deals, close all positions
    - **Flexible SL/TP**: Specify as absolute prices OR pips (auto-converted)
    - **Error handling**: Clear RuntimeError messages on trading failures

---

## 🔧 Constructor & Connection

### __init__

**Signature:** `def __init__(self, service, default_timeout, default_symbol)`

*Source: Line 245*

Initialize MT5Sugar with a service instance.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `service` | MT5Service | - | Mid-level service instance |
| `default_timeout` | float | 10.0 | Default timeout for operations in seconds |
| `default_symbol` | str | None | Default trading symbol (e.g., "EURUSD") |

---

### connect

**Signature:** `async def connect(cls, host, port, login, password) -> MT5Sugar`

*Source: Line 264*

Create and connect MT5Sugar instance (use as context manager).

!!! tip "Recommended Usage"
    Use this method with `async with` for automatic cleanup:
    ```python
    async with MT5Sugar.connect("ICMarkets-Demo") as sugar:
        # Your trading code here
        pass
    # Connection automatically closed
    ```

---

### service

**Signature:** `def service(self) -> MT5Service`

*Source: Line 280*

Get underlying MT5Service for advanced operations.

**Returns:** MT5Service instance

---

### is_connected

**Signature:** `def is_connected(self) -> bool`

*Source: Line 291*

Check if connection to MT5 server is active.

**Returns:** `True` if gRPC channel is ready or idle, `False` otherwise

!!! example "Example"
    ```python
    if sugar.is_connected():
        balance = await sugar.get_balance()
    else:
        print("Not connected to MT5 server")
    ```

---

### ping

**Signature:** `async def ping(self, timeout) -> bool`

*Source: Line 318*

Ping MT5 server to check connection health.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeout` | float | - | Timeout in seconds for ping attempt |

**Returns:** `True` if server responds successfully, `False` otherwise

---

### quick_connect

**Signature:** `async def quick_connect(self, cluster_name, base_symbol) -> None`

*Source: Line 340*

Quick connect (or reconnect) to MT5 cluster by name.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cluster_name` | str | - | MT5 cluster identifier (e.g., "ICMarkets-Demo", "FxPro-Live01") |
| `base_symbol` | str | "EURUSD" | Base chart symbol for connection |

!!! warning "Raises"
    - `RuntimeError`: If credentials are not accessible in MT5Account
    - `Exception`: If connection to cluster fails

---

## 👤 Account Information Methods

### get_balance

**Signature:** `async def get_balance(self) -> float`

*Source: Line 386*

Get account balance (realized profit only).

**Returns:** Account balance as float

---

### get_equity

**Signature:** `async def get_equity(self) -> float`

*Source: Line 396*

Get current equity (balance + floating P/L).

**Returns:** Current equity as float

---

### get_margin

**Signature:** `async def get_margin(self) -> float`

*Source: Line 406*

Get used margin.

**Returns:** Used margin as float

---

### get_free_margin

**Signature:** `async def get_free_margin(self) -> float`

*Source: Line 417*

Get available margin for new positions.

**Returns:** Free margin as float

---

### get_margin_level

**Signature:** `async def get_margin_level(self) -> float`

*Source: Line 428*

Get margin level % (Equity/Margin × 100).

**Returns:** Margin level percentage

!!! warning "Important"
    Brokers trigger margin call/stop out when level drops below threshold (typically 100%/50%).

---

### get_floating_profit

**Signature:** `async def get_floating_profit(self) -> float`

*Source: Line 439*

Get total floating profit/loss from open positions.

**Returns:** Total floating P&L

---

## 🔑 Account Properties (async)

### balance

**Signature:** `async def balance(self) -> float`

*Source: Line 452*

Property: Account balance

!!! example "Usage"
    ```python
    balance = await sugar.balance
    print(f"Balance: ${balance:.2f}")
    ```

---

### equity

**Signature:** `async def equity(self) -> float`

*Source: Line 457*

Property: Current equity

---

### margin

**Signature:** `async def margin(self) -> float`

*Source: Line 462*

Property: Used margin

---

### free_margin

**Signature:** `async def free_margin(self) -> float`

*Source: Line 467*

Property: Free margin

---

### margin_level

**Signature:** `async def margin_level(self) -> float`

*Source: Line 472*

Property: Margin level %

---

### profit

**Signature:** `async def profit(self) -> float`

*Source: Line 477*

Property: Total floating profit/loss

---

## 💹 Prices & Quotes Methods

### get_bid

**Signature:** `async def get_bid(self, symbol) -> float`

*Source: Line 488*

Get current BID price.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name (uses default_symbol if None) |

**Returns:** BID price

---

### get_ask

**Signature:** `async def get_ask(self, symbol) -> float`

*Source: Line 502*

Get current ASK price.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name (uses default_symbol if None) |

**Returns:** ASK price

---

### get_spread

**Signature:** `async def get_spread(self, symbol) -> float`

*Source: Line 516*

Get current spread in points.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name (uses default_symbol if None) |

**Returns:** Spread in points

---

### get_price_info

**Signature:** `async def get_price_info(self, symbol) -> PriceInfo`

*Source: Line 530*

Get complete price information.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name (uses default_symbol if None) |

**Returns:** `PriceInfo` dataclass with bid, ask, spread, time

---

### wait_for_price

**Signature:** `async def wait_for_price(self, symbol, timeout) -> PriceInfo`

*Source: Line 545*

Wait for valid price update with timeout.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name (uses default_symbol if None) |
| `timeout` | float | 10.0 | Timeout in seconds |

**Returns:** `PriceInfo` when price updates

---

## 📊 Simple Trading Methods

### buy_market

**Signature:** `async def buy_market(self, symbol, volume, comment, magic) -> int`

*Source: Line 568*

Open BUY position at market price.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name (uses default_symbol if None) |
| `volume` | float | - | Volume in lots |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Position ticket number

!!! example "Example"
    ```python
    ticket = await sugar.buy_market("EURUSD", 0.1)
    print(f"Opened BUY position #{ticket}")
    ```

---

### sell_market

**Signature:** `async def sell_market(self, symbol, volume, comment, magic) -> int`

*Source: Line 613*

Open SELL position at market price.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name (uses default_symbol if None) |
| `volume` | float | - | Volume in lots |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Position ticket number

---

### buy_limit

**Signature:** `async def buy_limit(self, symbol, volume, price, comment, magic) -> int`

*Source: Line 658*

Place BUY LIMIT pending order (buy below current price).

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name (uses default_symbol if None) |
| `volume` | float | - | Volume in lots |
| `price` | float | - | Limit price |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Order ticket number

!!! example "Example"
    ```python
    ticket = await sugar.buy_limit("EURUSD", 0.1, price=1.0850)
    ```

---

### sell_limit

**Signature:** `async def sell_limit(self, symbol, volume, price, comment, magic) -> int`

*Source: Line 698*

Place SELL LIMIT pending order (sell above current price).

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name (uses default_symbol if None) |
| `volume` | float | - | Volume in lots |
| `price` | float | - | Limit price |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Order ticket number

!!! example "Example"
    ```python
    ticket = await sugar.sell_limit("EURUSD", 0.1, price=1.0950)
    ```

---

### buy_stop

**Signature:** `async def buy_stop(self, symbol, volume, price, comment, magic) -> int`

*Source: Line 738*

Place BUY STOP pending order (buy above current price).

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name (uses default_symbol if None) |
| `volume` | float | - | Volume in lots |
| `price` | float | - | Stop price |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Order ticket number

!!! example "Example"
    ```python
    ticket = await sugar.buy_stop("EURUSD", 0.1, price=1.0950)
    ```

---

### sell_stop

**Signature:** `async def sell_stop(self, symbol, volume, price, comment, magic) -> int`

*Source: Line 778*

Place SELL STOP pending order (sell below current price).

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name (uses default_symbol if None) |
| `volume` | float | - | Volume in lots |
| `price` | float | - | Stop price |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Order ticket number

!!! example "Example"
    ```python
    ticket = await sugar.sell_stop("EURUSD", 0.1, price=1.0850)
    ```

---

## 🎯 Trading with SL/TP Methods

### buy_market_with_sltp

**Signature:** `async def buy_market_with_sltp(self, symbol, volume, sl, tp, sl_pips, tp_pips, comment, magic) -> int`

*Source: Line 824*

Open BUY position with Stop Loss and Take Profit.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name |
| `volume` | float | - | Volume in lots |
| `sl` | float | None | Stop Loss price (absolute) |
| `tp` | float | None | Take Profit price (absolute) |
| `sl_pips` | float | None | Stop Loss in pips (alternative to sl) |
| `tp_pips` | float | None | Take Profit in pips (alternative to tp) |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Position ticket number

!!! tip "Flexible SL/TP"
    You can specify SL/TP as either:
    - Absolute prices: `sl=1.0900, tp=1.1000`
    - Pips distance: `sl_pips=50, tp_pips=100`

!!! example "Examples"
    ```python
    # Using absolute prices
    ticket = await sugar.buy_market_with_sltp("EURUSD", 0.1, sl=1.0900, tp=1.1000)

    # Using pips
    ticket = await sugar.buy_market_with_sltp("EURUSD", 0.1, sl_pips=50, tp_pips=100)
    ```

---

### sell_market_with_sltp

**Signature:** `async def sell_market_with_sltp(self, symbol, volume, sl, tp, sl_pips, tp_pips, comment, magic) -> int`

*Source: Line 903*

Open SELL position with Stop Loss and Take Profit.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name |
| `volume` | float | - | Volume in lots |
| `sl` | float | None | Stop Loss price (absolute) |
| `tp` | float | None | Take Profit price (absolute) |
| `sl_pips` | float | None | Stop Loss in pips (alternative to sl) |
| `tp_pips` | float | None | Take Profit in pips (alternative to tp) |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Position ticket number

!!! example "Examples"
    ```python
    # Using absolute prices
    ticket = await sugar.sell_market_with_sltp("EURUSD", 0.1, sl=1.1000, tp=1.0900)

    # Using pips
    ticket = await sugar.sell_market_with_sltp("EURUSD", 0.1, sl_pips=50, tp_pips=100)
    ```

---

### buy_limit_with_sltp

**Signature:** `async def buy_limit_with_sltp(self, symbol, volume, price, sl, tp, sl_pips, tp_pips, comment, magic) -> int`

*Source: Line 984*

Place BUY LIMIT pending order with Stop Loss and Take Profit.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name |
| `volume` | float | - | Volume in lots |
| `price` | float | - | Limit order price |
| `sl` | float | None | Stop Loss price (absolute) |
| `tp` | float | None | Take Profit price (absolute) |
| `sl_pips` | float | None | Stop Loss in pips (alternative to sl) |
| `tp_pips` | float | None | Take Profit in pips (alternative to tp) |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Order ticket number

!!! example "Example"
    ```python
    ticket = await sugar.buy_limit_with_sltp("EURUSD", 0.1, price=1.0850, sl_pips=50, tp_pips=100)
    ```

---

### sell_limit_with_sltp

**Signature:** `async def sell_limit_with_sltp(self, symbol, volume, price, sl, tp, sl_pips, tp_pips, comment, magic) -> int`

*Source: Line 1059*

Place SELL LIMIT pending order with Stop Loss and Take Profit.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name |
| `volume` | float | - | Volume in lots |
| `price` | float | - | Limit order price |
| `sl` | float | None | Stop Loss price (absolute) |
| `tp` | float | None | Take Profit price (absolute) |
| `sl_pips` | float | None | Stop Loss in pips (alternative to sl) |
| `tp_pips` | float | None | Take Profit in pips (alternative to tp) |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Order ticket number

!!! example "Example"
    ```python
    ticket = await sugar.sell_limit_with_sltp("EURUSD", 0.1, price=1.0950, sl_pips=50, tp_pips=100)
    ```

---

### buy_market_with_pips

**Signature:** `async def buy_market_with_pips(self, symbol, volume, sl_pips, tp_pips, comment, magic) -> int`

*Source: Line 1948*

Open BUY position at market with SL/TP specified in pips.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name |
| `volume` | float | - | Volume in lots |
| `sl_pips` | float | - | Stop Loss in pips |
| `tp_pips` | float | - | Take Profit in pips |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Position ticket number

!!! example "Example"
    ```python
    # Buy 0.1 lot with 50 pip SL and 100 pip TP
    ticket = await sugar.buy_market_with_pips("EURUSD", 0.1, 50, 100)
    ```

---

### sell_market_with_pips

**Signature:** `async def sell_market_with_pips(self, symbol, volume, sl_pips, tp_pips, comment, magic) -> int`

*Source: Line 1986*

Open SELL position at market with SL/TP specified in pips.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Symbol name |
| `volume` | float | - | Volume in lots |
| `sl_pips` | float | - | Stop Loss in pips |
| `tp_pips` | float | - | Take Profit in pips |
| `comment` | str | "" | Order comment |
| `magic` | int | 0 | Magic number |

**Returns:** Position ticket number

!!! example "Example"
    ```python
    # Sell 0.1 lot with 50 pip SL and 100 pip TP
    ticket = await sugar.sell_market_with_pips("EURUSD", 0.1, 50, 100)
    ```

---

### calculate_sltp

**Signature:** `async def calculate_sltp(self, symbol, is_buy, sl_pips, tp_pips)`

*Source: Line 1896*

Convert SL/TP from pips to absolute prices.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | - | Symbol name |
| `is_buy` | bool | - | True for BUY, False for SELL |
| `sl_pips` | float | None | Stop Loss in pips |
| `tp_pips` | float | None | Take Profit in pips |

**Returns:** Tuple `(sl_price, tp_price)`. Returns `None` for values not specified.

!!! example "Examples"
    ```python
    # For BUY position
    sl_price, tp_price = await sugar.calculate_sltp("EURUSD", True, 50, 100)
    print(f"SL: {sl_price}, TP: {tp_price}")

    # For SELL position
    sl_price, tp_price = await sugar.calculate_sltp("EURUSD", False, 50, 100)
    ```

---

## 📈 Position Management Methods

### close_position

**Signature:** `async def close_position(self, ticket) -> bool`

*Source: Line 1141*

Close position completely by ticket.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket` | int | Position ticket number |

**Returns:** `True` if position closed successfully

---

### close_position_partial

**Signature:** `async def close_position_partial(self, ticket, volume) -> bool`

*Source: Line 1241*

Partially close position by specified volume.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket` | int | Position ticket number |
| `volume` | float | Volume to close (must be less than position volume) |

**Returns:** `True` if partial close successful

!!! example "Example"
    ```python
    # Close half of the position volume
    success = await sugar.close_position_partial(123456, 0.05)
    ```

---

### close_all_positions

**Signature:** `async def close_all_positions(self, symbol) -> int`

*Source: Line 1165*

Close all open positions.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | If specified, close only positions for this symbol |

**Returns:** Number of positions closed

---

### modify_position_sltp

**Signature:** `async def modify_position_sltp(self, ticket, sl, tp) -> bool`

*Source: Line 1196*

Modify position SL/TP.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket` | int | Position ticket number |
| `sl` | float | New Stop Loss price (None to keep current) |
| `tp` | float | New Take Profit price (None to keep current) |

**Returns:** `True` if modification successful

---

### modify_position_sl

**Signature:** `async def modify_position_sl(self, ticket, sl) -> bool`

*Source: Line 1299*

Modify position Stop Loss only.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket` | int | Position ticket number |
| `sl` | float | New Stop Loss price |

**Returns:** `True` if modification successful

!!! example "Example"
    ```python
    success = await sugar.modify_position_sl(123456, 1.0900)
    ```

---

### modify_position_tp

**Signature:** `async def modify_position_tp(self, ticket, tp) -> bool`

*Source: Line 1315*

Modify position Take Profit only.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket` | int | Position ticket number |
| `tp` | float | New Take Profit price |

**Returns:** `True` if modification successful

!!! example "Example"
    ```python
    success = await sugar.modify_position_tp(123456, 1.1000)
    ```

---

### get_open_positions

**Signature:** `async def get_open_positions(self)`

*Source: Line 1338*

Get all open positions.

**Returns:** List of open positions

---

### get_position_by_ticket

**Signature:** `async def get_position_by_ticket(self, ticket)`

*Source: Line 1343*

Get position by ticket number.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticket` | int | Position ticket number |

**Returns:** Position info or `None`

---

### get_positions_by_symbol

**Signature:** `async def get_positions_by_symbol(self, symbol)`

*Source: Line 1353*

Get all positions for specified symbol.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |

**Returns:** List of positions for symbol

---

### has_open_position

**Signature:** `async def has_open_position(self, symbol) -> bool`

*Source: Line 1359*

Check if there are open positions (optionally filtered by symbol).

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Optional symbol filter |

**Returns:** `True` if positions exist

---

### count_open_positions

**Signature:** `async def count_open_positions(self, symbol) -> int`

*Source: Line 1368*

Count open positions (optionally filtered by symbol).

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | None | Optional symbol filter |

**Returns:** Number of open positions

---

### get_total_profit

**Signature:** `async def get_total_profit(self) -> float`

*Source: Line 1377*

Get total profit/loss across all open positions.

**Returns:** Total floating P&L

---

### get_profit_by_symbol

**Signature:** `async def get_profit_by_symbol(self, symbol) -> float`

*Source: Line 1383*

Get total profit/loss for positions of specified symbol.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |

**Returns:** Total P&L for symbol

---

## 📜 History & Statistics Methods

### get_deals

**Signature:** `async def get_deals(self, period, from_date, to_date) -> List`

*Source: Line 1437*

Get deals for specified period.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | Period | - | Predefined period (TODAY, YESTERDAY, THIS_WEEK, THIS_MONTH, CUSTOM) |
| `from_date` | date | None | Custom start date (required if period=CUSTOM) |
| `to_date` | date | None | Custom end date (required if period=CUSTOM) |

**Returns:** List of orders (deals) for the specified period

---

### get_profit

**Signature:** `async def get_profit(self, period, from_date, to_date) -> float`

*Source: Line 1473*

Get total profit for specified period.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | Period | - | Predefined period (TODAY, YESTERDAY, THIS_WEEK, THIS_MONTH, CUSTOM) |
| `from_date` | date | None | Custom start date (required if period=CUSTOM) |
| `to_date` | date | None | Custom end date (required if period=CUSTOM) |

**Returns:** Total profit for the period

---

### get_deals_today

**Signature:** `async def get_deals_today(self) -> List`

*Source: Line 1497*

Get all deals made today.

**Returns:** List of today's orders

!!! example "Example"
    ```python
    deals = await sugar.get_deals_today()
    print(f"Today's deals: {len(deals)}")
    ```

---

### get_deals_yesterday

**Signature:** `async def get_deals_yesterday(self) -> List`

*Source: Line 1510*

Get all deals made yesterday.

**Returns:** List of yesterday's orders

---

### get_deals_this_week

**Signature:** `async def get_deals_this_week(self) -> List`

*Source: Line 1522*

Get all deals made this week (from Monday to today).

**Returns:** List of this week's orders

!!! example "Example"
    ```python
    deals = await sugar.get_deals_this_week()
    print(f"This week: {len(deals)} deals")
    ```

---

### get_deals_this_month

**Signature:** `async def get_deals_this_month(self) -> List`

*Source: Line 1535*

Get all deals made this month.

**Returns:** List of this month's orders

!!! example "Example"
    ```python
    deals = await sugar.get_deals_this_month()
    total_volume = sum(d.volume for d in deals)
    ```

---

### get_deals_date_range

**Signature:** `async def get_deals_date_range(self, from_date, to_date) -> List`

*Source: Line 1548*

Get all deals within a specific date range.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `from_date` | date | Start date (inclusive) |
| `to_date` | date | End date (inclusive) |

**Returns:** List of orders in the date range

!!! example "Example"
    ```python
    # Get January 2024 deals
    deals = await sugar.get_deals_date_range(
        date(2024, 1, 1),
        date(2024, 1, 31)
    )
    ```

---

### get_profit_today

**Signature:** `async def get_profit_today(self) -> float`

*Source: Line 1568*

Get total profit made today.

**Returns:** Today's profit/loss

!!! example "Example"
    ```python
    profit = await sugar.get_profit_today()
    print(f"Today's P/L: {profit:.2f}")
    ```

---

### get_profit_this_week

**Signature:** `async def get_profit_this_week(self) -> float`

*Source: Line 1581*

Get total profit made this week.

**Returns:** This week's profit/loss

---

### get_profit_this_month

**Signature:** `async def get_profit_this_month(self) -> float`

*Source: Line 1593*

Get total profit made this month.

**Returns:** This month's profit/loss

!!! example "Example"
    ```python
    profit = await sugar.get_profit_this_month()
    balance = await sugar.get_balance()
    monthly_return = (profit / balance) * 100
    print(f"Monthly return: {monthly_return:.2f}%")
    ```

---

### get_daily_stats

**Signature:** `async def get_daily_stats(self, target_date) -> DailyStats`

*Source: Line 2061*

Get daily trading statistics.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_date` | date | None | Date to get stats for (default: today) |

**Returns:** `DailyStats` dataclass with trading statistics for the day

!!! example "Examples"
    ```python
    # Today's stats
    stats = await sugar.get_daily_stats()
    print(f"Deals: {stats.deals_count}")
    print(f"Profit: {stats.profit}")
    print(f"Volume: {stats.volume} lots")

    # Specific date
    stats = await sugar.get_daily_stats(date(2024, 1, 15))
    ```

---

## 🔍 Symbol Information Methods

### get_symbol_info

**Signature:** `async def get_symbol_info(self, symbol) -> SymbolInfo`

*Source: Line 1615*

Get complete symbol information.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |

**Returns:** `SymbolInfo` dataclass

---

### get_all_symbols

**Signature:** `async def get_all_symbols(self)`

*Source: Line 1642*

Get list of all available symbols.

**Returns:** List of all symbols

---

### is_symbol_available

**Signature:** `async def is_symbol_available(self, symbol) -> bool`

*Source: Line 1672*

Check if symbol exists and is tradable.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |

**Returns:** `True` if available

---

### get_min_stop_level

**Signature:** `async def get_min_stop_level(self, symbol) -> int`

*Source: Line 1677*

Get minimum stop level (minimum distance for SL/TP) in points.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |

**Returns:** Minimum stop level in points

!!! example "Example"
    ```python
    min_level = await sugar.get_min_stop_level("EURUSD")
    print(f"Minimum SL/TP distance: {min_level} points")
    ```

---

### get_symbol_digits

**Signature:** `async def get_symbol_digits(self, symbol) -> int`

*Source: Line 1697*

Get number of decimal places in symbol price.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |

**Returns:** Number of digits after decimal point

!!! example "Example"
    ```python
    digits = await sugar.get_symbol_digits("EURUSD")
    print(f"EURUSD has {digits} digits")  # Usually 5 for EURUSD
    ```

---

## 🛡️ Risk Management Methods

### calculate_position_size

**Signature:** `async def calculate_position_size(self, symbol, risk_percent, sl_pips) -> float`

*Source: Line 1724*

Calculate position size based on risk percentage.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `risk_percent` | float | Risk as percentage of balance (e.g., 2.0 for 2%) |
| `sl_pips` | float | Stop Loss distance in pips |

**Returns:** Optimal position size in lots

!!! success "Risk Management Formula"
    Formula: `volume = risk_amount / (sl_pips × pip_value)`

    Where:
    - `risk_amount = balance × (risk_percent / 100)`
    - `pip_value = point × 10 × contract_size`

    Rounds to `volume_step`, clamps to `volume_min/max`.

!!! example "Example"
    ```python
    # Risk 2% of balance with 50 pip SL
    lot_size = await sugar.calculate_position_size("EURUSD", 2.0, 50)
    print(f"Optimal lot size: {lot_size}")
    ```

---

### can_open_position

**Signature:** `async def can_open_position(self, symbol, volume)`

*Source: Line 1774*

Validate if position can be opened.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |
| `volume` | float | Position volume in lots |

**Returns:** `(can_open, reason)` tuple

---

### get_max_lot_size

**Signature:** `async def get_max_lot_size(self, symbol) -> float`

*Source: Line 1821*

Get maximum lot size allowed for this symbol.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | str | Symbol name |

**Returns:** Maximum volume in lots

!!! example "Example"
    ```python
    max_lots = await sugar.get_max_lot_size("EURUSD")
    print(f"Maximum lot size: {max_lots}")
    ```

---

### calculate_required_margin

**Signature:** `async def calculate_required_margin(self, symbol, volume, order_type) -> float`

*Source: Line 1841*

Calculate margin required to open a position.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | - | Symbol name |
| `volume` | float | - | Position volume in lots |
| `order_type` | OrderType | BUY | Order type enum value |

**Returns:** Required margin in account currency

---

### get_account_info

**Signature:** `async def get_account_info(self) -> AccountInfo`

*Source: Line 2031*

Get complete account information in a structured dataclass.

**Returns:** `AccountInfo` dataclass with all account details

!!! example "Example"
    ```python
    account = await sugar.get_account_info()
    print(f"Account: {account.login}")
    print(f"Balance: {account.balance}")
    print(f"Equity: {account.equity}")
    print(f"Free Margin: {account.free_margin}")
    print(f"Margin Level: {account.margin_level}%")
    ```

---

## 🔄 Context Manager Methods

### __aenter__

**Signature:** `async def __aenter__(self)`

*Source: Line 2128*

Async context manager entry.

---

### __aexit__

**Signature:** `async def __aexit__(self, exc_type, exc_val, exc_tb)`

*Source: Line 2132*

Async context manager exit.

---
