# PyMT5 Project Map

> Complete reference to project structure. Shows what is located where, what is user-facing vs internal, and how components are connected.

---

## 🗂️ Project Overview

```
PyMT5/
├── 📦 package/ - Core package (portable)
│   └── MetaRpcMT5/
│       ├── helpers/mt5_account.py (Layer 1 - Foundation)
│       ├── helpers/errors.py (Error handling & trade return codes)
│       └── (Protobuf definitions)
│   
│
├── 📦 src/pymt5/ - High-level API layers
│   ├── mt5_service.py (Layer 2 - Wrappers)
│   └── mt5_sugar.py (Layer 3 - Convenience)
│
├── 👤 User Code (Orchestrators, Examples)
├── 📝 Documentation
└── ⚙️ Configuration and build

External dependencies:
└── 🔌 gRPC & Protobuf (Python packages)
```

---

## 📦 Core API (Three-layer architecture)

**What:** Three-tier architecture for MT5 trading automation.

```
package/MetaRpcMT5/
├── helpers/
│   ├── mt5_account.py            <- LAYER 1: Low-level gRPC 🔥 FOUNDATION
│   │   └── Direct gRPC calls to MT5 terminal
│   │   └── Connection management with retry logic
│   │   └── Proto Request/Response handling
│   │   └── Built-in connection resilience
│   │   └── Independent Python package (portable)
│   │   └── Class: MT5Account
│   │
│   └── errors.py                 <- Error handling & trade result codes
│       └── NotConnectedError exception (connection errors)
│       └── ApiError wrapper (3-level: API/MQL/Trade)
│       └── Trade return code constants & helpers
│       └── Centralized error inspection methods
│
├── *_pb2.py                      <- Protobuf message definitions
├── *_pb2_grpc.py                 <- gRPC service stubs
├── mt5_term_api_*.py             <- MT5 API protocol definitions
└── __init__.py                   <- Package initialization

src/pymt5/
├── mt5_service.py                <- LAYER 2: Wrapper methods
│   └── Simplified signatures (no proto objects)
│   └── Type conversion (proto → Python types)
│   └── Direct data return
│   └── Extension methods for convenience
│   └── Class: MT5Service
│
└── mt5_sugar.py                  <- LAYER 3: Convenience layer 🔥
    └── Auto-normalization (volumes, prices)
    └── Risk management (CalculateVolume, BuyByRisk)
    └── Points-based methods (BuyLimitPoints, etc.)
    └── Batch operations (CloseAll, CancelAll)
    └── Snapshots (GetAccountSnapshot, GetSymbolSnapshot)
    └── Smart helpers (conversions, limits)
    └── Class: MT5Sugar

package/pyproject.toml            <- Package configuration (dependencies, metadata)
```

**Architecture flow:**
```
MT5Sugar → uses → MT5Service → uses → MT5Account → gRPC → MT5 Terminal
       ↓                ↓                    ↓
src/pymt5/       src/pymt5/         package/MetaRpcMT5/helpers/
```

**💡 Creating Your Own Project:**

For your own standalone project using PyMT5, you only need to import the `package` module:

```python
from MetaRpcMT5 import MT5Account
from MetaRpcMT5.helpers.errors import ApiError, check_retcode
```

The `package` module contains **everything you need to start**:

- ✅ All protobuf definitions (proto-generated code)
- ✅ gRPC stubs and service contracts
- ✅ MT5Account (Layer 1 - Foundation)
- ✅ Independent Python package (can be used without src/)

This makes the package **portable** and easy to integrate into any Python project!

**User decision:**

- **Building your own app:** Import `package` and use MT5Account directly
- **Learning/Examples:** Use the full PyMT5 repo with all 3 layers
- **95% of demo cases:** Start with `MT5Sugar` (highest level, easiest)
- **Need wrappers:** Move to `MT5Service` (without auto-normalization)
- **Need raw proto:** Move to `MT5Account` (full control)


### Built-in Reconnect Protection

**What:** All low-level gRPC calls in `MT5Account` have automatic reconnection logic.

**Two protection mechanisms:**

#### 1. Regular gRPC Calls (`execute_with_reconnect`)

All basic MT5Account methods (account info, trading operations, etc.) use built-in reconnection:

**How it works:**

