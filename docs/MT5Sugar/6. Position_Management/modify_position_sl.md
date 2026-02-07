# Modify Position Stop Loss Only (`modify_position_sl`)

> **Sugar method:** Convenience method to modify only the Stop Loss of a position.

**API Information:**

* **Method:** `sugar.modify_position_sl(ticket, sl)`
* **Returns:** `True` if modified successfully, `False` otherwise
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def modify_position_sl(self, ticket: int, sl: float) -> bool
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Yes | - | Position ticket number |
| `sl` | `float` | Yes | - | New Stop Loss price |

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

- Modifies only the Stop Loss price
- Keeps Take Profit unchanged
- Convenience wrapper around `modify_position_sltp()`
- Cleaner syntax for SL-only modifications

**Key behaviors:**

- Take Profit remains unchanged
- Must respect broker's minimum stop level
- SL must be valid for position direction
- Internally calls `modify_position_sltp(ticket, sl=sl, tp=None)`

---

## ⚡ Under the Hood

```
MT5Sugar.modify_position_sl()
    ↓ calls
MT5Sugar.modify_position_sltp(ticket, sl=sl, tp=None)
    ↓ fetches position
MT5Service.get_opened_orders()
    ↓ builds OrderModifyRequest
MT5Service.modify_order()
    ↓ gRPC protobuf
TradingHelperService.OrderModify()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar calls modify_position_sltp() with sl parameter and tp=None
2. See [modify_position_sltp](modify_position_sltp.md) for full chain
3. Take Profit value is preserved from current position

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1299`
- Internal call: `src/pymt5/mt5_sugar.py:1196`

---

## When to Use

**Use `modify_position_sl()` when:**

- Only need to change Stop Loss
- Implementing trailing stops
- Moving SL to breakeven
- Take Profit should stay unchanged

**Don't use when:**

- Need to modify both SL and TP (use `modify_position_sltp()`)
- Only want to modify TP (use `modify_position_tp()`)

---

## 🔗 Examples

### Example 1: Move SL to Breakeven

```python
from pymt5 import MT5Sugar

async def breakeven_sl():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open position at 1.0850
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=100
    )

    entry_price = await sugar.get_ask()  # 1.0850

    # Wait for 30 pips profit
    while True:
        current = await sugar.get_bid()

        if current >= entry_price + 0.0030:
            # Move SL to breakeven (TP stays at original target)
            success = await sugar.modify_position_sl(ticket, sl=entry_price)

            if success:
                print(f"SL moved to breakeven: {entry_price}")
                break

        await asyncio.sleep(5)

```

### Example 2: Tighten Stop Loss

```python
async def tighten_sl():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open with 50 pip SL
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=100
    )

    entry = await sugar.get_ask()
    initial_sl = entry - 0.0050  # 50 pips

    print(f"Initial SL: {initial_sl}")

    # After some time, tighten to 30 pips
    await asyncio.sleep(300)

    new_sl = entry - 0.0030  # 30 pips
    success = await sugar.modify_position_sl(ticket, sl=new_sl)

    if success:
        print(f"SL tightened to: {new_sl}")

```

### Example 3: Simple Trailing Stop

```python
async def simple_trailing():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open position
    ticket = await sugar.buy_market(volume=0.1)

    entry = await sugar.get_ask()
    trail_distance = 0.0030  # 30 pips

    current_sl = entry - 0.0050  # Initial SL
    await sugar.modify_position_sl(ticket, sl=current_sl)

    # Trail the stop
    highest = entry

    while True:
        price = await sugar.get_bid()

        if price > highest:
            highest = price
            new_sl = highest - trail_distance

            # Only move SL up
            if new_sl > current_sl:
                success = await sugar.modify_position_sl(ticket, sl=new_sl)

                if success:
                    current_sl = new_sl
                    print(f"SL trailed to: {new_sl:.5f}")

        await asyncio.sleep(5)

```

---

## Common Pitfalls

**Pitfall 1: Forgetting TP remains unchanged**
```python
# If position had TP at 1.0950, it stays at 1.0950
await sugar.modify_position_sl(ticket, sl=1.0800)

# TP is still 1.0950, not removed
```

**Solution:** To also modify TP, use modify_position_sltp()
```python
# Modify both
await sugar.modify_position_sltp(ticket, sl=1.0800, tp=1.1000)
```

**Pitfall 2: Wrong SL direction**
```python
# BUY position at 1.0850
ticket = await sugar.buy_market()

# ERROR: SL above entry price
await sugar.modify_position_sl(ticket, sl=1.0900)  # Wrong direction
```

**Solution:** Remember BUY: SL below entry
```python
await sugar.modify_position_sl(ticket, sl=1.0800)  # Correct
```

**Pitfall 3: Not checking return value**
```python
# Modification may fail (broker limits, etc.)
await sugar.modify_position_sl(ticket, sl=1.0800)
# SL may not have changed if it failed
```

**Solution:** Check return value
```python
success = await sugar.modify_position_sl(ticket, sl=1.0800)

if not success:
    print("SL modification failed")
```

---

## Pro Tips

**Tip 1: Remove SL by setting to 0**
```python
# Remove Stop Loss (keep TP)
await sugar.modify_position_sl(ticket, sl=0.0)
```

**Tip 2: Batch modify SL for all positions**
```python
# Move all positions to breakeven
positions_data = await sugar._service.get_opened_orders()

for pos in positions_data.position_infos:
    if pos.profit > 0:
        # Move SL to entry price
        await sugar.modify_position_sl(pos.ticket, sl=pos.price_open)
        print(f"Position #{pos.ticket} moved to breakeven")
```

**Tip 3: Incremental SL tightening**
```python
# Gradually tighten SL as price moves
entry = 1.0850
stops = [1.0830, 1.0840, 1.0845, 1.0850]  # Progressively tighter

for new_sl in stops:
    # Wait for price to justify tighter SL
    while await sugar.get_bid() < new_sl + 0.0030:
        await asyncio.sleep(10)

    await sugar.modify_position_sl(ticket, sl=new_sl)
    print(f"SL tightened to {new_sl}")
```

---

## 📚 See Also

- [modify_position_tp](modify_position_tp.md) - Modify only Take Profit
- [modify_position_sltp](modify_position_sltp.md) - Modify both SL and TP
- [buy_market_with_sltp](../5.%20Trading_With_SLTP/buy_market_with_sltp.md) - Open with SL/TP
- [close_position](close_position.md) - Close position
