# Get All Symbols (`get_all_symbols`)

> **Sugar method:** Returns complete list of all available trading symbols.

**API Information:**

* **Method:** `sugar.get_all_symbols()`
* **Returns:** List of symbol names (strings)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_all_symbols(self) -> List[str]
```

---

## 🔽 Input Parameters

No parameters required.

---

## Return Value

| Type | Description |
|------|-------------|
| `List[str]` | List of all available symbol names (e.g., ["EURUSD", "GBPUSD", ...]) |

---

## 🏛️ Essentials

**What it does:**

- Fetches complete list of all symbols available on broker
- Uses optimized batch fetching with pagination
- Returns 100 symbols per page
- More efficient than individual symbol queries

**Key behaviors:**

- Automatically handles pagination
- Returns ALL symbols (not just visible ones)
- Fetches 100 symbols per request
- Can return hundreds of symbols
- Returns symbol names only (not full info)

---

## ⚡ Under the Hood

```
MT5Sugar.get_all_symbols()
    ↓ loops with pagination (100 per page)
    ↓ calls
MT5Service.get_symbol_params_many(name_filter=None)
    ↓ calls
MT5Account.symbol_params_many()
    ↓ gRPC protobuf
MarketInfoService.SymbolParamsMany()
    ↓ MT5 Terminal
    ↓ extracts symbol names from SymbolParams
```

**Call chain:**

1. Sugar starts pagination loop (page=1, size=100)
2. Sugar calls Service.get_symbol_params_many() with no filter
3. Service forwards to Account.symbol_params_many()
4. Account sends gRPC request to terminal
5. Sugar extracts name from each SymbolParams
6. Continues pagination until all symbols fetched
7. Returns complete list of symbol names

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1642`
- Service: `src/pymt5/mt5_service.py:658`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1221`

---

## When to Use

**Use `get_all_symbols()` when:**

- Building symbol selection UI
- Scanning all symbols for opportunities
- Validating symbol lists
- Discovering available instruments
- Symbol autocomplete features

**Don't use when:**

- Only need specific symbols (hardcode them)
- Only need forex pairs (use filtered approach)
- Need full symbol info (use `get_symbol_info()`)
- Checking if one symbol exists (use `is_symbol_available()`)

---

## 🔗 Examples

### Example 1: List All Available Symbols

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def list_symbols():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get all symbols
    symbols = await sugar.get_all_symbols()

    print(f"Total symbols available: {len(symbols)}")
    print(f"First 10 symbols: {symbols[:10]}")

# Output:
# Total symbols available: 358
# First 10 symbols: ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'CHFJPY', 'EURAUD', 'EURCAD']
```

### Example 2: Find Forex Pairs Only

```python
async def find_forex_pairs():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get all symbols
    all_symbols = await sugar.get_all_symbols()

    # Common forex currency codes
    currencies = ['EUR', 'USD', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']

    # Filter forex pairs (both currencies in common list)
    forex_pairs = [
        s for s in all_symbols
        if len(s) == 6 and s[:3] in currencies and s[3:] in currencies
    ]

    print(f"Forex pairs: {len(forex_pairs)}")
    print(forex_pairs)

# Output:
# Forex pairs: 28
# ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', ...]
```

### Example 3: Search for Specific Symbols

```python
async def search_symbols():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Get all symbols
    all_symbols = await sugar.get_all_symbols()

    # Find gold symbols
    gold_symbols = [s for s in all_symbols if 'XAU' in s or 'GOLD' in s]
    print(f"Gold symbols: {gold_symbols}")

    # Find EUR pairs
    eur_pairs = [s for s in all_symbols if s.startswith('EUR')]
    print(f"EUR pairs ({len(eur_pairs)}): {eur_pairs}")

    # Find crypto
    crypto = [s for s in all_symbols if 'BTC' in s or 'ETH' in s]
    print(f"Crypto: {crypto}")
```

---

## Common Pitfalls

**Pitfall 1: Expecting sorted results**
```python
# Symbols may not be in alphabetical order
symbols = await sugar.get_all_symbols()
# Order depends on broker's response
```

**Solution:** Sort manually if needed
```python
symbols = await sugar.get_all_symbols()
symbols_sorted = sorted(symbols)
```

**Pitfall 2: Not caching results**
```python
# Fetching all symbols repeatedly is slow
for i in range(10):
    symbols = await sugar.get_all_symbols()  # Slow!
    # Do something with symbols
```

**Solution:** Cache the list
```python
# Fetch once
symbols_cache = await sugar.get_all_symbols()

# Use cached list
for i in range(10):
    # Use symbols_cache
    pass
```

**Pitfall 3: Assuming all symbols are tradable**
```python
# Not all symbols may be currently tradable
symbols = await sugar.get_all_symbols()

# Some might be disabled or restricted
for symbol in symbols:
    await sugar.buy_market(symbol, volume=0.01)  # May fail!
```

**Solution:** Check if symbol is tradable first
```python
symbols = await sugar.get_all_symbols()

for symbol in symbols:
    # Check availability
    is_available = await sugar.is_symbol_available(symbol)

    if is_available:
        # Now safe to trade
        pass
```

---

## Pro Tips

**Tip 1: Cache symbols with TTL**
```python
from datetime import datetime, timedelta

class SymbolCache:
    def __init__(self, ttl_minutes=60):
        self.symbols = None
        self.last_fetch = None
        self.ttl = timedelta(minutes=ttl_minutes)

    async def get_symbols(self, sugar):
        """Get symbols with 1-hour cache."""
        now = datetime.now()

        if self.symbols is None or (now - self.last_fetch) > self.ttl:
            self.symbols = await sugar.get_all_symbols()
            self.last_fetch = now

        return self.symbols

# Usage
cache = SymbolCache(ttl_minutes=60)
symbols = await cache.get_symbols(sugar)
```

**Tip 2: Group symbols by type**
```python
from collections import defaultdict

async def group_symbols_by_type():
    """Group symbols into categories."""
    symbols = await sugar.get_all_symbols()

    groups = defaultdict(list)

    for symbol in symbols:
        if 'XAU' in symbol or 'GOLD' in symbol:
            groups['Metals'].append(symbol)
        elif 'BTC' in symbol or 'ETH' in symbol:
            groups['Crypto'].append(symbol)
        elif len(symbol) == 6:  # Likely forex
            groups['Forex'].append(symbol)
        else:
            groups['Other'].append(symbol)

    for category, syms in groups.items():
        print(f"{category}: {len(syms)} symbols")
```

**Tip 3: Create symbol autocomplete**
```python
async def autocomplete_symbol(prefix: str):
    """Autocomplete symbol names."""
    all_symbols = await sugar.get_all_symbols()

    # Find matches
    matches = [s for s in all_symbols if s.startswith(prefix.upper())]

    return matches[:10]  # Return top 10 matches

# Usage
matches = await autocomplete_symbol("EUR")
print(matches)  # ['EURAUD', 'EURCAD', 'EURCHF', ...]
```

---

## 📚 See Also

- [get_symbol_info](get_symbol_info.md) - Get complete symbol parameters
- [is_symbol_available](is_symbol_available.md) - Check if symbol exists
- [get_symbol_digits](get_symbol_digits.md) - Get decimal places for symbol
