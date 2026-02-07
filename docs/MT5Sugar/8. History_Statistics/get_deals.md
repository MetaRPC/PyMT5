# Get Historical Deals (`get_deals`)

> **Sugar method:** Retrieves closed positions (deals) for specified time period.

**API Information:**

* **Method:** `sugar.get_deals(period, from_date, to_date)`
* **Returns:** List of closed position objects
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_deals(
    self,
    period: Period = Period.TODAY,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> List
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
| `List` | List of closed position objects (empty list if no deals) |

---

## 🏛️ Essentials

**What it does:**

- Fetches closed positions from history
- Supports predefined periods via Period enum
- Returns full position details (ticket, symbol, profit, commission, swap, etc.)
- Fetches up to 10,000 positions per request

**Key behaviors:**

- Uses positions_history (includes profit/commission/swap)
- Sorted by open time ascending
- Returns empty list if no deals
- CUSTOM period requires from_date and to_date

---

## ⚡ Under the Hood

```
MT5Sugar.get_deals()
    ↓ converts period to datetime range
MT5Sugar._get_period_range()
    ↓ calls
MT5Service.get_positions_history()
    ↓ calls
MT5Account.positions_history()
    ↓ gRPC protobuf
AccountHelperService.PositionsHistory()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar converts Period enum to datetime range
2. Sugar calls Service.get_positions_history() with date range
3. Service forwards to Account.positions_history()
4. Account sends gRPC request to terminal
5. Returns list of history_positions (up to 10,000)

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1437`
- Service: `src/pymt5/mt5_service.py:810`
- Account: `package/helpers/mt5_account.py:1475`

---

## Convenience Methods

All these methods internally call `get_deals()` with different periods:

```python
# Today's deals
deals = await sugar.get_deals_today()
# Same as: await sugar.get_deals(Period.TODAY)

# Yesterday's deals
deals = await sugar.get_deals_yesterday()
# Same as: await sugar.get_deals(Period.YESTERDAY)

# This week's deals (Monday to today)
deals = await sugar.get_deals_this_week()
# Same as: await sugar.get_deals(Period.THIS_WEEK)

# This month's deals
deals = await sugar.get_deals_this_month()
# Same as: await sugar.get_deals(Period.THIS_MONTH)

# Custom date range
deals = await sugar.get_deals_date_range(date(2024, 1, 1), date(2024, 1, 31))
# Same as: await sugar.get_deals(Period.CUSTOM, date(2024, 1, 1), date(2024, 1, 31))
```

---

## When to Use

**Use `get_deals()` when:**

- Analyzing trading history
- Calculating statistics (win rate, avg profit, etc.)
- Reviewing past trades
- Building trading journal

**Don't use when:**

- Need only profit total (use `get_profit()`)
- Need current open positions (use `get_open_positions()`)
- Need real-time data (this is historical)

---

## 🔗 Examples

### Example 1: Today's Deals

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account
from pymt5.constants import Period

async def todays_deals():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get today's deals
    deals = await sugar.get_deals(Period.TODAY)
    # Or: deals = await sugar.get_deals_today()

    print(f"Today's deals: {len(deals)}")

    for deal in deals:
        print(f"#{deal.ticket}: {deal.symbol} {deal.volume} lots, "
              f"Profit: ${deal.profit:.2f}")

# Output:
# Today's deals: 5
# #123456: EURUSD 0.1 lots, Profit: $12.50
# #123457: GBPUSD 0.05 lots, Profit: -$3.20
```

### Example 2: This Week's Performance

```python
from datetime import date

async def weekly_performance():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get this week's deals
    deals = await sugar.get_deals_this_week()

    if deals:
        # Calculate statistics
        total_trades = len(deals)
        winning = sum(1 for d in deals if d.profit > 0)
        losing = sum(1 for d in deals if d.profit < 0)
        win_rate = (winning / total_trades) * 100

        total_profit = sum(d.profit for d in deals)

        print(f"This Week's Performance:")
        print(f"  Total trades: {total_trades}")
        print(f"  Win rate: {win_rate:.1f}%")
        print(f"  Total P&L: ${total_profit:.2f}")
```

### Example 3: Custom Date Range Analysis

```python
from datetime import date

async def january_analysis():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get January 2024 deals
    deals = await sugar.get_deals(
        period=Period.CUSTOM,
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31)
    )
    # Or: deals = await sugar.get_deals_date_range(date(2024, 1, 1), date(2024, 1, 31))

    # Analyze by symbol
    from collections import defaultdict
    by_symbol = defaultdict(list)

    for deal in deals:
        by_symbol[deal.symbol].append(deal)

    print("January 2024 by Symbol:")
    for symbol, symbol_deals in by_symbol.items():
        profit = sum(d.profit for d in symbol_deals)
        print(f"  {symbol}: {len(symbol_deals)} trades, ${profit:.2f}")
