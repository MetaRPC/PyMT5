# ✅ Order History

> **Request:** paginated **order & deal history** for a time range.
> One RPC that returns a page of historical entries (orders + deals) with server‑side sorting.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `order_history(...)`
* `MetaRpcMT5/mt5_term_api_account_helper_pb2.py` — `OrderHistory*`, `OrdersHistoryData`, `HistoryData`, `OrderHistoryData`, `DealHistoryData`, `BMT5_ENUM_ORDER_HISTORY_SORT_TYPE`

---

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `OrderHistory(OrderHistoryRequest) → OrderHistoryReply`
* **Low-level client:** `AccountHelperStub.OrderHistory(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.order_history(from_dt, to_dt, sort_mode, page_number=0, items_per_page=0, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Minimal canonical example: last 7 days, sort by CLOSE_TIME desc, first page
from datetime import datetime, timedelta, timezone
from google.protobuf.timestamp_pb2 import Timestamp
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

now = datetime.now(timezone.utc)
from_dt = now - timedelta(days=7)

res = await acct.order_history(
    from_dt=from_dt,
    to_dt=now,
    sort_mode=ah_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_CLOSE_TIME_DESC,
    page_number=1,
    items_per_page=100,
)

print(res.arrayTotal, len(res.history_data))  # total items, items on this page
```

---

### Method Signature

```python
async def order_history(
    self,
    from_dt: datetime,
    to_dt: datetime,
    sort_mode: account_helper_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE,
    page_number: int = 1,
    items_per_page: int = 100,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> account_helper_pb2.OrdersHistoryData
```

---

## 💬 Plain English

* **What it is.** Your **time machine ledger**: ask for a date window, get a neat page of historical **orders** and **deals** (both types in one list).
* **Why you care.** Audit, reporting, and troubleshooting (“what actually happened between X and Y?”) with stable server‑side sorting.
* **Mind the traps.**

  * This call is **paginated** — you get `arrayTotal`, `pageNumber`, `itemsPerPage` and a **page** of `history_data`.
  * The server returns a **mix**: each `HistoryData` has **either** `history_order` **or** `history_deal` set (the other is empty).
---

## 🔽 Input

