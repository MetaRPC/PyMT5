# Get Symbol Margin Rates

> **Request:** retrieve margin rates for symbol and order type.

**API Information:**

* **Low-level API:** `MT5Account.symbol_info_margin_rate(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.MarketInfo`
* **Proto definition:** `SymbolInfoMarginRate` (defined in `mt5-term-api-market-info.proto`)

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolInfoMarginRate(SymbolInfoMarginRateRequest) -> SymbolInfoMarginRateReply`
* **Low-level client (generated):** `MarketInfoStub.SymbolInfoMarginRate(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Retrieve initial and maintenance margin rates for a specific symbol and order type.
* **Why you need it.** Calculate margin requirements before placing orders, understand leverage conditions.
* **When to use.** Use before trading to estimate margin needs, especially for different order types (BUY/SELL).

---

## 🎯 Purpose

Use it to query margin requirements:

* Calculate required margin before opening positions
* Understand margin differences between BUY and SELL orders
* Estimate leverage impact on margin
* Validate available margin before trading
* Compare margin requirements across symbols
* Plan position sizing based on margin availability

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_info_margin_rate - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_margin_rate_HOW.md)**

---

## Method Signature

```python
async def symbol_info_margin_rate(
    self,
    symbol: str,
    order_type: market_info_pb2.ENUM_ORDER_TYPE,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoMarginRateData
```

**Request message:**

```protobuf
message SymbolInfoMarginRateRequest {
  string symbol = 1;
  ENUM_ORDER_TYPE order_type = 2;
}
```

**Reply message:**

```protobuf
message SymbolInfoMarginRateReply {
  oneof response {
    SymbolInfoMarginRateData data = 1;
    Error error = 2;
  }
}

message SymbolInfoMarginRateData {
  double maintenance_margin_rate = 1;
  double initial_margin_rate = 2;
}
```

---

## 🔽 Input

| Parameter    | Type                     | Description                           |
| ------------ | ------------------------ | ------------------------------------- |
| `symbol`     | `str` (required)         | Symbol name                           |
| `order_type` | `ENUM_ORDER_TYPE` (enum) | Order type (BUY, SELL, etc.)          |
| `deadline`    | `datetime` (optional)   | Deadline for the gRPC call (UTC datetime) |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation |

---

## ⬆️ Output

| Field                     | Type     | Python Type | Description                     |
| ------------------------- | -------- | ----------- | ------------------------------- |
| `initial_margin_rate`     | `double` | `float`     | Initial margin rate             |
| `maintenance_margin_rate` | `double` | `float`     | Maintenance margin rate         |

**Return value:** The method returns `SymbolInfoMarginRateData` object with margin rate fields.

---

## 🧱 Related enums (from proto)

> **Note:** In Python code, use the full enum path from the market_info module.

### `ENUM_ORDER_TYPE`

