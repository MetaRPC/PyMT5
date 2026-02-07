# MT5Sugar - Master Overview

> High-level convenience methods for MetaTrader 5 trading automation in Python

**MT5Sugar** extends `MT5Service` with convenient methods for:

- Risk-based position sizing (percentage risk, pip-based SL/TP)
- Automatic volume and price normalization
- Bulk operations (close all positions, manage multiple trades)
- Historical analysis and statistics
- Pre-trade validation and margin checking
- Real-time P/L monitoring and position tracking
- Simplified connection management

---

## Navigation by Category

### 🔌 [01] CONNECTION

**Connect to MT5 terminal and check connection status**

| Method | Description | Documentation |
|--------|-------------|---------------|
| `quick_connect()` | Connect using cluster name (RECOMMENDED) | [Docs](1.%20Connection/quick_connect.md) |
| `is_connected()` | Check if connected to MT5 | [Docs](1.%20Connection/is_connected.md) |
| `ping()` | Verify connection is alive | [Docs](1.%20Connection/ping.md) |

---

### 💰 [02] ACCOUNT PROPERTIES

**Quick access to account balance and margin metrics**

| Method | Description | Documentation |
|--------|-------------|---------------|
| `get_balance()` | Account balance (realized profit only) | [Docs](2.%20Account_Properties/get_balance.md) |
| `get_equity()` | Current equity (balance + floating P/L) | [Docs](2.%20Account_Properties/get_equity.md) |
| `get_margin()` | Currently used margin | [Docs](2.%20Account_Properties/get_margin.md) |
| `get_free_margin()` | Available margin for new positions | [Docs](2.%20Account_Properties/get_free_margin.md) |
| `get_margin_level()` | Margin level percent (Equity / Margin x 100) | [Docs](2.%20Account_Properties/get_margin_level.md) |
| `get_floating_profit()` | Total floating profit/loss from all open positions | [Docs](2.%20Account_Properties/get_floating_profit.md) |
| `get_account_info()` | Complete account snapshot in one call | [Docs](2.%20Account_Properties/get_account_info.md) |

**Property syntax:**

- `balance` -- async property, equivalent to `get_balance()` | [Docs](2.%20Account_Properties/balance_property.md)

**Data structures:**

- `AccountInfo` -- login, balance, equity, profit, margin, free_margin, margin_level, leverage, currency, company, trade_allowed, trade_expert, server_name, server_time

---

### 💹 [03] PRICES AND QUOTES

**Working with current market prices**

| Method | Description | Documentation |
|--------|-------------|---------------|
| `get_bid()` | Current BID price for symbol | [Docs](3.%20Prices_Quotes/get_bid.md) |
| `get_ask()` | Current ASK price for symbol | [Docs](3.%20Prices_Quotes/get_ask.md) |
| `get_spread()` | Current spread (ASK - BID) in price units | [Docs](3.%20Prices_Quotes/get_spread.md) |
| `get_price_info()` | Complete price snapshot (bid, ask, spread, time) | [Docs](3.%20Prices_Quotes/get_price_info.md) |
| `wait_for_price()` | Wait for valid price with timeout | [Docs](3.%20Prices_Quotes/wait_for_price.md) |

**Data structures:**

- `PriceInfo` -- symbol, bid, ask, spread, time

---

### 📦 [04] SIMPLE TRADING

**Place market and pending orders without SL/TP**

#### Market Orders

| Method | Description | Documentation |
|--------|-------------|---------------|
| `buy_market()` | BUY at current ASK price | [Docs](4.%20Simple_Trading/buy_market.md) |
| `sell_market()` | SELL at current BID price | [Docs](4.%20Simple_Trading/sell_market.md) |

#### Pending Orders

