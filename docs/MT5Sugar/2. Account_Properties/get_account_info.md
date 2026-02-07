# Get Account Info (`get_account_info`)

> **Sugar method:** Returns complete account information as structured dataclass.

**API Information:**

* **Method:** `sugar.get_account_info()`
* **Returns:** `AccountInfo` dataclass with 10 fields
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def get_account_info(self) -> AccountInfo
```

---

## ℹ️ Input / Output

| Input | Type | Description |
|-------|------|-------------|
| *None* | - | No parameters required |

| Output | Type | Description |
|--------|------|-------------|
| `AccountInfo` | `dataclass` | Complete account information |

**AccountInfo fields:**

- `login` (int) - Account number
- `balance` (float) - Account balance
- `equity` (float) - Current equity
- `profit` (float) - Floating P/L
- `margin` (float) - Used margin
- `free_margin` (float) - Free margin
- `margin_level` (float) - Margin level %
- `leverage` (int) - Account leverage
- `currency` (str) - Account currency
- `company` (str) - Broker name

---

## 🏛️ Essentials

* **What it is:** Single method to get ALL account data at once.
* **Why you need it:** More efficient than calling 10+ separate methods.
* **Advantage:** One API call instead of multiple requests.

---

## ⚡ Under the Hood

```
MT5Sugar.get_account_info()
    ↓ calls
MT5Service.get_account_summary()
    ↓ calls multiple
MT5Account.account_summary() + account_info_double() × 4
    ↓ gRPC protobuf (5 calls internally)
AccountHelperService + AccountInformationService
    ↓ MT5 Terminal
```

**What happens:**

1. **Sugar Layer:** Calls service, wraps result in AccountInfo dataclass
2. **Service Layer:** Makes 5 internal gRPC calls, returns AccountSummary
3. **Account Layer:** Combines account_summary() + 4 account_info_double() calls
4. **Result:** Complete account snapshot in one dataclass

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:2031`
- Service: `src/pymt5/mt5_service.py:254`
- Account: `package/helpers/mt5_account.py:540`

---

## When to Use

**Account dashboard** - Display all account metrics

**Risk checks** - Verify multiple parameters at once

**Logging** - Record complete account state

**Decision making** - Access all data for trading logic

**Efficiency** - Replace multiple individual calls

---

## 🔗 Usage Examples

### 1) Get all account data at once

```python
info = await sugar.get_account_info()

print(f"Account:      {info.login}")
print(f"Balance:      ${info.balance:.2f}")
print(f"Equity:       ${info.equity:.2f}")
print(f"Profit:       ${info.profit:+.2f}")
print(f"Free Margin:  ${info.free_margin:.2f}")
print(f"Margin Level: {info.margin_level:.2f}%")
print(f"Leverage:     1:{info.leverage}")
print(f"Currency:     {info.currency}")
```

---

### 2) Efficient vs inefficient approach

```python
# INEFFICIENT - 6 separate calls
balance = await sugar.get_balance()
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = await sugar.get_free_margin()
margin_level = await sugar.get_margin_level()
profit = await sugar.get_floating_profit()

# EFFICIENT - 1 call gets everything
info = await sugar.get_account_info()
# Access: info.balance, info.equity, info.margin, etc.
```

---

### 3) Complete account health check

```python
info = await sugar.get_account_info()

print("=" * 50)
print("ACCOUNT HEALTH REPORT")
print("=" * 50)
print(f"Broker:        {info.company}")
print(f"Account:       {info.login}")
print(f"Currency:      {info.currency}")
print(f"Leverage:      1:{info.leverage}")
print("-" * 50)
print(f"Balance:       ${info.balance:>12,.2f}")
print(f"Equity:        ${info.equity:>12,.2f}")
print(f"Profit/Loss:   ${info.profit:>12,.2f}")
print("-" * 50)
print(f"Used Margin:   ${info.margin:>12,.2f}")
print(f"Free Margin:   ${info.free_margin:>12,.2f}")
print(f"Margin Level:  {info.margin_level:>11.2f}%")
print("=" * 50)

# Health assessment
if info.margin_level < 100:
    status = "CRITICAL"
elif info.margin_level < 200:
    status = "WARNING"
elif info.free_margin < 100:
    status = "LOW MARGIN"
else:
    status = "HEALTHY"

print(f"Status: {status}")
```

---

## Related Methods

**Individual getters (less efficient):**

* `get_balance()` - Just balance
* `get_equity()` - Just equity
* `get_margin()` - Just margin
* `get_free_margin()` - Just free margin
* `get_margin_level()` - Just margin level
* `get_floating_profit()` - Just floating P/L

**Best practice:**

```python
# If you need 1-2 values:
balance = await sugar.get_balance()
equity = await sugar.get_equity()

# If you need 3+ values:
info = await sugar.get_account_info()
# Use info.balance, info.equity, info.margin, etc.
```

---

## Common Pitfalls

### 1) Making multiple calls when one is enough

```python
# WRONG - wasteful
balance = await sugar.get_balance()
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = await sugar.get_free_margin()
# 4 separate gRPC roundtrips!

# CORRECT - efficient
info = await sugar.get_account_info()
# 1 call, access all fields
```

### 2) Not using dataclass properly

```python
# WRONG - recreating what's already there
info = await sugar.get_account_info()
my_balance = info.balance
my_equity = info.equity
# Just use info directly!

# CORRECT - use dataclass as-is
info = await sugar.get_account_info()
print(f"Balance: ${info.balance:.2f}")
print(f"Equity: ${info.equity:.2f}")
```

---

## Pro Tips

1. **Use for dashboards** - Perfect for displaying complete account state

2. **Cache for efficiency** - If you need multiple fields, call once and reuse

3. **Dataclass benefits** - Type hints, auto-completion in IDE

4. **Check margin health** - Use `margin_level` and `free_margin` for risk monitoring

5. **Single call advantage** - More efficient than multiple individual method calls

---

## 📚 See Also

- [get_balance](get_balance.md) - Get current account balance
- [get_equity](get_equity.md) - Get equity (balance + floating P/L)
- [get_margin](get_margin.md) - Get used margin
