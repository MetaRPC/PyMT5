# Protobuf Inspector - Interactive Type Explorer

> **Interactive developer utility for exploring MT5 protobuf types, fields, enums, and data structures from the MT5 gRPC API**

---

## 🏛️ What This Tool Does

The Protobuf Inspector is an **interactive command-line tool** that helps you explore the structure of the MT5 gRPC API:

- Interactive search for types, fields, and enums
- Real-time inspection of protobuf message structures
- Field-level discovery - find which types contain specific fields
- Field type discovery - find fields by their data type (double, string, enum, etc.)
- Enum value exploration - see all possible enum values
- Enum usage tracking - find where specific enums are used
- Type browsing with filters - list types by category
- JSON export - export type structures for documentation
- Statistics analysis - field types, enum counts, comprehensive metrics

---

## 🏁 Getting Started

### Running the Inspector

```bash
cd examples
python main.py inspect
```

You will see an interactive prompt:

```
===========================================================
MT5 PROTOBUF TYPES INSPECTOR
===========================================================

  Discovered 163 protobuf message types
  Discovered 60 enum types

  Type 'help' to see available commands
  Type 'list' to see all types
===========================================================

>
```

---

## 🧰 Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `list` or `ls` | Show all available protobuf types | `list` |
| `list --request` | Show only Request types | `list --request` |
| `list --reply` | Show only Reply types | `list --reply` |
| `list --data` | Show only Data types | `list --data` |
| `list --info` | Show only Info types | `list --info` |
| `<TypeName>` | Inspect specific type structure | `PositionInfo` |
| `search <text>` or `find <text>` | Search for types containing text | `search Order` |
| `field <name>` | Find all types with a specific field | `field ticket` |
| `findtype <type>` | Find all fields of a specific type | `findtype double` |
| `enum <name>` | Show all enum values | `enum ENUM_ORDER_TYPE_TF` |
| `whereenum <name>` | Find where enum is used | `whereenum ENUM_ORDER_TYPE_TF` |
| `export <TypeName>` | Export type structure to JSON | `export PositionInfo` |
| `stats` | Show detailed statistics | `stats` |
| `help` or `?` | Show help message | `help` |
| `exit` or `quit` | Exit the inspector | `exit` |

---

## Practical Examples

### Example 1: Find out what fields PositionInfo has

**Command:**
```
> PositionInfo
```

**Output:**
```
===========================================================
TYPE: PositionInfo
===========================================================
FIELDS (20):
-----------------------------------------------------------
  #  1 index                         : uint32
  #  2 ticket                        : uint64
  #  3 open_time                     : Timestamp
  #  4 volume                        : double
  #  5 price_open                    : double
  #  6 stop_loss                     : double
  #  7 take_profit                   : double
  #  8 price_current                 : double
  #  9 swap                          : double
  # 10 profit                        : double
  # 11 last_update_time              : Timestamp
  # 12 type                          : ENUM_ORDER_TYPE_TF
  # 13 magic_number                  : int64
  # 14 identifier                    : int64
  # 15 reason                        : ENUM_POSITION_REASON_TYPE
  # 16 symbol                        : string
  # 17 comment                       : string
  # 18 external_id                   : string
  # 19 position_commission           : double
  # 20 account_login                 : int64
```

---

### Example 2: Find which types have the "ticket" field

**Command:**
```
> field ticket
```

**Output:**
```
EXACT MATCH: field 'ticket' found in:
-----------------------------------------------------------
    1. DealInfo
    2. HistoryDealsGetByTicketRequest
    3. HistoryOrdersGetByTicketRequest
    4. OrderCloseRequest
    5. OrderInfo
    6. OrderModifyRequest
    7. PositionCloseRequest
    8. PositionInfo
    9. PositionModifyRequest
   10. TradeTransactionInfo
```

---

### Example 3: See all ORDER_TYPE enum values

**Command:**
```
> enum ENUM_ORDER_TYPE_TF
```

**Output:**
```
ENUM: ENUM_ORDER_TYPE_TF
===========================================================
  ORDER_TYPE_TF_BUY                        = 0
  ORDER_TYPE_TF_SELL                       = 1
  ORDER_TYPE_TF_BUY_LIMIT                  = 2
  ORDER_TYPE_TF_SELL_LIMIT                 = 3
  ORDER_TYPE_TF_BUY_STOP                   = 4
  ORDER_TYPE_TF_SELL_STOP                  = 5
  ORDER_TYPE_TF_BUY_STOP_LIMIT             = 6
  ORDER_TYPE_TF_SELL_STOP_LIMIT            = 7
  ORDER_TYPE_TF_CLOSE_BY                   = 8
```

