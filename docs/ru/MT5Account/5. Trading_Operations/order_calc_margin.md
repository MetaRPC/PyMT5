# Расчёт необходимой маржи

> **Запрос:** Рассчитать маржу, необходимую для планируемой торговой операции.

**Информация об API:**

* **Python API:** `MT5Account.order_calc_margin(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.TradeFunctions`
* **Proto-определение:** `OrderCalcMargin` (определено в `mt5-term-api-trade-functions.proto`)
* **Enum'ы в этом методе:** 1 enum с 9 константами (1 вход)

### RPC

* **Сервис:** `mt5_term_api.TradeFunctions`
* **Метод:** `OrderCalcMargin(OrderCalcMarginRequest) -> OrderCalcMarginReply`
* **Низкоуровневый клиент (сгенерированный):** `TradeFunctionsStub.OrderCalcMargin(request, metadata)`

---

## 💬 Только самое главное

* **Что это.** Рассчитывает необходимую маржу для сделки без её исполнения.
* **Зачем это нужно.** Планирование размера позиции и управление рисками.
* **Валюта счёта.** Возвращает маржу в валюте вашего счёта (USD, EUR и т. д.).

---

## 🎯 Назначение

Используйте для того, чтобы:

* Рассчитать требования к марже перед торговлей
* Определить максимальный размер позиции для доступной маржи
* Спланировать несколько позиций
* Выполнить расчёты для управления рисками
* Анализировать маржу портфеля
* Сравнить требования к марже по разным символам

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[OrderCalcMargin - Как это работает](../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_margin_HOW.md)**


```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

class MT5Account:
    # ...

    async def order_calc_margin(
        self,
        request: trade_pb2.OrderCalcMarginRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trade_pb2.OrderCalcMarginData:
        """
        Calculates the margin required for a planned trade operation.

        Returns:
            OrderCalcMarginData: The required margin in account currency.
        """
```

**Сообщение запроса:**

```protobuf
message OrderCalcMarginRequest {
  string symbol = 1;            // Имя символа
  ENUM_ORDER_TYPE_TF order_type = 2;  // Тип ордера
  double volume = 3;            // Объём сделки в лотах
  double open_price = 4;        // Цена открытия ордера
}
```

---

## 🔽 Вход

| Параметр             | Тип                            | Описание                                      |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `request`            | `OrderCalcMarginRequest`       | Запрос на расчёт маржи                         |
| `deadline`           | `Optional[datetime]`           | Крайний срок операции (опционально)           |
| `cancellation_event` | `Optional[asyncio.Event]`      | Событие для отмены запроса (опционально)       |

**Поля OrderCalcMarginRequest:**

| Поле         | Тип                     | Описание                             |
| ------------ | ----------------------- | ------------------------------------ |
| `symbol`     | `string`                | Имя символа (например, "EURUSD")     |
| `order_type` | `ENUM_ORDER_TYPE_TF`    | Тип ордера (enum)                    |
| `volume`     | `double`                | Объём сделки в лотах                 |
| `open_price` | `double`                | Цена открытия ордера                 |

---

## ⬆️ Выход

Возвращает объект `OrderCalcMarginData` с результатом расчёта маржи.

**Поля OrderCalcMarginData:**

| Поле     | Тип      | Описание                             |
| -------- | -------- | ------------------------------------ |
| `margin` | `double` | Необходимая маржа в валюте счёта     |

---

## 🧱 Связанные enum'ы (из proto)

### `ENUM_ORDER_TYPE_TF`

Используется в `OrderCalcMarginRequest` для указания типа ордера при расчёте маржи.

| Имя константы                 | Значение | Описание                             |
| ----------------------------- | ----- | ------------------------------------ |
| `ORDER_TYPE_TF_BUY`           | 0     | Рыночный ордер на покупку            |
| `ORDER_TYPE_TF_SELL`          | 1     | Рыночный ордер на продажу            |
| `ORDER_TYPE_TF_BUY_LIMIT`     | 2     | Отложенный ордер buy limit           |
| `ORDER_TYPE_TF_SELL_LIMIT`    | 3     | Отложенный ордер sell limit          |
| `ORDER_TYPE_TF_BUY_STOP`      | 4     | Отложенный ордер buy stop            |
| `ORDER_TYPE_TF_SELL_STOP`     | 5     | Отложенный ордер sell stop           |
| `ORDER_TYPE_TF_BUY_STOP_LIMIT`| 6     | Отложенный ордер buy stop limit      |
| `ORDER_TYPE_TF_SELL_STOP_LIMIT`|7    | Отложенный ордер sell stop limit     |
| `ORDER_TYPE_TF_CLOSE_BY`      | 8     | Закрытие встречной позицией          |

