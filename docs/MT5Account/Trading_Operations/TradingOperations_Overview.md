# MT5Account · Trading\_Operations — Overview

> Quick map of the **trading ops** APIs: send/modify/close orders, pre‑flight checks, and margin calc. Use this page to pick the right call fast.

## 📁 What lives here

* **[order\_send](./order_send.md)** — place **market** or **pending** orders; returns deal/order IDs & return code.
* **[order\_modify](./order_modify.md)** — edit **SL/TP**, **pending price**, **expiration**, **stop‑limit** trigger.
* **[order\_close](./order_close.md)** — **close** a position (full/partial) or **cancel** a pending order.
* **[order\_check](./order_check.md)** — **dry‑run** a trade request → return code + projected margins.
* **[order\_calc\_margin](./order_calc_margin.md)** — compute **required margin** for a hypothetical order.

---

## 🧭 Plain English

* **order\_send** → the **“place it”** button.
* **order\_modify** → the **“edit ticket”** wrench.
* **order\_close** → the **“exit/cancel”** switch.
* **order\_check** → the **“preflight”**: will it pass? how much margin after?
* **order\_calc\_margin** → the **“what‑if margin”** calculator for a single order.

> Rule of thumb: need to **know before you place** → `order_check` / `order_calc_margin`. Ready to **act** → `order_send` / `order_modify` / `order_close`.

---

## Quick choose

| If you need…                              | Use                 | Returns               | Key inputs (enums)                                                                                                                                                    |
| ----------------------------------------- | ------------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Place market/pending order                | `order_send`        | `OrderSendData`       | `symbol`, `operation:TMT5_ENUM_ORDER_TYPE`, `volume`, `price`, `slippage`, `SL/TP`, `expiration_time_type:TMT5_ENUM_ORDER_TYPE_TIME`, `expiration`                    |
| Edit SL/TP, price, expiration, stop‑limit | `order_modify`      | `OrderModifyData`     | `ticket`, `stop_loss`, `take_profit`, `price`, `stop_limit`, `expiration_time_type`, `expiration`                                                                     |
| Close position / cancel pending           | `order_close`       | `OrderCloseData`      | `ticket`, `volume` (optional), `price` (0.0 → market), `slippage`, `comment`                                                                                          |
| Pre‑flight: return code & margins         | `order_check`       | `OrderCheckData`      | `MrpcMqlTradeRequest{ action:MRPC_ENUM_TRADE_REQUEST_ACTIONS, order_type:ENUM_ORDER_TYPE_TF, symbol, volume, price, deviation, type_filling, type_time, expiration }` |
| Required margin for a hypothetical order  | `order_calc_margin` | `OrderCalcMarginData` | `order_type:ENUM_ORDER_TYPE_TF`, `symbol`, `volume`, `price`                                                                                                          |

---

## ❌ Cross‑refs & gotchas

* **Market vs pending.** Market ops usually use `price=0.0` + `slippage`. Pending ops require a **price** (and `stop_limit` for \*\_STOP\_LIMIT).
* **UTC timestamps** for expirations. Choose `*_TIME_*` enums deliberately (GTC/DAY/SPECIFIED/SPECIFIED\_DAY).
* **Filling modes** matter (FOK/IOC/RETURN/BOC) in `order_send` and `order_check` — brokers differ.
* **Return codes.** All trading ops return numeric + string codes; render user‑friendly messages in UI.
* For partial closes, ensure lot **step/min** via symbol params before calling `order_close`.

---

## 🟢 Minimal snippets

```python
# order_send — market BUY 0.10 with slippage
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2
req = th_pb2.OrderSendRequest(symbol="EURUSD", operation=th_pb2.TMT5_ENUM_ORDER_TYPE.TMT5_ORDER_TYPE_BUY, volume=0.10, price=0.0, slippage=20, expiration_time_type=th_pb2.TMT5_ENUM_ORDER_TYPE_TIME.TMT5_ORDER_TIME_GTC)
res = await acct.order_send(req); print(res.deal, res.returned_string_code)
```

```python
# order_modify — adjust SL/TP
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2
req = th_pb2.OrderModifyRequest(ticket=1234567890, stop_loss=1.07200, take_profit=1.07800, expiration_time_type=th_pb2.TMT5_ENUM_ORDER_TYPE_TIME.TMT5_ORDER_TIME_GTC)
print((await acct.order_modify(req)).returned_string_code)
```

```python
# order_close — partial close at market
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2
req = th_pb2.OrderCloseRequest(ticket=1234567890, volume=0.05, price=0.0, slippage=15)
print((await acct.order_close(req)).deal)
```

```python
# order_check — preflight for BUY_LIMIT
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf_pb2
rq = tf_pb2.MrpcMqlTradeRequest(action=tf_pb2.MRPC_ENUM_TRADE_REQUEST_ACTIONS.TRADE_ACTION_PENDING, order_type=tf_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY_LIMIT, symbol="XAUUSD", volume=0.10, price=2300.0)
print((await acct.order_check(tf_pb2.OrderCheckRequest(mql_trade_request=rq))).mql_trade_check_result.margin)
```

```python
# order_calc_margin — what-if margin for SELL @ market
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf_pb2
req = tf_pb2.OrderCalcMarginRequest(order_type=tf_pb2.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_SELL, symbol="BTCUSD", volume=0.02, price=0.0)
print((await acct.order_calc_margin(req)).margin)
```
