# Размещение ордера SELL STOP (`sell_stop`)

> **Sugar-метод:** Размещает отложенный ордер SELL STOP для продажи ниже текущей цены (вход на пробое вниз).

**Информация об API:**

* **Метод:** `sugar.sell_stop(symbol, volume, price, comment, magic)`
* **Возвращает:** номер тикета ордера (`int`)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def sell_stop(
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
| `price` | `float` | Да | `0.0` | Стоп-цена (должна быть НИЖЕ текущего BID) |
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

- Создаёт отложенный ордер SELL STOP
- Ордер срабатывает, когда цена BID падает до указанного уровня
- Автоматически преобразуется в позицию SELL при срабатывании
- Ордер остаётся отложенным до срабатывания или отмены

**Ключевое поведение:**

- Стоп-цена SELL STOP должна быть НИЖЕ текущего BID
- Используется для торговли на пробое вниз (продажа при пробое поддержки)
- Исполняется по рынку при достижении стоп-цены (не по точной цене)
- Полезен для стратегий следования за трендом и пробоя поддержки

---

## ⚡ Под капотом

```
MT5Sugar.sell_stop()
    ↓ builds OrderSendRequest
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar строит OrderSendRequest с TMT5_ORDER_TYPE_SELL_STOP
2. Sugar вызывает Service.place_order() с запросом
3. Service передаёт в Account.order_send()
4. Account отправляет gRPC-запрос в терминал
5. Sugar проверяет returned_code == 10009 (TRADE_RETCODE_DONE)
6. Возвращает тикет ордера из result.order
7. Ордер остаётся отложенным до достижения ценой стоп-уровня

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:778`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## Когда использовать

**Используйте `sell_stop()`, когда:**

- Торгуете пробои вниз ниже поддержки
- Следуете нисходящему тренду (продажа на импульсе)
- Хотите войти только при подтверждении направления ценой
- Реализуете стратегии пробоя вниз

**Не используйте, когда:**

- Нужна немедленная позиция (используйте `sell_market()`)
- Хотите продать по более высокой цене (используйте `sell_limit()`)
- Цена может развернуться до достижения стопа
- На флэтовом рынке (ложные пробои вниз)

---

## 🔗 Примеры

### Пример 1: Базовый вход на пробое вниз

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def breakdown_sell():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Текущий BID: 1.0850
    # Поддержка на 1.0830
    # Разместить SELL STOP ниже поддержки
    ticket = await sugar.sell_stop(
        price=1.0825,
        volume=0.1,
        comment="Breakdown sell at 1.0825"
    )

    print(f"SELL STOP order placed: #{ticket}")

# Вывод:
# SELL STOP order placed: #123456794
```

### Пример 2: Несколько уровней поддержки

```python
async def tiered_breakdown():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Текущая цена: 1.0850
    # Ключевые уровни поддержки
    supports = [1.0830, 1.0800, 1.0770]

    tickets = []
    for support in supports:
        # Разместить SELL STOP чуть ниже каждой поддержки
        stop_price = support - 0.0005  # на 5 пунктов ниже

        ticket = await sugar.sell_stop(
            price=stop_price,
            volume=0.01,
            comment=f"Breakdown {support}"
        )
        tickets.append(ticket)
        print(f"SELL STOP at {stop_price}: #{ticket}")

    print(f"Total breakdown orders: {len(tickets)}")
```

### Пример 3: Следование за трендом с SELL STOP

```python
async def downtrend_following():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Получить текущий минимум
    bid = await sugar.get_bid()

    # Разместить SELL STOP на 20 пунктов ниже текущей цены
    # (входит только если нисходящий тренд продолжается)
    symbol_info = await sugar.get_symbol_info()
    point = symbol_info.point

    stop_price = bid - (20 * point * 10)  # на 20 пунктов ниже

    ticket = await sugar.sell_stop(
        price=stop_price,
        volume=0.1,
        comment="Downtrend confirmation"
    )

    print(f"SELL STOP at {stop_price} (confirms downtrend)")
    print(f"Order: #{ticket}")
```

---

## Частые ошибки

**Ошибка 1: Цена выше текущего BID**
```python
# ОШИБКА: SELL STOP должен быть НИЖЕ текущей цены
# Текущий BID: 1.0850
try:
    ticket = await sugar.sell_stop(price=1.0860)  # Выше текущей цены
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price for SELL STOP"
```

**Решение:** убедитесь, что стоп-цена ниже текущего BID
```python
bid = await sugar.get_bid()  # 1.0850
stop_price = bid - 0.0020    # 1.0830 (ниже текущей)
ticket = await sugar.sell_stop(price=stop_price)
```

**Ошибка 2: Путаница SELL STOP с SELL LIMIT**
```python
# SELL LIMIT: продажа ВЫШЕ текущей цены (лучшая цена)
# SELL STOP: продажа НИЖЕ текущей цены (пробой вниз)

# Текущая цена: 1.0850

# LIMIT: продать, если цена поднимается до 1.0870
sell_limit = await sugar.sell_limit(price=1.0870)

# STOP: продать, если цена падает до 1.0830
sell_stop = await sugar.sell_stop(price=1.0830)
```

**Ошибка 3: Ложные пробои вниз**
```python
# Цена касается уровня стопа, затем разворачивается
# Ордер срабатывает на 1.0830, затем цена поднимается до 1.0850
# Результат: немедленный убыток

# Стоп-ордер размещён на 1.0830
ticket = await sugar.sell_stop(price=1.0830)
# Цена резко падает до 1.0829 (срабатывает ордер)
# Цена поднимается обратно до 1.0850 (убыток)
```

**Решение:** размещайте стоп за значимым уровнем с буфером
```python
# Добавить буфер за поддержкой
support = 1.0830
buffer = 0.0005  # буфер 5 пунктов

stop_price = support - buffer  # 1.0825
ticket = await sugar.sell_stop(price=stop_price)
```

---

## Советы профи

**Совет 1: Используйте с дневным минимумом**
```python
# Стратегия пробоя вниз: продажа ниже вчерашнего минимума
yesterday_low = 1.0835

# Разместить SELL STOP на 5 пунктов ниже
stop_price = yesterday_low - 0.0005

ticket = await sugar.sell_stop(
    price=stop_price,
    volume=0.1,
    comment="Below yesterday low"
)
```

**Совет 2: Сочетайте с несколькими таймфреймами**
```python
# Разместить SELL STOP ниже поддержки на нескольких таймфреймах
h4_support = 1.0830
h1_support = 1.0840
m15_support = 1.0845

# Использовать сильнейшую (самую низкую) поддержку
main_support = min(h4_support, h1_support, m15_support)

# Разместить ниже сильнейшей поддержки
stop_price = main_support - 0.0005

ticket = await sugar.sell_stop(
    price=stop_price,
    comment="Multi-timeframe breakdown"
)
```

---

## 📚 См. также

- [buy_stop](buy_stop.md) - Размещение отложенного ордера BUY STOP
- [sell_limit](sell_limit.md) - Размещение отложенного ордера SELL LIMIT
- [sell_market](sell_market.md) - Немедленное открытие позиции SELL

