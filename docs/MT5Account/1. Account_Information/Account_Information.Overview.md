# MT5Account - Account Information - Overview

> Account balance, equity, margin, leverage, currency, and other account properties. Use this page to choose the right API for accessing account state.

## 📁 What lives here

* **[account_summary](./account_summary.md)** - **all account info** at once (balance, equity, leverage, credit, server time, etc.). **RECOMMENDED**
* **[account_info_double](./account_info_double.md)** - **single double value** from account (balance, equity, margin, profit, credit, margin level, etc.).
* **[account_info_integer](./account_info_integer.md)** - **single integer value** from account (login, leverage, trade mode, limit orders, trade allowed, etc.).
* **[account_info_string](./account_info_string.md)** - **single string value** from account (name, server, currency, company).

---

## 📚 Step-by-step tutorials

Want detailed explanations with line-by-line code breakdown? Check these guides:

* **[account_summary - How it works](../HOW_IT_WORK/1. Account_information_HOW/account_summary_HOW.md)**
* **[account_info_double - How it works](../HOW_IT_WORK/1. Account_information_HOW/account_info_double_HOW.md)**
* **[account_info_integer - How it works](../HOW_IT_WORK/1. Account_information_HOW/account_info_integer_HOW.md)**
* **[account_info_string - How it works](../HOW_IT_WORK/1. Account_information_HOW/account_info_string_HOW.md)**

---

## 🧭 Plain English

* **account_summary** - the **one-stop shop** for complete account snapshot (balance, equity, leverage, currency, etc.).
* **account_info_double** - grab **one numeric property** when you need just balance or margin.
* **account_info_integer** - grab **one integer property** like login number or leverage.
* **account_info_string** - grab **one text property** like account name or currency.

> Rule of thumb: need **full snapshot** - `account_summary()`; need **one specific value** - `account_info_*` (double/integer/string).

---

## Quick choose

| If you need                                          | Use                       | Returns                    | Key inputs                          |
| ---------------------------------------------------- | ------------------------- | -------------------------- | ----------------------------------- |
| Complete account snapshot (all values)               | `account_summary`         | AccountSummaryData         | *(none)*                            |
| One numeric value (balance, equity, margin, etc.)    | `account_info_double`     | Single `float`             | Property enum (BALANCE, EQUITY, etc.) |
| One integer value (login, leverage, etc.)            | `account_info_integer`    | Single `int`               | Property enum (LOGIN, LEVERAGE, etc.) |
| One text value (name, currency, server, etc.)        | `account_info_string`     | Single `str`               | Property enum (NAME, CURRENCY, etc.) |

---

## ℹ️ Cross-refs & gotchas

* **Margin Level** - use `account_info_double(ACCOUNT_MARGIN_LEVEL)` to get as percentage.
* **Free Margin** - use `account_info_double(ACCOUNT_MARGIN_FREE)` for available margin.
* **account_summary** includes basic info (balance, equity, leverage); for margin use `account_info_double`.
* **account_info_*** methods are lighter if you only need one property.
* **Currency** affects how profits are calculated - always check account currency.
* **Leverage** determines margin requirements - higher leverage = less margin needed.
* **Deadline/timeout** - Remember to set appropriate deadline for async calls.

---

## 🟢 Minimal snippets

```python
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2
from datetime import datetime, timedelta

# Get complete account snapshot
summary = await account.account_summary()

print(f"Balance: ${summary.account_balance:.2f}, "
      f"Equity: ${summary.account_equity:.2f}, "
      f"Leverage: 1:{summary.account_leverage}")
```

```python
# Get single property - account balance
deadline = datetime.utcnow() + timedelta(seconds=3)

balance = await account.account_info_double(
    property_id=account_info_pb2.ACCOUNT_BALANCE,
    deadline=deadline
)

print(f"Balance: ${balance:.2f}")
```

```python
# Get account leverage
leverage = await account.account_info_integer(
    property_id=account_info_pb2.ACCOUNT_LEVERAGE
)

print(f"Leverage: 1:{leverage}")
```

```python
# Get account currency
currency = await account.account_info_string(
    property_id=account_info_pb2.ACCOUNT_CURRENCY
)

print(f"Currency: {currency}")
```

```python
# Check account health
summary = await account.account_summary()

# Get margin level (account_summary doesn't include margin, need separate call)
margin_level = await account.account_info_double(
    account_info_pb2.ACCOUNT_MARGIN_LEVEL
)

if margin_level < 100:
    print("[WARNING] Margin level critical!")
elif margin_level < 200:
    print("[WARNING] Low margin level")
else:
    print("[OK] Healthy margin level")
```

```python
# Validate account before trading
summary = await account.account_summary()

# Check if trading is allowed
trade_allowed = await account.account_info_integer(
    account_info_pb2.ACCOUNT_TRADE_ALLOWED
)

if not trade_allowed:
    raise RuntimeError("Trading is disabled on this account")

# Check minimum balance
if summary.account_balance < 100:
    raise ValueError(f"Balance too low: ${summary.account_balance:.2f}")

print(f"[OK] Account ready to trade")
print(f"   Balance: ${summary.account_balance:.2f} {summary.account_currency}")
print(f"   Leverage: 1:{summary.account_leverage}")
```

```python
# Monitor account equity in real-time
async def monitor_equity(interval: float = 5.0):
    """Monitor equity every N seconds"""
    while True:
        summary = await account.account_summary()

        floating_pnl = summary.account_equity - summary.account_balance

        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"Equity: ${summary.account_equity:,.2f} | "
              f"Floating P/L: ${floating_pnl:+,.2f}")

        await asyncio.sleep(interval)

# await monitor_equity(interval=5.0)
```

```python
# Get all account details for logging
async def log_account_details():
    """Log comprehensive account information"""
    summary = await account.account_summary()

    # Get additional margin info
    margin_level = await account.account_info_double(
        account_info_pb2.ACCOUNT_MARGIN_LEVEL
    )

    free_margin = await account.account_info_double(
        account_info_pb2.ACCOUNT_MARGIN_FREE
    )

    mode_names = {0: "DEMO", 1: "CONTEST", 2: "REAL"}
    mode = mode_names.get(summary.account_trade_mode, "UNKNOWN")

    print(f"{'='*60}")
    print(f"ACCOUNT DETAILS")
    print(f"{'='*60}")
    print(f"Login:          #{summary.account_login}")
    print(f"Name:           {summary.account_user_name}")
    print(f"Broker:         {summary.account_company_name}")
    print(f"Mode:           {mode}")
    print(f"Currency:       {summary.account_currency}")
    print(f"Leverage:       1:{summary.account_leverage}")
    print(f"")
    print(f"Balance:        ${summary.account_balance:,.2f}")
    print(f"Equity:         ${summary.account_equity:,.2f}")
    print(f"Credit:         ${summary.account_credit:,.2f}")
    print(f"Free Margin:    ${free_margin:,.2f}")
    print(f"Margin Level:   {margin_level:.2f}%")
    print(f"{'='*60}")

# await log_account_details()
```

---

## 📚 See also

* **Symbol Information:** [Symbol_Information.Overview](../2. Symbol_Information/Symbol_Information.Overview.md) - get symbol/market data
* **Positions & Orders:** [Positions_Orders.Overview](../3. Positions_Orders/Positions_Orders.Overview.md) - manage positions and orders
* **Trading:** [Trading_Operations.Overview](../5. Trading_Operations/Trading_Operations.Overview.md) - place and manage trades
