# ✅ Symbol Is Synchronized

> **Request:** check whether a **symbol** is currently **synchronized** in the terminal (i.e., the terminal has recent data and can operate on it).

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_is_synchronized(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolIsSynchronized*` messages (`SymbolIsSynchronizedRequest`, `SymbolIsSynchronizedReply`, `SymbolIsSynchronizedData`)
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolIsSynchronized(SymbolIsSynchronizedRequest) → SymbolIsSynchronizedReply`
* **Low-level client:** `MarketInfoStub.SymbolIsSynchronized(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_is_synchronized(symbol, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Ensure the symbol is synchronized before requesting quotes / book
info = await acct.symbol_is_synchronized("EURUSD")
print(info.synchronized)  # True/False
```

---

### Method Signature

```python
async def symbol_is_synchronized(
    self,
    symbol: str,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolIsSynchronizedData
```

---

## 💬 Plain English

* **What it is.** A lightweight health check: is the **symbol synced** (has data, ready for operations)?
* **Why you care.** Prevents calling heavier RPCs (quotes, book, orders) on symbols the terminal hasn’t synced yet.
* **Mind the traps.**

  * Request field is the **symbol name** (`symbol`).
  * If the symbol isn’t selected in Market Watch, some terminals may remain **unsynchronized** until selected.

---

## 🔽 Input

| Parameter            | Type                 | Description                                |                                                    |
| -------------------- | -------------------- | ------------------------------------------ | -------------------------------------------------- |
| `symbol`             | `str` (**required**) | Symbol name (maps to `symbol` in request). |                                                    |
| `deadline`           | \`datetime           | None\`                                     | Absolute per‑call deadline → converted to timeout. |
| `cancellation_event` | \`asyncio.Event      | None\`                                     | Cooperative cancel for the retry wrapper.          |

> **Request message:** `SymbolIsSynchronizedRequest { symbol: string }`

---

## ⬆️ Output

### Payload: `SymbolIsSynchronizedData`

| Field          | Proto Type | Description                                 |
| -------------- | ---------- | ------------------------------------------- |
| `synchronized` | `bool`     | `True` if the terminal considers it synced. |

> **Wire reply:** `SymbolIsSynchronizedReply { data: SymbolIsSynchronizedData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Pre‑flight check before quotes, book, and trading ops.
* UI status badge (e.g., “Synced / Not synced”).
* Health monitoring across a batch of symbols.

### 🧩 Notes & Tips

* If result is `False`, try `symbol_select(symbol, True)` to force Market Watch listing, then re‑check.
* Combine with `symbol_exist` to avoid syncing non‑existent symbols.

---

**See also:** [symbol\_select.md](./symbol_select.md), [symbol\_name.md](./symbol_name.md), [symbol\_info\_tick.md](./symbol_info_tick.md)

## Usage Examples

### 1) Guard before subscribing to book/quotes

```python
s = "XAUUSD"
if (await acct.symbol_is_synchronized(s)).synchronized:
    # safe to proceed
    ...
else:
    # fall back: force select and retry
    await acct.symbol_select(s, True)
    again = await acct.symbol_is_synchronized(s)
    assert again.synchronized
```

### 2) Batch sync check with auto‑select

```python
symbols = ["EURUSD", "BTCUSD", "US500.cash"]
for s in symbols:
    info = await acct.symbol_is_synchronized(s)
    if not info.synchronized and (await acct.symbol_exist(s)).exists:
        await acct.symbol_select(s, True)
```

### 3) Timeout‑sensitive check

```python
from datetime import datetime, timedelta, timezone

info = await acct.symbol_is_synchronized(
    "EURUSD",
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
)
print("synced:", info.synchronized)
```
