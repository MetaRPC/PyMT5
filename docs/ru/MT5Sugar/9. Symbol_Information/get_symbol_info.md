# Получить информацию о символе (`get_symbol_info`)

> **Sugar-метод:** Возвращает полные торговые параметры символа.

**Информация об API:**

* **Метод:** `sugar.get_symbol_info(symbol)`
* **Возвращает:** Dataclass `SymbolInfo` с торговыми параметрами
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_symbol_info(self, symbol: str) -> SymbolInfo
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Да | - | Торговый символ (например, "EURUSD") |

---

## Возвращаемое значение

Dataclass `SymbolInfo` со следующими полями:

| Поле | Тип | Описание |
|-------|------|-------------|
| `name` | `str` | Имя символа |
| `bid` | `float` | Текущая цена BID |
| `ask` | `float` | Текущая цена ASK |
| `spread` | `int` | Текущий спред в пунктах |
| `digits` | `int` | Число десятичных знаков в цене |
| `point` | `float` | Минимальное изменение цены (0.00001 для EURUSD) |
| `volume_min` | `float` | Минимальный объём в лотах |
| `volume_max` | `float` | Максимальный объём в лотах |
| `volume_step` | `float` | Шаг объёма (например, 0.01) |
| `contract_size` | `float` | Размер контракта (100 000 для стандартного форекс) |

**Вызывает исключение:**

- `ValueError`, если символ не найден

---

## 🏛️ Основное

**Что делает:**

- Получает полные параметры символа за один вызов
- Возвращает структурированный объект SymbolInfo
- Эффективнее нескольких отдельных вызовов
- Включает текущие цены и торговые ограничения

**Ключевое поведение:**

- Вызывает ValueError, если символ не существует
- Возвращает текущие цены (bid/ask)
- Включает ограничения по объёму для проверки
- Размер контракта для расчёта маржи/пипса

---

## ⚡ Под капотом

```
MT5Sugar.get_symbol_info()
    ↓ вызывает
MT5Service.get_symbol_params_many(name_filter=symbol)
    ↓ вызывает
MT5Account.symbol_params_many()
    ↓ gRPC protobuf
MarketInfoService.SymbolParamsMany()
    ↓ терминал MT5
    ↓ извлекает 10 ключевых полей в SymbolInfo
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_symbol_params_many() с фильтром по символу
2. Service перенаправляет в Account.symbol_params_many()
3. Account отправляет gRPC-запрос в терминал
4. Sugar извлекает 10 ключевых полей из SymbolParams
5. Возвращает dataclass SymbolInfo

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1615`
- Dataclass SymbolInfo: `src/pymt5/mt5_sugar.py:179`
- Service: `src/pymt5/mt5_service.py:658`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1221`

---

## Когда использовать

**Используйте `get_symbol_info()`, когда:**

- Нужно несколько параметров символа
- Проверяете объём перед торговлей
- Рассчитываете стоимость пипсов
- Форматируете цены с корректным числом знаков
- Проверяете торговые ограничения

**Не используйте, когда:**

- Нужна только текущая цена (используйте `get_bid()`/`get_ask()`)
- Нужен только один параметр (используйте специальные методы)
- Нужны все символы (используйте `get_all_symbols()`)

---

## 🔗 Примеры

### Пример 1: Базовая информация о символе

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def symbol_details():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить информацию по EURUSD
    info = await sugar.get_symbol_info("EURUSD")

    print(f"Symbol: {info.name}")
    print(f"BID: {info.bid:.{info.digits}f}")
    print(f"ASK: {info.ask:.{info.digits}f}")
    print(f"Spread: {info.spread} points")
    print(f"Digits: {info.digits}")
    print(f"Point: {info.point}")
    print(f"Volume limits: {info.volume_min} - {info.volume_max}")
    print(f"Volume step: {info.volume_step}")
    print(f"Contract size: {info.contract_size}")

# Вывод:
# Symbol: EURUSD
# BID: 1.08432
# ASK: 1.08445
# Spread: 13 points
# Digits: 5
# Point: 0.00001
# Volume limits: 0.01 - 100.0
# Volume step: 0.01
# Contract size: 100000.0
```

### Пример 2: Проверка объёма

