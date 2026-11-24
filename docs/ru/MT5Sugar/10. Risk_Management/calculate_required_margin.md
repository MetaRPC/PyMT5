# Рассчитать требуемую маржу (`calculate_required_margin`)

> **Sugar-метод:** Рассчитывает маржу, необходимую для открытия позиции с заданными параметрами.

**Информация об API:**

* **Метод:** `sugar.calculate_required_margin(symbol, volume, order_type)`
* **Возвращает:** Требуемую маржу в валюте счёта (float)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def calculate_required_margin(
    self,
    symbol: str,
    volume: float,
    order_type: Optional[int] = None
) -> float
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Да | - | Торговый символ (например, "EURUSD") |
| `volume` | `float` | Да | - | Объём позиции в лотах |
| `order_type` | `Optional[int]` | Нет | `None` | Перечисление типа ордера (по умолчанию BUY) |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `float` | Требуемая маржа в валюте счёта (например, USD) |

---

## 🏛️ Основное

**Что делает:**

- Рассчитывает маржу, необходимую для открытия позиции
- Использует встроенный расчёт маржи MT5
- Учитывает кредитное плечо и спецификации символа
- Возвращает сумму в валюте счёта

**Ключевое поведение:**

- По умолчанию берёт ордер BUY, если тип не указан
- Использует текущую рыночную цену (ASK для BUY, BID для SELL)
- Расчёт: `margin = (volume × contract_size × price) / leverage`
- Обходит слой Service, вызывает Account напрямую
- Возвращает фактическое требование к марже от MT5

**Формула:**

```
margin = (volume × contract_size × price) / leverage
```

---

## ⚡ Под капотом

```
MT5Sugar.calculate_required_margin()
    ↓ вызывает
MT5Service.get_symbol_tick(symbol)
    ↓ создаёт OrderCalcMarginRequest
    ↓ вызывает
MT5Account.order_calc_margin(request)
    ↓ gRPC protobuf
TradingService.OrderCalcMargin()
    ↓ терминал MT5 рассчитывает маржу
    ↓ возвращает result.margin
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_symbol_tick() для текущей цены
2. Sugar определяет цену на основе order_type (ASK для BUY, BID для SELL)
3. Sugar создаёт OrderCalcMarginRequest с symbol, type, volume, price
4. Sugar получает экземпляр Account из Service
5. Sugar вызывает Account.order_calc_margin() напрямую
6. Account отправляет gRPC-запрос расчёта маржи
7. Терминал рассчитывает точное требование к марже
8. Возвращает значение маржи как float

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1841`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1892`

---

## Когда использовать

**Используйте `calculate_required_margin()`, когда:**

- Проверяете достаточность маржи перед торговлей
- Рассчитываете максимально доступный размер позиции
- Расчёты управления рисками
- Предторговая проверка
- Мониторинг уровня маржи

**Не используйте, когда:**

- Точная маржа не нужна (используйте оценку)
- Приблизительная маржа уже известна
- Нет ограничений по марже
- Критична производительность

---

## 🔗 Примеры

### Пример 1: Проверка маржи перед торговлей

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def check_margin():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    volume = 1.0

    # Рассчитать требуемую маржу
    margin_needed = await sugar.calculate_required_margin(symbol, volume)

    # Получить доступную маржу
    free_margin = await sugar.get_free_margin()

    print(f"Required margin: ${margin_needed:.2f}")
    print(f"Available margin: ${free_margin:.2f}")

    if margin_needed <= free_margin:
        print("Sufficient margin - opening position")
        ticket = await sugar.buy_market(symbol, volume=volume)
        print(f"Order opened: {ticket}")
    else:
        print("Insufficient margin")
        shortage = margin_needed - free_margin
        print(f"Short by: ${shortage:.2f}")

# Вывод:
# Required margin: $1084.32
# Available margin: $5000.00
# Sufficient margin - opening position
# Order opened: 123456789
```

### Пример 2: Расчёт максимально доступного объёма

