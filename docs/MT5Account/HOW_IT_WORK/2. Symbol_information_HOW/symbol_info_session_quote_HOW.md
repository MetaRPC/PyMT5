## symbol_info_session_quote — How it works

---

## 📌 Overview

This example demonstrates how to retrieve **quote sessions** for a trading symbol using the low-level asynchronous method `symbol_info_session_quote()`.

The method is used to determine **at what hours the terminal publishes quotes** for a specific symbol on a particular day of the week.

Important:

* This concerns *quotes*, not trading availability
* Sessions may differ by day of the week
* A single day can have multiple sessions

---

## Method Signature

```python
async def symbol_info_session_quote(
    symbol: str,
    day_of_week: DayOfWeek,
    session_index: int,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and must be called with `await`
* `symbol` — trading symbol name (e.g., `"EURUSD"`)
* `day_of_week` — specific day of the week
* `session_index` — session index within the day (numbering starts from `0`)
* The method returns an object with session start and end time

---

## 🧩 Code Example — Getting All Weekly Quote Sessions

```python
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
    except Exception:
        print(f"  {day_name:10s} No session")
```

In this example, the **first quote session (`session_index = 0`)** is requested for each day of the week.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Iterating Through Days of the Week

```python
for day_enum, day_name in days.items():
```

The code sequentially iterates through all days of the week.

* `day_enum` is used when calling the API
* `day_name` is used only for formatted output

Each day is processed independently.

---

### 2️⃣ Requesting Quote Session

```python
session = await account.symbol_info_session_quote(
    symbol="EURUSD",
    day_of_week=day_enum,
    session_index=0
)
```

At this step, one asynchronous call is executed.

The method answers the question:

> *Is there a quote session with index 0 for this symbol on this day?*

If the session exists:

* An object with start and end time is returned

If there is no session:

* The server returns an error
* Control passes to `except`

---

### 3️⃣ Session Time Format

```python
from_hours = session.from.seconds // 3600
from_mins = (session.from.seconds % 3600) // 60
```

Session start and end time is returned as **number of seconds from the beginning of the day**.

Conversion to `HH:MM` format is performed entirely on the user code side.

The API returns only raw time values.

---

### 4️⃣ Displaying Session Information

```python
print(f"  {day_name:10s} {from_hours:02d}:{from_mins:02d} - {to_hours:02d}:{to_mins:02d}")
```

If the session exists:

* Day of the week is displayed
* Quote interval is displayed

This is purely a visual representation of data.

---

### 5️⃣ Handling Missing Session

```python
except Exception:
    print(f"  {day_name:10s} No session")
```

If there is no quote session with index `0` for the given day:

* The exception is caught
* Message `No session` is displayed

Absence of a session is treated as a normal situation.

---

## Summary

In this example, `symbol_info_session_quote()` is used to retrieve information about quote sessions for a trading symbol.

The method returns start and end time for one session for the specified day of the week and index, and all logic for iterating through days, formatting time, and handling missing sessions remains on the user code side.
