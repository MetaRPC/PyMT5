# Balance Property (`balance`)

> **Async Property:** Альтернативный синтаксис для `get_balance()`.

**Информация об API:**

* **Property:** `await sugar.balance`
* **Returns:** Текущий баланс как `float`
* **Layer:** HIGH (MT5Sugar)

---

## Сигнатура property

```python
@property
async def balance(self) -> float
```

---

## ℹ️ Вход / Выход

| Вход | Тип | Описание |
|-------|------|-------------|
| *Нет* | - | Параметры не требуются |

| Выход | Тип | Описание |
|--------|------|-------------|
| `balance` | `float` | Текущий баланс счёта |

---

## 🏛️ Основы

* **Что это:** Синтаксис property в Python для получения баланса.
* **Зачем использовать:** Более чистый и питонический синтаксис, чем `get_balance()`.
* **Разница:** `await sugar.balance` против `await sugar.get_balance()` — оба идентичны.

---

## ⚡ Под капотом

```
await sugar.balance
    ↓ internally calls
sugar.get_balance()
    ↓ calls
MT5Service.get_account_summary()
    ↓ calls
MT5Account.account_summary()
    ↓ gRPC protobuf
MT5 Terminal
```

**Что происходит:**

1. **Property:** Перенаправляет на метод `get_balance()`
2. **Та же цепочка:** Идентично прямому вызову `get_balance()`

**Связанные файлы:**
- Sugar: `src/pymt5/mt5_sugar.py:451`

---

## Когда использовать

**Более чистый синтаксис** — когда вы предпочитаете стиль property

**Быстрый доступ** — более короткий код для проверки баланса

**Питонический код** — более естественный синтаксис Python

---

## 🔗 Примеры использования

### 1) Синтаксис property против метода

```python
# Используем property (чище)
balance = await sugar.balance
print(f"Balance: ${balance:.2f}")

# Используем метод (традиционно)
balance = await sugar.get_balance()
print(f"Balance: ${balance:.2f}")

# Оба ИДЕНТИЧНЫ
```

---

### 2) Использование в выражениях

```python
# Синтаксис property выглядит чище
if await sugar.balance < 1000:
    print("Low balance")

# против синтаксиса метода
if await sugar.get_balance() < 1000:
    print("Low balance")
```

---

### 3) Несколько property вместе

```python
# Очень чисто с property
balance = await sugar.balance
equity = await sugar.equity
profit = await sugar.profit

print(f"Balance: ${balance:.2f}")
print(f"Equity:  ${equity:.2f}")
print(f"Profit:  ${profit:+.2f}")
```

---

## Связанные property

**Другие async property:**

* `equity` — текущие средства (equity)
* `margin` — используемая маржа
* `free_margin` — свободная маржа
* `margin_level` — уровень маржи %
* `profit` — плавающая прибыль/убыток

**Эквивалентные методы:**

* `get_balance()` — тот же результат, другой синтаксис
* `get_account_info()` — получить все данные счёта за один раз

---

## Частые ошибки

### 1) Забытый await

```python
# НЕВЕРНО - пропущен await
balance = sugar.balance  # Возвращает корутину!

# ВЕРНО - всегда await для property
balance = await sugar.balance
```

### 2) Попытка присвоить значение property

```python
# НЕВЕРНО - property доступны только для чтения
sugar.balance = 10000  # Не допускается!

# Property только для ЧТЕНИЯ
balance = await sugar.balance  # Верно
```

---

## Советы профи

1. **Выбирайте свой стиль** — property против методов — оба работают идентично

2. **По-прежнему async** — property нужно await, как и методы

3. **Только для чтения** — нельзя задавать значения через property

4. **Поддержка IDE** — property отображаются в автодополнении

5. **Используйте get_account_info()** — эффективнее для нескольких значений

---

## 📚 См. также

- [get_balance](get_balance.md) — доступ к балансу в стиле метода
- [get_equity](get_equity.md) — получить средства (equity) (баланс + плавающая P/L)
