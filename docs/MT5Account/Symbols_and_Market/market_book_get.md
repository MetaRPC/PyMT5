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
# Fetch current DOM snapshot and print top-of-book (best bid/ask)
book = await acct.market_book_get("EURUSD")
levels = getattr(book, "levels", None) or getattr(book, "entries", None)
if levels:
    bids = [e for e in levels if int(getattr(e, "entry_type", getattr(e, "type", 0))) == 1]
    asks = [e for e in levels if int(getattr(e, "entry_type", getattr(e, "type", 0))) == 2]
    bids.sort(key=lambda x: float(x.price), reverse=True)
    asks.sort(key=lambda x: float(x.price))
    if bids and asks:
        best_bid, best_ask = bids[0], asks[0]
        spread = float(best_ask.price) - float(best_bid.price)
        print(best_bid.price, best_ask.price, spread)
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

* **What it is.** A one-shot **depth snapshot**: aggregated price/volume levels tagged as **BID** or **ASK**.
* **Why you care.** Power depth widgets, slippage models, and liquidity checks before order placement.
* **Mind the traps.**

  * Some brokers expose limited depth (e.g., 5 levels) or none → the level list can be **empty**.
  * Call `market_book_add(symbol)` beforehand to enable the feed; snapshots may still work but won’t auto-update.
  * Price order convention: **BIDs** descending, **ASKs** ascending; sort client‑side as needed.

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

| Field    | Proto Type               | Description                                     |
| -------- | ------------------------ | ----------------------------------------------- |
| `levels` | `repeated MarketBookRow` | Unified list of depth levels (**BID**/**ASK**). |

#### `MarketBookRow`

| Field        | Proto Type | Description                      |
| ------------ | ---------- | -------------------------------- |
| `entry_type` | `int32`    | **1 = BID**, **2 = ASK**.        |
| `price`      | `double`   | Price for this level.            |
| `volume`     | `double`   | Volume/size at this price level. |

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

**See also:** [market\_book\_add.md](./market_book_add.md), [market\_book\_release.md](./market_book_release.md), [on\_symbol\_tick.md](../Subscriptions_Streaming/on_symbol_tick.md)

## Usage Examples

### 1) Render a compact depth table

```python
book = await acct.market_book_get("XAUUSD")
levels = getattr(book, "levels", None) or getattr(book, "entries", None) or []
# split and sort
bids = sorted((e for e in levels if int(getattr(e, "entry_type", getattr(e, "type", 0))) == 1), key=lambda x: x.price, reverse=True)
asks = sorted((e for e in levels if int(getattr(e, "entry_type", getattr(e, "type", 0))) == 2), key=lambda x: x.price)
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

cancel_event = asyncio.Event()
res = await acct.market_book_get(
    "EURUSD",
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
levels = getattr(res, "levels", None) or getattr(res, "entries", None) or []
print(len(levels))
```

### 3) Compute VWAP of top N bids/asks

```python
N = 5
book = await acct.market_book_get("BTCUSD")
levels = getattr(book, "levels", None) or getattr(book, "entries", None) or []
bids = sorted((e for e in levels if int(getattr(e, "entry_type", getattr(e, "type", 0))) == 1), key=lambda x: x.price, reverse=True)[:N]
asks = sorted((e for e in levels if int(getattr(e, "entry_type", getattr(e, "type", 0))) == 2), key=lambda x: x.price)[:N]

def vwap(rows):
    vol = sum(r.volume for r in rows)
    return sum(r.price * r.volume for r in rows) / vol if vol else None

print("vwap bid:", vwap(bids))
print("vwap ask:", vwap(asks))
```
