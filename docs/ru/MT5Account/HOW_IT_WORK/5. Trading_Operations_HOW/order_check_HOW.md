## order_check — Как это работает

---

## 📌 Обзор

Этот пример показывает, как использовать низкоуровневый метод `order_check()` для **проверки исполнимости торгового запроса** до его фактической отправки на сервер.

Метод используется на стадии *предторговой валидации* и отвечает на ключевой вопрос:

> «Примет ли сервер такую сделку прямо сейчас при текущих условиях?»

Важно: `order_check()` **не открывает сделку** и **не изменяет состояние счёта**. Он используется исключительно для проверки.

---

## Сигнатура метода

```python
async def order_check(
    request: OrderCheckRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> OrderCheckData
```

Ключевые моменты:

* метод асинхронный
* принимает почти полный торговый запрос
* выполняет валидацию на стороне сервера
* не создаёт ордер и не резервирует средства

---

## 🧩 Пример кода — Проверка нескольких объёмов

```python
async def check_multiple_volumes():
    volumes = [0.01, 0.05, 0.10, 0.50, 1.00]

    print("Checking volumes for EURUSD BUY:")
    print("-" * 60)

    for volume in volumes:
        request = OrderCheckRequest()
        request.mql_trade_request.action = TRADE_ACTION_DEAL
        request.mql_trade_request.symbol = "EURUSD"
        request.mql_trade_request.volume = volume
        request.mql_trade_request.order_type = ORDER_TYPE_TF_BUY
        request.mql_trade_request.price = 0.0
        request.mql_trade_request.deviation = 20
        request.mql_trade_request.type_filling = ORDER_FILLING_FOK
        request.mql_trade_request.type_time = ORDER_TIME_GTC

        result = await account.order_check(request)

        if result.mql_trade_check_result.returned_code == 0:
            print(
                f"[OK] {volume:>6.2f} lots - "
                f"Margin: ${result.mql_trade_check_result.margin:>10,.2f}, "
                f"Free: ${result.mql_trade_check_result.free_margin:>10,.2f}"
            )
        else:
            print(
                f"[FAIL] {volume:>6.2f} lots - "
                f"{result.mql_trade_check_result.comment}"
            )
```

---

## 🟢 Подробное объяснение

---

### 1️⃣ Перебор возможных объёмов

```python
volumes = [0.01, 0.05, 0.10, 0.50, 1.00]
```

Здесь пользовательский код:

* определяет возможные размеры позиции
* заранее не знает, какие из них приемлемы
* использует `order_check()` как инструмент проверки

---

### 2️⃣ Формирование торгового запроса

```python
request.mql_trade_request.action = TRADE_ACTION_DEAL
request.mql_trade_request.symbol = "EURUSD"
request.mql_trade_request.volume = volume
request.mql_trade_request.order_type = ORDER_TYPE_TF_BUY
```

Важно:

* структура запроса соответствует реальному ордеру
* заданы все критически важные параметры
* это *планируемая*, а не фактическая сделка

---

### 3️⃣ Серверная валидация ордера

```python
result = await account.order_check(request)
```

На этой стадии сервер проверяет:

* корректность параметров
* достаточность средств
* торговые ограничения брокера
* текущие рыночные условия
* возможность исполнения (filling, deviation)

Изменения состояния счёта не происходит.

---

### 4️⃣ Анализ результата валидации

```python
result.mql_trade_check_result.returned_code
```

Интерпретация:

* `0` — ордер может быть исполнен
* ненулевое значение — ордер будет отклонён

Дополнительно возвращается:

* рассчитанная маржа
* свободная маржа после сделки
* текстовый комментарий с объяснением причины отказа

---

### 5️⃣ Определение диапазона допустимых объёмов

Перебирая объёмы, пользовательский код:

* находит максимально допустимый объём
* видит, где начинается отказ
* получает точную причину ограничения

Это финальная стадия перед фактической торговлей.

---

## Роль низкоуровневого метода

Чёткая граница ответственности:

**`order_check()`**:

* валидирует торговый запрос на сервере
* возвращает технический результат проверки
* не принимает торговых решений

**Пользовательский код**:

* формирует параметры сделки
* перебирает объёмы
* интерпретирует результат
* решает, отправлять ли ордер

---

## Итог

Этот пример иллюстрирует последний безопасный шаг перед торговлей:

> **проверить исполнимость → проанализировать результат → принять решение**

Метод `order_check()` предназначен для строгой предторговой валидации и должен использоваться **перед `order_send()`**, особенно при динамическом выборе объёма и в автоматизированной торговле.
