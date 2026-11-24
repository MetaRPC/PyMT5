# Изменение только тейк-профита позиции (`modify_position_tp`)

> **Sugar-метод:** Удобный метод для изменения только тейк-профита позиции.

**Информация об API:**

* **Метод:** `sugar.modify_position_tp(ticket, tp)`
* **Возвращает:** `True` при успешном изменении, иначе `False`
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def modify_position_tp(self, ticket: int, tp: float) -> bool
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Да | - | Номер тикета позиции |
| `tp` | `float` | Да | - | Новая цена тейк-профита |

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

- Изменяет только цену тейк-профита
- Оставляет стоп-лосс без изменений
- Удобная обёртка над `modify_position_sltp()`
- Более чистый синтаксис для изменений только TP

**Ключевое поведение:**

- Стоп-лосс остаётся без изменений
- Должен соблюдаться минимальный уровень стопа брокера
- TP должен быть корректным для направления позиции
- Внутри вызывает `modify_position_sltp(ticket, sl=None, tp=tp)`

---

## ⚡ Под капотом

```
MT5Sugar.modify_position_tp()
    ↓ calls
MT5Sugar.modify_position_sltp(ticket, sl=None, tp=tp)
    ↓ fetches position
MT5Service.get_opened_orders()
    ↓ builds OrderModifyRequest
MT5Service.modify_order()
    ↓ gRPC protobuf
TradingHelperService.OrderModify()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar вызывает modify_position_sltp() с параметром tp и sl=None
2. Полную цепочку см. в [modify_position_sltp](modify_position_sltp.md)
3. Значение стоп-лосса сохраняется из текущей позиции

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1315`
- Internal call: `src/pymt5/mt5_sugar.py:1196`

---

## Когда использовать

**Используйте `modify_position_tp()`, когда:**

- Нужно изменить только тейк-профит
- Расширяете целевой уровень прибыли
- Добавляете TP к позиции без TP
- Стоп-лосс должен остаться без изменений

**Не используйте, когда:**

- Нужно изменить и SL, и TP (используйте `modify_position_sltp()`)
- Хотите изменить только SL (используйте `modify_position_sl()`)

---

## 🔗 Примеры

### Пример 1: Добавление TP к позиции

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def add_tp():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию без TP
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=None  # Сначала без TP
    )

    print(f"Position opened: #{ticket} with SL only")

    # Позже добавить Тейк-профит
    entry = 1.0850
    tp_price = entry + 0.0100  # TP 100 пунктов

    success = await sugar.modify_position_tp(ticket, tp=tp_price)

    if success:
        print(f"TP added at {tp_price}")

```

### Пример 2: Расширение целевого уровня прибыли

```python
async def extend_tp():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть с консервативным TP
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=50  # Консервативный 1:1 R/R
    )

    entry = await sugar.get_ask()
    initial_tp = entry + 0.0050

    print(f"Initial TP: {initial_tp} (50 pips)")

    # Если тренд продолжается, расширить TP
    await asyncio.sleep(300)

    current = await sugar.get_bid()
    if current > entry + 0.0030:
        # Расширить TP до 100 пунктов
        new_tp = entry + 0.0100

        success = await sugar.modify_position_tp(ticket, tp=new_tp)

        if success:
            print(f"TP extended to {new_tp} (100 pips)")

```

### Пример 3: Динамический TP на основе волатильности

```python
async def dynamic_tp():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию
    ticket = await sugar.buy_market_with_sltp(
        volume=0.1,
        sl_pips=50,
        tp_pips=None
    )

    entry = await sugar.get_ask()

    # Рассчитать TP на основе недавнего движения цены (упрощённо)
    # В реальном сценарии используйте ATR или другую меру волатильности
    spread = await sugar.get_spread()
    volatility_multiplier = 3

    # Установить TP в 3× текущего спреда
    tp_distance = spread * volatility_multiplier
    tp_price = entry + tp_distance

    success = await sugar.modify_position_tp(ticket, tp=tp_price)

    if success:
        print(f"Dynamic TP set at {tp_price}")
        print(f"TP distance: {tp_distance:.5f}")

```

---

## Частые ошибки

**Ошибка 1: Забывают, что SL остаётся без изменений**
```python
# Если у позиции был SL на 1.0800, он остаётся на 1.0800
await sugar.modify_position_tp(ticket, tp=1.0950)

# SL всё ещё 1.0800, не удалён
```

**Решение:** чтобы изменить и SL, используйте modify_position_sltp()
```python
# Изменить оба
await sugar.modify_position_sltp(ticket, sl=1.0800, tp=1.0950)
```

**Ошибка 2: Неверное направление TP**
```python
# Позиция BUY по 1.0850
ticket = await sugar.buy_market()

# ОШИБКА: TP ниже цены входа
await sugar.modify_position_tp(ticket, tp=1.0800)  # Неверное направление
```

**Решение:** помните, BUY: TP выше входа
```python
await sugar.modify_position_tp(ticket, tp=1.0950)  # Верно
```

**Ошибка 3: TP задан слишком близко**
```python
# Брокер требует минимальную дистанцию
bid = await sugar.get_bid()  # 1.0850

# ОШИБКА: TP всего в 2 пунктах (минимум брокера — 10)
await sugar.modify_position_tp(ticket, tp=bid + 0.0002)
# Возвращает False
```

**Решение:** соблюдайте минимальный уровень стопа брокера
```python
bid = await sugar.get_bid()

# Используйте хотя бы минимум брокера (например, 10 пунктов)
await sugar.modify_position_tp(ticket, tp=bid + 0.0010)
```

---

## Советы профи

**Совет 1: Удаляйте TP, задав значение 0**
```python
# Удалить Тейк-профит (оставить SL)
await sugar.modify_position_tp(ticket, tp=0.0)
```

**Совет 2: Масштабируйте TP в зависимости от размера позиции**
```python
# Бóльшие позиции = ближе TP (меньше риска)
positions_data = await sugar._service.get_opened_orders()

for pos in positions_data.position_infos:
    if pos.volume >= 0.5:
        # Крупная позиция: консервативный TP (50 пунктов)
        tp = pos.price_open + 0.0050
    else:
        # Небольшая позиция: агрессивный TP (100 пунктов)
        tp = pos.price_open + 0.0100

    # Для позиций BUY
    if pos.type == 0:  # BUY
        await sugar.modify_position_tp(pos.ticket, tp=tp)
```

**Совет 3: Постепенная корректировка TP**
```python
# Расширять TP по мере движения позиции в прибыль
entry = 1.0850
tps = [1.0900, 1.0950, 1.1000]  # Постепенные цели

for new_tp in tps:
    # Ждать, пока цена приблизится к текущему TP
    while await sugar.get_bid() < new_tp - 0.0030:
        await asyncio.sleep(10)

    await sugar.modify_position_tp(ticket, tp=new_tp)
    print(f"TP extended to {new_tp}")
```

---

## 📚 См. также

- [modify_position_sl](modify_position_sl.md) - Изменение только стоп-лосса
- [modify_position_sltp](modify_position_sltp.md) - Изменение и SL, и TP
- [buy_market_with_sltp](../5.%20Trading_With_SLTP/buy_market_with_sltp.md) - Открытие с SL/TP
- [close_position](close_position.md) - Закрытие позиции
