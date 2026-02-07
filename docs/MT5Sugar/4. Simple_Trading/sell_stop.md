# Place SELL STOP Order (`sell_stop`)

> **Sugar method:** Places SELL STOP pending order to sell below current price (breakdown entry).

**API Information:**

* **Method:** `sugar.sell_stop(symbol, volume, price, comment, magic)`
* **Returns:** Order ticket number (`int`)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def sell_stop(
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
| `price` | `float` | Yes | `0.0` | Stop price (must be BELOW current BID) |
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

- Creates pending SELL STOP order
- Order triggers when BID price falls to specified level
- Automatically converts to SELL position when triggered
- Order remains pending until triggered or cancelled

**Key behaviors:**

- SELL STOP price must be BELOW current BID
- Used for breakdown trading (sell when price breaks support)
- Executes at market once stop price reached (not at exact price)
- Useful for trend following and support breakdown strategies

---

## ⚡ Under the Hood

```
MT5Sugar.sell_stop()
    ↓ builds OrderSendRequest
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar builds OrderSendRequest with TMT5_ORDER_TYPE_SELL_STOP
2. Sugar calls Service.place_order() with request
3. Service forwards to Account.order_send()
4. Account sends gRPC request to terminal
5. Sugar validates returned_code == 10009 (TRADE_RETCODE_DONE)
6. Returns order ticket from result.order
7. Order stays pending until price reaches stop level

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:778`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/helpers/mt5_account.py:1713`

---

## When to Use

**Use `sell_stop()` when:**

- Trading breakdowns below support
- Following downward trend (sell momentum)
- Want to enter only if price confirms direction
- Implementing breakdown strategies

**Don't use when:**

- Need immediate position (use `sell_market()`)
- Want to sell at higher price (use `sell_limit()`)
- Price may reverse before reaching stop
- In ranging market (false breakdowns)

---

## 🔗 Examples

### Example 1: Basic Breakdown Entry

```python
from pymt5 import MT5Sugar

async def breakdown_sell():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Current BID: 1.0850
    # Support at 1.0830
    # Place SELL STOP below support
    ticket = await sugar.sell_stop(
        price=1.0825,
        volume=0.1,
        comment="Breakdown sell at 1.0825"
    )

    print(f"SELL STOP order placed: #{ticket}")

# Output:
# SELL STOP order placed: #123456794
```

### Example 2: Multiple Support Levels

```python
async def tiered_breakdown():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Current price: 1.0850
    # Key support levels
    supports = [1.0830, 1.0800, 1.0770]

    tickets = []
    for support in supports:
        # Place SELL STOP slightly below each support
        stop_price = support - 0.0005  # 5 pips below

        ticket = await sugar.sell_stop(
            price=stop_price,
            volume=0.01,
            comment=f"Breakdown {support}"
        )
        tickets.append(ticket)
        print(f"SELL STOP at {stop_price}: #{ticket}")

    print(f"Total breakdown orders: {len(tickets)}")
```

### Example 3: Trend Following with SELL STOP

```python
async def downtrend_following():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Get current low
    bid = await sugar.get_bid()

    # Place SELL STOP 20 pips below current price
    # (enters only if downtrend continues)
    symbol_info = await sugar.get_symbol_info()
    point = symbol_info.point

    stop_price = bid - (20 * point * 10)  # 20 pips below

    ticket = await sugar.sell_stop(
        price=stop_price,
        volume=0.1,
        comment="Downtrend confirmation"
    )

    print(f"SELL STOP at {stop_price} (confirms downtrend)")
    print(f"Order: #{ticket}")
```

---

## Common Pitfalls

**Pitfall 1: Price above current BID**
```python
# ERROR: SELL STOP must be BELOW current price
# Current BID: 1.0850
try:
    ticket = await sugar.sell_stop(price=1.0860)  # Above current price
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price for SELL STOP"
```

**Solution:** Ensure stop price is below current BID
```python
bid = await sugar.get_bid()  # 1.0850
stop_price = bid - 0.0020    # 1.0830 (below current)
ticket = await sugar.sell_stop(price=stop_price)
```

**Pitfall 2: Confusing SELL STOP with SELL LIMIT**
```python
# SELL LIMIT: Sell ABOVE current price (better price)
# SELL STOP: Sell BELOW current price (breakdown)

# Current price: 1.0850

# LIMIT: Sell if price rises to 1.0870
sell_limit = await sugar.sell_limit(price=1.0870)

# STOP: Sell if price falls to 1.0830
sell_stop = await sugar.sell_stop(price=1.0830)
```

**Pitfall 3: False breakdowns**
```python
# Price touches stop level then reverses
# Order gets triggered at 1.0830, then price rises to 1.0850
# Result: Immediate loss

# Stop order placed at 1.0830
ticket = await sugar.sell_stop(price=1.0830)
# Price spikes to 1.0829 (triggers order)
# Price rises back to 1.0850 (loss)
```

**Solution:** Place stop beyond significant level with buffer
```python
# Add buffer beyond support
support = 1.0830
buffer = 0.0005  # 5 pips buffer

stop_price = support - buffer  # 1.0825
ticket = await sugar.sell_stop(price=stop_price)
```

---

## Pro Tips

**Tip 1: Use with daily low**
```python
# Breakdown strategy: sell below yesterday's low
yesterday_low = 1.0835

# Place SELL STOP 5 pips below
stop_price = yesterday_low - 0.0005

ticket = await sugar.sell_stop(
    price=stop_price,
    volume=0.1,
    comment="Below yesterday low"
)
```

**Tip 2: Combine with multiple timeframes**
```python
# Place SELL STOP below support on multiple timeframes
h4_support = 1.0830
h1_support = 1.0840
m15_support = 1.0845

# Use the strongest (lowest) support
main_support = min(h4_support, h1_support, m15_support)

# Place below strongest support
stop_price = main_support - 0.0005

ticket = await sugar.sell_stop(
    price=stop_price,
    comment="Multi-timeframe breakdown"
)
```

---

## 📚 See Also

- [buy_stop](buy_stop.md) - Place BUY STOP pending order
- [sell_limit](sell_limit.md) - Place SELL LIMIT pending order
- [sell_market](sell_market.md) - Open SELL position immediately

