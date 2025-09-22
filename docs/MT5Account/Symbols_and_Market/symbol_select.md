# ✅ Symbol Select

> **Request:** add or remove a **symbol** from **Market Watch**.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_select(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolSelect*` messages (`SymbolSelectRequest`, `SymbolSelectReply`, `SymbolSelectData`)
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolSelect(SymbolSelectRequest) → SymbolSelectReply`
* **Low-level client:** `MarketInfoStub.SymbolSelect(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_select(symbol, select, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Ensure a symbol appears in Market Watch
# (English-only comments per project style)
res = await acct.symbol_select("EURUSD", True)
print(res.success)  # True if operation succeeded
```

---

### Method Signature

```python
async def symbol_select(
    self,
    symbol: str,
    select: bool,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolSelectData
```

---

## 💬 Plain English

* **What it is.** Turns a symbol **on/off** in **Market Watch**.
* **Why you care.** Many terminals stream quotes **only** for Market Watch symbols; selecting ensures data & UI visibility.
* **Mind the traps.**

  * `select=True` → add to Market Watch; `False` → remove.
  * If the symbol does not exist, the server may not select it. Guard with `symbol_exist(...)` when in doubt.

---

## 🔽 Input

| Parameter            | Type                  | Description                                                       |                                                    |
| -------------------- | --------------------- | ----------------------------------------------------------------- | -------------------------------------------------- |
| `symbol`             | `str` (**required**)  | Symbol to toggle (maps to `symbol` in request).                   |                                                    |
| `select`             | `bool` (**required**) | `True` → add to Market Watch; `False` → remove from Market Watch. |                                                    |
| `deadline`           | \`datetime            | None\`                                                            | Absolute per-call deadline → converted to timeout. |
| `cancellation_event` | \`asyncio.Event       | None\`                                                            | Cooperative cancel for the retry wrapper.          |

---

## ⬆️ Output

### Payload: `SymbolSelectData`

| Field     | Proto Type | Description                        |
| --------- | ---------- | ---------------------------------- |
| `success` | `bool`     | `True` if the operation succeeded. |

> **Wire reply:** `SymbolSelectReply { data: SymbolSelectData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Ensure the symbols you care about are visible and streaming.
* Drive UX (e.g., add/remove from watchlists from within your app).
* Prep before quote/market book subscriptions.

### 🧩 Notes & Tips

* For batch flows, **check existence first** (`symbol_exist`) to avoid noisy ops.
* Idempotent usage: calling `select=True` when already selected will still return `success=True`.

---

**See also:** [symbol\_is\_synchronized.md](./symbol_is_synchronized.md), [symbol\_name.md](./symbol_name.md), [symbols\_total.md](./symbols_total.md)

## Usage Examples

### 1) Ensure selected before subscribing

```python
if (await acct.symbol_exist("BTCUSD")).exists:
    state = await acct.symbol_select("BTCUSD", True)
    assert state.success
```

### 2) Remove from Market Watch

```python
state = await acct.symbol_select("USDRUB", False)
print("Operation ok?", state.success)
```

### 3) Batch ensure a list is present

```python
wanted = ["EURUSD", "GBPUSD", "XAUUSD"]
for s in wanted:
    if (await acct.symbol_exist(s)).exists:
        ok = (await acct.symbol_select(s, True)).success
        if not ok:
            print("Failed to select:", s)
```
