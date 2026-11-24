# Получить число знаков символа (`get_symbol_digits`)

> **Sugar-метод:** Возвращает число десятичных знаков в цене символа.

**Информация об API:**

* **Метод:** `sugar.get_symbol_digits(symbol)`
* **Возвращает:** Число знаков после запятой (целое число)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_symbol_digits(self, symbol: str) -> int
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
| `int` | Число десятичных знаков (например, 5 для EURUSD, 3 для USDJPY, 2 для XAUUSD) |

---

## 🏛️ Основное

**Что делает:**

- Получает десятичную точность для цен символа
- Необходимо для форматирования цен
- Используется в расчётах цен
- Значение, специфичное для брокера

**Ключевое поведение:**

- Основные пары форекс обычно имеют 5 знаков (EURUSD: 1.08432)
- Пары с JPY обычно имеют 3 знака (USDJPY: 149.385)
- Металлы обычно имеют 2 знака (XAUUSD: 2043.50)
- Требуется для корректного отображения цены
- Используется в расчётах округления

---

## ⚡ Под капотом

```
MT5Sugar.get_symbol_digits()
    ↓ вызывает
MT5Service.get_symbol_integer(symbol, SYMBOL_DIGITS)
    ↓ вызывает
MT5Account.symbol_info_integer()
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoInteger(property=SYMBOL_DIGITS)
    ↓ терминал MT5
    ↓ возвращает значение digits
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_symbol_integer() со свойством SYMBOL_DIGITS
2. Service перенаправляет в Account.symbol_info_integer()
3. Account отправляет gRPC-запрос с перечислением свойства
4. Терминал извлекает значение digits для символа
5. Возвращает целое число (число десятичных знаков)

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1697`
- Service: `src/pymt5/mt5_service.py:497`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:951`

---

## Когда использовать

**Используйте `get_symbol_digits()`, когда:**

- Форматируете цены для отображения
- Округляете цены до корректной точности
- Рассчитываете разницу цен
- Логируете значения цен
- Строите проверку ввода цены

**Не используйте, когда:**

- У вас уже есть SymbolInfo (используйте info.digits)
- Символы заданы жёстко с известными знаками
- Точное форматирование не нужно
- Работаете с объёмами (не ценами)

---

## 🔗 Примеры

### Пример 1: Корректное форматирование цен

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def format_prices():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbols = ["EURUSD", "USDJPY", "XAUUSD"]

    for symbol in symbols:
        # Получить число знаков
        digits = await sugar.get_symbol_digits(symbol)

        # Получить текущую цену
        bid = await sugar.get_bid(symbol)

        # Форматировать с корректной точностью
        formatted = f"{bid:.{digits}f}"

        print(f"{symbol}: {formatted} ({digits} digits)")

# Вывод:
# EURUSD: 1.08432 (5 digits)
# USDJPY: 149.385 (3 digits)
# XAUUSD: 2043.50 (2 digits)
```

### Пример 2: Округление цены до корректной точности

```python
async def round_price():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Пользователь рассчитывает собственную цену
    calculated_price = 1.084567890123  # Слишком много знаков

    # Получить корректную точность
    digits = await sugar.get_symbol_digits(symbol)

    # Округлить до корректной точности
    valid_price = round(calculated_price, digits)

    print(f"Calculated: {calculated_price}")
    print(f"Rounded ({digits} digits): {valid_price:.{digits}f}")

    # Теперь безопасно использовать в ордере
    ticket = await sugar.buy_limit(
        symbol,
        volume=0.1,
        price=valid_price
    )

# Вывод:
# Calculated: 1.084567890123
# Rounded (5 digits): 1.08457
```

### Пример 3: Расчёт стоимости пипса

```python
async def calculate_pips():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"

    # Получить две цены
    price1 = 1.08432
    price2 = 1.08567

    # Получить число знаков для определения размера пипса
    digits = await sugar.get_symbol_digits(symbol)

    # Рассчитать разницу
    diff = abs(price2 - price1)

    # Перевести в пипсы на основе числа знаков
    if digits == 5 or digits == 3:
        # 5-значное ценообразование: 1 пипс = 10 пунктов
        pips = diff * (10 ** (digits - 1)) / 10
    elif digits == 4 or digits == 2:
        # 4-значное ценообразование: 1 пипс = 1 пункт
        pips = diff * (10 ** digits)
    else:
        pips = 0

    print(f"{symbol} ({digits} digits):")
    print(f"Price 1: {price1:.{digits}f}")
    print(f"Price 2: {price2:.{digits}f}")
    print(f"Difference: {pips:.1f} pips")

# Вывод:
# EURUSD (5 digits):
# Price 1: 1.08432
# Price 2: 1.08567
# Difference: 13.5 pips
```

