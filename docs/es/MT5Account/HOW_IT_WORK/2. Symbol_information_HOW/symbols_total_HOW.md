## symbols_total — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `symbols_total()` to get **the number of trading symbols** and calculate Market Watch usage based on it.

The `symbols_total()` method returns only a numeric value — the total number of symbols. All analytics and interpretation are performed on the user code side.

---

## Method Signature

```python
async def symbols_total(
    selected_only: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and called with `await`
* `selected_only=True` — count only symbols from Market Watch
* `selected_only=False` — count all available symbols on the server
* The method returns an object with numeric value `total`

---

## 🧩 Code Example — Market Watch Usage Calculation

```python
async def calculate_mw_usage(account: MT5Account) -> dict:
    all_data = await account.symbols_total(selected_only=False)
    mw_data = await account.symbols_total(selected_only=True)

    total = all_data.total
    used = mw_data.total
    usage_pct = (used / total * 100) if total > 0 else 0

    result = {
        "total_available": total,
        "in_market_watch": used,
        "usage_percent": usage_pct
    }

    print(f"Market Watch Usage:")
    print(f"  Using {used} of {total} symbols ({usage_pct:.1f}%)")

    return result
```

In this example, the method is called twice with different parameters to compare the total number of symbols and the number of symbols added to Market Watch.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Getting Total Symbol Count

```python
all_data = await account.symbols_total(selected_only=False)
```

At this step:

* one asynchronous call is performed
* the server returns the count of all symbols available on the platform
* the value is available in the `all_data.total` field

---

### 2️⃣ Getting Market Watch Symbol Count

```python
mw_data = await account.symbols_total(selected_only=True)
```

Here the method is used again, but for a different data slice:

* only symbols added to Market Watch are counted
* the result is also returned in the `mw_data.total` field

---

### 3️⃣ Extracting Numeric Values

```python
total = all_data.total
used = mw_data.total
```

At this stage:

* the API is no longer used
* regular work with numbers in Python follows

---

### 4️⃣ Calculating Usage Percentage

```python
usage_pct = (used / total * 100) if total > 0 else 0
```

User code:

* protects against division by zero
* calculates the percentage of symbols added to Market Watch

---

### 5️⃣ Forming the Result

```python
result = {
    "total_available": total,
    "in_market_watch": used,
    "usage_percent": usage_pct
}
```

The `symbols_total()` method returns only a number, while the result structure is entirely formed on the user side.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`symbols_total()`**:

* returns the symbol count
* does not compare values
* does not calculate percentages
* does not draw conclusions

**`calculate_mw_usage()`**:

* calls the method with different parameters
* compares results
* performs calculations
* forms statistics

---

## Summary

This example illustrates a simple but important pattern of working with low-level API:

> **get numeric values → perform calculation → interpret result**

The `symbols_total()` method provides basic data, while all analytics and conclusions remain on the user code side.
