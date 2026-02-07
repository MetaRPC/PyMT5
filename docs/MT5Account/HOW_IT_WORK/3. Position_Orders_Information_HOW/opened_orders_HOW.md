## opened_orders — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `opened_orders()` to get **a current snapshot of the trading account state**:

* list of pending orders
* list of open positions

The method is used for account monitoring, displaying trading state, and making subsequent decisions.

---

## Method Signature

```python
async def opened_orders(
    sort_mode: BMT5_ENUM_OPENED_ORDER_SORT_TYPE = BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and called with `await`
* `sort_mode` affects **only the order of pending orders**
* positions are returned without sorting
* The method returns one aggregated state object

---

## 🧩 Code Example — Getting Opened Orders and Positions

```python
data = await account.opened_orders(
    sort_mode=account_helper_pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
    deadline=deadline
)

print(f"Pending orders: {len(data.opened_orders)}")
print(f"Open positions: {len(data.position_infos)}")

# Show positions
for pos in data.position_infos:
    print(
        f"Position #{pos.ticket} {pos.symbol}: "
        f"{pos.volume} lots @ {pos.price_open}, P/L: ${pos.profit:.2f}"
    )

# Show orders
for order in data.opened_orders:
    print(
        f"Order #{order.ticket} {order.symbol}: "
        f"{order.volume_initial} lots @ {order.price_open}"
    )
```

This example demonstrates working with the result without additional filtering or transformations.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Calling the opened_orders Method

```python
data = await account.opened_orders(
    sort_mode=account_helper_pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
    deadline=deadline
)
```

At this step:

* one asynchronous request is performed
* the server forms the current trading state of the account
* data is returned as one object

This object represents **a snapshot of the state at a specific moment in time**.

---

### 2️⃣ Result Structure

The response contains two independent lists:

```python
data.opened_orders     # pending orders
data.position_infos    # open positions
```

These are fundamentally different entities:

* positions — already opened trades
* orders — instructions waiting for execution

They are returned together because they reflect the same account state.

---

### 3️⃣ Counting Orders and Positions

```python
len(data.opened_orders)
len(data.position_infos)
```

Here:

* lists are already formed by the server
* the client simply counts elements

The method does not filter or hide data.

---

### 4️⃣ Iterating Through Open Positions

```python
for pos in data.position_infos:
```

Each element in the positions list contains a set of fields, such as:

* `ticket` — position identifier
* `symbol` — trading instrument
* `volume` — position volume
* `price_open` — opening price
* `profit` — current profit or loss

User code:

* selects needed fields
* formats output
* decides what to consider important

---

### 5️⃣ Iterating Through Pending Orders

```python
for order in data.opened_orders:
```

Pending orders:

* do not have current profit
* use `volume_initial` instead of `volume`
* exist separately from positions

This emphasizes why the method returns two different lists.

---

### 6️⃣ The Role of sort_mode Parameter

```python
sort_mode=BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
```

Important:

* sorting applies **only to pending orders**
* positions are not sorted
* sorting is performed on the server side

The client receives an already ordered list of orders.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`opened_orders()`**:

* returns the current state of orders and positions
* aggregates data on the server side
* does not filter or analyze them
* does not make trading decisions

**User code**:

* decides which fields to use
* how to display data
* what actions to perform next

---

## Summary

This example illustrates the basic pattern of working with aggregating low-level methods:

> **get state snapshot → parse data → make decision**

The `opened_orders()` method provides the current trading state, while all analysis logic and subsequent actions remain on the user code side.
