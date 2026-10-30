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

!!! note "Numbers in this guide are a live snapshot"
    The counts and sample outputs below were captured from the current `MetaRpcMT5` protobuf package. They **grow as the API evolves**, so your run may show different totals — run `stats` and the commands yourself for the live values. The commands and workflow stay the same.

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

  Discovered 216 protobuf message types
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
  #  1 index                          : uint32
  #  2 ticket                         : uint64
  #  3 open_time                      : Timestamp
  #  4 volume                         : double
  #  5 price_open                     : double
  #  6 stop_loss                      : double
  #  7 take_profit                    : double
  #  8 price_current                  : double
  #  9 swap                           : double
  # 10 profit                         : double
  # 11 last_update_time               : Timestamp
  # 12 type                           : BMT5_ENUM_POSITION_TYPE
  # 13 magic_number                   : int64
  # 14 identifier                     : int64
  # 15 reason                         : BMT5_ENUM_POSITION_REASON
  # 16 symbol                         : string
  # 17 comment                        : string
  # 18 external_id                    : string
  # 19 position_commission            : double
  # 20 account_login                  : int64
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
    1. DealHistoryData
    2. HistoryOrderInfo
    3. OnPositionProfitPositionInfo
    4. OnTradeHistoryDealInfo
    5. OnTradeHistoryOrderInfo
    6. OnTradeOrderInfo
    7. OnTradePositionInfo
    8. OpenedOrderInfo
    9. OrderCloseRequest
   10. OrderHistoryData
   11. OrderModifyRequest
   12. PositionInfo

PARTIAL MATCHES (field contains 'ticket'):
-----------------------------------------------------------
    1. MqlTradeRequest
    2. MqlTradeResult
    3. MqlTradeTransaction
    4. OnPositionsAndPendingOrdersTicketsData
    5. OpenedOrdersTicketsData
    6. PositionHistoryInfo
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

### Example 3a: See streaming event ORDER_TYPE enum

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
FOUND 16 TYPES MATCHING 'Position':
-----------------------------------------------------------
    1. OnPositionProfitData
    2. OnPositionProfitPositionInfo
    3. OnPositionProfitReply
    4. OnPositionProfitRequest
    5. OnPositionsAndPendingOrdersTicketsData
    6. OnPositionsAndPendingOrdersTicketsReply
    7. OnPositionsAndPendingOrdersTicketsRequest
    8. OnTradePositionInfo
    9. OnTradePositionUpdate
   10. PositionHistoryInfo
   11. PositionInfo
   12. PositionsHistoryData
   13. PositionsHistoryReply
   14. PositionsHistoryRequest
   15. PositionsTotalData
   16. PositionsTotalReply
```

---

### Example 5: Show all available types

**Command:**
```
> list
```

**Output:**
```
AVAILABLE PROTOBUF TYPES (216)
-----------------------------------------------------------

[Request] (64 types):
    1. AccountInfoDoubleRequest
    2. AccountInfoIntegerRequest
    3. AccountInfoStringRequest
    ...

[Reply] (60 types):
    1. AccountInfoDoubleReply
    2. AccountInfoIntegerReply
    ...

[Data] (61 types):
    1. AccountInfoDoubleData
    2. AccountSummaryData
    3. AllHistoryOrdersData
    ...

[Info] (12 types):
    1. HistoryOrderInfo
    2. MrpcMqlBookInfo
    3. OnEventAccountInfo
    4. OnPositionProfitPositionInfo
    5. OnTradeHistoryDealInfo
    ...

[Other] (19 types):
    1. ConnectStreamEvent
    2. EaLogRow
    3. MqlTradeResult
    ...
```

---

### Example 6: Find all double fields

**Command:**
```
> findtype double
```

**Output:**
```
FIELDS OF TYPE 'double' (228 fields):
===========================================================

  AccountInfoDoubleData:
    - requested_value

  AccountSummaryData:
    - account_balance
    - account_credit
    - account_equity

  DealHistoryData:
    - commission
    - fee
    - price
    - profit
    - stop_loss
    - swap
    - take_profit
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

  ... (and more)
```

---

### Example 7: Find where enum is used

**Command:**
```
> whereenum ENUM_ORDER_TYPE_TF
```

**Output:**
```
ENUM 'ENUM_ORDER_TYPE_TF' USED IN (3 fields):
===========================================================

  MrpcMqlTradeRequest:
    - order_type

  OrderCalcMarginRequest:
    - order_type

  OrderCalcProfitRequest:
    - order_type
