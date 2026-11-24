## symbol_info_integer — How it works

---

## 📌 Overview

This example demonstrates how to retrieve **integer properties of a trading symbol** using the low-level asynchronous method `symbol_info_integer()`.

The method is used to read symbol parameters that are represented in MetaTrader as integers: number of decimal places, spread, trading modes, and other numeric characteristics.

Each method call requests **one specific integer property of one symbol**.

---

## Method Signature

```python
async def symbol_info_integer(
    symbol: str,
    property: SymbolInfoIntegerProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and must be called with `await`
* `symbol` — trading symbol name (e.g., `"EURUSD"`)
* `property` specifies **which integer property of the symbol** to retrieve
* `deadline` and `cancellation_event` control execution time
* The method returns an object with the integer property value

---

## 🧩 Code Example — Getting Digits and Spread

```python
# Get digits (decimal places)
result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DIGITS
)
print(f"Digits: {result.value}")

# Get spread in points
spread_result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_SPREAD
)
print(f"Spread: {spread_result.value} points")
```

In this example, `symbol_info_integer()` is used to retrieve parameters that directly affect price calculations and symbol trading conditions.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Requesting Number of Decimal Places

```python
result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DIGITS
)
```

At this step, one asynchronous call is executed.

* The symbol name is passed to the method
* The second argument specifies the integer property type (`SYMBOL_DIGITS`)
* The terminal returns a response object with the result

The numeric value itself is located in the `result.value` field.

---

### 2️⃣ Using Retrieved Value

```python
print(f"Digits: {result.value}")
```

* `result.value` — number of decimal places
* Value type — `int`
* The value can be used directly in price calculations

No additional API calls occur at this stage.

---

### 3️⃣ Requesting Spread

```python
spread_result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_SPREAD
)
```

The method is called again for the same symbol, but with a different property.

Important:

* Each call retrieves **exactly one property**
* Values are not cached automatically
* Each property is requested with a separate call

---

### 4️⃣ Working with Spread Value

```python
print(f"Spread: {spread_result.value} points")
```

* `spread_result.value` — spread in points
* The value is an integer
* Used directly, without conversions

---

## Summary

In this example, `symbol_info_integer()` is used as a source of integer trading symbol parameters.

The method is called separately for each required property, and all logic for using retrieved values remains on the calling code side.
