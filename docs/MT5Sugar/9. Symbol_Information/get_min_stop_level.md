# Get Minimum Stop Level (`get_min_stop_level`)

> **Sugar method:** Returns minimum allowed distance for Stop Loss and Take Profit in points.

**API Information:**

* **Method:** `sugar.get_min_stop_level(symbol)`
* **Returns:** Minimum stop level in points (integer)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_min_stop_level(self, symbol: str) -> int
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
| `int` | Minimum stop level in points (0 means no restriction) |

---

## 🏛️ Essentials

**What it does:**

- Gets minimum allowed distance between price and SL/TP
- Returns value in points (not pips)
- Used to validate SL/TP placement
- Broker-defined restriction

**Key behaviors:**

- Returns 0 if no minimum restriction
- Value is in points (EURUSD: 1 point = 0.00001)
- Same minimum applies to both SL and TP
- Measured from current price, not open price
- Violating this causes trade rejection

---

## ⚡ Under the Hood

```
MT5Sugar.get_min_stop_level()
    ↓ calls
MT5Service.get_symbol_integer(symbol, SYMBOL_TRADE_STOPS_LEVEL)
    ↓ calls
MT5Account.symbol_info_integer()
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoInteger(property=SYMBOL_TRADE_STOPS_LEVEL)
    ↓ MT5 Terminal
    ↓ returns minimum stop level
```

**Call chain:**

1. Sugar calls Service.get_symbol_integer() with SYMBOL_TRADE_STOPS_LEVEL property
2. Service forwards to Account.symbol_info_integer()
3. Account sends gRPC request with property enum
4. Terminal retrieves minimum stop level for symbol
5. Returns integer value in points

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1677`
- Service: `src/pymt5/mt5_service.py:497`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:951`

---

## When to Use

**Use `get_min_stop_level()` when:**

- Validating SL/TP before order placement
- Calculating safe SL/TP distances
- Building order validation logic
- Error prevention in automated trading
- Adjusting SL/TP to broker requirements

**Don't use when:**

- Broker has no restrictions (returns 0 anyway)
- Already know the minimum level
- Not using SL/TP in orders
- Only doing market orders without SL/TP

---

## 🔗 Examples

### Example 1: Check Minimum Stop Level

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def check_min_level():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Get minimum stop level
    min_level = await sugar.get_min_stop_level(symbol)

    if min_level == 0:
        print(f"{symbol}: No minimum stop level restriction")
    else:
        print(f"{symbol}: Minimum stop level = {min_level} points")

        # Get symbol info to convert points to price
        info = await sugar.get_symbol_info(symbol)
        min_distance = min_level * info.point

        print(f"Minimum SL/TP distance: {min_distance:.{info.digits}f}")

# Output:
# EURUSD: Minimum stop level = 20 points
# Minimum SL/TP distance: 0.00020
```

### Example 2: Validate SL/TP Before Order

```python
async def validate_sltp():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Get current price and min level
    bid = await sugar.get_bid(symbol)
    min_level = await sugar.get_min_stop_level(symbol)
    info = await sugar.get_symbol_info(symbol)

    # Desired SL 10 points from price
    desired_sl_points = 10
    desired_sl = bid - (desired_sl_points * info.point)

    # Validate
    if min_level > 0 and desired_sl_points < min_level:
        print(f"ERROR: SL too close to price")
        print(f"Desired: {desired_sl_points} points")
        print(f"Minimum: {min_level} points")

        # Adjust to minimum
        adjusted_sl = bid - (min_level * info.point)
        print(f"Adjusted SL: {adjusted_sl:.{info.digits}f}")
    else:
        print(f"SL validation passed")

        # Safe to place order
        ticket = await sugar.sell_market_with_sltp(
            symbol,
            volume=0.1,
            sl=desired_sl
        )

# Output:
# ERROR: SL too close to price
# Desired: 10 points
# Minimum: 20 points
# Adjusted SL: 1.08412
```

### Example 3: Safe SL/TP Calculator

```python
async def calculate_safe_sltp():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Get requirements
    ask = await sugar.get_ask(symbol)
    min_level = await sugar.get_min_stop_level(symbol)
    info = await sugar.get_symbol_info(symbol)

    # User wants 50 pips SL/TP
    desired_pips = 50
    desired_points = desired_pips * 10  # 500 points

    # Check against minimum
    actual_points = max(desired_points, min_level)

    if actual_points > desired_points:
        print(f"Adjusted from {desired_pips} to {actual_points/10} pips (broker minimum)")

    # Calculate SL/TP for BUY order
    sl_price = ask - (actual_points * info.point)
    tp_price = ask + (actual_points * info.point)

    print(f"Entry: {ask:.{info.digits}f}")
    print(f"SL: {sl_price:.{info.digits}f} ({actual_points} points)")
    print(f"TP: {tp_price:.{info.digits}f} ({actual_points} points)")

    # Place order
    ticket = await sugar.buy_market_with_sltp(
        symbol,
        volume=0.1,
        sl=sl_price,
        tp=tp_price
    )
    print(f"Order placed: {ticket}")
