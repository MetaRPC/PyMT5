## on_positions_and_pending_orders_tickets — How it works

---

## 📌 Overview

This example demonstrates a **complete usage scenario** of the streaming low-level method `on_positions_and_pending_orders_tickets()` for tracking changes in account trading state and transforming these changes into user-defined events.

Key idea of the example:

> The server **does not report what exactly happened** — it only returns the current state.
> All interpretation is performed on the client side.

---

## Method Signature

```python
async def on_positions_and_pending_orders_tickets(
    interval_ms: int,
    cancellation_event: Optional[asyncio.Event] = None,
):
    -> AsyncIterator[OnPositionsAndPendingOrdersTicketsData]
```

---

## 🧩 Code Example — Ticket change logger to file

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def log_ticket_changes():
    prev_positions = set()
    prev_orders = set()

    with open('ticket_changes.log', 'w') as logfile:
        logfile.write("Timestamp,Event,Ticket\n")

        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000
        ):
            timestamp = datetime.now().isoformat()

            current_positions = set(update.position_tickets)
            current_orders = set(update.pending_order_tickets)

            for ticket in current_positions - prev_positions:
                logfile.write(f"{timestamp},POSITION_OPENED,{ticket}\n")
                logfile.flush()

            for ticket in prev_positions - current_positions:
                logfile.write(f"{timestamp},POSITION_CLOSED,{ticket}\n")
                logfile.flush()

            for ticket in current_orders - prev_orders:
                logfile.write(f"{timestamp},ORDER_CREATED,{ticket}\n")
                logfile.flush()

            for ticket in prev_orders - current_orders:
                logfile.write(f"{timestamp},ORDER_REMOVED,{ticket}\n")
                logfile.flush()

            prev_positions = current_positions
            prev_orders = current_orders

asyncio.run(log_ticket_changes())
```

---

## 🟢 Detailed Step-by-Step Explanation

---

### 1️⃣ User state initialization

```python
prev_positions = set()
prev_orders = set()
```

User code creates **local state** upfront, which will be used for comparison.

The API method **does not store history** and has no knowledge of previous calls.

---

### 2️⃣ Opening log file

```python
with open('ticket_changes.log', 'w') as logfile:
```

This is purely user responsibility:

* file format
* storage method
* write policy

The API does not participate in this.

---

### 3️⃣ Subscribing to streaming updates

```python
async for update in account.on_positions_and_pending_orders_tickets(...):
```

At this stage:

* a long-lived stream is created
* server periodically sends **full snapshot**
* loop continues until cancellation

---

### 4️⃣ Receiving current snapshot

```python
current_positions = set(update.position_tickets)
current_orders = set(update.pending_order_tickets)
```

Each update contains:

* full list of position ticket IDs
* full list of pending order ticket IDs

This is **state**, not an event.

---

### 5️⃣ User diff logic

```python
current_positions - prev_positions
prev_positions - current_positions
```

This is where key user work happens:

* determine what appeared
* determine what disappeared

The API **intentionally** does not do this for the user.

---

### 6️⃣ Interpreting diff as events

```python
POSITION_OPENED
POSITION_CLOSED
ORDER_CREATED
ORDER_REMOVED
```

At this stage the user:

* gives meaning to changes
* introduces custom event types
* decides what is considered important

---

### 7️⃣ Recording result

```python
logfile.write(...)
logfile.flush()
```

Processing result:

* is saved
* can be passed further
* can be used for auditing

---

### 8️⃣ Updating base state

```python
prev_positions = current_positions
prev_orders = current_orders
```

This closes the processing loop and prepares the code for the next snapshot.

---

## Role of low-level method

**`on_positions_and_pending_orders_tickets()`**:

* returns current state of ticket IDs
* does not analyze changes
* does not classify events

**User logic**:

* stores state
* calculates diff
* interprets events
* decides what to do with them

---

## Summary

This method is the foundation for building **state-based logic**:

* loggers
* audit
* alerts
* external systems synchronization

It deliberately remains low-level and delegates all semantics to the user.
