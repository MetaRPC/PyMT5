# Unsubscribe from Market Depth

> **Request:** Unsubscribe from Depth of Market (order book) updates for a symbol.

**API Information:**

* **Python API:** `MT5Account.market_book_release(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `MarketBookRelease` (defined in `mt5-term-api-market-info.proto`)
* **Enums in this method:** 0 enums (simple boolean result)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `MarketBookRelease(MarketBookReleaseRequest) -> MarketBookReleaseReply`
* **Low-level client (generated):** `MarketInfoStub.MarketBookRelease(request, metadata)`

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def market_book_release(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> market_info_pb2.MarketBookReleaseData:
        """
        Closes the Depth of Market (DOM) for a symbol and unsubscribes from updates.

        Returns:
            MarketBookReleaseData: Unsubscription result.
        """
```

**Request message:**

```protobuf
MarketBookReleaseRequest {
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

Returns `MarketBookReleaseData` object.

**MarketBookReleaseData fields:**

| Field                  | Type   | Description                          |
| ---------------------- | ------ | ------------------------------------ |
| `closed_successfully`  | `bool` | True if unsubscription was successful|

---

## 💬 Just the essentials

* **What it is.** Unsubscribes from Level 2 market data (order book) for a symbol.
* **Why you need it.** Clean up resources and stop receiving DOM updates when no longer needed.
* **Best practice.** Always call when done monitoring DOM to free resources.

---

## 🎯 Purpose

Use it to:

* Unsubscribe from DOM updates
* Free system resources
* Clean up after DOM analysis
* Stop market depth monitoring
* Manage subscription lifecycle
* Reduce bandwidth usage

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[MarketBookRelease - How it works](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_release_HOW.md)**

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Resource cleanup:** Always call this when done with DOM monitoring.
* **No error if not subscribed:** Safe to call even if not currently subscribed.
* **Per-symbol basis:** Each symbol must be released separately.
* **Paired with add:** Every `market_book_add` should have a matching `market_book_release`.
* **Session cleanup:** Subscriptions persist until explicitly released or session ends.
* **Check success:** Always verify `closed_successfully == True`.

---

## 🔗 Usage Examples

### 1) Basic unsubscribe

```python
import asyncio
from MetaRpcMT5 import MT5Account

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
        symbol = "EURUSD"

        # Subscribe to DOM
        add_result = await account.market_book_add(symbol)
        if add_result.opened_successfully:
            print(f"[SUBSCRIBED] {symbol} DOM")

        # Do some analysis...
        dom_data = await account.market_book_get(symbol)
        print(f"[ANALYSIS] {len(dom_data.mql_book_infos)} DOM levels")

        # Unsubscribe when done
        release_result = await account.market_book_release(symbol)
        if release_result.closed_successfully:
            print(f"[UNSUBSCRIBED] {symbol} DOM released")

    finally:
        await account.channel.close()

asyncio.run(unsubscribe_dom())
```

### 2) Context manager pattern

```python
import asyncio
from MetaRpcMT5 import MT5Account
from contextlib import asynccontextmanager

@asynccontextmanager
async def dom_subscription(account, symbol):
    """Context manager for automatic DOM subscription cleanup"""
    try:
        # Subscribe
        result = await account.market_book_add(symbol)
        if not result.opened_successfully:
            raise Exception(f"Failed to subscribe to {symbol} DOM")

        print(f"[SUBSCRIBED] {symbol} DOM")
        yield
    finally:
        # Always release on exit
        await account.market_book_release(symbol)
        print(f"[RELEASED] {symbol} DOM")

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
        async with dom_subscription(account, "EURUSD"):
            # DOM is active here
            dom_data = await account.market_book_get("EURUSD")
            print(f"[ANALYSIS] {len(dom_data.mql_book_infos)} DOM levels")
        # DOM automatically released here

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 3) Release multiple symbols

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def release_multiple_symbols():
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
        # Subscribe to multiple symbols
        print("[SUBSCRIBING] To multiple symbols...")
        for symbol in symbols:
            result = await account.market_book_add(symbol)
            if result.opened_successfully:
                print(f"  [OK] {symbol} subscribed")

        # Do analysis...
        await asyncio.sleep(5)

        # Release all symbols
        print("\n[RELEASING] All subscriptions...")
        for symbol in symbols:
            result = await account.market_book_release(symbol)
            if result.closed_successfully:
                print(f"  [OK] {symbol} released")

    finally:
        await account.channel.close()

asyncio.run(release_multiple_symbols())
```

### 4) Error handling and cleanup

```python
import asyncio
from MetaRpcMT5 import MT5Account, ApiExceptionMT5

