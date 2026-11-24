# MT5Service - Обзор API среднего уровня

---

## ⚠️ Критически важно для понимания

**MT5Service - это архитектурная прослойка (middleware)** - она располагается между MT5Account (gRPC protobuf) и MT5Sugar (бизнес-логика).

### Трёхслойная архитектура:

```text
┌──────────────────────────────────────────────────────────┐
│ MT5Sugar  —  ВЫСОКИЙ                                      │
│ Бизнес-логика, готовые шаблоны, операции в одну строку    │
└────────────────────┬─────────────────────────────────────┘
                     │  использует методы Service
                     ▼
┌──────────────────────────────────────────────────────────┐
│ MT5Service  —  СРЕДНИЙ     ← вы находитесь здесь          │
│ Распаковывает protobuf в dataclasses                     │
│ (некоторые методы добавляют ценность, некоторые — сквозные)│
└────────────────────┬─────────────────────────────────────┘
                     │  вызывает методы Account
                     ▼
┌──────────────────────────────────────────────────────────┐
│ MT5Account  —  НИЗКИЙ                                     │
│ Прямые вызовы gRPC, возвращает protobuf-объекты Data      │
└────────────────────┬─────────────────────────────────────┘
                     │  gRPC
                     ▼
                     Терминал MT5
```

### Проверка реальной ценности

**Не все методы MT5Service добавляют одинаковую ценность:**

- ✅ **ВЫСОКАЯ/ОЧЕНЬ ВЫСОКАЯ ценность** - Сложная распаковка protobuf + преобразование в dataclass

- ⚪ **СРЕДНЯЯ/НИЗКАЯ ценность** - Простое извлечение поля protobuf

- ⚪ **НЕТ ценности** - Прямая передача (`return await account.method()` или `yield data`)

**Ключевая мысль:** MT5Service существует прежде всего ради **архитектурных потребностей MT5Sugar**. Для прямого использования оценивайте реальную ценность обработки каждого метода.

---

## Быстрая навигация - Обзоры разделов

### [1. Информация о счёте](./1.%20Account_Information.md)

**4 метода** - Баланс/средства/маржа/кредитное плечо счёта

- ✅ 1 метод ВЫСОКОЙ ценности: `get_account_summary()` - агрегирует 5 RPC-вызовов + преобразование datetime

- ⚪ 3 метода БЕЗ ценности: Простые сквозные обёртки для архитектурной согласованности

### [2. Информация о символах](./2.%20Symbol_Information.md)

**13 методов** - Свойства символов, котировки, торговые условия

- ✅ 9 методов имеют ценность - MT5Account возвращает protobuf Data, который требует распаковки (от ОЧЕНЬ ВЫСОКОЙ до НИЗКОЙ)
- ⚪ 4 метода БЕЗ ценности - Прямая передача для архитектурной согласованности

### [3. Позиции и ордера](./3.%20Positions_Orders.md)

**5 методов** - Открытые позиции, отложенные ордера, история

- ✅ 1 метод СРЕДНЕЙ ценности: `get_opened_tickets()` - преобразует protobuf repeated → списки Python

- ⚪ 1 метод НИЗКОЙ ценности: Простая распаковка

- ⚪ 3 метода БЕЗ ценности: Прямая передача

### [4. Глубина рынка](./4.%20Market_Depth.md)

**3 метода** - Котировки Level II, стакан ордеров (DOM)

- ✅ 1 метод ВЫСОКОЙ ценности: `get_market_depth()` - преобразует protobuf repeated → List[BookInfo]

- ⚪ 2 метода СРЕДНЕЙ ценности: Простая распаковка bool

### [5. Торговые операции](./5.%20Trading_Operations.md)

**6 методов** - Исполнение ордеров, расчёты маржи

- ✅ 1 метод ОЧЕНЬ ВЫСОКОЙ ценности: `check_order()` - извлекает глубоко вложенную структуру protobuf

- ✅ 2 метода ВЫСОКОЙ ценности: `place_order()`, `modify_order()` - уплощают 10 полей → dataclass

- ⚪ 3 метода НИЗКОЙ ценности: Простое извлечение одного поля

### [6. Методы стриминга](./6.%20Streaming_Methods.md)

**5 асинхронных генераторов** - Тики, сделки, прибыль в реальном времени

- ✅ 1 метод ВЫСОКОЙ ценности: `stream_ticks()` - преобразование datetime + создание dataclass

