## order_close — How it works

---

## 📌 Overview

This example shows how to use the low-level method `order_close()` for **actually closing an already open trading position**.

Unlike calculation and validation methods, `order_close()` initiates an **actual trading operation** that:

* changes account state
* closes the position
* locks in the financial result

The method is used when a position already exists and its `ticket` is known.

---

## Method Signature

```python
async def order_close(
    request: OrderCloseRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> OrderCloseData
```

Key points:

* the method is asynchronous
* executes a trading operation
* works with a specific ticket
* returns the execution result

---

## 🧩 Code Example — Closing entire position

```python
request = OrderCloseRequest(
    ticket=123456,
    volume=0,        # 0 = close position completely
    slippage=20      # maximum acceptable slippage
)

result = await account.order_close(request)

if result.returned_code == 10009:
    print("[SUCCESS] Position closed")
else:
    print(f"[FAILED] Code: {result.returned_code}")
    print(f"Description: {result.returned_code_description}")
```

---

## 🟢 Detailed Explanation

---

### 1️⃣ Specifying Position Ticket

```python
ticket=123456
```

The ticket uniquely identifies the position:

* the method does not search for the position automatically
* does not check its existence beforehand
* responsibility for ticket correctness lies with the user

If the ticket is incorrect — the server will return an error.

---

### 2️⃣ Full Position Close via `volume = 0`

```python
volume=0
```

Parameter feature:

* `0` means **close position completely**
* the server determines the current position volume itself
* no need to know the actual size

If you specify `volume > 0`, a **partial close** will be executed.

---

### 3️⃣ Slippage Control

```python
slippage=20
```

This parameter sets:

* maximum acceptable price deviation
* protection against unfavorable execution
* trading constraint, not API logic

If the price moved beyond the acceptable range — the close may be rejected.

---

### 4️⃣ Executing Trading Operation

```python
result = await account.order_close(request)
```

At this stage:

* a trading command is sent to the server
* an attempt to close the position at market occurs
* account state may change

This is an **unsafe operation** in the sense that it affects the trading result.

---

### 5️⃣ Checking Execution Result

```python
result.returned_code
```

The return code determines the operation outcome:

* `10009` — successful execution
* any other value — rejection

Additionally, a text description of the rejection reason is returned.

Checking the result is a mandatory part of correct method usage.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`order_close()`**:

* sends the position close command
* attempts to execute it on the server
* returns the technical result

**User code**:

* selects the position to close
* determines the close volume
* sets acceptable slippage
* analyzes the result
* makes further decisions

---

## Summary

The `order_close()` method is used for **explicit and controlled position closing**.

Correct usage pattern:

> **form request → send → check result → act further**

This is a basic building block for automated trading systems, risk management, and market exit strategies.
