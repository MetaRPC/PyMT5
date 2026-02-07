## order_modify — How it works

---

## 📌 Overview

This example shows how to use the low-level method `order_modify()` to **modify parameters of an already existing order**, specifically — **changing the entry price of a pending order**.

Important to understand:

* the order **already exists**
* it has a `ticket`
* the method **does not create a new order**
* the method **does not open a position**

It is used when you need to adapt a previously placed order to the current market situation.

---

## Method Signature

```python
async def order_modify(
    request: OrderModifyRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> OrderModifyData
```

Key points:

* the method is asynchronous
* executes a real trading action
* works with an existing order by `ticket`
* modifies **only explicitly specified parameters**

---

## 🧩 Code Example — Modify pending order price

```python
# Get current instrument price
tick_data = await account.symbol_info_tick("EURUSD")
current_bid = tick_data.bid

# Calculate new price (15 pips below market)
pip_size = 0.0001
new_price = current_bid - (15 * pip_size)

# Form order modification request
request = OrderModifyRequest(
    ticket=789012,      # ticket of existing pending order
    stop_loss=0,        # SL is not changed
    take_profit=0,      # TP is not changed
    price=new_price     # new entry price
)

result = await account.order_modify(request)
```

---

## 🟢 Detailed Explanation

---

### 1️⃣ Getting Current Market Price

```python
tick_data = await account.symbol_info_tick("EURUSD")
current_bid = tick_data.bid
```

At this step:

* the last tick for the symbol is requested
* current Bid price is used
* the API returns only market data, without trading logic

The price is used as the basis for calculating the new order price.

---

### 2️⃣ Calculating New Price for Pending Order

```python
new_price = current_bid - (15 * pip_size)
```

This is user trading logic:

* the order is shifted below the current price
* typical scenario for BUY LIMIT
* the shift amount (15 pips) is set by the strategy

The API does not participate in this step.

---

### 3️⃣ Forming OrderModifyRequest

```python
request = OrderModifyRequest(
    ticket=789012,
    stop_loss=0,
    take_profit=0,
    price=new_price
)
```

Key points:

* `ticket` — identifier of the order being modified
* **only the `price` parameter is being changed**
* SL and TP parameters are explicitly indicated as unchanged

The `order_modify()` method does not make assumptions and does not change parameters that were not passed.

---

### 4️⃣ Sending Modification Command

```python
result = await account.order_modify(request)
```

At this stage:

* a trading command is sent to the server
* the server checks the validity of the new price
* broker restrictions and trading rules are taken into account

The order is either modified or the operation is rejected.

---

### 5️⃣ Operation Result

The response contains:

* operation execution code
* result description
* updated order information

The result **must be checked** by user code.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`order_modify()`**:

* accepts order modification request
* attempts to apply changes on the server
* returns the technical result
* does not calculate trading logic

**User code**:

* decides when and why to change the order
* calculates the new price
* selects parameters to modify
* analyzes the operation result

---

## Summary

The `order_modify()` method is used for **precise modification of existing order parameters**.

Correct usage pattern:

> **get market data → calculate new parameters → send modification → check result**

It is a key tool for dynamic management of pending orders in automated trading strategies.
