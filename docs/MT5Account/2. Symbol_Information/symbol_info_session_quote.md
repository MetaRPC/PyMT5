# Get Symbol Quote Session Times

> **Request:** retrieve quote session start and end times for symbol.

**API Information:**

* **Low-level API:** `MT5Account.symbol_info_session_quote(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolInfoSessionQuote` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoSessionQuote(SymbolInfoSessionQuoteRequest) -> SymbolInfoSessionQuoteReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolInfoSessionQuote(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Retrieve quote session start and end times for a symbol on a specific day of the week.
* **Why you need it.** Know when you can receive price quotes for symbols, understand market hours.
* **When to use.** Use to check symbol quote availability, plan automated trading schedules, validate market open times.

---

## 🎯 Purpose

Use it to query quote session schedules:

* Get symbol quote session hours for each day
* Check when price updates are available
* Validate market open/close times
* Plan quote monitoring schedules
* Understand session breaks
* Coordinate with trading sessions

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_info_session_quote - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_quote_HOW.md)**

---

## Method Signature

```python
async def symbol_info_session_quote(
    self,
    symbol: str,
    day_of_week: market_info_pb2.DayOfWeek,
    session_index: int,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoSessionQuoteData
```

**Request message:**

```protobuf
message SymbolInfoSessionQuoteRequest {
  string symbol = 1;
  DayOfWeek day_of_week = 2;
  uint32 session_index = 3;
}
```

**Reply message:**

```protobuf
message SymbolInfoSessionQuoteReply {
  oneof response {
    SymbolInfoSessionQuoteData data = 1;
    Error error = 2;
  }
}

message SymbolInfoSessionQuoteData {
  google.protobuf.Timestamp from = 1;
  google.protobuf.Timestamp to = 2;
}
```

---

## 🔽 Input

| Parameter       | Type                      | Description                  |
| --------------- | ------------------------- | ---------------------------- |
| `symbol`        | `str` (required)          | Symbol name                  |
| `day_of_week`   | `DayOfWeek` (enum)        | Day of week (SUNDAY, MONDAY, etc.) |
| `session_index` | `int` (required)          | Session index (usually 0 for main session) |
| `deadline`    | `datetime` (optional)     | Deadline for the gRPC call (UTC datetime) |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation |

---

## ⬆️ Output

| Field   | Type        | Python Type | Description           |
| ------- | ----------- | ----------- | --------------------- |
| `from`  | `Timestamp` | `Timestamp` | Session start time (google.protobuf.Timestamp) |
| `to`    | `Timestamp` | `Timestamp` | Session end time (google.protobuf.Timestamp)   |

**Return value:** The method returns `SymbolInfoSessionQuoteData` object with `from` and `to` Timestamp fields.

---

## 🧱 Related enums (from proto)

> **Note:** In Python code, use constants directly from the market_info module.

### `DayOfWeek`

Defined in `mt5-term-api-market-info.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `SUNDAY` | 0 | Sunday |
| `MONDAY` | 1 | Monday |
| `TUESDAY` | 2 | Tuesday |
| `WEDNESDAY` | 3 | Wednesday |
| `THURSDAY` | 4 | Thursday |
| `FRIDAY` | 5 | Friday |
| `SATURDAY` | 6 | Saturday |

**Usage in Python:**
```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get Monday quote session
session = await account.symbol_info_session_quote(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)
print(f"From: {session.from.seconds}s, To: {session.to.seconds}s")
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Timestamp format:** The `from` and `to` fields are `google.protobuf.Timestamp` objects with `seconds` and `nanos` attributes.
* **Time interpretation:** Times represent seconds from midnight (00:00) for the specified day.
* **Session index:** Most symbols have one main session (index 0). Some may have multiple sessions (lunch breaks, etc.).
* **Multiple sessions:** If a symbol has multiple quote sessions per day, use different session_index values (0, 1, 2...).
* **Timezone:** Times are in the broker's server timezone, not UTC.
* **No session:** If a session doesn't exist, the method may return an error or zero timestamps.

---

## 🔗 Usage Examples

