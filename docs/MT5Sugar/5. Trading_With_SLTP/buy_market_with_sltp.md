# Open BUY Position with SL/TP (`buy_market_with_sltp`)

> **Sugar method:** Opens BUY position at market with Stop Loss and Take Profit in one call.

**API Information:**

* **Method:** `sugar.buy_market_with_sltp(symbol, volume, sl, tp, sl_pips, tp_pips, comment, magic)`
* **Returns:** Position ticket number (`int`)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def buy_market_with_sltp(
    self,
    symbol: Optional[str] = None,
    volume: float = 0.01,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    sl_pips: Optional[float] = None,
    tp_pips: Optional[float] = None,
    comment: str = "",
    magic: int = 0
) -> int
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | No | `None` | Trading symbol (uses default if not specified) |
| `volume` | `float` | No | `0.01` | Position volume in lots |
| `sl` | `Optional[float]` | No | `None` | Stop Loss price (absolute price) |
| `tp` | `Optional[float]` | No | `None` | Take Profit price (absolute price) |
| `sl_pips` | `Optional[float]` | No | `None` | Stop Loss in pips (alternative to sl) |
| `tp_pips` | `Optional[float]` | No | `None` | Take Profit in pips (alternative to tp) |
| `comment` | `str` | No | `""` | Order comment (visible in terminal) |
| `magic` | `int` | No | `0` | Magic number for order identification |

---

## Return Value

| Type | Description |
|------|-------------|
| `int` | Position ticket number (unique identifier) |

**Raises:**

- `ValueError` if symbol not specified and no default set
- `RuntimeError` if order execution fails (returned_code != 10009)

---

## 🏛️ Essentials

**What it does:**

- Opens BUY position at current ASK price
- Sets Stop Loss and Take Profit automatically
- Supports both absolute prices and pips notation
- Calculates SL/TP from pips using symbol point value

**Key behaviors:**

- BUY: SL below entry, TP above entry
- Can use absolute prices (sl, tp) OR pips (sl_pips, tp_pips)
- Pips calculation: `price ± (pips × point × 10)`
- Fetches symbol info if pips used
- Default slippage: 10 points

---

## ⚡ Under the Hood

```
MT5Sugar.buy_market_with_sltp()
    ↓ fetches price
MT5Service.get_symbol_tick()
    ↓ if pips provided, fetches
MT5Sugar.get_symbol_info()
    ↓ calculates SL/TP prices
    ↓ builds OrderSendRequest with SL/TP
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar fetches current tick (ASK price)
2. If sl_pips or tp_pips provided, fetches symbol info for point value
3. Calculates SL/TP prices: SL = ask - (pips × point × 10), TP = ask + (pips × point × 10)
4. Builds OrderSendRequest with stop_loss and take_profit fields
5. Sends order through Service → Account → gRPC
6. Returns ticket number on success

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:824`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## When to Use

**Use `buy_market_with_sltp()` when:**

- Need risk management from entry (SL/TP required)
- Want to set SL/TP in pips (easier than calculating prices)
- Implementing automated strategies with fixed risk/reward
- Need position opened with protection immediately

**Don't use when:**

- Want to add SL/TP later (use `buy_market()` then `modify_position_sltp()`)
- Need complex order modification logic
- SL/TP not required initially

---

## 🔗 Examples

### Example 1: Using Pips (Recommended)

```python
from pymt5 import MT5Sugar

async def buy_with_pips():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open BUY with 50 pips SL and 100 pips TP
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,   # Stop Loss 50 pips below entry
        tp_pips=100,  # Take Profit 100 pips above entry
        comment="1:2 risk/reward"
    )

    print(f"BUY position opened: #{ticket}")
    print(f"SL: 50 pips, TP: 100 pips (1:2 R/R)")

# Output:
# BUY position opened: #123456795
# SL: 50 pips, TP: 100 pips (1:2 R/R)
```

### Example 2: Using Absolute Prices

```python
async def buy_with_prices():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Get current price
    ask = await sugar.get_ask()  # 1.0850

    # Open BUY with specific SL/TP prices
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl=1.0800,  # Stop Loss at 1.0800
        tp=1.0950,  # Take Profit at 1.0950
        comment="Support/Resistance levels"
    )

    print(f"BUY at {ask}")
    print(f"SL: 1.0800, TP: 1.0950")
```

### Example 3: Risk Management Strategy

