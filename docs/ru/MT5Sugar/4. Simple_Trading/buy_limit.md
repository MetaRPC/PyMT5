# Размещение ордера BUY LIMIT (`buy_limit`)

> **Sugar-метод:** Размещает отложенный ордер BUY LIMIT для покупки ниже текущей цены.

**Информация об API:**

* **Метод:** `sugar.buy_limit(symbol, volume, price, comment, magic)`
* **Возвращает:** номер тикета ордера (`int`)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def buy_limit(
    self,
    symbol: Optional[str] = None,
    volume: float = 0.01,
    price: float = 0.0,
    comment: str = "",
    magic: int = 0
) -> int
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | Нет | `None` | Торговый символ (использует значение по умолчанию, если не указан) |
| `volume` | `float` | Нет | `0.01` | Объём ордера в лотах |
| `price` | `float` | Да | `0.0` | Цена лимита (должна быть НИЖЕ текущего ASK) |
| `comment` | `str` | Нет | `""` | Комментарий к ордеру (виден в терминале) |
| `magic` | `int` | Нет | `0` | Magic number для идентификации ордера |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `int` | Номер тикета ордера (уникальный идентификатор) |

**Вызывает:**

- `ValueError`, если символ не указан и не задан по умолчанию
- `RuntimeError`, если размещение ордера не удалось (returned_code != 10009)

---

## 🏛️ Основное

**Что делает:**

- Создаёт отложенный ордер BUY LIMIT
- Ордер срабатывает, когда цена ASK падает до указанного уровня
- Автоматически преобразуется в позицию BUY при срабатывании
- Ордер остаётся отложенным до срабатывания или отмены

**Ключевое поведение:**

- Цена BUY LIMIT должна быть НИЖЕ текущего ASK
- Ордер исполняется только по указанной цене или лучше
- Используется для покупки по более низкой цене (покупка на просадке)
- Не использует проскальзывание (лимитный ордер исполняется по точной цене)

---

## ⚡ Под капотом

```
MT5Sugar.buy_limit()
    ↓ builds OrderSendRequest
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar строит OrderSendRequest с TMT5_ORDER_TYPE_BUY_LIMIT
2. Sugar вызывает Service.place_order() с запросом
3. Service передаёт в Account.order_send()
4. Account отправляет gRPC-запрос в терминал
5. Sugar проверяет returned_code == 10009 (TRADE_RETCODE_DONE)
6. Возвращает тикет ордера из result.order
7. Ордер остаётся отложенным в терминале до достижения цены

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:658`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## Когда использовать

**Используйте `buy_limit()`, когда:**

- Хотите купить по более низкой цене (ждёте отката)
- Планируете вход до того, как цена достигнет уровня
- Избегаете уплаты спреда при немедленном исполнении
- Реализуете стратегию покупки на просадке

**Не используйте, когда:**

- Нужна немедленная позиция (используйте `buy_market()`)
- Хотите купить выше текущей цены (используйте `buy_stop()`)
- Цена может никогда не достичь уровня лимита (рассмотрите рыночный ордер)

---

## 🔗 Примеры

### Пример 1: Базовый ордер Buy Limit

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def buy_the_dip():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Текущий ASK: 1.0850
    # Разместить BUY LIMIT по 1.0840 (ниже текущей цены)
    ticket = await sugar.buy_limit(
        price=1.0840,
        volume=0.1,
        comment="Buy dip at 1.0840"
    )

    print(f"BUY LIMIT order placed: #{ticket}")

# Вывод:
# BUY LIMIT order placed: #123456791
```

### Пример 2: Несколько лимитных ордеров (сеточная торговля)

```python
async def buy_grid():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Текущая цена: 1.0850
    # Разместить ордера BUY LIMIT на нескольких уровнях
    levels = [1.0840, 1.0830, 1.0820, 1.0810]

    tickets = []
    for price in levels:
        ticket = await sugar.buy_limit(
            price=price,
            volume=0.01,
            comment=f"Grid buy at {price}"
        )
        tickets.append(ticket)
        print(f"Order #{ticket} at {price}")

    print(f"Total orders placed: {len(tickets)}")
