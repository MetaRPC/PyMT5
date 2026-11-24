## symbol_info_margin_rate — Как это работает

---

## 📌 Обзор

Этот пример демонстрирует, как получить **требования к марже для торгового символа** в зависимости от направления сделки с помощью низкоуровневого асинхронного метода `symbol_info_margin_rate()`.

В отличие от параметров символа, которые не зависят от направления (digits, спред, своп и т. д.), требования к марже могут **различаться для BUY и SELL**.

Метод используется, когда нужно понять:

* Сколько маржи требуется для открытия позиции
* Одинаковы ли условия для покупки и продажи
* Как тип счёта или инструмент влияет на расчёт маржи

---

## Сигнатура метода

```python
async def symbol_info_margin_rate(
    symbol: str,
    order_type: ENUM_ORDER_TYPE,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Ключевые моменты:

* Метод асинхронный и должен вызываться с `await`
* `symbol` — имя торгового символа (например, `"XAUUSD"`)
* `order_type` задаёт направление сделки (`BUY`, `SELL` и т. д.)
* `deadline` и `cancellation_event` управляют временем выполнения
* Метод возвращает объект с коэффициентами маржи

---

## 🧩 Пример кода — Сравнение маржи для BUY и SELL

```python
# Получить ставки маржи для BUY
buy_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

# Получить ставки маржи для SELL
sell_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_SELL
)

print(f"XAUUSD Margin Rates:")
print(f"  BUY  - Initial: {buy_rates.initial_margin_rate}, Maintenance: {buy_rates.maintenance_margin_rate}")
print(f"  SELL - Initial: {sell_rates.initial_margin_rate}, Maintenance: {sell_rates.maintenance_margin_rate}")

if buy_rates.initial_margin_rate == sell_rates.initial_margin_rate:
    print("  Same margin rates for both directions (hedge account)")
else:
    print("  Different margin rates (check account type)")
```

В этом примере метод вызывается дважды для одного и того же символа, но с разными направлениями сделки.

---

## 🟢 Подробное объяснение

---

### 1️⃣ Запрос параметров маржи для BUY

```python
buy_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)
```

На этом шаге:

* Выполняется один асинхронный вызов
* Имя символа и тип ордера BUY передаются в терминал
* Возвращается объект с параметрами маржи для покупки

Возвращаемый объект содержит коэффициенты, которые терминал использует при расчёте маржи для позиции BUY.

---

### 2️⃣ Запрос параметров маржи для SELL

```python
sell_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_SELL
)
```

Метод вызывается снова:

* Тот же символ
* Тот же метод
* Другое направление сделки

Результат — второй объект с параметрами маржи, теперь для позиции SELL.

Каждый вызов:

* Независим
* Выполняется отдельным запросом
* Возвращает данные только для указанного направления

---

### 3️⃣ Работа с полученными данными

```python
buy_rates.initial_margin_rate
buy_rates.maintenance_margin_rate
```

Оба объекта (`buy_rates` и `sell_rates`) содержат одни и те же поля:

* `initial_margin_rate` — коэффициент начальной маржи
* `maintenance_margin_rate` — коэффициент поддерживающей маржи

Это числовые значения, которые можно:

* Сравнивать
* Логировать
* Использовать в собственных расчётах

---

### 4️⃣ Сравнение требований к марже

```python
if buy_rates.initial_margin_rate == sell_rates.initial_margin_rate:
```

Начинается прикладная логика.

В примере сравнивается **начальная маржа** для BUY и SELL:

* Если значения равны — условия по марже симметричны
* Если различаются — требования зависят от направления сделки

Это сравнение не является частью API — это решение пользовательского кода.

---

### 5️⃣ Интерпретация результатов

```python
print("Same margin rates for both directions (hedge account)")
```

Когда значения совпадают, обычно можно сделать вывод, что:

* Счёт работает в режиме хеджирования
* Требования к марже одинаковы для BUY и SELL

---

```python
print("Different margin rates (check account type)")
```

Если значения различаются:

* Маржа зависит от направления позиции
* Это может быть связано с типом счёта или инструментом

Код не делает предположений, а только фиксирует факт различия.

---

## Итог

В этом примере `symbol_info_margin_rate()` используется для получения и сравнения требований к марже для одного символа по разным направлениям сделки.

Метод возвращает коэффициенты маржи для указанного символа и типа ордера, а вся логика анализа и интерпретации остаётся на стороне вызывающего кода.
