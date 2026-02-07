# PyMT5 Glossary

> Project-specific terms and concepts. This glossary covers PyMT5 architecture, components, and trading automation terminology used throughout the codebase.

---

## 🏗️ Architectural Terms

### Three-Tier Architecture

Core design pattern of PyMT5 with three abstraction levels:

- **Tier 1 (MT5Account):** Low-level gRPC communication with MT5 terminal
- **Tier 2 (MT5Service):** Wrapper methods with dataclasses and Python types
- **Tier 3 (MT5Sugar):** High-level convenience methods with ready patterns

---

### MT5Account

**🔹 Tier 1 - Low-Level API**

Base layer providing direct access to MT5 terminal via gRPC protocol.

**Key characteristics:**

- Raw gRPC calls to MT5 terminal
- Built-in connection resilience with automatic reconnection
- Works with protobuf Request/Response objects
- Full control, maximum complexity
- **42 async methods**, covering all MT5 operations
- Returns protobuf Data objects
- Automatic reconnection with exponential backoff
- Session management with UUID tracking

**When to use:** Advanced users who need granular control, custom integrations, building custom wrappers.

**Location:** `package/helpers/mt5_account.py` (2100+ lines)

**Documentation:** [MT5Account.Master.Overview.md](../MT5Account/MT5Account.Master.Overview.md)


---

### MT5Service
**🔸 Tier 2 - Wrappers API**

Middle layer providing simplified method signatures without proto complexity.

**Key characteristics:**

- Returns clean Python types (float, int, str, datetime)
- Automatically unpacks protobuf .data wrappers
- Converts Timestamp to datetime objects
- Type conversion (proto to Python primitives/dataclasses)
- Simplified method names
- No auto-normalization (you control precision)
- **36 methods** for common scenarios
- Primary purpose: Architectural middleware layer for MT5Sugar

**Value distribution:**

- ✅ **11 HIGH/VERY HIGH value methods** - Aggregate multiple RPC calls, complex protobuf unpacking, datetime conversions

- ⚪ **25 NONE/LOW value methods** - Direct pass-through or simple single-field extraction

**When to use:** Building custom strategies that need more control than Sugar but less complexity than MT5Account.

**Location:** `src/pymt5/mt5_service.py` (1200+ lines)

**Documentation:** [MT5Service.Overview.md](../MT5Service/MT5Service.Overview.md)


---

### MT5Sugar
**🔺 Tier 3 - Convenience API**

High-level API for common trading operations.

**Key characteristics:**

- Properties for instant access (`await sugar.balance`)
- Context manager support (`async with MT5Sugar(service) as sugar`)
- Enums instead of magic numbers (`Period.TODAY`, `OrderType.BUY`)
- Unified methods with smart defaults
- One-line operations
- Type hints everywhere
- Simplest API, handles edge cases
- **Best starting point** for 95% of use cases
- **62 methods + 7 properties = 69 total**

**Key features:**

- `buy_market(symbol, volume)` - one line to open a position
- `calculate_position_size(symbol, risk_percent, sl_pips)` - automatic volume calculation by risk
- `buy_market_with_pips(symbol, volume, sl_pips, tp_pips)` - open with SL/TP in pips
- `get_balance()`, `get_equity()` - async methods for account information
- `close_all_positions()` - emergency exit

**When to use:** Rapid development, prototyping, simple strategies, quick scripts.

**Location:** `src/pymt5/mt5_sugar.py` (2100+ lines)

**Documentation:** [MT5Sugar Overview](../MT5Sugar/MT5Sugar.Master.Overview.md)


---

## 🧩 Python-Specific Concepts

### Async/Await Pattern
Python's built-in asynchronous programming model.

**All methods in PyMT5 are async:**
```python
import asyncio
from MetaRpcMT5 import MT5Account
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

async def main():
    # Create and connect
    account = MT5Account.create()
    await account.connect_by_server_name(...)

    # Must use 'await' for all async operations
    balance = await account.account_info_double(
        account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
    )
    positions = await account.positions_total()

    await account.channel.close()

# Run async function
asyncio.run(main())
```

**Why async?**

- Non-blocking I/O for gRPC calls
- Better performance for multiple operations
- Can handle streaming data efficiently
- Standard Python pattern for network operations

