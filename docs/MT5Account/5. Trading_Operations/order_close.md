# Close Position or Order

> **Request:** Close a market position or delete a pending order.

**API Information:**

* **Python API:** `MT5Account.order_close(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.TradingHelper`
* **Proto definition:** `OrderClose` (defined in `mt5-term-api-trading-helper.proto`)
* **Enums in this method:** 1 enum with 3 constants (1 output)

### RPC

* **Service:** `mt5_term_api.TradingHelper`
* **Method:** `OrderClose(OrderCloseRequest) -> OrderCloseReply`
* **Low-level client (generated):** `TradingHelperStub.OrderClose(request, metadata)`


## 💬 Just the essentials

* **What it is.** Closes market positions or deletes pending orders.
* **Why you need it.** Exit positions or cancel pending orders.
* **Partial close.** Set volume < position volume to close partially, or 0 to close all.

---

## 🎯 Purpose

Use it to:

* Close market positions completely or partially
* Delete pending orders
* Exit losing positions quickly
* Take profits on winning positions
* Cancel unfilled pending orders


```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


class MT5Account:
    # ...

    async def order_close(
        self,
        request: trading_pb2.OrderCloseRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Closes a market or pending order asynchronously.

        Returns:
            OrderCloseData: The close result and return codes.
        """
```

**Request message:**

```protobuf
OrderCloseRequest {
  uint64 ticket = 1;      // Order/position ticket to close
  double volume = 2;      // Volume to close (0 = close all)
  int32 slippage = 5;     // Max slippage in points
}
```

---

## 🔽 Input

| Parameter            | Type                           | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `request`            | `OrderCloseRequest`            | Close request (see fields above)              |
| `deadline`           | `Optional[datetime]`           | Deadline for the operation (optional)         |
| `cancellation_event` | `Optional[asyncio.Event]`      | Event to cancel the request (optional)        |

---

## ⬆️ Output

Returns `OrderCloseData` object.

**OrderCloseData fields:**

| Field                         | Type      | Description                          |
| ----------------------------- | --------- | ------------------------------------ |
| `returned_code`               | `int32`   | Return code (10009 = success)        |
| `returned_string_code`        | `string`  | String return code                   |
| `returned_code_description`   | `string`  | Description of return code           |
| `close_mode`                  | `int32`   | Close mode used                      |

---

## 🧱 Related enums (from proto)

### `MRPC_ORDER_CLOSE_MODE`

Used in `OrderCloseData` to indicate the close mode.

| Constant Name                      | Value | Description                          |
| ---------------------------------- | ----- | ------------------------------------ |
| `MRPC_MARKET_ORDER_CLOSE`          | 0     | Full position close                  |
| `MRPC_MARKET_ORDER_PARTIAL_CLOSE`  | 1     | Partial position close               |
| `MRPC_PENDING_ORDER_REMOVE`        | 2     | Pending order removal                |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Access enum values
trading_pb2.MRPC_MARKET_ORDER_CLOSE          # = 0
trading_pb2.MRPC_MARKET_ORDER_PARTIAL_CLOSE  # = 1
trading_pb2.MRPC_PENDING_ORDER_REMOVE        # = 2
```

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[OrderClose - How it works](../HOW_IT_WORK/5. Trading_Operations_HOW/order_close_HOW.md)**

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Return code:** Always check `returned_code == 10009` to verify success.
* **Close all:** Set `volume = 0` to close entire position.
* **Partial close:** Set `volume` to specific amount to close partially.
* **Slippage:** Set appropriate slippage for market positions to allow price movement.
* **Pending orders:** Slippage is ignored when closing pending orders.
* **Ticket number:** Get ticket from `opened_orders` or track it when opening positions.
  
---

## 🔗 Usage Examples

### 1) Close entire position

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def close_position():
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
        # Close position with ticket 123456
        request = trading_pb2.OrderCloseRequest(
            ticket=123456,
            volume=0,  # 0 = close all
            slippage=20  # 20 points max slippage
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Position closed!")
            print(f"  Mode: {result.close_mode}")
        else:
            print(f"[FAILED] Code: {result.returned_code}")
            print(f"  Description: {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(close_position())
```