```

---

### Example 8: Export type to JSON

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
  "full_name": "mt5_term_api.PositionInfo",
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
      "type": "BMT5_ENUM_POSITION_TYPE",
      "label": "optional",
      "enum_name": "BMT5_ENUM_POSITION_TYPE",
      "enum_values": {
        "BMT5_POSITION_TYPE_BUY": 0,
        "BMT5_POSITION_TYPE_SELL": 1
      }
    },
    ...
  ]
}
```

---

### Example 9: Show statistics

**Command:**
```
> stats
```

**Output:**
```
PROTOBUF INSPECTOR STATISTICS
===========================================================

Message Types: 216 total
-----------------------------------------------------------
  Request         :  64 types
  Reply           :  60 types
  Data            :  61 types
  Info            :  12 types
  Other           :  19 types

Enum Types: 60 total
-----------------------------------------------------------
  Total enum values  : 644

  Top 5 largest enums:
    BMT5_ENUM_SYMBOL_INDUSTRY                : 152 values
    SymbolInfoDoubleProperty                 :  60 values
    SymbolInfoIntegerProperty                :  37 values
    EnumOpenTerminalChartWithEaChatPeriod    :  22 values
    BMT5_ENUM_DEAL_TYPE                      :  18 values

Field Types: 167 distinct types
-----------------------------------------------------------
  Top 10 most common field types:
    double               : 228 fields
    string               : 167 fields
    int64                :  66 fields
    error                :  62 fields
    int32                :  53 fields
    timestamp            :  49 fields
    uint64               :  43 fields
    bool                 :  36 fields
    uint32               :  24 fields
    bmt5_enum_order_type :   4 fields

Total Fields: 945
===========================================================
```

---

### Example 10: List only Request types

**Command:**
```
> list --request
```

**Output:**
```
REQUEST TYPES
-----------------------------------------------------------

[Request] (64 types):
    1. AccountInfoDoubleRequest
    2. AccountInfoIntegerRequest
    3. AccountInfoStringRequest
    4. AccountSummaryRequest
    5. AllHistoryOrdersRequest
    6. AttachEaRequest
    7. CheckConnectRequest
    8. ConnectByTokenRequest
    9. ConnectExRequest
   10. ConnectRequest
   11. MarketBookAddRequest
   12. MarketBookGetRequest
   13. OpenedOrdersRequest
   14. OrderCalcMarginRequest
   15. OrderCalcProfitRequest
   16. OrderCheckRequest
   17. OrderCloseRequest
   18. OrderModifyRequest
   19. OrderSendRequest
   20. SymbolInfoDoubleRequest
    ... (and more)
```

---

## 📦 Common Use Cases

### USE CASE 1: "Getting 'field not found' error"

**Problem:** Your code reads `position.balance` but it doesn't work

**Solution:**
```
> field balance
```

**Result:** Shows which types actually carry a balance field
```
EXACT MATCH: field 'balance' found in:
-----------------------------------------------------------
    1. OnEventAccountInfo

PARTIAL MATCHES (field contains 'balance'):
-----------------------------------------------------------
    1. AccountSummaryData
    2. MrpcMqlTradeCheckResult
```

**Fix:** Balance lives on the account, not a position — read `AccountSummaryData.account_balance` (via `MT5Service.get_account_summary()` or `MT5Sugar.balance`).

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

**Result:** Shows all 16 types with "Position" in the name

---

### USE CASE 5: "Want to browse what's available"

**Problem:** New to the API, want to explore

**Solution:**
```
> list
```

**Result:** Shows all available types, grouped by category

---

### USE CASE 6: "Need all price fields"

**Problem:** Want to find all price-related fields in the API

**Solution:**
```
> findtype double
```

**Result:** Shows all double fields (prices, volumes, profits, etc.) grouped by type

---

### USE CASE 7: "Where is this enum used?"

**Problem:** Have an enum, need to know which types use it

**Solution:**
```
> whereenum ENUM_ORDER_TYPE_TF
```

**Result:** Shows all types and fields that use this enum

---

### USE CASE 8: "Generate documentation"

**Problem:** Need to document type structure for team or external tools

