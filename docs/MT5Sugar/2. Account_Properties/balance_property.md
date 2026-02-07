# Balance Property (`balance`)

> **Async Property:** Alternative syntax for `get_balance()`.

**API Information:**

* **Property:** `await sugar.balance`
* **Returns:** Current balance as `float`
* **Layer:** HIGH (MT5Sugar)

---

## Property Signature

```python
@property
async def balance(self) -> float
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

* **What it is:** Python property syntax for getting balance.
* **Why use it:** Cleaner, more Pythonic syntax than `get_balance()`.
* **Difference:** `await sugar.balance` vs `await sugar.get_balance()` - both are identical.

---

## ⚡ Under the Hood

```
await sugar.balance
    ↓ internally calls
sugar.get_balance()
    ↓ calls
MT5Service.get_account_summary()
    ↓ calls
MT5Account.account_summary()
    ↓ gRPC protobuf
MT5 Terminal
```

**What happens:**

1. **Property:** Forwards to `get_balance()` method
2. **Same chain:** Identical to calling `get_balance()` directly

**Related files:**
- Sugar: `src/pymt5/mt5_sugar.py:451`

---

## When to Use

**Cleaner syntax** - When you prefer property style

**Quick access** - Shorter code for balance checks

**Pythonic code** - More natural Python syntax

---

## 🔗 Usage Examples

### 1) Property vs method syntax

```python
# Using property (cleaner)
balance = await sugar.balance
print(f"Balance: ${balance:.2f}")

# Using method (traditional)
balance = await sugar.get_balance()
print(f"Balance: ${balance:.2f}")

# Both are IDENTICAL
```

---

### 2) Use in expressions

```python
# Property syntax looks cleaner
if await sugar.balance < 1000:
    print("Low balance")

# vs method syntax
if await sugar.get_balance() < 1000:
    print("Low balance")
```

---

### 3) Multiple properties together

```python
# Very clean with properties
balance = await sugar.balance
equity = await sugar.equity
profit = await sugar.profit

print(f"Balance: ${balance:.2f}")
print(f"Equity:  ${equity:.2f}")
print(f"Profit:  ${profit:+.2f}")
```

---

## Related Properties

**Other async properties:**

* `equity` - Current equity
* `margin` - Used margin
* `free_margin` - Free margin
* `margin_level` - Margin level %
* `profit` - Floating profit/loss

**Equivalent methods:**

* `get_balance()` - Same result, different syntax
* `get_account_info()` - Get all account data at once

---

## Common Pitfalls

### 1) Forgetting await

```python
# WRONG - missing await
balance = sugar.balance  # Returns coroutine!

# CORRECT - always await properties
balance = await sugar.balance
```

### 2) Trying to set property

```python
# WRONG - properties are read-only
sugar.balance = 10000  # Not allowed!

# Properties are for READING only
balance = await sugar.balance  # Correct
```

---

## Pro Tips

1. **Choose your style** - Properties vs methods - both work identically

2. **Still async** - Must await properties just like methods

3. **Read-only** - Cannot set values via properties

4. **IDE support** - Properties show up in auto-completion

5. **Use get_account_info()** - More efficient for multiple values

---

## 📚 See Also

- [get_balance](get_balance.md) - Method-style access to balance
- [get_equity](get_equity.md) - Get equity (balance + floating P/L)