- Detects gRPC `UNAVAILABLE` status (server unreachable)

- Detects terminal errors:

  - `TERMINAL_INSTANCE_NOT_FOUND`

  - `TERMINAL_REGISTRY_TERMINAL_NOT_FOUND`

- On error: waits 0.5 seconds, reconnects, retries the call

- Continues until success or cancellation

**What this means for you:**

- No manual reconnection needed
- Network hiccups handled automatically
- Terminal restarts recovered seamlessly

**Example:**

```python
# This call automatically reconnects if connection is lost
balance = await account.account_info_double(
    account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
)
# If connection drops: auto-reconnect → retry → return result
```

#### 2. Streaming Calls (`execute_stream_with_reconnect`)

Streaming methods (position updates, tick streams, trade events) have separate stream-specific protection:

**How it works:**

- Same error detection (UNAVAILABLE, terminal not found)
- Properly closes existing stream before reconnecting
- Reopens stream after reconnection
- Continues yielding data transparently

**What this means for you:**

- Stream interruptions handled automatically
- No data loss on reconnection
- Seamless continuation of real-time data

**Example:**

```python
# Stream automatically recovers from connection issues
async for trade in account.on_trade(cancellation_event):
    print(f"Trade: {trade}")
    # If connection drops: stream closes → reconnect → stream reopens → continues
```

**Important notes:**

- Both mechanisms require valid connection parameters (host/port or server_name)
- Reconnection uses the same credentials from initial connection
- Use `cancellation_event` to stop retry loops
- 0.5 second delay between retry attempts prevents server overload

---

## 👤 User Code (Your Trading Strategies)

### Orchestrators (examples/4_orchestrators/)

**What:** Ready-made trading strategy implementations.

```
examples/4_orchestrators/
├── 11_trailing_stop.py           <- Trailing stop (price following)
├── 12_position_scaler.py         <- Position scaling
├── 13_grid_trader.py             <- Grid trading (sideways markets)
├── 14_risk_manager.py            <- Risk manager
└── 15_portfolio_rebalancer.py    <- Portfolio rebalancing
```

**Purpose:** Educational examples showing complete strategy workflows:

- Entry logic (risk-based volume where applicable)
- Position monitoring with progress bars
- Exit management and cleanup
- Performance tracking (balance, equity, P/L)
- Configurable parameters via properties

**How to use:**

1. Study existing orchestrators
2. Copy one as a template
3. Modify for your strategy
4. Test on demo account

**How to run:**
```bash
python examples/main.py 11         # Trailing Stop
python examples/main.py trailing    # Same with alias
python examples/main.py scaler      # Position Scaler
python examples/main.py grid        # Grid Trader
python examples/main.py risk        # Risk Manager
python examples/main.py rebalancer  # Portfolio Rebalancer
```

**Documentation:**
- Orchestrator documentation files: See source code comments in each .py file
- Usage examples included directly in the Python files

---

### Examples (examples/)

**What:** Runnable examples demonstrating API usage at different layers.

**User interaction:** ✅ **Learning materials** - run to understand the API.

```
examples/
├── 0_common/                          <- Common utilities
│   ├── settings.json                  <- Connection configuration
│   ├── demo_helpers.py                <- Helper functions for demos
│   ├── progress_bar.py                <- Progress bar utilities
│   └── 16_protobuf_inspector.py       <- Protobuf structure inspector
│
├── 1_lowlevel/                        <- MT5Account examples (proto level) 🔥 FOUNDATION
│   ├── 01_general_operations.py       <- General operations (connection, account, symbols)
│   ├── 02_trading_operations.py       <- Trading operations (orders, positions)
│   └── 03_streaming_methods.py        <- Streaming methods (real-time subscriptions)
│
├── 2_service/                         <- MT5Service examples (wrapper level)
│   ├── 04_service_demo.py             <- Service API demonstration
│   └── 05_service_streaming.py        <- Service streaming methods
│
├── 3_sugar/                           <- MT5Sugar examples (convenience level)
│   ├── 06_sugar_basics.py             <- Sugar API basics (balance, prices)
│   ├── 07_sugar_trading.py            <- Trading (market/limit orders)
│   ├── 08_sugar_positions.py          <- Position management
│   ├── 09_sugar_history.py            <- History and statistics
│   └── 10_sugar_advanced.py           <- Advanced Sugar capabilities
│
├── 4_orchestrators/                   <- Strategy implementations
│   └── (see Orchestrators section above)
│
├── 5_usercode/                        <- User code sandbox
│   └── 17_usercode.py                 <- Your custom strategies
│
└── main.py                            <- Main entry point with menu
```

