# Calculate Position Size (`calculate_position_size`)

> **Sugar method:** Calculates optimal position size based on account risk percentage and stop loss.

**API Information:**

* **Method:** `sugar.calculate_position_size(symbol, risk_percent, sl_pips)`
* **Returns:** Position size in lots (float)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def calculate_position_size(
    self,
    symbol: str,
    risk_percent: float,
    sl_pips: float
) -> float
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Yes | - | Trading symbol (e.g., "EURUSD") |
| `risk_percent` | `float` | Yes | - | Risk as percentage of balance (e.g., 2.0 for 2%) |
| `sl_pips` | `float` | Yes | - | Stop Loss distance in pips |

---

## Return Value

| Type | Description |
|------|-------------|
| `float` | Optimal position size in lots, adjusted to symbol constraints |

---

## 🏛️ Essentials

**What it does:**

- Calculates position size based on fixed risk percentage
- Uses standard forex risk management formula
- Automatically adjusts to symbol volume constraints
- Returns volume ready to use in orders

**Key behaviors:**

- Formula: `volume = (balance × risk% / 100) / (sl_pips × pip_value)`
- Pip value calculated as: `point × 10 × contract_size`
- Rounds to symbol's volume_step
- Clamps to volume_min and volume_max
- Based on current account balance

**Risk management formula:**

1. Calculate risk amount in account currency
2. Calculate pip value for 1 lot
3. Calculate volume = risk_amount / (sl_pips × pip_value)
4. Round and clamp to symbol constraints

---

## ⚡ Under the Hood

```
MT5Sugar.calculate_position_size()
    ↓ calls
MT5Sugar.get_balance()
    ↓ calls
MT5Sugar.get_symbol_info(symbol)
    ↓ calculates:
        risk_amount = balance × (risk_percent / 100)
        pip_value = point × 10 × contract_size
        volume = risk_amount / (sl_pips × pip_value)
    ↓ rounds to volume_step
    ↓ clamps to volume_min/volume_max
    ↓ returns adjusted volume
```

**Call chain:**

1. Sugar calls get_balance() to get current balance
2. Sugar calls get_symbol_info() for symbol parameters
3. Sugar calculates risk_amount from balance and risk_percent
4. Sugar calculates pip_value using point and contract_size
5. Sugar calculates raw volume using formula
6. Sugar rounds volume to volume_step
7. Sugar clamps to volume_min and volume_max
8. Returns final volume

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1724`
- Uses: get_balance (line 386), get_symbol_info (line 1615)

---

## When to Use

**Use `calculate_position_size()` when:**

- Implementing fixed percentage risk management
- Building automated trading systems
- Calculating safe position sizes
- Risk-based position sizing
- Following money management rules

**Don't use when:**

- Using fixed lot sizes
- Manual position sizing
- Not using stop loss
- Need more complex risk calculations
- Position size is predetermined

---

## 🔗 Examples

### Example 1: Basic 2% Risk Per Trade

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def risk_based_trading():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    risk_percent = 2.0  # Risk 2% per trade
    sl_pips = 50  # 50 pip stop loss

    # Calculate position size
    volume = await sugar.calculate_position_size(
        symbol,
        risk_percent,
        sl_pips
    )

    # Get account info
    balance = await sugar.get_balance()

    print(f"Account balance: ${balance:.2f}")
    print(f"Risk per trade: {risk_percent}% = ${balance * 0.02:.2f}")
    print(f"Stop loss: {sl_pips} pips")
    print(f"Position size: {volume} lots")

    # Place order with calculated size
    current_ask = await sugar.get_ask(symbol)
    sl_price = current_ask - (sl_pips * 0.0001)

    ticket = await sugar.buy_market_with_sltp(
        symbol,
        volume=volume,
        sl=sl_price
    )
    print(f"Order placed: {ticket}")

# Output:
# Account balance: $10000.00
# Risk per trade: 2.0% = $200.00
# Stop loss: 50 pips
# Position size: 0.4 lots
# Order placed: 123456789
```

### Example 2: Different Risk Levels

```python
async def compare_risk_levels():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    sl_pips = 30

    # Try different risk levels
    risk_levels = [0.5, 1.0, 2.0, 5.0]

    print(f"Position sizes for {symbol} with {sl_pips} pip SL:")

    for risk_pct in risk_levels:
        volume = await sugar.calculate_position_size(
            symbol,
            risk_pct,
            sl_pips
        )

        print(f"  {risk_pct}% risk: {volume} lots")

# Output:
# Position sizes for EURUSD with 30 pip SL:
#   0.5% risk: 0.17 lots
#   1.0% risk: 0.33 lots
#   2.0% risk: 0.67 lots
#   5.0% risk: 1.67 lots
```

### Example 3: Tight vs Wide Stop Loss

