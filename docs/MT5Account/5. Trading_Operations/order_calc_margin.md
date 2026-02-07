# Calculate Required Margin

> **Request:** Calculate the margin required for a planned trade operation.

**API Information:**

* **Python API:** `MT5Account.order_calc_margin(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.TradeFunctions`
* **Proto definition:** `OrderCalcMargin` (defined in `mt5-term-api-trade-functions.proto`)
* **Enums in this method:** 1 enum with 9 constants (1 input)

### RPC

* **Service:** `mt5_term_api.TradeFunctions`
* **Method:** `OrderCalcMargin(OrderCalcMarginRequest) -> OrderCalcMarginReply`
* **Low-level client (generated):** `TradeFunctionsStub.OrderCalcMargin(request, metadata)`

---

## 💬 Just the essentials

* **What it is.** Calculates required margin for a trade without executing it.
* **Why you need it.** Plan position sizing and risk management.
* **Account currency.** Returns margin in your account currency (USD, EUR, etc.).

---

## 🎯 Purpose

Use it to:

* Calculate margin requirements before trading
* Determine maximum position size for available margin
* Plan multiple positions
* Risk management calculations
* Portfolio margin analysis
* Compare margin requirements across symbols

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[OrderCalcMargin - How it works](../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_margin_HOW.md)**


```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

class MT5Account:
    # ...

    async def order_calc_margin(
        self,
        request: trade_pb2.OrderCalcMarginRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trade_pb2.OrderCalcMarginData:
        """
        Calculates the margin required for a planned trade operation.

        Returns:
            OrderCalcMarginData: The required margin in account currency.
        """
```

**Request message:**

```protobuf
message OrderCalcMarginRequest {
  string symbol = 1;            // Symbol name
  ENUM_ORDER_TYPE_TF order_type = 2;  // Order type
  double volume = 3;            // Trade volume in lots
  double open_price = 4;        // Order open price
}
```

---

## 🔽 Input

| Parameter            | Type                           | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `request`            | `OrderCalcMarginRequest`       | Margin calculation request                    |
| `deadline`           | `Optional[datetime]`           | Deadline for the operation (optional)         |
| `cancellation_event` | `Optional[asyncio.Event]`      | Event to cancel the request (optional)        |

**OrderCalcMarginRequest fields:**

| Field        | Type                    | Description                          |
| ------------ | ----------------------- | ------------------------------------ |
| `symbol`     | `string`                | Symbol name (e.g., "EURUSD")         |
| `order_type` | `ENUM_ORDER_TYPE_TF`    | Order type (enum)                    |
| `volume`     | `double`                | Trade volume in lots                 |
| `open_price` | `double`                | Order open price                     |

---

## ⬆️ Output

Returns `OrderCalcMarginData` object with margin calculation.

**OrderCalcMarginData fields:**

| Field    | Type     | Description                          |
| -------- | -------- | ------------------------------------ |
| `margin` | `double` | Required margin in account currency  |

---

## 🧱 Related enums (from proto)

### `ENUM_ORDER_TYPE_TF`

Used in `OrderCalcMarginRequest` to specify order type for margin calculation.

| Constant Name                 | Value | Description                          |
| ----------------------------- | ----- | ------------------------------------ |
| `ORDER_TYPE_TF_BUY`           | 0     | Market buy order                     |
| `ORDER_TYPE_TF_SELL`          | 1     | Market sell order                    |
| `ORDER_TYPE_TF_BUY_LIMIT`     | 2     | Buy limit pending order              |
| `ORDER_TYPE_TF_SELL_LIMIT`    | 3     | Sell limit pending order             |
| `ORDER_TYPE_TF_BUY_STOP`      | 4     | Buy stop pending order               |
| `ORDER_TYPE_TF_SELL_STOP`     | 5     | Sell stop pending order              |
| `ORDER_TYPE_TF_BUY_STOP_LIMIT`| 6     | Buy stop limit pending order         |
| `ORDER_TYPE_TF_SELL_STOP_LIMIT`|7    | Sell stop limit pending order        |
| `ORDER_TYPE_TF_CLOSE_BY`      | 8     | Close by opposite position           |

