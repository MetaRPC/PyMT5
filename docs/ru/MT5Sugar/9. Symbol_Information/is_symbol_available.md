# Доступен ли символ (`is_symbol_available`)

> **Sugar-метод:** Проверяет, существует ли торговый символ и доступен ли он.

**Информация об API:**

* **Метод:** `sugar.is_symbol_available(symbol)`
* **Возвращает:** Булево значение, указывающее, существует ли символ
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def is_symbol_available(self, symbol: str) -> bool
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Да | - | Торговый символ для проверки (например, "EURUSD") |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `bool` | `True`, если символ существует и доступен, иначе `False` |

---

## 🏛️ Основное

**Что делает:**

- Проверяет, существует ли символ у брокера
- Проверяет, доступен ли символ в данный момент
- Быстрая проверка перед торговлей
- Возвращает булево значение (True/False)

**Ключевое поведение:**

- Возвращает False, если символ не существует
- Возвращает False, если символ отключён
- Имя символа чувствительно к регистру
- Быстрый одиночный запрос (не пакетный)
- НЕ проверяет, торгуем ли символ (только существование)

---

## ⚡ Под капотом

```
MT5Sugar.is_symbol_available()
    ↓ вызывает
MT5Service.symbol_exist(symbol)
    ↓ вызывает
MT5Account.symbol_exist()
    ↓ gRPC protobuf
MarketInfoService.SymbolExist()
    ↓ терминал MT5
    ↓ возвращает (exists: bool, _)
```

**Цепочка вызовов:**

1. Sugar вызывает Service.symbol_exist() с именем символа
2. Service перенаправляет в Account.symbol_exist()
3. Account отправляет gRPC-запрос в терминал
4. Терминал проверяет существование символа
5. Возвращает кортеж (exists: bool, unknown)
6. Sugar извлекает и возвращает булево значение exists

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1672`
- Service: `src/pymt5/mt5_service.py:567`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:730`

---

## Когда использовать

**Используйте `is_symbol_available()`, когда:**

- Проверяете пользовательский ввод перед торговлей
- Проверяете существование символа перед получением информации
- Предотвращаете ошибки в торговых циклах
- Проверяете символы в конфигурации
- Строите безопасные торговые приложения

**Не используйте, когда:**

- Уже известно, что символ существует (пропустите проверку)
- Нужна полная информация о символе (используйте `get_symbol_info()`)
- Выводите список всех символов (используйте `get_all_symbols()`)
- Символ задан жёстко и заведомо валиден

---

## 🔗 Примеры

### Пример 1: Проверка символа перед торговлей

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

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

    # Проверить, существует ли символ
    if await sugar.is_symbol_available(symbol):
        print(f"{symbol} is available")

        # Безопасно торговать
        ticket = await sugar.buy_market(symbol, volume=0.1)
        print(f"Order placed: {ticket}")
    else:
        print(f"{symbol} not available on this broker")

# Вывод:
# EURUSD is available
# Order placed: 123456789
```

### Пример 2: Проверка пользовательского ввода

```python
async def validate_user_symbol():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Пользователь вводит символ
    user_symbol = input("Enter symbol: ").upper()

    # Проверить
    if not await sugar.is_symbol_available(user_symbol):
        print(f"Error: '{user_symbol}' is not available")
        print("Please check the symbol name and try again")
        return

    # Продолжить с валидным символом
    info = await sugar.get_symbol_info(user_symbol)
    print(f"{user_symbol}: BID={info.bid}, ASK={info.ask}")

# Пример взаимодействия:
# Enter symbol: FAKEUSD
# Error: 'FAKEUSD' is not available
# Please check the symbol name and try again
```

### Пример 3: Проверка списка символов

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

    # Список наблюдения пользователя
    watchlist = ["EURUSD", "GBPUSD", "FAKEUSD", "USDJPY", "XAUUSD"]

    # Проверить все символы
    valid_symbols = []
    invalid_symbols = []

    for symbol in watchlist:
        if await sugar.is_symbol_available(symbol):
            valid_symbols.append(symbol)
        else:
            invalid_symbols.append(symbol)

    print(f"Valid symbols ({len(valid_symbols)}): {valid_symbols}")
    print(f"Invalid symbols ({len(invalid_symbols)}): {invalid_symbols}")

# Вывод:
# Valid symbols (4): ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
# Invalid symbols (1): ['FAKEUSD']
```

