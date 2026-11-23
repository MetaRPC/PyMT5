# Get Margin Level (`get_margin_level`)

> **Sugar method:** Returns margin level percentage (Equity/Margin × 100) in one line.

**API Information:**

* **Method:** `sugar.get_margin_level()`
* **Returns:** Margin level as `float` (percentage)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_margin_level(self) -> float
```

---

## ℹ️ Input / Output

| Input | Type | Description |
|-------|------|-------------|
| *None* | - | No parameters required |

| Output | Type | Description |
|--------|------|-------------|
| `margin_level` | `float` | Margin level percentage |

---

## 🏛️ Essentials

* **What it is:** Ratio of equity to used margin expressed as percentage.
* **Why you need it:** Monitor account health and avoid margin calls.
* **Formula:** Margin Level = (Equity / Used Margin) × 100

---

## ⚡ Under the Hood

```
MT5Sugar.get_margin_level()
    ↓ calls
MT5Service.get_account_double(ACCOUNT_MARGIN_LEVEL)
    ↓ calls
MT5Account.account_info_double(property_id=ACCOUNT_MARGIN_LEVEL)
    ↓ gRPC protobuf
AccountInformationService.AccountInfoDouble(property_id=12)
    ↓ MT5 Terminal
```

**What happens:**

1. **Sugar Layer:** Calls service with ACCOUNT_MARGIN_LEVEL constant
2. **Service Layer:** Requests margin level property
3. **Account Layer:** gRPC call to terminal
4. **Result:** Pre-calculated margin level from MT5

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:428`
- Service: `src/pymt5/mt5_service.py:298`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:578`

---

## When to Use

**Risk monitoring** - Check account safety continuously

**Stop-out prevention** - Avoid forced position closure

**Position management** - Decide when to close or reduce positions

**Trading limits** - Set minimum margin level thresholds

**Automated systems** - Trigger alerts or actions based on level

---

## 🔗 Usage Examples

### 1) Basic margin level check

```python
margin_level = await sugar.get_margin_level()
print(f"Margin Level: {margin_level:.2f}%")

if margin_level < 200:
    print("WARNING: Low margin level")
# Output: Margin Level: 450.00%
```

---

### 2) Risk-based position management

```python
margin_level = await sugar.get_margin_level()

if margin_level < 100:
    print("CRITICAL: Stop-out imminent!")
    # Close losing positions
    await sugar.close_all_positions()
elif margin_level < 200:
    print("WARNING: Reduce exposure")
    # Close 50% of positions
elif margin_level > 500:
    print("Safe to trade")
```

---

### 3) Complete margin dashboard

```python
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = await sugar.get_free_margin()
margin_level = await sugar.get_margin_level()

print("=" * 40)
print("MARGIN HEALTH DASHBOARD")
print("=" * 40)
print(f"Equity:        ${equity:>10,.2f}")
print(f"Used Margin:   ${margin:>10,.2f}")
print(f"Free Margin:   ${free_margin:>10,.2f}")
print(f"Margin Level:  {margin_level:>9.2f}%")
print("=" * 40)

if margin_level < 100:
    status = "DANGER"
elif margin_level < 200:
    status = "WARNING"
else:
    status = "HEALTHY"

print(f"Status: {status}")
```

---

## Related Methods

**Margin analysis methods:**

* `get_equity()` - Total account value
* `get_margin()` - Used margin
* `get_free_margin()` - Available margin
* `get_balance()` - Account balance
* `get_account_info()` - All account data at once

**Understanding margin levels:**
```python
# Manual calculation
equity = await sugar.get_equity()
margin = await sugar.get_margin()
manual_level = (equity / margin * 100) if margin > 0 else 0

# Or get directly from MT5
margin_level = await sugar.get_margin_level()

# Both should match
```

---

## Common Pitfalls

### 1) Not understanding margin level thresholds

```python
# WRONG - not knowing broker limits
margin_level = await sugar.get_margin_level()
if margin_level < 50:
    print("Need to close positions")  # Too late!

# CORRECT - act early
if margin_level < 200:
    print("Reduce exposure now")
elif margin_level < 100:
    print("CRITICAL: Close positions immediately")
```

### 2) Ignoring zero margin case

```python
# WRONG - division by zero when no positions
equity = await sugar.get_equity()
margin = await sugar.get_margin()
level = equity / margin * 100  # Error if margin = 0!

# CORRECT - use get_margin_level() or check first
margin_level = await sugar.get_margin_level()
# Or manual with check:
level = (equity / margin * 100) if margin > 0 else 0
```

---

## Pro Tips

1. **Broker thresholds** - Typical stop-out levels: 20-50%, margin call: 80-100%

2. **Monitor continuously** - In live trading, check every few minutes

3. **Set alerts** - Trigger warnings at 200%, 150%, 100%

4. **Act early** - Don't wait for margin call - reduce positions at 200%

5. **Zero = No positions** - Margin level is 0 when you have no open positions

---

## 📚 See Also

- [get_margin](get_margin.md) - Get used margin
- [get_free_margin](get_free_margin.md) - Get available margin for trading
- [get_equity](get_equity.md) - Get equity (balance + floating P/L)
