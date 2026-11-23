# Check if Positions Exist (`has_open_position`)

> **Sugar method:** Quick check if any positions are open (optionally filtered by symbol).

**API Information:**

* **Method:** `sugar.has_open_position(symbol: Optional[str] = None)`
* **Returns:** `True` if positions exist, `False` otherwise
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def has_open_position(self, symbol: Optional[str] = None) -> bool
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | No | `None` | Filter by symbol (None = check any symbol) |

---

## Return Value

| Type | Description |
|------|-------------|
| `bool` | `True` if positions exist (matching filter), `False` otherwise |

---

## 🏛️ Essentials

**What it does:**

- Checks if any open positions exist
- Optionally filters by symbol
- Returns boolean (True/False)
- Efficient check without retrieving full details

**Key behaviors:**

- No symbol: checks ANY open position
- With symbol: checks positions for that symbol only
- Case-sensitive symbol matching
- Returns False if no positions

---

## ⚡ Under the Hood

```
MT5Sugar.has_open_position()
    ↓ calls
MT5Service.get_opened_orders(sort_mode=0)
    ↓ checks len(position_infos) > 0
    ↓ or any(pos.symbol == symbol)
    ↓ returns boolean
```

**Call chain:**

1. Sugar calls Service.get_opened_orders()
2. If no symbol: checks if position_infos length > 0
3. If symbol provided: checks if any position matches symbol
4. Returns True if found, False otherwise

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1359`
- Service: `src/pymt5/mt5_service.py:742`

---

## When to Use

**Use `has_open_position()` when:**

- Quick existence check before operations
- Validating no positions before action
- Conditional logic based on positions
- Pre-flight checks

**Don't use when:**

- Need position count (use `count_open_positions()`)
- Need position details (use `get_open_positions()`)
- Need specific position (use `get_position_by_ticket()`)

---

## 🔗 Examples

### Example 1: Check Before Opening

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def safe_open():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Only open if no positions
    if not await sugar.has_open_position():
        ticket = await sugar.buy_market(volume=0.1)
        print(f"Opened position #{ticket}")
    else:
        print("Already have open positions, skipping")
```

### Example 2: Symbol-Specific Check

```python
async def symbol_check():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Check specific symbol
    has_eurusd = await sugar.has_open_position("EURUSD")
    has_gbpusd = await sugar.has_open_position("GBPUSD")

    print(f"EURUSD positions: {'Yes' if has_eurusd else 'No'}")
    print(f"GBPUSD positions: {'Yes' if has_gbpusd else 'No'}")

    # Open only if no EURUSD
    if not has_eurusd:
        await sugar.buy_market("EURUSD", volume=0.1)
```

### Example 3: Wait Until All Closed

```python
import asyncio

async def wait_until_flat():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Close all positions
    await sugar.close_all_positions()

    print("Waiting for all positions to close...")

    # Wait until no positions remain
    while await sugar.has_open_position():
        print("Still have open positions...")
        await asyncio.sleep(2)

    print("All positions closed")
```

---

## Common Pitfalls

**Pitfall 1: Case-sensitive symbol**
```python
# ERROR: Symbol case matters
has_pos = await sugar.has_open_position("eurusd")
# Returns False if positions are "EURUSD"
```

**Solution:** Use uppercase symbols
```python
has_pos = await sugar.has_open_position("EURUSD")
```

**Pitfall 2: Confusing with count**
```python
# has_open_position returns bool, not count
if await sugar.has_open_position():
    # Don't know HOW MANY positions
    pass
```

**Solution:** Use count if you need number
```python
count = await sugar.count_open_positions()
print(f"Have {count} positions")
```

**Pitfall 3: Not awaiting (async method)**
```python
# ERROR: Forgetting await
if sugar.has_open_position():  # Missing await
    pass
```

**Solution:** Always await async methods
```python
if await sugar.has_open_position():
    pass
```

---

## Pro Tips

**Tip 1: Quick pre-check pattern**
```python
# Common pattern: check before action
if await sugar.has_open_position("EURUSD"):
    print("Already trading EURUSD")
else:
    # Safe to open new position
    await sugar.buy_market("EURUSD", volume=0.1)
```

**Tip 2: Multiple symbol check**
```python
# Check multiple symbols efficiently
symbols = ["EURUSD", "GBPUSD", "USDJPY"]

for symbol in symbols:
    if await sugar.has_open_position(symbol):
        print(f"{symbol}: trading")
    else:
        print(f"{symbol}: flat")
```

**Tip 3: Use as assertion**
```python
# Ensure no positions before test
assert not await sugar.has_open_position(), "Must start with no positions"

# Run test logic
ticket = await sugar.buy_market(volume=0.01)

# Verify position opened
assert await sugar.has_open_position(), "Position should be open"
```

---

## 📚 See Also

- [count_open_positions](count_open_positions.md) - Get position count
- [get_open_positions](get_open_positions.md) - Get all positions
- [get_positions_by_symbol](get_positions_by_symbol.md) - Get symbol positions
- [close_all_positions](../6.%20Position_Management/close_all_positions.md) - Close all