---

## Типичные ошибки

**Ошибка 1: Чувствительность к регистру**
```python
# ОШИБКА: регистр символа имеет значение
exists = await sugar.is_symbol_available("eurusd")
# Возвращает False, если брокер использует "EURUSD"
```

**Решение:** Всегда используйте верхний регистр
```python
symbol = "eurusd"
exists = await sugar.is_symbol_available(symbol.upper())
```

**Ошибка 2: Предположение, что доступный означает торгуемый**
```python
# Символ существует, но может быть не торгуем прямо сейчас
if await sugar.is_symbol_available("EURUSD"):
    # Символ существует, но может быть:
    # - Рынок закрыт
    # - Торговля отключена
    # - Недостаточно маржи
    await sugar.buy_market("EURUSD", volume=0.1)  # Всё равно может не сработать
```

**Решение:** Обрабатывайте торговые ошибки отдельно
```python
if await sugar.is_symbol_available("EURUSD"):
    try:
        ticket = await sugar.buy_market("EURUSD", volume=0.1)
    except Exception as e:
        print(f"Trade failed: {e}")
```

**Ошибка 3: Проверка перед каждой операцией**
```python
# Избыточные проверки
if await sugar.is_symbol_available("EURUSD"):
    info = await sugar.get_symbol_info("EURUSD")  # Уже проверяет

if await sugar.is_symbol_available("EURUSD"):
    bid = await sugar.get_bid("EURUSD")  # Тоже проверяет
```

**Решение:** Проверьте один раз, затем продолжайте
```python
# Единственная проверка
if await sugar.is_symbol_available("EURUSD"):
    # Все последующие вызовы сработают
    info = await sugar.get_symbol_info("EURUSD")
    bid = await sugar.get_bid("EURUSD")
```

---

## Полезные советы

**Совет 1: Проверка с резервным вариантом**
```python
async def get_symbol_with_fallback(primary, fallback):
    """Попробовать основной символ, при недоступности использовать резервный."""
    if await sugar.is_symbol_available(primary):
        return primary
    elif await sugar.is_symbol_available(fallback):
        print(f"{primary} not available, using {fallback}")
        return fallback
    else:
        raise ValueError(f"Neither {primary} nor {fallback} available")

# Использование
symbol = await get_symbol_with_fallback("EURUSD", "EURUSD.a")
```

**Совет 2: Вспомогательная функция пакетной проверки**
```python
async def validate_symbols(symbols: List[str]) -> dict:
    """Эффективно проверить несколько символов."""
    results = {}

    for symbol in symbols:
        results[symbol] = await sugar.is_symbol_available(symbol)

    return results

# Использование
symbols = ["EURUSD", "GBPUSD", "FAKEUSD"]
results = await validate_symbols(symbols)

valid = [s for s, exists in results.items() if exists]
invalid = [s for s, exists in results.items() if not exists]

print(f"Valid: {valid}")
print(f"Invalid: {invalid}")
```

**Совет 3: Безопасный получатель символа**
```python
async def get_symbol_info_safe(symbol: str):
    """Получить информацию о символе с проверкой существования."""
    if not await sugar.is_symbol_available(symbol):
        raise ValueError(f"Symbol '{symbol}' not available")

    return await sugar.get_symbol_info(symbol)

# Использование
try:
    info = await get_symbol_info_safe("EURUSD")
    print(f"Got info: {info.name}")
except ValueError as e:
    print(f"Error: {e}")
```

---

## 📚 См. также

- [get_symbol_info](get_symbol_info.md) - Получить полную информацию о символе
- [get_all_symbols](get_all_symbols.md) - Список всех доступных символов
- [get_symbol_digits](get_symbol_digits.md) - Получить число десятичных знаков
