# Add or Remove Symbol from Market Watch

> **Request:** add or remove symbol from Market Watch window to make it available for trading and data subscriptions.

**API Information:**

* **Low-level API:** `MT5Account.symbol_select(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolSelect` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolSelect(SymbolSelectRequest) -> SymbolSelectReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolSelect(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Add or remove symbol from Market Watch window (makes symbol available/unavailable for trading and subscriptions).
* **Why you need it.** Required before trading or subscribing to symbol data - MT5 only allows operations on symbols in Market Watch.
* **When to use.** Before any trading operations or data subscriptions for a symbol; when cleaning up unused symbols.

---

## 🎯 Purpose

Use it to manage Market Watch:

* Add symbol to Market Watch before trading
* Enable symbol for quote subscriptions
* Remove unused symbols to reduce overhead
* Prepare trading environment programmatically
* Clean up Market Watch after trading session
* Verify symbol availability for operations

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_select - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_select_HOW.md)**

---

## Method Signature

```python
async def symbol_select(
    self,
    symbol: str,
    select: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolSelectData
```

**Request message:**

```protobuf
message SymbolSelectRequest {
  string symbol = 1;
  bool select = 2;
}
```

**Reply message:**

```protobuf
message SymbolSelectReply {
  oneof response {
    SymbolSelectData data = 1;
    Error error = 2;
  }
}

message SymbolSelectData {
  bool success = 1;
}
```

---

## 🔽 Input

| Parameter     | Type                    | Description                                             |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `symbol`      | `str` (required)        | Symbol name (e.g., "EURUSD", "BTCUSD")                  |
| `select`      | `bool` (required)       | `True` = add to Market Watch, `False` = remove          |
| `deadline`    | `datetime` (optional)   | Deadline for the gRPC call (UTC datetime)               |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                    |

---

## ⬆️ Output

| Field     | Type   | Python Type | Description                                              |
| --------- | ------ | ----------- | -------------------------------------------------------- |
| `success` | `bool` | `bool`      | `True` if operation succeeded, `False` if failed         |

**Return value:** The method returns `SymbolSelectData` object with success status.

---

## 🧱 Related enums

No enums used by this method.

---

## 🧩 Notes & Tips

* **Required before trading:** Symbol MUST be in Market Watch before you can trade it or subscribe to its data.
* **Idempotent operation:** Adding already-selected symbol or removing already-removed symbol returns success.
* **Non-existent symbols:** Selecting non-existent symbol returns `success=False`.
* **Market Watch management:** Use this to programmatically manage which symbols are visible in MT5.
* **Performance:** Removing unused symbols from Market Watch can improve performance and reduce network traffic.
* **Symbol groups:** Some brokers organize symbols into groups - ensure symbol name is exact including suffixes.
* **Case sensitive:** Symbol names are case-sensitive (usually uppercase).
* **Success indicator:** Always check `data.success` to verify the operation completed successfully.

---

## 🔗 Usage Examples

### 1) Add symbol to Market Watch (RECOMMENDED)

```python
from MetaRpcMT5.mt5_account import MT5Account

async def add_to_market_watch(account: MT5Account, symbol: str):
    """Add symbol to Market Watch before trading"""

    # Add symbol
    data = await account.symbol_select(symbol=symbol, select=True)

    if data.success:
        print(f"{symbol} added to Market Watch")
        return True
    else:
        print(f"Failed to add {symbol} to Market Watch")
        return False

# Usage
success = await add_to_market_watch(account, "EURUSD")
```

### 2) Remove symbol from Market Watch

```python
async def remove_from_market_watch(account: MT5Account, symbol: str):
    """Remove symbol from Market Watch to clean up"""

    # Remove symbol
    data = await account.symbol_select(symbol=symbol, select=False)

    if data.success:
        print(f"{symbol} removed from Market Watch")
        return True
    else:
        print(f"Failed to remove {symbol}")
        return False

# Usage
await remove_from_market_watch(account, "GBPJPY")
```

### 3) Add multiple symbols with error handling

```python
async def add_symbols_batch(account: MT5Account, symbols: list[str]):
    """Add multiple symbols to Market Watch"""

    results = {'added': [], 'failed': []}

    for symbol in symbols:
        data = await account.symbol_select(symbol=symbol, select=True)

        if data.success:
            results['added'].append(symbol)
            print(f"{symbol}")
        else:
            results['failed'].append(symbol)
            print(f"{symbol}")

    print(f"\nAdded: {len(results['added'])}, Failed: {len(results['failed'])}")
    return results

# Usage
symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
results = await add_symbols_batch(account, symbols)
```

