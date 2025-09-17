# ✅ Symbol Name

> **Request:** get the **symbol name** by its **index** with the option to resolve from **Market Watch only**.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_name(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolName*` messages (`SymbolNameRequest`, `SymbolNameReply`, `SymbolNameData`)
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolName(SymbolNameRequest) → SymbolNameReply`
* **Low-level client:** `MarketInfoStub.SymbolName(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_name(index, selected, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Resolve a symbol name by position in Market Watch
name = await acct.symbol_name(index=0, selected=True)
print(name.name)  # e.g., "EURUSD"
```

---

### Method Signature

```python
async def symbol_name(
    self,
    index: int,
    selected: bool,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolNameData
```

---

## 💬 Plain English

* **What it is.** Returns the **symbol name** at a given position.
* **Why you care.** Enables paging through symbol lists (all symbols or just Market Watch) without fetching the full list.
* **Mind the traps.**

  * `selected=True` means the index is taken from **Market Watch**; `False` means from the **full server list**.
  * If the index is **out of range**, the server typically returns an **empty name**.

---

## 🔽 Input

| Parameter            | Type                  | Description                                                     |                                                    |   |
| -------------------- | --------------------- | --------------------------------------------------------------- | -------------------------------------------------- | - |
| `index`              | `int` (**required**)  | Zero‑based position of the symbol to resolve.                   |                                                    |   |
| `selected`           | `bool` (**required**) | `True` → use Market Watch list; `False` → use full symbol list. |                                                    |   |
| `deadline`           | \`datetime            | None\`                                                          | Absolute per‑call deadline → converted to timeout. |   |
| `cancellation_event` | \`asyncio.Event       | None\`                                                          | Cooperative cancel for the retry wrapper.          |   |

> **Request message:** `SymbolNameRequest { index: int32, selected: bool }`

---

## ⬆️ Output

### Payload: `SymbolNameData`

| Field  | Proto Type | Description                    |
| ------ | ---------- | ------------------------------ |
| `name` | `string`   | Resolved symbol name or empty. |

> **Wire reply:** `SymbolNameReply { data: SymbolNameData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Page through symbol universe in a deterministic order.
* Build symbol pickers (e.g., first 100 in Market Watch).
* Lightweight integrity checks before `symbol_exist` / `symbol_select`.

### 🧩 Notes & Tips

* Combine with `symbols_total(selected_only)` to stay within bounds: `index in [0, total)`.
* Expect empty result for out‑of‑range `index`; handle gracefully in UI.

---
**See also:** [symbols\_total.md](./symbols_total.md), [symbol\_select.md](./symbol_select.md), [symbol\_exist.md](./symbol_exist.md)

## Usage Examples

### 1) Iterate Market Watch symbols

```python
sel_total = await acct.symbols_total(True)
for i in range(sel_total.total):
    nm = await acct.symbol_name(i, True)
    print(i, nm.name)
```

### 2) Get the first 5 from the full list

```python
all_total = await acct.symbols_total(False)
count = min(5, all_total.total)
for i in range(count):
    nm = await acct.symbol_name(i, False)
    print(nm.name)
```

### 3) Guard against out‑of‑range

```python
idx = 999999
nm = await acct.symbol_name(idx, True)
if not nm.name:
    print("Index out of range for Market Watch")
```
