# Get Symbol Digits (`get_symbol_digits`)

> **Sugar method:** Returns number of decimal places in symbol price.

**API Information:**

* **Method:** `sugar.get_symbol_digits(symbol)`
* **Returns:** Number of digits after decimal point (integer)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_symbol_digits(self, symbol: str) -> int
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Yes | - | Trading symbol (e.g., "EURUSD") |

---

## Return Value

| Type | Description |
|------|-------------|
| `int` | Number of decimal places (e.g., 5 for EURUSD, 3 for USDJPY, 2 for XAUUSD) |

---

## 🏛️ Essentials

**What it does:**

- Gets decimal precision for symbol prices
- Essential for price formatting
- Used in price calculations
- Broker-specific value

**Key behaviors:**

- Forex majors typically 5 digits (EURUSD: 1.08432)
- JPY pairs typically 3 digits (USDJPY: 149.385)
- Metals typically 2 digits (XAUUSD: 2043.50)
- Required for proper price display
- Used in rounding calculations

---

## ⚡ Under the Hood

```
MT5Sugar.get_symbol_digits()
    ↓ calls
MT5Service.get_symbol_integer(symbol, SYMBOL_DIGITS)
    ↓ calls
MT5Account.symbol_info_integer()
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoInteger(property=SYMBOL_DIGITS)
    ↓ MT5 Terminal
    ↓ returns digits value
```

**Call chain:**

1. Sugar calls Service.get_symbol_integer() with SYMBOL_DIGITS property
2. Service forwards to Account.symbol_info_integer()
3. Account sends gRPC request with property enum
4. Terminal retrieves digits value for symbol
5. Returns integer (number of decimal places)

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:1697`
- Service: `src/pymt5/mt5_service.py:497`
- Account: `package/helpers/mt5_account.py:951`

---

## When to Use

**Use `get_symbol_digits()` when:**

- Formatting prices for display
- Rounding prices to valid precision
- Calculating price differences
- Logging price values
- Building price input validation

**Don't use when:**

- Already have SymbolInfo (use info.digits)
- Hardcoded symbols with known digits
- Don't need precise formatting
- Working with volumes (not prices)

---

## 🔗 Examples

### Example 1: Format Prices Correctly

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def format_prices():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbols = ["EURUSD", "USDJPY", "XAUUSD"]

    for symbol in symbols:
        # Get digits
        digits = await sugar.get_symbol_digits(symbol)

        # Get current price
        bid = await sugar.get_bid(symbol)

        # Format with correct precision
        formatted = f"{bid:.{digits}f}"

        print(f"{symbol}: {formatted} ({digits} digits)")

# Output:
# EURUSD: 1.08432 (5 digits)
# USDJPY: 149.385 (3 digits)
# XAUUSD: 2043.50 (2 digits)
```

### Example 2: Round Price to Valid Precision

```python
async def round_price():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # User calculates custom price
    calculated_price = 1.084567890123  # Too many decimals

    # Get valid precision
    digits = await sugar.get_symbol_digits(symbol)

    # Round to valid precision
    valid_price = round(calculated_price, digits)

    print(f"Calculated: {calculated_price}")
    print(f"Rounded ({digits} digits): {valid_price:.{digits}f}")

    # Now safe to use in order
    ticket = await sugar.buy_limit(
        symbol,
        volume=0.1,
        price=valid_price
    )

# Output:
# Calculated: 1.084567890123
# Rounded (5 digits): 1.08457
```

### Example 3: Calculate Pip Value

```python
async def calculate_pips():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Get two prices
    price1 = 1.08432
    price2 = 1.08567

    # Get digits to determine pip size
    digits = await sugar.get_symbol_digits(symbol)

    # Calculate difference
    diff = abs(price2 - price1)

    # Convert to pips based on digits
    if digits == 5 or digits == 3:
        # 5-digit pricing: 1 pip = 10 points
        pips = diff * (10 ** (digits - 1)) / 10
    elif digits == 4 or digits == 2:
        # 4-digit pricing: 1 pip = 1 point
        pips = diff * (10 ** digits)
    else:
        pips = 0

    print(f"{symbol} ({digits} digits):")
    print(f"Price 1: {price1:.{digits}f}")
    print(f"Price 2: {price2:.{digits}f}")
    print(f"Difference: {pips:.1f} pips")

# Output:
# EURUSD (5 digits):
# Price 1: 1.08432
# Price 2: 1.08567
# Difference: 13.5 pips
```

