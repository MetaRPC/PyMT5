## account_info_integer — Как это работает

---

## 📌 Обзор

Этот пример показывает, как получить **целочисленные свойства счёта** с помощью низкоуровневого асинхронного метода `account_info_integer()`.

Метод используется для запроса значений, которые в MetaTrader представлены как целые числа: разрешена ли торговля, размер кредитного плеча, логин счёта, торговый режим и другие флаги или параметры.

В отличие от `account_info_double()`, этот метод всегда возвращает **целое число (`int`)**.

---

## Сигнатура метода

```python
async def account_info_integer(
    property_id: AccountInfoIntegerPropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> int
```

**Ключевые моменты:**

* Метод асинхронный и вызывается с `await`.
* `property_id` указывает, **какое целочисленное свойство** счёта запрашивать.
* `deadline` и `cancellation_event` управляют временем выполнения вызова.
* Результат возвращается как обычный Python `int`.

---

## 🧩 Пример кода — Предварительная проверка счёта перед торговлей

```python
async def validate_account_for_trading(account: MT5Account) -> bool:
    deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

    # Проверка: разрешена ли торговля на счёте
    trade_allowed = await account.account_info_integer(
        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_ALLOWED,
        deadline
    )

    if not trade_allowed:
        print("[ERROR] Trading is disabled on this account")
        return False

    # Проверка: корректно ли настроено кредитное плечо
    leverage = await account.account_info_integer(
        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE,
        deadline
    )

    if leverage < 1:
        print("[ERROR] Invalid leverage setting")
        return False

    print(f"[OK] Account ready to trade (Leverage: 1:{leverage})")
    return True
```

В этом примере `account_info_integer()` используется как источник **флагов и параметров**, необходимых для базовой проверки готовности счёта к торговле.

---

## 🟢 Подробное объяснение

---

### 1️⃣ Проверка разрешения на торговлю

```python
trade_allowed = await account.account_info_integer(
    account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_ALLOWED,
    deadline
)
```

Здесь выполняется запрос одного целочисленного свойства счёта — флага, который указывает, разрешена ли торговля.

* метод выполняет асинхронный вызов
* возвращаемое значение — целое число (`int`)

На практике это значение используется как логический флаг:

* `0` — торговля запрещена
* ненулевое значение — торговля разрешена

Сам метод **не интерпретирует** это значение — он только возвращает число.

---

### 2️⃣ Использование значения в прикладной логике

```python
if not trade_allowed:
    print("[ERROR] Trading is disabled on this account")
    return False
```

На этом этапе начинается обычная пользовательская логика:

* значение, полученное из `account_info_integer()`, используется в условии
* когда торговля запрещена, выполнение функции прекращается

Это решение полностью **находится вне зоны ответственности низкоуровневого API**.

---

### 3️⃣ Проверка кредитного плеча

```python
leverage = await account.account_info_integer(
    account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE,
    deadline
)
```

Здесь выполняется второй вызов того же метода, но с другим `property_id`.

Важно:

* каждый вызов запрашивает **ровно одно свойство**
* метод не кэширует значения
* каждое значение извлекается независимо

---

### 4️⃣ Применение проверки

```python
if leverage < 1:
    print("[ERROR] Invalid leverage setting")
    return False
```

Полученное значение используется напрямую:

* сравнивается с ожидаемым порогом
* когда значение некорректно, выполнение прерывается

Как и в предыдущем случае:

* метод не знает, какое кредитное плечо считается приемлемым
* интерпретация значения — ответственность вызывающего кода

---

## Итог

В этом примере `account_info_integer()` используется как простой источник целочисленных параметров счёта.

Метод вызывается несколько раз с разными `property_id`, и вся логика принятия решений строится поверх возвращённых значений.

Такой подход позволяет:

* отделить получение данных от интерпретации
* повторно использовать низкоуровневый API в разных стратегиях
* явно контролировать поведение торговой логики
