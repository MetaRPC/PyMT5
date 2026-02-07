# MT5Account - Symbol Information - Overview

> Symbol prices, properties, parameters, and trading conditions. Query individual properties or get complete symbol data.

## 📁 What lives here

* **[symbols_total](./symbols_total.md)** - **count** of available symbols.
* **[symbol_exist](./symbol_exist.md)** - **check if symbol exists** on platform.
* **[symbol_name](./symbol_name.md)** - **get symbol name** by index position.
* **[symbol_select](./symbol_select.md)** - **add/remove symbol** from Market Watch.
* **[symbol_is_synchronized](./symbol_is_synchronized.md)** - **check if symbol data** is synchronized.
* **[symbol_info_double](./symbol_info_double.md)** - **single double property** (BID, ASK, POINT, etc.).
* **[symbol_info_integer](./symbol_info_integer.md)** - **single integer property** (DIGITS, SPREAD, etc.).
* **[symbol_info_string](./symbol_info_string.md)** - **single string property** (DESCRIPTION, CURRENCY_BASE, etc.).
* **[symbol_info_tick](./symbol_info_tick.md)** - **current tick data** (BID, ASK, volume, time).
* **[symbol_info_margin_rate](./symbol_info_margin_rate.md)** - **margin rates** for symbol and order type.
* **[symbol_info_session_quote](./symbol_info_session_quote.md)** - **quote session times** for day of week.
* **[symbol_info_session_trade](./symbol_info_session_trade.md)** - **trade session times** for day of week.
* **[symbol_params_many](./symbol_params_many.md)** - **all symbol parameters at once** (RECOMMENDED for multiple properties).

---

## 📚 Step-by-step tutorials

Want detailed explanations with line-by-line code breakdown? Check these guides:

* **[symbols_total - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbols_total_HOW.md)**
* **[symbol_exist - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_exist_HOW.md)**
* **[symbol_name - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_name_HOW.md)**
* **[symbol_select - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_select_HOW.md)**
* **[symbol_is_synchronized - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_is_synchronized_HOW.md)**
* **[symbol_info_double - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_double_HOW.md)**
* **[symbol_info_integer - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_integer_HOW.md)**
* **[symbol_info_string - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_string_HOW.md)**
* **[symbol_info_tick - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_tick_HOW.md)**
* **[symbol_info_margin_rate - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_margin_rate_HOW.md)**
* **[symbol_info_session_quote - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_quote_HOW.md)**
* **[symbol_info_session_trade - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_trade_HOW.md)**
* **[symbol_params_many - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_params_many_HOW.md)**

---

## 🧭 Plain English

* **symbols_total** - how many symbols are available (all or Market Watch only).
* **symbol_exist** - check if symbol name is valid.
* **symbol_name** - get symbol name by position number.
* **symbol_select** - show/hide symbol in Market Watch.
* **symbol_is_synchronized** - verify symbol data is up-to-date.
* **symbol_info_double** - get one numeric value (price, spread, etc.).
* **symbol_info_integer** - get one integer value (digits, spread points, etc.).
* **symbol_info_string** - get one text value (description, currency, etc.).
* **symbol_info_tick** - get current price snapshot.
* **symbol_info_margin_rate** - get margin requirements.
* **symbol_info_session_quote/trade** - get trading hours.
* **symbol_params_many** - get ALL properties in one call (most efficient).

> Rule of thumb: need **all properties** - `symbol_params_many()` (RECOMMENDED); need **one property** - `symbol_info_*`; need **current price** - `symbol_info_tick()`.

---

## Quick choose

| If you need                                          | Use                           | Returns                    | Key inputs                          |
| ---------------------------------------------------- | ----------------------------- | -------------------------- | ----------------------------------- |
| Count of symbols                                     | `symbols_total`               | SymbolsTotalData (count)   | selected_only (bool)                |
| Check symbol exists                                  | `symbol_exist`                | SymbolExistData (bool)     | symbol name                         |
| Symbol name by position                              | `symbol_name`                 | SymbolNameData (string)    | index, selected                     |
| Add/remove from Market Watch                         | `symbol_select`               | SymbolSelectData (bool)    | symbol, select                      |
| Check data synchronized                              | `symbol_is_synchronized`      | SymbolIsSynchronizedData   | symbol name                         |
| Single double value                                  | `symbol_info_double`          | SymbolInfoDoubleData       | symbol, property enum               |
| Single integer value                                 | `symbol_info_integer`         | SymbolInfoIntegerData      | symbol, property enum               |
| Single string value                                  | `symbol_info_string`          | SymbolInfoStringData       | symbol, property enum               |
| Current tick (BID/ASK/volume)                        | `symbol_info_tick`            | MrpcMqlTick                | symbol name                         |
| Margin rates                                         | `symbol_info_margin_rate`     | SymbolInfoMarginRateData   | symbol, order_type                  |
| Quote session times                                  | `symbol_info_session_quote`   | SymbolInfoSessionQuoteData | symbol, day, session_index          |
| Trade session times                                  | `symbol_info_session_trade`   | SymbolInfoSessionTradeData | symbol, day, session_index          |
| ALL symbol parameters (RECOMMENDED)                  | `symbol_params_many`          | SymbolParamsManyData       | symbol_name (optional), pagination  |

