# Глоссарий PyMT5

> Термины и концепции, специфичные для проекта. Этот глоссарий охватывает архитектуру PyMT5, её компоненты и терминологию автоматизации торговли, используемую во всей кодовой базе.

---

## 🏗️ Архитектурные термины

### Трёхуровневая архитектура

Основной шаблон проектирования PyMT5 с тремя уровнями абстракции:

- **Уровень 1 (MT5Account):** Низкоуровневое взаимодействие по gRPC с терминалом MT5
- **Уровень 2 (MT5Service):** Методы-обёртки с датаклассами и типами Python
- **Уровень 3 (MT5Sugar):** Высокоуровневые удобные методы с готовыми паттернами

---

### MT5Account

**🔹 Уровень 1 — Низкоуровневый API**

Базовый слой, обеспечивающий прямой доступ к терминалу MT5 по протоколу gRPC.

**Ключевые характеристики:**

- Прямые вызовы gRPC к терминалу MT5
- Встроенная устойчивость соединения с автоматическим переподключением
- Работает с объектами Request/Response protobuf
- Полный контроль, максимальная сложность
- **43 асинхронных метода**, покрывающих все операции MT5
- Возвращает объекты Data protobuf
- Автоматическое переподключение с экспоненциальной задержкой
- Управление сессией с отслеживанием по UUID

**Когда использовать:** Продвинутые пользователи, которым нужен детальный контроль, нестандартные интеграции, построение собственных обёрток.

**Расположение:** `package/MetaRpcMT5/mt5_account.py` (~1900 строк) — класс, экспортируемый из `MetaRpcMT5`

**Документация:** [MT5Account.Master.Overview.md](../MT5Account/MT5Account.Master.Overview.md)


---

### MT5Service
**🔸 Уровень 2 — API обёрток**

Средний слой, предоставляющий упрощённые сигнатуры методов без сложности proto.

**Ключевые характеристики:**

- Возвращает чистые типы Python (float, int, str, datetime)
- Автоматически распаковывает обёртки .data protobuf
- Преобразует Timestamp в объекты datetime
- Преобразование типов (proto в примитивы/датаклассы Python)
- Упрощённые имена методов
- Без авто-нормализации (точностью управляете вы)
- **37 методов** для типовых сценариев
- Основное назначение: архитектурный промежуточный слой для MT5Sugar

**Распределение ценности:**

- ✅ **11 методов ВЫСОКОЙ/ОЧЕНЬ ВЫСОКОЙ ценности** — агрегируют несколько вызовов RPC, сложную распаковку protobuf, преобразования datetime

- ⚪ **25 методов НУЛЕВОЙ/НИЗКОЙ ценности** — прямая передача или простое извлечение одного поля

**Когда использовать:** Построение собственных стратегий, которым нужно больше контроля, чем даёт Sugar, но меньше сложности, чем MT5Account.

**Расположение:** `src/pymt5/mt5_service.py` (1200+ строк)

**Документация:** [MT5Service.Overview.md](../MT5Service/MT5Service.Overview.md)


---

### MT5Sugar
**🔺 Уровень 3 — Удобный API**

Высокоуровневый API для типовых торговых операций.

**Ключевые характеристики:**

- Свойства для мгновенного доступа (`await sugar.balance`)
- Поддержка контекстного менеджера (`async with MT5Sugar(service) as sugar`)
- Перечисления (enum) вместо «магических» чисел (`Period.TODAY`, `OrderType.BUY`)
- Унифицированные методы с разумными значениями по умолчанию
- Операции в одну строку
- Подсказки типов повсюду
- Простейший API, обрабатывает краевые случаи
- **Лучшая отправная точка** для 95% сценариев
- **62 метода + 7 свойств = 69 в сумме**

**Ключевые возможности:**

- `buy_market(symbol, volume)` — одна строка для открытия позиции
- `calculate_position_size(symbol, risk_percent, sl_pips)` — автоматический расчёт объёма по риску
- `buy_market_with_pips(symbol, volume, sl_pips, tp_pips)` — открытие с SL/TP в пипсах
- `get_balance()`, `get_equity()` — асинхронные методы для получения информации о счёте
- `close_all_positions()` — аварийный выход

**Когда использовать:** Быстрая разработка, прототипирование, простые стратегии, короткие скрипты.

**Расположение:** `src/pymt5/mt5_sugar.py` (2100+ строк)

**Документация:** [Обзор MT5Sugar](../MT5Sugar/MT5Sugar.Master.Overview.md)


---

## 🧩 Концепции, специфичные для Python

### Паттерн Async/Await
Встроенная модель асинхронного программирования Python.

**Все методы в PyMT5 асинхронные:**
```python
import asyncio
from MetaRpcMT5 import MT5Account
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

async def main():
    # Создание и подключение
    account = MT5Account(user=591129415, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="FxPro-MT5 Demo", base_chart_symbol="EURUSD")

    # Для всех асинхронных операций необходимо использовать 'await'
    balance = await account.account_info_double(
        account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
    )
    positions = await account.positions_total()

    await account.disconnect()

# Запуск асинхронной функции
asyncio.run(main())
```

**Почему async?**