```

### Пример 3: Условный лимитный ордер

```python
async def smart_limit():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Получить текущую цену
    ask = await sugar.get_ask()

    # Разместить лимит на 20 пунктов ниже текущей цены
    symbol_info = await sugar.get_symbol_info()
    point = symbol_info.point

    limit_price = ask - (20 * point * 10)  # на 20 пунктов ниже

    # Убедиться, что цена разумна
    if limit_price > 0:
        ticket = await sugar.buy_limit(
            price=limit_price,
            volume=0.1,
            comment=f"Limit 20 pips below"
        )
        print(f"BUY LIMIT set at {limit_price}")
    else:
        print("Invalid limit price calculated")
```

---

## Частые ошибки

**Ошибка 1: Цена выше текущего ASK**
```python
# ОШИБКА: BUY LIMIT должен быть НИЖЕ текущей цены
# Текущий ASK: 1.0850
try:
    ticket = await sugar.buy_limit(price=1.0860)  # Выше текущей цены
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price for BUY LIMIT"
```

**Решение:** убедитесь, что цена лимита ниже текущего ASK
```python
ask = await sugar.get_ask()  # 1.0850
limit_price = ask - 0.0010   # 1.0840 (ниже текущей)
ticket = await sugar.buy_limit(price=limit_price)
```

**Ошибка 2: Неверный формат цены**
```python
# ОШИБКА: использование пунктов вместо цены
ticket = await sugar.buy_limit(price=20)  # НЕВЕРНО: 20 — это не цена
```

**Решение:** используйте фактическую цену, а не пункты
```python
# Сначала получить текущую цену
ask = await sugar.get_ask()  # 1.0850

# Рассчитать целевую цену
target = ask - 0.0020  # на 20 пунктов ниже для EURUSD

ticket = await sugar.buy_limit(price=target)  # 1.0830
```

---

## Советы профи

**Совет 1: Используйте разрядность символа для точности цены**
```python
# Убедиться, что у цены верное число знаков после запятой
symbol_info = await sugar.get_symbol_info()
digits = symbol_info.digits

# Округлить цену лимита до разрядности символа
ask = await sugar.get_ask()
limit_price = round(ask - 0.0020, digits)

ticket = await sugar.buy_limit(price=limit_price)
```

**Совет 2: Отслеживайте отложенные ордера**
```python
# Разместить лимитный ордер
ticket = await sugar.buy_limit(price=1.0840)

# Проверить, ордер ещё отложен или исполнен
orders = await sugar._service.get_opened_orders()

for order in orders.order_infos:
    if order.ticket == ticket:
        print(f"Order {ticket} still pending")
        break
else:
    print(f"Order {ticket} filled (became position)")
```

**Совет 3: Сочетайте со Stop Loss**
```python
# Разместить лимитный ордер, затем добавить SL после исполнения
ticket = await sugar.buy_limit(price=1.0840, volume=0.1)

# Дождаться исполнения ордера (становится позицией)
# Затем добавить стоп-лосс
try:
    await sugar.modify_position_sltp(
        ticket=ticket,
        sl=1.0820  # 20 пунктов SL
    )
except ValueError:
    print("Order not yet filled")
```

---

## 📚 См. также

- [sell_limit](sell_limit.md) - Размещение отложенного ордера SELL LIMIT
- [buy_stop](buy_stop.md) - Размещение отложенного ордера BUY STOP
- [buy_market](buy_market.md) - Немедленное открытие позиции BUY
- [buy_limit_with_sltp](../5.%20Trading_With_SLTP/buy_limit_with_sltp.md) - BUY LIMIT с SL/TP
