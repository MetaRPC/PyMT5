## order_check — How it works

---

## 📌 Overview

This example shows how to use the low-level method `order_check()` to **verify trade request executability** before actually sending it to the server.

The method is used at the *pre-trade validation* stage and answers a key question:

> "Will the server accept such a trade right now under current conditions?"

Important: `order_check()` **does not open a trade** and **does not change account state**. It is used exclusively for verification.

---

## Method Signature

```python
async def order_check(
    request: OrderCheckRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> OrderCheckData
```

Key points:

* the method is asynchronous
* accepts an almost complete trade request
* performs server-side validation
* does not create an order and does not reserve funds

---

## 🧩 Code Example — Checking multiple volumes

```python
async def check_multiple_volumes():
    volumes = [0.01, 0.05, 0.10, 0.50, 1.00]

    print("Checking volumes for EURUSD BUY:")
    print("-" * 60)

    for volume in volumes:
        request = OrderCheckRequest()
        request.mql_trade_request.action = TRADE_ACTION_DEAL
        request.mql_trade_request.symbol = "EURUSD"
        request.mql_trade_request.volume = volume
        request.mql_trade_request.order_type = ORDER_TYPE_TF_BUY
        request.mql_trade_request.price = 0.0
        request.mql_trade_request.deviation = 20
        request.mql_trade_request.type_filling = ORDER_FILLING_FOK
        request.mql_trade_request.type_time = ORDER_TIME_GTC

        result = await account.order_check(request)

        if result.mql_trade_check_result.returned_code == 0:
            print(
                f"[OK] {volume:>6.2f} lots - "
                f"Margin: ${result.mql_trade_check_result.margin:>10,.2f}, "
                f"Free: ${result.mql_trade_check_result.free_margin:>10,.2f}"
            )
        else:
            print(
                f"[FAIL] {volume:>6.2f} lots - "
                f"{result.mql_trade_check_result.comment}"
            )
```

---

## 🟢 Detailed Explanation

---

### 1️⃣ Iterating Through Potential Volumes

```python
volumes = [0.01, 0.05, 0.10, 0.50, 1.00]
```

Here user code:

* defines possible position sizes
* does not know in advance which are acceptable
* uses `order_check()` as a verification tool

---

### 2️⃣ Forming Trade Request

```python
request.mql_trade_request.action = TRADE_ACTION_DEAL
request.mql_trade_request.symbol = "EURUSD"
request.mql_trade_request.volume = volume
request.mql_trade_request.order_type = ORDER_TYPE_TF_BUY
```

Important:

* the request structure matches a real order
* all critically important parameters are set
* this is a *planned*, not an actual trade

---

### 3️⃣ Server-Side Order Validation

```python
result = await account.order_check(request)
```

At this stage the server checks:

* parameter correctness
* fund sufficiency
* broker trading restrictions
* current market conditions
* execution possibility (filling, deviation)

No account state changes occur.

---

### 4️⃣ Analyzing Validation Result

```python
result.mql_trade_check_result.returned_code
```

Interpretation:

* `0` — order can be executed
* non-zero value — order will be rejected

Additionally returned:

* calculated margin
* free margin after the trade
* text comment explaining rejection reason

---

### 5️⃣ Identifying Acceptable Volume Range

By iterating through volumes, user code:

* finds the maximum acceptable volume
* sees where rejection begins
* gets the exact reason for the limitation

This is the final stage before actual trading.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`order_check()`**:

* validates trade request on the server
* returns technical validation result
* does not make trading decisions

**User code**:

* forms trade parameters
* iterates through volumes
* interprets the result
* decides whether to send the order

---

## Summary

This example illustrates the last safe step before trading:

> **check executability → analyze result → make decision**

The `order_check()` method is designed for strict pre-trade validation and should be used **before `order_send()`**, especially when dynamically selecting volume and in automated trading.