### 2) Close all open positions

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def close_all_positions():
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
        # Get all open positions
        request = account_pb2.OpenedOrdersRequest()
        positions_data = await account.opened_orders(request)

        closed_count = 0
        failed_count = 0

        # Close each position
        for position in positions_data.positions:
            close_req = trading_pb2.OrderCloseRequest(
                ticket=position.ticket,
                volume=0,  # Close all
                slippage=20
            )

            result = await account.order_close(close_req)

            if result.returned_code == 10009:
                closed_count += 1
                print(f"[CLOSED] Position #{position.ticket}")
            else:
                failed_count += 1
                print(f"[FAILED] Position #{position.ticket}: "
                      f"{result.returned_code_description}")

        print(f"\n[SUMMARY] Closed: {closed_count}, Failed: {failed_count}")

    finally:
        await account.channel.close()

asyncio.run(close_all_positions())
```

### 3) Partial position close

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def partial_close():
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
        # Close half of a 0.10 lot position
        request = trading_pb2.OrderCloseRequest(
            ticket=123456,
            volume=0.05,  # Close 0.05 lots
            slippage=20
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Partial close executed!")
            print(f"  Closed volume: 0.05 lots")
            print(f"  Remaining: 0.05 lots")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(partial_close())
```

### 4) Delete pending order

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def delete_pending_order():
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
        # Delete pending order
        request = trading_pb2.OrderCloseRequest(
            ticket=789012,
            volume=0,
            slippage=0  # Slippage not used for pending orders
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Pending order deleted!")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(delete_pending_order())
```

### 5) Close positions by symbol

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def close_by_symbol(symbol: str):
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
        # Get all open positions
        request = account_pb2.OpenedOrdersRequest()
        positions_data = await account.opened_orders(request)

        closed = []
        failed = []

        # Close positions for specific symbol
        for position in positions_data.positions:
            if position.symbol == symbol:
                close_req = trading_pb2.OrderCloseRequest(
                    ticket=position.ticket,
                    volume=0,
                    slippage=20
                )

                result = await account.order_close(close_req)

                if result.returned_code == 10009:
                    closed.append(position.ticket)
                    print(f"[CLOSED] {symbol} position #{position.ticket}")
                else:
                    failed.append(position.ticket)
                    print(f"[FAILED] #{position.ticket}: "
                          f"{result.returned_code_description}")

        print(f"\n[{symbol}] Closed: {len(closed)}, Failed: {len(failed)}")

    finally:
        await account.channel.close()

# Close all EURUSD positions
asyncio.run(close_by_symbol("EURUSD"))
```

### 6) Close with retry and error handling

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def close_with_retry(ticket: int, max_retries=3):
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
        for attempt in range(1, max_retries + 1):
            print(f"[ATTEMPT {attempt}/{max_retries}]")

            request = trading_pb2.OrderCloseRequest(
                ticket=ticket,
                volume=0,
                slippage=30  # Allow higher slippage for retries
            )

            try:
                result = await account.order_close(request)

                if result.returned_code == 10009:
                    print(f"[SUCCESS] Position closed on attempt {attempt}!")
                    return True
                else:
                    print(f"[FAILED] Code: {result.returned_code}")
                    print(f"  Description: {result.returned_code_description}")

                    if attempt < max_retries:
                        print(f"  Retrying in 1 second...")
                        await asyncio.sleep(1)

            except Exception as e:
                print(f"[ERROR] {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1)

        print(f"[GIVING UP] Failed to close position after {max_retries} attempts")
        return False

    finally:
        await account.channel.close()

asyncio.run(close_with_retry(123456))
```

---

## 📚 See also

* [OrderSend](./order_send.md) - Open positions
* [OrderModify](./order_modify.md) - Modify positions/orders
* [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Get open positions
