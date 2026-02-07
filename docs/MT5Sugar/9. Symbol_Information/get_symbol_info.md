# Get Symbol Information (`get_symbol_info`)

> **Sugar method:** Returns complete trading parameters for symbol.

**API Information:**

* **Method:** `sugar.get_symbol_info(symbol)`
* **Returns:** `SymbolInfo` dataclass with trading parameters
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_symbol_info(self, symbol: str) -> SymbolInfo
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Yes | - | Trading symbol (e.g., "EURUSD") |

---

## Return Value

`SymbolInfo` dataclass with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Symbol name |
| `bid` | `float` | Current BID price |
| `ask` | `float` | Current ASK price |
| `spread` | `int` | Current spread in points |
| `digits` | `int` | Decimal places in price |
| `point` | `float` | Minimum price change (0.00001 for EURUSD) |
| `volume_min` | `float` | Minimum volume in lots |
| `volume_max` | `float` | Maximum volume in lots |
| `volume_step` | `float` | Volume step (e.g., 0.01) |
| `contract_size` | `float` | Contract size (100,000 for standard forex) |

**Raises:**

- `ValueError` if symbol not found

---

## 🏛️ Essentials

**What it does:**

- Fetches complete symbol parameters in one call
- Returns structured SymbolInfo object
- More efficient than multiple separate calls
- Includes current prices and trading constraints

**Key behaviors:**

- Raises ValueError if symbol doesn't exist
- Returns current prices (bid/ask)
- Includes volume constraints for validation
- Contract size for margin/pip calculations

---

## ⚡ Under the Hood

```
MT5Sugar.get_symbol_info()
    ↓ calls
MT5Service.get_symbol_params_many(name_filter=symbol)
    ↓ calls
MT5Account.symbol_params_many()
    ↓ gRPC protobuf
MarketInfoService.SymbolParamsMany()
    ↓ MT5 Terminal
    ↓ extracts 10 key fields into SymbolInfo
```

**Call chain:**

1. Sugar calls Service.get_symbol_params_many() with symbol filter
2. Service forwards to Account.symbol_params_many()
3. Account sends gRPC request to terminal
4. Sugar extracts 10 key fields from SymbolParams
5. Returns SymbolInfo dataclass

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1615`
- SymbolInfo dataclass: `src/pymt5/mt5_sugar.py:179`
- Service: `src/pymt5/mt5_service.py:658`
- Account: `package/helpers/mt5_account.py:1221`

---

## When to Use

**Use `get_symbol_info()` when:**

- Need multiple symbol parameters
- Validating volume before trading
- Calculating pip values
- Price formatting with correct digits
- Checking trading constraints

**Don't use when:**

- Only need current price (use `get_bid()`/`get_ask()`)
- Only need one parameter (use specific methods)
- Need all symbols (use `get_all_symbols()`)

---

## 🔗 Examples

### Example 1: Basic Symbol Information

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def symbol_details():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get EURUSD information
    info = await sugar.get_symbol_info("EURUSD")

    print(f"Symbol: {info.name}")
    print(f"BID: {info.bid:.{info.digits}f}")
    print(f"ASK: {info.ask:.{info.digits}f}")
    print(f"Spread: {info.spread} points")
    print(f"Digits: {info.digits}")
    print(f"Point: {info.point}")
    print(f"Volume limits: {info.volume_min} - {info.volume_max}")
    print(f"Volume step: {info.volume_step}")
    print(f"Contract size: {info.contract_size}")

# Output:
# Symbol: EURUSD
# BID: 1.08432
# ASK: 1.08445
# Spread: 13 points
# Digits: 5
# Point: 0.00001
# Volume limits: 0.01 - 100.0
# Volume step: 0.01
# Contract size: 100000.0
```

### Example 2: Volume Validation

