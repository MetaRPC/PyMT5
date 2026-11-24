# Protobuf Inspector — интерактивный обозреватель типов

> **Интерактивная утилита для разработчика, позволяющая исследовать типы protobuf MT5, поля, перечисления (enum) и структуры данных из gRPC API MT5**

---

## 🏛️ Что делает этот инструмент

Protobuf Inspector — это **интерактивный инструмент командной строки**, который помогает исследовать структуру gRPC API MT5:

- Интерактивный поиск типов, полей и перечислений
- Инспекция структур protobuf-сообщений в реальном времени
- Обнаружение на уровне полей — найти, какие типы содержат определённые поля
- Обнаружение по типу поля — найти поля по их типу данных (double, string, enum и т. д.)
- Исследование значений enum — увидеть все возможные значения enum
- Отслеживание использования enum — найти, где используется конкретный enum
- Просмотр типов с фильтрами — вывести типы по категориям
- Экспорт в JSON — экспортировать структуры типов для документации
- Статистический анализ — типы полей, количество enum, исчерпывающие метрики

!!! note "Числа в этом руководстве — это живой снимок"
    Приведённые ниже значения и примеры вывода были сняты с текущего protobuf-пакета `MetaRpcMT5`. Они **растут по мере развития API**, поэтому ваш запуск может показать другие итоги — запускайте `stats` и команды самостоятельно для актуальных значений. Команды и порядок работы остаются прежними.

---

## 🏁 Начало работы

### Запуск инспектора

```bash
cd examples
python main.py inspect
```

Вы увидите интерактивное приглашение:

```
===========================================================
MT5 PROTOBUF TYPES INSPECTOR
===========================================================

  Discovered 216 protobuf message types
  Discovered 60 enum types

  Type 'help' to see available commands
  Type 'list' to see all types
===========================================================

>
```

---

## 🧰 Доступные команды

| Команда | Описание | Пример |
|---------|-------------|---------|
| `list` или `ls` | Показать все доступные типы protobuf | `list` |
| `list --request` | Показать только типы Request | `list --request` |
| `list --reply` | Показать только типы Reply | `list --reply` |
| `list --data` | Показать только типы Data | `list --data` |
| `list --info` | Показать только типы Info | `list --info` |
| `<TypeName>` | Исследовать структуру конкретного типа | `PositionInfo` |
| `search <text>` или `find <text>` | Искать типы, содержащие текст | `search Order` |
| `field <name>` | Найти все типы с определённым полем | `field ticket` |
| `findtype <type>` | Найти все поля определённого типа | `findtype double` |
| `enum <name>` | Показать все значения enum | `enum ENUM_ORDER_TYPE_TF` |
| `whereenum <name>` | Найти, где используется enum | `whereenum ENUM_ORDER_TYPE_TF` |
| `export <TypeName>` | Экспортировать структуру типа в JSON | `export PositionInfo` |
| `stats` | Показать подробную статистику | `stats` |
| `help` или `?` | Показать справочное сообщение | `help` |
| `exit` или `quit` | Выйти из инспектора | `exit` |

---

## Практические примеры

### Пример 1: узнать, какие поля есть у PositionInfo

**Команда:**
```
> PositionInfo
```

**Вывод:**
```
===========================================================
TYPE: PositionInfo
===========================================================
FIELDS (20):
-----------------------------------------------------------
  #  1 index                          : uint32
  #  2 ticket                         : uint64
  #  3 open_time                      : Timestamp
  #  4 volume                         : double
  #  5 price_open                     : double
  #  6 stop_loss                      : double
  #  7 take_profit                    : double
  #  8 price_current                  : double
  #  9 swap                           : double
  # 10 profit                         : double
  # 11 last_update_time               : Timestamp
  # 12 type                           : BMT5_ENUM_POSITION_TYPE
  # 13 magic_number                   : int64
  # 14 identifier                     : int64
  # 15 reason                         : BMT5_ENUM_POSITION_REASON
  # 16 symbol                         : string
  # 17 comment                        : string
  # 18 external_id                    : string
  # 19 position_commission            : double
  # 20 account_login                  : int64
```