| Method | Description | Documentation |
|--------|-------------|---------------|
| `buy_limit()` | Buy Limit -- buy below current price | [Docs](4.%20Simple_Trading/buy_limit.md) |
| `sell_limit()` | Sell Limit -- sell above current price | [Docs](4.%20Simple_Trading/sell_limit.md) |
| `buy_stop()` | Buy Stop -- buy above current price (breakout) | [Docs](4.%20Simple_Trading/buy_stop.md) |
| `sell_stop()` | Sell Stop -- sell below current price (breakdown) | [Docs](4.%20Simple_Trading/sell_stop.md) |

---

### 🎯 [05] TRADING WITH SL/TP

**Place orders with Stop Loss and Take Profit in one call**

Supports both absolute price values and pip-based notation via `sl_pips` / `tp_pips` parameters.

#### Market Orders with SL/TP

| Method | Description | Documentation |
|--------|-------------|---------------|
| `buy_market_with_sltp()` | BUY with SL/TP (prices or pips) | [Docs](5.%20Trading_With_SLTP/buy_market_with_sltp.md) |
| `sell_market_with_sltp()` | SELL with SL/TP (prices or pips) | [Docs](5.%20Trading_With_SLTP/sell_market_with_sltp.md) |

#### Pending Orders with SL/TP

| Method | Description | Documentation |
|--------|-------------|---------------|
| `buy_limit_with_sltp()` | Buy Limit with SL/TP | [Docs](5.%20Trading_With_SLTP/buy_limit_with_sltp.md) |
| `sell_limit_with_sltp()` | Sell Limit with SL/TP | [Docs](5.%20Trading_With_SLTP/sell_limit_with_sltp.md) |

**Example:**
```python
# BUY EURUSD: 50 pip SL, 100 pip TP (1:2 R:R)
ticket = await sugar.buy_market_with_sltp("EURUSD", volume=0.1, sl_pips=50, tp_pips=100)
```

---

### ⚙️ [06] POSITION MANAGEMENT

**Modify and close existing positions**

| Method | Description | Documentation |
|--------|-------------|---------------|
| `close_position()` | Close entire position by ticket | [Docs](6.%20Position_Management/close_position.md) |
| `close_position_partial()` | Partial close with specified volume | [Docs](6.%20Position_Management/close_position_partial.md) |
| `close_all_positions()` | Close all open positions (optionally by symbol) | [Docs](6.%20Position_Management/close_all_positions.md) |
| `modify_position_sltp()` | Modify SL and/or TP (pass None to keep) | [Docs](6.%20Position_Management/modify_position_sltp.md) |
| `modify_position_sl()` | Modify only Stop Loss | [Docs](6.%20Position_Management/modify_position_sl.md) |
| `modify_position_tp()` | Modify only Take Profit | [Docs](6.%20Position_Management/modify_position_tp.md) |

---

### 📋 [07] POSITION INFORMATION

**Query and analyze open positions**

| Method | Description | Documentation |
|--------|-------------|---------------|
| `get_open_positions()` | Get all open positions | [Docs](7.%20Position_Information/get_open_positions.md) |
| `get_position_by_ticket()` | Get specific position by ticket (None if not found) | [Docs](7.%20Position_Information/get_position_by_ticket.md) |
| `get_positions_by_symbol()` | Get all positions for specific symbol | [Docs](7.%20Position_Information/get_positions_by_symbol.md) |
| `has_open_position()` | Check if positions exist (optionally by symbol) | [Docs](7.%20Position_Information/has_open_position.md) |
| `count_open_positions()` | Total number of open positions | [Docs](7.%20Position_Information/count_open_positions.md) |
| `get_total_profit()` | Total floating P/L across all positions | [Docs](7.%20Position_Information/get_total_profit.md) |
| `get_profit_by_symbol()` | Floating P/L for specific symbol | [Docs](7.%20Position_Information/get_profit_by_symbol.md) |

**Data structures:**

- `PositionInfo` -- ticket, symbol, volume, type, profit, sl, tp, open_price, open_time

---

### 📊 [08] HISTORY AND STATISTICS

**Retrieve trading history and performance analytics**