---

### Example 3a: See streaming event ORDER_TYPE enum (NEW)

**Command:**
```
> enum SUB_ENUM_ORDER_TYPE
```

**Output:**
```
ENUM: SUB_ENUM_ORDER_TYPE
===========================================================
  SUB_ORDER_TYPE_BUY                       = 0
  SUB_ORDER_TYPE_SELL                      = 1
  SUB_ORDER_TYPE_BUY_LIMIT                 = 2
  SUB_ORDER_TYPE_SELL_LIMIT                = 3
  SUB_ORDER_TYPE_BUY_STOP                  = 4
  SUB_ORDER_TYPE_SELL_STOP                 = 5
  SUB_ORDER_TYPE_BUY_STOP_LIMIT            = 6
  SUB_ORDER_TYPE_SELL_STOP_LIMIT           = 7
  SUB_ORDER_TYPE_CLOSE_BY                  = 8
```

**Note:** Use `SUB_ENUM_*` enums for streaming events (on_trade, on_trade_transaction, etc.), and `ENUM_*_TF` enums for trading functions (order_send, order_modify, etc.).

---

### Example 4: Find all types related to "Position"

**Command:**
```
> search Position
```

**Output:**
```
FOUND 12 TYPES MATCHING 'Position':
-----------------------------------------------------------
    1. ClosedPositionsGetRequest
    2. ClosedPositionsGetRequestReply
    3. ENUM_POSITION_REASON_TYPE
    4. OpenedPositionsGetRequest
    5. OpenedPositionsGetRequestReply
    6. PositionCloseRequest
    7. PositionCloseRequestReply
    8. PositionInfo
    9. PositionModifyRequest
   10. PositionModifyRequestReply
   11. PositionProfitCallbackInfo
   12. PositionsTicketsCallbackInfo
```

---

### Example 5: Show all available types

**Command:**
```
> list
```

**Output:**
```
AVAILABLE PROTOBUF TYPES (163)
-----------------------------------------------------------

[Request] (47 types):
    1. AccountInfoDoubleGetRequest
    2. AccountInfoIntegerGetRequest
    3. AccountInfoStringGetRequest
    ...

[Reply] (44 types):
    1. AccountInfoDoubleGetRequestReply
    2. AccountInfoIntegerGetRequestReply
    ...

[Data] (47 types):
    1. AccountSummaryData
    2. MarketBookData
    3. OnSymbolTickData
    4. OnTradeData
    5. OnTradeTransactionData
    ...

[Info] (10 types):
    1. DealInfo
    2. OnEventAccountInfo
    3. OnTradeHistoryDealInfo
    4. OnTradeOrderInfo
    5. OnTradePositionInfo
    ...

[Other] (15 types):
    ...
```

---

### Example 6: Find all double fields (NEW)

**Command:**
```
> findtype double
```

**Output:**
```
FIELDS OF TYPE 'double' (120+ fields):
===========================================================

  AccountInfoDoubleGetRequestReply:
    - value

  AccountSummaryData:
    - account_balance
    - account_equity
    - account_margin
    - account_freemargin
    - account_profit

  DealInfo:
    - commission
    - fee
    - price
    - profit
    - swap
    - volume

  PositionInfo:
    - position_commission
    - price_current
    - price_open
    - profit
    - stop_loss
    - swap
    - take_profit
    - volume

  SymbolInfo:
    - ask
    - bid
    - point
    - swap_long
    - swap_short
    - volume_max
    - volume_min
    - volume_step

  ... (and more)
```

---

### Example 7: Find where enum is used (NEW)

**Command:**
```
> whereenum ENUM_ORDER_TYPE_TF
```

**Output:**
```
ENUM 'ENUM_ORDER_TYPE_TF' USED IN (8 fields):
===========================================================

  DealInfo:
    - type

  MqlTradeRequest:
    - type

  OrderInfo:
    - type

  OrderSendRequest:
    - operation

  PositionInfo:
    - type

  TradeTransactionInfo:
    - order_type
    - type

  ... (and more)
```

---

### Example 8: Export type to JSON (NEW)

**Command:**
```
> export PositionInfo
```

