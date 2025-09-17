# ✅ Symbol Info Session Quote

> **Request:** get **quote session window** (time interval) for a **symbol** on a given **day of week** and **session index**.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_info_session_quote(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolInfoSessionQuote*` messages (`SymbolInfoSessionQuoteRequest`, `SymbolInfoSessionQuoteReply`, `SymbolInfoSessionQuoteData`) and enum `DayOfWeek`
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoSessionQuote(SymbolInfoSessionQuoteRequest) → SymbolInfoSessionQuoteReply`
* **Low-level client:** `MarketInfoStub.SymbolInfoSessionQuote(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_info_session_quote(symbol, day_of_week, session_index, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Get quote session window for Monday, session #0
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

sess = await acct.symbol_info_session_quote(
    "EURUSD",
    mi_pb2.DayOfWeek.MONDAY,
    0,
)
print(sess.from.seconds, sess.to.seconds)  # UTC seconds
```

---

### Method Signature

```python
async def symbol_info_session_quote(
    self,
    symbol: str,
    day_of_week: market_info_pb2.DayOfWeek,
    session_index: int,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolInfoSessionQuoteData
```

---

## 💬 Plain English

* **What it is.** Returns the **time window** when **quotes are available** for the symbol on a specific weekday.
* **Why you care.** Lets UIs gray‑out off‑market hours and lets strategies respect **session boundaries**.
* **Mind the traps.**

  * `session_index` is **zero‑based** (0, 1, 2, …). Many brokers have **0 or 1** session per day; some have breaks.
  * Timestamps are `google.protobuf.Timestamp` (UTC). Convert before showing.
  * If the session is **absent**, the window may be **empty** (both ends epoch or equal). Handle this gracefully.

---

## 🔽 Input

| Parameter            | Type                       | Description                                           |   |
| -------------------- | -------------------------- | ----------------------------------------------------- | - |
| `symbol`             | `str` (**required**)       | Symbol name.                                          |   |
| `day_of_week`        | `DayOfWeek` (**required**) | Weekday selector (enum below).                        |   |
| `session_index`      | `uint32` (**required**)    | Zero‑based session index within the selected weekday. |   |
| `deadline`           | `datetime \| None`         | Absolute per‑call deadline → converted to timeout.    |   |
| `cancellation_event` | `asyncio.Event \| None`    | Cooperative cancel for the retry wrapper.             |   |

> **Request message:** `SymbolInfoSessionQuoteRequest { symbol: string, day_of_week: DayOfWeek, session_index: uint32 }`

---

## ⬆️ Output

### Payload: `SymbolInfoSessionQuoteData`

| Field  | Proto Type                  | Description              |
| ------ | --------------------------- | ------------------------ |
| `from` | `google.protobuf.Timestamp` | Session **start** (UTC). |
| `to`   | `google.protobuf.Timestamp` | Session **end** (UTC).   |

> **Wire reply:** `SymbolInfoSessionQuoteReply { data: SymbolInfoSessionQuoteData, error: Error? }`
> SDK returns `reply.data`.

---

## Enum: `DayOfWeek`

| Number | Value       |
| -----: | ----------- |
|      0 | `SUNDAY`    |
|      1 | `MONDAY`    |
|      2 | `TUESDAY`   |
|      3 | `WEDNESDAY` |
|      4 | `THURSDAY`  |
|      5 | `FRIDAY`    |
|      6 | `SATURDAY`  |

---

### 🎯 Purpose

* Respect market hours in strategies and UI.
* Build weekly calendars with quote availability.
* Validate broker config (detect gaps or unexpected breaks).

### 🧩 Notes & Tips

* To enumerate all sessions for a day, keep increasing `session_index` until you get an **empty window**.
* For **trading** permissions (not just quoting), use `SymbolInfoSessionTrade`.

---

**See also:** [symbol\_info\_session\_trade.md](./symbol_info_session_trade.md), [symbol\_info\_tick.md](./symbol_info_tick.md), [symbol\_info\_string.md](./symbol_info_string.md)

## Usage Examples

### 1) Print all Monday sessions

```python
# English-only comments per project style
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

s = "XAUUSD"
for i in range(10):  # stop when window is empty
    w = await acct.symbol_info_session_quote(s, mi_pb2.DayOfWeek.MONDAY, i)
    if (not getattr(w, "from") or not getattr(w, "to") or w.from.seconds == 0 and w.to.seconds == 0):
        break
    print(i, w.from.seconds, w.to.seconds)
```

### 2) Convert to local time and format

```python
from datetime import datetime, timezone

w = await acct.symbol_info_session_quote("EURUSD", mi_pb2.DayOfWeek.FRIDAY, 0)
start = datetime.fromtimestamp(w.from.seconds, tz=timezone.utc)
end = datetime.fromtimestamp(w.to.seconds, tz=timezone.utc)
print(start.isoformat(), "→", end.isoformat())
```

### 3) Guard for off‑hours

```python
from datetime import datetime, timezone
import time

w = await acct.symbol_info_session_quote("BTCUSD", mi_pb2.DayOfWeek.SUNDAY, 0)
now_utc = datetime.now(timezone.utc).timestamp()
inside = (w.from.seconds <= now_utc <= w.to.seconds)
print("in session?", inside)
```
