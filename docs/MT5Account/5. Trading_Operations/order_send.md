# Send Market or Pending Order

> **Request:** Send a market or pending order to the trading server.

**API Information:**

* **Python API:** `MT5Account.order_send(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.TradingHelper`
* **Proto definition:** `OrderSend` (defined in `mt5-term-api-trading-helper.proto`)
* **Enums in this method:** 2 enums with 13 constants (2 input)

### RPC

* **Service:** `mt5_term_api.TradingHelper`
* **Method:** `OrderSend(OrderSendRequest) -> OrderSendReply`
* **Low-level client (generated):** `TradingHelperStub.OrderSend(request, metadata)`

---

## 💬 Just the essentials

* **What it is.** Sends market or pending orders to the MT5 trading server.
* **Why you need it.** Primary method for opening positions and placing pending orders.
* **Success code.** Return code 10009 means success.

---

## 🎯 Purpose

Use it to:

* Open market positions (BUY or SELL)
* Place pending orders (LIMIT, STOP, STOP_LIMIT)
* Set Stop Loss and Take Profit levels
* Specify order expiration
* Add order comments and magic numbers

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[OrderSend - How it works](../HOW_IT_WORK/5. Trading_Operations_HOW/order_send_HOW.md)**

```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

class MT5Account:
    # ...

    async def order_send(
        self,
        request: trading_pb2.OrderSendRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trading_pb2.OrderSendData:
        """
        Sends a market or pending order to the trading server asynchronously.

        Returns:
            OrderSendData: Response with deal/order confirmation data.
        """
```

**Request message:**

```protobuf
message OrderSendRequest {
  string symbol = 1;                             // Trading symbol
  TMT5_ENUM_ORDER_TYPE operation = 2;            // Order type (BUY, SELL, BUY_LIMIT, etc.)
  double volume = 3;                             // Order volume in lots
  double price = 4;                              // Order price (for pending orders)
  uint64 slippage = 5;                           // Max slippage in points
  double stop_loss = 6;                          // Stop loss price (optional)
  double take_profit = 7;                        // Take profit price (optional)
  string comment = 8;                            // Order comment
  uint64 expert_id = 9;                          // Expert Advisor ID (magic number)
  double stop_limit_price = 10;                  // Stop limit price (for STOP_LIMIT orders)
  TMT5_ENUM_ORDER_TYPE_TIME expiration_time_type = 11;  // Expiration type (GTC, DAY, etc.)
  google.protobuf.Timestamp expiration_time = 12;       // Expiration time
}
```

---

## 🔽 Input

| Parameter            | Type                           | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `request`            | `OrderSendRequest`             | Order request (see fields above)              |
| `deadline`           | `Optional[datetime]`           | Deadline for the operation (optional)         |
| `cancellation_event` | `Optional[asyncio.Event]`      | Event to cancel the request (optional)        |

---

## ⬆️ Output

Returns `OrderSendData` object.

**OrderSendData fields:**

| Field                         | Type      | Description                          |
| ----------------------------- | --------- | ------------------------------------ |
| `returned_code`               | `uint32`  | Return code (10009 = success)        |
| `deal`                        | `uint32`  | Deal ticket (for market orders)      |
| `order`                       | `uint32`  | Order ticket (for pending orders)    |
| `volume`                      | `double`  | Executed volume                      |
| `price`                       | `double`  | Execution price                      |
| `bid`                         | `double`  | Current Bid price                    |
| `ask`                         | `double`  | Current Ask price                    |
| `comment`                     | `string`  | Broker comment                       |
| `request_id`                  | `uint32`  | Request ID                           |
| `ret_code_external`           | `uint64`  | External return code                 |
| `returned_string_code`        | `string`  | String return code                   |
| `returned_code_description`   | `string`  | Description of return code           |

---

## 🧱 Related enums (from proto)

### `TMT5_ENUM_ORDER_TYPE`

Used in `OrderSendRequest` to specify order type.