**Solution:**
```
> export PositionInfo
```

**Result:** Gets complete JSON structure with field numbers, types, and enum values

---

## ℹ️ Statistics

When you run the inspector, it provides complete coverage of the current protobuf package:

- **Total Message Types:** 216 (all MT5 gRPC protobuf message types)
- **Total Enums:** 60 (with 644 enum values)
- **Total Fields:** 945 (across all types)
- **Field Types:** 167 distinct protobuf types
- **Coverage:** 100% of the scanned MT5 gRPC modules

---

## Important Enums (Frequently Used)

| Enum Name | Description | Common Values |
|-----------|-------------|---------------|
| `ENUM_ORDER_TYPE_TF` | Order types (trade functions) | BUY, SELL, BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP (9 values) |
| `TMT5_ENUM_ORDER_TYPE` | Order types (order_send) | TMT5_ORDER_TYPE_BUY, …_SELL, …_BUY_LIMIT, etc. (9 values) |
| `SUB_ENUM_ORDER_TYPE` | Order types (streaming events) | SUB_ORDER_TYPE_BUY, SUB_ORDER_TYPE_SELL, etc. (9 values) |
| `BMT5_ENUM_POSITION_TYPE` | Position direction | BMT5_POSITION_TYPE_BUY, …_SELL (2 values) |
| `BMT5_ENUM_ORDER_STATE` | Order states | STARTED, PLACED, CANCELED, PARTIAL, FILLED, REJECTED (10 values) |
| `SUB_ENUM_DEAL_TYPE` | Deal types (streaming) | SUB_DEAL_TYPE_BUY, SUB_DEAL_TYPE_SELL, etc. (18 values) |
| `BMT5_ENUM_DEAL_REASON` | Deal execution reason | Client, Expert, SL, TP, Mobile (11 values) |
| `BMT5_ENUM_POSITION_REASON` | Why position opened | Client, Mobile, Web, Expert, SL, TP, SO (7 values) |
| `SymbolInfoDoubleProperty` | Symbol price properties | BID, ASK, POINT, SWAP_LONG, SWAP_SHORT (60 values) |
| `SymbolInfoIntegerProperty` | Symbol integer properties | DIGITS, SPREAD, TRADE_MODE, etc. (37 values) |
| `AccountInfoDoublePropertyType` | Account double properties | BALANCE, EQUITY, MARGIN, etc. (14 values) |

**Note:** Enum name prefixes indicate their usage context:

- `TMT5_*` / `ENUM_*_TF` - trading-function enums (order_send, order_calc_*)
- `BMT5_*` - base MT5 enums (positions, orders, historical data, reasons)
- `SUB_*` - subscription/streaming enums (real-time events)

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
FOUND 40 TYPES MATCHING 'Order':
-----------------------------------------------------------
    1. AllHistoryOrdersData
    2. HistoryOrderInfo
    3. OnTradeOrderInfo
    4. OpenedOrderInfo
    5. OpenedOrdersData
    6. OrderCalcMarginRequest
    7. OrderCheckRequest
    8. OrderCloseRequest
    9. OrderModifyRequest
   10. OrderSendRequest
   ...

> OpenedOrderInfo
===========================================================
TYPE: OpenedOrderInfo
===========================================================
FIELDS (24):
-----------------------------------------------------------
  #  1 index                          : uint32
  #  2 ticket                         : uint64
  #  3 price_current                  : double
  #  4 price_open                     : double
  #  5 stop_limit                     : double
  #  6 stop_loss                      : double
  #  7 take_profit                    : double
  #  8 volume_current                 : double
  #  9 volume_initial                 : double
  # 10 magic_number                   : int64
  # 11 reason                         : int32
  # 12 type                           : BMT5_ENUM_ORDER_TYPE
  # 13 state                          : BMT5_ENUM_ORDER_STATE
  # 14 time_expiration                : Timestamp
  # 15 time_setup                     : Timestamp
  # 16 time_done                      : Timestamp
  # 17 type_filling                   : BMT5_ENUM_ORDER_TYPE_FILLING
  # 18 type_time                      : BMT5_ENUM_ORDER_TYPE_TIME
  # 19 position_id                    : int64
  # 20 position_by_id                 : int64
  # 21 symbol                         : string
  # 22 external_id                    : string
  # 23 comment                        : string
  # 24 account_login                  : int64