**How to run:**
```bash
# Low-level examples (MT5Account - FOUNDATION OF EVERYTHING)
python examples/main.py 1              # General operations
python examples/main.py lowlevel01     # Same with alias
python examples/main.py 2              # Trading operations
python examples/main.py 3              # Streaming methods

# Service examples (MT5Service - wrappers)
python examples/main.py 4              # Service API demo
python examples/main.py service        # Same with alias
python examples/main.py 5              # Service streaming methods

# Sugar examples (MT5Sugar - convenience API)
python examples/main.py 6              # Sugar basics
python examples/main.py sugar06        # Same with alias
python examples/main.py 7              # Sugar trading
python examples/main.py 8              # Sugar positions
python examples/main.py 9              # Sugar history
python examples/main.py 10             # Advanced Sugar

# UserCode (your code)
python examples/main.py 17             # Custom strategies
python examples/main.py usercode       # Same with alias

# Interactive menu
python examples/main.py                # Show menu with all options
```

---

### main.py (examples/)

**What:** Main entry point that routes commands to corresponding examples/orchestrators.

**User interaction:** 📋 **Runner + Documentation** - launches everything.

```
main.py
├── main()                              <- Entry point, parses arguments
├── execute_command()                   <- Maps aliases to runners
├── main_loop()                         <- Interactive menu loop
└── Documentation in header             <- Full command reference
```

**How it works:**

```
python main.py grid
    ↓
main(args)  # args[1] = "grid"
    ↓
execute_command("grid")
    ↓
import and run grid orchestrator
    ↓
GridTrader.main()
```

**Purpose:**

- Single entry point for all runnable code
- Command routing with aliases (grid, trailing, etc.)
- Interactive menu mode when no arguments provided
- Helpful error messages for unknown commands
- Ctrl+C handling for graceful shutdown

**Available commands:** See header comment in `main.py` for full list.

---

### Helpers (examples/0_common/)

**What:** Utilities for examples and orchestrators.

```
examples/0_common/
├── settings.json                 <- MT5 connection configuration
├── demo_helpers.py               <- Connection setup & error handling
├── progress_bar.py               <- Visual progress bars
└── 16_protobuf_inspector.py      <- Protobuf structure inspector (runnable)
```

**demo_helpers.py:**
```python
# Load configuration from settings.json
settings = load_settings()

# Create and connect to MT5
account = await create_and_connect_mt5(settings)

# Error handling helpers
print_if_error(response)
check_retcode(response)
print_success("Order placed successfully")
```

**progress_bar.py:**
```python
# Visual countdown during orchestrator operation
bar = TimeProgressBar(
    total_seconds=60,
    message="Monitoring positions"
)
# Update progress in a loop
bar.update(elapsed_seconds)
# Finish when done
bar.finish()
```

**settings.json structure:**
```json
{
  "user": 12345678,
  "password": "YourPassword",
  "host": "mt5.mrpc.pro",
  "port": 443,
  "grpc_server": "mt5.mrpc.pro:443",
  "mt_cluster": "MetaQuotes-Demo",
  "test_symbol": "EURUSD",
  "test_volume": 0.01
}
```

**ProtobufInspector:**
```python
# Inspect protobuf structures for debugging
python examples/main.py 16
python examples/main.py inspect
```

---

## 📝 Documentation (docs/)

**What:** Complete API and strategy documentation.

**User interaction:** 📖 **Read first!** Comprehensive reference.