---

### Пример 2: найти, какие типы имеют поле «ticket»

**Команда:**
```
> field ticket
```

**Вывод:**
```
EXACT MATCH: field 'ticket' found in:
-----------------------------------------------------------
    1. DealHistoryData
    2. HistoryOrderInfo
    3. OnPositionProfitPositionInfo
    4. OnTradeHistoryDealInfo
    5. OnTradeHistoryOrderInfo
    6. OnTradeOrderInfo
    7. OnTradePositionInfo
    8. OpenedOrderInfo
    9. OrderCloseRequest
   10. OrderHistoryData
   11. OrderModifyRequest
   12. PositionInfo

PARTIAL MATCHES (field contains 'ticket'):
-----------------------------------------------------------
    1. MqlTradeRequest
    2. MqlTradeResult
    3. MqlTradeTransaction
    4. OnPositionsAndPendingOrdersTicketsData
    5. OpenedOrdersTicketsData
    6. PositionHistoryInfo
```

---

### Пример 3: увидеть все значения enum ORDER_TYPE

**Команда:**
```
> enum ENUM_ORDER_TYPE_TF
```

**Вывод:**
```
ENUM: ENUM_ORDER_TYPE_TF
===========================================================
  ORDER_TYPE_TF_BUY                        = 0
  ORDER_TYPE_TF_SELL                       = 1
  ORDER_TYPE_TF_BUY_LIMIT                  = 2
  ORDER_TYPE_TF_SELL_LIMIT                 = 3
  ORDER_TYPE_TF_BUY_STOP                   = 4
  ORDER_TYPE_TF_SELL_STOP                  = 5
  ORDER_TYPE_TF_BUY_STOP_LIMIT             = 6
  ORDER_TYPE_TF_SELL_STOP_LIMIT            = 7
  ORDER_TYPE_TF_CLOSE_BY                   = 8
```

---

### Пример 3a: увидеть enum ORDER_TYPE для событий стриминга

**Команда:**
```
> enum SUB_ENUM_ORDER_TYPE
```

**Вывод:**
```
ENUM: SUB_ENUM_ORDER_TYPE
===========================================================
  SUB_ORDER_TYPE_BUY                       = 0
  SUB_ORDER_TYPE_SELL                      = 1
  SUB_ORDER_TYPE_BUY_LIMIT                 = 2
  SUB_ORDER_TYPE_SELL_LIMIT                = 3
  SUB_ORDER_TYPE_BUY_STOP                  = 4
  SUB_ORDER_TYPE_SELL_STOP                 = 5
  SUB_ORDER_TYPE_BUY_STOP_LIMIT            = 6
  SUB_ORDER_TYPE_SELL_STOP_LIMIT           = 7
  SUB_ORDER_TYPE_CLOSE_BY                  = 8
```

**Примечание:** используйте enum `SUB_ENUM_*` для событий стриминга (on_trade, on_trade_transaction и т. д.) и enum `ENUM_*_TF` для торговых функций (order_send, order_modify и т. д.).

---

### Пример 4: найти все типы, связанные с «Position»

**Команда:**
```
> search Position
```

**Вывод:**
```
FOUND 16 TYPES MATCHING 'Position':
-----------------------------------------------------------
    1. OnPositionProfitData
    2. OnPositionProfitPositionInfo
    3. OnPositionProfitReply
    4. OnPositionProfitRequest
    5. OnPositionsAndPendingOrdersTicketsData
    6. OnPositionsAndPendingOrdersTicketsReply
    7. OnPositionsAndPendingOrdersTicketsRequest
    8. OnTradePositionInfo
    9. OnTradePositionUpdate
   10. PositionHistoryInfo
   11. PositionInfo
   12. PositionsHistoryData
   13. PositionsHistoryReply
   14. PositionsHistoryRequest
   15. PositionsTotalData
   16. PositionsTotalReply
```

