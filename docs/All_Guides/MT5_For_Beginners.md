# MT5 for Beginners: Your First Steps in Trading

Welcome! This guide is designed for complete beginners who have never worked with MetaTrader 5 or trading. We'll walk you through everything you need to know to get started.

---

## What is MetaTrader 5 (MT5)?

**MetaTrader 5** is a powerful trading platform used by millions of traders worldwide. It allows you to:

- Trade forex, stocks, commodities, and cryptocurrencies
- Analyze markets with charts and indicators
- Execute automated trading strategies
- Monitor your positions in real-time

Think of MT5 as your "cockpit" for accessing financial markets. PyMT5 allows you to programmatically control this cockpit using Python.

---

## Demo vs Live Account: Start Safely

### Why start with a demo account?

A **demo account** is a risk-free practice account with virtual money. We **strongly recommend** starting with demo for several reasons:

- ✅ **Zero risk** - practice with virtual funds (typically $10,000 - $100,000)
- ✅ **Real market conditions** - live prices and market behavior
- ✅ **Learn the platform** - understand how MT5 works before risking real money
- ✅ **Test your code** - perfect for developing and testing your PyMT5 applications

### Live Account

A **live account** uses your real money. Only move to live trading when you:

- Understand how MT5 works
- Have thoroughly tested your strategies on demo
- Are aware of the risks involved

---

## Quick Start: Creating a Demo Account

The fastest way to get started is to create a demo account directly through the MT5 terminal application.

### Step 1️⃣: Download and Install MT5 Terminal

