# Размещение ордера SELL LIMIT (`sell_limit`)

> **Sugar-метод:** Размещает отложенный ордер SELL LIMIT для продажи выше текущей цены.

**Информация об API:**

* **Метод:** `sugar.sell_limit(symbol, volume, price, comment, magic)`
* **Возвращает:** номер тикета ордера (`int`)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def sell_limit(
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
| `price` | `float` | Да | `0.0` | Цена лимита (должна быть ВЫШЕ текущего BID) |
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

- Создаёт отложенный ордер SELL LIMIT
- Ордер срабатывает, когда цена BID поднимается до указанного уровня
- Автоматически преобразуется в позицию SELL при срабатывании
- Ордер остаётся отложенным до срабатывания или отмены

**Ключевое поведение:**

- Цена SELL LIMIT должна быть ВЫШЕ текущего BID
- Ордер исполняется только по указанной цене или лучше
- Используется для продажи по более высокой цене (продажа на росте)
- Не использует проскальзывание (лимитный ордер исполняется по точной цене)

---

## ⚡ Под капотом

```
MT5Sugar.sell_limit()
    ↓ builds OrderSendRequest
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar строит OrderSendRequest с TMT5_ORDER_TYPE_SELL_LIMIT
2. Sugar вызывает Service.place_order() с запросом
3. Service передаёт в Account.order_send()
4. Account отправляет gRPC-запрос в терминал
5. Sugar проверяет returned_code == 10009 (TRADE_RETCODE_DONE)
6. Возвращает тикет ордера из result.order
7. Ордер остаётся отложенным в терминале до достижения цены

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:698`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## Когда использовать

**Используйте `sell_limit()`, когда:**

- Хотите продать по более высокой цене (ждёте роста)
- Планируете вход до того, как цена достигнет уровня
- Ожидаете роста цены с последующим падением (продажа на вершине)
- Реализуете стратегию продажи на росте

**Не используйте, когда:**

- Нужна немедленная позиция (используйте `sell_market()`)
- Хотите продать ниже текущей цены (используйте `sell_stop()`)
- Цена может никогда не достичь уровня лимита (рассмотрите рыночный ордер)

---

## 🔗 Примеры

### Пример 1: Базовый ордер Sell Limit

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def sell_the_rally():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Текущий BID: 1.0850
    # Разместить SELL LIMIT по 1.0860 (выше текущей цены)
    ticket = await sugar.sell_limit(
        price=1.0860,
        volume=0.1,
        comment="Sell rally at 1.0860"
    )

    print(f"SELL LIMIT order placed: #{ticket}")

# Вывод:
# SELL LIMIT order placed: #123456792
```

### Пример 2: Цели по тейк-профиту

```python
async def profit_targets():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Сначала открыть позицию BUY
    buy_ticket = await sugar.buy_market(volume=0.3)
    print(f"BUY position: #{buy_ticket}")

    # Разместить ордера SELL LIMIT как цели по прибыли
    # Текущая цена: 1.0850
    bid = await sugar.get_bid()

    targets = [
        (0.1, bid + 0.0030),  # Тейк-профит 30 пунктов: 0.1 лота
        (0.1, bid + 0.0050),  # Тейк-профит 50 пунктов: 0.1 лота
        (0.1, bid + 0.0100)   # Тейк-профит 100 пунктов: 0.1 лота
    ]

    for volume, price in targets:
        ticket = await sugar.sell_limit(
            price=price,
            volume=volume,
            comment=f"TP at {price}"
        )
        print(f"Profit target #{ticket} at {price}")
```

### Пример 3: Продажа на уровне сопротивления

```python
async def sell_at_resistance():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Известный уровень сопротивления
    resistance = 1.0900

    # Текущая цена
    bid = await sugar.get_bid()

    # Размещать ордер, только если ниже сопротивления
    if bid < resistance:
        ticket = await sugar.sell_limit(
            price=resistance,
            volume=0.1,
            comment="Sell at resistance"
        )
        print(f"SELL LIMIT at resistance {resistance}: #{ticket}")

        # Расстояние до сопротивления
        pips_away = (resistance - bid) / 0.0001
        print(f"Resistance is {pips_away:.1f} pips away")
    else:
        print("Already above resistance level")
```

---

## Частые ошибки

**Ошибка 1: Цена ниже текущего BID**
```python
# ОШИБКА: SELL LIMIT должен быть ВЫШЕ текущей цены
# Текущий BID: 1.0850
try:
    ticket = await sugar.sell_limit(price=1.0840)  # Ниже текущей цены
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price for SELL LIMIT"
```

**Решение:** убедитесь, что цена лимита выше текущего BID
```python
bid = await sugar.get_bid()  # 1.0850
limit_price = bid + 0.0010   # 1.0860 (выше текущей)
ticket = await sugar.sell_limit(price=limit_price)
```

**Ошибка 2: Путаница с закрытием BUY**
```python
# НЕВЕРНО: думать, что SELL LIMIT закроет позицию BUY
buy_ticket = await sugar.buy_market()

# Это НЕ закрывает позицию BUY
# Это создаёт НОВЫЙ отложенный ордер SELL LIMIT
sell_ticket = await sugar.sell_limit(price=1.0870)

# Чтобы закрыть позицию BUY, используйте:
await sugar.close_position(buy_ticket)
```

**Ошибка 3: Слишком далеко от текущей цены**
```python
# Ордер может никогда не исполниться, если цена слишком далеко
bid = await sugar.get_bid()  # 1.0850

# Размещение на 500 пунктов выше (может не достичь)
ticket = await sugar.sell_limit(price=bid + 0.0500)  # 1.1350
# Ордер остаётся отложенным бесконечно
```

**Решение:** используйте реалистичные целевые цены
```python
bid = await sugar.get_bid()

# Разумная цель: на 20-50 пунктов выше
realistic_target = bid + 0.0030  # 30 пунктов
ticket = await sugar.sell_limit(price=realistic_target)
```

---

## Советы профи

**Совет 1: Стратегия сеточной продажи**
```python
# Разместить несколько ордеров SELL LIMIT выше текущей цены
bid = await sugar.get_bid()

# Создать сетку каждые 10 пунктов
for i in range(1, 6):
    price = bid + (i * 0.0010)  # +10, +20, +30, +40, +50 пунктов
    ticket = await sugar.sell_limit(
        price=price,
        volume=0.01,
        comment=f"Grid sell {i}"
    )
    print(f"Grid level {i}: {price}")
```

**Совет 2: Сочетайте с поддержкой/сопротивлением**
```python
# Технический анализ: разместить ордер на сопротивлении
resistance_levels = [1.0900, 1.0950, 1.1000]

bid = await sugar.get_bid()

# Разместить SELL LIMIT на ближайшем сопротивлении выше
for level in resistance_levels:
    if level > bid:
        ticket = await sugar.sell_limit(
            price=level,
            volume=0.1,
            comment=f"Resistance at {level}"
        )
        print(f"Order placed at resistance: {level}")
        break
```

---

## 📚 См. также

- [buy_limit](buy_limit.md) - Размещение отложенного ордера BUY LIMIT
- [sell_stop](sell_stop.md) - Размещение отложенного ордера SELL STOP
- [sell_market](sell_market.md) - Немедленное открытие позиции SELL
- [sell_limit_with_sltp](../5.%20Trading_With_SLTP/sell_limit_with_sltp.md) - SELL LIMIT с SL/TP
