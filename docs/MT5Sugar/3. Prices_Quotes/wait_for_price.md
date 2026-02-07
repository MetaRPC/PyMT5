# Wait for Price Update (`wait_for_price`)

> **Sugar method:** Waits for valid price update with configurable timeout.

**API Information:**

* **Method:** `sugar.wait_for_price(symbol: Optional[str] = None, timeout: float = 5.0)`
* **Returns:** `PriceInfo` dataclass when price is received
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def wait_for_price(
    self,
    symbol: Optional[str] = None,
    timeout: float = 5.0
) -> PriceInfo
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | No | `None` | Symbol name (uses default if not specified) |
| `timeout` | `float` | No | `5.0` | Maximum wait time in seconds |

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

- Attempts to fetch price within timeout period
- Uses asyncio.timeout for time-limited operation
- Raises TimeoutError if no price received in time
- Returns PriceInfo on success

**Key behaviors:**

- Raises `ValueError` if no symbol specified and no default set
- Raises `TimeoutError` if timeout expires before price received
- Default timeout is 5 seconds
- Internally calls `get_price_info()`

---

## ⚡ Under the Hood

```
MT5Sugar.wait_for_price()
    ↓ wraps with timeout
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

1. Sugar wraps get_price_info() with asyncio.timeout context
2. If price received within timeout, returns PriceInfo
3. If timeout expires, raises TimeoutError with descriptive message
4. Timeout mechanism prevents indefinite hanging

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:545`
- Internal call to get_price_info: `src/pymt5/mt5_sugar.py:530`

---

## When to Use

**Use `wait_for_price()` when:**

- Starting up and need to ensure market connection
- Validating symbol has live quotes
- Need price with timeout guarantee
- Building robust startup sequences

**Don't use when:**

- You know market is open (use `get_price_info()`)
- Need streaming updates (use position profit streaming)
- Timeout isn't important (use `get_price_info()`)

---

## 🔗 Examples

### Example 1: Safe Connection Startup

```python
from pymt5 import MT5Sugar

async def connect_and_validate():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    try:
        # Wait up to 10 seconds for valid price
        price = await sugar.wait_for_price(timeout=10.0)
        print(f"Connection validated! BID: {price.bid}")

    except TimeoutError as e:
        print(f"Failed to get price: {e}")
        await sugar.disconnect()
        return

    # Continue with trading logic
    await sugar.disconnect()
```

### Example 2: Multiple Symbol Validation

```python
async def validate_symbols():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await sugar.connect()

    symbols = ["EURUSD", "GBPUSD", "USDJPY"]

    for symbol in symbols:
        try:
            price = await sugar.wait_for_price(symbol, timeout=3.0)
            print(f"{symbol}: OK (BID: {price.bid})")

        except TimeoutError:
            print(f"{symbol}: No quotes available")

    await sugar.disconnect()
```

### Example 3: Retry with Exponential Backoff

```python
import asyncio

async def get_price_with_retry():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    max_attempts = 3
    timeout = 5.0

    for attempt in range(max_attempts):
        try:
            price = await sugar.wait_for_price(timeout=timeout)
            print(f"Success on attempt {attempt + 1}")
            print(f"BID: {price.bid}, ASK: {price.ask}")
            break

        except TimeoutError:
            print(f"Attempt {attempt + 1} failed, retrying...")
            timeout *= 2  # Exponential backoff

            if attempt == max_attempts - 1:
                print("All attempts failed")

    await sugar.disconnect()
```

---

## Common Pitfalls

**Pitfall 1: Too short timeout**
```python
# ERROR: Timeout too short for slow connections
try:
    price = await sugar.wait_for_price(timeout=0.1)
except TimeoutError:
    # Fails even with valid connection
    pass
```

**Solution:** Use reasonable timeout (5-10 seconds)
```python
# Give enough time for network and terminal
price = await sugar.wait_for_price(timeout=10.0)
```

**Pitfall 2: Using during market close**
```python
# Market closed, will always timeout
try:
    price = await sugar.wait_for_price("EURUSD", timeout=5.0)
except TimeoutError:
    # Expected during weekends/holidays
    pass
```

**Solution:** Check market hours first or handle timeout gracefully
```python
try:
    price = await sugar.wait_for_price(timeout=5.0)
except TimeoutError:
    print("Market may be closed or symbol unavailable")
```

**Pitfall 3: Not handling TimeoutError**
```python
# ERROR: Unhandled exception crashes program
price = await sugar.wait_for_price(timeout=3.0)  # May raise!
```

**Solution:** Always wrap in try-except
```python
try:
    price = await sugar.wait_for_price(timeout=3.0)
except TimeoutError as e:
    # Handle timeout gracefully
    logger.error(f"Price timeout: {e}")
```

---

## Pro Tips

**Tip 1: Validate connection after connect**
```python
await sugar.connect()

# Ensure connection is fully operational
try:
    await sugar.wait_for_price(timeout=10.0)
    print("Connection ready")
except TimeoutError:
    print("Connection established but no market data")
```

**Tip 2: Use for market hours detection**
```python
# Quick market availability check
try:
    await sugar.wait_for_price(timeout=2.0)
    market_open = True
except TimeoutError:
    market_open = False

print(f"Market {'open' if market_open else 'closed'}")
```

**Tip 3: Combine with symbol selection**
```python
# Ensure symbol is selected and has quotes
symbol = "EURUSD"
await sugar._service.symbol_select(symbol, True)

# Wait for price to confirm selection worked
try:
    price = await sugar.wait_for_price(symbol, timeout=5.0)
    print(f"{symbol} selected and receiving quotes")
except TimeoutError:
    print(f"{symbol} selection failed or no quotes")
```

---

## 📚 See Also

- [get_price_info](get_price_info.md) - Get price without timeout
- [get_bid](get_bid.md) - Get only BID price
- [get_ask](get_ask.md) - Get only ASK price
- [get_spread](get_spread.md) - Get only spread
