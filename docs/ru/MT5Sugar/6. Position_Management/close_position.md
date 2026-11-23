# Полное закрытие позиции (`close_position`)

> **Sugar-метод:** Закрывает открытую позицию по номеру тикета за один вызов.

**Информация об API:**

* **Метод:** `sugar.close_position(ticket: int)`
* **Возвращает:** `True` при успешном закрытии, иначе `False`
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def close_position(self, ticket: int) -> bool
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Да | - | Номер тикета позиции для закрытия |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `bool` | `True`, если позиция закрыта (return_code == 10009), иначе `False` |

---

## 🏛️ Основное

**Что делает:**

- Закрывает всю позицию по номеру тикета
- Автоматически создаёт противоположный рыночный ордер (BUY→SELL, SELL→BUY)
- Возвращает булев статус успеха
- Проверяет код возврата из терминала

**Ключевое поведение:**

- Позиции BUY закрываются ордером SELL по цене BID
- Позиции SELL закрываются ордером BUY по цене ASK
- Возвращает False, если закрытие не удалось (без исключения)
- При успехе позиция удаляется из терминала

---

## ⚡ Под капотом

```
MT5Sugar.close_position()
    ↓ builds OrderCloseRequest
MT5Service.close_order()
    ↓ calls
MT5Account.order_close()
    ↓ gRPC protobuf
TradingHelperService.OrderClose()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar создаёт OrderCloseRequest с тикетом
2. Sugar вызывает Service.close_order()
3. Service передаёт в Account.order_close()
4. Account отправляет gRPC-запрос в терминал
5. Терминал создаёт противоположный рыночный ордер для закрытия позиции
6. Sugar проверяет return_code == 10009 (TRADE_RETCODE_DONE)
7. Возвращает True при успехе, False при неудаче

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1141`
- Service: `src/pymt5/mt5_service.py:996`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1803`

---

## Когда использовать

**Используйте `close_position()`, когда:**

- Нужно полностью выйти из позиции
- Фиксируете прибыль или вручную ограничиваете убытки
- Экстренное закрытие позиции
- Очистка в конце торговой сессии

**Не используйте, когда:**

- Нужно частичное закрытие (используйте `close_position_partial()`)
- Нужно закрыть все позиции (используйте `close_all_positions()`)
- Позиция уже закрыта

---

## 🔗 Примеры

### Пример 1: Базовое закрытие позиции

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def simple_close():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию
    ticket = await sugar.buy_market(volume=0.1)
    print(f"Position opened: #{ticket}")

    # Закрыть позицию
    success = await sugar.close_position(ticket)

    if success:
        print(f"Position #{ticket} closed successfully")
    else:
        print(f"Failed to close position #{ticket}")
```

### Пример 2: Закрытие с проверкой прибыли

```python
async def close_with_profit_check():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию
    ticket = await sugar.buy_market(volume=0.1)

    # Мониторинг прибыли
    while True:
        profit = await sugar.get_floating_profit()
        print(f"Current profit: ${profit:.2f}")

        # Закрыть, если прибыль >= $50 или убыток >= $20
        if profit >= 50 or profit <= -20:
            success = await sugar.close_position(ticket)

            if success:
                print(f"Position closed at ${profit:.2f}")
                break
            else:
                print("Close failed, retrying...")

        await asyncio.sleep(5)
```

### Пример 3: Закрытие нескольких позиций

```python
async def close_multiple():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть несколько позиций
    tickets = []
    for i in range(3):
        ticket = await sugar.buy_market(volume=0.01)
        tickets.append(ticket)
        print(f"Position {i+1}: #{ticket}")

    # Закрыть каждую позицию
    for ticket in tickets:
        success = await sugar.close_position(ticket)

        if success:
            print(f"Closed #{ticket}")
        else:
            print(f"Failed #{ticket}")
```

---

## Частые ошибки

**Ошибка 1: Не проверяется возвращаемое значение**
```python
# ПЛОХО: Предполагаем, что закрытие всегда успешно
await sugar.close_position(ticket)
# Позиция может остаться открытой, если закрытие не удалось!
```

**Решение:** всегда проверяйте возвращаемое значение
```python
success = await sugar.close_position(ticket)

if not success:
    print(f"Position {ticket} failed to close")
    # Обработать неудачу (повтор, оповещение и т.д.)
```

**Ошибка 2: Попытка закрыть уже закрытую позицию**
```python
# Закрыть позицию
await sugar.close_position(ticket)

# ОШИБКА: Попытка закрыть снова
await sugar.close_position(ticket)  # Возвращает False
```

**Решение:** отслеживайте закрытые позиции
```python
success = await sugar.close_position(ticket)

if success:
    closed_tickets.add(ticket)

# Позже: проверить перед закрытием
if ticket not in closed_tickets:
    await sugar.close_position(ticket)
```

**Ошибка 3: Игнорирование состояния рынка**
```python
# Рынок закрыт в выходные
success = await sugar.close_position(ticket)  # Возвращает False
```

**Решение:** проверяйте часы работы рынка или обрабатывайте корректно
```python
success = await sugar.close_position(ticket)

if not success:
    # Может быть закрыт рынок, проблема с соединением и т.д.
    print("Close failed - check market status")
```

---

## Советы профи

**Совет 1: Используйте try-except для надёжности**
```python
try:
    success = await sugar.close_position(ticket)

    if success:
        print("Position closed")
    else:
        print("Close returned False")

except Exception as e:
    print(f"Exception during close: {e}")
```

**Совет 2: Сочетайте с проверкой прибыли позиции**
```python
# Получить итоговую прибыль перед закрытием
profit = await sugar.get_floating_profit()

success = await sugar.close_position(ticket)

if success:
    print(f"Closed with profit: ${profit:.2f}")
```

**Совет 3: Закрывайте позиции по magic number**
```python
# Получить все позиции
positions_data = await sugar._service.get_opened_orders()

# Закрыть только позиции с конкретным magic
magic_to_close = 12345

for pos in positions_data.position_infos:
    if pos.magic_number == magic_to_close:
        success = await sugar.close_position(pos.ticket)
        print(f"Closed magic {magic_to_close}: #{pos.ticket}")
```

---

## 📚 См. также

- [close_all_positions](close_all_positions.md) - Закрытие всех открытых позиций
- [close_position_partial](close_position_partial.md) - Частичное закрытие позиции
- [buy_market](../4.%20Simple_Trading/buy_market.md) - Открытие позиции BUY
- [sell_market](../4.%20Simple_Trading/sell_market.md) - Открытие позиции SELL
