# Get Used Margin (`get_margin`)

> **Sugar method:** Returns currently used margin (locked funds) in one line.

**API Information:**

* **Method:** `sugar.get_margin()`
* **Returns:** Used margin as `float`
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_margin(self) -> float
```

---

## ℹ️ Input / Output

| Input | Type | Description |
|-------|------|-------------|
| *None* | - | No parameters required |

| Output | Type | Description |
|--------|------|-------------|
| `margin` | `float` | Currently used margin |

---

## 🏛️ Essentials

* **What it is:** Sum of margin locked by all your open positions.
* **Why you need it:** Check available margin before opening new trades, calculate margin level.
* **Formula:** Total margin required to maintain current open positions.

---

## ⚡ Under the Hood

```
MT5Sugar.get_margin()
    ↓ calls
MT5Service.get_account_double(ACCOUNT_MARGIN)
    ↓ calls
MT5Account.account_info_double(property_id=ACCOUNT_MARGIN)
    ↓ gRPC protobuf
AccountInformationService.AccountInfoDouble(property_id=10)
    ↓ MT5 Terminal
```

**What happens:**

1. **Sugar Layer:** Calls service with ACCOUNT_MARGIN constant
2. **Service Layer:** Calls account with property_id for margin
3. **Account Layer:** gRPC call with specific property enum
4. **Result:** Used margin as float

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:406`
- Service: `src/pymt5/mt5_service.py:298`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:578`

---

## When to Use

**Before trading** - Check if you have free margin for new positions

**Risk management** - Monitor margin usage vs account size

**Margin level calculation** - Calculate (Equity / Margin) * 100

**Position sizing** - Ensure you don't exceed margin limits

**Multiple positions** - Track total margin commitment

---

## 🔗 Usage Examples

### 1) Basic usage

```python
margin = await sugar.get_margin()
print(f"Used Margin: ${margin:.2f}")
# Output: Used Margin: $500.00
```

---

### 2) Check available margin before trading

```python
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = equity - margin

print(f"Equity:        ${equity:.2f}")
print(f"Used Margin:   ${margin:.2f}")
print(f"Free Margin:   ${free_margin:.2f}")

if free_margin < 100:
    print("Not enough free margin to trade")
```

---

### 3) Calculate margin level

```python
equity = await sugar.get_equity()
margin = await sugar.get_margin()

if margin > 0:
    margin_level = (equity / margin) * 100
    print(f"Margin Level: {margin_level:.2f}%")

    if margin_level < 200:
        print("WARNING: Low margin level")
    elif margin_level < 100:
        print("DANGER: Stop-out risk!")
else:
    print("No open positions")
```

---

## Related Methods

**Margin-related methods:**

* `get_free_margin()` - Available margin for trading
* `get_margin_level()` - Margin level percentage
* `get_equity()` - Current account value
* `calculate_required_margin()` - Calculate margin for planned trade
* `get_account_info()` - All account data including margin

**Margin calculation:**

```python
# Manual calculation
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = equity - margin
margin_level = (equity / margin * 100) if margin > 0 else 0

# Or use dedicated methods
free_margin = await sugar.get_free_margin()
margin_level = await sugar.get_margin_level()
```

---

## Common Pitfalls

### 1) Confusing margin with balance

```python
# WRONG - margin is not balance
margin = await sugar.get_margin()
print(f"I have ${margin:.2f}")  # This is locked, not available!

# CORRECT - use balance or equity
balance = await sugar.get_balance()
print(f"Balance: ${balance:.2f}")
```

### 2) Not checking margin before trading

```python
# WRONG - opening trade without margin check
ticket = await sugar.buy_market("EURUSD", 1.0)  # Might fail!

# CORRECT - verify free margin first
free_margin = await sugar.get_free_margin()
required_margin = await sugar.calculate_required_margin("EURUSD", 1.0)

if free_margin >= required_margin:
    ticket = await sugar.buy_market("EURUSD", 1.0)
else:
    print("Insufficient margin")
```

---

## Pro Tips

1. **Zero margin = No positions** - Margin is 0 when you have no open positions

2. **Margin increases with leverage** - Lower leverage = more margin required

3. **Watch margin level** - Keep margin level above 200% for safety

4. **Use get_free_margin()** - Simpler than equity - margin calculation

5. **Calculate before trading** - Use `calculate_required_margin()` to plan trades

---

## 📚 See Also

- [get_free_margin](get_free_margin.md) - Get available margin for trading
- [get_margin_level](get_margin_level.md) - Get margin level percentage
- [calculate_required_margin](../10.%20Risk_Management/calculate_required_margin.md) - Calculate required margin for a trade
