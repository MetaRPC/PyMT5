# ✅ Opened Orders Tickets

> **Request:** fetch IDs (tickets) of all currently opened **orders** and **positions**.
> Lightweight call to build fast lookups, cross‑checks, and polling loops.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `opened_orders_tickets(...)`
* `MetaRpcMT5/mt5_term_api_account_helper_pb2.py` — `OpenedOrdersTickets*`

**Menu entry:** `OpenedOrdersTickets`

---

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `OpenedOrdersTickets(OpenedOrdersTicketsRequest) → OpenedOrdersTicketsReply`
* **Low-level client:** `AccountHelperStub.OpenedOrdersTickets(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.opened_orders_tickets(deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Minimal canonical example
res = await acct.opened_orders_tickets()
# res is OpenedOrdersTicketsData
print(len(res.opened_orders_tickets), len(res.opened_position_tickets))
```

---

### Method Signature

```python
async def opened_orders_tickets(
    self,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> account_helper_pb2.OpenedOrdersTicketsData
```

---

## 💬 Plain English

* **What it is.** The **guest list** for your trading party: two neat lists of IDs — order tickets and position tickets — nothing more, nothing less.
* **Why you care.** Super fast checks ("do we still have anything open?"), set math (diff vs previous poll), and drill‑down fetches by ticket without transferring full objects.
* **Mind the traps.**

  * Tickets are **integers**; the call does **not** return prices/volumes. Use `OpenedOrders` (full objects) if you need rich data.
  * Lists may be **empty** — that’s valid and means no open orders/positions.
  * Treat them as **snapshots**; if you poll, compare sets and act on the delta.

---

## 🔽 Input

No required input parameters.

| Parameter            | Type            | Description |                                                    |
| -------------------- | --------------- | ----------- | -------------------------------------------------- |
| `deadline`           | \`datetime      | None\`      | Absolute per‑call deadline → converted to timeout. |
| `cancellation_event` | \`asyncio.Event | None\`      | Cooperative cancel for the retry wrapper.          |

---

## ⬆️ Output

### Payload: `OpenedOrdersTicketsData`

| Field                     | Proto Type       | Description                                    |
| ------------------------- | ---------------- | ---------------------------------------------- |
| `opened_orders_tickets`   | `repeated int64` | Ticket IDs of all currently opened **orders**. |
| `opened_position_tickets` | `repeated int64` | Ticket IDs of all **positions**.               |

---

### 🎯 Purpose

* Fast presence checks and polling loops with minimal payload.
* Build ticket‑indexed caches, then fetch details only when needed.
* Detect openings/closings by comparing previous and current snapshots.

### 🧩 Notes & Tips

* For **details**, pair this with `OpenedOrders` (full objects) or ticket‑specific RPCs.
* Convert lists to **sets** for O(1) membership checks and diffs.
* Wrapper retries transient gRPC errors via `execute_with_reconnect(...)`.

**See also:** [OpenedOrders](../Orders_Positions_History/opened_orders.md), [PositionsTotal](../Orders_Positions_History/positions_total.md).


---

## Usage Examples

### 1) Count & union (what’s live now)

```python
res = await acct.opened_orders_tickets()
all_tickets = set(res.opened_orders_tickets) | set(res.opened_position_tickets)
print(f"orders={len(res.opened_orders_tickets)} positions={len(res.opened_position_tickets)} total={len(all_tickets)}")
```

### 2) Delta vs previous poll (open/close events)

```python
prev = prev if 'prev' in globals() else (set(), set())
res = await acct.opened_orders_tickets()
orders_now = set(res.opened_orders_tickets)
pos_now    = set(res.opened_position_tickets)

orders_opened  = orders_now - prev[0]
orders_closed  = prev[0] - orders_now
pos_opened     = pos_now - prev[1]
pos_closed     = prev[1] - pos_now
print(orders_opened, orders_closed, pos_opened, pos_closed)
prev = (orders_now, pos_now)
```

### 3) With deadline & cancellation

```python
import asyncio
from datetime import datetime, timedelta, timezone

cancel_event = asyncio.Event()
res = await acct.opened_orders_tickets(
    deadline=datetime.now(timezone.utc) + timedelta(seconds=3),
    cancellation_event=cancel_event,
)
print(bool(res.opened_orders_tickets or res.opened_position_tickets))
```
