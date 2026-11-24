## symbol_is_synchronized — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `symbol_is_synchronized()` to determine **whether a symbol is ready for use**, and how to implement waiting for symbol synchronization with the server based on it.

Symbol synchronization means that:

* the terminal has loaded data for the instrument
* the symbol is available for retrieving quotes, sessions, and ticks

Before synchronization is complete, many market methods may return empty or incorrect data.

---

## Method Signature

```python
async def symbol_is_synchronized(
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and called with `await`
* `symbol` — trading symbol name
* The method returns an object with synchronization flag
* The method does not initiate synchronization, it only reports the current state

---

## 🧩 Code Example — Waiting for symbol synchronization

```python
async def ensure_symbol_synchronized(account, symbol: str, max_retries: int = 5) -> bool:
    result = await account.symbol_is_synchronized(symbol)
    if result.synchronized:
        print(f"{symbol} already synchronized")
        return True

    print(f"Selecting {symbol}...")
    await account.symbol_select(symbol, True)

    for attempt in range(max_retries):
        await asyncio.sleep(0.5 * (attempt + 1))

        result = await account.symbol_is_synchronized(symbol)
        if result.synchronized:
            print(f"{symbol} synchronized after {attempt + 1} attempt(s)")
            return True

        print(f"Attempt {attempt + 1}/{max_retries}: still waiting...")

    print(f"Failed to synchronize {symbol} after {max_retries} attempts")
    return False
```

This example demonstrates a typical pattern: **check → initiate → wait → recheck**.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Checking Current Synchronization State

```python
result = await account.symbol_is_synchronized(symbol)
```

At this step:

* one asynchronous call is performed
* the server reports whether the symbol is synchronized
* the result is available in the `result.synchronized` field

If the value is `True`, no additional work is required.

---

### 2️⃣ Selecting Symbol in Terminal

```python
await account.symbol_select(symbol, True)
```

If the symbol is not yet synchronized:

* it is forcibly selected (added) to Market Watch
* this starts the data loading process for the symbol

Important: synchronization does not happen instantly.

---

### 3️⃣ Repeated Checks with Waiting

```python
for attempt in range(max_retries):
    await asyncio.sleep(0.5 * (attempt + 1))
```

Waiting with increasing delay is implemented:

* first attempt — after 0.5 seconds
* delay gradually increases thereafter

This allows the server to complete data loading.

---

### 4️⃣ Checking Result After Waiting

```python
result = await account.symbol_is_synchronized(symbol)
if result.synchronized:
```

After each pause:

* a recheck is performed
* if synchronization is complete, the function returns `True`

---

### 5️⃣ Handling Failed Synchronization

```python
print(f"Failed to synchronize {symbol} after {max_retries} attempts")
return False
```

If after all attempts the symbol is not synchronized:

* it is considered unavailable
* no further work with it is performed

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`symbol_is_synchronized()`**:

* reports the current synchronization state of the symbol
* does not initiate data loading
* does not wait for synchronization to complete

**`ensure_symbol_synchronized()`**:

* decides what to do when synchronization is absent
* initiates symbol selection
* implements waiting and retries
* makes the final decision

---

## Summary

This example illustrates a typical pattern of working with states in low-level API:

> **check state → initiate action → recheck → decision**

The `symbol_is_synchronized()` method provides only information about the current state, while all logic for waiting and managing the synchronization process is implemented on the user code side.
