# ✅ Market Book Get 

> **Request:** fetch a **snapshot of the Level II order book** (bids/asks ladder) for a **symbol**.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `market_book_get(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `MarketBookGet*` messages (`MarketBookGetRequest`, `MarketBookGetReply`, `MarketBookGetData`, `MrpcMqlBookInfo`, enum `BookType`)
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

## RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `MarketBookGet(MarketBookGetRequest) → MarketBookGetReply`
* **Low-level client:** `MarketInfoStub.MarketBookGet(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.market_book_get(symbol, deadline=None, cancellation_event=None)`

---

## 🔗 Code Example 

```python
# Fetch DOM snapshot and print top-of-book using mql_book_infos
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

book = await acct.market_book_get("EURUSD")
rows = list(getattr(book, "mql_book_infos", []))

# Split by side (limit levels)
bids = [r for r in rows if r.type == mi_pb2.BookType.BOOK_TYPE_BUY]
asks = [r for r in rows if r.type == mi_pb2.BookType.BOOK_TYPE_SELL]

# Sort: bids desc, asks asc
bids.sort(key=lambda r: float(r.price), reverse=True)
asks.sort(key=lambda r: float(r.price))

if bids and asks:
    best_bid, best_ask = bids[0], asks[0]
    spread = float(best_ask.price) - float(best_bid.price)
    print(best_bid.price, best_ask.price, spread)
else:
    print("Empty book (no depth for this symbol/broker).")
```

---

## Method Signature

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

* **What it is.** A one-shot **depth snapshot**: aggregated price/volume levels tagged as **BID**/**ASK** (and optional `*_MARKET`).
* **Why you care.** Power depth widgets, slippage models, and liquidity checks before order placement.
* **Mind the traps.**

  * Some brokers expose limited depth (e.g., 5 levels) or none → the list can be **empty**.
  * Calling `market_book_add(symbol)` enables streaming; snapshots can work without it but won’t auto‑update.
  * Price order convention: **BIDs** descending, **ASKs** ascending; sort client‑side as needed.

---

## 🔽 Input

| Parameter            | Type                 | Description                                |                                           |
| -------------------- | -------------------- | ------------------------------------------ | ----------------------------------------- |
| `symbol`             | `str` (**required**) | Symbol name (maps to `symbol` in request). |                                           |
| `deadline`           | \`datetime           | None\`                                     | Absolute per‑call deadline → timeout.     |
| `cancellation_event` | \`asyncio.Event      | None\`                                     | Cooperative cancel for the retry wrapper. |

> **Request message:** `MarketBookGetRequest { symbol: string }`

---

## ⬆️ Output

### Payload: `MarketBookGetData`

| Field              | Proto Type        | Description                   |
| ------------------ | ----------------- | ----------------------------- |
| `mql_book_infos[]` | `MrpcMqlBookInfo` | Unified list of depth levels. |

#### `MrpcMqlBookInfo`

| Field         | Proto Type | Description                                                                            |
| ------------- | ---------- | -------------------------------------------------------------------------------------- |
| `type`        | `BookType` | Side/type: `BOOK_TYPE_BUY` (= **BID**), `BOOK_TYPE_SELL` (= **ASK**), plus `*_MARKET`. |
| `price`       | `double`   | Price for this level.                                                                  |
| `volume`      | `int64`    | Size/volume at this price level (integer).                                             |
| `volume_real` | `double`   | Real volume (if provided by the broker; otherwise 0).                                  |

> **Wire reply:** `MarketBookGetReply { data: MarketBookGetData, error: Error? }` — SDK returns `reply.data`.

---

## 🎯 Purpose

* Render a **DOM** view and compute top‑of‑book spread.
* Feed execution logic (iceberg detection, slippage estimates, partial fill planning).
* Monitor liquidity changes for alerts.

---

## 🧩 Notes & Tips

* Pair with `market_book_add` and `market_book_release` to manage subscription lifecycle.
* If you need to treat market prints separately, filter `BOOK_TYPE_*_MARKET` types into distinct lists.

---

## Usage Examples

### 1) Render a compact depth table

```python
book = await acct.market_book_get("XAUUSD")
rows = list(getattr(book, "mql_book_infos", []))

bids = sorted((r for r in rows if r.type == mi_pb2.BookType.BOOK_TYPE_BUY), key=lambda r: r.price, reverse=True)
asks = sorted((r for r in rows if r.type == mi_pb2.BookType.BOOK_TYPE_SELL), key=lambda r: r.price)

print("BID       VOL   |   ASK       VOL")
for i in range(max(len(bids), len(asks))):
    b = bids[i] if i < len(bids) else None
    a = asks[i] if i < len(asks) else None
    print(f"{getattr(b,'price',None):>8} {getattr(b,'volume',None):>6} | {getattr(a,'price',None):>8} {getattr(a,'volume',None):>6}")
```

### 2) With deadline & cancel

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

cancel_event = asyncio.Event()
res = await acct.market_book_get(
    "EURUSD",
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
rows = list(getattr(res, "mql_book_infos", []))
print(len(rows))
```

### 3) Compute VWAP of top N bids/asks

```python
N = 5
book = await acct.market_book_get("BTCUSD")
rows = list(getattr(book, "mql_book_infos", []))

bids = sorted((r for r in rows if r.type == mi_pb2.BookType.BOOK_TYPE_BUY), key=lambda r: r.price, reverse=True)[:N]
asks = sorted((r for r in rows if r.type == mi_pb2.BookType.BOOK_TYPE_SELL), key=lambda r: r.price)[:N]

def vwap(rs):
    vol = sum(r.volume for r in rs)
    return sum(r.price * r.volume for r in rs) / vol if vol else None

print("vwap bid:", vwap(bids))
print("vwap ask:", vwap(asks))
```
