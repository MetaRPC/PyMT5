# Getting Account String Properties

> **Request:** specific string-type account property from **MT5** terminal using property identifier.

**API Information:**

* **Low-level API:** `MT5Account.account_info_string(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.AccountInformation`
* **Proto definition:** `AccountInfoString` (defined in `mt5-term-api-account-information.proto`)

### RPC

* **Service:** `mt5_term_api.AccountInformation`
* **Method:** `AccountInfoString(AccountInfoStringRequest) -> AccountInfoStringReply`
* **Low-level client (generated):** `AccountInformationStub.AccountInfoString(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Retrieve a specific string-type account property by ID (name, server, currency, company).
* **Why you need it.** Get individual account text properties without fetching all data. Useful for logging and configuration.
* **When to use.** Use `account_summary()` for multiple properties. Use this method for single property queries.

---

## 🎯 Purpose

Use it to query specific string account properties:

* Get account owner name
* Get trading server name
* Get account currency (USD, EUR, etc.)
* Get broker/company name
* Verify server connection
* Log account details

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [account_info_string - How it works](../HOW_IT_WORK/1. Account_information_HOW/account_info_string_HOW.md)**

---

## Method Signature

```python
async def account_info_string(
    self,
    property_id: account_info_pb2.AccountInfoStringPropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> str
```

**Request message:**

```protobuf
message AccountInfoStringRequest {
  AccountInfoStringPropertyType property_id = 1;
}
```

**Reply message:**

```protobuf
message AccountInfoStringReply {
  oneof response {
    AccountInfoStringData data = 1;
    Error error = 2;
  }
}

message AccountInfoStringData {
  string requested_value = 1;
}
```

---

## 🔽 Input

| Parameter     | Type                              | Description                                             |
| ------------- | --------------------------------- | ------------------------------------------------------- |
| `property_id` | `AccountInfoStringPropertyType` (enum) | Property identifier specifying which property to retrieve |
| `deadline`    | `datetime` (optional)             | Deadline for the gRPC call (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                           |

**Deadline options:**

```python
from datetime import datetime, timedelta
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# 1. With deadline (recommended)
deadline = datetime.utcnow() + timedelta(seconds=3)
value = await account.account_info_string(
    property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
    deadline=deadline
)

# 2. With cancellation event
cancel_event = asyncio.Event()
value = await account.account_info_string(
    property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
    cancellation_event=cancel_event
)

# 3. No deadline (uses default timeout if configured)
value = await account.account_info_string(
    property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY
)
```

---

## ⬆️ Output

| Field             | Type     | Python Type | Description                                      |
| ----------------- | -------- | ----------- | ------------------------------------------------ |
| `requested_value` | `string` | `str`       | The value of the requested account property      |

**Return value:** The method directly returns `str` (extracted from `AccountInfoStringData.requested_value`).

---

## 🧱 Related enums (from proto)

> **Note:** In Python code, you should use the full enum class path for type safety and clarity:
>
> **Recommended:** `account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY`
> **Also valid:** `account_info_pb2.ACCOUNT_CURRENCY` (direct access)
>
> We recommend the **full format** for better IDE support and to avoid confusion between different property types.

### `AccountInfoStringPropertyType`

Defined in `mt5-term-api-account-information.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `ACCOUNT_NAME` | 0 | Client name |
| `ACCOUNT_SERVER` | 1 | Trade server name |
| `ACCOUNT_CURRENCY` | 2 | Account currency (USD, EUR, etc.) |
| `ACCOUNT_COMPANY` | 3 | Name of a company that serves the account |

**Usage in Python:**
```python
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# Recommended: use full enum class path
property_id = account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY  # = 2

# Also valid: direct access (but less clear)
property_id = account_info_pb2.ACCOUNT_CURRENCY  # = 2
```

---

## 🧩 Notes & Tips

* **Prefer account_summary:** For multiple properties, use `account_summary()` instead to avoid multiple round-trips.
* **Connection required:** You must call `connect_by_host_port()` or `connect_by_server_name()` before using this method.
* **Currency format:** Currency is returned as 3-letter code (USD, EUR, GBP, etc.).

---

## 🔗 Usage Examples

### 1) Get account currency

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

        # Get currency
        currency = await account.account_info_string(
            property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
            deadline=deadline
        )

        print(f"Account Currency: {currency}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Get account owner name

```python
async def get_account_name(account: MT5Account) -> str:
    """Get account owner name"""
    deadline = datetime.utcnow() + timedelta(seconds=3)

    name = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline=deadline
    )

    return name

# Usage:
name = await get_account_name(account)
print(f"Account Name: {name}")
```

### 3) Get trading server name

```python
async def get_server_name(account: MT5Account) -> str:
    """Get trading server name"""
    deadline = datetime.utcnow() + timedelta(seconds=3)

    server = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline=deadline
    )

    return server

# Usage:
server = await get_server_name(account)
print(f"Trading Server: {server}")
```

### 4) Get broker company name

```python
async def get_broker_name(account: MT5Account) -> str:
    """Get broker/company name"""
    deadline = datetime.utcnow() + timedelta(seconds=3)

    company = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline=deadline
    )

    return company

# Usage:
broker = await get_broker_name(account)
print(f"Broker: {broker}")
```

### 5) Log account details

```python
async def log_account_details(account: MT5Account):
    """Log all string account properties"""
    deadline = datetime.utcnow() + timedelta(seconds=10)

    # Get all string properties
    name = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline
    )

    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline
    )

    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
        deadline
    )

    company = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline
    )

    # Log details
    print(f"=" * 50)
    print(f"Account Details:")
    print(f"  Owner: {name}")
    print(f"  Server: {server}")
    print(f"  Currency: {currency}")
    print(f"  Broker: {company}")
    print(f"=" * 50)

# Usage:
await log_account_details(account)
```

### 6) Verify server connection

```python
async def verify_server_connection(account: MT5Account, expected_server: str) -> bool:
    """
    Verify we're connected to the expected server.

    Args:
        account: MT5Account instance
        expected_server: Expected server name

    Returns:
        True if connected to correct server
    """
    deadline = datetime.utcnow() + timedelta(seconds=3)

    server = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline=deadline
    )

    if server.lower() != expected_server.lower():
        print(f"[WARNING] Connected to {server}, expected {expected_server}")
        return False

    print(f"[OK] Confirmed: Connected to {server}")
    return True

# Usage:
if not await verify_server_connection(account, "MetaQuotes-Demo"):
    raise RuntimeError("Wrong server!")
```

### 7) Currency-based formatting

```python
async def format_balance(account: MT5Account, balance: float) -> str:
    """
    Format balance with account currency symbol.

    Args:
        account: MT5Account instance
        balance: Balance amount

    Returns:
        Formatted balance string
    """
    deadline = datetime.utcnow() + timedelta(seconds=3)

    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
        deadline
    )

    # Map currency codes to symbols
    currency_symbols = {
        "USD": "$",
        "EUR": "EUR",
        "GBP": "GBP",
        "JPY": "JPY",
        "CHF": "CHF",
        "AUD": "A$",
        "CAD": "C$"
    }

    symbol = currency_symbols.get(currency, currency + " ")

    # Format based on currency
    if currency == "JPY":
        # JPY doesn't use decimal places
        return f"{symbol}{balance:.0f}"
    else:
        return f"{symbol}{balance:.2f}"

# Usage:
balance = 10000.50
formatted = await format_balance(account, balance)
print(f"Balance: {formatted}")  # Output: Balance: $10000.50
```

### 8) Generate session header

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SessionInfo:
    timestamp: str
    account_name: str
    broker: str
    server: str
    currency: str

async def get_session_info(account: MT5Account) -> SessionInfo:
    """Get comprehensive session information for logging"""
    deadline = datetime.utcnow() + timedelta(seconds=10)

    # Get all string properties
    name = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline
    )

    company = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline
    )

    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline
    )

    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
        deadline
    )

    return SessionInfo(
        timestamp=datetime.now().isoformat(),
        account_name=name,
        broker=company,
        server=server,
        currency=currency
    )

