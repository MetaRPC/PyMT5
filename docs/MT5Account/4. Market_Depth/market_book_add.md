# Subscribe to Market Depth (DOM)

> **Request:** Subscribe to Depth of Market (order book) updates for a symbol.

**API Information:**

* **Python API:** `MT5Account.market_book_add(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `MarketBookAdd` (defined in `mt5-term-api-market-info.proto`)
* **Enums in this method:** 0 enums (simple boolean result)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `MarketBookAdd(MarketBookAddRequest) -> MarketBookAddReply`
* **Low-level client (generated):** `MarketInfoStub.MarketBookAdd(request, metadata)`

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def market_book_add(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> market_info_pb2.MarketBookAddData:
        """
        Opens the Depth of Market (DOM) for a symbol and subscribes to updates.

        Returns:
            MarketBookAddData: Subscription result.
        """
```

**Request message:**

```protobuf
MarketBookAddRequest {
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

Returns `MarketBookAddData` object.

**MarketBookAddData fields:**

| Field                  | Type   | Description                          |
| ---------------------- | ------ | ------------------------------------ |
| `opened_successfully`  | `bool` | True if subscription was successful  |

---

## 💬 Just the essentials

* **What it is.** Subscribes to Level 2 market data (order book) for a symbol.
* **Why you need it.** Required before you can call `market_book_get` to retrieve DOM data.
* **One-time subscription.** Call once per symbol, then use `market_book_get` to fetch data.

---

## 🎯 Purpose

Use it to:

* Subscribe to market depth (DOM) updates
* Enable Level 2 data access for a symbol
* Prepare for order book analysis
* Monitor bid/ask liquidity levels
* Analyze market microstructure

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[market_book_add - How it works](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_add_HOW.md)**

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Subscription required:** Must call this before `market_book_get`.
* **Symbol must be selected:** Ensure symbol is in Market Watch before subscribing.
* **Broker support:** Not all brokers provide DOM data.
* **Resource cleanup:** Call `market_book_release` when done to unsubscribe.
* **One subscription:** You only need to subscribe once per symbol.
* **Check success:** Always verify `opened_successfully == True`.

---

## 🔗 Usage Examples

### 1) Subscribe to DOM for EURUSD

```python
import asyncio
from MetaRpcMT5 import MT5Account

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
        # Subscribe to DOM
        result = await account.market_book_add("EURUSD")

        if result.opened_successfully:
            print(f"[SUCCESS] Subscribed to EURUSD DOM")
        else:
            print(f"[FAILED] Could not subscribe to DOM")

    finally:
        await account.channel.close()

asyncio.run(subscribe_dom())
```

### 2) Subscribe and verify

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def subscribe_and_verify():
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

        # First, ensure symbol is selected in Market Watch
        await account.symbol_select(symbol=symbol, select=True)
        print(f"[1] Symbol {symbol} selected in Market Watch")

        # Now subscribe to DOM
        result = await account.market_book_add(symbol)

        if result.opened_successfully:
            print(f"[2] Successfully subscribed to {symbol} DOM")

            # Verify by getting DOM data
            dom_data = await account.market_book_get(symbol)
            print(f"[3] DOM has {len(dom_data.mql_book_infos)} levels")
        else:
            print(f"[2] Failed to subscribe to DOM")

    finally:
        await account.channel.close()

asyncio.run(subscribe_and_verify())
```

### 3) Subscribe to multiple symbols

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def subscribe_multiple():
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
        for symbol in symbols:
            result = await account.market_book_add(symbol)

            if result.opened_successfully:
                print(f"[OK] {symbol} - DOM subscribed")
            else:
                print(f"[FAIL] {symbol} - Could not subscribe")

    finally:
        await account.channel.close()

asyncio.run(subscribe_multiple())
```

### 4) Subscribe with error handling

```python
import asyncio
from MetaRpcMT5 import MT5Account, ApiExceptionMT5

async def subscribe_with_error_handling():
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
        # Subscribe to DOM
        result = await account.market_book_add(symbol)

        if result.opened_successfully:
            print(f"[SUCCESS] Subscribed to {symbol} DOM")
            return True
        else:
            print(f"[WARNING] Subscription returned false")
            return False

    except ApiExceptionMT5 as e:
        print(f"[API ERROR] {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

    finally:
        await account.channel.close()

asyncio.run(subscribe_with_error_handling())
```

### 5) Check broker DOM support

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def check_dom_support():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    test_symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]

    try:
        print("Checking DOM support for symbols:\n")
        print(f"{'Symbol':<10} {'DOM Support':<15}")
        print("-" * 30)

        for symbol in test_symbols:
            try:
                result = await account.market_book_add(symbol)

                if result.opened_successfully:
                    # Try to get DOM data
                    dom_data = await account.market_book_get(symbol)

                    if len(dom_data.mql_book_infos) > 0:
                        print(f"{symbol:<10} {'YES ('+str(len(dom_data.mql_book_infos))+' levels)':<15}")
                    else:
                        print(f"{symbol:<10} {'NO DATA':<15}")

                    # Clean up
                    await account.market_book_release(symbol)
                else:
                    print(f"{symbol:<10} {'NOT SUPPORTED':<15}")

            except Exception as e:
                print(f"{symbol:<10} {'ERROR':<15}")

    finally:
        await account.channel.close()

asyncio.run(check_dom_support())
```

### 6) Subscribe and monitor DOM

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
        # Subscribe to DOM
        result = await account.market_book_add(symbol)

        if not result.opened_successfully:
            print(f"[FAILED] Could not subscribe to {symbol} DOM")
            return

        print(f"[SUBSCRIBED] Monitoring {symbol} DOM for {duration} seconds\n")

        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < duration:
            # Get current DOM state
            dom_data = await account.market_book_get(symbol)

            # Clear screen
            print("\033[2J\033[H")

            print(f"=== {symbol} Market Depth ===")
            print(f"Total levels: {len(dom_data.mql_book_infos)}\n")

            print(f"{'Type':<10} {'Price':<15} {'Volume':<15}")
            print("-" * 45)

            for book_entry in dom_data.mql_book_infos[:10]:  # Show first 10 levels
                entry_type = "BUY" if book_entry.type in [1, 3] else "SELL"
                print(f"{entry_type:<10} {book_entry.price:<15.5f} {book_entry.volume_real:<15.2f}")

            await asyncio.sleep(1)  # Update every second

        # Unsubscribe when done
        await account.market_book_release(symbol)
        print(f"\n[UNSUBSCRIBED] Stopped monitoring {symbol} DOM")

    finally:
        await account.channel.close()

asyncio.run(monitor_dom("EURUSD", duration=10))
```

---

## 📚 See also

* [MarketBookGet](./market_book_get.md) - Get current DOM data
* [MarketBookRelease](./market_book_release.md) - Unsubscribe from DOM
* [SymbolSelect](../2.%20Symbol_Information/symbol_select.md) - Add symbol to Market Watch
