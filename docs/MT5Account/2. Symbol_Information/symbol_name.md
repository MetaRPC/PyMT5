# Get Symbol Name by Index

> **Request:** retrieve symbol name by index position.

**API Information:**

* **Low-level API:** `MT5Account.symbol_name(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolName` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolName(SymbolNameRequest) -> SymbolNameReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolName(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Retrieve symbol name by its numerical index position in the symbol list.
* **Why you need it.** Enumerate symbols sequentially, iterate through available symbols programmatically.
* **When to use.** Use with `symbols_total()` to iterate all symbols or Market Watch symbols.

---

## 🎯 Purpose

Use it to enumerate symbols:

* Iterate through all available symbols
* Get Market Watch symbols by position
* Build symbol lists programmatically
* Implement symbol selection UI
* Discover available trading instruments
* Map index positions to symbol names

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_name - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_name_HOW.md)**

---

## Method Signature

```python
async def symbol_name(
    self,
    index: int,
    selected: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolNameData
```

**Request message:**

```protobuf
message SymbolNameRequest {
  uint32 index = 1;
  bool selected = 2;
}
```

**Reply message:**

```protobuf
message SymbolNameReply {
  oneof response {
    SymbolNameData data = 1;
    Error error = 2;
  }
}

message SymbolNameData {
  string name = 1;
}
```

---

## 🔽 Input

| Parameter     | Type                    | Description                                             |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `index`       | `int` (required)        | Symbol index (zero-based, starting at 0)                |
| `selected`    | `bool` (required)       | True = Market Watch only, False = all available symbols |
| `deadline`    | `datetime` (optional)   | Deadline for the gRPC call (UTC datetime)               |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                    |

---

## ⬆️ Output

| Field  | Type     | Python Type | Description                        |
| ------ | -------- | ----------- | ---------------------------------- |
| `name` | `string` | `str`       | Symbol name at the specified index |

**Return value:** The method returns `SymbolNameData` object with `name` field containing the symbol name.

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Access the value:** The returned object has a `.name` field containing the symbol name string.
* **Index range:** Valid indices are 0 to `symbols_total() - 1`. Out-of-range indices will raise an error.
* **Selected vs all:** Use `selected=True` for Market Watch symbols, `selected=False` for all broker symbols.
* **Order dependency:** Symbol order may change between calls if Market Watch is modified.
* **Zero-based indexing:** First symbol is at index 0, not 1.
* **Combine with symbols_total:** Always call `symbols_total()` first to get the valid index range.

---

## 🔗 Usage Examples

### 1) Get all Market Watch symbols

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_market_watch_symbols(account) -> list[str]:
    """Get list of all symbols in Market Watch"""

    # Get total count of Market Watch symbols
    count_data = await account.symbols_total(selected_only=True)
    total = count_data.total

    print(f"Found {total} symbols in Market Watch")

    # Iterate and collect all symbol names
    symbols = []
    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=True)
        symbols.append(symbol_data.name)

    return symbols

# Usage
mw_symbols = await get_all_market_watch_symbols(account)
print(f"Market Watch symbols: {mw_symbols}")
```

### 2) Get all available symbols from broker

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_broker_symbols(account) -> list[str]:
    """Get list of ALL symbols available from broker"""

    # Get total count of all symbols
    count_data = await account.symbols_total(selected_only=False)
    total = count_data.total

    print(f"Found {total} total symbols from broker")

    # Iterate and collect all symbol names
    symbols = []
    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=False)
        symbols.append(symbol_data.name)

    return symbols

# Usage
all_symbols = await get_all_broker_symbols(account)
print(f"Total symbols available: {len(all_symbols)}")
```

