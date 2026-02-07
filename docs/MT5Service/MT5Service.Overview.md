# MT5Service - Mid-Level API Overview

---

## ⚠️ Critical Understanding

**MT5Service is an architectural middleware** - it sits between MT5Account (gRPC protobuf) and MT5Sugar (business logic).

### Three-Layer Architecture:

```
┌───────────────────────────────────────────────────────────────
│  MT5Sugar (HIGH)                                        
│  Business logic, ready patterns, high-level operations  
└────────────────────┬──────────────────────────────────────────
                     │ Uses Service methods
                     ↓
┌───────────────────────────────────────────────────────────────
│  MT5Service (MID) ← YOU ARE HERE                        
│  Unpacks protobuf + creates dataclasses                 
│  SOME methods add value, SOME are pass-through          
└────────────────────┬──────────────────────────────────────────
                     │ Calls Account methods
                     ↓
┌───────────────────────────────────────────────────────────────
│  MT5Account (LOW)                                      
│  Direct gRPC calls, returns protobuf Data objects       
└────────────────────┬──────────────────────────────────────────
                     │ gRPC stream
                     ↓
                  MT5 Terminal
```

### Value Reality Check

**Not all MT5Service methods add the same value:**

- ✅ **HIGH/VERY HIGH value** - Complex protobuf unpacking + dataclass conversion

- ⚪ **MEDIUM/LOW value** - Simple protobuf field extraction

- ⚪ **NONE value** - Direct pass-through (`return await account.method()` or `yield data`)

**Key insight:** MT5Service exists primarily for **MT5Sugar's architectural needs**. For direct usage, evaluate each method's actual processing value.

---

## Quick Navigation - Section Overviews

### [1. Account Information](./1.%20Account_Information.md)

**4 methods** - Account balance/equity/margin/leverage

- ✅ 1 HIGH value: `get_account_summary()` - aggregates 5 RPC calls + datetime conversion

- ⚪ 3 NONE value: Simple pass-through wrappers for architectural consistency

### [2. Symbol Information](./2.%20Symbol_Information.md)

**13 methods** - Symbol properties, quotes, trading conditions

- ✅ 9 methods have value - MT5Account returns protobuf Data that needs unpacking (VERY HIGH to LOW)
- ⚪ 4 methods NONE value - Direct pass-through for architectural consistency

### [3. Positions & Orders](./3.%20Positions_Orders.md)

**5 methods** - Open positions, pending orders, history

- ✅ 1 MEDIUM value: `get_opened_tickets()` - converts protobuf repeated → Python lists

- ⚪ 1 LOW value: Simple unpacking

- ⚪ 3 NONE value: Direct pass-through

### [4. Market Depth](./4.%20Market_Depth.md)

**3 methods** - Level II quotes, order book (DOM)

- ✅ 1 HIGH value: `get_market_depth()` - converts protobuf repeated → List[BookInfo]

- ⚪ 2 MEDIUM value: Simple bool unpacking

### [5. Trading Operations](./5.%20Trading_Operations.md)

**6 methods** - Order execution, margin calculations

- ✅ 1 VERY HIGH value: `check_order()` - extracts deeply nested protobuf structure

- ✅ 2 HIGH value: `place_order()`, `modify_order()` - flatten 10 fields → dataclass

- ⚪ 3 LOW value: Simple single-field extraction

### [6. Streaming Methods](./6.%20Streaming_Methods.md)

**5 async generators** - Real-time ticks, trades, profits

- ✅ 1 HIGH value: `stream_ticks()` - datetime conversion + dataclass creation

- ⚪ 4 NONE value: Direct pass-through (`yield data`)

---

## All 36 Methods - Grouped by Value

### ✅ Methods Worth Using Directly

**VERY HIGH Value** (1 method):

- `check_order()` - Extracts deeply nested `mrpc_mql_trade_check_result` → OrderCheckResult

**HIGH Value** (7 methods):

- `get_account_summary()` - Aggregates 5 RPC calls + datetime conversion
- `get_symbol_params_many()` - Aggregates 17 fields + unpacks protobuf list
- `get_symbol_tick()` - Unix timestamp → datetime + unpacks 8 fields
- `get_symbol_session_quote()` - 2x protobuf Timestamp → datetime
- `get_symbol_session_trade()` - 2x protobuf Timestamp → datetime
- `place_order()` - Flattens 10 protobuf fields → OrderResult dataclass
- `modify_order()` - Flattens 10 protobuf fields → OrderResult dataclass
- `get_market_depth()` - Converts protobuf repeated → List[BookInfo] dataclass
- `stream_ticks()` - Converts protobuf Timestamp → datetime + SymbolTick dataclass

**MEDIUM Value** (3 methods):

- `get_symbol_margin_rate()` - Unpacks protobuf + creates dataclass
- `get_opened_tickets()` - Converts protobuf repeated → Python lists
- `subscribe_market_depth()` - Unpacks `data.success` from protobuf
- `unsubscribe_market_depth()` - Unpacks `data.success` from protobuf

