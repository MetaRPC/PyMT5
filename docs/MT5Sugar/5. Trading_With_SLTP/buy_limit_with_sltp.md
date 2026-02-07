# Place BUY LIMIT with SL/TP (`buy_limit_with_sltp`)

> **Sugar method:** Places BUY LIMIT pending order with Stop Loss and Take Profit.

**API Information:**

* **Method:** `sugar.buy_limit_with_sltp(symbol, volume, price, sl, tp, sl_pips, tp_pips, comment, magic)`
* **Returns:** Order ticket number (`int`)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def buy_limit_with_sltp(
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
| `price` | `float` | Yes | `0.0` | Limit price (must be BELOW current ASK) |
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

- Places BUY LIMIT order below current price
- Sets SL/TP on the pending order
- When order fills, SL/TP automatically active
- Supports both absolute prices and pips from entry

**Key behaviors:**

- BUY LIMIT price must be BELOW current ASK
- SL/TP calculated from entry price (not current price)
- BUY: SL below entry, TP above entry
- Pips calculation uses entry price as reference
- Order stays pending until price reached

---

## ⚡ Under the Hood

```
MT5Sugar.buy_limit_with_sltp()
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
3. Calculates SL/TP from entry price: SL = price - (pips × point × 10), TP = price + (pips × point × 10)
4. Builds OrderSendRequest with TMT5_ORDER_TYPE_BUY_LIMIT and SL/TP
5. Sends order through Service → Account → gRPC
6. Returns order ticket, order stays pending

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:984`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/helpers/mt5_account.py:1713`

---

## When to Use

**Use `buy_limit_with_sltp()` when:**

- Want to buy at lower price with automatic risk management
- Planning entry with predefined SL/TP
- Buy the dip strategy with protection
- Setting up orders before market moves

**Don't use when:**

- Need immediate entry (use `buy_market_with_sltp()`)
- Want to modify SL/TP after order fills
- Price may never reach limit level

---

## 🔗 Examples

### Example 1: Buy Dip with Pips Protection

```python
from pymt5 import MT5Sugar

async def buy_dip_protected():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Current ASK: 1.0850
    # Place BUY LIMIT at 1.0840 with SL/TP
    ticket = await sugar.buy_limit_with_sltp(
        price=1.0840,
        volume=0.1,
        sl_pips=50,   # 50 pips below 1.0840 entry
        tp_pips=100,  # 100 pips above 1.0840 entry
        comment="Buy dip protected"
    )

    print(f"BUY LIMIT order: #{ticket} at 1.0840")
    print(f"When filled: SL=1.0790, TP=1.0940")
```

### Example 2: Support Level Entry

```python
async def buy_at_support():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Support at 1.0820
    support = 1.0820

    # Place BUY LIMIT at support with absolute SL/TP
    ticket = await sugar.buy_limit_with_sltp(
        price=support,
        volume=0.1,
        sl=support - 0.0030,  # SL 30 pips below support
        tp=support + 0.0100,  # TP 100 pips above
        comment="Support bounce"
    )

    print(f"Order at support {support}: #{ticket}")
```

### Example 3: Grid Trading with Protection

```python
async def protected_grid():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Current ASK: 1.0850
    # Place grid of BUY LIMIT orders below
    base_price = 1.0840
    grid_step = 0.0010  # 10 pips

    tickets = []
    for i in range(5):
        entry_price = base_price - (i * grid_step)

        ticket = await sugar.buy_limit_with_sltp(
            price=entry_price,
            volume=0.01,
            sl_pips=50,
            tp_pips=100,
            comment=f"Grid {i+1} at {entry_price}"
        )
        tickets.append(ticket)
        print(f"Grid order #{ticket} at {entry_price}")

    print(f"Total grid orders: {len(tickets)}")
```

---

## Common Pitfalls

**Pitfall 1: Using current price for SL/TP calculation**
```python
# WRONG: Calculating SL/TP from current price
ask = await sugar.get_ask()  # 1.0850
entry_price = 1.0840

# ERROR: SL/TP should be relative to entry (1.0840), not current (1.0850)
ticket = await sugar.buy_limit_with_sltp(
    price=entry_price,
    sl=ask - 0.0050,  # WRONG: Based on current price
    tp=ask + 0.0100   # WRONG: Based on current price
)
```

**Solution:** Calculate SL/TP from entry price or use pips
```python
entry_price = 1.0840

# Option 1: Use pips (automatic calculation from entry)
ticket = await sugar.buy_limit_with_sltp(
    price=entry_price,
    sl_pips=50,
    tp_pips=100
)

# Option 2: Calculate from entry price
ticket = await sugar.buy_limit_with_sltp(
    price=entry_price,
    sl=entry_price - 0.0050,  # From entry
    tp=entry_price + 0.0100   # From entry
)
```

**Pitfall 2: Entry price above current ASK**
```python
# ERROR: BUY LIMIT must be BELOW current price
ask = await sugar.get_ask()  # 1.0850

try:
    ticket = await sugar.buy_limit_with_sltp(
        price=1.0860,  # Above current ASK
        sl_pips=50,
        tp_pips=100
    )
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price"
```

**Solution:** Ensure limit price below current ASK
```python
ask = await sugar.get_ask()  # 1.0850
entry_price = ask - 0.0010   # 1.0840 (below)

ticket = await sugar.buy_limit_with_sltp(
    price=entry_price,
    sl_pips=50,
    tp_pips=100
)
```

**Pitfall 3: Forgetting SL/TP direction**
```python
# ERROR: SL above entry, TP below entry (backwards!)
ticket = await sugar.buy_limit_with_sltp(
    price=1.0840,
    sl=1.0850,  # WRONG: Above entry
    tp=1.0830   # WRONG: Below entry
)
```

**Solution:** BUY = SL below, TP above
```python
entry = 1.0840

ticket = await sugar.buy_limit_with_sltp(
    price=entry,
    sl=entry - 0.0050,  # Below entry
    tp=entry + 0.0100   # Above entry
)
```

---

## Pro Tips

**Tip 1: Use pips for clean orders**
```python
# Pips automatically calculate correct SL/TP from entry
ticket = await sugar.buy_limit_with_sltp(
    price=1.0840,
    volume=0.1,
    sl_pips=50,   # Will be 1.0790
    tp_pips=100,  # Will be 1.0940
    comment="Clean setup"
)
```

**Tip 2: Place orders ahead of known levels**
```python
# Economic calendar: support at 1.0820
# Place order before market reaches level
ticket = await sugar.buy_limit_with_sltp(
    price=1.0820,
    volume=0.1,
    sl_pips=30,
    tp_pips=90,
    comment="Pre-placed at support"
)
# Order waits until price drops to 1.0820
```

**Tip 3: Check order status later**
```python
# Place order
ticket = await sugar.buy_limit_with_sltp(
    price=1.0840,
    sl_pips=50,
    tp_pips=100
)

# Later: check if filled
positions = await sugar._service.get_opened_orders()

filled = False
for pos in positions.position_infos:
    if pos.ticket == ticket:
        filled = True
        print(f"Order #{ticket} filled and now a position")
        break

if not filled:
    print(f"Order #{ticket} still pending")
```

---

## 📚 See Also

- [sell_limit_with_sltp](sell_limit_with_sltp.md) - SELL LIMIT with SL/TP
- [buy_market_with_sltp](buy_market_with_sltp.md) - BUY at market with SL/TP
- [buy_limit](../4.%20Simple_Trading/buy_limit.md) - BUY LIMIT without SL/TP
- [modify_position_sltp](../6.%20Position_Management/modify_position_sltp.md) - Modify SL/TP after fill
