# Проверить наличие позиций (`has_open_position`)

> **Sugar-метод:** Быстрая проверка наличия открытых позиций (опционально с фильтром по символу).

**Информация об API:**

* **Метод:** `sugar.has_open_position(symbol: Optional[str] = None)`
* **Возвращает:** `True`, если позиции есть, иначе `False`
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def has_open_position(self, symbol: Optional[str] = None) -> bool
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | Нет | `None` | Фильтр по символу (None = проверить любой символ) |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `bool` | `True`, если позиции есть (по фильтру), иначе `False` |

---

## 🏛️ Основное

**Что делает:**

- Проверяет наличие любых открытых позиций
- Опционально фильтрует по символу
- Возвращает булево значение (True/False)
- Эффективная проверка без получения полных деталей

**Ключевое поведение:**

- Без символа: проверяет ЛЮБУЮ открытую позицию
- С символом: проверяет позиции только по этому символу
- Сопоставление символа чувствительно к регистру
- Возвращает False, если позиций нет

---

## ⚡ Под капотом

```
MT5Sugar.has_open_position()
    ↓ вызывает
MT5Service.get_opened_orders(sort_mode=0)
    ↓ проверяет len(position_infos) > 0
    ↓ или any(pos.symbol == symbol)
    ↓ возвращает булево значение
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_opened_orders()
2. Если символа нет: проверяет, что длина position_infos > 0
3. Если символ указан: проверяет, соответствует ли символу какая-либо позиция
4. Возвращает True при наличии, иначе False

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1359`
- Service: `src/pymt5/mt5_service.py:742`

---

## Когда использовать

**Используйте `has_open_position()`, когда:**

- Быстрая проверка наличия перед операциями
- Проверка отсутствия позиций перед действием
- Условная логика на основе позиций
- Предварительные проверки

**Не используйте, когда:**

- Нужно количество позиций (используйте `count_open_positions()`)
- Нужны детали позиций (используйте `get_open_positions()`)
- Нужна конкретная позиция (используйте `get_position_by_ticket()`)

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

    # Открыть только при отсутствии позиций
    if not await sugar.has_open_position():
        ticket = await sugar.buy_market(volume=0.1)
        print(f"Opened position #{ticket}")
    else:
        print("Already have open positions, skipping")
```

### Пример 2: Проверка по конкретному символу

```python
async def symbol_check():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Проверить конкретный символ
    has_eurusd = await sugar.has_open_position("EURUSD")
    has_gbpusd = await sugar.has_open_position("GBPUSD")

    print(f"EURUSD positions: {'Yes' if has_eurusd else 'No'}")
    print(f"GBPUSD positions: {'Yes' if has_gbpusd else 'No'}")

    # Открыть, только если нет EURUSD
    if not has_eurusd:
        await sugar.buy_market("EURUSD", volume=0.1)
```

### Пример 3: Ожидание, пока всё закроется

```python
import asyncio

async def wait_until_flat():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Закрыть все позиции
    await sugar.close_all_positions()

    print("Waiting for all positions to close...")

    # Ждать, пока не останется позиций
    while await sugar.has_open_position():
        print("Still have open positions...")
        await asyncio.sleep(2)

    print("All positions closed")
```

---

## Типичные ошибки

**Ошибка 1: Чувствительность символа к регистру**
```python
# ОШИБКА: регистр символа имеет значение
has_pos = await sugar.has_open_position("eurusd")
# Возвращает False, если позиции по "EURUSD"
```

**Решение:** Используйте символы в верхнем регистре
```python
has_pos = await sugar.has_open_position("EURUSD")
```

**Ошибка 2: Путаница с количеством**
```python
# has_open_position возвращает bool, а не количество
if await sugar.has_open_position():
    # Неизвестно, СКОЛЬКО позиций
    pass
```

**Решение:** Используйте count, если нужно число
```python
count = await sugar.count_open_positions()
print(f"Have {count} positions")
```

**Ошибка 3: Отсутствие await (асинхронный метод)**
```python
# ОШИБКА: забыт await
if sugar.has_open_position():  # Отсутствует await
    pass
```

**Решение:** Всегда используйте await с асинхронными методами
```python
if await sugar.has_open_position():
    pass
```

---

## Полезные советы

**Совет 1: Шаблон быстрой предварительной проверки**
```python
# Распространённый шаблон: проверка перед действием
if await sugar.has_open_position("EURUSD"):
    print("Already trading EURUSD")
else:
    # Безопасно открыть новую позицию
    await sugar.buy_market("EURUSD", volume=0.1)
```

**Совет 2: Проверка нескольких символов**
```python
# Эффективно проверить несколько символов
symbols = ["EURUSD", "GBPUSD", "USDJPY"]

for symbol in symbols:
    if await sugar.has_open_position(symbol):
        print(f"{symbol}: trading")
    else:
        print(f"{symbol}: flat")
```

**Совет 3: Использование как утверждения (assert)**
```python
# Убедиться в отсутствии позиций перед тестом
assert not await sugar.has_open_position(), "Must start with no positions"

# Выполнить логику теста
ticket = await sugar.buy_market(volume=0.01)

# Проверить, что позиция открыта
assert await sugar.has_open_position(), "Position should be open"
```

---

## 📚 См. также

- [count_open_positions](count_open_positions.md) - Получить количество позиций
- [get_open_positions](get_open_positions.md) - Получить все позиции
- [get_positions_by_symbol](get_positions_by_symbol.md) - Получить позиции по символу
- [close_all_positions](../6.%20Position_Management/close_all_positions.md) - Закрыть все