| Method | Description | Documentation |
|--------|-------------|---------------|
| `get_deals()` | Closed positions for specified period | [Docs](8.%20History_Statistics/get_deals.md) |
| `get_profit()` | Total realized P/L for specified period | [Docs](8.%20History_Statistics/get_profit.md) |
| `get_daily_stats()` | Comprehensive daily statistics | [Docs](8.%20History_Statistics/get_daily_stats.md) |

**Convenience wrappers for `get_deals()`:**

- `get_deals_today()` -- Period.TODAY
- `get_deals_yesterday()` -- Period.YESTERDAY
- `get_deals_this_week()` -- Period.THIS_WEEK (Monday to now)
- `get_deals_this_month()` -- Period.THIS_MONTH
- `get_deals_date_range(from_date, to_date)` -- Period.CUSTOM

**Convenience wrappers for `get_profit()`:**

- `get_profit_today()` -- Period.TODAY
- `get_profit_this_week()` -- Period.THIS_WEEK
- `get_profit_this_month()` -- Period.THIS_MONTH

**Data structures:**

- `DailyStats` -- date, deals_count, profit, commission, swap, volume

---

### 🏷️ [09] SYMBOL INFORMATION

**Symbol properties and trading conditions**

| Method | Description | Documentation |
|--------|-------------|---------------|
| `get_symbol_info()` | Complete symbol parameters in one call | [Docs](9.%20Symbol_Information/get_symbol_info.md) |
| `get_all_symbols()` | List of all available symbols on broker | [Docs](9.%20Symbol_Information/get_all_symbols.md) |
| `is_symbol_available()` | Check if symbol exists and is available | [Docs](9.%20Symbol_Information/is_symbol_available.md) |
| `get_min_stop_level()` | Minimum SL/TP distance in points | [Docs](9.%20Symbol_Information/get_min_stop_level.md) |
| `get_symbol_digits()` | Decimal precision for symbol price | [Docs](9.%20Symbol_Information/get_symbol_digits.md) |

**Data structures:**

- `SymbolInfo` -- name, bid, ask, spread, digits, point, volume_min, volume_max, volume_step, contract_size

---

### 🛡️ [10] RISK MANAGEMENT

**Position sizing, margin calculations, and pre-trade validation**

| Method | Description | Documentation |
|--------|-------------|---------------|
| `calculate_position_size()` | Auto-calculate lot size by risk percent | [Docs](10.%20Risk_Management/calculate_position_size.md) |
| `calculate_required_margin()` | Margin needed for a specific position | [Docs](10.%20Risk_Management/calculate_required_margin.md) |
| `can_open_position()` | Full pre-trade validation via MT5 order_check | [Docs](10.%20Risk_Management/can_open_position.md) |
| `get_max_lot_size()` | Maximum tradeable volume for symbol | [Docs](10.%20Risk_Management/get_max_lot_size.md) |

**Example:**
```python
# Auto-calculate lot size to risk 2% with 50 pip SL
volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)
```

---

## Common Use Cases

### 1. Simple market order
```python
ticket = await sugar.buy_market("EURUSD", volume=0.10)
print(f"Position opened: #{ticket}")
```

### 2. Market order with SL/TP in pips
```python
ticket = await sugar.buy_market_with_sltp(
    "EURUSD", volume=0.10,
    sl_pips=50, tp_pips=100
)
print(f"BUY #{ticket} opened (1:2 R:R)")
```

### 3. Risk-based position sizing
```python
symbol = "EURUSD"
risk_percent = 2.0      # Risk 2% of balance
sl_pips = 50            # 50 pip stop loss

# Calculate lot size automatically
volume = await sugar.calculate_position_size(symbol, risk_percent, sl_pips)

# Validate before trading
can_open, reason = await sugar.can_open_position(symbol, volume)
if not can_open:
    print(f"Cannot trade: {reason}")
else:
    ticket = await sugar.buy_market_with_sltp(symbol, volume, sl_pips=50, tp_pips=100)
    print(f"Position #{ticket} opened (risking {risk_percent}%)")
```

