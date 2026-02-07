# Get Symbol Current Tick

> **Request:** retrieve current tick data for a symbol (bid, ask, last, volume, time).

**API Information:**

* **Low-level API:** `MT5Account.symbol_info_tick(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolInfoTick` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoTick(SymbolInfoTickRequest) -> SymbolInfoTickRequestReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolInfoTick(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Retrieve the latest tick snapshot for a symbol with bid/ask prices, volume, and timestamps.
* **Why you need it.** Get real-time price data for quotes, spread calculation, freshness checks before trading.
* **When to use.** Use for single tick queries. For continuous updates, use streaming method `on_symbol_tick()`.

---

## 🎯 Purpose

Use it to get current market data:

* Display live bid/ask prices in UI
* Calculate current spread
* Check quote freshness (tick age)
* Get last trade price and volumes
* Validate market data before order placement
* Monitor tick timestamps for latency

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_info_tick - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_tick_HOW.md)**

---

## Method Signature

```python
async def symbol_info_tick(
    self,
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.MrpcMqlTick
```

**Request message:**

```protobuf
message SymbolInfoTickRequest {
  string symbol = 1;
}
```

**Reply message:**

```protobuf
message SymbolInfoTickRequestReply {
  oneof response {
    MrpcMqlTick data = 1;
    Error error = 2;
  }
}

message MrpcMqlTick {
  int64 time = 1;
  double bid = 2;
  double ask = 3;
  double last = 4;
  uint64 volume = 5;
  int64 time_msc = 6;
  uint32 flags = 7;
  double volume_real = 8;
}
```

---

## 🔽 Input

| Parameter   | Type                    | Description          |
| ----------- | ----------------------- | -------------------- |
| `symbol`    | `str` (required)        | Symbol name          |
| `deadline`    | `datetime` (optional)             | Deadline for the gRPC call (UTC datetime) |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation |

---

## ⬆️ Output

| Field         | Type     | Python Type | Description                                      |
| ------------- | -------- | ----------- | ------------------------------------------------ |
| `time`        | `int64`  | `int`       | Tick time in seconds since epoch (UTC)           |
| `bid`         | `double` | `float`     | Current best bid price                           |
| `ask`         | `double` | `float`     | Current best ask price                           |
| `last`        | `double` | `float`     | Last deal price (if applicable)                  |
| `volume`      | `uint64` | `int`       | Tick volume (number of ticks)                    |
| `time_msc`    | `int64`  | `int`       | Tick time in milliseconds since epoch (UTC)      |
| `flags`       | `uint32` | `int`       | Tick flags bitmask (MT5 tick flags)              |
| `volume_real` | `double` | `float`     | Real volume (if provided by broker)              |

**Return value:** The method returns `MrpcMqlTick` object with all tick data fields.

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Symbol synchronization:** Symbol must be selected and synchronized for valid data. If bid/ask are zero, call `symbol_select()` and `symbol_is_synchronized()` first.
* **Time fields:** `time` is in seconds, `time_msc` is in milliseconds. Both represent Unix epoch UTC timestamps.
* **Spread calculation:** Spread = `ask - bid`. Mid price = `(ask + bid) / 2`.
* **Volume fields:** `volume` is tick count (uint64), `volume_real` is actual traded volume (double).
* **Flags field:** Bitmask indicating tick properties (bid change, ask change, last change, volume change).
* **Freshness check:** Compare `time` with current timestamp to detect stale data.
* **Zero values:** If tick data is zeros, symbol may not be synchronized or selected.

---

## 🔗 Usage Examples

### 1) Get current bid/ask and spread

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get current tick
tick = await account.symbol_info_tick(symbol="EURUSD")

