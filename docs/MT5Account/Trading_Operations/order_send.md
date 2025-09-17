# ✅ Order Send

> **Request:** send a **market or pending order** to the trading server.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `order_send(...)`
* `MetaRpcMT5/mt5_term_api_trading_helper_pb2.py` — `OrderSend*` messages (`OrderSendRequest`, `OrderSendReply`, `OrderSendData`) and enums `TMT5_ENUM_ORDER_TYPE`, `TMT5_ENUM_ORDER_TYPE_TIME`
* `MetaRpcMT5/mt5_term_api_trading_helper_pb2_grpc.py` — service stub `TradingHelperStub`

---

### RPC

* **Service:** `mt5_term_api.TradingHelper`
* **Method:** `OrderSend(OrderSendRequest) → OrderSendReply`
* **Low-level client:** `TradingHelperStub.OrderSend(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.order_send(request, deadline=None, cancellation_event=None)` → returns `OrderSendData`

---

### 🔗 Code Example

```python
# Example 1: Market BUY 0.10 — max slippage 10 points
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2

req = th_pb2.OrderSendRequest(
    symbol="EURUSD",
    operation=th_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY,
    volume=0.10,
    price=0.0,            # market orders: server will fill at current price
    slippage=10,          # max price deviation in points
    stop_loss=0.0,        # set if needed
    take_profit=0.0,      # set if needed
    comment="SDK demo",
    expert_id=0,
    expiration_time_type=th_pb2.TMT5_ENUM_ORDER_TYPE_TIME.TMT5_ORDER_TIME_GTC,
)
res = await acct.order_send(req)
print(res.returned_code, res.deal, res.order)
```

```python
# Example 2: Pending BUY_LIMIT with expiration today
from datetime import datetime, timezone, timedelta
from google.protobuf.timestamp_pb2 import Timestamp
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2

exp_ts = Timestamp()
exp_ts.FromDatetime(datetime.now(timezone.utc).replace(hour=21, minute=0, second=0, microsecond=0))

req = th_pb2.OrderSendRequest(
    symbol="XAUUSD",
    operation=th_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY_LIMIT,
    volume=0.10,
    price=2300.00,            # required for *LIMIT/*STOP orders
    slippage=0,               # not used for pending orders
    stop_loss=2290.00,
    take_profit=2320.00,
    comment="limit until 21:00",
    expert_id=42,
    expiration_time_type=th_pb2.TMT5_ENUM_ORDER_TYPE_TIME.TMT5_ORDER_TIME_SPECIFIED_DAY,
    expiration_time=exp_ts,
)
res = await acct.order_send(req)
print(res.order, res.returned_string_code)
```

---

### Method Signature

```python
async def order_send(
    self,
    request: trading_helper_pb2.OrderSendRequest,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> trading_helper_pb2.OrderSendData
```

---

## 💬 Plain English

* **What it is.** One call to place **market** or **pending** orders (incl. stop‑limit).
* **Why you care.** Returns a compact confirmation with **deal/order IDs** and server **return code**.
* **Mind the traps.**

  * For **market** orders, `price` can be `0.0`; server uses current price; `slippage` limits deviation.
  * For **pending** orders (`*_LIMIT`/`*_STOP`/`*_STOP_LIMIT`), you **must** set `price` (and `stop_limit_price` for stop‑limit).
  * `expiration_time_type` controls GTC/DAY/SPECIFIED/SPECIFIED\_DAY; set `expiration_time` accordingly.
  * All times are UTC (`google.protobuf.Timestamp`).

---

## 🔽 Input

### Message: `OrderSendRequest`

|  # | Field                  | Proto Type                       | Required | Description                                            |
| -: | ---------------------- | -------------------------------- | :------: | ------------------------------------------------------ |
|  1 | `symbol`               | `string`                         |    yes   | Symbol name.                                           |
|  2 | `operation`            | `enum TMT5_ENUM_ORDER_TYPE`      |    yes   | Order type (see enum).                                 |
|  3 | `volume`               | `double`                         |    yes   | Volume in lots.                                        |
|  4 | `price`                | `double`                         |  market? | Price for pending orders; `0.0` for market.            |
|  5 | `slippage`             | `uint64`                         |  market? | Max deviation (points) for market orders.              |
|  6 | `stop_loss`            | `double`                         |    no    | SL price.                                              |
|  7 | `take_profit`          | `double`                         |    no    | TP price.                                              |
|  8 | `comment`              | `string`                         |    no    | Client comment.                                        |
|  9 | `expert_id`            | `uint64`                         |    no    | Magic/EA ID.                                           |
| 10 | `stop_limit_price`     | `double`                         |  when SL | Price of the stop‑limit trigger (for \*\_STOP\_LIMIT). |
| 11 | `expiration_time_type` | `enum TMT5_ENUM_ORDER_TYPE_TIME` |    yes   | GTC/DAY/SPECIFIED/SPECIFIED\_DAY.                      |
| 12 | `expiration_time`      | `google.protobuf.Timestamp`      | when set | Expiration instant (UTC).                              |

> **Request message:** `OrderSendRequest { symbol, operation, volume, price, slippage, stop_loss, take_profit, comment, expert_id, stop_limit_price, expiration_time_type, expiration_time }`