```
docs/
├── index.md                           <- Home page - project introduction
│
├── mkdocs.yml                         <- MkDocs configuration
├── styles/custom.css                  <- Custom theme (ocean aurora)
├── javascripts/ux.js                  <- Interactive features
│
├── All_Guides/                        <- Guides
│   ├── MT5_For_Beginners.md           <- 🔥 Demo account registration
│   ├── GETTING_STARTED.md             <- 🔥 Start here! Setup and first steps
│   ├── Your_First_Project.md          <- Your first project
│   ├── GLOSSARY.md                    <- 🔥 Terms and definitions
│   ├── GRPC_STREAM_MANAGEMENT.md      <- Managing streaming subscriptions
│   ├── RETURN_CODES_REFERENCE.md      <- Proto return code reference
│   ├── ENUMS_USAGE_REFERENCE.md       <- Enums and constants guide
│   ├── PROTOBUF_INSPECTOR_GUIDE.md    <- Protobuf inspector tool
│   └── USERCODE_SANDBOX_GUIDE.md      <- How to write custom strategies
│
├── PROJECT_MAP.md                     <- 🔥 This file - complete structure
│
├── API_Reference/                     <- Concise API documentation
│   ├── MT5Account.md                  <- 🔥 Layer 1 API (foundation) → from package/MetaRpcMT5/helpers/mt5_account.py
│   ├── MT5Service.md                  <- Layer 2 API → from src/pymt5/mt5_service.py
│   └── MT5Sugar.md                    <- Layer 3 API → from src/pymt5/mt5_sugar.py
│
├── MT5Account/                        <- 🔥 FOUNDATION - Detailed Layer 1 documentation
│   ├── MT5Account.Master.Overview.md  <- 🔥 Complete API reference
│   │
│   ├── 1. Account_Information/        <- Account methods (~4 files)
│   │   ├── Account_Information.Overview.md  <- Section overview
│   │   ├── account_info_double.md     <- Get account double parameters
│   │   ├── account_info_integer.md    <- Get account integer parameters
│   │   ├── account_info_string.md     <- Get account string parameters
│   │   ├── account_summary.md         <- Complete account summary
│   │   └── 💡 Each example linked with examples/1_lowlevel
│   │
│   ├── 2. Symbol_Information/         <- Symbol/market data methods (~13 files)
│   │   ├── Symbol_Information.Overview.md  <- Section overview
│   │   ├── symbol_info_tick.md        <- Current symbol tick
│   │   ├── symbol_info_double.md      <- Symbol double parameters
│   │   ├── symbols_total.md           <- Total symbols count
│   │   ├── symbol_exist.md            <- Check if symbol exists
│   │   ├── symbol_is_synchronized.md  <- Check synchronization
│   │   └── ...                        <- And other symbol methods
│   │   └── 💡 Examples in examples/1_lowlevel
│   │
│   ├── 3. Positions_Orders/           <- Position/order methods (~6 files)
│   │   ├── Positions_Orders.Overview.md  <- Section overview
│   │   ├── opened_orders.md           <- List of open orders
│   │   ├── positions_total.md         <- Total positions count
│   │   ├── positions_history.md       <- Position history
│   │   └── ...                        <- And other position methods
│   │   └── 💡 Examples in examples/1_lowlevel
│   │
│   ├── 4. Market_Depth/               <- Market depth methods (~3 files)
│   │   ├── Market_Depth.Overview.md   <- Section overview
│   │   ├── market_book_add.md         <- Subscribe to market depth
│   │   ├── market_book_get.md         <- Get market depth data
│   │   └── market_book_release.md     <- Unsubscribe from market depth
│   │
│   ├── 5. Trading_Operations/         <- Trading operation methods (~7 files)
│   │   ├── Trading_Operations.Overview.md  <- Section overview
│   │   ├── order_send.md              <- Send order (main method)
│   │   ├── order_check.md             <- Check order before sending
│   │   ├── order_calc_margin.md       <- Calculate margin
│   │   ├── order_calc_profit.md       <- Calculate profit
│   │   ├── order_close.md             <- Close position
│   │   ├── order_modify.md            <- Modify order/position
│   │   └── 💡 Examples in examples/1_lowlevel/02_trading_operations.py
│   │
│   ├── 6. Streaming_Methods/          <- Real-time subscription methods (~5 files)
│   │   ├── Streaming_Methods.Overview.md  <- Section overview
│   │   ├── on_symbol_tick.md          <- Subscribe to symbol ticks
│   │   ├── on_trade.md                <- Subscribe to trade events
│   │   ├── on_position_profit.md      <- Subscribe to profit changes
│   │   ├── on_trade_transaction.md    <- Subscribe to trade transactions
│   │   └── ...                        <- And other streaming methods
│   │   └── 💡 Stream management examples in All_Guides/GRPC_STREAM_MANAGEMENT
│   │
│   └── HOW_IT_WORK/                   <- Detailed algorithm explanations
│       ├── 1. Account_information_HOW/
│       ├── 2. Symbol_information_HOW/
│       ├── 3. Position_Orders_Information_HOW/
│       ├── 4. Market_Depth(DOM)_HOW/
│       ├── 5. Trading_Operations_HOW/
│       └── 6. Streaming_Methods_HOW/
│
├── MT5Service/                        <- Service level method documentation
│   ├── MT5Service.Overview.md          <- 🔥 Complete Service API reference
│   ├── 1. Account_Information.md      <- Account helper methods
│   ├── 2. Symbol_Information.md       <- Symbol helper methods
│   ├── 3. Positions_Orders.md         <- Position/order helper methods
│   ├── 4. Market_Depth.md             <- Market depth helper methods
│   ├── 5. Trading_Operations.md       <- Trading helper methods
│   └── 6. Streaming_Methods.md        <- Streaming helper methods
│
└── MT5Sugar/                          <- Sugar level method documentation
    ├── MT5Sugar.Master.Overview.md     <- 🔥 Complete Sugar API reference
    │
    ├── 1. Connection/                  <- Connection methods (~3 files)
    │   ├── quick_connect.md            <- Quick connection
    │   ├── is_connected.md             <- Check connection
    │   └── ping.md                    <- Connection test
    │
    ├── 2. Account_Properties/          <- Account properties (~7 files)
    │   ├── get_balance.md              <- Get balance
    │   ├── get_equity.md               <- Get equity
    │   ├── get_free_margin.md          <- Free margin
    │   └── ...                        <- And other account methods
    │
    ├── 3. Prices_Quotes/               <- Prices and quotes (~5 files)
    │   ├── get_bid.md                  <- Get Bid
    │   ├── get_ask.md                  <- Get Ask
    │   ├── get_spread.md               <- Get spread
    │   └── ...                        <- And other price methods
    │
    ├── 4. Simple_Trading/              <- Simple trading (~6 files)
    │   ├── buy_market.md               <- Buy at market
    │   ├── sell_market.md              <- Sell at market
    │   ├── buy_limit.md                <- Buy Limit order
    │   └── ...                        <- And other simple orders
    │
    ├── 5. Trading_With_SLTP/           <- Trading with SL/TP (~4 files)
    │   ├── buy_market_with_sltp.md     <- Buy with SL/TP
    │   ├── sell_market_with_sltp.md    <- Sell with SL/TP
    │   └── ...                        <- And other orders with SL/TP
    │
    ├── 6. Position_Management/         <- Position management (~6 files)
    │   ├── close_position.md           <- Close position
    │   ├── close_all_positions.md      <- Close all positions
    │   ├── modify_position_sltp.md     <- Modify SL/TP
    │   └── ...                        <- And other management methods
    │
    ├── 7. Position_Information/        <- Position information (~7 files)
    │   ├── has_open_position.md        <- Has open position
    │   ├── count_open_positions.md     <- Count positions
    │   ├── get_position_by_ticket.md   <- Get position by ticket
    │   └── ...                        <- And other information methods
    │
    ├── 8. History_Statistics/          <- History and statistics (~3 files)
    │   ├── get_deals.md                <- Get deals
    │   ├── get_profit.md               <- Get profit
    │   ├── get_daily_stats.md          <- Daily statistics
    │   └── ...                        <- And other history methods
    │
    ├── 9. Symbol_Information/          <- Symbol information (~4 files)
    │   ├── get_symbol_info.md          <- Complete symbol information
    │   ├── get_all_symbols.md          <- All available symbols
    │   └── ...                        <- And other symbol methods
    │
    └── 10. Risk_Management/            <- Risk management (~4 files)
        ├── calculate_position_size.md  <- Calculate position size
        ├── can_open_position.md        <- Can open position
        └── ...                        <- And other risk methods
```