```python
async def compare_stop_losses():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    risk_percent = 2.0

    # Different stop loss sizes
    stop_losses = [20, 50, 100, 200]

    print(f"Position sizes at {risk_percent}% risk:")

    for sl_pips in stop_losses:
        volume = await sugar.calculate_position_size(
            symbol,
            risk_percent,
            sl_pips
        )

        print(f"  {sl_pips} pip SL: {volume} lots")

# Output:
# Position sizes at 2.0% risk:
#   20 pip SL: 1.0 lots
#   50 pip SL: 0.4 lots
#   100 pip SL: 0.2 lots
#   200 pip SL: 0.1 lots
```

---

## Common Pitfalls

**Pitfall 1: Using points instead of pips**
```python
# ERROR: sl_pips expects pips, not points
sl_points = 200  # 200 points = 20 pips for EURUSD

volume = await sugar.calculate_position_size("EURUSD", 2.0, sl_points)
# Calculates for 200 pips instead of 20 pips, volume will be 10x too small
```

**Solution:** Convert points to pips
```python
sl_points = 200
sl_pips = sl_points / 10  # 20 pips

volume = await sugar.calculate_position_size("EURUSD", 2.0, sl_pips)
```

**Pitfall 2: Not checking minimum volume**
```python
# Very tight SL or low risk might give volume < minimum
volume = await sugar.calculate_position_size("EURUSD", 0.1, 5)
# Returns volume_min (0.01) even if calculation gives 0.001
```

**Solution:** Check what you get
```python
volume = await sugar.calculate_position_size("EURUSD", 0.1, 5)

info = await sugar.get_symbol_info("EURUSD")
if volume == info.volume_min:
    print(f"Warning: Using minimum volume {volume}")
    print("Consider increasing risk% or widening stop loss")
```

**Pitfall 3: Balance changes during trading**
```python
# Calculated volume based on starting balance
volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)

# After several trades, balance changed
# But using old volume calculation
await sugar.buy_market("EURUSD", volume=volume)  # May risk more/less than 2%
```

**Solution:** Recalculate before each trade
```python
# Always calculate fresh before each trade
volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)

# Immediately use it
ticket = await sugar.buy_market("EURUSD", volume=volume)
```

---

## Pro Tips

**Tip 1: Safe position sizer with validation**
```python
async def safe_position_size(sugar, symbol, risk_pct, sl_pips):
    """Calculate position size with validation."""
    # Calculate
    volume = await sugar.calculate_position_size(symbol, risk_pct, sl_pips)

    # Get constraints
    info = await sugar.get_symbol_info(symbol)

    # Check if at minimum
    if volume == info.volume_min:
        print(f"WARNING: At minimum volume {volume}")
        print(f"Actual risk may be higher than {risk_pct}%")

    # Check if at maximum
    if volume == info.volume_max:
        print(f"WARNING: At maximum volume {volume}")
        print(f"Risk exceeds {risk_pct}% - reduce risk or widen SL")

    return volume

# Usage
volume = await safe_position_size(sugar, "EURUSD", 2.0, 50)
```

**Tip 2: Calculate actual dollar risk**
```python
async def show_dollar_risk(sugar, symbol, risk_pct, sl_pips):
    """Calculate and display dollar risk."""
    balance = await sugar.get_balance()
    volume = await sugar.calculate_position_size(symbol, risk_pct, sl_pips)

    # Get symbol info
    info = await sugar.get_symbol_info(symbol)

    # Calculate pip value
    pip_value = info.point * 10 * info.contract_size

    # Calculate dollar risk
    dollar_risk = sl_pips * pip_value * volume

    print(f"Balance: ${balance:.2f}")
    print(f"Risk: {risk_pct}% = ${balance * (risk_pct/100):.2f}")
    print(f"Volume: {volume} lots")
    print(f"SL: {sl_pips} pips")
    print(f"Actual risk: ${dollar_risk:.2f}")

# Usage
await show_dollar_risk(sugar, "EURUSD", 2.0, 50)
```

**Tip 3: Multi-position risk allocation**
```python
async def allocate_risk_to_positions(sugar, positions, total_risk_pct):
    """Allocate total risk across multiple positions."""
    # Divide risk equally
    risk_per_position = total_risk_pct / len(positions)

    sizes = {}
    for pos in positions:
        symbol = pos["symbol"]
        sl_pips = pos["sl_pips"]

        volume = await sugar.calculate_position_size(
            symbol,
            risk_per_position,
            sl_pips
        )

        sizes[symbol] = volume

    return sizes

# Usage
positions = [
    {"symbol": "EURUSD", "sl_pips": 50},
    {"symbol": "GBPUSD", "sl_pips": 60},
    {"symbol": "USDJPY", "sl_pips": 40}
]

sizes = await allocate_risk_to_positions(sugar, positions, total_risk_pct=6.0)
# Each position risks 2% (6% / 3 positions)

for symbol, volume in sizes.items():
    print(f"{symbol}: {volume} lots")
```

---

## 📚 See Also

- [calculate_required_margin](calculate_required_margin.md) - Calculate margin for position
- [can_open_position](can_open_position.md) - Check if position can be opened
- [get_balance](../2.%20Account_Properties/get_balance.md) - Get account balance
- [get_symbol_info](../9.%20Symbol_Information/get_symbol_info.md) - Get symbol parameters
