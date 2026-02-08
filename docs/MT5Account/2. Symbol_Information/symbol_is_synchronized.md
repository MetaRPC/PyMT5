# Check if Symbol is Synchronized

> **Request:** check if symbol data is synchronized with the server.

**API Information:**

* **Low-level API:** `MT5Account.symbol_is_synchronized(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolIsSynchronized` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolIsSynchronized(SymbolIsSynchronizedRequest) -> SymbolIsSynchronizedReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolIsSynchronized(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Check if a symbol's market data is currently synchronized with the broker's server.
* **Why you need it.** Ensure symbol has valid, up-to-date data before querying prices or placing orders.
* **When to use.** After selecting a symbol, before reading tick data, or when validating symbol availability.

---

## 🎯 Purpose

Use it to verify symbol data availability:

* Check symbol synchronization status before trading
* Validate symbol data after calling `symbol_select()`
* Ensure tick data is current and valid
* Diagnose missing or stale market data
* Implement retry logic for symbol selection
* Verify symbol connectivity before operations

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_is_synchronized - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_is_synchronized_HOW.md)**

---

## Method Signature

```python
async def symbol_is_synchronized(
    self,
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolIsSynchronizedData
```

**Request message:**

```protobuf
message SymbolIsSynchronizedRequest {
  string symbol = 1;
}
```

**Reply message:**

```protobuf
message SymbolIsSynchronizedReply {
  oneof response {
    SymbolIsSynchronizedData data = 1;
    Error error = 2;
  }
}

message SymbolIsSynchronizedData {
  bool synchronized = 1;
}
```

---

## 🔽 Input

| Parameter     | Type                    | Description                                             |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `symbol`      | `str` (required)        | Symbol name to check                                    |
| `deadline`    | `datetime` (optional)   | Deadline for the gRPC call (UTC datetime)               |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                    |

---

## ⬆️ Output

| Field          | Type   | Python Type | Description                                |
| -------------- | ------ | ----------- | ------------------------------------------ |
| `synchronized` | `bool` | `bool`      | True if symbol data is synchronized        |

**Return value:** The method returns `SymbolIsSynchronizedData` object with `synchronized` boolean field.

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Access the value:** The returned object has a `.synchronized` field (not `.is_synchronized`).
* **Symbol selection:** If `synchronized` is `False`, call `symbol_select(symbol, True)` to add symbol to Market Watch.
* **Synchronization delay:** After selecting a symbol, synchronization may take 1-2 seconds.
* **Retry logic:** Implement polling with delays when waiting for synchronization.
* **Tick data dependency:** If not synchronized, `symbol_info_tick()` may return zero or stale values.
* **Not an error:** Returning `False` is a normal state, not an error condition.

---

## 🔗 Usage Examples

### 1) Check if symbol is synchronized

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Check synchronization status
result = await account.symbol_is_synchronized(symbol="EURUSD")

if result.synchronized:
    print("Symbol is synchronized")
else:
    print("Symbol is NOT synchronized")
```

### 2) Ensure symbol is synchronized before getting tick

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_synchronized_tick(account, symbol: str):
    """Get tick data only if symbol is synchronized"""

    # Check synchronization
    sync_status = await account.symbol_is_synchronized(symbol)

    if not sync_status.synchronized:
        print(f"Symbol {symbol} not synchronized, selecting...")

        # Select symbol
        await account.symbol_select(symbol, True)

        # Wait a moment for synchronization
        import asyncio
        await asyncio.sleep(1)

        # Re-check
        sync_status = await account.symbol_is_synchronized(symbol)

        if not sync_status.synchronized:
            raise RuntimeError(f"Failed to synchronize {symbol}")

    # Now safe to get tick
    tick = await account.symbol_info_tick(symbol)
    return tick

# Usage
tick = await get_synchronized_tick(account, "EURUSD")
print(f"Bid: {tick.bid}, Ask: {tick.ask}")
```

### 3) Wait for synchronization with timeout

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import asyncio

async def wait_for_synchronization(
    account,
    symbol: str,
    timeout: float = 10.0,
    check_interval: float = 0.5
) -> bool:
    """Wait for symbol to synchronize with timeout"""

    start_time = asyncio.get_event_loop().time()

    while True:
        # Check current status
        result = await account.symbol_is_synchronized(symbol)

        if result.synchronized:
            print(f"{symbol} synchronized")
            return True

        # Check timeout
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= timeout:
            print(f"Timeout waiting for {symbol} synchronization")
            return False

        # Wait before next check
        await asyncio.sleep(check_interval)