**Использование:**
```python
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as trade_pb2

# Доступ к значениям enum
trade_pb2.ORDER_TYPE_TF_BUY         # = 0
trade_pb2.ORDER_TYPE_TF_SELL        # = 1
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных gRPC-ошибок с автоматическим переподключением через `execute_with_reconnect`.
* **Без исполнения:** Этот метод только рассчитывает маржу, НЕ исполняет ордера.
* **Тот же запрос:** Использует такую же структуру запроса, что и `order_send`.
* **Влияние плеча:** Результат зависит от кредитного плеча символа и настроек счёта.
* **Расчёт в реальном времени:** Для расчёта используются текущие рыночные цены.
* **Отличие от order_check:** Этот метод возвращает только маржу, `order_check` проверяет весь ордер.

---

## 🔗 Примеры использования

### 1) Расчёт маржи для одной сделки

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def calc_margin():
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
        # Рассчитать маржу для 0.10 лотов EURUSD
        request = trade_pb2.OrderCalcMarginRequest(
            symbol="EURUSD",
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            volume=0.10,
            open_price=1.0850
        )

        result = await account.order_calc_margin(request)

        print(f"[SUCCESS] Margin calculation:")
        print(f"  Symbol: EURUSD")
        print(f"  Volume: 0.10 lots")
        print(f"  Required margin: ${result.margin:,.2f}")

    finally:
        await account.channel.close()

asyncio.run(calc_margin())
```

### 2) Сравнение маржи по символам

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

async def compare_margin():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
    volume = 0.10

    try:
        print(f"Margin requirements for {volume} lots:\n")
        print(f"{'Symbol':<10} {'Margin':<15}")
        print("-" * 30)

        for symbol in symbols:
            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)
            print(f"{symbol:<10} ${result.margin:>12,.2f}")

    finally:
        await account.channel.close()

asyncio.run(compare_margin())
```

### 3) Расчёт максимального размера позиции

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def calc_max_position(symbol: str, margin_percent: float = 50.0):
    """Calculate max position size using X% of free margin"""
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
        # Получить доступную маржу
        summary_req = account_pb2.AccountSummaryRequest()
        summary = await account.account_summary(summary_req)
        available_margin = summary.margin_free * (margin_percent / 100.0)

        print(f"Calculating max position for {symbol}:")
        print(f"  Free margin: ${summary.margin_free:,.2f}")
        print(f"  Using {margin_percent}% = ${available_margin:,.2f}\n")

        # Бинарный поиск максимального объёма
        min_vol = 0.01
        max_vol = 100.0
        best_volume = 0.01

        while max_vol - min_vol > 0.01:
            test_volume = (min_vol + max_vol) / 2

            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=test_volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)

            if result.margin <= available_margin:
                best_volume = test_volume
                min_vol = test_volume
            else:
                max_vol = test_volume

        print(f"[RESULT] Maximum position size: {best_volume:.2f} lots")

        # Проверить итоговый расчёт
        final_req = trade_pb2.OrderCalcMarginRequest(
            symbol=symbol,
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            volume=best_volume,
            open_price=1.0
        )
        final_result = await account.order_calc_margin(final_req)

        print(f"  Required margin: ${final_result.margin:,.2f}")
        print(f"  Margin usage: {(final_result.margin / available_margin * 100):.1f}%")

    finally:
        await account.channel.close()

asyncio.run(calc_max_position("EURUSD", margin_percent=50.0))
```

