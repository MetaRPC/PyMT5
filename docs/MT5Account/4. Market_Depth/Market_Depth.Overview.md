# MT5Account - Market Depth - Overview

> Subscribe to, retrieve, and manage Depth of Market (DOM) data: monitor order book, analyze liquidity, track bid/ask levels.

## 📁 What lives here

### DOM Operations

* **[market_book_add](./market_book_add.md)** - subscribe to DOM updates for a symbol.
* **[market_book_get](./market_book_get.md)** - retrieve current DOM data.
* **[market_book_release](./market_book_release.md)** - unsubscribe from DOM updates.

---

## 📚 Step-by-step tutorials

**Note:** All DOM operations are async methods. Check individual method pages for detailed examples.

* **[market_book_add](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_add_HOW.md)** - Subscription examples
* **[market_book_get](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_get_HOW.md)** - DOM analysis patterns
* **[market_book_release](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_release_HOW.md)** - Resource cleanup examples

---

## 🧭 Plain English

* **market_book_add** -> **subscribe** to Level 2 market data (order book).
* **market_book_get** -> **retrieve** current DOM snapshot with bid/ask levels.
* **market_book_release** -> **unsubscribe** and free resources when done.

> Rule of thumb: **subscribe once** with `market_book_add`, **poll repeatedly** with `market_book_get`, **cleanup** with `market_book_release`.

---

## Quick choose

| If you need...                                   | Use                   | Returns                    | Key inputs                          |
| ------------------------------------------------ | --------------------- | -------------------------- | ----------------------------------- |
| Subscribe to DOM updates                         | `market_book_add`     | MarketBookAddData          | symbol                              |
| Get current order book snapshot                  | `market_book_get`     | MarketBookGetData          | symbol                              |
| Unsubscribe from DOM                             | `market_book_release` | MarketBookReleaseData      | symbol                              |
| Analyze bid/ask liquidity                        | `market_book_get`     | MarketBookGetData          | symbol                              |
| Monitor order flow                               | `market_book_get`     | MarketBookGetData          | symbol (in loop)                    |
| Find support/resistance levels                   | `market_book_get`     | MarketBookGetData          | symbol                              |

---

## ℹ️ Cross-refs & gotchas

* **Broker support:** Not all brokers provide DOM data - check with your broker.
* **Subscription required:** Must call `market_book_add` before `market_book_get`.
* **Symbol must be selected:** Ensure symbol is in Market Watch before subscribing.
* **Always release:** Call `market_book_release` when done to free resources.
* **Empty data:** Returns empty list if no DOM data available or not subscribed.
* **Async methods:** All DOM operations are async - use `await`.
* **Automatic reconnection:** All methods have built-in reconnection via `execute_with_reconnect`.
* **Per-symbol basis:** Subscribe/unsubscribe each symbol separately.
* **Type enum:** In `MrpcMqlBookInfo`, type 1 = SELL orders, type 2 = BUY orders.
* **Volume fields:** Use `volume_real` (double) instead of `volume` (int64).
* **Real-time data:** DOM is updated in real-time, call `market_book_get` repeatedly for monitoring.

---

## 🟢 Minimal snippets

```python
import asyncio
from MetaRpcMT5 import MT5Account

# Subscribe to DOM
async def subscribe_dom():
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
        # Subscribe to EURUSD DOM
        result = await account.market_book_add("EURUSD")

        if result.opened_successfully:
            print(f"[SUCCESS] Subscribed to EURUSD DOM")
        else:
            print(f"[FAILED] Could not subscribe")

    finally:
        await account.channel.close()

asyncio.run(subscribe_dom())
```

```python
# Get DOM data
async def get_dom():
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
        # Subscribe first
        await account.market_book_add("EURUSD")

        # Get DOM snapshot
        dom_data = await account.market_book_get("EURUSD")

        print(f"[DOM] EURUSD has {len(dom_data.mql_book_infos)} levels")

        for entry in dom_data.mql_book_infos[:5]:  # Show first 5
            entry_type = "SELL" if entry.type in [0, 2] else "BUY"
            print(f"{entry_type:<6} {entry.price:.5f} Vol: {entry.volume_real:.2f}")

    finally:
        await account.channel.close()

asyncio.run(get_dom())
```

```python
# Unsubscribe from DOM
async def unsubscribe_dom():
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
        # Subscribe
        await account.market_book_add("EURUSD")

        # Do analysis...
        dom_data = await account.market_book_get("EURUSD")
        print(f"[ANALYSIS] {len(dom_data.mql_book_infos)} levels")

        # Unsubscribe when done
        result = await account.market_book_release("EURUSD")

        if result.closed_successfully:
            print(f"[SUCCESS] DOM released")

    finally:
        await account.channel.close()

asyncio.run(unsubscribe_dom())
```

