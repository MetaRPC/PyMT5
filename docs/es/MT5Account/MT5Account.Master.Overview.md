# MT5Account - Master Overview

> One page to **orient fast**: what lives where, how to choose the right API, and jump links to every **overview** and **method spec** in this docs set.

---

## 🚦 Start here - Section Overviews

* **[1. Account Information - Overview](./1.%20Account_Information/Account_Information.Overview.md)**
  Account balance/equity/margin/leverage, complete snapshot or single properties.

* **[2. Symbol Information - Overview](./2.%20Symbol_Information/Symbol_Information.Overview.md)**
  Quotes, symbol properties, trading rules, Market Watch management.

* **[3. Positions & Orders - Overview](./3.%20Positions_Orders/Positions_Orders.Overview.md)**
  Open positions, pending orders, historical deals, order history.

* **[4. Market Depth (DOM) - Overview](./4.%20Market_Depth/Market_Depth.Overview.md)**
  Level II quotes, order book data, market depth subscription.

* **[5. Trading Operations - Overview](./5.%20Trading_Operations/Trading_Operations.Overview.md)**
  Order execution, position management, margin calculations, trade validation.

* **[6. Streaming Methods - Overview](./6.%20Streaming_Methods/Streaming_Methods.Overview.md)**
  Real-time streams: ticks, trades, profit updates, transaction log.

---

## 🧭 How to pick an API

| If you need...                   | Go to...                      | Typical methods                                                              |
| -------------------------------- | ----------------------------- | ---------------------------------------------------------------------------- |
| Account snapshot                 | Account Information           | `account_summary()`, `account_info_double()`, `account_info_integer()`       |
| Quotes & symbol properties       | Symbol Information            | `symbol_info_tick()`, `symbol_info_double()`, `symbols_total()`              |
| Current positions & orders       | Positions & Orders            | `positions_total()`, `opened_orders()`, `opened_orders_tickets()`            |
| Historical trades                | Positions & Orders            | `order_history()`, `positions_history()`                                     |
| Tick values for P/L calculation  | Positions & Orders            | `tick_value_with_size()`                                                     |
| Level II / Order book            | Market Depth (DOM)            | `market_book_add()`, `market_book_get()`, `market_book_release()`            |
| Trading operations               | Trading Operations            | `order_send()`, `order_modify()`, `order_close()`                            |
| Pre-trade calculations           | Trading Operations            | `order_calc_margin()`, `order_check()`                                       |
| Real-time updates                | Streaming Methods             | `on_symbol_tick()`, `on_trade()`, `on_position_profit()`                     |

---

## 🔌  Usage pattern (Python async/await)

Every method follows async pattern with gRPC under the hood:

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def main():
    # Create MT5Account instance using create() - RECOMMENDED
    account = MT5Account.create(
        user=591129415,
        password="IpoHj17tYu67@",
        grpc_server="mt5.mrpc.pro:443"
    )

    # Connect to MT5 terminal
    await account.connect_by_server_name(
        server_name="FxPro-MT5 Demo",
        base_chart_symbol="EURUSD",
        timeout_seconds=120
    )

    try:
        # Call async method - using account_summary() (RECOMMENDED)
        summary = await account.account_summary()
        print(f"Balance: ${summary.account_balance:.2f}")
        print(f"Equity:  ${summary.account_equity:.2f}")

    finally:
        # Always close connection
        await account.channel.close()

