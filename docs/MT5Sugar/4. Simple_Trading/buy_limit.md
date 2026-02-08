# Place BUY LIMIT Order (`buy_limit`)

> **Sugar method:** Places BUY LIMIT pending order to buy below current price.

**API Information:**

* **Method:** `sugar.buy_limit(symbol, volume, price, comment, magic)`
* **Returns:** Order ticket number (`int`)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def buy_limit(
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
| `price` | `float` | Yes | `0.0` | Limit price (must be BELOW current ASK) |
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

- Creates pending BUY LIMIT order
- Order triggers when ASK price falls to specified level
- Automatically converts to BUY position when triggered
- Order remains pending until triggered or cancelled

**Key behaviors:**

- BUY LIMIT price must be BELOW current ASK
- Order executes only at specified price or better
- Used to buy at lower price (buy the dip)
- Does not use slippage (limit order fills at exact price)

---

## ⚡ Under the Hood

```
MT5Sugar.buy_limit()
    ↓ builds OrderSendRequest
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar builds OrderSendRequest with TMT5_ORDER_TYPE_BUY_LIMIT
2. Sugar calls Service.place_order() with request
3. Service forwards to Account.order_send()
4. Account sends gRPC request to terminal
5. Sugar validates returned_code == 10009 (TRADE_RETCODE_DONE)
6. Returns order ticket from result.order
7. Order stays pending in terminal until price reached

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:658`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## When to Use

**Use `buy_limit()` when:**

- Want to buy at lower price (wait for pullback)
- Planning entry before price reaches level
- Avoid paying spread on immediate execution
- Implementing buy the dip strategy

**Don't use when:**

- Need immediate position (use `buy_market()`)
- Want to buy above current price (use `buy_stop()`)
- Price may never reach limit level (consider market order)

---

## 🔗 Examples

### Example 1: Basic Buy Limit Order

```python
from pymt5 import MT5Sugar

async def buy_the_dip():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Current ASK: 1.0850
    # Place BUY LIMIT at 1.0840 (below current price)
    ticket = await sugar.buy_limit(
        price=1.0840,
        volume=0.1,
        comment="Buy dip at 1.0840"
    )

    print(f"BUY LIMIT order placed: #{ticket}")

# Output:
# BUY LIMIT order placed: #123456791
```

### Example 2: Multiple Limit Orders (Grid Trading)

```python
async def buy_grid():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Current price: 1.0850
    # Place BUY LIMIT orders at multiple levels
    levels = [1.0840, 1.0830, 1.0820, 1.0810]

    tickets = []
    for price in levels:
        ticket = await sugar.buy_limit(
            price=price,
            volume=0.01,
            comment=f"Grid buy at {price}"
        )
        tickets.append(ticket)
        print(f"Order #{ticket} at {price}")

    print(f"Total orders placed: {len(tickets)}")
```

### Example 3: Conditional Limit Order

```python
async def smart_limit():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Get current price
    ask = await sugar.get_ask()

    # Place limit 20 pips below current price
    symbol_info = await sugar.get_symbol_info()
    point = symbol_info.point

    limit_price = ask - (20 * point * 10)  # 20 pips below

    # Ensure price is reasonable
    if limit_price > 0:
        ticket = await sugar.buy_limit(
            price=limit_price,
            volume=0.1,
            comment=f"Limit 20 pips below"
        )
        print(f"BUY LIMIT set at {limit_price}")
    else:
        print("Invalid limit price calculated")
```

---

## Common Pitfalls

**Pitfall 1: Price above current ASK**
```python
# ERROR: BUY LIMIT must be BELOW current price
# Current ASK: 1.0850
try:
    ticket = await sugar.buy_limit(price=1.0860)  # Above current price
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price for BUY LIMIT"
```

**Solution:** Ensure limit price is below current ASK
```python
ask = await sugar.get_ask()  # 1.0850
limit_price = ask - 0.0010   # 1.0840 (below current)
ticket = await sugar.buy_limit(price=limit_price)
```

**Pitfall 2: Wrong price format**
```python
# ERROR: Using pips instead of price
ticket = await sugar.buy_limit(price=20)  # WRONG: 20 is not a price
```

**Solution:** Use actual price, not pips
```python
# Get current price first
ask = await sugar.get_ask()  # 1.0850

# Calculate target price
target = ask - 0.0020  # 20 pips below for EURUSD

ticket = await sugar.buy_limit(price=target)  # 1.0830
```

---

## Pro Tips

**Tip 1: Use symbol digits for price precision**
```python
# Ensure price has correct decimal places
symbol_info = await sugar.get_symbol_info()
digits = symbol_info.digits

# Round limit price to symbol digits
ask = await sugar.get_ask()
limit_price = round(ask - 0.0020, digits)

ticket = await sugar.buy_limit(price=limit_price)
```

**Tip 2: Monitor pending orders**
```python
# Place limit order
ticket = await sugar.buy_limit(price=1.0840)

# Check if order is still pending or filled
orders = await sugar._service.get_opened_orders()

for order in orders.order_infos:
    if order.ticket == ticket:
        print(f"Order {ticket} still pending")
        break
else:
    print(f"Order {ticket} filled (became position)")
```

**Tip 3: Combine with Stop Loss**
```python
# Place limit order, then modify with SL once filled
ticket = await sugar.buy_limit(price=1.0840, volume=0.1)

# Wait for order to fill (becomes position)
# Then add stop loss
try:
    await sugar.modify_position_sltp(
        ticket=ticket,
        sl=1.0820  # 20 pips SL
    )
except ValueError:
    print("Order not yet filled")
```

---

## 📚 See Also

- [sell_limit](sell_limit.md) - Place SELL LIMIT pending order
- [buy_stop](buy_stop.md) - Place BUY STOP pending order
- [buy_market](buy_market.md) - Open BUY position immediately
- [buy_limit_with_sltp](../5.%20Trading_With_SLTP/buy_limit_with_sltp.md) - BUY LIMIT with SL/TP
