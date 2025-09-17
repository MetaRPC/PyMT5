# ✅ On Positions And Pending Orders Tickets

> **Request:** subscribe to periodic **IDs-only snapshots** of **open positions** and **pending orders**. Lightweight stream — perfect for fast diff/poll logic without heavy objects.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `on_positions_and_pending_orders_tickets(...)`
* `MetaRpcMT5/mt5_term_api_subscriptions_pb2.py` — `OnPositionsAndPendingOrdersTickets*` messages
* `MetaRpcMT5/mt5_term_api_subscriptions_pb2_grpc.py` — service stub `SubscriptionServiceStub`

### RPC

* **Service:** `mt5_term_api.SubscriptionService`
* **Method:** `OnPositionsAndPendingOrdersTickets(OnPositionsAndPendingOrdersTicketsRequest) → stream OnPositionsAndPendingOrdersTicketsReply`
* **Low-level client:** `SubscriptionServiceStub.OnPositionsAndPendingOrdersTickets(request, metadata, timeout)` *(server‑streaming iterator)*
* **SDK wrapper:** `MT5Account.on_positions_and_pending_orders_tickets(interval_ms, cancellation_event=None) → async stream of OnPositionsAndPendingOrdersTicketsData`

---

### 🔗 Code Example

```python
# Minimal: stream tickets every 1s and print counts
async for ev in acct.on_positions_and_pending_orders_tickets(1000):
    print(len(ev.opened_position_tickets), len(ev.opened_orders_tickets))
```

```python
# Diff detector: fire only when sets change (cooperative cancel after first change)
import asyncio
cancel = asyncio.Event()
prev_pos, prev_ord = set(), set()
async for ev in acct.on_positions_and_pending_orders_tickets(500, cancellation_event=cancel):
    pos = set(ev.opened_position_tickets)
    ords = set(ev.opened_orders_tickets)
    if pos != prev_pos or ords != prev_ord:
        added_pos = pos - prev_pos; removed_pos = prev_pos - pos
        added_ord = ords - prev_ord; removed_ord = prev_ord - ords
        print("pos +", added_pos, "-", removed_pos, "| ord +", added_ord, "-", removed_ord)
        cancel.set()
    prev_pos, prev_ord = pos, ords
```

---

### Method Signature

```python
async def on_positions_and_pending_orders_tickets(
    self,
    interval_ms: int,
    cancellation_event: asyncio.Event | None = None,
) -> subscription_client.OnPositionsAndPendingOrdersTickets  # async iterable of OnPositionsAndPendingOrdersTicketsData
```

---

## 💬 Just about the main thing

* **What is it.** A timed **IDs-only** stream for open **positions** and **pending orders**.
* **Why.** Super‑cheap heartbeat to drive UI badges and **set‑diff** logic. Fetch full details only when something changed.
* **Be careful.**

  * This is a **snapshot** on a timer, not a delta. Do your own set‑diff client‑side.
  * Choose a sensible `interval_ms` — too small hammers the network/UI.
  * Lists may be empty (no open positions / no pending orders).

---

## 🔽 Input

| Parameter            | Type                 | Description                                         |                                         |
| -------------------- | -------------------- | --------------------------------------------------- | --------------------------------------- |
| `interval_ms`        | `int` (**required**) | Sampling period in **milliseconds** (server timer). |                                         |
| `cancellation_event` | \`asyncio.Event      | None\`                                              | Cooperative stop for the streaming RPC. |

> **Request message:** `OnPositionsAndPendingOrdersTicketsRequest { timer_period_milliseconds: int32 }`

---

## ⬆️ Output

### Stream payload: `OnPositionsAndPendingOrdersTicketsData`

| Field                       | Proto Type                      | Description                                   |
| --------------------------- | ------------------------------- | --------------------------------------------- |
| `type`                      | `MT5_SUB_ENUM_EVENT_GROUP_TYPE` | Event group marker (typically `OrderUpdate`). |
| `opened_position_tickets[]` | `repeated uint64`               | IDs of **open positions**.                    |
| `opened_orders_tickets[]`   | `repeated uint64`               | IDs of **pending orders**.                    |
| `terminal_instance_guid_id` | `string`                        | Source terminal GUID.                         |

> **Wire stream:** `OnPositionsAndPendingOrdersTicketsReply { data: OnPositionsAndPendingOrdersTicketsData, error?: Error }`
> SDK wrapper yields `OnPositionsAndPendingOrdersTicketsData` objects one by one.

---

## Enum: `MT5_SUB_ENUM_EVENT_GROUP_TYPE`

| Number | Value         |
| -----: | ------------- |
|      0 | `OrderProfit` |
|      1 | `OrderUpdate` |

---

### 🎯 Purpose

* Power **fast polling/diff** loops in UI/services.
* Trigger detailed fetch (`OpenedOrders`, `OrderHistory`, etc.) **only on change**.
* Cheap liveness signal for terminals.

### 🧩 Notes & Tips

* For full objects (prices, SL/TP, volumes) use `OpenedOrders` or `OnTrade` stream.
* Combine with `OrderCheck/OrderSend` to react immediately after placement.
* Persist the last seen sets to avoid flicker across UI reloads.

---

## Usage Examples

### 1) Show counts badge in UI

```python
async for ev in acct.on_positions_and_pending_orders_tickets(1000):
    badge_positions = len(ev.opened_position_tickets)
    badge_orders = len(ev.opened_orders_tickets)
    print(badge_positions, badge_orders)
```

### 2) Trigger detail fetch only on change

```python
prev = (set(), set())
async for ev in acct.on_positions_and_pending_orders_tickets(750):
    pos, ords = set(ev.opened_position_tickets), set(ev.opened_orders_tickets)
    if (pos, ords) != prev:
        details = await acct.opened_orders(...)  # fetch heavy only when needed
        prev = (pos, ords)
```

### 3) Stop after 10 seconds (external watchdog)

```python
import asyncio
stop = asyncio.Event()
async def watchdog():
    await asyncio.sleep(10)
    stop.set()
asyncio.create_task(watchdog())

async for ev in acct.on_positions_and_pending_orders_tickets(250, cancellation_event=stop):
    print("tick")
```
