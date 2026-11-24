## positions_history — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `positions_history()` to retrieve **the history of closed positions for a given period** and use it for **exporting data to an external format (CSV)**.

In this scenario, the method serves as a source of historical data, while all formatting, calculation, and result saving logic is implemented on the user code side.

---

## Method Signature

```python
async def positions_history(
    sort_type: AH_ENUM_POSITIONS_HISTORY_SORT_TYPE,
    open_from: Optional[datetime] = None,
    open_to: Optional[datetime] = None,
    page: int = 0,
    size: int = 0,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* the method is asynchronous and called with `await`
* `open_from` / `open_to` define the position opening time range
* `size=0` means all records are returned in one response
* the method returns only historical data without any aggregation

---

## 🧩 Code Example — Exporting Position History to CSV

```python
import csv

async def export_positions_to_csv(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    filename: str = "positions_history.csv"
):
    """Export closed positions to CSV"""

    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Ticket', 'Symbol', 'Open Time', 'Close Time',
            'Volume', 'Open Price', 'Close Price',
            'Profit', 'Commission', 'Swap', 'Total'
        ])

        for pos in data.history_positions:
            open_time = pos.open_time.ToDatetime()
            close_time = pos.close_time.ToDatetime()
            total = pos.profit - pos.commission + pos.swap

            writer.writerow([
                pos.position_ticket,
                pos.symbol,
                open_time.strftime('%Y-%m-%d %H:%M:%S'),
                close_time.strftime('%Y-%m-%d %H:%M:%S'),
                pos.volume,
                pos.open_price,
                pos.close_price,
                pos.profit,
                pos.commission,
                pos.swap,
                total
            ])

    print(f"[OK] Exported {len(data.history_positions)} positions to {filename}")
```

This example demonstrates a complete user-level data export scenario built on top of a low-level method.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Calling the positions_history Method

```python
data = await account.positions_history(
    sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
    open_from=from_dt,
    open_to=to_dt
)
```

At this step:

* one asynchronous request is made to the server
* the server filters historical positions by opening time
* data is returned as a `history_positions` list

The method does not perform any calculations or modify data.

---

### 2️⃣ Preparing the CSV File

```python
with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
```

This is entirely user logic:

* format selection (CSV)
* encoding
* data writing method

The API does not participate in this process.

---

### 3️⃣ Writing the Header

```python
writer.writerow([
    'Ticket', 'Symbol', 'Open Time', 'Close Time',
    'Volume', 'Open Price', 'Close Price',
    'Profit', 'Commission', 'Swap', 'Total'
])
```

Column headers:

* are user-defined
* reflect the selected set of fields

---

### 4️⃣ Iterating Through Historical Positions

```python
for pos in data.history_positions:
```

Each `pos` element represents one closed position and contains:

* identifiers
* opening and closing prices
* financial metrics

---

### 5️⃣ Time Conversion

```python
open_time = pos.open_time.ToDatetime()
close_time = pos.close_time.ToDatetime()
```

Time values:

* arrive in protobuf format
* are converted to `datetime` for convenient formatting

---

### 6️⃣ User Calculations

```python
total = pos.profit - pos.commission + pos.swap
```

Calculating the final position result:

* performed on the client side
* the API does not calculate aggregated values

---

### 7️⃣ Writing a Row to CSV

```python
writer.writerow([...])
```

At this step:

* the required position fields are selected
* data is converted to string format
* one CSV file row is formed

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`positions_history()`**:

* returns position history based on specified filters
* performs sorting and time filtering
* does not analyze or format data

**User code**:

* defines the export format
* performs calculations
* manages data output

---

## Summary

This example illustrates the standard pattern for working with historical data:

> **retrieve history → transform data → save to external format**

The `positions_history()` method provides access to historical positions, while all export and data processing logic is fully implemented on the user side.
