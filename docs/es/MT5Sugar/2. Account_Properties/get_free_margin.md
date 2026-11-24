# Get Free Margin (`get_free_margin`)

> **Sugar method:** Returns available margin for new positions in one line.

**API Information:**

* **Method:** `sugar.get_free_margin()`
* **Returns:** Free margin as `float`
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_free_margin(self) -> float
```

---

## ℹ️ Input / Output

| Input | Type | Description |
|-------|------|-------------|
| *None* | - | No parameters required |

| Output | Type | Description |
|--------|------|-------------|
| `free_margin` | `float` | Available margin for trading |

---

## 🏛️ Essentials

* **What it is:** Equity minus used margin - the funds available for opening new positions.
* **Why you need it:** Verify you have enough margin before opening trades.
* **Formula:** Free Margin = Equity - Used Margin

---

## ⚡ Under the Hood

```
MT5Sugar.get_free_margin()
    ↓ calls
MT5Service.get_account_double(ACCOUNT_MARGIN_FREE)
    ↓ calls
MT5Account.account_info_double(property_id=ACCOUNT_MARGIN_FREE)
    ↓ gRPC protobuf
AccountInformationService.AccountInfoDouble(property_id=11)
    ↓ MT5 Terminal
```

**What happens:**

1. **Sugar Layer:** Calls service with ACCOUNT_MARGIN_FREE constant
2. **Service Layer:** Requests specific property from account
3. **Account Layer:** gRPC call with property enum
4. **Result:** Available margin calculated by MT5

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:417`
- Service: `src/pymt5/mt5_service.py:298`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:578`

---

## When to Use

**Before trading** - Always check before opening new positions

**Position sizing** - Calculate maximum safe volume

**Risk management** - Ensure sufficient margin buffer

**Multiple orders** - Verify margin for planned trades

**Prevent failures** - Avoid "not enough money" errors

---

## 🔗 Usage Examples

### 1) Check before opening position

```python
free_margin = await sugar.get_free_margin()

if free_margin < 100:
    print("Insufficient margin to trade")
    return

# Safe to proceed
ticket = await sugar.buy_market("EURUSD", 0.1)
```

---

### 2) Calculate maximum position size

```python
free_margin = await sugar.get_free_margin()
# Assume 1 lot requires ~1000 margin
max_lots = free_margin / 1000

print(f"Free Margin:  ${free_margin:.2f}")
print(f"Max Lots:     {max_lots:.2f}")

# Better: use calculate_position_size()
lot_size = await sugar.calculate_position_size("EURUSD", 2.0, 50)
```

---

### 3) Monitor margin health

```python
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = await sugar.get_free_margin()

margin_level = (equity / margin * 100) if margin > 0 else 0

print(f"Equity:       ${equity:.2f}")
print(f"Used Margin:  ${margin:.2f}")
print(f"Free Margin:  ${free_margin:.2f}")
print(f"Margin Level: {margin_level:.0f}%")

if free_margin < 500:
    print("WARNING: Low free margin!")
```

---

## Related Methods

**Margin-related methods:**

* `get_margin()` - Currently used margin
* `get_equity()` - Total account value
* `get_margin_level()` - Margin level percentage
* `calculate_required_margin()` - Calculate margin for planned trade
* `can_open_position()` - Validate if trade is possible

**Margin check pattern:**
```python
# Manual check
free_margin = await sugar.get_free_margin()
required_margin = await sugar.calculate_required_margin("EURUSD", 1.0)

if free_margin >= required_margin:
    # Safe to trade
    pass

# Or use helper
can_trade = await sugar.can_open_position("EURUSD", 1.0)
```

---

## Common Pitfalls

### 1) Not checking margin before trading

```python
# WRONG - trading without margin check
ticket = await sugar.buy_market("EURUSD", 1.0)  # Might fail!

# CORRECT - verify free margin first
free_margin = await sugar.get_free_margin()
if free_margin >= 1000:  # Rough estimate
    ticket = await sugar.buy_market("EURUSD", 1.0)
```

### 2) Using outdated margin value

```python
# WRONG - checking once and reusing
free_margin = await sugar.get_free_margin()
# ... later ...
ticket = await sugar.buy_market("EURUSD", 0.1)  # Margin might have changed!

# CORRECT - check before each trade
free_margin = await sugar.get_free_margin()
if free_margin >= 100:
    ticket = await sugar.buy_market("EURUSD", 0.1)
```

---

## Pro Tips

1. **Always check** - Never trade without verifying free margin

2. **Use calculate_required_margin()** - More accurate than rough estimates

3. **Keep buffer** - Don't use 100% of free margin (keep 20-30% safety)

4. **Margin changes** - Free margin updates with every price tick

5. **Use can_open_position()** - Combines margin check with other validations

---

## 📚 See Also

- [get_margin](get_margin.md) - Get used margin
- [get_margin_level](get_margin_level.md) - Get margin level percentage
- [calculate_required_margin](../10.%20Risk_Management/calculate_required_margin.md) - Calculate required margin for a trade