```python
async def max_affordable_volume():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Получить доступную маржу
    free_margin = await sugar.get_free_margin()

    print(f"Available margin: ${free_margin:.2f}")

    # Двоичный поиск максимального объёма
    min_vol = 0.01
    max_vol = 100.0
    best_volume = 0.01

    while max_vol - min_vol > 0.01:
        test_vol = (min_vol + max_vol) / 2

        margin_needed = await sugar.calculate_required_margin(symbol, test_vol)

        if margin_needed <= free_margin:
            best_volume = test_vol
            min_vol = test_vol
        else:
            max_vol = test_vol

    # Округлить до шага символа
    info = await sugar.get_symbol_info(symbol)
    best_volume = round(best_volume / info.volume_step) * info.volume_step

    margin_for_best = await sugar.calculate_required_margin(symbol, best_volume)

    print(f"Maximum affordable volume: {best_volume} lots")
    print(f"Margin required: ${margin_for_best:.2f}")

# Вывод:
# Available margin: $5000.00
# Maximum affordable volume: 4.61 lots
# Margin required: $4998.23
```

### Пример 3: Сравнение маржи для разных символов

```python
async def compare_margin_requirements():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
    volume = 1.0

    print(f"Margin required for {volume} lot:")

    for symbol in symbols:
        margin = await sugar.calculate_required_margin(symbol, volume)
        print(f"  {symbol}: ${margin:.2f}")

    # Получить доступную маржу
    free_margin = await sugar.get_free_margin()
    print(f"\nAvailable margin: ${free_margin:.2f}")

    # Найти самый дешёвый символ
    margins = {}
    for symbol in symbols:
        margins[symbol] = await sugar.calculate_required_margin(symbol, volume)

    cheapest = min(margins, key=margins.get)
    print(f"\nCheapest to trade: {cheapest} (${margins[cheapest]:.2f})")

# Вывод:
# Margin required for 1.0 lot:
#   EURUSD: $1084.32
#   GBPUSD: $1267.89
#   USDJPY: $1493.85
#   XAUUSD: $20435.00
#
# Available margin: $5000.00
#
# Cheapest to trade: EURUSD ($1084.32)
```

---

## Типичные ошибки

**Ошибка 1: Неучёт существующих позиций**
```python
# ОШИБКА: свободная маржа уже учитывает открытые позиции
margin_needed = await sugar.calculate_required_margin("EURUSD", 1.0)
free_margin = await sugar.get_free_margin()

# Это верно — free_margin уже уменьшена открытыми позициями
if margin_needed <= free_margin:
    # Безопасно открывать
```

**Ошибка 2: Использование старого расчёта маржи**
```python
# ОШИБКА: цена меняется — маржа меняется
margin = await sugar.calculate_required_margin("EURUSD", 1.0)

await asyncio.sleep(60)

# Расчёт маржи теперь устарел
if margin <= free_margin:  # Старое значение маржи
    await sugar.buy_market("EURUSD", volume=1.0)
```

**Решение:** Рассчитывайте непосредственно перед торговлей
```python
# Рассчитать свежую маржу прямо перед сделкой
margin = await sugar.calculate_required_margin("EURUSD", 1.0)
free_margin = await sugar.get_free_margin()

if margin <= free_margin:
    # Сразу выполнить
    await sugar.buy_market("EURUSD", volume=1.0)
```

**Ошибка 3: Игнорирование параметра order_type**
```python
# В большинстве случаев маржа для BUY/SELL одинакова
# Но у некоторых символов могут быть направленные различия маржи

margin_buy = await sugar.calculate_required_margin("XAUUSD", 1.0)
# По умолчанию BUY
```

**Решение:** Указывайте тип ордера при необходимости
```python
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as trade_pb2

# Для BUY
margin_buy = await sugar.calculate_required_margin(
    "XAUUSD",
    1.0,
    order_type=trade_pb2.ORDER_TYPE_TF_BUY
)

# Для SELL
margin_sell = await sugar.calculate_required_margin(
    "XAUUSD",
    1.0,
    order_type=trade_pb2.ORDER_TYPE_TF_SELL
)
```

