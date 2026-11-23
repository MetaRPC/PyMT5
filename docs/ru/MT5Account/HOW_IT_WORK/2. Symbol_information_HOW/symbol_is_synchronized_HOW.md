## symbol_is_synchronized — Как это работает

---

## 📌 Обзор

Этот пример показывает, как использовать низкоуровневый асинхронный метод `symbol_is_synchronized()` для определения того, **готов ли символ к использованию**, и как на его основе реализовать ожидание синхронизации символа с сервером.

Синхронизация символа означает, что:

* терминал загрузил данные по инструменту
* символ доступен для получения котировок, сессий и тиков

До завершения синхронизации многие рыночные методы могут возвращать пустые или некорректные данные.

---

## Сигнатура метода

```python
async def symbol_is_synchronized(
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Ключевые моменты:

* Метод асинхронный и вызывается с `await`
* `symbol` — имя торгового символа
* Метод возвращает объект с флагом синхронизации
* Метод не инициирует синхронизацию, он лишь сообщает текущее состояние

---

## 🧩 Пример кода — Ожидание синхронизации символа

```python
async def ensure_symbol_synchronized(account, symbol: str, max_retries: int = 5) -> bool:
    result = await account.symbol_is_synchronized(symbol)
    if result.synchronized:
        print(f"{symbol} already synchronized")
        return True

    print(f"Selecting {symbol}...")
    await account.symbol_select(symbol, True)

    for attempt in range(max_retries):
        await asyncio.sleep(0.5 * (attempt + 1))

        result = await account.symbol_is_synchronized(symbol)
        if result.synchronized:
            print(f"{symbol} synchronized after {attempt + 1} attempt(s)")
            return True

        print(f"Attempt {attempt + 1}/{max_retries}: still waiting...")

    print(f"Failed to synchronize {symbol} after {max_retries} attempts")
    return False
```

Этот пример демонстрирует типичный паттерн: **проверить → инициировать → ждать → перепроверить**.

---

## 🟢 Подробное объяснение

---

### 1️⃣ Проверка текущего состояния синхронизации

```python
result = await account.symbol_is_synchronized(symbol)
```

На этом шаге:

* выполняется один асинхронный вызов
* сервер сообщает, синхронизирован ли символ
* результат доступен в поле `result.synchronized`

Если значение `True`, дополнительная работа не требуется.

---

### 2️⃣ Выбор символа в терминале

```python
await account.symbol_select(symbol, True)
```

Если символ ещё не синхронизирован:

* он принудительно выбирается (добавляется) в «Обзор рынка» (Market Watch)
* это запускает процесс загрузки данных по символу

Важно: синхронизация не происходит мгновенно.

---

### 3️⃣ Повторные проверки с ожиданием

```python
for attempt in range(max_retries):
    await asyncio.sleep(0.5 * (attempt + 1))
```

Реализовано ожидание с нарастающей задержкой:

* первая попытка — через 0.5 секунды
* далее задержка постепенно увеличивается

Это даёт серверу время завершить загрузку данных.

---

### 4️⃣ Проверка результата после ожидания

```python
result = await account.symbol_is_synchronized(symbol)
if result.synchronized:
```

После каждой паузы:

* выполняется повторная проверка
* если синхронизация завершена, функция возвращает `True`

---

### 5️⃣ Обработка неудачной синхронизации

```python
print(f"Failed to synchronize {symbol} after {max_retries} attempts")
return False
```

Если после всех попыток символ не синхронизирован:

* он считается недоступным
* дальнейшая работа с ним не выполняется

---

## Роль низкоуровневого метода

Чёткая граница ответственности:

**`symbol_is_synchronized()`**:

* сообщает текущее состояние синхронизации символа
* не инициирует загрузку данных
* не ждёт завершения синхронизации

**`ensure_symbol_synchronized()`**:

* решает, что делать при отсутствии синхронизации
* инициирует выбор символа
* реализует ожидание и повторные попытки
* принимает окончательное решение

---

## Итог

Этот пример иллюстрирует типичный паттерн работы с состояниями в низкоуровневом API:

> **проверить состояние → инициировать действие → перепроверить → решение**

Метод `symbol_is_synchronized()` предоставляет только информацию о текущем состоянии, а вся логика ожидания и управления процессом синхронизации реализуется на стороне пользовательского кода.