---

### Пример 5: показать все доступные типы

**Команда:**
```
> list
```

**Вывод:**
```
AVAILABLE PROTOBUF TYPES (216)
-----------------------------------------------------------

[Request] (64 types):
    1. AccountInfoDoubleRequest
    2. AccountInfoIntegerRequest
    3. AccountInfoStringRequest
    ...

[Reply] (60 types):
    1. AccountInfoDoubleReply
    2. AccountInfoIntegerReply
    ...

[Data] (61 types):
    1. AccountInfoDoubleData
    2. AccountSummaryData
    3. AllHistoryOrdersData
    ...

[Info] (12 types):
    1. HistoryOrderInfo
    2. MrpcMqlBookInfo
    3. OnEventAccountInfo
    4. OnPositionProfitPositionInfo
    5. OnTradeHistoryDealInfo
    ...

[Other] (19 types):
    1. ConnectStreamEvent
    2. EaLogRow
    3. MqlTradeResult
    ...
```

---

### Пример 6: найти все поля типа double

**Команда:**
```
> findtype double
```

**Вывод:**
```
FIELDS OF TYPE 'double' (228 fields):
===========================================================

  AccountInfoDoubleData:
    - requested_value

  AccountSummaryData:
    - account_balance
    - account_credit
    - account_equity

  DealHistoryData:
    - commission
    - fee
    - price
    - profit
    - stop_loss
    - swap
    - take_profit
    - volume

  PositionInfo:
    - position_commission
    - price_current
    - price_open
    - profit
    - stop_loss
    - swap
    - take_profit
    - volume

  ... (and more)
```

---

### Пример 7: найти, где используется enum

**Команда:**
```
> whereenum ENUM_ORDER_TYPE_TF
```

**Вывод:**
```
ENUM 'ENUM_ORDER_TYPE_TF' USED IN (3 fields):
===========================================================

  MrpcMqlTradeRequest:
    - order_type

  OrderCalcMarginRequest:
    - order_type

  OrderCalcProfitRequest:
    - order_type
```

---

### Пример 8: экспортировать тип в JSON

**Команда:**
```
> export PositionInfo
```

**Вывод:**
```
TYPE: PositionInfo (JSON export)
===========================================================
{
  "type_name": "PositionInfo",
  "full_name": "mt5_term_api.PositionInfo",
  "fields": [
    {
      "number": 1,
      "name": "index",
      "type": "uint32",
      "label": "optional"
    },
    {
      "number": 2,
      "name": "ticket",
      "type": "uint64",
      "label": "optional"
    },
    {
      "number": 12,
      "name": "type",
      "type": "BMT5_ENUM_POSITION_TYPE",
      "label": "optional",
      "enum_name": "BMT5_ENUM_POSITION_TYPE",
      "enum_values": {
        "BMT5_POSITION_TYPE_BUY": 0,
        "BMT5_POSITION_TYPE_SELL": 1
      }
    },
    ...
  ]
}
```

---

### Пример 9: показать статистику

**Команда:**
```
> stats
```

**Вывод:**
```
PROTOBUF INSPECTOR STATISTICS
===========================================================

Message Types: 216 total
-----------------------------------------------------------
  Request         :  64 types
  Reply           :  60 types
  Data            :  61 types
  Info            :  12 types
  Other           :  19 types

Enum Types: 60 total
-----------------------------------------------------------
  Total enum values  : 644

  Top 5 largest enums:
    BMT5_ENUM_SYMBOL_INDUSTRY                : 152 values
    SymbolInfoDoubleProperty                 :  60 values
    SymbolInfoIntegerProperty                :  37 values
    EnumOpenTerminalChartWithEaChatPeriod    :  22 values
    BMT5_ENUM_DEAL_TYPE                      :  18 values

Field Types: 167 distinct types
-----------------------------------------------------------
  Top 10 most common field types:
    double               : 228 fields
    string               : 167 fields
    int64                :  66 fields
    error                :  62 fields
    int32                :  53 fields
    timestamp            :  49 fields
    uint64               :  43 fields
    bool                 :  36 fields
    uint32               :  24 fields
    bmt5_enum_order_type :   4 fields

Total Fields: 945
===========================================================
```

