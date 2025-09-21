# ✅ Opened Orders

> **Request:** fetch all currently opened **orders** and active **positions** for the connected MT5 account.
> Returns a combined payload so you can render an immediate “what’s live now” view.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `opened_orders(...)`
* `MetaRpcMT5/mt5_term_api_account_helper_pb2.py` — `OpenedOrders*`, `BMT5_ENUM_OPENED_ORDER_SORT_TYPE`, `OpenedOrderInfo`, `PositionInfo`

---

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `OpenedOrders(OpenedOrdersRequest) → OpenedOrdersReply`
* **Low-level client:** `AccountHelperStub.OpenedOrders(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.opened_orders(sort_mode, deadline=None, cancellation_event=None) -> OpenedOrdersData`

**Request message:** `OpenedOrdersRequest { inputSortMode: BMT5_ENUM_OPENED_ORDER_SORT_TYPE }`

**Reply message:** `OpenedOrdersReply { data: OpenedOrdersData }`

---

### 🔗 Code Example

```python
# Minimal canonical example: sort by open-time ascending
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

res = await acct.opened_orders(
    ah_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
)
# res is OpenedOrdersData
print(len(res.opened_orders), len(res.position_infos))
```

---

### Method Signature

```python
async def opened_orders(
    self,
    sort_mode: account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> account_helper_pb2.OpenedOrdersData
```

---

## 💬 Plain English

* **What it is.** Think of this as your **“Now Playing”** board: one call that lists current **orders** (pending) and **positions** (active exposure).
* **Why you care.** It powers dashboards, risk views, and quick operator checks without stitching multiple RPCs.
* **Mind the traps.**

  * Sorting is done **server‑side** by the `sort_mode` enum — pick ascending/descending explicitly.
  * `orders` and `positions` are **different**: pending orders can have `time_expiration`, positions have `profit/swap` and `position_commission`.
  * Timestamps are `google.protobuf.Timestamp` (UTC). Convert before printing.
* **When to call.** On screen open, periodic refresh, or right before sensitive actions.
* **Quick check.** You should get two lists: `opened_orders[]` and `position_infos[]`. Empty lists are valid.

---

## 🔽 Input

| Parameter            | Type                                                    | Description                                        |
| -------------------- | ------------------------------------------------------- | -------------------------------------------------- |
| `sort_mode`          | `BMT5_ENUM_OPENED_ORDER_SORT_TYPE` (enum, **required**) | Server‑side sort to apply (see enum below).        |
| `deadline`           | `datetime \| None`                                      | Absolute per‑call deadline → converted to timeout. |
| `cancellation_event` | `asyncio.Event \| None`                                 | Cooperative cancel for the retry wrapper.          |

> **Request message:** `OpenedOrdersRequest { inputSortMode: BMT5_ENUM_OPENED_ORDER_SORT_TYPE }`

---

## ⬆️ Output

### Payload: `OpenedOrdersData`

| Field            | Proto Type                 | Description                           |
| ---------------- | -------------------------- | ------------------------------------- |
| `opened_orders`  | `repeated OpenedOrderInfo` | Pending orders currently on the book. |
| `position_infos` | `repeated PositionInfo`    | Active positions for the account.     |

#### `OpenedOrderInfo`

|  # | Field             | Type                                | Notes                                |
| -: | ----------------- | ----------------------------------- | ------------------------------------ |
|  1 | `index`           | `uint32`                            | Internal ordering index.             |
|  2 | `ticket`          | `uint64`                            | Order ticket ID.                     |
|  3 | `price_current`   | `double`                            | Current market price.                |
|  4 | `price_open`      | `double`                            | Order price (for pending orders).    |
|  5 | `stop_limit`      | `double`                            | Stop‑limit price (if applicable).    |
|  6 | `stop_loss`       | `double`                            | SL.                                  |
|  7 | `take_profit`     | `double`                            | TP.                                  |
|  8 | `volume_current`  | `double`                            | Remaining volume.                    |
|  9 | `volume_initial`  | `double`                            | Initial volume.                      |
| 10 | `magic_number`    | `int64`                             | EA/strategy tag.                     |
| 11 | `reason`          | `int32`                             | Broker reason code.                  |
| 12 | `type`            | `enum BMT5_ENUM_ORDER_TYPE`         | Market/limit/stop/... (see enum).    |
| 13 | `state`           | `enum BMT5_ENUM_ORDER_STATE`        | Started/Placed/Partial/… (see enum). |
| 14 | `time_expiration` | `google.protobuf.Timestamp`         | Expiration time (GTD).               |
| 15 | `time_setup`      | `google.protobuf.Timestamp`         | Created at.                          |
| 16 | `time_done`       | `google.protobuf.Timestamp`         | Filled/canceled time.                |
| 17 | `type_filling`    | `enum BMT5_ENUM_ORDER_TYPE_FILLING` | FOK/IOC/RETURN/BOC.                  |
| 18 | `type_time`       | `enum BMT5_ENUM_ORDER_TYPE_TIME`    | GTC/DAY/SPECIFIED/…                  |
| 19 | `position_id`     | `int64`                             | Related position ID.                 |
| 20 | `position_by_id`  | `int64`                             | Close‑by position ID.                |
| 21 | `symbol`          | `string`                            | Symbol name.                         |
| 22 | `external_id`     | `string`                            | External ID if any.                  |
| 23 | `comment`         | `string`                            | User/broker comment.                 |
| 24 | `account_login`   | `int64`                             | Account login.                       |

#### `PositionInfo`

