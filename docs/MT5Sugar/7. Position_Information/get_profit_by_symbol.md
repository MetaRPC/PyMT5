# Get Profit by Symbol (`get_profit_by_symbol`)

> **Sugar method:** Returns total unrealized profit/loss for specific symbol.

**API Information:**

* **Method:** `sugar.get_profit_by_symbol(symbol)`
* **Returns:** Total floating P&L for symbol as float
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_profit_by_symbol(self, symbol: str) -> float
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
| `float` | Total floating P&L for symbol in account currency (positive = profit, negative = loss) |

---

## 🏛️ Essentials

**What it does:**

- Sums profit/loss for all positions of specified symbol
- Returns total unrealized P&L for that symbol
- Returns 0.0 if no positions for symbol
- Calculated in account currency

**Key behaviors:**

- Case-sensitive symbol matching
- Includes both BUY and SELL positions
- Returns 0.0 if no matching positions
- Floating (unrealized) P&L only

---

## ⚡ Under the Hood

```
MT5Sugar.get_profit_by_symbol()
    ↓ calls
MT5Service.get_opened_orders(sort_mode=0)
    ↓ filters by symbol
    ↓ sums pos.profit where pos.symbol == symbol
    ↓ returns total
```

**Call chain:**

1. Sugar calls Service.get_opened_orders()
2. Sugar filters position_infos by symbol
3. Sums pos.profit for matching positions
4. Returns total sum (0.0 if no matches)

**Related files:**
- Sugar: `src/pymt5/mt5_sugar.py:1383`
- Service: `src/pymt5/mt5_service.py:742`

---

## When to Use

**Use `get_profit_by_symbol()` when:**

- Monitoring symbol-specific performance
- Symbol-based risk management
- Comparing profitability across symbols
- Symbol-focused strategies

**Don't use when:**

- Need total profit for all symbols (use `get_total_profit()`)
- Need profit for specific position (use position.profit)
- Need realized profit (use history methods)

---

## 🔗 Examples

### Example 1: Basic Symbol P&L

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def symbol_profit():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get profit for EURUSD
    eurusd_profit = await sugar.get_profit_by_symbol("EURUSD")

    if eurusd_profit > 0:
        print(f"EURUSD profit: ${eurusd_profit:.2f}")
    elif eurusd_profit < 0:
        print(f"EURUSD loss: ${abs(eurusd_profit):.2f}")
    else:
        print("EURUSD breakeven or no positions")
```

### Example 2: Compare Symbol Performance

```python
async def compare_symbols():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbols = ["EURUSD", "GBPUSD", "USDJPY"]

    print("Symbol Performance:")
    for symbol in symbols:
        profit = await sugar.get_profit_by_symbol(symbol)

        if profit != 0.0:
            status = "profit" if profit > 0 else "loss"
            print(f"  {symbol}: ${profit:+.2f} ({status})")
        else:
            print(f"  {symbol}: no positions")
```

### Example 3: Symbol-Specific Stop Loss

```python
import asyncio

async def symbol_stop_loss():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    max_loss = -50.0  # Close EURUSD if loss exceeds $50

    # Open EURUSD positions
    await sugar.buy_market(symbol, volume=0.1)

    print(f"Monitoring {symbol} for max loss ${max_loss}...")

    while True:
        profit = await sugar.get_profit_by_symbol(symbol)

        print(f"{symbol} P&L: ${profit:.2f}")

        if profit <= max_loss:
            print(f"Max loss reached, closing all {symbol} positions")

            # Close all symbol positions
            closed = await sugar.close_all_positions(symbol=symbol)
            print(f"Closed {closed} {symbol} positions")
            break

        await asyncio.sleep(5)
```

---

## Common Pitfalls

**Pitfall 1: Case-sensitive symbol**
```python
# ERROR: Symbol case matters
profit = await sugar.get_profit_by_symbol("eurusd")
# Returns 0.0 if positions are "EURUSD"
```

**Solution:** Use uppercase symbols
```python
profit = await sugar.get_profit_by_symbol("EURUSD")
```

**Pitfall 2: Expecting None instead of 0**
```python
# Returns 0.0 if no positions, not None
profit = await sugar.get_profit_by_symbol("EURUSD")

if profit:  # 0.0 is falsy
    print("Have profit/loss")
```

**Solution:** Compare explicitly
```python
profit = await sugar.get_profit_by_symbol("EURUSD")

if profit != 0.0:
    print(f"EURUSD P&L: ${profit:.2f}")
else:
    print("EURUSD flat or no positions")
```

**Pitfall 3: Not checking if positions exist**
```python
# Getting profit for symbol without positions
profit = await sugar.get_profit_by_symbol("XAUUSD")
# Returns 0.0, can't distinguish between:
# 1. No positions
# 2. Positions at breakeven
```

**Solution:** Check position count first
```python
count = await sugar.count_open_positions("XAUUSD")

if count > 0:
    profit = await sugar.get_profit_by_symbol("XAUUSD")
    print(f"XAUUSD {count} positions: ${profit:.2f}")
else:
    print("No XAUUSD positions")
```

---

## Pro Tips

**Tip 1: Find best/worst performing symbol**
```python
# Get all traded symbols
all_positions = await sugar.get_open_positions()
symbols = set(p.symbol for p in all_positions)

# Find best performer
profits = {}
for symbol in symbols:
    profits[symbol] = await sugar.get_profit_by_symbol(symbol)

best_symbol = max(profits, key=profits.get)
worst_symbol = min(profits, key=profits.get)

print(f"Best: {best_symbol} (${profits[best_symbol]:.2f})")
print(f"Worst: {worst_symbol} (${profits[worst_symbol]:.2f})")
```

**Tip 2: Symbol exposure with P&L**
```python
async def symbol_exposure(sugar, symbol):
    """Get complete symbol exposure info."""
    count = await sugar.count_open_positions(symbol)
    profit = await sugar.get_profit_by_symbol(symbol)

    positions = await sugar.get_positions_by_symbol(symbol)
    total_volume = sum(p.volume for p in positions)

    return {
        "symbol": symbol,
        "count": count,
        "volume": total_volume,
        "profit": profit
    }

# Usage
exposure = await symbol_exposure(sugar, "EURUSD")
print(f"{exposure['symbol']}: {exposure['count']} pos, "
      f"{exposure['volume']} lots, ${exposure['profit']:.2f}")
```

**Tip 3: Close symbol if unprofitable**
```python
async def close_losing_symbols(sugar, max_loss=-20.0):
    """Close positions for symbols with loss > threshold."""
    all_positions = await sugar.get_open_positions()
    symbols = set(p.symbol for p in all_positions)

    for symbol in symbols:
        profit = await sugar.get_profit_by_symbol(symbol)

        if profit < max_loss:
            closed = await sugar.close_all_positions(symbol=symbol)
            print(f"Closed {closed} {symbol} positions (loss: ${profit:.2f})")
```

---

## 📚 See Also

- [get_total_profit](get_total_profit.md) - Total profit all symbols
- [get_positions_by_symbol](get_positions_by_symbol.md) - Get symbol positions
- [count_open_positions](count_open_positions.md) - Count by symbol
- [close_all_positions](../6.%20Position_Management/close_all_positions.md) - Close all for symbol