---

## ℹ️ Cross-refs & gotchas

* **symbol_params_many** - RECOMMENDED for getting multiple properties (single call instead of many).
* **BID vs ASK** - BID is sell price, ASK is buy price. Spread = ASK - BID.
* **DIGITS** - number of decimal places for symbol (e.g., 5 for EURUSD = 1.12345).
* **SPREAD** - current spread in points, not pips (for 5-digit: 1 pip = 10 points).
* **Market Watch** - symbols must be in Market Watch to get prices.
* **Synchronization** - check `symbol_is_synchronized()` before trading.
* **Session times** - returned in seconds from midnight (convert to hours:minutes).
* **Tick data** - use `symbol_info_tick()` for real-time price snapshot.

---

## 🟢 Minimal snippets

```python
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Get complete symbol parameters (RECOMMENDED)
request = account_helper_pb2.SymbolParamsManyRequest(symbol_name="EURUSD")
data = await account.symbol_params_many(request=request)
if data.symbol_infos:
    info = data.symbol_infos[0]
    print(f"BID: {info.bid}, ASK: {info.ask}")
    print(f"Spread: {info.spread}, Digits: {info.digits}")
    print(f"Contract Size: {info.trade_contract_size}")
```

```python
# Get current tick
tick = await account.symbol_info_tick(symbol="EURUSD")
print(f"BID: {tick.bid}, ASK: {tick.ask}")
print(f"Spread: {tick.ask - tick.bid}")
```

```python
# Get specific properties
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

bid_data = await account.symbol_info_double(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_BID
)

digits_data = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DIGITS
)

print(f"BID: {bid_data.value:.{digits_data.value}f}")
```

```python
# Check if symbol exists
data = await account.symbol_exist(symbol="EURUSD")
if data.exists:
    print(f"[OK] EURUSD exists ({'custom' if data.is_custom else 'standard'})")
```

```python
# Get all Market Watch symbols
count_data = await account.symbols_total(selected_only=True)

symbols = []
for i in range(count_data.total):
    name_data = await account.symbol_name(index=i, selected=True)
    symbols.append(name_data.name)

print(f"Market Watch symbols: {symbols}")
```

```python
# Add symbol to Market Watch
result = await account.symbol_select(symbol="EURUSD", select=True)
if result.success:
    print("[OK] Symbol added to Market Watch")
```

```python
# Calculate spread in pips
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

tick = await account.symbol_info_tick(symbol="EURUSD")
digits_data = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DIGITS
)

digits = digits_data.value
spread_points = (tick.ask - tick.bid) * (10 ** digits)
spread_pips = spread_points / 10 if digits == 5 else spread_points

print(f"Spread: {spread_pips:.1f} pips")
```

```python
# Get all symbols with parameters
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

request = account_helper_pb2.SymbolParamsManyRequest(items_per_page=100)
data = await account.symbol_params_many(request=request)

print(f"Total symbols: {data.symbols_total}")
for info in data.symbol_infos:
    print(f"{info.name}: BID={info.bid}, ASK={info.ask}, Spread={info.spread}")
```

```python
# Get margin rates
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

rates = await account.symbol_info_margin_rate(
    symbol="EURUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

print(f"Initial margin: {rates.initial_margin_rate}")
print(f"Maintenance margin: {rates.maintenance_margin_rate}")
```

```python
# Check trading hours
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

session = await account.symbol_info_session_trade(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

from_hours = session.from.seconds // 3600
from_mins = (session.from.seconds % 3600) // 60
to_hours = session.to.seconds // 3600
to_mins = (session.to.seconds % 3600) // 60

print(f"Monday trading: {from_hours:02d}:{from_mins:02d} - {to_hours:02d}:{to_mins:02d}")
```

---

## 📚 See also

* **Account Information:** [Account_Information.Overview](../1. Account_Information/Account_Information.Overview.md) - get account balance, equity, leverage
* **Positions & Orders:** [Positions_Orders.Overview](../3. Positions_Orders/Positions_Orders.Overview.md) - manage open positions and orders
* **Trading Operations:** [Trading_Operations.Overview](../5. Trading_Operations/Trading_Operations.Overview.md) - place and manage trades
