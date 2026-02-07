# User Code Sandbox Guide

## What is this?

This is **your sandbox** for writing custom MT5 trading code in Python. Connection setup is already done - you only need to add your trading logic!

## 🏁 Quick Start

1. **Case already active in main.py**
   - Open `examples/main.py`
   - Case "18" for user code sandbox is ready to use

2. **Open `examples/6_usercode/18_usercode.py`**
   - Write your code or uncomment examples

3. **Run:**
   ```bash
   cd examples
   python main.py usercode
   ```

That's it! Your code will execute with full MT5 connection.

## How to use

### Option 1: Uncomment examples

The file contains 5 ready-to-use examples:

```python
# Example 1: Get account balance (Sugar - easiest)
# balance = await sugar.get_balance()
# print(f"Balance: {balance:.2f}")
```

Just remove `#` to activate!

### Option 2: Write your own code

Add your logic between the markers:

```python
# =================================================================
# YOUR CODE HERE
# =================================================================

# Your trading strategy here...

# TODO: Write your trading logic here
```

## Available commands

Run your code with:

```bash
# From examples directory
python main.py usercode
python main.py 18
python main.py user
python main.py sandbox
```

## What's already configured

+ **Connection** - MT5 terminal connected via gRPC

+ **Configuration** - Loaded from `examples/0_common/settings.json`

+ **account** - Low-level gRPC client (MT5Account)

+ **service** - Mid-level wrapper (MT5Service)

+ **sugar** - High-level Sugar API (MT5Sugar)

+ **async/await** - All methods are asynchronous

## 🧩 Can I mix API levels?

**Yes!** You can use all three levels in the same file:

```python
# Low-level (direct gRPC protobuf)
summary = await account.account_summary()
balance_pb = summary.account_balance

# Mid-level (MT5Service)
account_info = await service.get_account_summary()
balance_svc = account_info.balance

# High-level (MT5Sugar)
balance_sugar = await sugar.get_balance()
```

All three variables are available simultaneously:

- `account` - for full control (gRPC protobuf)
- `service` - for convenient methods (Service layer)
- `sugar` - for simplest usage (Sugar API)

## Quick reference

### Get account information

```python
# Sugar API (easiest)
balance = await sugar.get_balance()
print(f"Balance: {balance:.2f}")

# Service API (more details)
account_info = await service.get_account_summary()
print(f"Balance: {account_info.balance:.2f} {account_info.currency}")
print(f"Equity:  {account_info.equity:.2f}")

# Account API (full control)
summary = await account.account_summary()
print(f"Balance: {summary.account_balance:.2f}")
```

### Get current price

```python
# Sugar API
bid = await sugar.get_bid("EURUSD")
ask = await sugar.get_ask("EURUSD")
print(f"EURUSD: Bid={bid:.5f}, Ask={ask:.5f}")

# Service API
tick = await service.get_symbol_tick("EURUSD")
print(f"EURUSD Bid: {tick.bid:.5f}, Ask: {tick.ask:.5f}")
```

### Open market order

```python
# Sugar API (easiest)
try:
    ticket = await sugar.buy_market("EURUSD", 0.01)
    print(f"Order opened: #{ticket}")
except Exception as e:
    print(f"Order failed: {e}")

# With SL/TP in pips
ticket = await sugar.buy_market_with_pips("EURUSD", 0.01, sl_pips=20, tp_pips=30)

# Calculate position size based on risk (2% with 50 pip SL)
lot_size = await sugar.calculate_position_size("EURUSD", risk_percent=2.0, sl_pips=50)
ticket = await sugar.buy_market_with_pips("EURUSD", lot_size, sl_pips=50, tp_pips=100)
```

### Place pending order

```python
# Buy Limit with absolute price and SL/TP in pips
ticket = await sugar.buy_limit_with_sltp("EURUSD", 0.01, price=1.0850,
                                          sl_pips=20, tp_pips=30)

# Buy Stop with absolute price
ticket = await sugar.buy_stop("EURUSD", 0.01, price=1.0950)

# Sell Limit with absolute price and SL/TP
ticket = await sugar.sell_limit_with_sltp("EURUSD", 0.01, price=1.1050,
                                           sl=1.1070, tp=1.1030)
```