### ⚪ Methods with Minimal/No Value

**LOW Value** (8 methods) - Simple single-field extraction:

- `get_symbols_total()` - Unpacks `data.total`
- `get_symbol_double()` - Unpacks `data.value`
- `get_symbol_integer()` - Unpacks `data.value`
- `get_symbol_string()` - Unpacks `data.value`
- `get_positions_total()` - Unpacks `data.total_positions`
- `close_order()` - Unpacks `data.returned_code`
- `calculate_margin()` - Unpacks `data.margin`
- `calculate_profit()` - Unpacks `data.profit`

**NONE Value** (18 methods) - Direct pass-through:

- `get_account_double()` - Just calls `account.account_info_double()`
- `get_account_integer()` - Just calls `account.account_info_integer()`
- `get_account_string()` - Just calls `account.account_info_string()`
- `symbol_exist()` - Just calls `account.symbol_exist()`
- `get_symbol_name()` - Just calls `account.symbol_name()`
- `symbol_select()` - Just calls `account.symbol_select()`
- `is_symbol_synchronized()` - Just calls `account.symbol_is_synchronized()`
- `get_opened_orders()` - Just calls `account.opened_orders()`
- `get_order_history()` - Just calls `account.order_history()`
- `get_positions_history()` - Just calls `account.positions_history()`
- `stream_trade_updates()` - Just `yield data`
- `stream_position_profits()` - Just `yield data`
- `stream_opened_tickets()` - Just `yield data`
- `stream_transactions()` - Just `yield data`

---

## When to Use MT5Service vs MT5Account

### Use MT5Service When:

- ✅ Method adds significant value (HIGH/VERY HIGH from list above)
- ✅ You need cleaner API than protobuf (datetime conversion, dataclasses)
- ✅ Working with MT5Sugar (architectural requirement)

### Use MT5Account Directly When:

- Method has NONE/LOW value (direct pass-through or simple unpacking)
- Need full control over protobuf structures
- Performance critical (avoid extra layer)
- Method not available in MT5Service

**Access MT5Account from MT5Service:**

```python
account = service.get_account()
# Now call low-level methods directly
```

---

## Usage Pattern

```python
import asyncio
from uuid import uuid4
from MetaRpcMT5 import MT5Account  # Low-level gRPC client
from pymt5.mt5_service import MT5Service  # Mid-level wrapper
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

async def main():
    # 1. Create MT5Account (low-level gRPC client)
    account = MT5Account(
        user=12345678,  # MT5 login number
        password="password",
        grpc_server="127.0.0.1:9999",  # optional, default "mt5.mrpc.pro:443"
        id_=uuid4()  # optional UUID for terminal instance
    )

    # 2. Connect to MT5 server
    await account.connect_by_server_name(
        server_name="MetaQuotes-Demo",  # MT5 broker server/cluster name
        base_chart_symbol="EURUSD",  # symbol for chart initialization
        timeout_seconds=120
    )

    # 3. Wrap in MT5Service (mid-level)
    service = MT5Service(account)

    # 4. Use HIGH-value methods
    summary = await service.get_account_summary()
    print(f"Balance: ${summary.balance:.2f}, Equity: ${summary.equity:.2f}")

    # 5. For NONE-value methods, consider calling Account directly
    # Instead of: balance = await service.get_account_double(account_info_pb2.ACCOUNT_BALANCE)
    # Direct call: balance = await account.account_info_double(account_info_pb2.ACCOUNT_BALANCE)

    # 6. Close connection when done
    await account.channel.close()

asyncio.run(main())
```

---

## Complete Method Index

### 1. Account Information (4 methods)

**Overview:** [Account_Information.md](./1.%20Account_Information.md)

| Method | Value | What It Does |
|--------|-------|--------------|
| `get_account_summary()` | ✅ HIGH | Aggregates 5 RPC calls + datetime conversion |
| `get_account_double()` | ⚪ NONE | Pass-through: `return await account.account_info_double()` |
| `get_account_integer()` | ⚪ NONE | Pass-through: `return await account.account_info_integer()` |
| `get_account_string()` | ⚪ NONE | Pass-through: `return await account.account_info_string()` |

---

### 2. Symbol Information (13 methods)

**Overview:** [Symbol_Information.md](./2.%20Symbol_Information.md)

| Method | Value | What It Does |
|--------|-------|--------------|
| `get_symbol_params_many()` | ✅ VERY HIGH | Aggregates 17 fields + unpacks protobuf list |
| `get_symbol_tick()` | ✅ HIGH | Unix timestamp → datetime + unpacks 8 fields |
| `get_symbol_session_quote()` | ✅ HIGH | 2x protobuf Timestamp → datetime |
| `get_symbol_session_trade()` | ✅ HIGH | 2x protobuf Timestamp → datetime |
| `get_symbol_margin_rate()` | ⚪ MEDIUM | Unpacks protobuf + creates dataclass |
| `get_symbols_total()` | ⚪ LOW | Unpacks `data.total` from protobuf |
| `get_symbol_double()` | ⚪ LOW | Unpacks `data.value` from protobuf |
| `get_symbol_integer()` | ⚪ LOW | Unpacks `data.value` from protobuf |
| `get_symbol_string()` | ⚪ LOW | Unpacks `data.value` from protobuf |
| `symbol_exist()` | ⚪ NONE | Pass-through: `return await account.symbol_exist()` |
| `get_symbol_name()` | ⚪ NONE | Pass-through: `return await account.symbol_name()` |
| `symbol_select()` | ⚪ NONE | Pass-through: `return await account.symbol_select()` |
| `is_symbol_synchronized()` | ⚪ NONE | Pass-through: `return await account.symbol_is_synchronized()` |

