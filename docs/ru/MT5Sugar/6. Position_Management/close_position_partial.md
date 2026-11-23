# Частичное закрытие позиции (`close_position_partial`)

> **Sugar-метод:** Закрывает часть позиции на указанный объём.

**Информация об API:**

* **Метод:** `sugar.close_position_partial(ticket, volume)`
* **Возвращает:** `True` при успешном частичном закрытии, иначе `False`
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def close_position_partial(self, ticket: int, volume: float) -> bool
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Да | - | Номер тикета позиции |
| `volume` | `float` | Да | - | Объём для закрытия (должен быть меньше объёма позиции) |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `bool` | `True` при успешном частичном закрытии (return_code == 10009), иначе `False` |

**Вызывает:**

- `ValueError`, если позиция не найдена
- `ValueError`, если volume >= объёма позиции

---

## 🏛️ Основное

**Что делает:**

- Закрывает указанный объём открытой позиции
- Оставшийся объём сохраняется как исходная позиция
- Создаёт противоположный рыночный ордер на указанный объём
- Тикет исходной позиции сохраняется с уменьшенным объёмом

**Ключевое поведение:**

- Объём должен быть меньше объёма позиции
- Позиции BUY: закрываются ордером SELL по цене BID
- Позиции SELL: закрываются ордером BUY по цене ASK
- Оставшаяся позиция сохраняет тот же номер тикета
- Использует проскальзывание по умолчанию 10 пунктов

---

## ⚡ Под капотом

```
MT5Sugar.close_position_partial()
    ↓ fetches position
MT5Service.get_opened_orders()
    ↓ validates volume < position.volume
    ↓ determines opposite order type
    ↓ fetches current price
MT5Service.get_symbol_tick()
    ↓ builds OrderSendRequest (opposite direction)
MT5Service.place_order()
    ↓ gRPC protobuf
TradingHelperService.OrderSend()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar получает все позиции для поиска совпадающего тикета
2. Вызывает ValueError, если позиция не найдена
3. Проверяет volume < position.volume (вызывает ошибку, если >=)
4. Определяет противоположный тип ордера (BUY→SELL, SELL→BUY)
5. Получает текущую цену тика (BID для SELL, ASK для BUY)
6. Создаёт OrderSendRequest с противоположной операцией и частичным объёмом
7. Отправляет ордер через Service.place_order()
8. Возвращает True, если returned_code == 10009

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1241`
- Service: `src/pymt5/mt5_service.py:929`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1713`

---

## Когда использовать

**Используйте `close_position_partial()`, когда:**

- Фиксируете частичную прибыль на целевых уровнях
- Постепенно выходите из позиций
- Снижаете экспозицию, сохраняя позицию открытой
- Реализуете многоуровневые стратегии выхода

**Не используйте, когда:**

- Хотите закрыть всю позицию (используйте `close_position()`)
- Объём равен или превышает объём позиции
- Позиция уже закрыта

---

## 🔗 Примеры

### Пример 1: Фиксация половины прибыли

```python
from pymt5 import MT5Account, MT5Service, MT5Sugar

async def take_half_profit():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию 0.1 лота
    ticket = await sugar.buy_market(volume=0.10)
    print(f"Position opened: #{ticket}, 0.10 lots")

    # Ждать прибыли (упрощённо)
    profit = await sugar.get_floating_profit()
    while profit < 50:
        await asyncio.sleep(5)
        profit = await sugar.get_floating_profit()

    # Закрыть половину позиции
    success = await sugar.close_position_partial(ticket, volume=0.05)

    if success:
        print("Closed 0.05 lots, 0.05 lots remaining")
    else:
        print("Partial close failed")

```

### Пример 2: Многоуровневая стратегия выхода

```python
async def tiered_exit():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию 0.3 лота
    ticket = await sugar.buy_market(volume=0.30)
    entry_price = await sugar.get_ask()

    print(f"Position: #{ticket}, 0.30 lots at {entry_price}")

    # Выход в 3 этапа
    targets = [
        (entry_price + 0.0030, 0.10, "Target 1: +30 pips"),
        (entry_price + 0.0060, 0.10, "Target 2: +60 pips"),
        (entry_price + 0.0100, 0.10, "Target 3: +100 pips")
    ]

    for target_price, close_volume, label in targets:
        # Ждать, пока цена достигнет цели
        while True:
            current = await sugar.get_bid()

            if current >= target_price:
                success = await sugar.close_position_partial(
                    ticket,
                    volume=close_volume
                )

                if success:
                    print(f"{label} - Closed {close_volume} lots")
                    break

            await asyncio.sleep(5)

    print("All targets hit, position fully closed")

