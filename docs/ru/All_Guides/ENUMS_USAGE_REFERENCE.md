# Справочник использования ENUM — MT5Account (Python)

> Таблица наличия ENUM для всех низкоуровневых методов MT5Account

---

## ✅ Сводная статистика

| Группа методов | С ENUM | Всего | Процент |
|--------------|------------|-------|------------|
| **Информация о счёте** | 4 | 4 | 100% |
| **Информация о символе** | 7 | 13 | 54% |
| **Позиции и ордера** | 3 | 6 | 50% |
| **Глубина рынка/DOM** | 1 | 3 | 33% |
| **Торговые операции** | 6 | 6 | 100% |
| **Методы стриминга** | 3 | 5 | 60% |
| **ВСЕГО** | **24** | **37** | **65%** |

---

## 👤 1. Информация о счёте (4 метода)

### 4/4 методов используют ENUM (100%)

| Метод | Количество ENUM | Описание | Входные ENUM | Выходные ENUM |
|--------|-------------|-------------|-------------|--------------|
| **account_summary** | **[In: 0, Out: 1]**<br>Всего: 1 ENUM (3 значения) | Получить все данные счёта за один вызов (РЕКОМЕНДУЕТСЯ) | - | `MrpcEnumAccountTradeMode` (3 значения) — тип счёта: DEMO, CONTEST, REAL |
| **account_info_double** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (14 значений) | Получить свойства типа double (баланс, средства (equity), маржа и т. д.) | `AccountInfoDoublePropertyType` (14 значений): ACCOUNT_BALANCE, ACCOUNT_CREDIT, ACCOUNT_PROFIT, ACCOUNT_EQUITY, ACCOUNT_MARGIN, ACCOUNT_MARGIN_FREE, ACCOUNT_MARGIN_LEVEL, ACCOUNT_MARGIN_SO_CALL, ACCOUNT_MARGIN_SO_SO, ACCOUNT_MARGIN_INITIAL, ACCOUNT_MARGIN_MAINTENANCE, ACCOUNT_ASSETS, ACCOUNT_LIABILITIES, ACCOUNT_COMMISSION_BLOCKED | - |
| **account_info_integer** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (11 значений) | Получить свойства типа integer (логин, кредитное плечо и т. д.) | `AccountInfoIntegerPropertyType` (11 значений): ACCOUNT_LOGIN, ACCOUNT_TRADE_MODE, ACCOUNT_LEVERAGE, ACCOUNT_LIMIT_ORDERS, ACCOUNT_MARGIN_SO_MODE, ACCOUNT_TRADE_ALLOWED, ACCOUNT_TRADE_EXPERT, ACCOUNT_MARGIN_MODE, ACCOUNT_CURRENCY_DIGITS, ACCOUNT_FIFO_CLOSE, ACCOUNT_HEDGE_ALLOWED | - |
| **account_info_string** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (4 значения) | Получить свойства типа string (валюта, компания и т. д.) | `AccountInfoStringPropertyType` (4 значения): ACCOUNT_NAME, ACCOUNT_SERVER, ACCOUNT_CURRENCY, ACCOUNT_COMPANY | - |

---

## 📊 2. Информация о символе (13 методов)

### 7/13 методов используют ENUM (54%)

| Метод | Количество ENUM | Описание | Входные ENUM | Выходные ENUM |
|--------|-------------|-------------|-------------|--------------|
| **symbols_total** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Подсчитать общее/выбранное число символов | - | - |
| **symbol_exist** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Проверить существование символа | - | - |
| **symbol_name** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Получить имя символа по индексу | - | - |
| **symbol_select** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Добавить/удалить символ из Market Watch | - | - |
| **symbol_is_synchronized** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Проверить статус синхронизации с сервером | - | - |
| **symbol_info_double** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (60 значений) | Получить свойства типа double (Bid, Ask, Point и т. д.) | `SymbolInfoDoubleProperty` (60 значений) — селектор свойства | - |
| **symbol_info_integer** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (37 значений) | Получить свойства типа integer (Digits, спред и т. д.) | `SymbolInfoIntegerProperty` (37 значений) — селектор свойства | - |
| **symbol_info_string** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (15 значений) | Получить свойства типа string (описание и т. д.) | `SymbolInfoStringProperty` (15 значений) — селектор свойства | - |
| **symbol_info_margin_rate** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (9 значений) | Получить требования к марже для типов ордеров | `ENUM_ORDER_TYPE` (9 значений) — тип ордера | - |
| **symbol_info_tick** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Получить данные последнего тика с временной меткой | - | - |
| **symbol_info_session_quote** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (7 значений) | Получить время сессий котировок | `BMT5_ENUM_DAY_OF_WEEK` (7 значений) — день недели | - |
| **symbol_info_session_trade** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (7 значений) | Получить время торговых сессий | `BMT5_ENUM_DAY_OF_WEEK` (7 значений) — день недели | - |
| **symbol_params_many** | **[In: 1, Out: 13]**<br>Всего: 14 ENUM | Получить подробные параметры для нескольких символов | `AH_SYMBOL_PARAMS_MANY_SORT_TYPE` (4 значения) — режим сортировки | **13 ENUM в SymbolParameters:** BMT5_ENUM_SYMBOL_SECTOR, BMT5_ENUM_SYMBOL_INDUSTRY, BMT5_ENUM_SYMBOL_CHART_MODE, BMT5_ENUM_SYMBOL_CALC_MODE, BMT5_ENUM_SYMBOL_TRADE_MODE, BMT5_ENUM_SYMBOL_TRADE_EXECUTION, BMT5_ENUM_SYMBOL_SWAP_MODE, BMT5_ENUM_DAY_OF_WEEK, BMT5_ENUM_ORDER_TYPE_FILLING, BMT5_ENUM_ORDER_TYPE, BMT5_ENUM_SYMBOL_ORDER_GTC_MODE, BMT5_ENUM_SYMBOL_OPTION_MODE, BMT5_ENUM_SYMBOL_OPTION_RIGHT |

