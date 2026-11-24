# Calculate Required Margin (`calculate_required_margin`)

> **Sugar method:** Calculates margin required to open a position with specified parameters.

**API Information:**

* **Method:** `sugar.calculate_required_margin(symbol, volume, order_type)`
* **Returns:** Required margin in account currency (float)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def calculate_required_margin(
    self,
    symbol: str,
    volume: float,
    order_type: Optional[int] = None
) -> float
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Yes | - | Trading symbol (e.g., "EURUSD") |
| `volume` | `float` | Yes | - | Position volume in lots |
| `order_type` | `Optional[int]` | No | `None` | Order type enum (defaults to BUY) |

---

## Return Value

| Type | Description |
|------|-------------|
| `float` | Required margin in account currency (e.g., USD) |

---

## 🏛️ Essentials

**What it does:**

- Calculates margin needed to open position
- Uses MT5's built-in margin calculation
- Accounts for leverage and symbol specifications
- Returns amount in account currency

**Key behaviors:**

- Defaults to BUY order if type not specified
- Uses current market price (ASK for BUY, BID for SELL)
- Calculation: `margin = (volume × contract_size × price) / leverage`
- Bypasses Service layer, calls Account directly
- Returns actual margin requirement from MT5

**Formula:**

```
margin = (volume × contract_size × price) / leverage
```

---

## ⚡ Under the Hood

```
MT5Sugar.calculate_required_margin()
    ↓ calls
MT5Service.get_symbol_tick(symbol)
    ↓ creates OrderCalcMarginRequest
    ↓ calls
MT5Account.order_calc_margin(request)
    ↓ gRPC protobuf
TradingService.OrderCalcMargin()
    ↓ MT5 Terminal calculates margin
    ↓ returns result.margin
```

**Call chain:**

1. Sugar calls Service.get_symbol_tick() for current price
2. Sugar determines price based on order_type (ASK for BUY, BID for SELL)
3. Sugar creates OrderCalcMarginRequest with symbol, type, volume, price
4. Sugar gets Account instance from Service
5. Sugar calls Account.order_calc_margin() directly
6. Account sends gRPC margin calculation request
7. Terminal calculates exact margin requirement
8. Returns margin value as float

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1841`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1892`

---

## When to Use

**Use `calculate_required_margin()` when:**

- Checking if sufficient margin before trading
- Calculating maximum affordable position size
- Risk management calculations
- Pre-trade validation
- Margin level monitoring

**Don't use when:**

- Don't need exact margin (use estimate)
- Already know approximate margin
- Not margin-constrained
- Performance is critical

---

## 🔗 Examples

### Example 1: Check Margin Before Trading

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

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
    volume = 1.0

    # Calculate required margin
    margin_needed = await sugar.calculate_required_margin(symbol, volume)

    # Get available margin
    free_margin = await sugar.get_free_margin()

    print(f"Required margin: ${margin_needed:.2f}")
    print(f"Available margin: ${free_margin:.2f}")

    if margin_needed <= free_margin:
        print("Sufficient margin - opening position")
        ticket = await sugar.buy_market(symbol, volume=volume)
        print(f"Order opened: {ticket}")
    else:
        print("Insufficient margin")
        shortage = margin_needed - free_margin
        print(f"Short by: ${shortage:.2f}")

# Output:
# Required margin: $1084.32
# Available margin: $5000.00
# Sufficient margin - opening position
# Order opened: 123456789
```

### Example 2: Calculate Maximum Affordable Volume

```python
async def max_affordable_volume():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Get available margin
    free_margin = await sugar.get_free_margin()

    print(f"Available margin: ${free_margin:.2f}")

    # Binary search for maximum volume
    min_vol = 0.01
    max_vol = 100.0
    best_volume = 0.01

    while max_vol - min_vol > 0.01:
        test_vol = (min_vol + max_vol) / 2

        margin_needed = await sugar.calculate_required_margin(symbol, test_vol)

        if margin_needed <= free_margin:
            best_volume = test_vol
            min_vol = test_vol
        else:
            max_vol = test_vol

    # Round to symbol step
    info = await sugar.get_symbol_info(symbol)
    best_volume = round(best_volume / info.volume_step) * info.volume_step

    margin_for_best = await sugar.calculate_required_margin(symbol, best_volume)

    print(f"Maximum affordable volume: {best_volume} lots")
    print(f"Margin required: ${margin_for_best:.2f}")

# Output:
# Available margin: $5000.00
# Maximum affordable volume: 4.61 lots
# Margin required: $4998.23
```

### Example 3: Compare Margin for Different Symbols

```python
async def compare_margin_requirements():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
    volume = 1.0

    print(f"Margin required for {volume} lot:")

    for symbol in symbols:
        margin = await sugar.calculate_required_margin(symbol, volume)
        print(f"  {symbol}: ${margin:.2f}")

    # Get available margin
    free_margin = await sugar.get_free_margin()
    print(f"\nAvailable margin: ${free_margin:.2f}")

    # Find cheapest symbol
    margins = {}
    for symbol in symbols:
        margins[symbol] = await sugar.calculate_required_margin(symbol, volume)

    cheapest = min(margins, key=margins.get)
    print(f"\nCheapest to trade: {cheapest} (${margins[cheapest]:.2f})")

