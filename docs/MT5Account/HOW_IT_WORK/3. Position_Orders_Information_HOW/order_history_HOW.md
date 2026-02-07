## order_history — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `order_history()` to retrieve **historical trading data for a given time range** and perform **custom trade analysis** on the client side.

In this scenario, the method is used as a raw data source to calculate:

* number of winning trades
* number of losing trades
* win rate
* total profit and loss

All analytical logic is implemented in user code.

---

## Method Signature

```python
async def order_history(
    from_dt: datetime,
    to_dt: datetime,
    sort_mode: BMT5_ENUM_ORDER_HISTORY_SORT_TYPE = BMT5_SORT_BY_CLOSE_TIME_ASC,
    page_number: int = 0,
    items_per_page: int = 0,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and called with `await`
* `from_dt` / `to_dt` define the time range for history retrieval
* `items_per_page=0` disables pagination and returns all data at once
* The method returns historical records without any analysis

---

## 🧩 Code Example — Winning vs Losing Trades Analysis

```python
async def analyze_win_loss(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> dict:
    """Analyze winning vs losing trades"""

    data = await account.order_history(
        from_dt=from_dt,
        to_dt=to_dt,
        items_per_page=0
    )

    wins = 0
    losses = 0
    total_win_profit = 0.0
    total_loss_profit = 0.0

    for item in data.history_data:
        if item.history_deal:
            profit = item.history_deal.profit
            if profit > 0:
                wins += 1
                total_win_profit += profit
            elif profit < 0:
                losses += 1
                total_loss_profit += profit

    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

    result = {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_win_profit": total_win_profit,
        "total_loss_profit": total_loss_profit,
        "net_profit": total_win_profit + total_loss_profit
    }

    print("Trading Statistics:")
    print(f"  Total trades: {total_trades}")
    print(f"  Wins: {wins} ({win_rate:.1f}%)")
    print(f"  Losses: {losses}")
    print(f"  Win profit: ${total_win_profit:.2f}")
    print(f"  Loss profit: ${total_loss_profit:.2f}")
    print(f"  Net profit: ${result['net_profit']:+.2f}")

    return result
```

This example demonstrates a complete user-level analysis workflow built on top of raw historical data.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Calling the order_history Method

```python
data = await account.order_history(
    from_dt=from_dt,
    to_dt=to_dt,
    items_per_page=0
)
```

At this step:

* one asynchronous request is performed
* the server returns all historical records within the given time range
* no filtering, aggregation, or classification is applied

The result represents **raw historical trading data**.

---

### 2️⃣ Initializing Counters and Accumulators

```python
wins = 0
losses = 0
total_win_profit = 0.0
total_loss_profit = 0.0
```

These variables are part of user logic:

* the API does not track win/loss statistics
* all counters are initialized manually

---

### 3️⃣ Iterating Through Historical Records

```python
for item in data.history_data:
```

`history_data` is a list of history records.

Each record may represent different entities (orders, deals, etc.), so user code must decide what to process.

---

### 4️⃣ Filtering Only Executed Deals

```python
if item.history_deal:
```

In this example:

* only executed deals are analyzed
* records without a deal are skipped

This filtering rule is entirely user-defined.

---

### 5️⃣ Classifying Trades by Profit

```python
profit = item.history_deal.profit
```

The profit value is then classified:

```python
if profit > 0:
    wins += 1
    total_win_profit += profit
elif profit < 0:
    losses += 1
    total_loss_profit += profit
```

The API does not define what constitutes a win or a loss.

---

### 6️⃣ Calculating Final Statistics

```python
total_trades = wins + losses
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
```

All statistical calculations are performed in user code, including edge-case handling.

---

### 7️⃣ Building the Result Object

```python
result = {
    "total_trades": total_trades,
    "wins": wins,
    "losses": losses,
    "win_rate": win_rate,
    "net_profit": total_win_profit + total_loss_profit
}
```

The final analytical result is a pure client-side construct.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`order_history()`**:

* retrieves historical trading records
* filters by time range
* supports sorting and pagination
* does not analyze or aggregate data

**User code**:

* selects which records to process
* defines win/loss logic
* computes statistics
* produces analytical output

---

## Summary

This example illustrates the standard pattern for working with historical data:

> **retrieve raw history → filter records → analyze results → build statistics**

The `order_history()` method provides historical data access, while all analytical and decision-making logic remains on the user side.