```python
# Complete DOM workflow
async def dom_workflow():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbol = "EURUSD"

    try:
        # 1. Subscribe to DOM
        add_result = await account.market_book_add(symbol)
        if not add_result.opened_successfully:
            print(f"[ERROR] Could not subscribe to {symbol}")
            return

        print(f"[1] Subscribed to {symbol} DOM")

        # 2. Monitor DOM for 10 seconds
        print(f"[2] Monitoring DOM...")

        for i in range(10):
            dom_data = await account.market_book_get(symbol)

            # Calculate liquidity
            sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
            buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

            print(f"  [{i+1}/10] Levels: {len(dom_data.mql_book_infos)}, "
                  f"BUY: {buy_volume:.2f}, SELL: {sell_volume:.2f}")

            await asyncio.sleep(1)

        # 3. Unsubscribe
        release_result = await account.market_book_release(symbol)
        if release_result.closed_successfully:
            print(f"[3] DOM released successfully")

    finally:
        await account.channel.close()

asyncio.run(dom_workflow())
```

```python
# Analyze bid/ask spread
async def analyze_spread():
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

        # Subscribe and get DOM
        await account.market_book_add(symbol)
        dom_data = await account.market_book_get(symbol)

        # Separate buy and sell orders
        sell_orders = [e for e in dom_data.mql_book_infos if e.type in [0, 2]]
        buy_orders = [e for e in dom_data.mql_book_infos if e.type in [1, 3]]

        if sell_orders and buy_orders:
            best_ask = min(sell_orders, key=lambda x: x.price)
            best_bid = max(buy_orders, key=lambda x: x.price)

            spread = best_ask.price - best_bid.price
            spread_pips = spread / 0.0001

            print(f"[SPREAD] {symbol}")
            print(f"  Best Bid: {best_bid.price:.5f}")
            print(f"  Best Ask: {best_ask.price:.5f}")
            print(f"  Spread: {spread_pips:.1f} pips")

        # Cleanup
        await account.market_book_release(symbol)

    finally:
        await account.channel.close()

asyncio.run(analyze_spread())
```

```python
# Monitor multiple symbols
async def monitor_multiple_symbols():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbols = ["EURUSD", "GBPUSD", "USDJPY"]

    try:
        # Subscribe to all symbols
        for symbol in symbols:
            result = await account.market_book_add(symbol)
            if result.opened_successfully:
                print(f"[SUBSCRIBED] {symbol}")

        # Monitor all symbols
        print("\n[MONITORING] DOM for all symbols:")

        for _ in range(5):  # Monitor for 5 iterations
            print("\n" + "="*50)

            for symbol in symbols:
                dom_data = await account.market_book_get(symbol)

                sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
                buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

                print(f"{symbol:<8} Levels: {len(dom_data.mql_book_infos):<4} "
                      f"BUY: {buy_volume:>8.2f}  SELL: {sell_volume:>8.2f}")

            await asyncio.sleep(2)

        # Unsubscribe from all symbols
        print("\n[RELEASING] All subscriptions...")
        for symbol in symbols:
            await account.market_book_release(symbol)

    finally:
        await account.channel.close()

asyncio.run(monitor_multiple_symbols())
```

```python
# Context manager for automatic cleanup
from contextlib import asynccontextmanager

@asynccontextmanager
async def dom_subscription(account, symbol):
    """Context manager for automatic DOM subscription cleanup"""
    try:
        result = await account.market_book_add(symbol)
        if not result.opened_successfully:
            raise Exception(f"Failed to subscribe to {symbol} DOM")
        yield
    finally:
        await account.market_book_release(symbol)

async def main():
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
        # DOM is automatically released on exit
        async with dom_subscription(account, "EURUSD"):
            dom_data = await account.market_book_get("EURUSD")
            print(f"[DOM] {len(dom_data.mql_book_infos)} levels")

    finally:
        await account.channel.close()

asyncio.run(main())
```

```python
# Find key liquidity levels
async def find_key_levels():
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

        await account.market_book_add(symbol)
        dom_data = await account.market_book_get(symbol)

        # Find top 5 volume levels
        sorted_levels = sorted(dom_data.mql_book_infos,
                             key=lambda x: x.volume_real,
                             reverse=True)

        print(f"[KEY LEVELS] {symbol} - Top 5 volume levels:\n")

        for i, entry in enumerate(sorted_levels[:5], 1):
            entry_type = "SELL" if entry.type in [0, 2] else "BUY"
            print(f"{i}. {entry_type:<6} {entry.price:.5f} - {entry.volume_real:.2f} lots")

        # Cleanup
        await account.market_book_release(symbol)

    finally:
        await account.channel.close()

asyncio.run(find_key_levels())
```

---

## 📚 See also

* **Symbols:** [symbol_select](../2.%20Symbol_Information/symbol_select.md) - add symbol to Market Watch before subscribing
* **Prices:** [symbol_info_tick](../2.%20Symbol_Information/symbol_info_tick.md) - get current tick prices
* **Streaming:** [on_symbol_tick](../6.%20Streaming_Methods/on_symbol_tick.md) - real-time tick stream