---

## 📋 3. Информация о позициях и ордерах (6 методов)

### 3/6 методов используют ENUM (50%)

| Метод | Количество ENUM | Описание | Входные ENUM | Выходные ENUM |
|--------|-------------|-------------|-------------|--------------|
| **positions_total** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Подсчитать открытые позиции | - | - |
| **opened_orders** | **[In: 1, Out: 6]**<br>Всего: 7 ENUM | Получить все открытые ордера и позиции | `BMT5_ENUM_OPENED_ORDER_SORT_TYPE` (4 значения) — режим сортировки | **6 ENUM:**<br>**В PositionInfo:** BMT5_ENUM_POSITION_TYPE, BMT5_ENUM_POSITION_REASON<br>**В OpenedOrderInfo:** BMT5_ENUM_ORDER_TYPE, BMT5_ENUM_ORDER_STATE, BMT5_ENUM_ORDER_TYPE_FILLING, BMT5_ENUM_ORDER_TYPE_TIME |
| **opened_orders_tickets** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Получить только номера тикетов (облегчённый) | - | - |
| **order_history** | **[In: 1, Out: 7]**<br>Всего: 8 ENUM | Получить исторические ордера с постраничной разбивкой | `BMT5_ENUM_ORDER_HISTORY_SORT_TYPE` (6 значений) — режим сортировки | **7 ENUM:**<br>**В OrderHistoryData:** BMT5_ENUM_ORDER_STATE, BMT5_ENUM_ORDER_TYPE, BMT5_ENUM_ORDER_TYPE_FILLING, BMT5_ENUM_ORDER_TYPE_TIME<br>**В DealHistoryData:** BMT5_ENUM_DEAL_ENTRY_TYPE, BMT5_ENUM_DEAL_TYPE, BMT5_ENUM_DEAL_REASON |
| **positions_history** | **[In: 1, Out: 1]**<br>Всего: 2 ENUM | Получить исторические позиции с P&L | `AH_ENUM_POSITIONS_HISTORY_SORT_TYPE` (4 значения) — режим сортировки | `AH_ENUM_POSITIONS_HISTORY_ORDER_TYPE` (9 значений) — тип ордера |
| **tick_value_with_size** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Получить стоимость и размер тика для символов | - | - |

---

## 📚 4. Глубина рынка / DOM (3 метода)

### 1/3 методов используют ENUM (33%)

| Метод | Количество ENUM | Описание | Входные ENUM | Выходные ENUM |
|--------|-------------|-------------|-------------|--------------|
| **market_book_add** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Подписаться на обновления глубины рынка | - | - |
| **market_book_release** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Отписаться от DOM | - | - |
| **market_book_get** | **[In: 0, Out: 1]**<br>Всего: 1 ENUM (4 значения) | Получить текущий снимок глубины рынка | - | `BookType` (4 значения) — тип ордера в книге: BOOK_TYPE_SELL, BOOK_TYPE_BUY, BOOK_TYPE_SELL_MARKET, BOOK_TYPE_BUY_MARKET |

---

## 💰 5. Торговые операции (6 методов)

### 6/6 методов используют ENUM (100%)

| Метод | Количество ENUM | Описание | Входные ENUM | Выходные ENUM |
|--------|-------------|-------------|-------------|--------------|
| **order_send** | **[In: 2, Out: 0]**<br>Всего: 2 ENUM (13 значений) | Отправить рыночный или отложенный ордер | **2 ENUM:**<br>`TMT5_ENUM_ORDER_TYPE` (9 значений) — тип ордера<br>`TMT5_ENUM_ORDER_TYPE_TIME` (4 значения) — время жизни ордера | - |
| **order_modify** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (4 значения) | Изменить параметры существующего ордера | `TMT5_ENUM_ORDER_TYPE_TIME` (4 значения) — время жизни ордера | - |
| **order_close** | **[In: 0, Out: 1]**<br>Всего: 1 ENUM (3 значения) | Закрыть рыночный или отложенный ордер | - | `MRPC_ORDER_CLOSE_MODE` (3 значения): MRPC_MARKET_ORDER_CLOSE, MRPC_MARKET_ORDER_PARTIAL_CLOSE, MRPC_PENDING_ORDER_REMOVE |
| **order_check** | **[In: 4, Out: 0]**<br>Всего: 4 ENUM (23 значения) | Проверить ордер перед отправкой | **4 ENUM в MrpcMqlTradeRequest:**<br>`MRPC_ENUM_TRADE_REQUEST_ACTIONS` (6 значений) — тип торгового действия<br>`ENUM_ORDER_TYPE_TF` (9 значений) — тип ордера<br>`MRPC_ENUM_ORDER_TYPE_FILLING` (4 значения) — политика заполнения ордера<br>`MRPC_ENUM_ORDER_TYPE_TIME` (4 значения) — время жизни ордера | - |
| **order_calc_margin** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (9 значений) | Рассчитать требуемую маржу | `ENUM_ORDER_TYPE_TF` (9 значений) — тип ордера | - |
| **order_calc_profit** | **[In: 1, Out: 0]**<br>Всего: 1 ENUM (9 значений) | Рассчитать потенциальную прибыль/убыток | `ENUM_ORDER_TYPE_TF` (9 значений) — тип ордера | - |

