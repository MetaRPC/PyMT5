# ✅ Symbol Info Integer

> **Request:** get an **integer** property of a **symbol** (e.g., DIGITS, SPREAD, TRADE\_MODE) via a single RPC.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_info_integer(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolInfoInteger*` messages (`SymbolInfoIntegerRequest`, `SymbolInfoIntegerReply`, `SymbolInfoIntegerData`) and enum `SymbolInfoIntegerProperty`
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoInteger(SymbolInfoIntegerRequest) → SymbolInfoIntegerReply`
* **Low-level client:** `MarketInfoStub.SymbolInfoInteger(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_info_integer(symbol, property, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Get the number of digits for the symbol
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

val = await acct.symbol_info_integer(
    "EURUSD",
    mi_pb2.SymbolInfoIntegerProperty.SYMBOL_DIGITS,
)
print(val.value)  # e.g., 5
```

---

### Method Signature

```python
async def symbol_info_integer(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoIntegerProperty,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolInfoIntegerData
```

---

## 💬 Plain English

* **What it is.** Direct read of an **integer field** for a symbol.
* **Why you care.** Lightweight and precise for discrete attributes (digits, spread, trade modes, flags, timestamps).

---

## 🔽 Input

| Parameter            | Type                                       | Description                                        |   |
| -------------------- | ------------------------------------------ | -------------------------------------------------- | - |
| `symbol`             | `str` (**required**)                       | Symbol name (maps to `symbol` in request).         |   |
| `property`           | `SymbolInfoIntegerProperty` (**required**) | Which integer property to retrieve (see enum).     |   |
| `deadline`           | `datetime \| None`                         | Absolute per‑call deadline → converted to timeout. |   |
| `cancellation_event` | `asyncio.Event \| None`                    | Cooperative cancel for the retry wrapper.          |   |

> **Request message:** `SymbolInfoIntegerRequest { symbol: string, type: SymbolInfoIntegerProperty }`

---

## ⬆️ Output

### Payload: `SymbolInfoIntegerData`

| Field   | Proto Type | Description                         |
| ------- | ---------- | ----------------------------------- |
| `value` | `int64`    | The numeric value for the property. |

> **Wire reply:** `SymbolInfoIntegerReply { data: SymbolInfoIntegerData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Pull specific discrete parameters for calculators and UI (digits/spread/modes).
* Quick validations and health checks.
* Compose with other calls for dashboards.

### 🧩 Notes & Tips

* When interpreting **modes** (TRADE/ORDER/FILLING/etc.), map the integer to your corresponding enum for human‑readable labels.
* For price/tick economics, see `symbol_info_double(...)` and `tick_value_with_size(...)`.

---

**See also:** [symbol\_info\_double.md](./symbol_info_double.md), [symbol\_info\_string.md](./symbol_info_string.md), [symbol\_info\_tick.md](./symbol_info_tick.md)

## Usage Examples

### 1) Get spread (points)

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
sp = await acct.symbol_info_integer("EURUSD", mi_pb2.SymbolInfoIntegerProperty.SYMBOL_SPREAD)
print(sp.value)
```

### 2) Get trade mode and map to label

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
mode = await acct.symbol_info_integer("XAUUSD", mi_pb2.SymbolInfoIntegerProperty.SYMBOL_TRADE_MODE)
# Map integer to your own enum/labels (disabled/full/long only/etc.)
print(mode.value)
```

### 3) Convert timestamps

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
import datetime as dt

raw = await acct.symbol_info_integer("BTCUSD", mi_pb2.SymbolInfoIntegerProperty.SYMBOL_START_TIME)
print(dt.datetime.utcfromtimestamp(raw.value))
```

---

## Enum: `SymbolInfoIntegerProperty`

> *Values per pb (number → value):*

| Number | Value                          |   |
| -----: | ------------------------------ | - |
|      0 | `SYMBOL_SUBSCRIPTION_DELAY`    |   |
|      1 | `SYMBOL_SECTOR`                |   |
|      2 | `SYMBOL_INDUSTRY`              |   |
|      3 | `SYMBOL_CUSTOM`                |   |
|      4 | `SYMBOL_BACKGROUND_COLOR`      |   |
|      5 | `SYMBOL_CHART_MODE`            |   |
|      6 | `SYMBOL_EXIST`                 |   |
|      7 | `SYMBOL_SELECT`                |   |
|      8 | `SYMBOL_VISIBLE`               |   |
|      9 | `SYMBOL_SESSION_DEALS`         |   |
|     10 | `SYMBOL_SESSION_BUY_ORDERS`    |   |
|     11 | `SYMBOL_SESSION_SELL_ORDERS`   |   |
|     12 | `SYMBOL_VOLUME`                |   |
|     13 | `SYMBOL_VOLUMEHIGH`            |   |
|     14 | `SYMBOL_VOLUMELOW`             |   |
|     15 | `SYMBOL_TIME`                  |   |
|     16 | `SYMBOL_TIME_MSC`              |   |
|     17 | `SYMBOL_DIGITS`                |   |
|     18 | `SYMBOL_SPREAD_FLOAT`          |   |
|     19 | `SYMBOL_SPREAD`                |   |
|     20 | `SYMBOL_TICKS_BOOKDEPTH`       |   |
|     21 | `SYMBOL_TRADE_CALC_MODE`       |   |
|     22 | `SYMBOL_TRADE_MODE`            |   |
|     23 | `SYMBOL_START_TIME`            |   |
|     24 | `SYMBOL_EXPIRATION_TIME`       |   |
|     25 | `SYMBOL_TRADE_STOPS_LEVEL`     |   |
|     26 | `SYMBOL_TRADE_FREEZE_LEVEL`    |   |
|     27 | `SYMBOL_TRADE_EXEMODE`         |   |
|     28 | `SYMBOL_SWAP_MODE`             |   |
|     29 | `SYMBOL_SWAP_ROLLOVER3DAYS`    |   |
|     30 | `SYMBOL_MARGIN_HEDGED_USE_LEG` |   |
|     31 | `SYMBOL_EXPIRATION_MODE`       |   |
|     32 | `SYMBOL_FILLING_MODE`          |   |
|     33 | `SYMBOL_ORDER_MODE`            |   |
|     34 | `SYMBOL_ORDER_GTC_MODE`        |   |
|     35 | `SYMBOL_OPTION_MODE`           |   |
|     36 | `SYMBOL_OPTION_RIGHT`          |   |
