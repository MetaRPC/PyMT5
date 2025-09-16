# MT5Account · Orders.Positions.History — Overview

> Quick map of the **live & historical** order/position APIs. Use this page to pick the right call fast. Links jump to detailed specs.

## 📁 What lives here

* **[OpenedOrders](./opened_orders.md)** — current **pending orders** and **open positions** (full objects) with server‑side sorting.
* **[OpenedOrdersTickets](./opened_orders_tickets.md)** — IDs only: tickets of open **orders** and **positions** (lightweight snapshot).
* **[OrderHistory](./order_history.md)** — paginated **orders & deals** for a time range (mixed list).
* **[PositionsHistory](./positions_history.md)** — paginated **positions** history for a time range (position‑level view).
* **[PositionsTotal](./positions_total.md)** — total count of currently **open positions**.

---

## 🧭 Plain English

* **OpenedOrders** → your **“Now Playing”** board (full details of what’s live right now).
* **OpenedOrdersTickets** → the **guest list** (just IDs to diff/cache/poll fast).
* **OrderHistory** → the **time machine ledger** for **orders + deals**.
* **PositionsHistory** → the **closed positions ledger** (aggregated per position).
* **PositionsTotal** → the **headcount** of open positions.

> Rule of thumb: need **details now** → `OpenedOrders`. Need **just IDs** → `OpenedOrdersTickets`. Need **past events** → `OrderHistory` or `PositionsHistory` depending on granularity.

---

## Quick choose

| If you need…                       | Use                   | Returns                                                                            | Key inputs                                                       |
| ---------------------------------- | --------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Live objects (orders + positions)  | `OpenedOrders`        | `OpenedOrdersData` (`opened_orders[]`, `position_infos[]`)                         | `sort_mode` + optional `deadline`, `cancellation_event`          |
| Live IDs only (fast snapshot)      | `OpenedOrdersTickets` | `OpenedOrdersTicketsData` (`opened_orders_tickets[]`, `opened_position_tickets[]`) | *(none)* + optional `deadline`, `cancellation_event`             |
| Orders & deals history (mixed)     | `OrderHistory`        | `OrdersHistoryData` (`history_data[]`)                                             | `from_dt`, `to_dt`, `sort_mode`, `page_number`, `items_per_page` |
| Positions history (position‑level) | `PositionsHistory`    | `PositionsHistoryData` (`positions_data[]`)                                        | `sort_type`, `open_from`, `open_to`, `page`, `size`              |
| Count of open positions            | `PositionsTotal`      | `PositionsTotalData` (`total_positions`)                                           | *(none)* + optional `deadline`, `cancellation_event`             |

---

## ❌ Cross‑refs & gotchas

* **UTC timestamps everywhere.** Convert once; don’t re‑parse per render frame.
* **Server‑side sorting** is explicit via enums. If you need price‑sorted lists, sort client‑side.
* **OrderHistory** is **mixed**: each item is either an order or a deal — check which field is set.
* **No server‑side symbol filter** in history calls — filter client‑side by `symbol`.
* **Hedging vs netting** affects how you interpret counts and duplicates across symbols.
* **Polling?** Use `OpenedOrdersTickets` for set‑diffs; fetch details with `OpenedOrders` only on changes.

---

## 🟢 Minimal snippets

```python
# OpenedOrders — how many live objects now?
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2
od = await acct.opened_orders(ah_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC)
print(len od.opened_orders, len od.position_infos)
```

```python
# OpenedOrdersTickets — union of IDs
res = await acct.opened_orders_tickets()
all_ids = set(res.opened_orders_tickets) | set(res.opened_position_tickets)
print(len(all_ids))
```

```python
# OrderHistory — last 7 days, first page
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2
now = datetime.now(timezone.utc)
h = await acct.order_history(now - timedelta(days=7), now, ah_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_CLOSE_TIME_DESC, 1, 100)
print(h.arrayTotal, len(h.history_data))
```

```python
# PositionsHistory — last 30 days, 100 per page
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2
now = datetime.now(timezone.utc)
ph = await acct.positions_history(ah_pb2.BMT5_ENUM_POSITIONS_HISTORY_SORT_TYPE.BMT5_POSHIST_SORT_BY_CLOSE_TIME_DESC, now - timedelta(days=30), now, 1, 100)
print(ph.arrayTotal, len(ph.positions_data))
```

```python
# PositionsTotal — count badge
data = await acct.positions_total()
print(int(data.total_positions))
```
