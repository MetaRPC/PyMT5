## symbol_info_margin_rate — How it works

---

## 📌 Overview

This example demonstrates how to retrieve **margin requirements for a trading symbol** depending on trade direction using the low-level asynchronous method `symbol_info_margin_rate()`.

Unlike symbol parameters that don't depend on direction (digits, spread, swap, etc.), margin requirements can **differ for BUY and SELL**.

The method is used when you need to understand:

* How much margin is required to open a position
* Whether conditions are the same for buying and selling
* How account type or instrument affects margin calculations

---

## Method Signature

```python
async def symbol_info_margin_rate(
    symbol: str,
    order_type: ENUM_ORDER_TYPE,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and must be called with `await`
* `symbol` — trading symbol name (e.g., `"XAUUSD"`)
* `order_type` specifies trade direction (`BUY`, `SELL`, etc.)
* `deadline` and `cancellation_event` control execution time
* The method returns an object with margin coefficients

---

## 🧩 Code Example — Comparing Margin for BUY and SELL

```python
# Get BUY margin rates
buy_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

# Get SELL margin rates
sell_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_SELL
)

print(f"XAUUSD Margin Rates:")
print(f"  BUY  - Initial: {buy_rates.initial_margin_rate}, Maintenance: {buy_rates.maintenance_margin_rate}")
print(f"  SELL - Initial: {sell_rates.initial_margin_rate}, Maintenance: {sell_rates.maintenance_margin_rate}")

if buy_rates.initial_margin_rate == sell_rates.initial_margin_rate:
    print("  Same margin rates for both directions (hedge account)")
else:
    print("  Different margin rates (check account type)")
```

In this example, the method is called twice for the same symbol but with different trade directions.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Requesting Margin Parameters for BUY

```python
buy_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)
```

At this step:

* One asynchronous call is executed
* Symbol name and BUY order type are passed to the terminal
* An object with margin parameters for buying is returned

The returned object contains coefficients that the terminal uses when calculating margin for a BUY position.

---

### 2️⃣ Requesting Margin Parameters for SELL

```python
sell_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_SELL
)
```

The method is called again:

* Same symbol
* Same method
* Different trade direction

The result is a second object with margin parameters — now for a SELL position.

Each call:

* Is independent
* Is executed with a separate request
* Returns data only for the specified direction

---

### 3️⃣ Working with Retrieved Data

```python
buy_rates.initial_margin_rate
buy_rates.maintenance_margin_rate
```

Both objects (`buy_rates` and `sell_rates`) contain the same fields:

* `initial_margin_rate` — initial margin coefficient
* `maintenance_margin_rate` — maintenance margin coefficient

These are numeric values that can be:

* Compared
* Logged
* Used in your own calculations

---

### 4️⃣ Comparing Margin Requirements

```python
if buy_rates.initial_margin_rate == sell_rates.initial_margin_rate:
```

Application logic begins.

In the example, the **initial margin** for BUY and SELL is compared:

* If values are equal — margin conditions are symmetric
* If they differ — requirements depend on trade direction

This comparison is not part of the API — it's a user code decision.

---

### 5️⃣ Interpreting Results

```python
print("Same margin rates for both directions (hedge account)")
```

When values match, you can usually conclude that:

* The account operates in hedge mode
* Margin requirements are the same for BUY and SELL

---

```python
print("Different margin rates (check account type)")
```

If values differ:

* Margin depends on position direction
* This may be related to account type or instrument

The code makes no assumptions, only records the fact of difference.

---

## Summary

In this example, `symbol_info_margin_rate()` is used to retrieve and compare margin requirements for one symbol across different trade directions.

The method returns margin coefficients for the specified symbol and order type, and all analysis and interpretation logic remains on the calling code side.