- ⚪ 4 метода БЕЗ ценности: Прямая передача (`yield data`)

---

## Все 36 методов - Сгруппированы по ценности

### ✅ Методы, которые стоит использовать напрямую

**ОЧЕНЬ ВЫСОКАЯ ценность** (1 метод):

- `check_order()` - Извлекает глубоко вложенный `mql_trade_check_result` → OrderCheckResult

**ВЫСОКАЯ ценность** (7 методов):

- `get_account_summary()` - Агрегирует 5 RPC-вызовов + преобразование datetime
- `get_symbol_params_many()` - Агрегирует 17 полей + распаковывает список protobuf
- `get_symbol_tick()` - Unix timestamp → datetime + распаковывает 8 полей
- `get_symbol_session_quote()` - 2x protobuf Timestamp → datetime
- `get_symbol_session_trade()` - 2x protobuf Timestamp → datetime
- `place_order()` - Уплощает 10 полей protobuf → dataclass OrderResult
- `modify_order()` - Уплощает 10 полей protobuf → dataclass OrderResult
- `get_market_depth()` - Преобразует protobuf repeated → dataclass List[BookInfo]
- `stream_ticks()` - Преобразует protobuf Timestamp → datetime + dataclass SymbolTick

**СРЕДНЯЯ ценность** (3 метода):

- `get_symbol_margin_rate()` - Распаковывает protobuf + создаёт dataclass
- `get_opened_tickets()` - Преобразует protobuf repeated → списки Python
- `subscribe_market_depth()` - Распаковывает `data.opened_successfully` из protobuf
- `unsubscribe_market_depth()` - Распаковывает `data.closed_successfully` из protobuf

### ⚪ Методы с минимальной/нулевой ценностью

**НИЗКАЯ ценность** (8 методов) - Простое извлечение одного поля:

- `get_symbols_total()` - Распаковывает `data.total`
- `get_symbol_double()` - Распаковывает `data.value`
- `get_symbol_integer()` - Распаковывает `data.value`
- `get_symbol_string()` - Распаковывает `data.value`
- `get_positions_total()` - Распаковывает `data.total_positions`
- `close_order()` - Распаковывает `data.returned_code`
- `calculate_margin()` - Распаковывает `data.margin`
- `calculate_profit()` - Распаковывает `data.profit`

**НЕТ ценности** (18 методов) - Прямая передача:

- `get_account_double()` - Просто вызывает `account.account_info_double()`
- `get_account_integer()` - Просто вызывает `account.account_info_integer()`
- `get_account_string()` - Просто вызывает `account.account_info_string()`
- `symbol_exist()` - Просто вызывает `account.symbol_exist()`
- `get_symbol_name()` - Просто вызывает `account.symbol_name()`
- `symbol_select()` - Просто вызывает `account.symbol_select()`
- `is_symbol_synchronized()` - Просто вызывает `account.symbol_is_synchronized()`
- `get_opened_orders()` - Просто вызывает `account.opened_orders()`
- `get_order_history()` - Просто вызывает `account.order_history()`
- `get_positions_history()` - Просто вызывает `account.positions_history()`
- `stream_trade_updates()` - Просто `yield data`
- `stream_position_profits()` - Просто `yield data`
- `stream_opened_tickets()` - Просто `yield data`
- `stream_transactions()` - Просто `yield data`

---

## Когда использовать MT5Service, а когда MT5Account

### Используйте MT5Service, когда:

- ✅ Метод добавляет значительную ценность (ВЫСОКАЯ/ОЧЕНЬ ВЫСОКАЯ из списка выше)
- ✅ Вам нужен более чистый API, чем protobuf (преобразование datetime, dataclasses)
- ✅ Работаете с MT5Sugar (архитектурное требование)

### Используйте MT5Account напрямую, когда:

- Метод имеет НЕТ/НИЗКУЮ ценность (прямая передача или простая распаковка)
- Нужен полный контроль над структурами protobuf
- Критична производительность (избегайте лишнего слоя)
- Метод недоступен в MT5Service

**Доступ к MT5Account из MT5Service:**

```python
account = service.get_account()
# Теперь можно вызывать низкоуровневые методы напрямую
```

---

## Шаблон использования