**Usage:**
```python
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as trade_pb2

# Access enum values
trade_pb2.ORDER_TYPE_TF_BUY         # = 0
trade_pb2.ORDER_TYPE_TF_SELL        # = 1
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **No execution:** This method only calculates margin, does NOT execute orders.
* **Same request:** Uses identical request structure as `order_send`.
* **Leverage impact:** Result depends on symbol leverage and account settings.
* **Real-time calculation:** Uses current market prices for calculation.
* **Different from order_check:** This only returns margin, `order_check` validates full order.

---

## 🔗 Usage Examples

### 1) Calculate margin for single trade

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_margin():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # Calculate margin for 0.10 lots EURUSD
        request = trade_pb2.OrderCalcMarginRequest(
            symbol="EURUSD",
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            volume=0.10,
            open_price=1.0850
        )

        result = await account.order_calc_margin(request)

        print(f"[SUCCESS] Margin calculation:")
        print(f"  Symbol: EURUSD")
        print(f"  Volume: 0.10 lots")
        print(f"  Required margin: ${result.margin:,.2f}")

    finally:
        await account.channel.close()

asyncio.run(calc_margin())
```

### 2) Compare margin across symbols

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def compare_margin():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
    volume = 0.10

    try:
        print(f"Margin requirements for {volume} lots:\n")
        print(f"{'Symbol':<10} {'Margin':<15}")
        print("-" * 30)

        for symbol in symbols:
            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)
            print(f"{symbol:<10} ${result.margin:>12,.2f}")

    finally:
        await account.channel.close()

asyncio.run(compare_margin())
```

### 3) Calculate maximum position size

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def calc_max_position(symbol: str, margin_percent: float = 50.0):
    """Calculate max position size using X% of free margin"""
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # Get available margin
        summary_req = account_pb2.AccountSummaryRequest()
        summary = await account.account_summary(summary_req)
        available_margin = summary.margin_free * (margin_percent / 100.0)

        print(f"Calculating max position for {symbol}:")
        print(f"  Free margin: ${summary.margin_free:,.2f}")
        print(f"  Using {margin_percent}% = ${available_margin:,.2f}\n")

        # Binary search for max volume
        min_vol = 0.01
        max_vol = 100.0
        best_volume = 0.01

        while max_vol - min_vol > 0.01:
            test_volume = (min_vol + max_vol) / 2

            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=test_volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)

            if result.margin <= available_margin:
                best_volume = test_volume
                min_vol = test_volume
            else:
                max_vol = test_volume

        print(f"[RESULT] Maximum position size: {best_volume:.2f} lots")

        # Verify final calculation
        final_req = trade_pb2.OrderCalcMarginRequest(
            symbol=symbol,
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            volume=best_volume,
            open_price=1.0
        )
        final_result = await account.order_calc_margin(final_req)

        print(f"  Required margin: ${final_result.margin:,.2f}")
        print(f"  Margin usage: {(final_result.margin / available_margin * 100):.1f}%")

    finally:
        await account.channel.close()

asyncio.run(calc_max_position("EURUSD", margin_percent=50.0))
```

### 4) Portfolio margin calculation

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def portfolio_margin():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Planned portfolio
    trades = [
        ("EURUSD", 0.10),
        ("GBPUSD", 0.05),
        ("USDJPY", 0.10),
        ("XAUUSD", 0.01),
    ]

    try:
        # Get current account state
        summary_req = account_pb2.AccountSummaryRequest()
        summary = await account.account_summary(summary_req)

        print(f"Portfolio Margin Analysis\n")
        print(f"Current state:")
        print(f"  Balance: ${summary.balance:,.2f}")
        print(f"  Free margin: ${summary.margin_free:,.2f}\n")

        print(f"Planned trades:")
        print(f"{'Symbol':<10} {'Volume':<10} {'Margin':<15}")
        print("-" * 40)

        total_margin = 0.0

        for symbol, volume in trades:
            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)

            print(f"{symbol:<10} {volume:<10.2f} ${result.margin:>12,.2f}")
            total_margin += result.margin

        print("-" * 40)
        print(f"{'TOTAL':<10} {'':<10} ${total_margin:>12,.2f}\n")

        # Check if portfolio fits
        if total_margin <= summary.margin_free:
            remaining = summary.margin_free - total_margin
            usage_percent = (total_margin / summary.margin_free) * 100
            print(f"[OK] Portfolio fits!")
            print(f"  Margin usage: {usage_percent:.1f}%")
            print(f"  Remaining free margin: ${remaining:,.2f}")
        else:
            shortage = total_margin - summary.margin_free
            print(f"[WARNING] Insufficient margin!")
            print(f"  Required: ${total_margin:,.2f}")
            print(f"  Available: ${summary.margin_free:,.2f}")
            print(f"  Shortage: ${shortage:,.2f}")

    finally:
        await account.channel.close()