---

### 3. Positions & Orders (5 methods)

**Overview:** [Positions_Orders.md](./3.%20Positions_Orders.md)

| Method | Value | What It Does |
|--------|-------|--------------|
| `get_opened_tickets()` | ✅ MEDIUM | Converts protobuf repeated → Python lists |
| `get_positions_total()` | ⚪ LOW | Unpacks `data.total_positions` from protobuf |
| `get_opened_orders()` | ⚪ NONE | Pass-through: `return await account.opened_orders()` |
| `get_order_history()` | ⚪ NONE | Pass-through: `return await account.order_history()` |
| `get_positions_history()` | ⚪ NONE | Pass-through: `return await account.positions_history()` |

---

### 4. Market Depth (3 methods)

**Overview:** [Market_Depth.md](./4.%20Market_Depth.md)

| Method | Value | What It Does |
|--------|-------|--------------|
| `get_market_depth()` | ✅ HIGH | Converts protobuf repeated → List[BookInfo] dataclass |
| `subscribe_market_depth()` | ⚪ MEDIUM | Unpacks `data.success` from protobuf |
| `unsubscribe_market_depth()` | ⚪ MEDIUM | Unpacks `data.success` from protobuf |

---

### 5. Trading Operations (6 methods)

**Overview:** [Trading_Operations.md](./5.%20Trading_Operations.md)

| Method | Value | What It Does |
|--------|-------|--------------|
| `check_order()` | ✅ VERY HIGH | Extracts deeply nested `mrpc_mql_trade_check_result` → OrderCheckResult (8 fields) |
| `place_order()` | ✅ HIGH | Flattens 10 protobuf fields → OrderResult dataclass |
| `modify_order()` | ✅ HIGH | Flattens 10 protobuf fields → OrderResult dataclass |
| `close_order()` | ⚪ LOW | Unpacks `data.returned_code` from protobuf → int |
| `calculate_margin()` | ⚪ LOW | Unpacks `data.margin` from protobuf → float |
| `calculate_profit()` | ⚪ LOW | Unpacks `data.profit` from protobuf → float |

---

### 6. Streaming Methods (5 async generators)

**Overview:** [Streaming_Methods.md](./6.%20Streaming_Methods.md)

| Method | Value | What It Does |
|--------|-------|--------------|
| `stream_ticks()` | ✅ HIGH | Converts protobuf Timestamp → datetime + creates SymbolTick dataclass (8 fields) |
| `stream_trade_updates()` | ⚪ NONE | Pass-through: `async for data in account.on_trade(): yield data` |
| `stream_position_profits()` | ⚪ NONE | Pass-through: `async for data in account.on_position_profit(): yield data` |
| `stream_opened_tickets()` | ⚪ NONE | Pass-through: `async for data in account.on_positions_and_pending_orders_tickets(): yield data` |
| `stream_transactions()` | ⚪ NONE | Pass-through: `async for data in account.on_trade_transaction(): yield data` |

---

## Best Practices

### 1. Use HIGH-value Methods

```python
# GOOD - use methods that add real value
summary = await service.get_account_summary()  # Aggregates 5 RPC calls
symbols, _ = await service.get_symbol_params_many("EURUSD")  # Aggregates 17 fields
result = await service.check_order(request)  # Extracts deeply nested protobuf

# CONSIDER - for NONE-value methods, call Account directly
balance = await account.account_info_double(account_info_pb2.ACCOUNT_BALANCE)
# Instead of: balance = await service.get_account_double(account_info_pb2.ACCOUNT_BALANCE)
```

### 2. Validate Trading Operations

```python
# ALWAYS use check_order() before place_order() - it has VERY HIGH value!
check = await service.check_order(request)
if check.returned_code == 0:
    result = await service.place_order(request)
    if result.returned_code == 10009:
        print(f"Success! Order: {result.order}")
```

### 3. Handle Errors

```python
try:
    summary = await service.get_account_summary()
except Exception as e:
    print(f"Error: {e}")
```

### 4. Use Cancellation Events for Streams

```python
import asyncio

cancel_event = asyncio.Event()

# Use HIGH-value stream_ticks()
async for tick in service.stream_ticks(["EURUSD"], cancel_event):
    print(f"{tick.time}: {tick.bid:.5f}")  # time is already datetime!
    if should_stop:
        cancel_event.set()
```

---


**Choose wisely based on actual processing value, not just API level!**
