## order_calc_profit — How it works

---

## 📌 Overview

This example shows how to use the low-level method `order_calc_profit()` to **calculate potential profit or loss before executing a trade**.

Important: in this example **no trading operation is performed**. The method is used exclusively for calculation — as a calculator, not as an action.

The main task of the example:

> calculate risk/reward ratio to assess trade viability before opening a position.

---

## Method Signature

```python
async def order_calc_profit(
    request: OrderCalcProfitRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> OrderCalcProfitData
```

Key points:

* the method is asynchronous
* does not open trades
* does not reserve funds
* does not change account state
* returns only the calculated profit/loss value

---

## 🧩 Code Example — Risk/Reward calculation

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_risk_reward():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        entry = 1.10000
        stop_loss = 1.09950  # 50 pips SL
        take_profit = 1.10100  # 100 pips TP

        # Calculate potential loss (hitting SL)
        loss_req = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=entry,
            close_price=stop_loss
        )

        loss_result = await account.order_calc_profit(loss_req)
        risk = abs(loss_result.profit)

        # Calculate potential profit (hitting TP)
        profit_req = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=entry,
            close_price=take_profit
        )

        profit_result = await account.order_calc_profit(profit_req)
        reward = profit_result.profit

        rr_ratio = reward / risk

        print(f"[RISK/REWARD ANALYSIS]")
        print(f"  Entry: {entry}")
        print(f"  SL: {stop_loss} (Risk: ${risk:.2f})")
        print(f"  TP: {take_profit} (Reward: ${reward:.2f})")
        print(f"  R:R Ratio: 1:{rr_ratio:.2f}")

    finally:
        await account.channel.close()

asyncio.run(calc_risk_reward())
```

---

## 🟢 Detailed Explanation

---

### 1️⃣ Connection and Setup

```python
account = MT5Account(
    user=12345,
    password="password",
    grpc_server="mt5.mrpc.pro:443"
)

await account.connect_by_server_name(
    server_name="YourBroker-Demo",
    base_chart_symbol="EURUSD"
)
```

At this step:

* MT5Account instance is created with connection credentials
* connection to MetaTrader 5 terminal is established via gRPC
* base chart symbol is specified for initialization

This is standard connection procedure required before any operations.

---

### 2️⃣ Defining Trade Parameters

```python
entry = 1.10000
stop_loss = 1.09950  # 50 pips SL
take_profit = 1.10100  # 100 pips TP
```

Here:

* entry price is defined (planned opening price)
* stop loss level is set 50 pips below entry
* take profit level is set 100 pips above entry

These are **hypothetical values** for planning purposes. No trade is opened yet.

---

### 3️⃣ Calculating Potential Loss (Risk)

```python
loss_req = trade_pb2.OrderCalcProfitRequest(
    order_type=trade_pb2.ORDER_TYPE_BUY,
    symbol="EURUSD",
    volume=0.10,
    open_price=entry,
    close_price=stop_loss
)

loss_result = await account.order_calc_profit(loss_req)
risk = abs(loss_result.profit)
```

Important to understand:

* the trade **is not opened**
* we calculate what would happen if stop loss is hit
* `open_price=entry` and `close_price=stop_loss` simulate worst-case scenario
* `abs()` is used because loss returns negative value

The request describes a *planned*, not a real operation.

---

### 4️⃣ Calculating Potential Profit (Reward)

```python
profit_req = trade_pb2.OrderCalcProfitRequest(
    order_type=trade_pb2.ORDER_TYPE_BUY,
    symbol="EURUSD",
    volume=0.10,
    open_price=entry,
    close_price=take_profit
)

profit_result = await account.order_calc_profit(profit_req)
reward = profit_result.profit
```

At this step:

* the server calculates profit if take profit is hit
* same trade parameters (symbol, volume, order type)
* only `close_price` differs — now it's the take profit level
* result is positive value representing potential gain

No account state is changed in the process.

---

### 5️⃣ Calculating Risk/Reward Ratio

```python
rr_ratio = reward / risk
```

Here user code:

* divides potential reward by potential risk
* produces the Risk/Reward ratio
* example: if reward=$100 and risk=$50, R:R = 2.0 (or 1:2)

The API does not participate in this step — it's pure business logic.

---

### 6️⃣ Displaying Results

```python
print(f"[RISK/REWARD ANALYSIS]")
print(f"  Entry: {entry}")
print(f"  SL: {stop_loss} (Risk: ${risk:.2f})")
print(f"  TP: {take_profit} (Reward: ${reward:.2f})")
print(f"  R:R Ratio: 1:{rr_ratio:.2f}")
```

Output example:

```
[RISK/REWARD ANALYSIS]
  Entry: 1.1
  SL: 1.0995 (Risk: $50.00)
  TP: 1.101 (Reward: $100.00)
  R:R Ratio: 1:2.00
```

This shows the trader that for every $1 risked, they could gain $2 — a favorable 1:2 risk/reward ratio.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`order_calc_profit()`**:

* performs server-side profit calculation
* takes into account symbol properties, lot size, and price movement
* opens nothing
* does not affect the account

**User code**:

* defines entry, stop loss, and take profit levels
* makes two calculations (risk and reward)
* interprets the result
* makes trading decisions based on R:R ratio

---

## Summary

This example illustrates a professional trading pattern:

> **plan trade → calculate risk → calculate reward → assess ratio → make decision**

The `order_calc_profit()` method is intended precisely for the planning stage and should be used **before opening a trade**, not after.

It allows making informed decisions without risking account state.

**Typical use cases:**

* Calculate risk/reward ratio before entering trade
* Determine if trade setup meets your trading rules (e.g., minimum 1:2 R:R)
* Calculate pip value for different lot sizes
* Compare profitability across different symbols
* Plan exit strategies based on expected profit/loss