**Structure:**

- Each method has its own `.md` file with examples
- Overview files (`*.Overview.md`, `*.Master.Overview.md`) provide navigation
- `HOW_IT_WORK/` folders explain algorithms step by step
- Links between related methods
- Usage examples in each file

**🔥 Important about MT5Account:**

- **FOUNDATION OF EVERYTHING** - all methods here are the foundation
- Each documentation example is linked with real code
- Understanding MT5Account is critical for effective use of MT5Service and MT5Sugar

---

## 🔌 gRPC & Proto (Python packages)

**What:** Protocol Buffer and gRPC libraries for communication with MT5 terminal.

**User interaction:** 📋 **Reference only** - managed via pip.

**Key dependencies:**

- `grpcio` - gRPC client
- `grpcio-tools` - gRPC tools for Python
- `protobuf` - Protocol Buffers runtime

**Package structure:**

```
package/
└── MetaRpcMT5/
    ├── helpers/
    │   ├── __init__.py
    │   ├── mt5_account.py      <- Layer 1 implementation
    │   └── errors.py           <- Error handling utilities
    │
    ├── __init__.py             <- Package initialization
    ├── *_pb2.py                <- Generated protobuf code
    ├── *_grpc_pb2.py           <- Generated gRPC stubs
    └── mt5_term_api_*.py       <- MT5 API protocol definitions


```

