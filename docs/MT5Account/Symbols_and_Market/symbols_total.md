# ✅ Symbols Total

> **Request:** get the **total number of symbols** on the server, with an option to count **only Market Watch** (selected) symbols.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbols_total(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolsTotal*` messages (`SymbolsTotalRequest`, `SymbolsTotalReply`, `SymbolsTotalData`)
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

> **Note (verified):** `SymbolsTotal*` **exist only** in `mt5_term_api_market_info_pb2.py`. The request field is `mode: bool`; the reply data has `total: int32`.

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolsTotal(SymbolsTotalRequest) → SymbolsTotalReply`
* **Low-level client:** `MarketInfoStub.SymbolsTotal(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbols_total(selected_only, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Count only symbols that are in Market Watch
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

total = await acct.symbols_total(selected_only=True)
print(total.total)  # integer count
```

---

### Method Signature

```python
async def symbols_total(
    self,
    selected_only: bool,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolsTotalData
```

---

## 💬 Plain English

* **What it is.** A tiny, cheap call that returns **how many symbols** are available.
* **Why you care.** Useful for sanity checks, monitoring, and UI decisions (e.g., pagination, lazy loading).
* **Mind the traps.**

  * `selected_only=True` counts **only** the symbols in **Market Watch**. `False` counts **all** known symbols.
  * The SDK returns **`.data`** from the reply; you’ll get a `SymbolsTotalData` object with a single `total` field.

---

## 🔽 Input

| Parameter            | Type                  | Description                                      |                                                    |   |
| -------------------- | --------------------- | ------------------------------------------------ | -------------------------------------------------- | - |
| `selected_only`      | `bool` (**required**) | `True` → count only Market Watch; `False` → all. |                                                    |   |
| `deadline`           | \`datetime            | None\`                                           | Absolute per-call deadline → converted to timeout. |   |
| `cancellation_event` | \`asyncio.Event       | None\`                                           | Cooperative cancel for the retry wrapper.          |   |

---

## ⬆️ Output

### Payload: `SymbolsTotalData`

| Field   | Proto Type | Description                 |
| ------- | ---------- | --------------------------- |
| `total` | `int32`    | The resulting symbol count. |

> **Wire reply:** `SymbolsTotalReply { data: SymbolsTotalData, error: Error? }`
> SDK returns `reply.data`.

---
**See also:** [symbol\_name.md](./symbol_name.md), [symbol\_exist.md](./symbol_exist.md), [symbol\_select.md](./symbol_select.md)

### 🎯 Purpose

* Fast check for **how big** the symbol universe is (all vs. Market Watch).
* Drive UI/UX (e.g., disable “Show All” if counts are huge).
* Monitor environment changes (e.g., sudden drop in selected symbols).

### 🧩 Notes & Tips

* Prefer `selected_only=True` for user-facing views (keeps counts relevant to what the user actually sees).
* For inventory/ops dashboards, do both (selected & all) to compare deltas.
* Wrapper uses `execute_with_reconnect(...)` — transient gRPC hiccups are retried under the hood.

---

## Usage Examples

### 1) Count all symbols

```python
all_total = await acct.symbols_total(selected_only=False)
print(f"All symbols: {all_total.total}")
```

### 2) Count selected (Market Watch) with deadline & cancel

```python
import asyncio
from datetime import datetime, timedelta, timezone

cancel_event = asyncio.Event()
sel_total = await acct.symbols_total(
    selected_only=True,
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
print(f"Selected symbols: {sel_total.total}")
```

### 3) Compare selected vs. all

```python
selected = await acct.symbols_total(True)
all_ = await acct.symbols_total(False)
print(f"{selected.total}/{all_.total} symbols in Market Watch")
```

