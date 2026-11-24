# MT5Account - Торговые операции - Обзор

> Исполнение, модификация и управление сделками: отправка ордеров, закрытие позиций, проверка запросов, расчёт маржи.

## 📁 Что здесь находится

### Исполнение ордеров

* **[order_send](./order_send.md)** - отправка рыночных или отложенных ордеров.
* **[order_close](./order_close.md)** - закрытие позиций или удаление отложенных ордеров.
* **[order_modify](./order_modify.md)** - изменение SL/TP, цены или срока действия.

### Проверка и расчёт ордеров

* **[order_check](./order_check.md)** - проверка ордеров перед исполнением.
* **[order_calc_margin](./order_calc_margin.md)** - расчёт необходимой маржи.
* **[order_calc_profit](./order_calc_profit.md)** - расчёт потенциальной прибыли/убытка.

---

## 📚 Пошаговые руководства

**Примечание:** Все торговые операции являются async-методами. Подробные примеры смотрите на страницах отдельных методов.

* **[order_send](../HOW_IT_WORK/5. Trading_Operations_HOW/order_send_HOW.md)** - Примеры исполнения ордеров
* **[order_close](../HOW_IT_WORK/5. Trading_Operations_HOW/order_close_HOW.md)** - Шаблоны закрытия позиций
* **[order_modify](../HOW_IT_WORK/5. Trading_Operations_HOW/order_modify_HOW.md)** - Примеры изменения SL/TP
* **[order_check](../HOW_IT_WORK/5. Trading_Operations_HOW/order_check_HOW.md)** - Шаблоны проверки ордеров
* **[order_calc_margin](../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_margin_HOW.md)** - Примеры расчёта маржи
* **[order_calc_profit](../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_profit_HOW.md)** - Примеры расчёта прибыли/убытка

---

## 🧭 Простыми словами

* **order_send** -> **открыть позиции** или разместить отложенные ордера (BUY, SELL, LIMIT, STOP).
* **order_close** -> **закрыть позиции** полностью или частично, либо удалить отложенные ордера.
* **order_modify** -> **изменить SL/TP** или параметры отложенного ордера.
* **order_check** -> **проверить ордера** перед отправкой (проверка маржи, параметров).
* **order_calc_margin** -> **рассчитать маржу**, необходимую для планируемых сделок.
* **order_calc_profit** -> **рассчитать прибыль/убыток** для планируемых сделок (анализ риск/доходность).

> Эмпирическое правило: **открыть** -> `order_send`; **закрыть** -> `order_close`; **скорректировать** -> `order_modify`; **проверить** -> `order_check`; **спланировать маржу** -> `order_calc_margin`; **спланировать прибыль** -> `order_calc_profit`.

---

## Быстрый выбор

| Если вам нужно...                                | Используйте         | Возвращает                 | Ключевые входные данные             |
| ------------------------------------------------ | ------------------- | -------------------------- | ----------------------------------- |
| Открыть рыночную позицию (BUY/SELL)              | `order_send`        | OrderSendData              | symbol, operation, volume, price    |
| Разместить отложенный ордер (LIMIT/STOP)         | `order_send`        | OrderSendData              | symbol, operation, volume, price    |
| Закрыть позицию полностью                        | `order_close`       | OrderCloseData             | ticket, volume=0, slippage          |
| Закрыть позицию частично                         | `order_close`       | OrderCloseData             | ticket, volume, slippage            |
| Удалить отложенный ордер                         | `order_close`       | OrderCloseData             | ticket, volume=0                    |
| Добавить/изменить Stop Loss или Take Profit      | `order_modify`      | OrderModifyData            | ticket, stop_loss, take_profit      |
| Изменить цену отложенного ордера                 | `order_modify`      | OrderModifyData            | ticket, price                       |
| Проверить ордер перед отправкой                  | `order_check`       | OrderCheckData             | OrderSendRequest                    |
| Рассчитать маржу для планируемой сделки          | `order_calc_margin` | OrderCalcMarginData        | symbol, operation, volume           |
| Рассчитать прибыль/убыток для планируемой сделки | `order_calc_profit` | OrderCalcProfitData        | symbol, operation, volume, open/close price |