**Output:**
```
TYPE: PositionInfo (JSON export)
===========================================================
{
  "type_name": "PositionInfo",
  "full_name": "mt5.PositionInfo",
  "fields": [
    {
      "number": 1,
      "name": "index",
      "type": "uint32",
      "label": "optional"
    },
    {
      "number": 2,
      "name": "ticket",
      "type": "uint64",
      "label": "optional"
    },
    {
      "number": 12,
      "name": "type",
      "type": "ENUM_ORDER_TYPE_TF",
      "label": "optional",
      "enum_name": "ENUM_ORDER_TYPE_TF",
      "enum_values": {
        "ORDER_TYPE_TF_BUY": 0,
        "ORDER_TYPE_TF_SELL": 1,
        "ORDER_TYPE_TF_BUY_LIMIT": 2,
        "ORDER_TYPE_TF_SELL_LIMIT": 3,
        ...
      }
    },
    ...
  ]
}
```

---

### Example 9: Show statistics (NEW)

**Command:**
```
> stats
```

**Output:**
```
PROTOBUF INSPECTOR STATISTICS
===========================================================

Message Types: 163 total
-----------------------------------------------------------
  Request         :  47 types
  Reply           :  44 types
  Data            :  47 types
  Info            :  10 types
  Other           :  15 types

Enum Types: 60 total
-----------------------------------------------------------
  Total enum values  : 644

  Top 5 largest enums:
    BMT5_ENUM_SYMBOL_INDUSTRY                : 152 values
    SymbolInfoDoubleProperty                 :  60 values
    SymbolInfoIntegerProperty                :  37 values
    EnumOpenTerminalChartWithEaChatPeriod    :  22 values
    BMT5_ENUM_DEAL_TYPE                      :  18 values

Field Types: 147 distinct types
-----------------------------------------------------------
  Top 10 most common field types:
    double               : 209 fields
    string               : 112 fields
    int64                :  54 fields
    error                :  45 fields
    int32                :  44 fields
    uint64               :  40 fields
    timestamp            :  38 fields
    bool                 :  28 fields
    uint32               :  16 fields
    sub_enum_order_type  :   4 fields

Total Fields: 771
===========================================================
```

---

### Example 10: List only Request types (NEW)

**Command:**
```
> list --request
```

**Output:**
```
REQUEST TYPES
-----------------------------------------------------------

[Request] (47 types):
    1. AccountInfoDoubleGetRequest
    2. AccountInfoIntegerGetRequest
    3. AccountInfoStringGetRequest
    4. AccountSummaryRequest
    5. HistoryDealsGetByTicketRequest
    6. HistoryDealsGetRequest
    7. HistoryOrdersGetByTicketRequest
    8. HistoryOrdersGetRequest
    9. MarketBookGetRequest
   10. OpenedOrdersGetRequest
   11. OpenedPositionsGetRequest
   12. OrderCalcMarginRequest
   13. OrderCheckRequest
   14. OrderCloseRequest
   15. OrderModifyRequest
   16. OrderSendRequest
   17. PositionCloseRequest
   18. PositionModifyRequest
   19. SymbolExistRequest
   20. SymbolInfoDoubleGetRequest
   21. SymbolInfoIntegerGetRequest
   22. SymbolInfoMarginRateGetRequest
   23. SymbolInfoSessionQuoteGetRequest
   24. SymbolInfoSessionTradeGetRequest
   25. SymbolInfoStringGetRequest
   26. SymbolInfoTickGetRequest
   27. SymbolIsSynchronizedRequest
   28. SymbolNameRequest
   29. SymbolSelectRequest
   30. SymbolsTotalRequest
    ... (and more)
```

---

## 📦 Common Use Cases

### USE CASE 1: "Getting 'field not found' error"

**Problem:** Your code has `position.ballance` but it doesn't work

**Solution:**
```
> field balance
```

**Result:** Shows the correct field name and which type has it
```
EXACT MATCH: field 'balance' found in:
  " AccountSummaryData
  " AccountInfo
```

**Fix:** Use `account.balance`, not `position.balance`

---

### USE CASE 2: "What fields does X have?"

**Problem:** Don't know what data is in `PositionInfo`

**Solution:**
```
> PositionInfo
```

**Result:** Shows all 20 fields (ticket, type, symbol, profit, etc.)

---

### USE CASE 3: "What are valid enum values?"

**Problem:** Don't know what value to use for `order_type`

