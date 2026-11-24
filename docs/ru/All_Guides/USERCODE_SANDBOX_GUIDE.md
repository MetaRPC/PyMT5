# Руководство по пользовательской песочнице (User Code Sandbox)

## Что это?

Это **ваша песочница** для написания собственного торгового кода MT5 на Python. Настройка подключения уже выполнена — вам нужно лишь добавить свою торговую логику!

## 🏁 Быстрый старт

1. **Кейс уже активен в main.py**
   - Откройте `examples/main.py`
   - Кейс «17» для пользовательской песочницы готов к использованию

2. **Откройте `examples/5_usercode/17_usercode.py`**
   - Напишите свой код или раскомментируйте примеры

3. **Запустите:**
   ```bash
   cd examples
   python main.py usercode
   ```

Вот и всё! Ваш код выполнится с полноценным подключением к MT5.

## Как пользоваться

### Вариант 1: раскомментировать примеры

Файл содержит 5 готовых к использованию примеров:

```python
# Пример 1: Получить баланс счёта (Sugar — проще всего)
# balance = await sugar.get_balance()
# print(f"Balance: {balance:.2f}")
```

Просто удалите `#`, чтобы активировать!

### Вариант 2: написать свой собственный код

Добавьте свою логику между маркерами:

```python
# =================================================================
# ВАШ КОД ЗДЕСЬ
# =================================================================

# Ваша торговая стратегия здесь...

# TODO: Напишите здесь свою торговую логику
```

## Доступные команды

Запустите свой код с помощью:

```bash
# Из каталога examples
python main.py usercode
python main.py 17
python main.py user
python main.py sandbox
```

## Что уже настроено

+ **Connection** — терминал MT5 подключён через gRPC

+ **Configuration** — загружена из `examples/0_common/settings.json`

+ **account** — низкоуровневый gRPC-клиент (MT5Account)

+ **service** — обёртка среднего уровня (MT5Service)

+ **sugar** — высокоуровневый Sugar API (MT5Sugar)

+ **async/await** — все методы асинхронны

## 🧩 Можно ли смешивать уровни API?

**Да!** Вы можете использовать все три уровня в одном файле:

```python
# Низкий уровень (прямой gRPC protobuf)
summary = await account.account_summary()
balance_pb = summary.account_balance

# Средний уровень (MT5Service)
account_info = await service.get_account_summary()
balance_svc = account_info.balance

# Высокий уровень (MT5Sugar)
balance_sugar = await sugar.get_balance()
```

Все три переменные доступны одновременно:

- `account` — для полного контроля (gRPC protobuf)
- `service` — для удобных методов (слой Service)
- `sugar` — для максимально простого использования (Sugar API)

## Краткий справочник

### Получить информацию о счёте

```python
# Sugar API (проще всего)
balance = await sugar.get_balance()
print(f"Balance: {balance:.2f}")

# Service API (больше деталей)
account_info = await service.get_account_summary()
print(f"Balance: {account_info.balance:.2f} {account_info.currency}")
print(f"Equity:  {account_info.equity:.2f}")

# Account API (полный контроль)
summary = await account.account_summary()
print(f"Balance: {summary.account_balance:.2f}")
```

### Получить текущую цену

```python
# Sugar API
bid = await sugar.get_bid("EURUSD")
ask = await sugar.get_ask("EURUSD")
print(f"EURUSD: Bid={bid:.5f}, Ask={ask:.5f}")

# Service API
tick = await service.get_symbol_tick("EURUSD")
print(f"EURUSD Bid: {tick.bid:.5f}, Ask: {tick.ask:.5f}")
```

### Открыть рыночный ордер

```python
# Sugar API (проще всего)
try:
    ticket = await sugar.buy_market("EURUSD", 0.01)
    print(f"Order opened: #{ticket}")
except Exception as e:
    print(f"Order failed: {e}")

# С SL/TP в пипсах
ticket = await sugar.buy_market_with_pips("EURUSD", 0.01, sl_pips=20, tp_pips=30)

# Рассчитать размер позиции на основе риска (2% при SL 50 пипсов)
lot_size = await sugar.calculate_position_size("EURUSD", risk_percent=2.0, sl_pips=50)
ticket = await sugar.buy_market_with_pips("EURUSD", lot_size, sl_pips=50, tp_pips=100)
```

### Разместить отложенный ордер

