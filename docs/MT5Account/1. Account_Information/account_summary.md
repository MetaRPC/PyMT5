# Getting Complete Account Summary

> **Request:** complete account snapshot with **all essential properties** in a single call (balance, equity, leverage, currency, server time, etc.).

**API Information:**

* **Low-level API:** `MT5Account.account_summary(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.AccountHelper`
* **Proto definition:** `AccountSummary` (defined in `mt5-term-api-account-helper.proto`)

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `AccountSummary(AccountSummaryRequest) -> AccountSummaryReply`
* **Low-level client (generated):** `AccountHelperStub.AccountSummary(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Get complete account snapshot with all essential properties in one call.
* **Why you need it.** Most efficient way to get multiple account properties (balance, equity, leverage, etc.).
* **When to use.** Use this for general account info. Use `account_info_*` methods only for single specific properties.

---

## 🎯 Purpose

Use it to get comprehensive account information:

* **RECOMMENDED** method for getting account overview
* Get balance, equity, credit in one call
* Check account login, name, server, company
* Get leverage and trade mode (demo/real)
* Get account currency
* Get server time with UTC offset
* Efficient - one round-trip instead of multiple calls

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [account_summary - How it works](../HOW_IT_WORK/1. Account_information_HOW/account_summary_HOW.md)**

---

## Method Signature

```python
async def account_summary(
    self,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
)
```

**Request message:**

```protobuf
message AccountSummaryRequest {
  // Empty - no parameters needed
}
```

**Reply message:**

```protobuf
message AccountSummaryReply {
  oneof response {
    AccountSummaryData data = 1;
    Error error = 2;
  }
}

message AccountSummaryData {
  int64 account_login = 1;
  double account_balance = 2;
  double account_equity = 3;
  string account_user_name = 4;
  int64 account_leverage = 5;
  MrpcEnumAccountTradeMode account_trade_mode = 6;
  string account_company_name = 7;
  string account_currency = 8;
  google.protobuf.Timestamp server_time = 9;
  int64 utc_timezone_server_time_shift_minutes = 10;
  double account_credit = 11;
}
```

---

## 🔽 Input

| Parameter     | Type                    | Description                                             |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `deadline`    | `datetime` (optional)   | Deadline for the gRPC call (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                    |

**No property_id required** - this method returns all available properties.

**Deadline options:**

```python
from datetime import datetime, timedelta

# 1. With deadline (recommended)
deadline = datetime.utcnow() + timedelta(seconds=3)
summary = await account.account_summary(deadline=deadline)

# 2. With cancellation event
cancel_event = asyncio.Event()
summary = await account.account_summary(cancellation_event=cancel_event)

# 3. No deadline (uses default timeout if configured)
summary = await account.account_summary()
```

---

## ⬆️ Output - `AccountSummaryData`

| Field                                  | Type                        | Python Type | Description                                          |
| -------------------------------------- | --------------------------- | ----------- | ---------------------------------------------------- |
| `account_login`                        | `int64`                     | `int`       | Account number                                       |
| `account_balance`                      | `double`                    | `float`     | Account balance in deposit currency                  |
| `account_equity`                       | `double`                    | `float`     | Account equity (balance + floating profit/loss)      |
| `account_user_name`                    | `string`                    | `str`       | Account owner name                                   |
| `account_leverage`                     | `int64`                     | `int`       | Account leverage (e.g., 100 for 1:100)              |
| `account_trade_mode`                   | `MrpcEnumAccountTradeMode`  | `int`       | Trade mode: 0=DEMO, 1=CONTEST, 2=REAL               |
| `account_company_name`                 | `string`                    | `str`       | Broker/company name                                  |
| `account_currency`                     | `string`                    | `str`       | Account currency (USD, EUR, etc.)                    |
| `server_time`                          | `google.protobuf.Timestamp` | `Timestamp` | Current server time                                  |
| `utc_timezone_server_time_shift_minutes` | `int64`                   | `int`       | Server timezone offset from UTC (in minutes)         |
| `account_credit`                       | `double`                    | `float`     | Account credit in deposit currency                   |

**Return value:** The method returns `AccountSummaryData` object with all fields accessible as attributes.

---

## 🧱 Related enums (from proto)

> **Note:** The tables show simplified constant names for readability.
> In Python code, use the full enum path from the account_helper module.

### `MrpcEnumAccountTradeMode`

Defined in `mt5-term-api-account-helper.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `MRPC_ACCOUNT_TRADE_MODE_DEMO` | 0 | Demo account |
| `MRPC_ACCOUNT_TRADE_MODE_CONTEST` | 1 | Contest account |
| `MRPC_ACCOUNT_TRADE_MODE_REAL` | 2 | Real account |

