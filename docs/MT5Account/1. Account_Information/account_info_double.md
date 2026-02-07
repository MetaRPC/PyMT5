# Getting Account Double Properties

> **Request:** specific double-type account property from **MT5** terminal using property identifier.

**API Information:**

* **Low-level API:** `MT5Account.account_info_double(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.AccountInformation`
* **Proto definition:** `AccountInfoDouble` (defined in `mt5-term-api-account-information.proto`)

### RPC

* **Service:** `mt5_term_api.AccountInformation`
* **Method:** `AccountInfoDouble(AccountInfoDoubleRequest) -> AccountInfoDoubleReply`
* **Low-level client (generated):** `AccountInformationStub.AccountInfoDouble(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Retrieve a specific double-type account property by ID (balance, equity, margin, etc.).
* **Why you need it.** Get individual account metrics without fetching all data. Useful for focused checks.
* **When to use.** Use `account_summary()` for multiple properties. Use this method for single property queries.

---

## 🎯 Purpose

Use it to query specific numeric account properties:

* Check account balance before trading
* Monitor margin usage and margin level
* Verify free margin availability
* Track floating profit/loss
* Monitor margin call and stop out levels

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [account_info_double - How it works](../HOW_IT_WORK/1. Account_information_HOW/account_info_double_HOW.md)**

---

## Method Signature

```python
async def account_info_double(
    self,
    property_id: account_info_pb2.AccountInfoDoublePropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> float
```

**Request message:**

```protobuf
message AccountInfoDoubleRequest {
  AccountInfoDoublePropertyType property_id = 1;
}
```

**Reply message:**

```protobuf
message AccountInfoDoubleReply {
  oneof response {
    AccountInfoDoubleData data = 1;
    Error error = 2;
  }
}

message AccountInfoDoubleData {
  double requested_value = 1;
}
```

---

## 🔽 Input

| Parameter     | Type                              | Description                                             |
| ------------- | --------------------------------- | ------------------------------------------------------- |
| `property_id` | `AccountInfoDoublePropertyType` (enum) | Property identifier specifying which property to retrieve |
| `deadline`    | `datetime` (optional)             | Deadline for the gRPC call (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                           |

**Deadline options:**

```python
from datetime import datetime, timedelta
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# 1. With deadline (recommended)
deadline = datetime.utcnow() + timedelta(seconds=3)
value = await account.account_info_double(
    property_id=account_info_pb2.ACCOUNT_BALANCE,
    deadline=deadline
)

# 2. With cancellation event
cancel_event = asyncio.Event()
value = await account.account_info_double(
    property_id=account_info_pb2.ACCOUNT_BALANCE,
    cancellation_event=cancel_event
)

# Later: cancel_event.set()

# 3. No deadline (uses default timeout if configured)
value = await account.account_info_double(
    property_id=account_info_pb2.ACCOUNT_BALANCE
)
```

---

## ⬆️ Output

| Field             | Type      | Python Type | Description                                      |
| ----------------- | --------- | ----------- | ------------------------------------------------ |
| `requested_value` | `double`  | `float`     | The value of the requested account property      |

**Return value:** The method directly returns `float` (extracted from `AccountInfoDoubleData.requested_value`).

---

## 🧱 Related enums (from proto)

> **💡 Note:** The tables show simplified constant names for readability.
> In Python code, you can use either the full or short form:
>
> **Full format:** `account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE`
> **Short format:** `account_info_pb2.ACCOUNT_BALANCE`
>
> Both forms are valid in Python protobuf. We recommend the **short format** for simplicity.

### `AccountInfoDoublePropertyType`

Defined in `mt5-term-api-account-information.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `ACCOUNT_BALANCE` | 0 | Account balance in the deposit currency |
| `ACCOUNT_CREDIT` | 1 | Account credit in the deposit currency |
| `ACCOUNT_PROFIT` | 2 | Current profit of an account in the deposit currency |
| `ACCOUNT_EQUITY` | 3 | Account equity in the deposit currency |
| `ACCOUNT_MARGIN` | 4 | Account margin used in the deposit currency |
| `ACCOUNT_MARGIN_FREE` | 5 | Free margin of an account in the deposit currency |
| `ACCOUNT_MARGIN_LEVEL` | 6 | Account margin level in percents |
| `ACCOUNT_MARGIN_SO_CALL` | 7 | Margin call level (in % or deposit currency) |
| `ACCOUNT_MARGIN_SO_SO` | 8 | Margin stop out level (in % or deposit currency) |
| `ACCOUNT_MARGIN_INITIAL` | 9 | Initial margin (reserved for pending orders) |
| `ACCOUNT_MARGIN_MAINTENANCE` | 10 | Maintenance margin (minimum equity reserved) |
| `ACCOUNT_ASSETS` | 11 | Current assets of an account |
| `ACCOUNT_LIABILITIES` | 12 | Current liabilities on an account |
| `ACCOUNT_COMMISSION_BLOCKED` | 13 | Current blocked commission amount |

**Usage in Python:**
```python
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# Access constants directly
property_id = account_info_pb2.ACCOUNT_BALANCE  # = 0
# or use full enum name
property_id = account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE  # = 0
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Property types:** Margin call and stop out levels can be in percents or deposit currency depending on account settings.
* **Thread safety:** All async methods are safe to call concurrently from multiple asyncio tasks.

---

## 🔗 Usage Examples

### 1) Get account balance

```python
import asyncio
from datetime import datetime, timedelta
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

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

        # Get balance
        balance = await account.account_info_double(
            property_id=account_info_pb2.ACCOUNT_BALANCE,
            deadline=deadline
        )

        print(f"Account Balance: ${balance:.2f}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Get current equity

```python
async def get_equity(account: MT5Account) -> float:
    """Get current account equity"""
    deadline = datetime.utcnow() + timedelta(seconds=3)

    equity = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_EQUITY,
        deadline=deadline
    )

    return equity

# Usage:
equity = await get_equity(account)
print(f"Current Equity: ${equity:.2f}")
```

### 3) Check margin level before trading

```python
async def check_margin_level(account: MT5Account, min_level: float = 200.0) -> bool:
    """
    Check if margin level is above minimum threshold.

    Args:
        account: MT5Account instance
        min_level: Minimum required margin level (%)

    Returns:
        True if margin level is sufficient

    Raises:
        ValueError: If margin level is below minimum
    """
    deadline = datetime.utcnow() + timedelta(seconds=3)

    margin_level = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_LEVEL,
        deadline=deadline
    )

    print(f"Margin Level: {margin_level:.2f}%")

    if margin_level < min_level:
        raise ValueError(
            f"Margin level {margin_level:.2f}% is below minimum {min_level:.2f}%"
        )

    return True

# Usage:
try:
    await check_margin_level(account, min_level=200.0)
    print("[OK] Safe to trade")
except ValueError as e:
    print(f"[ERROR] Cannot trade: {e}")
```

### 4) Get free margin

```python
async def get_free_margin(account: MT5Account) -> float:
    """Get available free margin"""
    # No deadline - uses default timeout
    free_margin = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE
    )

    return free_margin

# Usage:
free_margin = await get_free_margin(account)
print(f"Free Margin: ${free_margin:.2f}")
```

### 5) Monitor floating profit/loss

```python
async def monitor_profit(account: MT5Account, interval: float = 5.0):
    """Monitor floating P/L every N seconds"""
    while True:
        try:
            deadline = datetime.utcnow() + timedelta(seconds=3)

            profit = await account.account_info_double(
                property_id=account_info_pb2.ACCOUNT_PROFIT,
                deadline=deadline
            )

            sign = "+" if profit >= 0 else ""
            timestamp = datetime.now().strftime("%H:%M:%S")

            print(f"[{timestamp}] Floating P/L: {sign}${profit:.2f}")

        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(interval)

# Usage:
# await monitor_profit(account, interval=5.0)  # Update every 5 seconds
```

### 6) Check multiple properties sequentially

```python
from dataclasses import dataclass

@dataclass
class MarginInfo:
    used_margin: float
    free_margin: float
    margin_level: float

async def get_margin_info(account: MT5Account) -> MarginInfo:
    """Get comprehensive margin information"""
    deadline = datetime.utcnow() + timedelta(seconds=10)

    # Get used margin
    used_margin = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN,
        deadline=deadline
    )

    # Get free margin
    free_margin = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE,
        deadline=deadline
    )

    # Get margin level
    margin_level = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_LEVEL,
        deadline=deadline
    )

    return MarginInfo(
        used_margin=used_margin,
        free_margin=free_margin,
        margin_level=margin_level
    )

# Usage:
info = await get_margin_info(account)
print(f"Margin Info:")
print(f"  Used: ${info.used_margin:.2f}")
print(f"  Free: ${info.free_margin:.2f}")
print(f"  Level: {info.margin_level:.2f}%")

# Note: For better performance, use account_summary() instead
# to get all properties in one call
```

### 7) With cancellation event

```python
async def get_balance_cancellable(account: MT5Account, cancel_event: asyncio.Event) -> float:
    """Get balance with cancellation support"""
    try:
        balance = await account.account_info_double(
            property_id=account_info_pb2.ACCOUNT_BALANCE,
            cancellation_event=cancel_event
        )
        return balance
    except asyncio.CancelledError:
        print("Operation cancelled")
        raise

# Usage:
cancel_event = asyncio.Event()

# Start operation
task = asyncio.create_task(get_balance_cancellable(account, cancel_event))

# Cancel after 1 second
await asyncio.sleep(1)
cancel_event.set()

try:
    balance = await task
except asyncio.CancelledError:
    print("Cancelled by user")
```

---

## 🔧 Common Patterns

### Safe trading check

```python
async def can_trade(account: MT5Account, required_margin: float) -> bool:
    """
    Check if account has enough free margin to trade.

    Args:
        account: MT5Account instance
        required_margin: Required margin for the trade

    Returns:
        True if sufficient margin available
    """
    deadline = datetime.utcnow() + timedelta(seconds=3)

    free_margin = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE,
        deadline=deadline
    )

    if free_margin < required_margin:
        print(f"[ERROR] Insufficient margin: need ${required_margin:.2f}, have ${free_margin:.2f}")
        return False

    print(f"[OK] Sufficient margin: ${free_margin:.2f} available")
    return True
```

### Margin level warning system

```python
async def check_margin_warning(account: MT5Account):
    """Check margin level and warn if too low"""
    deadline = datetime.utcnow() + timedelta(seconds=3)

    level = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_LEVEL,
        deadline=deadline
    )

    if level < 100:
        print(f"[CRITICAL] Margin level {level:.2f}% - Stop out imminent!")
    elif level < 200:
        print(f"[WARNING] Margin level {level:.2f}% - Margin call zone")
    elif level < 500:
        print(f"[CAUTION] Margin level {level:.2f}% - Monitor closely")
    else:
        print(f"[OK] Margin level {level:.2f}%")
```

### Account health check

```python
async def check_account_health(account: MT5Account):
    """Comprehensive account health check"""
    deadline = datetime.utcnow() + timedelta(seconds=5)

    # Get all critical metrics
    balance = await account.account_info_double(
        account_info_pb2.ACCOUNT_BALANCE,
        deadline
    )

    equity = await account.account_info_double(
        account_info_pb2.ACCOUNT_EQUITY,
        deadline
    )

    profit = await account.account_info_double(
        account_info_pb2.ACCOUNT_PROFIT,
        deadline
    )

    margin_level = await account.account_info_double(
        account_info_pb2.ACCOUNT_MARGIN_LEVEL,
        deadline
    )

    print(f"Account Health Report:")
    print(f"  Balance: ${balance:.2f}")
    print(f"  Equity: ${equity:.2f}")
    print(f"  Floating P/L: ${profit:+.2f}")
    print(f"  Margin Level: {margin_level:.2f}%")

    # Health score
    if margin_level > 500 and equity >= balance:
        print("  Status: [HEALTHY]")
    elif margin_level > 200:
        print("  Status: [MODERATE]")
    else:
        print("  Status: [RISKY]")
```

---

## 📚 See also

* [account_summary](./account_summary.md) - Get all account properties in one call (RECOMMENDED)
* [account_info_integer](./account_info_integer.md) - Get specific integer account properties
* [account_info_string](./account_info_string.md) - Get specific string account properties
