# Изменение SL/TP позиции (`modify_position_sltp`)

> **Sugar-метод:** Изменяет стоп-лосс и/или тейк-профит открытой позиции.

**Информация об API:**

* **Метод:** `sugar.modify_position_sltp(ticket, sl, tp)`
* **Возвращает:** `True` при успешном изменении, иначе `False`
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def modify_position_sltp(
    self,
    ticket: int,
    sl: Optional[float] = None,
    tp: Optional[float] = None
) -> bool
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Да | - | Номер тикета позиции |
| `sl` | `Optional[float]` | Нет | `None` | Новая цена стоп-лосса (None — сохранить текущую) |
| `tp` | `Optional[float]` | Нет | `None` | Новая цена тейк-профита (None — сохранить текущую) |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `bool` | `True` при успешном изменении (return_code == 10009), иначе `False` |

**Вызывает:**
- `ValueError`, если позиция с заданным тикетом не найдена

---

## 🏛️ Основное

**Что делает:**

- Получает текущую позицию по тикету
- Изменяет стоп-лосс и/или тейк-профит
- Сохраняет неизменённые значения
- Проверяет изменение через терминал

**Ключевое поведение:**

- Передайте `None`, чтобы оставить текущий SL или TP без изменений
- Должен соблюдаться минимальный уровень стопа брокера
- SL/TP должны быть корректными для направления позиции
- Возвращает False, если изменение не удалось

---

## ⚡ Под капотом

```
MT5Sugar.modify_position_sltp()
    ↓ fetches position
MT5Service.get_opened_orders()
    ↓ finds position, preserves current SL/TP
    ↓ builds OrderModifyRequest
MT5Service.modify_order()
    ↓ calls
MT5Account.order_modify()
    ↓ gRPC protobuf
TradingHelperService.OrderModify()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar получает все позиции через Service.get_opened_orders()
2. Sugar ищет позицию с совпадающим тикетом
3. Если не найдена, вызывает ValueError
4. Sugar сохраняет текущие SL/TP, если новые значения равны None
5. Sugar создаёт OrderModifyRequest с тикетом и новыми SL/TP
6. Sugar вызывает Service.modify_order()
7. Service передаёт в Account.order_modify()
8. Возвращает True, если returned_code == 10009, иначе False

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1196`
- Service: `src/pymt5/mt5_service.py:963`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1758`

---

## Когда использовать

**Используйте `modify_position_sltp()`, когда:**

- Корректируете стоп-лосс после движения позиции в прибыль
- Устанавливаете тейк-профит после открытия позиции
- Реализуете стратегии трейлинг-стопа
- Корректируете управление риском

**Не используйте, когда:**

- Хотите изменить только SL (для ясности используйте `modify_position_sl()`)
- Хотите изменить только TP (для ясности используйте `modify_position_tp()`)
- Позиция уже закрыта

---

## 🔗 Примеры

### Пример 1: Добавление SL/TP к существующей позиции

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def add_stops():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию без SL/TP
    ticket = await sugar.buy_market(volume=0.1)
    print(f"Position opened: #{ticket}")

    # Добавить SL/TP после открытия
    success = await sugar.modify_position_sltp(
        ticket=ticket,
        sl=1.0800,  # Стоп-лосс на 1.0800
        tp=1.0950   # Тейк-профит на 1.0950
    )

    if success:
        print("SL/TP added successfully")
    else:
        print("Failed to add SL/TP")

```

### Пример 2: Перенос стоп-лосса в безубыток

```python
async def breakeven_stop():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию BUY по 1.0850
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,   # Начальный SL 50 пунктов
        tp_pips=100
    )

    entry_price = await sugar.get_ask()  # 1.0850

    # Мониторинг позиции
    while True:
        current_price = await sugar.get_bid()

        # Перенести SL в безубыток при прибыли 30 пунктов
        if current_price >= entry_price + 0.0030:
            success = await sugar.modify_position_sltp(
                ticket=ticket,
                sl=entry_price,  # Перенести SL на вход (безубыток)
                tp=None          # Оставить TP без изменений
            )

            if success:
                print("Stop Loss moved to breakeven")
                break

        await asyncio.sleep(5)

```

### Пример 3: Трейлинг-стоп