**Solution:**
```
> enum ENUM_ORDER_TYPE_TF
```

**Result:** Shows all values:
```
ORDER_TYPE_TF_BUY = 0
ORDER_TYPE_TF_SELL = 1
ORDER_TYPE_TF_BUY_LIMIT = 2
ORDER_TYPE_TF_SELL_LIMIT = 3
...
```

---

### USE CASE 4: "Need to find position-related types"

**Problem:** Exploring the API, need to see all position-related structures

**Solution:**
```
> search Position
```

**Result:** Shows all 12 types with "Position" in the name

---

### USE CASE 5: "Want to browse what's available"

**Problem:** New to the API, want to explore

**Solution:**
```
> list
```

**Result:** Shows all available types, grouped by category

---

### USE CASE 6: "Need all price fields" (NEW)

**Problem:** Want to find all price-related fields in the API

**Solution:**
```
> findtype double
```

**Result:** Shows all double fields (prices, volumes, profits, etc.) grouped by type

---

### USE CASE 7: "Where is this enum used?" (NEW)

**Problem:** Have an enum, need to know which types use it

**Solution:**
```
> whereenum ENUM_ORDER_TYPE_TF
```

**Result:** Shows all types and fields that use this enum

---

### USE CASE 8: "Generate documentation" (NEW)

**Problem:** Need to document type structure for team or external tools

**Solution:**
```
> export PositionInfo
```

**Result:** Gets complete JSON structure with field numbers, types, and enum values

---

## ℹ️ Statistics

When you run the inspector, it provides complete coverage of:

- **Total Message Types:** 163 (all MT5 gRPC protobuf message types)
- **Total Enums:** 60 (with 644 enum values)
- **Total Fields:** 771 (across all types)
- **Field Types:** 147 distinct protobuf types
- **Coverage:** 100% of MT5 gRPC API

---

## Important Enums (Frequently Used)

| Enum Name | Description | Common Values |
|-----------|-------------|---------------|
| `ENUM_ORDER_TYPE_TF` | Order types (trade functions) | BUY, SELL, BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP (9 values) |
| `SUB_ENUM_ORDER_TYPE` | Order types (streaming events) | SUB_ORDER_TYPE_BUY, SUB_ORDER_TYPE_SELL, etc. (9 values) |
| `SUB_ENUM_POSITION_TYPE` | Position types (streaming) | SUB_POSITION_TYPE_BUY, SUB_POSITION_TYPE_SELL (2 values) |
| `SUB_ENUM_DEAL_TYPE` | Deal types (streaming) | SUB_DEAL_TYPE_BUY, SUB_DEAL_TYPE_SELL, etc. (18 values) |
| `SUB_ENUM_ORDER_STATE` | Order states (streaming) | STARTED, PLACED, CANCELED, FILLED, REJECTED (10 values) |
| `MRPC_ENUM_ORDER_TYPE_FILLING` | Fill policies | FOK, IOC, Return, BOC (4 values) |
| `MRPC_ENUM_ORDER_TYPE_TIME` | Time in force | GTC, Day, Specified, Specified_Day (4 values) |
| `BMT5_ENUM_DEAL_REASON` | Deal execution reason | Client, Expert, SL, TP, Mobile (11 values) |
| `BMT5_ENUM_DEAL_ENTRY_TYPE` | Deal entry type | In, Out, InOut, Out_By (4 values) |
| `BMT5_ENUM_POSITION_REASON` | Why position opened | Client, Expert, Dealer, Mobile (7 values) |
| `SymbolInfoDoubleProperty` | Symbol price properties | BID, ASK, POINT, SWAP_LONG, SWAP_SHORT (60 values) |
| `SymbolInfoIntegerProperty` | Symbol integer properties | DIGITS, SPREAD, TRADE_MODE, etc. (37 values) |
| `AccountInfoDoublePropertyType` | Account double properties | BALANCE, EQUITY, MARGIN, etc. (14 values) |

**Note:** Enum names with prefixes (`MRPC_`, `BMT5_`, `SUB_`) indicate their usage context:

- `MRPC_*` - MetaRpc protocol enums (trading operations)
- `BMT5_*` - Base MT5 enums (historical data, reasons)
- `SUB_*` - Subscription/streaming enums (real-time events)

---

## Features

