## symbol_info_double — How it works

---

## 📌 Overview

This example demonstrates how to retrieve a **numeric property of a trading symbol** using the low-level asynchronous method `symbol_info_double()`.

The method is used to read symbol parameters that are represented in MetaTrader as floating-point numbers: swaps, spreads, price step, minimum distances, and other trading characteristics.

Each method call requests **one specific numeric property of one symbol**.

---

## Method Signature

```python
async def symbol_info_double(
    symbol: str,
    property: SymbolInfoDoubleProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and must be called with `await`
* `symbol` — trading symbol name (e.g., `"GBPUSD"`)
* `property` specifies **which numeric property of the symbol** to retrieve
* `deadline` and `cancellation_event` control execution time
* The method returns an object with the numeric property value

---

## 🧩 Code Example — Getting Swap Rates for a Symbol

```python
async def get_swap_info(account: MT5Account, symbol: str):
    # Get long swap
    long_swap_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SWAP_LONG
    )

    # Get short swap
    short_swap_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SWAP_SHORT
    )

    print(f"Swap for {symbol}:")
    print(f"  Long: {long_swap_data.value:.2f}")
    print(f"  Short: {short_swap_data.value:.2f}")

    return {
        "long": long_swap_data.value,
        "short": short_swap_data.value
    }
```

In this example, `symbol_info_double()` is used to retrieve swap values for long and short positions for one symbol.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Requesting Numeric Symbol Property

```python
long_swap_data = await account.symbol_info_double(
    symbol,
    market_info_pb2.SYMBOL_SWAP_LONG
)
```

At this step, one asynchronous call is executed.

* The symbol name is passed to the method
* The second argument specifies the type of numeric property
* A request to the terminal is executed

The result is a response object containing the property value.

---

### 2️⃣ Repeated Call for Another Property

```python
short_swap_data = await account.symbol_info_double(
    symbol,
    market_info_pb2.SYMBOL_SWAP_SHORT
)
```

The method is called again, but with a different `property` value.

Important:

* Each call requests **exactly one property**
* Values are not cached
* Each parameter is retrieved with a separate request

---

### 3️⃣ Extracting Numeric Value

```python
long_swap_data.value
short_swap_data.value
```

The returned object contains a `value` field.

* This field holds the numeric property value
* The value type is `float`

After extracting `.value`, you can work with the number as a regular Python value.

---

### 4️⃣ Using Retrieved Data

```python
return {
    "long": long_swap_data.value,
    "short": short_swap_data.value
}
```

The retrieved values are combined into a dictionary.

This is done solely for convenience of the calling code — the `symbol_info_double()` method:

* Does not combine properties
* Does not interpret values
* Does not know how they will be used

---

## Summary

In this example, `symbol_info_double()` is used as a source of numeric trading symbol parameters.

The method is called as many times as properties need to be retrieved, and all processing and data combination logic is performed on the user side.
