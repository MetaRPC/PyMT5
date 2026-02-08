# Get Symbol Trade Session Times

> **Request:** retrieve trade session start and end times for symbol.

**API Information:**

* **Low-level API:** `MT5Account.symbol_info_session_trade(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolInfoSessionTrade` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoSessionTrade(SymbolInfoSessionTradeRequest) -> SymbolInfoSessionTradeReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolInfoSessionTrade(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Retrieve trade session start and end times for a symbol on a specific day of the week.
* **Why you need it.** Know when you can place trades for symbols, understand trading hours vs quote hours.
* **When to use.** Use to check when trading is allowed, validate order placement times, plan automated trading schedules.

---

## 🎯 Purpose

Use it to query trade session schedules:

* Get symbol trade session hours for each day
* Check when order placement is allowed
* Validate trading hours vs quote hours
* Plan automated trading schedules
* Understand session breaks
* Coordinate with market hours

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_info_session_trade - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_trade_HOW.md)**

---

## Method Signature

```python
async def symbol_info_session_trade(
    self,
    symbol: str,
    day_of_week: market_info_pb2.DayOfWeek,
    session_index: int,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoSessionTradeData
```

**Request message:**

```protobuf
message SymbolInfoSessionTradeRequest {
  string symbol = 1;
  DayOfWeek day_of_week = 2;
  uint32 session_index = 3;
}
```

**Reply message:**

```protobuf
message SymbolInfoSessionTradeReply {
  oneof response {
    SymbolInfoSessionTradeData data = 1;
    Error error = 2;
  }
}

message SymbolInfoSessionTradeData {
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

**Return value:** The method returns `SymbolInfoSessionTradeData` object with `from` and `to` Timestamp fields.

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

# Get Monday trading session
session = await account.symbol_info_session_trade(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)
print(f"Trading hours: {session.from.seconds}s - {session.to.seconds}s")
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Timestamp format:** The `from` and `to` fields are `google.protobuf.Timestamp` objects with `seconds` and `nanos` attributes.
* **Time interpretation:** Times represent seconds from midnight (00:00) for the specified day.
* **Session index:** Most symbols have one main session (index 0). Some may have multiple sessions (lunch breaks, etc.).
* **Multiple sessions:** If a symbol has multiple trade sessions per day, use different session_index values (0, 1, 2...).
* **Timezone:** Times are in the broker's server timezone, not UTC.
* **No session:** If a session doesn't exist, the method may return an error or zero timestamps.
* **Trade vs Quote sessions:** Trade sessions (when orders can be placed) may differ from quote sessions (when prices update). Use both methods to understand full market schedule.

---

## 🔗 Usage Examples

### 1) Get Monday trade session

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get Monday trade session
session = await account.symbol_info_session_trade(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

print(f"Monday Trade Session:")
print(f"  From: {session.from.seconds}s ({session.from.seconds // 3600}h:{(session.from.seconds % 3600) // 60}m)")
print(f"  To: {session.to.seconds}s ({session.to.seconds // 3600}h:{(session.to.seconds % 3600) // 60}m)")
```

### 2) Get all weekly trade sessions

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

print("EURUSD Trade Sessions:")
for day_enum, day_name in days.items():
    try:
        session = await account.symbol_info_session_trade(
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

### 3) Compare trade vs quote sessions

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get trade session
trade_session = await account.symbol_info_session_trade(
    symbol="XAUUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

# Get quote session
quote_session = await account.symbol_info_session_quote(
    symbol="XAUUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

print(f"XAUUSD Monday Sessions:")
print(f"  Trade: {trade_session.from.seconds // 3600:02d}:{(trade_session.from.seconds % 3600) // 60:02d} - {trade_session.to.seconds // 3600:02d}:{(trade_session.to.seconds % 3600) // 60:02d}")
print(f"  Quote: {quote_session.from.seconds // 3600:02d}:{(quote_session.from.seconds % 3600) // 60:02d} - {quote_session.to.seconds // 3600:02d}:{(quote_session.to.seconds % 3600) // 60:02d}")

if trade_session.from.seconds != quote_session.from.seconds:
    print("  Trade and quote sessions differ!")
```

### 4) Check if trading is allowed now

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime

async def is_trading_allowed(account, symbol: str) -> bool:
    """Check if trading is allowed at current time"""
    now = datetime.utcnow()
    day_of_week = now.weekday() + 1  # Monday=1 in datetime, Monday=1 in enum
    if day_of_week == 7:  # Sunday
        day_of_week = 0

    try:
        session = await account.symbol_info_session_trade(
            symbol=symbol,
            day_of_week=day_of_week,
            session_index=0
        )

        # Current time in seconds from midnight
        current_seconds = now.hour * 3600 + now.minute * 60 + now.second

        # Check if within trading session
        if session.from.seconds <= current_seconds <= session.to.seconds:
            return True
        return False
    except Exception:
        return False

# Usage
if await is_trading_allowed(account, "EURUSD"):
    print("Trading is ALLOWED")
else:
    print("Trading is CLOSED")
```

### 5) Get all sessions for a day (multiple sessions)

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_trade_sessions(account, symbol: str, day_of_week: int):
    """Get all trade sessions for a symbol on a specific day"""
    sessions = []
    session_index = 0

    while session_index < 10:  # Max 10 sessions
        try:
            session = await account.symbol_info_session_trade(
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
sessions = await get_all_trade_sessions(account, "NIKKEI", market_info_pb2.MONDAY)
print(f"Found {len(sessions)} trade session(s):")
for s in sessions:
    from_h = s['from'] // 3600
    from_m = (s['from'] % 3600) // 60
    to_h = s['to'] // 3600
    to_m = (s['to'] % 3600) // 60
    print(f"  Session {s['index']}: {from_h:02d}:{from_m:02d} - {to_h:02d}:{to_m:02d}")
```

### 6) Get session with timeout

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta

deadline = datetime.utcnow() + timedelta(seconds=3)

try:
    session = await account.symbol_info_session_trade(
        symbol="GBPUSD",
        day_of_week=market_info_pb2.FRIDAY,
        session_index=0,
        deadline=deadline
    )
    print(f"Session retrieved successfully")
except Exception as e:
    print(f"Timeout or error: {e}")
```

---

## 📚 See also

* [symbol_info_session_quote](./symbol_info_session_quote.md) - Get quote session times
* [symbol_info_integer](./symbol_info_integer.md) - Get other symbol integer properties
* [symbol_info_double](./symbol_info_double.md) - Get symbol double properties
