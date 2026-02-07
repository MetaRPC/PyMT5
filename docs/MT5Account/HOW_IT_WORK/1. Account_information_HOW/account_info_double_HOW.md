## account_info_double — How it works

---

## 📌 Overview

This example shows how to retrieve **a specific numeric account property** using the low-level asynchronous method `account_info_double()`.

The method is designed to request **exactly one account value** stored as a floating-point number (e.g., balance, equity, margin level).

It performs **one request** and returns **one value of type `float`**.

The method performs no aggregation, validation, or trading logic.

Simply put:

> The method simply requests *"give me this numeric account property"*
> and returns the result as a regular Python `float`.

---

## Method Signature

```python
async def account_info_double(
    property_id: AccountInfoDoublePropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> float
```

**Key Points:**

* The method is **asynchronous** and must be called with `await`.
* `property_id` specifies **which account property** to request.
* `deadline` and `cancellation_event` control **call execution time**.
* Return value is a **regular Python `float`**.

---

## 🧩 Code Example — Checking Margin Level Before Trading

```python
async def check_margin_level(account: MT5Account, min_level: float = 200.0) -> bool:
    deadline = datetime.utcnow() + timedelta(seconds=3)

    margin_level = await account.account_info_double(
        property_id=account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_MARGIN_LEVEL,
        deadline=deadline
    )

    print(f"Margin Level: {margin_level:.2f}%")

    if margin_level < min_level:
        raise ValueError(
            f"Margin level {margin_level:.2f}% is below minimum {min_level:.2f}%"
        )

    return True
```

In this example, `account_info_double()` is used as a **building block** for a simple safety check before opening trades.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Method Call

```python
margin_level = await account.account_info_double(
    property_id=account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_MARGIN_LEVEL,
    deadline=deadline
)
```

This line performs **one request** for a single numeric account property.

* `ACCOUNT_MARGIN_LEVEL` specifies **which value to retrieve**
* the method asynchronously awaits the terminal's response
* upon successful execution, a `float` is returned

At this stage:

* no validation is performed
* no value interpretation occurs
* the number is returned exactly as provided by the terminal

---

### 2️⃣ Working with Return Value

```python
print(f"Margin Level: {margin_level:.2f}%")
```

The return value is a **regular Python number**.

* no protobuf objects
* no nested structures
* no additional data parsing required

The value can be immediately used in calculations, logs, or conditions.

---

### 3️⃣ Applying Business Logic

```python
if margin_level < min_level:
    raise ValueError(...)
```

After receiving the numeric value, **regular user application logic** begins.

In this example:

* `margin_level` is the value returned from `account_info_double()`
* `min_level` is a threshold defined by strategy logic or risk management

The code simply compares two numbers and makes a decision:

* if margin level is below acceptable — execution is interrupted
* if condition is met — function completes successfully

It's important to understand the boundary of responsibility:

* `account_info_double()` **only returns a number**
* comparison, interpretation, and reaction to the value **are not part of the API**

This is exactly how low-level methods are intended to be used — as a data source on top of which your own strategy logic is built.

---

## What This Method Does

* Requests **one numeric account property**
* Performs **one asynchronous call**
* Returns **one value of type `float`**

Typical use cases:

* balance checking
* equity monitoring
* margin and free margin control
* risk management conditions


---

## Summary

* `account_info_double()` is a **low-level getter** for numeric account properties.
* It retrieves **exactly one property** per call.
* The method returns a **clean Python `float`**, ready to use.
* All decision-making logic remains on the calling code side.
