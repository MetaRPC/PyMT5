# Get Market Depth Data

> **Request:** Retrieve current Depth of Market (order book) data for a subscribed symbol.

**API Information:**

* **Python API:** `MT5Account.market_book_get(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `MarketBookGet` (defined in `mt5-term-api-market-info.proto`)
* **Enums in this method:** 1 enum with 4 constants (1 output)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `MarketBookGet(MarketBookGetRequest) -> MarketBookGetReply`
* **Low-level client (generated):** `MarketInfoStub.MarketBookGet(request, metadata)`

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def market_book_get(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> market_info_pb2.MarketBookGetData:
        """
        Gets the current Depth of Market (DOM) data for a symbol.

        Returns:
            MarketBookGetData: A list of book entries for the symbol's DOM.
        """
```

**Request message:**

```protobuf
MarketBookGetRequest {
  string symbol = 1;  // Symbol name
}
```

---

## 🔽 Input

| Parameter            | Type                           | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `symbol`             | `str`                          | Symbol name (e.g., "EURUSD")                  |
| `deadline`           | `Optional[datetime]`           | Deadline for the operation (optional)         |
| `cancellation_event` | `Optional[asyncio.Event]`      | Event to cancel the request (optional)        |

---

## ⬆️ Output

Returns `MarketBookGetData` object.

**MarketBookGetData fields:**

| Field                  | Type                     | Description                          |
| ---------------------- | ------------------------ | ------------------------------------ |
| `mql_book_infos`       | `list[MrpcMqlBookInfo]`  | List of order book entries           |

**MrpcMqlBookInfo fields:**

| Field                  | Type      | Description                          |
| ---------------------- | --------- | ------------------------------------ |
| `type`                 | `BookType` | Order type (enum)                   |
| `price`                | `double`  | Price level                          |
| `volume`               | `int64`   | Volume in lots (legacy)              |
| `volume_real`          | `double`  | Real volume in lots                  |

---

## 🧱 Related enums (from proto)

### `BookType`

Used in `MrpcMqlBookInfo` to indicate order book entry type.

| Constant Name           | Value | Description                          |
| ----------------------- | ----- | ------------------------------------ |
| `BOOK_TYPE_SELL`        | 0     | Sell order                           |
| `BOOK_TYPE_BUY`         | 1     | Buy order                            |
| `BOOK_TYPE_SELL_MARKET` | 2     | Sell order at market price           |
| `BOOK_TYPE_BUY_MARKET`  | 3     | Buy order at market price            |

**Usage:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_pb2

# Access enum values
market_pb2.BOOK_TYPE_SELL        # = 0
market_pb2.BOOK_TYPE_BUY         # = 1
```

---

## 💬 Just the essentials

* **What it is.** Retrieves current Level 2 market data (order book) for a symbol.
* **Why you need it.** Analyze market depth, bid/ask liquidity, and order flow.
* **Subscription required.** Must call `market_book_add` first.

---

## 🎯 Purpose

Use it to:

* Get current DOM snapshot
* Analyze bid/ask liquidity levels
* Monitor order book depth
* Identify support/resistance zones
* Calculate volume at price levels
* Detect large orders (iceberg detection)
* Market microstructure analysis

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[MarketBookGet - How it works](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_get_HOW.md)**

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Subscription required:** Must call `market_book_add` before this method.
* **Empty data:** Returns empty list if no DOM data available.
* **Broker support:** Not all brokers provide DOM data.
* **Real-time snapshot:** Returns current state at the time of request.
* **Volume fields:** Use `volume_real` (double) instead of `volume` (int64).
* **Price levels:** Sorted by price (best bid/ask first).

---

## 🔗 Usage Examples

### 1) Get current DOM data

```python
import asyncio
from MetaRpcMT5 import MT5Account

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
        # First, subscribe to DOM
        await account.market_book_add("EURUSD")

        # Get DOM data
        dom_data = await account.market_book_get("EURUSD")

        print(f"[DOM] EURUSD Market Depth:")
        print(f"Total levels: {len(dom_data.mql_book_infos)}\n")

        print(f"{'Type':<10} {'Price':<15} {'Volume':<15}")
        print("-" * 45)

        for entry in dom_data.mql_book_infos[:10]:  # Show first 10 levels
            entry_type = "SELL" if entry.type in [0, 2] else "BUY"
            print(f"{entry_type:<10} {entry.price:<15.5f} {entry.volume_real:<15.2f}")

    finally:
        await account.channel.close()

