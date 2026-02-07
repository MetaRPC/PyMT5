# Get All Open Positions (`get_open_positions`)

> **Sugar method:** Returns list of all currently open positions.

**API Information:**

* **Method:** `sugar.get_open_positions()`
* **Returns:** List of position objects
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_open_positions(self)
```

---

## 🔽 Input Parameters

None

---

## Return Value

| Type | Description |
|------|-------------|
| `list[PositionInfo]` | List of all open positions (empty list if none) |

---

## 🏛️ Essentials

**What it does:**

- Fetches all currently open positions from terminal
- Returns as Python list
- Each position contains full information (ticket, symbol, volume, profit, etc.)
- Returns empty list if no positions open

**Key behaviors:**

- Returns actual position objects (not summary)
- List may be empty (no positions)
- Each position has: ticket, symbol, type, volume, price_open, profit, sl, tp, etc.
- Sorted by default sort mode (0)

---

## ⚡ Under the Hood

```
MT5Sugar.get_open_positions()
    ↓ calls
MT5Service.get_opened_orders(sort_mode=0)
    ↓ calls
MT5Account.opened_orders()
    ↓ gRPC protobuf
TradingHelperService.OpenedOrders()
    ↓ MT5 Terminal
    ↓ returns position_infos list
```

**Call chain:**

1. Sugar calls Service.get_opened_orders() with sort_mode=0
2. Service forwards to Account.opened_orders()
3. Account sends gRPC request to terminal
4. Terminal returns all open positions
5. Sugar converts to Python list from position_infos
6. Returns list (may be empty)

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1338`
- Service: `src/pymt5/mt5_service.py:742`
- Account: `package/helpers/mt5_account.py:1316`

---

## When to Use

**Use `get_open_positions()` when:**

- Need to iterate through all positions
- Checking position details
- Building custom position filters
- Monitoring all active trades

**Don't use when:**

- Only need position count (use `count_open_positions()`)
- Only checking if positions exist (use `has_open_position()`)
- Only need specific position (use `get_position_by_ticket()`)

---

## 🔗 Examples

### Example 1: List All Positions

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def list_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get all positions
    positions = await sugar.get_open_positions()

    if not positions:
        print("No open positions")
    else:
        print(f"Open positions: {len(positions)}")

        for pos in positions:
            print(f"#{pos.ticket}: {pos.symbol} {pos.volume} lots, "
                  f"Profit: ${pos.profit:.2f}")

# Output:
# Open positions: 3
# #123456: EURUSD 0.1 lots, Profit: $12.50
# #123457: GBPUSD 0.05 lots, Profit: -$5.30
# #123458: USDJPY 0.2 lots, Profit: $25.80
```

### Example 2: Calculate Statistics

```python
async def position_statistics():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    positions = await sugar.get_open_positions()

    if positions:
        # Calculate stats
        total_volume = sum(pos.volume for pos in positions)
        total_profit = sum(pos.profit for pos in positions)
        profitable = sum(1 for pos in positions if pos.profit > 0)
        losing = sum(1 for pos in positions if pos.profit < 0)

        print(f"Total positions: {len(positions)}")
        print(f"Total volume: {total_volume} lots")
        print(f"Total profit: ${total_profit:.2f}")
        print(f"Profitable: {profitable}, Losing: {losing}")
```

### Example 3: Close All Profitable Positions

```python
async def close_profitable():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    positions = await sugar.get_open_positions()

    closed_count = 0
    for pos in positions:
        if pos.profit > 0:
            success = await sugar.close_position(pos.ticket)

            if success:
                closed_count += 1
                print(f"Closed #{pos.ticket} with ${pos.profit:.2f} profit")

    print(f"Closed {closed_count} profitable positions")
```

---

## Common Pitfalls

**Pitfall 1: Assuming positions list is never empty**
```python
# ERROR: Crashes if no positions
positions = await sugar.get_open_positions()
first_position = positions[0]  # IndexError if empty
```

**Solution:** Always check if list is empty
```python
positions = await sugar.get_open_positions()

if positions:
    first_position = positions[0]
else:
    print("No positions open")
```

**Pitfall 2: Modifying while iterating**
```python
# ERROR: Modifying list while iterating
positions = await sugar.get_open_positions()

for pos in positions:
    await sugar.close_position(pos.ticket)
    # List may change during iteration
```

**Solution:** Iterate over copy or collect tickets first
```python
positions = await sugar.get_open_positions()
tickets = [pos.ticket for pos in positions]

for ticket in tickets:
    await sugar.close_position(ticket)
```

**Pitfall 3: Not handling position types**
```python
# Treating all positions as BUY
for pos in positions:
    # pos.type might be SELL!
    pass
```

**Solution:** Check position type
```python
for pos in positions:
    if pos.type == 0:  # BUY
        print(f"BUY position: {pos.symbol}")
    else:  # SELL
        print(f"SELL position: {pos.symbol}")
```

---

## Pro Tips

**Tip 1: Filter by multiple criteria**
```python
positions = await sugar.get_open_positions()

# Get large profitable EUR positions
eur_profitable = [
    pos for pos in positions
    if 'EUR' in pos.symbol
    and pos.profit > 0
    and pos.volume >= 0.1
]

print(f"Found {len(eur_profitable)} large profitable EUR positions")
```

**Tip 2: Group by symbol**
```python
from collections import defaultdict

positions = await sugar.get_open_positions()

# Group positions by symbol
by_symbol = defaultdict(list)
for pos in positions:
    by_symbol[pos.symbol].append(pos)

for symbol, symbol_positions in by_symbol.items():
    total_volume = sum(p.volume for p in symbol_positions)
    total_profit = sum(p.profit for p in symbol_positions)
    print(f"{symbol}: {len(symbol_positions)} pos, "
          f"{total_volume} lots, ${total_profit:.2f}")
```

**Tip 3: Sort by profit**

```python
positions = await sugar.get_open_positions()

# Sort by profit (descending)
sorted_positions = sorted(positions, key=lambda p: p.profit, reverse=True)

print("Best performers:")
for pos in sorted_positions[:3]:
    print(f"#{pos.ticket}: ${pos.profit:.2f}")
```

---

## 📚 See Also

- [get_position_by_ticket](get_position_by_ticket.md) - Get specific position
- [get_positions_by_symbol](get_positions_by_symbol.md) - Filter by symbol
- [count_open_positions](count_open_positions.md) - Get position count
- [has_open_position](has_open_position.md) - Check if positions exist