**How it works:**

1. `package/` is an independent Python package
2. Contains both proto-generated code and MT5Account implementation
3. Can be imported separately as a package
4. MT5Service and MT5Sugar import from package
5. All layers use proto-generated types from package

**Proto-generated types:**

- `mt5_term_api_*` - Trading API types
- Request/Response message types
- Enum definitions
- Service contracts

**Purpose:**

- Define gRPC service contracts
- Type-safe communication with MT5 terminal
- Used by MT5Account layer
- Hidden by MT5Service and MT5Sugar layers

---

## 📊 Component Interaction Diagram

```
YOUR CODE (User)
  ├─ Orchestrators (strategy implementations)
  └─ Examples (learning materials)
                  │
                  │ uses
                  ↓
MT5Sugar (Layer 3 - Convenience)
  📍 Location: src/pymt5/mt5_sugar.py
  ├─ Auto-normalization
  ├─ Risk management
  ├─ Points-based methods
  └─ Batch operations
                  │
                  │ uses
                  ↓
MT5Service (Layer 2 - Wrappers)
  📍 Location: src/pymt5/mt5_service.py
  ├─ Direct data return
  ├─ Type conversion
  └─ Simplified signatures
                  │
                  │ uses
                  ↓
MT5Account (Layer 1 - Low level) 🔥 FOUNDATION
  📍 Location: package/MetaRpcMT5/helpers/mt5_account.py
  ├─ Proto Request/Response
  ├─ gRPC communication
  ├─ Connection management
  ├─ Auto-reconnection
  └─ Independent Python package (portable)
                  │
                  │ gRPC
                  ↓
MT5 Gateway (mt5term) or MT5 Terminal
  └─ MetaTrader 5 with gRPC server
```

---

## 🔍 File Naming Conventions

### Core API (Multi-location)

**Layer 1 (Foundation):**

- `package/MetaRpcMT5/helpers/mt5_account.py` - Low-level gRPC (independent package)
- `package/MetaRpcMT5/helpers/errors.py` - Error handling utilities

**Protobuf (Generated):**

- `package/MetaRpcMT5/*_pb2.py` - Protobuf message definitions
- `package/MetaRpcMT5/*_pb2_grpc.py` - gRPC service stubs

**Layers 2-3 (High-level wrappers):**

- `src/pymt5/mt5_service.py` - Wrapper methods
- `src/pymt5/mt5_sugar.py` - Convenience API

**Package configuration:**

- `package/pyproject.toml` - Package dependencies and metadata

### User Code (examples/)

- `NN_name.py` - Numbered examples and strategies
- `main.py` - Entry point and command router
- `*_helpers.py` - Utilities (demo_helpers, progress_bar)
- `settings.json` - Configuration

### Documentation (docs/)

- `*.Master.Overview.md` - Complete category overviews
- `*.Overview.md` - Section overviews
- `MethodName.md` - Individual method documentation
- `*_HOW.md` - Algorithm explanations

---

## 📁 What to Modify vs What to Leave Alone

### ✅ MODIFY (User Code)

