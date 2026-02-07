# Check Order Validity

> **Request:** Validate if a trade request can be executed under current market conditions.

**API Information:**

* **Python API:** `MT5Account.order_check(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.TradeFunctions`
* **Proto definition:** `OrderCheck` (defined in `mt5-term-api-trade-functions.proto`)
* **Enums in this method:** 4 enums with 23 constants (4 input)

### RPC

* **Service:** `mt5_term_api.TradeFunctions`
* **Method:** `OrderCheck(OrderCheckRequest) -> OrderCheckReply`
* **Low-level client (generated):** `TradeFunctionsStub.OrderCheck(request, metadata)`

---

## 💬 Just the essentials

* **What it is.** Validates trade requests before execution.
* **Why you need it.** Check if account has sufficient margin and validate order parameters.
* **Use before sending.** Always check orders before sending to avoid rejections.

---

## 🎯 Purpose

Use it to:

* Verify sufficient margin before opening positions
* Validate order parameters (price, volume, SL/TP)
* Check broker restrictions
* Calculate margin requirements
* Estimate balance/equity changes
* Prevent rejected orders


```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

class MT5Account:
    # ...

    async def order_check(
        self,
        request: trade_pb2.OrderCheckRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trade_pb2.OrderCheckData:
        """
        Checks whether a trade request can be successfully executed.

        Returns:
            OrderCheckData: Result of the trade request check.
        """
```

**Request message:**

```protobuf
message OrderCheckRequest {
  MrpcMqlTradeRequest mql_trade_request = 1;  // Trade request to validate
}

message MrpcMqlTradeRequest {
  MRPC_ENUM_TRADE_REQUEST_ACTIONS action = 1;  // Trade operation type
  uint64 expert_advisor_magic_number = 2;      // Expert Advisor ID
  uint64 order = 3;                            // Order ticket
  string symbol = 4;                           // Symbol name
  double volume = 5;                           // Volume in lots
  double price = 6;                            // Price
  double stop_limit = 7;                       // Stop limit price
  double stop_loss = 8;                        // Stop loss price
  double take_profit = 9;                      // Take profit price
  uint64 deviation = 10;                       // Maximum deviation from price
  ENUM_ORDER_TYPE_TF order_type = 11;          // Order type
  MRPC_ENUM_ORDER_TYPE_FILLING type_filling = 12;  // Filling mode
  MRPC_ENUM_ORDER_TYPE_TIME type_time = 13;    // Order lifetime
  google.protobuf.Timestamp expiration = 14;   // Expiration time
  string comment = 15;                         // Comment
  uint64 position = 16;                        // Position ticket
  uint64 position_by = 17;                     // Opposite position ticket
}
```

---

## 🔽 Input

| Parameter            | Type                           | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `request`            | `OrderCheckRequest`            | Trade request to validate                     |
| `deadline`           | `Optional[datetime]`           | Deadline for the operation (optional)         |
| `cancellation_event` | `Optional[asyncio.Event]`      | Event to cancel the request (optional)        |

---

## ⬆️ Output

Returns `OrderCheckData` object with validation results.

**OrderCheckData fields:**

| Field                    | Type                          | Description                          |
| ------------------------ | ----------------------------- | ------------------------------------ |
| `mql_trade_check_result` | `MrpcMqlTradeCheckResult`     | Validation result structure          |

**MrpcMqlTradeCheckResult fields:**

| Field                | Type      | Description                          |
| -------------------- | --------- | ------------------------------------ |
| `returned_code`      | `uint32`  | Return code (0 = success)            |
| `balance_after_deal` | `double`  | Balance after order execution        |
| `equity_after_deal`  | `double`  | Equity after order execution         |
| `profit`             | `double`  | Estimated profit/loss                |
| `margin`             | `double`  | Required margin                      |
| `free_margin`        | `double`  | Free margin after order              |
| `margin_level`       | `double`  | Margin level percentage              |
| `comment`            | `string`  | Comment or error description         |

---

## 🧱 Related enums (from proto)

### `MRPC_ENUM_TRADE_REQUEST_ACTIONS`

Used in `MrpcMqlTradeRequest` to specify the type of trade operation.

