# Get Floating Profit (`get_floating_profit`)

> **Sugar method:** Returns total unrealized P/L from all open positions.

**API Information:**

* **Method:** `sugar.get_floating_profit()`
* **Returns:** Floating profit/loss as `float`
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_floating_profit(self) -> float
```

---

## ℹ️ Input / Output

| Input | Type | Description |
|-------|------|-------------|
| *None* | - | No parameters required |

| Output | Type | Description |
|--------|------|-------------|
| `profit` | `float` | Total floating profit (positive) or loss (negative) |

---

## 🏛️ Essentials

* **What it is:** Sum of unrealized profit/loss from all open positions.
* **Why you need it:** Track real-time performance without closing positions.
* **Formula:** Floating P/L = Equity - Balance

---

## ⚡ Under the Hood

```
MT5Sugar.get_floating_profit()
    ↓ calls
MT5Service.get_account_double(ACCOUNT_PROFIT)
    ↓ calls
MT5Account.account_info_double(property_id=ACCOUNT_PROFIT)
    ↓ gRPC protobuf
AccountInformationService.AccountInfoDouble(property_id=13)
    ↓ MT5 Terminal
```

**What happens:**

1. **Sugar Layer:** Calls service with ACCOUNT_PROFIT constant
2. **Service Layer:** Requests profit property from account
3. **Account Layer:** gRPC call to terminal
4. **Result:** Sum of all open positions P/L, updates with every tick

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:439`
- Service: `src/pymt5/mt5_service.py:298`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:578`

---

## When to Use

**Performance tracking** - Monitor profits without closing

**Risk management** - Check if losses exceed limits

**Take profit decisions** - Decide when to close profitable positions

**Stop loss monitoring** - Track if losses are acceptable

**Dashboard display** - Show real-time account P/L

---

## 🔗 Usage Examples

### 1) Basic floating P/L check

```python
profit = await sugar.get_floating_profit()

if profit > 0:
    print(f"Profit: +${profit:.2f}")
else:
    print(f"Loss: ${profit:.2f}")

# Output: Profit: +$125.50
```

---

### 2) Track performance vs balance

```python
balance = await sugar.get_balance()
equity = await sugar.get_equity()
floating_pl = await sugar.get_floating_profit()

# Verify: equity should equal balance + floating_pl
assert abs(equity - (balance + floating_pl)) < 0.01

print(f"Starting Balance: ${balance:.2f}")
print(f"Floating P/L:     ${floating_pl:+.2f}")
print(f"Current Equity:   ${equity:.2f}")

profit_percent = (floating_pl / balance) * 100
print(f"Return:           {profit_percent:+.2f}%")
```

---

### 3) Risk management - close if loss limit exceeded

```python
balance = await sugar.get_balance()
floating_pl = await sugar.get_floating_profit()

max_loss_percent = 5.0
max_loss = balance * max_loss_percent / 100

print(f"Balance:      ${balance:.2f}")
print(f"Floating P/L: ${floating_pl:+.2f}")
print(f"Max Loss:     -${max_loss:.2f}")

if floating_pl < -max_loss:
    print("Loss limit exceeded - closing all positions")
    await sugar.close_all_positions()
```

---

## Related Methods

**P/L tracking methods:**

* `get_balance()` - Starting capital + closed trades
* `get_equity()` - Balance + floating P/L
* `get_total_profit()` - Alias for get_floating_profit()
* `get_profit_by_symbol()` - P/L for specific symbol
* `get_profit()` - Historical profit for period

**P/L relationships:**
```python
balance = await sugar.get_balance()
floating_pl = await sugar.get_floating_profit()
equity = await sugar.get_equity()

# These are equivalent:
assert abs(equity - (balance + floating_pl)) < 0.01
```

---

## Common Pitfalls

### 1) Confusing floating vs realized profit

```python
# WRONG - floating profit is NOT realized
floating_pl = await sugar.get_floating_profit()
print(f"I made ${floating_pl:.2f}")  # Not yet!

# CORRECT - only when positions are closed
balance_before = await sugar.get_balance()
# ... close positions ...
balance_after = await sugar.get_balance()
realized_profit = balance_after - balance_before
print(f"Realized profit: ${realized_profit:.2f}")
```

### 2) Not handling negative values

```python
# WRONG - assuming profit is always positive
profit = await sugar.get_floating_profit()
print(f"Profit: ${profit:.2f}")  # Confusing if negative!

# CORRECT - show sign explicitly
profit = await sugar.get_floating_profit()
if profit >= 0:
    print(f"Profit: +${profit:.2f}")
else:
    print(f"Loss: ${profit:.2f}")
```

---

## Pro Tips

1. **Updates in real-time** - Floating P/L changes with every price tick

2. **Not realized until closed** - Floating profit can disappear before closing

3. **Use for monitoring** - Track but don't rely on it for decisions

4. **Equity formula** - Equity = Balance + Floating P/L (always)

5. **Symbol-specific tracking** - Use `get_profit_by_symbol()` for individual symbols

---

## 📚 See Also

- [get_equity](get_equity.md) - Get equity (balance + floating P/L)
- [get_balance](get_balance.md) - Get current account balance
- [get_profit_by_symbol](../7.%20Position_Information/get_profit_by_symbol.md) - Get profit for specific symbol
