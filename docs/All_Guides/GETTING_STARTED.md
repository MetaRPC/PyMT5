# Getting Started with PyMT5

> **Welcome to PyMT5** - a comprehensive educational project for learning MT5 trading automation from scratch using Python.

---

## Prerequisites and Installation

Before starting work with PyMT5, you need to set up your development environment.

### Step 1: Install Python 3.8+

PyMT5 requires Python version 3.8 or higher.

**Download and install:**

- **Official website:** [Python Downloads](https://www.python.org/downloads/)
- Choose the installer for your platform
- **Important for Windows:** Check "Add Python to PATH" during installation

**Verify installation:**

```bash
python --version
# Should show: Python 3.8.x or higher
```

---

### Step 2: Install Code Editor

**Visual Studio Code (Recommended):**

- **Download:** [VS Code](https://code.visualstudio.com/)

- **Extensions to install:**

  - Python (official Python extension from Microsoft)
  - Pylance (Python language server)
  - Python Test Explorer (optional)

**PyCharm (Alternative):**

- **Download:** [PyCharm by JetBrains](https://www.jetbrains.com/pycharm/)

- Professional IDE for Python with advanced features

**You can also use:**

- Vim/Neovim with python plugins
- Sublime Text
- Any text editor + command line

---

### Step 3: Clone the Repository

Clone the PyMT5 project from GitHub:

```bash
git clone https://github.com/MetaRPC/PyMT5
cd PyMT5
```

**If you don't have Git installed:**

- Download from [git-scm.com](https://git-scm.com/)
- Or download the project as ZIP from GitHub and extract

---

### Step 4: Understanding the Connection Flow

PyMT5 connects to the MT5 terminal via **gRPC gateway**.

**Connection flow:**
```
PyMT5 -> gRPC -> mt5term Gateway -> MT5 Terminal
```

**What is mt5term Gateway?**

- External gateway process that bridges PyMT5 with the MT5 terminal
- Handles connection pooling and session management
- Connection settings are specified in `examples/0_common/settings.json`

### 📝 Configuration File: settings.json

- Before starting work, let's specify your actual credentials in the configuration file.
- It's better to use a Demo account for learning.


```json
{
  "user": 591129415,
  "password": "IpoHj17tYu67@",
  "grpc_server": "mt5.mrpc.pro:443",
  "mt_cluster": "FxPro-MT5 Demo",
  "test_symbol": "EURUSD"
}
```

**Configuration parameters explanation:**

| Parameter | Description | Example |
|-----------|-------------|---------|
| **user** | Your MT5 account login number | `591129415` |
| **password** | Your MT5 account password (master password) | `"YourPassword"` |
| **mt_cluster** | MT5 server name from your broker | `"FxPro-MT5 Demo"` |
| **grpc_server** | Full gRPC server address (host:port) | `"mt5.mrpc.pro:443"` |
| **test_symbol** | Default trading symbol for examples | `"EURUSD"` |

**Important notes:**

- **user, password, mt_cluster** - These are your MT5 account credentials
- **grpc_server** - Provided by the MetaRPC team
- **test_symbol** - Change to your preferred trading symbol

---

## ➕ MT5 Account Setup

If you don't have an MT5 demo account yet or need help creating one, refer to the beginner's guide:

**[MT5 for Beginners - Creating Demo Account](MT5_For_Beginners.md)**

This guide covers:

- Downloading and installing MT5 terminal
- Step-by-step demo account creation
- Understanding master password and investor password
- Choosing a broker (optional)

---

## About the Project

This project is a **demonstration of capabilities** of our team's gateway for reproducing methods and functionality. It is designed to help you build your own trading logic system in the future.

We will guide you through all major aspects - from basic manual trading to a fully customizable algorithmic trading system. This journey will reveal the full potential of your acquired knowledge and fundamental understanding of trading and markets.

**What you will learn:**

- What gRPC methods do and how to use them directly
- How methods can be modified for your needs
- How to optimize your Python code for performance
- How to create convenient input/output systems
- How to effectively track positions by symbols
- How to build intelligent risk management systems
- How to work with Python asyncio for real-time streaming

**All we ask from you:**

> **The desire to learn, learn, and learn again.** In the end, this will lead to significant results and, most importantly, to a solid foundation of knowledge in algorithmic trading with Python.

---

## 🏗️ Project Architecture: Three-Tier System

The project consists of **three interconnected layers** in the `src/pymt5/` and `package/helpers/` directories, each building upon the previous one. Understanding this chain is key to mastering PyMT5.

### 🔹 Tier 1: MT5Account - Low-Level gRPC Foundation

**What it is:** Direct gRPC calls to the MT5 terminal - the absolute foundation of everything.

**[MT5Account Master Overview](../MT5Account/MT5Account.Master.Overview.md)**

**File:** `package/helpers/mt5_account.py` (2100+ lines)

- Raw protocol buffer messages and gRPC communication
- Maximum control and flexibility over each request/response
- **All other tiers use this internally**
- Automatic reconnection with exponential backoff
- **42 async methods**, covering all MT5 operations
- **Best for:** Advanced users who need granular control

**Key features:**

- Async/await based API
- Automatic reconnection on transient errors
- Built-in retry logic for network failures
- Session management with UUID tracking

**Two-Level Documentation:**

For each MT5Account methods, **two types of documentation** are available:

1. **Main reference** - complete method description with all input/output parameters and enums
   - Example: `docs/MT5Account/2. Symbol_Information/symbol_info_double.md`

2. **HOW_IT_WORK** - detailed step-by-step explanation with live code examples
   - Example: `docs/MT5Account/HOW_IT_WORK/2. Symbol_Information_HOW/symbol_info_double_HOW.md`
   - Line-by-line breakdown of actual code from demo files
   - Detailed comments for each step

This two-level approach allows you to quickly find reference information OR deeply understand how the method works internally.

### 🔸 Tier 2: MT5Service - Selective Convenience Layer

**What it is:** Mid-level wrapper that provides value-added methods on top of MT5Account.

**[MT5Service Overview](../MT5Service/MT5Service.Overview.md)**

**File:** `src/pymt5/mt5_service.py` (1200+ lines)

**Primary purpose:** Architectural middleware layer for MT5Sugar. MT5Service exists primarily to serve as a foundation for high-level MT5Sugar operations.

**Reality check:** Not all 36 methods add the same value:

- ✅ **11 HIGH/VERY HIGH value methods** - Aggregate multiple RPC calls, complex protobuf unpacking, datetime conversions, create structured dataclasses
- ⚪ **26 NONE/LOW value methods** - Direct pass-through or simple single-field extraction

**Key insight:** Since MT5Account already provides async methods with unpacked protobuf values, MT5Service's direct usage value comes from:

- Methods that **aggregate multiple calls** (e.g., `get_account_summary()` - combines 5 RPC calls)
- Methods that **create rich dataclasses** (e.g., `check_order()` - extracts deeply nested structures)
- Methods with **datetime conversions** (e.g., `get_symbol_tick()` - unix timestamp → datetime)


### 🔺 Tier 3: MT5Sugar - High-Level Helpers

**What it is:** Syntactic sugar and helper methods for maximum productivity.

**[MT5Sugar Overview](../MT5Sugar/MT5Sugar.Master.Overview.md)**

**File:** `src/pymt5/mt5_sugar.py` (2100+ lines)

- One-line operations for common tasks
- Smart defaults and automatic parameter inference
- Risk-based position size calculation
- SL/TP calculation based on pips
- Most intuitive and beginner-friendly
- **Best for:** Quick prototyping and simple strategies

**Key features:**

- `buy_market(symbol, volume)` - one line to open a position
- `calculate_position_size(symbol, risk_percent, sl_pips)` - automatic volume calculation by risk
- `buy_market_with_pips(symbol, volume, sl_pips, tp_pips)` - open with SL/TP in pips
- `get_balance()`, `get_equity()` - async methods for account information
- `close_all_positions()` - emergency exit

---

### ⚙️ Understanding the Chain

This three-tier chain represents the evolution from low-level control to high-level convenience:

```
MT5Sugar (easiest, highest abstraction)
    " uses
MT5Service (convenient wrappers)
    " uses
MT5Account (raw gRPC, foundation)
    " communicates with
MT5 Terminal (via gateway)
```

**Each overview document includes:**

- Detailed method descriptions with parameters
- Return types and error handling patterns
- Usage examples and best practices
- Common patterns and pitfalls to avoid
- Python-specific guidance (asyncio, type hints, dataclasses)

---

### ℹ️ Recommended Learning Paths

**Path A: For Python Developers (Bottom-Up Approach)**

If you have experience with Python and want to understand everything deeply:

1. **Start with MT5Account** - Study the gRPC foundation and async patterns
2. **Move to MT5Service** - Understand convenient wrappers
3. **Finish with MT5Sugar** - Appreciate high-level abstractions

This path gives you full control and deep understanding.

**Path B: For Traders (Top-Down Approach)**

If you're new to trading automation and want quick results:

1. **Start with MT5Sugar** - Easy, intuitive methods for quick trading
2. **Move to MT5Service** - Learn more advanced patterns as needed
3. **Deep dive into MT5Account** - Understand the foundation for full control

This path allows you to start trading quickly, leaving room for growth.

---

## Demo Examples

You can explore demo files that showcase various aspects of the SDK. These files are organized by complexity level and are located in the `examples/` folder.

**Each file includes inline code comments explaining what each operation does.**

### examples/0_common/ (Common Utilities)

Helper utilities and configuration:

- **demo_helpers.py** - Connection helper, config loading, error formatting
- **settings.json** - Configuration file (credentials, server)
- **protobuf_inspector.py** - Interactive protobuf types inspector (run: `python main.py inspect`)

### Ⅰ examples/1_lowlevel/ (MT5Account - Low Level)

Protobuf/gRPC methods - full control, maximum flexibility:

- **01_general_operations.py** - Information methods (account, symbols, positions, ticks)
- **02_trading_operations.py** - Trading operations (calculations, validation, orders)
- **03_streaming_methods.py** - Streaming methods (real-time ticks, deals, positions)

### Ⅱ examples/2_service/ (MT5Service - Mid Level)

Python wrappers over protobuf - native types, more convenient to work with:

- **04_service_demo.py** - Service API wrappers (account, symbols, positions, orders)
- **05_service_streaming.py** - Service API streaming methods (ticks, deals, profits)

### Ⅲ examples/3_sugar/ (MT5Sugar - High Level)

High-level API - maximum simplification, one line of code:

- **06_sugar_basics.py** - Basics: connection, balance, prices
- **07_sugar_trading.py** - Trading: market/pending orders, SL/TP
- **08_sugar_positions.py** - Positions: queries, modification, closing
- **09_sugar_history.py** - History: deals, profit over period
- **10_sugar_advanced.py** - Advanced: risk management, symbol info, helpers

### Ⅳ examples/4_orchestrators/ (Strategies)

Full-fledged trading strategies - examples of complex automation:

- **11_trailing_stop.py** - Automatic trailing stop manager
- **12_position_scaler.py** - Position scaling
- **13_grid_trader.py** - Grid trading for sideways market
- **14_risk_manager.py** - Automatic risk management
- **15_portfolio_rebalancer.py** - Portfolio rebalancing

### Ⅴ examples/5_usercode/

Sandbox for your custom code:

- **17_usercode.py** - Template file for your own trading logic

**[User Code Sandbox Guide](USERCODE_SANDBOX_GUIDE.md)**

---

## Running Examples with main.py

### What is main.py?

`examples/main.py` is the **single entry point** for all PyMT5 demo examples. It works as a dispatcher that:

1. **Runs any example** by number or readable name (alias)
2. **Manages connection** to MT5 via gRPC (creation, validation, closing)
3. **Loads configuration** from `0_common/settings.json` (credentials, server)
4. **Ensures clean exit** (graceful shutdown, connection closing)
5. **Shows interactive menu** for example selection (if run without parameters)

**Benefits of centralized main.py:**

- No need to copy connection code into each example
- All examples use one configuration
- Easy to switch between examples
- Automatic error handling and cleanup

---

### 🏁 Two Ways to Run

#### Method 1: Interactive Menu (recommended for learning)

Run without parameters - a menu with all available examples will appear:

```bash
cd examples
python main.py
```

You will see:
```
================================================================
                 PyMT5 - DEMONSTRATION EXAMPLES
================================================================

Select an example to run:

[LOW-LEVEL] MT5Account - Direct gRPC/Protobuf
  1  - General operations (account, symbols, positions)
  2  - Trading operations (orders, modify, close)
  3  - Streaming methods (real-time ticks, trades)

[MID-LEVEL] MT5Service - Python Wrappers
  4  - Service API demo
  5  - Service streaming demo

[HIGH-LEVEL] MT5Sugar - Convenience API
  6  - Sugar basics (connection, balance, prices)
  7  - Sugar trading (market orders, pending orders)
  8  - Sugar positions (query, modify, close)
  9  - Sugar history (deals, profit calculations)
  10 - Sugar advanced (risk management, symbol info)

[ORCHESTRATORS] Trading Strategies
  11 - Trailing Stop Manager
  12 - Position Scaler (pyramiding/averaging)
  13 - Grid Trader
  14 - Risk Manager
  15 - Portfolio Rebalancer

[TOOLS]
  16 - User Code Sandbox (your custom code)

Enter number or alias (or 'x' to exit):
```

#### Method 2: Direct Run (quick access)

If you know what you want to run, use **number** or **alias**:

```bash
cd examples

# By number
python main.py 1        # Will run example #1
python main.py 11       # Will run Trailing Stop
python main.py 16       # Will run User Sandbox

# By alias (more memorable)
python main.py lowlevel01       # Same as 1
python main.py trailing         # Same as 11
python main.py usercode         # Same as 16
```

---

### Full Command Table

#### LOW-LEVEL (MT5Account) - Direct gRPC Calls

| Number | Aliases | File | Description |
|-------|--------|------|----------|
| **1** | `lowlevel01`, `general` | `1_lowlevel/01_general_operations.py` | Information methods: account, symbols, positions, ticks |
| **2** | `lowlevel02`, `trading` | `1_lowlevel/02_trading_operations.py` | Trading operations: calculations, validation, orders |
| **3** | `lowlevel03`, `streaming`, `stream` | `1_lowlevel/03_streaming_methods.py` | Real-time streaming: ticks, deals, positions |

**When to use**: Learning low-level protobuf structures, maximum control.

---

#### MID-LEVEL (MT5Service) - Python Wrappers

| Number | Aliases | File | Description |
|-------|--------|------|----------|
| **4** | `service`, `mid` | `2_service/04_service_demo.py` | Service API wrappers: account, symbols, positions, orders |
| **5** | `service05`, `servicestreaming` | `2_service/05_service_streaming.py` | Service streaming methods: ticks, deals, profits |

**When to use**: More convenient work with Python types, less boilerplate code.

---

#### HIGH-LEVEL (MT5Sugar) - Simplified API

| Number | Aliases | File | Description |
|-------|--------|------|----------|
| **6** | `sugar06`, `sugarbasics`, `basics` | `3_sugar/06_sugar_basics.py` | Basics: connection, balance, prices |
| **7** | `sugar07`, `sugartrading` | `3_sugar/07_sugar_trading.py` | Trading: market/pending orders, SL/TP |
| **8** | `sugar08`, `sugarpositions`, `positions` | `3_sugar/08_sugar_positions.py` | Positions: queries, modification, closing |
| **9** | `sugar09`, `sugarhistory`, `history` | `3_sugar/09_sugar_history.py` | History: deals over period, profit calculation |
| **10** | `sugar10`, `sugaradvanced`, `advanced` | `3_sugar/10_sugar_advanced.py` | Advanced: risk management, symbol info |

**When to use**: Quick prototyping, simple scripts, one line of code.

---

#### ORCHESTRATORS - Trading Strategies

| Number | Aliases | File | Description |
|-------|--------|------|----------|
| **11** | `trailing`, `trailingstop` | `4_orchestrators/11_trailing_stop.py` | Automatic trailing stop manager |
| **12** | `scaler`, `positionscaler` | `4_orchestrators/12_position_scaler.py` | Position scaling (pyramiding/averaging) |
| **13** | `grid`, `gridtrading` | `4_orchestrators/13_grid_trader.py` | Grid trading for sideways market |
| **14** | `risk`, `riskmanager` | `4_orchestrators/14_risk_manager.py` | Automatic risk management |
| **15** | `rebalancer`, `portfolio` | `4_orchestrators/15_portfolio_rebalancer.py` | Portfolio rebalancing |

**When to use**: Learning complex strategies, combining multiple API methods.

---

#### TOOLS - Developer Tools

| Number | Aliases | File | Description |
|-------|--------|------|----------|
| **16** | `inspect`, `inspector`, `proto` | `0_common/16_protobuf_inspector.py` | Interactive protobuf types explorer |
| **17** | `usercode`, `user`, `sandbox`, `custom` | `5_usercode/17_usercode.py` | Sandbox for your code |

**When to use**: Exploring protobuf structures (16), writing your own trading logic (17)

---

### ⚡ Initial Setup (mandatory!)

**After cloning the repository, you must install dependencies:**

```bash
# 1. Navigate to the project root
cd PyMT5

# 2. Install dependencies and link local package (only once)
pip install -e ./package
```

**What `pip install -e ./package` does:**

- **Installs required dependencies** into your Python environment:
  - `grpcio>=1.60.0` (gRPC runtime)
  - `grpcio-tools>=1.60.0` (protobuf tools)
  - `googleapis-common-protos>=1.56.0` (Google API types)

- **Creates editable link** to local `package/MetaRpcMT5/` folder
  - Does NOT copy or duplicate the package
  - Uses the existing code from your repository
  - All changes to `package/` are immediately visible

**Important notes:**

- MetaRpcMT5 package **already exists** in the repository (`package/MetaRpcMT5/`)
- This command installs only **external dependencies** (grpcio, etc.)
- Run this command only **ONCE** after cloning the repository
- After installation, all examples will work immediately

---

### Usage Examples

#### Initial Learning (with interactive menu)

```bash
cd examples

# Run menu (dependencies already installed above)
python main.py

# Select an example (enter number and press Enter)
# Start with 1, 2, 3 to understand the basics
```

#### Quick Testing of Specific Functions

```bash
cd examples

# Testing Sugar API (simplest)
python main.py basics          # Balance, prices
python main.py trading         # Opening orders
python main.py positions       # Working with positions

# Testing orchestrators
python main.py trailing        # Trailing stop
python main.py grid            # Grid trading
python main.py scaler          # Pyramiding/averaging

# Working with your code
python main.py usercode        # Your sandbox
```

#### Learning Sequence (recommended)

```bash
# 1. Start with low level (understanding basics)
python main.py 1               # How gRPC calls work
python main.py 2               # How trading operations execute

# 2. Move to mid level (Python wrappers)
python main.py service         # More convenient API

# 3. Explore high level (simplification)
python main.py basics          # Sugar API - one line of code
python main.py trading         # Simple trading operations
python main.py advanced        # Risk management

# 4. Explore orchestrators (strategies)
python main.py trailing        # Ready-made strategy
python main.py grid            # Complex logic

# 5. Write your code
python main.py usercode        # Your trading logic
```

---

### 🔄 How main.py Handles Commands

Inside `main.py` there is a large routing block that handles commands:

```python
if arg in ["1", "lowlevel01"]:
    return await lowlevel01.main()  # -> 1_lowlevel/01_general_operations.py

elif arg in ["11", "trailing", "trailingstop"]:
    return await trailing.main()     # -> 4_orchestrators/11_trailing_stop.py

elif arg in ["16", "usercode", "user", "sandbox", "custom"]:
    return await usercode.main()     # -> 5_usercode/17_usercode.py
```

Each command calls the corresponding module, which:

1. Creates its own MT5Account connection using `create_and_connect_mt5()` helper
2. Executes the demonstration with full connection control
3. Closes the connection in `finally` block via `await account.channel.close()`
4. Returns control to main.py

**This means**: Each example is **fully independent** and manages its own connection lifecycle. The examples are self-contained and can be run standalone or through main.py.

---

## 🛠️ Development Dependencies

PyMT5 uses the following key packages:

```python
# Core dependencies
grpcio>=1.60.0                    # gRPC framework
grpcio-tools>=1.60.0              # gRPC code generation tools
googleapis-common-protos>=1.56.0  # Google API common protobuf types
# protobuf - installed automatically as dependency of grpcio

# Built-in Python modules (no installation needed)
asyncio         # Async I/O support (built-in)
dataclasses     # Structured data (built-in for Python 3.7+)
typing          # Type hints (built-in)
```

All dependencies are listed in `package/pyproject.toml` and will be installed automatically with `pip install -e ./package`

---

## 🧩 Exploring Advanced Features

After mastering the three-tier chain (MT5Account -> MT5Service -> MT5Sugar), you can explore advanced features:

### Real-Time Streaming

Learn how to work with real-time data streams in Python:

**[gRPC Stream Management](GRPC_STREAM_MANAGEMENT.md)**

Topics covered in the guide:

- Async generator patterns for streaming
- Reading streamed data with async for
- Asyncio task management and cancellation
- Automatic reconnection patterns
- Multiple concurrent streams

### Protobuf Inspector

Interactive tool for exploring MT5 API types:

**[Protobuf Inspector Guide](PROTOBUF_INSPECTOR_GUIDE.md)**

Features:

- Explore protobuf message types
- Search types and fields
- View enum values
- Understand message structures

---

## Building Your Own System

After studying all examples and understanding the architecture, you can start building your own trading system:

**Sandbox location:** `examples/5_usercode/17_usercode.py`

This file is prepared as a starter template for your custom code. Before you start coding here, make sure you've studied:

1. The three-tier API (MT5Account -> MT5Service -> MT5Sugar)
2. At least a few helper examples to understand the patterns
3. Error handling patterns from examples
4. Stream management, if you need real-time data

**[User Code Sandbox Guide](USERCODE_SANDBOX_GUIDE.md)**

**Quick start:**

```bash
cd examples
python main.py 16
# Edit 5_usercode/17_usercode.py and add your code
```

---

### Error Handling

PyMT5 has comprehensive error handling:

**File:** `package/helpers/errors.py`

Features:

- `NotConnectedError` - raised when connection is not established
- `ApiError` - wraps protobuf errors with Python exception
- Trading operation return codes - constants for all MT5 return codes
- Helper functions: `is_retcode_success()`, `is_retcode_retryable()`

### Return Codes Reference

Understanding return code meanings when executing trading operations:

**[Return Codes Reference](RETURN_CODES_REFERENCE.md)**

Common codes:

- `10009` - Success (market order)
- `10008` - Success (pending order)
- `10019` - Insufficient margin
- `10016` - Invalid stops (SL/TP too close)
- `10018` - Market closed

### gRPC Stream Management

If you're working with real-time streaming (ticks, events):

**[gRPC Stream Management](GRPC_STREAM_MANAGEMENT.md)**

Primary pattern (recommended):

- Create `cancellation_event = asyncio.Event()` at start
- Pass `cancellation_event` to all streaming method calls
- Use `async for` to iterate over streams
- Stop streams with `cancellation_event.set()`

Additional patterns:

- `asyncio.wait_for()` - auto-timeout (used in: 05_service_streaming.py, 03_streaming_methods.py)
- `asyncio.create_task()` - background tasks (used in: 03_streaming_methods.py)
- `asyncio.gather()` - concurrent streams (documentation only: GRPC_STREAM_MANAGEMENT.md)

---

## 🗂️ Complete Documentation

### Core API Documentation

- **[MT5Account Master Overview](../MT5Account/MT5Account.Master.Overview.md)** - Complete low-level API reference
- **[MT5Service Overview](../MT5Service/MT5Service.Overview.md)** - Mid-level wrappers API
- **[MT5Sugar Overview](../MT5Sugar/MT5Sugar.Master.Overview.md)** - High-level Sugar API

### Guides and Tutorials

- **[User Code Sandbox Guide](USERCODE_SANDBOX_GUIDE.md)** - Quick start for custom code
- **[gRPC Stream Management](GRPC_STREAM_MANAGEMENT.md)** - Working with real-time streams
- **[Protobuf Inspector Guide](PROTOBUF_INSPECTOR_GUIDE.md)** - Interactive type explorer
- **[Return Codes Reference](RETURN_CODES_REFERENCE.md)** - Trading operation return codes
- **[ENUMs Usage Reference](ENUMS_USAGE_REFERENCE.md)** - MT5 enum constants and usage


## Conclusion

**The MetaRPC team** strives to create favorable conditions for learning fundamental trading principles and building algorithmic trading systems with Python.

We believe that with diligence and desire to learn, you will be able to master everything - from low-level protocol communication to complex trading systems.

**Your journey starts here:**

1. Set up the environment (above)
2. Create or configure your MT5 demo account ([MT5 for Beginners](MT5_For_Beginners.md))
3. Choose a learning path (bottom-up or top-down)
4. Run your first example: `python main.py 1`
5. Study the code, experiment and create

**Good luck on your algorithmic trading journey with Python!**

> "The foundation of success in algorithmic trading is not only understanding markets, but also understanding the code that interacts with them. Master both, and you will have unlimited possibilities."
>
> — MetaRPC Team

---


### ℹ️ Want Results Here and Now?

**Don't want to clone the entire repository and study the architecture?**

**Need a quick start in your own directory?**

If you can't wait to try the gRPC gateway capabilities as soon as possible and see your first working code in 10 minutes:

**[Your First Project - Project from Scratch](Your_First_Project.md)**

**What you'll get:**

- Create your project from scratch (without cloning the repository)
- Connect only necessary dependencies
- Write your first low-level method in 10 minutes
- Get account balance and see the result
- Start working with the gateway in your code immediately

**Difference in approaches:**

| This Document (GETTING_STARTED) | Your First Project |
|----------------------------------|-------------------|
| Clone ready-made repository | Create project from scratch |
| Study examples and architecture | Write working code immediately |
| Full SDK immersion | Minimal quick start |
| For deep understanding | For instant result |

Recommendation: After a quick start with Your First Project, return to this document to learn the complete architecture and all SDK capabilities.

---

## Python-Specific Tips

**Effective Python practices used in this project:**

- **Async/await everywhere** - All methods use asyncio for non-blocking I/O
- **Type hints** - Full type annotations for better IDE support
- **Dataclasses** - Structured data instead of raw protobuf
- **Context managers** - Clean resource management with async with
- **Generators** - Streaming data with async for
- **Exception propagation** - Python exceptions for validation and errors (ValueError, RuntimeError, TimeoutError)
- **F-strings** - Modern string formatting

**Resources for Python beginners:**

- [Python Official Tutorial](https://docs.python.org/3/tutorial/) - Official guide
- [Real Python](https://realpython.com/) - Practical Python tutorials
- [Python Asyncio](https://docs.python.org/3/library/asyncio.html) - Async programming guide

---