```python
async def validate_volume():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    desired_volume = 0.15

    # Получить информацию о символе
    info = await sugar.get_symbol_info(symbol)

    # Проверить объём
    if desired_volume < info.volume_min:
        print(f"Volume too small (min: {info.volume_min})")
    elif desired_volume > info.volume_max:
        print(f"Volume too large (max: {info.volume_max})")
    elif (desired_volume % info.volume_step) != 0:
        # Округлить до ближайшего шага
        adjusted = round(desired_volume / info.volume_step) * info.volume_step
        print(f"Volume adjusted: {desired_volume} → {adjusted}")
        desired_volume = adjusted

    # Теперь безопасно торговать
    ticket = await sugar.buy_market(symbol, volume=desired_volume)
```

### Пример 3: Расчёт стоимости пипса

```python
async def calculate_pip_value():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    info = await sugar.get_symbol_info(symbol)

    # Рассчитать стоимость пипса для 1 лота
    # Для форекс: pip_value = point * 10 * contract_size
    pip_value = info.point * 10 * info.contract_size

    print(f"{symbol} Pip Value (1 lot):")
    print(f"  Point: {info.point}")
    print(f"  Contract size: {info.contract_size}")
    print(f"  1 pip = ${pip_value:.2f}")

    # Для 0.1 лота
    pip_value_mini = pip_value * 0.1
    print(f"  0.1 lot: ${pip_value_mini:.2f} per pip")

# Вывод:
# EURUSD Pip Value (1 lot):
#   Point: 1e-05
#   Contract size: 100000.0
#   1 pip = $10.00
#   0.1 lot: $1.00 per pip
```

---

## Типичные ошибки

**Ошибка 1: Необработка ValueError**
```python
# ОШИБКА: символ не существует
try:
    info = await sugar.get_symbol_info("FAKEUSD")
except ValueError as e:
    print(e)  # "Symbol FAKEUSD not found"
```

**Решение:** Оберните в try-except или сначала проверьте
```python
# Сначала проверить существование
exists = await sugar.is_symbol_available("EURUSD")

if exists:
    info = await sugar.get_symbol_info("EURUSD")
```

**Ошибка 2: Использование устаревших цен**
```python
# Цены в SymbolInfo — это снимок
info = await sugar.get_symbol_info("EURUSD")
await asyncio.sleep(60)

# info.bid и info.ask теперь устарели на 60 секунд!
```

**Решение:** Обновите info или используйте get_bid()/get_ask()
```python
# Для текущей цены используйте специальные методы
current_bid = await sugar.get_bid("EURUSD")

# Или обновите информацию о символе
info = await sugar.get_symbol_info("EURUSD")
```

**Ошибка 3: Путаница point и пипса**
```python
# Point != Pip
info = await sugar.get_symbol_info("EURUSD")

# Point = минимальное изменение цены (0.00001)
# Pip = 10 пунктов (0.0001)

# Рассчитать пипсы из пунктов
spread_pips = info.spread / 10  # Перевести пункты в пипсы
```

---

## Полезные советы

**Совет 1: Корректно форматируйте цены**
```python
info = await sugar.get_symbol_info("EURUSD")

# Использовать digits для форматирования
price = info.bid
formatted = f"{price:.{info.digits}f}"
print(f"Price: {formatted}")  # 1.08432 (5 знаков)
```

**Совет 2: Проверка и корректировка объёма**
```python
def adjust_volume(desired, info):
    """Скорректировать объём под ограничения символа."""
    # Ограничить min/max
    volume = max(info.volume_min, min(desired, info.volume_max))

    # Округлить до шага
    volume = round(volume / info.volume_step) * info.volume_step

    return volume

info = await sugar.get_symbol_info("EURUSD")
safe_volume = adjust_volume(0.15, info)
```

**Совет 3: Кэширование информации о символе**
```python
# Кэшировать часто используемые символы
symbol_cache = {}

async def get_cached_symbol_info(sugar, symbol):
    """Получить информацию о символе с кэшированием."""
    if symbol not in symbol_cache:
        symbol_cache[symbol] = await sugar.get_symbol_info(symbol)

    return symbol_cache[symbol]

# Использовать кэшированную информацию
info = await get_cached_symbol_info(sugar, "EURUSD")
```

---

## 📚 См. также

- [get_all_symbols](get_all_symbols.md) - Список всех доступных символов
- [is_symbol_available](is_symbol_available.md) - Проверить существование символа
- [get_symbol_digits](get_symbol_digits.md) - Получить только число десятичных знаков
- [get_min_stop_level](get_min_stop_level.md) - Получить минимальное расстояние SL/TP
