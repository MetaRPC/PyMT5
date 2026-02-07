# Check Connection Status (`is_connected`)

> **Sugar method:** Checks if gRPC connection to MT5 server is active.

**API Information:**

* **Method:** `sugar.is_connected()`
* **Returns:** `True` if connected, `False` otherwise
* **Layer:** HIGH (MT5Sugar)
* **Type:** Synchronous method (no async/await)

---

## Method Signature

```python
def is_connected(self) -> bool
```

---

## 🔽 Input Parameters

None

---

## Return Value

| Type | Description |
|------|-------------|
| `bool` | `True` if gRPC channel is READY or IDLE, `False` otherwise |

---

## 🏛️ Essentials

**What it does:**

- Checks gRPC channel connectivity state
- Returns True for READY or IDLE states
- Returns False if channel unavailable or in error state
- Does not attempt to connect (non-blocking check)

**Key behaviors:**

- Synchronous method (no await needed)
- Safe to call anytime (catches exceptions)
- Does not modify connection state
- Returns False on any exception

---

## ⚡ Under the Hood

```
MT5Sugar.is_connected()
    ↓ accesses
MT5Service.get_account()
    ↓ checks channel state
grpc.Channel.get_state(try_to_connect=False)
    ↓ returns
ChannelConnectivity enum (READY/IDLE/...)
```

**Call chain:**

1. Sugar accesses underlying MT5Account from service
2. Checks if account has channel attribute
3. Calls channel.get_state() with try_to_connect=False
4. Compares state against READY or IDLE
5. Returns True if connected, False otherwise
6. Catches all exceptions and returns False

**Related files:**
- Sugar: `src/pymt5/mt5_sugar.py:291`

---

## When to Use

**Use `is_connected()` when:**

- Checking connection before operations
- Implementing connection health monitoring
- Validating state before critical operations
- Building connection retry logic

**Don't use when:**

- You want to ping server (use `ping()`)
- Need to test actual server responsiveness
- Want to establish connection (use quick_connect())

---

## 🔗 Examples

### Example 1: Basic Connection Check

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

# Create MT5Sugar instance
account = MT5Account.create(
    user=591129415,
    password="your_password",
    grpc_server="mt5.mrpc.pro:443"
)
service = MT5Service(account)
sugar = MT5Sugar(service)

# Check connection (no await needed - synchronous)
if sugar.is_connected():
    print("Connected to MT5 server")
else:
    print("Not connected")

# Output:
# Connected to MT5 server
```

### Example 2: Conditional Operations

```python
async def safe_get_balance():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    # Connect first
    await sugar.quick_connect("FxPro-MT5 Demo")

    # Check before operation
    if sugar.is_connected():
        balance = await sugar.get_balance()
        print(f"Balance: ${balance}")
    else:
        print("Cannot get balance - not connected")
```

### Example 3: Connection Monitoring Loop

```python
import asyncio

async def monitor_connection():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Monitor connection every 10 seconds
    while True:
        if sugar.is_connected():
            print("Connection OK")
        else:
            print("Connection lost - reconnecting...")
            await sugar.quick_connect("FxPro-MT5 Demo")

        await asyncio.sleep(10)
```

---

## Common Pitfalls

**Pitfall 1: Confusing with ping**
```python
# is_connected() only checks channel state, not server health
if sugar.is_connected():
    # Channel is open, but server might not respond
    pass
```

**Solution:** Use ping() for actual server health check
```python
# Check channel state
channel_ok = sugar.is_connected()

# Check server responsiveness
server_ok = await sugar.ping()

if channel_ok and server_ok:
    print("Fully connected and responsive")
```

**Pitfall 2: Using await (it's synchronous)**
```python
# ERROR: is_connected() is NOT async
connected = await sugar.is_connected()  # SyntaxError
```

**Solution:** Call without await
```python
# Correct: synchronous call
connected = sugar.is_connected()
```

**Pitfall 3: Assuming False means permanent failure**
```python
if not sugar.is_connected():
    print("Connection permanently lost")
    # Not necessarily true - might just be initializing
```

**Solution:** Combine with retry logic
```python
if not sugar.is_connected():
    print("Not connected - attempting to connect")
    await sugar.quick_connect("FxPro-MT5 Demo")
```

---

## Pro Tips

**Tip 1: Quick pre-flight check**
```python
# Check before critical operations
if not sugar.is_connected():
    await sugar.quick_connect("FxPro-MT5 Demo")

# Proceed with operations
balance = await sugar.get_balance()
```

**Tip 2: Use in assertion for debugging**
```python
# Ensure connection in tests
assert sugar.is_connected(), "Must be connected before test"

# Run test operations
await sugar.buy_market(volume=0.01)
```

**Tip 3: Log connection state changes**
```python
previous_state = sugar.is_connected()

while True:
    current_state = sugar.is_connected()

    if current_state != previous_state:
        if current_state:
            print("Connection restored")
        else:
            print("Connection lost")

        previous_state = current_state

    await asyncio.sleep(5)
```

---

## 📚 See Also

- [ping](ping.md) - Test server responsiveness
- [quick_connect](quick_connect.md) - Connect to MT5 cluster