asyncio.run(get_dom())
```

### 2) Analyze bid/ask spread

```python
import asyncio
from MetaRpcMT5 import MT5Account

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

        if not dom_data.mql_book_infos:
            print(f"[WARNING] No DOM data available for {symbol}")
            return

        # Separate buy and sell orders
        sell_orders = [e for e in dom_data.mql_book_infos if e.type in [0, 2]]
        buy_orders = [e for e in dom_data.mql_book_infos if e.type in [1, 3]]

        if sell_orders and buy_orders:
            best_ask = min(sell_orders, key=lambda x: x.price)
            best_bid = max(buy_orders, key=lambda x: x.price)

            spread = best_ask.price - best_bid.price
            spread_pips = spread / 0.0001

            print(f"[SPREAD ANALYSIS] {symbol}")
            print(f"  Best Bid: {best_bid.price:.5f} (Volume: {best_bid.volume_real:.2f})")
            print(f"  Best Ask: {best_ask.price:.5f} (Volume: {best_ask.volume_real:.2f})")
            print(f"  Spread: {spread:.5f} ({spread_pips:.1f} pips)")

    finally:
        await account.channel.close()

asyncio.run(analyze_spread())
```

### 3) Calculate total liquidity

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

        await account.market_book_add(symbol)
        dom_data = await account.market_book_get(symbol)

        # Calculate total volume by side
        sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
        buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])
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

### 4) Find support/resistance levels

```python
import asyncio
from MetaRpcMT5 import MT5Account

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
        sorted_levels = sorted(dom_data.mql_book_infos, key=lambda x: x.volume_real, reverse=True)

        print(f"[KEY LEVELS] {symbol} - Highest Volume Levels:\n")
        print(f"{'Rank':<6} {'Type':<10} {'Price':<15} {'Volume':<15}")
        print("-" * 50)

        for i, entry in enumerate(sorted_levels[:5], 1):
            entry_type = "SELL" if entry.type in [0, 2] else "BUY"
            print(f"{i:<6} {entry_type:<10} {entry.price:<15.5f} {entry.volume_real:<15.2f}")

        print("\n[NOTE] Large volume clusters may act as support/resistance")

    finally:
        await account.channel.close()

asyncio.run(find_key_levels())
```

### 5) Monitor DOM imbalance

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_imbalance(duration: int = 30):
    """Monitor DOM imbalance for specified duration"""
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
        print(f"[MONITORING] {symbol} DOM imbalance for {duration} seconds\n")

        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < duration:
            dom_data = await account.market_book_get(symbol)

            # Calculate imbalance
            sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
            buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

            if sell_volume + buy_volume > 0:
                imbalance = ((buy_volume - sell_volume) / (buy_volume + sell_volume)) * 100

                # Clear screen
                print("\033[2J\033[H")

                print(f"=== {symbol} DOM Imbalance ===\n")
                print(f"BUY:  {buy_volume:>8.2f} lots")
                print(f"SELL: {sell_volume:>8.2f} lots")
                print(f"\nImbalance: {imbalance:+.2f}%")

                if imbalance > 20:
                    print("\n[SIGNAL] Strong BUY pressure")
                elif imbalance < -20:
                    print("\n[SIGNAL] Strong SELL pressure")
                else:
                    print("\n[SIGNAL] Balanced market")

            await asyncio.sleep(1)

        await account.market_book_release(symbol)
        print(f"\n[STOPPED] Monitoring ended")

    finally:
        await account.channel.close()

asyncio.run(monitor_imbalance(duration=30))
```

### 6) Volume at Price (VAP) analysis

```python
import asyncio
from MetaRpcMT5 import MT5Account
from collections import defaultdict

async def volume_at_price():
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

        # Group volume by price bins (e.g., 5 pip ranges)
        pip_range = 5
        pip_size = 0.0001
        bin_size = pip_range * pip_size

        volume_bins = defaultdict(float)

        for entry in dom_data.mql_book_infos:
            # Round price to nearest bin
            bin_price = round(entry.price / bin_size) * bin_size
            volume_bins[bin_price] += entry.volume_real

        # Sort by price
        sorted_bins = sorted(volume_bins.items(), key=lambda x: x[0])

        print(f"[VOLUME AT PRICE] {symbol} ({pip_range} pip bins)\n")
        print(f"{'Price Range':<20} {'Volume':<15} {'Bar':<30}")
        print("-" * 70)

        max_volume = max(volume_bins.values()) if volume_bins else 1

        for price, volume in sorted_bins[:15]:  # Show top 15 bins
            bar_length = int((volume / max_volume) * 30)
            bar = "#" * bar_length
            print(f"{price:.5f}-{price+bin_size:.5f}  {volume:>8.2f} lots  {bar}")

    finally:
        await account.channel.close()

asyncio.run(volume_at_price())
```

---

## 📚 See also

* [MarketBookAdd](./market_book_add.md) - Subscribe to DOM updates
* [MarketBookRelease](./market_book_release.md) - Unsubscribe from DOM
* [SymbolInfoTick](../2.%20Symbol_Information/symbol_info_tick.md) - Get current tick prices
