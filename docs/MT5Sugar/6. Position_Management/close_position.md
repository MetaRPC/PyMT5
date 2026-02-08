# Close Position Completely (`close_position`)

> **Sugar method:** Closes open position by ticket number in one call.

**API Information:**

* **Method:** `sugar.close_position(ticket: int)`
* **Returns:** `True` if closed successfully, `False` otherwise
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def close_position(self, ticket: int) -> bool
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Yes | - | Position ticket number to close |

---

## Return Value

| Type | Description |
|------|-------------|
| `bool` | `True` if position closed (return_code == 10009), `False` otherwise |

---

## 🏛️ Essentials

**What it does:**

- Closes entire position by ticket number
- Creates opposite market order automatically (BUY→SELL, SELL→BUY)
- Returns boolean success status
- Validates return code from terminal

**Key behaviors:**

- BUY positions closed with SELL at BID price
- SELL positions closed with BUY at ASK price
- Returns False if close failed (no exception)
- Position removed from terminal on success

---

## ⚡ Under the Hood

```
MT5Sugar.close_position()
    ↓ builds OrderCloseRequest
MT5Service.close_order()
    ↓ calls
MT5Account.order_close()
    ↓ gRPC protobuf
TradingHelperService.OrderClose()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar creates OrderCloseRequest with ticket
2. Sugar calls Service.close_order()
3. Service forwards to Account.order_close()
4. Account sends gRPC request to terminal
5. Terminal creates opposite market order to close position
6. Sugar checks return_code == 10009 (TRADE_RETCODE_DONE)
7. Returns True on success, False on failure

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1141`
- Service: `src/pymt5/mt5_service.py:996`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1803`

---

## When to Use

**Use `close_position()` when:**

- Need to exit position completely
- Take profit or cut losses manually
- Emergency position closure
- End of trading session cleanup

**Don't use when:**

- Want partial close (use `close_position_partial()`)
- Want to close all positions (use `close_all_positions()`)
- Position already closed

---

## 🔗 Examples

### Example 1: Basic Position Close

```python
from pymt5 import MT5Sugar

async def simple_close():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open position
    ticket = await sugar.buy_market(volume=0.1)
    print(f"Position opened: #{ticket}")

    # Close position
    success = await sugar.close_position(ticket)

    if success:
        print(f"Position #{ticket} closed successfully")
    else:
        print(f"Failed to close position #{ticket}")
```

### Example 2: Close with Profit Check

```python
async def close_with_profit_check():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open position
    ticket = await sugar.buy_market(volume=0.1)

    # Monitor profit
    while True:
        profit = await sugar.get_floating_profit()
        print(f"Current profit: ${profit:.2f}")

        # Close if profit >= $50 or loss >= $20
        if profit >= 50 or profit <= -20:
            success = await sugar.close_position(ticket)

            if success:
                print(f"Position closed at ${profit:.2f}")
                break
            else:
                print("Close failed, retrying...")

        await asyncio.sleep(5)
```

### Example 3: Close Multiple Positions

```python
async def close_multiple():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open multiple positions
    tickets = []
    for i in range(3):
        ticket = await sugar.buy_market(volume=0.01)
        tickets.append(ticket)
        print(f"Position {i+1}: #{ticket}")

    # Close each position
    for ticket in tickets:
        success = await sugar.close_position(ticket)

        if success:
            print(f"Closed #{ticket}")
        else:
            print(f"Failed #{ticket}")
```

---

## Common Pitfalls

**Pitfall 1: Not checking return value**
```python
# BAD: Assuming close always succeeds
await sugar.close_position(ticket)
# Position may still be open if close failed!
```

**Solution:** Always check return value
```python
success = await sugar.close_position(ticket)

if not success:
    print(f"Position {ticket} failed to close")
    # Handle failure (retry, alert, etc.)
```

**Pitfall 2: Trying to close already closed position**
```python
# Close position
await sugar.close_position(ticket)

# ERROR: Trying to close again
await sugar.close_position(ticket)  # Returns False
```

**Solution:** Track closed positions
```python
success = await sugar.close_position(ticket)

if success:
    closed_tickets.add(ticket)

# Later: check before closing
if ticket not in closed_tickets:
    await sugar.close_position(ticket)
```

**Pitfall 3: Ignoring market conditions**
```python
# Market closed on weekend
success = await sugar.close_position(ticket)  # Returns False
```

**Solution:** Check market hours or handle gracefully
```python
success = await sugar.close_position(ticket)

if not success:
    # Could be market closed, connection issue, etc.
    print("Close failed - check market status")
```

---

## Pro Tips

**Tip 1: Use with try-except for robustness**
```python
try:
    success = await sugar.close_position(ticket)

    if success:
        print("Position closed")
    else:
        print("Close returned False")

except Exception as e:
    print(f"Exception during close: {e}")
```

**Tip 2: Combine with position profit check**
```python
# Get final profit before closing
profit = await sugar.get_floating_profit()

success = await sugar.close_position(ticket)

if success:
    print(f"Closed with profit: ${profit:.2f}")
```

**Tip 3: Close positions by magic number**
```python
# Get all positions
positions_data = await sugar._service.get_opened_orders()

# Close only positions with specific magic
magic_to_close = 12345

for pos in positions_data.position_infos:
    if pos.expert_id == magic_to_close:
        success = await sugar.close_position(pos.ticket)
        print(f"Closed magic {magic_to_close}: #{pos.ticket}")
```

---

## 📚 See Also

- [close_all_positions](close_all_positions.md) - Close all open positions
- [close_position_partial](close_position_partial.md) - Close position partially
- [buy_market](../4.%20Simple_Trading/buy_market.md) - Open BUY position
- [sell_market](../4.%20Simple_Trading/sell_market.md) - Open SELL position
