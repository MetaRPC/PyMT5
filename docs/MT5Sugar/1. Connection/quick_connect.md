# Quick Connect to MT5 Cluster (`quick_connect`)

> **Sugar method:** Easiest way to connect to MT5 server by cluster name.

**API Information:**

* **Method:** `sugar.quick_connect(cluster_name, timeout_seconds=30)`
* **Returns:** None (raises exception on failure)
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def quick_connect(
    self,
    cluster_name: str,
    timeout_seconds: int = 30,
    **kwargs
) -> None
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `cluster_name` | `str` | Yes | - | MT5 cluster identifier (e.g., "FxPro-MT5 Demo") |
| `timeout_seconds` | `int` | No | `30` | Seconds to wait for the terminal to become ready |
| `**kwargs` | - | No | - | Reserved for forward-compatible connection options |

---

## Return Value

| Type | Description |
|------|-------------|
| `None` | Returns nothing on success, raises exception on failure |

**Raises:**

- `RuntimeError` if credentials not accessible in MT5Account
- `Exception` if connection to cluster fails

---

## 🏛️ Essentials

**What it does:**

- Connects to MT5 server using cluster name
- Uses credentials from MT5Account
- Validates connection with terminal
- Waits up to 30 seconds for terminal ready
- Updates session GUID from server

**Key behaviors:**

- Simplest connection method (just cluster name)
- Uses connect_by_server_name internally
- Blocks until terminal ready or timeout
- Perfect for reconnecting or switching accounts

---

## ⚡ Under the Hood

```
MT5Sugar.quick_connect()
    ↓ validates credentials
    ↓ calls
MT5Account.connect_by_server_name()
    ↓ gRPC protobuf
AccountHelperService.ConnectEx()
    ↓ MT5 Terminal
    ↓ waits for terminal ready (30s timeout)
    ↓ updates session GUID
```

**Call chain:**

1. Sugar accesses underlying MT5Account
2. Validates user and password attributes exist
3. Calls Account.connect_by_server_name() with cluster name
4. Account sends ConnectEx gRPC request to terminal
5. Terminal validates credentials and connects
6. Waits for terminal_is_alive with 30 second timeout
7. Updates session GUID from server response
8. Returns on success or raises exception

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:340`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:436`

---

## When to Use

**Use `quick_connect()` when:**

- First connection to MT5 server
- Reconnecting after disconnection
- Switching between demo/live clusters
- Simple connection without complex setup

**Don't use when:**

- Need custom connection parameters
- Don't know cluster name
- Want non-blocking connection

---

## 🔗 Examples

### Example 1: Basic Connection

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def connect_simple():
    # Create account with credentials
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    # Connect to FxPro demo cluster
    await sugar.quick_connect("FxPro-MT5 Demo")

    print("Connected successfully")

    # Check connection
    if sugar.is_connected():
        balance = await sugar.get_balance()
        print(f"Balance: ${balance}")
```

### Example 2: Connect with a Custom Timeout

```python
async def connect_custom_timeout():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    # Allow up to 60 seconds for the terminal to become ready
    await sugar.quick_connect(
        cluster_name="ICMarkets-Demo",
        timeout_seconds=60
    )

    print("Connected")
```

### Example 3: Auto-Reconnect on Failure

```python
import asyncio

async def connect_with_retry():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    max_retries = 3
    cluster = "FxPro-MT5 Demo"

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Connection attempt {attempt}/{max_retries}...")

            await sugar.quick_connect(cluster)

            print("Connected successfully")
            break

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

            if attempt < max_retries:
                wait_time = attempt * 2  # 2, 4, 6 seconds
                print(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                print("All connection attempts failed")
                raise

    # Verify connection
    if await sugar.ping():
        print("Server is responsive")
```

---

## Common Pitfalls

**Pitfall 1: Wrong cluster name**
```python
# ERROR: Cluster name doesn't exist or typo
try:
    await sugar.quick_connect("FxPro-MT5-Demo")  # Wrong hyphen
except Exception as e:
    print(e)  # Connection failed
```

**Solution:** Use exact cluster name from broker
```python
# Get cluster name from your broker's documentation
await sugar.quick_connect("FxPro-MT5 Demo")  # Correct
```

**Pitfall 2: Credentials not set**
```python
# ERROR: MT5Account created without credentials
account = MT5Account(id_=uuid4())  # No user/password
service = MT5Service(account)
sugar = MT5Sugar(service)

try:
    await sugar.quick_connect("FxPro-MT5 Demo")
except RuntimeError as e:
    print(e)  # "Cannot connect: credentials not accessible"
```

**Solution:** Always use create() with credentials
```python
account = MT5Account.create(
    user=591129415,
    password="your_password",
    grpc_server="mt5.mrpc.pro:443"
)
```

**Pitfall 3: Not handling connection failure**

```python
# No error handling
await sugar.quick_connect("FxPro-MT5 Demo")
# If fails, program crashes
```

**Solution:** Wrap in try-except
```python
try:
    await sugar.quick_connect("FxPro-MT5 Demo")
    print("Connected")
except Exception as e:
    print(f"Connection failed: {e}")
    # Handle gracefully
```

---

## Pro Tips

**Tip 1: Store cluster name in config**
```python
# config.py
CLUSTER_NAME = "FxPro-MT5 Demo"
CONNECT_TIMEOUT = 30

# main.py
from config import CLUSTER_NAME, CONNECT_TIMEOUT

await sugar.quick_connect(CLUSTER_NAME, CONNECT_TIMEOUT)
```

**Tip 2: Verify connection after connect**
```python
await sugar.quick_connect("FxPro-MT5 Demo")

# Verify both channel and server
assert sugar.is_connected(), "Channel not connected"
assert await sugar.ping(), "Server not responding"

print("Fully connected and verified")
```

**Tip 3: Switch between demo and live**
```python
# Connect to demo
await sugar.quick_connect("FxPro-MT5 Demo")
print("Trading on DEMO")

# Later: switch to live (if using different account)
# Note: Need to create new MT5Account with live credentials
# quick_connect() uses existing credentials
```

**Tip 4: Use context for automatic cleanup**

```python
async def trade_session():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    try:
        await sugar.quick_connect("FxPro-MT5 Demo")

        # Do trading operations
        balance = await sugar.get_balance()
        print(f"Balance: ${balance}")

    finally:
        # Cleanup if needed
        print("Session ended")
```

---

## 📚 See Also

- [is_connected](is_connected.md) - Check connection status
- [ping](ping.md) - Test server responsiveness