---

## 📡 6. Методы стриминга (5 методов)

### 3/5 методов используют ENUM (60%)

| Метод | Количество ENUM | Описание | Входные ENUM | Выходные ENUM |
|--------|-------------|-------------|-------------|--------------|
| **on_symbol_tick** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Стриминг данных тиков (обновления Bid/Ask) | - | - |
| **on_trade** | **[In: 0, Out: 1]**<br>Всего: 11 ENUM (75 значений) | Стриминг торговых событий | - | **1 прямой + 10 во вложенных структурах:**<br>1. `MT5_SUB_ENUM_EVENT_GROUP_TYPE` (2 значения) — OnTradeData.type<br>2-11. **Во вложенных структурах event_data:** SUB_ENUM_POSITION_TYPE (2), SUB_ENUM_POSITION_REASON (4), SUB_ENUM_ORDER_TYPE (9), SUB_ENUM_ORDER_STATE (10), SUB_ENUM_DEAL_TYPE (18), SUB_ENUM_ORDER_TYPE_TIME (4), SUB_ENUM_ORDER_TYPE_FILLING (4), SUB_ENUM_ORDER_REASON (7), SUB_ENUM_DEAL_ENTRY (4), SUB_ENUM_DEAL_REASON (11) |
| **on_position_profit** | **[In: 0, Out: 1]**<br>Всего: 1 ENUM (2 значения) | Стриминг обновлений P&L позиций | - | `MT5_SUB_ENUM_EVENT_GROUP_TYPE` (2 значения) — тип события в поле OnPositionProfitData.type |
| **on_positions_and_pending_orders_tickets** | **[In: 0, Out: 0]**<br>Всего: 0 ENUM | Стриминг изменений тикетов | - | - |
| **on_trade_transaction** | **[In: 0, Out: 9]**<br>Всего: 9 ENUM (107 значений) | Стриминг событий торговых транзакций | - | **11 полей ENUM из 9 уникальных типов:**<br>1. `MT5_SUB_ENUM_EVENT_GROUP_TYPE` (2 значения) — OnTradeTransactionData.type<br>2-6. **В MqlTradeTransaction:** SUB_ENUM_TRADE_TRANSACTION_TYPE (11 значений), SUB_ENUM_ORDER_TYPE (9 значений), SUB_ENUM_ORDER_STATE (10 значений), SUB_ENUM_DEAL_TYPE (18 значений), SUB_ENUM_ORDER_TYPE_TIME (4 значения)<br>7-10. **В MqlTradeRequest:** SUB_ENUM_TRADE_REQUEST_ACTIONS (7 значений), SUB_ENUM_ORDER_TYPE (9 значений), SUB_ENUM_ORDER_TYPE_FILLING (4 значения), SUB_ENUM_ORDER_TYPE_TIME (4 значения)<br>11. **В MqlTradeResult:** MqlErrorTradeCode (42 значения) |

---

## Важные примечания

### Доступ к ENUM в Python

Python обращается к ENUM через модули protobuf:

**Правильно:**
```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

# Использование ENUM
property_id = account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
```

**Неправильно:**
```python
ACCOUNT_BALANCE  # NameError: name 'ACCOUNT_BALANCE' is not defined
```

### Особые случаи

**1. AccountInfoInteger и SymbolInfoInteger:**

- Некоторые свойства возвращают значения, которые **представляют ENUM**, но возвращаются как `int64`

- Это **НЕ типизированные ENUM**, а просто числа!

**2. ReturnedCode:**

- Поле ReturnedCode в торговых операциях **НЕ является ENUM**

- Это обычный код возврата операции типа uint32

---

## См. также

- [MT5Account — Главный обзор](../MT5Account/MT5Account.Master.Overview.md) — все низкоуровневые методы, сгруппированные (счёт, символ, позиции и ордера, глубина рынка, торговля, стриминг).
- [Справочник кодов возврата](RETURN_CODES_REFERENCE.md) — коды возврата сделок (не enum).
- [Глоссарий → Enums](GLOSSARY.md) — как обращаться к enum из модулей protobuf.
