# Open SELL Position with SL/TP (`sell_market_with_sltp`)

> **Sugar method:** Opens SELL position at market with Stop Loss and Take Profit in one call.

**API Information:**

* **Method:** `sugar.sell_market_with_sltp(symbol, volume, sl, tp, sl_pips, tp_pips, comment, magic)`
* **Returns:** Position ticket number (`int`)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def sell_market_with_sltp(
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

- Opens SELL position at current BID price
- Sets Stop Loss and Take Profit automatically
- Supports both absolute prices and pips notation
- Calculates SL/TP from pips using symbol point value

**Key behaviors:**

- SELL: SL above entry, TP below entry
- Can use absolute prices (sl, tp) OR pips (sl_pips, tp_pips)
- Pips calculation: SL = bid + (pips × point × 10), TP = bid - (pips × point × 10)
- Fetches symbol info if pips used
- Default slippage: 10 points

---

## ⚡ Under the Hood

```
MT5Sugar.sell_market_with_sltp()
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

1. Sugar fetches current tick (BID price)
2. If sl_pips or tp_pips provided, fetches symbol info for point value
3. Calculates SL/TP prices: SL = bid + (pips × point × 10), TP = bid - (pips × point × 10)
4. Builds OrderSendRequest with stop_loss and take_profit fields
5. Sends order through Service → Account → gRPC
6. Returns ticket number on success

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:903`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/helpers/mt5_account.py:1713`

---

## When to Use

**Use `sell_market_with_sltp()` when:**

- Need risk management from entry (SL/TP required)
- Want to set SL/TP in pips (easier than calculating prices)
- Implementing automated strategies with fixed risk/reward
- Expecting price to fall with defined risk

**Don't use when:**

- Want to add SL/TP later (use `sell_market()` then `modify_position_sltp()`)
- Need complex order modification logic
- SL/TP not required initially

---

## 🔗 Examples

### Example 1: Using Pips (Recommended)

```python
from pymt5 import MT5Sugar

async def sell_with_pips():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open SELL with 50 pips SL and 100 pips TP
    ticket = await sugar.sell_market_with_sltp(
        volume=0.1,
        sl_pips=50,   # Stop Loss 50 pips above entry
        tp_pips=100,  # Take Profit 100 pips below entry
        comment="1:2 risk/reward"
    )

    print(f"SELL position opened: #{ticket}")
    print(f"SL: 50 pips, TP: 100 pips (1:2 R/R)")

# Output:
# SELL position opened: #123456796
# SL: 50 pips, TP: 100 pips (1:2 R/R)
```

### Example 2: Using Absolute Prices

```python
async def sell_with_prices():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Get current price
    bid = await sugar.get_bid()  # 1.0850

    # Open SELL with specific SL/TP prices
    ticket = await sugar.sell_market_with_sltp(
        volume=0.1,
        sl=1.0900,  # Stop Loss at 1.0900 (above entry)
        tp=1.0750,  # Take Profit at 1.0750 (below entry)
        comment="Resistance/Support levels"
    )

    print(f"SELL at {bid}")
    print(f"SL: 1.0900, TP: 1.0750")
```

### Example 3: Downtrend Strategy

```python
async def downtrend_trade():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Check if in downtrend (simplified)
    bid = await sugar.get_bid()

    # Open SELL expecting continuation
    ticket = await sugar.sell_market_with_sltp(
        volume=0.1,
        sl_pips=40,   # Tight stop
        tp_pips=120,  # 3x reward
        comment="Downtrend continuation"
    )

    print(f"SELL position: #{ticket}")
    print(f"Risk/Reward: 1:3")

    # Monitor position
    floating_profit = await sugar.get_floating_profit()
    print(f"Current P&L: ${floating_profit:.2f}")
```

---

## Common Pitfalls

**Pitfall 1: Wrong SL/TP direction for SELL**
```python
# ERROR: SL below entry, TP above entry (backwards!)
bid = await sugar.get_bid()  # 1.0850

ticket = await sugar.sell_market_with_sltp(
    sl=1.0800,  # WRONG: SL below entry
    tp=1.0900   # WRONG: TP above entry
)
# Order will likely fail or trigger immediately
```

**Solution:** Remember SELL: SL above, TP below
```python
bid = await sugar.get_bid()  # 1.0850

ticket = await sugar.sell_market_with_sltp(
    sl=1.0900,  # Correct: SL above entry (50 pips)
    tp=1.0750   # Correct: TP below entry (100 pips)
)
```

**Pitfall 2: Confusing BUY and SELL SL/TP logic**
```python
# BUY: SL below, TP above
buy_ticket = await sugar.buy_market_with_sltp(
    sl_pips=50,  # 50 pips BELOW entry
    tp_pips=100  # 100 pips ABOVE entry
)

# SELL: SL above, TP below (opposite!)
sell_ticket = await sugar.sell_market_with_sltp(
    sl_pips=50,  # 50 pips ABOVE entry
    tp_pips=100  # 100 pips BELOW entry
)
```

**Pitfall 3: Using same absolute prices for multiple trades**
```python
# ERROR: Market moved, old SL/TP prices invalid
first_bid = await sugar.get_bid()  # 1.0850
ticket1 = await sugar.sell_market_with_sltp(
    sl=1.0900,
    tp=1.0750
)

# 1 hour later, price at 1.0800
ticket2 = await sugar.sell_market_with_sltp(
    sl=1.0900,  # Still valid but very far (100 pips!)
    tp=1.0750   # Already hit! Order fails
)
```

**Solution:** Use pips for consistent behavior
```python
# Works regardless of current price
ticket1 = await sugar.sell_market_with_sltp(sl_pips=50, tp_pips=100)

# Later, still works correctly
ticket2 = await sugar.sell_market_with_sltp(sl_pips=50, tp_pips=100)
```

---

## Pro Tips

**Tip 1: Trailing SELL with improving entry**
```python
# If price moving down, wait for better entry
initial_bid = await sugar.get_bid()  # 1.0850

# Wait 60 seconds
await asyncio.sleep(60)

new_bid = await sugar.get_bid()  # 1.0840

# Better entry (price dropped)
if new_bid < initial_bid:
    ticket = await sugar.sell_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=100,
        comment="Improved entry"
    )