- Неблокирующий ввод-вывод для вызовов gRPC
- Лучшая производительность при множественных операциях
- Эффективная обработка потоковых данных
- Стандартный паттерн Python для сетевых операций

**Документация:** [Python asyncio](https://docs.python.org/3/library/asyncio.html)

---

### Датаклассы
Структурированные контейнеры данных в Python.

**MT5Service использует датаклассы для аккуратных структур данных:**
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AccountSummary:
    login: int                                      # Номер логина счёта
    balance: float                                  # Баланс счёта
    equity: float                                   # Средства (equity) (баланс + плавающий P&L)
    user_name: str                                  # Имя клиента
    leverage: int                                   # Кредитное плечо счёта (напр., 100)
    trade_mode: Any                                 # Режим торговли (demo/real/contest)
    company_name: str                               # Название компании-брокера
    currency: str                                   # Валюта депозита
    server_time: Optional[datetime]                 # Время сервера
    utc_timezone_shift_minutes: int                 # Сдвиг часового пояса относительно UTC
    credit: float                                   # Кредитные средства
    margin: float                                   # Использованная маржа
    free_margin: float                              # Свободная маржа
    margin_level: float                             # Уровень маржи, %
    profit: float                                   # Плавающий P&L

# Использование
summary = await service.get_account_summary()
print(f"Balance: {summary.balance}")  # Чистый доступ к атрибутам
print(f"Time: {summary.server_time}")  # Уже объект datetime
```

**Преимущества:**

- Подсказки типов для автодополнения в IDE
- Чистый доступ к атрибутам (без ключей словаря)
- Автоматические __repr__ и __eq__
- Неизменяемость при frozen=True

---

### Асинхронные генераторы
Способ Python для асинхронной передачи данных потоком.

**Потоковые методы возвращают асинхронные генераторы:**
```python
# Стриминг возвращает асинхронный генератор
async for tick_data in account.on_symbol_tick(["EURUSD"]):
    tick = tick_data.symbol_tick
    print(f"Bid: {tick.bid}, Ask: {tick.ask}")
    print(f"Time: {tick.time}")

    # Можно прервать в любой момент
    if some_condition:
        break

# Автоматическая очистка при выходе из цикла
```

**Критические правила:**

- Используйте `async for` для потребления данных
- Генератор автоматически останавливается при break
- Ручная очистка не нужна
- Можно использовать `async with` для стриминга с ограниченной областью

**Пример с тайм-аутом:**
```python
import asyncio

try:
    async for tick_data in account.on_symbol_tick(["EURUSD"]):
        tick = tick_data.symbol_tick
        await asyncio.wait_for(process_tick(tick), timeout=5.0)
except asyncio.TimeoutError:
    print("Processing timeout")
```

---

### ➕ Свойства
Вычисляемые атрибуты Python, которые выглядят как простые поля.

**MT5Sugar использует свойства для мгновенного доступа:**

```python
# Свойства — скобки не нужны!
balance = await sugar.balance       # Не sugar.get_balance()
equity = await sugar.equity         # Не sugar.get_equity()
margin = await sugar.margin         # Не sugar.get_margin()
free_margin = await sugar.free_margin
margin_level = await sugar.margin_level
profit = await sugar.profit

# Все они — асинхронные свойства
@property
async def balance(self) -> float:
    return await self.get_balance()
```

**Преимущества:**

- Более чистый синтаксис
- Выглядит как доступ к атрибуту
- Под капотом по-прежнему асинхронно
- Удобнее для коротких скриптов

---

### Контекстные менеджеры
Паттерн Python для автоматической очистки ресурсов.

**MT5Sugar поддерживает async with:**
```python
# Создаём полный стек
account = MT5Account(
    user=591129415,
    password="password",
    grpc_server="mt5.mrpc.pro:443"
)

await account.connect_by_server_name(
    server_name="FxPro-MT5 Demo",
    base_chart_symbol="EURUSD"
)

service = MT5Service(account)

# Используем sugar с контекстным менеджером
async with MT5Sugar(service) as sugar:
    balance = await sugar.balance
    ticket = await sugar.buy_market("EURUSD", 0.01)

# Очистка по завершении
await account.disconnect()
```

**Зачем контекстные менеджеры?**

- Более чистая структура кода
- Стандартный паттерн Python
- Использование ресурсов с ограниченной областью

**Важно: требуется ручная очистка**

Вызывайте `await account.disconnect()` по завершении работы. Это закрывает постоянное соединение gRPC (`account.channel`) и освобождает ресурсы:

- Закрыть постоянное соединение gRPC
- Освободить сетевые ресурсы
- Предотвратить утечки соединений
- Избежать ошибок DEADLINE_EXCEEDED при выходе

Без `disconnect()` соединение остаётся открытым и может вызвать утечки ресурсов или ошибки при завершении программы.

**Рекомендуемый паттерн с корректной очисткой:**

```python
account = MT5Account(
    user=591129415,
    password="password",
    grpc_server="mt5.mrpc.pro:443"
)

try:
    await account.connect_by_server_name(
        server_name="FxPro-MT5 Demo",
        base_chart_symbol="EURUSD"
    )

    service = MT5Service(account)
    sugar = MT5Sugar(service)

    # Работаем здесь
    balance = await sugar.balance
    ticket = await sugar.buy_market("EURUSD", 0.01)

finally:
    await account.disconnect()  # Всегда очищаем
```

---

## 📦 Технические концепции

### Авто-нормализация
Автоматическая подстройка торговых параметров под требования брокера.

**Что нормализуется:**

- **Объёмы:** Округляются до шага объёма брокера (напр., 0.01 лот)
- **Цены:** Округляются до размера тика/знаков символа (напр., 5 знаков после запятой для EURUSD)
- **Стоп-лосс / Тейк-профит:** Подстраиваются под точность символа

**Где:** Нормализацию выполняет сам терминал MT5 (это выгодно и MT5Service, и MT5Sugar)

**Пример:**
```python
# Вы передаёте: volume=0.0234
# Терминал нормализует до: volume=0.02 (если шаг брокера 0.01)
ticket = await sugar.buy_market("EURUSD", 0.0234)
```

**Ручная нормализация при необходимости:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

# Получаем шаг объёма
volume_step = await service.get_symbol_double(
    "EURUSD",
    market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_STEP
)

# Округляем до шага
volume = 0.0234
normalized_volume = round(volume / volume_step) * volume_step
# Результат: 0.02

# Получаем число знаков символа для нормализации цены
digits = await service.get_symbol_integer(
    "EURUSD",
    market_info_pb2.SymbolInfoIntegerProperty.SYMBOL_DIGITS
)

# Округляем цену до числа знаков
price = 1.09876543
normalized_price = round(price, digits)
# Результат: 1.09877 (для 5-значного брокера)
```

---

### Расчёт объёма на основе риска

Расчёт размера позиции исходя из денежного риска, а не фиксированного размера лота.

**Формула:** `volume = risk_amount / (stop_loss_pips * pip_value)`

**Параметры:**

- `risk_amount` — сумма в долларах, которой вы готовы рискнуть (напр., $50)
- `stop_loss_pips` — расстояние до SL в пипсах (напр., 20 пипсов)
- Результат: размер лота, при котором риск составляет ровно $50 при срабатывании SL

**Методы (MT5Sugar):**

```python
# Рассчитать объём для заданного риска
volume = await sugar.calculate_position_size("EURUSD", risk_percent=2.0, sl_pips=50)
# Риск 2% при SL 50 пипсов

# Покупка с расчётом на основе риска
lot_size = await sugar.calculate_position_size("EURUSD", 2.0, 50)
ticket = await sugar.buy_market_with_pips("EURUSD", lot_size, sl_pips=50, tp_pips=100)
```

**Сценарий использования:** Единообразное управление рисками по всем сделкам.

---

### Пункты (points) против пипсов (pips)
**Пункт (Point):** Минимальное изменение цены для символа (1 тик).

**Пипс (Pip):** Традиционная единица форекс (0.0001 для большинства пар).

**Соотношение:**

- **5-значные брокеры:** 1 пипс = 10 пунктов (EURUSD: от 1.10000 до 1.10010 = 1 пипс)
- **3-значные брокеры:** 1 пипс = 1 пункт (USDJPY: от 110.00 до 110.01 = 1 пипс)

**В PyMT5:** Все API используют **пункты (points)** для единообразия.

**Преобразование:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

# Получаем размер пункта
point = await service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_POINT)
# point = 0.00001 для 5-значного брокера