```python
import asyncio
from uuid import uuid4
from MetaRpcMT5 import MT5Account  # Низкоуровневый gRPC-клиент
from pymt5.mt5_service import MT5Service  # Обёртка среднего уровня
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

async def main():
    # 1. Создаём MT5Account (низкоуровневый gRPC-клиент)
    account = MT5Account(
        user=12345678,  # Номер логина MT5
        password="password",
        grpc_server="mt5.mrpc.pro:443",  # по умолчанию "mt5.mrpc.pro:443"
        id_=uuid4()  # необязательный UUID для экземпляра терминала
    )

    # 2. Подключаемся к серверу MT5
    await account.connect_by_server_name(
        server_name="MetaQuotes-Demo",  # имя сервера/кластера брокера MT5
        base_chart_symbol="EURUSD",  # символ для инициализации графика
        timeout_seconds=120
    )

    # 3. Оборачиваем в MT5Service (средний уровень)
    service = MT5Service(account)

    # 4. Используем методы ВЫСОКОЙ ценности
    summary = await service.get_account_summary()
    print(f"Balance: ${summary.balance:.2f}, Equity: ${summary.equity:.2f}")

    # 5. Для методов БЕЗ ценности рассмотрите прямой вызов Account
    # Вместо: balance = await service.get_account_double(account_info_pb2.ACCOUNT_BALANCE)
    # Прямой вызов: balance = await account.account_info_double(account_info_pb2.ACCOUNT_BALANCE)

    # 6. Закрываем соединение по завершении
    await account.disconnect()

asyncio.run(main())
```

---

## Полный указатель методов

### 1. Информация о счёте (4 метода)

**Обзор:** [Account_Information.md](./1.%20Account_Information.md)

| Метод | Ценность | Что он делает |
|--------|-------|--------------|
| `get_account_summary()` | ✅ ВЫСОКАЯ | Агрегирует 5 RPC-вызовов + преобразование datetime |
| `get_account_double()` | ⚪ НЕТ | Передача: `return await account.account_info_double()` |
| `get_account_integer()` | ⚪ НЕТ | Передача: `return await account.account_info_integer()` |
| `get_account_string()` | ⚪ НЕТ | Передача: `return await account.account_info_string()` |

---

### 2. Информация о символах (13 методов)

**Обзор:** [Symbol_Information.md](./2.%20Symbol_Information.md)

| Метод | Ценность | Что он делает |
|--------|-------|--------------|
| `get_symbol_params_many()` | ✅ ОЧЕНЬ ВЫСОКАЯ | Агрегирует 17 полей + распаковывает список protobuf |
| `get_symbol_tick()` | ✅ ВЫСОКАЯ | Unix timestamp → datetime + распаковывает 8 полей |
| `get_symbol_session_quote()` | ✅ ВЫСОКАЯ | 2x protobuf Timestamp → datetime |
| `get_symbol_session_trade()` | ✅ ВЫСОКАЯ | 2x protobuf Timestamp → datetime |
| `get_symbol_margin_rate()` | ⚪ СРЕДНЯЯ | Распаковывает protobuf + создаёт dataclass |
| `get_symbols_total()` | ⚪ НИЗКАЯ | Распаковывает `data.total` из protobuf |
| `get_symbol_double()` | ⚪ НИЗКАЯ | Распаковывает `data.value` из protobuf |
| `get_symbol_integer()` | ⚪ НИЗКАЯ | Распаковывает `data.value` из protobuf |
| `get_symbol_string()` | ⚪ НИЗКАЯ | Распаковывает `data.value` из protobuf |
| `symbol_exist()` | ⚪ НЕТ | Передача: `return await account.symbol_exist()` |
| `get_symbol_name()` | ⚪ НЕТ | Передача: `return await account.symbol_name()` |
| `symbol_select()` | ⚪ НЕТ | Передача: `return await account.symbol_select()` |
| `is_symbol_synchronized()` | ⚪ НЕТ | Передача: `return await account.symbol_is_synchronized()` |

---

### 3. Позиции и ордера (5 методов)

**Обзор:** [Positions_Orders.md](./3.%20Positions_Orders.md)

| Метод | Ценность | Что он делает |
|--------|-------|--------------|
| `get_opened_tickets()` | ✅ СРЕДНЯЯ | Преобразует protobuf repeated → списки Python |
| `get_positions_total()` | ⚪ НИЗКАЯ | Распаковывает `data.total_positions` из protobuf |
| `get_opened_orders()` | ⚪ НЕТ | Передача: `return await account.opened_orders()` |
| `get_order_history()` | ⚪ НЕТ | Передача: `return await account.order_history()` |
| `get_positions_history()` | ⚪ НЕТ | Передача: `return await account.positions_history()` |