| Constant Name           | Value | Description                          |
| ----------------------- | ----- | ------------------------------------ |
| `TRADE_ACTION_DEAL`     | 0     | Place market order                   |
| `TRADE_ACTION_PENDING`  | 1     | Place pending order                  |
| `TRADE_ACTION_SLTP`     | 2     | Modify SL/TP                         |
| `TRADE_ACTION_MODIFY`   | 3     | Modify order                         |
| `TRADE_ACTION_REMOVE`   | 4     | Remove order                         |
| `TRADE_ACTION_CLOSE_BY` | 5     | Close by opposite position           |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

# Access enum values
trade_pb2.TRADE_ACTION_DEAL     # = 0
trade_pb2.TRADE_ACTION_PENDING  # = 1
```

### `ENUM_ORDER_TYPE_TF`

Used in `MrpcMqlTradeRequest` to specify order type.

| Constant Name                  | Value | Description                          |
| ------------------------------ | ----- | ------------------------------------ |
| `ORDER_TYPE_TF_BUY`            | 0     | Market buy order                     |
| `ORDER_TYPE_TF_SELL`           | 1     | Market sell order                    |
| `ORDER_TYPE_TF_BUY_LIMIT`      | 2     | Buy limit pending order              |
| `ORDER_TYPE_TF_SELL_LIMIT`     | 3     | Sell limit pending order             |
| `ORDER_TYPE_TF_BUY_STOP`       | 4     | Buy stop pending order               |
| `ORDER_TYPE_TF_SELL_STOP`      | 5     | Sell stop pending order              |
| `ORDER_TYPE_TF_BUY_STOP_LIMIT` | 6     | Buy stop limit pending order         |
| `ORDER_TYPE_TF_SELL_STOP_LIMIT`| 7     | Sell stop limit pending order        |
| `ORDER_TYPE_TF_CLOSE_BY`       | 8     | Close by opposite position           |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

# Access enum values
trade_pb2.ORDER_TYPE_TF_BUY         # = 0
trade_pb2.ORDER_TYPE_TF_SELL        # = 1
trade_pb2.ORDER_TYPE_TF_BUY_LIMIT   # = 2
```

### `MRPC_ENUM_ORDER_TYPE_FILLING`

Used in `MrpcMqlTradeRequest` to specify order filling mode.

| Constant Name           | Value | Description                          |
| ----------------------- | ----- | ------------------------------------ |
| `ORDER_FILLING_FOK`     | 0     | Fill or Kill                         |
| `ORDER_FILLING_IOC`     | 1     | Immediate or Cancel                  |
| `ORDER_FILLING_RETURN`  | 2     | Return order                         |
| `ORDER_FILLING_BOC`     | 3     | Book or Cancel                       |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

# Access enum values
trade_pb2.ORDER_FILLING_FOK     # = 0
trade_pb2.ORDER_FILLING_IOC     # = 1
```

### `MRPC_ENUM_ORDER_TYPE_TIME`

Used in `MrpcMqlTradeRequest` to specify order lifetime.

| Constant Name              | Value | Description                          |
| -------------------------- | ----- | ------------------------------------ |
| `ORDER_TIME_GTC`           | 0     | Good till cancelled                  |
| `ORDER_TIME_DAY`           | 1     | Good till current trading day        |
| `ORDER_TIME_SPECIFIED`     | 2     | Good till specified date             |
| `ORDER_TIME_SPECIFIED_DAY` | 3     | Good till specified day              |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

# Access enum values
trade_pb2.ORDER_TIME_GTC        # = 0
trade_pb2.ORDER_TIME_DAY        # = 1
```

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[OrderCheck - How it works](../HOW_IT_WORK/5. Trading_Operations_HOW/order_check_HOW.md)**

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **No execution:** This method does NOT execute the order, only validates it.
* **Nested structure:** Request uses `OrderCheckRequest` which contains `MrpcMqlTradeRequest`.
* **Margin check:** Returns required margin and free margin after order.
* **Return code:** Check `returned_code` field (0 = success).
* **Best practice:** Always check before sending, especially for large volumes.

---

## 🔗 Usage Examples