```python
# Buy Limit с абсолютной ценой и SL/TP в пипсах
ticket = await sugar.buy_limit_with_sltp("EURUSD", 0.01, price=1.0850,
                                          sl_pips=20, tp_pips=30)

# Buy Stop с абсолютной ценой
ticket = await sugar.buy_stop("EURUSD", 0.01, price=1.0950)

# Sell Limit с абсолютной ценой и SL/TP
ticket = await sugar.sell_limit_with_sltp("EURUSD", 0.01, price=1.1050,
                                           sl=1.1070, tp=1.1030)
```

### Получить открытые позиции

```python
# Sugar API
positions = await sugar.get_open_positions()
print(f"Open positions: {len(positions)}")
for pos in positions:
    print(f"  #{pos.ticket} {pos.symbol} {pos.volume:.2f} lot, "
          f"Profit: {pos.profit:.2f}")

# Service API с фильтрами
opened_data = await service.get_opened_orders()
positions = opened_data.position_infos
```

### Закрыть позиции

```python
# Закрыть конкретную позицию
await sugar.close_position(ticket)

# Закрыть все позиции по символу
await sugar.close_all_positions("EURUSD")

# Закрыть все позиции (все символы)
await sugar.close_all_positions()
```

### Изменить позицию

```python
# Изменить SL/TP
await sugar.modify_position_sltp(ticket, sl=1.0850, tp=1.0950)

# Изменить только стоп-лосс
await sugar.modify_position_sl(ticket, sl=1.0850)

# Изменить только тейк-профит
await sugar.modify_position_tp(ticket, tp=1.0950)
```

### Рассчитать размер позиции

```python
# Рассчитать размер позиции на основе риска
volume = await sugar.calculate_position_size("EURUSD", risk_percent=2.0, sl_pips=20)
print(f"Volume for 2% risk with 20 pip SL: {volume:.2f} lot")

# Затем используйте рассчитанный объём
ticket = await sugar.buy_market("EURUSD", volume)
```

## Коды возврата (RetCodes)

**Всегда проверяйте returned_code после торговых операций!**

```python
from MetaRpcMT5.mt5_term_api_trading_helper_pb2 import OrderSendRequest
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as pb_trading

# Формируем запрос
request = OrderSendRequest(
    symbol="EURUSD",
    volume=0.01,
    operation=pb_trading.TMT5_ORDER_TYPE_BUY,
    price=0.0,  # Рыночный ордер (цена будет заполнена брокером)
    # ... другие поля
)

result = await service.place_order(request)

# Проверяем RetCode
if result.returned_code == 10009:  # Успех для рыночных ордеров
    print(f"[OK] Order opened: #{result.order}")
elif result.returned_code == 10008:  # Успех для отложенных ордеров
    print(f"[OK] Pending order placed: #{result.order}")
else:
    print(f"[X] Order failed: {result.comment} (code {result.returned_code})")
```

**Распространённые RetCodes:**

- `10009` — рыночный ордер успешно исполнен
- `10008` — отложенный ордер успешно размещён
- `10019` — недостаточно средств (недостаточно маржи)
- `10016` — некорректные стопы (SL/TP слишком близко к цене)
- `10018` — рынок закрыт

Полный список: [RETURN_CODES_REFERENCE.md](RETURN_CODES_REFERENCE.md)

## ℹ️ Обработка ошибок

PyMT5 использует исключения Python для обработки ошибок:

### 1. Ошибки подключения/сети

```python
try:
    result = await service.place_order(request)
except Exception as e:
    print(f"Connection or network error: {e}")
    return
```

### 2. Ошибки торговых операций (RetCode)

```python
result = await service.place_order(request)
if result.returned_code != 10009:
    print(f"Trade rejected: {result.comment}")
```

**Всегда проверяйте ОБА варианта!**

### Рекомендуемый шаблон:

```python
try:
    result = await service.place_order(request)

    if result.returned_code == 10009:
        print(f"[OK] Success: Order #{result.order}")
    else:
        print(f"[X] Failed: {result.comment} (code: {result.returned_code})")

except Exception as e:
    print(f"[X] Error: {e}")
```

## 📝 Документация

- [MT5Account Master Overview](../MT5Account/MT5Account.Master.Overview.md) — полный справочник по API (43 метода)
- [MT5Service Overview](../MT5Service/MT5Service.Overview.md) — обёртка среднего уровня (37 методов)
- [MT5Sugar Master Overview](../MT5Sugar/MT5Sugar.Master.Overview.md) — высокоуровневый Sugar API (62 метода + 7 свойств)
- [ENUMS Usage Reference](ENUMS_USAGE_REFERENCE.md) — все ENUM в одном месте

