# Получить минимальный стоп-уровень (`get_min_stop_level`)

> **Sugar-метод:** Возвращает минимально допустимое расстояние для стоп-лосса и тейк-профита в пунктах.

**Информация об API:**

* **Метод:** `sugar.get_min_stop_level(symbol)`
* **Возвращает:** Минимальный стоп-уровень в пунктах (целое число)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_min_stop_level(self, symbol: str) -> int
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Да | - | Торговый символ (например, "EURUSD") |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `int` | Минимальный стоп-уровень в пунктах (0 означает отсутствие ограничения) |

---

## 🏛️ Основное

**Что делает:**

- Получает минимально допустимое расстояние между ценой и SL/TP
- Возвращает значение в пунктах (не в пипсах)
- Используется для проверки размещения SL/TP
- Ограничение, задаваемое брокером

**Ключевое поведение:**

- Возвращает 0, если минимального ограничения нет
- Значение в пунктах (EURUSD: 1 пункт = 0.00001)
- Один и тот же минимум применяется и к SL, и к TP
- Измеряется от текущей цены, а не от цены открытия
- Нарушение этого приводит к отклонению сделки

---

## ⚡ Под капотом

```
MT5Sugar.get_min_stop_level()
    ↓ вызывает
MT5Service.get_symbol_integer(symbol, SYMBOL_TRADE_STOPS_LEVEL)
    ↓ вызывает
MT5Account.symbol_info_integer()
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoInteger(property=SYMBOL_TRADE_STOPS_LEVEL)
    ↓ терминал MT5
    ↓ возвращает минимальный стоп-уровень
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_symbol_integer() со свойством SYMBOL_TRADE_STOPS_LEVEL
2. Service перенаправляет в Account.symbol_info_integer()
3. Account отправляет gRPC-запрос с перечислением свойства
4. Терминал извлекает минимальный стоп-уровень для символа
5. Возвращает целочисленное значение в пунктах

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1677`
- Service: `src/pymt5/mt5_service.py:497`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:951`

---

## Когда использовать

**Используйте `get_min_stop_level()`, когда:**

- Проверяете SL/TP перед размещением ордера
- Рассчитываете безопасные расстояния SL/TP
- Строите логику проверки ордеров
- Предотвращаете ошибки в автоматической торговле
- Корректируете SL/TP под требования брокера

**Не используйте, когда:**

- У брокера нет ограничений (всё равно вернёт 0)
- Минимальный уровень уже известен
- SL/TP в ордерах не используются
- Выполняете только рыночные ордера без SL/TP

---

## 🔗 Примеры

### Пример 1: Проверка минимального стоп-уровня

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def check_min_level():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Получить минимальный стоп-уровень
    min_level = await sugar.get_min_stop_level(symbol)

    if min_level == 0:
        print(f"{symbol}: No minimum stop level restriction")
    else:
        print(f"{symbol}: Minimum stop level = {min_level} points")

        # Получить информацию о символе для перевода пунктов в цену
        info = await sugar.get_symbol_info(symbol)
        min_distance = min_level * info.point

        print(f"Minimum SL/TP distance: {min_distance:.{info.digits}f}")

# Вывод:
# EURUSD: Minimum stop level = 20 points
# Minimum SL/TP distance: 0.00020
```

### Пример 2: Проверка SL/TP перед ордером

```python
async def validate_sltp():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Получить текущую цену и минимальный уровень
    bid = await sugar.get_bid(symbol)
    min_level = await sugar.get_min_stop_level(symbol)
    info = await sugar.get_symbol_info(symbol)

    # Желаемый SL в 10 пунктах от цены
    desired_sl_points = 10
    desired_sl = bid - (desired_sl_points * info.point)

    # Проверить
    if min_level > 0 and desired_sl_points < min_level:
        print(f"ERROR: SL too close to price")
        print(f"Desired: {desired_sl_points} points")
        print(f"Minimum: {min_level} points")

        # Скорректировать до минимума
        adjusted_sl = bid - (min_level * info.point)
        print(f"Adjusted SL: {adjusted_sl:.{info.digits}f}")
    else:
        print(f"SL validation passed")

        # Безопасно размещать ордер
        ticket = await sugar.sell_market_with_sltp(
            symbol,
            volume=0.1,
            sl=desired_sl
        )

# Вывод:
# ERROR: SL too close to price
# Desired: 10 points
# Minimum: 20 points
# Adjusted SL: 1.08412
```

### Пример 3: Калькулятор безопасных SL/TP

```python
async def calculate_safe_sltp():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Получить требования
    ask = await sugar.get_ask(symbol)
    min_level = await sugar.get_min_stop_level(symbol)
    info = await sugar.get_symbol_info(symbol)

    # Пользователь хочет SL/TP в 50 пипсов
    desired_pips = 50
    desired_points = desired_pips * 10  # 500 пунктов

    # Проверить относительно минимума
    actual_points = max(desired_points, min_level)

    if actual_points > desired_points:
        print(f"Adjusted from {desired_pips} to {actual_points/10} pips (broker minimum)")

    # Рассчитать SL/TP для ордера BUY
    sl_price = ask - (actual_points * info.point)
    tp_price = ask + (actual_points * info.point)

    print(f"Entry: {ask:.{info.digits}f}")
    print(f"SL: {sl_price:.{info.digits}f} ({actual_points} points)")
    print(f"TP: {tp_price:.{info.digits}f} ({actual_points} points)")

    # Разместить ордер
    ticket = await sugar.buy_market_with_sltp(
        symbol,
        volume=0.1,
        sl=sl_price,
        tp=tp_price
    )
    print(f"Order placed: {ticket}")
```