### Get open positions

```python
# Sugar API
positions = await sugar.get_open_positions()
print(f"Open positions: {len(positions)}")
for pos in positions:
    print(f"  #{pos.ticket} {pos.symbol} {pos.volume:.2f} lot, "
          f"Profit: {pos.profit:.2f}")

# Service API with filters
opened_data = await service.get_opened_orders()
positions = opened_data.position_infos
```

### Close positions

```python
# Close specific position
await sugar.close_position(ticket)

# Close all positions for symbol
await sugar.close_all_positions("EURUSD")

# Close all positions (all symbols)
await sugar.close_all_positions()
```

### Modify position

```python
# Modify SL/TP
await sugar.modify_position_sltp(ticket, sl=1.0850, tp=1.0950)

# Modify only Stop Loss
await sugar.modify_position_sl(ticket, sl=1.0850)

# Modify only Take Profit
await sugar.modify_position_tp(ticket, tp=1.0950)
```

### Calculate position size

```python
# Calculate position size based on risk
volume = await sugar.calculate_position_size("EURUSD", risk_percent=2.0, sl_pips=20)
print(f"Volume for 2% risk with 20 pip SL: {volume:.2f} lot")

# Then use calculated volume
ticket = await sugar.buy_market("EURUSD", volume)
```

## Return Codes (RetCodes)

**Always check returned_code after trading operations!**

```python
from MetaRpcMT5.mt5_term_api_trading_helper_pb2 import OrderSendRequest
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as pb_trading

# Build request
request = OrderSendRequest(
    symbol="EURUSD",
    volume=0.01,
    operation=pb_trading.TMT5_ORDER_TYPE_BUY,
    price=0.0,  # Market order (price will be filled by broker)
    # ... other fields
)

result = await service.place_order(request)

# Check RetCode
if result.returned_code == 10009:  # Success for market orders
    print(f"[OK] Order opened: #{result.order}")
elif result.returned_code == 10008:  # Success for pending orders
    print(f"[OK] Pending order placed: #{result.order}")
else:
    print(f"[X] Order failed: {result.comment} (code {result.returned_code})")
```

**Common RetCodes:**

- `10009` - Market order executed successfully
- `10008` - Pending order placed successfully
- `10019` - Insufficient money (insufficient margin)
- `10016` - Invalid stops (SL/TP too close to price)
- `10018` - Market closed

Full list: [RETURN_CODES_REFERENCE.md](RETURN_CODES_REFERENCE.md)

## ℹ️ Error handling

PyMT5 uses Python exceptions for error handling:

### 1. Connection/Network errors

```python
try:
    result = await service.place_order(request)
except Exception as e:
    print(f"Connection or network error: {e}")
    return
```

### 2. Trading operation errors (RetCode)

```python
result = await service.place_order(request)
if result.returned_code != 10009:
    print(f"Trade rejected: {result.comment}")
```

**Always check BOTH!**

### Recommended pattern:

```python
try:
    result = await service.place_order(request)

    if result.returned_code == 10009:
        print(f"[OK] Success: Order #{result.order}")
    else:
        print(f"[X] Failed: {result.comment} (code: {result.returned_code})")

except Exception as e:
    print(f"[X] Error: {e}")
```

## 📝 Documentation

- [MT5Account Master Overview](../MT5Account/MT5Account.Master.Overview.md) - Complete API reference (40 methods)
- [MT5Service Overview](../MT5Service/MT5Service.Overview.md) - Mid-level wrapper (36 methods)
- [MT5Sugar Master Overview](../MT5Sugar/MT5Sugar.Master.Overview.md) - High-level Sugar API (62+ methods)
- [ENUMS Usage Reference](ENUMS_USAGE_REFERENCE.md) - All ENUMs in one place

## 🔑 Configuration

### Method 1: settings.json (Recommended)

Create `examples/0_common/settings.json`:

