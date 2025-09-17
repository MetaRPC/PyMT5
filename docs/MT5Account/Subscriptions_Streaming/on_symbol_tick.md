# ✅ On Symbol Tick

> **Request:** subscribe to **live ticks** for one or more **symbols**. Server‑streaming RPC that emits events with Bid/Ask/Last, volumes, flags, and time.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `on_symbol_tick(...)`
* `MetaRpcMT5/mt5_term_api_subscription_pb2.py` — `OnSymbolTick*` messages (request/reply/data/event)
* `MetaRpcMT5/mt5_term_api_subscription_pb2_grpc.py` — service stub `SubscriptionStub`

### RPC

* **Service:** `mt5_term_api.Subscription`
* **Method:** `OnSymbolTick(OnSymbolTickRequest) → stream OnSymbolTickReply`
* **Low-level client:** `SubscriptionStub.OnSymbolTick(request, metadata, timeout)` *(server‑streaming iterator)*
* **SDK wrapper:** `MT5Account.on_symbol_tick(symbols, cancellation_event=None) → Async stream of SymbolTickEvent`

---

### 🔗 Code Example

```python
# Minimal canonical example: stream ticks for two symbols
async for ev in acct.on_symbol_tick(["EURUSD", "XAUUSD"]):
    # ev: SymbolTickEvent
    print(ev.name, ev.bid, ev.ask)
```

```python
# With cooperative cancellation (stop after first 10 events)
import asyncio

cancel = asyncio.Event()
count = 0
async for ev in acct.on_symbol_tick(["EURUSD"], cancellation_event=cancel):
    spread = (ev.ask - ev.bid) if (ev.ask and ev.bid) else None
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
    symbols: list[str],
    cancellation_event: asyncio.Event | None = None,
) -> subscription_client.OnSymbolTick  # async iterable of SymbolTickEvent
```

---

## 💬 Just about the main thing

* **What is it.** A **live stream** of tick updates for specified symbols.
* **Why.** Drive real‑time widgets, alerts, and execution logic without polling.
* **Be careful.**

  * Symbols must exist and be **synchronized**; otherwise events may be sparse/empty.
  * This is a **long‑lived** call — remember to cancel via `cancellation_event` when your UI page closes.
  * Timestamps are UTC; `time_msc` is milliseconds since epoch if provided.

---

## 🔽 Input

| Parameter            | Type                       | Description                   |                                         |   |
| -------------------- | -------------------------- | ----------------------------- | --------------------------------------- | - |
| `symbols`            | `list[str]` (**required**) | Symbol names to subscribe to. |                                         |   |
| `cancellation_event` | \`asyncio.Event            | None\`                        | Cooperative stop for the streaming RPC. |   |

> **Request message:** `OnSymbolTickRequest { symbol_names: repeated string }`

---

## ⬆️ Output

### Stream payload: `SymbolTickEvent`

> *Emitted repeatedly for each subscribed symbol.*

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

* Combine with `symbol_is_synchronized` and `symbol_select` before subscribing to reduce empty updates.
* For depth/DOM, use the **market book** triplet instead: `market_book_add/get/release`.

---

## Usage Examples

### 1) Filter by symbol and compute mid

```python
async for ev in acct.on_symbol_tick(["EURUSD", "GBPUSD"]):
    if ev.name != "EURUSD":
        continue
    mid = (ev.bid + ev.ask) / 2 if ev.bid and ev.ask else None
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
async for ev in acct.on_symbol_tick(["XAUUSD"], cancellation_event=cancel):
    print(ev.name, ev.bid)
```

### 3) Wire into a queue for UI

```python
from asyncio import Queue
q = Queue(maxsize=100)

async for ev in acct.on_symbol_tick(["BTCUSD"], cancellation_event=None):
    if q.full():
        _ = q.get_nowait()
    await q.put(ev)
```
