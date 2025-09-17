# ✅ Symbol Info Margin Rate

> **Request:** get **margin rates** for a **symbol** given an **order type** (e.g., BUY/SELL), returning initial/maintenance/hedged rates.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_info_margin_rate(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolInfoMarginRat*` messages (`SymbolInfoMarginRatRequest`, `SymbolInfoMarginRatReply`, `SymbolInfoMarginRat`) and enum `BMT5_ENUM_ORDER_TYPE`
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoMarginRate(SymbolInfoMarginRatRequest) → SymbolInfoMarginRatReply`
* **Low-level client:** `MarketInfoStub.SymbolInfoMarginRate(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_info_margin_rate(symbol, order_type, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Ask margin rates for placing a BUY order
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

rates = await acct.symbol_info_margin_rate(
    "EURUSD",
    mi_pb2.BMT5_ENUM_ORDER_TYPE.BMT5_ORDER_TYPE_BUY,
)
print(rates.MarginInitial, rates.MarginMaintenance, rates.MarginHedged)
```

---

### Method Signature

```python
async def symbol_info_margin_rate(
    self,
    symbol: str,
    order_type: market_info_pb2.BMT5_ENUM_ORDER_TYPE,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolInfoMarginRat
```

---

## 💬 Plain English

* **What it is.** Server-calculated **margin rates** for a symbol and a specific **order type**.
* **Why you care.** Use these rates to estimate **required margin** before submitting orders or sizing positions.
* **Mind the traps.**

  * Margin rates are **broker- and symbol-specific** and can differ by **order type** (BUY vs SELL) and hedging settings.
  * For some symbols, **hedged margin** can be lower than initial.

---

## 🔽 Input

| Parameter            | Type                                  | Description                                           |                                                    |   |
| -------------------- | ------------------------------------- | ----------------------------------------------------- | -------------------------------------------------- | - |
| `symbol`             | `str` (**required**)                  | Symbol name.                                          |                                                    |   |
| `order_type`         | `BMT5_ENUM_ORDER_TYPE` (**required**) | Order type context for which to compute margin rates. |                                                    |   |
| `deadline`           | \`datetime                            | None\`                                                | Absolute per‑call deadline → converted to timeout. |   |
| `cancellation_event` | \`asyncio.Event                       | None\`                                                | Cooperative cancel for the retry wrapper.          |   |

> **Request message:** `SymbolInfoMarginRatRequest { symbol: string, order_type: BMT5_ENUM_ORDER_TYPE }`

---

## ⬆️ Output

### Payload: `SymbolInfoMarginRat`

| Field               | Proto Type | Description                                       |
| ------------------- | ---------- | ------------------------------------------------- |
| `MarginInitial`     | `double`   | Initial margin rate for the given order type.     |
| `MarginMaintenance` | `double`   | Maintenance margin rate.                          |
| `MarginHedged`      | `double`   | Margin rate for hedged positions (if applicable). |

> **Wire reply:** `SymbolInfoMarginRatReply { data: SymbolInfoMarginRat, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Pre-check margin requirements before placing or modifying orders.
* Display margin components in UI (initial/maintenance/hedged).
* Audit broker settings across instruments.

### 🧩 Notes & Tips

* Pair with `symbol_info_double(SYMBOL_TRADE_CONTRACT_SIZE)` and current price to project **absolute margin** per lot.
---

## Usage Examples

### 1) Show rates for BUY vs SELL

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

buy = await acct.symbol_info_margin_rate("XAUUSD", mi_pb2.BMT5_ENUM_ORDER_TYPE.BMT5_ORDER_TYPE_BUY)
sell = await acct.symbol_info_margin_rate("XAUUSD", mi_pb2.BMT5_ENUM_ORDER_TYPE.BMT5_ORDER_TYPE_SELL)
print("BUY:", buy.MarginInitial, "SELL:", sell.MarginInitial)
```

### 2) Compute rough initial margin per 1 lot (illustrative)

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

rates = await acct.symbol_info_margin_rate("EURUSD", mi_pb2.BMT5_ENUM_ORDER_TYPE.BMT5_ORDER_TYPE_BUY)
contract = await acct.symbol_info_double("EURUSD", mi_pb2.SymbolInfoDoubleProperty.SYMBOL_TRADE_CONTRACT_SIZE)
point = await acct.symbol_info_double("EURUSD", mi_pb2.SymbolInfoDoubleProperty.SYMBOL_POINT)
# Example: use returned rate with contract size and price model in your app logic
print("rate:", rates.MarginInitial, "contract:", contract.value)
```

### 3) With deadline & cancel

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

cancel_event = asyncio.Event()
res = await acct.symbol_info_margin_rate(
    "BTCUSD",
    mi_pb2.BMT5_ENUM_ORDER_TYPE.BMT5_ORDER_TYPE_BUY,
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
print(res.MarginInitial, res.MarginMaintenance)
```
