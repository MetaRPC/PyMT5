# MT5Account - Trading Operations - Overview

> Execute, modify, and manage trades: send orders, close positions, validate requests, calculate margin.

## 📁 What lives here

### Order Execution

* **[order_send](./order_send.md)** - send market or pending orders.
* **[order_close](./order_close.md)** - close positions or delete pending orders.
* **[order_modify](./order_modify.md)** - modify SL/TP, price, or expiration.

### Order Validation & Calculation

* **[order_check](./order_check.md)** - validate orders before execution.
* **[order_calc_margin](./order_calc_margin.md)** - calculate required margin.
* **[order_calc_profit](./order_calc_profit.md)** - calculate potential profit/loss.

---

## 📚 Step-by-step tutorials

**Note:** All trading operations are async methods. Check individual method pages for detailed examples.

* **[order_send](../HOW_IT_WORK/5. Trading_Operations_HOW/order_send_HOW.md)** - Order execution examples
* **[order_close](../HOW_IT_WORK/5. Trading_Operations_HOW/order_close_HOW.md)** - Position closing patterns
* **[order_modify](../HOW_IT_WORK/5. Trading_Operations_HOW/order_modify_HOW.md)** - SL/TP modification examples
* **[order_check](../HOW_IT_WORK/5. Trading_Operations_HOW/order_check_HOW.md)** - Order validation patterns
* **[order_calc_margin](../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_margin_HOW.md)** - Margin calculation examples
* **[order_calc_profit](../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_profit_HOW.md)** - Profit/loss calculation examples

---

## 🧭 Plain English

* **order_send** -> **open positions** or place pending orders (BUY, SELL, LIMIT, STOP).
* **order_close** -> **close positions** completely or partially, or delete pending orders.
* **order_modify** -> **change SL/TP** or modify pending order parameters.
* **order_check** -> **validate orders** before sending (check margin, parameters).
* **order_calc_margin** -> **calculate margin** required for planned trades.
* **order_calc_profit** -> **calculate profit/loss** for planned trades (risk/reward analysis).

> Rule of thumb: **open** -> `order_send`; **close** -> `order_close`; **adjust** -> `order_modify`; **validate** -> `order_check`; **plan margin** -> `order_calc_margin`; **plan profit** -> `order_calc_profit`.

---

## Quick choose

| If you need...                                   | Use                 | Returns                    | Key inputs                          |
| ------------------------------------------------ | ------------------- | -------------------------- | ----------------------------------- |
| Open market position (BUY/SELL)                  | `order_send`        | OrderSendData              | symbol, operation, volume, price    |
| Place pending order (LIMIT/STOP)                 | `order_send`        | OrderSendData              | symbol, operation, volume, price    |
| Close position completely                        | `order_close`       | OrderCloseData             | ticket, volume=0, slippage          |
| Close position partially                         | `order_close`       | OrderCloseData             | ticket, volume, slippage            |
| Delete pending order                             | `order_close`       | OrderCloseData             | ticket, volume=0                    |
| Add/modify Stop Loss or Take Profit              | `order_modify`      | OrderModifyData            | ticket, stop_loss, take_profit      |
| Change pending order price                       | `order_modify`      | OrderModifyData            | ticket, price                       |
| Validate order before sending                    | `order_check`       | OrderCheckData             | OrderSendRequest                    |
| Calculate margin for planned trade               | `order_calc_margin` | OrderCalcMarginData        | symbol, operation, volume           |
| Calculate profit/loss for planned trade          | `order_calc_profit` | OrderCalcProfitData        | symbol, operation, volume, open/close price |

---

## ℹ️ Cross-refs & gotchas

* **Return codes:** Always check `returned_code == 10009` for success (order_send/close), `== 0` for validation methods.
* **Async methods:** All trading operations are async - use `await`.
* **Automatic reconnection:** All methods have built-in reconnection via `execute_with_reconnect`.
* **Volume = 0:** In `order_close`, volume=0 means close entire position.
* **Slippage:** Set appropriate slippage for market orders (e.g., 20 points).
* **SL/TP = 0:** In `order_modify`, use 0 to remove SL or TP.
* **Check before send:** Always use `order_check` before `order_send` for large orders.
* **Margin calculation:** `order_check` includes margin, `order_calc_margin` only calculates margin.
* **Profit calculation:** `order_calc_profit` calculates potential profit/loss for risk/reward analysis.
* **Freeze level:** Cannot modify orders too close to market price (broker setting).
* **Min distance:** Broker enforces minimum distance from current price for SL/TP.

---

