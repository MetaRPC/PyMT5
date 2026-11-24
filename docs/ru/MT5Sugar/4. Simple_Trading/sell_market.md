# Открытие позиции SELL по рынку (`sell_market`)

> **Sugar-метод:** Открывает позицию SELL по текущей рыночной цене за один вызов.

**Информация об API:**

* **Метод:** `sugar.sell_market(symbol, volume, comment, magic)`
* **Возвращает:** номер тикета позиции (`int`)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def sell_market(
    self,
    symbol: Optional[str] = None,
    volume: float = 0.01,
    comment: str = "",
    magic: int = 0
) -> int
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | Нет | `None` | Торговый символ (использует значение по умолчанию, если не указан) |
| `volume` | `float` | Нет | `0.01` | Объём позиции в лотах |
| `comment` | `str` | Нет | `""` | Комментарий к ордеру (виден в терминале) |
| `magic` | `int` | Нет | `0` | Magic number для идентификации ордера |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `int` | Номер тикета позиции (уникальный идентификатор) |

**Вызывает:**

- `ValueError`, если символ не указан и не задан по умолчанию
- `RuntimeError`, если исполнение ордера не удалось (returned_code != 10009)

---

## 🏛️ Основное

**Что делает:**

- Получает текущую цену BID из терминала
- Создаёт запрос на рыночный ордер SELL
- Исполняет ордер с допуском проскальзывания 10 пунктов
- Возвращает номер тикета при успехе

**Ключевое поведение:**

- SELL = прибыль при ПАДЕНИИ цены
- Использует цену BID (более низкую)
- Проскальзывание по умолчанию: 10 пунктов
- Вызывает исключение, если ордер не удался
- Позиция открывается немедленно по рынку

---

## ⚡ Под капотом

```
MT5Sugar.sell_market()
    ↓ fetches price
MT5Service.get_symbol_tick()
    ↓ builds OrderSendRequest
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar получает текущий тик через слой Service
2. Sugar строит OrderSendRequest с TMT5_ORDER_TYPE_SELL
3. Sugar вызывает Service.place_order() с запросом
4. Service передаёт в Account.order_send()
5. Account отправляет gRPC-запрос в терминал
6. Sugar проверяет returned_code == 10009 (TRADE_RETCODE_DONE)
7. Возвращает номер тикета из result.order

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:613`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## Когда использовать

**Используйте `sell_market()`, когда:**

- Вы ожидаете ПАДЕНИЯ цены
- Нужно немедленное исполнение позиции
- Не нужны Stop Loss или Take Profit (простой вход)
- Строите базовые торговые стратегии

**Не используйте, когда:**

- Нужны SL/TP при входе (используйте `sell_market_with_sltp()`)
- Хотите войти по конкретной цене (используйте `sell_limit()` или `sell_stop()`)
- Рынок закрыт или неликвиден
- Цена движется слишком быстро (рассмотрите отложенные ордера)

---

## 🔗 Примеры

### Пример 1: Базовая позиция SELL

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def simple_sell():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию SELL с объёмом по умолчанию (0.01 лота)
    ticket = await sugar.sell_market()
    print(f"Position opened: #{ticket}")

# Вывод:
# Position opened: #123456790
```

### Пример 2: SELL с пользовательскими параметрами

```python
async def sell_with_params():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию SELL 0.1 лота на GBPUSD
    ticket = await sugar.sell_market(
        symbol="GBPUSD",
        volume=0.1,
        comment="Bear trend entry",
        magic=12345
    )

    print(f"GBPUSD SELL: ticket #{ticket}")
```

### Пример 3: Стратегия хеджирования (BUY + SELL)

```python
async def hedging_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    try:
        # Открыть противоположные позиции для хеджирования
        buy_ticket = await sugar.buy_market(volume=0.1, magic=1000)
        sell_ticket = await sugar.sell_market(volume=0.1, magic=1000)

        print(f"Hedge opened: BUY #{buy_ticket}, SELL #{sell_ticket}")

        # Отслеживать и позже закрыть прибыльную сторону
        balance = await sugar.get_balance()
        print(f"Balance: ${balance}")

    except RuntimeError as e:
        print(f"Hedging failed: {e}")
```

---

## Частые ошибки

**Ошибка 1: Путаница BUY и SELL**
```python
# НЕВЕРНО: думать, что SELL означает «продать для закрытия» позиции
# SELL открывает НОВУЮ позицию, прибыльную при падении цены
ticket = await sugar.sell_market()  # Открывает новую позицию SELL

# Чтобы закрыть позицию, используйте close_position()
await sugar.close_position(ticket)
```

**Решение:** помните, SELL = открытие короткой позиции
```python
# Открыть короткую (SELL) позицию
sell_ticket = await sugar.sell_market()  # Прибыль при падении цены

# Закрыть эту позицию
await sugar.close_position(sell_ticket)
```

**Ошибка 2: Мысленное использование ASK вместо BID**
```python
# SELL использует цену BID (более низкую)
# Если текущие цены: BID=1.08430, ASK=1.08445
# SELL открывается по 1.08430 (BID)
# Прибыль, если цена опускается ниже 1.08430
```

**Решение:** помните: SELL использует BID, BUY использует ASK
```python
bid = await sugar.get_bid()    # 1.08430
ask = await sugar.get_ask()    # 1.08445

# SELL открывается по BID
sell_ticket = await sugar.sell_market()  # Открывается по 1.08430
```

**Ошибка 3: Неверные ожидания по направлению прибыли**
```python
# НЕВЕРНО: ожидать прибыль при росте цены
ticket = await sugar.sell_market()
# Цена идёт с 1.0843 → 1.0850
# Результат: УБЫТОК (не прибыль)

# ВЕРНО: прибыль при падении цены
ticket = await sugar.sell_market()
# Цена идёт с 1.0843 → 1.0835
# Результат: ПРИБЫЛЬ
```

---

## Советы профи

**Совет 1: Проверяйте тренд перед SELL**
```python
# Простое пересечение скользящей средней для тренда
current_price = await sugar.get_bid()

# SELL, когда цена ниже скользящей средней (нисходящий тренд)
if current_price < moving_average:
    ticket = await sugar.sell_market()
```

**Совет 2: Сочетайте с мониторингом позиции**
```python
import asyncio

# Открыть SELL и отслеживать прибыль
ticket = await sugar.sell_market(volume=0.1)

# Опрашивать прибыль позиции, пока не достигнута цель
while True:
    pos = await sugar.get_position_by_ticket(ticket)
    if pos is None:
        break  # позиция больше не открыта
    print(f"Current profit: ${pos.profit:.2f}")

    # Закрыть, если достигнута цель по прибыли
    if pos.profit >= 50.0:
        await sugar.close_position(ticket)
        break

    await asyncio.sleep(1)
```

**Совет 3: Проверяйте спред перед SELL**
```python
# Убедиться в узком спреде перед продажей
spread = await sugar.get_spread()

if spread < 0.0002:  # 2 пункта для EURUSD
    ticket = await sugar.sell_market()
else:
    print(f"Spread too wide for SELL: {spread}")
```

---

## 📚 См. также

- [buy_market](buy_market.md) - Открытие позиции BUY по рынку
- [sell_limit](sell_limit.md) - Размещение отложенного ордера SELL LIMIT
- [sell_stop](sell_stop.md) - Размещение отложенного ордера SELL STOP
- [sell_market_with_sltp](../5.%20Trading_With_SLTP/sell_market_with_sltp.md) - Открытие SELL с SL/TP
- [close_position](../6.%20Position_Management/close_position.md) - Закрытие позиции по тикету
