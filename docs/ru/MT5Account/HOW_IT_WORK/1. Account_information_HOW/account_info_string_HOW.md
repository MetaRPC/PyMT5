## account_info_string — Как это работает

---

## 📌 Обзор

Этот пример демонстрирует, как получить **строковое свойство торгового счёта** с помощью низкоуровневого асинхронного метода `account_info_string()`.

Метод используется для запроса значений, которые в MetaTrader представлены в виде строк: имя сервера, имя счёта, валюта депозита и другие текстовые параметры.

Метод выполняет **один запрос** и возвращает **одно строковое значение (`str`)**.

---

## Сигнатура метода

```python
async def account_info_string(
    property_id: AccountInfoStringPropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> str
```

Ключевые моменты:

* Метод асинхронный и должен вызываться с `await`
* `property_id` указывает, **какое строковое свойство** запрашивать
* `deadline` и `cancellation_event` управляют временем выполнения
* Результат возвращается как обычная строка Python (`str`)

---

## 🧩 Пример кода — Проверка подключения к серверу

```python
async def verify_server_connection(account: MT5Account, expected_server: str) -> bool:
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    server = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline=deadline
    )

    if server.lower() != expected_server.lower():
        print(f"[WARNING] Connected to {server}, expected {expected_server}")
        return False

    print(f"[OK] Confirmed: Connected to {server}")
    return True
```

В этом примере `account_info_string()` используется для получения имени сервера и последующей проверки того, что счёт подключён к ожидаемой торговой среде.

---

## 🟢 Подробное объяснение

---

### 1️⃣ Запрос строкового свойства

```python
server = await account.account_info_string(
    property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
    deadline=deadline
)
```

На этом шаге запрашивается одно строковое свойство счёта.

* `ACCOUNT_SERVER` указывает, **какое значение получить**
* Метод асинхронно ожидает ответа
* Результат — обычная строка Python

Что здесь НЕ происходит:

* Нет валидации содержимого строки
* Нет нормализации регистра
* Нет интерпретации значения

Метод просто возвращает текстовое значение, полученное от терминала.

---

### 2️⃣ Работа с полученной строкой

```python
if server.lower() != expected_server.lower():
```

После получения значения начинается прикладная логика пользователя.

В этом примере:

* `server` — фактическое имя сервера, полученное от терминала
* `expected_server` — имя сервера, ожидаемое пользователем или стратегией

Оба значения приводятся к нижнему регистру, чтобы сравнение не зависело от регистра.

---

### 3️⃣ Реакция на результат проверки

```python
print(f"[WARNING] Connected to {server}, expected {expected_server}")
return False
```

Если сервер не совпадает:

* Выводится предупреждение
* Функция возвращает `False`

Это осознанное решение в прикладном коде. Сам метод `account_info_string()`:

* Не знает, какой сервер считается правильным
* Не принимает решений о корректности подключения

---

```python
print(f"[OK] Confirmed: Connected to {server}")
return True
```

Если сервер совпадает:

* Выводится подтверждение
* Функция возвращает `True`

---

## Итог

В этом примере `account_info_string()` используется как простой источник строковых параметров счёта.

Метод возвращает одно строковое значение, тогда как вся логика проверки и реакции на результат полностью находится в вызывающем коде.
