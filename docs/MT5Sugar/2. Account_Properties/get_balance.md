# Get Account Balance (`get_balance`)

> **Sugar method:** Returns current account balance in one line.

**API Information:**

* **Method:** `sugar.get_balance()`
* **Returns:** Current balance as `float`
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_balance(self) -> float
```

---

## ℹ️ Input / Output

| Input | Type | Description |
|-------|------|-------------|
| *None* | - | No parameters required |

| Output | Type | Description |
|--------|------|-------------|
| `balance` | `float` | Current account balance |

---

## 🏛️ Essentials

* **What it is:** Gets your account balance - the money you have before considering open positions.
* **Why you need it:** Check available funds, calculate risk amounts, validate before trading.
* **Sanity check:** Balance <= Equity (equity includes floating P/L).

---

## ⚡ Under the Hood

This method demonstrates the three-tier architecture in action:

```
MT5Sugar.get_balance()
    ↓ calls
MT5Service.get_account_summary()
    ↓ calls
MT5Account.account_summary()
    ↓ gRPC protobuf
AccountHelperService.AccountSummary()
    ↓ MT5 Terminal
```

**What happens:**

1. **Sugar Layer:** Simple async method with no parameters
2. **Service Layer:** Calls `account_summary()` and extracts `balance` field from AccountSummary dataclass
3. **Account Layer:** Makes gRPC call to MT5 terminal, returns protobuf Data object
4. **Result:** Clean float value ready to use

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:386`
- Service: `src/pymt5/mt5_service.py:254`
- Account: `package/helpers/mt5_account.py:540`

---

## When to Use

**Before trading** - Check if you have enough funds

**Risk calculation** - Calculate position size based on balance

**Monitoring** - Track account value

**Reporting** - Generate account reports

**Validation** - Ensure sufficient funds for trading

---

## 🔗 Usage Examples

### 1) Basic usage

```python
balance = await sugar.get_balance()
print(f"Balance: ${balance:.2f}")
# Output: Balance: $10000.00
```

---

### 2) Check before trading

```python
balance = await sugar.get_balance()

if balance < 1000:
    print("Insufficient balance for trading")
    return

print("Balance sufficient - proceeding with trade")
```

---

### 3) Calculate risk amount

```python
balance = await sugar.get_balance()
risk_percent = 2.0

risk_amount = balance * risk_percent / 100.0

print(f"Balance:     ${balance:.2f}")
print(f"Risk (2%):   ${risk_amount:.2f}")

# Better: use calculate_position_size()
lot_size = await sugar.calculate_position_size("EURUSD", risk_percent, 50)
print(f"Lot size:    {lot_size:.2f}")
```

---

## Related Methods

**Other balance methods:**

* `get_equity()` - Balance + floating P/L
* `get_margin()` - Used margin
* `get_free_margin()` - Available margin for trading
* `get_floating_profit()` - Current floating profit/loss
* `get_account_info()` - Get all account data at once

**Recommended pattern:**

```python
# Instead of calling get_balance, get_equity, etc separately:
account_info = await sugar.get_account_info()
# Now you have: balance, equity, margin, free_margin, profit, etc.
```

---

## Common Pitfalls

### 1) Confusing Balance vs Equity

```python
# WRONG - using Balance when you need Equity
balance = await sugar.get_balance()  # Doesn't include open positions!

# CORRECT - use Equity for total account value
equity = await sugar.get_equity()  # Includes floating P/L
```

### 2) Not using await

```python
# WRONG - forgetting await
balance = sugar.get_balance()  # Returns coroutine, not float!

# CORRECT - always await async methods
balance = await sugar.get_balance()
```

---

## Pro Tips

1. **Use get_account_info()** - More efficient than calling multiple methods

2. **Balance for risk calculation** - Use balance (not equity) for position sizing

3. **Check before trading** - Always verify sufficient balance

4. **Track changes** - Monitor balance to measure performance

5. **Equity is reality** - Balance is historical, Equity is current

---

## 📚 See Also

- [get_equity](get_equity.md) - Get equity (balance + floating P/L)
- [get_account_info](get_account_info.md) - Get all account data at once
