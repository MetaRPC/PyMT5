# Get Symbol String Property

> **Request:** retrieve string-type property value for a symbol.

**API Information:**

* **Low-level API:** `MT5Account.symbol_info_string(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolInfoString` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoString(SymbolInfoStringRequest) -> SymbolInfoStringReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolInfoString(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Retrieve a single string-type property value for a symbol (DESCRIPTION, CURRENCY_BASE, PATH, etc.).
* **Why you need it.** Get specific text symbol properties like currency codes, descriptions, and metadata.
* **When to use.** Use `symbol_params_many()` for multiple properties. Use this method for single property queries.

---

## 🎯 Purpose

Use it to query specific string symbol properties:

* Get symbol description and display names
* Retrieve currency codes (base, profit, margin)
* Check symbol path and categorization
* Get exchange and ISIN information
* Query symbol formula and metadata
* Check bank and country information

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_info_string - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_string_HOW.md)**

---

## Method Signature

```python
async def symbol_info_string(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoStringProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoStringData
```

**Request message:**

```protobuf
message SymbolInfoStringRequest {
  string symbol = 1;
  SymbolInfoStringProperty type = 2;
}
```

**Reply message:**

```protobuf
message SymbolInfoStringReply {
  oneof response {
    SymbolInfoStringData data = 1;
    Error error = 2;
  }
}

message SymbolInfoStringData {
  string value = 1;
}
```

---

## 🔽 Input

| Parameter   | Type                             | Description                                    |
| ----------- | -------------------------------- | ---------------------------------------------- |
| `symbol`    | `str` (required)                 | Symbol name                                    |
| `property`  | `SymbolInfoStringProperty` (enum) | Property to retrieve (DESCRIPTION, PATH, etc.) |
| `deadline`    | `datetime` (optional)             | Deadline for the gRPC call (UTC datetime) |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation |

---

## ⬆️ Output

| Field   | Type     | Python Type | Description                        |
| ------- | -------- | ----------- | ---------------------------------- |
| `value` | `string` | `str`       | The string value of the property   |

**Return value:** The method returns `SymbolInfoStringData` object with `value` field containing the requested property.

---

## 🧱 Related enums (from proto)

> **Note:** In Python code, use the full enum path from the market_info module.

### `SymbolInfoStringProperty`

Defined in `mt5-term-api-market-info.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `SYMBOL_BASIS` | 0 | Symbol basis |
| `SYMBOL_CATEGORY` | 1 | Symbol category |
| `SYMBOL_COUNTRY` | 2 | Symbol country |
| `SYMBOL_SECTOR_NAME` | 3 | Sector name |
| `SYMBOL_INDUSTRY_NAME` | 4 | Industry name |
| `SYMBOL_CURRENCY_BASE` | 5 | Base currency |
| `SYMBOL_CURRENCY_PROFIT` | 6 | Profit currency |
| `SYMBOL_CURRENCY_MARGIN` | 7 | Margin currency |
| `SYMBOL_BANK` | 8 | Feeder bank |
| `SYMBOL_DESCRIPTION` | 9 | Symbol description |
| `SYMBOL_EXCHANGE` | 10 | Exchange name |
| `SYMBOL_FORMULA` | 11 | Formula for custom symbols |
| `SYMBOL_ISIN` | 12 | ISIN code |
| `SYMBOL_PAGE` | 13 | Web page URL |
| `SYMBOL_PATH` | 14 | Symbol path in symbol tree |

**Usage in Python:**
```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get symbol description
desc = await account.symbol_info_string("EURUSD", market_info_pb2.SYMBOL_DESCRIPTION)
print(f"Description: {desc.value}")

# Get currency pair
base = await account.symbol_info_string("EURUSD", market_info_pb2.SYMBOL_CURRENCY_BASE)
profit = await account.symbol_info_string("EURUSD", market_info_pb2.SYMBOL_CURRENCY_PROFIT)
print(f"Pair: {base.value}/{profit.value}")
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Access the value:** The returned `SymbolInfoStringData` object has a `.value` field containing the string.
* **Currency properties:** CURRENCY_BASE, CURRENCY_PROFIT, and CURRENCY_MARGIN are essential for margin and profit calculations.
* **Path format:** SYMBOL_PATH uses backslash separators (e.g., "Forex\\Majors\\EURUSD").
* **Empty values:** Some properties may return empty strings if not set by the broker.
* **ISIN codes:** Only available for securities like stocks and bonds.

---

## 🔗 Usage Examples

### 1) Get symbol description

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get symbol description
result = await account.symbol_info_string(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DESCRIPTION
)
print(f"Description: {result.value}")  # Output: Description: Euro vs US Dollar
```

### 2) Get currency triplet (base, profit, margin)

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get all three currency codes
base = await account.symbol_info_string(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_CURRENCY_BASE
)

profit = await account.symbol_info_string(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_CURRENCY_PROFIT
)

margin = await account.symbol_info_string(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_CURRENCY_MARGIN
)

print(f"XAUUSD Currencies:")
print(f"  Base: {base.value}")      # XAU (Gold)
print(f"  Profit: {profit.value}")  # USD
print(f"  Margin: {margin.value}")  # USD
```

### 3) Get symbol path and parse hierarchy

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_string(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_PATH
)

# Parse path hierarchy
path = result.value
folders = path.split("\\")

print(f"Symbol Path: {path}")
print(f"Hierarchy: {' > '.join(folders)}")
# Output: Hierarchy: Forex > Majors > EURUSD
```

### 4) Get ISIN code for stocks

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_string(
    symbol="AAPL",
    property=market_info_pb2.SYMBOL_ISIN
)

if result.value:
    print(f"AAPL ISIN: {result.value}")
else:
    print("ISIN not available")
```

### 5) Get exchange name

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_string(
    symbol="BTCUSD",
    property=market_info_pb2.SYMBOL_EXCHANGE
)

print(f"Exchange: {result.value}")
```

### 6) Display symbol metadata

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def display_symbol_metadata(account, symbol: str):
    """Display comprehensive string metadata for a symbol"""

    # Get description
    desc = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_DESCRIPTION
    )

    # Get path
    path = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_PATH
    )

    # Get currencies
    base_curr = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_CURRENCY_BASE
    )

    profit_curr = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_CURRENCY_PROFIT
    )

    print(f"Symbol Metadata: {symbol}")
    print(f"  Description: {desc.value}")
    print(f"  Path: {path.value}")
    print(f"  Base Currency: {base_curr.value}")
    print(f"  Profit Currency: {profit_curr.value}")

# Usage
await display_symbol_metadata(account, "EURUSD")
```

### 7) Get symbol with timeout

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta

deadline = datetime.utcnow() + timedelta(seconds=3)

try:
    result = await account.symbol_info_string(
        symbol="GBPUSD",
        property=market_info_pb2.SYMBOL_DESCRIPTION,
        deadline=deadline
    )
    print(f"Description: {result.value}")
except Exception as e:
    print(f"Timeout or error: {e}")
```

---

## 📚 See also

* [symbol_info_double](./symbol_info_double.md) - Get double properties
* [symbol_info_integer](./symbol_info_integer.md) - Get integer properties
* [symbol_params_many](./symbol_params_many.md) - Get all symbol parameters at once
