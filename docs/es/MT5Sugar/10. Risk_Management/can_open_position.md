# Can Open Position (`can_open_position`)

> **Sugar method:** Validates if a position can be opened with specified parameters.

**API Information:**

* **Method:** `sugar.can_open_position(symbol, volume)`
* **Returns:** Tuple of (can_open: bool, reason: str)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def can_open_position(
    self,
    symbol: str,
    volume: float
) -> Tuple[bool, str]
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Yes | - | Trading symbol (e.g., "EURUSD") |
| `volume` | `float` | Yes | - | Position volume in lots |

---

## Return Value

| Type | Description |
|------|-------------|
| `Tuple[bool, str]` | First element: True if can open, False otherwise. Second element: reason string ("OK" or error description) |

---

## 🏛️ Essentials

**What it does:**

- Validates order before actual placement
- Checks margin requirements
- Checks symbol availability
- Checks volume constraints
- Returns validation result with reason

**Key behaviors:**

- Simulates BUY order at current ASK price
- Does NOT actually place order
- Uses MT5's order_check function
- Returns tuple (success, message)
- Return code 0 = OK
- Non-zero code = validation failed

---

## ⚡ Under the Hood

```
MT5Sugar.can_open_position()
    ↓ calls
MT5Service.get_symbol_tick(symbol)
    ↓ creates MrpcMqlTradeRequest (BUY at ASK)
    ↓ wraps in OrderCheckRequest
    ↓ calls
MT5Service.check_order(request)
    ↓ calls
MT5Account.order_check()
    ↓ gRPC protobuf
TradingService.OrderCheck()
    ↓ MT5 Terminal validates order
    ↓ returns (returned_code, comment)
```

**Call chain:**

1. Sugar calls Service.get_symbol_tick() for current price
2. Sugar creates MrpcMqlTradeRequest with BUY order
3. Sugar wraps request in OrderCheckRequest
4. Sugar calls Service.check_order()
5. Service forwards to Account.order_check()
6. Account sends gRPC order check request
7. Terminal validates order parameters
8. Returns result with code and comment
9. Sugar returns tuple (success: bool, reason: str)

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1774`
- Service: `src/pymt5/mt5_service.py:1018`

---

## When to Use

**Use `can_open_position()` when:**
- Validating orders before placement
- Checking margin availability
- Pre-flight checks in trading systems
- Error prevention
- Building safe trading applications

**Don't use when:**
- Already confident order will succeed
- Performance is critical (adds extra call)
- Order validation is redundant
- Testing with demo account

---

## 🔗 Examples

### Example 1: Validate Before Opening

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def safe_open():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    volume = 1.0

    # Check if can open
    can_open, reason = await sugar.can_open_position(symbol, volume)

    if can_open:
        print(f"Validation passed: {reason}")

        # Safe to open
        ticket = await sugar.buy_market(symbol, volume=volume)
        print(f"Order opened: {ticket}")
    else:
        print(f"Cannot open position: {reason}")

# Output:
# Validation passed: OK
# Order opened: 123456789
```

### Example 2: Check Margin Before Trading

```python
async def check_margin():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Want to open large position
    desired_volume = 10.0

    # Check if possible
    can_open, reason = await sugar.can_open_position(symbol, desired_volume)

    if not can_open:
        print(f"Cannot open {desired_volume} lots: {reason}")

        # Try smaller size
        for volume in [5.0, 2.0, 1.0, 0.5]:
            can_open, reason = await sugar.can_open_position(symbol, volume)

            if can_open:
                print(f"Can open {volume} lots")
                ticket = await sugar.buy_market(symbol, volume=volume)
                print(f"Opened: {ticket}")
                break
    else:
        print(f"Can open full {desired_volume} lots")

# Output:
# Cannot open 10.0 lots: Check failed: code=1
# Can open 2.0 lots
# Opened: 123456789
```

### Example 3: Validate Multiple Symbols

```python
async def validate_watchlist():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Check multiple symbols
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
    volume = 0.1

    print("Checking which symbols can be traded:")

    tradable = []
    not_tradable = []

    for symbol in symbols:
        can_open, reason = await sugar.can_open_position(symbol, volume)

        if can_open:
            tradable.append(symbol)
            print(f"  {symbol}: OK")
        else:
            not_tradable.append(symbol)
            print(f"  {symbol}: {reason}")

    print(f"\nTradable ({len(tradable)}): {tradable}")
    print(f"Not tradable ({len(not_tradable)}): {not_tradable}")
```

---

## Common Pitfalls

