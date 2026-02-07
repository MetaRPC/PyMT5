## opened_orders_tickets — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `opened_orders_tickets()` to track **changes in the trading account state by identifiers (ticket IDs)**.

Unlike `opened_orders()`, which returns detailed information, this method is designed for **lightweight change monitoring**:

* appearance of new orders or positions
* closing of existing ones

It is especially useful for background monitoring and reactive logic.

---

## Method Signature

```python
async def opened_orders_tickets(
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* the method is asynchronous and called with `await`
* does not accept filtering parameters
* returns only identifiers (tickets)
* does not contain detailed information about orders or positions

---

## 🧩 Code Example — Monitoring Changes by Tickets

```python
async def monitor_tickets(account: MT5Account, interval: float = 5.0):
    previous_tickets = set()

    while True:
        try:
            data = await account.opened_orders_tickets()

            current_tickets = set(
                data.opened_orders_tickets + data.opened_position_tickets
            )

            if previous_tickets:
                new = current_tickets - previous_tickets
                closed = previous_tickets - current_tickets

                for ticket in new:
                    print(f"[+] New ticket: #{ticket}")
                for ticket in closed:
                    print(f"[-] Closed ticket: #{ticket}")

            previous_tickets = current_tickets

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)
```

This example implements a simple observation loop for tracking trading state changes.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Storing Previous State

```python
previous_tickets = set()
```

* `set` is used for fast comparison
* it stores tickets from the previous iteration

---

### 2️⃣ Getting the Current Ticket List

```python
data = await account.opened_orders_tickets()
```

At this step:

* one asynchronous call is performed
* the server returns:

  * `opened_orders_tickets`
  * `opened_position_tickets`

These are two independent lists of numeric identifiers.

---

### 3️⃣ Merging Orders and Positions

```python
current_tickets = set(
    data.opened_orders_tickets + data.opened_position_tickets
)
```

Here:

* lists are merged
* converted into a `set`
* the current state of account tickets is formed

---

### 4️⃣ Comparing States

```python
new = current_tickets - previous_tickets
closed = previous_tickets - current_tickets
```

Standard set operation logic is used:

* `new` — tickets that appeared since the last poll
* `closed` — tickets that have disappeared

---

### 5️⃣ Reacting to Changes

```python
for ticket in new:
    print(f"[+] New ticket: #{ticket}")
```

User code:

* decides on its own how to react
* can log, update UI, trigger logic

The API method does not interpret changes.

---

### 6️⃣ Updating State

```python
previous_tickets = current_tickets
```

The current state is saved for the next loop iteration.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`opened_orders_tickets()`**:

* returns only order and position identifiers
* does not contain prices, volumes, or profit
* does not track changes over time

**`monitor_tickets()`**:

* implements the polling loop
* compares states
* determines what appeared and what disappeared
* makes decisions

---

## Summary

This example demonstrates the pattern of **lightweight state monitoring**:

> **get identifiers → compare states → react to changes**

The `opened_orders_tickets()` method provides the minimum set of data for tracking changes, while all monitoring and interpretation logic is implemented on the user code side.
