# Get Maximum Lot Size (`get_max_lot_size`)

> **Sugar method:** Returns maximum allowed position size for trading symbol.

**API Information:**

* **Method:** `sugar.get_max_lot_size(symbol)`
* **Returns:** Maximum volume in lots (float)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_max_lot_size(self, symbol: str) -> float
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Yes | - | Trading symbol (e.g., "EURUSD") |

---

## Return Value

| Type | Description |
|------|-------------|
| `float` | Maximum volume in lots (e.g., 100.0 for most forex pairs) |

---

## 🏛️ Essentials

**What it does:**

- Retrieves broker's maximum allowed lot size
- Symbol-specific constraint
- Essential for volume validation
- Part of symbol trading parameters

**Key behaviors:**

- Returns broker-defined maximum
- Typically 100.0 lots for forex majors
- Can vary by symbol type
- Exceeding this limit causes order rejection
- Same as SymbolInfo.volume_max

---

## ⚡ Under the Hood

```
MT5Sugar.get_max_lot_size()
    ↓ calls
MT5Service.get_symbol_double(symbol, SYMBOL_VOLUME_MAX)
    ↓ calls
MT5Account.symbol_info_double()
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoDouble(property=SYMBOL_VOLUME_MAX)
    ↓ MT5 Terminal
    ↓ returns maximum volume
```

**Call chain:**

1. Sugar calls Service.get_symbol_double() with SYMBOL_VOLUME_MAX property
2. Service forwards to Account.symbol_info_double()
3. Account sends gRPC request with property enum
4. Terminal retrieves maximum volume for symbol
5. Returns float value (maximum lots)

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1821`
- Service: `src/pymt5/mt5_service.py:474`
- Account: `package/helpers/mt5_account.py:906`

---

## When to Use

**Use `get_max_lot_size()` when:**

- Validating large position sizes
- Building position size validators
- Checking trading limits
- Clamping calculated volumes
- Building risk management systems

**Don't use when:**

- Already have SymbolInfo (use info.volume_max)
- Trading small positions (unlikely to hit limit)
- Maximum is hardcoded and known
- Not validating volumes

---

## 🔗 Examples

### Example 1: Check Maximum Lot Size

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def check_max_lots():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbols = ["EURUSD", "XAUUSD", "BTCUSD"]

    print("Maximum lot sizes:")

    for symbol in symbols:
        max_lots = await sugar.get_max_lot_size(symbol)
        print(f"  {symbol}: {max_lots} lots")

# Output:
# Maximum lot sizes:
#   EURUSD: 100.0 lots
#   XAUUSD: 50.0 lots
#   BTCUSD: 10.0 lots
```

### Example 2: Validate Volume Before Trading

```python
async def safe_trade():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    desired_volume = 150.0  # Too large

    # Get maximum
    max_volume = await sugar.get_max_lot_size(symbol)

    if desired_volume > max_volume:
        print(f"ERROR: {desired_volume} lots exceeds maximum of {max_volume}")
        print(f"Reducing to maximum: {max_volume}")
        desired_volume = max_volume

    # Now safe to trade
    ticket = await sugar.buy_market(symbol, volume=desired_volume)
    print(f"Order placed: {ticket} ({desired_volume} lots)")

# Output:
# ERROR: 150.0 lots exceeds maximum of 100.0
# Reducing to maximum: 100.0
# Order placed: 123456789 (100.0 lots)
```

### Example 3: Clamp Calculated Volume

```python
async def calculate_and_clamp():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Calculate position size based on risk
    calculated_volume = await sugar.calculate_position_size(
        symbol,
        risk_percent=10.0,  # High risk
        sl_pips=10  # Tight SL
    )

    print(f"Calculated volume: {calculated_volume} lots")

    # Get limits
    info = await sugar.get_symbol_info(symbol)
    max_volume = info.volume_max

    # Clamp to range
    final_volume = max(info.volume_min, min(calculated_volume, max_volume))

    if final_volume != calculated_volume:
        print(f"Volume clamped to: {final_volume} lots")

    # Trade with safe volume
    ticket = await sugar.buy_market(symbol, volume=final_volume)
    print(f"Order placed: {ticket}")

# Output:
# Calculated volume: 200.0 lots
# Volume clamped to: 100.0 lots
# Order placed: 123456789
```

