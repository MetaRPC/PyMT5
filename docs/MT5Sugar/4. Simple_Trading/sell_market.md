# Open SELL Position at Market (`sell_market`)

> **Sugar method:** Opens SELL position at current market price in one call.

**API Information:**

* **Method:** `sugar.sell_market(symbol, volume, comment, magic)`
* **Returns:** Position ticket number (`int`)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def sell_market(
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

- Fetches current BID price from terminal
- Creates SELL market order request
- Executes order with 10 points slippage tolerance
- Returns ticket number on success

**Key behaviors:**

- SELL = profit when price FALLS
- Uses BID price (lower price)
- Default slippage: 10 points
- Raises exception if order fails
- Position opens immediately at market

---

## ⚡ Under the Hood

```
MT5Sugar.sell_market()
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
2. Sugar builds OrderSendRequest with TMT5_ORDER_TYPE_SELL
3. Sugar calls Service.place_order() with request
4. Service forwards to Account.order_send()
5. Account sends gRPC request to terminal
6. Sugar validates returned_code == 10009 (TRADE_RETCODE_DONE)
7. Returns ticket number from result.order

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:613`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/helpers/mt5_account.py:1713`

---

## When to Use

**Use `sell_market()` when:**

- You expect price to go DOWN
- Need immediate position execution
- Don't need Stop Loss or Take Profit (simple entry)
- Building basic trading strategies

**Don't use when:**

- Need SL/TP on entry (use `sell_market_with_sltp()`)
- Want to enter at specific price (use `sell_limit()` or `sell_stop()`)
- Market is closed or illiquid
- Price is moving too fast (consider pending orders)

---

## 🔗 Examples

### Example 1: Basic SELL Position

```python
from pymt5 import MT5Sugar

async def simple_sell():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open SELL position with default volume (0.01 lot)
    ticket = await sugar.sell_market()
    print(f"Position opened: #{ticket}")

# Output:
# Position opened: #123456790
```

### Example 2: SELL with Custom Parameters

```python
async def sell_with_params():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await sugar.connect()

    # Open 0.1 lot SELL position on GBPUSD
    ticket = await sugar.sell_market(
        symbol="GBPUSD",
        volume=0.1,
        comment="Bear trend entry",
        magic=12345
    )

    print(f"GBPUSD SELL: ticket #{ticket}")
```

### Example 3: Hedging Strategy (BUY + SELL)

```python
async def hedging_positions():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    try:
        # Open opposite positions to hedge
        buy_ticket = await sugar.buy_market(volume=0.1, magic=1000)
        sell_ticket = await sugar.sell_market(volume=0.1, magic=1000)

        print(f"Hedge opened: BUY #{buy_ticket}, SELL #{sell_ticket}")

        # Monitor and close profitable side later
        balance = await sugar.get_balance()
        print(f"Balance: ${balance}")

    except RuntimeError as e:
        print(f"Hedging failed: {e}")
```

---

## Common Pitfalls

**Pitfall 1: Confusing BUY and SELL**
```python
# WRONG: Thinking SELL means "sell to close" a position
# SELL opens NEW position that profits from price falling
ticket = await sugar.sell_market()  # Opens new SELL position

# To close position, use close_position() instead
await sugar.close_position(ticket)
```

**Solution:** Remember SELL = open short position
```python
# Open short (SELL) position
sell_ticket = await sugar.sell_market()  # Profit if price drops

# Close that position
await sugar.close_position(sell_ticket)
```

**Pitfall 2: Using ASK instead of BID mentally**
```python
# SELL uses BID price (lower)
# If current prices: BID=1.08430, ASK=1.08445
# SELL opens at 1.08430 (BID)
# Profit if price falls below 1.08430
```

**Solution:** Remember: SELL uses BID, BUY uses ASK
```python
bid = await sugar.get_bid()    # 1.08430
ask = await sugar.get_ask()    # 1.08445

# SELL opens at BID
sell_ticket = await sugar.sell_market()  # Opens at 1.08430
```

**Pitfall 3: Wrong expectations about profit direction**
```python
# WRONG: Expecting profit when price rises
ticket = await sugar.sell_market()
# Price goes from 1.0843 → 1.0850
# Result: LOSS (not profit)

# CORRECT: Profit when price falls
ticket = await sugar.sell_market()
# Price goes from 1.0843 → 1.0835
# Result: PROFIT
```

---

## Pro Tips

**Tip 1: Check trend before SELL**
```python
# Simple moving average crossover for trend
current_price = await sugar.get_bid()

# SELL when price is below moving average (downtrend)
if current_price < moving_average:
    ticket = await sugar.sell_market()
```

**Tip 2: Combine with position monitoring**
```python
# Open SELL and monitor profit
ticket = await sugar.sell_market(volume=0.1)

# Subscribe to position profit updates
async for profit in sugar.stream_position_profit(ticket):
    print(f"Current profit: ${profit}")

    # Close if profit target reached
    if profit >= 50.0:
        await sugar.close_position(ticket)
        break
```

**Tip 3: Use spread check before SELL**
```python
# Ensure tight spread before selling
spread = await sugar.get_spread()

if spread < 0.0002:  # 2 pips for EURUSD
    ticket = await sugar.sell_market()
else:
    print(f"Spread too wide for SELL: {spread}")
```

---

## 📚 See Also

- [buy_market](buy_market.md) - Open BUY position at market
- [sell_limit](sell_limit.md) - Place SELL LIMIT pending order
- [sell_stop](sell_stop.md) - Place SELL STOP pending order
- [sell_market_with_sltp](../5.%20Trading_With_SLTP/sell_market_with_sltp.md) - Open SELL with SL/TP
- [close_position](../6.%20Position_Management/close_position.md) - Close position by ticket
