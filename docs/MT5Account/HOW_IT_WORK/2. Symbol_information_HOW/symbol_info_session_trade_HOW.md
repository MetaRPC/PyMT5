## symbol_info_session_trade — How it works

---

## 📌 Overview

This example shows how to determine **whether trading is allowed for a symbol at the current moment** using the low-level asynchronous method `symbol_info_session_trade()`.

Unlike quote sessions, trading sessions answer a different question:

> *Can you **open and close trades** for this symbol right now?*

This is a typical safety check used before sending orders.

---

## Method Signature

```python
async def symbol_info_session_trade(
    symbol: str,
    day_of_week: DayOfWeek,
    session_index: int,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and called with `await`
* `symbol` — trading symbol name
* `day_of_week` — day of week for which to check the trading session
* `session_index` — trading session index within the day (numbered from `0`)
* The method returns an object with trading session start and end times

---

## 🧩 Code Example — Checking if trading is allowed now

```python
async def is_trading_allowed(account, symbol: str) -> bool:
    now = datetime.utcnow()

    day_of_week = now.weekday() + 1
    if day_of_week == 7:  # Sunday
        day_of_week = 0

    try:
        session = await account.symbol_info_session_trade(
            symbol=symbol,
            day_of_week=day_of_week,
            session_index=0
        )

        current_seconds = now.hour * 3600 + now.minute * 60 + now.second

        if session.from.seconds <= current_seconds <= session.to.seconds:
            return True
        return False
    except Exception:
        return False
```

In this example, the method is used to check **a single trading session** at the current moment.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Determining Current Day of Week

```python
now = datetime.utcnow()
day_of_week = now.weekday() + 1
if day_of_week == 7:
    day_of_week = 0
```

Here, data is prepared for the API call.

* `datetime.weekday()` returns a number from `0` (Monday) to `6` (Sunday)
* The `DayOfWeek` enum in MT5 uses:

  * `0` — Sunday
  * `1` — Monday
  * …

The code converts the value to the format expected by the `symbol_info_session_trade()` method.

---

### 2️⃣ Requesting Trading Session

```python
session = await account.symbol_info_session_trade(
    symbol=symbol,
    day_of_week=day_of_week,
    session_index=0
)
```

At this step, one asynchronous call is performed.

The method answers the question:

> *Is there a trading session with index 0 for this symbol on this day?*

If the session exists:

* an object with trading start and end times is returned

If the session does not exist:

* the server returns an error
* control passes to the `except` block

---

### 3️⃣ Converting Current Time to API Format

```python
current_seconds = now.hour * 3600 + now.minute * 60 + now.second
```

Trading session time is returned as **number of seconds from the beginning of the day**.

To correctly compare current time with session boundaries, it is converted to the same format.

---

### 4️⃣ Checking Time Interval Match

```python
if session.from.seconds <= current_seconds <= session.to.seconds:
    return True
```

This is the key check in the example.

* if current time is within the trading session
* trading is considered allowed

If current time falls outside the interval — trading is closed.

---

### 5️⃣ Handling Absence of Trading Session

```python
except Exception:
    return False
```

If:

* the trading session does not exist
* the day is non-trading
* the session index is absent

The function returns `False`.

The absence of a trading session is treated as a normal situation.

---

## Summary

In this example, `symbol_info_session_trade()` is used to check whether trading is allowed for the symbol at the current moment.

The method returns the time boundaries of a single trading session, while all logic for determining current time, comparison, and result interpretation is performed on the user code side.
