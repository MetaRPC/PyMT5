# ✅ On Symbol Tick

> **Request:** subscribe to **live ticks** for one **symbol** (SDK wrapper) via a server‑streaming RPC that emits events with Bid/Ask/Last, volumes, flags, and time.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `on_symbol_tick(...)`
* `MetaRpcMT5/mt5_term_api_subscriptions_pb2.py` — `OnSymbolTick*` messages (request/reply/data/event)
* `MetaRpcMT5/mt5_term_api_subscriptions_pb2_grpc.py` — service stub `SubscriptionServiceStub`

---

### RPC

* **Service:** `mt5_term_api.SubscriptionService`
* **Method:** `OnSymbolTick(OnSymbolTickRequest) → stream OnSymbolTickReply`
* **Low‑level client:** `SubscriptionServiceStub.OnSymbolTick(request, metadata, timeout)` *(server‑streaming iterator)*
* **SDK wrapper:** `MT5Account.on_symbol_tick(symbol, deadline=None, cancellation_event=None) → async stream of SymbolTickEvent`

---

### 🔗 Code Example

```python
# Minimal canonical example: stream ticks for one symbol (SDK wrapper takes a single symbol)
async for ev in acct.on_symbol_tick("EURUSD"):
    # ev: SymbolTickEvent
    print(ev.name, ev.bid, ev.ask)
```

```python
# With cooperative cancellation (stop after first 10 events)
import asyncio

cancel = asyncio.Event()
count = 0
async for ev in acct.on_symbol_tick("EURUSD", cancellation_event=cancel):
    spread = (ev.ask - ev.bid) if (ev.ask is not None and ev.bid is not None) else None
    print(ev.name, ev.bid, ev.ask, spread)
    count += 1
    if count >= 10:
        cancel.set()
```

---

### Method Signature

```python
async def on_symbol_tick(
    self,
    symbol: str,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> subscription_client.OnSymbolTick  # async iterable of SymbolTickEvent
```

---

## 🔽 Input

| Parameter            | Type                 | Description                  |                                                     |
| -------------------- | -------------------- | ---------------------------- | --------------------------------------------------- |
| `symbol`             | `str` (**required**) | Symbol name to subscribe to. |                                                     |
| `deadline`           | \`datetime           | None\`                       | Absolute deadline; converted to client‑side timeout |
| `cancellation_event` | \`asyncio.Event      | None\`                       | Cooperative stop for the streaming RPC.             |

> **Request message:** `OnSymbolTickRequest { symbol_name: string }`

---

## ⬆️ Output

### Stream payload: `SymbolTickEvent`

> *Emitted repeatedly for the subscribed symbol.*

| Field         | Proto Type                  | Description                                  |
| ------------- | --------------------------- | -------------------------------------------- |
| `name`        | `string`                    | Symbol name.                                 |
| `bid`         | `double`                    | Current bid.                                 |
| `ask`         | `double`                    | Current ask.                                 |
| `last`        | `double`                    | Last trade price (if applicable).            |
| `volume`      | `uint64`                    | Tick volume.                                 |
| `volume_real` | `double`                    | Real volume (if provided by broker).         |
| `flags`       | `uint32`                    | Tick flags (bitmask).                        |
| `time`        | `google.protobuf.Timestamp` | Tick time (UTC seconds).                     |
| `time_msc`    | `int64`                     | Tick time in milliseconds since epoch (UTC). |

> **Wire stream:** `OnSymbolTickReply { data: SymbolTickEvent, error?: Error }`
> SDK wrapper yields `SymbolTickEvent` objects one by one.

---

### 🎯 Purpose

* Feed **real‑time quotes** to dashboards, chart overlays, and algos.
* Compute derived metrics (spread, mid, microstructure) on the fly.
* Power **alerts** (e.g., price thresholds, stale‑tick detection).

### 🧩 Notes & Tips

* Ensure the symbol is **selected/synchronized** (e.g., via `symbol_select` / `symbol_is_synchronized`) before subscribing.
* For depth/DOM, use the market book APIs: `market_book_add / market_book_get / market_book_release`.

---

**See also:** [symbol\_info\_tick.md](../Symbols_and_Market/symbol_info_tick.md), [on\_positions\_and\_pending\_orders\_tickets.md](./on_positions_and_pending_orders_tickets.md), [on\_trade.md](./on_trade.md)

## Usage Examples

### 1) Compute mid only for EURUSD

```python
async for ev in acct.on_symbol_tick("EURUSD"):
    mid = (ev.bid + ev.ask) / 2 if (ev.bid is not None and ev.ask is not None) else None
    print("mid:", mid)
```

### 2) Timeout guard via external task

```python
import asyncio

cancel = asyncio.Event()
async def watchdog():
    await asyncio.sleep(5)
    cancel.set()

asyncio.create_task(watchdog())
async for ev in acct.on_symbol_tick("XAUUSD", cancellation_event=cancel):
    print(ev.name, ev.bid)
```

### 3) Queue back‑pressure for UI

```python
from asyncio import Queue
q = Queue(maxsize=100)

async for ev in acct.on_symbol_tick("BTCUSD"):
    if q.full():
        _ = q.get_nowait()
    await q.put(ev)
```