---

## Common Pitfalls

**Pitfall 1: Hardcoding digits**
```python
# ERROR: Digits can vary by broker
price = 1.08432
formatted = f"{price:.5f}"  # Assumes 5 digits

# Works for some brokers, fails for others
```

**Solution:** Always fetch dynamically
```python
digits = await sugar.get_symbol_digits(symbol)
formatted = f"{price:.{digits}f}"
```

**Pitfall 2: Confusing digits with point**
```python
# ERROR: digits != point value
digits = await sugar.get_symbol_digits("EURUSD")  # Returns 5

# This is NOT the same as point (0.00001)
point = 10 ** -digits  # 0.00001 ✓
```

**Solution:** Use SymbolInfo for point
```python
info = await sugar.get_symbol_info("EURUSD")
digits = info.digits  # 5
point = info.point    # 0.00001
```

**Pitfall 3: Using wrong decimal separator**
```python
# System locale might use comma
import locale
locale.setlocale(locale.LC_ALL, 'de_DE')

price = 1.08432
formatted = f"{price:.5f}"  # Might print "1,08432" in some locales

# MT5 expects dot, not comma
```

**Solution:** Force dot separator
```python
# Always use dot for MT5
formatted = f"{price:.{digits}f}".replace(',', '.')

# Or use explicit formatting
formatted = "{:.{}f}".format(price, digits)
```

---

## Pro Tips

**Tip 1: Price formatter helper**
```python
async def format_price(sugar, symbol, price):
    """Format price with correct precision for symbol."""
    digits = await sugar.get_symbol_digits(symbol)
    return f"{price:.{digits}f}"

# Usage
bid = await sugar.get_bid("EURUSD")
formatted = await format_price(sugar, "EURUSD", bid)
print(f"BID: {formatted}")
```

**Tip 2: Price validator**
```python
async def validate_price_precision(sugar, symbol, price):
    """Check if price has valid precision."""
    digits = await sugar.get_symbol_digits(symbol)

    # Round to valid precision
    rounded = round(price, digits)

    # Check if it changed
    if rounded != price:
        print(f"Warning: Price {price} rounded to {rounded:.{digits}f}")
        return rounded

    return price

# Usage
price = 1.084567890  # Too many decimals
valid_price = await validate_price_precision(sugar, "EURUSD", price)
```

**Tip 3: Multi-symbol price table**
```python
async def price_table(sugar, symbols):
    """Display formatted prices for multiple symbols."""
    print(f"{'Symbol':<10} {'BID':<12} {'ASK':<12} {'Spread'}")
    print("-" * 50)

    for symbol in symbols:
        digits = await sugar.get_symbol_digits(symbol)
        bid = await sugar.get_bid(symbol)
        ask = await sugar.get_ask(symbol)
        spread = ask - bid

        print(f"{symbol:<10} "
              f"{bid:<12.{digits}f} "
              f"{ask:<12.{digits}f} "
              f"{spread:.{digits}f}")

# Usage
await price_table(sugar, ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"])

# Output:
# Symbol     BID          ASK          Spread
# --------------------------------------------------
# EURUSD     1.08432      1.08445      0.00013
# GBPUSD     1.26789      1.26805      0.00016
# USDJPY     149.385      149.398      0.013
# XAUUSD     2043.50      2043.80      0.30
```

---

## 📚 See Also

- [get_symbol_info](get_symbol_info.md) - Get complete symbol info (includes digits)
- [get_bid](../3.%20Prices_Quotes/get_bid.md) - Get current BID price
- [get_ask](../3.%20Prices_Quotes/get_ask.md) - Get current ASK price