### 1) Basic order validation

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def check_order():
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
        # Create order check request
        request = trade_pb2.OrderCheckRequest()
        request.mql_trade_request.action = trade_pb2.TRADE_ACTION_DEAL
        request.mql_trade_request.symbol = "EURUSD"
        request.mql_trade_request.volume = 0.10
        request.mql_trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
        request.mql_trade_request.price = 0.0
        request.mql_trade_request.deviation = 20
        request.mql_trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
        request.mql_trade_request.type_time = trade_pb2.ORDER_TIME_GTC
        request.mql_trade_request.comment = "Check order"

        # Check order validity
        result = await account.order_check(request)

        if result.mql_trade_check_result.returned_code == 0:  # 0 = valid
            print(f"[VALID] Order can be executed!")
            print(f"  Margin required: ${result.mql_trade_check_result.margin:.2f}")
            print(f"  Free margin after: ${result.mql_trade_check_result.free_margin:.2f}")
            print(f"  Balance after: ${result.mql_trade_check_result.balance_after_deal:.2f}")
        else:
            print(f"[INVALID] Order cannot be executed!")
            print(f"  Code: {result.mql_trade_check_result.returned_code}")
            print(f"  Comment: {result.mql_trade_check_result.comment}")

    finally:
        await account.channel.close()

asyncio.run(check_order())
```

### 2) Check and send pattern

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def check_and_send():
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
        # Create order check request
        check_request = trade_pb2.OrderCheckRequest()
        check_request.mql_trade_request.action = trade_pb2.TRADE_ACTION_DEAL
        check_request.mql_trade_request.symbol = "EURUSD"
        check_request.mql_trade_request.volume = 0.05
        check_request.mql_trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
        check_request.mql_trade_request.price = 0.0
        check_request.mql_trade_request.deviation = 20
        check_request.mql_trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
        check_request.mql_trade_request.type_time = trade_pb2.ORDER_TIME_GTC
        check_request.mql_trade_request.comment = "Checked order"

        # First, check the order
        check_result = await account.order_check(check_request)

        if check_result.mql_trade_check_result.returned_code == 0:
            print(f"[CHECK PASSED] Order is valid")
            print(f"  Margin: ${check_result.mql_trade_check_result.margin:.2f}")

            # Now send the order (use same trade request)
            send_request = trade_pb2.OrderSendRequest()
            send_request.mql_trade_request.CopyFrom(check_request.mql_trade_request)
            send_result = await account.order_send(send_request)

            if send_result.mql_trade_result.returned_code == 10009:
                print(f"[SUCCESS] Order executed!")
                print(f"  Deal: #{send_result.mql_trade_result.deal}")
                print(f"  Price: {send_result.mql_trade_result.price}")
            else:
                print(f"[FAILED] {send_result.mql_trade_result.comment}")
        else:
            print(f"[CHECK FAILED] Cannot send order")
            print(f"  Reason: {check_result.mql_trade_check_result.comment}")

    finally:
        await account.channel.close()

asyncio.run(check_and_send())
```

### 3) Check multiple volumes

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def check_multiple_volumes():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    volumes = [0.01, 0.05, 0.10, 0.50, 1.00]

    try:
        print("Checking volumes for EURUSD BUY:")
        print("-" * 60)

        for volume in volumes:
            request = trade_pb2.OrderCheckRequest()
            request.mql_trade_request.action = trade_pb2.TRADE_ACTION_DEAL
            request.mql_trade_request.symbol = "EURUSD"
            request.mql_trade_request.volume = volume
            request.mql_trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
            request.mql_trade_request.price = 0.0
            request.mql_trade_request.deviation = 20
            request.mql_trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
            request.mql_trade_request.type_time = trade_pb2.ORDER_TIME_GTC

            result = await account.order_check(request)

            if result.mql_trade_check_result.returned_code == 0:
                print(f"[OK] {volume:>6.2f} lots - "
                      f"Margin: ${result.mql_trade_check_result.margin:>10,.2f}, "
                      f"Free: ${result.mql_trade_check_result.free_margin:>10,.2f}")
            else:
                print(f"[FAIL] {volume:>6.2f} lots - "
                      f"{result.mql_trade_check_result.comment}")

    finally:
        await account.channel.close()

asyncio.run(check_multiple_volumes())
```

### 4) Find maximum volume

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def find_max_volume():
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
        max_volume = 0.01
        step = 0.01

        # Binary search for maximum volume
        current = 0.01

        while current <= 10.0:  # Max check up to 10 lots
            request = trade_pb2.OrderCheckRequest()
            request.mql_trade_request.action = trade_pb2.TRADE_ACTION_DEAL
            request.mql_trade_request.symbol = "EURUSD"
            request.mql_trade_request.volume = current
            request.mql_trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
            request.mql_trade_request.price = 0.0
            request.mql_trade_request.deviation = 20
            request.mql_trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
            request.mql_trade_request.type_time = trade_pb2.ORDER_TIME_GTC

            result = await account.order_check(request)

            if (result.mql_trade_check_result.returned_code == 0 and
                result.mql_trade_check_result.free_margin > 0):
                max_volume = current
                current += step
            else:
                break

        print(f"[RESULT] Maximum volume: {max_volume:.2f} lots")

    finally:
        await account.channel.close()

asyncio.run(find_max_volume())
```

