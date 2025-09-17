# ✅ Order Check

> **Request:** dry‑run a **trade request** (market/pending/modify/close\_by) and get **required margin**, **free margin after**, and a **return code** — without actually placing anything.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `order_check(...)`
* `MetaRpcMT5/mt5_term_api_trade_functions_pb2.py` — `OrderCheck*`, `MrpcMqlTradeRequest`, `MrpcMqlTradeCheckResult`, enums: `MRPC_ENUM_TRADE_REQUEST_ACTIONS`, `ENUM_ORDER_TYPE_TF`, `MRPC_ENUM_ORDER_TYPE_FILLING`, `MRPC_ENUM_ORDER_TYPE_TIME`
* `MetaRpcMT5/mt5_term_api_trade_functions_pb2_grpc.py` — service stub `TradeFunctionsStub`

### RPC

* **Service:** `mt5_term_api.TradeFunctions`
* **Method:** `OrderCheck(OrderCheckRequest) → OrderCheckReply`
* **Low-level client:** `TradeFunctionsStub.OrderCheck(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.order_check(request, deadline=None, cancellation_event=None) → OrderCheckData`

---

### Method Signature

```python
async def order_check(
    self,
    request: trade_functions_pb2.OrderCheckRequest,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> trade_functions_pb2.OrderCheckData
```

---

## 💬 Just about the main thing

* **What is it.** Server‑side **pre‑validation** of a trade request (like MT5 `OrderCheck`): returns margins & a code.
* **Why.** Use it to **fail fast** in UI/strategies before `OrderSend` — avoid rejections and needless noise.
* **Be careful.**

  * You must build `MrpcMqlTradeRequest` correctly (action/type/volume/price/SL/TP/filling/time/etc.).
  * It **does not** place or modify anything — numbers are estimates for current market state.

### 🔗 Code Example

```python
# Minimal: check if a market BUY 0.10 is ok, with 20pt deviation
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf_pb2
from google.protobuf.timestamp_pb2 import Timestamp

rq = tf_pb2.MrpcMqlTradeRequest(
    action=tf_pb2.MRPC_ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_DEAL,
    symbol="EURUSD",
    volume=0.10,
    order_type=tf_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY,
    price=0.0,              # market; server will use current price
    deviation=20,
    type_filling=tf_pb2.MRPC_ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_IOC,
    type_time=tf_pb2.MRPC_ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC,
    comment="preflight",
)
res = await acct.order_check(tf_pb2.OrderCheckRequest(mql_trade_request=rq))
chk = res.mql_trade_check_result
print(chk.returned_code, chk.margin, chk.free_margin)  # numeric code + margins
```

```python
# Pending BUY_LIMIT with expiration today (SPECIFIED_DAY)
from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf_pb2

exp = Timestamp(); exp.FromDatetime(datetime.now(timezone.utc).replace(hour=21, minute=0, second=0, microsecond=0))

rq = tf_pb2.MrpcMqlTradeRequest(
    action=tf_pb2.MRPC_ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_PENDING,
    symbol="XAUUSD",
    volume=0.10,
    order_type=tf_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY_LIMIT,
    price=2300.00,
    stop_loss=2290.00,
    take_profit=2320.00,
    type_time=tf_pb2.MRPC_ENUM_ORDER_TYPE_TIME.ORDER_TIME_SPECIFIED_DAY,
    expiration=exp,
    comment="limit preflight",
)
res = await acct.order_check(tf_pb2.OrderCheckRequest(mql_trade_request=rq))
print(res.mql_trade_check_result.returned_code)
```
---

## 🔽 Input

| Parameter            | Type                               | Description                                   |   |
| -------------------- | ---------------------------------- | --------------------------------------------- | - |
| `request`            | `OrderCheckRequest` (**required**) | Wraps your `MrpcMqlTradeRequest` (see below). |   |
| `deadline`           | `datetime \| None`                 | Absolute per‑call deadline → timeout.         |   |
| `cancellation_event` | `asyncio.Event \| None`            | Cooperative cancel for the retry wrapper.     |   |