**Usage in Python:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Access constants
mode = account_helper_pb2.MRPC_ACCOUNT_TRADE_MODE_DEMO  # = 0
# Check account mode
if summary.account_trade_mode == account_helper_pb2.MRPC_ACCOUNT_TRADE_MODE_REAL:
    print("Real account - be careful!")
```

---

## 🧩 Notes & Tips

* **RECOMMENDED method:** This is the most efficient way to get account information - use it instead of multiple `account_info_*` calls.
* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Connection required:** You must call `connect_by_host_port()` or `connect_by_server_name()` before using this method.
* **No margin info:** This method doesn't include margin/margin level - use `account_info_double()` for those.
* **Server time:** The `server_time` field is a protobuf Timestamp - convert with `.ToDatetime()` or `.seconds`.

---

## 🔗 Usage Examples

### 1) Get complete account summary

```python
import asyncio
from datetime import datetime, timedelta
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

async def main():
    # Create account instance
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="your-server.com:443"
    )

    # Connect first
    await account.connect_by_host_port()

    try:
        # Set deadline
        deadline = datetime.utcnow() + timedelta(seconds=3)

        # Get summary
        summary = await account.account_summary(deadline=deadline)

        # Access fields
        print(f"Account Summary:")
        print(f"  Login: {summary.account_login}")
        print(f"  Name: {summary.account_user_name}")
        print(f"  Balance: ${summary.account_balance:.2f}")
        print(f"  Equity: ${summary.account_equity:.2f}")
        print(f"  Credit: ${summary.account_credit:.2f}")
        print(f"  Currency: {summary.account_currency}")
        print(f"  Leverage: 1:{summary.account_leverage}")
        print(f"  Broker: {summary.account_company_name}")

        # Trade mode
        mode_names = {0: "DEMO", 1: "CONTEST", 2: "REAL"}
        mode = mode_names.get(summary.account_trade_mode, "UNKNOWN")
        print(f"  Mode: {mode}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Print formatted account info

```python
async def print_account_info(account: MT5Account):
    """Print nicely formatted account information"""
    summary = await account.account_summary()

    # Determine account type
    mode_names = {
        0: "DEMO",
        1: "CONTEST",
        2: "REAL"
    }
    mode = mode_names.get(summary.account_trade_mode, "UNKNOWN")

    # Calculate floating P/L
    floating_pnl = summary.account_equity - summary.account_balance

    print(f"\n{'='*60}")
    print(f"ACCOUNT INFORMATION")
    print(f"{'='*60}")
    print(f"Account:     #{summary.account_login} ({summary.account_user_name})")
    print(f"Type:        {mode}")
    print(f"Broker:      {summary.account_company_name}")
    print(f"Currency:    {summary.account_currency}")
    print(f"Leverage:    1:{summary.account_leverage}")
    print(f"")
    print(f"Balance:     ${summary.account_balance:,.2f}")
    print(f"Credit:      ${summary.account_credit:,.2f}")
    print(f"Equity:      ${summary.account_equity:,.2f}")
    print(f"Floating:    ${floating_pnl:+,.2f}")
    print(f"{'='*60}\n")

# Usage:
await print_account_info(account)
```

### 3) Check account health

```python
async def check_account_health(account: MT5Account) -> dict:
    """
    Comprehensive account health check.

    Returns:
        Dictionary with health metrics and status
    """
    summary = await account.account_summary()

    # Calculate metrics
    balance = summary.account_balance
    equity = summary.account_equity
    floating_pnl = equity - balance
    pnl_percent = (floating_pnl / balance * 100) if balance > 0 else 0

    # Determine health status
    if summary.account_trade_mode == 0:
        account_type = "DEMO"
    elif summary.account_trade_mode == 2:
        account_type = "REAL"
    else:
        account_type = "CONTEST"

    # Health assessment
    if equity > balance and pnl_percent > 5:
        status = "EXCELLENT"
    elif equity > balance:
        status = "HEALTHY"
    elif abs(pnl_percent) < 5:
        status = "NEUTRAL"
    elif pnl_percent < -10:
        status = "CRITICAL"
    else:
        status = "WARNING"

    health = {
        "status": status,
        "account_type": account_type,
        "balance": balance,
        "equity": equity,
        "floating_pnl": floating_pnl,
        "pnl_percent": pnl_percent,
        "leverage": summary.account_leverage,
        "currency": summary.account_currency
    }

    print(f"Account Health: {status}")
    print(f"  Balance: ${balance:,.2f}")
    print(f"  Equity: ${equity:,.2f}")
    print(f"  P/L: ${floating_pnl:+,.2f} ({pnl_percent:+.2f}%)")

    return health

# Usage:
health = await check_account_health(account)
if "CRITICAL" in health["status"]:
    print("[WARNING] Account needs attention!")
```

### 4) Get server time

```python
async def get_server_time(account: MT5Account):
    """Get server time and timezone info"""
    summary = await account.account_summary()

    # Convert protobuf Timestamp to datetime
    server_time = summary.server_time.ToDatetime()

    # Get timezone offset
    tz_offset_minutes = summary.utc_timezone_server_time_shift_minutes
    tz_offset_hours = tz_offset_minutes / 60

    print(f"Server Time: {server_time}")
    print(f"UTC Offset: {tz_offset_hours:+.1f} hours")

    # Calculate local time
    from datetime import timedelta
    utc_time = datetime.utcnow()
    server_time_calculated = utc_time + timedelta(minutes=tz_offset_minutes)

    print(f"UTC Time: {utc_time}")
    print(f"Server Time (calculated): {server_time_calculated}")

    return server_time

# Usage:
server_time = await get_server_time(account)
```

### 5) Validate account before trading

```python
async def validate_for_trading(account: MT5Account) -> bool:
    """
    Validate account is ready for trading.

    Returns:
        True if account passes all checks
    """
    summary = await account.account_summary()

    # Check 1: Minimum balance
    min_balance = 100
    if summary.account_balance < min_balance:
        print(f"[ERROR] Balance too low: ${summary.account_balance:.2f} < ${min_balance}")
        return False

    # Check 2: Equity > Balance (no heavy losses)
    if summary.account_equity < summary.account_balance * 0.5:
        pnl = summary.account_equity - summary.account_balance
        print(f"[ERROR] Heavy losses: ${pnl:.2f}")
        return False

    # Check 3: Reasonable leverage
    if summary.account_leverage < 10 or summary.account_leverage > 500:
        print(f"[WARNING] Unusual leverage: 1:{summary.account_leverage}")

    # Check 4: Supported currency
    supported_currencies = ["USD", "EUR", "GBP"]
    if summary.account_currency not in supported_currencies:
        print(f"[WARNING] Unsupported currency: {summary.account_currency}")

    print(f"[OK] Account validation passed:")
    print(f"   Balance: ${summary.account_balance:.2f}")
    print(f"   Equity: ${summary.account_equity:.2f}")
    print(f"   Leverage: 1:{summary.account_leverage}")

    return True

# Usage:
if await validate_for_trading(account):
    # Start trading
    pass
else:
    print("Cannot trade on this account")
```

### 6) Log session start

```python
import logging
from datetime import datetime

async def log_session_start(account: MT5Account):
    """Log session start with full account details"""
    summary = await account.account_summary()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Get mode name
    mode_names = {0: "DEMO", 1: "CONTEST", 2: "REAL"}
    mode = mode_names.get(summary.account_trade_mode, "UNKNOWN")

    # Log session info
    logging.info("=" * 60)
    logging.info("TRADING SESSION STARTED")
    logging.info(f"Account: #{summary.account_login} ({summary.account_user_name})")
    logging.info(f"Broker: {summary.account_company_name}")
    logging.info(f"Mode: {mode}")
    logging.info(f"Balance: {summary.account_balance:.2f} {summary.account_currency}")
    logging.info(f"Leverage: 1:{summary.account_leverage}")

    # Server time
    server_time = summary.server_time.ToDatetime()
    logging.info(f"Server Time: {server_time}")
    logging.info("=" * 60)

# Usage:
await log_session_start(account)
```

### 7) Monitor account equity

```python
async def monitor_equity(account: MT5Account, interval: float = 10.0):
    """
    Monitor account equity changes.

    Args:
        account: MT5Account instance
        interval: Update interval in seconds
    """
    previous_equity = None

    while True:
        try:
            summary = await account.account_summary()

            equity = summary.account_equity
            balance = summary.account_balance
            floating = equity - balance

            # Calculate change
            if previous_equity is not None:
                change = equity - previous_equity
                change_pct = (change / previous_equity * 100) if previous_equity > 0 else 0

                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Equity: ${equity:,.2f} | "
                      f"Floating: ${floating:+,.2f} | "
                      f"Change: ${change:+.2f} ({change_pct:+.2f}%)")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Equity: ${equity:,.2f} | "
                      f"Floating: ${floating:+,.2f}")

            previous_equity = equity

        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(interval)

# Usage:
# await monitor_equity(account, interval=10.0)  # Update every 10 seconds
```

### 8) Compare multiple accounts

```python
from dataclasses import dataclass

@dataclass
class AccountSummary:
    login: int
    name: str
    balance: float
    equity: float
    leverage: int
    currency: str
    mode: str

async def compare_accounts(accounts: list[MT5Account]) -> list[AccountSummary]:
    """
    Get summaries for multiple accounts.

    Args:
        accounts: List of MT5Account instances

    Returns:
        List of AccountSummary objects
    """
    mode_names = {0: "DEMO", 1: "CONTEST", 2: "REAL"}
    summaries = []

    for account in accounts:
        summary = await account.account_summary()

        summaries.append(AccountSummary(
            login=summary.account_login,
            name=summary.account_user_name,
            balance=summary.account_balance,
            equity=summary.account_equity,
            leverage=summary.account_leverage,
            currency=summary.account_currency,
            mode=mode_names.get(summary.account_trade_mode, "UNKNOWN")
        ))

    # Print comparison
    print("\nAccount Comparison:")
    print("-" * 80)
    for s in summaries:
        pnl = s.equity - s.balance
        print(f"#{s.login:10} | {s.name:20} | {s.mode:8} | "
              f"${s.balance:10,.2f} | ${s.equity:10,.2f} | ${pnl:+10,.2f}")
    print("-" * 80)

    return summaries

# Usage:
# account1 = MT5Account(...)
# account2 = MT5Account(...)
# summaries = await compare_accounts([account1, account2])
```

---

## Common Patterns

### Account initialization check

```python
async def initialize_account(account: MT5Account):
    """Initialize and validate account connection"""
    # Connect
    await account.connect_by_host_port()

    # Get summary to verify connection
    summary = await account.account_summary()

    print(f"[OK] Connected to account #{summary.account_login}")
    print(f"   Balance: ${summary.account_balance:.2f} {summary.account_currency}")

    # Return summary for further use
    return summary
```

### Risk assessment

```python
async def assess_trading_risk(account: MT5Account) -> str:
    """Assess trading risk level"""
    summary = await account.account_summary()

    # Calculate risk factors
    balance = summary.account_balance
    equity = summary.account_equity
    leverage = summary.account_leverage

    # Risk score
    if leverage > 200:
        risk = "HIGH"
    elif leverage > 100:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # Check current losses
    if equity < balance * 0.9:
        risk = "HIGH"

    print(f"Risk Assessment: {risk}")
    print(f"  Leverage: 1:{leverage}")
    print(f"  Balance: ${balance:.2f}")
    print(f"  Equity: ${equity:.2f}")

    return risk
```

---

## 📚 See also

* [account_info_double](./account_info_double.md) - Get specific double account properties (margin, etc.)
* [account_info_integer](./account_info_integer.md) - Get specific integer account properties
* [account_info_string](./account_info_string.md) - Get specific string account properties
