# ✅ Symbol Info Margin Rate

> **Request:** get **margin rates** for a **symbol** given an **order type** (BUY/SELL). Returns **initial** and **maintenance** rates.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_info_margin_rate(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolInfoMarginRate*` messages (`SymbolInfoMarginRateRequest`, `SymbolInfoMarginRateReply`, `SymbolInfoMarginRateData`) and enum `ENUM_ORDER_TYPE`
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoMarginRate(SymbolInfoMarginRateRequest) → SymbolInfoMarginRateReply`
* **Low-level client:** `MarketInfoStub.SymbolInfoMarginRate(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_info_margin_rate(symbol, order_type, deadline=None, cancellation_event=None)` → returns `SymbolInfoMarginRateData`

---

### 🔗 Code Example

```python
# Ask margin rates for placing a BUY order
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

rates = await acct.symbol_info_margin_rate(
    "EURUSD",
    mi_pb2.ENUM_ORDER_TYPE.ORDER_TYPE_BUY,
)
print(rates.initial_margin_rate, rates.maintenance_margin_rate)
```

```python
# Compare BUY vs SELL
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

buy = await acct.symbol_info_margin_rate("XAUUSD", mi_pb2.ENUM_ORDER_TYPE.ORDER_TYPE_BUY)
sell = await acct.symbol_info_margin_rate("XAUUSD", mi_pb2.ENUM_ORDER_TYPE.ORDER_TYPE_SELL)
print("BUY initial:", buy.initial_margin_rate, "SELL initial:", sell.initial_margin_rate)
```

---

### Method Signature

```python
async def symbol_info_margin_rate(
    self,
    symbol: str,
    order_type: market_info_pb2.ENUM_ORDER_TYPE,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolInfoMarginRateData
```

---

## 💬 Plain English

* **What it is.** Server-calculated **margin rates** (initial & maintenance) for a symbol under a specific **order type**.
* **Why you care.** Use these to estimate **required margin** before placing orders or sizing positions.
* **Mind the traps.**

  * Rates are **broker/symbol specific** and can vary by **order type** (BUY vs SELL) and account settings.
  * Returned values are **rates**, not absolute money — multiply by contract/price to project margin.

---

## 🔽 Input

| Parameter            | Type                             | Description                                       |                                                    |
| -------------------- | -------------------------------- | ------------------------------------------------- | -------------------------------------------------- |
| `symbol`             | `str` (**required**)             | Symbol name.                                      |                                                    |
| `order_type`         | `ENUM_ORDER_TYPE` (**required**) | BUY/SELL/etc. context for which to compute rates. |                                                    |
| `deadline`           | \`datetime                       | None\`                                            | Absolute per‑call deadline → converted to timeout. |
| `cancellation_event` | \`asyncio.Event                  | None\`                                            | Cooperative cancel for the retry wrapper.          |

> **Request message:** `SymbolInfoMarginRateRequest { symbol: string, order_type: ENUM_ORDER_TYPE }`

---

## ⬆️ Output

### Payload: `SymbolInfoMarginRateData`

| Field                     | Proto Type | Description                  |
| ------------------------- | ---------- | ---------------------------- |
| `maintenance_margin_rate` | `double`   | Maintenance margin **rate**. |
| `initial_margin_rate`     | `double`   | Initial margin **rate**.     |

> **Wire reply:** `SymbolInfoMarginRateReply { data: SymbolInfoMarginRateData, error: Error? }`
> SDK returns `reply.data`.


---

## Enum: `ENUM_ORDER_TYPE`

| Number | Value                        |
| -----: | ---------------------------- |
|      0 | `ORDER_TYPE_BUY`             |
|      1 | `ORDER_TYPE_SELL`            |
|      2 | `ORDER_TYPE_BUY_LIMIT`       |
|      3 | `ORDER_TYPE_SELL_LIMIT`      |
|      4 | `ORDER_TYPE_BUY_STOP`        |
|      5 | `ORDER_TYPE_SELL_STOP`       |
|      6 | `ORDER_TYPE_BUY_STOP_LIMIT`  |
|      7 | `ORDER_TYPE_SELL_STOP_LIMIT` |
|      8 | `ORDER_TYPE_CLOSE_BY`        |

---

### 🎯 Purpose

* Pre‑check margin requirements before placing or modifying orders.
* Display margin components in UI (initial & maintenance).
* Audit broker settings across instruments.

### 🧩 Notes & Tips

* Pair with `symbol_info_double(SYMBOL_TRADE_CONTRACT_SIZE)` and current price to project **absolute margin** per lot.
* For precise feasibility (free margin after/retcode), use `OrderCheck`.

---

**See also:** [order\_calc\_margin.md](../Trading_Operations/order_calc_margin.md), [order\_check.md](../Trading_Operations/order_check.md), [symbol\_info\_double.md](./symbol_info_double.md)

## Usage Examples

### 1) Rough initial margin per 1 lot (illustrative)

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

rates = await acct.symbol_info_margin_rate("EURUSD", mi_pb2.ENUM_ORDER_TYPE.ORDER_TYPE_BUY)
contract = await acct.symbol_info_double("EURUSD", mi_pb2.SymbolInfoDoubleProperty.SYMBOL_TRADE_CONTRACT_SIZE)
print("rate:", rates.initial_margin_rate, "contract:", contract.value)
```

### 2) With deadline & cancel

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

cancel_event = asyncio.Event()
res = await acct.symbol_info_margin_rate(
    "BTCUSD",
    mi_pb2.ENUM_ORDER_TYPE.ORDER_TYPE_BUY,
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
print(res.initial_margin_rate, res.maintenance_margin_rate)
```