**Documentation:** [Python asyncio](https://docs.python.org/3/library/asyncio.html)

---

### Dataclasses
Python's structured data containers.

**MT5Service uses dataclasses for clean data structures:**
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AccountSummary:
    login: int                                      # Account login number
    balance: float                                  # Account balance
    equity: float                                   # Equity (balance + floating P&L)
    user_name: str                                  # Client name
    leverage: int                                   # Account leverage (e.g., 100)
    trade_mode: Any                                 # Trade mode (demo/real/contest)
    company_name: str                               # Broker company name
    currency: str                                   # Deposit currency
    server_time: Optional[datetime]                 # Server time
    utc_timezone_shift_minutes: int                 # UTC timezone shift
    credit: float                                   # Credit facility
    margin: float                                   # Used margin
    free_margin: float                              # Free margin
    margin_level: float                             # Margin level %
    profit: float                                   # Floating P&L

# Usage
summary = await service.get_account_summary()
print(f"Balance: {summary.balance}")  # Clean attribute access
print(f"Time: {summary.server_time}")  # Already datetime object
```

**Benefits:**

- Type hints for IDE autocomplete
- Clean attribute access (no dict keys)
- Automatic __repr__ and __eq__
- Immutable with frozen=True

---

### Async Generators
Python's way to stream data asynchronously.

**Streaming methods return async generators:**
```python
# Streaming returns async generator
async for tick_data in account.on_symbol_tick(["EURUSD"]):
    tick = tick_data.symbol_tick
    print(f"Bid: {tick.bid}, Ask: {tick.ask}")
    print(f"Time: {tick.time}")

    # Can break anytime
    if some_condition:
        break

# Auto cleanup when loop exits
```

**Critical rules:**

- Use `async for` to consume data
- Generator auto-stops when you break
- No manual cleanup needed
- Can use `async with` for scoped streaming

**Example with timeout:**
```python
import asyncio

try:
    async for tick_data in account.on_symbol_tick(["EURUSD"]):
        tick = tick_data.symbol_tick
        await asyncio.wait_for(process_tick(tick), timeout=5.0)
except asyncio.TimeoutError:
    print("Processing timeout")
```

---

### ➕ Properties
Python's computed attributes that look like simple fields.

**MT5Sugar uses properties for instant access:**
```python
# Properties - no parentheses needed!
balance = await sugar.balance       # Not sugar.get_balance()
equity = await sugar.equity         # Not sugar.get_equity()
margin = await sugar.margin         # Not sugar.get_margin()
free_margin = await sugar.free_margin
margin_level = await sugar.margin_level
profit = await sugar.profit

# All are async properties
@property
async def balance(self) -> float:
    return await self.get_balance()
```

**Benefits:**

- Cleaner syntax
- Looks like attribute access
- Still async under the hood
- Better for quick scripts

---

### Context Managers
Python's pattern for automatic resource cleanup.

**MT5Sugar supports async with:**
```python
# Create full stack
account = MT5Account.create(
    user=591129415,
    password="password",
    grpc_server="mt5.mrpc.pro:443"
)

await account.connect_by_server_name(
    server_name="FxPro-MT5 Demo",
    base_chart_symbol="EURUSD"
)

service = MT5Service(account)

# Use sugar with context manager
async with MT5Sugar(service) as sugar:
    balance = await sugar.balance
    ticket = await sugar.buy_market("EURUSD", 0.01)

# Manual cleanup still needed
await account.channel.close()
```

**Why context managers?**

- Cleaner code structure
- Standard Python pattern
- Scoped resource usage

**Important: Manual channel cleanup required**

`account.channel` is the gRPC connection to MT5 terminal. You MUST call `await account.channel.close()` to:

- Close the persistent gRPC connection
- Release network resources
- Prevent connection leaks
- Avoid DEADLINE_EXCEEDED errors on exit

Without `channel.close()`, the connection stays open and may cause resource leaks or errors on program shutdown.

**Recommended pattern with proper cleanup:**

```python
account = MT5Account.create(
    user=591129415,
    password="password",
    grpc_server="mt5.mrpc.pro:443"
)

try:
    await account.connect_by_server_name(
        server_name="FxPro-MT5 Demo",
        base_chart_symbol="EURUSD"
    )

    service = MT5Service(account)
    sugar = MT5Sugar(service)

    # Work here
    balance = await sugar.balance
    ticket = await sugar.buy_market("EURUSD", 0.01)

finally:
    await account.channel.close()  # Always cleanup
```

---

## 📦 Technical Concepts

### Auto-Normalization
Automatic adjustment of trading parameters to broker requirements.

**What gets normalized:**

- **Volumes:** Rounded to broker's volume step (e.g., 0.01 lot)
- **Prices:** Rounded to symbol's tick size/digits (e.g., 5 decimal places for EURUSD)
- **Stop Loss / Take Profit:** Adjusted to symbol precision

**Where:** MT5 terminal itself handles normalization (both MT5Service and MT5Sugar benefit)

**Example:**
```python
# You pass: volume=0.0234
# Terminal normalizes to: volume=0.02 (if broker's step is 0.01)
ticket = await sugar.buy_market("EURUSD", 0.0234)
```

**Manual normalization if needed:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

# Get volume step
volume_step = await service.get_symbol_double(
    "EURUSD",
    market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_STEP
)

# Round to step
volume = 0.0234
normalized_volume = round(volume / volume_step) * volume_step
# Result: 0.02

# Get symbol digits for price normalization
digits = await service.get_symbol_integer(
    "EURUSD",
    market_info_pb2.SymbolInfoIntegerProperty.SYMBOL_DIGITS
)

# Round price to digits
price = 1.09876543
normalized_price = round(price, digits)
# Result: 1.09877 (for 5-digit broker)
```

---

### Risk-Based Volume Calculation
Calculate position size based on dollar risk rather than fixed lot size.

**Formula:** `volume = risk_amount / (stop_loss_pips * pip_value)`

**Parameters:**

- `risk_amount` - Dollar amount you're willing to risk (e.g., $50)
- `stop_loss_pips` - Distance to SL in pips (e.g., 20 pips)
- Result: Lot size that risks exactly $50 if SL hits

**Methods (MT5Sugar):**

```python
# Calculate volume for given risk
volume = await sugar.calculate_position_size("EURUSD", risk_percent=2.0, sl_pips=50)
# 2% risk with 50 pip SL

# Buy with risk-based calculation
lot_size = await sugar.calculate_position_size("EURUSD", 2.0, 50)
ticket = await sugar.buy_market_with_pips("EURUSD", lot_size, sl_pips=50, tp_pips=100)
```

**Use case:** Consistent risk management across all trades.

---

### Points vs Pips
**Point:** Smallest price movement for a symbol (1 tick).

**Pip:** Traditional forex unit (0.0001 for most pairs).

**Relationship:**

- **5-digit brokers:** 1 pip = 10 points (EURUSD: 1.10000 to 1.10010 = 1 pip)
- **3-digit brokers:** 1 pip = 1 point (USDJPY: 110.00 to 110.01 = 1 pip)

**In PyMT5:** All APIs use **points** for consistency.

**Conversion:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

# Get point size
point = await service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_POINT)
# point = 0.00001 for 5-digit broker

