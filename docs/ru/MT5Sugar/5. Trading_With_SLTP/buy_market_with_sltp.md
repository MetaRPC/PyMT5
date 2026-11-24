# Открытие позиции BUY с SL/TP (`buy_market_with_sltp`)

> **Sugar-метод:** Открывает позицию BUY по рынку со стоп-лоссом и тейк-профитом за один вызов.

**Информация об API:**

* **Метод:** `sugar.buy_market_with_sltp(symbol, volume, sl, tp, sl_pips, tp_pips, comment, magic)`
* **Возвращает:** номер тикета позиции (`int`)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def buy_market_with_sltp(
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

- Открывает позицию BUY по текущей цене ASK
- Автоматически устанавливает стоп-лосс и тейк-профит
- Поддерживает как абсолютные цены, так и запись в пунктах
- Вычисляет SL/TP из пунктов, используя значение point символа

**Ключевое поведение:**

- BUY: SL ниже входа, TP выше входа
- Можно использовать абсолютные цены (sl, tp) ЛИБО пункты (sl_pips, tp_pips)
- Расчёт по пунктам: `price ± (pips × point × 10)`
- Получает информацию о символе, если используются пункты
- Проскальзывание по умолчанию: 10 пунктов

---

## ⚡ Под капотом

```
MT5Sugar.buy_market_with_sltp()
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

1. Sugar получает текущий тик (цену ASK)
2. Если переданы sl_pips или tp_pips, получает информацию о символе для значения point
3. Вычисляет цены SL/TP: SL = ask - (pips × point × 10), TP = ask + (pips × point × 10)
4. Строит OrderSendRequest с полями stop_loss и take_profit
5. Отправляет ордер через Service → Account → gRPC
6. Возвращает номер тикета при успехе

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:824`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## Когда использовать

**Используйте `buy_market_with_sltp()`, когда:**

- Нужно управление риском с момента входа (требуются SL/TP)
- Хотите задать SL/TP в пунктах (проще, чем вычислять цены)
- Реализуете автоматические стратегии с фиксированным соотношением риск/прибыль
- Нужно открыть позицию с защитой немедленно

**Не используйте, когда:**

- Хотите добавить SL/TP позже (используйте `buy_market()`, затем `modify_position_sltp()`)
- Нужна сложная логика изменения ордера
- SL/TP изначально не требуются

---

## 🔗 Примеры

### Пример 1: Использование пунктов (рекомендуется)

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def buy_with_pips():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть BUY с SL 50 пунктов и TP 100 пунктов
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,   # Стоп-лосс на 50 пунктов ниже входа
        tp_pips=100,  # Тейк-профит на 100 пунктов выше входа
        comment="1:2 risk/reward"
    )

    print(f"BUY position opened: #{ticket}")
    print(f"SL: 50 pips, TP: 100 pips (1:2 R/R)")

# Вывод:
# BUY position opened: #123456795
# SL: 50 pips, TP: 100 pips (1:2 R/R)
```

### Пример 2: Использование абсолютных цен

```python
async def buy_with_prices():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Получить текущую цену
    ask = await sugar.get_ask()  # 1.0850

    # Открыть BUY с конкретными ценами SL/TP
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl=1.0800,  # Стоп-лосс на 1.0800
        tp=1.0950,  # Тейк-профит на 1.0950
        comment="Support/Resistance levels"
    )

    print(f"BUY at {ask}")
    print(f"SL: 1.0800, TP: 1.0950")
```

### Пример 3: Стратегия управления риском

```python
async def fixed_risk_trade():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Фиксированный риск: 1% баланса счёта
    balance = await sugar.get_balance()
    risk_amount = balance * 0.01  # риск 1%

    # Рассчитать объём на основе SL 50 пунктов
    # Для EURUSD: 1 пункт = $1 на 0.1 лота
    sl_pips = 50
    volume = risk_amount / (sl_pips * 10)  # упрощённо

    # Открыть с риск/прибыль 1:2
    ticket = await sugar.buy_market_with_sltp(
        volume=round(volume, 2),
        sl_pips=50,
        tp_pips=100,  # 2x прибыль
        comment=f"1% risk = ${risk_amount:.2f}"
    )

    print(f"Position: #{ticket}")
    print(f"Risk: ${risk_amount:.2f} (1% of ${balance})")
    print(f"Volume: {volume:.2f} lots")
