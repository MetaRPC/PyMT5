# Подсчёт открытых позиций (`count_open_positions`)

> **Sugar-метод:** Возвращает количество открытых позиций (опционально с фильтром по символу).

**Информация об API:**

* **Метод:** `sugar.count_open_positions(symbol: Optional[str] = None)`
* **Возвращает:** Количество позиций как целое число
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def count_open_positions(self, symbol: Optional[str] = None) -> int
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | Нет | `None` | Фильтр по символу (None = подсчитать все) |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `int` | Количество открытых позиций (0, если их нет) |

---

## 🏛️ Основное

**Что делает:**

- Подсчитывает открытые позиции
- Опционально фильтрует по символу
- Возвращает целочисленное количество
- Возвращает 0, если позиций нет

**Ключевое поведение:**

- Без символа: подсчитывает ВСЕ позиции
- С символом: подсчитывает только этот символ
- Сопоставление символа чувствительно к регистру
- Всегда возвращает целое число (никогда None)

---

## ⚡ Под капотом

```
MT5Sugar.count_open_positions()
    ↓ вызывает
MT5Service.get_opened_orders(sort_mode=0)
    ↓ подсчитывает len(position_infos)
    ↓ или sum(1 for pos if pos.symbol == symbol)
    ↓ возвращает количество
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_opened_orders()
2. Если символа нет: возвращает len(position_infos)
3. Если символ указан: подсчитывает подходящие позиции
4. Возвращает целочисленное количество

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1368`
- Service: `src/pymt5/mt5_service.py:742`

---

## Когда использовать

**Используйте `count_open_positions()`, когда:**

- Нужно количество позиций
- Ограничиваете максимальное число позиций
- Отслеживаете количество позиций
- Статистика и отчётность

**Не используйте, когда:**

- Проверяете только наличие (используйте `has_open_position()`)
- Нужны детали позиции (используйте `get_open_positions()`)
- Нужна конкретная позиция (используйте `get_position_by_ticket()`)

---

## 🔗 Примеры

### Пример 1: Базовый подсчёт позиций

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def check_count():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Подсчитать все позиции
    total = await sugar.count_open_positions()
    print(f"Total open positions: {total}")

    # Подсчитать по символу
    eurusd_count = await sugar.count_open_positions("EURUSD")
    gbpusd_count = await sugar.count_open_positions("GBPUSD")

    print(f"EURUSD: {eurusd_count}")
    print(f"GBPUSD: {gbpusd_count}")
```

### Пример 2: Ограничение максимального числа позиций

```python
async def limit_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    max_positions = 5

    # Проверить перед открытием
    current_count = await sugar.count_open_positions()

    if current_count < max_positions:
        ticket = await sugar.buy_market(volume=0.1)
        print(f"Opened position #{ticket} ({current_count + 1}/{max_positions})")
    else:
        print(f"Maximum positions reached ({max_positions})")
```

### Пример 3: Лимиты по конкретному символу

```python
async def symbol_limits():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    max_per_symbol = 3

    # Подсчитать позиции по EURUSD
    eurusd_count = await sugar.count_open_positions(symbol)

    if eurusd_count < max_per_symbol:
        ticket = await sugar.buy_market(symbol, volume=0.1)
        print(f"Opened {symbol} position ({eurusd_count + 1}/{max_per_symbol})")
    else:
        print(f"Max {symbol} positions reached")
```

---

## Типичные ошибки

**Ошибка 1: Чувствительность символа к регистру**
```python
# ОШИБКА: регистр символа имеет значение
count = await sugar.count_open_positions("eurusd")
# Возвращает 0, если позиции по "EURUSD"
```

**Решение:** Используйте символы в верхнем регистре
```python
count = await sugar.count_open_positions("EURUSD")
```

**Ошибка 2: Ожидание None вместо 0**
```python
# count_open_positions возвращает 0, а не None
count = await sugar.count_open_positions()

if count:  # Это работает (0 — ложное значение)
    print("Have positions")
```

**Решение:** Сравнивайте явно или используйте истинность
```python
# Оба варианта работают
if count > 0:
    print("Have positions")

if count:
    print("Have positions")
```

**Ошибка 3: Отсутствие кэширования количества**
```python
# Неэффективно: повторный подсчёт в цикле
for _ in range(100):
    if await sugar.count_open_positions() < 5:
        # Получает все позиции на каждой итерации
        pass
```

**Решение:** Кэшируйте количество, если проверяете несколько раз
```python
count = await sugar.count_open_positions()

for _ in range(100):
    if count < 5:
        # Использовать кэшированное значение
        pass
```

---

## Полезные советы

**Совет 1: Проверка доступной ёмкости для позиций**

```python
async def get_remaining_capacity(sugar, max_positions=10):
    """Получить, сколько ещё позиций можно открыть."""
    current = await sugar.count_open_positions()
    remaining = max(0, max_positions - current)
    return remaining

# Использование
remaining = await get_remaining_capacity(sugar)
print(f"Can open {remaining} more positions")
```

**Совет 2: Анализ распределения по символам**
```python
# Анализ распределения позиций по символам
all_positions = await sugar.get_open_positions()
symbols = set(p.symbol for p in all_positions)

for symbol in symbols:
    count = await sugar.count_open_positions(symbol)
    print(f"{symbol}: {count} positions")
```

**Совет 3: Ожидание, пока количество достигнет цели**
```python
import asyncio

async def wait_for_fills(sugar, expected_count):
    """Ждать, пока количество позиций достигнет ожидаемого."""
    while True:
        current = await sugar.count_open_positions()

        if current >= expected_count:
            print(f"Reached {current} positions")
            break

        print(f"Waiting... {current}/{expected_count}")
        await asyncio.sleep(2)
```

---

## 📚 См. также

- [has_open_position](has_open_position.md) - Проверить наличие позиций
- [get_open_positions](get_open_positions.md) - Получить все позиции
- [get_positions_by_symbol](get_positions_by_symbol.md) - Получить позиции по символу
- [close_all_positions](../6.%20Position_Management/close_all_positions.md) - Закрыть все
