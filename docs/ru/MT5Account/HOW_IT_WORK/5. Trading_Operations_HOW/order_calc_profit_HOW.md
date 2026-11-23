## order_calc_profit — Как это работает

---

## 📌 Обзор

Этот пример показывает, как использовать низкоуровневый метод `order_calc_profit()` для **расчёта потенциальной прибыли или убытка до выполнения сделки**.

Важно: в этом примере **не выполняется ни одной торговой операции**. Метод используется исключительно для расчёта — как калькулятор, а не как действие.

Основная задача примера:

> рассчитать соотношение риск/прибыль, чтобы оценить целесообразность сделки до открытия позиции.

---

## Сигнатура метода

```python
async def order_calc_profit(
    request: OrderCalcProfitRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> OrderCalcProfitData
```

Ключевые моменты:

* метод асинхронный
* не открывает сделки
* не резервирует средства
* не изменяет состояние счёта
* возвращает только рассчитанное значение прибыли/убытка

---

## 🧩 Пример кода — Расчёт риск/прибыль

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_risk_reward():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        entry = 1.10000
        stop_loss = 1.09950  # 50 пунктов SL
        take_profit = 1.10100  # 100 пунктов TP

        # Рассчитать потенциальный убыток (срабатывание SL)
        loss_req = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=entry,
            close_price=stop_loss
        )

        loss_result = await account.order_calc_profit(loss_req)
        risk = abs(loss_result.profit)

        # Рассчитать потенциальную прибыль (срабатывание TP)
        profit_req = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=entry,
            close_price=take_profit
        )

        profit_result = await account.order_calc_profit(profit_req)
        reward = profit_result.profit

        rr_ratio = reward / risk

        print(f"[RISK/REWARD ANALYSIS]")
        print(f"  Entry: {entry}")
        print(f"  SL: {stop_loss} (Risk: ${risk:.2f})")
        print(f"  TP: {take_profit} (Reward: ${reward:.2f})")
        print(f"  R:R Ratio: 1:{rr_ratio:.2f}")

    finally:
        await account.channel.close()

asyncio.run(calc_risk_reward())
```

---

## 🟢 Подробное объяснение

---

### 1️⃣ Подключение и настройка

```python
account = MT5Account(
    user=12345,
    password="password",
    grpc_server="mt5.mrpc.pro:443"
)

await account.connect_by_server_name(
    server_name="YourBroker-Demo",
    base_chart_symbol="EURUSD"
)
```

На этом шаге:

* создаётся экземпляр MT5Account с учётными данными для подключения
* устанавливается соединение с терминалом MetaTrader 5 через gRPC
* указывается базовый символ графика для инициализации

Это стандартная процедура подключения, необходимая перед любыми операциями.

---

### 2️⃣ Определение параметров сделки

```python
entry = 1.10000
stop_loss = 1.09950  # 50 пунктов SL
take_profit = 1.10100  # 100 пунктов TP
```

Здесь:

* определяется цена входа (планируемая цена открытия)
* уровень стоп-лосса устанавливается на 50 пунктов ниже входа
* уровень тейк-профита устанавливается на 100 пунктов выше входа

Это **гипотетические значения** для целей планирования. Сделка пока не открывается.

---

### 3️⃣ Расчёт потенциального убытка (риск)

```python
loss_req = trade_pb2.OrderCalcProfitRequest(
    order_type=trade_pb2.ORDER_TYPE_TF_BUY,
    symbol="EURUSD",
    volume=0.10,
    open_price=entry,
    close_price=stop_loss
)

loss_result = await account.order_calc_profit(loss_req)
risk = abs(loss_result.profit)
```

Важно понимать:

* сделка **не открывается**
* мы рассчитываем, что произойдёт, если сработает стоп-лосс
* `open_price=entry` и `close_price=stop_loss` моделируют худший сценарий
* `abs()` используется, потому что убыток возвращается как отрицательное значение

Запрос описывает *планируемую*, а не реальную операцию.

---

### 4️⃣ Расчёт потенциальной прибыли (вознаграждение)

```python
profit_req = trade_pb2.OrderCalcProfitRequest(
    order_type=trade_pb2.ORDER_TYPE_TF_BUY,
    symbol="EURUSD",
    volume=0.10,
    open_price=entry,
    close_price=take_profit
)

profit_result = await account.order_calc_profit(profit_req)
reward = profit_result.profit
```

На этом шаге:

* сервер рассчитывает прибыль при срабатывании тейк-профита
* те же параметры сделки (символ, объём, тип ордера)
* отличается только `close_price` — теперь это уровень тейк-профита
* результат — положительное значение, отражающее потенциальный доход

В процессе состояние счёта не изменяется.

---

### 5️⃣ Расчёт соотношения риск/прибыль

```python
rr_ratio = reward / risk
```

Здесь пользовательский код:

* делит потенциальное вознаграждение на потенциальный риск
* получает соотношение риск/прибыль
* пример: если reward=$100 и risk=$50, R:R = 2.0 (или 1:2)

API не участвует в этом шаге — это чистая бизнес-логика.

---

### 6️⃣ Отображение результатов

```python
print(f"[RISK/REWARD ANALYSIS]")
print(f"  Entry: {entry}")
print(f"  SL: {stop_loss} (Risk: ${risk:.2f})")
print(f"  TP: {take_profit} (Reward: ${reward:.2f})")
print(f"  R:R Ratio: 1:{rr_ratio:.2f}")
```

Пример вывода:

```
[RISK/REWARD ANALYSIS]
  Entry: 1.1
  SL: 1.0995 (Risk: $50.00)
  TP: 1.101 (Reward: $100.00)
  R:R Ratio: 1:2.00
```

Это показывает трейдеру, что на каждый $1 риска он может получить $2 — благоприятное соотношение риск/прибыль 1:2.

---

## Роль низкоуровневого метода

Чёткая граница ответственности:

**`order_calc_profit()`**:

* выполняет серверный расчёт прибыли
* учитывает свойства символа, размер лота и движение цены
* ничего не открывает
* не влияет на счёт

**Пользовательский код**:

* определяет уровни входа, стоп-лосса и тейк-профита
* выполняет два расчёта (риск и вознаграждение)
* интерпретирует результат
* принимает торговые решения на основе соотношения R:R

---

## Итог

Этот пример иллюстрирует профессиональный торговый паттерн:

> **спланировать сделку → рассчитать риск → рассчитать вознаграждение → оценить соотношение → принять решение**

Метод `order_calc_profit()` предназначен именно для стадии планирования и должен использоваться **до открытия сделки**, а не после.

Он позволяет принимать обоснованные решения, не рискуя состоянием счёта.

**Типичные сценарии использования:**

* Расчёт соотношения риск/прибыль перед входом в сделку
* Определение, соответствует ли конфигурация сделки вашим торговым правилам (например, минимум 1:2 R:R)
* Расчёт стоимости пункта для разных размеров лота
* Сравнение прибыльности между разными символами
* Планирование стратегий выхода на основе ожидаемой прибыли/убытка
