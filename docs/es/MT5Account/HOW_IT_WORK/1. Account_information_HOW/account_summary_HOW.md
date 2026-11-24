## account_summary — How it works

---

## 📌 Overview

This example demonstrates how to retrieve a **trading account summary** using the low-level asynchronous method `account_summary()`.

Unlike `account_info_*` methods that return one specific value, `account_summary()` is used when you need **multiple related account parameters at once**.

The method executes **one request** and returns an object with pre-collected account state data.

---

## Method Signature

```python
async def account_summary(
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and must be called with `await`
* Parameters `deadline` and `cancellation_event` control execution time
* The method does not accept `property_id` because it returns **a set of values**, not a single field

---

## 🧩 Code Example — Assessing Trading Risk

```python
async def assess_trading_risk(account: MT5Account) -> str:
    summary = await account.account_summary()

    # Calculate risk factors
    balance = summary.account_balance
    equity = summary.account_equity
    leverage = summary.account_leverage

    # Risk score
    if leverage > 200:
        risk = "HIGH"
    elif leverage > 100:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # Check current losses
    if equity < balance * 0.9:
        risk = "HIGH"

    print(f"Risk Assessment: {risk}")
    print(f"  Leverage: 1:{leverage}")
    print(f"  Balance: ${balance:.2f}")
    print(f"  Equity: ${equity:.2f}")

    return risk
```

In this example, `account_summary()` is used to retrieve the current account state and subsequently assess the trading risk level.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Retrieving Account Summary Data

```python
summary = await account.account_summary()
```

At this step, one asynchronous call is executed.

* The method requests the entire account state
* The result is a `summary` object
* No repeated API calls are required to read individual fields

After this line, all necessary data is already available locally.

---

### 2️⃣ Extracting Values from Summary

```python
balance = summary.account_balance
equity = summary.account_equity
leverage = summary.account_leverage
```

No server communication occurs here.

* `summary` is a regular Python object
* Values are accessible as attributes
* Reading fields is a local operation

Each line simply extracts the needed parameter from the already-retrieved account state snapshot.

---

### 3️⃣ Initial Risk Assessment by Leverage

```python
if leverage > 200:
    risk = "HIGH"
elif leverage > 100:
    risk = "MEDIUM"
else:
    risk = "LOW"
```

Application logic for risk assessment begins.

* Only the leverage value is used
* Threshold values are defined
* A base risk level is selected

These thresholds are part of user logic and are not related to API operation.

---

### 4️⃣ Additional Check for Current Losses

```python
if equity < balance * 0.9:
    risk = "HIGH"
```

A second check complements the initial assessment.

* Current equity is compared with balance
* If losses exceed the specified threshold, risk is elevated

Regular arithmetic comparison is used here without any special rules.

---

### 5️⃣ Output and Result Return

```python
print(f"Risk Assessment: {risk}")
...
return risk
```

At the end of the function:

* The final risk assessment is printed
* A string value of the risk level is returned

What to do with this result next is up to the calling code.

---

## Summary

In this example, `account_summary()` is used as a source of an **account state snapshot**.

One API call returns a set of related parameters, after which all analysis and decision-making logic executes locally, without additional server requests.
