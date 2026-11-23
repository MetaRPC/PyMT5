# Get Daily Statistics (`get_daily_stats`)

> **Sugar method:** Returns comprehensive trading statistics for specific day.

**API Information:**

* **Method:** `sugar.get_daily_stats(target_date)`
* **Returns:** `DailyStats` dataclass with complete statistics
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_daily_stats(self, target_date: Optional[date] = None) -> DailyStats
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target_date` | `Optional[date]` | No | `None` | Date to get stats for (None = today) |

---

## Return Value

`DailyStats` dataclass with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `date` | `date` | The date for these statistics |
| `deals_count` | `int` | Number of closed positions |
| `profit` | `float` | Total gross profit/loss |
| `commission` | `float` | Total commission paid |
| `swap` | `float` | Total swap (rollover) |
| `volume` | `float` | Total volume traded in lots |

**Calculated field:**

- `net_profit = profit + commission + swap` (calculate manually)

---

## 🏛️ Essentials

**What it does:**

- Fetches all closed positions for specified day
- Calculates comprehensive statistics
- Returns structured DailyStats object
- Includes commission and swap breakdown

**Key behaviors:**

- Defaults to today if no date specified
- Fetches up to 10,000 positions
- Commission is usually negative
- Swap can be positive or negative
- Returns stats even if no deals (all zeros)

---

## ⚡ Under the Hood

```
MT5Sugar.get_daily_stats()
    ↓ converts date to datetime range
    ↓ calls
MT5Service.get_positions_history()
    ↓ iterates positions
    ↓ sums profit, commission, swap, volume
    ↓ returns DailyStats dataclass
```

**Call chain:**

1. Sugar converts date to datetime range (00:00:00 to 23:59:59)
2. Sugar calls Service.get_positions_history() for day
3. Sugar iterates through history_positions
4. Sugar sums: profit, commission, swap, volume
5. Returns DailyStats dataclass with results

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:2061`
- DailyStats: `src/pymt5/mt5_sugar.py:209`
- Service: `src/pymt5/mt5_service.py:810`

---

## When to Use

**Use `get_daily_stats()` when:**

- Need complete daily breakdown
- Tracking commission costs
- Analyzing net profit after fees
- Daily performance reports
- Volume analysis

**Don't use when:**

- Only need gross profit (use `get_profit()`)
- Need deal details (use `get_deals()`)
- Need multi-day statistics (call multiple times)

---

## 🔗 Examples

### Example 1: Today's Complete Stats

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def daily_report():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get today's statistics
    stats = await sugar.get_daily_stats()

    # Calculate net profit
    net_profit = stats.profit + stats.commission + stats.swap

    print(f"Daily Report for {stats.date}:")
    print(f"  Trades: {stats.deals_count}")
    print(f"  Volume: {stats.volume} lots")
    print(f"  Gross Profit: ${stats.profit:.2f}")
    print(f"  Commission: ${stats.commission:.2f}")
    print(f"  Swap: ${stats.swap:.2f}")
    print(f"  Net Profit: ${net_profit:.2f}")

# Output:
# Daily Report for 2026-02-03:
#   Trades: 12
#   Volume: 1.5 lots
#   Gross Profit: $180.50
#   Commission: $-15.30
#   Swap: $-2.10
#   Net Profit: $163.10
```

### Example 2: Compare Multiple Days

```python
from datetime import date, timedelta

async def compare_days():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get last 5 days
    print("Last 5 Days Performance:")

    for i in range(5):
        target = date.today() - timedelta(days=i)
        stats = await sugar.get_daily_stats(target)

        net = stats.profit + stats.commission + stats.swap

        print(f"{target}: {stats.deals_count} trades, "
              f"${net:+.2f} net P&L")

