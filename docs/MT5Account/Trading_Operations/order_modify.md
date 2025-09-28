# ✅ Order Modify

> **Request:** modify an existing **order/position** (SL/TP, price, expiration, stop‑limit trigger).

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `order_modify(...)`
* `MetaRpcMT5/mt5_term_api_trading_helper_pb2.py` — `OrderModify*` messages (`OrderModifyRequest`, `OrderModifyReply`, `OrderModifyData`) and enum `TMT5_ENUM_ORDER_TYPE_TIME`
* `MetaRpcMT5/mt5_term_api_trading_helper_pb2_grpc.py` — service stub `TradingHelperStub`

---

### RPC

* **Service:** `mt5_term_api.TradingHelper`
* **Method:** `OrderModify(OrderModifyRequest) → OrderModifyReply`
* **Low-level client:** `TradingHelperStub.OrderModify(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.order_modify(request, deadline=None, cancellation_event=None)` → returns `OrderModifyData`

---

### Method Signature

```python
async def order_modify(
    self,
    request: trading_helper_pb2.OrderModifyRequest,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> trading_helper_pb2.OrderModifyData
```

## 💬 Plain English

* **What it is.** One call to adjust **SL/TP**, **pending price**, **expiration** (GTC/DAY/SPECIFIED/SPECIFIED\_DAY), and **stop‑limit** trigger.
* **Why you care.** Lightweight edit without cancel+recreate; returns updated **order/deal** references and server **return code**.
* **Mind the traps.**

  * `ticket` must reference the target **order or position**.
  * Pending orders: set a non‑zero `price` when changing the entry price.
  * For `*_STOP_LIMIT` use `stop_limit` to set the stop trigger
 
  ---

## 🔽 Input

### Message: `OrderModifyRequest`

|  # | Field                  | Proto Type                       | Required | Description                                    |
| -: | ---------------------- | -------------------------------- | :------: | ---------------------------------------------- |
|  1 | `ticket`               | `uint64`                         |    yes   | Ticket of order/position to modify.            |
|  2 | `stop_loss`            | `double`                         |    no    | New SL price (0.0 to keep unchanged).          |
|  3 | `take_profit`          | `double`                         |    no    | New TP price (0.0 to keep unchanged).          |
|  4 | `price`                | `double`                         |    no    | New price for **pending** orders; 0.0 to keep. |
|  5 | `expiration_time_type` | `enum TMT5_ENUM_ORDER_TYPE_TIME` |    no    | GTC/DAY/SPECIFIED/SPECIFIED\_DAY.              |
|  6 | `expiration_time`      | `google.protobuf.Timestamp`      | when set | Expiration instant (UTC).                      |
|  8 | `stop_limit`           | `double`                         |    no    | Stop trigger for **STOP\_LIMIT** orders.       |

> **Request message:** `OrderModifyRequest { ticket, stop_loss, take_profit, price, expiration_time_type, expiration_time, stop_limit }`

---

## ⬆️ Output

### Message: `OrderModifyData`

|  # | Field                       | Proto Type | Description                            |
| -: | --------------------------- | ---------: | -------------------------------------- |
|  1 | `returned_code`             |   `uint32` | Server return code (numeric).          |
|  2 | `deal`                      |   `uint64` | Deal ticket (if a deal was generated). |
|  3 | `order`                     |   `uint64` | Order ticket (affected).               |
|  4 | `volume`                    |   `double` | Affected volume.                       |
|  5 | `price`                     |   `double` | Effective price used.                  |
|  6 | `bid`                       |   `double` | Bid at processing time.                |
|  7 | `ask`                       |   `double` | Ask at processing time.                |
|  8 | `comment`                   |   `string` | Server comment.                        |
|  9 | `request_id`                |   `uint32` | Request identifier.                    |
| 10 | `ret_code_external`         |    `int32` | External/bridge code if provided.      |
| 11 | `returned_string_code`      |   `string` | Return code (string).                  |
| 12 | `returned_code_description` |   `string` | Human‑readable description of result.  |

> **Wire reply:** `OrderModifyReply { data: OrderModifyData, error: Error? }`
> SDK returns `reply.data`.

---

## Enum: `TMT5_ENUM_ORDER_TYPE_TIME`

| Number | Value                           |
| -----: | ------------------------------- |
|      0 | `TMT5_ORDER_TIME_GTC`           |
|      1 | `TMT5_ORDER_TIME_DAY`           |
|      2 | `TMT5_ORDER_TIME_SPECIFIED`     |
|      3 | `TMT5_ORDER_TIME_SPECIFIED_DAY` |

---

### 🎯 Purpose

* Adjust protective levels and pending parameters **in place**.
* Drive order‑ticket edits in UI with precise return codes and IDs.

### 🧩 Notes & Tips

* Use `symbol_info_integer(SYMBOL_TRADE_STOPS_LEVEL)` and freeze levels to validate SL/TP distances **before** modify.
* For positions vs pending orders, your UI should adapt fields (no `price` for market positions).
* Combine with `order_send` and `order_close` for full trade lifecycle.

**See also:** [order\_send.md](./order_send.md), [order\_close.md](./order_close.md), [on\_trade\_transaction.md](../Subscriptions_Streaming/on_trade_transaction.md)

### 🔗 Code Example

```python
# Example 1: Only change SL/TP on an existing ticket
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2

req = th_pb2.OrderModifyRequest(
    ticket=1234567890,
    stop_loss=1.07200,
    take_profit=1.07800,
    price=0.0,  # leave unchanged for market/position
    expiration_time_type=th_pb2.TMT5_ENUM_ORDER_TYPE_TIME.TMT5_ORDER_TIME_GTC,
)
res = await acct.order_modify(req)
print(res.returned_string_code, res.order)
```

```python
# Example 2: Modify pending order price and expiration (DAY)
from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2

expire = Timestamp(); expire.FromDatetime(datetime.now(timezone.utc).replace(hour=21, minute=0, second=0, microsecond=0))

req = th_pb2.OrderModifyRequest(
    ticket=222333444,
    price=1.23450,
    stop_loss=1.23300,
    take_profit=1.23900,
    expiration_time_type=th_pb2.TMT5_ENUM_ORDER_TYPE_TIME.TMT5_ORDER_TIME_SPECIFIED,
    expiration_time=expire,
)
res = await acct.order_modify(req)
print(res.order, res.returned_code_description)
```

```python
# Example 3: Stop‑limit pending order — adjust stop trigger
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2

req = th_pb2.OrderModifyRequest(
    ticket=987654321,
    stop_limit=64950.0,  # stop trigger for *_STOP_LIMIT orders
    expiration_time_type=th_pb2.TMT5_ENUM_ORDER_TYPE_TIME.TMT5_ORDER_TIME_GTC,
)
res = await acct.order_modify(req)
print(res.returned_code)
```
