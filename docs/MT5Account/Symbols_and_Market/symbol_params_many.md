# ✅ Symbol Params Many

> **Request:** fetch **many symbols' parameters** (paged + sortable), returning a structured list of per‑symbol fields.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_params_many(...)`
* `MetaRpcMT5/mt5_term_api_account_helper_pb2.py` — `SymbolParamsMany*` messages (`SymbolParamsManyRequest`, `SymbolParamsManyReply`, `SymbolParamsManyData`) and enums (`AH_SYMBOL_PARAMS_MANY_SORT_TYPE`)
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

* **What it is.** Paged **directory** of symbol parameters (contract size, tick size/value, volumes, spreads, etc.).
* **Why you care.** Drive symbol pickers, validations, and bulk analytics without N requests.
* **Mind the traps.**

  * The wrapper returns **`.data`** semantics on the wire; SDK returns a `SymbolParamsManyData` with `symbol_infos[]`.
  * Use **paging** (`page_number`, `items_per_page`) to avoid heavy responses on large servers.
  * `symbol_name` filter is an **exact match** — narrows results to a single symbol if present.

---

## 🔽 Input

### Message: `SymbolParamsManyRequest`

| Field            | Proto Type                             | Required | Description                                     |
| ---------------- | -------------------------------------- | -------- | ----------------------------------------------- |
| `symbol_name`    | `string`                               | no       | Optional exact‑name filter for a single symbol. |
| `sort_type`      | `enum AH_SYMBOL_PARAMS_MANY_SORT_TYPE` | no       | Server‑side sort (see enum below).              |
| `page_number`    | `int32`                                | no       | Zero‑based page index.                          |
| `items_per_page` | `int32`                                | no       | Page size (how many items to return).           |

> **Note:** The SDK wrapper maps your `deadline` → gRPC `timeout` and honors `cancellation_event`.

---

## ⬆️ Output

### Message: `SymbolParamsManyData`

| Field            | Proto Type                               | Description                                  |
| ---------------- | ---------------------------------------- | -------------------------------------------- |
| `symbol_infos`   | `repeated mt5_term_api.SymbolParameters` | List of per‑symbol parameter objects.        |
| `symbols_total`  | `int32`                                  | Total number of symbols matching the filter. |
| `page_number`    | `int32` (optional)                       | Echo of the requested page.                  |
| `items_per_page` | `int32` (optional)                       | Echo of the requested page size.             |

#### `mt5_term_api.SymbolParameters` — key fields

> **Many fields** are exposed. The most commonly used ones are listed here; the full set is available in the proto.

| Field                               | Proto Type      | Meaning                                            |
| ----------------------------------- | --------------- | -------------------------------------------------- |
| `name`                              | `string`        | Symbol name.                                       |
| `point`                             | `double`        | Price point size.                                  |
| `digits`                            | `int32`         | Number of digits in prices.                        |
| `bid`, `bid_high`, `bid_low`        | `double`        | Current/hi/lo bid.                                 |
| `ask`, `ask_high`, `ask_low`        | `double`        | Current/hi/lo ask.                                 |
| `last`, `last_high`, `last_low`     | `double`        | Last trade price triplet (if applicable).          |
| `volume_real`                       | `double`        | Current tick volume (real).                        |
| `trade_tick_value`                  | `double`        | Tick value (account currency).                     |
| `trade_tick_value_profit`           | `double`        | Tick value used for profit calc.                   |
| `trade_tick_value_loss`             | `double`        | Tick value used for loss calc.                     |
| `trade_tick_size`                   | `double`        | Price increment per tick.                          |
| `trade_contract_size`               | `double`        | Contract size.                                     |
| `volume_min/max/step/limit`         | `double`        | Lot constraints.                                   |
| `spread`, `spread_float`            | `int32`, `bool` | Spread (points) and whether it is floating.        |
| `ticks_book_depth`                  | `int32`         | DOM depth supported by the broker.                 |
| `trade_calc_mode`                   | `enum`          | Symbol calc mode (`BMT5_ENUM_SYMBOL_CALC_MODE`).   |
| `trade_mode`                        | `enum`          | Trade permissions (`BMT5_ENUM_SYMBOL_TRADE_MODE`). |
| `swap_mode`                         | `enum`          | Swap calculation mode.                             |
| `margin_initial/maintenance/hedged` | `double`        | Margin parameters.                                 |
| `currency_base/profit/margin`       | `string`        | Currency triplet.                                  |
| `sector/industry`                   | `enum`          | Sector and industry classifications.               |
| `path`, `page`, `sym_description`   | `string`        | Descriptive strings (path, web page, description). |

> Additional fields include rollover settings, session stats, execution/filling/order modes, timestamps, and more — see proto for the exhaustive list.

---

## Enum: `AH_SYMBOL_PARAMS_MANY_SORT_TYPE`

| Number | Value                                       |
| -----: | ------------------------------------------- |
|      0 | `AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_ASC`  |
|      1 | `AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_DESC` |
|      2 | `AH_PARAMS_MANY_SORT_TYPE_MQL_INDEX_ASC`    |
|      3 | `AH_PARAMS_MANY_SORT_TYPE_MQL_INDEX_DESC`   |

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

**See also:** [symbol\_info\_double.md](./symbol_info_double.md), [symbol\_info\_integer.md](./symbol_info_integer.md), [symbol\_info\_string.md](./symbol_info_string.md)

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
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

req = ah_pb2.SymbolParamsManyRequest(symbol_name="XAUUSD")
res = await acct.symbol_params_many(req)
print([p.name for p in res.symbol_infos])  # ["XAUUSD"] or []
```

### 3) Sorted by name (ascending)

```python
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

req = ah_pb2.SymbolParamsManyRequest(
    sort_type=ah_pb2.AH_SYMBOL_PARAMS_MANY_SORT_TYPE.AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_ASC,
    page_number=0,
    items_per_page=25,
)
page = await acct.symbol_params_many(req)
print(page.page_number, len(page.symbol_infos))
```
