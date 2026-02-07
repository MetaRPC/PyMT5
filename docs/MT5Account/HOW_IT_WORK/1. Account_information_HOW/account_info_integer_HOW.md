## account_info_integer — How it works

---

## 📌 Overview

This example shows how to retrieve **integer account properties** using the low-level asynchronous method `account_info_integer()`.

The method is used to request values that are represented in MetaTrader as integers: whether trading is allowed, leverage size, account login, trade mode, and other flags or parameters.

Unlike `account_info_double()`, this method always returns an **integer (`int`)**.

---

## Method Signature

```python
async def account_info_integer(
    property_id: AccountInfoIntegerPropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> int
```

**Key Points:**

* The method is asynchronous and called with `await`.
* `property_id` specifies **which integer property** of the account to request.
* `deadline` and `cancellation_event` control call execution time.
* The result is returned as a regular Python `int`.

---

## 🧩 Code Example — Pre-validation of Account Before Trading

```python
async def validate_account_for_trading(account: MT5Account) -> bool:
    deadline = datetime.utcnow() + timedelta(seconds=5)

    # Check: is trading allowed on the account
    trade_allowed = await account.account_info_integer(
        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_ALLOWED,
        deadline
    )

    if not trade_allowed:
        print("[ERROR] Trading is disabled on this account")
        return False

    # Check: is leverage configured correctly
    leverage = await account.account_info_integer(
        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE,
        deadline
    )

    if leverage < 1:
        print("[ERROR] Invalid leverage setting")
        return False

    print(f"[OK] Account ready to trade (Leverage: 1:{leverage})")
    return True
```

In this example, `account_info_integer()` is used as a source of **flags and parameters** needed for basic validation of account readiness for trading.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Checking Trading Permission

```python
trade_allowed = await account.account_info_integer(
    account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_ALLOWED,
    deadline
)
```

Here, a request is made for a single integer account property — a flag that indicates whether trading is allowed.

* the method performs an asynchronous call
* the return value is an integer (`int`)

In practice, this value is used as a boolean flag:

* `0` — trading is disabled
* non-zero value — trading is allowed

The method itself **does not interpret** this value — it only returns a number.

---

### 2️⃣ Using the Value in Application Logic

```python
if not trade_allowed:
    print("[ERROR] Trading is disabled on this account")
    return False
```

At this stage, regular user logic begins:

* the value received from `account_info_integer()` is used in a condition
* when trading is disabled, function execution terminates

This decision is completely **outside the responsibility of the low-level API**.

---

### 3️⃣ Checking Leverage

```python
leverage = await account.account_info_integer(
    account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE,
    deadline
)
```

Here, a second call to the same method is performed, but with a different `property_id`.

Important:

* each call requests **exactly one property**
* the method does not cache values
* each value is retrieved independently

---

### 4️⃣ Applying the Check

```python
if leverage < 1:
    print("[ERROR] Invalid leverage setting")
    return False
```

The received value is used directly:

* compared against expected threshold
* when value is incorrect, execution is interrupted

As in the previous case:

* the method doesn't know which leverage is considered acceptable
* value interpretation is the calling code's responsibility

---

## Summary

In this example, `account_info_integer()` is used as a simple source of integer account parameters.

The method is called multiple times with different `property_id`, and all decision-making logic is built on top of the returned values.

This approach allows:

* separating data retrieval from interpretation
* reusing low-level API in different strategies
* explicitly controlling trading logic behavior
