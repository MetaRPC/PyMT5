# Можно ли открыть позицию (`can_open_position`)

> **Sugar-метод:** Проверяет, можно ли открыть позицию с заданными параметрами.

**Информация об API:**

* **Метод:** `sugar.can_open_position(symbol, volume)`
* **Возвращает:** Кортеж (can_open: bool, reason: str)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def can_open_position(
    self,
    symbol: str,
    volume: float
) -> Tuple[bool, str]
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Да | - | Торговый символ (например, "EURUSD") |
| `volume` | `float` | Да | - | Объём позиции в лотах |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `Tuple[bool, str]` | Первый элемент: True, если можно открыть, иначе False. Второй элемент: строка с причиной ("OK" или описание ошибки) |

---

## 🏛️ Основное

**Что делает:**

- Проверяет ордер перед фактическим размещением
- Проверяет требования к марже
- Проверяет доступность символа
- Проверяет ограничения по объёму
- Возвращает результат проверки с причиной

**Ключевое поведение:**

- Симулирует ордер BUY по текущей цене ASK
- НЕ размещает ордер фактически
- Использует функцию order_check из MT5
- Возвращает кортеж (success, message)
- Код возврата 0 = OK
- Ненулевой код = проверка не пройдена

---

## ⚡ Под капотом

```
MT5Sugar.can_open_position()
    ↓ вызывает
MT5Service.get_symbol_tick(symbol)
    ↓ создаёт MrpcMqlTradeRequest (BUY по ASK)
    ↓ оборачивает в OrderCheckRequest
    ↓ вызывает
MT5Service.check_order(request)
    ↓ вызывает
MT5Account.order_check()
    ↓ gRPC protobuf
TradingService.OrderCheck()
    ↓ терминал MT5 проверяет ордер
    ↓ возвращает (returned_code, comment)
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_symbol_tick() для текущей цены
2. Sugar создаёт MrpcMqlTradeRequest с ордером BUY
3. Sugar оборачивает запрос в OrderCheckRequest
4. Sugar вызывает Service.check_order()
5. Service перенаправляет в Account.order_check()
6. Account отправляет gRPC-запрос проверки ордера
7. Терминал проверяет параметры ордера
8. Возвращает результат с кодом и комментарием
9. Sugar возвращает кортеж (success: bool, reason: str)

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1774`
- Service: `src/pymt5/mt5_service.py:1018`

---

## Когда использовать

**Используйте `can_open_position()`, когда:**
- Проверяете ордера перед размещением
- Проверяете наличие маржи
- Предварительные проверки в торговых системах
- Предотвращение ошибок
- Построение безопасных торговых приложений

**Не используйте, когда:**
- Уже уверены, что ордер пройдёт успешно
- Критична производительность (добавляет лишний вызов)
- Проверка ордера избыточна
- Тестируете на демо-счёте

---

## 🔗 Примеры

### Пример 1: Проверка перед открытием

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def safe_open():
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

    # Проверить, можно ли открыть
    can_open, reason = await sugar.can_open_position(symbol, volume)

    if can_open:
        print(f"Validation passed: {reason}")

        # Безопасно открывать
        ticket = await sugar.buy_market(symbol, volume=volume)
        print(f"Order opened: {ticket}")
    else:
        print(f"Cannot open position: {reason}")

# Вывод:
# Validation passed: OK
# Order opened: 123456789
```

### Пример 2: Проверка маржи перед торговлей

```python
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

    # Хотим открыть крупную позицию
    desired_volume = 10.0

    # Проверить, возможно ли
    can_open, reason = await sugar.can_open_position(symbol, desired_volume)

    if not can_open:
        print(f"Cannot open {desired_volume} lots: {reason}")

        # Попробовать меньший размер
        for volume in [5.0, 2.0, 1.0, 0.5]:
            can_open, reason = await sugar.can_open_position(symbol, volume)

            if can_open:
                print(f"Can open {volume} lots")
                ticket = await sugar.buy_market(symbol, volume=volume)
                print(f"Opened: {ticket}")
                break
    else:
        print(f"Can open full {desired_volume} lots")

# Вывод:
# Cannot open 10.0 lots: Check failed: code=1
# Can open 2.0 lots
# Opened: 123456789
```

### Пример 3: Проверка нескольких символов

```python
async def validate_watchlist():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Проверить несколько символов
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
    volume = 0.1

    print("Checking which symbols can be traded:")

    tradable = []
    not_tradable = []

    for symbol in symbols:
        can_open, reason = await sugar.can_open_position(symbol, volume)

        if can_open:
            tradable.append(symbol)
            print(f"  {symbol}: OK")
        else:
            not_tradable.append(symbol)
            print(f"  {symbol}: {reason}")

    print(f"\nTradable ({len(tradable)}): {tradable}")
    print(f"Not tradable ({len(not_tradable)}): {not_tradable}")