asyncio.run(portfolio_margin())
```

### 5) Risk-based position sizing

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def risk_based_sizing(symbol: str, risk_percent: float = 2.0):
    """Calculate position size based on risk percentage"""
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # Get account balance
        summary_req = account_pb2.AccountSummaryRequest()
        summary = await account.account_summary(summary_req)

        max_risk_amount = summary.balance * (risk_percent / 100.0)

        print(f"Risk-based position sizing for {symbol}:")
        print(f"  Account balance: ${summary.balance:,.2f}")
        print(f"  Risk: {risk_percent}% = ${max_risk_amount:,.2f}\n")

        # Test different volumes
        volumes = [0.01, 0.05, 0.10, 0.20, 0.50, 1.00]

        print(f"{'Volume':<10} {'Margin':<15} {'% of Balance':<15}")
        print("-" * 45)

        for volume in volumes:
            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)

            margin_percent = (result.margin / summary.balance) * 100

            status = "[OK]" if margin_percent <= risk_percent else "[OVER]"

            print(f"{volume:<10.2f} ${result.margin:>12,.2f} {margin_percent:>13.2f}% {status}")

    finally:
        await account.channel.close()

asyncio.run(risk_based_sizing("EURUSD", risk_percent=2.0))
```

### 6) Margin calculator helper class

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

class MarginCalculator:
    def __init__(self, account):
        self.account = account
        self.cache = {}  # Cache calculations

    async def get_margin(self, symbol: str, volume: float, order_type: int = 0):
        """Get margin with caching"""
        cache_key = f"{symbol}_{volume}_{order_type}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        request = trade_pb2.OrderCalcMarginRequest(
            symbol=symbol,
            order_type=order_type,
            volume=volume,
            open_price=1.0
        )

        result = await self.account.order_calc_margin(request)

        self.cache[cache_key] = result.margin
        return result.margin

    async def get_leverage_ratio(self, symbol: str, volume: float = 1.0):
        """Calculate effective leverage for symbol"""
        import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

        # Get contract size
        tick_req = market_pb2.SymbolInfoTickRequest(symbol=symbol)
        tick_data = await self.account.symbol_info_tick(tick_req)

        # Calculate margin for 1 lot
        margin = await self.get_margin(symbol, volume)

        # Contract value = price * contract_size
        contract_value = tick_data.tick.ask * 100000  # Assuming 100k contract

        leverage = contract_value / margin if margin > 0 else 0

        return leverage

async def main():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    calc = MarginCalculator(account)

    try:
        # Calculate margin
        margin = await calc.get_margin("EURUSD", 0.10)
        print(f"Margin for 0.10 lots EURUSD: ${margin:,.2f}")

        # Calculate leverage
        leverage = await calc.get_leverage_ratio("EURUSD", 1.0)
        print(f"Effective leverage: 1:{leverage:.0f}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

---

## 📚 See also

* [OrderCheck](./order_check.md) - Full order validation (includes margin)
* [OrderCalcProfit](./order_calc_profit.md) - Calculate potential profit/loss
* [OrderSend](./order_send.md) - Execute orders
* [AccountSummary](../1.%20Account_Information/account_summary.md) - Get account margin info
