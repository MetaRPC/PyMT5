## symbol_select — Как это работает

---

## 📌 Обзор

Этот пример показывает, как использовать низкоуровневый асинхронный метод `symbol_select()` для **управления содержимым «Обзора рынка» (Market Watch)** — добавления и удаления символов.

В примере реализована практическая задача: очистка «Обзора рынка» от всех символов, кроме заранее заданного списка.

---

## Сигнатура метода

```python
async def symbol_select(
    symbol: str,
    select: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Ключевые моменты:

* Метод асинхронный и вызывается с `await`
* `symbol` — имя торгового символа
* `select=True` добавляет символ в «Обзор рынка» (Market Watch)
* `select=False` удаляет символ из «Обзора рынка» (Market Watch)
* Метод возвращает результат операции

---

## 🧩 Пример кода — Очистка «Обзора рынка»

```python
async def cleanup_market_watch(account: MT5Account, keep_symbols: list[str]):
    total_data = await account.symbols_total(selected_only=True)
    total = total_data.total

    removed = []
    for i in range(total):
        name_data = await account.symbol_name(index=i, selected=True)
        symbol = name_data.name

        if symbol not in keep_symbols:
            data = await account.symbol_select(symbol=symbol, select=False)
            if data.success:
                removed.append(symbol)
                print(f"Removed: {symbol}")

    print(f"Removed {len(removed)} symbols from Market Watch")
    return removed
```

Этот пример демонстрирует практическое использование `symbol_select()` для управления списком отображаемых символов.

---

## 🟢 Подробное объяснение

---

### 1️⃣ Получение количества выбранных символов

```python
total_data = await account.symbols_total(selected_only=True)
total = total_data.total
```

На этом шаге:

* запрашивается количество символов в «Обзоре рынка» (Market Watch)
* это значение используется как граница перебора

---

### 2️⃣ Перебор символов по индексу

```python
for i in range(total):
```

Код последовательно перебирает все символы, добавленные в «Обзор рынка» (Market Watch) в данный момент.

---

### 3️⃣ Получение имени символа

```python
name_data = await account.symbol_name(index=i, selected=True)
symbol = name_data.name
```

На этом шаге:

* имя символа получается по индексу
* имя используется для принятия решения об удалении

---

### 4️⃣ Удаление символа из «Обзора рынка»

```python
data = await account.symbol_select(symbol=symbol, select=False)
```

Если символа нет в списке `keep_symbols`:

* `symbol_select()` вызывается с `select=False`
* терминалу отправляется команда на удаление символа из «Обзора рынка» (Market Watch)

---

### 5️⃣ Проверка результата операции

```python
if data.success:
```

Метод возвращает объект с флагом `success`:

* `True` — операция выполнена успешно
* `False` — операция не выполнена

Пользовательский код решает, как интерпретировать результат.

---

## Роль низкоуровневого метода

Чёткая граница ответственности:

**`symbol_select()`**:

* добавляет или удаляет символ из «Обзора рынка» (Market Watch)
* выполняет одну конкретную операцию
* возвращает результат операции

**`cleanup_market_watch()`**:

* определяет, какие символы оставить
* управляет перебором списка
* принимает решение об удалении
* агрегирует результат

---

## Итог

Этот пример иллюстрирует паттерн управления состоянием через низкоуровневый API:

> **получить текущее состояние → принять решение → изменить состояние → проверить результат**

Метод `symbol_select()` выполняет атомарную операцию добавления или удаления символа, а вся логика управления «Обзором рынка» (Market Watch) реализуется на стороне пользовательского кода.