# Convert pips to points
pips = 20
points = pips * 10  # For 5-digit pairs
```

**Why points?** Universal across all instruments (forex, metals, indices, crypto).

---

### Pip-Based Methods
Convenience methods that work with pips instead of points for forex traders.

**Methods (MT5Sugar):**

```python
# Market orders with SL/TP in pips
ticket = await sugar.buy_market_with_sltp("EURUSD", 0.01, sl_pips=20, tp_pips=30)
# Or use alias:
ticket = await sugar.buy_market_with_pips("EURUSD", 0.01, sl_pips=20, tp_pips=30)

ticket = await sugar.sell_market_with_sltp("GBPUSD", 0.01, sl_pips=20, tp_pips=30)
# Or use alias:
ticket = await sugar.sell_market_with_pips("GBPUSD", 0.01, sl_pips=20, tp_pips=30)

# Pending orders with SL/TP in pips (requires absolute price)
current_ask = await sugar.get_ask("EURUSD")
ticket = await sugar.buy_limit_with_sltp("EURUSD", 0.01, price=current_ask - 0.0020, sl_pips=15, tp_pips=30)

current_bid = await sugar.get_bid("EURUSD")
ticket = await sugar.sell_limit_with_sltp("EURUSD", 0.01, price=current_bid + 0.0020, sl_pips=15, tp_pips=30)
```

**Benefits:**

- SL/TP specified in pips (familiar for forex traders)
- Automatic conversion to prices
- Fewer errors than manual calculations

---

### Trailing Stop
Dynamic Stop Loss that follows price in profit direction.

**How it works:**

1. Position opens with initial SL
2. When profit reaches threshold (e.g., +40 pips)
3. SL moves to breakeven or better
4. SL continues to follow price at fixed distance
5. Locks in profit as price moves favorably

**Implementation example:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

async def trailing_stop_logic(sugar, ticket, symbol):
    # Get position to check profit
    position = await sugar.get_position_by_ticket(ticket)
    if not position:
        return

    current_profit = position.profit
    trailing_threshold = 40.0  # dollars
    trailing_distance_pips = 20  # 20 pips

    point = await sugar.service.get_symbol_double(
        symbol, market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_POINT
    )
    trailing_distance = trailing_distance_pips * 10 * point  # For 5-digit

    if current_profit >= trailing_threshold:
        current_price = await sugar.get_bid(symbol)
        new_sl = current_price - trailing_distance

        # Only move SL up (for BUY position)
        if new_sl > position.sl:
            await sugar.modify_position_sltp(ticket, sl=new_sl, tp=position.tp)
```

