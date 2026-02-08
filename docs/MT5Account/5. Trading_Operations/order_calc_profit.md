# Calculate Potential Profit/Loss

> **Request:** Calculate the potential profit or loss for a planned trade operation.

**API Information:**

* **Python API:** `MT5Account.order_calc_profit(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.TradeFunctions`
* **Proto definition:** `OrderCalcProfit` (defined in `mt5-term-api-trade-functions.proto`)
* **Enums in this method:** 1 enum with 9 constants (1 input)

### RPC

* **Service:** `mt5_term_api.TradeFunctions`
* **Method:** `OrderCalcProfit(OrderCalcProfitRequest) -> OrderCalcProfitReply`
* **Low-level client (generated):** `TradeFunctionsStub.OrderCalcProfit(request, metadata)`

---

## 💬 Just the essentials

* **What it is.** Calculates potential profit/loss for a trade without executing it.
* **Why you need it.** Plan trades, calculate risk/reward ratios, position sizing.
* **Account currency.** Returns profit/loss in your account currency (USD, EUR, etc.).

---

## 🎯 Purpose

Use it to:

* Calculate profit/loss before opening a trade
* Determine risk/reward ratio
* Plan exit strategies
* Compare profitability across symbols
* Calculate pip value for different lot sizes
* Portfolio profit/loss projections

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[OrderCalcProfit - How it works](../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_profit_HOW.md)**


```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

class MT5Account:
    # ...

    async def order_calc_profit(
        self,
        request: trade_pb2.OrderCalcProfitRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trade_pb2.OrderCalcProfitData:
        """
        Calculates potential profit/loss for a planned trade operation.

        Returns:
            OrderCalcProfitData: The potential profit/loss in account currency.
        """
```

**Request message:**

```protobuf
message OrderCalcProfitRequest {
  ENUM_ORDER_TYPE_TF order_type = 1;  // Order type
  string symbol = 2;                  // Symbol name
  double volume = 3;                  // Trade volume in lots
  double open_price = 4;              // Entry price
  double close_price = 5;             // Exit price
}
```

---

## 🔽 Input

| Parameter            | Type                           | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `request`            | `OrderCalcProfitRequest`       | Profit calculation request                    |
| `deadline`           | `Optional[datetime]`           | Deadline for the operation (optional)         |
| `cancellation_event` | `Optional[asyncio.Event]`      | Event to cancel the request (optional)        |

**OrderCalcProfitRequest fields:**

| Field         | Type                 | Description                          |
| ------------- | -------------------- | ------------------------------------ |
| `order_type`  | `ENUM_ORDER_TYPE_TF` | Order type (enum)                    |
| `symbol`      | `string`             | Symbol name (e.g., "EURUSD")         |
| `volume`      | `double`             | Trade volume in lots                 |
| `open_price`  | `double`             | Entry price                          |
| `close_price` | `double`             | Exit price                           |

---

## ⬆️ Output

Returns `OrderCalcProfitData` object.

**OrderCalcProfitData fields:**

| Field    | Type     | Description                                   |
| -------- | -------- | --------------------------------------------- |
| `profit` | `double` | Profit/loss in account currency (negative = loss) |

---

## 🧱 Related enums (from proto)

### `ENUM_ORDER_TYPE_TF`

Used in `OrderCalcProfitRequest` to specify order type.

| Constant Name            | Value | Description                          |
| ------------------------ | ----- | ------------------------------------ |
| `ORDER_TYPE_BUY`         | 0     | Market buy order                     |
| `ORDER_TYPE_SELL`        | 1     | Market sell order                    |
| `ORDER_TYPE_BUY_LIMIT`   | 2     | Buy limit pending order              |
| `ORDER_TYPE_SELL_LIMIT`  | 3     | Sell limit pending order             |
| `ORDER_TYPE_BUY_STOP`    | 4     | Buy stop pending order               |
| `ORDER_TYPE_SELL_STOP`   | 5     | Sell stop pending order              |
| `ORDER_TYPE_BUY_STOP_LIMIT`  | 6 | Buy stop limit pending order         |
| `ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Sell stop limit pending order        |
| `ORDER_TYPE_CLOSE_BY`    | 8     | Close by opposite position           |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

# Access enum values
trade_pb2.ORDER_TYPE_BUY          # = 0
trade_pb2.ORDER_TYPE_SELL         # = 1
trade_pb2.ORDER_TYPE_BUY_LIMIT    # = 2
trade_pb2.ORDER_TYPE_SELL_LIMIT   # = 3
```

---


## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Return code:** Check `returned_code == 0` for success (validation methods use 0, not 10009).
* **Positive/Negative:** Positive profit = gain, negative profit = loss.
* **Account currency:** Result is always in account currency (USD, EUR, etc.).
* **Spread not included:** This calculates theoretical profit - actual profit may differ due to spread and commissions.
* **Use for planning:** Great for calculating risk/reward before entering trades.
* **Pip value:** Use to calculate how much 1 pip is worth for your lot size.

---

## 🔗 Usage Examples

### 1) Calculate profit for a BUY trade

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_buy_profit():
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
        # Calculate profit for BUY 0.10 lots EURUSD
        # Entry: 1.10000, Exit: 1.10100 (100 pips profit)
        request = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=1.10000,
            close_price=1.10100
        )

        result = await account.order_calc_profit(request)

        print(f"[PROFIT CALCULATION]")
        print(f"  Entry: 1.10000")
        print(f"  Exit: 1.10100")
        print(f"  Volume: 0.10 lots")
        print(f"  Profit: ${result.profit:.2f}")

    finally:
        await account.channel.close()

asyncio.run(calc_buy_profit())
```

### 2) Calculate loss for a SELL trade

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_sell_loss():
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
        # Calculate loss for SELL 0.01 lots EURUSD
        # Entry: 1.10000, Exit: 1.10050 (50 pips loss)
        request = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_SELL,
            symbol="EURUSD",
            volume=0.01,
            open_price=1.10000,
            close_price=1.10050  # Price went against us
        )

        result = await account.order_calc_profit(request)

        print(f"[LOSS CALCULATION]")
        print(f"  Entry: 1.10000")
        print(f"  Exit: 1.10050")
        print(f"  Volume: 0.01 lots")
        print(f"  Loss: ${result.profit:.2f}")  # Will be negative

    finally:
        await account.channel.close()

asyncio.run(calc_sell_loss())
```

### 3) Calculate risk/reward ratio

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

### 4) Calculate pip value

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_pip_value():
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
        # Calculate value of 1 pip for 0.10 lots EURUSD
        pip_size = 0.0001

        request = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=1.10000,
            close_price=1.10000 + pip_size  # 1 pip movement
        )

        result = await account.order_calc_profit(request)

        print(f"[PIP VALUE CALCULATION]")
        print(f"  Symbol: EURUSD")
        print(f"  Volume: 0.10 lots")
        print(f"  1 pip = ${result.profit:.2f}")

    finally:
        await account.channel.close()

asyncio.run(calc_pip_value())
```

### 5) Compare profitability across symbols

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def compare_symbols():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbols = [
        ("EURUSD", 1.10000, 1.10100),
        ("GBPUSD", 1.30000, 1.30100),
        ("USDJPY", 150.000, 150.100),
    ]

    try:
        print("[PROFITABILITY COMPARISON]")
        print("Same pip movement (100 pips), same lot size (0.10)")
        print()

        for symbol, entry, exit in symbols:
            request = trade_pb2.OrderCalcProfitRequest(
                order_type=trade_pb2.ORDER_TYPE_BUY,
                symbol=symbol,
                volume=0.10,
                open_price=entry,
                close_price=exit
            )

            result = await account.order_calc_profit(request)

            print(f"{symbol}: ${result.profit:.2f}")

    finally:
        await account.channel.close()

asyncio.run(compare_symbols())
```

### 6) Position sizing based on risk

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_position_size():
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
        max_risk = 100.00  # Maximum $100 risk
        entry = 1.10000
        stop_loss = 1.09950  # 50 pips SL

        # Test different lot sizes to find appropriate size
        for volume in [0.01, 0.05, 0.10, 0.20]:
            request = trade_pb2.OrderCalcProfitRequest(
                order_type=trade_pb2.ORDER_TYPE_BUY,
                symbol="EURUSD",
                volume=volume,
                open_price=entry,
                close_price=stop_loss
            )

            result = await account.order_calc_profit(request)
            risk = abs(result.profit)

            print(f"Volume: {volume} lots -> Risk: ${risk:.2f}")

            if risk <= max_risk:
                recommended_size = volume
            else:
                break

        print(f"\n[RECOMMENDATION] Use {recommended_size} lots for max ${max_risk} risk")

    finally:
        await account.channel.close()

asyncio.run(calc_position_size())
```

---

## 📚 See also

* [OrderCalcMargin](./order_calc_margin.md) - Calculate required margin
* [OrderCheck](./order_check.md) - Validate order before sending
* [OrderSend](./order_send.md) - Send market or pending orders
* [SymbolInfoTick](../2.%20Symbol_Information/symbol_info_tick.md) - Get current prices