---

## ℹ️ Перекрёстные ссылки и подводные камни

* **Коды возврата:** Всегда проверяйте `returned_code == 10009` на успех (order_send/close), `== 0` для методов проверки.
* **Async-методы:** Все торговые операции асинхронны - используйте `await`.
* **Автоматическое переподключение:** У всех методов есть встроенное переподключение через `execute_with_reconnect`.
* **Volume = 0:** В `order_close` volume=0 означает закрытие всей позиции.
* **Проскальзывание:** Задавайте подходящее проскальзывание для рыночных ордеров (например, 20 пунктов).
* **SL/TP = 0:** В `order_modify` используйте 0 для удаления SL или TP.
* **Проверка перед отправкой:** Всегда используйте `order_check` перед `order_send` для крупных ордеров.
* **Расчёт маржи:** `order_check` включает маржу, `order_calc_margin` только рассчитывает маржу.
* **Расчёт прибыли:** `order_calc_profit` рассчитывает потенциальную прибыль/убыток для анализа риск/доходность.
* **Уровень заморозки (freeze level):** Нельзя изменять ордера слишком близко к рыночной цене (настройка брокера).
* **Минимальная дистанция:** Брокер требует минимальную дистанцию от текущей цены для SL/TP.

---

## 🟢 Минимальные сниппеты

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Отправить рыночный ордер BUY
async def market_buy():
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
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=0,  # 0 = BUY
            volume=0.01,
            price=0,
            slippage=20,
            comment="Market BUY"
        )

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Deal: #{result.deal}, Price: {result.price}")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(market_buy())
```

```python
# Закрыть позицию
async def close_position(ticket):
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
        request = trading_pb2.OrderCloseRequest(
            ticket=ticket,
            volume=0,  # Закрыть всё
            slippage=20
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Position closed")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(close_position(123456))
```

```python
# Изменить Stop Loss
async def modify_sl(ticket, new_sl):
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
        request = trading_pb2.OrderModifyRequest(
            ticket=ticket,
            stop_loss=new_sl,
            take_profit=0,  # Оставить текущий
            price=0
        )

        result = await account.order_modify(request)
        print(f"[SUCCESS] SL modified to {new_sl}")

    finally:
        await account.channel.close()

asyncio.run(modify_sl(123456, 1.08500))
```

```python
# Проверить ордер перед отправкой
async def check_and_send():
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
        import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

        # Создать торговый запрос
        trade_request = trade_pb2.MrpcMqlTradeRequest(
            action=0,  # TRADE_ACTION_DEAL
            symbol="EURUSD",
            volume=0.10,
            order_type=0,  # ORDER_TYPE_BUY
            type_filling=2,  # ORDER_FILLING_RETURN
            type_time=0  # ORDER_TIME_GTC
        )

        check_req = trade_pb2.OrderCheckRequest(mql_trade_request=trade_request)

        # Сначала проверить
        check_result = await account.order_check(check_req)

        if check_result.returned_code == 0:
            print(f"[VALID] Margin: ${check_result.margin:.2f}")

            # Отправить ордер
            send_request = trading_pb2.OrderSendRequest(
                symbol="EURUSD",
                operation=0,
                volume=0.10,
                price=0,
                slippage=20
            )

            send_result = await account.order_send(send_request)

            if send_result.returned_code == 10009:
                print(f"[SUCCESS] Deal: #{send_result.deal}")
        else:
            print(f"[INVALID] {check_result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(check_and_send())
```

```python
# Рассчитать маржу
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
        import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

        request = trade_pb2.OrderCalcMarginRequest(
            symbol="EURUSD",
            order_type=0,  # ORDER_TYPE_BUY
            volume=0.10,
            open_price=1.10000
        )

        result = await account.order_calc_margin(request)

        if result.returned_code == 0:
            print(f"Required margin: ${result.margin:,.2f}")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(calc_margin())
```

```python
# Полный торговый рабочий процесс
async def trading_workflow():
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
        import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

        # 1. Рассчитать маржу
        margin_req = trade_pb2.OrderCalcMarginRequest(
            symbol="EURUSD",
            order_type=0,
            volume=0.10,
            open_price=1.10000
        )

        margin_result = await account.order_calc_margin(margin_req)
        print(f"[1] Margin: ${margin_result.margin:.2f}")

        # 2. Проверить ордер
        trade_request = trade_pb2.MrpcMqlTradeRequest(
            action=0,
            symbol="EURUSD",
            volume=0.10,
            order_type=0,
            type_filling=2,
            type_time=0
        )

        check_req = trade_pb2.OrderCheckRequest(mql_trade_request=trade_request)
        check_result = await account.order_check(check_req)
        if check_result.returned_code != 0:
            print(f"[2] Check failed: {check_result.returned_code_description}")
            return

        print(f"[2] Order valid, free margin after: ${check_result.margin_free:.2f}")

        # 3. Отправить ордер
        send_req = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=0,
            volume=0.10,
            price=0,
            slippage=20
        )

        send_result = await account.order_send(send_req)
        if send_result.returned_code != 10009:
            print(f"[3] Send failed: {send_result.returned_code_description}")
            return

        print(f"[3] Order sent! Deal: #{send_result.deal}")
        ticket = send_result.deal

        # 4. Изменить, чтобы добавить SL/TP
        await asyncio.sleep(1)  # Подождать немного

        import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick = await account.symbol_info_tick(tick_req)

        pip_size = 0.0001
        sl = tick.tick.bid - (50 * pip_size)
        tp = tick.tick.bid + (100 * pip_size)

        modify_req = trading_pb2.OrderModifyRequest(
            ticket=ticket,
            stop_loss=sl,
            take_profit=tp,
            price=0
        )

        await account.order_modify(modify_req)
        print(f"[4] SL/TP added: SL={sl:.5f}, TP={tp:.5f}")

        # 5. Позже... закрыть позицию
        await asyncio.sleep(5)

        close_req = trading_pb2.OrderCloseRequest(
            ticket=ticket,
            volume=0,
            slippage=20
        )

        close_result = await account.order_close(close_req)
        if close_result.returned_code == 10009:
            print(f"[5] Position closed")

    finally:
        await account.channel.close()

asyncio.run(trading_workflow())
```

```python
# Пакетные операции
async def batch_operations():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbols = ["EURUSD", "GBPUSD", "USDJPY"]

    try:
        # Открыть несколько позиций
        deals = []

        for symbol in symbols:
            request = trading_pb2.OrderSendRequest(
                symbol=symbol,
                operation=0,
                volume=0.01,
                price=0,
                slippage=20,
                comment=f"{symbol} position"
            )

            result = await account.order_send(request)

            if result.returned_code == 10009:
                deals.append(result.deal)
                print(f"[OPENED] {symbol}: #{result.deal}")

        # Подождать...
        await asyncio.sleep(10)

        # Закрыть все позиции
        for deal in deals:
            close_req = trading_pb2.OrderCloseRequest(
                ticket=deal,
                volume=0,
                slippage=20
            )

            result = await account.order_close(close_req)

            if result.returned_code == 10009:
                print(f"[CLOSED] #{deal}")

    finally:
        await account.channel.close()

asyncio.run(batch_operations())
```

---

## 📚 См. также

* **Позиции:** [opened_orders](../3.%20Positions_Orders/opened_orders.md) - получить текущие позиции
* **История:** [order_history](../3.%20Positions_Orders/order_history.md) - получить историю ордеров
* **Счёт:** [account_summary](../1.%20Account_Information/account_summary.md) - получить состояние счёта
* **Цены:** [symbol_info_tick](../2.%20Symbol_Information/symbol_info_tick.md) - получить текущие цены