```

---

## Common Pitfalls

**Pitfall 1: Missing from_date/to_date for CUSTOM period**
```python
# ERROR: CUSTOM requires dates
try:
    deals = await sugar.get_deals(Period.CUSTOM)
except ValueError as e:
    print(e)  # "from_date and to_date required for CUSTOM period"
```

**Solution:** Always provide dates for CUSTOM
```python
deals = await sugar.get_deals(
    Period.CUSTOM,
    from_date=date(2024, 1, 1),
    to_date=date(2024, 1, 31)
)
```

**Pitfall 2: Assuming list is never empty**
```python
# ERROR: Crashes if no deals
deals = await sugar.get_deals_today()
first_deal = deals[0]  # IndexError if empty
```

**Solution:** Check if list is empty
```python
deals = await sugar.get_deals_today()

if deals:
    first_deal = deals[0]
else:
    print("No deals today")
```

**Pitfall 3: Exceeding 10,000 position limit**
```python
# Get deals for entire year
deals = await sugar.get_deals(
    Period.CUSTOM,
    from_date=date(2023, 1, 1),
    to_date=date(2023, 12, 31)
)
# Returns max 10,000 positions
```

**Solution:** Split large date ranges
```python
# Get deals month by month for large ranges
from datetime import date, timedelta

all_deals = []
start = date(2023, 1, 1)
end = date(2023, 12, 31)

current = start
while current <= end:
    month_end = min(current.replace(day=28) + timedelta(days=4), end)
    month_end = month_end.replace(day=1) - timedelta(days=1)

    deals = await sugar.get_deals(Period.CUSTOM, current, month_end)
    all_deals.extend(deals)

    current = month_end + timedelta(days=1)
```

---

## Pro Tips

**Tip 1: Calculate win rate**

```python
deals = await sugar.get_deals_today()

if deals:
    winners = [d for d in deals if d.profit > 0]
    losers = [d for d in deals if d.profit < 0]

    win_rate = (len(winners) / len(deals)) * 100
    print(f"Win rate: {win_rate:.1f}%")
```

**Tip 2: Find best/worst trade**
```python
deals = await sugar.get_deals_this_week()

if deals:
    best = max(deals, key=lambda d: d.profit)
    worst = min(deals, key=lambda d: d.profit)

    print(f"Best trade: #{best.ticket} ${best.profit:.2f}")
    print(f"Worst trade: #{worst.ticket} ${worst.profit:.2f}")
```

**Tip 3: Average profit per trade**
```python
deals = await sugar.get_deals_this_month()

if deals:
    total_profit = sum(d.profit for d in deals)
    avg_profit = total_profit / len(deals)

    print(f"Average per trade: ${avg_profit:.2f}")
```

---

## 📚 See Also

- [get_profit](get_profit.md) - Get total profit for period
- [get_daily_stats](get_daily_stats.md) - Comprehensive daily statistics
- [get_open_positions](../7.%20Position_Information/get_open_positions.md) - Current positions
