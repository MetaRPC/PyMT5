# ✅ Symbol Info Tick

> **Request:** get the **latest tick** for a **symbol** (bid/ask/last, volumes, timestamps, flags) via a single RPC.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_info_tick(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolInfoTick*` messages (`SymbolInfoTickRequest`, `SymbolInfoTickRequestReply`) and payload `MrpcMqlTick`
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoTick(SymbolInfoTickRequest) → SymbolInfoTickRequestReply`
* **Low-level client:** `MarketInfoStub.SymbolInfoTick(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_info_tick(symbol, deadline=None, cancellation_event=None)` → returns **`MrpcMqlTick`**

---

### 🔗 Code Example

```python
# Fetch the latest tick and print bid/ask and age
from datetime import datetime, timezone

tick = await acct.symbol_info_tick("EURUSD")
print(tick.bid, tick.ask)
# compute age in seconds if 'time' is present
if getattr(tick, "time", 0):
    age = int(datetime.now(timezone.utc).timestamp() - tick.time)
    print("age sec:", age)
```

```python
# Ensure symbol is selected & synchronized first
s = "BTCUSD"
if not (await acct.symbol_is_synchronized(s)).is_synchronized:
    await acct.symbol_select(s, True)
    _ = await acct.symbol_is_synchronized(s)
print((await acct.symbol_info_tick(s)).bid)
```

```python
# Timeout-sensitive request
import asyncio
from datetime import datetime, timedelta, timezone

cancel_event = asyncio.Event()
res = await acct.symbol_info_tick(
    "EURUSD",
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
print(res.bid, res.ask)
```

---

### Method Signature

```python
async def symbol_info_tick(
    self,
    symbol: str,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.MrpcMqlTick
```

---

## 💬 Plain English

* **What it is.** The terminal’s **latest tick snapshot** for a symbol.
* **Why you care.** Power price widgets, quote ribbons, and freshness checks before trading ops.
* **Mind the traps.**

  * Ensure the symbol is **selected & synchronized**; otherwise fields can be zero/empty.
  * `time` and `time_msc` represent the tick time (seconds and milliseconds since epoch, UTC). Convert before display.

---

## 🔽 Input

| Parameter            | Type                 | Description                                |                                           |
| -------------------- | -------------------- | ------------------------------------------ | ----------------------------------------- |
| `symbol`             | `str` (**required**) | Symbol name (maps to `symbol` in request). |                                           |
| `deadline`           | \`datetime           | None\`                                     | Absolute per‑call deadline → timeout.     |
| `cancellation_event` | \`asyncio.Event      | None\`                                     | Cooperative cancel for the retry wrapper. |

> **Request message:** `SymbolInfoTickRequest { symbol: string }`

---

## ⬆️ Output

### Payload: `MrpcMqlTick`

| Field         | Proto Type | Description                                      |
| ------------- | ---------- | ------------------------------------------------ |
| `time`        | `int64`    | Tick time in **seconds** since epoch (UTC).      |
| `bid`         | `double`   | Current best bid.                                |
| `ask`         | `double`   | Current best ask.                                |
| `last`        | `double`   | Last trade price (if applicable).                |
| `volume`      | `uint64`   | Tick volume (integer).                           |
| `time_msc`    | `int64`    | Tick time in **milliseconds** since epoch (UTC). |
| `flags`       | `uint32`   | Tick flags (bitmask).                            |
| `volume_real` | `double`   | Real volume (if provided by broker).             |

> **Wire reply:** `SymbolInfoTickRequestReply { data: MrpcMqlTick, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Render live **quote tiles** and price ribbons.
* Assess **freshness** of data (how old the last tick is).
* Drive downstream logic (spread display, slippage checks, etc.).

### 🧩 Notes & Tips

* If `bid/ask` are zeros or time is stale, call `symbol_is_synchronized(...)` and/or `symbol_select(symbol, True)` then retry.
* For derived metrics: spread = `ask - bid`; mid = `(ask + bid) / 2`.

---

**See also:** [symbol\_info\_double.md](./symbol_info_double.md), [symbol\_info\_integer.md](./symbol_info_integer.md), [on\_symbol\_tick.md](../Subscriptions_Streaming/on_symbol_tick.md)

## Usage Examples

### 1) Basic usage with freshness guard

```python
from datetime import datetime, timezone

s = "XAUUSD"
t = await acct.symbol_info_tick(s)
mid = (t.bid + t.ask) / 2 if (t.bid and t.ask) else None
age = None
if getattr(t, "time", 0):
    age = int(datetime.now(timezone.utc).timestamp() - t.time)
print(s, "mid=", mid, "age=", age)
```

### 2) Compute spread & mid

```python
x = await acct.symbol_info_tick("EURUSD")
spread = (x.ask - x.bid) if (x.ask and x.bid) else None
mid = (x.ask + x.bid) / 2 if (x.ask and x.bid) else None
print("spread:", spread, "mid:", mid)
```

### 3) Timeout‑sensitive request (with cancel)

```python
import asyncio
from datetime import datetime, timedelta, timezone

cancel_event = asyncio.Event()
res = await acct.symbol_info_tick(
    "EURUSD",
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
print(res.bid, res.ask)
```