| Constant Name                     | Value | Description                          |
| --------------------------------- | ----- | ------------------------------------ |
| `TMT5_ORDER_TYPE_BUY`             | 0     | Market buy order                     |
| `TMT5_ORDER_TYPE_SELL`            | 1     | Market sell order                    |
| `TMT5_ORDER_TYPE_BUY_LIMIT`       | 2     | Buy limit pending order              |
| `TMT5_ORDER_TYPE_SELL_LIMIT`      | 3     | Sell limit pending order             |
| `TMT5_ORDER_TYPE_BUY_STOP`        | 4     | Buy stop pending order               |
| `TMT5_ORDER_TYPE_SELL_STOP`       | 5     | Sell stop pending order              |
| `TMT5_ORDER_TYPE_BUY_STOP_LIMIT`  | 6     | Buy stop limit pending order         |
| `TMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7     | Sell stop limit pending order        |
| `TMT5_ORDER_TYPE_CLOSE_BY`        | 8     | Close by opposite position           |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Access enum values
trading_pb2.TMT5_ORDER_TYPE_BUY             # = 0
trading_pb2.TMT5_ORDER_TYPE_SELL            # = 1
trading_pb2.TMT5_ORDER_TYPE_BUY_LIMIT       # = 2
trading_pb2.TMT5_ORDER_TYPE_SELL_LIMIT      # = 3
trading_pb2.TMT5_ORDER_TYPE_BUY_STOP        # = 4
trading_pb2.TMT5_ORDER_TYPE_SELL_STOP       # = 5
trading_pb2.TMT5_ORDER_TYPE_BUY_STOP_LIMIT  # = 6
trading_pb2.TMT5_ORDER_TYPE_SELL_STOP_LIMIT # = 7
trading_pb2.TMT5_ORDER_TYPE_CLOSE_BY        # = 8
```

### `TMT5_ENUM_ORDER_TYPE_TIME`

Used in `OrderSendRequest` to specify order lifetime.

| Constant Name                   | Value | Description                          |
| ------------------------------- | ----- | ------------------------------------ |
| `TMT5_ORDER_TIME_GTC`           | 0     | Good till cancelled                  |
| `TMT5_ORDER_TIME_DAY`           | 1     | Good till current trading day        |
| `TMT5_ORDER_TIME_SPECIFIED`     | 2     | Good till specified date             |
| `TMT5_ORDER_TIME_SPECIFIED_DAY` | 3     | Good till specified day              |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Access enum values
trading_pb2.TMT5_ORDER_TIME_GTC            # = 0
trading_pb2.TMT5_ORDER_TIME_DAY            # = 1
trading_pb2.TMT5_ORDER_TIME_SPECIFIED      # = 2
trading_pb2.TMT5_ORDER_TIME_SPECIFIED_DAY  # = 3
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Return code:** Always check `returned_code == 10009` to verify success.
* **Market vs Pending:** Use operation 0 (BUY) or 1 (SELL) for market orders, other codes for pending orders.
* **Slippage:** Set appropriate slippage for market orders to allow price movement.
* **Volume:** Volume is specified in lots (e.g., 0.01 = 1 micro lot).
* **SL/TP:** Can be set during order placement or modified later.
* **Magic number:** Use `expert_id` to identify orders from your EA.
* **Validation:** Use `order_check` before sending to validate the order.

---

## 🔗 Usage Examples

### 1) Send market BUY order

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def market_buy():
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
        # Create market BUY order request
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
            volume=0.01,  # 0.01 lots (1 micro lot)
            price=0,      # 0 for market orders
            slippage=20,  # 20 points max slippage
            stop_loss=0,  # No SL
            take_profit=0,  # No TP
            comment="Market BUY",
            expert_id=12345
        )

        # Send order
        result = await account.order_send(request)

        # Check result
        if result.returned_code == 10009:
            print(f"[SUCCESS] Order executed!")
            print(f"  Deal: #{result.deal}")
            print(f"  Volume: {result.volume}")
            print(f"  Price: {result.price}")
            print(f"  Bid: {result.bid}, Ask: {result.ask}")
        else:
            print(f"[FAILED] Code: {result.returned_code}")
            print(f"  Description: {result.returned_code_description}")
            print(f"  Comment: {result.comment}")

    finally:
        await account.channel.close()

asyncio.run(market_buy())
```

### 2) Send market order with SL/TP

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def market_order_with_sl_tp():
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
        # Get current price first
        import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)

        current_ask = tick_data.tick.ask
        current_bid = tick_data.tick.bid

        # Calculate SL/TP levels (50 pips)
        pip_size = 0.0001
        sl_price = current_ask - (50 * pip_size)  # 50 pips below
        tp_price = current_ask + (50 * pip_size)  # 50 pips above

        # Create BUY order with SL/TP
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
            volume=0.01,
            price=0,
            slippage=20,
            stop_loss=sl_price,
            take_profit=tp_price,
            comment="BUY with SL/TP",
            expert_id=12345
        )

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Order with SL/TP executed!")
            print(f"  Entry: {result.price:.5f}")
            print(f"  SL: {sl_price:.5f}")
            print(f"  TP: {tp_price:.5f}")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(market_order_with_sl_tp())
```

