# Modify Position SL/TP (`modify_position_sltp`)

> **Sugar method:** Modifies Stop Loss and/or Take Profit of an open position.

**API Information:**

* **Method:** `sugar.modify_position_sltp(ticket, sl, tp)`
* **Returns:** `True` if modified successfully, `False` otherwise
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def modify_position_sltp(
    self,
    ticket: int,
    sl: Optional[float] = None,
    tp: Optional[float] = None
) -> bool
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Yes | - | Position ticket number |
| `sl` | `Optional[float]` | No | `None` | New Stop Loss price (None to keep current) |
| `tp` | `Optional[float]` | No | `None` | New Take Profit price (None to keep current) |

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

- Fetches current position by ticket
- Modifies Stop Loss and/or Take Profit
- Preserves unmodified values
- Validates modification with terminal

**Key behaviors:**

- Pass `None` to keep current SL or TP unchanged
- Must respect broker's minimum stop level
- SL/TP must be valid for position direction
- Returns False if modification failed

---

## ⚡ Under the Hood

```
MT5Sugar.modify_position_sltp()
    ↓ fetches position
MT5Service.get_opened_orders()
    ↓ finds position, preserves current SL/TP
    ↓ builds OrderModifyRequest
MT5Service.modify_order()
    ↓ calls
MT5Account.order_modify()
    ↓ gRPC protobuf
TradingHelperService.OrderModify()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar fetches all positions via Service.get_opened_orders()
2. Sugar searches for position with matching ticket
3. If not found, raises ValueError
4. Sugar preserves current SL/TP if new values are None
5. Sugar creates OrderModifyRequest with ticket and new SL/TP
6. Sugar calls Service.modify_order()
7. Service forwards to Account.order_modify()
8. Returns True if returned_code == 10009, False otherwise

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1196`
- Service: `src/pymt5/mt5_service.py:963`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1758`

---

## When to Use

**Use `modify_position_sltp()` when:**

- Adjusting Stop Loss after position moves in profit
- Setting Take Profit after opening position
- Implementing trailing stop strategies
- Risk management adjustments

**Don't use when:**

- Want to modify only SL (use `modify_position_sl()` for clarity)
- Want to modify only TP (use `modify_position_tp()` for clarity)
- Position already closed

---

## 🔗 Examples

### Example 1: Add SL/TP to Existing Position

```python
from pymt5 import MT5Sugar

async def add_stops():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open position without SL/TP
    ticket = await sugar.buy_market(volume=0.1)
    print(f"Position opened: #{ticket}")

    # Add SL/TP after opening
    success = await sugar.modify_position_sltp(
        ticket=ticket,
        sl=1.0800,  # Stop Loss at 1.0800
        tp=1.0950   # Take Profit at 1.0950
    )

    if success:
        print("SL/TP added successfully")
    else:
        print("Failed to add SL/TP")

```

### Example 2: Move Stop Loss to Breakeven

```python
async def breakeven_stop():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open BUY position at 1.0850
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,   # Initial SL 50 pips
        tp_pips=100
    )

    entry_price = await sugar.get_ask()  # 1.0850

    # Monitor position
    while True:
        current_price = await sugar.get_bid()

        # Move SL to breakeven when in 30 pips profit
        if current_price >= entry_price + 0.0030:
            success = await sugar.modify_position_sltp(
                ticket=ticket,
                sl=entry_price,  # Move SL to entry (breakeven)
                tp=None          # Keep TP unchanged
            )

            if success:
                print("Stop Loss moved to breakeven")
                break

        await asyncio.sleep(5)