```

---

## Типичные ошибки

**Ошибка 1: Ожидание подробных сообщений об ошибках**
```python
# ОШИБКА: строка причины может быть не очень информативной
can_open, reason = await sugar.can_open_position("EURUSD", 100.0)

if not can_open:
    print(reason)  # Может быть просто "Check failed: code=1"
```

**Решение:** Проверяйте конкретные условия отдельно
```python
# Проверить маржу отдельно
margin_needed = await sugar.calculate_required_margin("EURUSD", 100.0)
free_margin = await sugar.get_free_margin()

if margin_needed > free_margin:
    print(f"Insufficient margin: need ${margin_needed:.2f}, have ${free_margin:.2f}")
```

**Ошибка 2: Предположение, что проверка гарантирует успех**
```python
# Проверка пройдена, но ордер всё равно может не сработать
can_open, reason = await sugar.can_open_position("EURUSD", 1.0)

if can_open:
    # Рыночные условия могут измениться между проверкой и исполнением
    ticket = await sugar.buy_market("EURUSD", volume=1.0)  # Всё равно может не сработать
```

**Решение:** Обрабатывайте ошибки ордера
```python
can_open, reason = await sugar.can_open_position("EURUSD", 1.0)

if can_open:
    try:
        ticket = await sugar.buy_market("EURUSD", volume=1.0)
    except Exception as e:
        print(f"Order failed despite validation: {e}")
```

**Ошибка 3: Проверка только ордеров BUY**
```python
# can_open_position проверяет только ордера BUY
can_open, reason = await sugar.can_open_position("EURUSD", 1.0)

# Но вы можете захотеть открыть SELL
ticket = await sugar.sell_market("EURUSD", volume=1.0)
```

**Решение:** Проверка независима от направления для маржи
```python
# Для целей маржи проверка BUY/SELL схожа
# Требования к объёму и марже одинаковы
can_open, reason = await sugar.can_open_position("EURUSD", 1.0)

if can_open:
    # Любое направление должно сработать
    ticket = await sugar.sell_market("EURUSD", volume=1.0)
```

---

## Полезные советы

**Совет 1: Обёртка для безопасной торговли**
```python
async def safe_buy_market(sugar, symbol, volume):
    """Открыть позицию BUY с проверкой."""
    # Сначала проверить
    can_open, reason = await sugar.can_open_position(symbol, volume)

    if not can_open:
        raise ValueError(f"Cannot open position: {reason}")

    # Открыть позицию
    ticket = await sugar.buy_market(symbol, volume=volume)

    return ticket

# Использование
try:
    ticket = await safe_buy_market(sugar, "EURUSD", 1.0)
    print(f"Opened: {ticket}")
except ValueError as e:
    print(f"Error: {e}")
```

**Совет 2: Найти максимальный торгуемый объём**
```python
async def find_max_volume(sugar, symbol, start_volume=10.0):
    """Найти максимальный объём, который можно открыть."""
    volume = start_volume

    # Двоичный поиск максимума
    while volume > 0.01:
        can_open, reason = await sugar.can_open_position(symbol, volume)

        if can_open:
            return volume

        # Попробовать половину
        volume = volume / 2

    return 0.01  # Минимум

# Использование
max_vol = await find_max_volume(sugar, "EURUSD", start_volume=10.0)
print(f"Maximum volume: {max_vol} lots")
```

**Совет 3: Чек-лист предторговой проверки**
```python
async def validate_trade(sugar, symbol, volume):
    """Полная проверка сделки."""
    checks = {
        "symbol_exists": False,
        "can_open": False,
        "sufficient_margin": False
    }

    # Проверка 1: символ существует
    exists = await sugar.is_symbol_available(symbol)
    checks["symbol_exists"] = exists

    if not exists:
        return checks, "Symbol not available"

    # Проверка 2: можно открыть позицию
    can_open, reason = await sugar.can_open_position(symbol, volume)
    checks["can_open"] = can_open

    if not can_open:
        return checks, f"Validation failed: {reason}"

    # Проверка 3: проверка маржи
    margin_needed = await sugar.calculate_required_margin(symbol, volume)
    free_margin = await sugar.get_free_margin()
    checks["sufficient_margin"] = margin_needed <= free_margin

    if margin_needed > free_margin:
        return checks, f"Insufficient margin: ${margin_needed:.2f} needed, ${free_margin:.2f} available"

    return checks, "All checks passed"

# Использование
checks, message = await validate_trade(sugar, "EURUSD", 1.0)
print(f"Validation: {message}")
print(f"Checks: {checks}")

if all(checks.values()):
    ticket = await sugar.buy_market("EURUSD", volume=1.0)
```

---

## 📚 См. также

- [calculate_required_margin](calculate_required_margin.md) - Рассчитать необходимую маржу
- [get_free_margin](../2.%20Account_Properties/get_free_margin.md) - Проверить доступную маржу
- [buy_market](../4.%20Simple_Trading/buy_market.md) - Открыть позицию BUY
- [calculate_position_size](calculate_position_size.md) - Рассчитать безопасный размер позиции