# Usage:
session = await get_session_info(account)
print(f"Session started: {session.timestamp}")
print(f"Account: {session.account_name}")
print(f"Broker: {session.broker} ({session.server})")
print(f"Currency: {session.currency}")
```

---

## Common Patterns

### Account identification

```python
async def get_account_identifier(account: MT5Account) -> str:
    """
    Generate unique account identifier for logging.

    Returns:
        Identifier string: "name@server (broker)"
    """
    deadline = datetime.utcnow() + timedelta(seconds=5)

    name = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline
    )

    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline
    )

    company = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline
    )

    identifier = f"{name}@{server} ({company})"
    return identifier

# Usage:
account_id = await get_account_identifier(account)
print(f"Trading as: {account_id}")
# Output: Trading as: John Doe@MetaQuotes-Demo (MetaQuotes Software Corp.)
```

### Currency validator

```python
async def validate_account_currency(
    account: MT5Account,
    allowed_currencies: list[str]
) -> bool:
    """
    Validate account currency is in allowed list.

    Args:
        account: MT5Account instance
        allowed_currencies: List of allowed currency codes (e.g., ["USD", "EUR"])

    Returns:
        True if currency is allowed
    """
    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY
    )

    if currency not in allowed_currencies:
        print(f"[ERROR] Currency {currency} not allowed. Allowed: {allowed_currencies}")
        return False

    print(f"[OK] Currency {currency} is valid")
    return True

# Usage:
if not await validate_account_currency(account, ["USD", "EUR"]):
    raise ValueError("Account currency not supported")
```

### Server environment checker

```python
async def get_environment(account: MT5Account) -> str:
    """
    Determine environment (production/demo) based on server name.

    Returns:
        "PRODUCTION", "DEMO", or "UNKNOWN"
    """
    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER
    )

    server_lower = server.lower()

    if "demo" in server_lower:
        return "DEMO"
    elif "real" in server_lower or "live" in server_lower:
        return "PRODUCTION"
    else:
        return "UNKNOWN"

# Usage:
env = await get_environment(account)
print(f"Environment: {env}")

if env == "PRODUCTION":
    print("[WARNING] Trading on PRODUCTION server!")
```

---

## 📚 See also

* [account_summary](./account_summary.md) - Get all account properties in one call (RECOMMENDED)
* [account_info_double](./account_info_double.md) - Get specific double account properties
* [account_info_integer](./account_info_integer.md) - Get specific integer account properties
