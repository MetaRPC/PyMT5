## order_calc_margin — Как это работает

---

## 📌 Обзор

Этот пример показывает, как использовать низкоуровневый метод `order_calc_margin()` для **оценки допустимого размера позиции на основе заданного риска**.

Важно: в этом примере **не выполняется ни одной торговой операции**. Метод используется исключительно для расчёта — как калькулятор, а не как действие.

Основная задача примера:

> понять, какой объём позиции можно открыть, не превышая заданный риск по счёту.

---

## Сигнатура метода

```python
async def order_calc_margin(
    request: OrderCalcMarginRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> OrderCalcMarginData
```

Ключевые моменты:

* метод асинхронный
* не открывает сделки
* не резервирует средства
* не изменяет состояние счёта
* возвращает только рассчитанное значение маржи

---

## 🧩 Пример кода — Расчёт размера позиции на основе риска

```python
async def risk_based_sizing(symbol: str, risk_percent: float = 2.0):
    """Calculate position size based on risk percentage"""

    # Получить сводную информацию о счёте
    summary = await account.account_summary()

    # Максимально допустимый риск в деньгах
    max_risk_amount = summary.account_balance * (risk_percent / 100.0)

    print(f"Risk-based position sizing for {symbol}:")
    print(f"  Account balance: ${summary.account_balance:,.2f}")
    print(f"  Risk: {risk_percent}% = ${max_risk_amount:,.2f}\n")

    # Проверить несколько возможных объёмов
    volumes = [0.01, 0.05, 0.10, 0.20, 0.50, 1.00]

    print(f"{'Volume':<10} {'Margin':<15} {'% of Balance':<15}")
    print("-" * 45)

    for volume in volumes:
        request = OrderCalcMarginRequest(
            symbol=symbol,
            order_type=ORDER_TYPE_TF_BUY,
            volume=volume,
            open_price=1.0  # расчётная цена
        )

        result = await account.order_calc_margin(request)

        margin_percent = (result.margin / summary.account_balance) * 100
        status = "[OK]" if margin_percent <= risk_percent else "[OVER]"

        print(f"{volume:<10.2f} ${result.margin:>12,.2f} {margin_percent:>13.2f}% {status}")
```

---

## 🟢 Подробное объяснение

---

### 1️⃣ Получение баланса счёта

```python
summary = await account.account_summary()
```

На этом шаге:

* получается текущий баланс счёта
* он используется как база для расчёта риска

Это исходные данные, не связанные с торговлей.

---

### 2️⃣ Перевод риска из процентов в деньги

```python
max_risk_amount = summary.account_balance * (risk_percent / 100.0)
```

Пример:

* баланс = $10,000
* риск = 2%
* допустимый риск = $200

Это **чистая пользовательская бизнес-логика**, а не часть API.

---

### 3️⃣ Формирование гипотетической сделки

```python
request = OrderCalcMarginRequest(
    symbol=symbol,
    order_type=ORDER_TYPE_TF_BUY,
    volume=volume,
    open_price=1.0
)
```

Важно понимать:

* сделка **не открывается**
* параметры используются только для расчёта
* `open_price` может быть условным значением

Запрос описывает *планируемую*, а не реальную операцию.

---

### 4️⃣ Расчёт требуемой маржи

```python
result = await account.order_calc_margin(request)
```

На этом шаге:

* сервер рассчитывает маржу
* учитываются настройки счёта, символ и тип ордера
* возвращается единственное число — `result.margin`

В процессе состояние счёта не изменяется.

---

### 5️⃣ Сравнение с допустимым риском

```python
margin_percent = (result.margin / summary.account_balance) * 100
```

Здесь пользовательский код:

* сравнивает рассчитанную маржу с допустимым риском
* принимает решение, приемлем ли этот объём

API не участвует в этом шаге.

---

## Роль низкоуровневого метода

Чёткая граница ответственности:

**`order_calc_margin()`**:

* выполняет серверный расчёт маржи
* ничего не открывает
* не влияет на счёт

**Пользовательский код**:

* определяет риск
* выбирает объёмы
* интерпретирует результат
* принимает торговые решения

---

## Итог

Этот пример иллюстрирует безопасный и корректный паттерн:

> **спланировать сделку → рассчитать маржу → оценить риск → принять решение**

Метод `order_calc_margin()` предназначен именно для стадии планирования и должен использоваться **до открытия сделки**, а не после.

Он позволяет принимать обоснованные решения, не рискуя состоянием счёта.
