# Справочник кодов возврата MT5 (RetCodes) — Python

## 🛡️ Что такое RetCode?

**RetCode** (код возврата, Return Code) — это код статуса, который терминал MT5 возвращает после выполнения торговой операции. Код указывает на успех или причину неудачи.

RetCode **появляются только в торговых методах**, потому что только торговые операции проходят через брокера и могут быть отклонены по разным причинам (недостаточная маржа, некорректная цена, закрытый рынок и т. д.).

### Быстрый пример: Правильная обработка RetCode

```python
from MetaRpcMT5.helpers.errors import TRADE_RETCODE_DONE, get_retcode_message

# Размещаем ордер
result = await service.place_order(request)

# ✅ ВСЕГДА явно проверяйте returned_code
if result.returned_code == TRADE_RETCODE_DONE:
    print(f"✓ Trade successful! Order #{result.order}")
else:
    print(f"✗ Trade failed: {get_retcode_message(result.returned_code)}")
    # Например: "Insufficient funds" (10019) или "Market closed" (10018)
```

**Ключевой момент:** Отсутствие исключения = API сработал, но **проверьте RetCode**, чтобы узнать, **успешна ли сделка**.

---

## Источник RetCode

RetCode — это **стандартные коды MQL5**, определённые в официальной документации MetaQuotes:

