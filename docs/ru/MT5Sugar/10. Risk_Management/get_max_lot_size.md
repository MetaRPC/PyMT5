# Получить максимальный размер лота (`get_max_lot_size`)

> **Sugar-метод:** Возвращает максимально допустимый размер позиции для торгового символа.

**Информация об API:**

* **Метод:** `sugar.get_max_lot_size(symbol)`
* **Возвращает:** Максимальный объём в лотах (float)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_max_lot_size(self, symbol: str) -> float
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
| `float` | Максимальный объём в лотах (например, 100.0 для большинства валютных пар) |

---

## 🏛️ Основное

**Что делает:**

- Извлекает максимально допустимый размер лота у брокера
- Ограничение, специфичное для символа
- Необходимо для проверки объёма
- Часть торговых параметров символа

**Ключевое поведение:**

- Возвращает максимум, заданный брокером
- Обычно 100.0 лотов для основных пар форекс
- Может различаться по типу символа
- Превышение этого лимита приводит к отклонению ордера
- То же, что SymbolInfo.volume_max

---

## ⚡ Под капотом

```
MT5Sugar.get_max_lot_size()
    ↓ вызывает
MT5Service.get_symbol_double(symbol, SYMBOL_VOLUME_MAX)
    ↓ вызывает
MT5Account.symbol_info_double()
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoDouble(property=SYMBOL_VOLUME_MAX)
    ↓ терминал MT5
    ↓ возвращает максимальный объём
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_symbol_double() со свойством SYMBOL_VOLUME_MAX
2. Service перенаправляет в Account.symbol_info_double()
3. Account отправляет gRPC-запрос с перечислением свойства
4. Терминал извлекает максимальный объём для символа
5. Возвращает значение float (максимум лотов)

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1821`
- Service: `src/pymt5/mt5_service.py:474`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:906`

---

## Когда использовать

**Используйте `get_max_lot_size()`, когда:**

- Проверяете крупные размеры позиций
- Строите валидаторы размера позиции
- Проверяете торговые лимиты
- Ограничиваете рассчитанные объёмы
- Строите системы управления рисками

**Не используйте, когда:**

- У вас уже есть SymbolInfo (используйте info.volume_max)
- Торгуете малыми позициями (вряд ли достигнете лимита)
- Максимум задан жёстко и известен
- Не проверяете объёмы

---

## 🔗 Примеры

### Пример 1: Проверка максимального размера лота

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def check_max_lots():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbols = ["EURUSD", "XAUUSD", "BTCUSD"]

    print("Maximum lot sizes:")

    for symbol in symbols:
        max_lots = await sugar.get_max_lot_size(symbol)
        print(f"  {symbol}: {max_lots} lots")

# Вывод:
# Maximum lot sizes:
#   EURUSD: 100.0 lots
#   XAUUSD: 50.0 lots
#   BTCUSD: 10.0 lots
```

### Пример 2: Проверка объёма перед торговлей

```python
async def safe_trade():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    desired_volume = 150.0  # Слишком большой

    # Получить максимум
    max_volume = await sugar.get_max_lot_size(symbol)

    if desired_volume > max_volume:
        print(f"ERROR: {desired_volume} lots exceeds maximum of {max_volume}")
        print(f"Reducing to maximum: {max_volume}")
        desired_volume = max_volume

    # Теперь безопасно торговать
    ticket = await sugar.buy_market(symbol, volume=desired_volume)
    print(f"Order placed: {ticket} ({desired_volume} lots)")

# Вывод:
# ERROR: 150.0 lots exceeds maximum of 100.0
# Reducing to maximum: 100.0
# Order placed: 123456789 (100.0 lots)
```

### Пример 3: Ограничение рассчитанного объёма

```python
async def calculate_and_clamp():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Рассчитать размер позиции на основе риска
    calculated_volume = await sugar.calculate_position_size(
        symbol,
        risk_percent=10.0,  # Высокий риск
        sl_pips=10  # Тесный SL
    )

    print(f"Calculated volume: {calculated_volume} lots")

    # Получить лимиты
    info = await sugar.get_symbol_info(symbol)
    max_volume = info.volume_max

    # Ограничить диапазоном
    final_volume = max(info.volume_min, min(calculated_volume, max_volume))

    if final_volume != calculated_volume:
        print(f"Volume clamped to: {final_volume} lots")

    # Торговать с безопасным объёмом
    ticket = await sugar.buy_market(symbol, volume=final_volume)
    print(f"Order placed: {ticket}")

# Вывод:
# Calculated volume: 200.0 lots
# Volume clamped to: 100.0 lots
# Order placed: 123456789
```

