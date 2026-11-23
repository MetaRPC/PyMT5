# Изменение только стоп-лосса позиции (`modify_position_sl`)

> **Sugar-метод:** Удобный метод для изменения только стоп-лосса позиции.

**Информация об API:**

* **Метод:** `sugar.modify_position_sl(ticket, sl)`
* **Возвращает:** `True` при успешном изменении, иначе `False`
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def modify_position_sl(self, ticket: int, sl: float) -> bool
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Да | - | Номер тикета позиции |
| `sl` | `float` | Да | - | Новая цена стоп-лосса |

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

- Изменяет только цену стоп-лосса
- Оставляет тейк-профит без изменений
- Удобная обёртка над `modify_position_sltp()`
- Более чистый синтаксис для изменений только SL

**Ключевое поведение:**

- Тейк-профит остаётся без изменений
- Должен соблюдаться минимальный уровень стопа брокера
- SL должен быть корректным для направления позиции
- Внутри вызывает `modify_position_sltp(ticket, sl=sl, tp=None)`

---

## ⚡ Под капотом

```
MT5Sugar.modify_position_sl()
    ↓ calls
MT5Sugar.modify_position_sltp(ticket, sl=sl, tp=None)
    ↓ fetches position
MT5Service.get_opened_orders()
    ↓ builds OrderModifyRequest
MT5Service.modify_order()
    ↓ gRPC protobuf
TradingHelperService.OrderModify()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar вызывает modify_position_sltp() с параметром sl и tp=None
2. Полную цепочку см. в [modify_position_sltp](modify_position_sltp.md)
3. Значение тейк-профита сохраняется из текущей позиции

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1299`
- Internal call: `src/pymt5/mt5_sugar.py:1196`

---

## Когда использовать

**Используйте `modify_position_sl()`, когда:**

- Нужно изменить только стоп-лосс
- Реализуете трейлинг-стопы
- Переносите SL в безубыток
- Тейк-профит должен остаться без изменений

**Не используйте, когда:**

- Нужно изменить и SL, и TP (используйте `modify_position_sltp()`)
- Хотите изменить только TP (используйте `modify_position_tp()`)

---

## 🔗 Примеры

### Пример 1: Перенос SL в безубыток

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def breakeven_sl():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию по 1.0850
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=100
    )

    entry_price = await sugar.get_ask()  # 1.0850

    # Ждать прибыли 30 пунктов
    while True:
        current = await sugar.get_bid()

        if current >= entry_price + 0.0030:
            # Перенести SL в безубыток (TP остаётся на исходной цели)
            success = await sugar.modify_position_sl(ticket, sl=entry_price)

            if success:
                print(f"SL moved to breakeven: {entry_price}")
                break

        await asyncio.sleep(5)

```

### Пример 2: Ужесточение стоп-лосса

```python
async def tighten_sl():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть с SL 50 пунктов
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=100
    )

    entry = await sugar.get_ask()
    initial_sl = entry - 0.0050  # 50 пунктов

    print(f"Initial SL: {initial_sl}")

    # Через некоторое время ужесточить до 30 пунктов
    await asyncio.sleep(300)

    new_sl = entry - 0.0030  # 30 пунктов
    success = await sugar.modify_position_sl(ticket, sl=new_sl)

    if success:
        print(f"SL tightened to: {new_sl}")

```

### Пример 3: Простой трейлинг-стоп

```python
async def simple_trailing():
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

    entry = await sugar.get_ask()
    trail_distance = 0.0030  # 30 пунктов

    current_sl = entry - 0.0050  # Начальный SL
    await sugar.modify_position_sl(ticket, sl=current_sl)

    # Передвигать стоп
    highest = entry

    while True:
        price = await sugar.get_bid()

        if price > highest:
            highest = price
            new_sl = highest - trail_distance

            # Передвигать SL только вверх
            if new_sl > current_sl:
                success = await sugar.modify_position_sl(ticket, sl=new_sl)

                if success:
                    current_sl = new_sl
                    print(f"SL trailed to: {new_sl:.5f}")

        await asyncio.sleep(5)

```

---

## Частые ошибки

**Ошибка 1: Забывают, что TP остаётся без изменений**
```python
# Если у позиции был TP на 1.0950, он остаётся на 1.0950
await sugar.modify_position_sl(ticket, sl=1.0800)

# TP всё ещё 1.0950, не удалён
```

**Решение:** чтобы изменить и TP, используйте modify_position_sltp()
```python
# Изменить оба
await sugar.modify_position_sltp(ticket, sl=1.0800, tp=1.1000)
```

**Ошибка 2: Неверное направление SL**
```python
# Позиция BUY по 1.0850
ticket = await sugar.buy_market()

# ОШИБКА: SL выше цены входа
await sugar.modify_position_sl(ticket, sl=1.0900)  # Неверное направление
```

**Решение:** помните, BUY: SL ниже входа
```python
await sugar.modify_position_sl(ticket, sl=1.0800)  # Верно
```

**Ошибка 3: Не проверяется возвращаемое значение**
```python
# Изменение может не удаться (ограничения брокера и т.д.)
await sugar.modify_position_sl(ticket, sl=1.0800)
# SL мог не измениться, если не удалось
```

**Решение:** проверяйте возвращаемое значение
```python
success = await sugar.modify_position_sl(ticket, sl=1.0800)

if not success:
    print("SL modification failed")
```

---

## Советы профи

**Совет 1: Удаляйте SL, задав значение 0**
```python
# Удалить Стоп-лосс (оставить TP)
await sugar.modify_position_sl(ticket, sl=0.0)
```

**Совет 2: Пакетное изменение SL для всех позиций**
```python
# Перенести все позиции в безубыток
positions_data = await sugar._service.get_opened_orders()

for pos in positions_data.position_infos:
    if pos.profit > 0:
        # Перенести SL на цену входа
        await sugar.modify_position_sl(pos.ticket, sl=pos.price_open)
        print(f"Position #{pos.ticket} moved to breakeven")
```

**Совет 3: Постепенное ужесточение SL**
```python
# Постепенно ужесточать SL по мере движения цены
entry = 1.0850
stops = [1.0830, 1.0840, 1.0845, 1.0850]  # Постепенно жёстче

for new_sl in stops:
    # Ждать, пока цена оправдает более жёсткий SL
    while await sugar.get_bid() < new_sl + 0.0030:
        await asyncio.sleep(10)

    await sugar.modify_position_sl(ticket, sl=new_sl)
    print(f"SL tightened to {new_sl}")
```

---

## 📚 См. также

- [modify_position_tp](modify_position_tp.md) - Изменение только тейк-профита
- [modify_position_sltp](modify_position_sltp.md) - Изменение и SL, и TP
- [buy_market_with_sltp](../5.%20Trading_With_SLTP/buy_market_with_sltp.md) - Открытие с SL/TP
- [close_position](close_position.md) - Закрытие позиции