asyncio.run(main())
```

---

Every method follows the same shape:

* **Async/Await:** All methods are `async` - use `await` to call them
* **Automatic reconnection:** Built-in `execute_with_reconnect` wrapper for resilience
* **Protobuf messages:** Request/Response use protobuf structures under the hood
* **Return codes:** Trading operations return status codes (10009 = success)
* **Streaming methods:** Use `async for` to consume real-time data streams

**Timestamps:** Unix timestamps (seconds since epoch) or `datetime` objects.

**Streaming methods:** Return async generators - use `async for` loop to receive updates.

---

# 📚 Full Index - All Method Specs

---

## 📄 1. Account Information

* **Overview:** [Account_Information.Overview.md](./1.%20Account_Information/Account_Information.Overview.md)

### Complete Snapshot

* [account_summary.md](./1.%20Account_Information/account_summary.md) - All account info at once (balance, equity, margin, etc.)

### Individual Properties

* [account_info_double.md](./1.%20Account_Information/account_info_double.md) - Single double value (balance, equity, margin, profit, etc.)
* [account_info_integer.md](./1.%20Account_Information/account_info_integer.md) - Single integer value (login, leverage, limit orders, etc.)
* [account_info_string.md](./1.%20Account_Information/account_info_string.md) - Single string value (name, server, currency, company)

---

## 📊 2. Symbol Information

* **Overview:** [Symbol_Information.Overview.md](./2.%20Symbol_Information/Symbol_Information.Overview.md)

### Symbol Management

* [symbols_total.md](./2.%20Symbol_Information/symbols_total.md) - Count of available symbols
* [symbol_exist.md](./2.%20Symbol_Information/symbol_exist.md) - Check if symbol exists on platform
* [symbol_name.md](./2.%20Symbol_Information/symbol_name.md) - Get symbol name by index position
* [symbol_select.md](./2.%20Symbol_Information/symbol_select.md) - Add/remove symbol from Market Watch
* [symbol_is_synchronized.md](./2.%20Symbol_Information/symbol_is_synchronized.md) - Check if symbol data is synchronized

### Symbol Properties

* [symbol_info_double.md](./2.%20Symbol_Information/symbol_info_double.md) - Single double property (BID, ASK, POINT, etc.)
* [symbol_info_integer.md](./2.%20Symbol_Information/symbol_info_integer.md) - Single integer property (DIGITS, SPREAD, etc.)
* [symbol_info_string.md](./2.%20Symbol_Information/symbol_info_string.md) - Single string property (DESCRIPTION, CURRENCY_BASE, etc.)
* [symbol_info_tick.md](./2.%20Symbol_Information/symbol_info_tick.md) - Current tick data (BID, ASK, volume, time)
* [symbol_params_many.md](./2.%20Symbol_Information/symbol_params_many.md) - All symbol parameters at once (RECOMMENDED)

### Trading Conditions

* [symbol_info_margin_rate.md](./2.%20Symbol_Information/symbol_info_margin_rate.md) - Margin rates for symbol and order type
* [symbol_info_session_quote.md](./2.%20Symbol_Information/symbol_info_session_quote.md) - Quote session times for day of week
* [symbol_info_session_trade.md](./2.%20Symbol_Information/symbol_info_session_trade.md) - Trade session times for day of week

---

## 📦 3. Positions & Orders

* **Overview:** [Positions_Orders.Overview.md](./3.%20Positions_Orders/Positions_Orders.Overview.md)

### Current Positions & Orders

* [positions_total.md](./3.%20Positions_Orders/positions_total.md) - Count of open positions (lightweight)
* [opened_orders.md](./3.%20Positions_Orders/opened_orders.md) - Full details of all open orders/positions
* [opened_orders_tickets.md](./3.%20Positions_Orders/opened_orders_tickets.md) - Ticket IDs only (lighter payload)

### Historical Data

* [order_history.md](./3.%20Positions_Orders/order_history.md) - Historical orders/deals within time range
* [positions_history.md](./3.%20Positions_Orders/positions_history.md) - Historical closed positions

### Calculations

* [tick_value_with_size.md](./3.%20Positions_Orders/tick_value_with_size.md) - Tick values and contract sizes for P/L calculation

---

## 📈 4. Market Depth (DOM)

* **Overview:** [Market_Depth.Overview.md](./4.%20Market_Depth/Market_Depth.Overview.md)

### Level II Quotes

* [market_book_add.md](./4.%20Market_Depth/market_book_add.md) - Subscribe to Market Depth for symbol
* [market_book_get.md](./4.%20Market_Depth/market_book_get.md) - Get current order book data
* [market_book_release.md](./4.%20Market_Depth/market_book_release.md) - Unsubscribe from Market Depth

---

## 🛠 5. Trading Operations

* **Overview:** [Trading_Operations.Overview.md](./5.%20Trading_Operations/Trading_Operations.Overview.md)

### Order Execution & Management

* [order_send.md](./5.%20Trading_Operations/order_send.md) - Place market or pending orders
* [order_modify.md](./5.%20Trading_Operations/order_modify.md) - Modify SL/TP or order parameters
* [order_close.md](./5.%20Trading_Operations/order_close.md) - Close positions (full or partial)

### Pre-Trade Calculations

* [order_calc_margin.md](./5.%20Trading_Operations/order_calc_margin.md) - Calculate margin required for trade
* [order_check.md](./5.%20Trading_Operations/order_check.md) - Validate trade request before execution

---

## 📡 6. Streaming Methods

* **Overview:** [Streaming_Methods.Overview.md](./6.%20Streaming_Methods/Streaming_Methods.Overview.md)

### Real-Time Price Updates

* [on_symbol_tick.md](./6.%20Streaming_Methods/on_symbol_tick.md) - Real-time tick stream for symbols

### Trading Events

* [on_trade.md](./6.%20Streaming_Methods/on_trade.md) - Position/order changes (opened, closed, modified)
* [on_trade_transaction.md](./6.%20Streaming_Methods/on_trade_transaction.md) - Detailed transaction log (complete audit trail)

### Position Monitoring

* [on_position_profit.md](./6.%20Streaming_Methods/on_position_profit.md) - Periodic profit/loss updates
* [on_positions_and_pending_orders_tickets.md](./6.%20Streaming_Methods/on_positions_and_pending_orders_tickets.md) - Periodic ticket lists (lightweight)

---

## 🎯 Quick Navigation by Use Case

| I want to...                          | Use this method                                                              |
| ------------------------------------- | ---------------------------------------------------------------------------- |
| **ACCOUNT INFORMATION**               |                                                                              |
| Get complete account snapshot         | [account_summary](./1.%20Account_Information/account_summary.md)             |
| Get account balance                   | [account_info_double](./1.%20Account_Information/account_info_double.md) (BALANCE) |
| Get account equity                    | [account_info_double](./1.%20Account_Information/account_info_double.md) (EQUITY) |
| Get account leverage                  | [account_info_integer](./1.%20Account_Information/account_info_integer.md) (LEVERAGE) |
| Get account currency                  | [account_info_string](./1.%20Account_Information/account_info_string.md) (CURRENCY) |
| **POSITIONS & ORDERS**                |                                                                              |
| Get count of open positions           | [positions_total](./3.%20Positions_Orders/positions_total.md)                |
| Get all open orders/positions         | [opened_orders](./3.%20Positions_Orders/opened_orders.md)                    |
| Get ticket IDs only                   | [opened_orders_tickets](./3.%20Positions_Orders/opened_orders_tickets.md)    |
| Get order history                     | [order_history](./3.%20Positions_Orders/order_history.md)                    |
| Get closed positions history          | [positions_history](./3.%20Positions_Orders/positions_history.md)            |
| Get tick values for P/L calculation   | [tick_value_with_size](./3.%20Positions_Orders/tick_value_with_size.md)      |
| **MARKET DEPTH**                      |                                                                              |
| Subscribe to Level II quotes          | [market_book_add](./4.%20Market_Depth/market_book_add.md)                    |
| Get order book data                   | [market_book_get](./4.%20Market_Depth/market_book_get.md)                    |
| Unsubscribe from Level II             | [market_book_release](./4.%20Market_Depth/market_book_release.md)            |
| **TRADING OPERATIONS**                |                                                                              |
| Open market BUY position              | [order_send](./5.%20Trading_Operations/order_send.md) (operation=0)          |
| Open market SELL position             | [order_send](./5.%20Trading_Operations/order_send.md) (operation=1)          |
| Place BUY LIMIT order                 | [order_send](./5.%20Trading_Operations/order_send.md) (operation=2)          |
| Place SELL LIMIT order                | [order_send](./5.%20Trading_Operations/order_send.md) (operation=3)          |
| Place BUY STOP order                  | [order_send](./5.%20Trading_Operations/order_send.md) (operation=4)          |
| Place SELL STOP order                 | [order_send](./5.%20Trading_Operations/order_send.md) (operation=5)          |
| Modify SL/TP of position              | [order_modify](./5.%20Trading_Operations/order_modify.md)                    |
| Close a position                      | [order_close](./5.%20Trading_Operations/order_close.md)                      |
| Calculate margin before trade         | [order_calc_margin](./5.%20Trading_Operations/order_calc_margin.md)          |
| Validate trade before execution       | [order_check](./5.%20Trading_Operations/order_check.md)                      |
| **REAL-TIME SUBSCRIPTIONS**           |                                                                              |
| Stream live prices                    | [on_symbol_tick](./6.%20Streaming_Methods/on_symbol_tick.md)                 |
| Monitor trade events                  | [on_trade](./6.%20Streaming_Methods/on_trade.md)                             |
| Track profit changes                  | [on_position_profit](./6.%20Streaming_Methods/on_position_profit.md)         |
| Monitor ticket changes                | [on_positions_and_pending_orders_tickets](./6.%20Streaming_Methods/on_positions_and_pending_orders_tickets.md) |
| Detailed transaction log              | [on_trade_transaction](./6.%20Streaming_Methods/on_trade_transaction.md)     |

---

## 💡 Key Concepts

### Return Codes (Trading Operations)

* **10009** = Success / DONE
* **10004** = Requote
* **10006** = Request rejected
* **10013** = Invalid request
* **10014** = Invalid volume
* **10015** = Invalid price
* **10016** = Invalid stops
* **10018** = Market closed
* **10019** = Not enough money
* **10031** = No connection with trade server

Always check `returned_code` field in trading operation results.

---

## Important Notes

* **Check return codes:** Every trading operation returns status code (10009 = success)
* **Validate parameters:** Use `order_check()` before `order_send()`
* **Handle exceptions:** Network/protocol errors can occur
* **Async context:** All methods must be called within async context
* **Stream cleanup:** Cancel streams properly using `cancellation_event`
* **UTC timestamps:** All times are in UTC, not local time
* **Broker limitations:** Not all brokers support all features (DOM, hedging, etc.)
* **Automatic reconnection:** All methods have built-in reconnection logic

---

"Trade safe, code clean, and may your async streams always flow smoothly."