| Feature | Description |
|---------|-------------|
| **Case-insensitive search** | `search Order` = `search order` |
| **Partial field matching** | `field profit` finds both `profit` and `take_profit` |
| **Type categorization** | Shows `[Request]`, `[Reply]`, `[Data]`, `[Info]` tags |
| **Category filtering** | `list --request`, `list --reply`, etc. |
| **Field type search** | `findtype double` finds all double fields |
| **Enum usage tracking** | `whereenum <name>` shows where enum is used |
| **JSON export** | `export <TypeName>` outputs structured JSON |
| **Detailed statistics** | `stats` shows comprehensive metrics |
| **Array indicators** | `[]` suffix for repeated/array fields |
| **Protobuf field numbers** | Shows field `#N` for each field |
| **Smart error messages** | Suggests alternatives when type not found |

---

## Example Interactive Session

```bash
$ cd examples
$ python main.py inspect

===========================================================
MT5 PROTOBUF TYPES INSPECTOR
===========================================================

> search Order
FOUND 28 TYPES MATCHING 'Order':
-----------------------------------------------------------
    1. HistoryOrdersGetByTicketRequest
    2. HistoryOrdersGetRequest
    3. OpenedOrdersGetRequest
    4. OrderCalcMarginRequest
    5. OrderCheckRequest
    6. OrderCloseRequest
    7. OrderInfo
    8. OrderModifyRequest
    9. OrderSendRequest
   ...

> OrderInfo
===========================================================
TYPE: OrderInfo
===========================================================
FIELDS (25):
-----------------------------------------------------------
  #  1 ticket                        : uint64
  #  2 type                          : ENUM_ORDER_TYPE_TF
  #  3 state                         : ENUM_ORDER_STATE_TYPE
  #  4 type_filling                  : ENUM_ORDER_TYPE_FILLING
  #  5 type_time                     : ENUM_ORDER_TYPE_TIME
  #  6 magic_number                  : int64
  #  7 position_id                   : int64
  #  8 position_by_id                : int64
  #  9 reason                        : ENUM_ORDER_REASON_TYPE
  # 10 volume_initial                : double
  # 11 volume_current                : double
  # 12 price_open                    : double
  # 13 stop_loss                     : double
  # 14 take_profit                   : double
  # 15 price_current                 : double
  # 16 price_stoplimit               : double
  # 17 symbol                        : string
  # 18 comment                       : string
  # 19 external_id                   : string
  # 20 setup_time                    : Timestamp
  # 21 expiration_time               : Timestamp
  # 22 time_done                     : Timestamp
  # 23 account_login                 : int64
  # 24 index                         : uint32
  # 25 last_update_time              : Timestamp

> field magic
EXACT MATCH: field 'magic' found in:
-----------------------------------------------------------
    1. OrderInfo (magic_number)
    2. PositionInfo (magic_number)
    3. DealInfo (magic_number)
    4. MqlTradeRequest (magic)
    ...

PARTIAL MATCHES (field contains 'magic'):
-----------------------------------------------------------
    1. OrderInfo (magic_number)
    2. PositionInfo (magic_number)
    3. DealInfo (magic_number)
    ...

> enum ENUM_ORDER_STATE_TYPE
===========================================================
ENUM: ENUM_ORDER_STATE_TYPE
===========================================================
  ORDER_STATE_TYPE_STARTED                 = 0
  ORDER_STATE_TYPE_PLACED                  = 1
  ORDER_STATE_TYPE_CANCELED                = 2
  ORDER_STATE_TYPE_PARTIAL                 = 3
  ORDER_STATE_TYPE_FILLED                  = 4
  ORDER_STATE_TYPE_REJECTED                = 5
  ORDER_STATE_TYPE_EXPIRED                 = 6
  ORDER_STATE_TYPE_REQUEST_ADD             = 7
  ORDER_STATE_TYPE_REQUEST_MODIFY          = 8
  ORDER_STATE_TYPE_REQUEST_CANCEL          = 9

> findtype double
FIELDS OF TYPE 'double' (120+ fields):
===========================================================

  AccountSummaryData:
    - account_balance
    - account_equity
    - account_freemargin
    - account_margin
    - account_profit

  DealInfo:
    - commission
    - fee
    - price
    - profit
    - swap
    - volume

  OrderInfo:
    - price_current
    - price_open
    - price_stoplimit
    - stop_loss
    - take_profit
    - volume_current
    - volume_initial

  PositionInfo:
    - position_commission
    - price_current
    - price_open
    - profit
    - stop_loss
    - swap
    - take_profit
    - volume

  SymbolInfo:
    - ask
    - bid
    - point
    - swap_long
    - swap_short
    - volume_max
    - volume_min
    - volume_step

  ... (and more)

> whereenum ENUM_ORDER_TYPE_TF
ENUM 'ENUM_ORDER_TYPE_TF' USED IN (8 fields):
===========================================================

  DealInfo:
    - type

  MqlTradeRequest:
    - type

  OrderInfo:
    - type

  OrderSendRequest:
    - operation

  PositionInfo:
    - type

  TradeTransactionInfo:
    - order_type
    - type

> stats
PROTOBUF INSPECTOR STATISTICS
===========================================================

Message Types: 163 total
-----------------------------------------------------------
  Request         :  47 types
  Reply           :  44 types
  Data            :  47 types
  Info            :  10 types
  Other           :  15 types

Enum Types: 60 total
-----------------------------------------------------------
  Total enum values  : 644

  Top 5 largest enums:
    BMT5_ENUM_SYMBOL_INDUSTRY                : 152 values
    SymbolInfoDoubleProperty                 :  60 values
    SymbolInfoIntegerProperty                :  37 values
    EnumOpenTerminalChartWithEaChatPeriod    :  22 values
    BMT5_ENUM_DEAL_TYPE                      :  18 values

Field Types: 147 distinct types
-----------------------------------------------------------
  Top 10 most common field types:
    double               : 209 fields
    string               : 112 fields
    int64                :  54 fields
    error                :  45 fields
    int32                :  44 fields
    uint64               :  40 fields
    timestamp            :  38 fields
    bool                 :  28 fields
    uint32               :  16 fields
    sub_enum_order_type  :   4 fields

Total Fields: 771
===========================================================

> exit

[+] Goodbye!
```

