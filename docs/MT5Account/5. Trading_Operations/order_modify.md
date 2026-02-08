# Modify Order or Position

> **Request:** Modify Stop Loss, Take Profit, price, or expiration of an order/position.

**API Information:**

* **Python API:** `MT5Account.order_modify(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.TradingHelper`
* **Proto definition:** `OrderModify` (defined in `mt5-term-api-trading-helper.proto`)
* **Enums in this method:** 1 enum with 4 constants (1 input)

### RPC

* **Service:** `mt5_term_api.TradingHelper`
* **Method:** `OrderModify(OrderModifyRequest) -> OrderModifyReply`
* **Low-level client (generated):** `TradingHelperStub.OrderModify(request, metadata)`


## 💬 Just the essentials

* **What it is.** Modifies SL/TP, price, or expiration of existing orders/positions.
* **Why you need it.** Adjust risk management levels or pending order parameters.
* **Set to zero.** Use 0 to remove SL or TP.

---

## 🎯 Purpose

Use it to:

* Add or modify Stop Loss levels
* Add or modify Take Profit levels
* Change pending order prices
* Update order expiration times
* Adjust trailing stops
* Remove SL/TP (set to 0)


```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

class MT5Account:
    # ...

    async def order_modify(
        self,
        request: trading_pb2.OrderModifyRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Modifies an existing order or position asynchronously.

        Returns:
            OrderModifyData: Response containing updated order/deal info.
        """
```

**Request message:**

```protobuf
OrderModifyRequest {
  uint64 ticket = 1;                             // Order/position ticket to modify
  double stop_loss = 2;                          // New Stop Loss price (0 = remove)
  double take_profit = 3;                        // New Take Profit price (0 = remove)
  double price = 4;                              // New price (for pending orders)
  TMT5_ENUM_ORDER_TYPE_TIME expiration_time_type = 5;  // New expiration type
  google.protobuf.Timestamp expiration_time = 6;       // New expiration time
  double stop_limit = 8;                         // New stop limit price
}
```

---

## 🔽 Input

| Parameter            | Type                           | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `request`            | `OrderModifyRequest`           | Modification request (see fields above)       |
| `deadline`           | `Optional[datetime]`           | Deadline for the operation (optional)         |
| `cancellation_event` | `Optional[asyncio.Event]`      | Event to cancel the request (optional)        |

---

## ⬆️ Output

Returns `OrderModifyData` object.

**OrderModifyData fields:**

| Field                         | Type      | Description                          |
| ----------------------------- | --------- | ------------------------------------ |
| `returned_code`               | `int32`   | Return code (10009 = success)        |
| `returned_string_code`        | `string`  | String return code                   |
| `returned_code_description`   | `string`  | Description of return code           |
| `deal`                        | `uint64`  | Deal ticket (if executed)            |
| `order`                       | `uint64`  | Order ticket                         |
| `volume`                      | `double`  | Volume                               |
| `price`                       | `double`  | Execution price                      |
| `bid`                         | `double`  | Current bid price                    |
| `ask`                         | `double`  | Current ask price                    |
| `comment`                     | `string`  | Broker comment                       |
| `request_id`                  | `uint64`  | Request ID                           |
| `ret_code_external`           | `uint32`  | External return code                 |

---

## 🧱 Related enums (from proto)

### `TMT5_ENUM_ORDER_TYPE_TIME`

Used in `OrderModifyRequest` to specify expiration time type.

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


## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[OrderModify - How it works](../HOW_IT_WORK/5. Trading_Operations_HOW/order_modify_HOW.md)**

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Zero to remove:** Set `stop_loss=0` or `take_profit=0` to remove them.
* **Pending orders:** Can modify price and expiration of pending orders.
* **Market positions:** Can only modify SL/TP for market positions.
* **Min distance:** Broker enforces minimum distance from current price for SL/TP.
* **Freeze level:** Cannot modify orders too close to market price (broker setting).

---

## 🔗 Usage Examples

### 1) Add Stop Loss to position

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def add_stop_loss():
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

        # Set SL 50 pips below current price
        pip_size = 0.0001
        sl_price = current_bid - (50 * pip_size)

        # Modify position to add SL
        request = trading_pb2.OrderModifyRequest(
            ticket=123456,
            stop_loss=sl_price,
            take_profit=0,  # Keep existing TP or no TP
            price=0         # Not used for market positions
        )

        result = await account.order_modify(request)
        print(f"[SUCCESS] Stop Loss added at {sl_price:.5f}")

    finally:
        await account.channel.close()