# Преобразуем пипсы в пункты
pips = 20
points = pips * 10  # Для 5-значных пар
```

**Почему пункты?** Универсальны для всех инструментов (форекс, металлы, индексы, криптовалюта).

---

### Методы на основе пипсов
Удобные методы, работающие с пипсами вместо пунктов для форекс-трейдеров.

**Методы (MT5Sugar):**

```python
# Рыночные ордера с SL/TP в пипсах
ticket = await sugar.buy_market_with_sltp("EURUSD", 0.01, sl_pips=20, tp_pips=30)
# Или используйте псевдоним:
ticket = await sugar.buy_market_with_pips("EURUSD", 0.01, sl_pips=20, tp_pips=30)

ticket = await sugar.sell_market_with_sltp("GBPUSD", 0.01, sl_pips=20, tp_pips=30)
# Или используйте псевдоним:
ticket = await sugar.sell_market_with_pips("GBPUSD", 0.01, sl_pips=20, tp_pips=30)

# Отложенные ордера с SL/TP в пипсах (требуется абсолютная цена)
current_ask = await sugar.get_ask("EURUSD")
ticket = await sugar.buy_limit_with_sltp("EURUSD", 0.01, price=current_ask - 0.0020, sl_pips=15, tp_pips=30)

current_bid = await sugar.get_bid("EURUSD")
ticket = await sugar.sell_limit_with_sltp("EURUSD", 0.01, price=current_bid + 0.0020, sl_pips=15, tp_pips=30)
```

**Преимущества:**

- SL/TP задаются в пипсах (привычно для форекс-трейдеров)
- Автоматическое преобразование в цены
- Меньше ошибок, чем при ручных расчётах

---

### Трейлинг-стоп
Динамический стоп-лосс, следующий за ценой в направлении прибыли.

**Как это работает:**

1. Позиция открывается с начальным SL
2. Когда прибыль достигает порога (напр., +40 пипсов)
3. SL перемещается в безубыток или лучше
4. SL продолжает следовать за ценой на фиксированном расстоянии
5. Фиксирует прибыль по мере благоприятного движения цены

**Пример реализации:**

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

async def trailing_stop_logic(sugar, ticket, symbol):
    # Получаем позицию для проверки прибыли
    position = await sugar.get_position_by_ticket(ticket)
    if not position:
        return

    current_profit = position.profit
    trailing_threshold = 40.0  # долларов
    trailing_distance_pips = 20  # 20 пипсов

    point = await sugar.service.get_symbol_double(
        symbol, market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_POINT
    )
    trailing_distance = trailing_distance_pips * 10 * point  # Для 5-значного

    if current_profit >= trailing_threshold:
        current_price = await sugar.get_bid(symbol)
        new_sl = current_price - trailing_distance

        # Двигаем SL только вверх (для позиции BUY)
        if new_sl > position.sl:
            await sugar.modify_position_sltp(ticket, sl=new_sl, tp=position.tp)
```