---

## Полезные советы

**Совет 1: Вспомогательная функция проверки маржи**
```python
async def check_sufficient_margin(sugar, symbol, volume):
    """Проверить достаточность маржи для позиции."""
    margin_needed = await sugar.calculate_required_margin(symbol, volume)
    free_margin = await sugar.get_free_margin()

    if margin_needed > free_margin:
        shortage = margin_needed - free_margin
        raise ValueError(
            f"Insufficient margin: need ${margin_needed:.2f}, "
            f"have ${free_margin:.2f}, short ${shortage:.2f}"
        )

    return True

# Использование
try:
    await check_sufficient_margin(sugar, "EURUSD", 10.0)
    ticket = await sugar.buy_market("EURUSD", volume=10.0)
except ValueError as e:
    print(f"Cannot open: {e}")
```

**Совет 2: Расчёт уровня маржи после сделки**
```python
async def simulate_trade_impact(sugar, symbol, volume):
    """Показать, как изменится уровень маржи после сделки."""
    # Текущее состояние
    equity = await sugar.get_equity()
    margin = await sugar.get_margin()
    free_margin = await sugar.get_free_margin()
    margin_level = await sugar.get_margin_level()

    # Рассчитать дополнительную требуемую маржу
    additional_margin = await sugar.calculate_required_margin(symbol, volume)

    # Смоделированное состояние после сделки
    new_margin = margin + additional_margin
    new_free_margin = free_margin - additional_margin
    new_margin_level = (equity / new_margin) * 100 if new_margin > 0 else 0

    print("Current state:")
    print(f"  Margin: ${margin:.2f}")
    print(f"  Free margin: ${free_margin:.2f}")
    print(f"  Margin level: {margin_level:.2f}%")

    print(f"\nAfter opening {volume} lots of {symbol}:")
    print(f"  Margin: ${new_margin:.2f} (+${additional_margin:.2f})")
    print(f"  Free margin: ${new_free_margin:.2f}")
    print(f"  Margin level: {new_margin_level:.2f}%")

    if new_margin_level < 100:
        print("\nWARNING: Margin level would drop below 100%!")

# Использование
await simulate_trade_impact(sugar, "EURUSD", 5.0)
```

**Совет 3: Найти оптимальный объём для целевого уровня маржи**
```python
async def calculate_volume_for_margin_level(sugar, symbol, target_margin_level=200.0):
    """Рассчитать объём, поддерживающий целевой уровень маржи."""
    equity = await sugar.get_equity()
    current_margin = await sugar.get_margin()

    # Рассчитать максимально допустимую дополнительную маржу
    max_total_margin = equity / (target_margin_level / 100)
    max_additional_margin = max_total_margin - current_margin

    if max_additional_margin <= 0:
        print(f"Already below target margin level")
        return 0.0

    # Двоичный поиск объёма
    min_vol = 0.01
    max_vol = 100.0
    best_volume = 0.01

    while max_vol - min_vol > 0.01:
        test_vol = (min_vol + max_vol) / 2

        margin_needed = await sugar.calculate_required_margin(symbol, test_vol)

        if margin_needed <= max_additional_margin:
            best_volume = test_vol
            min_vol = test_vol
        else:
            max_vol = test_vol

    # Округлить до шага символа
    info = await sugar.get_symbol_info(symbol)
    best_volume = round(best_volume / info.volume_step) * info.volume_step

    return best_volume

# Использование
volume = await calculate_volume_for_margin_level(sugar, "EURUSD", target_margin_level=200.0)
print(f"Safe volume to maintain 200% margin level: {volume} lots")
```

---

## 📚 См. также

- [get_free_margin](../2.%20Account_Properties/get_free_margin.md) - Получить доступную маржу
- [get_margin_level](../2.%20Account_Properties/get_margin_level.md) - Получить уровень маржи в процентах
- [can_open_position](can_open_position.md) - Проверить, можно ли открыть позицию
- [calculate_position_size](calculate_position_size.md) - Рассчитать размер позиции по риску