---

### Пример 10: вывести только типы Request

**Команда:**
```
> list --request
```

**Вывод:**
```
REQUEST TYPES
-----------------------------------------------------------

[Request] (64 types):
    1. AccountInfoDoubleRequest
    2. AccountInfoIntegerRequest
    3. AccountInfoStringRequest
    4. AccountSummaryRequest
    5. AllHistoryOrdersRequest
    6. AttachEaRequest
    7. CheckConnectRequest
    8. ConnectByTokenRequest
    9. ConnectExRequest
   10. ConnectRequest
   11. MarketBookAddRequest
   12. MarketBookGetRequest
   13. OpenedOrdersRequest
   14. OrderCalcMarginRequest
   15. OrderCalcProfitRequest
   16. OrderCheckRequest
   17. OrderCloseRequest
   18. OrderModifyRequest
   19. OrderSendRequest
   20. SymbolInfoDoubleRequest
    ... (and more)
```

---

## 📦 Распространённые сценарии использования

### СЦЕНАРИЙ 1: «Получаю ошибку "field not found"»

**Проблема:** ваш код читает `position.balance`, но это не работает

**Решение:**
```
> field balance
```

**Результат:** показывает, какие типы действительно содержат поле balance
```
EXACT MATCH: field 'balance' found in:
-----------------------------------------------------------
    1. OnEventAccountInfo

PARTIAL MATCHES (field contains 'balance'):
-----------------------------------------------------------
    1. AccountSummaryData
    2. MrpcMqlTradeCheckResult
```

**Исправление:** баланс находится на счёте, а не на позиции — читайте `AccountSummaryData.account_balance` (через `MT5Service.get_account_summary()` или `MT5Sugar.balance`).

---

### СЦЕНАРИЙ 2: «Какие поля есть у X?»

**Проблема:** не знаете, какие данные находятся в `PositionInfo`

**Решение:**
```
> PositionInfo
```

**Результат:** показывает все 20 полей (ticket, type, symbol, profit и т. д.)

---

### СЦЕНАРИЙ 3: «Какие допустимые значения enum?»

**Проблема:** не знаете, какое значение использовать для `order_type`

**Решение:**
```
> enum ENUM_ORDER_TYPE_TF
```

**Результат:** показывает все значения:
```
ORDER_TYPE_TF_BUY = 0
ORDER_TYPE_TF_SELL = 1
ORDER_TYPE_TF_BUY_LIMIT = 2
ORDER_TYPE_TF_SELL_LIMIT = 3
...
```

---

### СЦЕНАРИЙ 4: «Нужно найти типы, связанные с позицией»

**Проблема:** исследуете API, нужно увидеть все структуры, связанные с позицией

**Решение:**
```
> search Position
```

**Результат:** показывает все 16 типов со словом «Position» в имени

---

### СЦЕНАРИЙ 5: «Хочу посмотреть, что доступно»

**Проблема:** новичок в API, хотите изучить его

**Решение:**
```
> list
```

**Результат:** показывает все доступные типы, сгруппированные по категориям

---

### СЦЕНАРИЙ 6: «Нужны все поля с ценами»

**Проблема:** хотите найти все поля API, связанные с ценами

**Решение:**
```
> findtype double
```

**Результат:** показывает все поля типа double (цены, объёмы, прибыль и т. д.), сгруппированные по типу

---

### СЦЕНАРИЙ 7: «Где используется этот enum?»