# Usage
if await wait_for_synchronization(account, "BTCUSD", timeout=10):
    print("Ready to trade")
else:
    print("Symbol not available")
```

### 4) Batch check multiple symbols

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def check_symbols_sync(account, symbols: list[str]):
    """Check synchronization status for multiple symbols"""

    results = {}

    for symbol in symbols:
        try:
            sync_status = await account.symbol_is_synchronized(symbol)
            results[symbol] = sync_status.synchronized
        except Exception as e:
            print(f"Error checking {symbol}: {e}")
            results[symbol] = False

    # Display results
    print(f"{'Symbol':<10} {'Status':<15}")
    print("=" * 25)
    for symbol, is_synced in results.items():
        status = "Synchronized" if is_synced else "Not synced"
        print(f"{symbol:<10} {status:<15}")

    return results

# Usage
symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
sync_results = await check_symbols_sync(account, symbols)
```

### 5) Select and wait for synchronization

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import asyncio

async def ensure_symbol_synchronized(
    account,
    symbol: str,
    max_retries: int = 5
) -> bool:
    """Select symbol and wait for synchronization"""

    # First check if already synchronized
    result = await account.symbol_is_synchronized(symbol)
    if result.synchronized:
        print(f"{symbol} already synchronized")
        return True

    # Select symbol
    print(f"Selecting {symbol}...")
    await account.symbol_select(symbol, True)

    # Retry with exponential backoff
    for attempt in range(max_retries):
        await asyncio.sleep(0.5 * (attempt + 1))  # 0.5s, 1s, 1.5s, 2s, 2.5s

        result = await account.symbol_is_synchronized(symbol)
        if result.synchronized:
            print(f"{symbol} synchronized after {attempt + 1} attempt(s)")
            return True

        print(f"Attempt {attempt + 1}/{max_retries}: still waiting...")

    print(f"Failed to synchronize {symbol} after {max_retries} attempts")
    return False

# Usage
if await ensure_symbol_synchronized(account, "EURUSD"):
    tick = await account.symbol_info_tick("EURUSD")
    print(f"Tick: {tick.bid}/{tick.ask}")
```

### 6) Check synchronization with timeout parameter

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta

# Set deadline for the call
deadline = datetime.utcnow() + timedelta(seconds=3)

try:
    result = await account.symbol_is_synchronized(
        symbol="GBPUSD",
        deadline=deadline
    )

    if result.synchronized:
        print("Symbol is synchronized")
    else:
        print("Symbol needs synchronization")
except Exception as e:
    print(f"Timeout or error: {e}")
```

### 7) Validate before trading operation

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import asyncio

async def validate_symbol_ready(account, symbol: str) -> bool:
    """
    Comprehensive check that symbol is ready for trading.
    Returns True only if symbol exists, is selected, and synchronized.
    """

    # Step 1: Check if symbol exists
    exists = await account.symbol_exist(symbol)
    if not exists.exists:
        print(f"Symbol {symbol} does not exist")
        return False
    print(f"Symbol exists")

    # Step 2: Check if selected
    select_status = await account.symbol_info_integer(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_SELECT
    )

    if not select_status.value:
        print(f"Symbol not selected, adding to Market Watch...")
        await account.symbol_select(symbol, True)
        await asyncio.sleep(1)

    # Step 3: Check synchronization
    sync_status = await account.symbol_is_synchronized(symbol)
    if not sync_status.synchronized:
        print(f"Waiting for synchronization...")

        # Wait up to 5 seconds
        for i in range(10):
            await asyncio.sleep(0.5)
            sync_status = await account.symbol_is_synchronized(symbol)
            if sync_status.synchronized:
                break

        if not sync_status.synchronized:
            print(f"Symbol {symbol} failed to synchronize")
            return False

    print(f"Symbol {symbol} is ready for trading")
    return True

# Usage
if await validate_symbol_ready(account, "EURUSD"):
    # Safe to place orders
    print("Proceeding with trade...")
else:
    print("Cannot trade - symbol not ready")
```

---

## 📚 See also

* [symbol_select](./symbol_select.md) - Select/deselect symbol in Market Watch
* [symbol_exist](./symbol_exist.md) - Check if symbol exists
* [symbol_info_tick](./symbol_info_tick.md) - Get current tick data (requires synchronized symbol)
* [symbol_info_integer](./symbol_info_integer.md) - Get symbol integer properties
