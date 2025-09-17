# ✅ Symbol Params Many

> **Request:** fetch **many symbols' parameters** (paged + sortable), returning a structured list of per‑symbol fields.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_params_many(...)`
* `MetaRpcMT5/mt5_term_api_account_helper_pb2.py` — `SymbolParamsMany*` messages (`SymbolParamsManyRequest`, `SymbolParamsManyReply`, `SymbolParamsManyData`) and enums (`AH_SYMBOL_PARAMS_SORT_TYPE`)
* `MetaRpcMT5/mt5_term_api_account_helper_pb2_grpc.py` — service stub `AccountHelperStub`

---

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `SymbolParamsMany(SymbolParamsManyRequest) → SymbolParamsManyReply`
* **Low-level client:** `AccountHelperStub.SymbolParamsMany(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_params_many(request, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Get first page of symbol parameters, sorted by server default
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

req = ah_pb2.SymbolParamsManyRequest(
    page_number=0,
    items_per_page=50,
)
res = await acct.symbol_params_many(req)
print(len(res.symbol_infos), res.symbols_total)
```

---

### Method Signature

```python
async def symbol_params_many(
    self,
    request: account_helper_pb2.SymbolParamsManyRequest,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> account_helper_pb2.SymbolParamsManyData
```

---

## 💬 Plain English

* **What it is.** Paged **directory** of symbol parameters (contract size, tick size/value, volumes, etc.).
* **Why you care.** Drive symbol pickers, validations, and bulk analytics without N requests.
* **Mind the traps.**

  * The wrapper returns **`.data`**; you receive a `SymbolParamsManyData` with `symbol_infos[]`.
  * Use **paging** (`page_number`, `items_per_page`) to avoid heavy responses on large servers.
  * `symbol_name` filter narrows results to one symbol (exact match).

---

## 🔽 Input

### Message: `SymbolParamsManyRequest`

| Field            | Proto Type                        | Required | Description                                     |
| ---------------- | --------------------------------- | -------- | ----------------------------------------------- |
| `symbol_name`    | `string`                          | no       | Optional exact‑name filter for a single symbol. |
| `sort_type`      | `enum AH_SYMBOL_PARAMS_SORT_TYPE` | no       | Server‑side sort (e.g., by name asc/desc).      |
| `page_number`    | `int32`                           | no       | Zero‑based page index.                          |
| `items_per_page` | `int32`                           | no       | Page size (how many items to return).           |

> **Note:** The SDK wrapper maps your `deadline` → gRPC `timeout` and honors `cancellation_event`.

---

## ⬆️ Output

### Message: `SymbolParamsManyData`

| Field            | Proto Type                               | Description                                  |
| ---------------- | ---------------------------------------- | -------------------------------------------- |
| `symbol_infos`   | `repeated mt5_term_api.SymbolParameters` | List of per‑symbol parameter objects.        |
| `symbols_total`  | `int32`                                  | Total number of symbols matching the filter. |
| `page_number`    | `int32`                                  | Echo of the requested page.                  |
| `items_per_page` | `int32`                                  | Echo of the requested page size.             |

#### `mt5_term_api.SymbolParameters` (key fields)

> *The exact proto exposes many fields; common ones you will typically use:*

| Field                     | Proto Type | Meaning                                          |
| ------------------------- | ---------- | ------------------------------------------------ |
| `symbol_name`             | `string`   | Symbol name.                                     |
| `point`                   | `double`   | Price point size.                                |
| `trade_tick_value`        | `double`   | Tick value (account currency).                   |
| `trade_tick_value_profit` | `double`   | Tick value for profit calculation (if distinct). |
| `trade_tick_size`         | `double`   | Price increment per tick.                        |
| `trade_contract_size`     | `double`   | Contract size.                                   |
| `volume_min`              | `double`   | Minimum lot volume.                              |
| `volume_max`              | `double`   | Maximum lot volume.                              |
| `volume_step`             | `double`   | Step of lot volume.                              |
| `volume_limit`            | `double`   | Broker limit per position/order (if provided).   |

> *Some builds also expose `digits`; if absent, derive as `round(log10(1/point))`.*

---

### 🎯 Purpose

* Power bulk symbol onboarding, validations, and UI tables.
* Compute derived metrics (pip value, lot value) client‑side from returned fields.
* Pre‑cache parameters for strategy/risk engines.

### 🧩 Notes & Tips

* Use paging for big servers; render `res.symbols_total` to drive pagination controls.
* If you only need a handful of symbols, pass `symbol_name` per call or filter client‑side.
* Combine with `symbol_exist`, `symbol_select`, and `symbol_is_synchronized` for robust UX.

---

## Usage Examples

### 1) First 100 parameters (2 pages × 50)

```python
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

all_rows = []
for page in range(2):
    req = ah_pb2.SymbolParamsManyRequest(page_number=page, items_per_page=50)
    data = await acct.symbol_params_many(req)
    all_rows.extend(data.symbol_infos)
print(len(all_rows), data.symbols_total)
```

### 2) Filter by exact name

```python
req = ah_pb2.SymbolParamsManyRequest(symbol_name="XAUUSD")
row = await acct.symbol_params_many(req)
print([p.symbol_name for p in row.symbol_infos])  # ["XAUUSD"] or []
```

### 3) Sorted by name (ascending)

```python
req = ah_pb2.SymbolParamsManyRequest(
    sort_type=ah_pb2.AH_SYMBOL_PARAMS_SORT_TYPE.AH_SYMBOL_PARAMS_SORT_BY_NAME_ASC,
    page_number=0,
    items_per_page=25,
)
page = await acct.symbol_params_many(req)
print(page.page_number, len(page.symbol_infos))
```
