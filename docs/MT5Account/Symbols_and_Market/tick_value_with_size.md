# ✅ Tick Value With Size

> **Request:** fetch **tick value** and **tick size** (plus contract size) for **multiple symbols** in one call.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `tick_value_with_size(...)`
* `MetaRpcMT5/mt5_term_api_account_helper_pb2.py` — `TickValueWithSize*` messages (`TickValueWithSizeRequest`, `TickValueWithSizeReply`, `TickValueWithSizeData`, `TickSizeSymbol`)
* `MetaRpcMT5/mt5_term_api_account_helper_pb2_grpc.py` — service stub `AccountHelperStub`

---

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `TickValueWithSize(TickValueWithSizeRequest) → TickValueWithSizeReply`
* **Low-level client:** `AccountHelperStub.TickValueWithSize(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.tick_value_with_size(symbols, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Get tick value/size/contract size for a batch of symbols
symbols = ["EURUSD", "GBPUSD", "XAUUSD"]
res = await acct.tick_value_with_size(symbols)

# Build a simple dict: name -> (tick_value, tick_size, contract_size)
info = {
    row.Name: (row.TradeTickValue, row.TradeTickSize, row.TradeContractSize)
    for row in res.symbol_tick_size_infos
}
print(info)
```

---

### Method Signature

```python
async def tick_value_with_size(
    self,
    symbols: list[str],
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> account_helper_pb2.TickValueWithSizeData
```

---

## 💬 Plain English

* **What it is.** Bulk retrieval of **tick economics** per symbol.
* **Why you care.** Avoids N separate calls when populating pricing/risk tables or validating strategy params.
* **Mind the traps.**

  * The request expects **symbol names**; unknown symbols will simply return **no entry** for that name.
  * The wrapper returns `reply.data` → you get a `TickValueWithSizeData` with a list of rows.

---

## 🔽 Input

| Parameter            | Type                       | Description                                     |                                                    |   |
| -------------------- | -------------------------- | ----------------------------------------------- | -------------------------------------------------- | - |
| `symbols`            | `list[str]` (**required**) | List of symbol names. Maps to `symbol_names[]`. |                                                    |   |
| `deadline`           | \`datetime                 | None\`                                          | Absolute per‑call deadline → converted to timeout. |   |
| `cancellation_event` | \`asyncio.Event            | None\`                                          | Cooperative cancel for the retry wrapper.          |   |

> **Request message:** `TickValueWithSizeRequest { symbol_names: repeated string }`

---

## ⬆️ Output

### Payload: `TickValueWithSizeData`

| Field                    | Proto Type                | Description                   |
| ------------------------ | ------------------------- | ----------------------------- |
| `symbol_tick_size_infos` | `repeated TickSizeSymbol` | Per‑symbol tick metrics rows. |

#### `TickSizeSymbol`

> *Field names per pb (PascalCase):*

| Field                  | Proto Type | Meaning                                        |
| ---------------------- | ---------- | ---------------------------------------------- |
| `Name`                 | `string`   | Symbol name.                                   |
| `TradeTickValue`       | `double`   | Tick value (account currency).                 |
| `TradeTickValueProfit` | `double`   | Tick value used for profit calc (if distinct). |
| `TradeTickValueLoss`   | `double`   | Tick value used for loss calc (if distinct).   |
| `TradeTickSize`        | `double`   | Price increment per tick.                      |
| `TradeContractSize`    | `double`   | Contract size.                                 |

> **Wire reply:** `TickValueWithSizeReply { data: TickValueWithSizeData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Populate pricing/lot calculators and risk dashboards.
* Precompute pip value and lot value per symbol for UI/strategies.
* Validate broker settings across a bulk symbol list.

### 🧩 Notes & Tips

* If you need just one symbol, you can still call this with a single‑item list.
* Combine with `symbol_exist` and `symbol_is_synchronized` to ensure data readiness.

---

**See also:** [symbol\_params\_many.md](./symbol_params_many.md), [symbol\_info\_double.md](./symbol_info_double.md), [order\_calc\_margin.md](../Trading_Operations/order_calc_margin.md)

## Usage Examples

### 1) Batch calculate per‑lot pip value table

```python
# English-only comments per project style
rows = await acct.tick_value_with_size(["EURUSD","GBPUSD","XAUUSD"])  
for r in rows.symbol_tick_size_infos:
    print(r.Name, r.TradeTickValue, r.TradeTickSize, r.TradeContractSize)
```

### 2) With deadline & cancellation

```python
import asyncio
from datetime import datetime, timedelta, timezone

cancel_event = asyncio.Event()
rows = await acct.tick_value_with_size(
    ["BTCUSD", "US500.cash"],
    deadline=datetime.now(timezone.utc) + timedelta(seconds=3),
    cancellation_event=cancel_event,
)
print(len(rows.symbol_tick_size_infos))
```

### 3) Build a dict for quick lookups

```python
rows = await acct.tick_value_with_size(["EURUSD","XAUUSD"])
by_name = {r.Name: r for r in rows.symbol_tick_size_infos}
print(by_name["EURUSD"].TradeTickValue)
```