```

### Example 3: Trailing Stop

```python
async def trailing_stop():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open BUY position
    ticket = await sugar.buy_market(volume=0.1)

    entry_price = await sugar.get_ask()
    trailing_distance = 0.0030  # 30 pips

    best_price = entry_price
    current_sl = entry_price - 0.0050  # Initial SL 50 pips

    # Set initial SL
    await sugar.modify_position_sltp(ticket, sl=current_sl, tp=None)

    # Trail the stop
    while True:
        current_price = await sugar.get_bid()

        # Update best price
        if current_price > best_price:
            best_price = current_price

            # Calculate new SL
            new_sl = best_price - trailing_distance

            # Only move SL up, never down
            if new_sl > current_sl:
                success = await sugar.modify_position_sltp(
                    ticket=ticket,
                    sl=new_sl,
                    tp=None
                )

                if success:
                    current_sl = new_sl
                    print(f"SL trailed to {new_sl:.5f}")

        await asyncio.sleep(5)

```

---

## Common Pitfalls

**Pitfall 1: Wrong SL/TP direction**
```python
# BUY position opened at 1.0850
ticket = await sugar.buy_market()

# ERROR: SL above entry, TP below entry (backwards!)
await sugar.modify_position_sltp(
    ticket=ticket,
    sl=1.0900,  # WRONG: SL above entry
    tp=1.0800   # WRONG: TP below entry
)
# Modification will likely fail
```

**Solution:** Remember BUY: SL below, TP above
```python
# BUY position at 1.0850
await sugar.modify_position_sltp(
    ticket=ticket,
    sl=1.0800,  # Correct: SL below entry
    tp=1.0950   # Correct: TP above entry
)
```

**Pitfall 2: Not handling position not found**
```python
# Position already closed or invalid ticket
try:
    await sugar.modify_position_sltp(ticket=999999, sl=1.0800)
except ValueError as e:
    print(e)  # "Position 999999 not found"
```

**Solution:** Check position exists first
```python
positions_data = await sugar._service.get_opened_orders()

position_exists = any(pos.ticket == ticket for pos in positions_data.position_infos)

if position_exists:
    await sugar.modify_position_sltp(ticket, sl=1.0800)
else:
    print(f"Position {ticket} not found")
```

**Pitfall 3: SL/TP too close to current price**
```python
# Broker requires minimum 10 pips stop level
bid = await sugar.get_bid()  # 1.0850

# ERROR: SL only 2 pips away (broker minimum is 10)
await sugar.modify_position_sltp(
    ticket=ticket,
    sl=bid - 0.0002  # Too close!
)
# Returns False
```

**Solution:** Respect broker's minimum stop level
```python
bid = await sugar.get_bid()

# Use at least broker minimum (e.g., 10 pips)
await sugar.modify_position_sltp(
    ticket=ticket,
    sl=bid - 0.0010  # 10 pips away
)
```

---

## Pro Tips

**Tip 1: Modify only what you need**
```python
# Only modify SL, keep TP unchanged
await sugar.modify_position_sltp(ticket, sl=1.0800, tp=None)

# Only modify TP, keep SL unchanged
await sugar.modify_position_sltp(ticket, sl=None, tp=1.0950)

# Modify both
await sugar.modify_position_sltp(ticket, sl=1.0800, tp=1.0950)
```

**Tip 2: Remove SL/TP by setting to 0**
```python
# Remove Stop Loss and Take Profit
await sugar.modify_position_sltp(ticket, sl=0.0, tp=0.0)
```

**Tip 3: Batch modify multiple positions**
```python
# Modify SL for all positions
positions_data = await sugar._service.get_opened_orders()

for pos in positions_data.position_infos:
    # Move SL to breakeven for all profitable positions
    if pos.profit > 0:
        await sugar.modify_position_sltp(
            ticket=pos.ticket,
            sl=pos.price_open,  # Entry price
            tp=None
        )
        print(f"Position #{pos.ticket} moved to breakeven")
```

---

## 📚 See Also

- [modify_position_sl](modify_position_sl.md) - Modify only Stop Loss
- [modify_position_tp](modify_position_tp.md) - Modify only Take Profit
- [buy_market_with_sltp](../5.%20Trading_With_SLTP/buy_market_with_sltp.md) - Open with SL/TP
- [close_position](close_position.md) - Close position completely
