# Размещение SELL LIMIT с SL/TP (`sell_limit_with_sltp`)

> **Sugar-метод:** Размещает отложенный ордер SELL LIMIT со стоп-лоссом и тейк-профитом.

**Информация об API:**

* **Метод:** `sugar.sell_limit_with_sltp(symbol, volume, price, sl, tp, sl_pips, tp_pips, comment, magic)`
* **Возвращает:** номер тикета ордера (`int`)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def sell_limit_with_sltp(
    self,
    symbol: Optional[str] = None,
    volume: float = 0.01,
    price: float = 0.0,
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
| `volume` | `float` | Нет | `0.01` | Объём ордера в лотах |
| `price` | `float` | Да | `0.0` | Цена лимита (должна быть ВЫШЕ текущего BID) |
| `sl` | `Optional[float]` | Нет | `None` | Цена стоп-лосса (абсолютная цена) |
| `tp` | `Optional[float]` | Нет | `None` | Цена тейк-профита (абсолютная цена) |
| `sl_pips` | `Optional[float]` | Нет | `None` | Стоп-лосс в пунктах от входа (альтернатива sl) |
| `tp_pips` | `Optional[float]` | Нет | `None` | Тейк-профит в пунктах от входа (альтернатива tp) |
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

- Размещает ордер SELL LIMIT выше текущей цены
- Устанавливает SL/TP на отложенном ордере
- При исполнении ордера SL/TP автоматически активируются
- Поддерживает как абсолютные цены, так и пункты от входа

**Ключевое поведение:**

- Цена SELL LIMIT должна быть ВЫШЕ текущего BID
- SL/TP вычисляются от цены входа (не от текущей цены)
- SELL: SL выше входа, TP ниже входа
- Расчёт по пунктам использует цену входа как ориентир
- Ордер остаётся отложенным до достижения цены

---

## ⚡ Под капотом

```
MT5Sugar.sell_limit_with_sltp()
    ↓ if pips provided, fetches
MT5Sugar.get_symbol_info()
    ↓ calculates SL/TP from entry price
    ↓ builds OrderSendRequest with SL/TP
MT5Service.place_order()
    ↓ calls
MT5Account.order_send()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar проверяет параметр цены входа
2. Если переданы sl_pips или tp_pips, получает информацию о символе для значения point
3. Вычисляет SL/TP от цены входа: SL = price + (pips × point × 10), TP = price - (pips × point × 10)
4. Строит OrderSendRequest с TMT5_ORDER_TYPE_SELL_LIMIT и SL/TP
5. Отправляет ордер через Service → Account → gRPC
6. Возвращает тикет ордера, ордер остаётся отложенным

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1059`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## Когда использовать

**Используйте `sell_limit_with_sltp()`, когда:**

- Хотите продать по более высокой цене с автоматическим управлением риском
- Планируете вход с заранее заданными SL/TP
- Стратегия продажи на росте с защитой
- Настраиваете ордера до движения рынка

**Не используйте, когда:**

- Нужен немедленный вход (используйте `sell_market_with_sltp()`)
- Хотите изменить SL/TP после исполнения ордера
- Цена может никогда не достичь уровня лимита

---

## 🔗 Примеры

### Пример 1: Продажа на росте с защитой в пунктах

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def sell_rally_protected():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Текущий BID: 1.0850
    # Разместить SELL LIMIT на 1.0870 с SL/TP
    ticket = await sugar.sell_limit_with_sltp(
        price=1.0870,
        volume=0.1,
        sl_pips=50,   # на 50 пунктов выше входа 1.0870
        tp_pips=100,  # на 100 пунктов ниже входа 1.0870
        comment="Sell rally protected"
    )

    print(f"SELL LIMIT order: #{ticket} at 1.0870")
    print(f"When filled: SL=1.0920, TP=1.0770")
```

### Пример 2: Вход на уровне сопротивления

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

    # Сопротивление на 1.0900
    resistance = 1.0900

    # Разместить SELL LIMIT на сопротивлении с абсолютными SL/TP
    ticket = await sugar.sell_limit_with_sltp(
        price=resistance,
        volume=0.1,
        sl=resistance + 0.0030,  # SL на 30 пунктов выше сопротивления
        tp=resistance - 0.0100,  # TP на 100 пунктов ниже
        comment="Resistance rejection"
    )

    print(f"Order at resistance {resistance}: #{ticket}")
```

### Пример 3: Лестница целей по прибыли

```python
async def profit_ladder():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Сначала открыть позицию SELL
    sell_ticket = await sugar.sell_market(volume=0.3)

    # Затем разместить ордера SELL LIMIT как цели прибыли
    bid = await sugar.get_bid()  # 1.0850

    targets = [
        (0.1, bid + 0.0030, 50),   # +30 пунктов: закрыть 0.1, SL 50
        (0.1, bid + 0.0050, 30),   # +50 пунктов: закрыть 0.1, SL 30
        (0.1, bid + 0.0100, 20)    # +100 пунктов: закрыть 0.1, SL 20
    ]

    tickets = []
    for volume, entry, sl_pips in targets:
        ticket = await sugar.sell_limit_with_sltp(
            price=entry,
            volume=volume,
            sl_pips=sl_pips,
            tp_pips=50,
            comment=f"Target at {entry}"
        )
        tickets.append(ticket)
        print(f"Profit target #{ticket} at {entry}")
```

---

## Частые ошибки

**Ошибка 1: Цена входа ниже текущего BID**
```python
# ОШИБКА: SELL LIMIT должен быть ВЫШЕ текущей цены
bid = await sugar.get_bid()  # 1.0850

try:
    ticket = await sugar.sell_limit_with_sltp(
        price=1.0840,  # ниже текущего BID
        sl_pips=50,
        tp_pips=100
    )
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price"
```

**Решение:** убедитесь, что цена лимита выше текущего BID
```python
bid = await sugar.get_bid()  # 1.0850
entry_price = bid + 0.0020   # 1.0870 (выше)

ticket = await sugar.sell_limit_with_sltp(
    price=entry_price,
    sl_pips=50,
    tp_pips=100
)
```

**Ошибка 2: Неверное направление SL/TP для SELL**
```python
# ОШИБКА: SL ниже входа, TP выше входа (наоборот!)
ticket = await sugar.sell_limit_with_sltp(
    price=1.0870,
    sl=1.0850,  # НЕВЕРНО: ниже входа
    tp=1.0900   # НЕВЕРНО: выше входа
)
```

**Решение:** SELL = SL выше, TP ниже
```python
entry = 1.0870

ticket = await sugar.sell_limit_with_sltp(
    price=entry,
    sl=entry + 0.0050,  # выше входа (1.0920)
    tp=entry - 0.0100   # ниже входа (1.0770)
)
```

**Ошибка 3: Расчёт от текущей цены вместо цены входа**
```python
# НЕВЕРНО: SL/TP относительно текущей цены, а не входа
bid = await sugar.get_bid()  # 1.0850
entry = 1.0870

ticket = await sugar.sell_limit_with_sltp(
    price=entry,
    sl=bid + 0.0050,  # НЕВЕРНО: от текущей цены (1.0900)
    tp=bid - 0.0100   # НЕВЕРНО: от текущей цены (1.0750)
)
# Когда ордер исполнится на 1.0870, SL всего в 30 пунктах!
```

**Решение:** используйте пункты или рассчитывайте от цены входа
```python
entry = 1.0870

# Вариант 1: используйте пункты (автоматически)
ticket = await sugar.sell_limit_with_sltp(
    price=entry,
    sl_pips=50,   # 50 пунктов от входа
    tp_pips=100   # 100 пунктов от входа
)

# Вариант 2: рассчитайте от входа
ticket = await sugar.sell_limit_with_sltp(
    price=entry,
    sl=entry + 0.0050,  # от входа
    tp=entry - 0.0100   # от входа
)
```

---

## Советы профи

**Совет 1: Заранее размещайте ордера на ключевых уровнях**
```python
# Разместить ордера до того, как рынок достигнет сопротивления
resistances = [1.0900, 1.0950, 1.1000]

tickets = []
for resistance in resistances:
    ticket = await sugar.sell_limit_with_sltp(
        price=resistance,
        volume=0.01,
        sl_pips=50,
        tp_pips=100,
        comment=f"R at {resistance}"
    )
    tickets.append(ticket)

print(f"Placed {len(tickets)} resistance orders")
```

**Совет 2: Динамический SL в зависимости от расстояния до входа**
```python
# Более узкий SL для ближних целей
bid = await sugar.get_bid()  # 1.0850

targets = [
    (1.0860, 30),  # ближняя цель = узкий SL
    (1.0880, 40),  # средняя цель = средний SL
    (1.0900, 50)   # дальняя цель = более широкий SL
]

for entry, sl_pips in targets:
    ticket = await sugar.sell_limit_with_sltp(
        price=entry,
        volume=0.01,
        sl_pips=sl_pips,
        tp_pips=100,
        comment=f"Entry {entry}, SL {sl_pips}"
    )
```

**Совет 3: Сочетайте с наращиванием позиции**
```python
# Открыть небольшую позицию, добавить ещё лимитами
initial = await sugar.sell_market_with_sltp(
    volume=0.05,
    sl_pips=50,
    tp_pips=150
)

# Добавить ещё, если цена вырастет до сопротивления
bid = await sugar.get_bid()
add_on = await sugar.sell_limit_with_sltp(
    price=bid + 0.0020,  # на 20 пунктов выше
    volume=0.05,
    sl_pips=50,
    tp_pips=150,
    comment="Add-on position"
)

print(f"Initial: #{initial}, Add-on: #{add_on}")
```

---

## 📚 См. также

- [buy_limit_with_sltp](buy_limit_with_sltp.md) - BUY LIMIT с SL/TP
- [sell_market_with_sltp](sell_market_with_sltp.md) - SELL по рынку с SL/TP
- [sell_limit](../4.%20Simple_Trading/sell_limit.md) - SELL LIMIT без SL/TP
- [modify_position_sltp](../6.%20Position_Management/modify_position_sltp.md) - Изменение SL/TP после исполнения