Defined in `mt5-term-api-market-info.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `ORDER_TYPE_BUY` | 0 | Buy market order |
| `ORDER_TYPE_SELL` | 1 | Sell market order |
| `ORDER_TYPE_BUY_LIMIT` | 2 | Buy Limit pending order |
| `ORDER_TYPE_SELL_LIMIT` | 3 | Sell Limit pending order |
| `ORDER_TYPE_BUY_STOP` | 4 | Buy Stop pending order |
| `ORDER_TYPE_SELL_STOP` | 5 | Sell Stop pending order |
| `ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Buy Stop Limit pending order |
| `ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Sell Stop Limit pending order |
| `ORDER_TYPE_CLOSE_BY` | 8 | Close by opposite order |

**Usage in Python:**
```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get margin rates for BUY orders
rates = await account.symbol_info_margin_rate(
    symbol="EURUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)
print(f"Initial margin rate: {rates.initial_margin_rate}")
print(f"Maintenance margin rate: {rates.maintenance_margin_rate}")
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Margin rates meaning:**
  - **Initial margin rate:** The rate used when opening a position (multiplied by contract value)
  - **Maintenance margin rate:** The rate used for maintaining an open position
* **Rate differences:** BUY and SELL orders may have different margin rates for the same symbol.
* **Hedge accounts:** On hedge accounts, margin rates are typically the same for BUY and SELL.
* **Netting accounts:** On netting accounts, margin calculations may differ based on position direction.
* **Calculation:** Required margin = (Contract Size × Volume × Price) × Margin Rate
* **UUID handling:** The terminal instance UUID is auto-generated by the server if not provided. 
  For explicit control (e.g., in streaming scenarios), pass `id_=uuid4()` to constructor.
  
---

## 🔗 Usage Examples

### 1) Get margin rates for BUY order

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get margin rates for BUY order
rates = await account.symbol_info_margin_rate(
    symbol="EURUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

print(f"BUY Order Margin Rates:")
print(f"  Initial: {rates.initial_margin_rate}")
print(f"  Maintenance: {rates.maintenance_margin_rate}")
```

### 2) Compare BUY vs SELL margin rates

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Get BUY margin rates
buy_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

# Get SELL margin rates
sell_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_SELL
)

print(f"XAUUSD Margin Rates:")
print(f"  BUY  - Initial: {buy_rates.initial_margin_rate}, Maintenance: {buy_rates.maintenance_margin_rate}")
print(f"  SELL - Initial: {sell_rates.initial_margin_rate}, Maintenance: {sell_rates.maintenance_margin_rate}")

if buy_rates.initial_margin_rate == sell_rates.initial_margin_rate:
    print("  Same margin rates for both directions (hedge account)")
else:
    print("  Different margin rates (check account type)")
```

### 3) Calculate required margin before trading

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def calculate_required_margin(
    account,
    symbol: str,
    volume: float,
    order_type: int = market_info_pb2.ORDER_TYPE_BUY
) -> float:
    """Calculate required margin for opening a position"""

    # Get margin rates
    rates = await account.symbol_info_margin_rate(
        symbol=symbol,
        order_type=order_type
    )

    # Get contract size
    contract_size_data = await account.symbol_info_double(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_TRADE_CONTRACT_SIZE
    )

    # Get current price (ASK for BUY, BID for SELL)
    if order_type in [market_info_pb2.ORDER_TYPE_BUY, market_info_pb2.ORDER_TYPE_BUY_LIMIT, market_info_pb2.ORDER_TYPE_BUY_STOP]:
        price_data = await account.symbol_info_double(symbol=symbol, property=market_info_pb2.SYMBOL_ASK)
    else:
        price_data = await account.symbol_info_double(symbol=symbol, property=market_info_pb2.SYMBOL_BID)

    # Calculate margin
    contract_value = contract_size_data.value * volume * price_data.value
    required_margin = contract_value * rates.initial_margin_rate

    return required_margin

# Usage
margin = await calculate_required_margin(
    account=account,
    symbol="EURUSD",
    volume=1.0,
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

print(f"Required margin for 1.0 lot EURUSD BUY: ${margin:.2f}")
```

### 4) Check if sufficient margin available

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

async def can_open_position(
    account,
    symbol: str,
    volume: float,
    order_type: int = market_info_pb2.ORDER_TYPE_BUY
) -> bool:
    """Check if account has sufficient margin to open position"""

    # Calculate required margin (from previous example)
    required_margin = await calculate_required_margin(account, symbol, volume, order_type)

    # Get free margin
    free_margin = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE
    )

    # Check if sufficient
    if free_margin >= required_margin:
        print(f"[OK] Sufficient margin:")
        print(f"  Required: ${required_margin:.2f}")
        print(f"  Available: ${free_margin:.2f}")
        return True
    else:
        print(f"[ERROR] Insufficient margin:")
        print(f"  Required: ${required_margin:.2f}")
        print(f"  Available: ${free_margin:.2f}")
        print(f"  Deficit: ${required_margin - free_margin:.2f}")
        return False

# Usage
if await can_open_position(account, "EURUSD", 2.0):
    print("Safe to open 2.0 lot position")
```

### 5) Get margin rates with timeout

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta

# Set deadline
deadline = datetime.utcnow() + timedelta(seconds=3)

try:
    rates = await account.symbol_info_margin_rate(
        symbol="GBPUSD",
        order_type=market_info_pb2.ORDER_TYPE_BUY,
        deadline=deadline
    )
    print(f"Margin rates retrieved: {rates.initial_margin_rate}")
except Exception as e:
    print(f"Timeout or error: {e}")
```

### 6) Compare margin requirements across symbols

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def compare_symbol_margins(account, symbols: list[str]):
    """Compare margin requirements for multiple symbols"""

    print(f"{'Symbol':<10} {'Initial Rate':<15} {'Maintenance Rate':<20}")
    print("=" * 45)

    for symbol in symbols:
        try:
            rates = await account.symbol_info_margin_rate(
                symbol=symbol,
                order_type=market_info_pb2.ORDER_TYPE_BUY
            )
            print(f"{symbol:<10} {rates.initial_margin_rate:<15.4f} {rates.maintenance_margin_rate:<20.4f}")
        except Exception as e:
            print(f"{symbol:<10} ERROR: {e}")

# Usage
await compare_symbol_margins(account, ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"])
```

---

## 📚 See also

* [symbol_info_double](./symbol_info_double.md) - Get symbol double properties (contract size, prices)
* [order_calc_margin](../5. Trading_Operations/order_calc_margin.md) - Calculate margin for specific order parameters
* [account_info_double](../1. Account_Information/account_info_double.md) - Get account margin information