async def safe_dom_usage():
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
    subscribed = False

    try:
        # Subscribe
        add_result = await account.market_book_add(symbol)
        if not add_result.opened_successfully:
            print(f"[ERROR] Failed to subscribe to {symbol}")
            return

        subscribed = True
        print(f"[SUBSCRIBED] {symbol} DOM")

        # Perform analysis
        dom_data = await account.market_book_get(symbol)
        print(f"[ANALYSIS] {len(dom_data.mql_book_infos)} levels")

    except ApiExceptionMT5 as e:
        print(f"[API ERROR] {e}")

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

    finally:
        # Always clean up if subscribed
        if subscribed:
            try:
                release_result = await account.market_book_release(symbol)
                if release_result.closed_successfully:
                    print(f"[CLEANUP] {symbol} DOM released successfully")
                else:
                    print(f"[WARNING] Failed to release {symbol} DOM")
            except Exception as e:
                print(f"[CLEANUP ERROR] {e}")

        await account.channel.close()

asyncio.run(safe_dom_usage())
```

### 5) Subscription manager class

```python
import asyncio
from MetaRpcMT5 import MT5Account

class DOMSubscriptionManager:
    def __init__(self, account):
        self.account = account
        self.active_subscriptions = set()

    async def subscribe(self, symbol: str):
        """Subscribe to DOM with tracking"""
        result = await self.account.market_book_add(symbol)

        if result.opened_successfully:
            self.active_subscriptions.add(symbol)
            print(f"[SUBSCRIBED] {symbol} (Total: {len(self.active_subscriptions)})")
            return True
        else:
            print(f"[FAILED] Could not subscribe to {symbol}")
            return False

    async def unsubscribe(self, symbol: str):
        """Unsubscribe from DOM"""
        if symbol not in self.active_subscriptions:
            print(f"[WARNING] {symbol} not in active subscriptions")
            return False

        result = await self.account.market_book_release(symbol)

        if result.closed_successfully:
            self.active_subscriptions.remove(symbol)
            print(f"[UNSUBSCRIBED] {symbol} (Remaining: {len(self.active_subscriptions)})")
            return True
        else:
            print(f"[FAILED] Could not unsubscribe from {symbol}")
            return False

    async def release_all(self):
        """Release all active subscriptions"""
        print(f"[RELEASING] All {len(self.active_subscriptions)} subscriptions...")

        for symbol in list(self.active_subscriptions):
            await self.unsubscribe(symbol)

        print(f"[DONE] All subscriptions released")

    def list_active(self):
        """List all active subscriptions"""
        return list(self.active_subscriptions)

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

    manager = DOMSubscriptionManager(account)

    try:
        # Subscribe to multiple symbols
        await manager.subscribe("EURUSD")
        await manager.subscribe("GBPUSD")
        await manager.subscribe("USDJPY")

        print(f"\n[ACTIVE] Subscriptions: {manager.list_active()}")

        # Do analysis...
        await asyncio.sleep(5)

        # Release specific symbol
        await manager.unsubscribe("GBPUSD")

        # Release all remaining
        await manager.release_all()

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 6) Temporary DOM snapshot helper

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def get_dom_snapshot(account, symbol: str):
    """
    Helper function to get a quick DOM snapshot with automatic cleanup.
    Subscribe -> Get data -> Release
    """
    try:
        # Subscribe
        add_result = await account.market_book_add(symbol)
        if not add_result.opened_successfully:
            print(f"[ERROR] Failed to subscribe to {symbol}")
            return None

        # Get DOM data
        dom_data = await account.market_book_get(symbol)

        return dom_data

    finally:
        # Always release
        try:
            await account.market_book_release(symbol)
        except Exception as e:
            print(f"[WARNING] Cleanup error: {e}")

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
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]

        for symbol in symbols:
            print(f"\n[SNAPSHOT] Getting {symbol} DOM...")

            dom_data = await get_dom_snapshot(account, symbol)

            if dom_data:
                sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
                buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

                print(f"  Levels: {len(dom_data.mql_book_infos)}")
                print(f"  BUY volume: {buy_volume:.2f} lots")
                print(f"  SELL volume: {sell_volume:.2f} lots")

            await asyncio.sleep(1)  # Brief pause between snapshots

    finally:
        await account.channel.close()

asyncio.run(main())
```

---

## 📚 See also

* [MarketBookAdd](./market_book_add.md) - Subscribe to DOM updates
* [MarketBookGet](./market_book_get.md) - Get DOM data
* [SymbolSelect](../2.%20Symbol_Information/symbol_select.md) - Manage Market Watch symbols