**Проблема:** есть enum, нужно узнать, какие типы его используют

**Решение:**
```
> whereenum ENUM_ORDER_TYPE_TF
```

**Результат:** показывает все типы и поля, которые используют этот enum

---

### СЦЕНАРИЙ 8: «Сгенерировать документацию»

**Проблема:** нужно задокументировать структуру типа для команды или внешних инструментов

**Решение:**
```
> export PositionInfo
```

**Результат:** получаете полную JSON-структуру с номерами полей, типами и значениями enum

---

## ℹ️ Статистика

Когда вы запускаете инспектор, он обеспечивает полное покрытие текущего protobuf-пакета:

- **Всего типов сообщений:** 216 (все типы protobuf-сообщений gRPC MT5)
- **Всего enum:** 60 (с 644 значениями enum)
- **Всего полей:** 945 (по всем типам)
- **Типов полей:** 167 различных типов protobuf
- **Покрытие:** 100% просканированных модулей gRPC MT5

---

## Важные enum (часто используемые)

| Имя enum | Описание | Распространённые значения |
|-----------|-------------|---------------|
| `ENUM_ORDER_TYPE_TF` | Типы ордеров (торговые функции) | BUY, SELL, BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP (9 значений) |
| `TMT5_ENUM_ORDER_TYPE` | Типы ордеров (order_send) | TMT5_ORDER_TYPE_BUY, …_SELL, …_BUY_LIMIT и т. д. (9 значений) |
| `SUB_ENUM_ORDER_TYPE` | Типы ордеров (события стриминга) | SUB_ORDER_TYPE_BUY, SUB_ORDER_TYPE_SELL и т. д. (9 значений) |
| `BMT5_ENUM_POSITION_TYPE` | Направление позиции | BMT5_POSITION_TYPE_BUY, …_SELL (2 значения) |
| `BMT5_ENUM_ORDER_STATE` | Состояния ордера | STARTED, PLACED, CANCELED, PARTIAL, FILLED, REJECTED (10 значений) |
| `SUB_ENUM_DEAL_TYPE` | Типы сделок (стриминг) | SUB_DEAL_TYPE_BUY, SUB_DEAL_TYPE_SELL и т. д. (18 значений) |
| `BMT5_ENUM_DEAL_REASON` | Причина исполнения сделки | Client, Expert, SL, TP, Mobile (11 значений) |
| `BMT5_ENUM_POSITION_REASON` | Почему позиция открыта | Client, Mobile, Web, Expert, SL, TP, SO (7 значений) |
| `SymbolInfoDoubleProperty` | Ценовые свойства символа | BID, ASK, POINT, SWAP_LONG, SWAP_SHORT (60 значений) |
| `SymbolInfoIntegerProperty` | Целочисленные свойства символа | DIGITS, SPREAD, TRADE_MODE и т. д. (37 значений) |
| `AccountInfoDoublePropertyType` | Свойства счёта типа double | BALANCE, EQUITY, MARGIN и т. д. (14 значений) |

**Примечание:** префиксы в именах enum указывают на контекст их использования:

- `TMT5_*` / `ENUM_*_TF` — enum торговых функций (order_send, order_calc_*)
- `BMT5_*` — базовые enum MT5 (позиции, ордера, исторические данные, причины)
- `SUB_*` — enum подписок/стриминга (события в реальном времени)

---

## Возможности

| Возможность | Описание |
|---------|-------------|
| **Поиск без учёта регистра** | `search Order` = `search order` |
| **Частичное совпадение по полю** | `field profit` находит и `profit`, и `take_profit` |
| **Категоризация типов** | Показывает теги `[Request]`, `[Reply]`, `[Data]`, `[Info]` |
| **Фильтрация по категориям** | `list --request`, `list --reply` и т. д. |
| **Поиск по типу поля** | `findtype double` находит все поля типа double |
| **Отслеживание использования enum** | `whereenum <name>` показывает, где используется enum |
| **Экспорт в JSON** | `export <TypeName>` выводит структурированный JSON |
| **Подробная статистика** | `stats` показывает исчерпывающие метрики |
| **Индикаторы массивов** | суффикс `[]` для повторяемых/массивных полей |
| **Номера полей protobuf** | Показывает `#N` для каждого поля |
| **Умные сообщения об ошибках** | Предлагает альтернативы, когда тип не найден |

