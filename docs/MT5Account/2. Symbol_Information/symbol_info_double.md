# Get Symbol Double Property

> **Request:** retrieve double-type property value for a symbol.

**API Information:**

* **Low-level API:** `MT5Account.symbol_info_double(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolInfoDouble` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoDouble(SymbolInfoDoubleRequest) -> SymbolInfoDoubleReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolInfoDouble(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Retrieve a single double-type property value for a symbol (BID, ASK, VOLUME, etc.).
* **Why you need it.** Get specific numeric symbol properties without fetching all symbol data.
* **When to use.** Use `symbol_params_many()` for multiple properties. Use this method for single property queries.

---

## 🎯 Purpose

Use it to query specific double symbol properties:

* Get current BID/ASK prices
* Check trading volumes
* Retrieve margin requirements
* Get swap rates
* Query tick values and contract sizes
* Monitor session prices and limits

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_info_double - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_double_HOW.md)**

---

## Method Signature

```python
async def symbol_info_double(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoDoubleProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
)
```

**Request message:**

```protobuf
message SymbolInfoDoubleRequest {
  string symbol = 1;
  SymbolInfoDoubleProperty type = 2;
}
```

**Reply message:**

```protobuf
message SymbolInfoDoubleReply {
  oneof response {
    SymbolInfoDoubleData data = 1;
    Error error = 2;
  }
}

message SymbolInfoDoubleData {
  double value = 1;
}
```

---

## 🔽 Input