> **Request message:** `OrderCheckRequest { mql_trade_request: MrpcMqlTradeRequest }`

### Message: `MrpcMqlTradeRequest`

|  # | Field                         | Proto Type                             | Notes                                     |
| -: | ----------------------------- | -------------------------------------- | ----------------------------------------- |
|  1 | `action`                      | `enum MRPC_ENUM_TRADE_REQUEST_ACTIONS` | DEAL/PENDING/SLTP/MODIFY/REMOVE/CLOSE\_BY |
|  2 | `expert_advisor_magic_number` | `uint64`                               | Magic/EA id                               |
|  3 | `order`                       | `uint64`                               | Order ticket (when applicable)            |
|  4 | `symbol`                      | `string`                               | Symbol name                               |
|  5 | `volume`                      | `double`                               | Lots                                      |
|  6 | `price`                       | `double`                               | Entry/close price; `0.0` for market       |
|  7 | `stop_limit`                  | `double`                               | Stop‑limit trigger (for \*\_STOP\_LIMIT)  |
|  8 | `stop_loss`                   | `double`                               | SL                                        |
|  9 | `take_profit`                 | `double`                               | TP                                        |
| 10 | `deviation`                   | `uint64`                               | Max deviation in **points** (market ops)  |
| 11 | `order_type`                  | `enum ENUM_ORDER_TYPE_TF`              | BUY/SELL/LIMIT/STOP/STOP\_LIMIT/CLOSE\_BY |
| 12 | `type_filling`                | `enum MRPC_ENUM_ORDER_TYPE_FILLING`    | FOK/IOC/RETURN/BOC                        |
| 13 | `type_time`                   | `enum MRPC_ENUM_ORDER_TYPE_TIME`       | GTC/DAY/SPECIFIED/SPECIFIED\_DAY          |
| 14 | `expiration`                  | `google.protobuf.Timestamp`            | Expiration (UTC)                          |
| 15 | `comment`                     | `string`                               | Optional note                             |
| 16 | `position`                    | `uint64`                               | Position ticket (when applicable)         |
| 17 | `position_by`                 | `uint64`                               | Close‑by ticket                           |

---

## ⬆️ Output

### Payload: `OrderCheckData`

| Field                    | Proto Type                | Description         |
| ------------------------ | ------------------------- | ------------------- |
| `mql_trade_check_result` | `MrpcMqlTradeCheckResult` | Result bundle below |

#### Message: `MrpcMqlTradeCheckResult`

|  # | Field                | Proto Type | Description                                             |
| -: | -------------------- | ---------: | ------------------------------------------------------- |
|  1 | `returned_code`      |   `uint32` | Numeric return code (0 = ok; non‑zero → error/warning). |
|  2 | `balance_after_deal` |   `double` | Balance projected **after** execution.                  |
|  3 | `equity_after_deal`  |   `double` | Equity projected **after** execution.                   |
|  4 | `profit`             |   `double` | Expected P/L (may be 0 for opens).                      |
|  5 | `margin`             |   `double` | Required margin for this request.                       |
|  6 | `free_margin`        |   `double` | Free margin projected **after** execution.              |
|  7 | `margin_level`       |   `double` | Margin level **%** after execution.                     |
|  8 | `comment`            |   `string` | Text explanation from server.                           |

> **Wire reply:** `OrderCheckReply { data: OrderCheckData, error: Error? }`
> SDK returns `reply.data`.

---

## Enums

### `MRPC_ENUM_TRADE_REQUEST_ACTIONS`