# Output:
# Margin required for 1.0 lot:
#   EURUSD: $1084.32
#   GBPUSD: $1267.89
#   USDJPY: $1493.85
#   XAUUSD: $20435.00
#
# Available margin: $5000.00
#
# Cheapest to trade: EURUSD ($1084.32)
```

---

## Common Pitfalls

**Pitfall 1: Not accounting for existing positions**
```python
# ERROR: Free margin already accounts for open positions
margin_needed = await sugar.calculate_required_margin("EURUSD", 1.0)
free_margin = await sugar.get_free_margin()

# This is correct - free_margin is already reduced by open positions
if margin_needed <= free_margin:
    # Safe to open
```

**Pitfall 2: Using old margin calculation**
```python
# ERROR: Price changes, margin changes
margin = await sugar.calculate_required_margin("EURUSD", 1.0)

await asyncio.sleep(60)

# Margin calculation is now stale
if margin <= free_margin:  # Old margin value
    await sugar.buy_market("EURUSD", volume=1.0)
```

**Solution:** Calculate immediately before trading
```python
# Calculate fresh margin right before trade
margin = await sugar.calculate_required_margin("EURUSD", 1.0)
free_margin = await sugar.get_free_margin()

if margin <= free_margin:
    # Immediately execute
    await sugar.buy_market("EURUSD", volume=1.0)
```

**Pitfall 3: Ignoring order_type parameter**
```python
# For most cases, BUY/SELL margin is same
# But some symbols might have directional margin differences

margin_buy = await sugar.calculate_required_margin("XAUUSD", 1.0)
# Defaults to BUY
```

**Solution:** Specify order type if needed
```python
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as trade_pb2

# For BUY
margin_buy = await sugar.calculate_required_margin(
    "XAUUSD",
    1.0,
    order_type=trade_pb2.ORDER_TYPE_TF_BUY
)

# For SELL
margin_sell = await sugar.calculate_required_margin(
    "XAUUSD",
    1.0,
    order_type=trade_pb2.ORDER_TYPE_TF_SELL
)
```

---

## Pro Tips

**Tip 1: Margin checker helper**
```python
async def check_sufficient_margin(sugar, symbol, volume):
    """Check if sufficient margin for position."""
    margin_needed = await sugar.calculate_required_margin(symbol, volume)
    free_margin = await sugar.get_free_margin()

    if margin_needed > free_margin:
        shortage = margin_needed - free_margin
        raise ValueError(
            f"Insufficient margin: need ${margin_needed:.2f}, "
            f"have ${free_margin:.2f}, short ${shortage:.2f}"
        )

    return True

# Usage
try:
    await check_sufficient_margin(sugar, "EURUSD", 10.0)
    ticket = await sugar.buy_market("EURUSD", volume=10.0)
except ValueError as e:
    print(f"Cannot open: {e}")
```

**Tip 2: Calculate margin level after trade**
```python
async def simulate_trade_impact(sugar, symbol, volume):
    """Show how margin level would change after trade."""
    # Current state
    equity = await sugar.get_equity()
    margin = await sugar.get_margin()
    free_margin = await sugar.get_free_margin()
    margin_level = await sugar.get_margin_level()

    # Calculate additional margin needed
    additional_margin = await sugar.calculate_required_margin(symbol, volume)

    # Simulated state after trade
    new_margin = margin + additional_margin
    new_free_margin = free_margin - additional_margin
    new_margin_level = (equity / new_margin) * 100 if new_margin > 0 else 0

    print("Current state:")
    print(f"  Margin: ${margin:.2f}")
    print(f"  Free margin: ${free_margin:.2f}")
    print(f"  Margin level: {margin_level:.2f}%")

    print(f"\nAfter opening {volume} lots of {symbol}:")
    print(f"  Margin: ${new_margin:.2f} (+${additional_margin:.2f})")
    print(f"  Free margin: ${new_free_margin:.2f}")
    print(f"  Margin level: {new_margin_level:.2f}%")

    if new_margin_level < 100:
        print("\nWARNING: Margin level would drop below 100%!")

# Usage
await simulate_trade_impact(sugar, "EURUSD", 5.0)
```

**Tip 3: Find optimal volume for target margin level**
```python
async def calculate_volume_for_margin_level(sugar, symbol, target_margin_level=200.0):
    """Calculate volume that maintains target margin level."""
    equity = await sugar.get_equity()
    current_margin = await sugar.get_margin()

    # Calculate maximum additional margin allowed
    max_total_margin = equity / (target_margin_level / 100)
    max_additional_margin = max_total_margin - current_margin

    if max_additional_margin <= 0:
        print(f"Already below target margin level")
        return 0.0

    # Binary search for volume
    min_vol = 0.01
    max_vol = 100.0
    best_volume = 0.01

    while max_vol - min_vol > 0.01:
        test_vol = (min_vol + max_vol) / 2

        margin_needed = await sugar.calculate_required_margin(symbol, test_vol)

        if margin_needed <= max_additional_margin:
            best_volume = test_vol
            min_vol = test_vol
        else:
            max_vol = test_vol

    # Round to symbol step
    info = await sugar.get_symbol_info(symbol)
    best_volume = round(best_volume / info.volume_step) * info.volume_step

    return best_volume

# Usage
volume = await calculate_volume_for_margin_level(sugar, "EURUSD", target_margin_level=200.0)
print(f"Safe volume to maintain 200% margin level: {volume} lots")
```

---

## 📚 See Also

- [get_free_margin](../2.%20Account_Properties/get_free_margin.md) - Get available margin
- [get_margin_level](../2.%20Account_Properties/get_margin_level.md) - Get margin level percentage
- [can_open_position](can_open_position.md) - Validate if position can be opened
- [calculate_position_size](calculate_position_size.md) - Calculate position size by risk
