# Открытие позиции SELL с SL/TP (`sell_market_with_sltp`)

> **Sugar-метод:** Открывает позицию SELL по рынку со стоп-лоссом и тейк-профитом за один вызов.

**Информация об API:**

* **Метод:** `sugar.sell_market_with_sltp(symbol, volume, sl, tp, sl_pips, tp_pips, comment, magic)`
* **Возвращает:** номер тикета позиции (`int`)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def sell_market_with_sltp(
    self,
    symbol: Optional[str] = None,
    volume: float = 0.01,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    sl_pips: Optional[float] = None,
    tp_pips: Optional[float] = None,
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
| `sl` | `Optional[float]` | Нет | `None` | Цена стоп-лосса (абсолютная цена) |
| `tp` | `Optional[float]` | Нет | `None` | Цена тейк-профита (абсолютная цена) |
| `sl_pips` | `Optional[float]` | Нет | `None` | Стоп-лосс в пунктах (альтернатива sl) |
| `tp_pips` | `Optional[float]` | Нет | `None` | Тейк-профит в пунктах (альтернатива tp) |
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

- Открывает позицию SELL по текущей цене BID
- Автоматически устанавливает стоп-лосс и тейк-профит
- Поддерживает как абсолютные цены, так и запись в пунктах
- Вычисляет SL/TP из пунктов, используя значение point символа

**Ключевое поведение:**

- SELL: SL выше входа, TP ниже входа
- Можно использовать абсолютные цены (sl, tp) ЛИБО пункты (sl_pips, tp_pips)
- Расчёт по пунктам: SL = bid + (pips × point × 10), TP = bid - (pips × point × 10)
- Получает информацию о символе, если используются пункты
- Проскальзывание по умолчанию: 10 пунктов

---

## ⚡ Под капотом

```
MT5Sugar.sell_market_with_sltp()
    ↓ fetches price
MT5Service.get_symbol_tick()
    ↓ if pips provided, fetches
MT5Sugar.get_symbol_info()
    ↓ calculates SL/TP prices
    ↓ builds OrderSendRequest with SL/TP
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar получает текущий тик (цену BID)
2. Если переданы sl_pips или tp_pips, получает информацию о символе для значения point
3. Вычисляет цены SL/TP: SL = bid + (pips × point × 10), TP = bid - (pips × point × 10)
4. Строит OrderSendRequest с полями stop_loss и take_profit
5. Отправляет ордер через Service → Account → gRPC
6. Возвращает номер тикета при успехе

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:903`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## Когда использовать

**Используйте `sell_market_with_sltp()`, когда:**

- Нужно управление риском с момента входа (требуются SL/TP)
- Хотите задать SL/TP в пунктах (проще, чем вычислять цены)
- Реализуете автоматические стратегии с фиксированным соотношением риск/прибыль
- Ожидаете падения цены с определённым риском

**Не используйте, когда:**

- Хотите добавить SL/TP позже (используйте `sell_market()`, затем `modify_position_sltp()`)
- Нужна сложная логика изменения ордера
- SL/TP изначально не требуются

---

## 🔗 Примеры

### Пример 1: Использование пунктов (рекомендуется)

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def sell_with_pips():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть SELL с SL 50 пунктов и TP 100 пунктов
    ticket = await sugar.sell_market_with_sltp(
        volume=0.1,
        sl_pips=50,   # Стоп-лосс на 50 пунктов выше входа
        tp_pips=100,  # Тейк-профит на 100 пунктов ниже входа
        comment="1:2 risk/reward"
    )

    print(f"SELL position opened: #{ticket}")
    print(f"SL: 50 pips, TP: 100 pips (1:2 R/R)")

# Вывод:
# SELL position opened: #123456796
# SL: 50 pips, TP: 100 pips (1:2 R/R)
```

### Пример 2: Использование абсолютных цен

```python
async def sell_with_prices():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Получить текущую цену
    bid = await sugar.get_bid()  # 1.0850

    # Открыть SELL с конкретными ценами SL/TP
    ticket = await sugar.sell_market_with_sltp(
        volume=0.1,
        sl=1.0900,  # Стоп-лосс на 1.0900 (выше входа)
        tp=1.0750,  # Тейк-профит на 1.0750 (ниже входа)
        comment="Resistance/Support levels"
    )

    print(f"SELL at {bid}")
    print(f"SL: 1.0900, TP: 1.0750")
```

### Пример 3: Стратегия нисходящего тренда

```python
async def downtrend_trade():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Проверить, нисходящий ли тренд (упрощённо)
    bid = await sugar.get_bid()

    # Открыть SELL в расчёте на продолжение
    ticket = await sugar.sell_market_with_sltp(
        volume=0.1,
        sl_pips=40,   # узкий стоп
        tp_pips=120,  # 3x прибыль
        comment="Downtrend continuation"
    )

    print(f"SELL position: #{ticket}")
    print(f"Risk/Reward: 1:3")

    # Отслеживать позицию
    floating_profit = await sugar.get_floating_profit()
    print(f"Current P&L: ${floating_profit:.2f}")
```

---

## Частые ошибки

**Ошибка 1: Неверное направление SL/TP для SELL**
```python
# ОШИБКА: SL ниже входа, TP выше входа (наоборот!)
bid = await sugar.get_bid()  # 1.0850

ticket = await sugar.sell_market_with_sltp(
    sl=1.0800,  # НЕВЕРНО: SL ниже входа
    tp=1.0900   # НЕВЕРНО: TP выше входа
)
# Ордер, скорее всего, не исполнится или сработает сразу
```

**Решение:** помните, SELL: SL выше, TP ниже
```python
bid = await sugar.get_bid()  # 1.0850

ticket = await sugar.sell_market_with_sltp(
    sl=1.0900,  # Верно: SL выше входа (50 пунктов)
    tp=1.0750   # Верно: TP ниже входа (100 пунктов)
)
```

**Ошибка 2: Путаница логики SL/TP для BUY и SELL**
```python
# BUY: SL ниже, TP выше
buy_ticket = await sugar.buy_market_with_sltp(
    sl_pips=50,  # на 50 пунктов НИЖЕ входа
    tp_pips=100  # на 100 пунктов ВЫШЕ входа
)

# SELL: SL выше, TP ниже (наоборот!)
sell_ticket = await sugar.sell_market_with_sltp(
    sl_pips=50,  # на 50 пунктов ВЫШЕ входа
    tp_pips=100  # на 100 пунктов НИЖЕ входа
)
```

**Ошибка 3: Использование одних и тех же абсолютных цен для нескольких сделок**
```python
# ОШИБКА: рынок сдвинулся, старые цены SL/TP недействительны
first_bid = await sugar.get_bid()  # 1.0850
ticket1 = await sugar.sell_market_with_sltp(
    sl=1.0900,
    tp=1.0750
)

# через 1 час, цена на 1.0800
ticket2 = await sugar.sell_market_with_sltp(
    sl=1.0900,  # всё ещё действительна, но очень далеко (100 пунктов!)
    tp=1.0750   # уже достигнута! Ордер не исполнится
)
```

**Решение:** используйте пункты для единообразного поведения
```python
# Работает независимо от текущей цены
ticket1 = await sugar.sell_market_with_sltp(sl_pips=50, tp_pips=100)

# Позже всё так же работает корректно
ticket2 = await sugar.sell_market_with_sltp(sl_pips=50, tp_pips=100)
```

---

## Советы профи

**Совет 1: Отслеживание SELL с улучшением входа**
```python
# Если цена идёт вниз, ждите лучшего входа
initial_bid = await sugar.get_bid()  # 1.0850

# Подождать 60 секунд
await asyncio.sleep(60)

new_bid = await sugar.get_bid()  # 1.0840

# Лучший вход (цена упала)
if new_bid < initial_bid:
    ticket = await sugar.sell_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=100,
        comment="Improved entry"
    )
