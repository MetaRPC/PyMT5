# Рассчитать размер позиции (`calculate_position_size`)

> **Sugar-метод:** Рассчитывает оптимальный размер позиции на основе процента риска от счёта и стоп-лосса.

**Информация об API:**

* **Метод:** `sugar.calculate_position_size(symbol, risk_percent, sl_pips)`
* **Возвращает:** Размер позиции в лотах (float)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def calculate_position_size(
    self,
    symbol: str,
    risk_percent: float,
    sl_pips: float
) -> float
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Да | - | Торговый символ (например, "EURUSD") |
| `risk_percent` | `float` | Да | - | Риск в процентах от баланса (например, 2.0 для 2%) |
| `sl_pips` | `float` | Да | - | Расстояние стоп-лосса в пипсах |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `float` | Оптимальный размер позиции в лотах, скорректированный под ограничения символа |

---

## 🏛️ Основное

**Что делает:**

- Рассчитывает размер позиции на основе фиксированного процента риска
- Использует стандартную формулу управления рисками форекс
- Автоматически корректирует под ограничения объёма символа
- Возвращает объём, готовый к использованию в ордерах

**Ключевое поведение:**

- Формула: `volume = (balance × risk% / 100) / (sl_pips × pip_value)`
- Стоимость пипса рассчитывается как: `point × 10 × contract_size`
- Округляет до volume_step символа
- Ограничивает значениями volume_min и volume_max
- Основано на текущем балансе счёта

**Формула управления рисками:**

1. Рассчитать сумму риска в валюте счёта
2. Рассчитать стоимость пипса для 1 лота
3. Рассчитать volume = risk_amount / (sl_pips × pip_value)
4. Округлить и ограничить под ограничения символа

---

## ⚡ Под капотом

```
MT5Sugar.calculate_position_size()
    ↓ вызывает
MT5Sugar.get_balance()
    ↓ вызывает
MT5Sugar.get_symbol_info(symbol)
    ↓ рассчитывает:
        risk_amount = balance × (risk_percent / 100)
        pip_value = point × 10 × contract_size
        volume = risk_amount / (sl_pips × pip_value)
    ↓ округляет до volume_step
    ↓ ограничивает значениями volume_min/volume_max
    ↓ возвращает скорректированный объём
```

**Цепочка вызовов:**

1. Sugar вызывает get_balance() для получения текущего баланса
2. Sugar вызывает get_symbol_info() для параметров символа
3. Sugar рассчитывает risk_amount из баланса и risk_percent
4. Sugar рассчитывает pip_value, используя point и contract_size
5. Sugar рассчитывает сырой объём по формуле
6. Sugar округляет объём до volume_step
7. Sugar ограничивает значениями volume_min и volume_max
8. Возвращает итоговый объём

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1724`
- Использует: get_balance (строка 386), get_symbol_info (строка 1615)

---

## Когда использовать

**Используйте `calculate_position_size()`, когда:**

- Реализуете управление рисками с фиксированным процентом
- Строите автоматические торговые системы
- Рассчитываете безопасные размеры позиций
- Определяете размер позиции на основе риска
- Следуете правилам управления капиталом

**Не используйте, когда:**

- Используете фиксированные размеры лотов
- Размер позиции задаётся вручную
- Не используете стоп-лосс
- Нужны более сложные расчёты риска
- Размер позиции предопределён

---

## 🔗 Примеры

### Пример 1: Базовый риск 2% на сделку

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def risk_based_trading():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    risk_percent = 2.0  # Риск 2% на сделку
    sl_pips = 50  # Стоп-лосс в 50 пипсов

    # Рассчитать размер позиции
    volume = await sugar.calculate_position_size(
        symbol,
        risk_percent,
        sl_pips
    )

    # Получить информацию о счёте
    balance = await sugar.get_balance()

    print(f"Account balance: ${balance:.2f}")
    print(f"Risk per trade: {risk_percent}% = ${balance * 0.02:.2f}")
    print(f"Stop loss: {sl_pips} pips")
    print(f"Position size: {volume} lots")

    # Разместить ордер с рассчитанным размером
    current_ask = await sugar.get_ask(symbol)
    sl_price = current_ask - (sl_pips * 0.0001)

    ticket = await sugar.buy_market_with_sltp(
        symbol,
        volume=volume,
        sl=sl_price
    )
    print(f"Order placed: {ticket}")

# Вывод:
# Account balance: $10000.00
# Risk per trade: 2.0% = $200.00
# Stop loss: 50 pips
# Position size: 0.4 lots
# Order placed: 123456789
```

### Пример 2: Разные уровни риска

```python
async def compare_risk_levels():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    sl_pips = 30

    # Попробовать разные уровни риска
    risk_levels = [0.5, 1.0, 2.0, 5.0]

    print(f"Position sizes for {symbol} with {sl_pips} pip SL:")

    for risk_pct in risk_levels:
        volume = await sugar.calculate_position_size(
            symbol,
            risk_pct,
            sl_pips
        )

        print(f"  {risk_pct}% risk: {volume} lots")

# Вывод:
# Position sizes for EURUSD with 30 pip SL:
#   0.5% risk: 0.17 lots
#   1.0% risk: 0.33 lots
#   2.0% risk: 0.67 lots
#   5.0% risk: 1.67 lots
```

### Пример 3: Тесный против широкого стоп-лосса

