# Check if Symbol Exists

> **Request:** check if a symbol with specified name exists on the trading platform.

**API Information:**

* **Low-level API:** `MT5Account.symbol_exist(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolExist` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolExist(SymbolExistRequest) -> SymbolExistReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolExist(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Check if a symbol exists and whether it's standard or custom.
* **Why you need it.** Validate symbol names before trading or querying data.
* **When to use.** Use this before trading or subscribing to symbol data.

---

## 🎯 Purpose

Use it to validate symbols:

* Check if symbol exists on platform
* Identify standard vs custom symbols
* Validate user input
* Prevent errors when querying non-existent symbols
* Pre-trade validation

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_exist - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_exist_HOW.md)**

---

## Method Signature

```python
async def symbol_exist(
    self,
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
)
```

**Request message:**

```protobuf
message SymbolExistRequest {
  string name = 1;
}
```

**Reply message:**

```protobuf
message SymbolExistReply {
  oneof response {
    SymbolExistData data = 1;
    Error error = 2;
  }
}

message SymbolExistData {
  bool exists = 1;
  bool is_custom = 2;
}
```

---

## 🔽 Input

| Parameter     | Type                    | Description                                             |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `symbol`      | `str` (required)        | Symbol name to check                                    |
| `deadline`    | `datetime` (optional)   | Deadline for the gRPC call (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                    |

---

## ⬆️ Output - `SymbolExistData`

| Field       | Type   | Python Type | Description                                      |
| ----------- | ------ | ----------- | ------------------------------------------------ |
| `exists`    | `bool` | `bool`      | True if symbol exists                            |
| `is_custom` | `bool` | `bool`      | True if symbol is custom (not standard)          |

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors.
* **Case sensitive:** Symbol names are case-sensitive.

---

## 🔗 Usage Examples

### 1) Check if symbol exists

```python
async def main():
    account = MT5Account(...)
    await account.connect_by_host_port()

    data = await account.symbol_exist(symbol="EURUSD")

    if data.exists:
        symbol_type = "custom" if data.is_custom else "standard"
        print(f"[OK] EURUSD exists ({symbol_type})")
    else:
        print("[ERROR] EURUSD does not exist")
```

### 2) Validate symbol before trading

```python
async def validate_symbol(account: MT5Account, symbol: str) -> bool:
    """Validate symbol exists before trading"""
    data = await account.symbol_exist(symbol=symbol)

    if not data.exists:
        print(f"[ERROR] Symbol {symbol} does not exist")
        return False

    print(f"[OK] Symbol {symbol} validated")
    return True

# Usage:
if await validate_symbol(account, "EURUSD"):
    # Place trade
    pass
```

### 3) Check multiple symbols

```python
async def check_symbols(account: MT5Account, symbols: list[str]):
    """Check which symbols exist"""
    results = {}

    for symbol in symbols:
        data = await account.symbol_exist(symbol=symbol)
        results[symbol] = data.exists

    # Print results
    for symbol, exists in results.items():
        status = "[OK]" if exists else "[ERROR]"
        print(f"{status} {symbol}: {'exists' if exists else 'not found'}")

    return results

# Usage:
symbols = ["EURUSD", "GBPUSD", "INVALID"]
await check_symbols(account, symbols)
```

### 4) Filter valid symbols

```python
async def filter_valid_symbols(
    account: MT5Account,
    symbols: list[str]
) -> list[str]:
    """Filter out non-existent symbols"""
    valid_symbols = []

    for symbol in symbols:
        data = await account.symbol_exist(symbol=symbol)
        if data.exists:
            valid_symbols.append(symbol)

    print(f"[OK] {len(valid_symbols)} of {len(symbols)} symbols are valid")
    return valid_symbols

# Usage:
symbols = ["EURUSD", "GBPUSD", "INVALID_SYMBOL"]
valid = await filter_valid_symbols(account, symbols)
```

### 5) Identify custom symbols

```python
async def get_symbol_type(account: MT5Account, symbol: str) -> str:
    """Get symbol type (standard/custom/not found)"""
    data = await account.symbol_exist(symbol=symbol)

    if not data.exists:
        return "not_found"
    return "custom" if data.is_custom else "standard"

# Usage:
symbol_type = await get_symbol_type(account, "EURUSD")
print(f"EURUSD type: {symbol_type}")
```

---

## Common Patterns

### Quick existence check

```python
async def symbol_exists(account: MT5Account, symbol: str) -> bool:
    """Quick check if symbol exists"""
    data = await account.symbol_exist(symbol=symbol)
    return data.exists
```

---

## 📚 See also

* [symbols_total](./symbols_total.md) - Get total symbol count
* [symbol_name](./symbol_name.md) - Get symbol name by index
* [symbol_select](./symbol_select.md) - Add/remove symbol from Market Watch