## 🔑 Конфигурация

Конфигурация считывается из `examples/0_common/settings.json` функцией `load_settings()` — это единственная конфигурация, которую используют примеры (слоя `.env` нет).

```json
{
  "user": 591129415,
  "password": "YourPassword",
  "grpc_server": "mt5.mrpc.pro:443",
  "mt_cluster": "MetaQuotes-Demo",
  "test_symbol": "EURUSD",
  "test_volume": 0.01,
  "api_key": "TRIAL"
}
```

Обязательно: `user`, `password`, `grpc_server`, `mt_cluster`, `test_symbol`. Поле `api_key` необязательно — при его отсутствии используется переменная окружения `MRPC_API_KEY`, а затем значение `"TRIAL"`.

См. загрузчик в [`demo_helpers.py`](https://github.com/MetaRPC/PyMT5/blob/main/examples/0_common/demo_helpers.py).

## Советы

1. **Начинайте с простого** — раскомментируйте по одному примеру за раз

2. **Используйте Sugar API** — методы вроде `buy_market_with_pips()` и 
`calculate_position_size()` проще, чем низкоуровневые

3. **Проверяйте returned_code** — всегда проверяйте торговые операции (10009 = успех)

4. **Тестируйте на демо** — убедитесь, что сначала используете демо-счёт!

5. **Читайте документацию** — [RETURN_CODES_REFERENCE.md](RETURN_CODES_REFERENCE.md) объясняет все коды ошибок

6. **Используйте async/await** — все методы асинхронны

7. **Подсказки типов** — используйте автодополнение IDE для более удобной разработки

8. **Смотрите примеры** — в папке `examples/` есть 15+ рабочих примеров

## Распространённые ошибки

[X] **Забыли использовать await**
```python
balance = sugar.get_balance()  # НЕ забудьте await!
```

[+] **Всегда используйте await**
```python
balance = await sugar.get_balance()
```

[X] **Не проверяете исключения**
```python
ticket = await sugar.buy_market("EURUSD", 0.01)  # Нет try/except!
```

[+] **Всегда обрабатывайте исключения**
```python
try:
    ticket = await sugar.buy_market("EURUSD", 0.01)
    print(f"Order opened: #{ticket}")
except Exception as e:
    print(f"Error: {e}")
```

[X] **Не проверяете returned_code**
```python
result = await service.place_order(request)
# Предполагаем, что это успех!
```

[+] **Проверяйте returned_code для торговых операций**
```python
result = await service.place_order(request)
if result.returned_code != 10009:
    print(f"Trade failed: {result.comment}")
    return
```

## Получение помощи

- **Типы protobuf**: смотрите папку `package/MetaRpcMT5/` для всех определений protobuf
- **Коды ошибок**: см. [RETURN_CODES_REFERENCE.md](RETURN_CODES_REFERENCE.md)
- **Примеры**: смотрите рабочий код в папке `examples/`
- **Документация по API**: смотрите полный справочник в папке docs

## Пример: полноценная торговая стратегия

Вот полный пример, демонстрирующий правильную обработку ошибок:

```python
async def run_user_code():
    """Your sandbox function - write your code here!"""

    try:
        # Загружаем конфигурацию
        config = load_settings()
    except Exception as e:
        print(f"Config error: {e}")
        return

    try:
        # Подключаемся к MT5
        account = await create_and_connect_mt5(config)
    except Exception as e:
        print(f"Connection error: {e}")
        return

    # Создаём обёртки service и sugar
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol=config.get('test_symbol', 'EURUSD'))

    # Получаем информацию о счёте
    try:
        balance = await sugar.get_balance()
        print(f"Balance: {balance:.2f}")
    except Exception as e:
        print(f"Balance error: {e}")
        return

    # Рассчитываем размер позиции на основе риска (1% при SL 50 пипсов)
    try:
        volume = await sugar.calculate_position_size("EURUSD",
                                                      risk_percent=1.0,
                                                      sl_pips=50)
    except Exception as e:
        print(f"Position size error: {e}")
        return

    # Открываем позицию с рассчитанным объёмом
    try:
        ticket = await sugar.buy_market_with_pips("EURUSD", volume,
                                                   sl_pips=50, tp_pips=100)
        print(f"[OK] Position opened: #{ticket} with {volume:.2f} lot")
    except Exception as e:
        print(f"Order error: {e}")
        return

    print("Strategy execution completed!")


if __name__ == "__main__":
    asyncio.run(run_user_code())
```

**Успешной торговли!**
