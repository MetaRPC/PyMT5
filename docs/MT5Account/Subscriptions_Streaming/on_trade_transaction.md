# ✅ On Trade Transaction

> **Request:** subscribe to **raw trade transactions** (like MQL5 `OnTradeTransaction`): each event carries the **transaction**, the original **request**, and the **result** returned by the trade server.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `on_trade_transaction(...)`
* `MetaRpcMT5/mt5_term_api_subscriptions_pb2.py` — `OnTradeTransaction*` messages and payloads; enums used here
* `MetaRpcMT5/mt5_term_api_subscriptions_pb2_grpc.py` — service stub `SubscriptionServiceStub`
* `MetaRpcMT5/mrpc_mt5_error_pb2.py` — `MqlErrorTradeCode` (for `trade_return_code`)

### RPC

* **Service:** `mt5_term_api.SubscriptionService`
* **Method:** `OnTradeTransaction(OnTradeTransactionRequest) → stream OnTradeTransactionReply`
* **Low-level client:** `SubscriptionServiceStub.OnTradeTransaction(request, metadata, timeout)` *(server‑streaming iterator)*
* **SDK wrapper:** `MT5Account.on_trade_transaction(cancellation_event=None) → async stream of OnTradeTransactionData`

---

### 🔗 Code Example

```python
# Minimal: print transaction type and ids
from MetaRpcMT5 import mt5_term_api_subscriptions_pb2 as sub_pb2

async for ev in acct.on_trade_transaction():
    tr = ev.trade_transaction
    print(tr.type, tr.order_ticket, tr.deal_ticket)
```

```python
# Cooperative cancellation after the first DEAL‑ADD
from MetaRpcMT5 import mt5_term_api_subscriptions_pb2 as sub_pb2
import asyncio

cancel = asyncio.Event()
async for ev in acct.on_trade_transaction(cancellation_event=cancel):
    tr = ev.trade_transaction
    if tr.type == sub_pb2.SUB_ENUM_TRADE_TRANSACTION_TYPE.TRADE_TRANSACTION_DEAL_ADD:
        print("deal added:", tr.deal_ticket, "price:", tr.price)
        cancel.set()
```

---

### Method Signature

```python
async def on_trade_transaction(
    self,
    cancellation_event: asyncio.Event | None = None,
) -> subscription_client.OnTradeTransaction  # async iterable of OnTradeTransactionData
```

---

## 💬 Just about the main thing

* **What it is.** A **low‑level event stream**: every trade server transaction as it happens — order add/update/delete, deal add, history add/update/delete, etc.
* **Why.** Perfect for accurate audit logs, reconciliation, and state machines that need **request+result** context per change.
* **Be careful.**

  * Stream is **infinite** until canceled via `cancellation_event`.
  * Timestamps are UTC; many structs have both `time` (Timestamp) and `time_msc` (ms since epoch).
  * Some transactions include only **ids** (e.g., order delete) — don’t assume full bodies are always present.

---

## 🔽 Input

