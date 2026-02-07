## on_position_profit — How it works

---

## 📌 Overview

This example shows how to use the low-level streaming method `on_position_profit()` for **reacting to profit changes of open positions in real time** and executing automatic trading actions when a specified condition is met.

In this case, a logical take-profit is implemented:

> if position profit reaches a specified value — the position is automatically closed.

Important: this is **not a server-side TP**, but user logic built on top of the update stream.

---

## Method Signature

```python
async def on_position_profit(
    interval_ms: int,
    ignore_empty: bool = True,
    cancellation_event: Optional[asyncio.Event] = None,
):
    -> AsyncIterator[OnPositionProfitData]
```

Key points:

* the method is asynchronous and streaming (`async for`)
* works over time, not as a one-time call
* returns **updates**, not a complete state snapshot
* does not make trading decisions

---

## 🧩 Code Example — Auto take-profit on profit target

```python
async for update in account.on_position_profit(
    interval_ms=500,
    ignore_empty=True
):
    for pos in update.updated_positions:
        if pos.profit >= target_profit:
            close_req = OrderCloseRequest(
                ticket=pos.ticket,
                volume=0,
                slippage=20,
                comment="Auto TP"
            )

            result = await account.order_close(close_req)

            if result.returned_code == 10009:
                print(f"[SUCCESS] Position #{pos.ticket} closed")
            else:
                print(f"[FAILED] Code: {result.returned_code}")
                print(f"Description: {result.returned_code_description}")
```

---

## 🟢 Detailed Explanation

---

### 1️⃣ Subscribing to Profit Update Stream

```python
async for update in account.on_position_profit(...):
```

At this stage:

* a subscription to profit updates is created
* the server periodically sends data
* the loop runs until explicitly stopped

This is a **stream**, not a regular request.

---

### 2️⃣ Update Interval

```python
interval_ms=500
```

The parameter sets:

* server polling frequency
* balance between freshness and load

The method does not work "on market event", but at a specified interval.

---

### 3️⃣ Filtering Empty Updates

```python
ignore_empty=True
```

When enabled:

* frames without changes are skipped
* user code receives only meaningful events

This simplifies processing and reduces noise.

---

### 4️⃣ Working Only with Changed Positions

```python
for pos in update.updated_positions:
```

Important:

* not all positions come in every update
* only those whose profit has changed
* this is a typical event-driven pattern

---

### 5️⃣ Checking User Condition

```python
if pos.profit >= target_profit:
```

Here **user business logic** is executed:

* the API does not know what target profit is
* the API does not compare values
* the API only reports facts

---

### 6️⃣ Initiating Trading Action

```python
result = await account.order_close(close_req)
```

When condition is met:

* a position close command is sent
* account state may change
* a real trading operation is executed

---

### 7️⃣ Checking Close Result

```python
if result.returned_code == 10009:
```

Even automatic closing:

* is not considered successful by default
* requires result verification (code 10009 = successful execution)
* may be rejected by the server

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`on_position_profit()`**:

* supplies profit update stream
* does not make decisions
* does not close positions

**`order_close()`**:

* executes trading action
* attempts to close position
* returns result

**User code**:

* sets target profit
* makes closing decision
* connects event and action

---

## Architectural Pattern

This example illustrates a fundamental pattern:

> **stream → condition → action**

Or in trading strategy terms:

> **observation → trigger → execution**

---

## Summary

The `on_position_profit()` method is designed for **reactive position state control**.

It allows building custom management strategies:

* take-profit
* trailing logic
* risk-based exits

while remaining strictly a low-level data source, not a decision-making mechanism.