**Сценарий использования:** Фиксация прибыли на трендовых рынках.

---

### Хеджирование
Открытие противоположной позиции для фиксации текущего уровня прибыли/убытка.

**Как это работает:**

1. Открыта основная позиция (напр., BUY EURUSD 0.1 лот)
2. Цена движется против вас (-50 пипсов)
3. Срабатывает хедж: SELL EURUSD 0.1 лот
4. Чистая позиция = 0 (убыток зафиксирован на -50 пипсов)

**Назначение:**

- Зафиксировать убытки вместо закрытия по стоп-лоссу
- Защитить позицию во время волатильности/новостей
- Дождаться лучшей возможности для выхода

**Реализация:**
```python
# Основная позиция
buy_ticket = await sugar.buy_market("EURUSD", 0.1)

# ... цена движется против вас ...

# Хедж
sell_ticket = await sugar.sell_market("EURUSD", 0.1)
# Чистая позиция = 0, убыток зафиксирован
```

**ПРЕДУПРЕЖДЕНИЕ:** Не все брокеры/регуляторы разрешают хеджирование. Брокеры США, как правило, не поддерживают хеджирование.

---

### Отложенный ордер
Ордер, исполняющийся автоматически при достижении ценой заданного уровня.

**Типы:**

- **BUY LIMIT:** Покупка по цене НИЖЕ текущей (ожидание отката, затем роста)
- **SELL LIMIT:** Продажа по цене ВЫШЕ текущей (ожидание роста, затем падения)
- **BUY STOP:** Покупка по цене ВЫШЕ текущей (пробой вверх)
- **SELL STOP:** Продажа по цене НИЖЕ текущей (пробой вниз)

**Методы (MT5Sugar):**

```python
# Buy limit без SL/TP
ticket = await sugar.buy_limit("EURUSD", 0.01, price=1.09950)

# Buy limit с SL/TP
ticket = await sugar.buy_limit_with_sltp("EURUSD", 0.01, price=1.09950, sl=1.09900, tp=1.10050)

# Sell stop без SL/TP
ticket = await sugar.sell_stop("EURUSD", 0.01, price=1.09950)

# Sell stop с SL/TP (нет отдельного метода, используйте sell_stop + modify)
ticket = await sugar.sell_stop("EURUSD", 0.01, price=1.09950)
await sugar.modify_position_sltp(ticket, sl=1.10000, tp=1.09900)
```

---

## 🔌 Термины gRPC и протокола

### gRPC

Высокопроизводительный фреймворк RPC (Remote Procedure Call), использующий HTTP/2.

**В PyMT5:**

- Уровень MT5Account отправляет запросы gRPC в терминал MT5
- Терминал запускает сервер gRPC (настраивается через шлюз)
- Паттерн Request/Response для всех операций
- Async/await для неблокирующих вызовов

**Настройка соединения:**
```python
account = MT5Account(
    user=591129415,
    password="password",
    grpc_server="mt5.mrpc.pro:443"
)

await account.connect_by_server_name(
    server_name="FxPro-MT5 Demo",
    base_chart_symbol="EURUSD"
)
```