---

## Пример интерактивной сессии

```bash
$ cd examples
$ python main.py inspect

===========================================================
MT5 PROTOBUF TYPES INSPECTOR
===========================================================

> search Order
FOUND 40 TYPES MATCHING 'Order':
-----------------------------------------------------------
    1. AllHistoryOrdersData
    2. HistoryOrderInfo
    3. OnTradeOrderInfo
    4. OpenedOrderInfo
    5. OpenedOrdersData
    6. OrderCalcMarginRequest
    7. OrderCheckRequest
    8. OrderCloseRequest
    9. OrderModifyRequest
   10. OrderSendRequest
   ...

> OpenedOrderInfo
===========================================================
TYPE: OpenedOrderInfo
===========================================================
FIELDS (24):
-----------------------------------------------------------
  #  1 index                          : uint32
  #  2 ticket                         : uint64
  #  3 price_current                  : double
  #  4 price_open                     : double
  #  5 stop_limit                     : double
  #  6 stop_loss                      : double
  #  7 take_profit                    : double
  #  8 volume_current                 : double
  #  9 volume_initial                 : double
  # 10 magic_number                   : int64
  # 11 reason                         : int32
  # 12 type                           : BMT5_ENUM_ORDER_TYPE
  # 13 state                          : BMT5_ENUM_ORDER_STATE
  # 14 time_expiration                : Timestamp
  # 15 time_setup                     : Timestamp
  # 16 time_done                      : Timestamp
  # 17 type_filling                   : BMT5_ENUM_ORDER_TYPE_FILLING
  # 18 type_time                      : BMT5_ENUM_ORDER_TYPE_TIME
  # 19 position_id                    : int64
  # 20 position_by_id                 : int64
  # 21 symbol                         : string
  # 22 external_id                    : string
  # 23 comment                        : string
  # 24 account_login                  : int64

> field magic
EXACT MATCH: field 'magic' found in:
-----------------------------------------------------------
    1. HistoryOrderInfo
    2. MqlTradeRequest
    3. OnTradeHistoryDealInfo
    4. OnTradeHistoryOrderInfo
    5. OnTradeOrderInfo
    6. OnTradePositionInfo
    7. PositionHistoryInfo

PARTIAL MATCHES (field contains 'magic'):
-----------------------------------------------------------
    1. MrpcMqlTradeRequest
    2. OpenedOrderInfo
    3. OrderHistoryData
    4. PositionInfo

> enum BMT5_ENUM_ORDER_STATE
===========================================================
ENUM: BMT5_ENUM_ORDER_STATE
===========================================================
  BMT5_ORDER_STATE_STARTED                 = 0
  BMT5_ORDER_STATE_PLACED                  = 1
  BMT5_ORDER_STATE_CANCELED                = 2
  BMT5_ORDER_STATE_PARTIAL                 = 3
  BMT5_ORDER_STATE_FILLED                  = 4
  BMT5_ORDER_STATE_REJECTED                = 5
  BMT5_ORDER_STATE_EXPIRED                 = 6
  BMT5_ORDER_STATE_REQUEST_ADD             = 7
  BMT5_ORDER_STATE_REQUEST_MODIFY          = 8
  BMT5_ORDER_STATE_REQUEST_CANCEL          = 9

> whereenum ENUM_ORDER_TYPE_TF
ENUM 'ENUM_ORDER_TYPE_TF' USED IN (3 fields):
===========================================================

  MrpcMqlTradeRequest:
    - order_type

  OrderCalcMarginRequest:
    - order_type

  OrderCalcProfitRequest:
    - order_type

> exit

[+] Goodbye!
```

