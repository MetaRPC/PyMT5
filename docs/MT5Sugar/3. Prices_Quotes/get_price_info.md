# Get Complete Price Information (`get_price_info`)

> **Sugar method:** Returns complete price data (BID, ASK, spread, timestamp) in one call.

**API Information:**

* **Method:** `sugar.get_price_info(symbol: Optional[str] = None)`
* **Returns:** `PriceInfo` dataclass with bid, ask, spread, time, symbol
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_price_info(
    self,
    symbol: Optional[str] = None
) -> PriceInfo
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | No | `None` | Symbol name (uses default if not specified) |

---

## Return Value

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Symbol name |
| `bid` | `float` | Current BID price (sell price) |
| `ask` | `float` | Current ASK price (buy price) |
| `spread` | `float` | Current spread (ask - bid) |
| `time` | `datetime` | Price timestamp |

---

## 🏛️ Essentials

**What it does:**

- Fetches complete tick data from MT5 terminal
- Calculates spread automatically
- Returns structured PriceInfo dataclass
- Uses default symbol if not specified

**Key behaviors:**

- Raises `ValueError` if no symbol specified and no default set
- Returns real-time market data
- Spread is calculated (not from terminal spread field)

---

## ⚡ Under the Hood

```
MT5Sugar.get_price_info()
    ↓ calls
MT5Service.get_symbol_tick()
    ↓ calls
MT5Account.symbol_info_tick()
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoTick()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar validates symbol (uses default or raises error)
2. Service retrieves tick via Account layer
3. Account sends gRPC request to terminal
4. Sugar wraps result in PriceInfo dataclass with calculated spread

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:530`
- Service: `src/pymt5/mt5_service.py:1145`
- Account: `package/helpers/mt5_account.py:1850`

---

## When to Use

**Use `get_price_info()` when:**

- You need complete price snapshot with timestamp
- Building price monitoring systems
- Need to log price data with exact time
- Want structured data instead of separate calls

**Don't use when:**

- You only need BID or ASK (use `get_bid()` or `get_ask()`)
- You only need spread (use `get_spread()`)
- Need streaming updates (use position profit streaming instead)

---

## 🔗 Examples

### Example 1: Basic Price Information

```python
from pymt5 import MT5Sugar

async def check_current_price():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Get complete price info
    price = await sugar.get_price_info()

    print(f"Symbol: {price.symbol}")
    print(f"BID: {price.bid}")
    print(f"ASK: {price.ask}")
    print(f"Spread: {price.spread}")
    print(f"Time: {price.time}")

    await sugar.disconnect()

# Output:
# Symbol: EURUSD
# BID: 1.08432
# ASK: 1.08445
# Spread: 0.00013
# Time: 2026-02-03 14:23:15
```

### Example 2: Price for Specific Symbol

```python
async def compare_symbols():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await sugar.connect()

    # Get prices for multiple symbols
    eurusd = await sugar.get_price_info("EURUSD")
    gbpusd = await sugar.get_price_info("GBPUSD")

    print(f"EURUSD spread: {eurusd.spread:.5f}")
    print(f"GBPUSD spread: {gbpusd.spread:.5f}")

    await sugar.disconnect()
```

### Example 3: Price Logging System

```python
import asyncio
from datetime import datetime

async def log_prices():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Log prices every 5 seconds
    for _ in range(10):
        price = await sugar.get_price_info()

        log_entry = (
            f"{price.time} | "
            f"BID: {price.bid} | "
            f"ASK: {price.ask} | "
            f"Spread: {price.spread:.5f}"
        )
        print(log_entry)

        await asyncio.sleep(5)

    await sugar.disconnect()
```

---

## Common Pitfalls

**Pitfall 1: No default symbol set**
```python
# ERROR: No symbol specified
sugar = MT5Sugar(user=123, password="pass", grpc_server="server")
await sugar.connect()
price = await sugar.get_price_info()  # Raises ValueError
```

**Solution:** Always specify symbol or set default
```python
# Option 1: Set default
sugar = MT5Sugar(..., default_symbol="EURUSD")
price = await sugar.get_price_info()

# Option 2: Pass explicitly
price = await sugar.get_price_info("EURUSD")
```

**Pitfall 2: Using stale price data**
```python
# Price is snapshot, not live-updating
price = await sugar.get_price_info()
await asyncio.sleep(60)
print(price.bid)  # Shows old price from 60 seconds ago
```

**Solution:** Always fetch fresh data before using
```python
# Get new snapshot when needed
price = await sugar.get_price_info()
print(price.bid)  # Current price
```

---

## Pro Tips

**Tip 1: Structured data for easy access**

```python
price = await sugar.get_price_info()

# Clean access to all fields
mid_price = (price.bid + price.ask) / 2
spread_pct = (price.spread / price.bid) * 100
age = datetime.now() - price.time
```

**Tip 2: Use for price validation**

```python
price = await sugar.get_price_info()

# Check if spread is too wide
if price.spread > 0.0005:  # 5 pips for EURUSD
    print(f"Warning: Wide spread detected ({price.spread})")
```

**Tip 3: Combine with symbol info**

```python
# Get price and calculate in account currency
price = await sugar.get_price_info("EURUSD")
symbol_info = await sugar._service.get_symbol_info("EURUSD")

# Use price with symbol digits for proper formatting
formatted_bid = f"{price.bid:.{symbol_info.digits}f}"
```

---

## 📚 See Also

- [get_bid](get_bid.md) - Get only BID price
- [get_ask](get_ask.md) - Get only ASK price
- [get_spread](get_spread.md) - Get only spread
- [wait_for_price](wait_for_price.md) - Wait for price update with timeout
