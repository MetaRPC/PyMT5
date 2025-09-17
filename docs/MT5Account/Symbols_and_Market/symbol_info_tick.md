# ✅ Symbol Info Tick

> **Request:** get the **latest tick** for a **symbol** (bid/ask/last, volumes, timestamps, flags) via a single RPC.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_info_tick(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolInfoTick*` messages (`SymbolInfoTickRequest`, `SymbolInfoTickReply`, `SymbolInfoTickData`)
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoTick(SymbolInfoTickRequest) → SymbolInfoTickReply`
* **Low-level client:** `MarketInfoStub.SymbolInfoTick(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_info_tick(symbol, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Fetch the latest tick and print bid/ask and age
from datetime import datetime, timezone

tick = await acct.symbol_info_tick("EURUSD")
print(tick.Bid, tick.Ask)
# compute age in seconds if Time is available
if hasattr(tick, "Time") and tick.Time.seconds:
    age = datetime.now(timezone.utc).timestamp() - tick.Time.seconds
    print("age sec:", int(age))
```

---

### Method Signature

```python
async def symbol_info_tick(
    self,
    symbol: str,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolInfoTickData
```

---

## 💬 Plain English

* **What it is.** The terminal’s **latest tick snapshot** for a symbol.
* **Why you care.** Power price widgets, quote ribbons, and freshness checks before trading ops.
* **Mind the traps.**

  * Ensure the symbol is **selected & synchronized**; otherwise some fields can be zero/empty.
  * `Time` and `TimeMsc` represent the tick time (seconds and milliseconds). Convert before display.

---

## 🔽 Input

| Parameter            | Type                 | Description                                |                                                    |   |
| -------------------- | -------------------- | ------------------------------------------ | -------------------------------------------------- | - |
| `symbol`             | `str` (**required**) | Symbol name (maps to `symbol` in request). |                                                    |   |
| `deadline`           | \`datetime           | None\`                                     | Absolute per‑call deadline → converted to timeout. |   |
| `cancellation_event` | \`asyncio.Event      | None\`                                     | Cooperative cancel for the retry wrapper.          |   |

> **Request message:** `SymbolInfoTickRequest { symbol: string }`

---

## ⬆️ Output

### Payload: `SymbolInfoTickData`

| Field        | Proto Type                  | Description                                  |
| ------------ | --------------------------- | -------------------------------------------- |
| `Bid`        | `double`                    | Current best bid.                            |
| `Ask`        | `double`                    | Current best ask.                            |
| `Last`       | `double`                    | Last trade price (if applicable).            |
| `Volume`     | `uint64`                    | Tick volume (integer).                       |
| `VolumeReal` | `double`                    | Real volume (if provided by broker).         |
| `Flags`      | `uint32`                    | Tick flags (bitmask).                        |
| `Time`       | `google.protobuf.Timestamp` | Tick time (seconds precision, UTC).          |
| `TimeMsc`    | `int64`                     | Tick time in milliseconds since epoch (UTC). |

> **Wire reply:** `SymbolInfoTickReply { data: SymbolInfoTickData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Render live **quote tiles** and price ribbons.
* Assess **freshness** of data (how old the last tick is).
* Drive downstream logic (slippage checks, spread display, etc.).

### 🧩 Notes & Tips

* If `Bid/Ask` are zeros or time is stale, call `symbol_is_synchronized(...)` and/or `symbol_select(symbol, True)` then retry.
* For derived metrics: spread = `Ask - Bid`; mid = `(Ask + Bid) / 2`.

---

## Usage Examples

### 1) Basic usage with freshness guard

```python
from datetime import datetime, timezone

s = "XAUUSD"
t = await acct.symbol_info_tick(s)
mid = (t.Bid + t.Ask) / 2 if (t.Bid and t.Ask) else None
age = None
if hasattr(t, "Time") and t.Time.seconds:
    age = int(datetime.now(timezone.utc).timestamp() - t.Time.seconds)
print(s, "mid=", mid, "age=", age)
```

### 2) Ensure selected & synchronized first

```python
s = "BTCUSD"
if not (await acct.symbol_is_synchronized(s)).is_synchronized:
    await acct.symbol_select(s, True)
    _ = await acct.symbol_is_synchronized(s)
print((await acct.symbol_info_tick(s)).Bid)
```

### 3) Timeout‑sensitive request

```python
import asyncio
from datetime import datetime, timedelta, timezone

cancel_event = asyncio.Event()
res = await acct.symbol_info_tick(
    "EURUSD",
    deadline=datetime.now(timezone.utc) + timedelta(seconds=2),
    cancellation_event=cancel_event,
)
print(res.Bid, res.Ask)
```