```

---

## Частые ошибки

**Ошибка 1: Смешивание пунктов и цен**
```python
# ОШИБКА: не смешивайте sl/tp с sl_pips/tp_pips
ticket = await sugar.buy_market_with_sltp(
    sl=1.0800,      # абсолютная цена
    tp_pips=100     # Пункты
)
# Будут использованы оба, tp_pips перезапишет tp
```

**Решение:** используйте либо абсолютные значения, ЛИБО пункты, но не оба сразу
```python
# Вариант 1: все в пунктах
ticket = await sugar.buy_market_with_sltp(sl_pips=50, tp_pips=100)

# Вариант 2: все абсолютные
ticket = await sugar.buy_market_with_sltp(sl=1.0800, tp=1.0950)
```

**Ошибка 2: Неверное направление SL/TP для BUY**
```python
# ОШИБКА: SL выше входа, TP ниже входа (наоборот!)
ask = await sugar.get_ask()  # 1.0850

ticket = await sugar.buy_market_with_sltp(
    sl=1.0900,  # НЕВЕРНО: SL выше входа
    tp=1.0800   # НЕВЕРНО: TP ниже входа
)
# Ордер, скорее всего, не исполнится или сработает сразу
```

**Решение:** помните, BUY: SL ниже, TP выше
```python
ask = await sugar.get_ask()  # 1.0850

ticket = await sugar.buy_market_with_sltp(
    sl=1.0800,  # Верно: SL ниже входа (50 пунктов)
    tp=1.0950   # Верно: TP выше входа (100 пунктов)
)
```

**Ошибка 3: SL/TP слишком близко к входу**
```python
# ОШИБКА: не соблюдён минимальный уровень стопа брокера
try:
    ticket = await sugar.buy_market_with_sltp(
        sl_pips=1,   # слишком близко (минимум брокера 10 пунктов)
        tp_pips=2
    )
except RuntimeError as e:
    print(e)  # "Order failed: Invalid stops"
```

**Решение:** проверьте минимальный уровень стопа брокера
```python
# Используйте разумные расстояния SL/TP
ticket = await sugar.buy_market_with_sltp(
    sl_pips=20,   # выше минимума брокера
    tp_pips=40
)
```

---

## Советы профи

**Совет 1: Быстрое соотношение риск/прибыль 1:2**
```python
# Установите TP в 2x SL для R/R 1:2
sl_pips = 50
tp_pips = sl_pips * 2  # 100 пунктов

ticket = await sugar.buy_market_with_sltp(
    volume=0.1,
    sl_pips=sl_pips,
    tp_pips=tp_pips,
    comment="1:2 R/R"
)
```

**Совет 2: Используйте пункты для единообразного риска по символам**
```python
# Одни и те же значения в пунктах работают для разных символов
for symbol in ["EURUSD", "GBPUSD", "USDJPY"]:
    ticket = await sugar.buy_market_with_sltp(
        symbol=symbol,
        volume=0.01,
        sl_pips=50,
        tp_pips=100
    )
    print(f"{symbol} position: #{ticket}")
```

**Совет 3: Рассчитывайте фактическую сумму риска**
```python
# Проверьте фактический риск в долларах перед торговлей
sl_pips = 50
volume = 0.1

# Для EURUSD: 1 пункт ≈ $1 на 0.1 лота
risk_dollars = sl_pips * (volume / 0.1) * 1

print(f"Risk: ${risk_dollars} for {volume} lots with {sl_pips} pip SL")

if risk_dollars <= 100:  # проверка максимального риска
    ticket = await sugar.buy_market_with_sltp(
        volume=volume,
        sl_pips=sl_pips,
        tp_pips=sl_pips * 2
    )
```

---

## 📚 См. также

- [sell_market_with_sltp](sell_market_with_sltp.md) - Открытие SELL с SL/TP
- [buy_limit_with_sltp](buy_limit_with_sltp.md) - BUY LIMIT с SL/TP
- [buy_market](../4.%20Simple_Trading/buy_market.md) - Открытие BUY без SL/TP
- [modify_position_sltp](../6.%20Position_Management/modify_position_sltp.md) - Изменение SL/TP после открытия
