# ENUMs Usage Reference - MT5Account (Python)



> ENUM presence lookup table for all MT5Account low-level methods



---



## ✅ Summary Statistics



| Method Group | With ENUMs | Total | Percentage |
|--------------|------------|-------|------------|
| **Account Information** | 4 | 4 | 100% |
| **Symbol Information** | 7 | 13 | 54% |
| **Positions & Orders** | 3 | 6 | 50% |
| **Market Depth/DOM** | 1 | 3 | 33% |
| **Trading Operations** | 6 | 6 | 100% |
| **Streaming Methods** | 3 | 5 | 60% |
| **TOTAL** | **24** | **37** | **65%** |



---





## 👤 1. Account Information (4 methods)



### 4/4 methods use ENUMs (100%)



| Method | ENUMs Count | Description | Input ENUMs | Output ENUMs |
|--------|-------------|-------------|-------------|--------------|
| **account_summary** | **[In: 0, Out: 1]**<br>Total: 1 ENUM (3 values) | Get all account data in one call (RECOMMENDED) | - | `MrpcEnumAccountTradeMode` (3 values) - Account type: DEMO, CONTEST, REAL |
| **account_info_double** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (14 values) | Get double properties (Balance, Equity, Margin, etc.) | `AccountInfoDoublePropertyType` (14 values): ACCOUNT_BALANCE, ACCOUNT_CREDIT, ACCOUNT_PROFIT, ACCOUNT_EQUITY, ACCOUNT_MARGIN, ACCOUNT_MARGIN_FREE, ACCOUNT_MARGIN_LEVEL, ACCOUNT_MARGIN_SO_CALL, ACCOUNT_MARGIN_SO_SO, ACCOUNT_MARGIN_INITIAL, ACCOUNT_MARGIN_MAINTENANCE, ACCOUNT_ASSETS, ACCOUNT_LIABILITIES, ACCOUNT_COMMISSION_BLOCKED | - |
| **account_info_integer** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (11 values) | Get integer properties (Login, Leverage, etc.) | `AccountInfoIntegerPropertyType` (11 values): ACCOUNT_LOGIN, ACCOUNT_TRADE_MODE, ACCOUNT_LEVERAGE, ACCOUNT_LIMIT_ORDERS, ACCOUNT_MARGIN_SO_MODE, ACCOUNT_TRADE_ALLOWED, ACCOUNT_TRADE_EXPERT, ACCOUNT_MARGIN_MODE, ACCOUNT_CURRENCY_DIGITS, ACCOUNT_FIFO_CLOSE, ACCOUNT_HEDGE_ALLOWED | - |
| **account_info_string** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (4 values) | Get string properties (Currency, Company, etc.) | `AccountInfoStringPropertyType` (4 values): ACCOUNT_NAME, ACCOUNT_SERVER, ACCOUNT_CURRENCY, ACCOUNT_COMPANY | - |



---



## 📊 2. Symbol Information (13 methods)



### 7/13 methods use ENUMs (54%)



| Method | ENUMs Count | Description | Input ENUMs | Output ENUMs |
|--------|-------------|-------------|-------------|--------------|
| **symbols_total** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Count total/selected symbols | - | - |
| **symbol_exist** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Check if symbol exists | - | - |
| **symbol_name** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Get symbol name by index | - | - |
| **symbol_select** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Add/remove symbol from Market Watch | - | - |
| **symbol_is_synchronized** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Check sync status with server | - | - |
| **symbol_info_double** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (60 values) | Get double properties (Bid, Ask, Point, etc.) | `SymbolInfoDoubleProperty` (60 values) - Property selector | - |
| **symbol_info_integer** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (37 values) | Get integer properties (Digits, Spread, etc.) | `SymbolInfoIntegerProperty` (37 values) - Property selector | - |
| **symbol_info_string** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (15 values) | Get string properties (Description, etc.) | `SymbolInfoStringProperty` (15 values) - Property selector | - |
| **symbol_info_margin_rate** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (9 values) | Get margin requirements for order types | `ENUM_ORDER_TYPE` (9 values) - Order type | - |
| **symbol_info_tick** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Get last tick data with timestamp | - | - |
| **symbol_info_session_quote** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (7 values) | Get quote session times | `BMT5_ENUM_DAY_OF_WEEK` (7 values) - Day of week | - |
| **symbol_info_session_trade** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (7 values) | Get trade session times | `BMT5_ENUM_DAY_OF_WEEK` (7 values) - Day of week | - |
| **symbol_params_many** | **[In: 1, Out: 13]**<br>Total: 14 ENUMs | Get detailed parameters for multiple symbols | `AH_SYMBOL_PARAMS_MANY_SORT_TYPE` (4 values) - Sort mode | **13 ENUMs in SymbolParameters:** BMT5_ENUM_SYMBOL_SECTOR, BMT5_ENUM_SYMBOL_INDUSTRY, BMT5_ENUM_SYMBOL_CHART_MODE, BMT5_ENUM_SYMBOL_CALC_MODE, BMT5_ENUM_SYMBOL_TRADE_MODE, BMT5_ENUM_SYMBOL_TRADE_EXECUTION, BMT5_ENUM_SYMBOL_SWAP_MODE, BMT5_ENUM_DAY_OF_WEEK, BMT5_ENUM_ORDER_TYPE_FILLING, BMT5_ENUM_ORDER_TYPE, BMT5_ENUM_SYMBOL_ORDER_GTC_MODE, BMT5_ENUM_SYMBOL_OPTION_MODE, BMT5_ENUM_SYMBOL_OPTION_RIGHT |



