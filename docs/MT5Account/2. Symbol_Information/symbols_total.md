# Get Total Number of Symbols

> **Request:** total count of available symbols on the trading platform.

**API Information:**

* **Low-level API:** `MT5Account.symbols_total(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolsTotal` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolsTotal(SymbolsTotalRequest) -> SymbolsTotalReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolsTotal(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Get the total count of symbols available on the platform.
* **Why you need it.** Check how many symbols are available, either all symbols or only Market Watch symbols.
* **When to use.** Use for quick symbol count. For symbol iteration, prefer `symbol_params_many()` (single call) over multiple `symbol_name()` calls.

---

## 🎯 Purpose

Use it to get symbol count:

* Check total number of symbols on platform
* Count symbols in Market Watch
* Validate symbol availability
* Quick check before iterating symbols
* Monitor symbol list changes

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbols_total - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbols_total_HOW.md)**

---

## Method Signature

```python
async def symbols_total(
    self,
    selected_only: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolsTotalData
```

**Request message:**

```protobuf
message SymbolsTotalRequest {
  bool mode = 1;
}
```

**Reply message:**

```protobuf
message SymbolsTotalReply {
  oneof response {
    SymbolsTotalData data = 1;
    Error error = 2;
  }
}

message SymbolsTotalData {
  int32 total = 1;
}
```

**Parameter mapping:**
- Python parameter `selected_only` maps to protobuf field `mode`

---

## 🔽 Input

| Parameter     | Type                    | Description                                             |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `selected_only` | `bool` (required)     | True = count only Market Watch symbols, False = count all |
| `deadline`    | `datetime` (optional)   | Deadline for the gRPC call (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                    |

**Usage:**

```python
from datetime import datetime, timedelta

# Count all symbols
data = await account.symbols_total(selected_only=False)

# Count only Market Watch symbols
data = await account.symbols_total(selected_only=True)
```

---

## ⬆️ Output - `SymbolsTotalData`

| Field   | Type    | Python Type | Description                                      |
| ------- | ------- | ----------- | ------------------------------------------------ |
| `total` | `int32` | `int`       | Total number of symbols                          |

**Return value:** The method returns `SymbolsTotalData` object with `total` field.

---

## 🧱 Related enums (from proto)

No enums used by this method.

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors.
* **Market Watch vs All:** `selected_only=True` counts only symbols visible in Market Watch; `False` counts all available symbols.
* **Connection required:** Call `connect_by_host_port()` or `connect_by_server_name()` first.
* **Thread safety:** Safe to call concurrently from multiple asyncio tasks.
* **Performance:** This is a lightweight call - use it freely for validation before operations.
* **Return type:** The method returns `SymbolsTotalData` protobuf object (Python type matches field types).

---

## 🔗 Usage Examples

### 1) Get total symbols count

```python
import asyncio
from datetime import datetime, timedelta
from MetaRpcMT5.mt5_account import MT5Account

async def main():
    account = MT5Account(
        account_number=12345678,
        password="your_password",
        host="your-server.com:443"
    )

    await account.connect_by_host_port()

    try:
        # Count all symbols
        data_all = await account.symbols_total(selected_only=False)
        print(f"Total symbols available: {data_all.total}")

        # Count Market Watch symbols
        data_mw = await account.symbols_total(selected_only=True)
        print(f"Market Watch symbols: {data_mw.total}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Compare Market Watch vs all symbols

```python
async def compare_symbol_counts(account: MT5Account):
    """Compare Market Watch vs all available symbols"""
    # Get counts
    all_symbols = await account.symbols_total(selected_only=False)
    mw_symbols = await account.symbols_total(selected_only=True)

    print(f"\nSymbol Statistics:")
    print(f"  All available: {all_symbols.total}")
    print(f"  Market Watch: {mw_symbols.total}")
    print(f"  Not in Market Watch: {all_symbols.total - mw_symbols.total}")

    return {
        "all": all_symbols.total,
        "market_watch": mw_symbols.total,
        "hidden": all_symbols.total - mw_symbols.total
    }

# Usage:
stats = await compare_symbol_counts(account)
```

### 3) Check if symbols available

```python
async def has_symbols(account: MT5Account) -> bool:
    """Check if any symbols are available"""
    data = await account.symbols_total(selected_only=False)

    if data.total > 0:
        print(f"[OK] {data.total} symbols available")
        return True
    else:
        print("[WARNING] No symbols available")
        return False

# Usage:
if await has_symbols(account):
    print("Ready to trade")
```

### 4) Monitor symbol count changes

```python
async def monitor_symbol_count(account: MT5Account, interval: float = 60.0):
    """Monitor for changes in symbol count"""
    previous_count = None

    while True:
        try:
            data = await account.symbols_total(selected_only=True)
            count = data.total

            if previous_count is not None and count != previous_count:
                if count > previous_count:
                    print(f"[+] Symbol added to Market Watch: {count} total")
                else:
                    print(f"[-] Symbol removed from Market Watch: {count} total")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Market Watch: {count} symbols")

            previous_count = count

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)

