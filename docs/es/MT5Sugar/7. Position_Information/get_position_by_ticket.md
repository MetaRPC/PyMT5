# Get Position by Ticket (`get_position_by_ticket`)

> **Sugar method:** Returns specific position by ticket number.

**API Information:**

* **Method:** `sugar.get_position_by_ticket(ticket)`
* **Returns:** Position object or `None` if not found
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_position_by_ticket(self, ticket: int)
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Yes | - | Position ticket number to find |

---

## Return Value

| Type | Description |
|------|-------------|
| `PositionInfo \| None` | Position object if found, `None` if not found |

---

## 🏛️ Essentials

**What it does:**

- Searches for position with specific ticket number
- Returns full position information if found
- Returns `None` if position not found
- Searches through all open positions

**Key behaviors:**

- Returns None (not exception) if not found
- Only searches open positions (not closed)
- Returns first match (tickets are unique)
- Full position object with all fields

---

## ⚡ Under the Hood

```
MT5Sugar.get_position_by_ticket()
    ↓ calls
MT5Service.get_opened_orders(sort_mode=0)
    ↓ iterates position_infos
    ↓ matches ticket
    ↓ returns position or None
```

**Call chain:**

1. Sugar calls Service.get_opened_orders()
2. Sugar iterates through position_infos list
3. Compares each pos.ticket with target ticket
4. Returns position object on match
5. Returns None if no match found

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1343`
- Service: `src/pymt5/mt5_service.py:742`

---

## When to Use

**Use `get_position_by_ticket()` when:**

- Need details of specific position
- Have ticket number from previous operation
- Checking if specific position still open
- Monitoring specific trade

**Don't use when:**

- Need all positions (use `get_open_positions()`)
- Only checking existence (use `has_open_position()`)
- Need positions by symbol (use `get_positions_by_symbol()`)

---

## 🔗 Examples

### Example 1: Check Position Status

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def check_position():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Open position
    ticket = await sugar.buy_market(volume=0.1)
    print(f"Opened position #{ticket}")

    # Later: get position details
    position = await sugar.get_position_by_ticket(ticket)

    if position:
        print(f"Position found:")
        print(f"  Symbol: {position.symbol}")
        print(f"  Volume: {position.volume}")
        print(f"  Profit: ${position.profit:.2f}")
    else:
        print(f"Position #{ticket} not found (already closed?)")
```

### Example 2: Monitor Position Until Target

```python
import asyncio

async def monitor_until_target():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Open position
    ticket = await sugar.buy_market(volume=0.1)
    target_profit = 50.0

    print(f"Monitoring position #{ticket} until ${target_profit} profit")

    while True:
        position = await sugar.get_position_by_ticket(ticket)

        if position is None:
            print("Position closed (SL/TP hit or manually closed)")
            break

        print(f"Current profit: ${position.profit:.2f}")

        if position.profit >= target_profit:
            print("Target reached, closing position")
            await sugar.close_position(ticket)
            break

        await asyncio.sleep(5)
```

### Example 3: Verify Multiple Positions

```python
async def verify_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Open several positions
    tickets = []
    for _ in range(3):
        ticket = await sugar.buy_market(volume=0.01)
        tickets.append(ticket)

    # Later: verify all still open
    still_open = []
    closed = []

    for ticket in tickets:
        position = await sugar.get_position_by_ticket(ticket)

        if position:
            still_open.append(ticket)
        else:
            closed.append(ticket)

    print(f"Still open: {len(still_open)}")
    print(f"Closed: {len(closed)}")
```

---

## Common Pitfalls

**Pitfall 1: Not checking for None**
```python
# ERROR: Crashes if position closed
position = await sugar.get_position_by_ticket(ticket)
profit = position.profit  # AttributeError if None
```

**Solution:** Always check for None
```python
position = await sugar.get_position_by_ticket(ticket)

if position:
    profit = position.profit
else:
    print("Position not found")
```

**Pitfall 2: Using wrong ticket**
```python
# Ticket from order placement (pending order)
order_ticket = await sugar.buy_limit(price=1.0840)

# ERROR: Pending order ticket != position ticket
position = await sugar.get_position_by_ticket(order_ticket)
# Returns None until order fills
```

**Solution:** Distinguish between order and position tickets
```python
# When limit order fills, it becomes position with SAME ticket
order_ticket = await sugar.buy_limit(price=1.0840)

# Wait for order to fill...
# Then it becomes position
position = await sugar.get_position_by_ticket(order_ticket)
```

**Pitfall 3: Repeated calls in tight loop**
```python
# Inefficient: fetching all positions repeatedly
while True:
    pos = await sugar.get_position_by_ticket(ticket)
    # Fetches ALL positions every iteration
    await asyncio.sleep(0.1)  # 10 times per second!
```

**Solution:** Use reasonable polling interval
```python
while True:
    pos = await sugar.get_position_by_ticket(ticket)
    await asyncio.sleep(5)  # Once every 5 seconds
```

---

## Pro Tips

**Tip 1: Cache position data**

```python
# Avoid repeated lookups
position = await sugar.get_position_by_ticket(ticket)

if position:
    # Use cached data for multiple operations
    symbol = position.symbol
    volume = position.volume
    profit = position.profit

    print(f"{symbol}: {volume} lots = ${profit:.2f}")
```

**Tip 2: Track position across operations**
```python
# Open and track position
ticket = await sugar.buy_market(volume=0.1)
entry_price = (await sugar.get_position_by_ticket(ticket)).price_open

# After some time
position = await sugar.get_position_by_ticket(ticket)

if position:
    pips_moved = (position.price_current - entry_price) / 0.0001
    print(f"Moved {pips_moved:.1f} pips from entry")
```

**Tip 3: Batch check multiple tickets**

```python
async def check_tickets(sugar, tickets):
    """Check multiple tickets efficiently."""
    # Get all positions once
    all_positions = await sugar.get_open_positions()
    ticket_set = set(tickets)

    # Filter in memory
    found = [p for p in all_positions if p.ticket in ticket_set]

    return found

# Usage
tickets = [123456, 123457, 123458]
positions = await check_tickets(sugar, tickets)
print(f"Found {len(positions)} of {len(tickets)} positions")
```

---

## 📚 See Also

- [get_open_positions](get_open_positions.md) - Get all positions
- [get_positions_by_symbol](get_positions_by_symbol.md) - Filter by symbol
- [has_open_position](has_open_position.md) - Check if positions exist
- [close_position](../6.%20Position_Management/close_position.md) - Close position
