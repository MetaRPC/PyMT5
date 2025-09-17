# ✅ OnTrade (subscription)

> **Request:** subscribe to **live trading events**: new/updated/removed **orders**, **deals history**, **positions**, plus account P/L snapshot bundled with each event.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `on_trade(...)`
* `MetaRpcMT5/mt5_term_api_subscriptions_pb2.py` — `OnTrade*` messages and event payloads
* `MetaRpcMT5/mt5_term_api_subscriptions_pb2_grpc.py` — service stub `SubscriptionServiceStub`

### RPC

* **Service:** `mt5_term_api.SubscriptionService`
* **Method:** `OnTrade(OnTradeRequest) → stream OnTradeReply`
* **Low-level client:** `SubscriptionServiceStub.OnTrade(request, metadata, timeout)` *(server‑streaming iterator)*
* **SDK wrapper:** `MT5Account.on_trade(cancellation_event=None) → async stream of OnTradeData`

---

### 🔗 Code Example

```python
# Minimal: print what changed per event
async for ev in acct.on_trade():
    d = ev.event_data
    print(
        len(d.new_orders), len(d.state_changed_orders), len(d.disappeared_orders),
        len(d.new_positions), len(d.updated_positions), len(d.disappeared_positions),
        len(d.new_history_deals)
    )
```

```python
# Cooperative cancellation after N events
import asyncio
cancel = asyncio.Event()
count = 0
async for ev in acct.on_trade(cancellation_event=cancel):
    count += 1
    # Example: account equity after event
    print(ev.account_info.equity)
    if count >= 20:
        cancel.set()
```

---

### Method Signature

```python
async def on_trade(
    self,
    cancellation_event: asyncio.Event | None = None,
) -> subscription_client.OnTrade  # async iterable of OnTradeData
```

---

## 💬 Just about the main thing

* **What it is.** A **live feed** of trade‑related updates grouped into a single event: order/position deltas, deal & order history deltas, and account equity/margin snapshot.
* **Why.** Ideal for keeping UIs and state machines in sync without polling multiple RPCs.
* **Be careful.**

  * Stream is **infinite** until you cancel via `cancellation_event`.
  * Timestamps are UTC (`Timestamp`) and some fields also provide **ms since epoch** (`*_time_msc`).
  * Handle **empty lists** — not every group changes on each event.

---

## 🔽 Input