| Parameter            | Type                                                     | Description                                                                                             |                                                    |
| -------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| `from_dt`            | `datetime` (UTC)                                         | Start of the time window (inclusive).                                                                   |                                                    |
| `to_dt`              | `datetime` (UTC)                                         | End of the time window (exclusive/inclusive per broker, safe to treat as inclusive for 1s granularity). |                                                    |
| `sort_mode`          | `BMT5_ENUM_ORDER_HISTORY_SORT_TYPE` (enum, **required**) | Server‑side sort to apply (see enum below).                                                             |                                                    |
| `page_number`        | `int`                                                    | 1‑based page number. Use `1` for the first page.                                                        |                                                    |
| `items_per_page`     | `int`                                                    | Items per page (e.g., 50/100/500). `0` may mean “all” (broker‑dependent).                               |                                                    |
| `deadline`           | \`datetime                                               | None\`                                                                                                  | Absolute per‑call deadline → converted to timeout. |
| `cancellation_event` | \`asyncio.Event                                          | None\`                                                                                                  | Cooperative cancel for the retry wrapper.          |

> **Request message:** `OrderHistoryRequest { inputFrom, inputTo, inputSortMode, pageNumber, itemsPerPage }`

---

## ⬆️ Output

### Payload: `OrdersHistoryData`

| Field          | Proto Type             | Description                             |
| -------------- | ---------------------- | --------------------------------------- |
| `arrayTotal`   | `int32`                | Total number of items across all pages. |
| `pageNumber`   | `int32`                | Page number in this reply.              |
| `itemsPerPage` | `int32`                | Items per page in this reply.           |
| `history_data` | `repeated HistoryData` | Mixed list of **orders** and **deals**. |

#### Message: `HistoryData`

| Field           | Proto Type                | Description                    |
| --------------- | ------------------------- | ------------------------------ |
| `index`         | `uint32`                  | Internal ordering index.       |
| `history_order` | `OrderHistoryData` (opt.) | Present for **order** entries. |
| `history_deal`  | `DealHistoryData` (opt.)  | Present for **deal** entries.  |

#### Message: `OrderHistoryData`

| Field             | Type                           | Notes                                       |
| ----------------- | ------------------------------ | ------------------------------------------- |
| `ticket`          | `uint64`                       | Order ticket ID.                            |
| `setup_time`      | `Timestamp`                    | When the order was created.                 |
| `done_time`       | `Timestamp`                    | When the order was filled/canceled/expired. |
| `state`           | `BMT5_ENUM_ORDER_STATE`        | STARTED/PLACED/CANCELED/PARTIAL/FILLED/…    |
| `price_current`   | `double`                       | Current price at fetch.                     |
| `price_open`      | `double`                       | Order price.                                |
| `stop_limit`      | `double`                       | Stop‑limit price (if any).                  |
| `stop_loss`       | `double`                       | SL.                                         |
| `take_profit`     | `double`                       | TP.                                         |
| `volume_current`  | `double`                       | Remaining volume.                           |
| `volume_initial`  | `double`                       | Initial volume.                             |
| `magic_number`    | `int64`                        | EA/strategy tag.                            |
| `type`            | `BMT5_ENUM_ORDER_TYPE`         | BUY\_LIMIT/SELL\_STOP/…                     |
| `time_expiration` | `Timestamp`                    | GTD expiration.                             |
| `type_filling`    | `BMT5_ENUM_ORDER_TYPE_FILLING` | FOK/IOC/RETURN/BOC.                         |
| `type_time`       | `BMT5_ENUM_ORDER_TYPE_TIME`    | GTC/DAY/SPECIFIED/…                         |
| `position_id`     | `uint64`                       | Related position ID.                        |
| `symbol`          | `string`                       | Symbol.                                     |
| `external_id`     | `string`                       | External ID if any.                         |
| `comment`         | `string`                       | Broker/user comment.                        |
| `account_login`   | `int64`                        | Account login.                              |

#### Message: `DealHistoryData`

| Field           | Type                        | Notes                    |
| --------------- | --------------------------- | ------------------------ |
| `ticket`        | `uint64`                    | Deal ticket ID.          |
| `profit`        | `double`                    | Profit for this deal.    |
| `commission`    | `double`                    | Commission.              |
| `fee`           | `double`                    | Fee.                     |
| `price`         | `double`                    | Deal price.              |
| `stop_loss`     | `double`                    | SL at time of deal.      |
| `take_profit`   | `double`                    | TP at time of deal.      |
| `swap`          | `double`                    | Swap accrued.            |
| `volume`        | `double`                    | Deal volume.             |
| `entry_type`    | `BMT5_ENUM_DEAL_ENTRY_TYPE` | IN/OUT/IN\_OUT/…         |
| `time`          | `Timestamp`                 | Deal time.               |
| `type`          | `BMT5_ENUM_DEAL_TYPE`       | BUY/SELL/…               |
| `reason`        | `BMT5_ENUM_DEAL_REASON`     | CLIENT/EXPERT/SL/TP/SO/… |
| `position_id`   | `uint64`                    | Position ID.             |
| `comment`       | `string`                    | Comment.                 |
| `symbol`        | `string`                    | Symbol.                  |
| `external_id`   | `string`                    | External ID.             |
| `account_login` | `int64`                     | Account login.           |

---

### Enum: `BMT5_ENUM_ORDER_HISTORY_SORT_TYPE`

| Number | Value                               | Meaning                |
| -----: | ----------------------------------- | ---------------------- |
|      0 | `BMT5_SORT_BY_OPEN_TIME_ASC`        | Open time ascending.   |
|      1 | `BMT5_SORT_BY_OPEN_TIME_DESC`       | Open time descending.  |
|      2 | `BMT5_SORT_BY_CLOSE_TIME_ASC`       | Close time ascending.  |
|      3 | `BMT5_SORT_BY_CLOSE_TIME_DESC`      | Close time descending. |
|      4 | `BMT5_SORT_BY_ORDER_TICKET_ID_ASC`  | Ticket ascending.      |
|      5 | `BMT5_SORT_BY_ORDER_TICKET_ID_DESC` | Ticket descending.     |

> Related enums used above: `BMT5_ENUM_ORDER_STATE`, `BMT5_ENUM_ORDER_TYPE`, `BMT5_ENUM_ORDER_TYPE_FILLING`, `BMT5_ENUM_ORDER_TYPE_TIME`, `BMT5_ENUM_DEAL_TYPE`, `BMT5_ENUM_DEAL_ENTRY_TYPE`, `BMT5_ENUM_DEAL_REASON`.

---

### 🎯 Purpose

* Build reports, audit trails, and UI history with server‑side sorting and pagination.
* Reconcile with broker statements; investigate fills/cancellations and reasons.
* Power infinite‑scroll history views efficiently.

### 🧩 Notes & Tips

* **Pagination 101:** fetch first page → read `arrayTotal` to estimate total pages → loop.
* Convert all `Timestamp` values once and reuse; don’t reparse per render.
* No server‑side symbol filter — filter client‑side.
* Wrapper handles transient gRPC hiccups via `execute_with_reconnect(...)`.

**See also:** [PositionsHistory](../Orders_Positions_History/positions_history.md), [OpenedOrders](../Orders_Positions_History/opened_orders.md), [OpenedOrdersTickets](../Orders_Positions_History/opened_orders_tickets.md).


---

## Usage Examples

### 1) Simple pager (last 30 days)

```python
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

now = datetime.now(timezone.utc)
from_dt = now - timedelta(days=30)

page, page_size = 1, 100
res = await acct.order_history(
    from_dt, now,
    ah_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_CLOSE_TIME_DESC,
    page, page_size
)
print(f"page {res.pageNumber}/{(res.arrayTotal + page_size - 1)//page_size}")
```

### 2) Fetch all pages (be kind to the server)

```python
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

now = datetime.now(timezone.utc)
from_dt = now - timedelta(days=7)

page_size = 200
page = 1
all_items = []
while True:
    res = await acct.order_history(
        from_dt, now,
        ah_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_OPEN_TIME_ASC,
        page, page_size
    )
    all_items.extend(res.history_data)
    if len(res.history_data) < page_size:
        break
    page += 1
print(len(all_items))
```

### 3) Client‑side filter: only symbol = "EURUSD"

```python
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

now = datetime.now(timezone.utc)
res = await acct.order_history(
    now - timedelta(days=3), now,
    ah_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_CLOSE_TIME_DESC,
    1, 100
)
filtered = []
for h in res.history_data:
    if h.history_order and h.history_order.symbol == "EURUSD":
        filtered.append(h)
    elif h.history_deal and h.history_deal.symbol == "EURUSD":
        filtered.append(h)
print(len(filtered))
```

### 4) With deadline & cancellation

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

cancel_event = asyncio.Event()
res = await acct.order_history(
    datetime.now(timezone.utc) - timedelta(days=1),
    datetime.now(timezone.utc),
    ah_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_ORDER_TICKET_ID_ASC,
    1, 100,
    deadline=datetime.now(timezone.utc) + timedelta(seconds=3),
    cancellation_event=cancel_event,
)
print(res.itemsPerPage)
```
