# Закрытие всех позиций (`close_all_positions`)

> **Sugar-метод:** Закрывает все открытые позиции, при необходимости с фильтром по символу.

**Информация об API:**

* **Метод:** `sugar.close_all_positions(symbol: Optional[str] = None)`
* **Возвращает:** количество закрытых позиций (`int`)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def close_all_positions(self, symbol: Optional[str] = None) -> int
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `Optional[str]` | Нет | `None` | Если указан, закрывает только позиции по этому символу |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `int` | Количество успешно закрытых позиций |

---

## 🏛️ Основное

**Что делает:**

- Получает все открытые позиции из терминала
- Закрывает каждую позицию по очереди
- При необходимости фильтрует по символу
- Продолжает закрытие, даже если некоторые не удаются

**Ключевое поведение:**

- Возвращает число успешно закрытых позиций
- Фильтрует по символу, если он указан
- Продолжает при отдельных неудачах (ошибка логируется)
- Безопасен для пустого списка позиций (возвращает 0)

---

## ⚡ Под капотом

```
MT5Sugar.close_all_positions()
    ↓ fetches all positions
MT5Service.get_opened_orders()
    ↓ iterates and closes each
MT5Sugar.close_position() (for each)
    ↓ calls
MT5Service.close_order()
    ↓ gRPC protobuf
TradingHelperService.OrderClose()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_opened_orders() для получения всех позиций
2. Sugar перебирает список position_infos
3. Если задан фильтр по символу, пропускает позиции, не совпадающие с символом
4. Для каждой позиции внутренне вызывает close_position()
5. Считает успешные закрытия (где close_position вернул True)
6. Продолжает, даже если отдельные закрытия не удались (логирует ошибку)
7. Возвращает общее число успешных закрытий

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1165`
- Service: `src/pymt5/mt5_service.py:742`
- Internal close: `src/pymt5/mt5_sugar.py:1141`

---

## Когда использовать

**Используйте `close_all_positions()`, когда:**

- Очистка в конце торгового дня/сессии
- Экстренный выход из всех позиций
- Сброс или перезапуск стратегии
- Управление риском на уровне всего счёта

**Не используйте, когда:**

- Нужно закрыть конкретную позицию (используйте `close_position()`)
- Нужны частичные закрытия (используйте `close_position_partial()`)
- Хотите оставить некоторые позиции открытыми

---

## 🔗 Примеры

### Пример 1: Закрытие всех позиций (без фильтра)

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def close_everything():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть несколько позиций
    ticket1 = await sugar.buy_market("EURUSD", volume=0.1)
    ticket2 = await sugar.sell_market("GBPUSD", volume=0.1)
    ticket3 = await sugar.buy_market("USDJPY", volume=0.1)

    print(f"Opened positions: #{ticket1}, #{ticket2}, #{ticket3}")

    # Закрыть все позиции
    closed_count = await sugar.close_all_positions()

    print(f"Closed {closed_count} positions")

# Вывод:
# Opened positions: #123456, #123457, #123458
# Closed 3 positions
```

### Пример 2: Закрытие позиций по конкретному символу

```python
async def close_symbol_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позиции по разным символам
    await sugar.buy_market("EURUSD", volume=0.1)
    await sugar.buy_market("EURUSD", volume=0.1)
    await sugar.sell_market("GBPUSD", volume=0.1)

    # Закрыть только позиции EURUSD
    eurusd_closed = await sugar.close_all_positions(symbol="EURUSD")

    print(f"Closed {eurusd_closed} EURUSD positions")
    print("GBPUSD position still open")

# Вывод:
# Closed 2 EURUSD positions
# GBPUSD position still open
```

### Пример 3: Очистка в конце дня

```python
import asyncio
from datetime import datetime, time

async def end_of_day_close():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Торговая логика в течение дня...
    # (открытие позиций, мониторинг и т.д.)

    # В 17:00 закрыть все позиции
    while True:
        now = datetime.now().time()
        close_time = time(17, 0)  # 17:00

        if now >= close_time:
            print("End of day - closing all positions")

            closed_count = await sugar.close_all_positions()
            print(f"Closed {closed_count} positions")

            # Показать итоговый баланс
            balance = await sugar.get_balance()
            print(f"Final balance: ${balance}")

            break

        await asyncio.sleep(60)  # Проверять каждую минуту