**Use case:** Locking in profit on trending markets.

---

### Hedging
Opening opposite position to lock in current profit/loss level.

**How it works:**

1. Main position open (e.g., BUY EURUSD 0.1 lot)
2. Price moves against you (-50 pips)
3. Hedge triggered: SELL EURUSD 0.1 lot
4. Net position = 0 (loss locked at -50 pips)

**Purpose:**

- Lock losses instead of closing at stop-loss
- Protect position during volatility/news
- Wait for better opportunity to exit

**Implementation:**
```python
# Main position
buy_ticket = await sugar.buy_market("EURUSD", 0.1)

# ... price moves against you ...

# Hedge
sell_ticket = await sugar.sell_market("EURUSD", 0.1)
# Net position = 0, loss locked
```

**WARNING:** Not all brokers/regulations allow hedging. US brokers typically do not support hedging.

---

### Pending Order
Order that executes automatically when price reaches specified level.

**Types:**

- **BUY LIMIT:** Buy at price BELOW current (expect pullback, then up)
- **SELL LIMIT:** Sell at price ABOVE current (expect rally, then down)
- **BUY STOP:** Buy at price ABOVE current (breakout up)
- **SELL STOP:** Sell at price BELOW current (breakout down)

**Methods (MT5Sugar):**
```python
# Buy limit without SL/TP
ticket = await sugar.buy_limit("EURUSD", 0.01, price=1.09950)

# Buy limit with SL/TP
ticket = await sugar.buy_limit_with_sltp("EURUSD", 0.01, price=1.09950, sl=1.09900, tp=1.10050)

# Sell stop without SL/TP
ticket = await sugar.sell_stop("EURUSD", 0.01, price=1.09950)

# Sell stop with SL/TP (no dedicated method, use sell_stop + modify)
ticket = await sugar.sell_stop("EURUSD", 0.01, price=1.09950)
await sugar.modify_position_sltp(ticket, sl=1.10000, tp=1.09900)
```

---

## 🔌 gRPC and Protocol Terms

### gRPC
High-performance RPC (Remote Procedure Call) framework using HTTP/2.

**In PyMT5:**

- MT5Account tier sends gRPC requests to MT5 terminal
- Terminal runs gRPC server (configured via gateway)
- Request/Response pattern for all operations
- Async/await for non-blocking calls

**Connection setup:**
```python
account = MT5Account.create(
    user=591129415,
    password="password",
    grpc_server="mt5.mrpc.pro:443"
)

await account.connect_by_server_name(
    server_name="FxPro-MT5 Demo",
    base_chart_symbol="EURUSD"
)
```

