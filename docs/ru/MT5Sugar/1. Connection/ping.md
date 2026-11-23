# Пинг сервера MT5 (`ping`)

> **Sugar-метод:** Проверяет отзывчивость сервера с помощью лёгкого запроса.

**Информация об API:**

* **Метод:** `sugar.ping(timeout: float = 5.0)`
* **Возвращает:** `True`, если сервер отвечает, иначе `False`
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def ping(self, timeout: float = 5.0) -> bool
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `timeout` | `float` | Нет | `5.0` | Тайм-аут в секундах для попытки пинга |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `bool` | `True`, если сервер отвечает в пределах тайм-аута, иначе `False` |

---

## 🏛️ Основное

**Что делает:**

- Отправляет лёгкий запрос на сервер MT5
- Ожидает ответ в пределах тайм-аута
- Проверяет фактическую работоспособность сервера (а не только состояние канала)
- Возвращает False при тайм-ауте или любой ошибке

**Ключевое поведение:**

- Использует get_symbols_total() в качестве запроса для пинга
- Тайм-аут по умолчанию 5 секунд
- Перехватывает TimeoutError и все исключения
- Не изменяет никакое состояние

---

## ⚡ Под капотом

```
MT5Sugar.ping()
    ↓ оборачивает в asyncio.timeout
MT5Service.get_symbols_total(selected_only=True)
    ↓ вызывает
MT5Account.symbols_total()
    ↓ gRPC protobuf
MarketInfoService.SymbolsTotal()
    ↓ MT5 Terminal
```

**Цепочка вызовов:**

1. Sugar оборачивает запрос в контекст asyncio.timeout
2. Вызывает Service.get_symbols_total() с selected_only=True
3. Service перенаправляет в Account.symbols_total()
4. Account отправляет gRPC-запрос в терминал
5. Если ответ пришёл в пределах тайм-аута, возвращает True
6. При тайм-ауте или исключении возвращает False

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:318`
- Service: `src/pymt5/mt5_service.py:377`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:687`

---

## Когда использовать

**Используйте `ping()`, когда:**

- Проверяете фактическую отзывчивость сервера
- Проверяете подключение после тайм-аута
- Выполняете проверки работоспособности в системах мониторинга
- Перед критичными операциями

**Не используйте, когда:**

- Нужно только состояние канала (используйте `is_connected()`)
- Выполняете фактические операции (не нужно сначала делать пинг)
- Выполняете высокочастотные проверки (слишком большие накладные расходы)

---

## 🔗 Примеры

### Пример 1: Базовый пинг сервера

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def test_connection():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Пинг сервера
    responsive = await sugar.ping()

    if responsive:
        print("Server is responsive")
    else:
        print("Server not responding")

# Вывод:
# Server is responsive
```

### Пример 2: Пинг с пользовательским тайм-аутом

```python
async def quick_ping():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Быстрый пинг с тайм-аутом 2 секунды
    responsive = await sugar.ping(timeout=2.0)

    if responsive:
        print("Server responded within 2 seconds")
    else:
        print("Server slow or unresponsive")
```

### Пример 3: Монитор работоспособности подключения

```python
import asyncio

async def health_monitor():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    consecutive_failures = 0
    max_failures = 3

    while True:
        # Проверить и канал, и сервер
        channel_ok = sugar.is_connected()
        server_ok = await sugar.ping(timeout=3.0)

        if channel_ok and server_ok:
            print("Health: OK")
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            print(f"Health: FAIL ({consecutive_failures}/{max_failures})")

            if consecutive_failures >= max_failures:
                print("Reconnecting...")
                await sugar.quick_connect("FxPro-MT5 Demo")
                consecutive_failures = 0

        await asyncio.sleep(30)
```

---

## Типичные ошибки

**Ошибка 1: Использование перед каждой операцией**
```python
# ПЛОХО: Пинг перед каждой операцией
for _ in range(100):
    if await sugar.ping():
        await sugar.get_balance()
    # Слишком большие накладные расходы!
```

**Решение:** Делайте пинг периодически, а не перед каждой операцией
```python
# Пинг один раз в начале
if not await sugar.ping():
    await sugar.quick_connect("FxPro-MT5 Demo")

# Затем выполняйте операции без пинга
for _ in range(100):
    balance = await sugar.get_balance()
```

**Ошибка 2: Слишком короткий тайм-аут**
```python
# ОШИБКА: Тайм-аут 0.1 секунды слишком короткий
responsive = await sugar.ping(timeout=0.1)
# Может завершиться неудачей даже при хорошем подключении
```

**Решение:** Используйте разумный тайм-аут (2-5 секунд)
```python
# Дайте достаточно времени на сетевой обмен туда-обратно
responsive = await sugar.ping(timeout=3.0)
```

**Ошибка 3: Необработанный результат False**
```python
# Нет действий при неудачном пинге
if not await sugar.ping():
    pass  # Что теперь?
```

**Решение:** Реализуйте логику восстановления
```python
if not await sugar.ping():
    print("Ping failed - attempting reconnect")
    try:
        await sugar.quick_connect("FxPro-MT5 Demo")
    except Exception as e:
        print(f"Reconnect failed: {e}")
```

---

## Полезные советы

**Совет 1: Сочетайте с is_connected для полной проверки**

```python
# Полная проверка подключения
async def is_fully_connected(sugar):
    channel_ok = sugar.is_connected()  # Быстрая проверка канала
    server_ok = await sugar.ping()     # Фактическая проверка сервера

    return channel_ok and server_ok

# Используйте перед критичными операциями
if await is_fully_connected(sugar):
    await sugar.buy_market(volume=1.0)
```

**Совет 2: Используйте прогрессивные тайм-ауты**
```python
# Сначала попробуйте быстрый пинг, затем более длительный
async def smart_ping(sugar):
    # Быстрая попытка (1 секунда)
    if await sugar.ping(timeout=1.0):
        return True

    # Более медленная попытка (5 секунд)
    if await sugar.ping(timeout=5.0):
        return True

    return False
```

**Совет 3: Логируйте задержку пинга**
```python
import time

async def ping_with_latency(sugar):
    start = time.time()
    responsive = await sugar.ping()
    latency = (time.time() - start) * 1000  # ms

    if responsive:
        print(f"Ping: {latency:.1f}ms")
    else:
        print("Ping: timeout")

    return responsive
```

---

## 📚 См. также

- [is_connected](is_connected.md) - Проверить состояние канала
- [quick_connect](quick_connect.md) - Подключиться к кластеру MT5