| Parameter   | Type                            | Description                          |
| ----------- | ------------------------------- | ------------------------------------ |
| `symbol`    | `str` (required)                | Symbol name                          |
| `property`  | `SymbolInfoDoubleProperty` (enum) | Property to retrieve (BID, ASK, etc.) |
| `deadline`    | `datetime` (optional)   | Deadline for the gRPC call (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                    |

---

## ⬆️ Output - `SymbolInfoDoubleData`

| Field   | Type     | Python Type | Description                          |
| ------- | -------- | ----------- | ------------------------------------ |
| `value` | `double` | `float`     | The value of the requested property  |

**Return value:** The method returns `SymbolInfoDoubleData` object. Access the numeric value via the `.value` attribute.

## 🧱 Related enums (from proto)

> **Note:** In Python code, use the full enum path from the market_info module.

### `SymbolInfoDoubleProperty`

Defined in `mt5-term-api-market-info.proto`.

### Price Properties

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_BID` | 0 | Current Bid price |
| `SYMBOL_BIDHIGH` | 1 | Maximal Bid for the day |
| `SYMBOL_BIDLOW` | 2 | Minimal Bid for the day |
| `SYMBOL_ASK` | 3 | Current Ask price |
| `SYMBOL_ASKHIGH` | 4 | Maximal Ask for the day |
| `SYMBOL_ASKLOW` | 5 | Minimal Ask for the day |
| `SYMBOL_LAST` | 6 | Last deal price |
| `SYMBOL_LASTHIGH` | 7 | Maximal Last for the day |
| `SYMBOL_LASTLOW` | 8 | Minimal Last for the day |

### Volume Properties

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_VOLUME_REAL` | 9 | Real volume of the day |
| `SYMBOL_VOLUMEHIGH_REAL` | 10 | Maximum real volume of the day |
| `SYMBOL_VOLUMELOW_REAL` | 11 | Minimum real volume of the day |
| `SYMBOL_VOLUME_MIN` | 22 | Minimal volume for a deal |
| `SYMBOL_VOLUME_MAX` | 23 | Maximal volume for a deal |
| `SYMBOL_VOLUME_STEP` | 24 | Minimal volume change step |
| `SYMBOL_VOLUME_LIMIT` | 25 | Maximum allowed aggregate volume |

### Trading Properties

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_POINT` | 13 | Symbol point value |
| `SYMBOL_TRADE_TICK_VALUE` | 14 | Calculated tick price for position |
| `SYMBOL_TRADE_TICK_VALUE_PROFIT` | 15 | Calculated tick price for profit |
| `SYMBOL_TRADE_TICK_VALUE_LOSS` | 16 | Calculated tick price for loss |
| `SYMBOL_TRADE_TICK_SIZE` | 17 | Minimal price change |
| `SYMBOL_TRADE_CONTRACT_SIZE` | 18 | Trade contract size |
| `SYMBOL_TRADE_ACCRUED_INTEREST` | 19 | Accrued interest |
| `SYMBOL_TRADE_FACE_VALUE` | 20 | Face value |
| `SYMBOL_TRADE_LIQUIDITY_RATE` | 21 | Liquidity rate |

### Swap Rates

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_SWAP_LONG` | 26 | Long swap value |
| `SYMBOL_SWAP_SHORT` | 27 | Short swap value |
| `SYMBOL_SWAP_SUNDAY` | 28 | Swap value for Sunday |
| `SYMBOL_SWAP_MONDAY` | 29 | Swap value for Monday |
| `SYMBOL_SWAP_TUESDAY` | 30 | Swap value for Tuesday |
| `SYMBOL_SWAP_WEDNESDAY` | 31 | Swap value for Wednesday |
| `SYMBOL_SWAP_THURSDAY` | 32 | Swap value for Thursday |
| `SYMBOL_SWAP_FRIDAY` | 33 | Swap value for Friday |
| `SYMBOL_SWAP_SATURDAY` | 34 | Swap value for Saturday |

### Margin Requirements

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_MARGIN_INITIAL` | 35 | Initial margin |
| `SYMBOL_MARGIN_MAINTENANCE` | 36 | Maintenance margin |
| `SYMBOL_MARGIN_HEDGED` | 48 | Hedged margin |

### Session Properties

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_SESSION_VOLUME` | 37 | Summary volume of the current session |
| `SYMBOL_SESSION_TURNOVER` | 38 | Summary turnover of the current session |
| `SYMBOL_SESSION_INTEREST` | 39 | Summary open interest |
| `SYMBOL_SESSION_BUY_ORDERS_VOLUME` | 40 | Current volume of buy orders |
| `SYMBOL_SESSION_SELL_ORDERS_VOLUME` | 41 | Current volume of sell orders |
| `SYMBOL_SESSION_OPEN` | 42 | Open price of the current session |
| `SYMBOL_SESSION_CLOSE` | 43 | Close price of the current session |
| `SYMBOL_SESSION_AW` | 44 | Average weighted price |
| `SYMBOL_SESSION_PRICE_SETTLEMENT` | 45 | Settlement price of the current session |
| `SYMBOL_SESSION_PRICE_LIMIT_MIN` | 46 | Minimal price of the current session |
| `SYMBOL_SESSION_PRICE_LIMIT_MAX` | 47 | Maximal price of the current session |

### Price Analytics & Options

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_OPTION_STRIKE` | 12 | Option strike price |
| `SYMBOL_PRICE_CHANGE` | 49 | Change of price in % |
| `SYMBOL_PRICE_VOLATILITY` | 50 | Price volatility in % |
| `SYMBOL_PRICE_THEORETICAL` | 51 | Theoretical option price |
| `SYMBOL_PRICE_DELTA` | 52 | Option/warrant delta |
| `SYMBOL_PRICE_THETA` | 53 | Option/warrant theta |
| `SYMBOL_PRICE_GAMMA` | 54 | Option/warrant gamma |
| `SYMBOL_PRICE_VEGA` | 55 | Option/warrant vega |
| `SYMBOL_PRICE_RHO` | 56 | Option/warrant rho |
| `SYMBOL_PRICE_OMEGA` | 57 | Option/warrant omega |
| `SYMBOL_PRICE_SENSITIVITY` | 58 | Option/warrant sensitivity |
| `SYMBOL_COUNT` | 59 | Total count of properties |

**Usage in Python:**
```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Access price constants
bid_property = market_info_pb2.SYMBOL_BID  # = 0
ask_property = market_info_pb2.SYMBOL_ASK  # = 3

# Use in method call
bid_data = await account.symbol_info_double("EURUSD", market_info_pb2.SYMBOL_BID)
print(f"BID: {bid_data.value}")
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Property availability:** Not all properties are available for all symbols. Check broker documentation for symbol-specific properties.
* **Tick values:** Use `SYMBOL_TRADE_TICK_VALUE` properties for accurate profit/loss calculations.
* **Volume limits:** Always check `SYMBOL_VOLUME_MIN`, `SYMBOL_VOLUME_MAX`, and `SYMBOL_VOLUME_STEP` before placing orders.

---

## 🔗 Usage Examples

### 1) Get BID and ASK prices

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get BID price (short format - recommended)
bid_data = await account.symbol_info_double("EURUSD", market_info_pb2.SYMBOL_BID)
print(f"BID: {bid_data.value}")

# Get ASK price
ask_data = await account.symbol_info_double(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_ASK
)
print(f"ASK: {ask_data.value}")

# Calculate spread
spread = ask_data.value - bid_data.value
print(f"Spread: {spread:.5f}")
```

### 2) Get volume limits for trading

```python
async def get_volume_limits(account: MT5Account, symbol: str):
    """Get volume constraints for a symbol"""

    # Get minimum volume
    min_vol_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_VOLUME_MIN
    )

    # Get maximum volume
    max_vol_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_VOLUME_MAX
    )

    # Get volume step
    step_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_VOLUME_STEP
    )

    print(f"Volume limits for {symbol}:")
    print(f"  Min: {min_vol_data.value:.2f} lots")
    print(f"  Max: {max_vol_data.value:.2f} lots")
    print(f"  Step: {step_data.value:.2f} lots")

    return {
        "min": min_vol_data.value,
        "max": max_vol_data.value,
        "step": step_data.value
    }

