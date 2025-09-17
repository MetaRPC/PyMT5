# ✅ Market Book Add

> **Request:** subscribe the terminal to **Level II (Market Book) updates** for a **symbol**.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `market_book_add(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `MarketBookAdd*` messages (`MarketBookAddRequest`, `MarketBookAddReply`, `MarketBookAddData`)
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `MarketBookAdd(MarketBookAddRequest) → MarketBookAddReply`
* **Low-level client:** `MarketInfoStub.MarketBookAdd(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.market_book_add(symbol, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Subscribe to DOM (order book) updates for a symbol
ok = await acct.market_book_add("EURUSD")
print(ok.opened_successfully)  # True if subscription is active
```

---

### Method Signature

```python
async def market_book_add(
    self,
    symbol: str,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.MarketBookAddData
```

---

## 💬 Plain English

* **What it is.** Turns on **order book streaming** for a symbol in the terminal.
* **Why you care.** Required before calling `market_book_get(...)` or listening to DOM updates in your app.
* **Mind the traps.**

  * Not every symbol/broker exposes a book → subscription may return **false**.
  * The symbol should be **selected & synchronized** to ensure updates arrive.
  * Remember to **release** the subscription with `market_book_release(symbol)` when done.

---

## 🔽 Input

| Parameter            | Type                 | Description                                |                                                    |   |
| -------------------- | -------------------- | ------------------------------------------ | -------------------------------------------------- | - |
| `symbol`             | `str` (**required**) | Symbol name (maps to `symbol` in request). |                                                    |   |
| `deadline`           | \`datetime           | None\`                                     | Absolute per‑call deadline → converted to timeout. |   |
| `cancellation_event` | \`asyncio.Event      | None\`                                     | Cooperative cancel for the retry wrapper.          |   |

> **Request message:** `MarketBookAddRequest { symbol: string }`

---

## ⬆️ Output

### Payload: `MarketBookAddData`

| Field                | Proto Type | Description                                      |
| -------------------- | ---------- | ------------------------------------------------ |
| `opened_successfully`| `bool`     | `True` if the book subscription was opened.     |

> **Wire reply:** `MarketBookAddReply { data: MarketBookAddData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Enable DOM/Level II **order book** features in UI/analytics.
* Prepare before reading the book via `market_book_get(...)`.
* Control resource usage by subscribing only to required symbols.

### 🧩 Notes & Tips

* Idempotent in practice: calling `market_book_add` on an already subscribed symbol keeps `subscribed=True`.
* Pair with `market_book_release(symbol)` to avoid leaking subscriptions.
* If `subscribed=False`, verify `symbol_exist`, `symbol_select(True)`, and permissions for Level II.

---

**See also:** [market\_book\_get.md](./market_book_get.md), [market\_book\_release.md](./market_book_release.md), [symbol\_info\_tick.md](./symbol_info_tick.md)

## Usage Examples

### 1) Subscribe then fetch the book

```python
ok = await acct.market_book_add("XAUUSD")
if ok.opened_successfully:
    book = await acct.market_book_get("XAUUSD")  # separate RPC
    for row in book.Bids + book.Asks:
        print(row.Price, row.Volume)

```

### 2) Ensure symbol is ready first

```python
s = "BTCUSD"
if not (await acct.symbol_is_synchronized(s)).is_synchronized:
    await acct.symbol_select(s, True)
    _ = await acct.symbol_is_synchronized(s)
print((await acct.market_book_add(s)).subscribed)
```

### 3) With deadline & cancel

```python
import asyncio
from datetime import datetime, timedelta, timezone

cancel_event = asyncio.Event()
res = await acct.market_book_add(
    "EURUSD",
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
print(res.opened_successfully)

```