```python
async def trailing_stop():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию BUY
    ticket = await sugar.buy_market(volume=0.1)

    entry_price = await sugar.get_ask()
    trailing_distance = 0.0030  # 30 пунктов

    best_price = entry_price
    current_sl = entry_price - 0.0050  # Начальный SL 50 пунктов

    # Установить начальный SL
    await sugar.modify_position_sltp(ticket, sl=current_sl, tp=None)

    # Передвигать стоп
    while True:
        current_price = await sugar.get_bid()

        # Обновить лучшую цену
        if current_price > best_price:
            best_price = current_price

            # Рассчитать новый SL
            new_sl = best_price - trailing_distance

            # Передвигать SL только вверх, никогда вниз
            if new_sl > current_sl:
                success = await sugar.modify_position_sltp(
                    ticket=ticket,
                    sl=new_sl,
                    tp=None
                )

                if success:
                    current_sl = new_sl
                    print(f"SL trailed to {new_sl:.5f}")

        await asyncio.sleep(5)

```

---

## Частые ошибки

**Ошибка 1: Неверное направление SL/TP**
```python
# Позиция BUY открыта по 1.0850
ticket = await sugar.buy_market()

# ОШИБКА: SL выше входа, TP ниже входа (наоборот!)
await sugar.modify_position_sltp(
    ticket=ticket,
    sl=1.0900,  # НЕВЕРНО: SL выше входа
    tp=1.0800   # НЕВЕРНО: TP ниже входа
)
# Изменение, скорее всего, не удастся
```

**Решение:** помните, BUY: SL ниже, TP выше
```python
# Позиция BUY по 1.0850
await sugar.modify_position_sltp(
    ticket=ticket,
    sl=1.0800,  # Верно: SL ниже входа
    tp=1.0950   # Верно: TP выше входа
)
```

**Ошибка 2: Не обрабатывается случай, когда позиция не найдена**
```python
# Позиция уже закрыта или недействительный тикет
try:
    await sugar.modify_position_sltp(ticket=999999, sl=1.0800)
except ValueError as e:
    print(e)  # "Position 999999 not found"
```

**Решение:** сначала проверьте, существует ли позиция
```python
positions_data = await sugar._service.get_opened_orders()

position_exists = any(pos.ticket == ticket for pos in positions_data.position_infos)

if position_exists:
    await sugar.modify_position_sltp(ticket, sl=1.0800)
else:
    print(f"Position {ticket} not found")
```

**Ошибка 3: SL/TP слишком близко к текущей цене**
```python
# Брокер требует минимальный уровень стопа 10 пунктов
bid = await sugar.get_bid()  # 1.0850

# ОШИБКА: SL всего в 2 пунктах (минимум брокера — 10)
await sugar.modify_position_sltp(
    ticket=ticket,
    sl=bid - 0.0002  # Слишком близко!
)
# Возвращает False
```

**Решение:** соблюдайте минимальный уровень стопа брокера
```python
bid = await sugar.get_bid()

# Используйте хотя бы минимум брокера (например, 10 пунктов)
await sugar.modify_position_sltp(
    ticket=ticket,
    sl=bid - 0.0010  # в 10 пунктах
)
```

---

## Советы профи

**Совет 1: Изменяйте только то, что нужно**
```python
# Изменить только SL, оставить TP без изменений
await sugar.modify_position_sltp(ticket, sl=1.0800, tp=None)

# Изменить только TP, оставить SL без изменений
await sugar.modify_position_sltp(ticket, sl=None, tp=1.0950)

# Изменить оба
await sugar.modify_position_sltp(ticket, sl=1.0800, tp=1.0950)
```

**Совет 2: Удаляйте SL/TP, задав значение 0**
```python
# Удалить Стоп-лосс и Тейк-профит
await sugar.modify_position_sltp(ticket, sl=0.0, tp=0.0)
```

**Совет 3: Пакетное изменение нескольких позиций**
```python
# Изменить SL для всех позиций
positions_data = await sugar._service.get_opened_orders()

for pos in positions_data.position_infos:
    # Перенести SL в безубыток для всех прибыльных позиций
    if pos.profit > 0:
        await sugar.modify_position_sltp(
            ticket=pos.ticket,
            sl=pos.price_open,  # Цена входа
            tp=None
        )
        print(f"Position #{pos.ticket} moved to breakeven")
```

---

## 📚 См. также

- [modify_position_sl](modify_position_sl.md) - Изменение только стоп-лосса
- [modify_position_tp](modify_position_tp.md) - Изменение только тейк-профита
- [buy_market_with_sltp](../5.%20Trading_With_SLTP/buy_market_with_sltp.md) - Открытие с SL/TP
- [close_position](close_position.md) - Полное закрытие позиции