**Документация MQL5**: [Trade Result Codes (ENUM_TRADE_RETCODE)](https://www.mql5.com/en/docs/constants/errorswarnings/enum_trade_return_codes)

Эти коды:

- **Единообразны для всех языков** (C#, Python, Java, Node.js, Go, PHP)
- **Единообразны с терминалом MT5** — возвращаются напрямую с торгового сервера
- **Определены в protobuf** — возвращаются как поле `uint32` `returned_code` в структурах результата торговли
- **Доступны как константы Python** — определены в `package/MetaRpcMT5/helpers/errors.py`

---

## 📥 Где RetCode используется в API?

RetCode возвращается во **всех торговых операциях**, изменяющих позиции или ордера:

### 1. OrderSend (Открытие ордеров)

```python
from MetaRpcMT5.helpers.errors import (
    ApiError,
    TRADE_RETCODE_DONE,
    get_retcode_message,
    is_retcode_success
)

# Используя Sugar API
try:
    ticket = await sugar.buy_market("EURUSD", 0.01)
    print(f"[OK] Order opened: #{ticket}")
except ApiError as e:
    # Проверяем, является ли это торговой ошибкой с RetCode
    retcode = e.mql_error_trade_int_code()
    print(f"RetCode: {retcode}")
    print(f"Description: {e.mql_error_trade_description()}")

# Используя Service API (средний уровень)
result = await service.place_order(request)
if result.returned_code == TRADE_RETCODE_DONE:
    print(f"[OK] Order opened! Ticket: {result.order}")
else:
    print(f"[X] Order failed: {get_retcode_message(result.returned_code)}")
```

### 2. OrderModify (Изменение SL/TP)

```python
from MetaRpcMT5.helpers.errors import TRADE_RETCODE_DONE, is_retcode_success, get_retcode_message

# Используя Sugar API
try:
    await sugar.modify_position_sltp(ticket, sl=1.0850, tp=1.0950)
    print("[OK] SL/TP modified successfully")
except ApiError as e:
    print(f"[X] Modification failed: {e.mql_error_trade_description()}")

# Используя Service API
result = await service.modify_order(request)
if is_retcode_success(result.returned_code):
    print("[OK] SL/TP modified successfully")
else:
    print(f"[X] Modification failed: {get_retcode_message(result.returned_code)}")
```

### 3. PositionClose (Закрытие позиций)

```python
from MetaRpcMT5.helpers.errors import ApiError, TRADE_RETCODE_DONE, TRADE_RETCODE_POSITION_CLOSED

# Используя Sugar API
try:
    await sugar.close_position(ticket)
    print("[OK] Position closed")
except ApiError as e:
    if e.mql_error_trade_int_code() == TRADE_RETCODE_POSITION_CLOSED:
        print("[WARN] Position already closed")
    else:
        print(f"[X] Close failed: {e}")

# Используя Service API
result = await service.close_order(request)
if result.returned_code == TRADE_RETCODE_DONE:
    print("[OK] Position closed")
```

---

## 👁️ Почему RetCode только в торговых методах?

**Информационные методы** (получение цен, символов, баланса) **НЕ возвращают RetCode**, потому что:

- Они не проходят через брокера
- Их нельзя «отклонить» — либо данные есть, либо произошла ошибка gRPC
- Они работают с локальными данными терминала

**Торговые методы** возвращают RetCode, потому что:

- Запрос отправляется брокеру через торговый сервер
- Брокер проверяет: маржу, правила символа, торговые часы, лимиты
- Брокер может отклонить запрос по десяткам причин
- У каждой причины свой уникальный код

---

## Полный список RetCode

### Коды успеха

| Код | Константа Python | Описание | Когда возвращается |
|------|-----------------|-------------|---------------|
| **10009** | `TRADE_RETCODE_DONE` | **Запрос успешно выполнен** | Рыночный ордер открыт/закрыт |
| **10010** | `TRADE_RETCODE_DONE_PARTIAL` | **Частичное исполнение** | Исполнена только часть объёма |
| **10008** | `TRADE_RETCODE_PLACED` | **Отложенный ордер размещён** | Размещён ордер Limit/Stop |

### Коды реквоты (рекомендуется повтор)

| Код | Константа Python | Описание | Действие |
|------|-----------------|-------------|--------|
| **10004** | `TRADE_RETCODE_REQUOTE` | **Реквота** | Цена изменилась, повторите запрос |
| **10020** | `TRADE_RETCODE_PRICE_CHANGED` | **Цена изменилась** | Похоже на реквоту, повторите |

**Вспомогательная функция:**
```python
from MetaRpcMT5.helpers.errors import is_retcode_requote

if is_retcode_requote(retcode):
    # Повторить с обновлённой ценой
    pass
```

### ⚠️ Ошибки валидации запроса

| Код | Константа Python | Описание | Частая причина |
|------|-----------------|-------------|--------------|
| **10013** | `TRADE_RETCODE_INVALID_REQUEST` | **Некорректный запрос** | Неверные параметры |
| **10014** | `TRADE_RETCODE_INVALID_VOLUME` | **Некорректный объём** | Объём < MinVolume или > MaxVolume |
| **10015** | `TRADE_RETCODE_INVALID_PRICE` | **Некорректная цена** | Цена не соответствует правилам символа |
| **10016** | `TRADE_RETCODE_INVALID_STOPS` | **Некорректные стопы** | SL/TP слишком близко к цене (проверьте StopLevel) |
| **10022** | `TRADE_RETCODE_INVALID_EXPIRATION` | **Некорректный срок истечения** | Неверное время истечения |
| **10030** | `TRADE_RETCODE_INVALID_FILL` | **Некорректный тип исполнения ордера** | Тип исполнения не разрешён |
| **10035** | `TRADE_RETCODE_INVALID_ORDER` | **Некорректный тип ордера** | Тип ордера запрещён для символа |
| **10038** | `TRADE_RETCODE_INVALID_CLOSE_VOLUME` | **Некорректный объём закрытия** | Объём закрытия превышает объём позиции |

### 🚫 Торговые ограничения

| Код | Константа Python | Описание | Причина |
|------|-----------------|-------------|--------|
| **10017** | `TRADE_RETCODE_TRADE_DISABLED` | **Торговля отключена** | Торговля отключена для символа |
| **10018** | `TRADE_RETCODE_MARKET_CLOSED` | **Рынок закрыт** | Вне торговых часов |
| **10026** | `TRADE_RETCODE_SERVER_DISABLES_AT` | **Автоторговля отключена сервером** | Сервер отключил автоторговлю |
| **10027** | `TRADE_RETCODE_CLIENT_DISABLES_AT` | **Автоторговля отключена клиентом** | Терминал отключил автоторговлю |
| **10032** | `TRADE_RETCODE_ONLY_REAL` | **Только реальные счета** | Действие недоступно на демо |
| **10042** | `TRADE_RETCODE_LONG_ONLY` | **Разрешены только длинные позиции** | Короткие позиции запрещены |
| **10043** | `TRADE_RETCODE_SHORT_ONLY` | **Разрешены только короткие позиции** | Длинные позиции запрещены |
| **10044** | `TRADE_RETCODE_CLOSE_ONLY` | **Разрешено только закрытие позиций** | Открытие новых позиций запрещено |
| **10045** | `TRADE_RETCODE_FIFO_CLOSE` | **Закрытие позиций только по правилу FIFO** | Применяется правило FIFO |
| **10046** | `TRADE_RETCODE_HEDGE_PROHIBITED` | **Противоположные позиции запрещены** | Хеджирование отключено |

### 💰 Лимиты ресурсов

| Код | Константа Python | Описание | Решение |
|------|-----------------|-------------|----------|
| **10019** | `TRADE_RETCODE_NO_MONEY` | **Недостаточно средств** | Проверьте свободную маржу |
| **10033** | `TRADE_RETCODE_LIMIT_ORDERS` | **Лимит отложенных ордеров** | Закройте часть отложенных ордеров |
| **10034** | `TRADE_RETCODE_LIMIT_VOLUME` | **Лимит объёма** | Уменьшите объём позиции |
| **10040** | `TRADE_RETCODE_LIMIT_POSITIONS` | **Лимит позиций** | Закройте часть позиций |

### 🔄 Технические проблемы (можно повторить)

| Код | Константа Python | Описание | Можно повторить |
|------|-----------------|-------------|-----------|
| **10011** | `TRADE_RETCODE_ERROR` | **Ошибка обработки** | Нет |
| **10012** | `TRADE_RETCODE_TIMEOUT` | **Тайм-аут запроса** | Да |
| **10021** | `TRADE_RETCODE_NO_QUOTES` | **Нет котировок** | Да |
| **10024** | `TRADE_RETCODE_TOO_MANY_REQUESTS` | **Ограничение частоты** | Да (с задержкой) |
| **10028** | `TRADE_RETCODE_LOCKED` | **Запрос заблокирован для обработки** | Да |
| **10029** | `TRADE_RETCODE_FROZEN` | **Ордер или позиция заморожены** | Да |
| **10031** | `TRADE_RETCODE_NO_CONNECTION` | **Нет соединения** | Да |

**Вспомогательная функция:**
```python
from MetaRpcMT5.helpers.errors import is_retcode_retryable
import asyncio

if is_retcode_retryable(retcode):
    # Безопасно повторить с экспоненциальной задержкой
    await asyncio.sleep(2)
    # Повторить операцию...
```

### Управление состоянием

| Код | Константа Python | Описание | Значение |
|------|-----------------|-------------|---------|
| **10023** | `TRADE_RETCODE_ORDER_CHANGED` | **Состояние ордера изменилось** | Ордер уже изменён/закрыт |
| **10025** | `TRADE_RETCODE_NO_CHANGES` | **Нет изменений** | Новые параметры = текущие параметры |
| **10036** | `TRADE_RETCODE_POSITION_CLOSED` | **Позиция закрыта** | Позиция не существует |
| **10039** | `TRADE_RETCODE_CLOSE_ORDER_EXIST` | **Ордер на закрытие существует** | Нельзя закрыть больше объёма позиции |

### ❌ Коды отклонения

| Код | Константа Python | Описание | Причина |
|------|-----------------|-------------|--------|
| **10006** | `TRADE_RETCODE_REJECT` | **Запрос отклонён** | Брокер отклонил |
| **10007** | `TRADE_RETCODE_CANCEL` | **Запрос отменён** | Отменён трейдером |
| **10041** | `TRADE_RETCODE_REJECT_CANCEL` | **Активация отложенного ордера отклонена** | Активация отклонена и отменена |

---

## Централизованный обработчик ошибок (`package/MetaRpcMT5/helpers/errors.py`)

**PyMT5 предоставляет модуль централизованной обработки ошибок**, который упрощает работу с RetCode.

Вместо ручной проверки кодов возврата и написания собственных сообщений об ошибках вы можете использовать встроенные вспомогательные функции из `package/MetaRpcMT5/helpers/errors.py`:

### Что внутри

Модуль содержит:

- **Все константы RetCode** (напр., `TRADE_RETCODE_DONE`, `TRADE_RETCODE_NO_MONEY`)

- **Вспомогательные функции** для проверки кодов возврата (`is_retcode_success`, `is_retcode_requote` и т. д.)

- **Понятные человеку сообщения об ошибках** для всех RetCode

- **Готовую логику обработки ошибок** для типовых сценариев

### Зачем это использовать?

✅ **Нет «магических» чисел** — используйте именованные константы вместо `10009`, `10019`

✅ **Автоматические описания ошибок** — получайте понятные человеку сообщения для любого RetCode

✅ **Умная категоризация** — легко определяйте реквоты, повторяемые ошибки и т. д.

✅ **Единообразная обработка ошибок** — используйте одну и ту же логику во всём проекте

### Когда явно проверять RetCode

**КРИТИЧНО:** Вы **ОБЯЗАНЫ явно проверять** `returned_code` после каждой торговой операции:

```python
# ❌ НЕВЕРНО — Перехвата только исключений НЕДОСТАТОЧНО!
try:
    result = await service.place_order(request)
    print(f"Order placed: {result.order}")  # ← Это не означает успех!
except ApiError as e:
    print(f"Error: {e}")

# ✅ ВЕРНО — Всегда проверяйте returned_code
try:
    result = await service.place_order(request)

    # ОБЯЗАТЕЛЬНО явно проверяйте RetCode
    if result.returned_code == TRADE_RETCODE_DONE:
        print(f"✓ Order placed: {result.order}")
    else:
        print(f"✗ Order failed: {get_retcode_message(result.returned_code)}")

except ApiError as e:
    print(f"API Error: {e}")
```

**Почему?** Потому что:

- Отсутствие исключения означает, что **вызов API успешен** (соединение в порядке, терминал ответил)

- Но это **НЕ** означает, что **сделка успешна** (брокер мог её отклонить)

- Нужно проверить `returned_code`, чтобы узнать **фактический результат сделки**

---

## Вспомогательные функции Python

Модуль `package/MetaRpcMT5/helpers/errors.py` предоставляет вспомогательные функции для работы с RetCode:

### is_retcode_success()

Проверяет, указывает ли RetCode на успешное исполнение сделки.

```python
from MetaRpcMT5.helpers.errors import is_retcode_success, TRADE_RETCODE_DONE

# Использование
if is_retcode_success(result.returned_code):
    print("Trade successful!")

# Возвращает True только для retcode == 10009 (TRADE_RETCODE_DONE)
```

### is_retcode_requote()

Проверяет, указывает ли RetCode на изменение цены (реквоту) — безопасно повторить немедленно.

```python
from MetaRpcMT5.helpers.errors import is_retcode_requote, TRADE_RETCODE_REQUOTE, TRADE_RETCODE_PRICE_CHANGED

# Использование
if is_retcode_requote(result.returned_code):
    print("Price changed, retrying...")
    # Повторить с обновлённой ценой

# Возвращает True для 10004 или 10020
```

### is_retcode_retryable()

Проверяет, указывает ли RetCode на временную ошибку — безопасно повторить с задержкой.

```python
from MetaRpcMT5.helpers.errors import (
    is_retcode_retryable,
    TRADE_RETCODE_TIMEOUT,
    TRADE_RETCODE_NO_CONNECTION,
    TRADE_RETCODE_FROZEN
)
import asyncio

# Использование
if is_retcode_retryable(result.returned_code):
    # Эти ошибки временные, повторить с задержкой
    await asyncio.sleep(2)
    # Повторить операцию

# Возвращает True для: Timeout, NoConnection, Frozen, Locked, TooManyRequests, NoQuotes
```

### get_retcode_message()

Возвращает понятное человеку описание для любого RetCode.

```python
from MetaRpcMT5.helpers.errors import get_retcode_message, TRADE_RETCODE_DONE

# Использование
if result.returned_code != TRADE_RETCODE_DONE:
    print(f"Error: {get_retcode_message(result.returned_code)}")

# Возвращает понятное человеку описание для любого RetCode
```

### check_retcode()

Выводит отформатированное сообщение с подсказками и возвращает `True` при успехе.

```python
from MetaRpcMT5.helpers.errors import check_retcode, TRADE_RETCODE_DONE

# Использование
result = await service.place_order(request)
if check_retcode(result.returned_code, "Order placement"):
    print(f"Order ticket: {result.order}")

# Выводит отформатированное сообщение и полезные подсказки для частых ошибок
```

---

## Примеры использования

### Пример 1: Базовое размещение ордера с проверкой RetCode

```python
import asyncio
from uuid import uuid4
from MetaRpcMT5 import MT5Account
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from MetaRpcMT5.helpers.errors import TRADE_RETCODE_DONE, get_retcode_message
from MetaRpcMT5.mt5_term_api_trading_helper_pb2 import OrderSendRequest
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as pb_trading

async def main():
    # Создаём экземпляр MT5Account
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",
        id_=uuid4()
    )

    # Подключаемся к серверу MT5
    await account.connect_by_server_name(
        server_name="MetaQuotes-Demo",
        base_chart_symbol="EURUSD",
        timeout_seconds=120
    )

    try:
        # Создаём service и sugar
        service = MT5Service(account)
        sugar = MT5Sugar(service, default_symbol="EURUSD")

        # Размещаем рыночный ордер на покупку
        request = OrderSendRequest(
            symbol="EURUSD",
            volume=0.01,
            operation=pb_trading.TMT5_ORDER_TYPE_BUY,
            price=0.0  # Рыночный ордер
        )

        result = await service.place_order(request)

        # Проверяем RetCode
        if result.returned_code == TRADE_RETCODE_DONE:
            print(f"[OK] Order opened successfully!")
            print(f"   Ticket: #{result.order}")
            print(f"   Volume: {result.volume:.2f} lots")
            print(f"   Price: {result.price:.5f}")
        else:
            print(f"[X] Order failed!")
            print(f"   RetCode: {result.returned_code}")
            print(f"   Description: {get_retcode_message(result.returned_code)}")

    finally:
        await account.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### Пример 2: Обработка частых ошибок (оператор if/elif)

```python
from MetaRpcMT5.helpers.errors import (
    ApiError,
    TRADE_RETCODE_NO_MONEY,
    TRADE_RETCODE_MARKET_CLOSED,
    TRADE_RETCODE_INVALID_STOPS,
    TRADE_RETCODE_INVALID_VOLUME,
    TRADE_RETCODE_REQUOTE,
    TRADE_RETCODE_PRICE_CHANGED
)
import asyncio

try:
    ticket = await sugar.buy_market("GBPUSD", 0.5)
    print(f"[OK] Order #{ticket} opened")

except ApiError as e:
    retcode = e.mql_error_trade_int_code()

    if retcode == TRADE_RETCODE_NO_MONEY:
        print("[WARN] Insufficient funds!")
        print("   Solution: Reduce volume or add margin")

    elif retcode == TRADE_RETCODE_MARKET_CLOSED:
        print("[WARN] Market closed")
        print("   Solution: Try during trading hours")

    elif retcode == TRADE_RETCODE_INVALID_STOPS:
        print("[WARN] SL/TP too close to market price")
        print("   Solution: Increase distance (check StopLevel)")

    elif retcode == TRADE_RETCODE_INVALID_VOLUME:
        print("[WARN] Invalid volume")
        # Получаем лимиты символа
        symbol_info = await sugar.get_symbol_info("GBPUSD")
        print(f"   Min: {symbol_info.volume_min:.2f}, "
              f"Max: {symbol_info.volume_max:.2f}, "
              f"Step: {symbol_info.volume_step:.2f}")

    elif retcode in (TRADE_RETCODE_REQUOTE, TRADE_RETCODE_PRICE_CHANGED):
        print("[WARN] Price changed, retrying...")
        await asyncio.sleep(0.1)
        # Повторить ордер

    else:
        print(f"[X] Error: {e.mql_error_trade_description()}")
```

### Пример 3: Логика повтора для временных ошибок

```python
import asyncio
from MetaRpcMT5.helpers.errors import (
    ApiError,
    is_retcode_requote,
    is_retcode_retryable
)

async def place_order_with_retry(
    sugar,
    symbol: str,
    volume: float,
    max_retries: int = 3
):
    """Place order with automatic retry logic."""

    for attempt in range(1, max_retries + 1):
        try:
            ticket = await sugar.buy_market(symbol, volume)
            # Успех
            return ticket

        except ApiError as e:
            retcode = e.mql_error_trade_int_code()

            # Реквота — повторить немедленно
            if is_retcode_requote(retcode):
                print(f"Requote on attempt {attempt}, retrying...")
                await asyncio.sleep(0.1)
                continue

            # Повторяемая ошибка — экспоненциальная задержка
            if is_retcode_retryable(retcode):
                wait_time = attempt  # 1с, 2с, 3с
                print(f"Temporary error on attempt {attempt}, "
                      f"waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue

            # Постоянная ошибка — прекратить повторы
            raise RuntimeError(
                f"Permanent error: {e.mql_error_trade_description()}"
            )

        except Exception as e:
            # Другая ошибка (сеть и т. д.)
            raise

    raise RuntimeError(f"Failed after {max_retries} attempts")

# Использование
try:
    ticket = await place_order_with_retry(sugar, "EURUSD", 0.01, max_retries=3)
    print(f"Order placed: #{ticket}")
except Exception as e:
    print(f"Failed to place order: {e}")
```

### Пример 4: Использование check_retcode()

```python
from MetaRpcMT5.helpers.errors import check_retcode

result = await service.place_order(request)

# check_retcode выводит отформатированное сообщение и возвращает True при успехе
if check_retcode(result.returned_code, "Order placement"):
    print(f"Order ticket: {result.order}")

# Вывод при успехе:
#   [OK] Order placement successful (RetCode: 10009)

# Вывод при неудаче (напр., рынок закрыт):
#   [FAIL] Order placement failed (RetCode: 10018)
#      Market is closed
#      Hint: Market is closed - check trading hours
```

### Пример 5: Изменение SL/TP с валидацией

```python
from MetaRpcMT5.helpers.errors import (
    TRADE_RETCODE_DONE,
    TRADE_RETCODE_NO_CHANGES,
    TRADE_RETCODE_POSITION_CLOSED,
    TRADE_RETCODE_INVALID_STOPS,
    get_retcode_message
)

try:
    await sugar.modify_position_sltp(123456, sl=1.0850, tp=1.0950)
    print("[OK] SL/TP updated successfully")

except ApiError as e:
    retcode = e.mql_error_trade_int_code()

    if retcode == TRADE_RETCODE_NO_CHANGES:
        print("[WARN] New SL/TP same as current - no action taken")

    elif retcode == TRADE_RETCODE_POSITION_CLOSED:
        print("[WARN] Position already closed by SL/TP or manually")

    elif retcode == TRADE_RETCODE_INVALID_STOPS:
        print("[X] Invalid SL/TP distance")
        # Получаем уровень стопа символа
        symbol_info = await sugar.get_symbol_info("EURUSD")
        print(f"   Minimum distance: {symbol_info.spread} points")

    else:
        print(f"[X] Modification failed: {get_retcode_message(retcode)}")
```

---

## Лучшие практики

### ДЕЛАЙТЕ:

1. **Всегда проверяйте returned_code** после торговых операций
   ```python
   if result.returned_code == TRADE_RETCODE_DONE:
       # Успех
       pass
   ```

2. **Используйте вспомогательные функции** для более чистого кода
   ```python
   if is_retcode_success(retcode): ...
   if is_retcode_requote(retcode): ...
   ```

3. **Повторяйте при реквотах** (10004, 10020)
   ```python
   if is_retcode_requote(retcode):
       # Повторить с обновлённой ценой
       pass
   ```

4. **Проверяйте маржу перед торговлей**, чтобы избежать 10019
   ```python
   free_margin = await sugar.get_free_margin()
   required_margin = await sugar.calculate_required_margin("EURUSD", 0.01)
   if free_margin < required_margin:
       print("Insufficient margin!")
   ```

### ❌ НЕ ДЕЛАЙТЕ:

1. **Не игнорируйте returned_code** — перехвата только исключений НЕДОСТАТОЧНО!
   ```python
   # ❌ НЕВЕРНО — Опасно! Выглядит как успех, но сделка могла не состояться!
   try:
       result = await service.place_order(request)
       print(f"Order: {result.order}")  # ← НЕТ! Может быть 0, если сделка не удалась
       # Отсутствие проверки RetCode = тихие сбои!
   except ApiError:
       pass

   # ✅ ВЕРНО — Всегда проверяйте returned_code
   try:
       result = await service.place_order(request)
       if result.returned_code == TRADE_RETCODE_DONE:
           # Теперь мы ЗНАЕМ, что сделка успешна
           print(f"Order: {result.order}")
       else:
           # Сделка не удалась — обрабатываем ошибку
           print(f"Failed: {get_retcode_message(result.returned_code)}")
   except ApiError as e:
       # Обрабатываем ошибку API/соединения
       print(f"API Error: {e}")
   ```

2. **Не используйте «магические» числа** — используйте константы
   ```python
   # НЕВЕРНО:
   if retcode == 10009: ...

   # ВЕРНО:
   if retcode == TRADE_RETCODE_DONE: ...
   ```

3. **Не повторяйте постоянные ошибки** (недостаточно маржи, рынок закрыт)
   ```python
   # Используйте is_retcode_retryable() для проверки
   if is_retcode_retryable(retcode):
       # Безопасно повторить
       pass
   ```

4. **Не считайте, что отсутствие исключения = успех**
   ```python
   # Нужно проверить и исключение, И RetCode
   try:
       result = await service.place_order(request)
       if result.returned_code != TRADE_RETCODE_DONE:
           raise RuntimeError(f"Trade failed: {get_retcode_message(result.returned_code)}")
   except Exception as e:
       # Обрабатываем ошибку
       pass
   ```

---

## ℹ️ Таблица быстрого справочника

| Категория | RetCode | Действие |
|----------|----------|--------|
| **Успех** | 10008, 10009, 10010 | Продолжать как обычно |
| **Реквота** | 10004, 10020 | Повторить немедленно |
| **Временные** | 10012, 10021, 10024, 10028, 10029, 10031 | Повторить с задержкой |
| **Валидация** | 10013-10016, 10022, 10030, 10035, 10038 | Исправить параметры |
| **Ограничения** | 10017, 10018, 10026, 10027, 10032, 10042-10046 | Проверить торговые условия |
| **Лимиты** | 10019, 10033, 10034, 10040 | Уменьшить объём/позиции |
| **Состояние** | 10023, 10025, 10036, 10039 | Проверить текущее состояние |
| **Отклонение** | 10006, 10007, 10041 | Проверить запрос |
| **Технические** | 10011 | Обратиться в поддержку |

---

## Справочник констант

Все константы RetCode определены в `package/MetaRpcMT5/helpers/errors.py`:

```python
# Коды успеха
TRADE_RETCODE_SUCCESS = 0           # Успех (общий, редко используется — предпочитайте DONE)
TRADE_RETCODE_DONE = 10009          # Запрос успешно выполнен
TRADE_RETCODE_DONE_PARTIAL = 10010  # Выполнена только часть запроса
TRADE_RETCODE_PLACED = 10008        # Ордер размещён (отложенный ордер активирован)

# Коды реквоты
TRADE_RETCODE_REQUOTE = 10004       # Реквота (цена изменилась, нужно повторить)
TRADE_RETCODE_PRICE_CHANGED = 10020 # Цены изменились (то же, что реквота)

# Коды отклонения запроса
TRADE_RETCODE_REJECT = 10006        # Запрос отклонён сервером
TRADE_RETCODE_CANCEL = 10007        # Запрос отменён трейдером
TRADE_RETCODE_INVALID_REQUEST = 10013       # Некорректный запрос
TRADE_RETCODE_INVALID_VOLUME = 10014        # Некорректный объём в запросе
TRADE_RETCODE_INVALID_PRICE = 10015         # Некорректная цена в запросе
TRADE_RETCODE_INVALID_STOPS = 10016         # Некорректные стопы (SL/TP слишком близко к цене)
TRADE_RETCODE_INVALID_EXPIRATION = 10022    # Некорректная дата истечения ордера
TRADE_RETCODE_INVALID_FILL = 10030          # Некорректный тип исполнения ордера
TRADE_RETCODE_INVALID_ORDER = 10035         # Некорректный или запрещённый тип ордера
TRADE_RETCODE_INVALID_CLOSE_VOLUME = 10038  # Некорректный объём закрытия

# Псевдоним для обратной совместимости
TRADE_RETCODE_INVALID = TRADE_RETCODE_INVALID_REQUEST

# Коды торговых ограничений
TRADE_RETCODE_TRADE_DISABLED = 10017    # Торговля отключена
TRADE_RETCODE_MARKET_CLOSED = 10018     # Рынок закрыт
TRADE_RETCODE_SERVER_DISABLES_AT = 10026 # Автоторговля отключена сервером
TRADE_RETCODE_CLIENT_DISABLES_AT = 10027 # Автоторговля отключена клиентским терминалом
TRADE_RETCODE_ONLY_REAL = 10032         # Операция разрешена только для реальных счетов
TRADE_RETCODE_LONG_ONLY = 10042         # Разрешены только длинные позиции
TRADE_RETCODE_SHORT_ONLY = 10043        # Разрешены только короткие позиции
TRADE_RETCODE_CLOSE_ONLY = 10044        # Разрешены только операции закрытия позиций
TRADE_RETCODE_FIFO_CLOSE = 10045        # Закрытие позиций только по правилу FIFO
TRADE_RETCODE_HEDGE_PROHIBITED = 10046  # Противоположные позиции запрещены (хеджирование отключено)

# Коды лимитов ресурсов
TRADE_RETCODE_NO_MONEY = 10019          # Недостаточно средств (недостаточная маржа)
TRADE_RETCODE_LIMIT_ORDERS = 10033      # Число отложенных ордеров достигло лимита
TRADE_RETCODE_LIMIT_VOLUME = 10034      # Объём ордеров и позиций достиг лимита
TRADE_RETCODE_LIMIT_POSITIONS = 10040   # Число открытых позиций достигло лимита

# Коды технических проблем
TRADE_RETCODE_ERROR = 10011             # Ошибка обработки запроса
TRADE_RETCODE_TIMEOUT = 10012           # Запрос отменён по тайм-ауту
TRADE_RETCODE_NO_QUOTES = 10021         # Нет котировок для обработки запроса
TRADE_RETCODE_TOO_MANY_REQUESTS = 10024 # Слишком частые запросы
TRADE_RETCODE_LOCKED = 10028            # Запрос заблокирован для обработки
TRADE_RETCODE_FROZEN = 10029            # Ордер или позиция заморожены
TRADE_RETCODE_NO_CONNECTION = 10031     # Нет соединения с торговым сервером

# Псевдонимы для обратной совместимости
TRADE_RETCODE_PRICE_OFF = TRADE_RETCODE_NO_QUOTES
TRADE_RETCODE_CONNECTION = TRADE_RETCODE_NO_CONNECTION

# Коды управления состоянием
TRADE_RETCODE_ORDER_CHANGED = 10023     # Состояние ордера изменилось во время запроса
TRADE_RETCODE_NO_CHANGES = 10025        # Нет изменений в запросе
TRADE_RETCODE_POSITION_CLOSED = 10036   # Позиция с указанным ID уже закрыта
TRADE_RETCODE_CLOSE_ORDER_EXIST = 10039 # Для позиции уже существует ордер на закрытие
TRADE_RETCODE_REJECT_CANCEL = 10041     # Активация отложенного ордера отклонена и отменена
```
