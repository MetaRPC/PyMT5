# Stream Trade Transaction Events

> **Request:** subscribe to real-time trade transaction events (detailed audit trail).

**API Information:**

* **Python API:** `MT5Account.on_trade_transaction(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.SubscriptionService`
* **Proto definition:** `OnTradeTransaction` (defined in `mt5-term-api-subscriptions.proto`)

### RPC

* **Service:** `mt5_term_api.SubscriptionService`
* **Method:** `OnTradeTransaction(OnTradeTransactionRequest) -> stream OnTradeTransactionReply`
* **Low-level client (generated):** `SubscriptionServiceStub.OnTradeTransaction(request, metadata)`

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def on_trade_transaction(
        self,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to real-time trade transaction events.

        Yields:
            OnTradeTransactionData: Trade transaction data.
        """
```

**Request message:**

```protobuf
message OnTradeTransactionRequest {
  // No parameters - subscribes to all trade transactions
}
```

## 💬 Just the essentials

* **What it is.** Real-time stream of detailed trade transaction events (most comprehensive).
* **Why you need it.** Complete audit trail, detailed transaction logging, trade verification.
* **Event-driven.** Updates triggered immediately on every transaction event.

---

## 🎯 Purpose

Use it to:

* Build complete trade audit logs
* Track detailed transaction lifecycle
* Monitor order state changes in detail
* Verify trade execution
* Debug trading operations
* Implement transaction-based logic
* Create detailed trade journals

---

## 🔽 Input

| Parameter            | Type                           | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `cancellation_event` | `Optional[asyncio.Event]`      | Event to cancel streaming (optional)          |

---

## ⬆️ Output - Async Generator

Returns an async generator that yields `OnTradeTransactionData` objects.

**OnTradeTransactionData fields:**

| Field                         | Type                      | Description                          |
| ----------------------------- | ------------------------- | ------------------------------------ |
| `type`                        | `int`                     | Transaction type                     |
| `trade_transaction`           | `MqlTradeTransaction`     | Detailed transaction information     |
| `trade_request`               | `MqlTradeRequest`         | Original trade request               |
| `trade_result`                | `MqlTradeResult`          | Trade execution result               |
| `account_info`                | `OnEventAccountInfo`      | Current account state                |
| `terminal_instance_guid_id`   | `str`                     | Terminal instance identifier         |

**Order type enum (SUB_ENUM_ORDER_TYPE):**

| Name                              | Value | Description                          |
| --------------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_TYPE_BUY`              | 0     | Market buy order                     |
| `SUB_ORDER_TYPE_SELL`             | 1     | Market sell order                    |
| `SUB_ORDER_TYPE_BUY_LIMIT`        | 2     | Buy limit pending order              |
| `SUB_ORDER_TYPE_SELL_LIMIT`       | 3     | Sell limit pending order             |
| `SUB_ORDER_TYPE_BUY_STOP`         | 4     | Buy stop pending order               |
| `SUB_ORDER_TYPE_SELL_STOP`        | 5     | Sell stop pending order              |
| `SUB_ORDER_TYPE_BUY_STOP_LIMIT`   | 6     | Buy stop limit pending order         |
| `SUB_ORDER_TYPE_SELL_STOP_LIMIT`  | 7     | Sell stop limit pending order        |
| `SUB_ORDER_TYPE_CLOSE_BY`         | 8     | Close by opposite position           |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_TYPE_BUY   # = 0
```

**Order state enum (SUB_ENUM_ORDER_STATE):**

| Name                              | Value | Description                          |
| --------------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_STATE_STARTED`         | 0     | Order checked, but not yet accepted  |
| `SUB_ORDER_STATE_PLACED`          | 1     | Order accepted                       |
| `SUB_ORDER_STATE_CANCELED`        | 2     | Order canceled by client             |
| `SUB_ORDER_STATE_PARTIAL`         | 3     | Order partially executed             |
| `SUB_ORDER_STATE_FILLED`          | 4     | Order fully executed                 |
| `SUB_ORDER_STATE_REJECTED`        | 5     | Order rejected                       |
| `SUB_ORDER_STATE_EXPIRED`         | 6     | Order expired                        |
| `SUB_ORDER_STATE_REQUEST_ADD`     | 7     | Order being registered               |
| `SUB_ORDER_STATE_REQUEST_MODIFY`  | 8     | Order being modified                 |
| `SUB_ORDER_STATE_REQUEST_CANCEL`  | 9     | Order being deleted                  |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_STATE_FILLED   # = 4
```

**Deal type enum (SUB_ENUM_DEAL_TYPE):**

| Name                                      | Value | Description                          |
| ----------------------------------------- | ----- | ------------------------------------ |
| `SUB_DEAL_TYPE_BUY`                       | 0     | Buy deal                             |
| `SUB_DEAL_TYPE_SELL`                      | 1     | Sell deal                            |
| `SUB_DEAL_TYPE_BALANCE`                   | 2     | Balance operation                    |
| `SUB_DEAL_TYPE_CREDIT`                    | 3     | Credit operation                     |
| `SUB_DEAL_TYPE_CHARGE`                    | 4     | Additional charge                    |
| `SUB_DEAL_TYPE_CORRECTION`                | 5     | Correction                           |
| `SUB_DEAL_TYPE_BONUS`                     | 6     | Bonus                                |
| `SUB_DEAL_TYPE_COMMISSION`                | 7     | Commission                           |
| `SUB_DEAL_TYPE_COMMISSION_DAILY`          | 8     | Daily commission                     |
| `SUB_DEAL_TYPE_COMMISSION_MONTHLY`        | 9     | Monthly commission                   |
| `SUB_DEAL_TYPE_COMMISSION_AGENT_DAILY`    | 10    | Agent daily commission               |
| `SUB_DEAL_TYPE_COMMISSION_AGENT_MONTHLY`  | 11    | Agent monthly commission             |
| `SUB_DEAL_TYPE_INTEREST`                  | 12    | Interest rate                        |
| `SUB_DEAL_TYPE_BUY_CANCELED`              | 13    | Canceled buy deal                    |
| `SUB_DEAL_TYPE_SELL_CANCELED`             | 14    | Canceled sell deal                   |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_TYPE_BUY   # = 0
```

**Deal entry enum (SUB_ENUM_DEAL_ENTRY):**

| Name                       | Value | Description                          |
| -------------------------- | ----- | ------------------------------------ |
| `SUB_DEAL_ENTRY_IN`        | 0     | Entry into position                  |
| `SUB_DEAL_ENTRY_OUT`       | 1     | Exit from position                   |
| `SUB_DEAL_ENTRY_INOUT`     | 2     | Reverse of position                  |
| `SUB_DEAL_ENTRY_OUT_BY`    | 3     | Close by opposite position           |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_ENTRY_IN   # = 0
```

**Deal reason enum (SUB_ENUM_DEAL_REASON):**

| Name                                  | Value | Description                          |
| ------------------------------------- | ----- | ------------------------------------ |
| `SUB_DEAL_REASON_CLIENT`              | 0     | Deal placed from desktop terminal    |
| `SUB_DEAL_REASON_MOBILE`              | 1     | Deal placed from mobile app          |
| `SUB_DEAL_REASON_WEB`                 | 2     | Deal placed from web terminal        |
| `SUB_DEAL_REASON_EXPERT`              | 3     | Deal placed by Expert Advisor        |
| `SUB_DEAL_REASON_SL`                  | 4     | Deal due to Stop Loss activation     |
| `SUB_DEAL_REASON_TP`                  | 5     | Deal due to Take Profit activation   |
| `SUB_DEAL_REASON_SO`                  | 6     | Deal due to Stop Out                 |
| `SUB_DEAL_REASON_ROLLOVER`            | 7     | Deal due to rollover                 |
| `SUB_DEAL_REASON_VMARGIN`             | 8     | Deal due to variation margin         |
| `SUB_DEAL_REASON_SPLIT`               | 9     | Deal due to split                    |
| `SUB_DEAL_REASON_CORPORATE_ACTION`    | 10    | Deal due to corporate action         |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_REASON_CLIENT   # = 0
```

**Order time type enum (SUB_ENUM_ORDER_TYPE_TIME):**

| Name                           | Value | Description                          |
| ------------------------------ | ----- | ------------------------------------ |
| `SUB_ORDER_TIME_GTC`           | 0     | Good till cancel                     |
| `SUB_ORDER_TIME_DAY`           | 1     | Good till current trading day        |
| `SUB_ORDER_TIME_SPECIFIED`     | 2     | Good till specified date             |
| `SUB_ORDER_TIME_SPECIFIED_DAY` | 3     | Good till specified day              |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_TIME_GTC   # = 0
```

**Order filling type enum (SUB_ENUM_ORDER_TYPE_FILLING):**

| Name                         | Value | Description                          |
| ---------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_FILLING_FOK`      | 0     | Fill or Kill                         |
| `SUB_ORDER_FILLING_IOC`      | 1     | Immediate or Cancel                  |
| `SUB_ORDER_FILLING_BOC`      | 2     | Book or Cancel                       |
| `SUB_ORDER_FILLING_RETURN`   | 3     | Return                               |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_FILLING_FOK   # = 0
```

**Order reason enum (SUB_ENUM_ORDER_REASON):**

| Name                         | Value | Description                          |
| ---------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_REASON_CLIENT`    | 0     | Order placed from desktop terminal   |
| `SUB_ORDER_REASON_MOBILE`    | 2     | Order placed from mobile app         |
| `SUB_ORDER_REASON_WEB`       | 3     | Order placed from web terminal       |
| `SUB_ORDER_REASON_EXPERT`    | 4     | Order placed by Expert Advisor       |
| `SUB_ORDER_REASON_SL`        | 5     | Order triggered by Stop Loss         |
| `SUB_ORDER_REASON_TP`        | 6     | Order triggered by Take Profit       |
| `SUB_ORDER_REASON_SO`        | 7     | Order triggered by Stop Out          |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_REASON_CLIENT   # = 0
```

**Position type enum (SUB_ENUM_POSITION_TYPE):**

| Name                       | Value | Description                          |
| -------------------------- | ----- | ------------------------------------ |
| `SUB_POSITION_TYPE_BUY`    | 0     | Buy position                         |
| `SUB_POSITION_TYPE_SELL`   | 1     | Sell position                        |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_POSITION_TYPE_BUY   # = 0
```

**Position reason enum (SUB_ENUM_POSITION_REASON):**

| Name                           | Value | Description                          |
| ------------------------------ | ----- | ------------------------------------ |
| `SUB_POSITION_REASON_CLIENT`   | 0     | Position from desktop terminal       |
| `SUB_POSITION_REASON_MOBILE`   | 2     | Position from mobile app             |
| `SUB_POSITION_REASON_WEB`      | 3     | Position from web terminal           |
| `SUB_POSITION_REASON_EXPERT`   | 4     | Position from Expert Advisor         |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_POSITION_REASON_CLIENT   # = 0
```

---

**MqlTradeTransaction fields (partial list):**

| Field                      | Type     | Description                              |
| -------------------------- | -------- | ---------------------------------------- |
| `deal_ticket`              | `uint64` | Deal ticket number                       |
| `order_ticket`             | `uint64` | Order ticket number                      |
| `symbol`                   | `string` | Trading symbol                           |
| `type`                     | `enum`   | Transaction type                         |
| `order_type`               | `enum`   | Order type (market, limit, stop, etc.)   |
| `order_state`              | `enum`   | Order state (started, placed, etc.)      |
| `deal_type`                | `enum`   | Deal type (buy, sell)                    |
| `order_time_type`          | `enum`   | Order time type (GTC, DAY, etc.)         |
| `price`                    | `double` | Price                                    |
| `price_stop_loss`          | `double` | Stop loss price                          |
| `price_take_profit`        | `double` | Take profit price                        |
| `volume`                   | `double` | Volume                                   |
| `position_ticket`          | `uint64` | Position ticket                          |

**MqlTradeRequest fields:**

| Field         | Type     | Description                              |
| ------------- | -------- | ---------------------------------------- |
| `action`      | `enum`   | Trade operation type                     |
| `magic`       | `uint64` | Expert Advisor ID                        |
| `order`       | `uint64` | Order ticket                             |
| `symbol`      | `string` | Trading symbol                           |
| `volume`      | `double` | Requested volume                         |
| `price`       | `double` | Price                                    |

**MqlTradeResult fields:**

| Field         | Type     | Description                              |
| ------------- | -------- | ---------------------------------------- |
| `retcode`     | `uint32` | Operation return code                    |
| `deal`        | `uint64` | Deal ticket                              |
| `order`       | `uint64` | Order ticket                             |
| `volume`      | `double` | Deal volume                              |
| `price`       | `double` | Deal price                               |
| `bid`         | `double` | Current Bid price                        |
| `ask`         | `double` | Current Ask price                        |
| `comment`     | `string` | Broker comment                           |

---


## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[OnTradeTransaction - How it works](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_transaction_HOW.md)**

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` streaming methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_stream_with_reconnect`.
* **Async generator:** The method returns an async generator - use `async for` to consume data.
* **Most detailed:** This is the most comprehensive transaction stream - includes full request/result data.
* **No parameters:** Subscribes to ALL trade transactions automatically.
* **Event-driven:** Updates arrive immediately when transactions occur (not periodic).
* **Complete lifecycle:** Tracks order placement, modification, execution, and cancellation.
* **Includes failures:** Receives events for both successful and failed transactions.
* **Resource intensive:** Most detailed stream - use `on_trade` if you don't need this level of detail.

---

## 🔗 Usage Examples

### 1) Basic transaction monitor

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_transactions():
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
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction

            print(f"\n[TRANSACTION EVENT]")
            print(f"   Type: {tx.type}")
            print(f"   Symbol: {tx.symbol}")
            print(f"   Order: #{tx.order_ticket}")
            print(f"   Deal: #{tx.deal_ticket}")
            print(f"   Position: #{tx.position_ticket}")
            print(f"   Price: {tx.price}")
            print(f"   Volume: {tx.volume}")
            print(f"   Order state: {tx.order_state}")

            # Show request if available
            if tx_data.trade_request and tx_data.trade_request.symbol:
                req = tx_data.trade_request
                print(f"\n   Request:")
                print(f"     Symbol: {req.symbol}")
                print(f"     Volume: {req.volume}")
                print(f"     Price: {req.price}")

            # Show result if available
            if tx_data.trade_result and tx_data.trade_result.retcode != 0:
                res = tx_data.trade_result
                print(f"\n   Result:")
                print(f"     Return code: {res.retcode}")
                print(f"     Comment: {res.comment}")

    except KeyboardInterrupt:
        print("\nStopping transaction monitor...")

    finally:
        await account.channel.close()

asyncio.run(monitor_transactions())
```

### 2) Complete transaction audit log

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def audit_log():
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
        with open('trade_audit.log', 'w') as logfile:
            logfile.write("Timestamp,Type,Symbol,Order,Deal,Position,Price,Volume,State\n")

            async for tx_data in account.on_trade_transaction():
                tx = tx_data.trade_transaction
                timestamp = datetime.now().isoformat()

                # Write to audit log
                logfile.write(
                    f"{timestamp},"
                    f"{tx.type},"
                    f"{tx.symbol},"
                    f"{tx.order_ticket},"
                    f"{tx.deal_ticket},"
                    f"{tx.position_ticket},"
                    f"{tx.price},"
                    f"{tx.volume},"
                    f"{tx.order_state}\n"
                )
                logfile.flush()

                print(f"[{timestamp}] Logged transaction: "
                      f"Order #{tx.order_ticket}, Deal #{tx.deal_ticket}")

    except KeyboardInterrupt:
        print("\nStopping audit log...")

    finally:
        await account.channel.close()

asyncio.run(audit_log())
```

### 3) Order lifecycle tracker

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def track_order_lifecycle():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    order_states = {}  # order_ticket -> list of states

    try:
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction

            if tx.order_ticket > 0:
                # Track order state changes
                if tx.order_ticket not in order_states:
                    order_states[tx.order_ticket] = []

                order_states[tx.order_ticket].append({
                    'state': tx.order_state,
                    'type': tx.type,
                    'price': tx.price,
                    'volume': tx.volume
                })

                print(f"\n[LIFECYCLE] Order #{tx.order_ticket}:")
                for i, state in enumerate(order_states[tx.order_ticket], 1):
                    print(f"   {i}. State: {state['state']}, "
                          f"Type: {state['type']}, "
                          f"Price: {state['price']}")

    except KeyboardInterrupt:
        print("\nStopping lifecycle tracker...")
        print(f"\nTracked {len(order_states)} orders")

    finally:
        await account.channel.close()

asyncio.run(track_order_lifecycle())
```

### 4) Failed transaction monitor

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_failed_transactions():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    failed_count = 0

    try:
        async for tx_data in account.on_trade_transaction():
            # Check for failed transactions
            if tx_data.trade_result and tx_data.trade_result.retcode != 10009:  # Not DONE
                failed_count += 1
                res = tx_data.trade_result
                tx = tx_data.trade_transaction

                print(f"\n[FAILED TRANSACTION #{failed_count}]")
                print(f"   Return code: {res.retcode}")
                print(f"   Comment: {res.comment}")
                print(f"   Symbol: {tx.symbol}")
                print(f"   Order: #{tx.order_ticket}")
                print(f"   Requested volume: {tx.volume}")
                print(f"   Price: {tx.price}")

                if tx_data.trade_request:
                    req = tx_data.trade_request
                    print(f"\n   Original request:")
                    print(f"     Action: {req.action}")
                    print(f"     Symbol: {req.symbol}")
                    print(f"     Volume: {req.volume}")

    except KeyboardInterrupt:
        print(f"\n\nStopping monitor. Total failed: {failed_count}")

    finally:
        await account.channel.close()

asyncio.run(monitor_failed_transactions())
```

### 5) Transaction statistics collector

```python
import asyncio
from collections import defaultdict
from MetaRpcMT5 import MT5Account

async def collect_transaction_stats(duration_seconds=300):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    stats = {
        'total_transactions': 0,
        'by_type': defaultdict(int),
        'by_state': defaultdict(int),
        'by_symbol': defaultdict(int),
        'successful': 0,
        'failed': 0,
    }

    cancel_event = asyncio.Event()

    async def auto_stop():
        await asyncio.sleep(duration_seconds)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        async for tx_data in account.on_trade_transaction(
            cancellation_event=cancel_event
        ):
            tx = tx_data.trade_transaction
            stats['total_transactions'] += 1
            stats['by_type'][tx.type] += 1
            stats['by_state'][tx.order_state] += 1

            if tx.symbol:
                stats['by_symbol'][tx.symbol] += 1

            # Check success/failure
            if tx_data.trade_result:
                if tx_data.trade_result.retcode == 10009:  # DONE
                    stats['successful'] += 1
                else:
                    stats['failed'] += 1

        await stop_task

        # Print statistics
        print("\n" + "=" * 70)
        print("TRANSACTION STATISTICS REPORT")
        print("=" * 70)
        print(f"Total transactions:  {stats['total_transactions']:>6,}")
        print(f"Successful:          {stats['successful']:>6,}")
        print(f"Failed:              {stats['failed']:>6,}")

        print("\nBy Type:")
        for tx_type, count in sorted(stats['by_type'].items()):
            print(f"  Type {tx_type}: {count:>6,}")

        print("\nBy State:")
        for state, count in sorted(stats['by_state'].items()):
            print(f"  State {state}: {count:>6,}")

        print("\nBy Symbol:")
        for symbol, count in sorted(stats['by_symbol'].items(),
                                    key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {symbol}: {count:>6,}")

        print("=" * 70)

    finally:
        await account.channel.close()

# Collect statistics for 5 minutes
asyncio.run(collect_transaction_stats(300))
```

### 6) Real-time trade journal

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def trade_journal():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    journal_entries = []

    try:
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction

            # Create journal entry
            entry = {
                'timestamp': datetime.now(),
                'type': tx.type,
                'symbol': tx.symbol,
                'order_ticket': tx.order_ticket,
                'deal_ticket': tx.deal_ticket,
                'position_ticket': tx.position_ticket,
                'price': tx.price,
                'volume': tx.volume,
                'order_state': tx.order_state,
                'sl': tx.price_stop_loss,
                'tp': tx.price_take_profit,
            }

            # Add result info if available
            if tx_data.trade_result:
                entry['retcode'] = tx_data.trade_result.retcode
                entry['comment'] = tx_data.trade_result.comment

            # Add account balance
            if tx_data.account_info:
                entry['balance'] = tx_data.account_info.balance
                entry['equity'] = tx_data.account_info.equity

            journal_entries.append(entry)

            # Display entry
            print(f"\n{'=' * 70}")
            print(f"JOURNAL ENTRY #{len(journal_entries)}")
            print(f"{'=' * 70}")
            print(f"Time:       {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Symbol:     {entry['symbol']}")
            print(f"Type:       {entry['type']}")
            print(f"Order:      #{entry['order_ticket']}")
            print(f"Deal:       #{entry['deal_ticket']}")
            print(f"Position:   #{entry['position_ticket']}")
            print(f"Price:      {entry['price']}")
            print(f"Volume:     {entry['volume']}")
            print(f"SL:         {entry['sl']}")
            print(f"TP:         {entry['tp']}")
            print(f"State:      {entry['order_state']}")

            if 'balance' in entry:
                print(f"Balance:    ${entry['balance']:.2f}")
                print(f"Equity:     ${entry['equity']:.2f}")

            # Save journal periodically
            if len(journal_entries) % 10 == 0:
                print(f"\n[SAVED] {len(journal_entries)} entries to journal")

    except KeyboardInterrupt:
        print(f"\n\nStopping journal. Total entries: {len(journal_entries)}")

        # Export journal
        with open('trade_journal.txt', 'w') as f:
            f.write("TRADE JOURNAL\n")
            f.write("=" * 70 + "\n\n")
            for i, entry in enumerate(journal_entries, 1):
                f.write(f"Entry #{i}\n")
                f.write(f"  Time: {entry['timestamp']}\n")
                f.write(f"  Symbol: {entry['symbol']}\n")
                f.write(f"  Order: #{entry['order_ticket']}\n")
                f.write(f"  Price: {entry['price']}\n")
                f.write("\n")

        print(f"Journal exported to trade_journal.txt")

    finally:
        await account.channel.close()

asyncio.run(trade_journal())
```

---

## 📚 See also

* [OnTrade](./on_trade.md) - Simpler trade event stream (less detailed)
* [OrderSend](../5.%20Trading_Operations/order_send.md) - Send trade orders
* [OrderCheck](../5.%20Trading_Operations/order_check.md) - Verify order before sending
* [OrderHistory](../3.%20Positions_Orders/order_history.md) - Get historical orders
