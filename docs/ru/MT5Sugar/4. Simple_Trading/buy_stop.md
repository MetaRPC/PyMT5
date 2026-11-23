# Размещение ордера BUY STOP (`buy_stop`)

> **Sugar-метод:** Размещает отложенный ордер BUY STOP для покупки выше текущей цены (вход на пробое).

**Информация об API:**

* **Метод:** `sugar.buy_stop(symbol, volume, price, comment, magic)`
* **Возвращает:** номер тикета ордера (`int`)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def buy_stop(
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
| `price` | `float` | Да | `0.0` | Стоп-цена (должна быть ВЫШЕ текущего ASK) |
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

- Создаёт отложенный ордер BUY STOP
- Ордер срабатывает, когда цена ASK поднимается до указанного уровня
- Автоматически преобразуется в позицию BUY при срабатывании
- Ордер остаётся отложенным до срабатывания или отмены

**Ключевое поведение:**

- Стоп-цена BUY STOP должна быть ВЫШЕ текущего ASK
- Используется для торговли на пробое (покупка при пробое сопротивления)
- Исполняется по рынку при достижении стоп-цены (не по точной цене)
- Полезен для стратегий следования за трендом

---

## ⚡ Под капотом

```
MT5Sugar.buy_stop()
    ↓ builds OrderSendRequest
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar строит OrderSendRequest с TMT5_ORDER_TYPE_BUY_STOP
2. Sugar вызывает Service.place_order() с запросом
3. Service передаёт в Account.order_send()
4. Account отправляет gRPC-запрос в терминал
5. Sugar проверяет returned_code == 10009 (TRADE_RETCODE_DONE)
6. Возвращает тикет ордера из result.order
7. Ордер остаётся отложенным до достижения ценой стоп-уровня

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:738`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## Когда использовать

**Используйте `buy_stop()`, когда:**

- Торгуете пробои выше сопротивления
- Следуете восходящему тренду (покупка на импульсе)
- Хотите войти только при подтверждении направления ценой
- Реализуете стратегии пробоя

**Не используйте, когда:**

- Нужна немедленная позиция (используйте `buy_market()`)
- Хотите купить по более низкой цене (используйте `buy_limit()`)
- Цена может развернуться до достижения стопа
- На флэтовом рынке (ложные пробои)

---

## 🔗 Примеры

### Пример 1: Базовый вход на пробое

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def breakout_buy():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Текущий ASK: 1.0850
    # Сопротивление на 1.0870
    # Разместить BUY STOP выше сопротивления
    ticket = await sugar.buy_stop(
        price=1.0875,
        volume=0.1,
        comment="Breakout buy at 1.0875"
    )

    print(f"BUY STOP order placed: #{ticket}")

# Вывод:
# BUY STOP order placed: #123456793
```

### Пример 2: Несколько уровней пробоя

```python
async def tiered_breakout():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Текущая цена: 1.0850
    # Ключевые уровни сопротивления
    resistances = [1.0870, 1.0900, 1.0930]

    tickets = []
    for resistance in resistances:
        # Разместить BUY STOP чуть выше каждого сопротивления
        stop_price = resistance + 0.0005  # на 5 пунктов выше

        ticket = await sugar.buy_stop(
            price=stop_price,
            volume=0.01,
            comment=f"Breakout {resistance}"
        )
        tickets.append(ticket)
        print(f"BUY STOP at {stop_price}: #{ticket}")

    print(f"Total breakout orders: {len(tickets)}")
```

### Пример 3: Следование за трендом с BUY STOP

```python
async def trend_following():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Получить текущий максимум
    ask = await sugar.get_ask()

    # Разместить BUY STOP на 20 пунктов выше текущей цены
    # (входит только если восходящий тренд продолжается)
    symbol_info = await sugar.get_symbol_info()
    point = symbol_info.point

    stop_price = ask + (20 * point * 10)  # на 20 пунктов выше

    ticket = await sugar.buy_stop(
        price=stop_price,
        volume=0.1,
        comment="Trend confirmation"
    )

    print(f"BUY STOP at {stop_price} (confirms uptrend)")
    print(f"Order: #{ticket}")
```

---

## Частые ошибки

**Ошибка 1: Цена ниже текущего ASK**
```python
# ОШИБКА: BUY STOP должен быть ВЫШЕ текущей цены
# Текущий ASK: 1.0850
try:
    ticket = await sugar.buy_stop(price=1.0840)  # Ниже текущей цены
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price for BUY STOP"
```

**Решение:** убедитесь, что стоп-цена выше текущего ASK
```python
ask = await sugar.get_ask()  # 1.0850
stop_price = ask + 0.0020    # 1.0870 (выше текущей)
ticket = await sugar.buy_stop(price=stop_price)
```

**Ошибка 2: Путаница BUY STOP с BUY LIMIT**
```python
# BUY LIMIT: покупка НИЖЕ текущей цены (лучшая цена)
# BUY STOP: покупка ВЫШЕ текущей цены (пробой)

# Текущая цена: 1.0850

# LIMIT: купить, если цена падает до 1.0840
buy_limit = await sugar.buy_limit(price=1.0840)

# STOP: купить, если цена поднимается до 1.0870
buy_stop = await sugar.buy_stop(price=1.0870)
```

**Ошибка 3: Ложные пробои**
```python
# Цена касается уровня стопа, затем разворачивается
# Ордер срабатывает на 1.0870, затем цена падает до 1.0850
# Результат: немедленный убыток

# Стоп-ордер размещён на 1.0870
ticket = await sugar.buy_stop(price=1.0870)
# Цена подскакивает до 1.0871 (срабатывает ордер)
# Цена падает обратно до 1.0850 (убыток)
```

**Решение:** размещайте стоп за значимым уровнем с буфером
```python
# Добавить буфер за сопротивлением
resistance = 1.0870
buffer = 0.0005  # буфер 5 пунктов

stop_price = resistance + buffer  # 1.0875
ticket = await sugar.buy_stop(price=stop_price)
```

---

## Советы профи

**Совет 1: Сочетайте со Stop Loss**
```python
# Разместить BUY STOP с планом немедленного SL
stop_price = 1.0870
stop_loss = 1.0850  # на 20 пунктов ниже входа

# Разместить ордер
ticket = await sugar.buy_stop(price=stop_price)

# После исполнения ордера (становится позицией) добавить SL
# Отслеживать и изменить, когда позиция откроется
```

**Совет 2: Используйте с дневным максимумом**
```python
# Стратегия пробоя: покупка выше вчерашнего максимума
yesterday_high = 1.0865

# Разместить BUY STOP на 5 пунктов выше
stop_price = yesterday_high + 0.0005

ticket = await sugar.buy_stop(
    price=stop_price,
    volume=0.1,
    comment="Above yesterday high"
)
```

---

## 📚 См. также

- [sell_stop](sell_stop.md) - Размещение отложенного ордера SELL STOP
- [buy_limit](buy_limit.md) - Размещение отложенного ордера BUY LIMIT
- [buy_market](buy_market.md) - Немедленное открытие позиции BUY
