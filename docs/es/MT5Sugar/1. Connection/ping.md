# Ping MT5 Server (`ping`)

> **Sugar method:** Tests server responsiveness with lightweight request.

**API Information:**

* **Method:** `sugar.ping(timeout: float = 5.0)`
* **Returns:** `True` if server responds, `False` otherwise
* **Layer:** HIGH (MT5Sugar)

---

## Method Signature

```python
async def ping(self, timeout: float = 5.0) -> bool
```

---

## 🔽 Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `timeout` | `float` | No | `5.0` | Timeout in seconds for ping attempt |

---

## Return Value

| Type | Description |
|------|-------------|
| `bool` | `True` if server responds within timeout, `False` otherwise |

---

## 🏛️ Essentials

**What it does:**

- Sends lightweight request to MT5 server
- Waits for response within timeout period
- Tests actual server health (not just channel state)
- Returns False on timeout or any error

**Key behaviors:**

- Uses get_symbols_total() as ping request
- Default 5 second timeout
- Catches TimeoutError and all exceptions
- Does not modify any state

---

## ⚡ Under the Hood

```
MT5Sugar.ping()
    ↓ wraps with asyncio.timeout
MT5Service.get_symbols_total(selected_only=True)
    ↓ calls
MT5Account.symbols_total()
    ↓ gRPC protobuf
MarketInfoService.SymbolsTotal()
    ↓ MT5 Terminal
```

**Call chain:**

1. Sugar wraps request with asyncio.timeout context
2. Calls Service.get_symbols_total() with selected_only=True
3. Service forwards to Account.symbols_total()
4. Account sends gRPC request to terminal
5. If response within timeout, returns True
6. If timeout or exception, returns False

**Related files:**

- Sugar: `src/pymt5/mt5_sugar.py:318`
- Service: `src/pymt5/mt5_service.py:377`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:687`

---

## When to Use

**Use `ping()` when:**

- Testing actual server responsiveness
- Validating connection after timeout
- Health checks in monitoring systems
- Before critical operations

**Don't use when:**

- Only need channel state (use `is_connected()`)
- Performing actual operations (no need to ping first)
- High-frequency checks (too much overhead)

---

## 🔗 Examples

### Example 1: Basic Server Ping

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def test_connection():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Ping server
    responsive = await sugar.ping()

    if responsive:
        print("Server is responsive")
    else:
        print("Server not responding")

# Output:
# Server is responsive
```

### Example 2: Ping with Custom Timeout

```python
async def quick_ping():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Quick ping with 2 second timeout
    responsive = await sugar.ping(timeout=2.0)

    if responsive:
        print("Server responded within 2 seconds")
    else:
        print("Server slow or unresponsive")
```

### Example 3: Connection Health Monitor

```python
import asyncio

async def health_monitor():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    consecutive_failures = 0
    max_failures = 3

    while True:
        # Check both channel and server
        channel_ok = sugar.is_connected()
        server_ok = await sugar.ping(timeout=3.0)

        if channel_ok and server_ok:
            print("Health: OK")
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            print(f"Health: FAIL ({consecutive_failures}/{max_failures})")

            if consecutive_failures >= max_failures:
                print("Reconnecting...")
                await sugar.quick_connect("FxPro-MT5 Demo")
                consecutive_failures = 0

        await asyncio.sleep(30)
```

---

## Common Pitfalls

**Pitfall 1: Using for every operation**
```python
# BAD: Pinging before every operation
for _ in range(100):
    if await sugar.ping():
        await sugar.get_balance()
    # Too much overhead!
```

**Solution:** Ping periodically, not before each operation
```python
# Ping once at start
if not await sugar.ping():
    await sugar.quick_connect("FxPro-MT5 Demo")

# Then perform operations without pinging
for _ in range(100):
    balance = await sugar.get_balance()
```

**Pitfall 2: Too short timeout**
```python
# ERROR: 0.1 second timeout too short
responsive = await sugar.ping(timeout=0.1)
# May fail even with good connection
```

**Solution:** Use reasonable timeout (2-5 seconds)
```python
# Give enough time for network round-trip
responsive = await sugar.ping(timeout=3.0)
```

**Pitfall 3: Not handling False result**
```python
# No action when ping fails
if not await sugar.ping():
    pass  # What now?
```

**Solution:** Implement recovery logic
```python
if not await sugar.ping():
    print("Ping failed - attempting reconnect")
    try:
        await sugar.quick_connect("FxPro-MT5 Demo")
    except Exception as e:
        print(f"Reconnect failed: {e}")
```

---

## Pro Tips

**Tip 1: Combine with is_connected for full check**

```python
# Complete connection check
async def is_fully_connected(sugar):
    channel_ok = sugar.is_connected()  # Fast channel check
    server_ok = await sugar.ping()     # Actual server test

    return channel_ok and server_ok

# Use before critical operations
if await is_fully_connected(sugar):
    await sugar.buy_market(volume=1.0)
```

**Tip 2: Use progressive timeouts**
```python
# Try quick ping first, then longer
async def smart_ping(sugar):
    # Quick attempt (1 second)
    if await sugar.ping(timeout=1.0):
        return True

    # Slower attempt (5 seconds)
    if await sugar.ping(timeout=5.0):
        return True

    return False
```

**Tip 3: Log ping latency**
```python
import time

async def ping_with_latency(sugar):
    start = time.time()
    responsive = await sugar.ping()
    latency = (time.time() - start) * 1000  # ms

    if responsive:
        print(f"Ping: {latency:.1f}ms")
    else:
        print("Ping: timeout")

    return responsive
```

---

## 📚 See Also

- [is_connected](is_connected.md) - Check channel state
- [quick_connect](quick_connect.md) - Connect to MT5 cluster