### 4. Complete trading workflow
```python
# Step 1: Connect
await sugar.quick_connect("FxPro-MT5 Demo")

# Step 2: Check symbol
if not await sugar.is_symbol_available("EURUSD"):
    raise ValueError("Symbol not available")

# Step 3: Calculate position size (risk 2%)
volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)

# Step 4: Validate
can_open, reason = await sugar.can_open_position("EURUSD", volume)
if not can_open:
    raise RuntimeError(f"Cannot trade: {reason}")

# Step 5: Trade
ticket = await sugar.buy_market_with_sltp("EURUSD", volume, sl_pips=50, tp_pips=100)
print(f"Position #{ticket} opened")
```

### 5. Monitor positions and close on drawdown
```python
total_profit = await sugar.get_total_profit()
print(f"Floating P/L: ${total_profit:.2f}")

if total_profit < -500:
    print("Drawdown $500 -- closing all positions")
    closed_count = await sugar.close_all_positions()
    print(f"Closed {closed_count} positions")
```

### 6. Daily performance report
```python
info = await sugar.get_account_info()
print(f"Account: #{info.login}, Balance: ${info.balance:.2f}, Equity: ${info.equity:.2f}")

stats = await sugar.get_daily_stats()
print(f"Today -- Deals: {stats.deals_count}, Profit: ${stats.profit:.2f}")
```

### 7. Symbol-specific analysis
```python
symbol = "EURUSD"

has_pos = await sugar.has_open_position(symbol)
print(f"{symbol} has open position: {has_pos}")

if has_pos:
    profit = await sugar.get_profit_by_symbol(symbol)
    print(f"{symbol} floating P/L: ${profit:.2f}")

    if profit < -100:
        closed = await sugar.close_all_positions(symbol)
        print(f"Closed {closed} positions for {symbol}")
```

### 8. Pending order with validation
```python
symbol = "EURUSD"
volume = 0.1
limit_price = 1.08500

# Get current price
price_info = await sugar.get_price_info(symbol)
print(f"Current bid: {price_info.bid}, ask: {price_info.ask}")

# Validate margin
margin_needed = await sugar.calculate_required_margin(symbol, volume)
free_margin = await sugar.get_free_margin()

if margin_needed > free_margin:
    raise RuntimeError("Insufficient margin")

# Place Buy Limit below current price
if limit_price < price_info.ask:
    ticket = await sugar.buy_limit_with_sltp(
        symbol, volume, price=limit_price,
        sl=1.08000, tp=1.09000
    )
    print(f"Buy Limit placed: #{ticket}")
```

### 9. Weekly performance tracking
```python
deals = await sugar.get_deals_this_week()
print(f"Trades this week: {len(deals)}")

if deals:
    total_profit = sum(d.profit for d in deals)
    winners = sum(1 for d in deals if d.profit > 0)
    win_rate = (winners / len(deals)) * 100

    print(f"Win rate: {win_rate:.1f}%")
    print(f"Total profit: ${total_profit:.2f}")
```

### 10. Multi-symbol portfolio
```python
symbols = ["EURUSD", "GBPUSD", "USDJPY"]

print("PORTFOLIO STATUS")
print("=" * 40)

total_floating = 0.0

for symbol in symbols:
    positions = await sugar.get_positions_by_symbol(symbol)
    count = len(positions)
    profit = 0.0

    if count > 0:
        profit = await sugar.get_profit_by_symbol(symbol)
        total_floating += profit

    print(f"{symbol}: {count} positions, P/L: ${profit:.2f}")

print(f"\nTotal floating P/L: ${total_floating:.2f}")
```

---

## Related Documentation

- **MT5Account** -- Low-level gRPC/Proto methods | [MT5Account Overview](../MT5Account/MT5Account.Master.Overview.md)
- **MT5Service** -- Mid-level service layer | [MT5Service Overview](../MT5Service/MT5Service.Overview.md)
- **MT5Sugar** (this document) -- High-level convenience methods

---

## Architecture

