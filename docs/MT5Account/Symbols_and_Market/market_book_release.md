# ✅ Market Book Release

> **Request:** unsubscribe the terminal from **Level II (Market Book) updates** for a **symbol** (stop DOM streaming).

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `market_book_release(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `MarketBookRelease*` messages (`MarketBookReleaseRequest`, `MarketBookReleaseReply`, `MarketBookReleaseData`)
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `MarketBookRelease(MarketBookReleaseRequest) → MarketBookReleaseReply`
* **Low-level client:** `MarketInfoStub.MarketBookRelease(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.market_book_release(symbol, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Unsubscribe from DOM (order book) updates for a symbol
res = await acct.market_book_release("EURUSD")
print(res.closed_successfully)  # True if DOM subscription was closed
```

---

### Method Signature

```python
async def market_book_release(
    self,
    symbol: str,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.MarketBookReleaseData
```

---

## 💬 Plain English

* **What it is.** Turns **off** the order book stream for a symbol.
* **Why you care.** Frees terminal/network resources and stops unnecessary updates when a DOM panel is closed.
* **Mind the traps.**

  * If there was **no active subscription**, brokers may return `closed_successfully=False`.
  * Always pair adds/releases to avoid leaking long‑lived subscriptions in your app.

---

## 🔽 Input

| Parameter            | Type                 | Description                                |                                                    |   |
| -------------------- | -------------------- | ------------------------------------------ | -------------------------------------------------- | - |
| `symbol`             | `str` (**required**) | Symbol name (maps to `symbol` in request). |                                                    |   |
| `deadline`           | \`datetime           | None\`                                     | Absolute per‑call deadline → converted to timeout. |   |
| `cancellation_event` | \`asyncio.Event      | None\`                                     | Cooperative cancel for the retry wrapper.          |   |

> **Request message:** `MarketBookReleaseRequest { symbol: string }`

---

## ⬆️ Output

### Payload: `MarketBookReleaseData`

| Field                 | Proto Type | Description                                |
| --------------------- | ---------- | ------------------------------------------ |
| `closed_successfully` | `bool`     | `True` if the DOM subscription was closed. |

> **Wire reply:** `MarketBookReleaseReply { data: MarketBookReleaseData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Disable DOM/Level II streaming when it’s no longer needed.
* Keep resource usage in check on terminals and networks.
* Clean up before disconnecting or switching workspaces.

### 🧩 Notes & Tips

* Use with `market_book_add(symbol)` to manage lifecycle of subscriptions.

---

**See also:** [market\_book\_add.md](./market_book_add.md), [market\_book\_get.md](./market_book_get.md)


## Usage Examples

### 1) Safe cleanup on panel close

```python
# English-only comments per project style
s = "XAUUSD"
res = await acct.market_book_release(s)
if not res.closed_successfully:
    print("No active DOM subscription to close")
```

### 2) Add → Get → Release flow

```python
ok = await acct.market_book_add("BTCUSD")
book = await acct.market_book_get("BTCUSD")
_ = await acct.market_book_release("BTCUSD")
```

### 3) With deadline & cancel

```python
import asyncio
from datetime import datetime, timedelta, timezone

cancel_event = asyncio.Event()
res = await acct.market_book_release(
    "EURUSD",
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
print(res.closed_successfully)
```