---

## ⬆️ Output

### Message: `OrderSendData`

|  # | Field                       | Proto Type | Description                       |
| -: | --------------------------- | ---------: | --------------------------------- |
|  1 | `returned_code`             |   `uint32` | Server return code (numeric).     |
|  2 | `deal`                      |   `uint64` | Deal ticket (for market fills).   |
|  3 | `order`                     |   `uint64` | Order ticket (created/placed).    |
|  4 | `volume`                    |   `double` | Executed or placed volume.        |
|  5 | `price`                     |   `double` | Executed/placed price.            |
|  6 | `bid`                       |   `double` | Server bid at processing time.    |
|  7 | `ask`                       |   `double` | Server ask at processing time.    |
|  8 | `comment`                   |   `string` | Server comment.                   |
|  9 | `request_id`                |   `uint32` | Request identifier.               |
| 10 | `ret_code_external`         |    `int32` | External/bridge code if provided. |
| 11 | `returned_string_code`      |   `string` | Return code (string).             |
| 12 | `returned_code_description` |   `string` | Human‑readable description.       |

> **Wire reply:** `OrderSendReply { data: OrderSendData, error: Error? }`
> SDK returns `reply.data`.

---

## Enum: `TMT5_ENUM_ORDER_TYPE`

| Number | Value                             |
| -----: | --------------------------------- |
|      0 | `TMT5_ORDER_TYPE_BUY`             |
|      1 | `TMT5_ORDER_TYPE_SELL`            |
|      2 | `TMT5_ORDER_TYPE_BUY_LIMIT`       |
|      3 | `TMT5_ORDER_TYPE_SELL_LIMIT`      |
|      4 | `TMT5_ORDER_TYPE_BUY_STOP`        |
|      5 | `TMT5_ORDER_TYPE_SELL_STOP`       |
|      6 | `TMT5_ORDER_TYPE_BUY_STOP_LIMIT`  |
|      7 | `TMT5_ORDER_TYPE_SELL_STOP_LIMIT` |
|      8 | `TMT5_ORDER_TYPE_CLOSE_BY`        |

## Enum: `TMT5_ENUM_ORDER_TYPE_TIME`

| Number | Value                           |
| -----: | ------------------------------- |
|      0 | `TMT5_ORDER_TIME_GTC`           |
|      1 | `TMT5_ORDER_TIME_DAY`           |
|      2 | `TMT5_ORDER_TIME_SPECIFIED`     |
|      3 | `TMT5_ORDER_TIME_SPECIFIED_DAY` |

---

### 🎯 Purpose

* Submit orders programmatically with precise control over **type**, **volume**, **price**, **SL/TP**, and **expiration**.
* Drive order tickets in UI and support strategy order placement.

### 🧩 Notes & Tips

* **Pending vs market:** Pending orders require `price`; market orders typically use `price=0.0` + `slippage`.
* **Stop‑limit:** For `*_STOP_LIMIT`, set both `price` and `stop_limit_price`.
* **Return codes:** Use `returned_code`/`returned_string_code`/`returned_code_description` to render user‑friendly results.
* Pair with `symbol_is_synchronized` & `symbol_select` to avoid stale data issues before sending.

---

**See also:** [order\_check.md](./order_check.md), [order\_modify.md](./order_modify.md), [order\_close.md](./order_close.md)

## Usage Examples

### 1) Simple market BUY with SL/TP

```python
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2

req = th_pb2.OrderSendRequest(
    symbol="EURUSD",
    operation=th_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY,
    volume=0.10,
    price=0.0,
    slippage=20,
    stop_loss=0.0,
    take_profit=0.0,
    comment="buy@market",
    expert_id=1001,
    expiration_time_type=th_pb2.TMT5_ENUM_ORDER_TYPE_TIME.TMT5_ORDER_TIME_GTC,
)
res = await acct.order_send(req)
print("deal:", res.deal, "ret:", res.returned_string_code)
```

### 2) Stop‑limit example

```python
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2

req = th_pb2.OrderSendRequest(
    symbol="BTCUSD",
    operation=th_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY_STOP_LIMIT,
    volume=0.05,
    price=65000.0,        # limit price
    stop_limit_price=64950.0,  # stop trigger
    slippage=0,
    comment="stop-limit demo",
    expiration_time_type=th_pb2.TMT5_ENUM_ORDER_TYPE_TIME.TMT5_ORDER_TIME_DAY,
)
res = await acct.order_send(req)
print(res.order)
```

### 3) Expire at specific UTC time

```python
from datetime import datetime, timezone
from google.protobuf.timestamp_pb2 import Timestamp
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2

ts = Timestamp(); ts.FromDatetime(datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0))
req = th_pb2.OrderSendRequest(
    symbol="XAUUSD",
    operation=th_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_SELL_LIMIT,
    volume=0.1,
    price=2310.0,
    slippage=0,
    expiration_time_type=th_pb2.TMT5_ENUM_ORDER_TYPE_TIME.TMT5_ORDER_TIME_SPECIFIED,
    expiration_time=ts,
)
res = await acct.order_send(req)
print(res.order, res.returned_code_description)
```
