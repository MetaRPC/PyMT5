# Get Symbol Integer Property

> **Request:** retrieve integer-type property value for a symbol.

**API Information:**

* **Low-level API:** `MT5Account.symbol_info_integer(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolInfoInteger` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoInteger(SymbolInfoIntegerRequest) -> SymbolInfoIntegerReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolInfoInteger(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Retrieve a single integer-type property value for a symbol (DIGITS, SPREAD, TRADE_MODE, etc.).
* **Why you need it.** Get specific integer symbol properties without fetching all symbol data.
* **When to use.** Use `symbol_params_many()` for multiple properties. Use this method for single property queries.

---

## 🎯 Purpose

Use it to query specific integer symbol properties:

* Get symbol digits (decimal places)
* Check current spread in points
* Query trading modes and execution modes
* Get timestamps (start time, expiration)
* Check volume parameters
* Retrieve trade stops and freeze levels
* Query swap rollover settings
* Monitor order and filling modes

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_info_integer - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_integer_HOW.md)**

---

## Method Signature

```python
async def symbol_info_integer(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoIntegerProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoIntegerData
```

**Request message:**

```protobuf
message SymbolInfoIntegerRequest {
  string symbol = 1;
  SymbolInfoIntegerProperty type = 2;
}
```

**Reply message:**

```protobuf
message SymbolInfoIntegerReply {
  oneof response {
    SymbolInfoIntegerData data = 1;
    Error error = 2;
  }
}

message SymbolInfoIntegerData {
  int64 value = 1;
}
```

---

## 🔽 Input

| Parameter   | Type                              | Description                               |
| ----------- | --------------------------------- | ----------------------------------------- |
| `symbol`    | `str` (required)                  | Symbol name                               |
| `property`  | `SymbolInfoIntegerProperty` (enum) | Property to retrieve (DIGITS, SPREAD, etc.) |
| `deadline`    | `datetime` (optional)             | Deadline for the gRPC call (UTC datetime) |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation |

---

## ⬆️ Output

| Field   | Type    | Python Type | Description                        |
| ------- | ------- | ----------- | ---------------------------------- |
| `value` | `int64` | `int`       | The integer value of the property  |

**Return value:** The method returns `SymbolInfoIntegerData` object with `value` field containing the requested property.

---

## 🧱 Related enums (from proto)

> **Note:** In Python code, use the full enum path from the market_info module.

### `SymbolInfoIntegerProperty`

Defined in `mt5-term-api-market-info.proto`.

### Symbol Status & Display

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_EXIST` | 6 | Symbol exists flag |
| `SYMBOL_SELECT` | 7 | Symbol selected in MarketWatch |
| `SYMBOL_VISIBLE` | 8 | Symbol visible in MarketWatch |
| `SYMBOL_SUBSCRIPTION_DELAY` | 0 | Subscription delay |
| `SYMBOL_CUSTOM` | 3 | Custom symbol flag |
| `SYMBOL_BACKGROUND_COLOR` | 4 | Background color |
| `SYMBOL_CHART_MODE` | 5 | Chart mode |

### Classification

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_SECTOR` | 1 | Sector |
| `SYMBOL_INDUSTRY` | 2 | Industry |

### Time & Precision

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_TIME` | 15 | Time of last quote |
| `SYMBOL_TIME_MSC` | 16 | Time of last quote in milliseconds |
| `SYMBOL_DIGITS` | 17 | Digits after decimal point |
| `SYMBOL_START_TIME` | 23 | Symbol start time |
| `SYMBOL_EXPIRATION_TIME` | 24 | Symbol expiration time |

### Spread & Volume

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_SPREAD` | 19 | Spread value in points |
| `SYMBOL_SPREAD_FLOAT` | 18 | Floating spread flag |
| `SYMBOL_VOLUME` | 12 | Last deal volume |
| `SYMBOL_VOLUMEHIGH` | 13 | Maximum volume for the day |
| `SYMBOL_VOLUMELOW` | 14 | Minimum volume for the day |
| `SYMBOL_TICKS_BOOKDEPTH` | 20 | Maximal number of requests shown in DOM |

### Session Data

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_SESSION_DEALS` | 9 | Number of deals in current session |
| `SYMBOL_SESSION_BUY_ORDERS` | 10 | Number of buy orders |
| `SYMBOL_SESSION_SELL_ORDERS` | 11 | Number of sell orders |

### Trading Properties

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_TRADE_CALC_MODE` | 21 | Contract price calculation mode |
| `SYMBOL_TRADE_MODE` | 22 | Order execution type |
| `SYMBOL_TRADE_STOPS_LEVEL` | 25 | Minimal distance of stops |
| `SYMBOL_TRADE_FREEZE_LEVEL` | 26 | Distance to freeze trading operations |
| `SYMBOL_TRADE_EXEMODE` | 27 | Deal execution mode |