### 5) Risk calculator

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def calculate_risk_percent(volume: float):
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
        # Get current balance
        summary_req = account_pb2.AccountSummaryRequest()
        summary = await account.account_summary(summary_req)
        current_balance = summary.balance

        # Check order
        request = trade_pb2.OrderCheckRequest()
        request.mql_trade_request.action = trade_pb2.TRADE_ACTION_DEAL
        request.mql_trade_request.symbol = "EURUSD"
        request.mql_trade_request.volume = volume
        request.mql_trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
        request.mql_trade_request.price = 0.0
        request.mql_trade_request.deviation = 20
        request.mql_trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
        request.mql_trade_request.type_time = trade_pb2.ORDER_TIME_GTC

        result = await account.order_check(request)

        if result.mql_trade_check_result.returned_code == 0:
            margin_required = result.mql_trade_check_result.margin
            risk_percent = (margin_required / current_balance) * 100

            print(f"[RISK ANALYSIS]")
            print(f"  Volume: {volume:.2f} lots")
            print(f"  Current balance: ${current_balance:,.2f}")
            print(f"  Margin required: ${margin_required:,.2f}")
            print(f"  Risk: {risk_percent:.2f}% of balance")
            print(f"  Free margin after: ${result.mql_trade_check_result.free_margin:,.2f}")
        else:
            print(f"[ERROR] {result.mql_trade_check_result.comment}")

    finally:
        await account.channel.close()

asyncio.run(calculate_risk_percent(0.10))
```

### 6) Validate order before automated trading

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

class OrderValidator:
    def __init__(self, account):
        self.account = account

    async def validate_and_execute(self, trade_request):
        """Validate order before execution"""

        # Check order
        check_request = trade_pb2.OrderCheckRequest()
        check_request.mql_trade_request.CopyFrom(trade_request)
        check_result = await self.account.order_check(check_request)

        if check_result.mql_trade_check_result.returned_code != 0:
            return {
                'success': False,
                'stage': 'validation',
                'error': check_result.mql_trade_check_result.comment
            }

        # Check free margin threshold (e.g., 30% minimum)
        balance = check_result.mql_trade_check_result.balance_after_deal
        margin_free = check_result.mql_trade_check_result.free_margin

        if margin_free < (balance * 0.30):
            return {
                'success': False,
                'stage': 'margin_check',
                'error': 'Insufficient free margin (< 30%)'
            }

        # Execute order
        send_request = trade_pb2.OrderSendRequest()
        send_request.mql_trade_request.CopyFrom(trade_request)
        send_result = await self.account.order_send(send_request)

        if send_result.mql_trade_result.returned_code == 10009:
            return {
                'success': True,
                'deal': send_result.mql_trade_result.deal,
                'price': send_result.mql_trade_result.price
            }
        else:
            return {
                'success': False,
                'stage': 'execution',
                'error': send_result.mql_trade_result.comment
            }

async def main():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    validator = OrderValidator(account)

    try:
        # Create trade request
        trade_request = trade_pb2.MrpcMqlTradeRequest()
        trade_request.action = trade_pb2.TRADE_ACTION_DEAL
        trade_request.symbol = "EURUSD"
        trade_request.volume = 0.05
        trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
        trade_request.price = 0.0
        trade_request.deviation = 20
        trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
        trade_request.type_time = trade_pb2.ORDER_TIME_GTC

        result = await validator.validate_and_execute(trade_request)

        if result['success']:
            print(f"[SUCCESS] Deal: #{result['deal']}, Price: {result['price']}")
        else:
            print(f"[FAILED] Stage: {result['stage']}, Error: {result['error']}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

---

## 📚 See also

* [OrderSend](./order_send.md) - Send orders after validation
* [OrderCalcMargin](./order_calc_margin.md) - Calculate margin only
* [OrderCalcProfit](./order_calc_profit.md) - Calculate potential profit/loss
* [AccountSummary](../1.%20Account_Information/account_summary.md) - Get account balance/margin
