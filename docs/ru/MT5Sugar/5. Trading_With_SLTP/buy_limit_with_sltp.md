# Размещение BUY LIMIT с SL/TP (`buy_limit_with_sltp`)

> **Sugar-метод:** Размещает отложенный ордер BUY LIMIT со стоп-лоссом и тейк-профитом.

**Информация об API:**

* **Метод:** `sugar.buy_limit_with_sltp(symbol, volume, price, sl, tp, sl_pips, tp_pips, comment, magic)`
* **Возвращает:** номер тикета ордера (`int`)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def buy_limit_with_sltp(
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
| `price` | `float` | Да | `0.0` | Цена лимита (должна быть НИЖЕ текущего ASK) |
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

- Размещает ордер BUY LIMIT ниже текущей цены
- Устанавливает SL/TP на отложенном ордере
- При исполнении ордера SL/TP автоматически активируются
- Поддерживает как абсолютные цены, так и пункты от входа

**Ключевое поведение:**

- Цена BUY LIMIT должна быть НИЖЕ текущего ASK
- SL/TP вычисляются от цены входа (не от текущей цены)
- BUY: SL ниже входа, TP выше входа
- Расчёт по пунктам использует цену входа как ориентир
- Ордер остаётся отложенным до достижения цены

---

## ⚡ Под капотом

```
MT5Sugar.buy_limit_with_sltp()
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
3. Вычисляет SL/TP от цены входа: SL = price - (pips × point × 10), TP = price + (pips × point × 10)
4. Строит OrderSendRequest с TMT5_ORDER_TYPE_BUY_LIMIT и SL/TP
5. Отправляет ордер через Service → Account → gRPC
6. Возвращает тикет ордера, ордер остаётся отложенным

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:984`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## Когда использовать

**Используйте `buy_limit_with_sltp()`, когда:**

- Хотите купить по более низкой цене с автоматическим управлением риском
- Планируете вход с заранее заданными SL/TP
- Стратегия покупки на просадке с защитой
- Настраиваете ордера до движения рынка

**Не используйте, когда:**

- Нужен немедленный вход (используйте `buy_market_with_sltp()`)
- Хотите изменить SL/TP после исполнения ордера
- Цена может никогда не достичь уровня лимита

---

## 🔗 Примеры

### Пример 1: Покупка на просадке с защитой в пунктах

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def buy_dip_protected():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Текущий ASK: 1.0850
    # Разместить BUY LIMIT на 1.0840 с SL/TP
    ticket = await sugar.buy_limit_with_sltp(
        price=1.0840,
        volume=0.1,
        sl_pips=50,   # на 50 пунктов ниже входа 1.0840
        tp_pips=100,  # на 100 пунктов выше входа 1.0840
        comment="Buy dip protected"
    )

    print(f"BUY LIMIT order: #{ticket} at 1.0840")
    print(f"When filled: SL=1.0790, TP=1.0940")
```

### Пример 2: Вход на уровне поддержки

```python
async def buy_at_support():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Поддержка на 1.0820
    support = 1.0820

    # Разместить BUY LIMIT на поддержке с абсолютными SL/TP
    ticket = await sugar.buy_limit_with_sltp(
        price=support,
        volume=0.1,
        sl=support - 0.0030,  # SL на 30 пунктов ниже поддержки
        tp=support + 0.0100,  # TP на 100 пунктов выше
        comment="Support bounce"
    )

    print(f"Order at support {support}: #{ticket}")
```

### Пример 3: Сеточная торговля с защитой

```python
async def protected_grid():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Текущий ASK: 1.0850
    # Разместить сетку ордеров BUY LIMIT ниже
    base_price = 1.0840
    grid_step = 0.0010  # 10 пунктов

    tickets = []
    for i in range(5):
        entry_price = base_price - (i * grid_step)

        ticket = await sugar.buy_limit_with_sltp(
            price=entry_price,
            volume=0.01,
            sl_pips=50,
            tp_pips=100,
            comment=f"Grid {i+1} at {entry_price}"
        )
        tickets.append(ticket)
        print(f"Grid order #{ticket} at {entry_price}")

    print(f"Total grid orders: {len(tickets)}")
```

---

## Частые ошибки

**Ошибка 1: Использование текущей цены для расчёта SL/TP**
```python
# НЕВЕРНО: расчёт SL/TP от текущей цены
ask = await sugar.get_ask()  # 1.0850
entry_price = 1.0840

# ОШИБКА: SL/TP должны быть относительно входа (1.0840), а не текущей цены (1.0850)
ticket = await sugar.buy_limit_with_sltp(
    price=entry_price,
    sl=ask - 0.0050,  # НЕВЕРНО: на основе текущей цены
    tp=ask + 0.0100   # НЕВЕРНО: на основе текущей цены
)
```

**Решение:** вычисляйте SL/TP от цены входа или используйте пункты
```python
entry_price = 1.0840

# Вариант 1: используйте пункты (автоматический расчёт от входа)
ticket = await sugar.buy_limit_with_sltp(
    price=entry_price,
    sl_pips=50,
    tp_pips=100
)

# Вариант 2: рассчитайте от цены входа
ticket = await sugar.buy_limit_with_sltp(
    price=entry_price,
    sl=entry_price - 0.0050,  # от входа
    tp=entry_price + 0.0100   # от входа
)
```

**Ошибка 2: Цена входа выше текущего ASK**
```python
# ОШИБКА: BUY LIMIT должен быть НИЖЕ текущей цены
ask = await sugar.get_ask()  # 1.0850

try:
    ticket = await sugar.buy_limit_with_sltp(
        price=1.0860,  # выше текущего ASK
        sl_pips=50,
        tp_pips=100
    )
except RuntimeError as e:
    print(e)  # "Order failed: Invalid price"
```

**Решение:** убедитесь, что цена лимита ниже текущего ASK
```python
ask = await sugar.get_ask()  # 1.0850
entry_price = ask - 0.0010   # 1.0840 (ниже)

ticket = await sugar.buy_limit_with_sltp(
    price=entry_price,
    sl_pips=50,
    tp_pips=100
)
```

**Ошибка 3: Забытое направление SL/TP**
```python
# ОШИБКА: SL выше входа, TP ниже входа (наоборот!)
ticket = await sugar.buy_limit_with_sltp(
    price=1.0840,
    sl=1.0850,  # НЕВЕРНО: выше входа
    tp=1.0830   # НЕВЕРНО: ниже входа
)
```

**Решение:** BUY = SL ниже, TP выше
```python
entry = 1.0840

ticket = await sugar.buy_limit_with_sltp(
    price=entry,
    sl=entry - 0.0050,  # ниже входа
    tp=entry + 0.0100   # выше входа
)
```

---

## Советы профи

**Совет 1: Используйте пункты для чистых ордеров**
```python
# Пункты автоматически рассчитывают правильные SL/TP от входа
ticket = await sugar.buy_limit_with_sltp(
    price=1.0840,
    volume=0.1,
    sl_pips=50,   # будет 1.0790
    tp_pips=100,  # будет 1.0940
    comment="Clean setup"
)
```

**Совет 2: Размещайте ордера заранее на известных уровнях**
```python
# Экономический календарь: поддержка на 1.0820
# Разместить ордер до того, как рынок достигнет уровня
ticket = await sugar.buy_limit_with_sltp(
    price=1.0820,
    volume=0.1,
    sl_pips=30,
    tp_pips=90,
    comment="Pre-placed at support"
)
# Ордер ждёт, пока цена не упадёт до 1.0820
```

**Совет 3: Проверяйте статус ордера позже**
```python
# Разместить ордер
ticket = await sugar.buy_limit_with_sltp(
    price=1.0840,
    sl_pips=50,
    tp_pips=100
)

# Позже: проверить, исполнен ли
positions = await sugar._service.get_opened_orders()

filled = False
for pos in positions.position_infos:
    if pos.ticket == ticket:
        filled = True
        print(f"Order #{ticket} filled and now a position")
        break

if not filled:
    print(f"Order #{ticket} still pending")
```

---

## 📚 См. также

- [sell_limit_with_sltp](sell_limit_with_sltp.md) - SELL LIMIT с SL/TP
- [buy_market_with_sltp](buy_market_with_sltp.md) - BUY по рынку с SL/TP
- [buy_limit](../4.%20Simple_Trading/buy_limit.md) - BUY LIMIT без SL/TP
- [modify_position_sltp](../6.%20Position_Management/modify_position_sltp.md) - Изменение SL/TP после исполнения
