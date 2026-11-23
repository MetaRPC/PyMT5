# Получение полной информации о цене (`get_price_info`)

> **Sugar-метод:** Возвращает полные данные о цене (BID, ASK, спред, временная метка) за один вызов.

**Информация об API:**

* **Метод:** `sugar.get_price_info(symbol: Optional[str] = None)`
* **Возвращает:** dataclass `PriceInfo` с полями bid, ask, spread, time, symbol
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_price_info(
    self,
    symbol: Optional[str] = None
) -> PriceInfo
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | Нет | `None` | Имя символа (использует значение по умолчанию, если не указано) |

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

- Получает полные данные тика из терминала MT5
- Автоматически вычисляет спред
- Возвращает структурированный dataclass PriceInfo
- Использует символ по умолчанию, если не указан

**Ключевое поведение:**

- Вызывает `ValueError`, если символ не указан и не задан по умолчанию
- Возвращает рыночные данные в реальном времени
- Спред вычисляется (не берётся из поля спреда терминала)

---

## ⚡ Под капотом

```
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

1. Sugar проверяет символ (использует значение по умолчанию или вызывает ошибку)
2. Service получает тик через слой Account
3. Account отправляет gRPC-запрос в терминал
4. Sugar оборачивает результат в dataclass PriceInfo с вычисленным спредом

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:530`
- Service: `src/pymt5/mt5_service.py:1145`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1850`

---

## Когда использовать

**Используйте `get_price_info()`, когда:**

- Нужен полный снимок цены с временной меткой
- Строите системы мониторинга цен
- Нужно логировать данные о цене с точным временем
- Хотите структурированные данные вместо отдельных вызовов

**Не используйте, когда:**

- Нужна только цена BID или ASK (используйте `get_bid()` или `get_ask()`)
- Нужен только спред (используйте `get_spread()`)
- Нужны потоковые обновления (используйте стриминг прибыли позиции)

---

## 🔗 Примеры

### Пример 1: Базовая информация о цене

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def check_current_price():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Получаем полную информацию о цене
    price = await sugar.get_price_info()

    print(f"Symbol: {price.symbol}")
    print(f"BID: {price.bid}")
    print(f"ASK: {price.ask}")
    print(f"Spread: {price.spread}")
    print(f"Time: {price.time}")

    await sugar.disconnect()

# Вывод:
# Symbol: EURUSD
# BID: 1.08432
# ASK: 1.08445
# Spread: 0.00013
# Time: 2026-02-03 14:23:15
```

### Пример 2: Цена для конкретного символа

```python
async def compare_symbols():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("YourBroker-Demo")

    # Получаем цены по нескольким символам
    eurusd = await sugar.get_price_info("EURUSD")
    gbpusd = await sugar.get_price_info("GBPUSD")

    print(f"EURUSD spread: {eurusd.spread:.5f}")
    print(f"GBPUSD spread: {gbpusd.spread:.5f}")

    await sugar.disconnect()
```

### Пример 3: Система логирования цен

```python
import asyncio
from datetime import datetime

async def log_prices():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Логируем цены каждые 5 секунд
    for _ in range(10):
        price = await sugar.get_price_info()

        log_entry = (
            f"{price.time} | "
            f"BID: {price.bid} | "
            f"ASK: {price.ask} | "
            f"Spread: {price.spread:.5f}"
        )
        print(log_entry)

        await asyncio.sleep(5)

    await sugar.disconnect()
```

---

## Частые ошибки

**Ошибка 1: Не задан символ по умолчанию**
```python
# ОШИБКА: символ не указан
account = MT5Account.create(
    user=123,
    password="pass",
    grpc_server="server",
)
service = MT5Service(account)
sugar = MT5Sugar(service)

await sugar.quick_connect("YourBroker-Demo")
price = await sugar.get_price_info()  # Вызывает ValueError
```

**Решение:** всегда указывайте символ или задавайте значение по умолчанию
```python
# Вариант 1: задать символ по умолчанию
sugar = MT5Sugar(..., default_symbol="EURUSD")
price = await sugar.get_price_info()

# Вариант 2: передать явно
price = await sugar.get_price_info("EURUSD")
```

**Ошибка 2: Использование устаревших данных о цене**
```python
# Цена — это снимок, не обновляется в реальном времени
price = await sugar.get_price_info()
await asyncio.sleep(60)
print(price.bid)  # Показывает старую цену 60-секундной давности
```

**Решение:** всегда получайте свежие данные перед использованием
```python
# Получаем новый снимок, когда нужно
price = await sugar.get_price_info()
print(price.bid)  # Текущая цена
```

---

## Советы профи

**Совет 1: Структурированные данные для удобного доступа**

```python
price = await sugar.get_price_info()

# Удобный доступ ко всем полям
mid_price = (price.bid + price.ask) / 2
spread_pct = (price.spread / price.bid) * 100
age = datetime.now() - price.time
```

**Совет 2: Используйте для проверки цены**

```python
price = await sugar.get_price_info()

# Проверяем, не слишком ли широкий спред
if price.spread > 0.0005:  # 5 пунктов для EURUSD
    print(f"Warning: Wide spread detected ({price.spread})")
```

**Совет 3: Сочетайте с информацией о символе**

```python
# Получаем цену и считаем в валюте счёта
price = await sugar.get_price_info("EURUSD")
symbol_info = await sugar._service.get_symbol_info("EURUSD")

# Используем цену с количеством знаков символа для правильного форматирования
formatted_bid = f"{price.bid:.{symbol_info.digits}f}"
```

---

## 📚 См. также

- [get_bid](get_bid.md) - Получение только цены BID
- [get_ask](get_ask.md) - Получение только цены ASK
- [get_spread](get_spread.md) - Получение только спреда
- [wait_for_price](wait_for_price.md) - Ожидание обновления цены с таймаутом