| Parameter            | Type            | Description |                                         |   |
| -------------------- | --------------- | ----------- | --------------------------------------- | - |
| `cancellation_event` | \`asyncio.Event | None\`      | Cooperative stop for the streaming RPC. |   |

> **Request message:** `OnTradeTransactionRequest {}`

---

## ⬆️ Output

### Stream payload: `OnTradeTransactionData`

| Field                       | Proto Type                      | Description                                |
| --------------------------- | ------------------------------- | ------------------------------------------ |
| `type`                      | `MT5_SUB_ENUM_EVENT_GROUP_TYPE` | Event group marker.                        |
| `trade_transaction`         | `MqlTradeTransaction`           | The actual transaction (type + ids + ctx). |
| `trade_request`             | `MqlTradeRequest`               | The request that triggered it.             |
| `trade_result`              | `MqlTradeResult`                | Server result/retcode for the request.     |
| `terminal_instance_guid_id` | `string`                        | Source terminal GUID.                      |
| `account_info`              | `OnEventAccountInfo`            | Balance/Equity/Margins snapshot.           |

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

#### `MqlTradeTransaction`

|  # | Field                           | Type                              |
| -: | ------------------------------- | --------------------------------- |
|  1 | `deal_ticket`                   | `uint64`                          |
|  2 | `order_ticket`                  | `uint64`                          |
|  3 | `symbol`                        | `string`                          |
|  4 | `type`                          | `SUB_ENUM_TRADE_TRANSACTION_TYPE` |
|  5 | `order_type`                    | `SUB_ENUM_ORDER_TYPE`             |
|  6 | `order_state`                   | `SUB_ENUM_ORDER_STATE`            |
|  7 | `deal_type`                     | `SUB_ENUM_DEAL_TYPE`              |
|  8 | `order_time_type`               | `SUB_ENUM_ORDER_TYPE_TIME`        |
|  9 | `order_expiration_time`         | `google.protobuf.Timestamp`       |
| 10 | `price`                         | `double`                          |
| 11 | `price_trigger_stop_limit`      | `double`                          |
| 12 | `price_stop_loss`               | `double`                          |
| 13 | `price_take_profit`             | `double`                          |
| 14 | `volume`                        | `double`                          |
| 15 | `position_ticket`               | `uint64`                          |
| 16 | `position_by_opposite_position` | `uint64`                          |

#### `MqlTradeRequest`

|  # | Field                           | Type                             |
| -: | ------------------------------- | -------------------------------- |
|  1 | `trade_operation_type`          | `SUB_ENUM_TRADE_REQUEST_ACTIONS` |
|  2 | `magic`                         | `uint64`                         |
|  3 | `order_ticket`                  | `uint64`                         |
|  4 | `symbol`                        | `string`                         |
|  5 | `requested_deal_volume_lots`    | `double`                         |
|  6 | `price`                         | `double`                         |
|  7 | `stopl_imit`                    | `double`                         |
|  8 | `stop_loss`                     | `double`                         |
|  9 | `take_profit`                   | `double`                         |
| 10 | `deviation`                     | `uint32`                         |
| 11 | `order_type`                    | `SUB_ENUM_ORDER_TYPE`            |
| 12 | `order_type_filling`            | `SUB_ENUM_ORDER_TYPE_FILLING`    |
| 13 | `type_time`                     | `SUB_ENUM_ORDER_TYPE_TIME`       |
| 14 | `order_expiration_time`         | `google.protobuf.Timestamp`      |
| 15 | `order_comment`                 | `string`                         |
| 16 | `position_ticket`               | `uint64`                         |
| 17 | `position_by_opposite_position` | `uint64`                         |

#### `MqlTradeResult`

|  # | Field                          | Type                |
| -: | ------------------------------ | ------------------- |
|  1 | `trade_return_int_code`        | `uint32`            |
|  2 | `trade_return_code`            | `MqlErrorTradeCode` |
|  3 | `deal_ticket`                  | `uint64`            |
|  4 | `order_ticket`                 | `uint64`            |
|  5 | `deal_volume`                  | `double`            |
|  6 | `deal_price`                   | `double`            |
|  7 | `current_bid`                  | `double`            |
|  8 | `current_ask`                  | `double`            |
|  9 | `broker_comment_to_operation`  | `string`            |
| 10 | `terminal_dispatch_request_id` | `uint32`            |
| 11 | `return_code_external`         | `int32`             |

---

## Enums

### `SUB_ENUM_TRADE_TRANSACTION_TYPE`

| Number | Value                              | Meaning                   |
| -----: | ---------------------------------- | ------------------------- |
|      0 | `TRADE_TRANSACTION_ORDER_ADD`      | Order placed/appeared.    |
|      1 | `TRADE_TRANSACTION_ORDER_UPDATE`   | Order parameters changed. |
|      2 | `TRADE_TRANSACTION_ORDER_DELETE`   | Order removed.            |
|      3 | `TRADE_TRANSACTION_DEAL_ADD`       | Deal executed/added.      |
|      4 | `TRADE_TRANSACTION_HISTORY_ADD`    | History record added.     |
|      5 | `TRADE_TRANSACTION_HISTORY_UPDATE` | History record updated.   |
|      6 | `TRADE_TRANSACTION_HISTORY_DELETE` | History record deleted.   |


---

### 🎯 Purpose

* Build **accurate audit logs** and state machines that rely on **transaction granularity**.
* Associate **request → result** for every server action to diagnose rejections or partial fills.
* Trigger alerts on specific transaction types (e.g., `DEAL_ADD`, `ORDER_DELETE`).

### 🧩 Notes & Tips

* Transaction stream is verbose; keep handlers **non‑blocking** (fan‑out to queues/executors).
* Use ids (`order_ticket`, `deal_ticket`, `position_ticket`) as keys; avoid accidental dedupe.
* Pair with `on_trade` for high‑level deltas and `OpenedOrders` for cold‑start snapshot.

---

**See also:** [on\_trade.md](./on_trade.md), [order\_send.md](../Trading_Operations/order_send.md), [order\_modify.md](../Trading_Operations/order_modify.md)

## Usage Examples

### 1) Log every DEAL\_ADD with concise info

```python
from MetaRpcMT5 import mt5_term_api_subscriptions_pb2 as sub_pb2

async for ev in acct.on_trade_transaction():
    tr = ev.trade_transaction
    if tr.type == sub_pb2.SUB_ENUM_TRADE_TRANSACTION_TYPE.TRADE_TRANSACTION_DEAL_ADD:
        print(f"deal={tr.deal_ticket} {tr.symbol} vol={tr.volume} price={tr.price}")
```

### 2) Correlate request → result for diagnostics

```python
async for ev in acct.on_trade_transaction():
    rq, rs = ev.trade_request, ev.trade_result
    print("ret:", rs.trade_return_int_code, rs.trade_return_code, "order:", rq.order_ticket, rq.order_type)
```

### 3) Watch for deletes only

```python
from MetaRpcMT5 import mt5_term_api_subscriptions_pb2 as sub_pb2

async for ev in acct.on_trade_transaction():
    if ev.trade_transaction.type == sub_pb2.SUB_ENUM_TRADE_TRANSACTION_TYPE.TRADE_TRANSACTION_ORDER_DELETE:
        print("order removed:", ev.trade_transaction.order_ticket)
```
