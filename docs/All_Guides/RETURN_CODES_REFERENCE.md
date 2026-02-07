# MT5 Return Codes (RetCodes) Reference - Python

## 🛡️ What is RetCode?

**RetCode** (Return Code) is a status code that MT5 terminal returns after executing a trading operation. The code indicates success or the reason for failure.

RetCodes **appear only in trading methods** because only trading operations go through the broker and can be rejected for various reasons (insufficient margin, invalid price, market closed, etc.).

### Quick Example: Proper RetCode Handling

```python
from helpers.errors import TRADE_RETCODE_DONE, get_retcode_message

# Place order
result = await service.place_order(request)

# ✅ ALWAYS check returned_code explicitly
if result.returned_code == TRADE_RETCODE_DONE:
    print(f"✓ Trade successful! Order #{result.order}")
else:
    print(f"✗ Trade failed: {get_retcode_message(result.returned_code)}")
    # Example: "Insufficient funds" (10019) or "Market closed" (10018)
```

**Key point:** No exception = API worked, but **check RetCode** to know if **trade succeeded**.

---

## RetCode Source

RetCodes are **standard MQL5 codes** defined in official MetaQuotes documentation:

**MQL5 Documentation**: [Trade Result Codes (ENUM_TRADE_RETCODE)](https://www.mql5.com/en/docs/constants/errorswarnings/enum_trade_return_codes)

These codes are:

- **Unified across all languages** (C#, Python, Java, Node.js, Go, PHP)
- **Unified with MT5 terminal** - returned directly from the trading server
- **Defined in protobuf** - returned as `uint32` field `returned_code` in trading result structures
- **Available as Python constants** - defined in `package/helpers/errors.py`

---

## 📥 Where is RetCode Used in the API?

RetCode is returned in **all trading operations** that modify positions or orders:

### 1. OrderSend (Opening Orders)

```python
from helpers.errors import (
    ApiError,
    TRADE_RETCODE_DONE,
    get_retcode_message,
    is_retcode_success
)

# Using Sugar API
try:
    ticket = await sugar.buy_market("EURUSD", 0.01)
    print(f"[OK] Order opened: #{ticket}")
except ApiError as e:
    # Check if it's a trade error with RetCode
    retcode = e.mql_error_trade_int_code()
    print(f"RetCode: {retcode}")
    print(f"Description: {e.mql_error_trade_description()}")

# Using Service API (mid-level)
result = await service.place_order(request)
if result.returned_code == TRADE_RETCODE_DONE:
    print(f"[OK] Order opened! Ticket: {result.order}")
else:
    print(f"[X] Order failed: {get_retcode_message(result.returned_code)}")
```

### 2. OrderModify (Modifying SL/TP)

```python
from helpers.errors import TRADE_RETCODE_DONE, is_retcode_success, get_retcode_message

# Using Sugar API
try:
    await sugar.modify_position_sltp(ticket, sl=1.0850, tp=1.0950)
    print("[OK] SL/TP modified successfully")
except ApiError as e:
    print(f"[X] Modification failed: {e.mql_error_trade_description()}")

# Using Service API
result = await service.modify_order(request)
if is_retcode_success(result.returned_code):
    print("[OK] SL/TP modified successfully")
else:
    print(f"[X] Modification failed: {get_retcode_message(result.returned_code)}")
```

### 3. PositionClose (Closing Positions)

```python
from helpers.errors import ApiError, TRADE_RETCODE_DONE, TRADE_RETCODE_POSITION_CLOSED

# Using Sugar API
try:
    await sugar.close_position(ticket)
    print("[OK] Position closed")
except ApiError as e:
    if e.mql_error_trade_int_code() == TRADE_RETCODE_POSITION_CLOSED:
        print("[WARN] Position already closed")
    else:
        print(f"[X] Close failed: {e}")

# Using Service API
result = await service.close_order(request)
if result.returned_code == TRADE_RETCODE_DONE:
    print("[OK] Position closed")
```

---

## 👁️ Why RetCode Only in Trading Methods?

**Informational methods** (getting prices, symbols, balance) **DO NOT return RetCode** because:

- They don't go through the broker
- They cannot be "rejected" - either data exists or there's a gRPC error
- They work with local terminal data

**Trading methods** return RetCode because:

- Request is sent to broker via trading server
- Broker validates: margin, symbol rules, trading hours, limits
- Broker can reject request for dozens of reasons
- Each reason has its own unique code

---

## Complete RetCode List

### Success Codes

| Code | Python Constant | Description | When Returned |
|------|-----------------|-------------|---------------|
| **10009** | `TRADE_RETCODE_DONE` | **Request completed successfully** | Market order opened/closed |
| **10010** | `TRADE_RETCODE_DONE_PARTIAL` | **Partial execution** | Only part of volume executed |
| **10008** | `TRADE_RETCODE_PLACED` | **Pending order placed** | Limit/Stop order placed |

### Requote Codes (Retry Recommended)

| Code | Python Constant | Description | Action |
|------|-----------------|-------------|--------|
| **10004** | `TRADE_RETCODE_REQUOTE` | **Requote** | Price changed, retry request |
| **10020** | `TRADE_RETCODE_PRICE_CHANGED` | **Price changed** | Similar to requote, retry |

**Helper function:**
```python
from helpers.errors import is_retcode_requote

if is_retcode_requote(retcode):
    # Retry with updated price
    pass
```

### ⚠️ Request Validation Errors

| Code | Python Constant | Description | Common Cause |
|------|-----------------|-------------|--------------|
| **10013** | `TRADE_RETCODE_INVALID_REQUEST` | **Invalid request** | Incorrect parameters |
| **10014** | `TRADE_RETCODE_INVALID_VOLUME` | **Invalid volume** | Volume < MinVolume or > MaxVolume |
| **10015** | `TRADE_RETCODE_INVALID_PRICE` | **Invalid price** | Price doesn't match symbol rules |
| **10016** | `TRADE_RETCODE_INVALID_STOPS` | **Invalid stops** | SL/TP too close to price (check StopLevel) |
| **10022** | `TRADE_RETCODE_INVALID_EXPIRATION` | **Invalid expiration** | Expiration time incorrect |
| **10030** | `TRADE_RETCODE_INVALID_FILL` | **Invalid order filling type** | Fill type not allowed |
| **10035** | `TRADE_RETCODE_INVALID_ORDER` | **Invalid order type** | Order type prohibited for symbol |
| **10038** | `TRADE_RETCODE_INVALID_CLOSE_VOLUME` | **Invalid close volume** | Close volume exceeds position volume |

### 🚫 Trading Restrictions

| Code | Python Constant | Description | Reason |
|------|-----------------|-------------|--------|
| **10017** | `TRADE_RETCODE_TRADE_DISABLED` | **Trading disabled** | Trading disabled for symbol |
| **10018** | `TRADE_RETCODE_MARKET_CLOSED` | **Market closed** | Outside trading hours |
| **10026** | `TRADE_RETCODE_SERVER_DISABLES_AT` | **Autotrading disabled by server** | Server disabled auto-trading |
| **10027** | `TRADE_RETCODE_CLIENT_DISABLES_AT` | **Autotrading disabled by client** | Terminal disabled auto-trading |
| **10032** | `TRADE_RETCODE_ONLY_REAL` | **Only real accounts** | Action unavailable on demo |
| **10042** | `TRADE_RETCODE_LONG_ONLY` | **Only long positions allowed** | Short positions prohibited |
| **10043** | `TRADE_RETCODE_SHORT_ONLY` | **Only short positions allowed** | Long positions prohibited |
| **10044** | `TRADE_RETCODE_CLOSE_ONLY` | **Only position closing allowed** | Opening new positions prohibited |
| **10045** | `TRADE_RETCODE_FIFO_CLOSE` | **Position close only by FIFO rule** | FIFO rule enforced |
| **10046** | `TRADE_RETCODE_HEDGE_PROHIBITED` | **Opposite positions prohibited** | Hedging disabled |

### 💰 Resource Limits

| Code | Python Constant | Description | Solution |
|------|-----------------|-------------|----------|
| **10019** | `TRADE_RETCODE_NO_MONEY` | **Insufficient funds** | Check free margin |
| **10033** | `TRADE_RETCODE_LIMIT_ORDERS` | **Pending orders limit** | Close some pending orders |
| **10034** | `TRADE_RETCODE_LIMIT_VOLUME` | **Volume limit** | Reduce position volume |
| **10040** | `TRADE_RETCODE_LIMIT_POSITIONS` | **Positions limit** | Close some positions |

### 🔄 Technical Issues (Retryable)

| Code | Python Constant | Description | Retryable |
|------|-----------------|-------------|-----------|
| **10011** | `TRADE_RETCODE_ERROR` | **Processing error** | No |
| **10012** | `TRADE_RETCODE_TIMEOUT` | **Request timeout** | Yes |
| **10021** | `TRADE_RETCODE_NO_QUOTES` | **No quotes** | Yes |
| **10024** | `TRADE_RETCODE_TOO_MANY_REQUESTS` | **Rate limiting** | Yes (with delay) |
| **10028** | `TRADE_RETCODE_LOCKED` | **Request locked for processing** | Yes |
| **10029** | `TRADE_RETCODE_FROZEN` | **Order or position frozen** | Yes |
| **10031** | `TRADE_RETCODE_NO_CONNECTION` | **No connection** | Yes |

**Helper function:**
```python
from helpers.errors import is_retcode_retryable
import asyncio

if is_retcode_retryable(retcode):
    # Safe to retry with exponential backoff
    await asyncio.sleep(2)
    # Retry operation...
```

### State Management

| Code | Python Constant | Description | Meaning |
|------|-----------------|-------------|---------|
| **10023** | `TRADE_RETCODE_ORDER_CHANGED` | **Order state changed** | Order already modified/closed |
| **10025** | `TRADE_RETCODE_NO_CHANGES` | **No changes** | New parameters = current parameters |
| **10036** | `TRADE_RETCODE_POSITION_CLOSED` | **Position closed** | Position doesn't exist |
| **10039** | `TRADE_RETCODE_CLOSE_ORDER_EXIST` | **Close order exists** | Cannot close more than position volume |

### ❌ Rejection Codes

| Code | Python Constant | Description | Reason |
|------|-----------------|-------------|--------|
| **10006** | `TRADE_RETCODE_REJECT` | **Request rejected** | Broker rejected |
| **10007** | `TRADE_RETCODE_CANCEL` | **Request canceled** | Canceled by trader |
| **10041** | `TRADE_RETCODE_REJECT_CANCEL` | **Pending order activation rejected** | Activation rejected and canceled |

---

## Centralized Error Handler (`package/helpers/errors.py`)

**PyMT5 provides a centralized error handling module** that simplifies working with RetCodes.

Instead of manually checking return codes and writing your own error messages, you can use the built-in helper functions from `package/helpers/errors.py`:

### What's Inside

The module contains:

- **All RetCode constants** (e.g., `TRADE_RETCODE_DONE`, `TRADE_RETCODE_NO_MONEY`)

- **Helper functions** to check return codes (`is_retcode_success`, `is_retcode_requote`, etc.)

- **Human-readable error messages** for all RetCodes

- **Pre-built error handling logic** for common scenarios

### Why Use It?

✅ **No magic numbers** - Use named constants instead of `10009`, `10019`

✅ **Automatic error descriptions** - Get human-readable messages for any RetCode

✅ **Smart categorization** - Easily identify requotes, retryable errors, etc.

✅ **Consistent error handling** - Use the same logic across your entire project

### When to Explicitly Check RetCode

**CRITICAL:** You **MUST explicitly check** `returned_code` after every trading operation:

```python
# ❌ WRONG - Only catching exceptions is NOT enough!
try:
    result = await service.place_order(request)
    print(f"Order placed: {result.order}")  # ← This doesn't mean success!
except ApiError as e:
    print(f"Error: {e}")

# ✅ CORRECT - Always check returned_code
try:
    result = await service.place_order(request)

    # MUST check RetCode explicitly
    if result.returned_code == TRADE_RETCODE_DONE:
        print(f"✓ Order placed: {result.order}")
    else:
        print(f"✗ Order failed: {get_retcode_message(result.returned_code)}")

except ApiError as e:
    print(f"API Error: {e}")
```

**Why?** Because:

- No exception means the **API call succeeded** (connection OK, terminal responded)

- But it does **NOT** mean the **trade succeeded** (broker may have rejected it)

- You need to check `returned_code` to know the **actual trade result**

---

## Python Helper Functions

The `package/helpers/errors.py` module provides helper functions for working with RetCodes:

### is_retcode_success()

Checks if the RetCode indicates successful trade execution.

```python
from helpers.errors import is_retcode_success, TRADE_RETCODE_DONE

# Usage
if is_retcode_success(result.returned_code):
    print("Trade successful!")

# Returns True only for retcode == 10009 (TRADE_RETCODE_DONE)
```

### is_retcode_requote()

Checks if the RetCode indicates a price change (requote) - safe to retry immediately.

```python
from helpers.errors import is_retcode_requote, TRADE_RETCODE_REQUOTE, TRADE_RETCODE_PRICE_CHANGED

# Usage
if is_retcode_requote(result.returned_code):
    print("Price changed, retrying...")
    # Retry with updated price

# Returns True for 10004 or 10020
```

### is_retcode_retryable()

Checks if the RetCode indicates a temporary error - safe to retry with delay.

```python
from helpers.errors import (
    is_retcode_retryable,
    TRADE_RETCODE_TIMEOUT,
    TRADE_RETCODE_NO_CONNECTION,
    TRADE_RETCODE_FROZEN
)
import asyncio

# Usage
if is_retcode_retryable(result.returned_code):
    # These errors are temporary, retry with delay
    await asyncio.sleep(2)
    # Retry operation

# Returns True for: Timeout, NoConnection, Frozen, Locked, TooManyRequests, NoQuotes
```

### get_retcode_message()

Returns a human-readable description for any RetCode.

```python
from helpers.errors import get_retcode_message, TRADE_RETCODE_DONE

# Usage
if result.returned_code != TRADE_RETCODE_DONE:
    print(f"Error: {get_retcode_message(result.returned_code)}")

# Returns human-readable description for any RetCode
```

### check_retcode()

Prints formatted message with hints and returns `True` if successful.

```python
from helpers.errors import check_retcode, TRADE_RETCODE_DONE

# Usage
result = await service.place_order(request)
if check_retcode(result.returned_code, "Order placement"):
    print(f"Order ticket: {result.order}")

# Prints formatted message and helpful hints for common errors
```

---

## Usage Examples

### Example 1: Basic Order Placement with RetCode Check

```python
import asyncio
from uuid import uuid4
from MetaRpcMT5 import MT5Account
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from helpers.errors import TRADE_RETCODE_DONE, get_retcode_message
from MetaRpcMT5.mt5_term_api_trading_helper_pb2 import OrderSendRequest
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as pb_trading

async def main():
    # Create MT5Account instance
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="127.0.0.1:9999",
        id_=uuid4()
    )

    # Connect to MT5 server
    await account.connect_by_server_name(
        server_name="MetaQuotes-Demo",
        base_chart_symbol="EURUSD",
        timeout_seconds=120
    )

    try:
        # Create service and sugar
        service = MT5Service(account)
        sugar = MT5Sugar(service, default_symbol="EURUSD")

        # Place buy market order
        request = OrderSendRequest(
            symbol="EURUSD",
            volume=0.01,
            operation=pb_trading.TMT5_ORDER_TYPE_BUY,
            price=0.0  # Market order
        )

        result = await service.place_order(request)

        # Check RetCode
        if result.returned_code == TRADE_RETCODE_DONE:
            print(f"[OK] Order opened successfully!")
            print(f"   Ticket: #{result.order}")
            print(f"   Volume: {result.volume:.2f} lots")
            print(f"   Price: {result.price:.5f}")
        else:
            print(f"[X] Order failed!")
            print(f"   RetCode: {result.returned_code}")
            print(f"   Description: {get_retcode_message(result.returned_code)}")

    finally:
        await account.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Handling Common Errors (if/elif Statement)

```python
from helpers.errors import (
    ApiError,
    TRADE_RETCODE_NO_MONEY,
    TRADE_RETCODE_MARKET_CLOSED,
    TRADE_RETCODE_INVALID_STOPS,
    TRADE_RETCODE_INVALID_VOLUME,
    TRADE_RETCODE_REQUOTE,
    TRADE_RETCODE_PRICE_CHANGED
)
import asyncio

try:
    ticket = await sugar.buy_market("GBPUSD", 0.5)
    print(f"[OK] Order #{ticket} opened")

except ApiError as e:
    retcode = e.mql_error_trade_int_code()

    if retcode == TRADE_RETCODE_NO_MONEY:
        print("[WARN] Insufficient funds!")
        print("   Solution: Reduce volume or add margin")

    elif retcode == TRADE_RETCODE_MARKET_CLOSED:
        print("[WARN] Market closed")
        print("   Solution: Try during trading hours")

    elif retcode == TRADE_RETCODE_INVALID_STOPS:
        print("[WARN] SL/TP too close to market price")
        print("   Solution: Increase distance (check StopLevel)")

    elif retcode == TRADE_RETCODE_INVALID_VOLUME:
        print("[WARN] Invalid volume")
        # Get symbol limits
        symbol_info = await sugar.get_symbol_info("GBPUSD")
        print(f"   Min: {symbol_info.volume_min:.2f}, "
              f"Max: {symbol_info.volume_max:.2f}, "
              f"Step: {symbol_info.volume_step:.2f}")

    elif retcode in (TRADE_RETCODE_REQUOTE, TRADE_RETCODE_PRICE_CHANGED):
        print("[WARN] Price changed, retrying...")
        await asyncio.sleep(0.1)
        # Retry order

    else:
        print(f"[X] Error: {e.mql_error_trade_description()}")
```

### Example 3: Retry Logic for Temporary Errors

```python
import asyncio
from helpers.errors import (
    ApiError,
    is_retcode_requote,
    is_retcode_retryable
)

async def place_order_with_retry(
    sugar,
    symbol: str,
    volume: float,
    max_retries: int = 3
):
    """Place order with automatic retry logic."""

    for attempt in range(1, max_retries + 1):
        try:
            ticket = await sugar.buy_market(symbol, volume)
            # Success
            return ticket

        except ApiError as e:
            retcode = e.mql_error_trade_int_code()

            # Requote - retry immediately
            if is_retcode_requote(retcode):
                print(f"Requote on attempt {attempt}, retrying...")
                await asyncio.sleep(0.1)
                continue

            # Retryable error - exponential backoff
            if is_retcode_retryable(retcode):
                wait_time = attempt  # 1s, 2s, 3s
                print(f"Temporary error on attempt {attempt}, "
                      f"waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue

            # Permanent error - stop retrying
            raise RuntimeError(
                f"Permanent error: {e.mql_error_trade_description()}"
            )

        except Exception as e:
            # Other error (network, etc.)
            raise

    raise RuntimeError(f"Failed after {max_retries} attempts")

# Usage
try:
    ticket = await place_order_with_retry(sugar, "EURUSD", 0.01, max_retries=3)
    print(f"Order placed: #{ticket}")
except Exception as e:
    print(f"Failed to place order: {e}")
```

### Example 4: Using check_retcode()

```python
from helpers.errors import check_retcode

result = await service.place_order(request)

# check_retcode prints formatted message and returns True on success
if check_retcode(result.returned_code, "Order placement"):
    print(f"Order ticket: {result.order}")

# Output on success:
#   [OK] Order placement successful (RetCode: 10009)

# Output on failure (e.g., market closed):
#   [FAIL] Order placement failed (RetCode: 10018)
#      Market is closed
#      Hint: Market is closed - check trading hours
```

### Example 5: Modifying SL/TP with Validation

```python
from helpers.errors import (
    TRADE_RETCODE_DONE,
    TRADE_RETCODE_NO_CHANGES,
    TRADE_RETCODE_POSITION_CLOSED,
    TRADE_RETCODE_INVALID_STOPS,
    get_retcode_message
)

try:
    await sugar.modify_position_sltp(123456, sl=1.0850, tp=1.0950)
    print("[OK] SL/TP updated successfully")

except ApiError as e:
    retcode = e.mql_error_trade_int_code()

    if retcode == TRADE_RETCODE_NO_CHANGES:
        print("[WARN] New SL/TP same as current - no action taken")

    elif retcode == TRADE_RETCODE_POSITION_CLOSED:
        print("[WARN] Position already closed by SL/TP or manually")

    elif retcode == TRADE_RETCODE_INVALID_STOPS:
        print("[X] Invalid SL/TP distance")
        # Get symbol stop level
        symbol_info = await sugar.get_symbol_info("EURUSD")
        print(f"   Minimum distance: {symbol_info.spread} points")

    else:
        print(f"[X] Modification failed: {get_retcode_message(retcode)}")
```

---

## Best Practices

### DO:

1. **Always check returned_code** after trading operations
   ```python
   if result.returned_code == TRADE_RETCODE_DONE:
       # Success
       pass
   ```

2. **Use helper functions** for cleaner code
   ```python
   if is_retcode_success(retcode): ...
   if is_retcode_requote(retcode): ...
   ```

3. **Retry requotes** (10004, 10020)
   ```python
   if is_retcode_requote(retcode):
       # Retry with updated price
       pass
   ```

4. **Check margin before trading** to avoid 10019
   ```python
   free_margin = await sugar.get_free_margin()
   required_margin = await sugar.calculate_required_margin("EURUSD", 0.01)
   if free_margin < required_margin:
       print("Insufficient margin!")
   ```

### ❌ DON'T:

1. **Don't ignore returned_code** - catching only exceptions is NOT enough!
   ```python
   # ❌ WRONG - Dangerous! This looks like success but trade might have failed!
   try:
       result = await service.place_order(request)
       print(f"Order: {result.order}")  # ← NO! This might be 0 if trade failed
       # Missing RetCode check = silent failures!
   except ApiError:
       pass

   # ✅ CORRECT - Always check returned_code
   try:
       result = await service.place_order(request)
       if result.returned_code == TRADE_RETCODE_DONE:
           # Now we KNOW trade succeeded
           print(f"Order: {result.order}")
       else:
           # Trade failed - handle the error
           print(f"Failed: {get_retcode_message(result.returned_code)}")
   except ApiError as e:
       # Handle API/connection error
       print(f"API Error: {e}")
   ```

2. **Don't use magic numbers** - use constants
   ```python
   # WRONG:
   if retcode == 10009: ...

   # CORRECT:
   if retcode == TRADE_RETCODE_DONE: ...
   ```

3. **Don't retry permanent errors** (insufficient margin, market closed)
   ```python
   # Use is_retcode_retryable() to check
   if is_retcode_retryable(retcode):
       # Safe to retry
       pass
   ```

4. **Don't assume no exception = success**
   ```python
   # Need to check both exception AND RetCode
   try:
       result = await service.place_order(request)
       if result.returned_code != TRADE_RETCODE_DONE:
           raise RuntimeError(f"Trade failed: {get_retcode_message(result.returned_code)}")
   except Exception as e:
       # Handle error
       pass
   ```

---

## ℹ️ Quick Reference Table

| Category | RetCodes | Action |
|----------|----------|--------|
| **Success** | 10008, 10009, 10010 | Continue normally |
| **Requote** | 10004, 10020 | Retry immediately |
| **Temporary** | 10012, 10021, 10024, 10028, 10029, 10031 | Retry with delay |
| **Validation** | 10013-10016, 10022, 10030, 10035, 10038 | Fix parameters |
| **Restrictions** | 10017, 10018, 10026, 10027, 10032, 10042-10046 | Check trading conditions |
| **Limits** | 10019, 10033, 10034, 10040 | Reduce volume/positions |
| **State** | 10023, 10025, 10036, 10039 | Check current state |
| **Rejection** | 10006, 10007, 10041 | Check request |
| **Technical** | 10011 | Contact support |

---

## Constants Reference

All RetCode constants are defined in `package/helpers/errors.py`:

```python
# Success codes
TRADE_RETCODE_SUCCESS = 0           # Success (generic, rarely used - prefer DONE)
TRADE_RETCODE_DONE = 10009          # Request completed successfully
TRADE_RETCODE_DONE_PARTIAL = 10010  # Only part of the request was completed
TRADE_RETCODE_PLACED = 10008        # Order placed (pending order activated)

# Requote codes
TRADE_RETCODE_REQUOTE = 10004       # Requote (price changed, need to retry)
TRADE_RETCODE_PRICE_CHANGED = 10020 # Prices changed (same as requote)

# Request rejection codes
TRADE_RETCODE_REJECT = 10006        # Request rejected by server
TRADE_RETCODE_CANCEL = 10007        # Request canceled by trader
TRADE_RETCODE_INVALID_REQUEST = 10013       # Invalid request
TRADE_RETCODE_INVALID_VOLUME = 10014        # Invalid volume in the request
TRADE_RETCODE_INVALID_PRICE = 10015         # Invalid price in the request
TRADE_RETCODE_INVALID_STOPS = 10016         # Invalid stops (SL/TP too close to price)
TRADE_RETCODE_INVALID_EXPIRATION = 10022    # Invalid order expiration date
TRADE_RETCODE_INVALID_FILL = 10030          # Invalid order filling type
TRADE_RETCODE_INVALID_ORDER = 10035         # Incorrect or prohibited order type
TRADE_RETCODE_INVALID_CLOSE_VOLUME = 10038  # Invalid close volume

# Backward compatibility alias
TRADE_RETCODE_INVALID = TRADE_RETCODE_INVALID_REQUEST

# Trading restriction codes
TRADE_RETCODE_TRADE_DISABLED = 10017    # Trading is disabled
TRADE_RETCODE_MARKET_CLOSED = 10018     # Market is closed
TRADE_RETCODE_SERVER_DISABLES_AT = 10026 # Autotrading disabled by server
TRADE_RETCODE_CLIENT_DISABLES_AT = 10027 # Autotrading disabled by client terminal
TRADE_RETCODE_ONLY_REAL = 10032         # Operation is allowed only for live accounts
TRADE_RETCODE_LONG_ONLY = 10042         # Only long positions allowed
TRADE_RETCODE_SHORT_ONLY = 10043        # Only short positions allowed
TRADE_RETCODE_CLOSE_ONLY = 10044        # Only position close operations allowed
TRADE_RETCODE_FIFO_CLOSE = 10045        # Position close only by FIFO rule
TRADE_RETCODE_HEDGE_PROHIBITED = 10046  # Opposite positions prohibited (hedging disabled)

# Resource limit codes
TRADE_RETCODE_NO_MONEY = 10019          # Not enough money (insufficient margin)
TRADE_RETCODE_LIMIT_ORDERS = 10033      # Number of pending orders reached the limit
TRADE_RETCODE_LIMIT_VOLUME = 10034      # Volume of orders and positions reached the limit
TRADE_RETCODE_LIMIT_POSITIONS = 10040   # Number of open positions reached the limit

# Technical issue codes
TRADE_RETCODE_ERROR = 10011             # Request processing error
TRADE_RETCODE_TIMEOUT = 10012           # Request canceled by timeout
TRADE_RETCODE_NO_QUOTES = 10021         # No quotes to process the request
TRADE_RETCODE_TOO_MANY_REQUESTS = 10024 # Too frequent requests
TRADE_RETCODE_LOCKED = 10028            # Request locked for processing
TRADE_RETCODE_FROZEN = 10029            # Order or position frozen
TRADE_RETCODE_NO_CONNECTION = 10031     # No connection with the trade server

# Backward compatibility aliases
TRADE_RETCODE_PRICE_OFF = TRADE_RETCODE_NO_QUOTES
TRADE_RETCODE_CONNECTION = TRADE_RETCODE_NO_CONNECTION

# State management codes
TRADE_RETCODE_ORDER_CHANGED = 10023     # Order state changed during request
TRADE_RETCODE_NO_CHANGES = 10025        # No changes in request
TRADE_RETCODE_POSITION_CLOSED = 10036   # Position with specified ID already closed
TRADE_RETCODE_CLOSE_ORDER_EXIST = 10039 # A close order already exists for position
TRADE_RETCODE_REJECT_CANCEL = 10041     # Pending order activation rejected and canceled
```
