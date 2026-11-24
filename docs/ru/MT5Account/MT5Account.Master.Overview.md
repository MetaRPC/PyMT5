# MT5Account - Главный обзор

> Одна страница, чтобы **быстро сориентироваться**: что где находится, как выбрать нужный API, и ссылки для перехода на каждый **обзор** и **спецификацию метода** в этом наборе документации.

---

## 🚦 Начните здесь - Обзоры разделов

* **[1. Account Information - Обзор](./1.%20Account_Information/Account_Information.Overview.md)**
  Баланс/средства (equity)/маржа/кредитное плечо счёта, полный снимок или отдельные свойства.

* **[2. Symbol Information - Обзор](./2.%20Symbol_Information/Symbol_Information.Overview.md)**
  Котировки, свойства символов, торговые правила, управление Market Watch.

* **[3. Positions & Orders - Обзор](./3.%20Positions_Orders/Positions_Orders.Overview.md)**
  Открытые позиции, отложенные ордера, исторические сделки, история ордеров.

* **[4. Market Depth (DOM) - Обзор](./4.%20Market_Depth/Market_Depth.Overview.md)**
  Котировки Level II, данные стакана ордеров, подписка на глубину рынка.

* **[5. Trading Operations - Обзор](./5.%20Trading_Operations/Trading_Operations.Overview.md)**
  Исполнение ордеров, управление позициями, расчёты маржи, проверка торговых запросов.

* **[6. Streaming Methods - Обзор](./6.%20Streaming_Methods/Streaming_Methods.Overview.md)**
  Потоки в реальном времени: тики, сделки, обновления прибыли, журнал транзакций.

---

## 🧭 Как выбрать API

| Если вам нужно...                | Перейдите к...                | Типичные методы                                                              |
| -------------------------------- | ----------------------------- | ---------------------------------------------------------------------------- |
| Снимок счёта                     | Account Information           | `account_summary()`, `account_info_double()`, `account_info_integer()`       |
| Котировки и свойства символов    | Symbol Information            | `symbol_info_tick()`, `symbol_info_double()`, `symbols_total()`              |
| Текущие позиции и ордера         | Positions & Orders            | `positions_total()`, `opened_orders()`, `opened_orders_tickets()`            |
| Исторические сделки              | Positions & Orders            | `order_history()`, `positions_history()`                                     |
| Значения тика для расчёта P/L    | Positions & Orders            | `tick_value_with_size()`                                                     |
| Level II / Стакан ордеров        | Market Depth (DOM)            | `market_book_add()`, `market_book_get()`, `market_book_release()`            |
| Торговые операции                | Trading Operations            | `order_send()`, `order_modify()`, `order_close()`                            |
| Предторговые расчёты             | Trading Operations            | `order_calc_margin()`, `order_check()`                                       |
| Обновления в реальном времени    | Streaming Methods             | `on_symbol_tick()`, `on_trade()`, `on_position_profit()`                     |

---

## 🔌  Шаблон использования (Python async/await)

Каждый метод следует асинхронному шаблону с gRPC «под капотом»:

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def main():
    # Создаём экземпляр MT5Account через create() - РЕКОМЕНДУЕТСЯ
    account = MT5Account.create(
        user=591129415,
        password="IpoHj17tYu67@",
        grpc_server="mt5.mrpc.pro:443"
    )

    # Подключаемся к терминалу MT5
    await account.connect_by_server_name(
        server_name="FxPro-MT5 Demo",
        base_chart_symbol="EURUSD",
        timeout_seconds=120
    )

    try:
        # Вызываем асинхронный метод - используем account_summary() (РЕКОМЕНДУЕТСЯ)
        summary = await account.account_summary()
        print(f"Balance: ${summary.account_balance:.2f}")
        print(f"Equity:  ${summary.account_equity:.2f}")

    finally:
        # Всегда закрываем соединение
        await account.channel.close()