---



## 📋 3. Positions & Orders Information (6 methods)



### 3/6 methods use ENUMs (50%)



| Method | ENUMs Count | Description | Input ENUMs | Output ENUMs |
|--------|-------------|-------------|-------------|--------------|
| **positions_total** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Count open positions | - | - |
| **opened_orders** | **[In: 1, Out: 6]**<br>Total: 7 ENUMs | Get all opened orders & positions | `BMT5_ENUM_OPENED_ORDER_SORT_TYPE` (4 values) - Sort mode | **6 ENUMs:**<br>**In PositionInfo:** BMT5_ENUM_POSITION_TYPE, BMT5_ENUM_POSITION_REASON<br>**In OpenedOrderInfo:** BMT5_ENUM_ORDER_TYPE, BMT5_ENUM_ORDER_STATE, BMT5_ENUM_ORDER_TYPE_FILLING, BMT5_ENUM_ORDER_TYPE_TIME |
| **opened_orders_tickets** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Get only ticket numbers (lightweight) | - | - |
| **order_history** | **[In: 1, Out: 7]**<br>Total: 8 ENUMs | Get historical orders with pagination | `BMT5_ENUM_ORDER_HISTORY_SORT_TYPE` (6 values) - Sort mode | **7 ENUMs:**<br>**In OrderHistoryData:** BMT5_ENUM_ORDER_STATE, BMT5_ENUM_ORDER_TYPE, BMT5_ENUM_ORDER_TYPE_FILLING, BMT5_ENUM_ORDER_TYPE_TIME<br>**In DealHistoryData:** BMT5_ENUM_DEAL_ENTRY_TYPE, BMT5_ENUM_DEAL_TYPE, BMT5_ENUM_DEAL_REASON |
| **positions_history** | **[In: 1, Out: 1]**<br>Total: 2 ENUMs | Get historical positions with P&L | `AH_ENUM_POSITIONS_HISTORY_SORT_TYPE` (4 values) - Sort mode | `AH_ENUM_POSITIONS_HISTORY_ORDER_TYPE` (9 values) - Order type |
| **tick_value_with_size** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Get tick value and size for symbols | - | - |



---



## 📚 4. Market Depth / DOM (3 methods)



### 1/3 methods use ENUMs (33%)



| Method | ENUMs Count | Description | Input ENUMs | Output ENUMs |
|--------|-------------|-------------|-------------|--------------|
| **market_book_add** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Subscribe to Depth of Market updates | - | - |
| **market_book_release** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Unsubscribe from DOM | - | - |
| **market_book_get** | **[In: 0, Out: 1]**<br>Total: 1 ENUM (4 values) | Get current market depth snapshot | - | `BookType` (4 values) - Order type in book: BOOK_TYPE_SELL, BOOK_TYPE_BUY, BOOK_TYPE_SELL_MARKET, BOOK_TYPE_BUY_MARKET |



---



## 💰 5. Trading Operations (6 methods)



### 6/6 methods use ENUMs (100%)



| Method | ENUMs Count | Description | Input ENUMs | Output ENUMs |
|--------|-------------|-------------|-------------|--------------|
| **order_send** | **[In: 2, Out: 0]**<br>Total: 2 ENUMs (13 values) | Send market or pending order | **2 ENUMs:**<br>`TMT5_ENUM_ORDER_TYPE` (9 values) - Order type<br>`TMT5_ENUM_ORDER_TYPE_TIME` (4 values) - Order lifetime | - |
| **order_modify** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (4 values) | Modify existing order parameters | `TMT5_ENUM_ORDER_TYPE_TIME` (4 values) - Order lifetime | - |
| **order_close** | **[In: 0, Out: 1]**<br>Total: 1 ENUM (3 values) | Close market or pending order | - | `MRPC_ORDER_CLOSE_MODE` (3 values): MRPC_MARKET_ORDER_CLOSE, MRPC_MARKET_ORDER_PARTIAL_CLOSE, MRPC_PENDING_ORDER_REMOVE |
| **order_check** | **[In: 4, Out: 0]**<br>Total: 4 ENUMs (23 values) | Validate order before sending | **4 ENUMs in MrpcMqlTradeRequest:**<br>`MRPC_ENUM_TRADE_REQUEST_ACTIONS` (6 values) - Trade action type<br>`ENUM_ORDER_TYPE_TF` (9 values) - Order type<br>`MRPC_ENUM_ORDER_TYPE_FILLING` (4 values) - Order filling policy<br>`MRPC_ENUM_ORDER_TYPE_TIME` (4 values) - Order lifetime | - |
| **order_calc_margin** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (9 values) | Calculate required margin | `ENUM_ORDER_TYPE_TF` (9 values) - Order type | - |
| **order_calc_profit** | **[In: 1, Out: 0]**<br>Total: 1 ENUM (9 values) | Calculate potential profit/loss | `ENUM_ORDER_TYPE_TF` (9 values) - Order type | - |