---

## Типичные ошибки

**Ошибка 1: Путаница пунктов и пипсов**
```python
# ОШИБКА: min_level в пунктах, а не в пипсах
min_level = await sugar.get_min_stop_level("EURUSD")
# Возвращает 20 (пунктов), а не 2 (пипса)

# Установка SL в 20 пипсах вместо 20 пунктов
info = await sugar.get_symbol_info("EURUSD")
sl = bid - (min_level * info.point * 10)  # НЕВЕРНО! Слишком далеко
```

**Решение:** Используйте пункты напрямую
```python
min_level = await sugar.get_min_stop_level("EURUSD")
info = await sugar.get_symbol_info("EURUSD")

# Верно: min_level уже в пунктах
sl = bid - (min_level * info.point)
```

**Ошибка 2: Непроверка на ноль**
```python
# Предположение, что минимум всегда существует
min_level = await sugar.get_min_stop_level("EURUSD")

# Если возвращает 0, минимум не требуется
# Ваша логика проверки может дать сбой
if desired_points < min_level:  # Всегда False, если min_level=0
    print("Too close")
```

**Решение:** Проверяйте на ноль явно
```python
min_level = await sugar.get_min_stop_level("EURUSD")

if min_level > 0 and desired_points < min_level:
    print(f"Too close, minimum is {min_level} points")
```

**Ошибка 3: Использование цены открытия вместо текущей цены**
```python
# ОШИБКА: минимум от ТЕКУЩЕЙ цены, а не от цены открытия
open_price = 1.08500
sl = open_price - (min_level * info.point)

# Если текущая цена сдвинулась, этот SL может нарушить минимум
```

**Решение:** Всегда используйте текущую рыночную цену
```python
# Для позиции BUY (проверка относительно BID)
current_bid = await sugar.get_bid(symbol)
sl = current_bid - (min_level * info.point)

# Для позиции SELL (проверка относительно ASK)
current_ask = await sugar.get_ask(symbol)
sl = current_ask + (min_level * info.point)
```

---

## Полезные советы

**Совет 1: Вспомогательная функция проверки SL/TP**
```python
async def validate_sltp_distance(sugar, symbol, order_type, price, sl, tp):
    """Проверить, что SL/TP соответствуют требованию минимального расстояния."""
    min_level = await sugar.get_min_stop_level(symbol)

    if min_level == 0:
        return True  # Нет ограничения

    info = await sugar.get_symbol_info(symbol)
    min_distance = min_level * info.point

    # Проверить SL
    if sl is not None:
        sl_distance = abs(price - sl)
        if sl_distance < min_distance:
            print(f"SL too close: {sl_distance:.{info.digits}f} < {min_distance:.{info.digits}f}")
            return False

    # Проверить TP
    if tp is not None:
        tp_distance = abs(price - tp)
        if tp_distance < min_distance:
            print(f"TP too close: {tp_distance:.{info.digits}f} < {min_distance:.{info.digits}f}")
            return False

    return True

# Использование
ask = await sugar.get_ask("EURUSD")
sl = ask - 0.00010  # 10 пунктов

is_valid = await validate_sltp_distance(sugar, "EURUSD", "BUY", ask, sl, None)
```

**Совет 2: Автокоррекция до минимума**
```python
async def adjust_sltp_to_minimum(sugar, symbol, desired_points):
    """Обеспечить соответствие SL/TP минимальному требованию."""
    min_level = await sugar.get_min_stop_level(symbol)

    # Использовать большее из желаемого или минимума
    actual_points = max(desired_points, min_level)

    if actual_points > desired_points:
        print(f"Adjusted from {desired_points} to {actual_points} points (broker minimum)")

    return actual_points

# Использование
actual_points = await adjust_sltp_to_minimum(sugar, "EURUSD", desired_points=10)
```

**Совет 3: Вспомогательная функция перевода пунктов в цену**
```python
async def calculate_sltp_prices(sugar, symbol, order_type, distance_points):
    """Рассчитать цены SL/TP с обеспечением минимального расстояния."""
    # Получить минимум и скорректировать
    min_level = await sugar.get_min_stop_level(symbol)
    actual_points = max(distance_points, min_level)

    info = await sugar.get_symbol_info(symbol)
    distance = actual_points * info.point

    if order_type == "BUY":
        price = info.ask
        sl = price - distance
        tp = price + distance
    else:  # SELL
        price = info.bid
        sl = price + distance
        tp = price - distance

    return {
        "entry": price,
        "sl": sl,
        "tp": tp,
        "distance_points": actual_points
    }

# Использование
prices = await calculate_sltp_prices(sugar, "EURUSD", "BUY", distance_points=50)
print(f"Entry: {prices['entry']}, SL: {prices['sl']}, TP: {prices['tp']}")
```

---

## 📚 См. также

- [get_symbol_info](get_symbol_info.md) - Получить параметры символа, включая значение пункта
- [buy_market_with_sltp](../5.%20Trading_With_SLTP/buy_market_with_sltp.md) - Открыть BUY с SL/TP
- [modify_position_sltp](../6.%20Position_Management/modify_position_sltp.md) - Изменить SL/TP у позиции
