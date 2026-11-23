## positions_total — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `positions_total()` to get **the current number of open positions** on the account and compare it with a specified target value.

This scenario is typical for risk management and trading state control:

* limiting the maximum number of positions
* maintaining a specified number of trades
* controlling account overload

The method is used exclusively as a source of actual state.

---

## Method Signature

```python
async def positions_total(
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* the method is asynchronous and called with `await`
* does not accept filters or parameters
* returns **only the number of open positions**
* does not perform checks or comparisons

---

## 🧩 Code Example — Comparing Position Count with Target Value

```python
async def compare_with_target(
    account: MT5Account,
    target_positions: int
) -> dict:
    data = await account.positions_total()
    current = data.total_positions

    difference = current - target_positions

    result = {
        "current": current,
        "target": target_positions,
        "difference": difference,
        "status": "exact" if difference == 0 else "above" if difference > 0 else "below"
    }

    if difference == 0:
        print(f"[OK] Exactly at target: {current} positions")
    elif difference > 0:
        print(f"[INFO] {abs(difference)} above target ({current}/{target_positions})")
    else:
        print(f"[INFO] {abs(difference)} below target ({current}/{target_positions})")

    return result
```

This example demonstrates an applied check of the trading state against a specified limit.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Getting the Current Position Count

```python
data = await account.positions_total()
current = data.total_positions
```

At this step:

* one asynchronous request is performed
* the server returns the number of **open** positions
* no additional information is transmitted

The method returns the current state, not history.

---

### 2️⃣ Comparing with Target Value

```python
difference = current - target_positions
```

User logic begins here:

* deviation from the target value is calculated
* positive value means exceeding the limit
* negative value means insufficient positions

---

### 3️⃣ Forming Status

```python
status = "exact" if difference == 0 else "above" if difference > 0 else "below"
```

Status is fully user-defined:

* `exact` — current count matches the target
* `above` — more positions than needed
* `below` — fewer positions than required

The API does not interpret the result.

---

### 4️⃣ Reacting to Result

```python
if difference == 0:
    ...
elif difference > 0:
    ...
else:
    ...
```

At this step:

* a decision is made
* logging is performed
* if necessary, trading logic can be here (closing / opening positions)

---

### 5️⃣ Returning Aggregated Result

```python
return result
```

The function returns a structure with the already interpreted state.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`positions_total()`**:

* returns only the number of open positions
* does not know what "target" or "limit" means
* does not make decisions

**User code**:

* sets the target value
* compares the current state with the target
* interprets the result
* takes further actions

---

## Summary

This example illustrates a simple but important state control pattern:

> **get current value → compare with target → make decision**

The `positions_total()` method provides the actual account state, while all control and management logic is implemented on the user side.
