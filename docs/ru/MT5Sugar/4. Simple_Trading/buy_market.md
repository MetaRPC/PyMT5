# Открытие позиции BUY по рынку (`buy_market`)

> **Sugar-метод:** Открывает позицию BUY по текущей рыночной цене за один вызов.

**Информация об API:**

* **Метод:** `sugar.buy_market(symbol, volume, comment, magic)`
* **Возвращает:** номер тикета позиции (`int`)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def buy_market(
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

- Получает текущую цену ASK из терминала
- Создаёт запрос на рыночный ордер BUY
- Исполняет ордер с допуском проскальзывания 10 пунктов
- Возвращает номер тикета при успехе

**Ключевое поведение:**

- BUY = прибыль при РОСТЕ цены
- Использует цену ASK (более высокую)
- Проскальзывание по умолчанию: 10 пунктов
- Вызывает исключение, если ордер не удался
- Позиция открывается немедленно по рынку

---

## ⚡ Под капотом

```
MT5Sugar.buy_market()
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
2. Sugar строит OrderSendRequest с TMT5_ORDER_TYPE_BUY
3. Sugar вызывает Service.place_order() с запросом
4. Service передаёт в Account.order_send()
5. Account отправляет gRPC-запрос в терминал
6. Sugar проверяет returned_code == 10009 (TRADE_RETCODE_DONE)
7. Возвращает номер тикета из result.order

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:568`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## Когда использовать

**Используйте `buy_market()`, когда:**

- Вы ожидаете РОСТА цены
- Нужно немедленное исполнение позиции
- Не нужны Stop Loss или Take Profit (простой вход)
- Строите базовые торговые стратегии

**Не используйте, когда:**

- Нужны SL/TP при входе (используйте `buy_market_with_sltp()`)
- Хотите войти по конкретной цене (используйте `buy_limit()` или `buy_stop()`)
- Рынок закрыт или неликвиден
- Цена движется слишком быстро (рассмотрите отложенные ордера)

---

## 🔗 Примеры

### Пример 1: Базовая позиция BUY

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def simple_buy():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию BUY с объёмом по умолчанию (0.01 лота)
    ticket = await sugar.buy_market()
    print(f"Position opened: #{ticket}")

# Вывод:
# Position opened: #123456789
```

### Пример 2: BUY с пользовательскими параметрами

```python
async def buy_with_params():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию BUY 0.1 лота на GBPUSD
    ticket = await sugar.buy_market(
        symbol="GBPUSD",
        volume=0.1,
        comment="Bull trend entry",
        magic=12345
    )

    print(f"GBPUSD BUY: ticket #{ticket}")
```

### Пример 3: Обработка ошибок

```python
async def safe_buy():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    try:
        ticket = await sugar.buy_market(volume=0.1)
        print(f"Success! Ticket: {ticket}")

        # Получить текущий баланс после сделки
        balance = await sugar.get_balance()
        print(f"New balance: ${balance}")

    except RuntimeError as e:
        print(f"Order failed: {e}")
        # Обработать ошибку (например, недостаточно маржи, рынок закрыт)
```

---

## Частые ошибки

**Ошибка 1: Не указан символ**
```python
# ОШИБКА: не задан символ по умолчанию
account = MT5Account.create(
    user=123,
    password="pass",
    grpc_server="server",
)
service = MT5Service(account)
sugar = MT5Sugar(service)

await sugar.quick_connect("YourBroker-Demo")
ticket = await sugar.buy_market()  # Вызывает ValueError
```

**Решение:** всегда задавайте значение по умолчанию или передавайте символ явно
```python
# Вариант 1: задать значение по умолчанию
sugar = MT5Sugar(..., default_symbol="EURUSD")
ticket = await sugar.buy_market()

# Вариант 2: передать явно
ticket = await sugar.buy_market(symbol="EURUSD")
```

**Ошибка 2: Недостаточно маржи**
```python
# ОШИБКА: попытка открыть позицию больше, чем позволяет маржа счёта
try:
    ticket = await sugar.buy_market(volume=10.0)  # Слишком большой объём
except RuntimeError as e:
    print(e)  # "Order failed: code=10019, comment=Insufficient margin"
```

**Решение:** проверяйте свободную маржу перед торговлей
```python
free_margin = await sugar.get_free_margin()
# Рассчитать безопасный объём на основе свободной маржи
safe_volume = min(requested_volume, free_margin / margin_per_lot)
```

**Ошибка 3: Рынок закрыт**
```python
# ОШИБКА: попытка торговать в выходные или праздники
try:
    ticket = await sugar.buy_market()  # Рынок закрыт
except RuntimeError as e:
    print(e)  # "Order failed: code=10018, comment=Market is closed"
```

**Решение:** проверяйте часы работы рынка или обрабатывайте корректно
```python
try:
    ticket = await sugar.buy_market()
except RuntimeError as e:
    if "Market is closed" in str(e):
        print("Market closed, will retry later")
    else:
        raise
```

---

## Советы профи

**Совет 1: Сохраняйте тикет для последующих операций**
```python
# Открыть позицию и сохранить тикет
ticket = await sugar.buy_market(volume=0.1)

# Позже: закрыть именно эту позицию
await sugar.close_position(ticket)
```

**Совет 2: Используйте magic number для группировки сделок**
```python
# Сделки стратегии 1 используют magic 1000
ticket1 = await sugar.buy_market(magic=1000)

# Сделки стратегии 2 используют magic 2000
ticket2 = await sugar.buy_market(magic=2000)

# Закрыть только сделки стратегии 1, фильтруя по magic-номеру
```

**Совет 3: Проверяйте цену перед открытием**
```python
# Проверить, что цена входа разумна
bid = await sugar.get_bid()
ask = await sugar.get_ask()
spread = ask - bid

# Торговать только при разумном спреде
if spread < 0.0005:  # 5 пунктов для EURUSD
    ticket = await sugar.buy_market()
else:
    print(f"Spread too wide: {spread}")
```

---

## 📚 См. также

- [sell_market](sell_market.md) - Открытие позиции SELL по рынку
- [buy_limit](buy_limit.md) - Размещение отложенного ордера BUY LIMIT
- [buy_stop](buy_stop.md) - Размещение отложенного ордера BUY STOP
- [buy_market_with_sltp](../5.%20Trading_With_SLTP/buy_market_with_sltp.md) - Открытие BUY с SL/TP
- [close_position](../6.%20Position_Management/close_position.md) - Закрытие позиции по тикету
