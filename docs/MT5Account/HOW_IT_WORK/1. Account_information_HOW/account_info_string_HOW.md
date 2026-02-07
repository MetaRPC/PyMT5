## account_info_string — How it works

---

## 📌 Overview

This example demonstrates how to retrieve a **string property of a trading account** using the low-level asynchronous method `account_info_string()`.

The method is used to request values that are represented as strings in MetaTrader: server name, account name, deposit currency, and other text parameters.

The method executes **one request** and returns **one string value (`str`)**.

---

## Method Signature

```python
async def account_info_string(
    property_id: AccountInfoStringPropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> str
```

Key points:

* The method is asynchronous and must be called with `await`
* `property_id` specifies **which string property** to request
* `deadline` and `cancellation_event` control the execution time
* The result is returned as a regular Python string (`str`)

---

## 🧩 Code Example — Verifying Server Connection

```python
async def verify_server_connection(account: MT5Account, expected_server: str) -> bool:
    deadline = datetime.utcnow() + timedelta(seconds=3)

    server = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline=deadline
    )

    if server.lower() != expected_server.lower():
        print(f"[WARNING] Connected to {server}, expected {expected_server}")
        return False

    print(f"[OK] Confirmed: Connected to {server}")
    return True
```

In this example, `account_info_string()` is used to retrieve the server name and subsequently verify that the account is connected to the expected trading environment.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Requesting a String Property

```python
server = await account.account_info_string(
    property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
    deadline=deadline
)
```

At this step, a single string property of the account is requested.

* `ACCOUNT_SERVER` specifies **which value to retrieve**
* The method asynchronously awaits the response
* The result is a regular Python string

What does NOT happen here:

* No validation of string content
* No case normalization
* No value interpretation

The method simply returns the text value received from the terminal.

---

### 2️⃣ Working with the Retrieved String

```python
if server.lower() != expected_server.lower():
```

After receiving the value, user application logic begins.

In this example:

* `server` — the actual server name received from the terminal
* `expected_server` — the server name expected by the user or strategy

Both values are converted to lowercase so the comparison is case-insensitive.

---

### 3️⃣ Reacting to Verification Result

```python
print(f"[WARNING] Connected to {server}, expected {expected_server}")
return False
```

If the server doesn't match:

* A warning is printed
* The function returns `False`

This is a deliberate decision in the application code. The `account_info_string()` method itself:

* Does not know which server is considered correct
* Makes no decisions about connection validity

---

```python
print(f"[OK] Confirmed: Connected to {server}")
return True
```

If the server matches:

* A confirmation is printed
* The function returns `True`

---

## Summary

In this example, `account_info_string()` is used as a simple source of string account parameters.

The method returns one string value, while all verification logic and reaction to the result is completely within the calling code.