---

## Типичные ошибки

**Ошибка 1: Предположение одинакового максимума для всех символов**
```python
# ОШИБКА: максимум различается по символам
max_forex = 100.0  # Жёстко задано для форекс

# У криптовалют может быть другой максимум
ticket = await sugar.buy_market("BTCUSD", volume=max_forex)  # Может не сработать
```

**Решение:** Всегда получайте динамически
```python
max_volume = await sugar.get_max_lot_size("BTCUSD")
ticket = await sugar.buy_market("BTCUSD", volume=max_volume)
```

**Ошибка 2: Непроверка также минимума**
```python
# Проверяется только максимум
desired = 0.005

max_vol = await sugar.get_max_lot_size("EURUSD")
volume = min(desired, max_vol)  # 0.005

# Но минимум может быть 0.01
await sugar.buy_market("EURUSD", volume=volume)  # Не сработает
```

**Решение:** Проверяйте и min, и max
```python
info = await sugar.get_symbol_info("EURUSD")

volume = max(info.volume_min, min(desired, info.volume_max))
```

**Ошибка 3: Превышение на малую ошибку округления**
```python
# Расчёт может немного превысить из-за плавающей точки
calculated = 100.00000001

max_vol = await sugar.get_max_lot_size("EURUSD")  # 100.0

# Строгое сравнение даёт сбой
if calculated > max_vol:
    # Излишне округляет вниз
```

**Решение:** Сначала округлите до шага объёма
```python
info = await sugar.get_symbol_info("EURUSD")

# Округлить до шага
volume = round(calculated / info.volume_step) * info.volume_step

# Затем ограничить
volume = min(volume, info.volume_max)
```

---

## Полезные советы

**Совет 1: Вспомогательная функция проверки объёма**
```python
async def validate_volume(sugar, symbol, volume):
    """Проверить и скорректировать объём под ограничения."""
    info = await sugar.get_symbol_info(symbol)

    # Округлить до шага
    volume = round(volume / info.volume_step) * info.volume_step

    # Ограничить диапазоном
    volume = max(info.volume_min, min(volume, info.volume_max))

    return volume

# Использование
desired = 150.0
safe_volume = await validate_volume(sugar, "EURUSD", desired)
print(f"Adjusted from {desired} to {safe_volume}")
```

**Совет 2: Получить все ограничения по объёму**
```python
async def get_volume_constraints(sugar, symbol):
    """Получить все ограничения, связанные с объёмом."""
    info = await sugar.get_symbol_info(symbol)

    return {
        "min": info.volume_min,
        "max": info.volume_max,
        "step": info.volume_step,
        "range": f"{info.volume_min} - {info.volume_max}",
        "step_count": int((info.volume_max - info.volume_min) / info.volume_step) + 1
    }

# Использование
constraints = await get_volume_constraints(sugar, "EURUSD")
print(f"Volume range: {constraints['range']}")
print(f"Step: {constraints['step']}")
print(f"Possible values: {constraints['step_count']}")

# Вывод:
# Volume range: 0.01 - 100.0
# Step: 0.01
# Possible values: 9991
```

**Совет 3: Калькулятор безопасного объёма**
```python
async def calculate_safe_volume(sugar, symbol, desired_volume):
    """Рассчитать объём с обеспечением всех ограничений."""
    info = await sugar.get_symbol_info(symbol)

    # Округлить до шага
    volume = round(desired_volume / info.volume_step) * info.volume_step

    # Ограничить диапазоном
    if volume < info.volume_min:
        print(f"Volume {desired_volume} below minimum {info.volume_min}, using minimum")
        volume = info.volume_min
    elif volume > info.volume_max:
        print(f"Volume {desired_volume} above maximum {info.volume_max}, using maximum")
        volume = info.volume_max

    # Итоговая проверка
    if volume != desired_volume:
        print(f"Adjusted volume: {desired_volume} → {volume}")

    return volume

# Использование
volume = await calculate_safe_volume(sugar, "EURUSD", 150.0)
# Вывод: Volume 150.0 above maximum 100.0, using maximum
# Вывод: Adjusted volume: 150.0 → 100.0
```

---

## 📚 См. также

- [get_symbol_info](../9.%20Symbol_Information/get_symbol_info.md) - Получить полную информацию о символе (включает volume_max)
- [calculate_position_size](calculate_position_size.md) - Рассчитать размер позиции с риском
- [can_open_position](can_open_position.md) - Проверить, можно ли открыть позицию
