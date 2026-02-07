## market_book_release — How it works

---

## 📌 Overview

The `market_book_release()` method is designed for **explicitly terminating work with the Depth of Market (DOM)** for a symbol.

It does not exist for data retrieval or market analysis, but for **correct lifecycle management of DOM as a resource**.

This method must be called **always** when work with the order book is completed.

---

## Why market_book_release exists

DOM is **not a one-time request**, but an active resource:

* it is opened by calling `market_book_add()`
* maintained by the server and terminal
* consumes resources
* exists over time

`market_book_release()` is needed to **explicitly tell the system** that:

> "This order book is no longer needed, resources can be freed"

Without this call, DOM is considered active.

---

## Method Signature

```python
async def market_book_release(
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* the method is asynchronous
* works within an already established connection
* does not return market data
* does not close the connection to the server

---

## 🧩 Code Example — Guaranteed Unsubscribe via Context Manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def dom_subscription(account, symbol):
    try:
        result = await account.market_book_add(symbol)
        if not result.opened_successfully:
            raise Exception(f"Failed to subscribe to {symbol} DOM")

        print(f"[SUBSCRIBED] {symbol} DOM")
        yield
    finally:
        await account.market_book_release(symbol)
        print(f"[RELEASED] {symbol} DOM")
```

This example demonstrates the correct usage pattern for `market_book_release()`.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Opening DOM

```python
await account.market_book_add(symbol)
```

DOM is transferred to active state:

* the terminal starts maintaining the order book
* data becomes available through `market_book_get()`

---

### 2️⃣ Working with Order Book Inside Context

```python
yield
```

In this block:

* DOM is guaranteed to be open
* you can safely request its state
* user code can terminate in any way

---

### 3️⃣ Automatic Unsubscribe

```python
await account.market_book_release(symbol)
```

This code is executed **always**:

* on normal exit
* on `return`
* on exception

This is a key guarantee of correct resource release.

---

## What market_book_release does and does NOT do

**Does:**

* closes DOM for the symbol
* releases terminal and server resources
* terminates order book subscription

**Does NOT:**

* does not close the connection
* does not terminate the trading session
* does not affect other symbols
* does not return data

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`market_book_release()`**:

* manages DOM lifecycle
* terminates resource work

**User code**:

* decides when DOM is no longer needed
* guarantees the release call
* defines architecture (try/finally, context manager, etc.)

---

## Summary

The `market_book_release()` method was created for one specific purpose:

> **explicitly and safely terminate work with the order book**

It is not optional and should be considered a **mandatory step** in any work with DOM.

Correct usage pattern:

> **open DOM → work → always release resource**