## 🟢 Minimal snippets

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Send market BUY order
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
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=0,  # 0 = BUY
            volume=0.01,
            price=0,
            slippage=20,
            comment="Market BUY"
        )

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Deal: #{result.deal}, Price: {result.price}")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(market_buy())
```

```python
# Close position
async def close_position(ticket):
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
        request = trading_pb2.OrderCloseRequest(
            ticket=ticket,
            volume=0,  # Close all
            slippage=20
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Position closed")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(close_position(123456))
```

```python
# Modify Stop Loss
async def modify_sl(ticket, new_sl):
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
        request = trading_pb2.OrderModifyRequest(
            ticket=ticket,
            stop_loss=new_sl,
            take_profit=0,  # Keep existing
            price=0
        )

        result = await account.order_modify(request)
        print(f"[SUCCESS] SL modified to {new_sl}")

    finally:
        await account.channel.close()

asyncio.run(modify_sl(123456, 1.08500))
```

```python
# Check order before sending
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
        import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

        # Create trade request
        trade_request = trade_pb2.MrpcMqlTradeRequest(
            action=0,  # TRADE_ACTION_DEAL
            symbol="EURUSD",
            volume=0.10,
            order_type=0,  # ORDER_TYPE_BUY
            type_filling=2,  # ORDER_FILLING_RETURN
            type_time=0  # ORDER_TIME_GTC
        )

        check_req = trade_pb2.OrderCheckRequest(mql_trade_request=trade_request)

        # Check first
        check_result = await account.order_check(check_req)

        if check_result.returned_code == 0:
            print(f"[VALID] Margin: ${check_result.margin:.2f}")

            # Send order
            send_request = trading_pb2.OrderSendRequest(
                symbol="EURUSD",
                operation=0,
                volume=0.10,
                price=0,
                slippage=20
            )

            send_result = await account.order_send(send_request)

            if send_result.returned_code == 10009:
                print(f"[SUCCESS] Deal: #{send_result.deal}")
        else:
            print(f"[INVALID] {check_result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(check_and_send())
```

```python
# Calculate margin
async def calc_margin():
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
        import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

        request = trade_pb2.OrderCalcMarginRequest(
            symbol="EURUSD",
            order_type=0,  # ORDER_TYPE_BUY
            volume=0.10,
            open_price=1.10000
        )

        result = await account.order_calc_margin(request)

        if result.returned_code == 0:
            print(f"Required margin: ${result.margin:,.2f}")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(calc_margin())
```

```python
# Complete trading workflow
async def trading_workflow():
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
        import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

        # 1. Calculate margin
        margin_req = trade_pb2.OrderCalcMarginRequest(
            symbol="EURUSD",
            order_type=0,
            volume=0.10,
            open_price=1.10000
        )

        margin_result = await account.order_calc_margin(margin_req)
        print(f"[1] Margin: ${margin_result.margin:.2f}")

        # 2. Check order
        trade_request = trade_pb2.MrpcMqlTradeRequest(
            action=0,
            symbol="EURUSD",
            volume=0.10,
            order_type=0,
            type_filling=2,
            type_time=0
        )

        check_req = trade_pb2.OrderCheckRequest(mql_trade_request=trade_request)
        check_result = await account.order_check(check_req)
        if check_result.returned_code != 0:
            print(f"[2] Check failed: {check_result.returned_code_description}")
            return

        print(f"[2] Order valid, free margin after: ${check_result.margin_free:.2f}")

        # 3. Send order
        send_req = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=0,
            volume=0.10,
            price=0,
            slippage=20
        )

        send_result = await account.order_send(send_req)
        if send_result.returned_code != 10009:
            print(f"[3] Send failed: {send_result.returned_code_description}")
            return

        print(f"[3] Order sent! Deal: #{send_result.deal}")
        ticket = send_result.deal

        # 4. Modify to add SL/TP
        await asyncio.sleep(1)  # Wait a moment

        import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick = await account.symbol_info_tick(tick_req)

        pip_size = 0.0001
        sl = tick.tick.bid - (50 * pip_size)
        tp = tick.tick.bid + (100 * pip_size)

        modify_req = trading_pb2.OrderModifyRequest(
            ticket=ticket,
            stop_loss=sl,
            take_profit=tp,
            price=0
        )

        await account.order_modify(modify_req)
        print(f"[4] SL/TP added: SL={sl:.5f}, TP={tp:.5f}")

        # 5. Later... close position
        await asyncio.sleep(5)

        close_req = trading_pb2.OrderCloseRequest(
            ticket=ticket,
            volume=0,
            slippage=20
        )

        close_result = await account.order_close(close_req)
        if close_result.returned_code == 10009:
            print(f"[5] Position closed")

    finally:
        await account.channel.close()

asyncio.run(trading_workflow())
```

```python
# Batch operations
async def batch_operations():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbols = ["EURUSD", "GBPUSD", "USDJPY"]

    try:
        # Open multiple positions
        deals = []

        for symbol in symbols:
            request = trading_pb2.OrderSendRequest(
                symbol=symbol,
                operation=0,
                volume=0.01,
                price=0,
                slippage=20,
                comment=f"{symbol} position"
            )

            result = await account.order_send(request)

            if result.returned_code == 10009:
                deals.append(result.deal)
                print(f"[OPENED] {symbol}: #{result.deal}")

        # Wait...
        await asyncio.sleep(10)

        # Close all positions
        for deal in deals:
            close_req = trading_pb2.OrderCloseRequest(
                ticket=deal,
                volume=0,
                slippage=20
            )

            result = await account.order_close(close_req)

            if result.returned_code == 10009:
                print(f"[CLOSED] #{deal}")

    finally:
        await account.channel.close()

asyncio.run(batch_operations())
```

---

## 📚 See also

* **Positions:** [opened_orders](../3.%20Positions_Orders/opened_orders.md) - get current positions
* **History:** [order_history](../3.%20Positions_Orders/order_history.md) - get order history
* **Account:** [account_summary](../1.%20Account_Information/account_summary.md) - get account state
* **Prices:** [symbol_info_tick](../2.%20Symbol_Information/symbol_info_tick.md) - get current prices