**Documentation:** [gRPC Python](https://grpc.io/docs/languages/python/)

---

### Protobuf
Protocol Buffers - Google's language-neutral data serialization format.

**In PyMT5:**

- All MT5Account methods use protobuf Request/Response
- Generated from .proto files
- Efficient binary serialization
- Type-safe message structures

**Example:**

```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

# MT5Account level - already unpacks protobuf response internally
balance = await account.account_info_double(
    account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
)
# Returns: float (e.g., 10000.0)
# NOTE: The method internally extracts res.data.requested_value before returning

# MT5Service level - same result, just different method name
balance = await service.get_account_double(
    account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
)
# Returns: float (e.g., 10000.0)
```

**Both MT5Account and MT5Service return clean Python types (float, int, str), not protobuf objects.**

---

### ℹ️ Return Codes
Protobuf return codes indicating operation success/failure.

**Common codes:**

- **10009** = Success (TRADE_RETCODE_DONE)
- **10008** = Pending order placed (TRADE_RETCODE_PLACED)
- **10004** = Requote
- **10006** = Request rejected
- **10013** = Invalid request
- **10014** = Invalid volume
- **10015** = Invalid price
- **10016** = Invalid stops
- **10018** = Market closed
- **10019** = Not enough money
- **10031** = No connection to trade server

**Always check returned_code in trading operations.**

**Example:**

```python
result = await account.order_send(request)

if result.returned_code == 10009:  # TRADE_RETCODE_DONE
    print(f"Trade successful! Ticket: {result.order}")
elif result.returned_code == 10019:
    print("Not enough money")
else:
    print(f"Trade failed: code {result.returned_code}")
```

**Documentation:** [Return Codes Reference](RETURN_CODES_REFERENCE.md)

---

### 📡 Streaming Pattern
Real-time data streams using async generators.

**Streaming methods:**
```python
# Stream tick data
async for tick_data in account.on_symbol_tick(["EURUSD"]):
    if tick_data.symbol_tick:
        tick = tick_data.symbol_tick
        print(f"Bid: {tick.bid}, Ask: {tick.ask}")
    if should_stop:
        break  # Auto cleanup

# Stream trade events
async for trade_data in account.on_trade():
    print(f"Type: {trade_data.type}")
    if trade_data.event_data:
        print(f"New orders: {len(trade_data.event_data.new_orders)}")

# Stream position profit (poll every 500ms)
async for profit_data in account.on_position_profit(interval_ms=500):
    for pos in profit_data.updated_positions:
        print(f"Ticket {pos.ticket}: ${pos.profit}")
```

**Critical rules:**

- Use `async for` to consume stream
- Break to stop stream (auto cleanup)
- No manual cleanup needed
- Can use asyncio.timeout for time limits (Python 3.11+)

**With timeout:**
```python
import asyncio

# Python 3.11+
async with asyncio.timeout(60):  # 60 seconds max
    async for tick_data in account.on_symbol_tick(["EURUSD"]):
        tick = tick_data.symbol_tick
        process(tick)

# Python 3.10 and earlier - use asyncio.wait_for instead
try:
    await asyncio.wait_for(stream_processing(), timeout=60)
except asyncio.TimeoutError:
    pass
```

**Documentation:** [gRPC Stream Management](GRPC_STREAM_MANAGEMENT.md)

---

## 🏛️ Trading Terms

### Basic Trading Terms

Core trading concepts that every trader must understand before working with MT5.

| Term | Description | Example / Details |
|------|-------------|-------------------|
| **Bid** | Price at which broker **buys** from you (you **sell** at Bid) | EURUSD Bid: 1.10000 |
| **Ask** | Price at which broker **sells** to you (you **buy** at Ask) | EURUSD Ask: 1.10002 |
| **Spread** | Difference between Ask and Bid (broker's commission) | Ask 1.10002 - Bid 1.10000 = 2 pips spread |
| **Long / Buy** | Opening a BUY position (profit when price goes up) | Buy EURUSD at 1.10000, close at 1.10050 = +50 pips profit |
| **Short / Sell** | Opening a SELL position (profit when price goes down) | Sell EURUSD at 1.10000, close at 1.09950 = +50 pips profit |
| **Position** | Open trade (BUY or SELL) that can result in profit or loss | BUY 0.1 lot EURUSD at 1.10000 (currently in profit +$50) |
| **Order** | Command to open a position | Market Order (immediate), Pending Order (at specific price) |
| **Market Order** | Order that executes immediately at current price | BUY EURUSD at current Ask price |
| **Pending Order** | Order that triggers automatically when price reaches level | BUY LIMIT at 1.09950 (when price drops to that level) |
| **Lot / Volume** | Position size (1 lot = 100,000 units of base currency) | 0.01 lot = 1,000 units (micro lot) |
| **Stop Loss (SL)** | Price level for automatic loss-limiting exit | SL at 1.09950 limits loss to 50 pips |
| **Take Profit (TP)** | Price level for automatic profit-taking exit | TP at 1.10050 locks in 50 pips profit |
| **Pip** | Standard unit of price movement (0.0001 for most forex) | EURUSD: 1.10000 to 1.10001 = 1 pip |
| **Point** | Smallest price movement (1 tick) | For 5-digit broker: 1 pip = 10 points |
| **Leverage** | Borrowed capital from broker (e.g., 1:100) | With 1:100, you control $100,000 with $1,000 margin |
| **Margin** | Funds locked as collateral for open positions | Open 1 lot EURUSD with 1:100 leverage = $1,000 margin |
| **Free Margin** | Available funds for opening new positions | Balance $10,000 - Margin $1,000 = Free Margin $9,000 |
| **Balance** | Account funds without considering open positions | Initial deposit + closed trades profit/loss |
| **Equity** | Current account value (Balance +/- floating profit/loss) | Balance $10,000 + Floating profit $500 = Equity $10,500 |
| **Floating P/L** | Unrealized profit/loss of open positions | Position currently in +$50 profit (not yet closed) |
| **Margin Level** | Ratio of Equity to Margin (%) | Equity $10,500 / Margin $1,000 = 1050% |
| **Margin Call** | Warning when Margin Level drops below threshold | Broker warns at 100% Margin Level |
| **Stop Out** | Forced closure of positions when Margin Level critically low | Broker closes positions at 50% Margin Level |
| **Drawdown** | Decline from peak balance/equity | Peak $11,000 to Current $10,000 = $1,000 drawdown (9.09%) |
| **Slippage** | Difference between expected and executed price | Requested 1.10000, executed at 1.10003 = 3 pips slippage |

**Critical for API usage:**

```python
# Get prices
bid = await sugar.get_bid("EURUSD")
ask = await sugar.get_ask("EURUSD")

# Get account state
balance = await sugar.balance
equity = await sugar.equity
margin = await sugar.margin
free_margin = await sugar.free_margin

# Open positions
buy_ticket = await sugar.buy_market("EURUSD", 0.01)
sell_ticket = await sugar.sell_market("EURUSD", 0.01)

# Close positions
await sugar.close_position(buy_ticket)

# Modify SL/TP
await sugar.modify_position_sltp(buy_ticket, sl=1.09950, tp=1.10050)
```

---

### Risk Amount
Dollar amount you're willing to risk if Stop Loss hits.

**Example:** $50 risk per trade means if SL hits, you lose exactly $50.

**Used in:**

```python
# Calculate volume for 2% risk with 50 pip SL
volume = await sugar.calculate_position_size("EURUSD", risk_percent=2.0, sl_pips=50)

# Open with risk-based calculation
lot_size = await sugar.calculate_position_size("EURUSD", 2.0, 50)
ticket = await sugar.buy_market("EURUSD", lot_size, sl_pips=50, tp_pips=100)
# Risk exactly 2% of balance
```

---

### Breakeven
Moving Stop Loss to entry price to eliminate risk.

**Example:**

- Entry: BUY at 1.10000
- Price rises to 1.10050 (+50 pips profit)
- Move SL from 1.09950 to 1.10000 (breakeven)
- Now risk-free: worst case = breakeven

**Implementation:**
```python
position = await sugar.get_position_by_ticket(ticket)
entry_price = position.price_open
breakeven_threshold = 40.0  # pips

current_profit = position.profit
if current_profit >= breakeven_threshold:
    await sugar.modify_position_sltp(ticket, sl=entry_price, tp=position.tp)
```

---

### Grid Trading
Strategy placing multiple pending orders at equal intervals above and below current price.

**How it works:**

1. Place Buy Limit orders below current price (e.g., every 20 pips)
2. Place Sell Limit orders above current price (e.g., every 20 pips)
3. As price oscillates, orders trigger and close at TP
4. Works best in ranging markets

**Example:**
```
Price: 1.10000
Buy Limits:  1.09980 (-20 pips), 1.09960 (-40 pips), 1.09940 (-60 pips)
Sell Limits: 1.10020 (+20 pips), 1.10040 (+40 pips), 1.10060 (+60 pips)
```

**Implementation:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

grid_step_pips = 20
levels = 5

ask = await sugar.get_ask("EURUSD")
bid = await sugar.get_bid("EURUSD")
point = await sugar.service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_POINT)

for i in range(1, levels + 1):
    offset = i * grid_step_pips * 10 * point  # Convert pips to points

    # Buy Limit below Ask
    buy_price = ask - offset
    await sugar.buy_limit("EURUSD", 0.01, price=buy_price, sl=buy_price - 15*10*point, tp=buy_price + 30*10*point)

    # Sell Limit above Bid
    sell_price = bid + offset
    await sugar.sell_limit("EURUSD", 0.01, price=sell_price, sl=sell_price + 15*10*point, tp=sell_price - 30*10*point)
```

**WARNING:** High volatility can trigger many orders, increasing exposure.

---

### Scalping
Fast trading strategy with small profits (5-25 pips) and tight stops (10-20 pips).

**Characteristics:**

- Very short hold times (seconds-minutes)
- High win rate, small profit per trade
- Risk:Reward typically 1:1 to 1:2
- Requires low spreads

**Implementation:**
```python
# Scalp with 10 pip SL, 15 pip TP
ticket = await sugar.buy_market_with_pips("EURUSD", 0.01, sl_pips=10, tp_pips=15)
```

---

### News Trading
Placing orders on both sides of price before major news events.

**How it works:**

1. Before news: Place Buy Stop above + Sell Stop below
2. News releases: Price breaks in one direction
3. One order triggers, cancel the other
4. Capture volatility spike

**Example:**
```
Current price: 1.10000
Buy Stop:  1.10030 (+30 pips)
Sell Stop: 1.09970 (-30 pips)
News -> Price spikes to 1.10050 -> Buy Stop triggers -> Cancel Sell Stop
```

**Implementation:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

ask = await sugar.get_ask("EURUSD")
bid = await sugar.get_bid("EURUSD")
point = await sugar.service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_POINT)

offset = 30 * 10 * point  # 30 pips

buy_ticket = await sugar.buy_stop("EURUSD", 0.01, price=ask + offset)
sell_ticket = await sugar.sell_stop("EURUSD", 0.01, price=bid - offset)

# ... wait for news ...

# NOTE: MT5Sugar doesn't have delete_order method
# To cancel pending orders, use MT5Service or MT5Account level methods
```

**WARNING:** Slippage during news can trigger both orders.

---

### Volume Limits
Broker restrictions on position size.

**Get via:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

min_vol = await service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_MIN)
max_vol = await service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_MAX)
step_vol = await service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_STEP)
```

**Used for:** Volume validation.

**Validation:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

async def validate_volume(service, symbol, volume):
    min_vol = await service.get_symbol_double(symbol, market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_MIN)
    max_vol = await service.get_symbol_double(symbol, market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_MAX)
    step_vol = await service.get_symbol_double(symbol, market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_STEP)

    if volume < min_vol:
        volume = min_vol
    if volume > max_vol:
        volume = max_vol

    # Round to step
    volume = round(volume / step_vol) * step_vol
    return volume
```

