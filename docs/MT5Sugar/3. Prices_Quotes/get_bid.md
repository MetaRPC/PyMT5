# Get BID Price (`get_bid`)

> **Sugar method:** Returns current BID price for a symbol.

**API Information:**

* **Method:** `sugar.get_bid(symbol)`
* **Returns:** BID price as `float`
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_bid(self, symbol: Optional[str] = None) -> float
```

---

## ℹ️ Input / Output

| Input | Type | Description |
|-------|------|-------------|
| `symbol` | `Optional[str]` | Trading symbol (e.g., "EURUSD"). Uses default_symbol if None |

| Output | Type | Description |
|--------|------|-------------|
| `bid` | `float` | Current BID price |

---

## 🏛️ Essentials

* **What it is:** BID price - the price at which you can SELL (close long / open short).
* **Why you need it:** Check current market price, calculate entry/exit points.
* **Remember:** BID < ASK always (spread = ASK - BID)

---

## ⚡ Under the Hood

```
MT5Sugar.get_bid(symbol)
    ↓ calls
MT5Service.get_symbol_tick(symbol)
    ↓ calls
MT5Account.symbol_info_tick(symbol)
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoTick()
    ↓ MT5 Terminal
```

**What happens:**

1. **Sugar Layer:** Validates symbol, extracts bid field from tick
2. **Service Layer:** Returns SymbolTick dataclass
3. **Account Layer:** gRPC call to get last tick
4. **Result:** Current BID price

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:488`
- Service: `src/pymt5/mt5_service.py:680`
- Account: `package/helpers/mt5_account.py:1095`

---

## When to Use

**Close long positions** - Sell at BID price

**Open short positions** - Entry price for shorts

**Price monitoring** - Track current market price

**Spread calculation** - Compare BID vs ASK

**Order validation** - Check if price is favorable

---

## 🔗 Usage Examples

### 1) Get current BID price

```python
bid = await sugar.get_bid("EURUSD")
print(f"EURUSD BID: {bid:.5f}")
# Output: EURUSD BID: 1.08530
```

---

### 2) Check if price is favorable before closing long

```python
# You have a long position at 1.08000
entry_price = 1.08000
target_profit = 50  # pips

bid = await sugar.get_bid("EURUSD")
profit_pips = (bid - entry_price) * 10000

if profit_pips >= target_profit:
    print(f"Target reached! Profit: {profit_pips:.1f} pips")
    ticket = await sugar.close_position(position_ticket)
else:
    print(f"Waiting... Current profit: {profit_pips:.1f} pips")
```

---

### 3) Calculate spread

```python
bid = await sugar.get_bid("EURUSD")
ask = await sugar.get_ask("EURUSD")
spread = (ask - bid) * 10000  # Convert to pips

print(f"BID:    {bid:.5f}")
print(f"ASK:    {ask:.5f}")
print(f"Spread: {spread:.1f} pips")
```

---

## Related Methods

**Price methods:**

* `get_ask()` - ASK price (buy price)
* `get_spread()` - Spread in points
* `get_price_info()` - Complete price data (BID, ASK, spread, time)
* `wait_for_price()` - Wait for price update

**BID vs ASK:**

```python
# BID = price you SELL at (close long, open short)
bid = await sugar.get_bid("EURUSD")

# ASK = price you BUY at (open long, close short)
ask = await sugar.get_ask("EURUSD")

# Spread = broker's commission
spread = ask - bid
```

---

## Common Pitfalls

### 1) Using BID when you need ASK

```python
# WRONG - using BID to open long position
bid = await sugar.get_bid("EURUSD")
# Long positions open at ASK, not BID!

# CORRECT - use ASK for opening longs
ask = await sugar.get_ask("EURUSD")
ticket = await sugar.buy_market("EURUSD", 0.1)
```

### 2) Not specifying symbol

```python
# WRONG - no default symbol set
sugar = MT5Sugar(service)  # No default_symbol
bid = await sugar.get_bid()  # ValueError!

# CORRECT - specify symbol or set default
sugar = MT5Sugar(service, default_symbol="EURUSD")
bid = await sugar.get_bid()  # Works
# OR
bid = await sugar.get_bid("EURUSD")  # Always works
```

---

## Pro Tips

1. **BID for closing longs** - You sell at BID price

2. **BID for opening shorts** - Short entry at BID

3. **Always lower than ASK** - BID + spread = ASK

4. **Use get_price_info()** - Get BID, ASK, spread at once

5. **Updates in real-time** - Price changes every tick

---

## 📚 See Also

- [get_ask](get_ask.md) - Get ASK price
- [get_spread](get_spread.md) - Get bid-ask spread
- [get_price_info](get_price_info.md) - Get BID, ASK, and spread together
