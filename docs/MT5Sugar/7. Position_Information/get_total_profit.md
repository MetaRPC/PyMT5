# Get Total Floating Profit (`get_total_profit`)

> **Sugar method:** Returns total unrealized profit/loss across all open positions.

**API Information:**

* **Method:** `sugar.get_total_profit()`
* **Returns:** Total floating P&L as float
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_total_profit(self) -> float
```

---

## 🔽 Input Parameters

None

---

## Return Value

| Type | Description |
|------|-------------|
| `float` | Total floating profit/loss in account currency (positive = profit, negative = loss) |

---

## 🏛️ Essentials

**What it does:**

- Sums profit/loss from all open positions
- Returns total unrealized P&L
- Returns 0.0 if no positions
- Calculated in account currency (USD, EUR, etc.)

**Key behaviors:**

- Includes ALL open positions
- Positive = total profit
- Negative = total loss
- Returns 0.0 if no positions (not None)
- Floating (unrealized) P&L only

---

## ⚡ Under the Hood

```
MT5Sugar.get_total_profit()
    ↓ calls
MT5Service.get_opened_orders(sort_mode=0)
    ↓ sums all pos.profit values
    ↓ returns total
```

**Call chain:**

1. Sugar calls Service.get_opened_orders()
2. Sugar iterates through position_infos
3. Sums pos.profit for each position
4. Returns total sum

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1377`
- Service: `src/pymt5/mt5_service.py:742`

---

## When to Use

**Use `get_total_profit()` when:**

- Monitoring overall account performance
- Risk management (close all if loss too high)
- Daily profit/loss tracking
- Account-wide P&L limits

**Don't use when:**

- Need profit for specific symbol (use `get_profit_by_symbol()`)
- Need realized profit (use history methods)
- Need floating profit property (use `get_floating_profit()`)

---

## 🔗 Examples

### Example 1: Basic P&L Check

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def check_profit():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get total profit
    total = await sugar.get_total_profit()

    if total > 0:
        print(f"Total profit: ${total:.2f}")
    elif total < 0:
        print(f"Total loss: ${abs(total):.2f}")
    else:
        print("Breakeven or no positions")
```

### Example 2: Stop Loss All Positions

```python
import asyncio

async def stop_loss_monitor():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    max_loss = -100.0  # Close all if loss exceeds $100

    while True:
        total_profit = await sugar.get_total_profit()

        print(f"Current P&L: ${total_profit:.2f}")

        if total_profit <= max_loss:
            print(f"Max loss reached (${total_profit:.2f}), closing all positions")
            closed = await sugar.close_all_positions()
            print(f"Closed {closed} positions")
            break

        await asyncio.sleep(5)
```

### Example 3: Profit Target

```python
async def profit_target():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Open multiple positions
    await sugar.buy_market("EURUSD", volume=0.1)
    await sugar.buy_market("GBPUSD", volume=0.1)

    target_profit = 50.0

    print(f"Monitoring for ${target_profit} total profit...")

    while True:
        total = await sugar.get_total_profit()

        if total >= target_profit:
            print(f"Target reached: ${total:.2f}")

            # Close all and lock in profit
            await sugar.close_all_positions()
            break

        print(f"Current: ${total:.2f} / ${target_profit:.2f}")
        await asyncio.sleep(5)
```

---

## Common Pitfalls

**Pitfall 1: Confusing with floating_profit property**
```python
# Both do same thing, but different syntax
total1 = await sugar.get_total_profit()      # Method
total2 = await sugar.get_floating_profit()   # Also method (Account_Properties)

# Use get_floating_profit() from Account_Properties group
```

**Pitfall 2: Expecting None instead of 0**
```python
# Returns 0.0 if no positions, not None
profit = await sugar.get_total_profit()

if profit:  # 0.0 is falsy, but valid
    print("Have profit/loss")
```

**Solution:** Compare explicitly
```python
profit = await sugar.get_total_profit()

if profit != 0.0:
    print(f"P&L: ${profit:.2f}")
else:
    print("No P&L or no positions")
```

**Pitfall 3: Using for realized profit**
```python
# ERROR: get_total_profit() only shows OPEN positions
# Closed positions profit not included
profit = await sugar.get_total_profit()
# This is only floating (unrealized) profit
```

**Solution:** Use history methods for realized profit
```python
# Floating profit (open positions)
floating = await sugar.get_total_profit()

# Realized profit (closed today)
# realized = await sugar.get_profit_today()

print(f"Floating: ${floating:.2f}")
# print(f"Realized: ${realized:.2f}")
```

---

## Pro Tips

**Tip 1: Calculate profit percentage**

```python
balance = await sugar.get_balance()
profit = await sugar.get_total_profit()

profit_pct = (profit / balance) * 100

print(f"Floating P&L: ${profit:.2f} ({profit_pct:+.2f}%)")
```

**Tip 2: Compare to margin used**
```python
margin = await sugar.get_margin()
profit = await sugar.get_total_profit()

if margin > 0:
    return_on_margin = (profit / margin) * 100
    print(f"Return on margin: {return_on_margin:+.2f}%")
```

**Tip 3: Log profit changes**
```python
import asyncio

async def log_profit_changes():
    previous = await sugar.get_total_profit()

    while True:
        await asyncio.sleep(10)

        current = await sugar.get_total_profit()
        change = current - previous

        if abs(change) >= 1.0:  # Log if change >= $1
            print(f"P&L changed: ${previous:.2f} → ${current:.2f} "
                  f"({change:+.2f})")
            previous = current
```

---

## 📚 See Also

- [get_profit_by_symbol](get_profit_by_symbol.md) - Profit for specific symbol
- [get_floating_profit](../2.%20Account_Properties/get_floating_profit.md) - Same as get_total_profit
- [get_open_positions](get_open_positions.md) - Get all positions
- [close_all_positions](../6.%20Position_Management/close_all_positions.md) - Close all
