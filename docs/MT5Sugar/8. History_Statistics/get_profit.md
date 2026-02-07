# Get Historical Profit (`get_profit`)

> **Sugar method:** Calculates total realized profit/loss for specified time period.

**API Information:**

* **Method:** `sugar.get_profit(period, from_date, to_date)`
* **Returns:** Total profit as float
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_profit(
    self,
    period: Period = Period.TODAY,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> float
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `period` | `Period` | No | `Period.TODAY` | Time period enum (TODAY, YESTERDAY, THIS_WEEK, THIS_MONTH, CUSTOM) |
| `from_date` | `Optional[date]` | No | `None` | Start date (required if period=CUSTOM) |
| `to_date` | `Optional[date]` | No | `None` | End date (required if period=CUSTOM) |

---

## Return Value

| Type | Description |
|------|-------------|
| `float` | Total realized profit/loss in account currency (positive = profit, negative = loss) |

---

## 🏛️ Essentials

**What it does:**

- Fetches closed positions for period
- Sums profit field from all deals
- Returns total realized P&L
- Returns 0.0 if no deals

**Key behaviors:**

- Only closed positions (realized profit)
- Includes both profits and losses
- Does NOT subtract commission/swap (use `get_daily_stats` for net)
- Returns 0.0 if no deals (not None)

---

## ⚡ Under the Hood

```
MT5Sugar.get_profit()
    ↓ calls
MT5Sugar.get_deals(period, from_date, to_date)
    ↓ sums order.profit for all deals
    ↓ returns total
```

**Call chain:**

1. Sugar calls get_deals() to fetch positions
2. Sugar sums order.profit field from all positions
3. Returns total sum

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1473`
- Calls get_deals: `src/pymt5/mt5_sugar.py:1437`

---

## Convenience Methods

All these methods internally call `get_profit()` with different periods:

```python
# Today's profit
profit = await sugar.get_profit_today()
# Same as: await sugar.get_profit(Period.TODAY)

# This week's profit (Monday to today)
profit = await sugar.get_profit_this_week()
# Same as: await sugar.get_profit(Period.THIS_WEEK)

# This month's profit
profit = await sugar.get_profit_this_month()
# Same as: await sugar.get_profit(Period.THIS_MONTH)

# Custom date range
profit = await sugar.get_profit(Period.CUSTOM, date(2024, 1, 1), date(2024, 1, 31))
```

---

## When to Use

**Use `get_profit()` when:**

- Quick profit check for period
- Daily/weekly/monthly performance tracking
- Comparing profitability across periods
- Performance reports

**Don't use when:**

- Need deal details (use `get_deals()`)
- Need commission/swap breakdown (use `get_daily_stats()`)
- Need floating profit (use `get_total_profit()`)

---

## 🔗 Examples

### Example 1: Today's Performance

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account
from pymt5.constants import Period

async def daily_profit():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get today's profit
    profit = await sugar.get_profit(Period.TODAY)
    # Or: profit = await sugar.get_profit_today()

    if profit > 0:
        print(f"Today's profit: ${profit:.2f}")
    elif profit < 0:
        print(f"Today's loss: ${abs(profit):.2f}")
    else:
        print("Breakeven or no trades today")

# Output:
# Today's profit: $125.50
```

### Example 2: Weekly Progress Tracking

```python
async def weekly_progress():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get this week's profit
    weekly = await sugar.get_profit_this_week()

    # Get balance to calculate percentage
    balance = await sugar.get_balance()
    weekly_pct = (weekly / balance) * 100

    print(f"This Week's Performance:")
    print(f"  Profit: ${weekly:.2f}")
    print(f"  Return: {weekly_pct:+.2f}%")
```

### Example 3: Monthly Comparison

```python
from datetime import date

async def compare_months():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Compare last 3 months
    months = [
        ("January", date(2024, 1, 1), date(2024, 1, 31)),
        ("February", date(2024, 2, 1), date(2024, 2, 29)),
        ("March", date(2024, 3, 1), date(2024, 3, 31))
    ]

    print("Monthly Performance:")
    for name, start, end in months:
        profit = await sugar.get_profit(Period.CUSTOM, start, end)
        print(f"  {name}: ${profit:+.2f}")

# Output:
# Monthly Performance:
#   January: $+250.30
#   February: $-45.20
#   March: $+180.50
```

---

## Common Pitfalls

**Pitfall 1: Confusing with floating profit**
```python
# get_profit() = REALIZED profit (closed positions)
realized = await sugar.get_profit_today()

# get_total_profit() = FLOATING profit (open positions)
floating = await sugar.get_total_profit()

# They're different!
print(f"Realized: ${realized:.2f}")
print(f"Floating: ${floating:.2f}")
```

**Pitfall 2: Expecting None instead of 0**
```python
# Returns 0.0 if no trades, not None
profit = await sugar.get_profit_today()

if profit:  # 0.0 is falsy, but valid
    print("Made profit/loss")
```

**Solution:** Compare explicitly
```python
profit = await sugar.get_profit_today()

if profit > 0:
    print(f"Profit: ${profit:.2f}")
elif profit < 0:
    print(f"Loss: ${abs(profit):.2f}")
else:
    print("No trades or breakeven")
```

**Pitfall 3: Not accounting for commission/swap**
```python
# get_profit() only sums order.profit field
# Doesn't subtract commission and swap separately
profit = await sugar.get_profit_today()
# This is gross profit, not net
```

**Solution:** Use get_daily_stats for breakdown
```python
stats = await sugar.get_daily_stats()
print(f"Gross profit: ${stats.total_profit:.2f}")
print(f"Commission: ${stats.total_commission:.2f}")
print(f"Swap: ${stats.total_swap:.2f}")
print(f"Net profit: ${stats.net_profit:.2f}")
```

---

## Pro Tips

**Tip 1: Daily profit target**
```python
# Set daily profit target
daily_target = 100.0

profit = await sugar.get_profit_today()

if profit >= daily_target:
    print(f"Target reached: ${profit:.2f}")

    # Stop trading for the day
    await sugar.close_all_positions()
```

**Tip 2: Compare today vs yesterday**
```python
today = await sugar.get_profit_today()
yesterday = await sugar.get_profit(Period.YESTERDAY)

change = today - yesterday
print(f"Today: ${today:.2f}")
print(f"Yesterday: ${yesterday:.2f}")
print(f"Change: ${change:+.2f}")
```

**Tip 3: Profit per day of week**
```python
from datetime import date, timedelta

async def profit_by_weekday():
    """Calculate average profit by day of week."""
    from collections import defaultdict

    # Get last month's data
    today = date.today()
    start = today.replace(day=1)

    deals = await sugar.get_deals(Period.CUSTOM, start, today)

    by_weekday = defaultdict(list)
    for deal in deals:
        weekday = deal.time_open.weekday()  # 0=Mon, 6=Sun
        by_weekday[weekday].append(deal.profit)

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for i, day in enumerate(days):
        if by_weekday[i]:
            avg = sum(by_weekday[i]) / len(by_weekday[i])
            print(f"{day}: ${avg:.2f} avg")
```

---

## 📚 See Also

- [get_deals](get_deals.md) - Get historical deals (positions)
- [get_daily_stats](get_daily_stats.md) - Comprehensive daily statistics with commission/swap
- [get_total_profit](../7.%20Position_Information/get_total_profit.md) - Floating profit (open positions)