```

**Tip 2: Combine with resistance levels**
```python
# Sell at resistance with SL above resistance
resistance = 1.0900
bid = await sugar.get_bid()

# Only trade if near resistance
if abs(bid - resistance) < 0.0010:  # Within 10 pips
    ticket = await sugar.sell_market_with_sltp(
        volume=0.1,
        sl=resistance + 0.0010,  # SL 10 pips above resistance
        tp=resistance - 0.0100,  # TP 100 pips below
        comment="Sell at resistance"
    )
```

**Tip 3: Scale in with multiple positions**
```python
# Open multiple SELL positions with different TP levels
base_sl_pips = 50

tickets = []
for i in range(3):
    tp_pips = 50 + (i * 25)  # 50, 75, 100 pips TP

    ticket = await sugar.sell_market_with_sltp(
        volume=0.01,
        sl_pips=base_sl_pips,
        tp_pips=tp_pips,
        comment=f"Scaled TP {tp_pips}"
    )
    tickets.append(ticket)

print(f"Opened {len(tickets)} scaled positions")
```

---

## 📚 See Also

- [buy_market_with_sltp](buy_market_with_sltp.md) - Open BUY with SL/TP
- [sell_limit_with_sltp](sell_limit_with_sltp.md) - SELL LIMIT with SL/TP
- [sell_market](../4.%20Simple_Trading/sell_market.md) - Open SELL without SL/TP
- [modify_position_sltp](../6.%20Position_Management/modify_position_sltp.md) - Modify SL/TP after opening