**Recommended starting point:**
```
examples/5_usercode/17_usercode.py  <- 🔥 SANDBOX - start writing your code here!
                                       All 3 API levels already initialized and ready.
                                       Run: python main.py 17
```

**Other files for modification:**
```
examples/4_orchestrators/     <- Copy and customize for your strategies
examples/1_lowlevel/          <- Add your low-level examples
examples/2_service/           <- Add your service examples
examples/3_sugar/             <- Add your sugar examples
examples/5_usercode/          <- Create your custom files alongside 17_usercode.py
examples/0_common/settings.json  <- Configure for your MT5 terminal/gateway
examples/main.py              <- Add new command routing if needed
README.md                     <- Update with your changes
```

### 📖 READ (Core API)

```
package/MetaRpcMT5/helpers/mt5_account.py  <- Use but don't modify (import and call) 🔥 FOUNDATION
package/MetaRpcMT5/helpers/errors.py       <- Use but don't modify
src/pymt5/mt5_service.py        <- Use but don't modify
src/pymt5/mt5_sugar.py          <- Use but don't modify
docs/                           <- Reference documentation
```

### 🔒 LEAVE ALONE (Generated/Build)

```
.vscode/                       <- VS Code settings
package/MetaRpcMT5/*_pb2.py    <- Auto-generated protobuf code
package/MetaRpcMT5/*_pb2_grpc.py  <- Auto-generated gRPC stubs
docs/site/                     <- Built documentation (auto-generated by MkDocs)
docs/styles/                   <- Documentation theme (don't change without understanding)
docs/javascripts/              <- Documentation scripts (don't change without understanding)
__pycache__/                   <- Python bytecode cache (auto-generated)
*.pyc                          <- Python compiled files (auto-generated)
```

---

## 👤 Project Philosophy

**Goal:** Make MT5 trading automation accessible through progressive complexity.

**Three-tier design:**

1. **Low level (MT5Account):** Full control, proto/gRPC 🔥 **FOUNDATION OF EVERYTHING**
2. **Wrappers (MT5Service):** Simplified method calls
3. **Convenience (MT5Sugar):** Auto-everything, batteries included

**User code:**

- **Orchestrators:** Ready-made strategy templates
- **Examples:** Learning materials at all levels

---

## 🛠️ Troubleshooting

### Installation Issues

```bash
# Clean and reinstall
pip uninstall MetaRpcMT5
pip install --upgrade pip

# Install package in development mode
pip install -e package/

# Or install specific dependencies
pip install grpcio grpcio-tools protobuf

# Check Python version
python --version   # Should be 3.8 or higher
```

### Runtime Issues

```
1. Always test on demo account first
2. Check return codes (10009 = success, 10031 = connection error)
3. Monitor console output for errors
4. Use retry logic for intermittent issues
5. Verify broker allows your strategy type (hedging, etc.)
6. Check that MT5 terminal is running and gRPC server is active
```

### Common Errors

```python
# Connection error
Error: ConnectExceptionMT5
Fix: Check MT5 terminal is running, verify settings.json

# Import error
Error: ModuleNotFoundError: No module named 'MetaRpcMT5'
Fix: pip install -e package/ (from project root)

# Return code 10004 (invalid request)
Fix: Check order parameters (volume, price, symbol)

# Return code 10031 (connection timeout)
Fix: Check network, verify grpc_server in settings.json
```

---

## 📊 Performance Considerations

### Connection Management
- Single gRPC connection shared across operations
- Built-in auto-reconnection handles temporary failures
- Retry logic with exponential backoff (1s → 2s → 4s)

### Rate Limiting
- 3-second delays between order placements (demo examples)
- Gateway may enforce additional rate limits
- Adjust delays based on broker requirements

### Resource Usage
- Async/await everywhere for non-blocking I/O
- Proper cleanup in try/finally blocks
- Context managers for resource management

---

## 📋 Best Practices

### Code Organization
```
✅ DO: Separate concerns (analysis, execution, monitoring)
✅ DO: Add comprehensive error handling
✅ DO: Document your strategy logic clearly
✅ DO: Use progress bars for long operations
✅ DO: Use async/await for concurrent operations

❌ DON'T: Mix strategy logic with API calls
❌ DON'T: Use time.sleep without context
❌ DON'T: Ignore return codes
❌ DON'T: Test on live accounts without extensive demo testing
```

