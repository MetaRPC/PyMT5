## order_send — How it works

---

## 📌 Overview

This example shows how to use the low-level method `order_send()` for **actually sending a trading order** to the server with result handling and retry logic.

The `order_send()` method is the key point of the entire trading chain:

* calculations and checks are performed before it
* account state may change after it

This is where the trading decision turns into action.

---

## Method Signature

```python
async def order_send(
    request: OrderSendRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> OrderSendData
```

Key points:

* the method is asynchronous
* executes a real trading operation
* sends order to the server
* returns the execution result

---

## 🧩 Code Example — Order with retry logic

```python
request = OrderSendRequest(
    symbol="EURUSD",
    operation=ORDER_TYPE_BUY,
    volume=0.01,
    price=0,
    slippage=20,
    comment="Order with retry",
    expert_id=12345
)

max_retries = 3
retry_delay = 1.0

for attempt in range(1, max_retries + 1):
    print(f"[ATTEMPT {attempt}/{max_retries}]")

    result = await account.order_send(request)

    if result.returned_code == 10009:
        print(f"[SUCCESS] Order executed on attempt {attempt}")
        print(f"Deal: #{result.deal}, Price: {result.price}")
        break
    else:
        print(f"[FAILED] Code: {result.returned_code}")
        print(f"Reason: {result.returned_code_description}")

        if attempt < max_retries:
            await asyncio.sleep(retry_delay)
```

---

## 🟢 Detailed Explanation

---

### 1️⃣ Forming Trading Request

```python
request = OrderSendRequest(...)
```

At this stage:

* a complete trading order is formed
* all required parameters are specified
* the request fully describes the future trade

This is the same object used in actual trading.

---

### 2️⃣ Sending Order to Server

```python
result = await account.order_send(request)
```

On each call:

* the request is sent to the trading server
* the server attempts to execute the order
* the execution result is returned

Important: absence of exception **does not mean success**.

---

### 3️⃣ Checking Execution Result

```python
result.returned_code
```

The return code determines the operation outcome:

* `10009` — order successfully executed
* any other value — rejection

Additionally, the server returns:

* deal number (`deal`)
* execution price (`price`)
* text description of rejection reason

---

### 4️⃣ Retry Logic

```python
for attempt in range(...)
```

Retry logic is implemented **entirely in user code**:

* the API does not retry automatically
* the user decides how many times to try
* a pause is maintained between attempts

This allows adaptation to changing market conditions.

---

### 5️⃣ Loop Completion

The loop terminates:

* on successful order execution
* or after exhausting all attempts

In both cases, user code knows exactly the operation outcome.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`order_send()`**:

* sends the trading order
* attempts to execute it on the server
* returns the technical result
* does not guarantee success
* does not retry attempts

**User code**:

* forms the trading decision
* defines retry strategy
* analyzes the result
* manages the risk of repeated submissions

---

## Summary

The `order_send()` method is the final step of the trading chain:

> **calculation → validation → sending → result**

Correct usage always implies:

* checking `returned_code`
* handling rejections
* conscious management of retry attempts

This approach makes trading systems robust and predictable in real market conditions.