```

---

## Common Pitfalls

**Pitfall 1: Confusing points and pips**
```python
# ERROR: min_level is in points, not pips
min_level = await sugar.get_min_stop_level("EURUSD")
# Returns 20 (points), not 2 (pips)

# Setting SL 20 pips away instead of 20 points
info = await sugar.get_symbol_info("EURUSD")
sl = bid - (min_level * info.point * 10)  # WRONG! Too far
```

**Solution:** Use points directly
```python
min_level = await sugar.get_min_stop_level("EURUSD")
info = await sugar.get_symbol_info("EURUSD")

# Correct: min_level is already in points
sl = bid - (min_level * info.point)
```

**Pitfall 2: Not checking for zero**
```python
# Assuming minimum always exists
min_level = await sugar.get_min_stop_level("EURUSD")

# If returns 0, no minimum required
# Your validation logic might fail
if desired_points < min_level:  # Always False if min_level=0
    print("Too close")
```

**Solution:** Check for zero explicitly
```python
min_level = await sugar.get_min_stop_level("EURUSD")

if min_level > 0 and desired_points < min_level:
    print(f"Too close, minimum is {min_level} points")
```

**Pitfall 3: Using open price instead of current price**
```python
# ERROR: Minimum is from CURRENT price, not open price
open_price = 1.08500
sl = open_price - (min_level * info.point)

# If current price moved, this SL might violate minimum
```

**Solution:** Always use current market price
```python
# For BUY position (check against BID)
current_bid = await sugar.get_bid(symbol)
sl = current_bid - (min_level * info.point)

# For SELL position (check against ASK)
current_ask = await sugar.get_ask(symbol)
sl = current_ask + (min_level * info.point)
```

---

## Pro Tips

**Tip 1: SL/TP validator helper**
```python
async def validate_sltp_distance(sugar, symbol, order_type, price, sl, tp):
    """Validate SL/TP meet minimum distance requirement."""
    min_level = await sugar.get_min_stop_level(symbol)

    if min_level == 0:
        return True  # No restriction

    info = await sugar.get_symbol_info(symbol)
    min_distance = min_level * info.point

    # Check SL
    if sl is not None:
        sl_distance = abs(price - sl)
        if sl_distance < min_distance:
            print(f"SL too close: {sl_distance:.{info.digits}f} < {min_distance:.{info.digits}f}")
            return False

    # Check TP
    if tp is not None:
        tp_distance = abs(price - tp)
        if tp_distance < min_distance:
            print(f"TP too close: {tp_distance:.{info.digits}f} < {min_distance:.{info.digits}f}")
            return False

    return True

# Usage
ask = await sugar.get_ask("EURUSD")
sl = ask - 0.00010  # 10 points

is_valid = await validate_sltp_distance(sugar, "EURUSD", "BUY", ask, sl, None)
```

**Tip 2: Auto-adjust to minimum**
```python
async def adjust_sltp_to_minimum(sugar, symbol, desired_points):
    """Ensure SL/TP meets minimum requirement."""
    min_level = await sugar.get_min_stop_level(symbol)

    # Use greater of desired or minimum
    actual_points = max(desired_points, min_level)

    if actual_points > desired_points:
        print(f"Adjusted from {desired_points} to {actual_points} points (broker minimum)")

    return actual_points

# Usage
actual_points = await adjust_sltp_to_minimum(sugar, "EURUSD", desired_points=10)
```

**Tip 3: Convert points to price helper**
```python
async def calculate_sltp_prices(sugar, symbol, order_type, distance_points):
    """Calculate SL/TP prices ensuring minimum distance."""
    # Get minimum and adjust
    min_level = await sugar.get_min_stop_level(symbol)
    actual_points = max(distance_points, min_level)

    info = await sugar.get_symbol_info(symbol)
    distance = actual_points * info.point

    if order_type == "BUY":
        price = info.ask
        sl = price - distance
        tp = price + distance
    else:  # SELL
        price = info.bid
        sl = price + distance
        tp = price - distance

    return {
        "entry": price,
        "sl": sl,
        "tp": tp,
        "distance_points": actual_points
    }

# Usage
prices = await calculate_sltp_prices(sugar, "EURUSD", "BUY", distance_points=50)
print(f"Entry: {prices['entry']}, SL: {prices['sl']}, TP: {prices['tp']}")
```

---

## 📚 See Also

- [get_symbol_info](get_symbol_info.md) - Get symbol parameters including point value
- [buy_market_with_sltp](../5.%20Trading_With_SLTP/buy_market_with_sltp.md) - Open BUY with SL/TP
- [modify_position_sltp](../6.%20Position_Management/modify_position_sltp.md) - Modify SL/TP on position
