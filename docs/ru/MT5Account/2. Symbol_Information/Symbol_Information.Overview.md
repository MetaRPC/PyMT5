# MT5Account - Информация о символах - Обзор

> Цены, свойства, параметры символов и торговые условия. Запрашивайте отдельные свойства или получайте полные данные символа.

## 📁 Что находится здесь

* **[symbols_total](./symbols_total.md)** - **количество** доступных символов.
* **[symbol_exist](./symbol_exist.md)** - **проверка существования символа** на платформе.
* **[symbol_name](./symbol_name.md)** - **получить имя символа** по позиции индекса.
* **[symbol_select](./symbol_select.md)** - **добавить/удалить символ** из Market Watch.
* **[symbol_is_synchronized](./symbol_is_synchronized.md)** - **проверка синхронизации данных символа**.
* **[symbol_info_double](./symbol_info_double.md)** - **одно свойство double** (BID, ASK, POINT и т. д.).
* **[symbol_info_integer](./symbol_info_integer.md)** - **одно целочисленное свойство** (DIGITS, SPREAD и т. д.).
* **[symbol_info_string](./symbol_info_string.md)** - **одно строковое свойство** (DESCRIPTION, CURRENCY_BASE и т. д.).
* **[symbol_info_tick](./symbol_info_tick.md)** - **текущие данные тика** (BID, ASK, объём, время).
* **[symbol_info_margin_rate](./symbol_info_margin_rate.md)** - **ставки маржи** для символа и типа ордера.
* **[symbol_info_session_quote](./symbol_info_session_quote.md)** - **время котировочной сессии** для дня недели.
* **[symbol_info_session_trade](./symbol_info_session_trade.md)** - **время торговой сессии** для дня недели.
* **[symbol_params_many](./symbol_params_many.md)** - **все параметры символа сразу** (РЕКОМЕНДУЕТСЯ для нескольких свойств).

---

## 📚 Пошаговые руководства

Нужны подробные объяснения с построчным разбором кода? Смотрите эти руководства:

* **[symbols_total - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbols_total_HOW.md)**
* **[symbol_exist - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_exist_HOW.md)**
* **[symbol_name - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_name_HOW.md)**
* **[symbol_select - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_select_HOW.md)**
* **[symbol_is_synchronized - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_is_synchronized_HOW.md)**
* **[symbol_info_double - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_double_HOW.md)**
* **[symbol_info_integer - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_integer_HOW.md)**
* **[symbol_info_string - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_string_HOW.md)**
* **[symbol_info_tick - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_tick_HOW.md)**
* **[symbol_info_margin_rate - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_margin_rate_HOW.md)**
* **[symbol_info_session_quote - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_quote_HOW.md)**
* **[symbol_info_session_trade - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_trade_HOW.md)**
* **[symbol_params_many - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_params_many_HOW.md)**

---

## 🧭 Простыми словами

* **symbols_total** - сколько символов доступно (все или только Market Watch).
* **symbol_exist** - проверить, является ли имя символа действительным.
* **symbol_name** - получить имя символа по номеру позиции.
* **symbol_select** - показать/скрыть символ в Market Watch.
* **symbol_is_synchronized** - проверить, что данные символа актуальны.
* **symbol_info_double** - получить одно числовое значение (цена, спред и т. д.).
* **symbol_info_integer** - получить одно целочисленное значение (знаки, пункты спреда и т. д.).
* **symbol_info_string** - получить одно текстовое значение (описание, валюта и т. д.).
* **symbol_info_tick** - получить текущий снимок цены.
* **symbol_info_margin_rate** - получить требования к марже.
* **symbol_info_session_quote/trade** - получить часы торговли.
* **symbol_params_many** - получить ВСЕ свойства за один вызов (наиболее эффективно).

> Правило большого пальца: нужны **все свойства** - `symbol_params_many()` (РЕКОМЕНДУЕТСЯ); нужно **одно свойство** - `symbol_info_*`; нужна **текущая цена** - `symbol_info_tick()`.

---

## Быстрый выбор