### 4) Расчёт маржи портфеля

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def portfolio_margin():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Планируемый портфель
    trades = [
        ("EURUSD", 0.10),
        ("GBPUSD", 0.05),
        ("USDJPY", 0.10),
        ("XAUUSD", 0.01),
    ]

    try:
        # Получить текущее состояние счёта
        summary_req = account_pb2.AccountSummaryRequest()
        summary = await account.account_summary(summary_req)

        print(f"Portfolio Margin Analysis\n")
        print(f"Current state:")
        print(f"  Balance: ${summary.balance:,.2f}")
        print(f"  Free margin: ${summary.margin_free:,.2f}\n")

        print(f"Planned trades:")
        print(f"{'Symbol':<10} {'Volume':<10} {'Margin':<15}")
        print("-" * 40)

        total_margin = 0.0

        for symbol, volume in trades:
            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)

            print(f"{symbol:<10} {volume:<10.2f} ${result.margin:>12,.2f}")
            total_margin += result.margin

        print("-" * 40)
        print(f"{'TOTAL':<10} {'':<10} ${total_margin:>12,.2f}\n")

        # Проверить, помещается ли портфель
        if total_margin <= summary.margin_free:
            remaining = summary.margin_free - total_margin
            usage_percent = (total_margin / summary.margin_free) * 100
            print(f"[OK] Portfolio fits!")
            print(f"  Margin usage: {usage_percent:.1f}%")
            print(f"  Remaining free margin: ${remaining:,.2f}")
        else:
            shortage = total_margin - summary.margin_free
            print(f"[WARNING] Insufficient margin!")
            print(f"  Required: ${total_margin:,.2f}")
            print(f"  Available: ${summary.margin_free:,.2f}")
            print(f"  Shortage: ${shortage:,.2f}")

    finally:
        await account.channel.close()

asyncio.run(portfolio_margin())
```

### 5) Расчёт размера позиции на основе риска

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def risk_based_sizing(symbol: str, risk_percent: float = 2.0):
    """Calculate position size based on risk percentage"""
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
        # Получить баланс счёта
        summary_req = account_pb2.AccountSummaryRequest()
        summary = await account.account_summary(summary_req)

        max_risk_amount = summary.balance * (risk_percent / 100.0)

        print(f"Risk-based position sizing for {symbol}:")
        print(f"  Account balance: ${summary.balance:,.2f}")
        print(f"  Risk: {risk_percent}% = ${max_risk_amount:,.2f}\n")

        # Протестировать разные объёмы
        volumes = [0.01, 0.05, 0.10, 0.20, 0.50, 1.00]

        print(f"{'Volume':<10} {'Margin':<15} {'% of Balance':<15}")
        print("-" * 45)

        for volume in volumes:
            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)

            margin_percent = (result.margin / summary.balance) * 100

            status = "[OK]" if margin_percent <= risk_percent else "[OVER]"

            print(f"{volume:<10.2f} ${result.margin:>12,.2f} {margin_percent:>13.2f}% {status}")

    finally:
        await account.channel.close()

asyncio.run(risk_based_sizing("EURUSD", risk_percent=2.0))
```

### 6) Вспомогательный класс-калькулятор маржи

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

class MarginCalculator:
    def __init__(self, account):
        self.account = account
        self.cache = {}  # Кэш расчётов

    async def get_margin(self, symbol: str, volume: float, order_type: int = 0):
        """Get margin with caching"""
        cache_key = f"{symbol}_{volume}_{order_type}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        request = trade_pb2.OrderCalcMarginRequest(
            symbol=symbol,
            order_type=order_type,
            volume=volume,
            open_price=1.0
        )

        result = await self.account.order_calc_margin(request)

        self.cache[cache_key] = result.margin
        return result.margin

    async def get_leverage_ratio(self, symbol: str, volume: float = 1.0):
        """Calculate effective leverage for symbol"""
        import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

        # Получить размер контракта
        tick_req = market_pb2.SymbolInfoTickRequest(symbol=symbol)
        tick_data = await self.account.symbol_info_tick(tick_req)

        # Рассчитать маржу для 1 лота
        margin = await self.get_margin(symbol, volume)

        # Стоимость контракта = цена * размер контракта
        contract_value = tick_data.tick.ask * 100000  # Предполагается контракт в 100k

        leverage = contract_value / margin if margin > 0 else 0

        return leverage

async def main():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    calc = MarginCalculator(account)

    try:
        # Рассчитать маржу
        margin = await calc.get_margin("EURUSD", 0.10)
        print(f"Margin for 0.10 lots EURUSD: ${margin:,.2f}")

        # Рассчитать плечо
        leverage = await calc.get_leverage_ratio("EURUSD", 1.0)
        print(f"Effective leverage: 1:{leverage:.0f}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

---

## 📚 См. также

* [OrderCheck](./order_check.md) - Полная проверка ордера (включает маржу)
* [OrderCalcProfit](./order_calc_profit.md) - Расчёт потенциальной прибыли/убытка
* [OrderSend](./order_send.md) - Исполнение ордеров
* [AccountSummary](../1.%20Account_Information/account_summary.md) - Получить информацию о марже счёта