# Usage:
# await monitor_symbol_count(account, interval=60.0)
```

### 5) Validate before iteration

```python
async def iterate_symbols_safe(account: MT5Account):
    """Safely iterate through symbols with validation"""
    # Check count first
    data = await account.symbols_total(selected_only=True)

    if data.total == 0:
        print("[WARNING] No symbols in Market Watch")
        return []

    print(f"[OK] Found {data.total} symbols")

    # Now safe to iterate
    symbols = []
    for i in range(data.total):
        symbol_name = await account.symbol_name(index=i, selected=True)
        symbols.append(symbol_name.name)

    return symbols

# Usage:
symbols = await iterate_symbols_safe(account)
print(f"Symbols: {symbols}")
```

### 6) Calculate Market Watch usage

```python
async def calculate_mw_usage(account: MT5Account) -> dict:
    """Calculate Market Watch usage statistics"""
    all_data = await account.symbols_total(selected_only=False)
    mw_data = await account.symbols_total(selected_only=True)

    total = all_data.total
    used = mw_data.total
    usage_pct = (used / total * 100) if total > 0 else 0

    result = {
        "total_available": total,
        "in_market_watch": used,
        "usage_percent": usage_pct
    }

    print(f"\nMarket Watch Usage:")
    print(f"  Using {used} of {total} symbols ({usage_pct:.1f}%)")

    return result

# Usage:
usage = await calculate_mw_usage(account)
```

### 7) Wait for symbols to load

```python
async def wait_for_symbols(
    account: MT5Account,
    min_symbols: int = 1,
    timeout_seconds: int = 30,
    check_interval: float = 1.0
):
    """Wait until minimum number of symbols available"""
    import time
    start_time = time.time()

    print(f"Waiting for at least {min_symbols} symbol(s)...")

    while True:
        # Check timeout
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Timeout: symbols not loaded after {timeout_seconds}s")

        # Check symbol count
        data = await account.symbols_total(selected_only=False)
        count = data.total

        if count >= min_symbols:
            print(f"[OK] {count} symbols loaded")
            return count

        print(f"[INFO] Waiting... ({count} symbols)")
        await asyncio.sleep(check_interval)

# Usage:
try:
    count = await wait_for_symbols(account, min_symbols=10)
except TimeoutError as e:
    print(f"[ERROR] {e}")
```

### 8) Log symbol statistics

```python
import logging

async def log_symbol_statistics(account: MT5Account):
    """Log comprehensive symbol statistics"""
    logging.basicConfig(level=logging.INFO)

    all_data = await account.symbols_total(selected_only=False)
    mw_data = await account.symbols_total(selected_only=True)

    logging.info("=" * 60)
    logging.info("SYMBOL STATISTICS")
    logging.info("=" * 60)
    logging.info(f"Total symbols available: {all_data.total}")
    logging.info(f"Market Watch symbols: {mw_data.total}")
    logging.info(f"Hidden symbols: {all_data.total - mw_data.total}")
    logging.info("=" * 60)

# Usage:
await log_symbol_statistics(account)
```

---

## Common Patterns

### Quick count check

```python
async def get_mw_symbol_count(account: MT5Account) -> int:
    """Get Market Watch symbol count"""
    data = await account.symbols_total(selected_only=True)
    return data.total
```

### Validate symbols loaded

```python
async def symbols_loaded(account: MT5Account) -> bool:
    """Check if symbols are loaded"""
    data = await account.symbols_total(selected_only=False)
    return data.total > 0
```

---

## 📚 See also

* [symbol_params_many](./symbol_params_many.md) - Get comprehensive parameters for all symbols (RECOMMENDED for iteration)
* [symbol_name](./symbol_name.md) - Get symbol name by index
* [symbol_exist](./symbol_exist.md) - Check if specific symbol exists
* [symbol_select](./symbol_select.md) - Add/remove symbol from Market Watch