```
MT5Sugar (High-level)  <-- You are here
    |  Simplified trading, risk management, analytics
    v
MT5Service (Mid-level)
    |  Type conversion, timeout management
    v
MT5Account (Low-level)
    |  Direct gRPC/Protobuf calls
    v
MetaTrader 5 Terminal
```

**Layer Comparison:**

| Feature | MT5Account | MT5Service | MT5Sugar |
|---------|------------|------------|----------|
| Complexity | Low-level Proto | Mid-level typed | High-level convenience |
| Learning curve | Steep | Moderate | Gentle |
| Verbosity | High | Medium | Low |
| Risk management | Manual | Manual | Built-in |
| Position sizing | Manual | Manual | Automatic |
| SL/TP | Prices only | Prices only | Pips or prices |
| Use case | Custom wrappers | Standard apps | Trading bots |

---

## Conventions

- All methods are async -- always use `await`
- Prices are always absolute (e.g., 1.08500), not relative
- Volumes are always in lots (e.g., 0.1), not currency units
- **Points** -- minimum price increment (for 5-digit: 0.00001)
- **Pips** -- standard trader unit (for 5-digit: 1 pip = 10 points = 0.0001)
- `sl_pips` / `tp_pips` parameters accept pips
- `get_min_stop_level()` returns points (not pips)
- Timeouts are built-in (typically 5 seconds) -- no need to specify
- All times are MT5 server time (not local time)
- Symbol names are case-sensitive -- use uppercase (e.g., "EURUSD")
- `get_profit()` returns gross profit -- does not subtract commission/swap. Use `get_daily_stats()` for net
- `get_deals()` returns up to 10,000 positions per request -- split large date ranges

---

## Best Practices

### Risk Management

```python
# ALWAYS use calculate_position_size for risk-based trading
volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)  # Good

# Do not use fixed lot sizes -- does not scale with account size
# volume = 0.1  # Bad
```

### Pre-Trade Validation

```python
# ALWAYS validate before trading
can_open, reason = await sugar.can_open_position("EURUSD", volume)
if not can_open:
    print(f"Cannot trade: {reason}")
else:
    ticket = await sugar.buy_market_with_sltp("EURUSD", volume, sl_pips=50, tp_pips=100)
```

### Error Handling

```python
# ALWAYS check errors
try:
    ticket = await sugar.buy_market("EURUSD", volume=0.1)
    print(f"Success: #{ticket}")
except RuntimeError as e:
    print(f"Trade failed: {e}")
```

### Use Pip-Based Methods

```python
# Prefer pip-based notation (more intuitive)
await sugar.buy_market_with_sltp("EURUSD", 0.1, sl_pips=50, tp_pips=100)  # Good

# Instead of calculating prices manually (error-prone)
# ask = await sugar.get_ask("EURUSD")
# sl = ask - 0.00050  # Bad -- manual calculation
```

### Connection Management

```python
# Check connection before trading
if not await sugar.is_connected():
    await sugar.quick_connect("FxPro-MT5 Demo")

# Verify with ping
if not await sugar.ping():
    raise RuntimeError("Connection lost")
```

---

## Quick Start

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def main():
    # 1. Create instances
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    # 2. Connect
    await sugar.quick_connect("FxPro-MT5 Demo")

    # 3. Calculate position size (risk 2%)
    volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)

    # 4. Validate
    can_open, reason = await sugar.can_open_position("EURUSD", volume)
    if not can_open:
        raise RuntimeError(f"Cannot trade: {reason}")

    # 5. Trade with pips
    ticket = await sugar.buy_market_with_sltp(
        "EURUSD", volume,
        sl_pips=50, tp_pips=100
    )
    print(f"Position #{ticket} opened")
    print(f"Risk: 2% | SL: 50 pips | TP: 100 pips | R:R 1:2")
```

---

Start with `buy_market_with_sltp()`, `calculate_position_size()`, and `can_open_position()` -- these three methods cover 80% of trading needs.