asyncio.run(add_stop_loss())
```

### 2) Modify both SL and TP

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def modify_sl_tp():
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

        pip_size = 0.0001
        new_sl = current_bid - (30 * pip_size)  # 30 pips SL
        new_tp = current_bid + (60 * pip_size)  # 60 pips TP (2:1 R:R)

        request = trading_pb2.OrderModifyRequest(
            ticket=123456,
            stop_loss=new_sl,
            take_profit=new_tp,
            price=0
        )

        result = await account.order_modify(request)
        print(f"[SUCCESS] Modified SL/TP!")
        print(f"  New SL: {new_sl:.5f}")
        print(f"  New TP: {new_tp:.5f}")

    finally:
        await account.channel.close()

asyncio.run(modify_sl_tp())
```

### 3) Remove Stop Loss

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def remove_stop_loss():
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
        # Set SL to 0 to remove it
        request = trading_pb2.OrderModifyRequest(
            ticket=123456,
            stop_loss=0,     # Remove SL
            take_profit=0,   # Keep existing TP
            price=0
        )

        result = await account.order_modify(request)
        print(f"[SUCCESS] Stop Loss removed!")

    finally:
        await account.channel.close()

asyncio.run(remove_stop_loss())
```

### 4) Modify pending order price

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def modify_pending_order_price():
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

        # New BUY LIMIT price (15 pips below current)
        pip_size = 0.0001
        new_price = current_bid - (15 * pip_size)

        request = trading_pb2.OrderModifyRequest(
            ticket=789012,  # Pending order ticket
            stop_loss=0,
            take_profit=0,
            price=new_price  # New entry price
        )

        result = await account.order_modify(request)
        print(f"[SUCCESS] Pending order price updated to {new_price:.5f}")

    finally:
        await account.channel.close()

asyncio.run(modify_pending_order_price())
```

### 5) Trailing stop implementation

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def trailing_stop(ticket: int, trail_distance_pips: int):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    pip_size = 0.0001
    last_sl = None

    try:
        while True:
            # Get current price
            tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
            tick_data = await account.symbol_info_tick(tick_req)
            current_bid = tick_data.tick.bid

            # Calculate new SL
            new_sl = current_bid - (trail_distance_pips * pip_size)

            # Only update if new SL is higher (for BUY)
            if last_sl is None or new_sl > last_sl:
                request = trading_pb2.OrderModifyRequest(
                    ticket=ticket,
                    stop_loss=new_sl,
                    take_profit=0,
                    price=0
                )

                result = await account.order_modify(request)
                print(f"[TRAIL] SL updated to {new_sl:.5f}")
                last_sl = new_sl

            await asyncio.sleep(1)  # Check every second

    except KeyboardInterrupt:
        print("\nTrailing stop stopped")

    finally:
        await account.channel.close()

# Trail stop 30 pips behind price
asyncio.run(trailing_stop(123456, 30))
```

### 6) Break-even stop loss

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def move_to_breakeven(ticket: int, breakeven_trigger_pips: int):
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
        # Get position details
        positions_req = account_pb2.OpenedOrdersRequest()
        positions_data = await account.opened_orders(positions_req)

        position = next((p for p in positions_data.positions if p.ticket == ticket), None)

        if not position:
            print(f"[ERROR] Position #{ticket} not found")
            return

        entry_price = position.price_open
        pip_size = 0.0001

        # Check if profit reached trigger level
        profit_pips = (position.price_current - entry_price) / pip_size

        if profit_pips >= breakeven_trigger_pips:
            # Move SL to breakeven
            request = trading_pb2.OrderModifyRequest(
                ticket=ticket,
                stop_loss=entry_price,  # Set SL to entry price
                take_profit=0,
                price=0
            )

            result = await account.order_modify(request)
            print(f"[BREAKEVEN] SL moved to entry price {entry_price:.5f}")
            print(f"  Current profit: {profit_pips:.1f} pips")
        else:
            print(f"[WAITING] Profit {profit_pips:.1f} pips < trigger {breakeven_trigger_pips} pips")

    finally:
        await account.channel.close()

# Move to breakeven when profit reaches 20 pips
asyncio.run(move_to_breakeven(123456, 20))
```

---

## 📚 See also

* [OrderSend](./order_send.md) - Open positions
* [OrderClose](./order_close.md) - Close positions
* [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Get position details