1. Visit the official MetaTrader website: [https://www.metatrader5.com/en/download](https://www.metatrader5.com/en/download)

2. Download the version for your operating system (Windows/Mac/Linux)

3. Install the application

---

### Step 2️⃣: Launch MT5 and Locate the Navigator Panel

When you open the MetaTrader 5 application, you'll typically see a popup window offering to:

- Register for the MQL community

- Open a new account or log into an existing one

If this popup doesn't appear automatically, you need to find the **Navigator** panel.

![Navigator Panel Location](../Guide_Images/1.%20NAV.png)


**Finding the Navigator Panel:**

The **Navigator** panel is usually located on the **left side** of the screen, below the **Market Watch** panel.

**Inside the Navigator panel** you'll see several sections:
- Accounts
- Subscriptions
- Indicators
- Expert Advisors
- And others

---

### Step 3️⃣: Opening a New Demo Account

1. In the **Navigator** panel, find the **Accounts** section
2. **Right-click** on "Accounts"
3. Select **"Open an account"** from the context menu

This will open the broker server search panel.

---

### Step 4️⃣: Select MetaQuotes Demo Server

In the broker search window, you'll see a list of available MT5 servers.

**For your first demo account, we'll use the simplest option:**

- Look for **"MetaQuotes-Demo"** or **"MetaQuotes Ltd"** in the list
- This is the standard demo server provided by MetaTrader developers
- If you don't see it immediately, use the search field at the top to find it

**Select the MetaQuotes server** and click **Next**.

![MetaQuotes Server Selection](../Guide_Images/2.%20META.png)

---

### Step 5️⃣: Account Type Selection

On the next screen, you'll have options:

- **Open a new demo account** (top option)
- Log into an existing account (demo or live)

**Select "Open a new demo account"** and click **Next**.

![Open New Demo Account](../Guide_Images/3.%20OPEN.png)


---

### Step 6️⃣: Fill in Your Personal Information

Now you'll see a form requesting your details:

- **Name**: Your first name
- **Last Name**: Your last name
- **Email**: Your email address
- **Phone**: Optional (can skip for demo)
- **Account Type**: Choose your preferred account settings
- **Deposit**: Virtual amount (e.g., $10,000)
- **Leverage**: 1:100 is a good starting point
- **Currency**: USD, EUR, etc.

**Check the box** to agree to the terms and conditions, then click **Next**.

![Personal Information Form](../Guide_Images/4.%20creator.png)

---

### Step 7️⃣: Save Your Account Credentials

MT5 will now create your demo account and display your credentials:

**Important credentials displayed:**

- **Login**: Your account number (e.g., 591129415)
- **Password**: Your master password for trading
- **Investor Password**: Read-only password (for monitoring)
- **Server**: Server name (e.g., "MetaQuotes-Demo")

**⚠️ CRITICALLY IMPORTANT**: **Save these credentials immediately!** You'll need them for:
- Logging back into MT5
- Configuring PyMT5 in `examples/0_common/settings.json`

Click **Finish** to complete account creation.

![Account Credentials](../Guide_Images/5.%20OKK.png)

---

### Step 8️⃣: Configure PyMT5 with Your Credentials

Now that you have an MT5 demo account, you need to configure PyMT5 to connect to it.

1. Open your PyMT5 project
2. Navigate to **`examples/0_common/settings.json`**
3. Fill in the credentials you just saved:


```json
{
  "user": 591129415,
  "password": "YourPasswordHere",
  "host": "mt5.mrpc.pro",
  "port": 443,
  "grpc_server": "mt5.mrpc.pro:443",
  "mt_cluster": "MetaQuotes-Demo",
  "test_symbol": "EURUSD",
  "test_volume": 0.01
}
```

**Important notes:**

- **user**: Replace with your login number
- **password**: Replace with your password
- **mt_cluster**: Use the exact server name from MT5 (e.g., "MetaQuotes-Demo")
- **host, port, grpc_server**: Provided by MetaRPC team (leave as is)

---

### Step 9️⃣: Verify MT5 Connection

Back in the MT5 terminal:

1. MT5 should automatically log you into your new demo account
2. Check the **bottom right corner** of the terminal window - you should see:
   - **Green connection indicator** (means connected to server)
   - **Your account balance** (e.g., $10,000)

**You're now ready to test!**

---

### Step 🔟: Start Testing PyMT5

With your MT5 demo account created and `settings.json` configured, you can start running examples:

```bash
# Navigate to the examples folder
cd examples

# Run your first example
python main.py 1

# Or run interactively
python main.py
```

When trading operations occur, your demo account balance will increase or decrease accordingly. **Experiment freely** - it's virtual money, so there's no risk!

All trades executed by PyMT5 will appear in your MT5 terminal in real-time.

---

## 🧩 Understanding MT5 Password Types

MT5 uses **two types of passwords** for security and flexibility:

### Master Password (Main Password)

- **Full access** to your trading account
- Can open/close trades, deposit/withdraw funds, change settings
- **This is the password you created** during account registration
- Use this password for:
  - Trading (including PyMT5 applications)
  - Changing account settings
  - Withdrawing funds (live accounts)

### Investor Password (Read-Only Password)

- **View-only access** to your account
- Can see trades, balance, history - **but cannot trade**
- Useful for:
  - Sharing your trading performance with others (investors, friends)
  - Monitoring your account without risk
  - Audit and analytics tools

**How to get your investor password:**

1. In MT5, go to **Tools → Options**
2. Select the **Server** tab
3. Click **Change** next to "Investor Password"
4. Set a new investor password

---

## Choosing a Broker (Optional)

While you can use the MetaQuotes demo server for practice, you may want to choose a specific broker for:

- Live trading later
- Better demo conditions (spreads, instruments)
- Specific regional support

### Popular MT5 Brokers:

**Note**: This is not financial advice. Always do your own research before choosing a broker.

- **IC Markets** - Popular for forex and low spreads
- **Pepperstone** - Well-regulated, beginner-friendly
- **OANDA** - Strong reputation, accepts US clients
- **XM** - Easy account opening, many account types
- **RoboForex** - Good for automated trading
- **FxPro** - Excellent demo trading conditions (used in PyMT5 examples)

### What to look for:

- ✅ **Regulation** - Check if regulated by FCA, ASIC, CySEC, etc.

- ✅ **MT5 Support** - Make sure they offer MT5 (not just MT4).

- ✅ **Demo Account** - Free demo without expiration (though demo accounts typically last 30 days, then become inactive).

- ✅ **Good Spreads** - Lower spreads = lower trading costs.

- ✅ **Customer Support** - Responsive support in your language.

---


---

## What's Next?

Now that you have a demo account and understand the basics, you're ready for:

### 1. Setting Up PyMT5

Follow our main getting started guide to connect PyMT5 to your MT5 account:

👉 **[Getting Started with PyMT5](GETTING_STARTED.md)**

### 2. Understanding API Architecture

PyMT5 is built in **three levels**, from low-level to high-level. You can choose where to start depending on your needs:

#### Level 1: MT5Account (Low-Level gRPC Foundation)
👉 **[MT5Account Overview](../MT5Account/MT5Account.Master.Overview.md)**

- **Direct gRPC calls** to MT5 terminal
- **Foundation of everything** - all other levels use this internally
- Maximum control and flexibility
- Best for: Advanced users who need fine-grained control

#### Level 2: MT5Service (Convenient Wrappers)
👉 **[MT5Service Overview](../MT5Service/MT5Service.Overview.md)**

- **Wrapper methods** over MT5Account gRPC calls
- Simplified error handling and response parsing
- Easier to work with than raw gRPC
- Best for: Most common trading scenarios

#### Level 3: MT5Sugar (High-Level Helpers)
👉 **[MT5Sugar API Overview](../MT5Sugar/MT5Sugar.Master.Overview.md)**

- **Syntactic sugar** and convenience methods
- Chainable operations, smart defaults
- Most intuitive and beginner-friendly
- Best for: Rapid prototyping and simple strategies

---

## Important Reminders

### 🛡️ Security

- **Never share your master password** with anyone
- Use investor password for monitoring/analytics tools
- Keep your credentials safe (use password managers)

### 📊 Risk Management

- Demo accounts are **risk-free**, but form good habits:
  - Always use Stop Loss
  - Don't risk more than 1-2% per trade
  - Understand position sizing calculations

### 🧪 Testing

- Test all your PyMT5 code **on demo first**
- Verify strategies over weeks/months, not days
- Paper trading (demo) doesn't guarantee live results

### 📚 Education

- Trading has a steep learning curve
- Focus on learning, not earning
- Consider courses, books, and communities

---

## Useful Python Commands

### Installation

```bash
# Install PyMT5 package with all dependencies
pip install MetaRpcMT5
```

### Running Examples

```bash
# Navigate to examples folder first
cd examples

# Option 1: Run specific example by number
python main.py 1

# Option 2: Interactive menu
python main.py

# Option 3: Run example file directly
python 1_lowlevel/01_general_operations.py
python 3_sugar/06_sugar_basics.py
```

### Checking Environment

```bash
# Verify Python version (requires 3.8+)
python --version
```

---

**Ready to start coding?** Head over to [Getting Started](GETTING_STARTED.md) to connect PyMT5 to your MT5 account!

**Good luck with your trading journey! 🚀**
