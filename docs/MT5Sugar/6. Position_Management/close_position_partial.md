# Close Position Partially (`close_position_partial`)

> **Sugar method:** Closes part of a position by specified volume.

**API Information:**

* **Method:** `sugar.close_position_partial(ticket, volume)`
* **Returns:** `True` if partial close successful, `False` otherwise
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def close_position_partial(self, ticket: int, volume: float) -> bool
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Yes | - | Position ticket number |
| `volume` | `float` | Yes | - | Volume to close (must be less than position volume) |

---

## Return Value

| Type | Description |
|------|-------------|
| `bool` | `True` if partial close successful (return_code == 10009), `False` otherwise |

**Raises:**

- `ValueError` if position not found
- `ValueError` if volume >= position volume

---

## 🏛️ Essentials

**What it does:**

- Closes specified volume of an open position
- Remaining volume stays as original position
- Creates opposite market order for specified volume
- Original position ticket remains with reduced volume

**Key behaviors:**

- Volume must be less than position volume
- BUY positions: closes with SELL at BID price
- SELL positions: closes with BUY at ASK price
- Remaining position keeps same ticket number
- Uses default 10 points slippage

---

## ⚡ Under the Hood

```
MT5Sugar.close_position_partial()
    ↓ fetches position
MT5Service.get_opened_orders()
    ↓ validates volume < position.volume
    ↓ determines opposite order type
    ↓ fetches current price
MT5Service.get_symbol_tick()
    ↓ builds OrderSendRequest (opposite direction)
MT5Service.place_order()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar fetches all positions to find matching ticket
2. Raises ValueError if position not found
3. Validates volume < position.volume (raises if >=)
4. Determines opposite order type (BUY→SELL, SELL→BUY)
5. Fetches current tick price (BID for SELL, ASK for BUY)
6. Creates OrderSendRequest with opposite operation and partial volume
7. Sends order through Service.place_order()
8. Returns True if returned_code == 10009

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1241`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/helpers/mt5_account.py:1713`

---

## When to Use

**Use `close_position_partial()` when:**

- Taking partial profits at targets
- Scaling out of positions gradually
- Reducing exposure while keeping position open
- Implementing tiered exit strategies

**Don't use when:**

- Want to close entire position (use `close_position()`)
- Volume equals or exceeds position volume
- Position already closed

---

## 🔗 Examples

### Example 1: Take Half Profit

```python
from pymt5 import MT5Sugar

async def take_half_profit():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open 0.1 lot position
    ticket = await sugar.buy_market(volume=0.10)
    print(f"Position opened: #{ticket}, 0.10 lots")

    # Wait for profit (simplified)
    profit = await sugar.get_floating_profit()
    while profit < 50:
        await asyncio.sleep(5)
        profit = await sugar.get_floating_profit()

    # Close half the position
    success = await sugar.close_position_partial(ticket, volume=0.05)

    if success:
        print("Closed 0.05 lots, 0.05 lots remaining")
    else:
        print("Partial close failed")

```

### Example 2: Tiered Exit Strategy

```python
async def tiered_exit():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open 0.3 lot position
    ticket = await sugar.buy_market(volume=0.30)
    entry_price = await sugar.get_ask()

    print(f"Position: #{ticket}, 0.30 lots at {entry_price}")

    # Exit in 3 stages
    targets = [
        (entry_price + 0.0030, 0.10, "Target 1: +30 pips"),
        (entry_price + 0.0060, 0.10, "Target 2: +60 pips"),
        (entry_price + 0.0100, 0.10, "Target 3: +100 pips")
    ]

    for target_price, close_volume, label in targets:
        # Wait for price to reach target
        while True:
            current = await sugar.get_bid()

            if current >= target_price:
                success = await sugar.close_position_partial(
                    ticket,
                    volume=close_volume
                )

                if success:
                    print(f"{label} - Closed {close_volume} lots")
                    break

            await asyncio.sleep(5)

    print("All targets hit, position fully closed")