> field magic
EXACT MATCH: field 'magic' found in:
-----------------------------------------------------------
    1. HistoryOrderInfo
    2. MqlTradeRequest
    3. OnTradeHistoryDealInfo
    4. OnTradeHistoryOrderInfo
    5. OnTradeOrderInfo
    6. OnTradePositionInfo
    7. PositionHistoryInfo

PARTIAL MATCHES (field contains 'magic'):
-----------------------------------------------------------
    1. MrpcMqlTradeRequest
    2. OpenedOrderInfo
    3. OrderHistoryData
    4. PositionInfo

> enum BMT5_ENUM_ORDER_STATE
===========================================================
ENUM: BMT5_ENUM_ORDER_STATE
===========================================================
  BMT5_ORDER_STATE_STARTED                 = 0
  BMT5_ORDER_STATE_PLACED                  = 1
  BMT5_ORDER_STATE_CANCELED                = 2
  BMT5_ORDER_STATE_PARTIAL                 = 3
  BMT5_ORDER_STATE_FILLED                  = 4
  BMT5_ORDER_STATE_REJECTED                = 5
  BMT5_ORDER_STATE_EXPIRED                 = 6
  BMT5_ORDER_STATE_REQUEST_ADD             = 7
  BMT5_ORDER_STATE_REQUEST_MODIFY          = 8
  BMT5_ORDER_STATE_REQUEST_CANCEL          = 9

> whereenum ENUM_ORDER_TYPE_TF
ENUM 'ENUM_ORDER_TYPE_TF' USED IN (3 fields):
===========================================================

  MrpcMqlTradeRequest:
    - order_type

  OrderCalcMarginRequest:
    - order_type

  OrderCalcProfitRequest:
    - order_type

> exit

[+] Goodbye!
```

---

## Implementation Details

The Protobuf Inspector uses Python reflection to:

1. Register all protobuf types at startup
2. Build in-memory indexes for:
   - Field names → Types mapping
   - Field types → Fields mapping
   - Enum names → Usage mapping
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
- **Complete coverage** - All types and enums from the scanned MT5 gRPC modules
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
> field ticket
EXACT MATCH: field 'ticket' found in:
-----------------------------------------------------------
    ...
    8. OpenedOrderInfo
    9. OrderCloseRequest
   ...

> OrderCloseRequest
===========================================================
TYPE: OrderCloseRequest
===========================================================
FIELDS (3):
-----------------------------------------------------------
  #  1 ticket                         : uint64
  #  2 volume                         : double
  #  5 slippage                       : int32

# Now you know:
# - Close via OrderCloseRequest (ticket, optional partial volume, slippage)
# - You get OrderCloseReply back — check returned_code == 10009 for success
#   (see RETURN_CODES_REFERENCE.md)
# - In practice, MT5Sugar.close_position(ticket) wraps all of this for you
```

---

## Troubleshooting

**Q: Type not found**

```
> MyType
[!] Type not found: MyType
    Did you mean: MqlTradeRequest, MqlTradeResult, ...
```

**A:** Use search with a partial name to find similar types

---

**Q: Multiple types match**

```
> OrderInfo
[!] Multiple types match 'OrderInfo':
    1. HistoryOrderInfo
    2. OnTradeHistoryOrderInfo
    3. OnTradeOrderInfo
    4. OpenedOrderInfo
```

**A:** Pick the specific one you mean (e.g. `OpenedOrderInfo` for a live pending/open order).

---

**Q: What's the difference between OpenedOrderInfo and OrderSendRequest?**

**A:** Use the inspector:

- `OpenedOrderInfo` - Information about an existing order (24 fields: state, times, type, etc.)
- `OrderSendRequest` - Request to create a new order (13 fields of order parameters)

Rule:

- `*Request` - Input for an API method (what you send)
- `*Reply` - Output from an API method (what you receive)
- `*Info` - Structured data about entities (position, order, deal, symbol)
- `*Data` - Payload data structures returned inside replies

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

## Command Quick Reference

```
BASIC COMMANDS:
  list               - Show all types
  list --request     - Show only Request types
  <TypeName>         - Inspect type structure
  search <text>      - Find types by name
  field <name>       - Find types with field
  enum <name>        - Show enum values

MORE COMMANDS:
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