---

## Типичные ошибки

**Ошибка 1: Жёсткое задание числа знаков**
```python
# ОШИБКА: число знаков может различаться у брокеров
price = 1.08432
formatted = f"{price:.5f}"  # Предполагает 5 знаков

# Работает у некоторых брокеров, но не у других
```

**Решение:** Всегда получайте динамически
```python
digits = await sugar.get_symbol_digits(symbol)
formatted = f"{price:.{digits}f}"
```

**Ошибка 2: Путаница digits с point**
```python
# ОШИБКА: digits != значение point
digits = await sugar.get_symbol_digits("EURUSD")  # Возвращает 5

# Это НЕ то же самое, что point (0.00001)
point = 10 ** -digits  # 0.00001 ✓
```

**Решение:** Используйте SymbolInfo для point
```python
info = await sugar.get_symbol_info("EURUSD")
digits = info.digits  # 5
point = info.point    # 0.00001
```

**Ошибка 3: Использование неправильного десятичного разделителя**
```python
# Локаль системы может использовать запятую
import locale
locale.setlocale(locale.LC_ALL, 'de_DE')

price = 1.08432
formatted = f"{price:.5f}"  # В некоторых локалях может вывести "1,08432"

# MT5 ожидает точку, а не запятую
```

**Решение:** Принудительно используйте точку в качестве разделителя
```python
# Всегда используйте точку для MT5
formatted = f"{price:.{digits}f}".replace(',', '.')

# Или используйте явное форматирование
formatted = "{:.{}f}".format(price, digits)
```

---

## Полезные советы

**Совет 1: Вспомогательная функция форматирования цены**
```python
async def format_price(sugar, symbol, price):
    """Форматировать цену с корректной точностью для символа."""
    digits = await sugar.get_symbol_digits(symbol)
    return f"{price:.{digits}f}"

# Использование
bid = await sugar.get_bid("EURUSD")
formatted = await format_price(sugar, "EURUSD", bid)
print(f"BID: {formatted}")
```

**Совет 2: Проверка цены**
```python
async def validate_price_precision(sugar, symbol, price):
    """Проверить, корректна ли точность цены."""
    digits = await sugar.get_symbol_digits(symbol)

    # Округлить до корректной точности
    rounded = round(price, digits)

    # Проверить, изменилась ли цена
    if rounded != price:
        print(f"Warning: Price {price} rounded to {rounded:.{digits}f}")
        return rounded

    return price

# Использование
price = 1.084567890  # Слишком много знаков
valid_price = await validate_price_precision(sugar, "EURUSD", price)
```

**Совет 3: Таблица цен по нескольким символам**
```python
async def price_table(sugar, symbols):
    """Отобразить отформатированные цены для нескольких символов."""
    print(f"{'Symbol':<10} {'BID':<12} {'ASK':<12} {'Spread'}")
    print("-" * 50)

    for symbol in symbols:
        digits = await sugar.get_symbol_digits(symbol)
        bid = await sugar.get_bid(symbol)
        ask = await sugar.get_ask(symbol)
        spread = ask - bid

        print(f"{symbol:<10} "
              f"{bid:<12.{digits}f} "
              f"{ask:<12.{digits}f} "
              f"{spread:.{digits}f}")

# Использование
await price_table(sugar, ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"])

# Вывод:
# Symbol     BID          ASK          Spread
# --------------------------------------------------
# EURUSD     1.08432      1.08445      0.00013
# GBPUSD     1.26789      1.26805      0.00016
# USDJPY     149.385      149.398      0.013
# XAUUSD     2043.50      2043.80      0.30
```

---

## 📚 См. также

- [get_symbol_info](get_symbol_info.md) - Получить полную информацию о символе (включает digits)
- [get_bid](../3.%20Prices_Quotes/get_bid.md) - Получить текущую цену BID
- [get_ask](../3.%20Prices_Quotes/get_ask.md) - Получить текущую цену ASK
