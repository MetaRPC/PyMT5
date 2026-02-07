# Getting Account Integer Properties

> **Request:** specific integer-type account property from **MT5** terminal using property identifier.

**API Information:**

* **Low-level API:** `MT5Account.account_info_integer(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.AccountInformation`
* **Proto definition:** `AccountInfoInteger` (defined in `mt5-term-api-account-information.proto`)

### RPC

* **Service:** `mt5_term_api.AccountInformation`
* **Method:** `AccountInfoInteger(AccountInfoIntegerRequest) -> AccountInfoIntegerReply`
* **Low-level client (generated):** `AccountInformationStub.AccountInfoInteger(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Retrieve a specific integer-type account property by ID (login, leverage, trade mode, etc.).
* **Why you need it.** Get individual account settings without fetching all data. Useful for configuration checks.
* **When to use.** Use `account_summary()` for multiple properties. Use this method for single property queries.

---

## 🎯 Purpose

Use it to query specific integer account properties:

* Get account login number
* Check account leverage
* Verify trading permissions (trade allowed, expert allowed)
* Check account trade mode (demo/real/contest)
* Get maximum pending orders limit
* Verify margin calculation mode
* Check FIFO close and hedge settings

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [account_info_integer - How it works](../HOW_IT_WORK/1. Account_information_HOW/account_info_integer_HOW.md)**

---

## Method Signature

```python
async def account_info_integer(
    self,
    property_id: account_info_pb2.AccountInfoIntegerPropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> int
```

**Request message:**

```protobuf
message AccountInfoIntegerRequest {
  AccountInfoIntegerPropertyType property_id = 1;
}
```

**Reply message:**

```protobuf
message AccountInfoIntegerReply {
  oneof response {
    AccountInfoIntegerData data = 1;
    Error error = 2;
  }
}

message AccountInfoIntegerData {
  int64 requested_value = 1;
}
```

---

## 🔽 Input

| Parameter     | Type                              | Description                                             |
| ------------- | --------------------------------- | ------------------------------------------------------- |
| `property_id` | `AccountInfoIntegerPropertyType` (enum) | Property identifier specifying which property to retrieve |
| `deadline`    | `datetime` (optional)             | Deadline for the gRPC call (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                           |

**Deadline options:**

```python
from datetime import datetime, timedelta
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# 1. With deadline (recommended)
deadline = datetime.utcnow() + timedelta(seconds=3)
value = await account.account_info_integer(
    property_id=account_info_pb2.ACCOUNT_LEVERAGE,
    deadline=deadline
)

# 2. With cancellation event
cancel_event = asyncio.Event()
value = await account.account_info_integer(
    property_id=account_info_pb2.ACCOUNT_LEVERAGE,
    cancellation_event=cancel_event
)

# 3. No deadline (uses default timeout if configured)
value = await account.account_info_integer(
    property_id=account_info_pb2.ACCOUNT_LEVERAGE
)
```

---

## ⬆️ Output

| Field             | Type    | Python Type | Description                                      |
| ----------------- | ------- | ----------- | ------------------------------------------------ |
| `requested_value` | `int64` | `int`       | The value of the requested account property      |

**Return value:** The method directly returns `int` (extracted from `AccountInfoIntegerData.requested_value`).

---

## 🧱 Related enums (from proto)

> **Note:** The tables show simplified constant names for readability.
> In Python code, you can use either the full or short form:
>
> **Full format:** `account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE`
> **Short format:** `account_info_pb2.ACCOUNT_LEVERAGE`
>
> Both forms are valid in Python protobuf. We recommend the **short format** for simplicity.

### `AccountInfoIntegerPropertyType`

Defined in `mt5-term-api-account-information.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `ACCOUNT_LOGIN` | 0 | Account number |
| `ACCOUNT_TRADE_MODE` | 1 | Account trade mode (demo/real/contest) |
| `ACCOUNT_LEVERAGE` | 2 | Account leverage |
| `ACCOUNT_LIMIT_ORDERS` | 3 | Maximum allowed number of active pending orders |
| `ACCOUNT_MARGIN_SO_MODE` | 4 | Mode for setting the minimal allowed margin |
| `ACCOUNT_TRADE_ALLOWED` | 5 | Allowed trade for the current account |
| `ACCOUNT_TRADE_EXPERT` | 6 | Allowed trade for an Expert Advisor |
| `ACCOUNT_MARGIN_MODE` | 7 | Margin calculation mode |
| `ACCOUNT_CURRENCY_DIGITS` | 8 | Number of digits after decimal point for account currency |
| `ACCOUNT_FIFO_CLOSE` | 9 | Flag that a position can be closed only by FIFO rule |
| `ACCOUNT_HEDGE_ALLOWED` | 10 | Hedging is allowed |

**Usage in Python:**
```python
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# Access constants directly
property_id = account_info_pb2.ACCOUNT_LEVERAGE  # = 2
# or use full enum name
property_id = account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE  # = 2
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Prefer account_summary:** For multiple properties, use `account_summary()` instead to avoid multiple round-trips.
* **Connection required:** You must call `connect_by_host_port()` or `connect_by_server_name()` before using this method.
* **Boolean values:** Properties like `TRADE_ALLOWED`, `TRADE_EXPERT`, `FIFO_CLOSE`, `HEDGE_ALLOWED` return 1 (true) or 0 (false).
* **Thread safety:** All async methods are safe to call concurrently from multiple asyncio tasks.
* **UUID handling:** The terminal instance UUID is auto-generated by the server if not provided. 
  For explicit control (e.g., in streaming scenarios), pass `id_=uuid4()` to constructor.

---

## 🔗 Usage Examples

### 1) Get account leverage

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

        # Get leverage
        leverage = await account.account_info_integer(
            property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE,
            deadline=deadline
        )

        print(f"Account Leverage: 1:{leverage}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Get account login number

```python
async def get_account_login(account: MT5Account) -> int:
    """Get account login number"""
    deadline = datetime.utcnow() + timedelta(seconds=3)

    login = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LOGIN,
        deadline=deadline
    )

    return login

