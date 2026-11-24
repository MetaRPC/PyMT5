# Get ASK Price (`get_ask`)

> **Sugar method:** Returns current ASK price for a symbol.

**API Information:**

* **Method:** `sugar.get_ask(symbol)`
* **Returns:** ASK price as `float`
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_ask(self, symbol: Optional[str] = None) -> float
```

---

## ℹ️ Input / Output

| Input | Type | Description |
|-------|------|-------------|
| `symbol` | `Optional[str]` | Trading symbol (e.g., "EURUSD"). Uses default_symbol if None |

| Output | Type | Description |
|--------|------|-------------|
| `ask` | `float` | Current ASK price |

---

## 🏛️ Essentials

* **What it is:** ASK price - the price at which you can BUY (open long / close short).
* **Why you need it:** Open long positions, close short positions, check execution price.
* **Remember:** ASK > BID always (you pay the spread)

---

## ⚡ Under the Hood

```
MT5Sugar.get_ask(symbol)
    ↓ calls
MT5Service.get_symbol_tick(symbol)
    ↓ calls
MT5Account.symbol_info_tick(symbol)
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoTick()
    ↓ MT5 Terminal
```

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:502`
- Service: `src/pymt5/mt5_service.py:680`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1095`

---

## When to Use

**Open long positions** - Buy at ASK price

**Close short positions** - Exit price for shorts

**Calculate entry cost** - ASK + spread

**Spread monitoring** - ASK - BID

**Order validation** - Verify favorable price

---

## 🔗 Usage Examples

### 1) Open long position at current ASK

```python
ask = await sugar.get_ask("EURUSD")
print(f"Opening long at ASK: {ask:.5f}")

ticket = await sugar.buy_market("EURUSD", 0.1)
# Position opens at ASK price
```

---

### 2) Calculate total entry cost with spread

```python
bid = await sugar.get_bid("EURUSD")
ask = await sugar.get_ask("EURUSD")
spread = ask - bid

print(f"BID:    {bid:.5f}")
print(f"ASK:    {ask:.5f}")
print(f"Spread: {spread:.5f}")
print(f"Cost:   ASK + spread = {ask:.5f}")
```

---

### 3) Wait for favorable ASK price

```python
max_ask = 1.09000

while True:
    ask = await sugar.get_ask("EURUSD")
    if ask <= max_ask:
        print(f"Good price! ASK: {ask:.5f}")
        ticket = await sugar.buy_market("EURUSD", 0.1)
        break
    await asyncio.sleep(1)
```

---

## Related Methods

**Price methods:**

* `get_bid()` - BID price (sell price)
* `get_spread()` - Spread in points
* `get_price_info()` - Complete price data
* `wait_for_price()` - Wait for price update

**Price relationships:**
```python
# ASK = price you BUY at
ask = await sugar.get_ask("EURUSD")

# BID = price you SELL at
bid = await sugar.get_bid("EURUSD")

# Always true:
assert ask > bid
```

---

## Common Pitfalls

### 1) Using ASK when you need BID

```python
# WRONG - using ASK to close long
ask = await sugar.get_ask("EURUSD")
# Long positions close at BID, not ASK!

# CORRECT - close longs at BID
bid = await sugar.get_bid("EURUSD")
ticket = await sugar.close_position(position_ticket)
```

### 2) Forgetting spread cost

```python
# WRONG - not accounting for spread
ask = await sugar.get_ask("EURUSD")
# To break even, price must move by spread amount!

# CORRECT - factor in spread
ask = await sugar.get_ask("EURUSD")
bid = await sugar.get_bid("EURUSD")
spread_pips = (ask - bid) * 10000
print(f"Need {spread_pips:.1f} pips just to break even")
```

---

## Pro Tips

1. **ASK for opening longs** - You buy at ASK price

2. **ASK for closing shorts** - Short exit at ASK

3. **Always higher than BID** - ASK = BID + spread

4. **Spread is your cost** - Must overcome spread to profit

5. **Use get_price_info()** - Get BID and ASK together

---

## 📚 See Also

- [get_bid](get_bid.md) - Get BID price
- [get_spread](get_spread.md) - Get bid-ask spread
- [get_price_info](get_price_info.md) - Get BID, ASK, and spread together
