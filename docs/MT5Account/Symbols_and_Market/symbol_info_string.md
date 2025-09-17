# ✅ Symbol Info String

> **Request:** get a **string** property of a **symbol** (e.g., DESCRIPTION, CURRENCY\_\*, PATH, ISIN, FORMULA) via a single RPC.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_info_string(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolInfoString*` messages (`SymbolInfoStringRequest`, `SymbolInfoStringReply`, `SymbolInfoStringData`) and enum `SymbolInfoStringProperty`
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoString(SymbolInfoStringRequest) → SymbolInfoStringReply`
* **Low-level client:** `MarketInfoStub.SymbolInfoString(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_info_string(symbol, property, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Get human-readable description
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

desc = await acct.symbol_info_string(
    "EURUSD",
    mi_pb2.SymbolInfoStringProperty.SYMBOL_DESCRIPTION,
)
print(desc.value)
```

---

### Method Signature

```python
async def symbol_info_string(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoStringProperty,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolInfoStringData
```

---

## 💬 Plain English

* **What it is.** Direct read of a **string field** for a symbol.
* **Why you care.** Ideal for UI labels, grouping, compliance (ISIN), and custom symbol metadata.

---

## 🔽 Input

| Parameter            | Type                                      | Description                                        |   |
| -------------------- | ----------------------------------------- | -------------------------------------------------- | - |
| `symbol`             | `str` (**required**)                      | Symbol name (maps to `symbol` in request).         |   |
| `property`           | `SymbolInfoStringProperty` (**required**) | Which string property to retrieve (see enum).      |   |
| `deadline`           | `datetime \| None`                        | Absolute per‑call deadline → converted to timeout. |   |
| `cancellation_event` | `asyncio.Event \| None`                   | Cooperative cancel for the retry wrapper.          |   |

> **Request message:** `SymbolInfoStringRequest { symbol: string, type: SymbolInfoStringProperty }`

---

## ⬆️ Output

### Payload: `SymbolInfoStringData`

| Field   | Proto Type | Description                        |
| ------- | ---------- | ---------------------------------- |
| `value` | `string`   | The string value for the property. |

> **Wire reply:** `SymbolInfoStringReply { data: SymbolInfoStringData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Populate UI labels and metadata (description, path, page link).
* Show/account currencies (base/profit/margin) for calculators.
* Compliance fields like **ISIN** for securities.

### 🧩 Notes & Tips

* For pricing and lot economics, combine with `symbol_info_double(...)` or `tick_value_with_size(...)`.
* For modes/flags (trade/order/filling), see `symbol_info_integer(...)`.

---

**See also:** [symbol\_info\_double.md](./symbol_info_double.md), [symbol\_info\_integer.md](./symbol_info_integer.md), [symbol\_info\_tick.md](./symbol_info_tick.md)

## Usage Examples

### 1) Get path and group by folders

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

p = await acct.symbol_info_string("EURUSD", mi_pb2.SymbolInfoStringProperty.SYMBOL_PATH)
folders = p.value.split("\\\\")  # ['Forex', 'Majors', 'EURUSD']
print(folders)
```

### 2) Currency triplet

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

base = await acct.symbol_info_string("XAUUSD", mi_pb2.SymbolInfoStringProperty.SYMBOL_CURRENCY_BASE)
profit = await acct.symbol_info_string("XAUUSD", mi_pb2.SymbolInfoStringProperty.SYMBOL_CURRENCY_PROFIT)
margin = await acct.symbol_info_string("XAUUSD", mi_pb2.SymbolInfoStringProperty.SYMBOL_CURRENCY_MARGIN)
print(base.value, profit.value, margin.value)
```

### 3) ISIN & web page

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

isin = await acct.symbol_info_string("AAPL", mi_pb2.SymbolInfoStringProperty.SYMBOL_ISIN)
page = await acct.symbol_info_string("AAPL", mi_pb2.SymbolInfoStringProperty.SYMBOL_PAGE)
print(isin.value, page.value)
```

---

## Enum: `SymbolInfoStringProperty`

* `SYMBOL_BASIS`
* `SYMBOL_CURRENCY_BASE`
* `SYMBOL_CURRENCY_PROFIT`
* `SYMBOL_CURRENCY_MARGIN`
* `SYMBOL_BANK_HOLIDAYS`
* `SYMBOL_DESCRIPTION`
* `SYMBOL_FORMULA`
* `SYMBOL_ISIN`
* `SYMBOL_NAME`
* `SYMBOL_PAGE`
* `SYMBOL_PATH`