| Parameter            | Type                      | Description         |                                         |
| -------------------- | ------------------------- | ------------------- | --------------------------------------- |
| `cancellation_event` | \`asyncio.Event           | None\`              | Cooperative stop for the streaming RPC. |

> **Request message:** `OnTradeRequest {}`

---

## ⬆️ Output

### Stream payload: `OnTradeData`

| Field                       | Proto Type                      | Description                               |
| --------------------------- | ------------------------------- | ----------------------------------------- |
| `type`                      | `MT5_SUB_ENUM_EVENT_GROUP_TYPE` | Event group marker (e.g., `OrderUpdate`). |
| `event_data`                | `OnTadeEventData`               | Batched deltas (lists below).             |
| `account_info`              | `OnEventAccountInfo`            | Balance/Equity/Margins snapshot.          |
| `terminal_instance_guid_id` | `string`                        | Source terminal GUID.                     |

#### `OnTadeEventData` (batched lists)

| List name                      | Item type                   | What it carries                        |
| ------------------------------ | --------------------------- | -------------------------------------- |
| `new_orders[]`                 | `OnTradeOrderInfo`          | Newly placed orders.                   |
| `disappeared_orders[]`         | `OnTradeOrderInfo`          | Orders removed from book.              |
| `state_changed_orders[]`       | `OnTradeOrderStateChange`   | Before/after for order state changes.  |
| `new_history_orders[]`         | `OnTradeHistoryOrderInfo`   | Fresh entries in order history.        |
| `disappeared_history_orders[]` | `OnTradeHistoryOrderInfo`   | Removed order‑history entries.         |
| `updated_history_orders[]`     | `OnTradeHistoryOrderUpdate` | Before/after for order‑history update. |
| `new_history_deals[]`          | `OnTradeHistoryDealInfo`    | Fresh deals.                           |
| `disappeared_history_deals[]`  | `OnTradeHistoryDealInfo`    | Removed deals.                         |
| `updated_history_deals[]`      | `OnTradeHistoryDealUpdate`  | Before/after for deal‑history update.  |
| `new_positions[]`              | `OnTradePositionInfo`       | Newly opened positions.                |
| `disappeared_positions[]`      | `OnTradePositionInfo`       | Closed positions.                      |
| `updated_positions[]`          | `OnTradePositionUpdate`     | Before/after for position updates.     |

#### `OnEventAccountInfo`

|  # | Field          | Type   |
| -: | -------------- | ------ |
|  1 | `balance`      | double |
|  2 | `credit`       | double |
|  3 | `equity`       | double |
|  4 | `margin`       | double |
|  5 | `free_margin`  | double |
|  6 | `profit`       | double |
|  7 | `margin_level` | double |
|  8 | `login`        | int64  |

#### `OnTradeOrderInfo`

|  # | Field                     | Type                          |
| -: | ------------------------- | ----------------------------- |
|  1 | `index`                   | int32                         |
|  2 | `ticket`                  | int64                         |
|  3 | `state`                   | `SUB_ENUM_ORDER_STATE`        |
|  4 | `setup_time_msc`          | int64                         |
|  5 | `stop_loss`               | double                        |
|  6 | `take_profit`             | double                        |
|  7 | `stop_limit`              | double                        |
|  8 | `price_current`           | double                        |
|  9 | `time_expiration`         | `Timestamp`                   |
| 10 | `time_type`               | `SUB_ENUM_ORDER_TYPE_TIME`    |
| 11 | `comment`                 | string                        |
| 12 | `symbol`                  | string                        |
| 13 | `magic`                   | int64                         |
| 14 | `price_open`              | double                        |
| 15 | `setup_time`              | `Timestamp`                   |
| 16 | `time_expiration_seconds` | int64                         |
| 17 | `volume_current`          | double                        |
| 18 | `volume_initial`          | double                        |
| 19 | `account_login`           | int64                         |
| 20 | `order_type`              | `SUB_ENUM_ORDER_TYPE`         |
| 21 | `order_type_filling`      | `SUB_ENUM_ORDER_TYPE_FILLING` |
| 22 | `order_reason`            | `SUB_ENUM_ORDER_REASON`       |
| 23 | `position_id`             | int64                         |
| 24 | `position_by_id`          | int64                         |

#### `OnTradeOrderStateChange`

|  # | Field            | Type               |
| -: | ---------------- | ------------------ |
|  1 | `previous_order` | `OnTradeOrderInfo` |
|  2 | `current_order`  | `OnTradeOrderInfo` |

#### `OnTradeHistoryOrderInfo`

|  # | Field                     | Type                          |
| -: | ------------------------- | ----------------------------- |
|  1 | `index`                   | int32                         |
|  2 | `ticket`                  | int64                         |
|  3 | `state`                   | `SUB_ENUM_ORDER_STATE`        |
|  4 | `setup_time`              | `Timestamp`                   |
|  5 | `done_time`               | `Timestamp`                   |
|  6 | `time_expiration`         | `Timestamp`                   |
|  7 | `position_id`             | uint64                        |
|  8 | `type_time`               | `SUB_ENUM_ORDER_TYPE_TIME`    |
|  9 | `stop_loss`               | double                        |
| 10 | `take_profit`             | double                        |
| 11 | `stop_limit`              | double                        |
| 12 | `price_current`           | double                        |
| 13 | `price_open`              | double                        |
| 14 | `volume_current`          | double                        |
| 15 | `volume_initial`          | double                        |
| 19 | `magic`                   | int64                         |
| 20 | `position_by`             | int64                         |
| 21 | `reason`                  | `SUB_ENUM_DEAL_REASON`        |
| 22 | `comment`                 | string                        |
| 23 | `symbol`                  | string                        |
| 24 | `time_expiration_seconds` | int64                         |
| 25 | `account_login`           | int64                         |
| 26 | `order_type`              | `SUB_ENUM_ORDER_TYPE`         |
| 27 | `order_type_filling`      | `SUB_ENUM_ORDER_TYPE_FILLING` |

#### `OnTradeHistoryOrderUpdate`

|  # | Field                    | Type                      |
| -: | ------------------------ | ------------------------- |
|  1 | `previous_history_order` | `OnTradeHistoryOrderInfo` |
|  2 | `current_history_order`  | `OnTradeHistoryOrderInfo` |

#### `OnTradeHistoryDealInfo`

|  # | Field              | Type                   |
| -: | ------------------ | ---------------------- |
|  1 | `index`            | int32                  |
|  2 | `ticket`           | uint64                 |
|  3 | `order_ticket`     | int64                  |
|  4 | `type`             | `SUB_ENUM_DEAL_TYPE`   |
|  5 | `deal_time`        | `Timestamp`            |
|  6 | `entry`            | `SUB_ENUM_DEAL_ENTRY`  |
|  7 | `deal_position_id` | int64                  |
|  8 | `commission`       | double                 |
|  9 | `fee`              | double                 |
| 10 | `price`            | double                 |
| 11 | `profit`           | double                 |
| 12 | `sl`               | double                 |
| 13 | `tp`               | double                 |
| 14 | `volume`           | double                 |
| 15 | `comment`          | string                 |
| 16 | `symbol`           | string                 |
| 17 | `swap`             | double                 |
| 18 | `reason`           | `SUB_ENUM_DEAL_REASON` |
| 19 | `magic`            | int64                  |
| 20 | `account_login`    | int64                  |

#### `OnTradeHistoryDealUpdate`

|  # | Field                   | Type                     |
| -: | ----------------------- | ------------------------ |
|  1 | `previous_history_deal` | `OnTradeHistoryDealInfo` |
|  2 | `current_history_deal`  | `OnTradeHistoryDealInfo` |

#### `OnTradePositionInfo`

|  # | Field                | Type                       |
| -: | -------------------- | -------------------------- |
|  1 | `index`              | int32                      |
|  2 | `ticket`             | int64                      |
|  3 | `type`               | `SUB_ENUM_POSITION_TYPE`   |
|  4 | `position_time`      | `Timestamp`                |
|  5 | `last_update_time`   | `Timestamp`                |
|  6 | `price_open`         | double                     |
|  7 | `profit`             | double                     |
|  8 | `sl`                 | double                     |
|  9 | `tp`                 | double                     |
| 10 | `volume`             | double                     |
| 11 | `swap`               | double                     |
| 12 | `comment`            | string                     |
| 13 | `symbol`             | string                     |
| 14 | `magic`              | int64                      |
| 15 | `price_current`      | double                     |
| 16 | `account_login`      | int64                      |
| 17 | `reason`             | `SUB_ENUM_POSITION_REASON` |
| 18 | `from_pending_order` | bool                       |

#### `OnTradePositionUpdate`

|  # | Field               | Type                  |
| -: | ------------------- | --------------------- |
|  1 | `previous_position` | `OnTradePositionInfo` |
|  2 | `current_position`  | `OnTradePositionInfo` |

---

## Enums (used here)

### `MT5_SUB_ENUM_EVENT_GROUP_TYPE`

| Number | Value         |
| -----: | ------------- |
|      0 | `OrderProfit` |
|      1 | `OrderUpdate` |

### `SUB_ENUM_ORDER_TYPE`

| Number | Value                            |
| -----: | -------------------------------- |
|      0 | `SUB_ORDER_TYPE_BUY`             |
|      1 | `SUB_ORDER_TYPE_SELL`            |
|      2 | `SUB_ORDER_TYPE_BUY_LIMIT`       |
|      3 | `SUB_ORDER_TYPE_SELL_LIMIT`      |
|      4 | `SUB_ORDER_TYPE_BUY_STOP`        |
|      5 | `SUB_ORDER_TYPE_SELL_STOP`       |
|      6 | `SUB_ORDER_TYPE_BUY_STOP_LIMIT`  |
|      7 | `SUB_ORDER_TYPE_SELL_STOP_LIMIT` |
|      8 | `SUB_ORDER_TYPE_CLOSE_BY`        |

### `SUB_ENUM_ORDER_STATE`

| Number | Value                            |
| -----: | -------------------------------- |
|      0 | `SUB_ORDER_STATE_STARTED`        |
|      1 | `SUB_ORDER_STATE_PLACED`         |
|      2 | `SUB_ORDER_STATE_CANCELED`       |
|      3 | `SUB_ORDER_STATE_PARTIAL`        |
|      4 | `SUB_ORDER_STATE_FILLED`         |
|      5 | `SUB_ORDER_STATE_REJECTED`       |
|      6 | `SUB_ORDER_STATE_EXPIRED`        |
|      7 | `SUB_ORDER_STATE_REQUEST_ADD`    |
|      8 | `SUB_ORDER_STATE_REQUEST_MODIFY` |
|      9 | `SUB_ORDER_STATE_REQUEST_CANCEL` |

### `SUB_ENUM_ORDER_TYPE_FILLING`

| Number | Value                      |
| -----: | -------------------------- |
|      0 | `SUB_ORDER_FILLING_FOK`    |
|      1 | `SUB_ORDER_FILLING_IOC`    |
|      2 | `SUB_ORDER_FILLING_BOC`    |
|      3 | `SUB_ORDER_FILLING_RETURN` |

### `SUB_ENUM_ORDER_TYPE_TIME`

| Number | Value                          |
| -----: | ------------------------------ |
|      0 | `SUB_ORDER_TIME_GTC`           |
|      1 | `SUB_ORDER_TIME_DAY`           |
|      2 | `SUB_ORDER_TIME_SPECIFIED`     |
|      3 | `SUB_ORDER_TIME_SPECIFIED_DAY` |

### `SUB_ENUM_POSITION_TYPE`

| Number | Value                    |
| -----: | ------------------------ |
|      0 | `SUB_POSITION_TYPE_BUY`  |
|      1 | `SUB_POSITION_TYPE_SELL` |

### `SUB_ENUM_POSITION_REASON`

| Number | Value                        |
| -----: | ---------------------------- |
|      0 | `SUB_POSITION_REASON_CLIENT` |
|      2 | `SUB_POSITION_REASON_MOBILE` |
|      3 | `SUB_POSITION_REASON_WEB`    |
|      4 | `SUB_POSITION_REASON_EXPERT` |

### `SUB_ENUM_DEAL_TYPE`

| Number | Value                                    |
| -----: | ---------------------------------------- |
|      0 | `SUB_DEAL_TYPE_BUY`                      |
|      1 | `SUB_DEAL_TYPE_SELL`                     |
|      2 | `SUB_DEAL_TYPE_BALANCE`                  |
|      3 | `SUB_DEAL_TYPE_CREDIT`                   |
|      4 | `SUB_DEAL_TYPE_CHARGE`                   |
|      5 | `SUB_DEAL_TYPE_CORRECTION`               |
|      6 | `SUB_DEAL_TYPE_BONUS`                    |
|      7 | `SUB_DEAL_TYPE_COMMISSION`               |
|      8 | `SUB_DEAL_TYPE_COMMISSION_DAILY`         |
|      9 | `SUB_DEAL_TYPE_COMMISSION_MONTHLY`       |
|     10 | `SUB_DEAL_TYPE_COMMISSION_AGENT_DAILY`   |
|     11 | `SUB_DEAL_TYPE_COMMISSION_AGENT_MONTHLY` |
|     12 | `SUB_DEAL_TYPE_INTEREST`                 |
|     13 | `SUB_DEAL_TYPE_BUY_CANCELED`             |
|     14 | `SUB_DEAL_TYPE_SELL_CANCELED`            |
|     15 | `SUB_DEAL_TYPE_DIVIDEND`                 |
|     16 | `SUB_DEAL_TYPE_DIVIDEND_FRANKED`         |
|     17 | `SUB_DEAL_TYPE_TAX`                      |

### `SUB_ENUM_DEAL_ENTRY`

| Number | Value                   |
| -----: | ----------------------- |
|      0 | `SUB_DEAL_ENTRY_IN`     |
|      1 | `SUB_DEAL_ENTRY_OUT`    |
|      2 | `SUB_DEAL_ENTRY_INOUT`  |
|      3 | `SUB_DEAL_ENTRY_OUT_BY` |

### `SUB_ENUM_DEAL_REASON`

| Number | Value                              |
| -----: | ---------------------------------- |
|      0 | `SUB_DEAL_REASON_CLIENT`           |
|      1 | `SUB_DEAL_REASON_MOBILE`           |
|      2 | `SUB_DEAL_REASON_WEB`              |
|      3 | `SUB_DEAL_REASON_EXPERT`           |
|      4 | `SUB_DEAL_REASON_SL`               |
|      5 | `SUB_DEAL_REASON_TP`               |
|      6 | `SUB_DEAL_REASON_SO`               |
|      7 | `SUB_DEAL_REASON_ROLLOVER`         |
|      8 | `SUB_DEAL_REASON_VMARGIN`          |
|      9 | `SUB_DEAL_REASON_SPLIT`            |
|     10 | `SUB_DEAL_REASON_CORPORATE_ACTION` |

---

### 🎯 Purpose

* Keep **orders/positions** and **account equity** synchronized in real time.
* Drive UI badges & logs: new orders, fills, closes, cancels, SL/TP hits.
* Trigger strategy reactions on **state changes** without extra polling.

### 🧩 Notes & Tips

* Use IDs (`ticket`, `position_id`) as primary keys for diff/merge in your state store.
* Lists are **additive per event** — process each group independently.
* Combine with `OpenedOrders` for a cold start snapshot, then switch to this stream.

---

## Usage Examples

### 1) Build an event counter

```python
stats = {"orders":0, "deals":0, "positions":0}
async for ev in acct.on_trade():
    d = ev.event_data
    stats["orders"] += len(d.new_orders) + len(d.state_changed_orders) + len(d.disappeared_orders)
    stats["deals"] += len(d.new_history_deals) + len(d.updated_history_deals) + len(d.disappeared_history_deals)
    stats["positions"] += len(d.new_positions) + len(d.updated_positions) + len(d.disappeared_positions)
```

### 2) React on filled orders only

```python
from MetaRpcMT5 import mt5_term_api_subscriptions_pb2 as sub_pb2

async for ev in acct.on_trade():
    for ch in ev.event_data.state_changed_orders:
        if ch.current_order.state == sub_pb2.SUB_ENUM_ORDER_STATE.SUB_ORDER_STATE_FILLED:
            print("filled:", ch.current_order.ticket)
```

### 3) Watch equity drift while streaming

```python
async for ev in acct.on_trade():
    print("Equity:", ev.account_info.equity)
```