---

### 4. Глубина рынка (3 метода)

**Обзор:** [Market_Depth.md](./4.%20Market_Depth.md)

| Метод | Ценность | Что он делает |
|--------|-------|--------------|
| `get_market_depth()` | ✅ ВЫСОКАЯ | Преобразует protobuf repeated → dataclass List[BookInfo] |
| `subscribe_market_depth()` | ⚪ СРЕДНЯЯ | Распаковывает `data.opened_successfully` из protobuf |
| `unsubscribe_market_depth()` | ⚪ СРЕДНЯЯ | Распаковывает `data.closed_successfully` из protobuf |

---

### 5. Торговые операции (6 методов)

**Обзор:** [Trading_Operations.md](./5.%20Trading_Operations.md)

| Метод | Ценность | Что он делает |
|--------|-------|--------------|
| `check_order()` | ✅ ОЧЕНЬ ВЫСОКАЯ | Извлекает глубоко вложенный `mql_trade_check_result` → OrderCheckResult (8 полей) |
| `place_order()` | ✅ ВЫСОКАЯ | Уплощает 10 полей protobuf → dataclass OrderResult |
| `modify_order()` | ✅ ВЫСОКАЯ | Уплощает 10 полей protobuf → dataclass OrderResult |
| `close_order()` | ⚪ НИЗКАЯ | Распаковывает `data.returned_code` из protobuf → int |
| `calculate_margin()` | ⚪ НИЗКАЯ | Распаковывает `data.margin` из protobuf → float |
| `calculate_profit()` | ⚪ НИЗКАЯ | Распаковывает `data.profit` из protobuf → float |

---

### 6. Методы стриминга (5 асинхронных генераторов)

**Обзор:** [Streaming_Methods.md](./6.%20Streaming_Methods.md)

| Метод | Ценность | Что он делает |
|--------|-------|--------------|
| `stream_ticks()` | ✅ ВЫСОКАЯ | Преобразует protobuf Timestamp → datetime + создаёт dataclass SymbolTick (8 полей) |
| `stream_trade_updates()` | ⚪ НЕТ | Передача: `async for data in account.on_trade(): yield data` |
| `stream_position_profits()` | ⚪ НЕТ | Передача: `async for data in account.on_position_profit(): yield data` |
| `stream_opened_tickets()` | ⚪ НЕТ | Передача: `async for data in account.on_positions_and_pending_orders_tickets(): yield data` |
| `stream_transactions()` | ⚪ НЕТ | Передача: `async for data in account.on_trade_transaction(): yield data` |

---

## Лучшие практики

### 1. Используйте методы ВЫСОКОЙ ценности

```python
# ХОРОШО - используйте методы, которые добавляют реальную ценность
summary = await service.get_account_summary()  # Агрегирует 5 RPC-вызовов
symbols, _ = await service.get_symbol_params_many("EURUSD")  # Агрегирует 17 полей
result = await service.check_order(request)  # Извлекает глубоко вложенный protobuf

# ПОДУМАЙТЕ - для методов БЕЗ ценности вызывайте Account напрямую
balance = await account.account_info_double(account_info_pb2.ACCOUNT_BALANCE)
# Вместо: balance = await service.get_account_double(account_info_pb2.ACCOUNT_BALANCE)
```

### 2. Валидируйте торговые операции

```python
# ВСЕГДА используйте check_order() перед place_order() - у него ОЧЕНЬ ВЫСОКАЯ ценность!
check = await service.check_order(request)
if check.returned_code == 0:
    result = await service.place_order(request)
    if result.returned_code == 10009:
        print(f"Success! Order: {result.order}")
```

### 3. Обрабатывайте ошибки

```python
try:
    summary = await service.get_account_summary()
except Exception as e:
    print(f"Error: {e}")
```

### 4. Используйте события отмены для стримов

```python
import asyncio

cancel_event = asyncio.Event()

# Используем stream_ticks() ВЫСОКОЙ ценности
async for tick in service.stream_ticks(["EURUSD"], cancel_event):
    print(f"{tick.time}: {tick.bid:.5f}")  # time уже datetime!
    if should_stop:
        cancel_event.set()
```

---


**Выбирайте мудро, исходя из реальной ценности обработки, а не только из уровня API!**
