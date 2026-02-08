# Open BUY Position at Market (`buy_market`)

> **Sugar method:** Opens BUY position at current market price in one call.

**API Information:**

* **Method:** `sugar.buy_market(symbol, volume, comment, magic)`
* **Returns:** Position ticket number (`int`)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def buy_market(
    self,
    symbol: Optional[str] = None,
    volume: float = 0.01,
    comment: str = "",
    magic: int = 0
) -> int
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | No | `None` | Trading symbol (uses default if not specified) |
| `volume` | `float` | No | `0.01` | Position volume in lots |
| `comment` | `str` | No | `""` | Order comment (visible in terminal) |
| `magic` | `int` | No | `0` | Magic number for order identification |

---

## Return Value

| Type | Description |
|------|-------------|
| `int` | Position ticket number (unique identifier) |

**Raises:**

- `ValueError` if symbol not specified and no default set
- `RuntimeError` if order execution fails (returned_code != 10009)

---

## 🏛️ Essentials

**What it does:**

- Fetches current ASK price from terminal
- Creates BUY market order request
- Executes order with 10 points slippage tolerance
- Returns ticket number on success

**Key behaviors:**

- BUY = profit when price RISES
- Uses ASK price (higher price)
- Default slippage: 10 points
- Raises exception if order fails
- Position opens immediately at market

---

## ⚡ Under the Hood

```
MT5Sugar.buy_market()
    ↓ fetches price
MT5Service.get_symbol_tick()
    ↓ builds OrderSendRequest
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar fetches current tick via Service layer
2. Sugar builds OrderSendRequest with TMT5_ORDER_TYPE_BUY
3. Sugar calls Service.place_order() with request
4. Service forwards to Account.order_send()
5. Account sends gRPC request to terminal
6. Sugar validates returned_code == 10009 (TRADE_RETCODE_DONE)
7. Returns ticket number from result.order

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:568`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## When to Use

**Use `buy_market()` when:**

- You expect price to go UP
- Need immediate position execution
- Don't need Stop Loss or Take Profit (simple entry)
- Building basic trading strategies

**Don't use when:**

- Need SL/TP on entry (use `buy_market_with_sltp()`)
- Want to enter at specific price (use `buy_limit()` or `buy_stop()`)
- Market is closed or illiquid
- Price is moving too fast (consider pending orders)

---

## 🔗 Examples

### Example 1: Basic BUY Position

```python
from pymt5 import MT5Sugar

async def simple_buy():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open BUY position with default volume (0.01 lot)
    ticket = await sugar.buy_market()
    print(f"Position opened: #{ticket}")

# Output:
# Position opened: #123456789
```

### Example 2: BUY with Custom Parameters

```python
async def buy_with_params():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await sugar.connect()

    # Open 0.1 lot BUY position on GBPUSD
    ticket = await sugar.buy_market(
        symbol="GBPUSD",
        volume=0.1,
        comment="Bull trend entry",
        magic=12345
    )

    print(f"GBPUSD BUY: ticket #{ticket}")
```

### Example 3: Error Handling

```python
async def safe_buy():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    try:
        ticket = await sugar.buy_market(volume=0.1)
        print(f"Success! Ticket: {ticket}")

        # Get current balance after trade
        balance = await sugar.get_balance()
        print(f"New balance: ${balance}")

    except RuntimeError as e:
        print(f"Order failed: {e}")
        # Handle failure (e.g., insufficient margin, market closed)
```

---

## Common Pitfalls

**Pitfall 1: No symbol specified**
```python
# ERROR: No default symbol set
sugar = MT5Sugar(user=123, password="pass", grpc_server="server")
await sugar.connect()
ticket = await sugar.buy_market()  # Raises ValueError
```

**Solution:** Always set default or pass symbol explicitly
```python
# Option 1: Set default
sugar = MT5Sugar(..., default_symbol="EURUSD")
ticket = await sugar.buy_market()

# Option 2: Pass explicitly
ticket = await sugar.buy_market(symbol="EURUSD")
```

**Pitfall 2: Insufficient margin**
```python
# ERROR: Trying to open position larger than account margin allows
try:
    ticket = await sugar.buy_market(volume=10.0)  # Too large
except RuntimeError as e:
    print(e)  # "Order failed: code=10019, comment=Insufficient margin"
```

**Solution:** Check free margin before trading
```python
free_margin = await sugar.get_free_margin()
# Calculate safe volume based on free margin
safe_volume = min(requested_volume, free_margin / margin_per_lot)
```

**Pitfall 3: Market closed**
```python
# ERROR: Trying to trade during weekend or holidays
try:
    ticket = await sugar.buy_market()  # Market closed
except RuntimeError as e:
    print(e)  # "Order failed: code=10018, comment=Market is closed"
```

**Solution:** Check market hours or handle gracefully
```python
try:
    ticket = await sugar.buy_market()
except RuntimeError as e:
    if "Market is closed" in str(e):
        print("Market closed, will retry later")
    else:
        raise
```

---

## Pro Tips

**Tip 1: Save ticket for later operations**
```python
# Open position and save ticket
ticket = await sugar.buy_market(volume=0.1)

# Later: close this specific position
await sugar.close_position(ticket)
```

**Tip 2: Use magic numbers to group trades**
```python
# Strategy 1 trades use magic 1000
ticket1 = await sugar.buy_market(magic=1000)

# Strategy 2 trades use magic 2000
ticket2 = await sugar.buy_market(magic=2000)

# Close only strategy 1 trades by filtering magic number
```

**Tip 3: Check price before opening**
```python
# Validate entry price is reasonable
bid = await sugar.get_bid()
ask = await sugar.get_ask()
spread = ask - bid

# Only trade if spread is reasonable
if spread < 0.0005:  # 5 pips for EURUSD
    ticket = await sugar.buy_market()
else:
    print(f"Spread too wide: {spread}")
```

---

## 📚 See Also

- [sell_market](sell_market.md) - Open SELL position at market
- [buy_limit](buy_limit.md) - Place BUY LIMIT pending order
- [buy_stop](buy_stop.md) - Place BUY STOP pending order
- [buy_market_with_sltp](../5.%20Trading_With_SLTP/buy_market_with_sltp.md) - Open BUY with SL/TP
- [close_position](../6.%20Position_Management/close_position.md) - Close position by ticket
