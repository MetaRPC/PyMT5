# Get Account Equity (`get_equity`)

> **Sugar method:** Returns current equity (balance + floating P/L) in one line.

**API Information:**

* **Method:** `sugar.get_equity()`
* **Returns:** Current equity as `float`
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_equity(self) -> float
```

---

## ℹ️ Input / Output

| Input | Type | Description |
|-------|------|-------------|
| *None* | - | No parameters required |

| Output | Type | Description |
|--------|------|-------------|
| `equity` | `float` | Current equity (balance + floating profit) |

---

## 🏛️ Essentials

* **What it is:** Current account value including open positions' floating profit/loss.
* **Why you need it:** Real-time account worth, margin level calculations, risk management.
* **Formula:** Equity = Balance + Floating Profit - Floating Loss

---

## ⚡ Under the Hood

```
MT5Sugar.get_equity()
    ↓ calls
MT5Service.get_account_summary()
    ↓ calls
MT5Account.account_summary()
    ↓ gRPC protobuf
AccountHelperService.AccountSummary()
    ↓ MT5 Terminal
```

**What happens:**

1. **Sugar Layer:** Simple async method extracts equity field
2. **Service Layer:** Returns AccountSummary dataclass
3. **Account Layer:** gRPC call to terminal
4. **Result:** Balance + all open positions P/L

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:396`
- Service: `src/pymt5/mt5_service.py:254`
- Account: `package/helpers/mt5_account.py:540`

---

## When to Use

**Risk management** - Calculate margin level and available funds

**Position monitoring** - Track real-time account value

**Stop-out prevention** - Monitor equity to avoid margin calls

**Performance tracking** - See total account value including open trades

**Before trading** - Verify sufficient equity for new positions

---

## 🔗 Usage Examples

### 1) Basic usage

```python
equity = await sugar.get_equity()
print(f"Equity: ${equity:.2f}")
# Output: Equity: $10250.50
```

---

### 2) Compare balance vs equity

```python
balance = await sugar.get_balance()
equity = await sugar.get_equity()
floating_pl = equity - balance

print(f"Balance:      ${balance:.2f}")
print(f"Equity:       ${equity:.2f}")
print(f"Floating P/L: ${floating_pl:+.2f}")

# Output:
# Balance:      $10000.00
# Equity:       $10250.50
# Floating P/L: +$250.50
```

---

### 3) Monitor margin level

```python
equity = await sugar.get_equity()
margin = await sugar.get_margin()

if margin > 0:
    margin_level = (equity / margin) * 100
    print(f"Equity:        ${equity:.2f}")
    print(f"Margin:        ${margin:.2f}")
    print(f"Margin Level:  {margin_level:.2f}%")

    if margin_level < 100:
        print("WARNING: Low margin level!")
```

---

## Related Methods

**Account value methods:**

* `get_balance()` - Balance without open positions
* `get_floating_profit()` - Only the P/L from open positions
* `get_margin()` - Used margin
* `get_margin_level()` - Margin level percentage
* `get_account_info()` - All account data at once

**Key difference:**
```python
# Balance: What you started with + closed trades
balance = await sugar.get_balance()

# Equity: Balance + floating P/L (reality check)
equity = await sugar.get_equity()

# The difference is your open positions P/L
floating = equity - balance
```

---

## Common Pitfalls

### 1) Using balance instead of equity for margin checks

```python
# WRONG - balance doesn't reflect open positions
balance = await sugar.get_balance()
if balance < 1000:
    print("Low funds")  # Might be wrong!

# CORRECT - equity shows real account value
equity = await sugar.get_equity()
if equity < 1000:
    print("Low funds")  # Accurate check
```

### 2) Not considering floating losses

```python
# WRONG - only checking balance
balance = await sugar.get_balance()
print(f"I have ${balance:.2f}")  # Misleading if positions are losing

# CORRECT - check equity for reality
equity = await sugar.get_equity()
print(f"Real value: ${equity:.2f}")  # Shows true situation
```

---

## Pro Tips

1. **Equity is reality** - Always use equity for current account worth

2. **Margin level formula** - (Equity / Margin) * 100

3. **Stop-out watch** - Brokers close positions when margin level drops below threshold (typically 20-50%)

4. **Use get_account_info()** - Get equity, balance, margin all at once

5. **Track equity changes** - Monitor equity over time to measure performance

---

## 📚 See Also

- [get_balance](get_balance.md) - Get current account balance
- [get_floating_profit](get_floating_profit.md) - Get current floating profit/loss
- [get_margin_level](get_margin_level.md) - Get margin level percentage