```json
{
  "user": 591129415,
  "password": "YourPassword",
  "grpc_server": "127.0.0.1:9999",
  "mt_cluster": "MetaQuotes-Demo",
  "test_symbol": "EURUSD",
  "test_volume": 0.01
}
```

### Method 2: Environment variables

```bash
# Linux/Mac
export MT5_USER=591129415
export MT5_PASSWORD="YourPassword"
export MT5_GRPC_SERVER="127.0.0.1:9999"
export MT5_CLUSTER="MetaQuotes-Demo"

# Windows PowerShell
$env:MT5_USER="591129415"
$env:MT5_PASSWORD="YourPassword"
$env:MT5_GRPC_SERVER="127.0.0.1:9999"
```

See [demo_helpers.py](../../examples/0_common/demo_helpers.py) for details.

## Tips

1. **Start simple** - Uncomment one example at a time

2. **Use Sugar API** - Methods like `buy_market_with_pips()` and 
`calculate_position_size()` are easier than low-level

3. **Check returned_code** - Always validate trading operations (10009 = success)

4. **Test on demo** - Make sure you're using demo account first!

5. **Read documentation** - [RETURN_CODES_REFERENCE.md](RETURN_CODES_REFERENCE.md) explains all error codes

6. **Use async/await** - All methods are asynchronous

7. **Type hints** - Use IDE autocomplete for better development experience

8. **Check examples** - See `examples/` folder for 15+ working examples

## Common mistakes

[X] **Forgot to use await**
```python
balance = sugar.get_balance()  # DON'T forget await!
```

[+] **Always use await**
```python
balance = await sugar.get_balance()
```

[X] **Not checking exceptions**
```python
ticket = await sugar.buy_market("EURUSD", 0.01)  # No try/except!
```

[+] **Always handle exceptions**
```python
try:
    ticket = await sugar.buy_market("EURUSD", 0.01)
    print(f"Order opened: #{ticket}")
except Exception as e:
    print(f"Error: {e}")
```

[X] **Not checking returned_code**
```python
result = await service.place_order(request)
# Assuming it's success!
```

[+] **Check returned_code for trading operations**
```python
result = await service.place_order(request)
if result.returned_code != 10009:
    print(f"Trade failed: {result.comment}")
    return
```

## Getting help

- **Protobuf types**: Check `package/MetaRpcMT5/` folder for all protobuf definitions
- **Error codes**: See [RETURN_CODES_REFERENCE.md](RETURN_CODES_REFERENCE.md)
- **Examples**: Check `examples/` folder for working code
- **API documentation**: See docs folder for complete reference

## Example: Complete trading strategy

Here's a complete example demonstrating proper error handling:

```python
async def run_user_code():
    """Your sandbox function - write your code here!"""

    try:
        # Load configuration
        config = load_settings()
    except Exception as e:
        print(f"Config error: {e}")
        return

    try:
        # Connect to MT5
        account = await create_and_connect_mt5(config)
    except Exception as e:
        print(f"Connection error: {e}")
        return

    # Create service and sugar wrappers
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol=config.get('test_symbol', 'EURUSD'))

    # Get account information
    try:
        balance = await sugar.get_balance()
        print(f"Balance: {balance:.2f}")
    except Exception as e:
        print(f"Balance error: {e}")
        return

    # Calculate position size based on risk (1% with 50 pip SL)
    try:
        volume = await sugar.calculate_position_size("EURUSD",
                                                      risk_percent=1.0,
                                                      sl_pips=50)
    except Exception as e:
        print(f"Position size error: {e}")
        return

    # Open position with calculated volume
    try:
        ticket = await sugar.buy_market_with_pips("EURUSD", volume,
                                                   sl_pips=50, tp_pips=100)
        print(f"[OK] Position opened: #{ticket} with {volume:.2f} lot")
    except Exception as e:
        print(f"Order error: {e}")
        return

    print("Strategy execution completed!")


if __name__ == "__main__":
    asyncio.run(run_user_code())
```

**Happy trading!**
