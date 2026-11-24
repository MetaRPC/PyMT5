## order_calc_margin — How it works

---

## 📌 Overview

This example shows how to use the low-level method `order_calc_margin()` to **estimate acceptable position size based on specified risk**.

Important: in this example **no trading operation is performed**. The method is used exclusively for calculation — as a calculator, not as an action.

The main task of the example:

> understand what position volume can be opened without exceeding the specified account risk.

---

## Method Signature

```python
async def order_calc_margin(
    request: OrderCalcMarginRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> OrderCalcMarginData
```

Key points:

* the method is asynchronous
* does not open trades
* does not reserve funds
* does not change account state
* returns only the calculated margin value

---

## 🧩 Code Example — Risk-based position sizing

```python
async def risk_based_sizing(symbol: str, risk_percent: float = 2.0):
    """Calculate position size based on risk percentage"""

    # Get account summary information
    summary = await account.account_summary()

    # Maximum acceptable risk in money
    max_risk_amount = summary.account_balance * (risk_percent / 100.0)

    print(f"Risk-based position sizing for {symbol}:")
    print(f"  Account balance: ${summary.account_balance:,.2f}")
    print(f"  Risk: {risk_percent}% = ${max_risk_amount:,.2f}\n")

    # Check several possible volumes
    volumes = [0.01, 0.05, 0.10, 0.20, 0.50, 1.00]

    print(f"{'Volume':<10} {'Margin':<15} {'% of Balance':<15}")
    print("-" * 45)

    for volume in volumes:
        request = OrderCalcMarginRequest(
            symbol=symbol,
            order_type=ORDER_TYPE_TF_BUY,
            volume=volume,
            open_price=1.0  # calculated price
        )

        result = await account.order_calc_margin(request)

        margin_percent = (result.margin / summary.account_balance) * 100
        status = "[OK]" if margin_percent <= risk_percent else "[OVER]"

        print(f"{volume:<10.2f} ${result.margin:>12,.2f} {margin_percent:>13.2f}% {status}")
```

---

## 🟢 Detailed Explanation

---

### 1️⃣ Getting Account Balance

```python
summary = await account.account_summary()
```

At this step:

* the current account balance is obtained
* it is used as the base for risk calculation

This is source data, not related to trading.

---

### 2️⃣ Converting Risk from Percentage to Money

```python
max_risk_amount = summary.account_balance * (risk_percent / 100.0)
```

Example:

* balance = $10,000
* risk = 2%
* acceptable risk = $200

This is **pure user business logic**, not part of the API.

---

### 3️⃣ Forming Hypothetical Trade

```python
request = OrderCalcMarginRequest(
    symbol=symbol,
    order_type=ORDER_TYPE_TF_BUY,
    volume=volume,
    open_price=1.0
)
```

Important to understand:

* the trade **is not opened**
* parameters are used only for calculation
* `open_price` can be a conditional value

The request describes a *planned*, not a real operation.

---

### 4️⃣ Calculating Required Margin

```python
result = await account.order_calc_margin(request)
```

At this step:

* the server calculates the margin
* account settings, symbol, and order type are taken into account
* a single number is returned — `result.margin`

No account state is changed in the process.

---

### 5️⃣ Comparing with Acceptable Risk

```python
margin_percent = (result.margin / summary.account_balance) * 100
```

Here user code:

* compares the calculated margin with acceptable risk
* makes a decision whether this volume is acceptable

The API does not participate in this step.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`order_calc_margin()`**:

* performs server-side margin calculation
* opens nothing
* does not affect the account

**User code**:

* defines risk
* selects volumes
* interprets the result
* makes trading decisions

---

## Summary

This example illustrates a safe and correct pattern:

> **plan trade → calculate margin → assess risk → make decision**

The `order_calc_margin()` method is intended precisely for the planning stage and should be used **before opening a trade**, not after.

It allows making informed decisions without risking account state.