---

## 🔑 Configuration Terms

### Environment Variables
Configuration via environment variables or .env file.

**Variables:**

```bash
# Required
MT5_USER=591129415
MT5_PASSWORD="YourPassword"
MT5_SERVER="FxPro-MT5 Demo"
MT5_GRPC_HOST="mt5.mrpc.pro:443"

# Optional (have defaults)
MT5_SYMBOL="EURUSD"
MT5_VOLUME=0.01
```

**Set (Windows PowerShell):**
```powershell
$env:MT5_USER="591129415"
$env:MT5_PASSWORD="YourPassword"
```

**Set (Linux/Mac):**
```bash
export MT5_USER=591129415
export MT5_PASSWORD="YourPassword"
```

**Load in Python:**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

user = int(os.getenv("MT5_USER"))
password = os.getenv("MT5_PASSWORD")
server = os.getenv("MT5_SERVER")
grpc_host = os.getenv("MT5_GRPC_HOST")
```

---

### .env File
Configuration file for environment variables.

**Location:** Project root (`.env`)

**Format:**
```env
MT5_USER=591129415
MT5_PASSWORD=YourPassword
MT5_SERVER=FxPro-MT5 Demo
MT5_GRPC_HOST=mt5.mrpc.pro:443
MT5_SYMBOL=EURUSD
MT5_VOLUME=0.01
```

**Usage:**
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env into environment

# Access via os.getenv()
user = int(os.getenv("MT5_USER"))
password = os.getenv("MT5_PASSWORD")
```

