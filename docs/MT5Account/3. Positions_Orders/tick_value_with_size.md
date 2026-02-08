# Get Tick Value and Contract Size for Symbols

> **Request:** tick value and contract size information for multiple symbols.

**API Information:**

* **Low-level API:** `MT5Account.tick_value_with_size(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.AccountHelper`
* **Proto definition:** `TickValueWithSize` (defined in `mt5-term-api-account-helper.proto`)
* **Enums in this method:** 0 enums (simple data structure)

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `TickValueWithSize(TickValueWithSizeRequest) -> TickValueWithSizeReply`
* **Low-level client (generated):** `AccountHelperStub.TickValueWithSize(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Get tick values and contract sizes for multiple symbols in one call.
* **Why you need it.** Calculate position value, margin requirements, and profit/loss in account currency.
* **When to use.** Use before trading to understand tick value and contract size for risk calculation.

---

## 🎯 Purpose

Use it to get critical trading parameters:

* Get tick value (value of one tick movement)
* Get tick size (minimum price change)
* Get contract size (lot size)
* Calculate profit/loss per tick
* Understand margin requirements
* Batch query multiple symbols efficiently

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [tick_value_with_size - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/tick_value_with_size_HOW.md)**

---

## Method Signature

```python
async def tick_value_with_size(
    self,
    symbols: list[str],
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.TickValueWithSizeData
```

**Request message:**

```protobuf
message TickValueWithSizeRequest {
  repeated string symbol_names = 1;
}
```

**Reply message:**

```protobuf
message TickValueWithSizeReply {
  TickValueWithSizeData data = 1;
  Error error = 2;
}

message TickValueWithSizeData {
  repeated TickSizeSymbol symbol_tick_size_infos = 1;
}
```

---

## 🔽 Input

| Parameter     | Type                    | Description                                             |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `symbols`     | `list[str]` (required)  | List of symbol names to query                           |
| `deadline`    | `datetime` (optional)   | Deadline for the gRPC call (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                    |

**Usage:**

```python
from datetime import datetime, timedelta

# Query multiple symbols
symbols = ["EURUSD", "GBPUSD", "USDJPY"]

deadline = datetime.utcnow() + timedelta(seconds=5)
data = await account.tick_value_with_size(
    symbols=symbols,
    deadline=deadline
)
```

---

## ⬆️ Output - `TickValueWithSizeData`

| Field                    | Type                      | Python Type            | Description                              |
| ------------------------ | ------------------------- | ---------------------- | ---------------------------------------- |
| `symbol_tick_size_infos` | `repeated TickSizeSymbol` | `list[TickSizeSymbol]` | List of tick value/size info per symbol |

**Each TickSizeSymbol contains:**

| Field                  | Type     | Python Type | Description                                          |
| ---------------------- | -------- | ----------- | ---------------------------------------------------- |
| `Index`                | `int32`  | `int`       | Index in the result set                              |
| `Name`                 | `string` | `str`       | Symbol name                                          |
| `TradeTickValue`       | `double` | `float`     | Tick value (for both profit and loss)                |
| `TradeTickValueProfit` | `double` | `float`     | Tick value for profit calculation                    |
| `TradeTickValueLoss`   | `double` | `float`     | Tick value for loss calculation                      |
| `TradeTickSize`        | `double` | `float`     | Minimum price change (tick size)                     |
| `TradeContractSize`    | `double` | `float`     | Contract size (lot size, e.g., 100000 for EURUSD)    |

---

## 🧩 Notes & Tips

* **Batch query:** Query multiple symbols in one call for efficiency.
* **Tick value:** The value in account currency of one tick movement.
* **Contract size:** The size of one standard lot (e.g., 100000 units for EURUSD).
* **Profit/Loss calculation:** Use tick value and tick size to calculate P/L per pip/tick.
* **Automatic reconnection:** Built-in protection against transient gRPC errors.
* **Connection required:** Call `connect_by_host_port()` or `connect_by_server_name()` first.
* **Thread safety:** Safe to call concurrently from multiple asyncio tasks.

---

## 🔗 Usage Examples

### 1) Get tick values for multiple symbols

```python
import asyncio
from datetime import datetime, timedelta
from MetaRpcMT5 import MT5Account

async def main():
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        deadline = datetime.utcnow() + timedelta(seconds=5)

        data = await account.tick_value_with_size(
            symbols=symbols,
            deadline=deadline
        )

        for info in data.symbol_tick_size_infos:
            print(f"\n{info.Name}:")
            print(f"  Tick Value: ${info.TradeTickValue:.2f}")
            print(f"  Tick Size: {info.TradeTickSize}")
            print(f"  Contract Size: {info.TradeContractSize:.0f}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Calculate profit per pip

```python
async def calculate_profit_per_pip(
    account: MT5Account,
    symbol: str,
    lots: float
) -> float:
    """Calculate profit per pip for given symbol and volume"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Symbol {symbol} not found")

    info = data.symbol_tick_size_infos[0]

    # Calculate profit per pip (assuming 10 ticks per pip for most pairs)
    profit_per_pip = info.TradeTickValue * 10 * lots

    print(f"{symbol}:")
    print(f"  Volume: {lots} lots")
    print(f"  Profit per pip: ${profit_per_pip:.2f}")

    return profit_per_pip

# Usage:
profit_per_pip = await calculate_profit_per_pip(account, "EURUSD", 1.0)
```

### 3) Calculate margin requirement

```python
async def calculate_margin(
    account: MT5Account,
    symbol: str,
    lots: float,
    price: float,
    leverage: int
) -> float:
    """Calculate margin requirement for position"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Symbol {symbol} not found")

    info = data.symbol_tick_size_infos[0]

    # Margin = (Contract Size * Lots * Price) / Leverage
    contract_value = info.TradeContractSize * lots * price
    margin = contract_value / leverage

    print(f"Margin calculation for {symbol}:")
    print(f"  Volume: {lots} lots")
    print(f"  Price: {price}")
    print(f"  Leverage: 1:{leverage}")
    print(f"  Contract Size: {info.TradeContractSize:.0f}")
    print(f"  Required Margin: ${margin:.2f}")

    return margin

# Usage:
margin = await calculate_margin(account, "EURUSD", 1.0, 1.10000, 100)
```

### 4) Get tick info for all major pairs

```python
async def get_major_pairs_info(account: MT5Account):
    """Get tick value info for major currency pairs"""
    major_pairs = [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
        "AUDUSD", "USDCAD", "NZDUSD"
    ]

    data = await account.tick_value_with_size(symbols=major_pairs)

    print("\nMajor Pairs Tick Information:")
    print(f"{'Symbol':<10} {'Tick Value':<12} {'Tick Size':<12} {'Contract Size':<15}")
    print("-" * 60)

    for info in data.symbol_tick_size_infos:
        print(f"{info.Name:<10} ${info.TradeTickValue:<11.2f} "
              f"{info.TradeTickSize:<12} {info.TradeContractSize:<15.0f}")

    return data

# Usage:
await get_major_pairs_info(account)
```

### 5) Calculate position value

```python
async def calculate_position_value(
    account: MT5Account,
    symbol: str,
    lots: float,
    price: float
) -> dict:
    """Calculate total position value"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Symbol {symbol} not found")

    info = data.symbol_tick_size_infos[0]

    # Position value = Contract Size * Lots * Price
    position_value = info.TradeContractSize * lots * price

    result = {
        "symbol": symbol,
        "lots": lots,
        "price": price,
        "contract_size": info.TradeContractSize,
        "position_value": position_value,
        "tick_value": info.TradeTickValue,
        "tick_size": info.TradeTickSize
    }

    print(f"\nPosition Value Calculation:")
    print(f"  Symbol: {symbol}")
    print(f"  Volume: {lots} lots")
    print(f"  Price: {price}")
    print(f"  Contract Size: {info.TradeContractSize:.0f}")
    print(f"  Position Value: ${position_value:,.2f}")

    return result

# Usage:
value = await calculate_position_value(account, "EURUSD", 1.0, 1.10000)
```

### 6) Compare tick values across symbols

```python
async def compare_tick_values(account: MT5Account, symbols: list[str]):
    """Compare tick values across multiple symbols"""
    data = await account.tick_value_with_size(symbols=symbols)

    # Sort by tick value
    sorted_infos = sorted(
        data.symbol_tick_size_infos,
        key=lambda x: x.TradeTickValue,
        reverse=True
    )

    print("\nSymbols sorted by tick value:")
    for i, info in enumerate(sorted_infos, 1):
        print(f"{i}. {info.Name}: ${info.TradeTickValue:.2f} per tick")

    return sorted_infos

# Usage:
symbols = ["EURUSD", "GBPUSD", "USDJPY", "GOLD", "OIL"]
await compare_tick_values(account, symbols)
```

### 7) Calculate stop loss distance

```python
async def calculate_sl_distance(
    account: MT5Account,
    symbol: str,
    lots: float,
    max_loss: float
) -> float:
    """Calculate maximum SL distance for given max loss"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Symbol {symbol} not found")

    info = data.symbol_tick_size_infos[0]

    # Calculate pips allowed
    profit_per_pip = info.TradeTickValue * 10 * lots
    max_pips = max_loss / profit_per_pip if profit_per_pip > 0 else 0

    print(f"\nStop Loss Calculation for {symbol}:")
    print(f"  Volume: {lots} lots")
    print(f"  Max Loss: ${max_loss:.2f}")
    print(f"  Profit per pip: ${profit_per_pip:.2f}")
    print(f"  Max SL distance: {max_pips:.1f} pips")

    return max_pips

# Usage:
max_pips = await calculate_sl_distance(account, "EURUSD", 1.0, 100.0)
```

### 8) Validate symbols exist

```python
async def validate_symbols(
    account: MT5Account,
    symbols: list[str]
) -> dict:
    """Check which symbols are valid and available"""
    data = await account.tick_value_with_size(symbols=symbols)

    returned_symbols = {info.Name for info in data.symbol_tick_size_infos}
    requested_symbols = set(symbols)

    valid = list(returned_symbols)
    invalid = list(requested_symbols - returned_symbols)

    result = {
        "valid": valid,
        "invalid": invalid,
        "valid_count": len(valid),
        "invalid_count": len(invalid)
    }

    print(f"\nSymbol Validation:")
    print(f"  Valid symbols: {valid}")
    if invalid:
        print(f"  Invalid symbols: {invalid}")

    return result

# Usage:
symbols = ["EURUSD", "INVALID_SYMBOL", "GBPUSD"]
validation = await validate_symbols(account, symbols)
```

---

## Common Patterns

### Get tick value for single symbol

```python
async def get_symbol_tick_value(account: MT5Account, symbol: str) -> float:
    """Get tick value for single symbol"""
    data = await account.tick_value_with_size(symbols=[symbol])
    if data.symbol_tick_size_infos:
        return data.symbol_tick_size_infos[0].TradeTickValue
    return 0.0
```

### Calculate risk per position

```python
async def calculate_risk(
    account: MT5Account,
    symbol: str,
    lots: float,
    sl_pips: float
) -> float:
    """Calculate risk amount for position with SL"""
    data = await account.tick_value_with_size(symbols=[symbol])
    if not data.symbol_tick_size_infos:
        return 0.0

    info = data.symbol_tick_size_infos[0]
    profit_per_pip = info.TradeTickValue * 10 * lots
    risk = profit_per_pip * sl_pips

    return risk
```

---

## 📚 See also

* [opened_orders](./opened_orders.md) - Get currently open positions
* [positions_total](./positions_total.md) - Get count of open positions