asyncio.run(main())
```

---

Каждый метод имеет одинаковую структуру:

* **Async/Await:** Все методы являются `async` - используйте `await` для их вызова
* **Автоматическое переподключение:** Встроенная обёртка `execute_with_reconnect` для устойчивости
* **Protobuf-сообщения:** Запрос/Ответ используют структуры protobuf «под капотом»
* **Коды возврата:** Торговые операции возвращают коды статуса (10009 = успех)
* **Стриминговые методы:** Используйте `async for` для получения потоков данных в реальном времени

**Временные метки:** Unix-метки времени (секунды с эпохи) или объекты `datetime`.

**Стриминговые методы:** Возвращают асинхронные генераторы - используйте цикл `async for` для получения обновлений.

---

# 📚 Полный указатель - Все спецификации методов

---

## 📄 1. Account Information

* **Обзор:** [Account_Information.Overview.md](./1.%20Account_Information/Account_Information.Overview.md)

### Полный снимок

* [account_summary.md](./1.%20Account_Information/account_summary.md) - Вся информация о счёте сразу (баланс, средства, маржа и т.д.)

### Отдельные свойства

* [account_info_double.md](./1.%20Account_Information/account_info_double.md) - Одно значение double (баланс, средства, маржа, прибыль и т.д.)
* [account_info_integer.md](./1.%20Account_Information/account_info_integer.md) - Одно целочисленное значение (логин, кредитное плечо, лимит ордеров и т.д.)
* [account_info_string.md](./1.%20Account_Information/account_info_string.md) - Одно строковое значение (имя, сервер, валюта, компания)

---

## 📊 2. Symbol Information

* **Обзор:** [Symbol_Information.Overview.md](./2.%20Symbol_Information/Symbol_Information.Overview.md)

### Управление символами

* [symbols_total.md](./2.%20Symbol_Information/symbols_total.md) - Количество доступных символов
* [symbol_exist.md](./2.%20Symbol_Information/symbol_exist.md) - Проверка существования символа на платформе
* [symbol_name.md](./2.%20Symbol_Information/symbol_name.md) - Получение имени символа по индексу позиции
* [symbol_select.md](./2.%20Symbol_Information/symbol_select.md) - Добавление/удаление символа из Market Watch
* [symbol_is_synchronized.md](./2.%20Symbol_Information/symbol_is_synchronized.md) - Проверка синхронизации данных символа

### Свойства символа

* [symbol_info_double.md](./2.%20Symbol_Information/symbol_info_double.md) - Одно свойство double (BID, ASK, POINT и т.д.)
* [symbol_info_integer.md](./2.%20Symbol_Information/symbol_info_integer.md) - Одно целочисленное свойство (DIGITS, SPREAD и т.д.)
* [symbol_info_string.md](./2.%20Symbol_Information/symbol_info_string.md) - Одно строковое свойство (DESCRIPTION, CURRENCY_BASE и т.д.)
* [symbol_info_tick.md](./2.%20Symbol_Information/symbol_info_tick.md) - Текущие данные тика (BID, ASK, объём, время)
* [symbol_params_many.md](./2.%20Symbol_Information/symbol_params_many.md) - Все параметры символа сразу (РЕКОМЕНДУЕТСЯ)

### Торговые условия

* [symbol_info_margin_rate.md](./2.%20Symbol_Information/symbol_info_margin_rate.md) - Ставки маржи для символа и типа ордера
* [symbol_info_session_quote.md](./2.%20Symbol_Information/symbol_info_session_quote.md) - Время котировочных сессий для дня недели
* [symbol_info_session_trade.md](./2.%20Symbol_Information/symbol_info_session_trade.md) - Время торговых сессий для дня недели

---

## 📦 3. Positions & Orders

* **Обзор:** [Positions_Orders.Overview.md](./3.%20Positions_Orders/Positions_Orders.Overview.md)

### Текущие позиции и ордера

* [positions_total.md](./3.%20Positions_Orders/positions_total.md) - Количество открытых позиций (облегчённый вызов)
* [opened_orders.md](./3.%20Positions_Orders/opened_orders.md) - Полные сведения обо всех открытых ордерах/позициях
* [opened_orders_tickets.md](./3.%20Positions_Orders/opened_orders_tickets.md) - Только ID тикетов (более лёгкий ответ)

### Исторические данные

* [order_history.md](./3.%20Positions_Orders/order_history.md) - Исторические ордера/сделки за временной диапазон
* [positions_history.md](./3.%20Positions_Orders/positions_history.md) - Исторические закрытые позиции

### Расчёты

* [tick_value_with_size.md](./3.%20Positions_Orders/tick_value_with_size.md) - Значения тика и размеры контрактов для расчёта P/L

---

## 📈 4. Market Depth (DOM)

* **Обзор:** [Market_Depth.Overview.md](./4.%20Market_Depth/Market_Depth.Overview.md)

### Котировки Level II

* [market_book_add.md](./4.%20Market_Depth/market_book_add.md) - Подписка на глубину рынка по символу
* [market_book_get.md](./4.%20Market_Depth/market_book_get.md) - Получение текущих данных стакана ордеров
* [market_book_release.md](./4.%20Market_Depth/market_book_release.md) - Отписка от глубины рынка

---

## 🛠 5. Trading Operations

* **Обзор:** [Trading_Operations.Overview.md](./5.%20Trading_Operations/Trading_Operations.Overview.md)

### Исполнение и управление ордерами

* [order_send.md](./5.%20Trading_Operations/order_send.md) - Размещение рыночных или отложенных ордеров
* [order_modify.md](./5.%20Trading_Operations/order_modify.md) - Изменение SL/TP или параметров ордера
* [order_close.md](./5.%20Trading_Operations/order_close.md) - Закрытие позиций (полное или частичное)

### Предторговые расчёты

* [order_calc_margin.md](./5.%20Trading_Operations/order_calc_margin.md) - Расчёт маржи, необходимой для сделки
* [order_check.md](./5.%20Trading_Operations/order_check.md) - Проверка торгового запроса перед исполнением

---

## 📡 6. Streaming Methods

* **Обзор:** [Streaming_Methods.Overview.md](./6.%20Streaming_Methods/Streaming_Methods.Overview.md)

### Обновления цен в реальном времени

* [on_symbol_tick.md](./6.%20Streaming_Methods/on_symbol_tick.md) - Поток тиков в реальном времени для символов

### Торговые события

* [on_trade.md](./6.%20Streaming_Methods/on_trade.md) - Изменения позиций/ордеров (открытие, закрытие, модификация)
* [on_trade_transaction.md](./6.%20Streaming_Methods/on_trade_transaction.md) - Подробный журнал транзакций (полный аудиторский след)

### Мониторинг позиций

* [on_position_profit.md](./6.%20Streaming_Methods/on_position_profit.md) - Периодические обновления прибыли/убытка
* [on_positions_and_pending_orders_tickets.md](./6.%20Streaming_Methods/on_positions_and_pending_orders_tickets.md) - Периодические списки тикетов (облегчённо)

---

## 🎯 Быстрая навигация по сценариям

| Я хочу...                             | Используйте этот метод                                                       |
| ------------------------------------- | ---------------------------------------------------------------------------- |
| **ИНФОРМАЦИЯ О СЧЁТЕ**                |                                                                              |
| Получить полный снимок счёта          | [account_summary](./1.%20Account_Information/account_summary.md)             |
| Получить баланс счёта                 | [account_info_double](./1.%20Account_Information/account_info_double.md) (BALANCE) |
| Получить средства (equity) счёта      | [account_info_double](./1.%20Account_Information/account_info_double.md) (EQUITY) |
| Получить кредитное плечо счёта        | [account_info_integer](./1.%20Account_Information/account_info_integer.md) (LEVERAGE) |
| Получить валюту счёта                 | [account_info_string](./1.%20Account_Information/account_info_string.md) (CURRENCY) |
| **ПОЗИЦИИ И ОРДЕРА**                  |                                                                              |
| Получить количество открытых позиций  | [positions_total](./3.%20Positions_Orders/positions_total.md)                |
| Получить все открытые ордера/позиции  | [opened_orders](./3.%20Positions_Orders/opened_orders.md)                    |
| Получить только ID тикетов            | [opened_orders_tickets](./3.%20Positions_Orders/opened_orders_tickets.md)    |
| Получить историю ордеров              | [order_history](./3.%20Positions_Orders/order_history.md)                    |
| Получить историю закрытых позиций     | [positions_history](./3.%20Positions_Orders/positions_history.md)            |
| Получить значения тика для расчёта P/L | [tick_value_with_size](./3.%20Positions_Orders/tick_value_with_size.md)      |
| **ГЛУБИНА РЫНКА**                     |                                                                              |
| Подписаться на котировки Level II     | [market_book_add](./4.%20Market_Depth/market_book_add.md)                    |
| Получить данные стакана ордеров       | [market_book_get](./4.%20Market_Depth/market_book_get.md)                    |
| Отписаться от Level II                | [market_book_release](./4.%20Market_Depth/market_book_release.md)            |
| **ТОРГОВЫЕ ОПЕРАЦИИ**                 |                                                                              |
| Открыть рыночную позицию BUY          | [order_send](./5.%20Trading_Operations/order_send.md) (operation=0)          |
| Открыть рыночную позицию SELL         | [order_send](./5.%20Trading_Operations/order_send.md) (operation=1)          |
| Разместить ордер BUY LIMIT            | [order_send](./5.%20Trading_Operations/order_send.md) (operation=2)          |
| Разместить ордер SELL LIMIT           | [order_send](./5.%20Trading_Operations/order_send.md) (operation=3)          |
| Разместить ордер BUY STOP             | [order_send](./5.%20Trading_Operations/order_send.md) (operation=4)          |
| Разместить ордер SELL STOP            | [order_send](./5.%20Trading_Operations/order_send.md) (operation=5)          |
| Изменить SL/TP позиции                | [order_modify](./5.%20Trading_Operations/order_modify.md)                    |
| Закрыть позицию                       | [order_close](./5.%20Trading_Operations/order_close.md)                      |
| Рассчитать маржу перед сделкой        | [order_calc_margin](./5.%20Trading_Operations/order_calc_margin.md)          |
| Проверить сделку перед исполнением    | [order_check](./5.%20Trading_Operations/order_check.md)                      |
| **ПОДПИСКИ В РЕАЛЬНОМ ВРЕМЕНИ**       |                                                                              |
| Стримить живые цены                   | [on_symbol_tick](./6.%20Streaming_Methods/on_symbol_tick.md)                 |
| Отслеживать торговые события          | [on_trade](./6.%20Streaming_Methods/on_trade.md)                             |
| Отслеживать изменения прибыли         | [on_position_profit](./6.%20Streaming_Methods/on_position_profit.md)         |
| Отслеживать изменения тикетов         | [on_positions_and_pending_orders_tickets](./6.%20Streaming_Methods/on_positions_and_pending_orders_tickets.md) |
| Подробный журнал транзакций           | [on_trade_transaction](./6.%20Streaming_Methods/on_trade_transaction.md)     |

---

## 💡 Ключевые понятия

### Коды возврата (торговые операции)

* **10009** = Успех / DONE
* **10004** = Requote
* **10006** = Запрос отклонён
* **10013** = Некорректный запрос
* **10014** = Некорректный объём
* **10015** = Некорректная цена
* **10016** = Некорректные стопы
* **10018** = Рынок закрыт
* **10019** = Недостаточно средств
* **10031** = Нет связи с торговым сервером

Всегда проверяйте поле `returned_code` в результатах торговой операции.

---

## Важные замечания

* **Проверяйте коды возврата:** Каждая торговая операция возвращает код статуса (10009 = успех)
* **Проверяйте параметры:** Используйте `order_check()` перед `order_send()`
* **Обрабатывайте исключения:** Могут возникать сетевые/протокольные ошибки
* **Асинхронный контекст:** Все методы должны вызываться в асинхронном контексте
* **Очистка потоков:** Корректно отменяйте потоки с помощью `cancellation_event`
* **Временные метки в UTC:** Всё время указано в UTC, а не в местном времени
* **Ограничения брокера:** Не все брокеры поддерживают все возможности (DOM, хеджирование и т.д.)
* **Автоматическое переподключение:** Все методы имеют встроенную логику переподключения

---

"Торгуйте безопасно, пишите чистый код, и пусть ваши асинхронные потоки всегда текут гладко."