**Pitfall 1: Expecting detailed error messages**
```python
# ERROR: Reason string may not be very descriptive
can_open, reason = await sugar.can_open_position("EURUSD", 100.0)

if not can_open:
    print(reason)  # May just be "Check failed: code=1"
```

**Solution:** Check specific conditions separately
```python
# Check margin separately
margin_needed = await sugar.calculate_required_margin("EURUSD", 100.0)
free_margin = await sugar.get_free_margin()

if margin_needed > free_margin:
    print(f"Insufficient margin: need ${margin_needed:.2f}, have ${free_margin:.2f}")
```

**Pitfall 2: Assuming validation guarantees success**
```python
# Validation passed but order still might fail
can_open, reason = await sugar.can_open_position("EURUSD", 1.0)

if can_open:
    # Market conditions might change between check and execution
    ticket = await sugar.buy_market("EURUSD", volume=1.0)  # May still fail
```

**Solution:** Handle order errors
```python
can_open, reason = await sugar.can_open_position("EURUSD", 1.0)

if can_open:
    try:
        ticket = await sugar.buy_market("EURUSD", volume=1.0)
    except Exception as e:
        print(f"Order failed despite validation: {e}")
```

**Pitfall 3: Validating only BUY orders**
```python
# can_open_position only checks BUY orders
can_open, reason = await sugar.can_open_position("EURUSD", 1.0)

# But you might want to open SELL
ticket = await sugar.sell_market("EURUSD", volume=1.0)
```

**Solution:** Validation is directional-agnostic for margin
```python
# For margin purposes, BUY/SELL validation is similar
# Volume and margin requirements are same
can_open, reason = await sugar.can_open_position("EURUSD", 1.0)

if can_open:
    # Either direction should work
    ticket = await sugar.sell_market("EURUSD", volume=1.0)
```

---

## Pro Tips

**Tip 1: Safe trading wrapper**
```python
async def safe_buy_market(sugar, symbol, volume):
    """Open BUY position with validation."""
    # Validate first
    can_open, reason = await sugar.can_open_position(symbol, volume)

    if not can_open:
        raise ValueError(f"Cannot open position: {reason}")

    # Open position
    ticket = await sugar.buy_market(symbol, volume=volume)

    return ticket

# Usage
try:
    ticket = await safe_buy_market(sugar, "EURUSD", 1.0)
    print(f"Opened: {ticket}")
except ValueError as e:
    print(f"Error: {e}")
```

**Tip 2: Find maximum tradable volume**
```python
async def find_max_volume(sugar, symbol, start_volume=10.0):
    """Find maximum volume that can be opened."""
    volume = start_volume

    # Binary search for maximum
    while volume > 0.01:
        can_open, reason = await sugar.can_open_position(symbol, volume)

        if can_open:
            return volume

        # Try half
        volume = volume / 2

    return 0.01  # Minimum

# Usage
max_vol = await find_max_volume(sugar, "EURUSD", start_volume=10.0)
print(f"Maximum volume: {max_vol} lots")
```

**Tip 3: Pre-trade validation checklist**
```python
async def validate_trade(sugar, symbol, volume):
    """Complete trade validation."""
    checks = {
        "symbol_exists": False,
        "can_open": False,
        "sufficient_margin": False
    }

    # Check 1: Symbol exists
    exists = await sugar.is_symbol_available(symbol)
    checks["symbol_exists"] = exists

    if not exists:
        return checks, "Symbol not available"

    # Check 2: Can open position
    can_open, reason = await sugar.can_open_position(symbol, volume)
    checks["can_open"] = can_open

    if not can_open:
        return checks, f"Validation failed: {reason}"

    # Check 3: Margin check
    margin_needed = await sugar.calculate_required_margin(symbol, volume)
    free_margin = await sugar.get_free_margin()
    checks["sufficient_margin"] = margin_needed <= free_margin

    if margin_needed > free_margin:
        return checks, f"Insufficient margin: ${margin_needed:.2f} needed, ${free_margin:.2f} available"

    return checks, "All checks passed"

# Usage
checks, message = await validate_trade(sugar, "EURUSD", 1.0)
print(f"Validation: {message}")
print(f"Checks: {checks}")

if all(checks.values()):
    ticket = await sugar.buy_market("EURUSD", volume=1.0)
```

---

## 📚 See Also

- [calculate_required_margin](calculate_required_margin.md) - Calculate margin needed
- [get_free_margin](../2.%20Account_Properties/get_free_margin.md) - Check available margin
- [buy_market](../4.%20Simple_Trading/buy_market.md) - Open BUY position
- [calculate_position_size](calculate_position_size.md) - Calculate safe position size
