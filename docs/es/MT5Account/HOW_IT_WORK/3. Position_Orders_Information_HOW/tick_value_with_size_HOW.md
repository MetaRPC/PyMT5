## tick_value_with_size — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `tick_value_with_size()` to get **the tick value and tick size of an instrument** and use this data to **calculate the acceptable Stop Loss distance** for a given maximum loss.

The method is used as a source of instrument market parameters, while all risk calculations are performed on the user code side.

---

## Method Signature

```python
async def tick_value_with_size(
    symbols: list[str],
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* the method is asynchronous and called with `await`
* accepts a list of symbols (even if only one is needed)
* returns tick value and tick size parameters
* does not perform any risk or SL calculations

---

## 🧩 Code Example — Calculating Stop Loss Distance

```python
async def calculate_sl_distance(
    account: MT5Account,
    symbol: str,
    lots: float,
    max_loss: float
) -> float:
    """Calculate maximum SL distance for given max loss"""

    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Symbol {symbol} not found")

    info = data.symbol_tick_size_infos[0]

    # Calculate pips allowed
    profit_per_pip = info.TradeTickValue * 10 * lots
    max_pips = max_loss / profit_per_pip if profit_per_pip > 0 else 0

    print(f"\nStop Loss Calculation for {symbol}:")
    print(f"  Volume: {lots} lots")
    print(f"  Max Loss: ${max_loss:.2f}")
    print(f"  Profit per pip: ${profit_per_pip:.2f}")
    print(f"  Max SL distance: {max_pips:.1f} pips")

    return max_pips
```

This example demonstrates a complete user-level Stop Loss parameter calculation based on market data.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Getting Instrument Tick Parameters

```python
data = await account.tick_value_with_size(symbols=[symbol])
```

At this step:

* one asynchronous request is performed
* the server returns instrument parameters
* data arrives as a `symbol_tick_size_infos` list

The method does not know how these values will be used.

---

### 2️⃣ Checking Symbol Data Availability

```python
if not data.symbol_tick_size_infos:
    raise ValueError(f"Symbol {symbol} not found")
```

This is user-level protection:

* checks if the server returned data
* stops calculation if data is missing

---

### 3️⃣ Extracting Symbol Data

```python
info = data.symbol_tick_size_infos[0]
```

Each element contains:

* `TradeTickValue` — value of one tick
* tick size and contract parameters

The user chooses which fields to use.

---

### 4️⃣ Calculating Pip Value

```python
profit_per_pip = info.TradeTickValue * 10 * lots
```

Business logic begins here:

* tick value is scaled
* position volume in lots is accounted for
* an assumption about pip size is used

The API does not perform this calculation.

---

### 5️⃣ Calculating Acceptable Stop Loss Distance

```python
max_pips = max_loss / profit_per_pip if profit_per_pip > 0 else 0
```

At this step:

* maximum acceptable loss is converted to pips
* protection against division by zero is added

This is entirely a user-level decision.

---

### 6️⃣ Output and Result Return

```python
return max_pips
```

The function returns an already interpreted value, ready for use in trading decisions.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`tick_value_with_size()`**:

* returns tick value and size parameters
* does not know the position volume
* does not know the acceptable risk
* does not calculate Stop Loss

**User code**:

* sets volume and risk
* performs all calculations
* makes trading decisions

---

## Summary

This example illustrates a basic risk pattern:

> **get market parameters → calculate risk → determine trading levels**

The `tick_value_with_size()` method provides the source data, while all risk management logic is implemented on the user side.