```python
async def fixed_risk_trade():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Fixed risk: 1% account balance
    balance = await sugar.get_balance()
    risk_amount = balance * 0.01  # 1% risk

    # Calculate volume based on 50 pip SL
    # For EURUSD: 1 pip = $1 per 0.1 lot
    sl_pips = 50
    volume = risk_amount / (sl_pips * 10)  # Simplified

    # Open with 1:2 risk/reward
    ticket = await sugar.buy_market_with_sltp(
        volume=round(volume, 2),
        sl_pips=50,
        tp_pips=100,  # 2x reward
        comment=f"1% risk = ${risk_amount:.2f}"
    )

    print(f"Position: #{ticket}")
    print(f"Risk: ${risk_amount:.2f} (1% of ${balance})")
    print(f"Volume: {volume:.2f} lots")
```

---

## Common Pitfalls

**Pitfall 1: Mixing pips and prices**
```python
# ERROR: Don't mix sl/tp with sl_pips/tp_pips
ticket = await sugar.buy_market_with_sltp(
    sl=1.0800,      # Absolute price
    tp_pips=100     # Pips
)
# Both will be used, tp_pips overwrites tp
```

**Solution:** Use either absolute OR pips, not both
```python
# Option 1: All pips
ticket = await sugar.buy_market_with_sltp(sl_pips=50, tp_pips=100)

# Option 2: All absolute
ticket = await sugar.buy_market_with_sltp(sl=1.0800, tp=1.0950)
```

**Pitfall 2: Wrong SL/TP direction for BUY**
```python
# ERROR: SL above entry, TP below entry (backwards!)
ask = await sugar.get_ask()  # 1.0850

ticket = await sugar.buy_market_with_sltp(
    sl=1.0900,  # WRONG: SL above entry
    tp=1.0800   # WRONG: TP below entry
)
# Order will likely fail or trigger immediately
```

**Solution:** Remember BUY: SL below, TP above
```python
ask = await sugar.get_ask()  # 1.0850

ticket = await sugar.buy_market_with_sltp(
    sl=1.0800,  # Correct: SL below entry (50 pips)
    tp=1.0950   # Correct: TP above entry (100 pips)
)
```

**Pitfall 3: SL/TP too close to entry**
```python
# ERROR: Broker minimum stop level not respected
try:
    ticket = await sugar.buy_market_with_sltp(
        sl_pips=1,   # Too close (broker min is 10 pips)
        tp_pips=2
    )
except RuntimeError as e:
    print(e)  # "Order failed: Invalid stops"
```

**Solution:** Check broker's minimum stop level
```python
# Use reasonable SL/TP distances
ticket = await sugar.buy_market_with_sltp(
    sl_pips=20,   # Above broker minimum
    tp_pips=40
)
```

---

## Pro Tips

**Tip 1: Quick 1:2 risk/reward ratio**
```python
# Set TP to 2x SL for 1:2 R/R
sl_pips = 50
tp_pips = sl_pips * 2  # 100 pips

ticket = await sugar.buy_market_with_sltp(
    volume=0.1,
    sl_pips=sl_pips,
    tp_pips=tp_pips,
    comment="1:2 R/R"
)
```

**Tip 2: Use pips for consistent risk across symbols**
```python
# Same pip values work across different symbols
for symbol in ["EURUSD", "GBPUSD", "USDJPY"]:
    ticket = await sugar.buy_market_with_sltp(
        symbol=symbol,
        volume=0.01,
        sl_pips=50,
        tp_pips=100
    )
    print(f"{symbol} position: #{ticket}")
```

**Tip 3: Calculate actual risk amount**
```python
# Check actual dollar risk before trading
sl_pips = 50
volume = 0.1

# For EURUSD: 1 pip ≈ $1 per 0.1 lot
risk_dollars = sl_pips * (volume / 0.1) * 1

print(f"Risk: ${risk_dollars} for {volume} lots with {sl_pips} pip SL")

if risk_dollars <= 100:  # Max risk check
    ticket = await sugar.buy_market_with_sltp(
        volume=volume,
        sl_pips=sl_pips,
        tp_pips=sl_pips * 2
    )
```

---

## 📚 See Also

- [sell_market_with_sltp](sell_market_with_sltp.md) - Open SELL with SL/TP
- [buy_limit_with_sltp](buy_limit_with_sltp.md) - BUY LIMIT with SL/TP
- [buy_market](../4.%20Simple_Trading/buy_market.md) - Open BUY without SL/TP
- [modify_position_sltp](../6.%20Position_Management/modify_position_sltp.md) - Modify SL/TP after opening
