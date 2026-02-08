# Place BUY STOP Order (`buy_stop`)

> **Sugar method:** Places BUY STOP pending order to buy above current price (breakout entry).

**API Information:**

* **Method:** `sugar.buy_stop(symbol, volume, price, comment, magic)`
* **Returns:** Order ticket number (`int`)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def buy_stop(
    self,
    symbol: Optional[str] = None,
    volume: float = 0.01,
    price: float = 0.0,
    comment: str = "",
    magic: int = 0
) -> int
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | No | `None` | Trading symbol (uses default if not specified) |
| `volume` | `float` | No | `0.01` | Order volume in lots |
| `price` | `float` | Yes | `0.0` | Stop price (must be ABOVE current ASK) |
| `comment` | `str` | No | `""` | Order comment (visible in terminal) |
| `magic` | `int` | No | `0` | Magic number for order identification |

---

## Return Value

| Type | Description |
|------|-------------|
| `int` | Order ticket number (unique identifier) |

**Raises:**

- `ValueError` if symbol not specified and no default set
- `RuntimeError` if order placement fails (returned_code != 10009)

---

## 🏛️ Essentials

**What it does:**

- Creates pending BUY STOP order
- Order triggers when ASK price rises to specified level
- Automatically converts to BUY position when triggered
- Order remains pending until triggered or cancelled

**Key behaviors:**

- BUY STOP price must be ABOVE current ASK
- Used for breakout trading (buy when price breaks resistance)
- Executes at market once stop price reached (not at exact price)
- Useful for trend following strategies

---

## ⚡ Under the Hood

```
MT5Sugar.buy_stop()
    ↓ builds OrderSendRequest
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar builds OrderSendRequest with TMT5_ORDER_TYPE_BUY_STOP
2. Sugar calls Service.place_order() with request
3. Service forwards to Account.order_send()
4. Account sends gRPC request to terminal
5. Sugar validates returned_code == 10009 (TRADE_RETCODE_DONE)
6. Returns order ticket from result.order
7. Order stays pending until price reaches stop level

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:738`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## When to Use

**Use `buy_stop()` when:**

- Trading breakouts above resistance
- Following upward trend (buy momentum)
- Want to enter only if price confirms direction
- Implementing breakout strategies

**Don't use when:**

- Need immediate position (use `buy_market()`)
- Want to buy at lower price (use `buy_limit()`)
- Price may reverse before reaching stop
- In ranging market (false breakouts)

---

## 🔗 Examples

### Example 1: Basic Breakout Entry

```python
from pymt5 import MT5Sugar

async def breakout_buy():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Current ASK: 1.0850
    # Resistance at 1.0870
    # Place BUY STOP above resistance
    ticket = await sugar.buy_stop(
        price=1.0875,
        volume=0.1,
        comment="Breakout buy at 1.0875"
    )

    print(f"BUY STOP order placed: #{ticket}")

# Output:
# BUY STOP order placed: #123456793
```

### Example 2: Multiple Breakout Levels

```python
async def tiered_breakout():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Current price: 1.0850
    # Key resistance levels
    resistances = [1.0870, 1.0900, 1.0930]

    tickets = []
    for resistance in resistances:
        # Place BUY STOP slightly above each resistance
        stop_price = resistance + 0.0005  # 5 pips above

        ticket = await sugar.buy_stop(
            price=stop_price,
            volume=0.01,
            comment=f"Breakout {resistance}"
        )
        tickets.append(ticket)
        print(f"BUY STOP at {stop_price}: #{ticket}")

    print(f"Total breakout orders: {len(tickets)}")
```

### Example 3: Trend Following with BUY STOP

```python
async def trend_following():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Get current high
    ask = await sugar.get_ask()

    # Place BUY STOP 20 pips above current price
    # (enters only if uptrend continues)
    symbol_info = await sugar.get_symbol_info()
    point = symbol_info.point

    stop_price = ask + (20 * point * 10)  # 20 pips above

    ticket = await sugar.buy_stop(
        price=stop_price,
        volume=0.1,
        comment="Trend confirmation"
    )

    print(f"BUY STOP at {stop_price} (confirms uptrend)")
    print(f"Order: #{ticket}")
```

---

## Common Pitfalls

**Pitfall 1: Price below current ASK**
```python
# ERROR: BUY STOP must be ABOVE current price
# Current ASK: 1.0850
try:
    ticket = await sugar.buy_stop(price=1.0840)  # Below current price
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price for BUY STOP"
```

**Solution:** Ensure stop price is above current ASK
```python
ask = await sugar.get_ask()  # 1.0850
stop_price = ask + 0.0020    # 1.0870 (above current)
ticket = await sugar.buy_stop(price=stop_price)
```

**Pitfall 2: Confusing BUY STOP with BUY LIMIT**
```python
# BUY LIMIT: Buy BELOW current price (better price)
# BUY STOP: Buy ABOVE current price (breakout)

# Current price: 1.0850

# LIMIT: Buy if price drops to 1.0840
buy_limit = await sugar.buy_limit(price=1.0840)

# STOP: Buy if price rises to 1.0870
buy_stop = await sugar.buy_stop(price=1.0870)
```

**Pitfall 3: False breakouts**
```python
# Price touches stop level then reverses
# Order gets triggered at 1.0870, then price falls to 1.0850
# Result: Immediate loss

# Stop order placed at 1.0870
ticket = await sugar.buy_stop(price=1.0870)
# Price spikes to 1.0871 (triggers order)
# Price falls back to 1.0850 (loss)
```

**Solution:** Place stop beyond significant level with buffer
```python
# Add buffer beyond resistance
resistance = 1.0870
buffer = 0.0005  # 5 pips buffer

stop_price = resistance + buffer  # 1.0875
ticket = await sugar.buy_stop(price=stop_price)
```

---

## Pro Tips

**Tip 1: Combine with Stop Loss**
```python
# Place BUY STOP with immediate SL plan
stop_price = 1.0870
stop_loss = 1.0850  # 20 pips below entry

# Place order
ticket = await sugar.buy_stop(price=stop_price)

# After order fills (becomes position), add SL
# Monitor and modify once position opens
```

**Tip 2: Use with daily high**
```python
# Breakout strategy: buy above yesterday's high
yesterday_high = 1.0865

# Place BUY STOP 5 pips above
stop_price = yesterday_high + 0.0005

ticket = await sugar.buy_stop(
    price=stop_price,
    volume=0.1,
    comment="Above yesterday high"
)
```

---

## 📚 See Also

- [sell_stop](sell_stop.md) - Place SELL STOP pending order
- [buy_limit](buy_limit.md) - Place BUY LIMIT pending order
- [buy_market](buy_market.md) - Open BUY position immediately
