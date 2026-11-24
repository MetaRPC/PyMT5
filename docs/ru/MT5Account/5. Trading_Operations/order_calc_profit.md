# Расчёт потенциальной прибыли/убытка

> **Запрос:** Рассчитать потенциальную прибыль или убыток для планируемой торговой операции.

**Информация об API:**

* **Python API:** `MT5Account.order_calc_profit(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.TradeFunctions`
* **Proto-определение:** `OrderCalcProfit` (определено в `mt5-term-api-trade-functions.proto`)
* **Enum'ы в этом методе:** 1 enum с 9 константами (1 вход)

### RPC

* **Сервис:** `mt5_term_api.TradeFunctions`
* **Метод:** `OrderCalcProfit(OrderCalcProfitRequest) -> OrderCalcProfitReply`
* **Низкоуровневый клиент (сгенерированный):** `TradeFunctionsStub.OrderCalcProfit(request, metadata)`

---

## 💬 Только самое главное

* **Что это.** Рассчитывает потенциальную прибыль/убыток для сделки без её исполнения.
* **Зачем это нужно.** Планирование сделок, расчёт соотношений риск/доходность, определение размера позиции.
* **Валюта счёта.** Возвращает прибыль/убыток в валюте вашего счёта (USD, EUR и т. д.).

---

## 🎯 Назначение

Используйте для того, чтобы:

* Рассчитать прибыль/убыток перед открытием сделки
* Определить соотношение риск/доходность
* Спланировать стратегии выхода
* Сравнить прибыльность по разным символам
* Рассчитать стоимость пипса для разных размеров лота
* Спрогнозировать прибыль/убыток портфеля

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[OrderCalcProfit - Как это работает](../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_profit_HOW.md)**


```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

class MT5Account:
    # ...

    async def order_calc_profit(
        self,
        request: trade_pb2.OrderCalcProfitRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trade_pb2.OrderCalcProfitData:
        """
        Calculates potential profit/loss for a planned trade operation.

        Returns:
            OrderCalcProfitData: The potential profit/loss in account currency.
        """
```

**Сообщение запроса:**

```protobuf
message OrderCalcProfitRequest {
  ENUM_ORDER_TYPE_TF order_type = 1;  // Тип ордера
  string symbol = 2;                  // Имя символа
  double volume = 3;                  // Объём сделки в лотах
  double open_price = 4;              // Цена входа
  double close_price = 5;             // Цена выхода
}
```

---

## 🔽 Вход

| Параметр             | Тип                            | Описание                                      |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `request`            | `OrderCalcProfitRequest`       | Запрос на расчёт прибыли                       |
| `deadline`           | `Optional[datetime]`           | Крайний срок операции (опционально)           |
| `cancellation_event` | `Optional[asyncio.Event]`      | Событие для отмены запроса (опционально)       |

**Поля OrderCalcProfitRequest:**

| Поле          | Тип                  | Описание                             |
| ------------- | -------------------- | ------------------------------------ |
| `order_type`  | `ENUM_ORDER_TYPE_TF` | Тип ордера (enum)                    |
| `symbol`      | `string`             | Имя символа (например, "EURUSD")     |
| `volume`      | `double`             | Объём сделки в лотах                 |
| `open_price`  | `double`             | Цена входа                           |
| `close_price` | `double`             | Цена выхода                          |

---

## ⬆️ Выход

Возвращает объект `OrderCalcProfitData`.

**Поля OrderCalcProfitData:**

| Поле     | Тип      | Описание                                      |
| -------- | -------- | --------------------------------------------- |
| `profit` | `double` | Прибыль/убыток в валюте счёта (отрицательное = убыток) |

---

## 🧱 Связанные enum'ы (из proto)

### `ENUM_ORDER_TYPE_TF`

Используется в `OrderCalcProfitRequest` для указания типа ордера.

| Имя константы            | Значение | Описание                             |
| ------------------------ | ----- | ------------------------------------ |
| `ORDER_TYPE_TF_BUY`         | 0     | Рыночный ордер на покупку            |
| `ORDER_TYPE_TF_SELL`        | 1     | Рыночный ордер на продажу            |
| `ORDER_TYPE_TF_BUY_LIMIT`   | 2     | Отложенный ордер buy limit           |
| `ORDER_TYPE_TF_SELL_LIMIT`  | 3     | Отложенный ордер sell limit          |
| `ORDER_TYPE_TF_BUY_STOP`    | 4     | Отложенный ордер buy stop            |
| `ORDER_TYPE_TF_SELL_STOP`   | 5     | Отложенный ордер sell stop           |
| `ORDER_TYPE_TF_BUY_STOP_LIMIT`  | 6 | Отложенный ордер buy stop limit      |
| `ORDER_TYPE_TF_SELL_STOP_LIMIT` | 7 | Отложенный ордер sell stop limit     |
| `ORDER_TYPE_TF_CLOSE_BY`    | 8     | Закрытие встречной позицией          |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