---



## 📡 6. Streaming Methods (5 methods)



### 3/5 methods use ENUMs (60%)



| Method | ENUMs Count | Description | Input ENUMs | Output ENUMs |
|--------|-------------|-------------|-------------|--------------|
| **on_symbol_tick** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Stream tick data (Bid/Ask updates) | - | - |
| **on_trade** | **[In: 0, Out: 1]**<br>Total: 11 ENUMs (68 values) | Stream trade events | - | **1 direct + 10 in nested structures:**<br>1. `MT5_SUB_ENUM_EVENT_GROUP_TYPE` (2 values) - OnTradeData.type<br>2-11. **In event_data nested structures:** SUB_ENUM_POSITION_TYPE (2), SUB_ENUM_POSITION_REASON (7), SUB_ENUM_ORDER_TYPE (9), SUB_ENUM_ORDER_STATE (10), SUB_ENUM_DEAL_TYPE (8), SUB_ENUM_ORDER_TYPE_TIME (4), SUB_ENUM_ORDER_TYPE_FILLING (4), SUB_ENUM_ORDER_REASON (7), SUB_ENUM_DEAL_ENTRY (4), SUB_ENUM_DEAL_REASON (11) |
| **on_position_profit** | **[In: 0, Out: 1]**<br>Total: 1 ENUM (2 values) | Stream position P&L updates | - | `MT5_SUB_ENUM_EVENT_GROUP_TYPE` (2 values) - Event type in OnPositionProfitData.type field |
| **on_positions_and_pending_orders_tickets** | **[In: 0, Out: 0]**<br>Total: 0 ENUMs | Stream ticket changes | - | - |
| **on_trade_transaction** | **[In: 0, Out: 9]**<br>Total: 9 ENUMs (107 values) | Stream trade transaction events | - | **11 ENUM fields from 9 unique types:**<br>1. `MT5_SUB_ENUM_EVENT_GROUP_TYPE` (2 values) - OnTradeTransactionData.type<br>2-6. **In MqlTradeTransaction:** SUB_ENUM_TRADE_TRANSACTION_TYPE (11 values), SUB_ENUM_ORDER_TYPE (9 values), SUB_ENUM_ORDER_STATE (10 values), SUB_ENUM_DEAL_TYPE (18 values), SUB_ENUM_ORDER_TYPE_TIME (4 values)<br>7-10. **In MqlTradeRequest:** SUB_ENUM_TRADE_REQUEST_ACTIONS (7 values), SUB_ENUM_ORDER_TYPE (9 values), SUB_ENUM_ORDER_TYPE_FILLING (4 values), SUB_ENUM_ORDER_TYPE_TIME (4 values)<br>11. **In MqlTradeResult:** MqlErrorTradeCode (42 values) |



---



## Important Notes



### Python ENUM Access

Python accesses ENUMs through protobuf modules:

**Correct:**
```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

# Using ENUM
property_id = account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
```

**Incorrect:**
```python
ACCOUNT_BALANCE  # NameError: name 'ACCOUNT_BALANCE' is not defined
```



### Special Cases



**1. AccountInfoInteger and SymbolInfoInteger:**

- Some properties return values that **represent ENUMs**, but are returned as `int64`

- These are **NOT typed ENUMs**, just numbers!



**2. ReturnedCode:**

- ReturnedCode field in trading operations is **NOT an ENUM**

- It's a plain uint32 operation return code



---



## See Also



### Documentation by Group:



- [Account Information Overview](../MT5Account/1.%20Account_Information/Account_Information.Overview.md)

- [Symbol Information Overview](../MT5Account/2.%20Symbol_Information/Symbol_Information.Overview.md)

- [Positions & Orders Overview](../MT5Account/3.%20Positions_Orders/Positions_Orders.Overview.md)

- [Market Depth Overview](../MT5Account/4.%20Market_Depth/Market_Depth.Overview.md)

- [Trading Operations Overview](../MT5Account/5.%20Trading_Operations/Trading_Operations.Overview.md)

- [Streaming Methods Overview](../MT5Account/6.%20Streaming_Methods/Streaming_Methods.Overview.md)





