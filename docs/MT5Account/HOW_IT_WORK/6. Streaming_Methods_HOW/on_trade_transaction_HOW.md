## on_trade_transaction — How it works

---

## 📌 Overview

`on_trade_transaction()` is a low-level streaming method for receiving **atomic trading transactions** in real-time.

Each transaction reflects **one specific trading action or state transition**, for example:

* order appearance
* order state change
* execution
* closing

Unlike aggregated trading streams, this method is designed for **auditing, debugging, and restoring complete event history**.

In this example, `on_trade_transaction()` is used to **track order lifecycle**, recording all their states by `order_ticket`.

---

## Method Signature

```python
async def on_trade_transaction(
    cancellation_event: Optional[asyncio.Event] = None,
):
    -> AsyncIterator[OnTradeTransactionData]
```

Key features:

* asynchronous stream (`async for`)
* returns atomic trading transactions
* does not aggregate events
* does not store history
* designed for detailed analysis of trading processes

---

## 🧩 Code Example — Order lifecycle tracker

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def track_order_lifecycle():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    order_states = {}  # order_ticket -> list of states

    try:
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction

            if tx.order_ticket > 0:
                if tx.order_ticket not in order_states:
                    order_states[tx.order_ticket] = []

                order_states[tx.order_ticket].append({
                    'state': tx.order_state,
                    'type': tx.type,
                    'price': tx.price,
                    'volume': tx.volume
                })

                print(f"\n[LIFECYCLE] Order #{tx.order_ticket}:")
                for i, state in enumerate(order_states[tx.order_ticket], 1):
                    print(f"   {i}. State: {state['state']}, "
                          f"Type: {state['type']}, "
                          f"Price: {state['price']}")

    except KeyboardInterrupt:
        print("\nStopping lifecycle tracker...")
        print(f"\nTracked {len(order_states)} orders")

    finally:
        await account.channel.close()

asyncio.run(track_order_lifecycle())
```

---

## 🟢 Detailed Explanation

---

### 1️⃣ Subscribing to Trade Transaction Stream

```python
async for tx_data in account.on_trade_transaction():
```

A subscription to the low-level trading stream is created:

* server sends each trading transaction
* events arrive as they occur
* stream does not aggregate or filter data

Each loop iteration is **one atomic event**.

---

### 2️⃣ Extracting Transaction

```python
tx = tx_data.trade_transaction
```

`trade_transaction` describes a single trading action and contains:

* order identifier (`order_ticket`)
* current order state (`order_state`)
* operation type
* price and volume

This is the minimal unit of trading history.

---

### 3️⃣ Filtering Order Transactions

```python
if tx.order_ticket > 0:
```

Not every trading transaction relates to orders.

Filtering allows to:

* exclude service and irrelevant events
* focus on order lifecycle
* not mix different types of trading entities

---

### 4️⃣ Initializing Order History

```python
if tx.order_ticket not in order_states:
    order_states[tx.order_ticket] = []
```

On first appearance of `order_ticket`:

* a new record is created
* state history collection begins
* subsequent events are added sequentially

---

### 5️⃣ Recording Order State

```python
order_states[tx.order_ticket].append({...})
```

Each transaction is saved as a lifecycle step:

* order state
* operation type
* deal parameters

The `on_trade_transaction()` method does not store history — this is the user's responsibility.

---

### 6️⃣ Reconstructing Lifecycle

```python
for i, state in enumerate(order_states[tx.order_ticket], 1):
```

Order history is displayed completely on each new event:

* transition sequence is visible
* convenient for analyzing order behavior
* useful for diagnostics and auditing

This is a diagnostic technique, not a mandatory pattern.

---

### 7️⃣ Stream Termination

In this example, the stream runs indefinitely:

* termination is manual (`Ctrl+C`)
* `KeyboardInterrupt` is caught
* connection is closed properly

---

## Final Responsibility Model

**`on_trade_transaction()`**:

* delivers atomic trading transactions
* reflects each step of the trading process
* does not aggregate or interpret events
* does not store history

**User code**:

* groups transactions
* reconstructs lifecycles
* performs auditing and analysis
* builds diagnostic tools

---

## Summary

This example illustrates the transaction-level event sourcing pattern:

**subscribe → receive atomic events → group by entity → reconstruct lifecycle**

Key points:

* `on_trade_transaction()` delivers atomic trade events, not aggregated state
* each event represents a single step in the trading process
* user code is responsible for:
  * grouping events (by `order_ticket`)
  * preserving their order
  * reconstructing higher-level meaning (order lifecycle)

The API acts purely as a source of facts, while all interpretation, history building, and analysis remain entirely on the user side.