|  # | Field                 | Type                             | Notes                                     |
| -: | --------------------- | -------------------------------- | ----------------------------------------- |
|  1 | `index`               | `uint32`                         | Internal ordering index.                  |
|  2 | `ticket`              | `uint64`                         | Position ticket ID.                       |
|  3 | `open_time`           | `google.protobuf.Timestamp`      | When the position was opened.             |
|  4 | `volume`              | `double`                         | Current volume.                           |
|  5 | `price_open`          | `double`                         | Open price.                               |
|  6 | `stop_loss`           | `double`                         | SL.                                       |
|  7 | `take_profit`         | `double`                         | TP.                                       |
|  8 | `price_current`       | `double`                         | Current market price.                     |
|  9 | `swap`                | `double`                         | Accrued swap.                             |
| 10 | `profit`              | `double`                         | Floating P/L.                             |
| 11 | `last_update_time`    | `google.protobuf.Timestamp`      | Last time server updated the position.    |
| 12 | `type`                | `enum BMT5_ENUM_POSITION_TYPE`   | BUY/SELL.                                 |
| 13 | `magic_number`        | `int64`                          | EA/strategy tag.                          |
| 14 | `identifier`          | `int64`                          | Position identifier.                      |
| 15 | `reason`              | `enum BMT5_ENUM_POSITION_REASON` | Open reason (client/web/expert/SL/TP/SO). |
| 16 | `symbol`              | `string`                         | Symbol name.                              |
| 17 | `comment`             | `string`                         | User/broker comment.                      |
| 18 | `external_id`         | `string`                         | External ID if any.                       |
| 19 | `position_commission` | `double`                         | Commission attributed to the position.    |
| 20 | `account_login`       | `int64`                          | Account login.                            |

---

### Enum: `BMT5_ENUM_OPENED_ORDER_SORT_TYPE`

| Number | Value                                            | Meaning               |
| -----: | ------------------------------------------------ | --------------------- |
|      0 | `BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC`        | Open time ascending.  |
|      1 | `BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_DESC`       | Open time descending. |
|      2 | `BMT5_OPENED_ORDER_SORT_BY_ORDER_TICKET_ID_ASC`  | Ticket ID ascending.  |
|      3 | `BMT5_OPENED_ORDER_SORT_BY_ORDER_TICKET_ID_DESC` | Ticket ID descending. |

**Related enums used above (values per pb):**

* `BMT5_ENUM_ORDER_TYPE`: BUY, SELL, BUY\_LIMIT, SELL\_LIMIT, BUY\_STOP, SELL\_STOP, BUY\_STOP\_LIMIT, SELL\_STOP\_LIMIT, CLOSE\_BY.
* `BMT5_ENUM_ORDER_STATE`: STARTED, PLACED, CANCELED, PARTIAL, FILLED, REJECTED, EXPIRED, REQUEST\_ADD, REQUEST\_MODIFY, REQUEST\_CANCEL.
* `BMT5_ENUM_ORDER_TYPE_FILLING`: FOK, IOC, RETURN, BOC.
* `BMT5_ENUM_ORDER_TYPE_TIME`: GTC, DAY, SPECIFIED, SPECIFIED\_DAY.
* `BMT5_ENUM_POSITION_TYPE`: BUY, SELL.
* `BMT5_ENUM_POSITION_REASON`: CLIENT, MOBILE, WEB, EXPERT, ORDER\_REASON\_SL, ORDER\_REASON\_TP, ORDER\_REASON\_SO.

---

### 🎯 Purpose

* Render a live “Opened Orders & Positions” widget in UI/CLI.
* Drive risk/ops checks (e.g., detect stale SL/TP or unusual fills).
* Provide a single RPC for most “what’s open now?” use‑cases.

### 🧩 Notes & Tips

* Use `sort_mode` for stable snapshots (open time vs ticket order). For price‑sorted views, sort client‑side.
* Convert `Timestamp` to local time **once** and reuse; don’t recompute in every render tick.
* The SDK wrapper retries transient gRPC errors via `execute_with_reconnect(...)`.

**See also:** [OpenedOrdersTickets](../Orders_Positions_History/opened_orders_tickets.md), [OrderHistory](../Orders_Positions_History/order_history.md), [PositionsHistory](../Orders_Positions_History/positions_history.md), [PositionsTotal](../Orders_Positions_History/positions_total.md).

---

## Usage Examples

### 1) By open time (ASC) → print compact table

```python
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

od = await acct.opened_orders(
    ah_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
)
for o in od.opened_orders:
    print(f"#{o.ticket} {o.symbol} vol={o.volume_current:.2f} state={o.state}")
for p in od.position_infos:
    print(f"POS#{p.ticket} {p.symbol} vol={p.volume:.2f} pnl={p.profit:.2f}")
```

### 2) By ticket (DESC) with deadline & cancellation

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

cancel_event = asyncio.Event()

od = await acct.opened_orders(
    ah_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_ORDER_TICKET_ID_DESC,
    deadline=datetime.now(timezone.utc) + timedelta(seconds=3),
    cancellation_event=cancel_event,
)
print(len(od.opened_orders), len(od.position_infos))
```

### 3) Client‑side filter: only one symbol

```python
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

od = await acct.opened_orders(
    ah_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
)
filtered_orders = [o for o in od.opened_orders if o.symbol == "EURUSD"]
filtered_positions = [p for p in od.position_infos if p.symbol == "EURUSD"]
print(len(filtered_orders), len(filtered_positions))
```