# Доступ к значениям enum
trade_pb2.ORDER_TYPE_TF_BUY          # = 0
trade_pb2.ORDER_TYPE_TF_SELL         # = 1
trade_pb2.ORDER_TYPE_TF_BUY_LIMIT    # = 2
trade_pb2.ORDER_TYPE_TF_SELL_LIMIT   # = 3
```

---


## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных gRPC-ошибок с автоматическим переподключением через `execute_with_reconnect`.
* **Код возврата:** Проверяйте `returned_code == 0` на успех (методы проверки используют 0, а не 10009).
* **Положительное/отрицательное:** Положительная прибыль = выигрыш, отрицательная прибыль = убыток.
* **Валюта счёта:** Результат всегда в валюте счёта (USD, EUR и т. д.).
* **Спред не учитывается:** Этот метод рассчитывает теоретическую прибыль - фактическая прибыль может отличаться из-за спреда и комиссий.
* **Для планирования:** Отлично подходит для расчёта риск/доходность перед входом в сделки.
* **Стоимость пипса:** Используйте для расчёта того, сколько стоит 1 пипс для вашего размера лота.

---

## 🔗 Примеры использования

### 1) Расчёт прибыли для сделки BUY

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_buy_profit():
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
        # Рассчитать прибыль для BUY 0.10 лотов EURUSD
        # Вход: 1.10000, Выход: 1.10100 (прибыль 100 пипсов)
        request = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=1.10000,
            close_price=1.10100
        )

        result = await account.order_calc_profit(request)

        print(f"[PROFIT CALCULATION]")
        print(f"  Entry: 1.10000")
        print(f"  Exit: 1.10100")
        print(f"  Volume: 0.10 lots")
        print(f"  Profit: ${result.profit:.2f}")

    finally:
        await account.channel.close()

asyncio.run(calc_buy_profit())
```

### 2) Расчёт убытка для сделки SELL

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_sell_loss():
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
        # Рассчитать убыток для SELL 0.01 лота EURUSD
        # Вход: 1.10000, Выход: 1.10050 (убыток 50 пипсов)
        request = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_TF_SELL,
            symbol="EURUSD",
            volume=0.01,
            open_price=1.10000,
            close_price=1.10050  # Цена пошла против нас
        )

        result = await account.order_calc_profit(request)

        print(f"[LOSS CALCULATION]")
        print(f"  Entry: 1.10000")
        print(f"  Exit: 1.10050")
        print(f"  Volume: 0.01 lots")
        print(f"  Loss: ${result.profit:.2f}")  # Будет отрицательным

    finally:
        await account.channel.close()

asyncio.run(calc_sell_loss())
```

### 3) Расчёт соотношения риск/доходность

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
        stop_loss = 1.09950  # SL 50 пипсов
        take_profit = 1.10100  # TP 100 пипсов

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

### 4) Расчёт стоимости пипса

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_pip_value():
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
        # Рассчитать стоимость 1 пипса для 0.10 лотов EURUSD
        pip_size = 0.0001

        request = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=1.10000,
            close_price=1.10000 + pip_size  # Движение в 1 пипс
        )

        result = await account.order_calc_profit(request)

        print(f"[PIP VALUE CALCULATION]")
        print(f"  Symbol: EURUSD")
        print(f"  Volume: 0.10 lots")
        print(f"  1 pip = ${result.profit:.2f}")

    finally:
        await account.channel.close()

asyncio.run(calc_pip_value())
```

### 5) Сравнение прибыльности по символам

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def compare_symbols():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbols = [
        ("EURUSD", 1.10000, 1.10100),
        ("GBPUSD", 1.30000, 1.30100),
        ("USDJPY", 150.000, 150.100),
    ]

    try:
        print("[PROFITABILITY COMPARISON]")
        print("Same pip movement (100 pips), same lot size (0.10)")
        print()

        for symbol, entry, exit in symbols:
            request = trade_pb2.OrderCalcProfitRequest(
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                symbol=symbol,
                volume=0.10,
                open_price=entry,
                close_price=exit
            )

            result = await account.order_calc_profit(request)

            print(f"{symbol}: ${result.profit:.2f}")

    finally:
        await account.channel.close()

asyncio.run(compare_symbols())
```

### 6) Определение размера позиции на основе риска

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_position_size():
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
        max_risk = 100.00  # Максимальный риск $100
        entry = 1.10000
        stop_loss = 1.09950  # SL 50 пипсов

        # Протестировать разные размеры лота, чтобы найти подходящий
        for volume in [0.01, 0.05, 0.10, 0.20]:
            request = trade_pb2.OrderCalcProfitRequest(
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                symbol="EURUSD",
                volume=volume,
                open_price=entry,
                close_price=stop_loss
            )

            result = await account.order_calc_profit(request)
            risk = abs(result.profit)

            print(f"Volume: {volume} lots -> Risk: ${risk:.2f}")

            if risk <= max_risk:
                recommended_size = volume
            else:
                break

        print(f"\n[RECOMMENDATION] Use {recommended_size} lots for max ${max_risk} risk")

    finally:
        await account.channel.close()

asyncio.run(calc_position_size())
```

---

## 📚 См. также

* [OrderCalcMargin](./order_calc_margin.md) - Расчёт необходимой маржи
* [OrderCheck](./order_check.md) - Проверка ордера перед отправкой
* [OrderSend](./order_send.md) - Отправка рыночных или отложенных ордеров
* [SymbolInfoTick](../2.%20Symbol_Information/symbol_info_tick.md) - Получить текущие цены