**Документация:** [gRPC Python](https://grpc.io/docs/languages/python/)

---

### Protobuf

Protocol Buffers — языконезависимый формат сериализации данных от Google.

**В PyMT5:**

- Все методы MT5Account используют Request/Response protobuf
- Генерируется из файлов .proto
- Эффективная бинарная сериализация
- Типобезопасные структуры сообщений

**Пример:**

```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

# Уровень MT5Account — уже распаковывает ответ protobuf внутри
balance = await account.account_info_double(
    account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
)
# Возвращает: float (напр., 10000.0)
# ПРИМЕЧАНИЕ: Метод внутри извлекает res.data.requested_value перед возвратом

# Уровень MT5Service — тот же результат, просто другое имя метода
balance = await service.get_account_double(
    account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
)
# Возвращает: float (напр., 10000.0)
```

**И MT5Account, и MT5Service возвращают чистые типы Python (float, int, str), а не объекты protobuf.**

---

### ℹ️ Коды возврата

Коды возврата protobuf, указывающие на успех/неудачу операции.

**Распространённые коды:**

- **10009** = Успех (TRADE_RETCODE_DONE)
- **10008** = Отложенный ордер размещён (TRADE_RETCODE_PLACED)
- **10004** = Реквота
- **10006** = Запрос отклонён
- **10013** = Некорректный запрос
- **10014** = Некорректный объём
- **10015** = Некорректная цена
- **10016** = Некорректные стопы
- **10018** = Рынок закрыт
- **10019** = Недостаточно средств
- **10031** = Нет соединения с торговым сервером

**Всегда проверяйте returned_code в торговых операциях.**

**Пример:**

```python
result = await account.order_send(request)

if result.returned_code == 10009:  # TRADE_RETCODE_DONE
    print(f"Trade successful! Ticket: {result.order}")
elif result.returned_code == 10019:
    print("Not enough money")
else:
    print(f"Trade failed: code {result.returned_code}")
```

**Документация:** [Справочник кодов возврата](RETURN_CODES_REFERENCE.md)

---

### 📡 Паттерн стриминга
Потоки данных в реальном времени с использованием асинхронных генераторов.

**Потоковые методы:**
```python
# Стрим тиковых данных
async for tick_data in account.on_symbol_tick(["EURUSD"]):
    if tick_data.symbol_tick:
        tick = tick_data.symbol_tick
        print(f"Bid: {tick.bid}, Ask: {tick.ask}")
    if should_stop:
        break  # Автоматическая очистка

# Стрим торговых событий
async for trade_data in account.on_trade():
    print(f"Type: {trade_data.type}")
    if trade_data.event_data:
        print(f"New orders: {len(trade_data.event_data.new_orders)}")

# Стрим прибыли позиций (опрос каждые 500 мс)
async for profit_data in account.on_position_profit(interval_ms=500):
    for pos in profit_data.updated_positions:
        print(f"Ticket {pos.ticket}: ${pos.profit}")
```

**Критические правила:**

- Используйте `async for` для потребления потока
- Прерывайте (break) для остановки потока (автоочистка)
- Ручная очистка не нужна
- Можно использовать asyncio.timeout для ограничения по времени (Python 3.11+)

**С тайм-аутом:**
```python
import asyncio

# Python 3.11+
async with asyncio.timeout(60):  # Максимум 60 секунд
    async for tick_data in account.on_symbol_tick(["EURUSD"]):
        tick = tick_data.symbol_tick
        process(tick)

# Python 3.10 и ранее — используйте asyncio.wait_for
try:
    await asyncio.wait_for(stream_processing(), timeout=60)
except asyncio.TimeoutError:
    pass
```

**Документация:** [Управление потоками gRPC](GRPC_STREAM_MANAGEMENT.md)

---

## 🏛️ Торговые термины

### Основные торговые термины

Базовые торговые концепции, которые должен понимать каждый трейдер перед работой с MT5.

| Термин | Описание | Пример / Детали |
|------|-------------|-------------------|
| **Bid** | Цена, по которой брокер **покупает** у вас (вы **продаёте** по Bid) | EURUSD Bid: 1.10000 |
| **Ask** | Цена, по которой брокер **продаёт** вам (вы **покупаете** по Ask) | EURUSD Ask: 1.10002 |
| **Спред** | Разница между Ask и Bid (комиссия брокера) | Ask 1.10002 − Bid 1.10000 = спред 2 пипса |
| **Long / Buy** | Открытие позиции BUY (прибыль при росте цены) | Покупка EURUSD по 1.10000, закрытие по 1.10050 = +50 пипсов прибыли |
| **Short / Sell** | Открытие позиции SELL (прибыль при падении цены) | Продажа EURUSD по 1.10000, закрытие по 1.09950 = +50 пипсов прибыли |
| **Позиция** | Открытая сделка (BUY или SELL), которая может принести прибыль или убыток | BUY 0.1 лот EURUSD по 1.10000 (сейчас в прибыли +$50) |
| **Ордер** | Команда на открытие позиции | Рыночный ордер (немедленно), отложенный ордер (по заданной цене) |
| **Рыночный ордер** | Ордер, исполняющийся немедленно по текущей цене | BUY EURUSD по текущей цене Ask |
| **Отложенный ордер** | Ордер, срабатывающий автоматически при достижении ценой уровня | BUY LIMIT по 1.09950 (когда цена опускается до этого уровня) |
| **Лот / Объём** | Размер позиции (1 лот = 100 000 единиц базовой валюты) | 0.01 лот = 1 000 единиц (микролот) |
| **Стоп-лосс (SL)** | Уровень цены для автоматического выхода с ограничением убытка | SL на 1.09950 ограничивает убыток 50 пипсами |
| **Тейк-профит (TP)** | Уровень цены для автоматического выхода с фиксацией прибыли | TP на 1.10050 фиксирует 50 пипсов прибыли |
| **Пипс** | Стандартная единица движения цены (0.0001 для большинства форекс) | EURUSD: от 1.10000 до 1.10001 = 1 пипс |
| **Пункт (Point)** | Минимальное движение цены (1 тик) | Для 5-значного брокера: 1 пипс = 10 пунктов |
| **Кредитное плечо** | Заёмный капитал от брокера (напр., 1:100) | При 1:100 вы управляете $100 000 с маржой $1 000 |
| **Маржа** | Средства, заблокированные как залог под открытые позиции | Открытие 1 лота EURUSD с плечом 1:100 = маржа $1 000 |
| **Свободная маржа** | Доступные средства для открытия новых позиций | Баланс $10 000 − Маржа $1 000 = Свободная маржа $9 000 |
| **Баланс** | Средства счёта без учёта открытых позиций | Начальный депозит + прибыль/убыток закрытых сделок |
| **Средства (Equity)** | Текущая стоимость счёта (Баланс +/- плавающая прибыль/убыток) | Баланс $10 000 + Плавающая прибыль $500 = Средства $10 500 |
| **Плавающий P/L** | Нереализованная прибыль/убыток открытых позиций | Позиция сейчас в прибыли +$50 (ещё не закрыта) |
| **Уровень маржи** | Отношение Средств к Марже (%) | Средства $10 500 / Маржа $1 000 = 1050% |
| **Margin Call** | Предупреждение при падении уровня маржи ниже порога | Брокер предупреждает при уровне маржи 100% |
| **Stop Out** | Принудительное закрытие позиций при критически низком уровне маржи | Брокер закрывает позиции при уровне маржи 50% |
| **Просадка (Drawdown)** | Снижение от пикового баланса/средств | Пик $11 000 до текущих $10 000 = просадка $1 000 (9.09%) |
| **Проскальзывание (Slippage)** | Разница между ожидаемой и исполненной ценой | Запрошено 1.10000, исполнено по 1.10003 = проскальзывание 3 пипса |

**Критично для использования API:**

```python
# Получаем цены
bid = await sugar.get_bid("EURUSD")
ask = await sugar.get_ask("EURUSD")

# Получаем состояние счёта
balance = await sugar.balance
equity = await sugar.equity
margin = await sugar.margin
free_margin = await sugar.free_margin

# Открываем позиции
buy_ticket = await sugar.buy_market("EURUSD", 0.01)
sell_ticket = await sugar.sell_market("EURUSD", 0.01)

# Закрываем позиции
await sugar.close_position(buy_ticket)

# Изменяем SL/TP
await sugar.modify_position_sltp(buy_ticket, sl=1.09950, tp=1.10050)
```

---

### Сумма риска (Risk Amount)
Сумма в долларах, которой вы готовы рискнуть при срабатывании стоп-лосса.

**Пример:** Риск $50 на сделку означает, что при срабатывании SL вы теряете ровно $50.

**Используется в:**

```python
# Рассчитать объём для риска 2% при SL 50 пипсов
volume = await sugar.calculate_position_size("EURUSD", risk_percent=2.0, sl_pips=50)

# Открытие с расчётом на основе риска
lot_size = await sugar.calculate_position_size("EURUSD", 2.0, 50)
ticket = await sugar.buy_market("EURUSD", lot_size, sl_pips=50, tp_pips=100)
# Риск ровно 2% от баланса
```

---

### Безубыток (Breakeven)
Перемещение стоп-лосса на цену входа для устранения риска.

**Пример:**

- Вход: BUY по 1.10000
- Цена растёт до 1.10050 (+50 пипсов прибыли)
- Переместить SL с 1.09950 на 1.10000 (безубыток)
- Теперь без риска: худший случай = безубыток

**Реализация:**
```python
position = await sugar.get_position_by_ticket(ticket)
entry_price = position.price_open
breakeven_threshold = 40.0  # пипсов

current_profit = position.profit
if current_profit >= breakeven_threshold:
    await sugar.modify_position_sltp(ticket, sl=entry_price, tp=position.tp)
```

---

### Сеточная торговля (Grid Trading)
Стратегия размещения нескольких отложенных ордеров через равные интервалы выше и ниже текущей цены.

**Как это работает:**

1. Размещаем ордера Buy Limit ниже текущей цены (напр., каждые 20 пипсов)
2. Размещаем ордера Sell Limit выше текущей цены (напр., каждые 20 пипсов)
3. По мере колебаний цены ордера срабатывают и закрываются по TP
4. Лучше всего работает на флэтовых рынках

**Пример:**
```
Price: 1.10000
Buy Limits:  1.09980 (-20 pips), 1.09960 (-40 pips), 1.09940 (-60 pips)
Sell Limits: 1.10020 (+20 pips), 1.10040 (+40 pips), 1.10060 (+60 pips)
```

**Реализация:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

grid_step_pips = 20
levels = 5

ask = await sugar.get_ask("EURUSD")
bid = await sugar.get_bid("EURUSD")
point = await sugar.service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_POINT)

