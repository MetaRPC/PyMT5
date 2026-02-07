# Close All Positions (`close_all_positions`)

> **Sugar method:** Closes all open positions, optionally filtered by symbol.

**API Information:**

* **Method:** `sugar.close_all_positions(symbol: Optional[str] = None)`
* **Returns:** Number of positions closed (`int`)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def close_all_positions(self, symbol: Optional[str] = None) -> int
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | No | `None` | If specified, close only positions for this symbol |

---

## Return Value

| Type | Description |
|------|-------------|
| `int` | Number of positions successfully closed |

---

## 🏛️ Essentials

**What it does:**

- Fetches all open positions from terminal
- Closes each position one by one
- Optionally filters by symbol
- Continues closing even if some fail

**Key behaviors:**

- Returns count of successfully closed positions
- Filters by symbol if provided
- Continues on individual failures (error logged)
- Safe for empty position list (returns 0)

---

## ⚡ Under the Hood

```
MT5Sugar.close_all_positions()
    ↓ fetches all positions
MT5Service.get_opened_orders()
    ↓ iterates and closes each
MT5Sugar.close_position() (for each)
    ↓ calls
MT5Service.close_order()
    ↓ gRPC protobuf
TradingHelperService.OrderClose()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar calls Service.get_opened_orders() to fetch all positions
2. Sugar iterates through position_infos list
3. If symbol filter provided, skips positions not matching symbol
4. For each position, calls close_position() internally
5. Counts successful closes (where close_position returned True)
6. Continues even if individual closes fail (logs error)
7. Returns total count of successful closes

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1165`
- Service: `src/pymt5/mt5_service.py:742`
- Internal close: `src/pymt5/mt5_sugar.py:1141`

---

## When to Use

**Use `close_all_positions()` when:**

- End of trading day/session cleanup
- Emergency exit all positions
- Strategy reset or restart
- Account-wide risk management

**Don't use when:**

- Want to close specific position (use `close_position()`)
- Need partial closes (use `close_position_partial()`)
- Want to keep some positions open

---

## 🔗 Examples

### Example 1: Close All Positions (No Filter)

```python
from pymt5 import MT5Sugar

async def close_everything():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open several positions
    ticket1 = await sugar.buy_market("EURUSD", volume=0.1)
    ticket2 = await sugar.sell_market("GBPUSD", volume=0.1)
    ticket3 = await sugar.buy_market("USDJPY", volume=0.1)

    print(f"Opened positions: #{ticket1}, #{ticket2}, #{ticket3}")

    # Close all positions
    closed_count = await sugar.close_all_positions()

    print(f"Closed {closed_count} positions")

# Output:
# Opened positions: #123456, #123457, #123458
# Closed 3 positions
```

### Example 2: Close Positions for Specific Symbol

```python
async def close_symbol_positions():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await sugar.connect()

    # Open positions on different symbols
    await sugar.buy_market("EURUSD", volume=0.1)
    await sugar.buy_market("EURUSD", volume=0.1)
    await sugar.sell_market("GBPUSD", volume=0.1)

    # Close only EURUSD positions
    eurusd_closed = await sugar.close_all_positions(symbol="EURUSD")

    print(f"Closed {eurusd_closed} EURUSD positions")
    print("GBPUSD position still open")

# Output:
# Closed 2 EURUSD positions
# GBPUSD position still open
```

### Example 3: End of Day Cleanup

```python
import asyncio
from datetime import datetime, time

async def end_of_day_close():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Trading logic during the day...
    # (open positions, monitor, etc.)

    # At 5 PM, close all positions
    while True:
        now = datetime.now().time()
        close_time = time(17, 0)  # 5:00 PM

        if now >= close_time:
            print("End of day - closing all positions")

            closed_count = await sugar.close_all_positions()
            print(f"Closed {closed_count} positions")

            # Show final balance
            balance = await sugar.get_balance()
            print(f"Final balance: ${balance}")

            break

        await asyncio.sleep(60)  # Check every minute
```

---

## Common Pitfalls

**Pitfall 1: Expecting all positions to close**
```python
# Some positions may fail to close
closed = await sugar.close_all_positions()

# If you had 5 positions, closed might be 4 or 3
# (some may fail due to market conditions, etc.)
```

**Solution:** Check return value and verify
```python
# Get count before closing
positions_data = await sugar._service.get_opened_orders()
initial_count = len(positions_data.position_infos)

# Close all
closed_count = await sugar.close_all_positions()

if closed_count < initial_count:
    print(f"Warning: Only {closed_count}/{initial_count} closed")
    # Retry or investigate
```

**Pitfall 2: Closing positions with pending orders**
```python
# close_all_positions() only closes POSITIONS, not PENDING ORDERS
await sugar.buy_limit(price=1.0840)  # Pending order
await sugar.buy_market()              # Open position

closed = await sugar.close_all_positions()  # Only closes position
# Pending order still active!
```

**Solution:** Cancel pending orders separately
```python
# Close positions
await sugar.close_all_positions()

# Cancel pending orders (if method exists)
# await sugar.cancel_all_orders()
```

**Pitfall 3: Not handling partial failures**
```python
# If 1 out of 5 fails, you might not notice
closed = await sugar.close_all_positions()
# Silently continues, returns 4 instead of 5
```

**Solution:** Log and check
```python
positions_before = await sugar._service.get_opened_orders()
initial = len(positions_before.position_infos)

closed = await sugar.close_all_positions()

if closed < initial:
    print(f"Failed to close {initial - closed} positions")

    # Check which positions remain
    positions_after = await sugar._service.get_opened_orders()
    for pos in positions_after.position_infos:
        print(f"Position #{pos.ticket} still open")
```

---

## Pro Tips

**Tip 1: Get total profit before closing**
```python
# Check total profit/loss before closing all
total_profit = await sugar.get_floating_profit()

print(f"Total P&L: ${total_profit:.2f}")

# Close all positions
closed = await sugar.close_all_positions()

print(f"Closed {closed} positions with ${total_profit:.2f} P&L")
```

**Tip 2: Close by symbol in sequence**
```python
# Close positions symbol by symbol for better control
symbols = ["EURUSD", "GBPUSD", "USDJPY"]

total_closed = 0
for symbol in symbols:
    count = await sugar.close_all_positions(symbol=symbol)
    print(f"{symbol}: closed {count} positions")
    total_closed += count

print(f"Total closed: {total_closed}")
```

**Tip 3: Retry on partial failure**
```python
# Retry closing remaining positions
max_retries = 3

for attempt in range(max_retries):
    positions_data = await sugar._service.get_opened_orders()
    remaining = len(positions_data.position_infos)

    if remaining == 0:
        print("All positions closed")
        break

    print(f"Attempt {attempt + 1}: Closing {remaining} positions")
    closed = await sugar.close_all_positions()

    if closed == remaining:
        print("All positions closed")
        break

    await asyncio.sleep(2)  # Wait before retry
```

---

## 📚 See Also

- [close_position](close_position.md) - Close specific position by ticket
- [close_position_partial](close_position_partial.md) - Close position partially
- [get_floating_profit](../2.%20Account_Properties/get_floating_profit.md) - Get total unrealized profit
