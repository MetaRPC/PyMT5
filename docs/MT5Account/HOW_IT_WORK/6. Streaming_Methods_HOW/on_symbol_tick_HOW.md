## on_symbol_tick — How it works

---

## 📌 Overview

`on_symbol_tick()` is a low-level streaming method designed to receive **raw tick data in real-time** for one or multiple symbols.

The method provides access to each market tick (bid / ask), but **does not perform any calculations or maintain state**. All derived metrics, analytics, and trading logic are implemented exclusively on the user side.

In this example, the tick stream is used to **collect bid-ask spread statistics** over a fixed time period.

---

## Method Signature

```python
async def on_symbol_tick(
    symbols: list[str],
    cancellation_event: Optional[asyncio.Event] = None,
):
    -> AsyncIterator[OnSymbolTickData]
```

Key features:

* asynchronous streaming method (`async for`)
* returns stream of tick updates
* has no built-in stop mechanism
* lifetime is fully controlled by the user

---

## 🧩 Code Example — Track bid-ask spread statistics

```python
import asyncio
from collections import defaultdict
from MetaRpcMT5 import MT5Account

async def track_spread_stats():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    spreads = defaultdict(list)
    cancel_event = asyncio.Event()

    async def stop_after(seconds: int):
        await asyncio.sleep(seconds)
        cancel_event.set()

    try:
        asyncio.create_task(stop_after(60))

        symbols = ["EURUSD", "GBPUSD"]

        async for tick_data in account.on_symbol_tick(
            symbols=symbols,
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            spread = tick.ask - tick.bid
            spreads[tick.symbol].append(spread)

        print("\n=== Spread Statistics ===")
        for symbol, values in spreads.items():
            avg_spread = sum(values) / len(values)
            print(f"\n{symbol}:")
            print(f"  Ticks received: {len(values)}")
            print(f"  Average spread: {avg_spread * 10000:.1f} pips")
            print(f"  Min spread: {min(values) * 10000:.1f} pips")
            print(f"  Max spread: {max(values) * 10000:.1f} pips")

    finally:
        await account.channel.close()

asyncio.run(track_spread_stats())
```

---

## 🟢 Detailed Explanation

---

### 1️⃣ Data Storage Preparation

```python
spreads = defaultdict(list)
```

A structure is created to accumulate user data:

* key — trading symbol name
* value — list of recorded spread values

The `on_symbol_tick()` method **does not aggregate or store history**, so all statistics are collected manually.

---

### 2️⃣ Stream Lifetime Management

```python
cancel_event = asyncio.Event()
```

The stream has no built-in termination mechanism.

The stream lifetime is fully controlled by the user via `cancellation_event`.

---

### 3️⃣ Asynchronous Timer-Based Termination

```python
async def stop_after(seconds: int):
    await asyncio.sleep(seconds)
    cancel_event.set()
```

Helper coroutine:

* runs in parallel with tick processing
* waits for the specified time interval
* properly terminates the stream without exceptions

---

### 4️⃣ Subscribing to Tick Stream

```python
async for tick_data in account.on_symbol_tick(
    symbols=symbols,
    cancellation_event=cancel_event
):
```

At this stage:

* subscription is created for the specified symbols
* server starts sending tick updates
* each loop iteration corresponds to one market tick

The method returns an **event stream**, not market state.

---

### 5️⃣ User-Side Tick Processing

```python
spread = tick.ask - tick.bid
spreads[tick.symbol].append(spread)
```

This is where all business logic is executed:

* calculation of derived values
* data aggregation
* analytics preparation

The API acts exclusively as a data source in this process.

---

### 6️⃣ Stream Termination and Post-Processing

After `cancel_event` is set:

* data stream terminates properly
* user code proceeds to analysis
* any necessary calculations are performed

---

### 7️⃣ Post-Processing and Statistics Output

```python
print("\n=== Spread Statistics ===")
for symbol, values in spreads.items():
    avg_spread = sum(values) / len(values)
    print(f"\n{symbol}:")
    print(f"  Ticks received: {len(values)}")
    print(f"  Average spread: {avg_spread * 10000:.1f} pips")
    print(f"  Min spread: {min(values) * 10000:.1f} pips")
    print(f"  Max spread: {max(values) * 10000:.1f} pips")
```

At this stage, the stream is already completed, and the code works **exclusively with accumulated data**.

The following is performed here:

* iteration through all symbols for which ticks were received
* analysis of collected spread values
* calculation of aggregated metrics

---

#### Number of Received Ticks

```python
len(values)
```

Shows:

* how many market events were received
* actual stream density
* indirect assessment of symbol liquidity for the selected period

---

#### Average Spread

```python
avg_spread = sum(values) / len(values)
```

The average value is calculated **after stream completion**:

* API does not provide ready-made aggregates
* calculations are performed on the user side
* formula can be modified for any requirements

Conversion to pips:

```python
avg_spread * 10000
```

— this is a user convention, not part of the API.

---

#### Minimum and Maximum Spread

```python
min(values)
max(values)
```

Allows to:

* assess the range of spread fluctuations
* identify extreme values
* compare behavior of different symbols

---

## Final Responsibility Model

**`on_symbol_tick()`**:

* delivers raw market events
* does not interpret data
* does not manage lifetime
* does not store history

**User code**:

* manages subscription
* determines processing duration
* calculates metrics
* builds analytics or strategies

---

## Summary

This example illustrates the raw data streaming pattern:

**subscribe → receive raw ticks → accumulate data → calculate statistics**

Key points:

* `on_symbol_tick()` delivers raw market ticks (bid/ask), not derived metrics
* each tick is an atomic market event
* user code is responsible for:
  * storing tick history
  * calculating derived values (spread, averages, min/max)
  * determining stream lifetime
  * post-processing accumulated data

The API acts purely as a data source, while all analytics, aggregation, and interpretation remain entirely on the user side.