### Order & Expiration Modes

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_EXPIRATION_MODE` | 31 | Flags of allowed expiration modes |
| `SYMBOL_FILLING_MODE` | 32 | Flags of allowed filling modes |
| `SYMBOL_ORDER_MODE` | 33 | Flags of allowed order types |
| `SYMBOL_ORDER_GTC_MODE` | 34 | Expiration of pending orders GTC mode |

### Swap & Margin

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_SWAP_MODE` | 28 | Swap calculation model |
| `SYMBOL_SWAP_ROLLOVER3DAYS` | 29 | Day of week to charge 3 days swap |
| `SYMBOL_MARGIN_HEDGED_USE_LEG` | 30 | Calculating hedged margin using larger leg |

### Options

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_OPTION_MODE` | 35 | Option type |
| `SYMBOL_OPTION_RIGHT` | 36 | Option right (Call/Put) |

**Usage in Python:**
```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get symbol digits
digits_data = await account.symbol_info_integer("EURUSD", market_info_pb2.SYMBOL_DIGITS)
print(f"Digits: {digits_data.value}")

# Check spread
spread_data = await account.symbol_info_integer("EURUSD", market_info_pb2.SYMBOL_SPREAD)
print(f"Spread: {spread_data.value} points")
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Access the value:** The returned `SymbolInfoIntegerData` object has a `.value` field containing the integer.
* **Trading modes:** Mode properties return integer flags - refer to MT5 documentation for flag meanings.
* **Timestamps:** TIME and TIME_MSC properties return Unix timestamps (seconds or milliseconds).
* **Spread units:** SYMBOL_SPREAD returns spread in points, not pips.
* **Boolean flags:** Properties like SYMBOL_EXIST, SYMBOL_SELECT, SYMBOL_VISIBLE return 0 or 1.

---

## 🔗 Usage Examples

### 1) Get symbol digits and spread

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get digits (decimal places)
result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DIGITS
)
print(f"Digits: {result.value}")  # Output: Digits: 5

# Get spread in points
spread_result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_SPREAD
)
print(f"Spread: {spread_result.value} points")  # Output: Spread: 10 points
```

### 2) Check if symbol is selected in MarketWatch

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="GBPUSD",
    property=market_info_pb2.SYMBOL_SELECT
)

if result.value:
    print("Symbol is in MarketWatch")
else:
    print("Symbol is NOT in MarketWatch")
```

### 3) Get trade mode

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_TRADE_MODE
)

# Map to trade mode names
trade_modes = {
    0: "DISABLED",
    1: "LONG_ONLY",
    2: "SHORT_ONLY",
    3: "CLOSE_ONLY",
    4: "FULL"
}

mode_name = trade_modes.get(result.value, "UNKNOWN")
print(f"Trade mode: {mode_name} (value: {result.value})")
```

### 4) Get last quote timestamp

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime

# Get timestamp in seconds
result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TIME
)

# Convert to datetime
quote_time = datetime.utcfromtimestamp(result.value)
print(f"Last quote time: {quote_time}")

# Or get milliseconds timestamp
result_msc = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TIME_MSC
)
quote_time_msc = datetime.utcfromtimestamp(result_msc.value / 1000)
print(f"Last quote time (ms precision): {quote_time_msc}")
```

### 5) Check stops level before placing order

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TRADE_STOPS_LEVEL
)

stops_level = result.value
print(f"Minimum stops level: {stops_level} points")
print(f"SL/TP must be at least {stops_level} points away from current price")
```

### 6) Get freeze level

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TRADE_FREEZE_LEVEL
)

freeze_level = result.value
if freeze_level > 0:
    print(f"Freeze level: {freeze_level} points")
    print(f"Orders cannot be modified when price is within {freeze_level} points")
else:
    print("No freeze level set")
```

### 7) Check allowed order types

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="BTCUSD",
    property=market_info_pb2.SYMBOL_ORDER_MODE
)

# ORDER_MODE is a bitfield
order_flags = result.value

# Check specific order types (example flag values)
if order_flags & 1:
    print("Market orders allowed")
if order_flags & 2:
    print("Limit orders allowed")
if order_flags & 4:
    print("Stop orders allowed")
if order_flags & 8:
    print("Stop Limit orders allowed")
```

---

## 📚 See also

* [symbol_info_double](./symbol_info_double.md) - Get double properties
* [symbol_info_string](./symbol_info_string.md) - Get string properties
* [symbol_params_many](./symbol_params_many.md) - Get all symbol parameters at once