for i in range(1, levels + 1):
    offset = i * grid_step_pips * 10 * point  # Преобразуем пипсы в пункты

    # Buy Limit ниже Ask
    buy_price = ask - offset
    await sugar.buy_limit("EURUSD", 0.01, price=buy_price, sl=buy_price - 15*10*point, tp=buy_price + 30*10*point)

    # Sell Limit выше Bid
    sell_price = bid + offset
    await sugar.sell_limit("EURUSD", 0.01, price=sell_price, sl=sell_price + 15*10*point, tp=sell_price - 30*10*point)
```

**ПРЕДУПРЕЖДЕНИЕ:** Высокая волатильность может сработать по многим ордерам, увеличивая экспозицию.

---

### Скальпинг
Быстрая торговая стратегия с небольшой прибылью (5-25 пипсов) и тесными стопами (10-20 пипсов).

**Характеристики:**

- Очень короткое время удержания (секунды-минуты)
- Высокий процент выигрышных сделок, небольшая прибыль на сделку
- Риск:Доходность обычно от 1:1 до 1:2
- Требует низких спредов

**Реализация:**
```python
# Скальпинг с SL 10 пипсов, TP 15 пипсов
ticket = await sugar.buy_market_with_pips("EURUSD", 0.01, sl_pips=10, tp_pips=15)
```

---

### Новостная торговля
Размещение ордеров по обе стороны цены перед крупными новостными событиями.

**Как это работает:**

1. Перед новостями: размещаем Buy Stop выше + Sell Stop ниже
2. Выход новостей: цена пробивает в одну сторону
3. Один ордер срабатывает, другой отменяем
4. Захватываем всплеск волатильности

**Пример:**
```
Current price: 1.10000
Buy Stop:  1.10030 (+30 pips)
Sell Stop: 1.09970 (-30 pips)
News -> Price spikes to 1.10050 -> Buy Stop triggers -> Cancel Sell Stop
```

**Реализация:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

ask = await sugar.get_ask("EURUSD")
bid = await sugar.get_bid("EURUSD")
point = await sugar.service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_POINT)

offset = 30 * 10 * point  # 30 пипсов

buy_ticket = await sugar.buy_stop("EURUSD", 0.01, price=ask + offset)
sell_ticket = await sugar.sell_stop("EURUSD", 0.01, price=bid - offset)

# ... ждём новостей ...

# ПРИМЕЧАНИЕ: у MT5Sugar нет метода delete_order
# Для отмены отложенных ордеров используйте методы уровня MT5Service или MT5Account
```

