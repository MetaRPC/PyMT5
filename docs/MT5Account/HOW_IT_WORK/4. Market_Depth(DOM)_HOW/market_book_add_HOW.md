## market_book_add / market_book_get / market_book_release — How it works

---

## 📌 Overview

This example shows **the complete lifecycle of working with Depth of Market (DOM)**:

1. subscribing to DOM for a symbol
2. periodically retrieving the current order book state
3. displaying order levels
4. properly closing the subscription

Here DOM is used as **a live market state** that updates over time, while low-level methods serve as data sources and control operations.

---

## Methods Used

This example uses three low-level methods:

```python
market_book_add(symbol)
market_book_get(symbol)
market_book_release(symbol)
```

Their roles:

* `market_book_add` — opens DOM and registers subscription
* `market_book_get` — returns current order book snapshot
* `market_book_release` — closes DOM and releases resources

---

## 🧩 Code Example — Subscribe and Monitor DOM

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_dom(symbol: str, duration: int = 10):
    """Subscribe and monitor DOM for specified duration"""

    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # 1. Subscribe to DOM
        result = await account.market_book_add(symbol)

        if not result.opened_successfully:
            print(f"[FAILED] Could not subscribe to {symbol} DOM")
            return

        print(f"[SUBSCRIBED] Monitoring {symbol} DOM for {duration} seconds\n")

        start_time = asyncio.get_event_loop().time()

        # 2. Periodically read DOM snapshot
        while (asyncio.get_event_loop().time() - start_time) < duration:
            dom_data = await account.market_book_get(symbol)

            print("\033[2J\033[H")  # clear screen

            print(f"=== {symbol} Market Depth ===")
            print(f"Total levels: {len(dom_data.mql_book_infos)}\n")

            print(f"{'Type':<10} {'Price':<15} {'Volume':<15}")
            print("-" * 45)

            for book_entry in dom_data.mql_book_infos[:10]:
                entry_type = "BUY" if book_entry.type in [1, 3] else "SELL"
                print(
                    f"{entry_type:<10} "
                    f"{book_entry.price:<15.5f} "
                    f"{book_entry.volume_real:<15.2f}"
                )

            await asyncio.sleep(1)

        # 3. Unsubscribe from DOM
        await account.market_book_release(symbol)
        print(f"\n[UNSUBSCRIBED] Stopped monitoring {symbol} DOM")

    finally:
        await account.channel.close()

asyncio.run(monitor_dom("EURUSD", duration=10))
```

---

## 🟢 Detailed Explanation

---

### 1️⃣ Subscribing to DOM

```python
result = await account.market_book_add(symbol)
```

At this step:

* the terminal opens the order book for the symbol
* the server starts maintaining DOM state
* an operation success flag is returned

Without this step, `market_book_get` will not work.

---

### 2️⃣ Monitoring Loop

```python
while (asyncio.get_event_loop().time() - start_time) < duration:
```

The loop:

* runs for the specified time
* regularly requests the current DOM state
* does not store history — only the current snapshot

---

### 3️⃣ Getting Current Order Book State

```python
dom_data = await account.market_book_get(symbol)
```

The method returns:

* a list of order levels
* each level contains price, volume, and type

This is **a snapshot of the market state at the current moment in time**.

---

### 4️⃣ Displaying Levels

```python
for book_entry in dom_data.mql_book_infos[:10]:
```

User code:

* chooses how many levels to display
* interprets the order type (BUY / SELL)
* formats the output

The API does not participate in visualization.

---

### 5️⃣ Closing Subscription

```python
await account.market_book_release(symbol)
```

Important:

* DOM must be explicitly closed
* this releases resources on the server and terminal
* without this, the subscription will remain active

---

## The Role of Low-Level Methods

Clear boundary of responsibility:

**`market_book_add`**:

* opens DOM
* registers subscription

**`market_book_get`**:

* returns current order book snapshot
* does not stream data

**`market_book_release`**:

* closes DOM
* releases resources

**User code**:

* determines polling frequency
* formats data
* decides how long to monitor the market

---

## Summary

This example illustrates the standard DOM pattern:

> **subscribe → regularly retrieve state → process → properly unsubscribe**

Low-level methods control DOM access, while all monitoring and data usage logic remains on the user side.