### 3) Place pending BUY LIMIT order

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def buy_limit_order():
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
        # Get current price
        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)

        current_bid = tick_data.tick.bid

        # Place BUY LIMIT 20 pips below current price
        pip_size = 0.0001
        limit_price = current_bid - (20 * pip_size)

        # Create BUY LIMIT order
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY_LIMIT,
            volume=0.01,
            price=limit_price,
            slippage=0,  # Not used for pending orders
            stop_loss=0,
            take_profit=0,
            comment="BUY LIMIT order",
            expert_id=12345
        )

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] BUY LIMIT order placed!")
            print(f"  Order: #{result.order}")
            print(f"  Price: {limit_price:.5f}")
            print(f"  Current: {current_bid:.5f}")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(buy_limit_order())
```

### 4) Place BUY STOP order with expiration

```python
import asyncio
from datetime import datetime, timedelta
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def buy_stop_with_expiration():
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
        # Get current price
        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)

        current_ask = tick_data.tick.ask

        # Place BUY STOP 20 pips above current price
        pip_size = 0.0001
        stop_price = current_ask + (20 * pip_size)

        # Set expiration to 1 hour from now
        from google.protobuf.timestamp_pb2 import Timestamp
        expiration = datetime.now() + timedelta(hours=1)
        expiration_timestamp = Timestamp()
        expiration_timestamp.FromDatetime(expiration)

        # Create BUY STOP order
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY_STOP,
            volume=0.01,
            price=stop_price,
            slippage=0,
            stop_loss=0,
            take_profit=0,
            comment="BUY STOP 1h expiry",
            expert_id=12345,
            expiration_time_type=trading_pb2.TMT5_ORDER_TIME_SPECIFIED
        )
        request.expiration_time.CopyFrom(expiration_timestamp)

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] BUY STOP order placed!")
            print(f"  Order: #{result.order}")
            print(f"  Price: {stop_price:.5f}")
            print(f"  Expires: {expiration.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(buy_stop_with_expiration())
```

### 5) Multiple orders with error handling

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def multiple_orders():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    orders = [
        ("EURUSD", 0.01, "EUR order"),
        ("GBPUSD", 0.01, "GBP order"),
        ("USDJPY", 0.01, "JPY order"),
    ]

    successful = 0
    failed = 0

    try:
        for symbol, volume, comment in orders:
            request = trading_pb2.OrderSendRequest(
                symbol=symbol,
                operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
                volume=volume,
                price=0,
                slippage=20,
                comment=comment,
                expert_id=12345
            )

            try:
                result = await account.order_send(request)

                if result.returned_code == 10009:
                    successful += 1
                    print(f"[OK] {symbol}: Deal #{result.deal} @ {result.price}")
                else:
                    failed += 1
                    print(f"[FAIL] {symbol}: {result.returned_code_description}")

            except Exception as e:
                failed += 1
                print(f"[ERROR] {symbol}: {e}")

        print(f"\n[SUMMARY] Successful: {successful}, Failed: {failed}")

    finally:
        await account.channel.close()

asyncio.run(multiple_orders())
```

### 6) Order with retry logic

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def order_with_retry():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    max_retries = 3
    retry_delay = 1.0  # seconds

    try:
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
            volume=0.01,
            price=0,
            slippage=20,
            comment="Order with retry",
            expert_id=12345
        )

        for attempt in range(1, max_retries + 1):
            print(f"[ATTEMPT {attempt}/{max_retries}]")

            result = await account.order_send(request)

            if result.returned_code == 10009:
                print(f"[SUCCESS] Order executed on attempt {attempt}!")
                print(f"  Deal: #{result.deal}")
                print(f"  Price: {result.price}")
                break
            else:
                print(f"[FAILED] Code: {result.returned_code}")
                print(f"  Description: {result.returned_code_description}")

                if attempt < max_retries:
                    print(f"  Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"  Max retries reached. Giving up.")

    finally:
        await account.channel.close()

asyncio.run(order_with_retry())
```

---

## 📚 See also

* [OrderCheck](./order_check.md) - Validate order before sending
* [OrderModify](./order_modify.md) - Modify existing orders
* [OrderClose](./order_close.md) - Close positions
* [OrderCalcMargin](./order_calc_margin.md) - Calculate required margin
* [OrderCalcProfit](./order_calc_profit.md) - Calculate potential profit/loss
