## symbol_info_tick — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `symbol_info_tick()` to retrieve the current tick for a symbol and perform **custom validation of market data before trading**.

A tick is the latest available market information (Bid, Ask, time, etc.). By itself, it does not guarantee that the data is suitable for trading, so the example immediately demonstrates how this data is validated on the user side.

---

## Method Signature

```python
async def symbol_info_tick(
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and called with `await`
* `symbol` — trading symbol name
* The method returns an object with the last known tick
* The method does not perform data correctness checks

---

## 🧩 Code Example — Tick validation before trading

```python
async def validate_tick(account, symbol: str) -> bool:
    try:
        tick = await account.symbol_info_tick(symbol)

        if tick.bid <= 0 or tick.ask <= 0:
            print(f"Invalid prices: bid={tick.bid}, ask={tick.ask}")
            return False

        spread = tick.ask - tick.bid
        if spread <= 0:
            print(f"Invalid spread: {spread}")
            return False

        if tick.time > 0:
            current_time = datetime.now(timezone.utc).timestamp()
            age = current_time - tick.time

            if age > 10:
                print(f"Tick too old: {age} seconds")
                return False

        print("Tick validation passed")
        return True

    except Exception as e:
        print(f"Validation error: {e}")
        return False
```

This example demonstrates a typical safety check that is performed **before sending trading operations**.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Retrieving Last Tick

```python
tick = await account.symbol_info_tick(symbol)
```

At this step:

* one asynchronous call is performed
* the terminal returns the last known tick for the symbol
* the `tick` object contains prices and time

The method returns data "as is", without interpretation.

---

### 2️⃣ Checking Bid and Ask Prices

```python
if tick.bid <= 0 or tick.ask <= 0:
```

The presence of valid prices is checked:

* values `<= 0` indicate absence of valid quotes
* such data cannot be used for trading

---

### 3️⃣ Checking Spread

```python
spread = tick.ask - tick.bid
if spread <= 0:
```

Here, the logical correctness of prices is checked:

* Ask must be greater than Bid
* spread must be positive

---

### 4️⃣ Checking Tick Freshness

```python
if tick.time > 0:
    current_time = datetime.now(timezone.utc).timestamp()
    age = current_time - tick.time
```

Tick time is compared with current time:

* `tick.time` — Unix timestamp
* tick age is calculated in seconds

---

```python
if age > 10:
```

The example uses a custom rule:

* a tick older than 10 seconds is considered unsuitable for trading

This is not an API rule, but a decision of the application code.

---

### 5️⃣ Successful Validation

```python
print("Tick validation passed")
return True
```

If all checks pass, the tick is considered valid.

---

### 6️⃣ Error Handling

```python
except Exception:
    return False
```

Any error when retrieving or checking the tick leads to trading prohibition.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`symbol_info_tick()`**:

* returns the last tick
* does not check its correctness
* does not assess data freshness

**`validate_tick()`**:

* checks prices
* checks spread
* checks tick age
* makes the decision whether trading is allowed

---

## Summary

This example illustrates the basic pattern of working with low-level API:

> **low-level data → custom validation → trading decision**

The `symbol_info_tick()` method provides raw market data, while all logic for their interpretation and validation remains on the user side.