---

## Implementation Details

The Protobuf Inspector uses Python reflection to:

1. Register all protobuf types at startup
2. Build in-memory indexes for:
   - Field names ‚¬„¢ Types mapping
   - Field types ‚¬„¢ Fields mapping
   - Enum names ‚¬„¢ Usage mapping
3. Provide instant search and lookup
4. Format output with structure and clarity
5. Export to JSON with complete metadata

**Source file:** `examples/0_common/16_protobuf_inspector.py`

**Modules scanned:**

- `mt5_term_api_account_helper_pb2`
- `mt5_term_api_account_information_pb2`
- `mt5_term_api_market_info_pb2`
- `mt5_term_api_trade_functions_pb2`
- `mt5_term_api_trading_helper_pb2`
- `mt5_term_api_subscriptions_pb2` (streaming events, SUB_ENUM_* enums)
- `mt5_term_api_charts_pb2` (chart operations)
- `mt5_term_api_connection_pb2` (connection management)

---

## Technical Notes

- **No MT5 connection required** - This is a purely offline tool that inspects type definitions
- **Complete coverage** - All 163 types and 60 enums from the MT5 gRPC API
- **Instant search** - In-memory indexes for fast lookup
- **Development only** - Not intended for production use
- **Python reflection** - Uses protobuf DESCRIPTOR API for introspection
- **JSON export** - Compatible with external documentation tools

---

## When to Use This Tool

**Use the inspector when:**

- Learning the MT5 gRPC API structure
- Debugging "field not found" errors
- Exploring available protobuf types
- Looking up enum values
- Finding the correct request/response types for API calls
- Understanding message structures before writing code
- Identifying all fields of a specific type (e.g., all double fields)
- Tracking enum usage across the API
- Generating documentation for types
- Analyzing API statistics

**Don't use for:**

- Inspecting runtime data (use debugger instead)
- Production code (this is a development tool)
- Testing API connectivity (use demo connections instead)

---

## Tips and Tricks

1. **Start with search** - If you know the general area, use `search <keyword>` first
2. **Use field search** - When you see a field name but don't know which type, use `field <name>`
3. **Explore enums early** - Understanding enum values saves debugging time later
4. **List is your friend** - When stuck, use `list` to browse available types
5. **Case doesn't matter** - Type commands in lowercase, it's faster
6. **Use filters** - `list --request` shows only what you need
7. **Find by type** - `findtype double` to see all price/volume fields
8. **Track enum usage** - `whereenum` shows relationships between types
9. **Export for docs** - Use `export` to generate JSON for team documentation
10. **Check stats** - Use `stats` to understand API structure overview