```

---

## Частые ошибки

**Ошибка 1: Ожидание, что все позиции закроются**
```python
# Некоторые позиции могут не закрыться
closed = await sugar.close_all_positions()

# Если было 5 позиций, closed может быть 4 или 3
# (некоторые могут не закрыться из-за состояния рынка и т.д.)
```

**Решение:** проверяйте возвращаемое значение и перепроверяйте
```python
# Получить количество перед закрытием
positions_data = await sugar._service.get_opened_orders()
initial_count = len(positions_data.position_infos)

# Закрыть все
closed_count = await sugar.close_all_positions()

if closed_count < initial_count:
    print(f"Warning: Only {closed_count}/{initial_count} closed")
    # Повторить или разобраться
```

**Ошибка 2: Закрытие позиций при наличии отложенных ордеров**
```python
# close_all_positions() закрывает только ПОЗИЦИИ, а не ОТЛОЖЕННЫЕ ОРДЕРА
await sugar.buy_limit(price=1.0840)  # Отложенный ордер
await sugar.buy_market()              # Открытая позиция

closed = await sugar.close_all_positions()  # Закрывает только позицию
# Отложенный ордер всё ещё активен!
```

**Решение:** отменяйте отложенные ордера отдельно
```python
# Закрыть позиции
await sugar.close_all_positions()

# Примечание: close_all_positions() закрывает только открытые позиции; отложенные ордера
# не затрагиваются и должны отменяться через слой service/account.
```

**Ошибка 3: Не обрабатываются частичные неудачи**
```python
# Если 1 из 5 не удастся, вы можете не заметить
closed = await sugar.close_all_positions()
# Молча продолжает, возвращает 4 вместо 5
```

**Решение:** логируйте и проверяйте
```python
positions_before = await sugar._service.get_opened_orders()
initial = len(positions_before.position_infos)

closed = await sugar.close_all_positions()

if closed < initial:
    print(f"Failed to close {initial - closed} positions")

    # Проверить, какие позиции остались
    positions_after = await sugar._service.get_opened_orders()
    for pos in positions_after.position_infos:
        print(f"Position #{pos.ticket} still open")
```

---

## Советы профи

**Совет 1: Узнайте общую прибыль перед закрытием**
```python
# Проверить общую прибыль/убыток перед закрытием всех
total_profit = await sugar.get_floating_profit()

print(f"Total P&L: ${total_profit:.2f}")

# Закрыть все позиции
closed = await sugar.close_all_positions()

print(f"Closed {closed} positions with ${total_profit:.2f} P&L")
```

**Совет 2: Закрывайте по символу последовательно**
```python
# Закрывать позиции символ за символом для лучшего контроля
symbols = ["EURUSD", "GBPUSD", "USDJPY"]

total_closed = 0
for symbol in symbols:
    count = await sugar.close_all_positions(symbol=symbol)
    print(f"{symbol}: closed {count} positions")
    total_closed += count

print(f"Total closed: {total_closed}")
```

**Совет 3: Повтор при частичной неудаче**
```python
# Повтор закрытия оставшихся позиций
max_retries = 3

for attempt in range(max_retries):
    positions_data = await sugar._service.get_opened_orders()
    remaining = len(positions_data.position_infos)

    if remaining == 0:
        print("All positions closed")
        break

    print(f"Attempt {attempt + 1}: Closing {remaining} positions")
    closed = await sugar.close_all_positions()

    if closed == remaining:
        print("All positions closed")
        break

    await asyncio.sleep(2)  # Подождать перед повтором
```

---

## 📚 См. также

- [close_position](close_position.md) - Закрытие конкретной позиции по тикету
- [close_position_partial](close_position_partial.md) - Частичное закрытие позиции
- [get_floating_profit](../2.%20Account_Properties/get_floating_profit.md) - Получение общей нереализованной прибыли