---

## Common Pitfalls

**Pitfall 1: Assuming same maximum for all symbols**
```python
# ERROR: Maximum varies by symbol
max_forex = 100.0  # Hardcoded for forex

# Crypto might have different max
ticket = await sugar.buy_market("BTCUSD", volume=max_forex)  # May fail
```

**Solution:** Always fetch dynamically
```python
max_volume = await sugar.get_max_lot_size("BTCUSD")
ticket = await sugar.buy_market("BTCUSD", volume=max_volume)
```

**Pitfall 2: Not checking minimum as well**
```python
# Only checking maximum
desired = 0.005

max_vol = await sugar.get_max_lot_size("EURUSD")
volume = min(desired, max_vol)  # 0.005

# But minimum might be 0.01
await sugar.buy_market("EURUSD", volume=volume)  # Fails
```

**Solution:** Check both min and max
```python
info = await sugar.get_symbol_info("EURUSD")

volume = max(info.volume_min, min(desired, info.volume_max))
```

**Pitfall 3: Exceeding by small rounding error**
```python
# Calculation might slightly exceed due to floating point
calculated = 100.00000001

max_vol = await sugar.get_max_lot_size("EURUSD")  # 100.0

# Strict comparison fails
if calculated > max_vol:
    # Rounds down unnecessarily
```

**Solution:** Round to volume step first
```python
info = await sugar.get_symbol_info("EURUSD")

# Round to step
volume = round(calculated / info.volume_step) * info.volume_step

# Then clamp
volume = min(volume, info.volume_max)
```

---

## Pro Tips

**Tip 1: Volume validator helper**
```python
async def validate_volume(sugar, symbol, volume):
    """Validate and adjust volume to constraints."""
    info = await sugar.get_symbol_info(symbol)

    # Round to step
    volume = round(volume / info.volume_step) * info.volume_step

    # Clamp to range
    volume = max(info.volume_min, min(volume, info.volume_max))

    return volume

# Usage
desired = 150.0
safe_volume = await validate_volume(sugar, "EURUSD", desired)
print(f"Adjusted from {desired} to {safe_volume}")
```

**Tip 2: Get all volume constraints**
```python
async def get_volume_constraints(sugar, symbol):
    """Get all volume-related constraints."""
    info = await sugar.get_symbol_info(symbol)

    return {
        "min": info.volume_min,
        "max": info.volume_max,
        "step": info.volume_step,
        "range": f"{info.volume_min} - {info.volume_max}",
        "step_count": int((info.volume_max - info.volume_min) / info.volume_step) + 1
    }

# Usage
constraints = await get_volume_constraints(sugar, "EURUSD")
print(f"Volume range: {constraints['range']}")
print(f"Step: {constraints['step']}")
print(f"Possible values: {constraints['step_count']}")

# Output:
# Volume range: 0.01 - 100.0
# Step: 0.01
# Possible values: 9991
```

**Tip 3: Safe volume calculator**
```python
async def calculate_safe_volume(sugar, symbol, desired_volume):
    """Calculate volume ensuring all constraints."""
    info = await sugar.get_symbol_info(symbol)

    # Round to step
    volume = round(desired_volume / info.volume_step) * info.volume_step

    # Clamp to range
    if volume < info.volume_min:
        print(f"Volume {desired_volume} below minimum {info.volume_min}, using minimum")
        volume = info.volume_min
    elif volume > info.volume_max:
        print(f"Volume {desired_volume} above maximum {info.volume_max}, using maximum")
        volume = info.volume_max

    # Final validation
    if volume != desired_volume:
        print(f"Adjusted volume: {desired_volume} → {volume}")

    return volume

# Usage
volume = await calculate_safe_volume(sugar, "EURUSD", 150.0)
# Output: Volume 150.0 above maximum 100.0, using maximum
# Output: Adjusted volume: 150.0 → 100.0
```

---

## 📚 See Also

- [get_symbol_info](../9.%20Symbol_Information/get_symbol_info.md) - Get complete symbol info (includes volume_max)
- [calculate_position_size](calculate_position_size.md) - Calculate position size with risk
- [can_open_position](can_open_position.md) - Validate if position can be opened
