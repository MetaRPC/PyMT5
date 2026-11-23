# Get Positions by Symbol (`get_positions_by_symbol`)

> **Sugar method:** Returns all positions for specific symbol.

**API Information:**

* **Method:** `sugar.get_positions_by_symbol(symbol)`
* **Returns:** List of positions for symbol (may be empty)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_positions_by_symbol(self, symbol: str)
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Yes | - | Trading symbol (e.g., "EURUSD") |

---

## Return Value

| Type | Description |
|------|-------------|
| `list[PositionInfo]` | List of positions for symbol (empty list if none) |

---

## 🏛️ Essentials

**What it does:**

- Filters all open positions by symbol
- Returns list of matching positions
- Returns empty list if no matches
- Case-sensitive symbol matching

**Key behaviors:**

- Returns list (may be empty)
- Exact symbol match required
- Includes both BUY and SELL positions
- Multiple positions for same symbol supported

---

## ⚡ Under the Hood

```
MT5Sugar.get_positions_by_symbol()
    ↓ calls
MT5Service.get_opened_orders(sort_mode=0)
    ↓ filters position_infos
    ↓ pos.symbol == symbol
    ↓ returns filtered list
```

**Call chain:**

1. Sugar calls Service.get_opened_orders()
2. Sugar filters position_infos by symbol
3. Returns list of matching positions
4. Returns empty list if no matches

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1353`
- Service: `src/pymt5/mt5_service.py:742`

---

## When to Use

**Use `get_positions_by_symbol()` when:**

- Managing positions for specific symbol
- Calculating symbol-specific exposure
- Closing all positions for symbol
- Symbol-focused strategies

**Don't use when:**

- Need all positions (use `get_open_positions()`)
- Only need count (use `count_open_positions(symbol)`)
- Only checking existence (use `has_open_position(symbol)`)

---

## 🔗 Examples

### Example 1: Get EURUSD Positions

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def eurusd_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get all EURUSD positions
    eurusd_positions = await sugar.get_positions_by_symbol("EURUSD")

    if not eurusd_positions:
        print("No EURUSD positions")
    else:
        print(f"EURUSD positions: {len(eurusd_positions)}")

        for pos in eurusd_positions:
            direction = "BUY" if pos.type == 0 else "SELL"
            print(f"  #{pos.ticket}: {direction} {pos.volume} lots, "
                  f"${pos.profit:.2f}")

# Output:
# EURUSD positions: 2
#   #123456: BUY 0.1 lots, $12.50
#   #123457: SELL 0.05 lots, -$3.20
```

### Example 2: Close All Symbol Positions

```python
async def close_symbol_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "GBPUSD"

    # Get all GBPUSD positions
    positions = await sugar.get_positions_by_symbol(symbol)

    print(f"Closing {len(positions)} {symbol} positions...")

    closed = 0
    for pos in positions:
        success = await sugar.close_position(pos.ticket)

        if success:
            closed += 1
            print(f"Closed #{pos.ticket}")

    print(f"Closed {closed}/{len(positions)} positions")
```

### Example 3: Symbol Exposure Analysis

```python
async def symbol_exposure():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    positions = await sugar.get_positions_by_symbol(symbol)

    if positions:
        # Calculate net exposure
        buy_volume = sum(p.volume for p in positions if p.type == 0)
        sell_volume = sum(p.volume for p in positions if p.type == 1)
        net_volume = buy_volume - sell_volume

        # Calculate P&L
        total_profit = sum(p.profit for p in positions)

        print(f"{symbol} Exposure:")
        print(f"  BUY: {buy_volume} lots")
        print(f"  SELL: {sell_volume} lots")
        print(f"  NET: {net_volume:+.2f} lots")
        print(f"  P&L: ${total_profit:.2f}")
```

---

## Common Pitfalls

**Pitfall 1: Case sensitivity**
```python
# ERROR: Symbol case matters
positions = await sugar.get_positions_by_symbol("eurusd")
# Returns [] if positions are "EURUSD"
```

**Solution:** Use uppercase symbol names
```python
positions = await sugar.get_positions_by_symbol("EURUSD")
# or
symbol = "eurusd".upper()
positions = await sugar.get_positions_by_symbol(symbol)
```

**Pitfall 2: Assuming list is never empty**
```python
# ERROR: Crashes if no positions
positions = await sugar.get_positions_by_symbol("EURUSD")
first = positions[0]  # IndexError if empty
```

**Solution:** Check if list is empty
```python
positions = await sugar.get_positions_by_symbol("EURUSD")

if positions:
    first = positions[0]
else:
    print("No EURUSD positions")
```

**Pitfall 3: Modifying while iterating**
```python
# ERROR: Closing positions while iterating
positions = await sugar.get_positions_by_symbol("EURUSD")

for pos in positions:
    await sugar.close_position(pos.ticket)
    # List won't update during iteration
```

**Solution:** Collect tickets first
```python
positions = await sugar.get_positions_by_symbol("EURUSD")
tickets = [p.ticket for p in positions]

for ticket in tickets:
    await sugar.close_position(ticket)
```

---

## Pro Tips

**Tip 1: Calculate net position**
```python
positions = await sugar.get_positions_by_symbol("EURUSD")

# Calculate net exposure (BUY - SELL)
net = sum(
    p.volume if p.type == 0 else -p.volume
    for p in positions
)

if net > 0:
    print(f"Net LONG: {net} lots")
elif net < 0:
    print(f"Net SHORT: {abs(net)} lots")
else:
    print("Flat (hedged)")
```

**Tip 2: Find largest position**
```python
positions = await sugar.get_positions_by_symbol("EURUSD")

if positions:
    largest = max(positions, key=lambda p: p.volume)
    print(f"Largest position: #{largest.ticket} ({largest.volume} lots)")
```

**Tip 3: Check all symbols at once**
```python
async def analyze_all_symbols(sugar):
    """Analyze exposure for all traded symbols."""
    all_positions = await sugar.get_open_positions()

    # Group by symbol
    symbols = set(p.symbol for p in all_positions)

    for symbol in symbols:
        symbol_positions = await sugar.get_positions_by_symbol(symbol)

        total_volume = sum(p.volume for p in symbol_positions)
        total_profit = sum(p.profit for p in symbol_positions)

        print(f"{symbol}: {len(symbol_positions)} pos, "
              f"{total_volume} lots, ${total_profit:.2f}")
```

---

## 📚 See Also

- [get_open_positions](get_open_positions.md) - Get all positions
- [get_position_by_ticket](get_position_by_ticket.md) - Get specific position
- [count_open_positions](count_open_positions.md) - Count by symbol
- [get_profit_by_symbol](get_profit_by_symbol.md) - Symbol profit
- [close_all_positions](../6.%20Position_Management/close_all_positions.md) - Close all for symbol
