# Count Open Positions (`count_open_positions`)

> **Sugar method:** Returns number of open positions (optionally filtered by symbol).

**API Information:**

* **Method:** `sugar.count_open_positions(symbol: Optional[str] = None)`
* **Returns:** Number of positions as integer
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def count_open_positions(self, symbol: Optional[str] = None) -> int
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | No | `None` | Filter by symbol (None = count all) |

---

## Return Value

| Type | Description |
|------|-------------|
| `int` | Number of open positions (0 if none) |

---

## 🏛️ Essentials

**What it does:**

- Counts open positions
- Optionally filters by symbol
- Returns integer count
- Returns 0 if no positions

**Key behaviors:**

- No symbol: counts ALL positions
- With symbol: counts only that symbol
- Case-sensitive symbol matching
- Always returns integer (never None)

---

## ⚡ Under the Hood

```
MT5Sugar.count_open_positions()
    ↓ calls
MT5Service.get_opened_orders(sort_mode=0)
    ↓ counts len(position_infos)
    ↓ or sum(1 for pos if pos.symbol == symbol)
    ↓ returns count
```

**Call chain:**

1. Sugar calls Service.get_opened_orders()
2. If no symbol: returns len(position_infos)
3. If symbol provided: counts matching positions
4. Returns integer count

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1368`
- Service: `src/pymt5/mt5_service.py:742`

---

## When to Use

**Use `count_open_positions()` when:**

- Need number of positions
- Limiting maximum positions
- Monitoring position count
- Statistics and reporting

**Don't use when:**

- Only checking existence (use `has_open_position()`)
- Need position details (use `get_open_positions()`)
- Need specific position (use `get_position_by_ticket()`)

---

## 🔗 Examples

### Example 1: Basic Position Count

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def check_count():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Count all positions
    total = await sugar.count_open_positions()
    print(f"Total open positions: {total}")

    # Count by symbol
    eurusd_count = await sugar.count_open_positions("EURUSD")
    gbpusd_count = await sugar.count_open_positions("GBPUSD")

    print(f"EURUSD: {eurusd_count}")
    print(f"GBPUSD: {gbpusd_count}")
```

### Example 2: Limit Maximum Positions

```python
async def limit_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    max_positions = 5

    # Check before opening
    current_count = await sugar.count_open_positions()

    if current_count < max_positions:
        ticket = await sugar.buy_market(volume=0.1)
        print(f"Opened position #{ticket} ({current_count + 1}/{max_positions})")
    else:
        print(f"Maximum positions reached ({max_positions})")
```

### Example 3: Symbol-Specific Limits

```python
async def symbol_limits():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    max_per_symbol = 3

    # Count EURUSD positions
    eurusd_count = await sugar.count_open_positions(symbol)

    if eurusd_count < max_per_symbol:
        ticket = await sugar.buy_market(symbol, volume=0.1)
        print(f"Opened {symbol} position ({eurusd_count + 1}/{max_per_symbol})")
    else:
        print(f"Max {symbol} positions reached")
```

---

## Common Pitfalls

**Pitfall 1: Case-sensitive symbol**
```python
# ERROR: Symbol case matters
count = await sugar.count_open_positions("eurusd")
# Returns 0 if positions are "EURUSD"
```

**Solution:** Use uppercase symbols
```python
count = await sugar.count_open_positions("EURUSD")
```

**Pitfall 2: Expecting None instead of 0**
```python
# count_open_positions returns 0, not None
count = await sugar.count_open_positions()

if count:  # This works (0 is falsy)
    print("Have positions")
```

**Solution:** Compare explicitly or use truthiness
```python
# Both work
if count > 0:
    print("Have positions")

if count:
    print("Have positions")
```

**Pitfall 3: Not caching count**
```python
# Inefficient: counting repeatedly in loop
for _ in range(100):
    if await sugar.count_open_positions() < 5:
        # Fetches all positions every iteration
        pass
```

**Solution:** Cache count if checking multiple times
```python
count = await sugar.count_open_positions()

for _ in range(100):
    if count < 5:
        # Use cached value
        pass
```

---

## Pro Tips

**Tip 1: Position capacity check**

```python
async def get_remaining_capacity(sugar, max_positions=10):
    """Get how many more positions can be opened."""
    current = await sugar.count_open_positions()
    remaining = max(0, max_positions - current)
    return remaining

# Usage
remaining = await get_remaining_capacity(sugar)
print(f"Can open {remaining} more positions")
```

**Tip 2: Symbol distribution analysis**
```python
# Analyze position distribution across symbols
all_positions = await sugar.get_open_positions()
symbols = set(p.symbol for p in all_positions)

for symbol in symbols:
    count = await sugar.count_open_positions(symbol)
    print(f"{symbol}: {count} positions")
```

**Tip 3: Wait until count reaches target**
```python
import asyncio

async def wait_for_fills(sugar, expected_count):
    """Wait until position count reaches expected."""
    while True:
        current = await sugar.count_open_positions()

        if current >= expected_count:
            print(f"Reached {current} positions")
            break

        print(f"Waiting... {current}/{expected_count}")
        await asyncio.sleep(2)
```

---

## 📚 See Also

- [has_open_position](has_open_position.md) - Check if positions exist
- [get_open_positions](get_open_positions.md) - Get all positions
- [get_positions_by_symbol](get_positions_by_symbol.md) - Get symbol positions
- [close_all_positions](../6.%20Position_Management/close_all_positions.md) - Close all
