## on_trade — How it works

---

## 📌 Overview

`on_trade()` is a low-level streaming method for subscribing to **all account trading events** in real-time.

It provides a unified stream of changes related to:

* positions
* orders
* deals

The method does not separate events into different streams and does not perform business logic. It only **records the fact of trading state changes**, leaving interpretation and reaction entirely on the user side.

In this example, `on_trade()` is used as a **universal trading logger**, tracking and displaying all types of trading events.

---

## Method Signature

```python
async def on_trade(
    cancellation_event: Optional[asyncio.Event] = None,
):
    -> AsyncIterator[OnTradeData]
```

Key features:

* asynchronous streaming method (`async for`)
* returns stream of account trading events
* combines positions, orders, and deals
* has no built-in timeout
* can be stopped via `cancellation_event` or external interruption

---

## 🧩 Code Example — Trade event logger

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def log_trade_events():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    event_count = 0

    try:
        async for trade_data in account.on_trade():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            event = trade_data.event_data

            for pos in event.new_positions:
                event_count += 1
                print(f"[{timestamp}] NEW_POSITION | Index: {pos.index}")

            for pos in event.disappeared_positions:
                event_count += 1
                print(f"[{timestamp}] CLOSED_POSITION | Index: {pos.index}")

            for pos in event.updated_positions:
                event_count += 1
                print(f"[{timestamp}] UPDATED_POSITION | Index: {pos.index}")

            for order in event.new_orders:
                event_count += 1
                print(f"[{timestamp}] NEW_ORDER | Index: {order.index}")

            for order in event.state_changed_orders:
                event_count += 1
                print(f"[{timestamp}] ORDER_STATE_CHANGE | Index: {order.index}")

            for deal in event.new_history_deals:
                event_count += 1
                print(f"[{timestamp}] NEW_DEAL | Index: {deal.index}")

            if event_count % 10 == 0:
                print(f"\n--- Total events logged: {event_count} ---\n")

    except KeyboardInterrupt:
        print(f"\nStopping logger. Total events: {event_count}")

    finally:
        await account.channel.close()

asyncio.run(log_trade_events())
```

---

## 🟢 Detailed Explanation

---

### 1️⃣ Subscribing to Trading Events

```python
async for trade_data in account.on_trade():
```

A subscription to the trading changes stream is created:

* server sends updates on any trading event
* stream operates continuously
* each iteration is a **batch of changes**, not a single event

---

### 2️⃣ Event Container `event_data`

```python
event = trade_data.event_data
```

`event_data` contains lists of changes grouped by types:

* `new_positions`
* `disappeared_positions`
* `updated_positions`
* `new_orders`
* `state_changed_orders`
* `new_history_deals`

Each list can be empty or contain multiple elements.

---

### 3️⃣ Processing Events as Lists

```python
for pos in event.new_positions:
```

A single trading update can include **multiple events of the same type**.

Therefore:

* processing is always done through loops
* cannot assume one object per update
* code is resilient to high trading activity

---

### 4️⃣ Logging Event Facts

For each detected event:

* local time is recorded
* event counter is incremented
* event type and its index are displayed

Log example:

```
[2026-02-05 12:01:22] NEW_POSITION | Index: 123456
```

---

### 5️⃣ Event Counter

```python
event_count += 1
```

Counter is used for:

* monitoring stream activity
* debugging statistics
* periodic logger state output

```python
if event_count % 10 == 0:
```

Every 10 events, an intermediate summary is displayed.

---

### 6️⃣ Stream Termination

In this example, the stream is considered infinite:

* termination is done manually (`Ctrl+C`)
* `KeyboardInterrupt` is explicitly caught
* connection is closed properly

---

## Final Responsibility Model

**`on_trade()`**:

* delivers trading events
* combines positions, orders, and deals
* does not interpret changes
* does not make trading decisions

**User code**:

* chooses which events to process
* implements reaction or logging logic
* manages stream lifetime

---

## Summary

This example illustrates the unified trading event streaming pattern:

**subscribe → receive trade events → classify by type → process each category**

Key points:

* `on_trade()` delivers unified stream of all trading activity (positions, orders, deals)
* each update may contain multiple event types simultaneously
* user code is responsible for:
  * iterating through event lists (`new_positions`, `disappeared_positions`, etc.)
  * classifying event types
  * implementing business logic per event type
  * logging or reacting to changes

The API acts as a comprehensive trading event source, combining positions, orders, and deals into a single stream, while all event handling and business logic remain entirely on the user side.