---

## Детали реализации

Protobuf Inspector использует рефлексию Python, чтобы:

1. Зарегистрировать все типы protobuf при запуске
2. Построить индексы в памяти для:
   - Сопоставления имён полей → типам
   - Сопоставления типов полей → полям
   - Сопоставления имён enum → их использованию
3. Обеспечить мгновенный поиск и выборку
4. Форматировать вывод со структурой и ясностью
5. Экспортировать в JSON с полными метаданными

**Исходный файл:** `examples/0_common/16_protobuf_inspector.py`

**Просканированные модули:**

- `mt5_term_api_account_helper_pb2`
- `mt5_term_api_account_information_pb2`
- `mt5_term_api_market_info_pb2`
- `mt5_term_api_trade_functions_pb2`
- `mt5_term_api_trading_helper_pb2`
- `mt5_term_api_subscriptions_pb2` (события стриминга, enum SUB_ENUM_*)
- `mt5_term_api_connection_pb2` (управление подключением)

---

## Технические примечания

- **Подключение к MT5 не требуется** — это полностью офлайн-инструмент, который инспектирует определения типов
- **Полное покрытие** — все типы и enum из просканированных модулей gRPC MT5
- **Мгновенный поиск** — индексы в памяти для быстрой выборки
- **Только для разработки** — не предназначен для использования в продакшене
- **Рефлексия Python** — использует API protobuf DESCRIPTOR для интроспекции
- **Экспорт в JSON** — совместим с внешними инструментами документации

---

## Когда использовать этот инструмент

**Используйте инспектор, когда:**

- Изучаете структуру gRPC API MT5
- Отлаживаете ошибки «field not found»
- Исследуете доступные типы protobuf
- Ищете значения enum
- Находите правильные типы запроса/ответа для вызовов API
- Разбираетесь в структурах сообщений перед написанием кода
- Выявляете все поля определённого типа (например, все поля double)
- Отслеживаете использование enum по всему API
- Генерируете документацию для типов
- Анализируете статистику API

**Не используйте для:**

- Инспекции данных во время выполнения (используйте отладчик)
- Продакшен-кода (это инструмент для разработки)
- Проверки связи с API (используйте демо-подключения)

---

## Советы и хитрости

1. **Начинайте с поиска** — если знаете общую область, сначала используйте `search <keyword>`
2. **Используйте поиск по полю** — когда видите имя поля, но не знаете тип, используйте `field <name>`
3. **Изучайте enum заранее** — понимание значений enum экономит время на отладку позже
4. **list — ваш друг** — когда зашли в тупик, используйте `list`, чтобы просмотреть доступные типы
5. **Регистр не важен** — набирайте команды строчными буквами, так быстрее
6. **Используйте фильтры** — `list --request` показывает только то, что нужно
7. **Поиск по типу** — `findtype double`, чтобы увидеть все поля цен/объёмов
8. **Отслеживайте использование enum** — `whereenum` показывает связи между типами
9. **Экспорт для документации** — используйте `export`, чтобы сгенерировать JSON для документации команды
10. **Проверяйте статистику** — используйте `stats`, чтобы получить обзор структуры API

---

## Порядок работы для быстрого старта

**Порядок работы для новичка при исследовании API:**

```bash
# 1. Запускаем инспектор
cd examples
python main.py inspect

# 2. Смотрим, что доступно
> list

# 3. Ищем то, что нужно
> search Position

# 4. Исследуем тип
> PositionInfo

# 5. Проверяем значения enum
> enum ENUM_ORDER_TYPE_TF

# 6. Находим связанные типы
> field ticket

# 7. Находим поля по типу
> findtype double

# 8. Проверяем использование enum
> whereenum ENUM_ORDER_TYPE_TF

# 9. Получаем подробную статистику
> stats

# 10. Экспортируем в JSON
> export PositionInfo
```