**WARNING:** Never commit .env to git (add to .gitignore)

---

## Cross-Component Terms

### Batch Operations
Executing action across multiple positions/orders at once.

**Methods (MT5Sugar):**
```python
# Close all positions
count = await sugar.close_all_positions()          # All positions
count = await sugar.close_all_positions("EURUSD")  # By symbol only
```

**Note:** To delete pending orders, use MT5Service or MT5Account level methods.

**Use case:** Emergency exits, end-of-session cleanup, strategy resets.

---

### 📝 History Queries
Retrieving past orders and positions for analysis.

**Methods (MT5Account):**
```python
from datetime import datetime, timedelta
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as account_helper_pb2

# Get order history
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

history = await account.order_history(
    from_dt=start_date,
    to_dt=end_date,
    sort_mode=account_helper_pb2.BMT5_SORT_BY_OPEN_TIME_ASC,
    page_number=0,
    items_per_page=100
)

# Get position history
positions = await account.positions_history(
    sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
    open_from=start_date,
    open_to=end_date,
    page=0,
    size=100
)
```

**Use case:** Performance analysis, trade logs, strategy validation.

---

### Educational Project

PyMT5 examples and helpers are educational materials and API demonstrations, NOT production trading systems.

**Implications:**

- Study code and patterns (YES)
- Modify for your needs (YES)
- Test on demo accounts (YES)
- Use as templates for building your strategies (YES)
- Don't use as-is with real money (NO)
- Don't expect production-grade risk management (NO)
- Don't expect proper error handling for all edge cases (NO)