print(f"Symbol: EURUSD")
print(f"  Bid: {tick.bid}")
print(f"  Ask: {tick.ask}")
print(f"  Spread: {tick.ask - tick.bid}")
print(f"  Mid: {(tick.bid + tick.ask) / 2}")
```

### 2) Check tick freshness

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

# Get tick and check age
tick = await account.symbol_info_tick(symbol="XAUUSD")

if tick.time > 0:
    current_time = datetime.now(timezone.utc).timestamp()
    age_seconds = int(current_time - tick.time)

    print(f"Tick age: {age_seconds} seconds")

    if age_seconds > 5:
        print("Warning: Tick data may be stale!")
    else:
        print("Tick data is fresh")
else:
    print("No tick time available")
```

### 3) Ensure symbol is synchronized before getting tick

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

symbol = "BTCUSD"

# Check if symbol is synchronized
sync_status = await account.symbol_is_synchronized(symbol)

if not sync_status.is_synchronized:
    print(f"Symbol {symbol} not synchronized, selecting...")

    # Select symbol
    await account.symbol_select(symbol, True)

    # Wait for synchronization
    sync_status = await account.symbol_is_synchronized(symbol)
    print(f"Synchronized: {sync_status.is_synchronized}")

# Now get tick
tick = await account.symbol_info_tick(symbol)
print(f"{symbol} - Bid: {tick.bid}, Ask: {tick.ask}")
```

### 4) Display volume information

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get tick with volume data
tick = await account.symbol_info_tick(symbol="EURUSD")

print(f"Volume Information:")
print(f"  Tick volume (count): {tick.volume}")
print(f"  Real volume: {tick.volume_real}")
print(f"  Last trade price: {tick.last}")
```

### 5) Convert timestamps to readable format

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

# Get tick
tick = await account.symbol_info_tick(symbol="GBPUSD")

# Convert timestamps
if tick.time > 0:
    time_dt = datetime.fromtimestamp(tick.time, tz=timezone.utc)
    print(f"Tick time: {time_dt.isoformat()}")

if tick.time_msc > 0:
    time_msc_dt = datetime.fromtimestamp(tick.time_msc / 1000, tz=timezone.utc)
    print(f"Tick time (ms): {time_msc_dt.isoformat()}")
    print(f"Milliseconds precision: {tick.time_msc % 1000}ms")
```

### 6) Get tick with timeout

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone
import asyncio

# Create cancellation event
cancel_event = asyncio.Event()

# Set deadline
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    tick = await account.symbol_info_tick(
        symbol="EURUSD",
        deadline=deadline,
        cancellation_event=cancel_event
    )
    print(f"Tick retrieved: Bid={tick.bid}, Ask={tick.ask}")
except Exception as e:
    print(f"Timeout or error: {e}")
```

### 7) Validate tick data before trading

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

async def validate_tick(account, symbol: str) -> bool:
    """Validate that tick data is fresh and valid for trading"""
    try:
        tick = await account.symbol_info_tick(symbol)

        # Check bid/ask are non-zero
        if tick.bid <= 0 or tick.ask <= 0:
            print(f"Invalid prices: bid={tick.bid}, ask={tick.ask}")
            return False

        # Check spread is reasonable (not zero, not too wide)
        spread = tick.ask - tick.bid
        if spread <= 0:
            print(f"Invalid spread: {spread}")
            return False

        # Check tick freshness (less than 10 seconds old)
        if tick.time > 0:
            current_time = datetime.now(timezone.utc).timestamp()
            age = current_time - tick.time

            if age > 10:
                print(f"Tick too old: {age} seconds")
                return False

        print(f"Tick validation passed")
        return True

    except Exception as e:
        print(f"Validation error: {e}")
        return False

# Usage
if await validate_tick(account, "EURUSD"):
    print("Ready to place order")
else:
    print("Tick validation failed, cannot trade")
```

---

## 📚 See also

* [symbol_is_synchronized](./symbol_is_synchronized.md) - Check symbol synchronization status
* [symbol_select](./symbol_select.md) - Select/deselect symbol in Market Watch
* [on_symbol_tick](../6. Streaming_Methods/on_symbol_tick.md) - Subscribe to real-time tick updates
* [symbol_info_double](./symbol_info_double.md) - Get symbol double properties
