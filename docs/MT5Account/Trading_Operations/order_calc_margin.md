# ✅ Order Calc Margin

> **Request:** calculate the **required margin** for a hypothetical order (market or pending) — **without placing** it.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `order_calc_margin(...)`
* `MetaRpcMT5/mt5_term_api_trade_functions_pb2.py` — `OrderCalcMargin*` messages (`OrderCalcMarginRequest`, `OrderCalcMarginReply`, `OrderCalcMarginData`) and enum `ENUM_ORDER_TYPE_TF`
* `MetaRpcMT5/mt5_term_api_trade_functions_pb2_grpc.py` — service stub `TradeFunctionsStub`

---

### RPC

* **Service:** `mt5_term_api.TradeFunctions`
* **Method:** `OrderCalcMargin(OrderCalcMarginRequest) → OrderCalcMarginReply`
* **Low-level client:** `TradeFunctionsStub.OrderCalcMargin(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.order_calc_margin(request, deadline=None, cancellation_event=None) → OrderCalcMarginData`

---

### 🔗 Code Example

```python
# Minimal canonical example: margin for BUY 0.10 @ market
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf_pb2

req = tf_pb2.OrderCalcMarginRequest(
    order_type=tf_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY,
    symbol="EURUSD",
    volume=0.10,
    open_price=0.0,  # market: server uses current price
)
res = await acct.order_calc_margin(req)
print(res.margin)
```

```python
# Pending BUY_LIMIT at a specific price
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf_pb2

req = tf_pb2.OrderCalcMarginRequest(
    order_type=tf_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY_LIMIT,
    symbol="XAUUSD",
    volume=0.05,
    open_price=2300.00,
)
res = await acct.order_calc_margin(req)
print("required margin:", res.margin)
```

---

### Method Signature

```python
async def order_calc_margin(
    self,
    request: trade_functions_pb2.OrderCalcMarginRequest,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> trade_functions_pb2.OrderCalcMarginData
```

---

## 💬 Just about the main thing

* **What is it.** Server‑side calculation of **required margin** for an order you *could* place.
* **Why.** Show margin requirements in order tickets and in strategies **before** sending.
* **Be careful.**

  * `order_type` controls direction & kind (BUY/SELL/LIMIT/STOP/STOP\_LIMIT/etc.).
  * For market scenarios, `open_price=0.0` is fine — server uses current price; for pendings, pass the **entry price**.
  * The result is sensitive to account type, leverage, symbol settings, and current quotes.
* **When to call.** Right before `OrderSend`, or when a user edits **volume** or **price** in the ticket.
* **Quick check.** You should get `OrderCalcMarginData` with a single `margin: double`.

---

## 🔽 Input

### Message: `OrderCalcMarginRequest`

|  # | Field        | Proto Type                | Required | Description                                       |
| -: | ------------ | ------------------------- | :------: | ------------------------------------------------- |
|  1 | `order_type` | `enum ENUM_ORDER_TYPE_TF` |    yes   | BUY/SELL/*\_LIMIT/*\_STOP/\*\_STOP\_LIMIT/etc.    |
|  2 | `symbol`     | `string`                  |    yes   | Symbol name.                                      |
|  3 | `volume`     | `double`                  |    yes   | Volume in lots.                                   |
|  4 | `open_price` | `double`                  |    yes   | `0.0` for market; entry price for pending orders. |

> **Request message:** `OrderCalcMarginRequest { order_type, symbol, volume, open_price }`

---

## ⬆️ Output

### Message: `OrderCalcMarginData`

|  # | Field    | Proto Type | Description                            |
| -: | -------- | ---------: | -------------------------------------- |
|  1 | `margin` |   `double` | Required margin for the given request. |

> **Wire reply:** `OrderCalcMarginReply { data: OrderCalcMarginData, error: Error? }`
> SDK returns `reply.data`.

---

## Enum: `ENUM_ORDER_TYPE_TF`

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

---

### 🎯 Purpose

* Display margin requirements in order tickets.
* Validate user volumes against available free margin.
* What‑if analysis in risk dashboards.

### 🧩 Notes & Tips

* For detailed feasibility (free margin after / retcode), see `OrderCheck`.
* Combine with `symbol_info_margin_rate` and `symbol_info_double(SYMBOL_TRADE_CONTRACT_SIZE)` for cross‑checks.
* Market vs pending pricing can change results — recalc after price edits.

---

**See also:** [symbol\_info\_margin\_rate.md](../Symbols_and_Market/symbol_info_margin_rate.md), [order\_check.md](./order_check.md), [symbol\_info\_double.md](../Symbols_and_Market/symbol_info_double.md)

## Usage Examples

### 1) Quick UI ticket calculation

```python
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf_pb2

req = tf_pb2.OrderCalcMarginRequest(
    order_type=tf_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_SELL,
    symbol="BTCUSD",
    volume=0.02,
    open_price=0.0,
)
print((await acct.order_calc_margin(req)).margin)
```

### 2) Pending limit at user price

```python
req = tf_pb2.OrderCalcMarginRequest(
    order_type=tf_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_SELL_LIMIT,
    symbol="EURUSD",
    volume=1.0,
    open_price=1.12345,
)
res = await acct.order_calc_margin(req)
print(res.margin)
```

### 3) Refresh on every change (volume/price)

```python
async def calc(symbol, order_type, volume, price):
    from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf_pb2
    req = tf_pb2.OrderCalcMarginRequest(order_type=order_type, symbol=symbol, volume=volume, open_price=price)
    return (await acct.order_calc_margin(req)).margin
```