# Usage:
limits = await get_volume_limits(account, "EURUSD")
```

### 3) Get swap rates

```python
async def get_swap_info(account: MT5Account, symbol: str):
    """Get long and short swap rates"""

    # Get long swap
    long_swap_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SWAP_LONG
    )

    # Get short swap
    short_swap_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SWAP_SHORT
    )

    print(f"Swap for {symbol}:")
    print(f"  Long: {long_swap_data.value:.2f}")
    print(f"  Short: {short_swap_data.value:.2f}")

    return {
        "long": long_swap_data.value,
        "short": short_swap_data.value
    }

# Usage:
swaps = await get_swap_info(account, "GBPUSD")
```

### 4) Get tick size and contract size

```python
async def get_trading_specs(account: MT5Account, symbol: str):
    """Get tick size and contract size for precise calculations"""

    # Get tick size (minimal price change)
    tick_size_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_TRADE_TICK_SIZE
    )

    # Get contract size
    contract_size_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_TRADE_CONTRACT_SIZE
    )

    # Get point value
    point_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_POINT
    )

    print(f"Trading specs for {symbol}:")
    print(f"  Tick size: {tick_size_data.value}")
    print(f"  Contract size: {contract_size_data.value}")
    print(f"  Point value: {point_data.value}")

    return {
        "tick_size": tick_size_data.value,
        "contract_size": contract_size_data.value,
        "point": point_data.value
    }

# Usage:
specs = await get_trading_specs(account, "EURUSD")
```

### 5) Check if price is within session limits

```python
async def check_price_limits(account: MT5Account, symbol: str, price: float) -> bool:
    """Check if price is within current session limits"""

    # Get session price limits
    min_price_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SESSION_PRICE_LIMIT_MIN
    )

    max_price_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SESSION_PRICE_LIMIT_MAX
    )

    min_price = min_price_data.value
    max_price = max_price_data.value

    if min_price <= price <= max_price:
        print(f"[OK] Price {price} is within limits [{min_price}, {max_price}]")
        return True
    else:
        print(f"[ERROR] Price {price} is outside limits [{min_price}, {max_price}]")
        return False

# Usage:
is_valid = await check_price_limits(account, "EURUSD", 1.08500)
```

---

## Common Patterns

### Validate volume before order

```python
async def validate_volume(account: MT5Account, symbol: str, volume: float) -> bool:
    """Validate volume meets symbol requirements"""

    min_data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_VOLUME_MIN)
    max_data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_VOLUME_MAX)
    step_data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_VOLUME_STEP)

    min_vol = min_data.value
    max_vol = max_data.value
    step = step_data.value

    # Check range
    if volume < min_vol or volume > max_vol:
        print(f"[ERROR] Volume {volume} outside range [{min_vol}, {max_vol}]")
        return False

    # Check step
    if (volume - min_vol) % step != 0:
        print(f"[ERROR] Volume {volume} doesn't match step {step}")
        return False

    return True
```

### Get current market price

```python
async def get_market_price(account: MT5Account, symbol: str, side: str) -> float:
    """Get current market price for buy or sell"""

    if side.upper() == "BUY":
        # For buy orders, use ASK price
        data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_ASK)
    else:
        # For sell orders, use BID price
        data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_BID)

    return data.value
```

---

## 📚 See also

* [symbol_info_integer](./symbol_info_integer.md) - Get integer properties
* [symbol_info_string](./symbol_info_string.md) - Get string properties
* [symbol_params_many](./symbol_params_many.md) - Get all symbol parameters at once
