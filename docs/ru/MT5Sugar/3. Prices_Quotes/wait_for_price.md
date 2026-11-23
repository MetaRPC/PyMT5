# Ожидание обновления цены (`wait_for_price`)

> **Sugar-метод:** Ожидает корректного обновления цены с настраиваемым таймаутом.

**Информация об API:**

* **Метод:** `sugar.wait_for_price(symbol: Optional[str] = None, timeout: float = 5.0)`
* **Возвращает:** dataclass `PriceInfo` при получении цены
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def wait_for_price(
    self,
    symbol: Optional[str] = None,
    timeout: float = 5.0
) -> PriceInfo
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | Нет | `None` | Имя символа (использует значение по умолчанию, если не указано) |
| `timeout` | `float` | Нет | `5.0` | Максимальное время ожидания в секундах |

---

## Возвращаемое значение

| Поле | Тип | Описание |
|-------|------|-------------|
| `symbol` | `str` | Имя символа |
| `bid` | `float` | Текущая цена BID (цена продажи) |
| `ask` | `float` | Текущая цена ASK (цена покупки) |
| `spread` | `float` | Текущий спред (ask - bid) |
| `time` | `datetime` | Временная метка цены |

---

## 🏛️ Основное

**Что делает:**

- Пытается получить цену в пределах периода таймаута
- Использует asyncio.timeout для операции с ограничением по времени
- Вызывает TimeoutError, если цена не получена вовремя
- Возвращает PriceInfo при успехе

**Ключевое поведение:**

- Вызывает `ValueError`, если символ не указан и не задан по умолчанию
- Вызывает `TimeoutError`, если таймаут истекает до получения цены
- Таймаут по умолчанию — 5 секунд
- Внутри вызывает `get_price_info()`

---

## ⚡ Под капотом

```
MT5Sugar.wait_for_price()
    ↓ wraps with timeout
MT5Sugar.get_price_info()
    ↓ calls
MT5Service.get_symbol_tick()
    ↓ calls
MT5Account.symbol_info_tick()
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoTick()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar оборачивает get_price_info() в контекст asyncio.timeout
2. Если цена получена в пределах таймаута, возвращает PriceInfo
3. Если таймаут истекает, вызывает TimeoutError с описательным сообщением
4. Механизм таймаута предотвращает бесконечное зависание

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:545`
- Internal call to get_price_info: `src/pymt5/mt5_sugar.py:530`

---

## Когда использовать

**Используйте `wait_for_price()`, когда:**

- Запускаетесь и нужно убедиться в подключении к рынку
- Проверяете, что у символа есть живые котировки
- Нужна цена с гарантией таймаута
- Строите надёжные последовательности запуска

**Не используйте, когда:**

- Вы знаете, что рынок открыт (используйте `get_price_info()`)
- Нужны потоковые обновления (используйте стриминг прибыли позиции)
- Таймаут не важен (используйте `get_price_info()`)

---

## 🔗 Примеры

### Пример 1: Безопасный запуск подключения

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def connect_and_validate():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    try:
        # Ждём корректную цену до 10 секунд
        price = await sugar.wait_for_price(timeout=10.0)
        print(f"Connection validated! BID: {price.bid}")

    except TimeoutError as e:
        print(f"Failed to get price: {e}")
        await sugar.disconnect()
        return

    # Продолжаем торговую логику
    await sugar.disconnect()
```

### Пример 2: Проверка нескольких символов

```python
async def validate_symbols():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("YourBroker-Demo")

    symbols = ["EURUSD", "GBPUSD", "USDJPY"]

    for symbol in symbols:
        try:
            price = await sugar.wait_for_price(symbol, timeout=3.0)
            print(f"{symbol}: OK (BID: {price.bid})")

        except TimeoutError:
            print(f"{symbol}: No quotes available")

    await sugar.disconnect()
```

### Пример 3: Повтор с экспоненциальной задержкой

```python
import asyncio

async def get_price_with_retry():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    max_attempts = 3
    timeout = 5.0

    for attempt in range(max_attempts):
        try:
            price = await sugar.wait_for_price(timeout=timeout)
            print(f"Success on attempt {attempt + 1}")
            print(f"BID: {price.bid}, ASK: {price.ask}")
            break

        except TimeoutError:
            print(f"Attempt {attempt + 1} failed, retrying...")
            timeout *= 2  # Экспоненциальная задержка

            if attempt == max_attempts - 1:
                print("All attempts failed")

    await sugar.disconnect()
```

---

## Частые ошибки

**Ошибка 1: Слишком короткий таймаут**
```python
# ОШИБКА: слишком короткий таймаут для медленных соединений
try:
    price = await sugar.wait_for_price(timeout=0.1)
except TimeoutError:
    # Падает даже при рабочем соединении
    pass
```

**Решение:** используйте разумный таймаут (5-10 секунд)
```python
# Даём достаточно времени для сети и терминала
price = await sugar.wait_for_price(timeout=10.0)
```

**Ошибка 2: Использование при закрытом рынке**
```python
# Рынок закрыт, таймаут будет всегда
try:
    price = await sugar.wait_for_price("EURUSD", timeout=5.0)
except TimeoutError:
    # Ожидаемо в выходные/праздники
    pass
```

**Решение:** сначала проверьте часы работы рынка или корректно обработайте таймаут
```python
try:
    price = await sugar.wait_for_price(timeout=5.0)
except TimeoutError:
    print("Market may be closed or symbol unavailable")
```

**Ошибка 3: Необработанный TimeoutError**
```python
# ОШИБКА: необработанное исключение завершает программу
price = await sugar.wait_for_price(timeout=3.0)  # Может вызвать исключение!
```

**Решение:** всегда оборачивайте в try-except
```python
try:
    price = await sugar.wait_for_price(timeout=3.0)
except TimeoutError as e:
    # Корректно обрабатываем таймаут
    logger.error(f"Price timeout: {e}")
```

---

## Советы профи

**Совет 1: Проверяйте подключение после connect**
```python
await sugar.quick_connect("YourBroker-Demo")

# Убеждаемся, что соединение полностью работает
try:
    await sugar.wait_for_price(timeout=10.0)
    print("Connection ready")
except TimeoutError:
    print("Connection established but no market data")
```

**Совет 2: Используйте для определения часов работы рынка**
```python
# Быстрая проверка доступности рынка
try:
    await sugar.wait_for_price(timeout=2.0)
    market_open = True
except TimeoutError:
    market_open = False

print(f"Market {'open' if market_open else 'closed'}")
```

**Совет 3: Сочетайте с выбором символа**
```python
# Убеждаемся, что символ выбран и есть котировки
symbol = "EURUSD"
await sugar._service.symbol_select(symbol, True)

# Ждём цену, чтобы подтвердить, что выбор сработал
try:
    price = await sugar.wait_for_price(symbol, timeout=5.0)
    print(f"{symbol} selected and receiving quotes")
except TimeoutError:
    print(f"{symbol} selection failed or no quotes")
```

---

## 📚 См. также

- [get_price_info](get_price_info.md) - Получение цены без таймаута
- [get_bid](get_bid.md) - Получение только цены BID
- [get_ask](get_ask.md) - Получение только цены ASK
- [get_spread](get_spread.md) - Получение только спреда