---

## Quick Start Workflow

**Beginner workflow for exploring the API:**

```bash
# 1. Start the inspector
cd examples
python main.py inspect

# 2. Browse what's available
> list

# 3. Search for what you need
> search Position

# 4. Inspect a type
> PositionInfo

# 5. Check enum values
> enum ENUM_ORDER_TYPE_TF

# 6. Find related types
> field ticket

# 7. Find fields by type
> findtype double

# 8. Check enum usage
> whereenum ENUM_ORDER_TYPE_TF

# 9. Get detailed stats
> stats

# 10. Export to JSON
> export PositionInfo
```

---

## Learning Session Example

**Goal:** "I want to close a position, what do I need?"

```bash
> search position close
FOUND 2 TYPES MATCHING 'position close':
  " PositionCloseRequest
  " PositionCloseRequestReply

> PositionCloseRequest
FIELDS (3):
  #  1 ticket                        : uint64
  #  2 deviation                     : uint64
  #  3 comment                       : string

> PositionCloseRequestReply
FIELDS (2):
  #  1 returned_code                 : uint32
  #  2 order_ticket                  : uint64

> field ticket
EXACT MATCH: field 'ticket' found in:
  " PositionInfo
  " OrderInfo
  " DealInfo
  " PositionCloseRequest
  " HistoryDealsGetByTicketRequest
  ...

# Now you know:
# - Use PositionCloseRequest with ticket field
# - You'll get PositionCloseRequestReply back
# - Check returned_code == 10009 for success (see RETURN_CODES_REFERENCE.md)
```

---

## Troubleshooting

**Q: Type not found**

```
> MyType
[!] Type not found: MyType
    Did you mean: MqlTradeRequest, MqlTradeResult, ...
```

**A:** Use search with partial name to find similar types

---

**Q: Too many results**

```
> search data
FOUND 156 TYPES...
```

**A:** Be more specific in your search query, or use filters like `list --data`

---

**Q: What's the difference between OrderInfo and OrderSendRequest?**

**A:** Use the inspector:

- `OrderInfo` - Information about an existing order (has 25 fields including state, times, etc.)
- `OrderSendRequest` - Request to create a new order (has 15 fields for order parameters)

Rule:

- `*Request` - Input for API method (what you send)
- `*Reply` - Output from API method (what you receive)
- `*Info` - Structured data about entities (position, order, deal, symbol)
- `*Data` - Helper data structures

---

**Q: Which fields are double vs int64?**

**A:** Use field type search:

```
> findtype double    # All price/volume/profit fields
> findtype int64     # All ID/magic/ticket fields
> findtype string    # All text fields (symbol, comment, etc.)
```

---

**Q: Where is enum X used?**

**A:** Use enum usage search:

```
> whereenum ENUM_ORDER_TYPE_TF
# Shows all types and fields that use this enum
```

---

## Summary

The Protobuf Inspector is your **first stop** when working with the MT5 gRPC API. Use it to:

1. **Discover** available types and their structure
2. 
3. **Learn** message field names and types
4. 
5. **Debug** field name and type issues
6. 
7. **Verify** enum values and usage
8. 
9. **Track** relationships between types
10. 
11. **Export** documentation for your team
12. 
13. **Analyze** API structure and statistics
14. 
15. **Speed up** development workflow

**Remember:** Type `help` at any time for command reference!

---

## Command Quick Reference

```
BASIC COMMANDS:
  list               - Show all types
  list --request     - Show only Request types
  <TypeName>         - Inspect type structure
  search <text>      - Find types by name
  field <name>       - Find types with field
  enum <name>        - Show enum values

NEW COMMANDS:
  findtype <type>    - Find fields by type
  whereenum <name>   - Find enum usage
  export <TypeName>  - Export to JSON
  stats              - Show statistics

NAVIGATION:
  help               - Show help
  exit               - Exit inspector
```

---

**Next Steps:**

- Run `python main.py inspect` and explore!
- Check [MT5Account Master Overview](../MT5Account/MT5Account.Master.Overview.md) for complete API documentation
- Try the demo examples in `examples/`
- See [RETURN_CODES_REFERENCE.md](RETURN_CODES_REFERENCE.md) for error codes
- See [USERCODE_SANDBOX_GUIDE.md](USERCODE_SANDBOX_GUIDE.md) for coding examples
