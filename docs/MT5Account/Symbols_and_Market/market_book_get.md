# ✅ Market Book Get

> **Request:** fetch a **snapshot of the Level II order book** (bids/asks ladder) for a **symbol**.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `market_book_get(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `MarketBookGet*` messages (`MarketBookGetRequest`, `MarketBookGetReply`, `MarketBookGetData`)
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `MarketBookGet(MarketBookGetRequest) → MarketBookGetReply`
* **Low-level client:** `MarketInfoStub.MarketBookGet(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.market_book_get(symbol, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Fetch current DOM snapshot and print top-of-book
book = await acct.market_book_get("EURUSD")
if book.Bids and book.Asks:
    best_bid = book.Bids[0]
    best_ask = book.Asks[0]
    spread = best_ask.Price - best_bid.Price
    print(best_bid.Price, best_ask.Price, spread)
```

---

### Method Signature

```python
async def market_book_get(
    self,
    symbol: str,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.MarketBookGetData
```

---

## 💬 Plain English

* **What it is.** A one-shot **depth snapshot**: aggregated **Bids** and **Asks** with price/volume per level.
* **Why you care.** Power depth widgets, slippage models, and liquidity checks before order placement.
* **Mind the traps.**

  * Some brokers expose limited depth (e.g., 5 levels); others none → arrays can be **empty**.
  * Ensure you’ve called `market_book_add(symbol)` to enable streaming; without it, snapshots may still work but won’t update automatically.
  * Prices ascend on **Asks** and descend on **Bids** (server‑side convention). Sort client‑side if you need a different order.

---

## 🔽 Input

| Parameter            | Type                 | Description                                |                                                    |   |
| -------------------- | -------------------- | ------------------------------------------ | -------------------------------------------------- | - |
| `symbol`             | `str` (**required**) | Symbol name (maps to `symbol` in request). |                                                    |   |
| `deadline`           | \`datetime           | None\`                                     | Absolute per‑call deadline → converted to timeout. |   |
| `cancellation_event` | \`asyncio.Event      | None\`                                     | Cooperative cancel for the retry wrapper.          |   |

> **Request message:** `MarketBookGetRequest { symbol: string }`

---

## ⬆️ Output

### Payload: `MarketBookGetData`

| Field  | Proto Type                     | Description                        |
| ------ | ------------------------------ | ---------------------------------- |
| `Bids` | `repeated MarketBookPriceData` | Bid ladder (price levels to buy).  |
| `Asks` | `repeated MarketBookPriceData` | Ask ladder (price levels to sell). |

#### `MarketBookPriceData`

| Field    | Proto Type | Description                 |
| -------- | ---------- | --------------------------- |
| `Price`  | `double`   | Price for this level.       |
| `Volume` | `double`   | Volume at this price level. |

> **Wire reply:** `MarketBookGetReply { data: MarketBookGetData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Render a **DOM** view and compute top-of-book spread.
* Feed execution logic (iceberg detection, slip estimates, partial fill planning).
* Monitor liquidity changes for alerts.

### 🧩 Notes & Tips

* Pair with `market_book_add` and `market_book_release` to manage subscription lifecycle.

---

## Usage Examples

### 1) Render a compact depth table

```python
book = await acct.market_book_get("XAUUSD")
print("BID       VOL   |   ASK       VOL")
for i in range(max(len(book.Bids), len(book.Asks))):
    b = book.Bids[i] if i < len(book.Bids) else None
    a = book.Asks[i] if i < len(book.Asks) else None
    print(f"{getattr(b,'Price',None):>8} {getattr(b,'Volume',None):>6} | {getattr(a,'Price',None):>8} {getattr(a,'Volume',None):>6}")
```

### 2) With deadline & cancel

```python
import asyncio
from datetime import datetime, timedelta, timezone

cancel_event = asyncio.Event()
res = await acct.market_book_get(
    "EURUSD",
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
print(len(res.Bids), len(res.Asks))
```

### 3) Compute VWAP of top N levels

```python
N = 5
book = await acct.market_book_get("BTCUSD")

# English-only comments per project style
def vwap(levels):
    take = levels[:N]
    vol = sum(l.Volume for l in take)
    return sum(l.Price * l.Volume for l in take) / vol if vol else None

print("vwap bid:", vwap(book.Bids))
print("vwap ask:", vwap(book.Asks))
```