**ПРЕДУПРЕЖДЕНИЕ:** Проскальзывание во время новостей может сработать по обоим ордерам.

---

### Лимиты объёма
Ограничения брокера на размер позиции.

**Получение через:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

min_vol = await service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_MIN)
max_vol = await service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_MAX)
step_vol = await service.get_symbol_double("EURUSD", market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_STEP)
```

**Используется для:** Валидации объёма.

**Валидация:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2

async def validate_volume(service, symbol, volume):
    min_vol = await service.get_symbol_double(symbol, market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_MIN)
    max_vol = await service.get_symbol_double(symbol, market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_MAX)
    step_vol = await service.get_symbol_double(symbol, market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_VOLUME_STEP)

    if volume < min_vol:
        volume = min_vol
    if volume > max_vol:
        volume = max_vol

    # Округляем до шага
    volume = round(volume / step_vol) * step_vol
    return volume
```

---

## 🔑 Термины конфигурации

### settings.json

Примеры читают свою конфигурацию из **`examples/0_common/settings.json`** — обычного JSON, загружаемого функцией `load_settings()` в `examples/0_common/demo_helpers.py`. В этом проекте нет слоя `.env` / переменных окружения.

**Поля:**
```json
{
  "user": 591129415,
  "password": "YourPassword",
  "grpc_server": "mt5.mrpc.pro:443",
  "mt_cluster": "FxPro-MT5 Demo",
  "test_symbol": "EURUSD",
  "api_key": "TRIAL",
  "host": "mt5.mrpc.pro",
  "port": 443,
  "test_volume": 0.01
}
```

- **Обязательные** (проверяются `load_settings()`): `user`, `password`, `grpc_server`, `mt_cluster`, `test_symbol`.
- **Необязательные:** `api_key` — при отсутствии берётся из переменной окружения `MRPC_API_KEY`, затем `"TRIAL"`.
- `host`, `port` и `test_volume` оставлены для справки, но **не** читаются `load_settings()` / `create_and_connect_mt5()`.

`grpc_server` — адрес шлюза MetaRPC; `mt_cluster` — имя сервера MT5, передаваемое в `connect_by_server_name()`.

**Использование:**
```python
from demo_helpers import load_settings, create_and_connect_mt5

config = load_settings()                        # читает settings.json
account = await create_and_connect_mt5(config)  # создаёт MT5Account, затем connect_by_server_name(server_name=config["mt_cluster"])
```

**ПРЕДУПРЕЖДЕНИЕ:** `settings.json` хранит реальные учётные данные — держите его вне git (добавьте в `.gitignore`).

---

## Межкомпонентные термины

### Пакетные операции
Выполнение действия сразу над несколькими позициями/ордерами.

**Методы (MT5Sugar):**
```python
# Закрыть все позиции
count = await sugar.close_all_positions()          # Все позиции
count = await sugar.close_all_positions("EURUSD")  # Только по символу
```

**Примечание:** Для удаления отложенных ордеров используйте методы уровня MT5Service или MT5Account.