### 4) Setup trading environment

```python
async def setup_trading_symbols(account: MT5Account):
    """Setup symbols before trading session"""

    # Define required symbols
    required_symbols = [
        "EURUSD", "GBPUSD", "USDJPY",
        "AUDUSD", "USDCAD", "NZDUSD"
    ]

    print("Setting up trading environment...")

    for symbol in required_symbols:
        data = await account.symbol_select(symbol=symbol, select=True)

        if data.success:
            print(f"  {symbol} ready")
        else:
            print(f"  {symbol} FAILED - check symbol name")
            return False

    print("All symbols ready for trading!")
    return True

# Usage
if await setup_trading_symbols(account):
    print("Starting trading strategy...")
```

### 5) Cleanup unused symbols

```python
async def cleanup_market_watch(account: MT5Account, keep_symbols: list[str]):
    """Remove all symbols except specified ones"""

    # Get all symbols currently in Market Watch
    import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

    # Get total symbols
    total_data = await account.symbols_total(selected_only=True)
    total = total_data.total

    removed = []
    for i in range(total):
        # Get symbol name by index
        name_data = await account.symbol_name(index=i, selected=True)
        symbol = name_data.name

        # Remove if not in keep list
        if symbol not in keep_symbols:
            data = await account.symbol_select(symbol=symbol, select=False)
            if data.success:
                removed.append(symbol)
                print(f"Removed: {symbol}")

    print(f"\nRemoved {len(removed)} symbols from Market Watch")
    return removed

# Usage
keep = ["EURUSD", "GBPUSD", "USDJPY"]
await cleanup_market_watch(account, keep)
```

### 6) Verify symbol selection with timeout

```python
from datetime import datetime, timedelta

async def select_symbol_with_timeout(
    account: MT5Account,
    symbol: str,
    select: bool,
    timeout_seconds: int = 5
):
    """Select symbol with timeout"""

    # Calculate deadline
    deadline = datetime.utcnow() + timedelta(seconds=timeout_seconds)

    try:
        data = await account.symbol_select(
            symbol=symbol,
            select=select,
            deadline=deadline
        )

        action = "added to" if select else "removed from"
        if data.success:
            print(f"{symbol} {action} Market Watch")
        else:
            print(f"Failed to {action.split()[0]} {symbol}")

        return data.success

    except Exception as e:
        print(f"Timeout or error selecting {symbol}: {e}")
        return False

# Usage
success = await select_symbol_with_timeout(account, "EURUSD", True, timeout_seconds=3)
```

### 7) Prepare symbols for strategy

```python
async def prepare_symbols_for_strategy(
    account: MT5Account,
    strategy_symbols: dict[str, bool]
):
    """
    Prepare Market Watch for trading strategy

    Args:
        strategy_symbols: Dict of {symbol: should_select}
    """

    print("Configuring Market Watch for strategy...")

    success_count = 0
    fail_count = 0

    for symbol, should_select in strategy_symbols.items():
        action = "Adding" if should_select else "Removing"

        data = await account.symbol_select(
            symbol=symbol,
            select=should_select
        )

        if data.success:
            status = "success_count += 1
        else:
            status = "fail_count += 1

        action_word = "to" if should_select else "from"
        print(f"{status} {action} {symbol} {action_word} Market Watch")

    print(f"\nResults: {success_count} succeeded, {fail_count} failed")

    if fail_count > 0:
        print("WARNING: Some symbols failed - check symbol names")
        return False

    return True

# Usage
strategy_config = {
    "EURUSD": True,   # Add
    "GBPUSD": True,   # Add
    "USDJPY": True,   # Add
    "XAUUSD": False,  # Remove
    "BTCUSD": False   # Remove
}

if await prepare_symbols_for_strategy(account, strategy_config):
    print("Market Watch configured successfully!")
```

---

## 📚 See also

* [symbol_exist](./symbol_exist.md) - Check if symbol exists on server
* [symbol_name](./symbol_name.md) - Get symbol name by index
* [symbols_total](./symbols_total.md) - Get total number of symbols
* [symbol_info_tick](./symbol_info_tick.md) - Get symbol tick data (requires symbol to be selected first)