---

## Пример обучающей сессии

**Цель:** «Я хочу закрыть позицию, что мне для этого нужно?»

```bash
> field ticket
EXACT MATCH: field 'ticket' found in:
-----------------------------------------------------------
    ...
    8. OpenedOrderInfo
    9. OrderCloseRequest
   ...

> OrderCloseRequest
===========================================================
TYPE: OrderCloseRequest
===========================================================
FIELDS (3):
-----------------------------------------------------------
  #  1 ticket                         : uint64
  #  2 volume                         : double
  #  5 slippage                       : int32

# Теперь вы знаете:
# - Закрытие через OrderCloseRequest (ticket, необязательный частичный объём, slippage)
# - В ответ приходит OrderCloseReply — проверяйте returned_code == 10009 для успеха
#   (см. RETURN_CODES_REFERENCE.md)
# - На практике MT5Sugar.close_position(ticket) оборачивает всё это за вас
```

---

## Устранение неполадок

**В: Тип не найден**

```
> MyType
[!] Type not found: MyType
    Did you mean: MqlTradeRequest, MqlTradeResult, ...
```

**О:** используйте поиск с частичным именем, чтобы найти похожие типы

---

**В: Совпадает несколько типов**

```
> OrderInfo
[!] Multiple types match 'OrderInfo':
    1. HistoryOrderInfo
    2. OnTradeHistoryOrderInfo
    3. OnTradeOrderInfo
    4. OpenedOrderInfo
```

**О:** выберите конкретный, который имеете в виду (например, `OpenedOrderInfo` для действующего отложенного/открытого ордера).

---

**В: В чём разница между OpenedOrderInfo и OrderSendRequest?**

**О:** используйте инспектор:

- `OpenedOrderInfo` — информация о существующем ордере (24 поля: state, times, type и т. д.)
- `OrderSendRequest` — запрос на создание нового ордера (13 полей параметров ордера)

Правило:

- `*Request` — вход для метода API (то, что вы отправляете)
- `*Reply` — выход метода API (то, что вы получаете)
- `*Info` — структурированные данные о сущностях (позиция, ордер, сделка, символ)
- `*Data` — структуры полезных данных, возвращаемые внутри ответов

---

**В: Какие поля double, а какие int64?**

**О:** используйте поиск по типу поля:

```
> findtype double    # Все поля цен/объёмов/прибыли
> findtype int64     # Все поля ID/magic/тикетов
> findtype string    # Все текстовые поля (symbol, comment и т. д.)
```

---

**В: Где используется enum X?**

**О:** используйте поиск использования enum:

```
> whereenum ENUM_ORDER_TYPE_TF
# Показывает все типы и поля, использующие этот enum
```

---

## Краткий справочник команд

```
BASIC COMMANDS:
  list               - Show all types
  list --request     - Show only Request types
  <TypeName>         - Inspect type structure
  search <text>      - Find types by name
  field <name>       - Find types with field
  enum <name>        - Show enum values

MORE COMMANDS:
  findtype <type>    - Find fields by type
  whereenum <name>   - Find enum usage
  export <TypeName>  - Export to JSON
  stats              - Show statistics

NAVIGATION:
  help               - Show help
  exit               - Exit inspector
```

---

**Дальнейшие шаги:**

- Запустите `python main.py inspect` и исследуйте!
- Смотрите [MT5Account Master Overview](../MT5Account/MT5Account.Master.Overview.md) для полной документации по API
- Попробуйте демо-примеры в `examples/`
- См. [RETURN_CODES_REFERENCE.md](RETURN_CODES_REFERENCE.md) для кодов ошибок
- См. [USERCODE_SANDBOX_GUIDE.md](USERCODE_SANDBOX_GUIDE.md) для примеров кода
