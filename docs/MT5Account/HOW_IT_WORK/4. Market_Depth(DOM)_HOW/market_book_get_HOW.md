## market_book_get — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `market_book_get()` to get **the current Depth of Market (DOM) snapshot** and perform **custom liquidity calculations** by BUY and SELL sides.

In this scenario, DOM is used as a source of instantaneous market state, while all analytics and interpretation are performed on the client side.

---

## Method Signature

```python
async def market_book_get(
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* the method is asynchronous and called with `await`
* returns **the current DOM snapshot**, not a stream of updates
* does not aggregate or analyze data
* assumes that DOM subscription is already open

---

## 🧩 Code Example — Calculating Total Liquidity

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def calculate_liquidity():
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
        symbol = "EURUSD"

        # 1. Open DOM
        await account.market_book_add(symbol)

        # 2. Get current DOM snapshot
        dom_data = await account.market_book_get(symbol)

        # 3. Calculate total volume by side
        sell_volume = sum(
            e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2]
        )
        buy_volume = sum(
            e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3]
        )
        total_volume = sell_volume + buy_volume

        print(f"[LIQUIDITY] {symbol}")
        print(f"  Total DOM levels: {len(dom_data.mql_book_infos)}")
        print(f"  BUY side volume: {buy_volume:.2f} lots")
        print(f"  SELL side volume: {sell_volume:.2f} lots")
        print(f"  Total volume: {total_volume:.2f} lots")

        if total_volume > 0:
            buy_percent = (buy_volume / total_volume) * 100
            sell_percent = (sell_volume / total_volume) * 100

            print(f"\n  BUY: {buy_percent:.1f}% | SELL: {sell_percent:.1f}%")

            if buy_percent > 60:
                print("  [SIGNAL] Strong BUY side liquidity")
            elif sell_percent > 60:
                print("  [SIGNAL] Strong SELL side liquidity")
            else:
                print("  [SIGNAL] Balanced liquidity")

    finally:
        await account.channel.close()

asyncio.run(calculate_liquidity())
```

This example demonstrates a complete user-level liquidity calculation based on DOM data.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Opening DOM

```python
await account.market_book_add(symbol)
```

At this step:

* the terminal starts maintaining the order book for the symbol
* without this call, `market_book_get` may return empty data

---

### 2️⃣ Getting DOM Snapshot

```python
dom_data = await account.market_book_get(symbol)
```

The method returns:

* a list of order levels `mql_book_infos`
* each element represents one order book level

This is **an instantaneous snapshot**, not a stream.

---

### 3️⃣ Separating Orders by Sides

```python
e.type in [0, 2]  # SELL
e.type in [1, 3]  # BUY
```

Order type determines the market side:

* SELL — liquidity offers
* BUY — liquidity demand

Type interpretation is performed by the user.

---

### 4️⃣ Volume Aggregation

```python
sell_volume = sum(...)
buy_volume = sum(...)
```

At this step:

* volumes are summed by sides
* the API does not perform aggregation

---

### 5️⃣ User-Level Analytics

```python
if buy_percent > 60:
    ...
elif sell_percent > 60:
    ...
```

Threshold values:

* are chosen by the user
* do not have fixed values in the API

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`market_book_get()`**:

* returns the current order book state
* does not store history
* does not calculate liquidity
* does not generate signals

**User code**:

* aggregates volumes
* calculates percentages
* interprets the balance of supply and demand

---

## Summary

This example illustrates the DOM analysis pattern:

> **get order book snapshot → aggregate levels → evaluate liquidity → make conclusions**

The `market_book_get()` method provides raw DOM data, while all analytics and signals are fully formed on the user side.
