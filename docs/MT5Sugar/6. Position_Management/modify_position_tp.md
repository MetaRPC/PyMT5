# Modify Position Take Profit Only (`modify_position_tp`)

> **Sugar method:** Convenience method to modify only the Take Profit of a position.

**API Information:**

* **Method:** `sugar.modify_position_tp(ticket, tp)`
* **Returns:** `True` if modified successfully, `False` otherwise
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def modify_position_tp(self, ticket: int, tp: float) -> bool
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Yes | - | Position ticket number |
| `tp` | `float` | Yes | - | New Take Profit price |

---

## Return Value

| Type | Description |
|------|-------------|
| `bool` | `True` if modification successful (return_code == 10009), `False` otherwise |

**Raises:**
- `ValueError` if position with given ticket not found

---

## 🏛️ Essentials

**What it does:**

- Modifies only the Take Profit price
- Keeps Stop Loss unchanged
- Convenience wrapper around `modify_position_sltp()`
- Cleaner syntax for TP-only modifications

**Key behaviors:**

- Stop Loss remains unchanged
- Must respect broker's minimum stop level
- TP must be valid for position direction
- Internally calls `modify_position_sltp(ticket, sl=None, tp=tp)`

---

## ⚡ Under the Hood

```
MT5Sugar.modify_position_tp()
    ↓ calls
MT5Sugar.modify_position_sltp(ticket, sl=None, tp=tp)
    ↓ fetches position
MT5Service.get_opened_orders()
    ↓ builds OrderModifyRequest
MT5Service.modify_order()
    ↓ gRPC protobuf
TradingHelperService.OrderModify()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar calls modify_position_sltp() with tp parameter and sl=None
2. See [modify_position_sltp](modify_position_sltp.md) for full chain
3. Stop Loss value is preserved from current position

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1315`
- Internal call: `src/pymt5/mt5_sugar.py:1196`

---

## When to Use

**Use `modify_position_tp()` when:**

- Only need to change Take Profit
- Extending profit target
- Adding TP to position without TP
- Stop Loss should stay unchanged

**Don't use when:**

- Need to modify both SL and TP (use `modify_position_sltp()`)
- Only want to modify SL (use `modify_position_sl()`)

---

## 🔗 Examples

### Example 1: Add TP to Position

```python
from pymt5 import MT5Sugar

async def add_tp():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open position without TP
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=None  # No TP initially
    )

    print(f"Position opened: #{ticket} with SL only")

    # Later, add Take Profit
    entry = 1.0850
    tp_price = entry + 0.0100  # 100 pips TP

    success = await sugar.modify_position_tp(ticket, tp=tp_price)

    if success:
        print(f"TP added at {tp_price}")

```

### Example 2: Extend Profit Target

```python
async def extend_tp():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open with conservative TP
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=50  # Conservative 1:1 R/R
    )

    entry = await sugar.get_ask()
    initial_tp = entry + 0.0050

    print(f"Initial TP: {initial_tp} (50 pips)")

    # If trend continues, extend TP
    await asyncio.sleep(300)

    current = await sugar.get_bid()
    if current > entry + 0.0030:
        # Extend TP to 100 pips
        new_tp = entry + 0.0100

        success = await sugar.modify_position_tp(ticket, tp=new_tp)

        if success:
            print(f"TP extended to {new_tp} (100 pips)")

```

### Example 3: Dynamic TP Based on Volatility

```python
async def dynamic_tp():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open position
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=None
    )

    entry = await sugar.get_ask()

    # Calculate TP based on recent price movement (simplified)
    # In real scenario, use ATR or other volatility measure
    spread = await sugar.get_spread()
    volatility_multiplier = 3

    # Set TP to 3x current spread
    tp_distance = spread * volatility_multiplier
    tp_price = entry + tp_distance

    success = await sugar.modify_position_tp(ticket, tp=tp_price)

    if success:
        print(f"Dynamic TP set at {tp_price}")
        print(f"TP distance: {tp_distance:.5f}")

```

---

## Common Pitfalls

**Pitfall 1: Forgetting SL remains unchanged**
```python
# If position had SL at 1.0800, it stays at 1.0800
await sugar.modify_position_tp(ticket, tp=1.0950)

# SL is still 1.0800, not removed
```

**Solution:** To also modify SL, use modify_position_sltp()
```python
# Modify both
await sugar.modify_position_sltp(ticket, sl=1.0800, tp=1.0950)
```

**Pitfall 2: Wrong TP direction**
```python
# BUY position at 1.0850
ticket = await sugar.buy_market()

# ERROR: TP below entry price
await sugar.modify_position_tp(ticket, tp=1.0800)  # Wrong direction
```

**Solution:** Remember BUY: TP above entry
```python
await sugar.modify_position_tp(ticket, tp=1.0950)  # Correct
```

**Pitfall 3: Setting TP too close**
```python
# Broker requires minimum distance
bid = await sugar.get_bid()  # 1.0850

# ERROR: TP only 2 pips away (broker minimum is 10)
await sugar.modify_position_tp(ticket, tp=bid + 0.0002)
# Returns False
```

**Solution:** Respect broker's minimum stop level
```python
bid = await sugar.get_bid()

# Use at least broker minimum (e.g., 10 pips)
await sugar.modify_position_tp(ticket, tp=bid + 0.0010)
```

---

## Pro Tips

**Tip 1: Remove TP by setting to 0**
```python
# Remove Take Profit (keep SL)
await sugar.modify_position_tp(ticket, tp=0.0)
```

**Tip 2: Scale TP based on position size**
```python
# Larger positions = closer TP (less risk)
positions_data = await sugar._service.get_opened_orders()

for pos in positions_data.position_infos:
    if pos.volume >= 0.5:
        # Large position: conservative TP (50 pips)
        tp = pos.price_open + 0.0050
    else:
        # Small position: aggressive TP (100 pips)
        tp = pos.price_open + 0.0100

    # For BUY positions
    if pos.type == 0:  # BUY
        await sugar.modify_position_tp(pos.ticket, tp=tp)
```

**Tip 3: Progressive TP adjustment**
```python
# Extend TP as position moves in profit
entry = 1.0850
tps = [1.0900, 1.0950, 1.1000]  # Progressive targets

for new_tp in tps:
    # Wait for price to move closer to current TP
    while await sugar.get_bid() < new_tp - 0.0030:
        await asyncio.sleep(10)

    await sugar.modify_position_tp(ticket, tp=new_tp)
    print(f"TP extended to {new_tp}")
```

---

## 📚 See Also

- [modify_position_sl](modify_position_sl.md) - Modify only Stop Loss
- [modify_position_sltp](modify_position_sltp.md) - Modify both SL and TP
- [buy_market_with_sltp](../5.%20Trading_With_SLTP/buy_market_with_sltp.md) - Open with SL/TP
- [close_position](close_position.md) - Close position
