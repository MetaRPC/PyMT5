# Проверка состояния подключения (`is_connected`)

> **Sugar-метод:** Проверяет, активно ли gRPC-соединение с сервером MT5.

**Информация об API:**

* **Метод:** `sugar.is_connected()`
* **Возвращает:** `True`, если подключение установлено, иначе `False`
* **Слой:** HIGH (MT5Sugar)
* **Тип:** Синхронный метод (без async/await)

---

## Сигнатура метода

```python
def is_connected(self) -> bool
```

---

## 🔽 Входные параметры

Нет

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `bool` | `True`, если gRPC-канал в состоянии READY или IDLE, иначе `False` |

---

## 🏛️ Основное

**Что делает:**

- Проверяет состояние подключения gRPC-канала
- Возвращает True для состояний READY или IDLE
- Возвращает False, если канал недоступен или находится в состоянии ошибки
- Не пытается установить подключение (неблокирующая проверка)

**Ключевое поведение:**

- Синхронный метод (await не нужен)
- Безопасно вызывать в любой момент (перехватывает исключения)
- Не изменяет состояние подключения
- Возвращает False при любом исключении

---

## ⚡ Под капотом

```
MT5Sugar.is_connected()
    ↓ обращается к
MT5Service.get_account()
    ↓ проверяет состояние канала
grpc.Channel.get_state(try_to_connect=False)
    ↓ возвращает
ChannelConnectivity enum (READY/IDLE/...)
```

**Цепочка вызовов:**

1. Sugar обращается к базовому MT5Account через сервис
2. Проверяет, есть ли у account атрибут channel
3. Вызывает channel.get_state() с try_to_connect=False
4. Сравнивает состояние с READY или IDLE
5. Возвращает True, если подключено, иначе False
6. Перехватывает все исключения и возвращает False

**Связанные файлы:**
- Sugar: `src/pymt5/mt5_sugar.py:291`

---

## Когда использовать

**Используйте `is_connected()`, когда:**

- Проверяете подключение перед операциями
- Реализуете мониторинг состояния подключения
- Проверяете состояние перед критичными операциями
- Строите логику повторного подключения

**Не используйте, когда:**

- Хотите выполнить пинг сервера (используйте `ping()`)
- Нужно проверить фактическую отзывчивость сервера
- Хотите установить подключение (используйте quick_connect())

---

## 🔗 Примеры

### Пример 1: Базовая проверка подключения

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

# Создать экземпляр MT5Sugar
account = MT5Account.create(
    user=591129415,
    password="your_password",
    grpc_server="mt5.mrpc.pro:443"
)
service = MT5Service(account)
sugar = MT5Sugar(service)

# Проверить подключение (await не нужен - синхронно)
if sugar.is_connected():
    print("Connected to MT5 server")
else:
    print("Not connected")

# Вывод:
# Connected to MT5 server
```

### Пример 2: Условные операции

```python
async def safe_get_balance():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    # Сначала подключиться
    await sugar.quick_connect("FxPro-MT5 Demo")

    # Проверить перед операцией
    if sugar.is_connected():
        balance = await sugar.get_balance()
        print(f"Balance: ${balance}")
    else:
        print("Cannot get balance - not connected")
```

### Пример 3: Цикл мониторинга подключения

```python
import asyncio

async def monitor_connection():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Проверять подключение каждые 10 секунд
    while True:
        if sugar.is_connected():
            print("Connection OK")
        else:
            print("Connection lost - reconnecting...")
            await sugar.quick_connect("FxPro-MT5 Demo")

        await asyncio.sleep(10)
```

---

## Типичные ошибки

**Ошибка 1: Путаница с ping**
```python
# is_connected() проверяет только состояние канала, а не работоспособность сервера
if sugar.is_connected():
    # Канал открыт, но сервер может не отвечать
    pass
```

**Решение:** Используйте ping() для фактической проверки работоспособности сервера
```python
# Проверить состояние канала
channel_ok = sugar.is_connected()

# Проверить отзывчивость сервера
server_ok = await sugar.ping()

if channel_ok and server_ok:
    print("Fully connected and responsive")
```

**Ошибка 2: Использование await (метод синхронный)**
```python
# ОШИБКА: is_connected() НЕ является async
connected = await sugar.is_connected()  # SyntaxError
```

**Решение:** Вызывайте без await
```python
# Верно: синхронный вызов
connected = sugar.is_connected()
```

**Ошибка 3: Предположение, что False означает постоянный сбой**
```python
if not sugar.is_connected():
    print("Connection permanently lost")
    # Не обязательно верно - возможно, идёт инициализация
```

**Решение:** Сочетайте с логикой повтора
```python
if not sugar.is_connected():
    print("Not connected - attempting to connect")
    await sugar.quick_connect("FxPro-MT5 Demo")
```

---

## Полезные советы

**Совет 1: Быстрая предварительная проверка**
```python
# Проверить перед критичными операциями
if not sugar.is_connected():
    await sugar.quick_connect("FxPro-MT5 Demo")

# Продолжить операции
balance = await sugar.get_balance()
```

**Совет 2: Используйте в assertion для отладки**
```python
# Убедиться в подключении в тестах
assert sugar.is_connected(), "Must be connected before test"

# Запустить тестовые операции
await sugar.buy_market(volume=0.01)
```

**Совет 3: Логируйте изменения состояния подключения**
```python
previous_state = sugar.is_connected()

while True:
    current_state = sugar.is_connected()

    if current_state != previous_state:
        if current_state:
            print("Connection restored")
        else:
            print("Connection lost")

        previous_state = current_state

    await asyncio.sleep(5)
```

---

## 📚 См. также

- [ping](ping.md) - Проверить отзывчивость сервера
- [quick_connect](quick_connect.md) - Подключиться к кластеру MT5