### 1) Get Monday quote session

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get Monday quote session
session = await account.symbol_info_session_quote(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

print(f"Monday Quote Session:")
print(f"  From: {session.from.seconds}s ({session.from.seconds // 3600}h:{(session.from.seconds % 3600) // 60}m)")
print(f"  To: {session.to.seconds}s ({session.to.seconds // 3600}h:{(session.to.seconds % 3600) // 60}m)")
```

### 2) Get all weekly quote sessions

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

days = {
    market_info_pb2.SUNDAY: "Sunday",
    market_info_pb2.MONDAY: "Monday",
    market_info_pb2.TUESDAY: "Tuesday",
    market_info_pb2.WEDNESDAY: "Wednesday",
    market_info_pb2.THURSDAY: "Thursday",
    market_info_pb2.FRIDAY: "Friday",
    market_info_pb2.SATURDAY: "Saturday"
}

print("EURUSD Quote Sessions:")
for day_enum, day_name in days.items():
    try:
        session = await account.symbol_info_session_quote(
            symbol="EURUSD",
            day_of_week=day_enum,
            session_index=0
        )

        from_hours = session.from.seconds // 3600
        from_mins = (session.from.seconds % 3600) // 60
        to_hours = session.to.seconds // 3600
        to_mins = (session.to.seconds % 3600) // 60

        print(f"  {day_name:10s} {from_hours:02d}:{from_mins:02d} - {to_hours:02d}:{to_mins:02d}")
    except Exception as e:
        print(f"  {day_name:10s} No session")
```

### 3) Convert timestamp to readable time

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import time

def timestamp_to_time(timestamp) -> time:
    """Convert protobuf Timestamp to datetime.time"""
    total_seconds = timestamp.seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return time(hour=hours, minute=minutes, second=seconds)

# Get session
session = await account.symbol_info_session_quote(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

# Convert to time objects
from_time = timestamp_to_time(session.from)
to_time = timestamp_to_time(session.to)

print(f"Quote session: {from_time} - {to_time}")
# Output: Quote session: 00:00:00 - 23:59:59
```

### 4) Check if symbol has quote session on specific day

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def has_quote_session(account, symbol: str, day_of_week: int) -> bool:
    """Check if symbol has quote session on specified day"""
    try:
        session = await account.symbol_info_session_quote(
            symbol=symbol,
            day_of_week=day_of_week,
            session_index=0
        )

        # Check if session has valid times (not zero)
        if session.from.seconds > 0 or session.to.seconds > 0:
            return True
        return False
    except Exception:
        return False

# Usage
if await has_quote_session(account, "EURUSD", market_info_pb2.SATURDAY):
    print("EURUSD has quotes on Saturday")
else:
    print("EURUSD has NO quotes on Saturday")
```

### 5) Get session with timeout

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta

deadline = datetime.utcnow() + timedelta(seconds=3)

try:
    session = await account.symbol_info_session_quote(
        symbol="GBPUSD",
        day_of_week=market_info_pb2.FRIDAY,
        session_index=0,
        deadline=deadline
    )
    print(f"Session retrieved successfully")
except Exception as e:
    print(f"Timeout or error: {e}")
```

### 6) Check for multiple sessions (lunch breaks)

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_sessions(account, symbol: str, day_of_week: int):
    """Get all quote sessions for a symbol on a specific day"""
    sessions = []
    session_index = 0

    while session_index < 10:  # Max 10 sessions
        try:
            session = await account.symbol_info_session_quote(
                symbol=symbol,
                day_of_week=day_of_week,
                session_index=session_index
            )

            # Check if session is valid
            if session.from.seconds == 0 and session.to.seconds == 0:
                break

            sessions.append({
                'index': session_index,
                'from': session.from.seconds,
                'to': session.to.seconds
            })
            session_index += 1
        except Exception:
            break

    return sessions

# Usage
sessions = await get_all_sessions(account, "NIKKEI", market_info_pb2.MONDAY)
print(f"Found {len(sessions)} quote session(s):")
for s in sessions:
    from_h = s['from'] // 3600
    from_m = (s['from'] % 3600) // 60
    to_h = s['to'] // 3600
    to_m = (s['to'] % 3600) // 60
    print(f"  Session {s['index']}: {from_h:02d}:{from_m:02d} - {to_h:02d}:{to_m:02d}")
```

---

## 📚 See also

* [symbol_info_session_trade](./symbol_info_session_trade.md) - Get trading session times
* [symbol_info_integer](./symbol_info_integer.md) - Get other symbol integer properties
* [symbol_info_double](./symbol_info_double.md) - Get symbol double properties