# Output:
# Last 5 Days Performance:
# 2026-02-03: 12 trades, $+163.10 net P&L
# 2026-02-02: 8 trades, $-45.20 net P&L
# 2026-02-01: 15 trades, $+220.50 net P&L
```

### Example 3: Cost Analysis

```python
async def cost_analysis():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    stats = await sugar.get_daily_stats()

    if stats.deals_count > 0:
        # Calculate costs per trade
        avg_commission = abs(stats.commission) / stats.deals_count
        total_costs = abs(stats.commission) + abs(stats.swap)
        costs_pct = (total_costs / abs(stats.profit)) * 100 if stats.profit != 0 else 0

        print(f"Cost Analysis:")
        print(f"  Average commission per trade: ${avg_commission:.2f}")
        print(f"  Total trading costs: ${total_costs:.2f}")
        print(f"  Costs as % of gross profit: {costs_pct:.1f}%")
```

---

## Common Pitfalls

**Pitfall 1: Forgetting commission is negative**
```python
stats = await sugar.get_daily_stats()

# ERROR: Commission is already negative, don't subtract again
net_profit = stats.profit - stats.commission  # WRONG!

# CORRECT: Commission is negative, so add it
net_profit = stats.profit + stats.commission  # RIGHT
```

**Pitfall 2: Not checking deals_count**
```python
stats = await sugar.get_daily_stats()

# Calculating average without checking for zero
avg_profit = stats.profit / stats.deals_count  # ZeroDivisionError if no deals
```

**Solution:** Always check deals_count first
```python
stats = await sugar.get_daily_stats()

if stats.deals_count > 0:
    avg_profit = stats.profit / stats.deals_count
else:
    avg_profit = 0.0
```

**Pitfall 3: Expecting historical data to exist**
```python
# Asking for date before account existed
stats = await sugar.get_daily_stats(date(2020, 1, 1))
# Returns all zeros, not an error
```

**Solution:** Check if data exists
```python
stats = await sugar.get_daily_stats(date(2020, 1, 1))

if stats.deals_count == 0:
    print("No trades on this date")
```

---

## Pro Tips

**Tip 1: Calculate net profit helper**
```python
def calculate_net(stats):
    """Calculate net profit from DailyStats."""
    return stats.profit + stats.commission + stats.swap

stats = await sugar.get_daily_stats()
net = calculate_net(stats)
print(f"Net profit: ${net:.2f}")
```

**Tip 2: Weekly summary**
```python
from datetime import date, timedelta

async def weekly_summary():
    """Aggregate weekly statistics."""
    total_deals = 0
    total_profit = 0.0
    total_commission = 0.0
    total_swap = 0.0
    total_volume = 0.0

    # Get last 7 days
    for i in range(7):
        target = date.today() - timedelta(days=i)
        stats = await sugar.get_daily_stats(target)

        total_deals += stats.deals_count
        total_profit += stats.profit
        total_commission += stats.commission
        total_swap += stats.swap
        total_volume += stats.volume

    net_profit = total_profit + total_commission + total_swap

    print(f"Weekly Summary:")
    print(f"  Total trades: {total_deals}")
    print(f"  Total volume: {total_volume} lots")
    print(f"  Net profit: ${net_profit:.2f}")
```

**Tip 3: Profit factor calculation**
```python
async def profit_factor():
    """Calculate profit factor (gross profit / gross loss)."""
    from datetime import date, timedelta

    gross_profit = 0.0
    gross_loss = 0.0

    # Get this month
    for i in range(30):
        target = date.today() - timedelta(days=i)
        deals = await sugar.get_deals(Period.CUSTOM, target, target)

        for deal in deals:
            if deal.profit > 0:
                gross_profit += deal.profit
            else:
                gross_loss += abs(deal.profit)

    if gross_loss > 0:
        pf = gross_profit / gross_loss
        print(f"Profit Factor: {pf:.2f}")
    else:
        print("No losing trades")
```

---

## 📚 See Also

- [get_deals](get_deals.md) - Get historical deals
- [get_profit](get_profit.md) - Get gross profit for period
- [get_total_profit](../7.%20Position_Information/get_total_profit.md) - Floating profit