```python
async def validate_volume():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    desired_volume = 0.15

    # Get symbol info
    info = await sugar.get_symbol_info(symbol)

    # Validate volume
    if desired_volume < info.volume_min:
        print(f"Volume too small (min: {info.volume_min})")
    elif desired_volume > info.volume_max:
        print(f"Volume too large (max: {info.volume_max})")
    elif (desired_volume % info.volume_step) != 0:
        # Round to nearest step
        adjusted = round(desired_volume / info.volume_step) * info.volume_step
        print(f"Volume adjusted: {desired_volume} → {adjusted}")
        desired_volume = adjusted

    # Now safe to trade
    ticket = await sugar.buy_market(symbol, volume=desired_volume)
```

### Example 3: Calculate Pip Value

```python
async def calculate_pip_value():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    info = await sugar.get_symbol_info(symbol)

    # Calculate pip value for 1 lot
    # For forex: pip_value = point * 10 * contract_size
    pip_value = info.point * 10 * info.contract_size

    print(f"{symbol} Pip Value (1 lot):")
    print(f"  Point: {info.point}")
    print(f"  Contract size: {info.contract_size}")
    print(f"  1 pip = ${pip_value:.2f}")

    # For 0.1 lot
    pip_value_mini = pip_value * 0.1
    print(f"  0.1 lot: ${pip_value_mini:.2f} per pip")

# Output:
# EURUSD Pip Value (1 lot):
#   Point: 1e-05
#   Contract size: 100000.0
#   1 pip = $10.00
#   0.1 lot: $1.00 per pip
```

---

## Common Pitfalls

**Pitfall 1: Not handling ValueError**
```python
# ERROR: Symbol doesn't exist
try:
    info = await sugar.get_symbol_info("FAKEUSD")
except ValueError as e:
    print(e)  # "Symbol FAKEUSD not found"
```

**Solution:** Wrap in try-except or check first
```python
# Check if exists first
exists = await sugar.is_symbol_available("EURUSD")

if exists:
    info = await sugar.get_symbol_info("EURUSD")
```

**Pitfall 2: Using stale prices**
```python
# Prices in SymbolInfo are snapshot
info = await sugar.get_symbol_info("EURUSD")
await asyncio.sleep(60)

# info.bid and info.ask are 60 seconds old now!
```

**Solution:** Refresh info or use get_bid()/get_ask()
```python
# For current price, use dedicated methods
current_bid = await sugar.get_bid("EURUSD")

# Or refresh symbol info
info = await sugar.get_symbol_info("EURUSD")
```

**Pitfall 3: Confusing point and pip**
```python
# Point != Pip
info = await sugar.get_symbol_info("EURUSD")

# Point = minimum price change (0.00001)
# Pip = 10 points (0.0001)

# Calculate pips from points
spread_pips = info.spread / 10  # Convert points to pips
```

---

## Pro Tips

**Tip 1: Format prices correctly**
```python
info = await sugar.get_symbol_info("EURUSD")

# Use digits for formatting
price = info.bid
formatted = f"{price:.{info.digits}f}"
print(f"Price: {formatted}")  # 1.08432 (5 decimals)
```

**Tip 2: Validate and adjust volume**
```python
def adjust_volume(desired, info):
    """Adjust volume to symbol constraints."""
    # Clamp to min/max
    volume = max(info.volume_min, min(desired, info.volume_max))

    # Round to step
    volume = round(volume / info.volume_step) * info.volume_step

    return volume

info = await sugar.get_symbol_info("EURUSD")
safe_volume = adjust_volume(0.15, info)
```

**Tip 3: Cache symbol info**
```python
# Cache frequently used symbols
symbol_cache = {}

async def get_cached_symbol_info(sugar, symbol):
    """Get symbol info with caching."""
    if symbol not in symbol_cache:
        symbol_cache[symbol] = await sugar.get_symbol_info(symbol)

    return symbol_cache[symbol]

# Use cached info
info = await get_cached_symbol_info(sugar, "EURUSD")
```

---

## 📚 See Also

- [get_all_symbols](get_all_symbols.md) - List all available symbols
- [is_symbol_available](is_symbol_available.md) - Check if symbol exists
- [get_symbol_digits](get_symbol_digits.md) - Get decimal places only
- [get_min_stop_level](get_min_stop_level.md) - Get minimum SL/TP distance