```python
async def compare_stop_losses():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    risk_percent = 2.0

    # Разные размеры стоп-лосса
    stop_losses = [20, 50, 100, 200]

    print(f"Position sizes at {risk_percent}% risk:")

    for sl_pips in stop_losses:
        volume = await sugar.calculate_position_size(
            symbol,
            risk_percent,
            sl_pips
        )

        print(f"  {sl_pips} pip SL: {volume} lots")

# Вывод:
# Position sizes at 2.0% risk:
#   20 pip SL: 1.0 lots
#   50 pip SL: 0.4 lots
#   100 pip SL: 0.2 lots
#   200 pip SL: 0.1 lots
```

---

## Типичные ошибки

**Ошибка 1: Использование пунктов вместо пипсов**
```python
# ОШИБКА: sl_pips ожидает пипсы, а не пункты
sl_points = 200  # 200 пунктов = 20 пипсов для EURUSD

volume = await sugar.calculate_position_size("EURUSD", 2.0, sl_points)
# Рассчитывает для 200 пипсов вместо 20 пипсов, объём будет в 10 раз меньше
```

**Решение:** Переведите пункты в пипсы
```python
sl_points = 200
sl_pips = sl_points / 10  # 20 пипсов

volume = await sugar.calculate_position_size("EURUSD", 2.0, sl_pips)
```

**Ошибка 2: Непроверка минимального объёма**
```python
# Очень тесный SL или низкий риск может дать объём < минимума
volume = await sugar.calculate_position_size("EURUSD", 0.1, 5)
# Возвращает volume_min (0.01), даже если расчёт даёт 0.001
```

**Решение:** Проверяйте полученное значение
```python
volume = await sugar.calculate_position_size("EURUSD", 0.1, 5)

info = await sugar.get_symbol_info("EURUSD")
if volume == info.volume_min:
    print(f"Warning: Using minimum volume {volume}")
    print("Consider increasing risk% or widening stop loss")
```

**Ошибка 3: Изменение баланса во время торговли**
```python
# Объём рассчитан на основе начального баланса
volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)

# После нескольких сделок баланс изменился
# Но используется старый расчёт объёма
await sugar.buy_market("EURUSD", volume=volume)  # Может рисковать больше/меньше 2%
```

**Решение:** Пересчитывайте перед каждой сделкой
```python
# Всегда рассчитывайте заново перед каждой сделкой
volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)

# Сразу использовать
ticket = await sugar.buy_market("EURUSD", volume=volume)
```

---

## Полезные советы

**Совет 1: Безопасный расчёт размера позиции с проверкой**
```python
async def safe_position_size(sugar, symbol, risk_pct, sl_pips):
    """Рассчитать размер позиции с проверкой."""
    # Рассчитать
    volume = await sugar.calculate_position_size(symbol, risk_pct, sl_pips)

    # Получить ограничения
    info = await sugar.get_symbol_info(symbol)

    # Проверить, не на минимуме ли
    if volume == info.volume_min:
        print(f"WARNING: At minimum volume {volume}")
        print(f"Actual risk may be higher than {risk_pct}%")

    # Проверить, не на максимуме ли
    if volume == info.volume_max:
        print(f"WARNING: At maximum volume {volume}")
        print(f"Risk exceeds {risk_pct}% - reduce risk or widen SL")

    return volume

# Использование
volume = await safe_position_size(sugar, "EURUSD", 2.0, 50)
```

**Совет 2: Расчёт фактического риска в долларах**
```python
async def show_dollar_risk(sugar, symbol, risk_pct, sl_pips):
    """Рассчитать и отобразить риск в долларах."""
    balance = await sugar.get_balance()
    volume = await sugar.calculate_position_size(symbol, risk_pct, sl_pips)

    # Получить информацию о символе
    info = await sugar.get_symbol_info(symbol)

    # Рассчитать стоимость пипса
    pip_value = info.point * 10 * info.contract_size

    # Рассчитать риск в долларах
    dollar_risk = sl_pips * pip_value * volume

    print(f"Balance: ${balance:.2f}")
    print(f"Risk: {risk_pct}% = ${balance * (risk_pct/100):.2f}")
    print(f"Volume: {volume} lots")
    print(f"SL: {sl_pips} pips")
    print(f"Actual risk: ${dollar_risk:.2f}")

# Использование
await show_dollar_risk(sugar, "EURUSD", 2.0, 50)
```

**Совет 3: Распределение риска между несколькими позициями**
```python
async def allocate_risk_to_positions(sugar, positions, total_risk_pct):
    """Распределить общий риск между несколькими позициями."""
    # Разделить риск поровну
    risk_per_position = total_risk_pct / len(positions)

    sizes = {}
    for pos in positions:
        symbol = pos["symbol"]
        sl_pips = pos["sl_pips"]

        volume = await sugar.calculate_position_size(
            symbol,
            risk_per_position,
            sl_pips
        )

        sizes[symbol] = volume

    return sizes

# Использование
positions = [
    {"symbol": "EURUSD", "sl_pips": 50},
    {"symbol": "GBPUSD", "sl_pips": 60},
    {"symbol": "USDJPY", "sl_pips": 40}
]

sizes = await allocate_risk_to_positions(sugar, positions, total_risk_pct=6.0)
# Каждая позиция рискует 2% (6% / 3 позиции)

for symbol, volume in sizes.items():
    print(f"{symbol}: {volume} lots")
```

---

## 📚 См. также

- [calculate_required_margin](calculate_required_margin.md) - Рассчитать маржу для позиции
- [can_open_position](can_open_position.md) - Проверить, можно ли открыть позицию
- [get_balance](../2.%20Account_Properties/get_balance.md) - Получить баланс счёта
- [get_symbol_info](../9.%20Symbol_Information/get_symbol_info.md) - Получить параметры символа
