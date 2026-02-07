# Get Spread (`get_spread`)

> **Sugar method:** Returns current spread (ASK - BID) in price units.

**API Information:**

* **Method:** `sugar.get_spread(symbol)`
* **Returns:** Spread as `float` (in price units, not pips)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_spread(self, symbol: Optional[str] = None) -> float
```

---

## ℹ️ Input / Output

| Input | Type | Description |
|-------|------|-------------|
| `symbol` | `Optional[str]` | Trading symbol (e.g., "EURUSD"). Uses default_symbol if None |

| Output | Type | Description |
|--------|------|-------------|
| `spread` | `float` | Current spread (ASK - BID) in price units |

---

## 🏛️ Essentials

* **What it is:** Spread = ASK - BID, the broker's fee per trade.
* **Why you need it:** Assess trading costs, choose low-spread times.
* **Formula:** Spread (pips) = (ASK - BID) × 10000 (for EURUSD)

---

## ⚡ Under the Hood

```
MT5Sugar.get_spread(symbol)
    ↓ calls
MT5Service.get_symbol_tick(symbol)
    ↓ calls
MT5Account.symbol_info_tick(symbol)
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoTick()
    ↓ MT5 Terminal
```

**Calculation:** Sugar layer calculates `tick.ask - tick.bid`

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:516`
- Service: `src/pymt5/mt5_service.py:680`
- Account: `package/helpers/mt5_account.py:1095`

---

## When to Use

**Cost analysis** - Understand trading fees

**Timing trades** - Choose low-spread periods

**Broker comparison** - Compare execution costs

**Scalping** - Critical for short-term strategies

**Risk calculation** - Factor spread into P/L

---

## 🔗 Usage Examples

### 1) Check current spread

```python
spread = await sugar.get_spread("EURUSD")
spread_pips = spread * 10000  # Convert to pips

print(f"EURUSD Spread: {spread:.5f}")
print(f"Spread (pips): {spread_pips:.1f}")
# Output: Spread (pips): 1.2
```

---

### 2) Wait for low spread before trading

```python
max_spread_pips = 2.0

spread = await sugar.get_spread("EURUSD")
spread_pips = spread * 10000

if spread_pips <= max_spread_pips:
    print(f"Good spread: {spread_pips:.1f} pips")
    ticket = await sugar.buy_market("EURUSD", 0.1)
else:
    print(f"Spread too high: {spread_pips:.1f} pips - waiting")
```

---

### 3) Calculate break-even price

```python
ask = await sugar.get_ask("EURUSD")
spread = await sugar.get_spread("EURUSD")

# After buying at ASK, price must rise by spread to break even
breakeven = ask + spread

print(f"Entry (ASK):  {ask:.5f}")
print(f"Spread:       {spread:.5f}")
print(f"Break-even:   {breakeven:.5f}")
print(f"Must move:    {spread * 10000:.1f} pips to profit")
```

---

## Related Methods

**Price methods:**

* `get_bid()` - BID price
* `get_ask()` - ASK price
* `get_price_info()` - Complete price data including spread
* `get_symbol_info()` - Symbol parameters including typical spread

**Manual calculation:**

```python
# Method returns this automatically:
bid = await sugar.get_bid("EURUSD")
ask = await sugar.get_ask("EURUSD")
spread = ask - bid

# Or use get_spread() directly:
spread = await sugar.get_spread("EURUSD")
```

---

## Common Pitfalls

### 1) Confusing price units with pips

```python
# WRONG - spread is in price units, not pips
spread = await sugar.get_spread("EURUSD")
print(f"Spread: {spread} pips")  # Wrong! Shows 0.00012, not 1.2

# CORRECT - convert to pips
spread = await sugar.get_spread("EURUSD")
spread_pips = spread * 10000
print(f"Spread: {spread_pips:.1f} pips")
```

### 2) Not accounting for spread in profit calculations

```python
# WRONG - ignoring spread
entry = await sugar.get_ask("EURUSD")
current = await sugar.get_bid("EURUSD")
profit_pips = (current - entry) * 10000  # Doesn't account for spread!

# CORRECT - spread already factored in
# When you buy at ASK and sell at BID, spread is automatic cost
entry_ask = await sugar.get_ask("EURUSD")
current_bid = await sugar.get_bid("EURUSD")
profit_pips = (current_bid - entry_ask) * 10000  # Includes spread cost
```

---

## Pro Tips

1. **Varies by time** - Spread increases during low liquidity (news, market open/close)

2. **Lower is better** - Typical EURUSD spread: 0.5-2 pips

3. **Hidden cost** - Spread is paid on every trade, both entry and exit

4. **Scalping killer** - High spread makes short-term trading unprofitable

5. **Use get_price_info()** - Get BID, ASK, and spread in one call

---

## 📚 See Also

- [get_bid](get_bid.md) - Get BID price
- [get_ask](get_ask.md) - Get ASK price
- [get_price_info](get_price_info.md) - Get BID, ASK, and spread together