| Если вам нужно                                       | Используйте                   | Возвращает                 | Ключевые входные данные             |
| ---------------------------------------------------- | ----------------------------- | -------------------------- | ----------------------------------- |
| Количество символов                                  | `symbols_total`               | SymbolsTotalData (count)   | selected_only (bool)                |
| Проверить существование символа                      | `symbol_exist`                | SymbolExistData (bool)     | symbol name                         |
| Имя символа по позиции                               | `symbol_name`                 | SymbolNameData (string)    | index, selected                     |
| Добавить/удалить из Market Watch                     | `symbol_select`               | SymbolSelectData (bool)    | symbol, select                      |
| Проверить синхронизацию данных                       | `symbol_is_synchronized`      | SymbolIsSynchronizedData   | symbol name                         |
| Одно значение double                                 | `symbol_info_double`          | SymbolInfoDoubleData       | symbol, property enum               |
| Одно целочисленное значение                          | `symbol_info_integer`         | SymbolInfoIntegerData      | symbol, property enum               |
| Одно строковое значение                              | `symbol_info_string`          | SymbolInfoStringData       | symbol, property enum               |
| Текущий тик (BID/ASK/объём)                          | `symbol_info_tick`            | MrpcMqlTick                | symbol name                         |
| Ставки маржи                                         | `symbol_info_margin_rate`     | SymbolInfoMarginRateData   | symbol, order_type                  |
| Время котировочной сессии                            | `symbol_info_session_quote`   | SymbolInfoSessionQuoteData | symbol, day, session_index          |
| Время торговой сессии                                | `symbol_info_session_trade`   | SymbolInfoSessionTradeData | symbol, day, session_index          |
| ВСЕ параметры символа (РЕКОМЕНДУЕТСЯ)                 | `symbol_params_many`          | SymbolParamsManyData       | symbol_name (optional), pagination  |

---

## ℹ️ Перекрёстные ссылки и подводные камни

* **symbol_params_many** - РЕКОМЕНДУЕТСЯ для получения нескольких свойств (один вызов вместо многих).
* **BID vs ASK** - BID это цена продажи, ASK это цена покупки. Спред = ASK - BID.
* **DIGITS** - количество десятичных знаков для символа (например, 5 для EURUSD = 1.12345).
* **SPREAD** - текущий спред в пунктах, не в пипсах (для 5 знаков: 1 пипс = 10 пунктов).
* **Market Watch** - символы должны быть в Market Watch, чтобы получить цены.
* **Синхронизация** - проверяйте `symbol_is_synchronized()` перед торговлей.
* **Время сессий** - возвращается в секундах от полуночи (переводите в часы:минуты).
* **Данные тика** - используйте `symbol_info_tick()` для снимка цены в реальном времени.

---

## 🟢 Минимальные фрагменты

```python
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Получить полные параметры символа (РЕКОМЕНДУЕТСЯ)
request = account_helper_pb2.SymbolParamsManyRequest(symbol_name="EURUSD")
data = await account.symbol_params_many(request=request)
if data.symbol_infos:
    info = data.symbol_infos[0]
    print(f"BID: {info.bid}, ASK: {info.ask}")
    print(f"Spread: {info.spread}, Digits: {info.digits}")
    print(f"Contract Size: {info.trade_contract_size}")
```

```python
# Получить текущий тик
tick = await account.symbol_info_tick(symbol="EURUSD")
print(f"BID: {tick.bid}, ASK: {tick.ask}")
print(f"Spread: {tick.ask - tick.bid}")
```

```python
# Получить конкретные свойства
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
# Проверить существование символа
data = await account.symbol_exist(symbol="EURUSD")
if data.exists:
    print(f"[OK] EURUSD exists ({'custom' if data.is_custom else 'standard'})")
```

```python
# Получить все символы Market Watch
count_data = await account.symbols_total(selected_only=True)

symbols = []
for i in range(count_data.total):
    name_data = await account.symbol_name(index=i, selected=True)
    symbols.append(name_data.name)

print(f"Market Watch symbols: {symbols}")
```

```python
# Добавить символ в Market Watch
result = await account.symbol_select(symbol="EURUSD", select=True)
if result.success:
    print("[OK] Symbol added to Market Watch")
```

```python
# Рассчитать спред в пипсах
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
# Получить все символы с параметрами
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

request = account_helper_pb2.SymbolParamsManyRequest(items_per_page=100)
data = await account.symbol_params_many(request=request)

print(f"Total symbols: {data.symbols_total}")
for info in data.symbol_infos:
    print(f"{info.name}: BID={info.bid}, ASK={info.ask}, Spread={info.spread}")
```

```python
# Получить ставки маржи
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

rates = await account.symbol_info_margin_rate(
    symbol="EURUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

print(f"Initial margin: {rates.initial_margin_rate}")
print(f"Maintenance margin: {rates.maintenance_margin_rate}")
```

```python
# Проверить часы торговли
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

session = await account.symbol_info_session_trade(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

from_hours = getattr(session, 'from').seconds // 3600
from_mins = (getattr(session, 'from').seconds % 3600) // 60
to_hours = session.to.seconds // 3600
to_mins = (session.to.seconds % 3600) // 60

print(f"Monday trading: {from_hours:02d}:{from_mins:02d} - {to_hours:02d}:{to_mins:02d}")
```

---

## 📚 См. также

* **Информация о счёте:** [Account_Information.Overview](../1. Account_Information/Account_Information.Overview.md) - получить баланс счёта, средства (equity), кредитное плечо
* **Позиции и ордера:** [Positions_Orders.Overview](../3. Positions_Orders/Positions_Orders.Overview.md) - управление открытыми позициями и ордерами
* **Торговые операции:** [Trading_Operations.Overview](../5. Trading_Operations/Trading_Operations.Overview.md) - размещение и управление сделками