### 3) Print first 10 Market Watch symbols

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def print_first_symbols(account, count: int = 10):
    """Display first N symbols from Market Watch"""

    print(f"First {count} Market Watch symbols:")
    print("=" * 40)

    for i in range(count):
        try:
            symbol_data = await account.symbol_name(index=i, selected=True)
            print(f"{i+1:3d}. {symbol_data.name}")
        except Exception as e:
            print(f"[ERROR] Index {i}: {e}")
            break

# Usage
await print_first_symbols(account, count=10)
```

### 4) Find symbols matching pattern

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def find_symbols_by_pattern(account, pattern: str, selected_only: bool = True) -> list[str]:
    """Find symbols matching a text pattern"""

    # Get total count
    count_data = await account.symbols_total(selected_only=selected_only)
    total = count_data.total

    # Search for matching symbols
    matching_symbols = []
    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=selected_only)

        if pattern.upper() in symbol_data.name.upper():
            matching_symbols.append(symbol_data.name)

    return matching_symbols

# Usage
usd_symbols = await find_symbols_by_pattern(account, "USD")
print(f"Found {len(usd_symbols)} symbols containing 'USD': {usd_symbols}")
```

### 5) Compare Market Watch vs all available symbols

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def compare_symbol_lists(account):
    """Compare Market Watch symbols with all available symbols"""

    # Get Market Watch symbols
    mw_count = await account.symbols_total(selected_only=True)
    mw_total = mw_count.total

    # Get all broker symbols
    all_count = await account.symbols_total(selected_only=False)
    all_total = all_count.total

    print(f"Symbol Statistics:")
    print(f"  Market Watch: {mw_total} symbols")
    print(f"  Available from broker: {all_total} symbols")
    print(f"  Not in Market Watch: {all_total - mw_total} symbols")

# Usage
await compare_symbol_lists(account)
```

### 6) Get symbols with error handling

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_symbols_safe(account, selected_only: bool = True) -> list[str]:
    """Get symbols with robust error handling"""

    symbols = []

    try:
        # Get total count
        count_data = await account.symbols_total(selected_only=selected_only)
        total = count_data.total

        # Iterate with error handling
        for i in range(total):
            try:
                symbol_data = await account.symbol_name(index=i, selected=selected_only)
                symbols.append(symbol_data.name)
            except Exception as e:
                print(f"Error getting symbol at index {i}: {e}")
                # Continue with next symbol
                continue

        print(f"Successfully retrieved {len(symbols)} out of {total} symbols")

    except Exception as e:
        print(f"Error getting symbol count: {e}")

    return symbols

# Usage
symbols = await get_symbols_safe(account, selected_only=True)
```

### 7) Get symbol name with timeout

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta

# Set deadline
deadline = datetime.utcnow() + timedelta(seconds=3)

try:
    symbol_data = await account.symbol_name(
        index=0,
        selected=True,
        deadline=deadline
    )
    print(f"First symbol: {symbol_data.name}")
except Exception as e:
    print(f"Timeout or error: {e}")
```

### 8) Build symbol dictionary with metadata

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def build_symbol_dict(account) -> dict:
    """Build dictionary mapping indices to symbol info"""

    count_data = await account.symbols_total(selected_only=True)
    total = count_data.total

    symbol_dict = {}

    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=True)
        symbol_name = symbol_data.name

        # Get additional info
        digits_data = await account.symbol_info_integer(
            symbol=symbol_name,
            property=market_info_pb2.SYMBOL_DIGITS
        )

        symbol_dict[i] = {
            'name': symbol_name,
            'index': i,
            'digits': digits_data.value
        }

    return symbol_dict

# Usage
symbols_info = await build_symbol_dict(account)
for idx, info in symbols_info.items():
    print(f"{idx}: {info['name']} (digits={info['digits']})")
```

---

## 📚 See also

* [symbols_total](./symbols_total.md) - Get total symbol count (use before calling symbol_name)
* [symbol_exist](./symbol_exist.md) - Check if specific symbol exists
* [symbol_select](./symbol_select.md) - Add/remove symbols from Market Watch