**Сценарий использования:** Аварийные выходы, очистка в конце сессии, сброс стратегии.

---

### 📝 Запросы истории
Получение прошлых ордеров и позиций для анализа.

**Методы (MT5Account):**
```python
from datetime import datetime, timedelta
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as account_helper_pb2

# Получаем историю ордеров
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

history = await account.order_history(
    from_dt=start_date,
    to_dt=end_date,
    sort_mode=account_helper_pb2.BMT5_SORT_BY_OPEN_TIME_ASC,
    page_number=0,
    items_per_page=100
)

# Получаем историю позиций
positions = await account.positions_history(
    sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
    open_from=start_date,
    open_to=end_date,
    page=0,
    size=100
)
```

**Сценарий использования:** Анализ результативности, журналы сделок, валидация стратегии.

---

### Учебный проект

Примеры и вспомогательные функции PyMT5 — это учебные материалы и демонстрации API, а НЕ торговые системы для продакшена.

**Следствия:**

- Изучать код и паттерны (ДА)
- Изменять под свои нужды (ДА)
- Тестировать на демо-счетах (ДА)
- Использовать как шаблоны для построения своих стратегий (ДА)
- Не использовать как есть с реальными деньгами (НЕТ)
- Не ожидать управления рисками уровня продакшена (НЕТ)
- Не ожидать корректной обработки ошибок для всех краевых случаев (НЕТ)

**Помните:** Это учебные примеры, а не проверенные в бою продакшен-системы.

---

## Паттерны, специфичные для Python

### Обработка исключений
Механизм обработки ошибок API в Python.

**Пользовательские исключения:**
```python
from MetaRpcMT5 import ConnectExceptionMT5, ApiExceptionMT5

try:
    await account.connect_by_server_name(
        server_name="FxPro-MT5 Demo",
        base_chart_symbol="EURUSD"
    )
except ConnectExceptionMT5 as e:
    print(f"Connection failed: {e}")
except ApiExceptionMT5 as e:
    print(f"API error: {e}")
```

**Ошибки торговых операций:**
```python
try:
    ticket = await sugar.buy_market("EURUSD", 0.01)
    print(f"Position opened: ticket {ticket}")
except RuntimeError as e:
    # MT5Sugar вызывает RuntimeError, если returned_code != 10009
    print(f"Trade failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

### Подсказки типов
Необязательная статическая типизация Python для лучшей поддержки IDE.

**Весь код PyMT5 использует подсказки типов:**
```python
from typing import Optional, List
from datetime import datetime

async def get_balance(self) -> float:
    """Get account balance."""
    from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2
    return await self.service.get_account_double(
        account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
    )

async def buy_market(
    self,
    symbol: str,
    volume: float,
    sl: Optional[float] = None,
    tp: Optional[float] = None
) -> int:
    """Open BUY position at market price.

    Returns:
        int: Ticket number
    """
    pass
```

**Преимущества:**

- Автодополнение в IDE
- Статическая проверка типов (mypy)
- Лучшая документация
- Обнаружение ошибок до выполнения

---

### 🧱 Перечисления (Enums)
Перечислимые типы Python для именованных констант.

**PyMT5 использует перечисления вместо «магических» чисел:**
```python
# Перечисления MT5Sugar
from pymt5.mt5_sugar import OrderType, Period

# Перечисления protobuf
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_info_pb2
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

# Вместо «магических» чисел
order_type = OrderType.BUY  # Не 0
period = Period.TODAY       # Не 0

# Свойства символа
bid = await service.get_symbol_double(
    "EURUSD",
    market_info_pb2.SymbolInfoDoubleProperty.SYMBOL_BID  # Не 1
)

# Свойства счёта
balance = await service.get_account_double(
    account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE  # Не 0
)
```

**Документация:** [Справочник по использованию перечислений](ENUMS_USAGE_REFERENCE.md)

---

## См. также

- **[Главный обзор MT5Account](../MT5Account/MT5Account.Master.Overview.md)** — Полный справочник низкоуровневого API
- **[Обзор API MT5Service](../MT5Service/MT5Service.Overview.md)** — API обёрток среднего уровня
- **[Справочник API MT5Sugar](../MT5Sugar/MT5Sugar.Master.Overview.md)** — Высокоуровневый API Sugar
- **[Управление потоками gRPC](GRPC_STREAM_MANAGEMENT.md)** — Руководство по потоковым подпискам
- **[Справочник кодов возврата](RETURN_CODES_REFERENCE.md)** — Полный справочник кодов возврата
- **[Руководство по песочнице пользовательского кода](USERCODE_SANDBOX_GUIDE.md)** — Как писать собственный код
- **[Ваш первый проект](Your_First_Project.md)** — Руководство по настройке и быстрому старту
- **[Справочник по использованию перечислений](ENUMS_USAGE_REFERENCE.md)** — Все доступные перечисления
- **[Руководство по инспектору Protobuf](PROTOBUF_INSPECTOR_GUIDE.md)** — Исследование типов protobuf

---

"Торгуйте безопасно, пишите код чисто, и пусть ваши асинхронные функции всегда изящно ждут (await)."
