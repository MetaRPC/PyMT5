# Place SELL LIMIT Order (`sell_limit`)

> **Sugar method:** Places SELL LIMIT pending order to sell above current price.

**API Information:**

* **Method:** `sugar.sell_limit(symbol, volume, price, comment, magic)`
* **Returns:** Order ticket number (`int`)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def sell_limit(
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
| `price` | `float` | Yes | `0.0` | Limit price (must be ABOVE current BID) |
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

- Creates pending SELL LIMIT order
- Order triggers when BID price rises to specified level
- Automatically converts to SELL position when triggered
- Order remains pending until triggered or cancelled

**Key behaviors:**

- SELL LIMIT price must be ABOVE current BID
- Order executes only at specified price or better
- Used to sell at higher price (sell the rally)
- Does not use slippage (limit order fills at exact price)

---

## ⚡ Under the Hood

```
MT5Sugar.sell_limit()
    ↓ builds OrderSendRequest
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar builds OrderSendRequest with TMT5_ORDER_TYPE_SELL_LIMIT
2. Sugar calls Service.place_order() with request
3. Service forwards to Account.order_send()
4. Account sends gRPC request to terminal
5. Sugar validates returned_code == 10009 (TRADE_RETCODE_DONE)
6. Returns order ticket from result.order
7. Order stays pending in terminal until price reached

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:698`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/helpers/mt5_account.py:1713`

---

## When to Use

**Use `sell_limit()` when:**

- Want to sell at higher price (wait for rally)
- Planning entry before price reaches level
- Expecting price to rise then fall (sell the top)
- Implementing sell the rally strategy

**Don't use when:**

- Need immediate position (use `sell_market()`)
- Want to sell below current price (use `sell_stop()`)
- Price may never reach limit level (consider market order)

---

## 🔗 Examples

### Example 1: Basic Sell Limit Order

```python
from pymt5 import MT5Sugar

async def sell_the_rally():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Current BID: 1.0850
    # Place SELL LIMIT at 1.0860 (above current price)
    ticket = await sugar.sell_limit(
        price=1.0860,
        volume=0.1,
        comment="Sell rally at 1.0860"
    )

    print(f"SELL LIMIT order placed: #{ticket}")

# Output:
# SELL LIMIT order placed: #123456792
```

### Example 2: Take Profit Targets

```python
async def profit_targets():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Open BUY position first
    buy_ticket = await sugar.buy_market(volume=0.3)
    print(f"BUY position: #{buy_ticket}")

    # Set SELL LIMIT orders as profit targets
    # Current price: 1.0850
    bid = await sugar.get_bid()

    targets = [
        (0.1, bid + 0.0030),  # Take profit 30 pips: 0.1 lot
        (0.1, bid + 0.0050),  # Take profit 50 pips: 0.1 lot
        (0.1, bid + 0.0100)   # Take profit 100 pips: 0.1 lot
    ]

    for volume, price in targets:
        ticket = await sugar.sell_limit(
            price=price,
            volume=volume,
            comment=f"TP at {price}"
        )
        print(f"Profit target #{ticket} at {price}")
```

### Example 3: Resistance Level Selling

```python
async def sell_at_resistance():
    sugar = MT5Sugar(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        default_symbol="EURUSD"
    )

    await sugar.connect()

    # Known resistance level
    resistance = 1.0900

    # Current price
    bid = await sugar.get_bid()

    # Only place order if below resistance
    if bid < resistance:
        ticket = await sugar.sell_limit(
            price=resistance,
            volume=0.1,
            comment="Sell at resistance"
        )
        print(f"SELL LIMIT at resistance {resistance}: #{ticket}")

        # Distance to resistance
        pips_away = (resistance - bid) / 0.0001
        print(f"Resistance is {pips_away:.1f} pips away")
    else:
        print("Already above resistance level")
```

---

## Common Pitfalls

**Pitfall 1: Price below current BID**
```python
# ERROR: SELL LIMIT must be ABOVE current price
# Current BID: 1.0850
try:
    ticket = await sugar.sell_limit(price=1.0840)  # Below current price
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price for SELL LIMIT"
```

**Solution:** Ensure limit price is above current BID
```python
bid = await sugar.get_bid()  # 1.0850
limit_price = bid + 0.0010   # 1.0860 (above current)
ticket = await sugar.sell_limit(price=limit_price)
```

**Pitfall 2: Confusing with BUY close**
```python
# WRONG: Thinking SELL LIMIT will close a BUY position
buy_ticket = await sugar.buy_market()

# This does NOT close the BUY position
# It creates a NEW pending SELL LIMIT order
sell_ticket = await sugar.sell_limit(price=1.0870)

# To close BUY position, use:
await sugar.close_position(buy_ticket)
```

**Pitfall 3: Too far from current price**
```python
# Order may never fill if price too far away
bid = await sugar.get_bid()  # 1.0850

# Placing 500 pips above (may never reach)
ticket = await sugar.sell_limit(price=bid + 0.0500)  # 1.1350
# Order sits pending indefinitely
```

**Solution:** Use realistic price targets
```python
bid = await sugar.get_bid()

# Reasonable target: 20-50 pips above
realistic_target = bid + 0.0030  # 30 pips
ticket = await sugar.sell_limit(price=realistic_target)
```

---

## Pro Tips

**Tip 1: Grid selling strategy**
```python
# Place multiple SELL LIMIT orders above current price
bid = await sugar.get_bid()

# Create grid every 10 pips
for i in range(1, 6):
    price = bid + (i * 0.0010)  # +10, +20, +30, +40, +50 pips
    ticket = await sugar.sell_limit(
        price=price,
        volume=0.01,
        comment=f"Grid sell {i}"
    )
    print(f"Grid level {i}: {price}")
```

**Tip 2: Combine with support/resistance**
```python
# Technical analysis: place order at resistance
resistance_levels = [1.0900, 1.0950, 1.1000]

bid = await sugar.get_bid()

# Place SELL LIMIT at nearest resistance above
for level in resistance_levels:
    if level > bid:
        ticket = await sugar.sell_limit(
            price=level,
            volume=0.1,
            comment=f"Resistance at {level}"
        )
        print(f"Order placed at resistance: {level}")
        break
```

---

## 📚 See Also

- [buy_limit](buy_limit.md) - Place BUY LIMIT pending order
- [sell_stop](sell_stop.md) - Place SELL STOP pending order
- [sell_market](sell_market.md) - Open SELL position immediately
- [sell_limit_with_sltp](../5.%20Trading_With_SLTP/sell_limit_with_sltp.md) - SELL LIMIT with SL/TP
