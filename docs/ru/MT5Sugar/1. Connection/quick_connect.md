# Быстрое подключение к кластеру MT5 (`quick_connect`)

> **Sugar-метод:** Самый простой способ подключиться к серверу MT5 по имени кластера.

**Информация об API:**

* **Метод:** `sugar.quick_connect(cluster_name, timeout_seconds=30)`
* **Возвращает:** None (вызывает исключение при сбое)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def quick_connect(
    self,
    cluster_name: str,
    timeout_seconds: int = 30,
    **kwargs
) -> None
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `cluster_name` | `str` | Да | - | Идентификатор кластера MT5 (например, "FxPro-MT5 Demo") |
| `timeout_seconds` | `int` | Нет | `30` | Секунды ожидания готовности терминала |
| `**kwargs` | - | Нет | - | Зарезервировано для совместимых с будущими версиями опций подключения |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `None` | Ничего не возвращает при успехе, вызывает исключение при сбое |

**Вызывает:**

- `RuntimeError`, если учётные данные недоступны в MT5Account
- `Exception`, если подключение к кластеру не удалось

---

## 🏛️ Основное

**Что делает:**

- Подключается к серверу MT5 по имени кластера
- Использует учётные данные из MT5Account
- Проверяет подключение с терминалом
- Ожидает до 30 секунд готовности терминала
- Обновляет GUID сессии от сервера

**Ключевое поведение:**

- Самый простой метод подключения (только имя кластера)
- Внутри использует connect_by_server_name
- Блокируется до готовности терминала или тайм-аута
- Идеально для переподключения или смены счетов

---

## ⚡ Под капотом

```
MT5Sugar.quick_connect()
    ↓ проверяет учётные данные
    ↓ вызывает
MT5Account.connect_by_server_name()
    ↓ gRPC protobuf
AccountHelperService.ConnectEx()
    ↓ MT5 Terminal
    ↓ ожидает готовности терминала (тайм-аут 30с)
    ↓ обновляет GUID сессии
```

**Цепочка вызовов:**

1. Sugar обращается к базовому MT5Account
2. Проверяет наличие атрибутов user и password
3. Вызывает Account.connect_by_server_name() с именем кластера
4. Account отправляет gRPC-запрос ConnectEx в терминал
5. Терминал проверяет учётные данные и подключается
6. Ожидает terminal_is_alive с тайм-аутом 30 секунд
7. Обновляет GUID сессии из ответа сервера
8. Возвращает управление при успехе или вызывает исключение

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:340`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:436`

---

## Когда использовать

**Используйте `quick_connect()`, когда:**

- Первое подключение к серверу MT5
- Переподключение после разрыва связи
- Переключение между демо/реальными кластерами
- Простое подключение без сложной настройки

**Не используйте, когда:**

- Нужны пользовательские параметры подключения
- Не знаете имя кластера
- Хотите неблокирующее подключение

---

## 🔗 Примеры

### Пример 1: Базовое подключение

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def connect_simple():
    # Создать account с учётными данными
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    # Подключиться к демо-кластеру FxPro
    await sugar.quick_connect("FxPro-MT5 Demo")

    print("Connected successfully")

    # Проверить подключение
    if sugar.is_connected():
        balance = await sugar.get_balance()
        print(f"Balance: ${balance}")
```

### Пример 2: Подключение с пользовательским тайм-аутом

```python
async def connect_custom_timeout():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    # Разрешить до 60 секунд на готовность терминала
    await sugar.quick_connect(
        cluster_name="ICMarkets-Demo",
        timeout_seconds=60
    )

    print("Connected")
```

### Пример 3: Автоматическое переподключение при сбое

```python
import asyncio

async def connect_with_retry():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    max_retries = 3
    cluster = "FxPro-MT5 Demo"

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Connection attempt {attempt}/{max_retries}...")

            await sugar.quick_connect(cluster)

            print("Connected successfully")
            break

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

            if attempt < max_retries:
                wait_time = attempt * 2  # 2, 4, 6 секунд
                print(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                print("All connection attempts failed")
                raise

    # Проверить подключение
    if await sugar.ping():
        print("Server is responsive")
```

---

## Типичные ошибки

**Ошибка 1: Неправильное имя кластера**
```python
# ОШИБКА: Имя кластера не существует или опечатка
try:
    await sugar.quick_connect("FxPro-MT5-Demo")  # Неправильный дефис
except Exception as e:
    print(e)  # Ошибка подключения
```

**Решение:** Используйте точное имя кластера от брокера
```python
# Возьмите имя кластера из документации вашего брокера
await sugar.quick_connect("FxPro-MT5 Demo")  # Верно
```

**Ошибка 2: Учётные данные не заданы**
```python
# ОШИБКА: MT5Account создан без учётных данных
account = MT5Account(id_=uuid4())  # Нет user/password
service = MT5Service(account)
sugar = MT5Sugar(service)

try:
    await sugar.quick_connect("FxPro-MT5 Demo")
except RuntimeError as e:
    print(e)  # "Cannot connect: credentials not accessible"
```

**Решение:** Всегда используйте create() с учётными данными
```python
account = MT5Account.create(
    user=591129415,
    password="your_password",
    grpc_server="mt5.mrpc.pro:443"
)
```

**Ошибка 3: Необработанный сбой подключения**

```python
# Нет обработки ошибок
await sugar.quick_connect("FxPro-MT5 Demo")
# При сбое программа аварийно завершится
```

**Решение:** Оберните в try-except
```python
try:
    await sugar.quick_connect("FxPro-MT5 Demo")
    print("Connected")
except Exception as e:
    print(f"Connection failed: {e}")
    # Обработать корректно
```

---

## Полезные советы

**Совет 1: Храните имя кластера в конфигурации**
```python
# config.py
CLUSTER_NAME = "FxPro-MT5 Demo"
CONNECT_TIMEOUT = 30

# main.py
from config import CLUSTER_NAME, CONNECT_TIMEOUT

await sugar.quick_connect(CLUSTER_NAME, CONNECT_TIMEOUT)
```

**Совет 2: Проверяйте подключение после подключения**
```python
await sugar.quick_connect("FxPro-MT5 Demo")

# Проверить и канал, и сервер
assert sugar.is_connected(), "Channel not connected"
assert await sugar.ping(), "Server not responding"

print("Fully connected and verified")
```

**Совет 3: Переключение между демо и реальным счётом**
```python
# Подключиться к демо
await sugar.quick_connect("FxPro-MT5 Demo")
print("Trading on DEMO")

# Позже: переключиться на реальный (при использовании другого счёта)
# Примечание: нужно создать новый MT5Account с реальными учётными данными
# quick_connect() использует существующие учётные данные
```

**Совет 4: Используйте контекст для автоматической очистки**

```python
async def trade_session():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    try:
        await sugar.quick_connect("FxPro-MT5 Demo")

        # Выполнить торговые операции
        balance = await sugar.get_balance()
        print(f"Balance: ${balance}")

    finally:
        # Очистка при необходимости
        print("Session ended")
```

---

## 📚 См. также

- [is_connected](is_connected.md) - Проверить состояние подключения
- [ping](ping.md) - Проверить отзывчивость сервера
