# Your First Project in 10 Minutes

> **Practice Before Theory** - create a working trading project with MT5 before diving into the documentation

---

## Why This Guide?

I want to show you with a simple example how easy it is to use our gRPC gateway to work with MetaTrader 5.

**Before diving into the fundamentals and core concepts of the project - let's create your first project.**

We will install one Python package `MetaRpcMT5`, which contains:

- ✅ Protobuf definitions of all MT5 methods
- ✅ MT5Account - ready-to-use gRPC client
- ✅ Error handler - ApiError types and return codes
- ✅ Everything needed to get started

**This is the foundation** for your future algorithmic trading system.

---

> 💡 After getting your first results, proceed to [MT5Account.Master.Overview.md](../MT5Account/MT5Account.Master.Overview.md) for a deep understanding of the SDK architecture.

---

## Step 1: Install Python 3.8 or Higher

If you don't have Python installed yet:

**Download and install:**

- [Python Download](https://www.python.org/downloads/)

**Verify installation:**

```bash
python --version
# Should show: Python 3.8.x or higher
```

**On Windows you may need:**
```bash
py --version
# or
python3 --version
```

---

## Step 2: Create a New Python Project

Open a terminal (command prompt) and execute:

```bash
# Create project folder
mkdir MyMT5Project
cd MyMT5Project

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

**What happened:**

- ✅ Created `MyMT5Project` folder
- ✅ Created `venv` virtual environment - isolated Python environment
- ✅ Activated environment - now you can install packages

---

## Step 3: Install MetaRpcMT5 Package

This is the most important step - installing the **single package** that contains everything you need:

```bash
pip install git+https://github.com/MetaRPC/PyMT5.git#subdirectory=package
```

> **📌 Important:** The package will be installed in the `venv/` virtual environment of your project (not globally on the computer).

**How to verify installation?**

Choose any method:

```bash
# Method 1: Full package information
pip show MetaRpcMT5

# Method 2: Import check
python -c "from MetaRpcMT5 import MT5Account; print('✅ OK')"

# Method 3: Package list (Windows PowerShell)
pip list | Select-String "MetaRpcMT5"

# Method 3: Package list (Linux/Mac)
pip list | grep MetaRpcMT5
```

If you see package information - **installation successful!** ✅

---

## Step 4: Create Configuration File settings.json

You have **two ways** to store connection settings:

### Method 1: JSON file (recommended for beginners)

Create a `settings.json` file in the project root:

**Basic variant (minimum parameters):**
```json
{
  "user": 591129415,
  "password": "YourPassword123",
  "grpc_server": "mt5.mrpc.pro:443",
  "mt_cluster": "YourBroker-MT5 Demo",
  "test_symbol": "EURUSD"
}
```

**Extended variant (all parameters):**
```json
{
  "user": 591129415,
  "password": "YourPassword123",
  "host": "mt5.mrpc.pro",
  "port": 443,
  "grpc_server": "mt5.mrpc.pro:443",
  "mt_cluster": "YourBroker-MT5 Demo",
  "test_symbol": "EURUSD",
  "test_volume": 0.01
}
```

**Parameter explanation:**

| Parameter | Required | Description |
|----------|--------------|----------|
| **user** | ✅ Yes | Your MT5 account number (login) |
| **password** | ✅ Yes | Master password for MT5 account |
| **grpc_server** | ✅ Yes | gRPC gateway address: `mt5.mrpc.pro:443` |
| **mt_cluster** | ✅ Yes | Broker cluster name (server name in MT5) |
| **test_symbol** | ✅ Yes | Trading symbol: `EURUSD`, `GBPUSD`, etc. |
| **host** | ⚪ No | gRPC server host separately: `mt5.mrpc.pro` |
| **port** | ⚪ No | gRPC server port: `443` |
| **test_volume** | ⚪ No | Volume for test orders: `0.01` |

### Method 2: Environment variables (for production)

Instead of JSON, you can use environment variables:

**Windows (PowerShell):**

```powershell
$env:MT5_USER="591129415"
$env:MT5_PASSWORD="YourPassword123"
$env:MT5_GRPC_SERVER="mt5.mrpc.pro:443"
$env:MT5_CLUSTER="YourBroker-MT5 Demo"
$env:MT5_TEST_SYMBOL="EURUSD"
```

**Linux/Mac (Bash):**

```bash
export MT5_USER="591129415"
export MT5_PASSWORD="YourPassword123"
export MT5_GRPC_SERVER="mt5.mrpc.pro:443"
export MT5_CLUSTER="YourBroker-MT5 Demo"
export MT5_TEST_SYMBOL="EURUSD"
```

> **💡 Tip:** For this guide, use **Method 1 (JSON)** - it's simpler for beginners

---

## Step 5: Write Code to Connect and Get Account Information

Create a `main.py` file in the project root:

```python
"""
═══════════════════════════════════════════════════════════════════
YOUR FIRST PROJECT WITH MT5
═══════════════════════════════════════════════════════════════════
This script demonstrates:
  - Creating MT5Account
  - Connecting to MT5 via gRPC
  - Getting account information
═══════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import sys
from uuid import uuid4
from datetime import datetime

# Import MetaRpcMT5
from MetaRpcMT5 import MT5Account


def load_settings():
    """Load settings from settings.json"""
    with open('settings.json', 'r', encoding='utf-8') as f:
        return json.load(f)


async def main():
    """Main function"""

    print("═" * 80)
    print("          WELCOME TO YOUR FIRST PROJECT WITH MT5")
    print("═" * 80)
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 1: LOAD CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════

    print("📋 Loading configuration...")

    try:
        config = load_settings()
    except FileNotFoundError:
        print("❌ Error: settings.json file not found!")
        print("   Create settings.json with your MT5 credentials")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: invalid JSON in settings.json: {e}")
        sys.exit(1)

    print("✅ Configuration loaded:")
    print(f"   User:           {config['user']}")
    print(f"   Cluster:        {config['mt_cluster']}")
    print(f"   gRPC Server:    {config['grpc_server']}")
    print(f"   Test Symbol:    {config['test_symbol']}")
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 2: CREATE MT5ACCOUNT
    # ═══════════════════════════════════════════════════════════════════════

    print("🔌 Creating MT5Account instance...")

    # Generate unique UUID for this terminal
    terminal_guid = uuid4()

    # Create MT5Account with credentials
    account = MT5Account(
        user=config['user'],
        password=config['password'],
        grpc_server=config['grpc_server'],
        id_=terminal_guid
    )

    print(f"✅ MT5Account created (UUID: {terminal_guid})")
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 3: CONNECT TO MT5
    # ═══════════════════════════════════════════════════════════════════════

    print("🔗 Connecting to MT5 terminal...")
    print(f"   Waiting for response (timeout: 120 seconds)...")
    print()

    try:
        # Connect to MT5 using server name
        # This is the RECOMMENDED method - simpler than ConnectEx
        await account.connect_by_server_name(
            server_name=config['mt_cluster'],
            base_chart_symbol=config['test_symbol'],
            timeout_seconds=120
        )

        print(f"✅ Successfully connected!")
        print(f"   Terminal GUID: {account.id}")
        print()

    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("   Check:")
        print("   - Correct login/password")
        print("   - gRPC server availability")
        print("   - Correct cluster name")
        await account.channel.close()
        sys.exit(1)

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 4: GET ACCOUNT INFORMATION
    # ═══════════════════════════════════════════════════════════════════════

    print("📊 Getting account information...")
    print()

    try:
        # Request full account information in one call
        summary_data = await account.account_summary()

        # ═══════════════════════════════════════════════════════════════════════
        # STEP 5: OUTPUT RESULTS
        # ═══════════════════════════════════════════════════════════════════════

        print()
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║              ACCOUNT INFORMATION                               ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print()
        print(f"   Login:              {summary_data.account_login}")
        print(f"   User name:          {summary_data.account_user_name}")
        print(f"   Company:            {summary_data.account_company_name}")
        print(f"   Currency:           {summary_data.account_currency}")
        print()
        print(f"💰 Balance:            {summary_data.account_balance:.2f} {summary_data.account_currency}")
        print(f"💎 Equity:             {summary_data.account_equity:.2f} {summary_data.account_currency}")
        print()
        print(f"   Credit:             {summary_data.account_credit:.2f} {summary_data.account_currency}")
        print(f"   Leverage:           1:{summary_data.account_leverage}")
        print(f"   Trade mode:         {summary_data.account_trade_mode}")
        print()

        # Server time - protobuf Timestamp, needs conversion
        if summary_data.server_time:
            server_time = summary_data.server_time.ToDatetime()
            print(f"   Server time:        {server_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # UTC offset: server time offset from UTC in minutes
        # Example: 120 minutes = UTC+2 (server is 2 hours ahead of UTC)
        utc_shift = summary_data.utc_timezone_server_time_shift_minutes
        print(f"   UTC offset:         {utc_shift} minutes (UTC{utc_shift/60:+.1f})")

        print()
        print("╚════════════════════════════════════════════════════════════════╝")

    except Exception as e:
        print(f"❌ Error getting account data: {e}")
        await account.channel.close()
        sys.exit(1)

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 6: DISCONNECT FROM MT5
    # ═══════════════════════════════════════════════════════════════════════

    print()
    print("🔌 Disconnecting from MT5...")

    try:
        await account.channel.close()
        print("✅ Successfully disconnected!")
    except Exception as e:
        print(f"⚠️  Disconnect warning: {e}")

    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   🎉 CONGRATULATIONS! YOUR FIRST PROJECT WORKS! 🎉             ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    # Run async function
    asyncio.run(main())
```

---

## Step 6: Run the Project

Save all files and execute:

```bash
python main.py
```

**Expected output:**

```
════════════════════════════════════════════════════════════════════════════════
          WELCOME TO YOUR FIRST PROJECT WITH MT5
════════════════════════════════════════════════════════════════════════════════

📋 Loading configuration...
✅ Configuration loaded:
   User:           591129415
   Cluster:        FxPro-MT5 Demo
   gRPC Server:    mt5.mrpc.pro:443
   Test Symbol:    EURUSD

🔌 Creating MT5Account instance...
✅ MT5Account created (UUID: 12345678-90ab-cdef-1234-567890abcdef)

🔗 Connecting to MT5 terminal...
   Waiting for response (timeout: 120 seconds)...

✅ Successfully connected!
   Terminal GUID: 12345678-90ab-cdef-1234-567890abcdef

📊 Getting account information...

╔════════════════════════════════════════════════════════════════╗
║              ACCOUNT INFORMATION                               ║
╚════════════════════════════════════════════════════════════════╝

   Login:              591129415
   User name:          Demo User
   Company:            FxPro Financial Services Ltd
   Currency:           USD

💰 Balance:            10000.00 USD
💎 Equity:             10000.00 USD

   Credit:             0.00 USD
   Leverage:           1:100
   Trade mode:         0

   Server time:        2026-02-04 15:30:45
   UTC offset:         120 minutes (UTC+2.0)

╚════════════════════════════════════════════════════════════════╝

🔌 Disconnecting from MT5...
✅ Successfully disconnected!

╔════════════════════════════════════════════════════════════════╗
║   🎉 CONGRATULATIONS! YOUR FIRST PROJECT WORKS! 🎉             ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🎉 Congratulations! You Did It!

You just:

✅ Created a new Python project from scratch

✅ Integrated the **single** Python package `MetaRpcMT5` to work with MT5

✅ Configured connection parameters

✅ Connected to MT5 terminal via gRPC

✅ Retrieved full account information programmatically

**This was a low-level approach** using `MT5Account` and protobuf directly.

---

## 📁 Your Project Structure

After completing all steps, the project structure should look like this:

```
MyMT5Project/
├── venv/                # Python virtual environment
├── settings.json        # MT5 connection configuration
├── main.py              # Main application code
```

**requirements.txt contents (optional):**

If you want to save dependencies:

```bash
pip freeze > requirements.txt
```

The content will be approximately:

```
MetaRpcMT5 @ git+https://github.com/MetaRPC/PyMT5.git@main#subdirectory=package
grpcio>=1.60.0
grpcio-tools>=1.60.0
googleapis-common-protos>=1.56.0
```

---

## 🚀 What's Next?

Now that you have a working project, you can:

### 1. Add More Functionality

**Examples of what you can do:**

#### Get Current Quotes

```python
# Get last tick for symbol
tick_data = await account.symbol_info_tick(symbol=config['test_symbol'])

print(f"Last tick for {config['test_symbol']}:")
print(f"  Bid: {tick_data.bid:.5f}")
print(f"  Ask: {tick_data.ask:.5f}")
print(f"  Last: {tick_data.last:.5f}")
```

#### Get All Open Positions

```python
# Get all open orders and positions
opened_data = await account.opened_orders()

print(f"Open positions: {len(opened_data.position_infos)}")
for pos in opened_data.position_infos:
    print(f"  #{pos.ticket} {pos.symbol} {pos.volume:.2f} lots, Profit: {pos.profit:.2f}")
```

#### Open Market Order

```python
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as trading_pb2

# Create order request
order_req = trading_pb2.OrderSendRequest(
    symbol=config['test_symbol'],
    operation=trading_pb2.TMT5_ORDER_TYPE_BUY,  # Buy
    volume=0.01,  # 0.01 lot
    comment="PyMT5 Test Order"
)

# Send order
order_result = await account.order_send(order_req)

if order_result.retcode == 10009:  # TRADE_RETCODE_DONE
    print(f"✅ Order opened: Deal #{order_result.deal}, Order #{order_result.order}")
else:
    print(f"❌ Order error: code {order_result.retcode}")
```

#### Data Streaming

```python
# Subscribe to real-time ticks
# The on_symbol_tick method accepts a list of symbols directly
tick_stream = account.on_symbol_tick(
    symbols=[config['test_symbol']]
)

print(f"🔄 Receiving tick stream for {config['test_symbol']}...")
print("   (Press Ctrl+C to stop)")

event_count = 0
try:
    async for tick_event in tick_stream:
        event_count += 1
        tick = tick_event.symbol_tick
        print(f"[{event_count}] Bid: {tick.bid:.5f}, Ask: {tick.ask:.5f}")

        # Stop after 10 events (for example)
        if event_count >= 10:
            break

except KeyboardInterrupt:
    print(f"\n✅ Received {event_count} events")
```

### 2. Study the Complete SDK Architecture

The PyMT5 repository has **three API levels**:

```
┌─────────────────────────────────────────────
│  MT5Sugar (Level 3) - Convenient API
│  examples/3_sugar/
│  sugar.buy_market("EURUSD", 0.01)
└─────────────────────────────────────────────
              ↓ uses
┌─────────────────────────────────────────────
│  MT5Service (Level 2) - Wrappers
│  examples/2_service/
│  service.get_balance()
└─────────────────────────────────────────────
              ↓ uses
┌─────────────────────────────────────────────
│  MT5Account (Level 1) - Base gRPC ⭐
│  package/MetaRpcMT5/helpers/mt5_account.py
│  account.account_summary()
└─────────────────────────────────────────────
```

**You just used Level 1 (MT5Account)** - this is the foundation of everything!

To study levels 2 and 3:

- Explore examples in the `examples/` folder
- Read [MT5Account.Master.Overview.md](../MT5Account/MT5Account.Master.Overview.md)
- Check out ready-made demonstrations

### 3. Explore Ready-Made Examples

The PyMT5 repository contains many examples:

- `examples/1_lowlevel/` - examples with MT5Account (what you used)
- `examples/2_service/` - examples with MT5Service
- `examples/3_sugar/` - examples with MT5Sugar
- `examples/4_orchestrators/` - complex trading strategies

**Running examples:**

```bash
cd examples
python main.py
# Select the desired example from the interactive menu
```

### 4. Read the Documentation

- [MT5Account API Reference](../API_Reference/MT5Account.md) - ⭐ complete reference for the base level
- [MT5Account.Master.Overview.md](../MT5Account/MT5Account.Master.Overview.md) - project map and architecture
- [GRPC_STREAM_MANAGEMENT.md](./GRPC_STREAM_MANAGEMENT.md) - working with streaming data
- [RETURN_CODES_REFERENCE.md](./RETURN_CODES_REFERENCE.md) - operation return codes
- [ENUMS_USAGE_REFERENCE.md](./ENUMS_USAGE_REFERENCE.md) - using enumerations

---

## ❓ Frequently Asked Questions

### What Is the MetaRpcMT5 Package?

`MetaRpcMT5` is an **independent Python package** that contains:

- MT5Account (base gRPC client)
- All protobuf definitions of MT5 API
- gRPC stubs for all methods
- Helper types and structures

It's a **portable package** - you can use it in any Python project!

### How to Work with Environment Variables Instead of settings.json?

You can use environment variables:

```python
import os

def load_settings_from_env():
    """Load settings from environment variables"""
    return {
        'user': int(os.getenv('MT5_USER')),
        'password': os.getenv('MT5_PASSWORD'),
        'grpc_server': os.getenv('MT5_GRPC_SERVER'),
        'mt_cluster': os.getenv('MT5_CLUSTER'),
        'test_symbol': os.getenv('MT5_TEST_SYMBOL', 'EURUSD')
    }
```

**Set variables:**

```bash
# Windows (PowerShell)
$env:MT5_USER="591129415"
$env:MT5_PASSWORD="YourPassword123"
$env:MT5_GRPC_SERVER="mt5.mrpc.pro:443"
$env:MT5_CLUSTER="FxPro-MT5 Demo"
$env:MT5_TEST_SYMBOL="EURUSD"

# Linux/Mac
export MT5_USER="591129415"
export MT5_PASSWORD="YourPassword123"
export MT5_GRPC_SERVER="mt5.mrpc.pro:443"
export MT5_CLUSTER="FxPro-MT5 Demo"
export MT5_TEST_SYMBOL="EURUSD"
```

### How to Use Level 2 (MT5Service) and Level 3 (MT5Sugar)?

These levels are in the **main PyMT5 repository**:

1. Clone the repository (or download files):

   ```bash
   git clone https://github.com/MetaRPC/PyMT5.git
   ```

2. Copy the necessary files to your project:

   - From the `src/` folder (or corresponding)
   - MT5Service and MT5Sugar classes

3. Use convenient methods:

   ```python
   from mt5_service import MT5Service
   from mt5_sugar import MT5Sugar

   # Level 2 - Service
   service = MT5Service(account)
   balance = await service.get_balance()

   # Level 3 - Sugar
   sugar = MT5Sugar(service)
   ticket = await sugar.buy_market("EURUSD", 0.01)
   ```

See details in [MT5Account.Master.Overview.md](../MT5Account/MT5Account.Master.Overview.md)

### What to Do If Errors Occur?

**Connection error:**

- Check correct login/password
- Make sure gRPC server is available
- Check cluster name (exact MT5 server name)

**Connection timeout:**

- Increase `timeout_seconds` to 180 or 240
- Check internet connection
- Check firewall/antivirus

**Import errors:**

- Make sure virtual environment is activated
- Reinstall package:

**Windows PowerShell:**

```powershell
pip uninstall MetaRpcMT5 -y
pip install git+https://github.com/MetaRPC/PyMT5.git#subdirectory=package
```

**Linux/Mac/PowerShell 7+:**

```bash
pip uninstall MetaRpcMT5 && pip install git+https://github.com/MetaRPC/PyMT5.git#subdirectory=package
```

---

## 📝 Summary: What We Did

In this guide, you created a minimalist project that:

1. ✅ **Uses only Python modules** - doesn't require cloning the repository

2. ✅ **Imports MetaRpcMT5 package** - the only dependency for MT5

3. ✅ **Connects to MT5** via gRPC gateway

4. ✅ **Reads configuration** from `settings.json`

5. ✅ **Uses MT5Account** (Level 1 - base level)

6. ✅ **Gets account information** and outputs to console

**This is the foundation** for any of your MT5 projects in Python.

---

**Good luck developing trading systems! 🚀**

"Trade safely, code cleanly, and may your gRPC connections always be stable."
