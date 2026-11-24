# Get Account Balance (`get_balance`)

> **Sugar method:** Возвращает текущий баланс счёта в одну строку.

**Информация об API:**

* **Method:** `sugar.get_balance()`
* **Returns:** Текущий баланс как `float`
* **Layer:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_balance(self) -> float
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

* **Что это:** Получает баланс вашего счёта — деньги, которые у вас есть до учёта открытых позиций.
* **Зачем это нужно:** Проверить доступные средства, рассчитать суммы риска, проверить перед торговлей.
* **Проверка на разумность:** Balance <= Equity (средства (equity) включают плавающую P/L).

---

## ⚡ Под капотом

Этот метод демонстрирует трёхуровневую архитектуру в действии:

```
MT5Sugar.get_balance()
    ↓ calls
MT5Service.get_account_summary()
    ↓ calls
MT5Account.account_summary()
    ↓ gRPC protobuf
AccountHelperService.AccountSummary()
    ↓ MT5 Terminal
```

**Что происходит:**

1. **Sugar Layer:** Простой async-метод без параметров
2. **Service Layer:** Вызывает `account_summary()` и извлекает поле `balance` из dataclass AccountSummary
3. **Account Layer:** Делает вызов gRPC к терминалу MT5, возвращает объект protobuf Data
4. **Result:** Чистое значение float, готовое к использованию

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:386`
- Service: `src/pymt5/mt5_service.py:254`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:540`

---

## Когда использовать

**Перед торговлей** — проверить, достаточно ли у вас средств

**Расчёт риска** — рассчитать размер позиции на основе баланса

**Мониторинг** — отслеживать стоимость счёта

**Отчётность** — генерировать отчёты по счёту

**Валидация** — убедиться в достаточности средств для торговли

---

## 🔗 Примеры использования

### 1) Базовое использование

```python
balance = await sugar.get_balance()
print(f"Balance: ${balance:.2f}")
# Вывод: Balance: $10000.00
```

---

### 2) Проверка перед торговлей

```python
balance = await sugar.get_balance()

if balance < 1000:
    print("Insufficient balance for trading")
    return

print("Balance sufficient - proceeding with trade")
```

---

### 3) Расчёт суммы риска

```python
balance = await sugar.get_balance()
risk_percent = 2.0

risk_amount = balance * risk_percent / 100.0

print(f"Balance:     ${balance:.2f}")
print(f"Risk (2%):   ${risk_amount:.2f}")

# Лучше: используйте calculate_position_size()
lot_size = await sugar.calculate_position_size("EURUSD", risk_percent, 50)
print(f"Lot size:    {lot_size:.2f}")
```

---

## Связанные методы

**Другие методы баланса:**

* `get_equity()` — баланс + плавающая P/L
* `get_margin()` — используемая маржа
* `get_free_margin()` — доступная маржа для торговли
* `get_floating_profit()` — текущая плавающая прибыль/убыток
* `get_account_info()` — получить все данные счёта за один раз

**Рекомендуемый паттерн:**

```python
# Вместо раздельного вызова get_balance, get_equity и т.д.:
account_info = await sugar.get_account_info()
# Теперь у вас есть: balance, equity, margin, free_margin, profit и т.д.
```

---

## Частые ошибки

### 1) Путаница между балансом и средствами (equity)

```python
# НЕВЕРНО - используется баланс, когда нужны средства (equity)
balance = await sugar.get_balance()  # Не учитывает открытые позиции!

# ВЕРНО - используйте средства (equity) для полной стоимости счёта
equity = await sugar.get_equity()  # Включает плавающую P/L
```

### 2) Отсутствие await

```python
# НЕВЕРНО - забыт await
balance = sugar.get_balance()  # Возвращает корутину, а не float!

# ВЕРНО - всегда await для async-методов
balance = await sugar.get_balance()
```

---

## Советы профи

1. **Используйте get_account_info()** — эффективнее, чем вызов нескольких методов

2. **Баланс для расчёта риска** — используйте баланс (не средства (equity)) для определения размера позиции

3. **Проверяйте перед торговлей** — всегда проверяйте достаточность баланса

4. **Отслеживайте изменения** — следите за балансом для измерения результативности

5. **Средства (equity) — это реальность** — баланс историчен, средства (equity) актуальны

---

## 📚 См. также

- [get_equity](get_equity.md) — получить средства (equity) (баланс + плавающая P/L)
- [get_account_info](get_account_info.md) — получить все данные счёта за один раз