### Strategy Development
```
✅ DO: Start with existing orchestrator as template
✅ DO: Test each component separately
✅ DO: Log all trading decisions and outcomes
✅ DO: Use demo accounts for development
✅ DO: Implement proper risk management

❌ DON'T: Over-optimize on limited data
❌ DON'T: Ignore edge cases and failures
❌ DON'T: Use fixed lots without risk calculation
❌ DON'T: Deploy without backtesting and forward testing
```

### Python-Specific Best Practices
```
✅ DO: Use type hints for better IDE support
✅ DO: Follow PEP 8 style guidelines
✅ DO: Use dataclasses for data structures
✅ DO: Use f-strings for string formatting
✅ DO: Use pathlib for file paths

❌ DON'T: Use mutable default arguments
❌ DON'T: Catch Exception without re-raising
❌ DON'T: Use global variables in strategies
❌ DON'T: Forget to close streams and connections
```

---

## 📦 Project File Tree

```
PyMT5/
│
├── .github/                           <- GitHub configuration
├── .vscode/                           <- VS Code settings
│   ├── launch.json
│   └── settings.json
│
├── docs/                              <- Documentation (see Documentation section above)
│   ├── index.md
│   ├── mkdocs.yml
│   ├── All_Guides/
│   ├── API_Reference/
│   ├── MT5Account/
│   ├── MT5Service/
│   ├── MT5Sugar/
│   ├── Guide_Images/
│   ├── includes/
│   ├── javascripts/
│   └── styles/
│
├── examples/                          <- Examples and user code (see Examples section above)
│   ├── 0_common/
│   │   ├── __init__.py
│   │   ├── settings.json              <- 🔥 Connection configuration
│   │   ├── demo_helpers.py
│   │   ├── progress_bar.py
│   │   └── 16_protobuf_inspector.py
│   │
│   ├── 1_lowlevel/                    <- 🔥 FOUNDATION examples
│   │   ├── __init__.py
│   │   ├── 01_general_operations.py
│   │   ├── 02_trading_operations.py
│   │   └── 03_streaming_methods.py
│   │
│   ├── 2_service/
│   │   ├── __init__.py
│   │   ├── 04_service_demo.py
│   │   └── 05_service_streaming.py
│   │
│   ├── 3_sugar/
│   │   ├── __init__.py
│   │   ├── 06_sugar_basics.py
│   │   ├── 07_sugar_trading.py
│   │   ├── 08_sugar_positions.py
│   │   ├── 09_sugar_history.py
│   │   └── 10_sugar_advanced.py
│   │
│   ├── 4_orchestrators/
│   │   ├── 11_trailing_stop.py
│   │   ├── 12_position_scaler.py
│   │   ├── 13_grid_trader.py
│   │   ├── 14_risk_manager.py
│   │   └── 15_portfolio_rebalancer.py
│   │
│   ├── 5_usercode/
│   │   └── 17_usercode.py             <- 🔥 START HERE for your code
│   │
│   ├── __init__.py
│   └── main.py                        <- 🔥 Main entry point
│
├── package/                           <- Core package (portable)
│   └── MetaRpcMT5/                    <- Package root
│       ├── helpers/
│       │   ├── __init__.py
│       │   ├── mt5_account.py         <- 🔥 FOUNDATION - Layer 1
│       │   └── errors.py              <- Error handling
│       │
│       ├── __init__.py
│       ├── *_pb2.py                   <- Generated protobuf code (11 files)
│       └── *_pb2_grpc.py              <- Generated gRPC stubs (11 files)
│                 
│
├── src/                               <- High-level API layers
│   └── pymt5/
│       ├── __init__.py
│       ├── mt5_service.py             <- Layer 2 - Wrappers
│       └── mt5_sugar.py               <- Layer 3 - Convenience
│
├── .gitignore                         <- Git ignore patterns
├── mkdocs.yml                         <- MkDocs configuration
└── README.md                          <- Project readme
```

---

> 💡 **Remember:** This is an educational project. All orchestrators are demonstration examples, not production-ready trading systems. Always test on demo accounts, thoroughly understand the code, and implement proper risk management before considering live trading.

---

"Trade safely, code cleanly, and may your gRPC connections always be stable."