# Usage:
login = await get_account_login(account)
print(f"Account Login: {login}")
```

### 3) Check if trading is allowed

```python
async def is_trading_allowed(account: MT5Account) -> bool:
    """
    Check if trading is allowed for this account.

    Returns:
        True if trading is allowed, False otherwise
    """
    deadline = datetime.utcnow() + timedelta(seconds=3)

    trade_allowed = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_ALLOWED,
        deadline=deadline
    )

    # Returns 1 (true) or 0 (false)
    is_allowed = bool(trade_allowed)

    if is_allowed:
        print("[OK] Trading is allowed")
    else:
        print("[ERROR] Trading is disabled")

    return is_allowed

# Usage:
if await is_trading_allowed(account):
    # Place orders
    pass
else:
    print("Cannot trade on this account")
```

### 4) Check Expert Advisor permissions

```python
async def is_ea_allowed(account: MT5Account) -> bool:
    """Check if Expert Advisors are allowed to trade"""
    deadline = datetime.utcnow() + timedelta(seconds=3)

    ea_allowed = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_EXPERT,
        deadline=deadline
    )

    return bool(ea_allowed)

# Usage:
if await is_ea_allowed(account):
    print("[OK] Expert Advisors can trade")
else:
    print("[ERROR] Expert Advisors are disabled")
```

### 5) Get maximum pending orders limit

```python
async def get_max_pending_orders(account: MT5Account) -> int:
    """Get maximum allowed number of pending orders"""
    deadline = datetime.utcnow() + timedelta(seconds=3)

    limit = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LIMIT_ORDERS,
        deadline=deadline
    )

    return limit

# Usage:
max_orders = await get_max_pending_orders(account)
print(f"Maximum pending orders: {max_orders}")

if max_orders == 0:
    print("[WARNING] No limit on pending orders (or unlimited)")
```

### 6) Check account type (demo/real/contest)

```python
async def get_account_type(account: MT5Account) -> str:
    """
    Get account trade mode.

    Returns:
        "DEMO", "CONTEST", or "REAL"
    """
    deadline = datetime.utcnow() + timedelta(seconds=3)

    trade_mode = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_MODE,
        deadline=deadline
    )

    # Map to readable names
    mode_map = {
        0: "DEMO",
        1: "CONTEST",
        2: "REAL"
    }

    mode_name = mode_map.get(trade_mode, f"UNKNOWN ({trade_mode})")
    print(f"Account Type: {mode_name}")

    return mode_name

# Usage:
account_type = await get_account_type(account)

if account_type == "DEMO":
    print("[WARNING] Running on demo account")
elif account_type == "REAL":
    print("[CRITICAL] Running on real account - be careful!")
```

### 7) Check hedging settings

```python
async def check_hedging_settings(account: MT5Account):
    """Check if hedging and FIFO close are enabled"""
    deadline = datetime.utcnow() + timedelta(seconds=5)

    # Check if hedging is allowed
    hedge_allowed = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_HEDGE_ALLOWED,
        deadline=deadline
    )

    # Check FIFO close rule
    fifo_close = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_FIFO_CLOSE,
        deadline=deadline
    )

    print(f"Hedging Settings:")
    print(f"  Hedging allowed: {'Yes' if hedge_allowed else 'No'}")
    print(f"  FIFO close: {'Enabled' if fifo_close else 'Disabled'}")

    return {
        "hedge_allowed": bool(hedge_allowed),
        "fifo_close": bool(fifo_close)
    }

# Usage:
settings = await check_hedging_settings(account)

if settings["hedge_allowed"]:
    print("[OK] Can open opposite positions on same symbol")
else:
    print("[INFO] Cannot hedge - only netting mode")
```

---

## Common Patterns

### Pre-trade validation

```python
async def validate_account_for_trading(account: MT5Account) -> bool:
    """
    Validate account is ready for trading.

    Returns:
        True if account is ready to trade
    """
    deadline = datetime.utcnow() + timedelta(seconds=5)

    # Check trading is allowed
    trade_allowed = await account.account_info_integer(
        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_ALLOWED,
        deadline
    )

    if not trade_allowed:
        print("[ERROR] Trading is disabled on this account")
        return False

    # Check leverage is reasonable
    leverage = await account.account_info_integer(
        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE,
        deadline
    )

    if leverage < 1:
        print("[ERROR] Invalid leverage setting")
        return False

    print(f"[OK] Account ready to trade (Leverage: 1:{leverage})")
    return True
```

### Account type checker

```python
async def require_demo_account(account: MT5Account):
    """Ensure we're running on demo account (safety check)"""
    trade_mode = await account.account_info_integer(
        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_MODE
    )

    if trade_mode != 0:  # 0 = DEMO
        raise RuntimeError(
            f"[CRITICAL] This script requires DEMO account! Current mode: {trade_mode}"
        )

    print("[OK] Confirmed: Running on DEMO account")
```

---

## 📚 See also

* [account_summary](./account_summary.md) - Get all account properties in one call (RECOMMENDED)
* [account_info_double](./account_info_double.md) - Get specific double account properties
* [account_info_string](./account_info_string.md) - Get specific string account properties
