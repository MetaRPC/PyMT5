# Place SELL LIMIT with SL/TP (`sell_limit_with_sltp`)

> **Sugar method:** Places SELL LIMIT pending order with Stop Loss and Take Profit.

**API Information:**

* **Method:** `sugar.sell_limit_with_sltp(symbol, volume, price, sl, tp, sl_pips, tp_pips, comment, magic)`
* **Returns:** Order ticket number (`int`)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def sell_limit_with_sltp(
    self,
    symbol: Optional[str] = None,
    volume: float = 0.01,
    price: float = 0.0,
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
| `volume` | `float` | No | `0.01` | Order volume in lots |
| `price` | `float` | Yes | `0.0` | Limit price (must be ABOVE current BID) |
| `sl` | `Optional[float]` | No | `None` | Stop Loss price (absolute price) |
| `tp` | `Optional[float]` | No | `None` | Take Profit price (absolute price) |
| `sl_pips` | `Optional[float]` | No | `None` | Stop Loss in pips from entry (alternative to sl) |
| `tp_pips` | `Optional[float]` | No | `None` | Take Profit in pips from entry (alternative to tp) |
| `comment` | `str` | No | `""` | Order comment (visible in terminal) |
| `magic` | `int` | No | `0` | Magic number for order identification |

---

## Return Value

| Type | Description |
|------|-------------|
| `int` | Order ticket number (unique identifier) |

**Raises:**

- `ValueError` if symbol not specified and no default set
- `RuntimeError` if order placement fails (returned_code != 10009)

---

## 🏛️ Essentials

**What it does:**

- Places SELL LIMIT order above current price
- Sets SL/TP on the pending order
- When order fills, SL/TP automatically active
- Supports both absolute prices and pips from entry

**Key behaviors:**

- SELL LIMIT price must be ABOVE current BID
- SL/TP calculated from entry price (not current price)
- SELL: SL above entry, TP below entry
- Pips calculation uses entry price as reference
- Order stays pending until price reached

---

## ⚡ Under the Hood

```
MT5Sugar.sell_limit_with_sltp()
    ↓ if pips provided, fetches
MT5Sugar.get_symbol_info()
    ↓ calculates SL/TP from entry price
    ↓ builds OrderSendRequest with SL/TP
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar validates entry price parameter
2. If sl_pips or tp_pips provided, fetches symbol info for point value
3. Calculates SL/TP from entry price: SL = price + (pips × point × 10), TP = price - (pips × point × 10)
4. Builds OrderSendRequest with TMT5_ORDER_TYPE_SELL_LIMIT and SL/TP
5. Sends order through Service → Account → gRPC
6. Returns order ticket, order stays pending

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1059`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## When to Use

**Use `sell_limit_with_sltp()` when:**

- Want to sell at higher price with automatic risk management
- Planning entry with predefined SL/TP
- Sell the rally strategy with protection
- Setting up orders before market moves

**Don't use when:**

- Need immediate entry (use `sell_market_with_sltp()`)
- Want to modify SL/TP after order fills
- Price may never reach limit level

---

## 🔗 Examples

### Example 1: Sell Rally with Pips Protection

```python
from pymt5 import MT5Sugar

async def sell_rally_protected():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Current BID: 1.0850
    # Place SELL LIMIT at 1.0870 with SL/TP
    ticket = await sugar.sell_limit_with_sltp(
        price=1.0870,
        volume=0.1,
        sl_pips=50,   # 50 pips above 1.0870 entry
        tp_pips=100,  # 100 pips below 1.0870 entry
        comment="Sell rally protected"
    )

    print(f"SELL LIMIT order: #{ticket} at 1.0870")
    print(f"When filled: SL=1.0920, TP=1.0770")
```

### Example 2: Resistance Level Entry

```python
async def sell_at_resistance():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Resistance at 1.0900
    resistance = 1.0900

    # Place SELL LIMIT at resistance with absolute SL/TP
    ticket = await sugar.sell_limit_with_sltp(
        price=resistance,
        volume=0.1,
        sl=resistance + 0.0030,  # SL 30 pips above resistance
        tp=resistance - 0.0100,  # TP 100 pips below
        comment="Resistance rejection"
    )

    print(f"Order at resistance {resistance}: #{ticket}")
```

### Example 3: Profit Target Ladder

```python
async def profit_ladder():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open SELL position first
    sell_ticket = await sugar.sell_market(volume=0.3)

    # Then place SELL LIMIT orders as profit targets
    bid = await sugar.get_bid()  # 1.0850

    targets = [
        (0.1, bid + 0.0030, 50),   # +30 pips: close 0.1, SL 50
        (0.1, bid + 0.0050, 30),   # +50 pips: close 0.1, SL 30
        (0.1, bid + 0.0100, 20)    # +100 pips: close 0.1, SL 20
    ]

    tickets = []
    for volume, entry, sl_pips in targets:
        ticket = await sugar.sell_limit_with_sltp(
            price=entry,
            volume=volume,
            sl_pips=sl_pips,
            tp_pips=50,
            comment=f"Target at {entry}"
        )
        tickets.append(ticket)
        print(f"Profit target #{ticket} at {entry}")
```

---

## Common Pitfalls

**Pitfall 1: Entry price below current BID**
```python
# ERROR: SELL LIMIT must be ABOVE current price
bid = await sugar.get_bid()  # 1.0850

try:
    ticket = await sugar.sell_limit_with_sltp(
        price=1.0840,  # Below current BID
        sl_pips=50,
        tp_pips=100
    )
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price"
```

**Solution:** Ensure limit price above current BID
```python
bid = await sugar.get_bid()  # 1.0850
entry_price = bid + 0.0020   # 1.0870 (above)

ticket = await sugar.sell_limit_with_sltp(
    price=entry_price,
    sl_pips=50,
    tp_pips=100
)
```

**Pitfall 2: Wrong SL/TP direction for SELL**
```python
# ERROR: SL below entry, TP above entry (backwards!)
ticket = await sugar.sell_limit_with_sltp(
    price=1.0870,
    sl=1.0850,  # WRONG: Below entry
    tp=1.0900   # WRONG: Above entry
)
```

**Solution:** SELL = SL above, TP below
```python
entry = 1.0870

ticket = await sugar.sell_limit_with_sltp(
    price=entry,
    sl=entry + 0.0050,  # Above entry (1.0920)
    tp=entry - 0.0100   # Below entry (1.0770)
)
```

**Pitfall 3: Calculating from current price instead of entry**
```python
# WRONG: SL/TP relative to current, not entry
bid = await sugar.get_bid()  # 1.0850
entry = 1.0870

ticket = await sugar.sell_limit_with_sltp(
    price=entry,
    sl=bid + 0.0050,  # WRONG: From current (1.0900)
    tp=bid - 0.0100   # WRONG: From current (1.0750)
)
# When order fills at 1.0870, SL is only 30 pips away!
```

**Solution:** Use pips or calculate from entry price
```python
entry = 1.0870

# Option 1: Use pips (automatic)
ticket = await sugar.sell_limit_with_sltp(
    price=entry,
    sl_pips=50,   # 50 pips from entry
    tp_pips=100   # 100 pips from entry
)

# Option 2: Calculate from entry
ticket = await sugar.sell_limit_with_sltp(
    price=entry,
    sl=entry + 0.0050,  # From entry
    tp=entry - 0.0100   # From entry
)
```

---

## Pro Tips

**Tip 1: Pre-place orders at key levels**
```python
# Place orders before market reaches resistance
resistances = [1.0900, 1.0950, 1.1000]

tickets = []
for resistance in resistances:
    ticket = await sugar.sell_limit_with_sltp(
        price=resistance,
        volume=0.01,
        sl_pips=50,
        tp_pips=100,
        comment=f"R at {resistance}"
    )
    tickets.append(ticket)

print(f"Placed {len(tickets)} resistance orders")
```

**Tip 2: Dynamic SL based on entry distance**
```python
# Tighter SL for closer targets
bid = await sugar.get_bid()  # 1.0850

targets = [
    (1.0860, 30),  # Close target = tight SL
    (1.0880, 40),  # Medium target = medium SL
    (1.0900, 50)   # Far target = wider SL
]

for entry, sl_pips in targets:
    ticket = await sugar.sell_limit_with_sltp(
        price=entry,
        volume=0.01,
        sl_pips=sl_pips,
        tp_pips=100,
        comment=f"Entry {entry}, SL {sl_pips}"
    )
```

**Tip 3: Combine with position scaling**
```python
# Open small position, add more with limits
initial = await sugar.sell_market_with_sltp(
    volume=0.05,
    sl_pips=50,
    tp_pips=150
)

# Add more if price rallies to resistance
bid = await sugar.get_bid()
add_on = await sugar.sell_limit_with_sltp(
    price=bid + 0.0020,  # 20 pips above
    volume=0.05,
    sl_pips=50,
    tp_pips=150,
    comment="Add-on position"
)

print(f"Initial: #{initial}, Add-on: #{add_on}")
```

---

## 📚 See Also

- [buy_limit_with_sltp](buy_limit_with_sltp.md) - BUY LIMIT with SL/TP
- [sell_market_with_sltp](sell_market_with_sltp.md) - SELL at market with SL/TP
- [sell_limit](../4.%20Simple_Trading/sell_limit.md) - SELL LIMIT without SL/TP
- [modify_position_sltp](../6.%20Position_Management/modify_position_sltp.md) - Modify SL/TP after fill