```

### Example 3: Risk Reduction on Profit

```python
async def reduce_risk_on_profit():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open position
    ticket = await sugar.buy_market(volume=0.20)
    entry_price = await sugar.get_ask()

    # Close 75% when in 50 pips profit, let 25% run
    while True:
        current_price = await sugar.get_bid()
        profit_pips = (current_price - entry_price) / 0.0001

        if profit_pips >= 50:
            # Close 0.15 lots (75%), keep 0.05 lots (25%)
            success = await sugar.close_position_partial(
                ticket,
                volume=0.15
            )

            if success:
                print("Closed 75%, letting 25% run with trailing stop")

                # Move remaining 0.05 lots to breakeven
                await sugar.modify_position_sltp(
                    ticket,
                    sl=entry_price,
                    tp=None
                )
                break

        await asyncio.sleep(5)

```

---

## Common Pitfalls

**Pitfall 1: Volume too large**
```python
# Position has 0.10 lots
ticket = await sugar.buy_market(volume=0.10)

# ERROR: Can't close 0.10 or more
try:
    await sugar.close_position_partial(ticket, volume=0.10)
except ValueError as e:
    print(e)  # "Partial volume must be less than position volume"
```

**Solution:** Always close less than position volume
```python
# Close part, not all
await sugar.close_position_partial(ticket, volume=0.05)  # OK
await sugar.close_position_partial(ticket, volume=0.09)  # OK
```

**Pitfall 2: Not tracking remaining volume**
```python
# Open 0.10 lots
ticket = await sugar.buy_market(volume=0.10)

# Close 0.05 lots
await sugar.close_position_partial(ticket, volume=0.05)

# ERROR: Can't close 0.06 (only 0.05 remaining)
await sugar.close_position_partial(ticket, volume=0.06)
```

**Solution:** Track or check remaining volume
```python
# Check position volume before closing
positions_data = await sugar._service.get_opened_orders()

for pos in positions_data.position_infos:
    if pos.ticket == ticket:
        remaining = pos.volume
        print(f"Remaining volume: {remaining}")

        # Close only what remains
        close_vol = min(0.05, remaining)
        await sugar.close_position_partial(ticket, close_vol)
```

**Pitfall 3: Multiple partial closes not updating volume**
```python
# Open 0.30 lots
ticket = await sugar.buy_market(volume=0.30)

# Close in steps
await sugar.close_position_partial(ticket, 0.10)  # 0.20 left
await sugar.close_position_partial(ticket, 0.10)  # 0.10 left
await sugar.close_position_partial(ticket, 0.10)  # 0.00 left

# ERROR: Position fully closed, ticket invalid for further partials
await sugar.close_position_partial(ticket, 0.05)
```

**Solution:** Check if position still exists
```python
# After each partial close, verify position exists
success = await sugar.close_position_partial(ticket, 0.10)

if success:
    # Check if position still exists
    positions_data = await sugar._service.get_opened_orders()
    still_open = any(p.ticket == ticket for p in positions_data.position_infos)

    if not still_open:
        print("Position fully closed")
```

---

## Pro Tips

**Tip 1: Scale out with percentage**
```python
# Get current position volume
positions_data = await sugar._service.get_opened_orders()

for pos in positions_data.position_infos:
    if pos.ticket == ticket:
        # Close 50% of position
        close_volume = pos.volume * 0.5

        await sugar.close_position_partial(ticket, close_volume)
        print(f"Closed 50%: {close_volume} lots")
```

**Tip 2: Combine with SL adjustment**
```python
# Close partial and move SL to breakeven
entry_price = 1.0850

# Close 50%
await sugar.close_position_partial(ticket, volume=0.05)

# Move SL to breakeven for remaining
await sugar.modify_position_sltp(ticket, sl=entry_price, tp=None)
```

**Tip 3: Pyramid exit strategy**
```python
# Exit in pyramid fashion (larger amounts first)
total_volume = 0.30

exits = [
    (0.15, "50%"),  # Close half
    (0.10, "33%"),  # Close third of remaining
    (0.05, "17%")   # Let small amount run
]

for volume, label in exits:
    success = await sugar.close_position_partial(ticket, volume)

    if success:
        print(f"Closed {label}: {volume} lots")

    await asyncio.sleep(60)  # Wait between exits
```

---

## 📚 See Also

- [close_position](close_position.md) - Close entire position
- [close_all_positions](close_all_positions.md) - Close all positions
- [modify_position_sltp](modify_position_sltp.md) - Modify SL/TP
- [buy_market](../4.%20Simple_Trading/buy_market.md) - Open BUY position
