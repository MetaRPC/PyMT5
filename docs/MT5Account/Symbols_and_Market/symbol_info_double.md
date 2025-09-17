# ✅ Symbol Info Double

> **Request:** get a **double** property of a **symbol** (e.g., BID, ASK, POINT, TICK\_VALUE) via a single RPC.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_info_double(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolInfoDouble*` messages (`SymbolInfoDoubleRequest`, `SymbolInfoDoubleReply`, `SymbolInfoDoubleData`) and enum `SymbolInfoDoubleProperty`
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoDouble(SymbolInfoDoubleRequest) → SymbolInfoDoubleReply`
* **Low-level client:** `MarketInfoStub.SymbolInfoDouble(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_info_double(symbol, property, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Get current Bid price as double
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

val = await acct.symbol_info_double(
    "EURUSD",
    mi_pb2.SymbolInfoDoubleProperty.SYMBOL_BID,
)
print(val.value)
```

---

### Method Signature

```python
async def symbol_info_double(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoDoubleProperty,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolInfoDoubleData
```

---

## 💬 Plain English

* **What it is.** Direct read of a **double field** for a symbol.
* **Why you care.** Cheap, precise, and avoids fetching large structs when you need a single numeric attribute.
* **Mind the traps.**

  * Pass the **exact** symbol name in `symbol`.
  * Choose the correct enum in `property` from `SymbolInfoDoubleProperty` (see list below).
  * Non‑applicable properties may return **0.0**.

---

## 🔽 Input

| Parameter            | Type                                      | Description                                        |   |
| -------------------- | ----------------------------------------- | -------------------------------------------------- | - |
| `symbol`             | `str` (**required**)                      | Symbol name (maps to `symbol` in request).         |   |
| `property`           | `SymbolInfoDoubleProperty` (**required**) | Which double property to retrieve (see enum).      |   |
| `deadline`           | `datetime \| None`                        | Absolute per‑call deadline → converted to timeout. |   |
| `cancellation_event` | `asyncio.Event \| None`                   | Cooperative cancel for the retry wrapper.          |   |

> **Request message:** `SymbolInfoDoubleRequest { symbol: string, type: SymbolInfoDoubleProperty }`

---

## ⬆️ Output

### Payload: `SymbolInfoDoubleData`

| Field   | Proto Type | Description                         |
| ------- | ---------- | ----------------------------------- |
| `value` | `double`   | The numeric value for the property. |

> **Wire reply:** `SymbolInfoDoubleReply { data: SymbolInfoDoubleData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Pull specific prices/params (BID/ASK/POINT/TICK metrics) for calculators and UI.
* Quick validations and health checks without heavy payloads.
* Compose with other calls for dashboards.

### 🧩 Notes & Tips

* Prefer batching via your app logic when you need many symbols: loop over names and store results.
* For tick economics across many symbols, consider `tick_value_with_size(...)`.
* Pair with `symbol_is_synchronized(...)` to avoid stale/empty values.

---

## Usage Examples

### 1) Get point size

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
pt = await acct.symbol_info_double("XAUUSD", mi_pb2.SymbolInfoDoubleProperty.SYMBOL_POINT)
print(pt.value)
```

### 2) Tick parameters

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

v = await acct.symbol_info_double("EURUSD", mi_pb2.SymbolInfoDoubleProperty.SYMBOL_TRADE_TICK_VALUE)
s = await acct.symbol_info_double("EURUSD", mi_pb2.SymbolInfoDoubleProperty.SYMBOL_TRADE_TICK_SIZE)
print("tick value:", v.value, "tick size:", s.value)
```

### 3) With deadline & cancel

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

cancel_event = asyncio.Event()
res = await acct.symbol_info_double(
    "BTCUSD",
    mi_pb2.SymbolInfoDoubleProperty.SYMBOL_ASK,
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
print(res.value)
```

---

## Enum: `SymbolInfoDoubleProperty`

> *Full list from pb (number → value).*

| Number | Value                               |
| -----: | ----------------------------------- |
|      0 | `SYMBOL_BID`                        |
|      1 | `SYMBOL_BIDHIGH`                    |
|      2 | `SYMBOL_BIDLOW`                     |
|      3 | `SYMBOL_ASK`                        |
|      4 | `SYMBOL_ASKHIGH`                    |
|      5 | `SYMBOL_ASKLOW`                     |
|      6 | `SYMBOL_LAST`                       |
|      7 | `SYMBOL_LASTHIGH`                   |
|      8 | `SYMBOL_LASTLOW`                    |
|      9 | `SYMBOL_VOLUME_REAL`                |
|     10 | `SYMBOL_VOLUMEHIGH_REAL`            |
|     11 | `SYMBOL_VOLUMELOW_REAL`             |
|     12 | `SYMBOL_OPTION_STRIKE`              |
|     13 | `SYMBOL_POINT`                      |
|     14 | `SYMBOL_TRADE_TICK_VALUE`           |
|     15 | `SYMBOL_TRADE_TICK_VALUE_PROFIT`    |
|     16 | `SYMBOL_TRADE_TICK_VALUE_LOSS`      |
|     17 | `SYMBOL_TRADE_TICK_SIZE`            |
|     18 | `SYMBOL_TRADE_CONTRACT_SIZE`        |
|     19 | `SYMBOL_TRADE_ACCRUED_INTEREST`     |
|     20 | `SYMBOL_TRADE_FACE_VALUE`           |
|     21 | `SYMBOL_TRADE_LIQUIDITY_RATE`       |
|     22 | `SYMBOL_VOLUME_MIN`                 |
|     23 | `SYMBOL_VOLUME_MAX`                 |
|     24 | `SYMBOL_VOLUME_STEP`                |
|     25 | `SYMBOL_VOLUME_LIMIT`               |
|     26 | `SYMBOL_SWAP_LONG`                  |
|     27 | `SYMBOL_SWAP_SHORT`                 |
|     28 | `SYMBOL_SWAP_SUNDAY`                |
|     29 | `SYMBOL_SWAP_MONDAY`                |
|     30 | `SYMBOL_SWAP_TUESDAY`               |
|     31 | `SYMBOL_SWAP_WEDNESDAY`             |
|     32 | `SYMBOL_SWAP_THURSDAY`              |
|     33 | `SYMBOL_SWAP_FRIDAY`                |
|     34 | `SYMBOL_SWAP_SATURDAY`              |
|     35 | `SYMBOL_MARGIN_INITIAL`             |
|     36 | `SYMBOL_MARGIN_MAINTENANCE`         |
|     37 | `SYMBOL_SESSION_VOLUME`             |
|     38 | `SYMBOL_SESSION_TURNOVER`           |
|     39 | `SYMBOL_SESSION_INTEREST`           |
|     40 | `SYMBOL_SESSION_BUY_ORDERS_VOLUME`  |
|     41 | `SYMBOL_SESSION_SELL_ORDERS_VOLUME` |
|     42 | `SYMBOL_SESSION_OPEN`               |
|     43 | `SYMBOL_SESSION_CLOSE`              |
|     44 | `SYMBOL_SESSION_AW`                 |
|     45 | `SYMBOL_SESSION_PRICE_SETTLEMENT`   |
|     46 | `SYMBOL_SESSION_PRICE_LIMIT_MIN`    |
|     47 | `SYMBOL_SESSION_PRICE_LIMIT_MAX`    |
|     48 | `SYMBOL_MARGIN_HEDGED`              |
|     49 | `SYMBOL_PRICE_CHANGE`               |
|     50 | `SYMBOL_PRICE_VOLATILITY`           |
|     51 | `SYMBOL_PRICE_THEORETICAL`          |
|     52 | `SYMBOL_PRICE_DELTA`                |
|     53 | `SYMBOL_PRICE_THETA`                |
|     54 | `SYMBOL_PRICE_GAMMA`                |
|     55 | `SYMBOL_PRICE_VEGA`                 |
|     56 | `SYMBOL_PRICE_RHO`                  |
|     57 | `SYMBOL_PRICE_OMEGA`                |
|     58 | `SYMBOL_PRICE_SENSITIVITY`          |
|     59 | `SYMBOL_COUNT`                      |
