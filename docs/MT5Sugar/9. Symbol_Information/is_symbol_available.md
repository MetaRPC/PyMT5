# Is Symbol Available (`is_symbol_available`)

> **Sugar method:** Checks if trading symbol exists and is available.

**API Information:**

* **Method:** `sugar.is_symbol_available(symbol)`
* **Returns:** Boolean indicating if symbol exists
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def is_symbol_available(self, symbol: str) -> bool
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Yes | - | Trading symbol to check (e.g., "EURUSD") |

---

## Return Value

| Type | Description |
|------|-------------|
| `bool` | `True` if symbol exists and is available, `False` otherwise |

---

## 🏛️ Essentials

**What it does:**

- Checks if symbol exists on broker
- Verifies symbol is currently available
- Fast validation before trading
- Returns boolean (True/False)

**Key behaviors:**

- Returns False if symbol doesn't exist
- Returns False if symbol is disabled
- Case-sensitive symbol name
- Fast single query (not batch)
- Does NOT check if symbol is tradable (only if it exists)

---

## ⚡ Under the Hood

```
MT5Sugar.is_symbol_available()
    ↓ calls
MT5Service.symbol_exist(symbol)
    ↓ calls
MT5Account.symbol_exist()
    ↓ gRPC protobuf
MarketInfoService.SymbolExist()
    ↓ MT5 Terminal
    ↓ returns (exists: bool, _)
```

**Call chain:**

1. Sugar calls Service.symbol_exist() with symbol name
2. Service forwards to Account.symbol_exist()
3. Account sends gRPC request to terminal
4. Terminal checks if symbol exists
5. Returns tuple (exists: bool, unknown)
6. Sugar extracts and returns exists boolean

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1672`
- Service: `src/pymt5/mt5_service.py:567`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:730`

---

## When to Use

**Use `is_symbol_available()` when:**

- Validating user input before trading
- Checking symbol existence before fetching info
- Error prevention in trading loops
- Symbol validation in configuration
- Building safe trading applications

**Don't use when:**

- Already know symbol exists (skip check)
- Need full symbol info (use `get_symbol_info()`)
- Listing all symbols (use `get_all_symbols()`)
- Symbol is hardcoded and known valid

---

## 🔗 Examples

### Example 1: Validate Symbol Before Trading

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def safe_trade():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Check if symbol exists
    if await sugar.is_symbol_available(symbol):
        print(f"{symbol} is available")

        # Safe to trade
        ticket = await sugar.buy_market(symbol, volume=0.1)
        print(f"Order placed: {ticket}")
    else:
        print(f"{symbol} not available on this broker")

# Output:
# EURUSD is available
# Order placed: 123456789
```

### Example 2: Validate User Input

```python
async def validate_user_symbol():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # User provides symbol
    user_symbol = input("Enter symbol: ").upper()

    # Validate
    if not await sugar.is_symbol_available(user_symbol):
        print(f"Error: '{user_symbol}' is not available")
        print("Please check the symbol name and try again")
        return

    # Continue with valid symbol
    info = await sugar.get_symbol_info(user_symbol)
    print(f"{user_symbol}: BID={info.bid}, ASK={info.ask}")

# Example interaction:
# Enter symbol: FAKEUSD
# Error: 'FAKEUSD' is not available
# Please check the symbol name and try again
```

### Example 3: Validate Symbol List

```python
async def validate_watchlist():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # User's watchlist
    watchlist = ["EURUSD", "GBPUSD", "FAKEUSD", "USDJPY", "XAUUSD"]

    # Validate all symbols
    valid_symbols = []
    invalid_symbols = []

    for symbol in watchlist:
        if await sugar.is_symbol_available(symbol):
            valid_symbols.append(symbol)
        else:
            invalid_symbols.append(symbol)

    print(f"Valid symbols ({len(valid_symbols)}): {valid_symbols}")
    print(f"Invalid symbols ({len(invalid_symbols)}): {invalid_symbols}")

# Output:
# Valid symbols (4): ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
# Invalid symbols (1): ['FAKEUSD']
```

---

## Common Pitfalls

**Pitfall 1: Case sensitivity**
```python
# ERROR: Symbol case matters
exists = await sugar.is_symbol_available("eurusd")
# Returns False if broker uses "EURUSD"
```

**Solution:** Always use uppercase
```python
symbol = "eurusd"
exists = await sugar.is_symbol_available(symbol.upper())
```

**Pitfall 2: Assuming available means tradable**
```python
# Symbol exists but might not be tradable right now
if await sugar.is_symbol_available("EURUSD"):
    # Symbol exists, but might be:
    # - Market closed
    # - Trading disabled
    # - Insufficient margin
    await sugar.buy_market("EURUSD", volume=0.1)  # May still fail
```

**Solution:** Handle trade errors separately
```python
if await sugar.is_symbol_available("EURUSD"):
    try:
        ticket = await sugar.buy_market("EURUSD", volume=0.1)
    except Exception as e:
        print(f"Trade failed: {e}")
```

**Pitfall 3: Checking before every operation**
```python
# Redundant checks
if await sugar.is_symbol_available("EURUSD"):
    info = await sugar.get_symbol_info("EURUSD")  # Already validates

if await sugar.is_symbol_available("EURUSD"):
    bid = await sugar.get_bid("EURUSD")  # Also validates
```

**Solution:** Check once, then proceed
```python
# Single validation
if await sugar.is_symbol_available("EURUSD"):
    # All subsequent calls will work
    info = await sugar.get_symbol_info("EURUSD")
    bid = await sugar.get_bid("EURUSD")
```

---

## Pro Tips

**Tip 1: Validate with fallback**
```python
async def get_symbol_with_fallback(primary, fallback):
    """Try primary symbol, fall back if unavailable."""
    if await sugar.is_symbol_available(primary):
        return primary
    elif await sugar.is_symbol_available(fallback):
        print(f"{primary} not available, using {fallback}")
        return fallback
    else:
        raise ValueError(f"Neither {primary} nor {fallback} available")

# Usage
symbol = await get_symbol_with_fallback("EURUSD", "EURUSD.a")
```

**Tip 2: Batch validation helper**
```python
async def validate_symbols(symbols: List[str]) -> dict:
    """Validate multiple symbols efficiently."""
    results = {}

    for symbol in symbols:
        results[symbol] = await sugar.is_symbol_available(symbol)

    return results

# Usage
symbols = ["EURUSD", "GBPUSD", "FAKEUSD"]
results = await validate_symbols(symbols)

valid = [s for s, exists in results.items() if exists]
invalid = [s for s, exists in results.items() if not exists]

print(f"Valid: {valid}")
print(f"Invalid: {invalid}")
```

**Tip 3: Safe symbol getter**
```python
async def get_symbol_info_safe(symbol: str):
    """Get symbol info with existence check."""
    if not await sugar.is_symbol_available(symbol):
        raise ValueError(f"Symbol '{symbol}' not available")

    return await sugar.get_symbol_info(symbol)

# Usage
try:
    info = await get_symbol_info_safe("EURUSD")
    print(f"Got info: {info.name}")
except ValueError as e:
    print(f"Error: {e}")
```

---

## 📚 See Also

- [get_symbol_info](get_symbol_info.md) - Get complete symbol information
- [get_all_symbols](get_all_symbols.md) - List all available symbols
- [get_symbol_digits](get_symbol_digits.md) - Get decimal places