| Number | Value                   | Meaning                        |
| -----: | ----------------------- | ------------------------------ |
|      0 | `TRADE_ACTION_DEAL`     | Market operation (open/close). |
|      1 | `TRADE_ACTION_PENDING`  | Place/alter pending order.     |
|      2 | `TRADE_ACTION_SLTP`     | SL/TP change.                  |
|      3 | `TRADE_ACTION_MODIFY`   | Generic modify.                |
|      4 | `TRADE_ACTION_REMOVE`   | Remove pending.                |
|      5 | `TRADE_ACTION_CLOSE_BY` | Close by opposite position.    |

### `ENUM_ORDER_TYPE_TF`

| Number | Value                           |
| -----: | ------------------------------- |
|      0 | `ORDER_TYPE_TF_BUY`             |
|      1 | `ORDER_TYPE_TF_SELL`            |
|      2 | `ORDER_TYPE_TF_BUY_LIMIT`       |
|      3 | `ORDER_TYPE_TF_SELL_LIMIT`      |
|      4 | `ORDER_TYPE_TF_BUY_STOP`        |
|      5 | `ORDER_TYPE_TF_SELL_STOP`       |
|      6 | `ORDER_TYPE_TF_BUY_STOP_LIMIT`  |
|      7 | `ORDER_TYPE_TF_SELL_STOP_LIMIT` |
|      8 | `ORDER_TYPE_TF_CLOSE_BY`        |

### `MRPC_ENUM_ORDER_TYPE_FILLING`

| Number | Value                  |
| -----: | ---------------------- |
|      0 | `ORDER_FILLING_FOK`    |
|      1 | `ORDER_FILLING_IOC`    |
|      3 | `ORDER_FILLING_BOC`    |
|      2 | `ORDER_FILLING_RETURN` |

### `MRPC_ENUM_ORDER_TYPE_TIME`

| Number | Value                      |
| -----: | -------------------------- |
|      0 | `ORDER_TIME_GTC`           |
|      1 | `ORDER_TIME_DAY`           |
|      2 | `ORDER_TIME_SPECIFIED`     |
|      3 | `ORDER_TIME_SPECIFIED_DAY` |

---

### 🎯 Purpose

* Pre‑flight validation for **OrderSend/OrderModify** in UI and algos.
* Show **required margin/free margin after** before committing.
* Explain failures to users via `returned_code` + `comment`.

### 🧩 Notes & Tips

* Use `symbol_info_margin_rate`/`symbol_info_double(SYMBOL_TRADE_CONTRACT_SIZE)` to cross‑check expectations.
* Always set `type_filling`/`type_time` deliberately; brokers differ.

---

## Usage Examples

### 1) Check partial close feasibility

```python
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf_pb2
rq = tf_pb2.MrpcMqlTradeRequest(
    action=tf_pb2.MRPC_ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_DEAL,
    symbol="EURUSD",
    volume=0.05,
    order_type=tf_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_SELL,  # closing BUY position
    price=0.0,
    deviation=15,
)
res = await acct.order_check(tf_pb2.OrderCheckRequest(mql_trade_request=rq))
print(res.mql_trade_check_result.free_margin)
```

### 2) Validate SL/TP modification

```python
rq = tf_pb2.MrpcMqlTradeRequest(
    action=tf_pb2.MRPC_ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_SLTP,
    symbol="XAUUSD",
    stop_loss=2288.0,
    take_profit=2325.0,
)
res = await acct.order_check(tf_pb2.OrderCheckRequest(mql_trade_request=rq))
print(res.mql_trade_check_result.returned_code, res.mql_trade_check_result.comment)
```

### 3) Pending STOP\_LIMIT with stop trigger

```python
rq = tf_pb2.MrpcMqlTradeRequest(
    action=tf_pb2.MRPC_ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_PENDING,
    symbol="BTCUSD",
    volume=0.03,
    order_type=tf_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY_STOP_LIMIT,
    price=65000.0,          # limit price
    stop_limit=64950.0,     # stop trigger
)
res = await acct.order_check(tf_pb2.OrderCheckRequest(mql_trade_request=rq))
print(res.mql_trade_check_result.margin)
```