```

**Совет 2: Сочетайте с уровнями сопротивления**
```python
# Продажа у сопротивления с SL выше сопротивления
resistance = 1.0900
bid = await sugar.get_bid()

# Торговать только вблизи сопротивления
if abs(bid - resistance) < 0.0010:  # в пределах 10 пунктов
    ticket = await sugar.sell_market_with_sltp(
        volume=0.1,
        sl=resistance + 0.0010,  # SL на 10 пунктов выше сопротивления
        tp=resistance - 0.0100,  # TP на 100 пунктов ниже
        comment="Sell at resistance"
    )
```

**Совет 3: Наращивание позиции несколькими сделками**
```python
# Открыть несколько позиций SELL с разными уровнями TP
base_sl_pips = 50

tickets = []
for i in range(3):
    tp_pips = 50 + (i * 25)  # 50, 75, 100 пунктов TP

    ticket = await sugar.sell_market_with_sltp(
        volume=0.01,
        sl_pips=base_sl_pips,
        tp_pips=tp_pips,
        comment=f"Scaled TP {tp_pips}"
    )
    tickets.append(ticket)

print(f"Opened {len(tickets)} scaled positions")
```

---

## 📚 См. также

- [buy_market_with_sltp](buy_market_with_sltp.md) - Открытие BUY с SL/TP
- [sell_limit_with_sltp](sell_limit_with_sltp.md) - SELL LIMIT с SL/TP
- [sell_market](../4.%20Simple_Trading/sell_market.md) - Открытие SELL без SL/TP
- [modify_position_sltp](../6.%20Position_Management/modify_position_sltp.md) - Изменение SL/TP после открытия