```

### Пример 3: Снижение риска при прибыли

```python
async def reduce_risk_on_profit():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol="EURUSD")

    await sugar.quick_connect("YourBroker-Demo")

    # Открыть позицию
    ticket = await sugar.buy_market(volume=0.20)
    entry_price = await sugar.get_ask()

    # Закрыть 75% при прибыли 50 пунктов, оставить 25%
    while True:
        current_price = await sugar.get_bid()
        profit_pips = (current_price - entry_price) / 0.0001

        if profit_pips >= 50:
            # Закрыть 0.15 лота (75%), оставить 0.05 лота (25%)
            success = await sugar.close_position_partial(
                ticket,
                volume=0.15
            )

            if success:
                print("Closed 75%, letting 25% run with trailing stop")

                # Перенести оставшиеся 0.05 лота в безубыток
                await sugar.modify_position_sltp(
                    ticket,
                    sl=entry_price,
                    tp=None
                )
                break

        await asyncio.sleep(5)

```

---

## Частые ошибки

**Ошибка 1: Слишком большой объём**
```python
# У позиции 0.10 лота
ticket = await sugar.buy_market(volume=0.10)

# ОШИБКА: Нельзя закрыть 0.10 или больше
try:
    await sugar.close_position_partial(ticket, volume=0.10)
except ValueError as e:
    print(e)  # "Partial volume must be less than position volume"
```

**Решение:** всегда закрывайте объём меньше объёма позиции
```python
# Закрыть часть, не всё
await sugar.close_position_partial(ticket, volume=0.05)  # OK
await sugar.close_position_partial(ticket, volume=0.09)  # OK
```

**Ошибка 2: Не отслеживается оставшийся объём**
```python
# Открыть 0.10 лота
ticket = await sugar.buy_market(volume=0.10)

# Закрыть 0.05 лота
await sugar.close_position_partial(ticket, volume=0.05)

# ОШИБКА: Нельзя закрыть 0.06 (осталось только 0.05)
await sugar.close_position_partial(ticket, volume=0.06)
```

**Решение:** отслеживайте или проверяйте оставшийся объём
```python
# Проверить объём позиции перед закрытием
positions_data = await sugar._service.get_opened_orders()

for pos in positions_data.position_infos:
    if pos.ticket == ticket:
        remaining = pos.volume
        print(f"Remaining volume: {remaining}")

        # Закрыть только то, что осталось
        close_vol = min(0.05, remaining)
        await sugar.close_position_partial(ticket, close_vol)
```

**Ошибка 3: Несколько частичных закрытий без обновления объёма**
```python
# Открыть 0.30 лота
ticket = await sugar.buy_market(volume=0.30)

# Закрывать по шагам
await sugar.close_position_partial(ticket, 0.10)  # осталось 0.20
await sugar.close_position_partial(ticket, 0.10)  # осталось 0.10
await sugar.close_position_partial(ticket, 0.10)  # осталось 0.00

# ОШИБКА: Позиция полностью закрыта, тикет недействителен для дальнейших частичных закрытий
await sugar.close_position_partial(ticket, 0.05)
```

**Решение:** проверяйте, существует ли ещё позиция
```python
# После каждого частичного закрытия проверять, существует ли позиция
success = await sugar.close_position_partial(ticket, 0.10)

if success:
    # Проверить, существует ли ещё позиция
    positions_data = await sugar._service.get_opened_orders()
    still_open = any(p.ticket == ticket for p in positions_data.position_infos)

    if not still_open:
        print("Position fully closed")
```

---

## Советы профи

**Совет 1: Выход долями в процентах**
```python
# Получить текущий объём позиции
positions_data = await sugar._service.get_opened_orders()

for pos in positions_data.position_infos:
    if pos.ticket == ticket:
        # Закрыть 50% позиции
        close_volume = pos.volume * 0.5

        await sugar.close_position_partial(ticket, close_volume)
        print(f"Closed 50%: {close_volume} lots")
```

**Совет 2: Сочетайте с корректировкой SL**
```python
# Частично закрыть и перенести SL в безубыток
entry_price = 1.0850

# Закрыть 50%
await sugar.close_position_partial(ticket, volume=0.05)

# Перенести SL в безубыток для оставшегося
await sugar.modify_position_sltp(ticket, sl=entry_price, tp=None)
```

**Совет 3: Пирамидальная стратегия выхода**
```python
# Выход пирамидой (сначала бóльшие объёмы)
total_volume = 0.30

exits = [
    (0.15, "50%"),  # Закрыть половину
    (0.10, "33%"),  # Закрыть треть оставшегося
    (0.05, "17%")   # Оставить небольшой объём
]

for volume, label in exits:
    success = await sugar.close_position_partial(ticket, volume)

    if success:
        print(f"Closed {label}: {volume} lots")

    await asyncio.sleep(60)  # Подождать между выходами
```

---

## 📚 См. также

- [close_position](close_position.md) - Закрытие всей позиции
- [close_all_positions](close_all_positions.md) - Закрытие всех позиций
- [modify_position_sltp](modify_position_sltp.md) - Изменение SL/TP
- [buy_market](../4.%20Simple_Trading/buy_market.md) - Открытие позиции BUY