**Remember:** These are educational examples, not battle-tested production systems.

---

## Python-Specific Patterns

### Exception Handling
Python's error handling mechanism for API errors.

**Custom exceptions:**
```python
from MetaRpcMT5 import ConnectExceptionMT5, ApiExceptionMT5

try:
    await account.connect_by_server_name(
        server_name="FxPro-MT5 Demo",
        base_chart_symbol="EURUSD"
    )
except ConnectExceptionMT5 as e:
    print(f"Connection failed: {e}")
except ApiExceptionMT5 as e:
    print(f"API error: {e}")
```

**Trading operation errors:**
```python
try:
    ticket = await sugar.buy_market("EURUSD", 0.01)
    print(f"Position opened: ticket {ticket}")
except RuntimeError as e:
    # MT5Sugar raises RuntimeError if returned_code != 10009
    print(f"Trade failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

### Type Hints
Python's optional static typing for better IDE support.

**All PyMT5 code uses type hints:**
```python
from typing import Optional, List
from datetime import datetime

async def get_balance(self) -> float:
    """Get account balance."""
    from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2
    return await self.service.get_account_double(
        account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
    )

async def buy_market(
    self,
    symbol: str,
    volume: float,
    sl: Optional[float] = None,
    tp: Optional[float] = None
) -> int:
    """Open BUY position at market price.

    Returns:
        int: Ticket number
    """
    pass
```

**Benefits:**

- IDE autocomplete
- Static type checking (mypy)
- Better documentation
- Catch errors before runtime

---

### 🧱 Enums
Python's enumeration types for named constants.

**PyMT5 uses enums instead of magic numbers:**
```python
# MT5Sugar enums
from pymt5.mt5_sugar import OrderType, Period

# Protobuf enums
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

# Instead of magic numbers
order_type = OrderType.BUY  # Not 0
period = Period.TODAY       # Not 0

# Symbol properties
bid = await service.get_symbol_double(
    "EURUSD",
    market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_BID  # Not 1
)

# Account properties
balance = await service.get_account_double(
    account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE  # Not 0
)
```

**Documentation:** [Enums Usage Reference](ENUMS_USAGE_REFERENCE.md)

---

## See Also

- **[MT5Account Master Overview](../MT5Account/MT5Account.Master.Overview.md)** - Complete low-level API reference
- **[MT5Service API Overview](../MT5Service/MT5Service.Overview.md)** - Mid-level wrappers API
- **[MT5Sugar API Reference](../API_Reference/MT5Sugar.md)** - High-level Sugar API
- **[gRPC Stream Management](GRPC_STREAM_MANAGEMENT.md)** - Guide to streaming subscriptions
- **[Return Codes Reference](RETURN_CODES_REFERENCE.md)** - Complete return codes reference
- **[User Code Sandbox Guide](USERCODE_SANDBOX_GUIDE.md)** - How to write custom code
- **[Your First Project](Your_First_Project.md)** - Setup and quick start guide
- **[Enums Usage Reference](ENUMS_USAGE_REFERENCE.md)** - All available enums
- **[Protobuf Inspector Guide](PROTOBUF_INSPECTOR_GUIDE.md)** - Explore protobuf types

---

"Trade safely, code cleanly, and may your async functions always await gracefully."
