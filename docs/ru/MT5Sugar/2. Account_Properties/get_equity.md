# Get Account Equity (`get_equity`)

> **Sugar method:** Возвращает текущие средства (equity) (баланс + плавающая P/L) в одну строку.

**Информация об API:**

* **Method:** `sugar.get_equity()`
* **Returns:** Текущие средства (equity) как `float`
* **Layer:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_equity(self) -> float
```

---

## ℹ️ Вход / Выход

| Вход | Тип | Описание |
|-------|------|-------------|
| *Нет* | - | Параметры не требуются |

| Выход | Тип | Описание |
|--------|------|-------------|
| `equity` | `float` | Текущие средства (equity) (баланс + плавающая прибыль) |

---

## 🏛️ Основы

* **Что это:** Текущая стоимость счёта, включая плавающую прибыль/убыток открытых позиций.
* **Зачем это нужно:** Реальная стоимость счёта в реальном времени, расчёт уровня маржи, управление рисками.
* **Формула:** Equity = Balance + Floating Profit - Floating Loss

---

## ⚡ Под капотом

```
MT5Sugar.get_equity()
    ↓ calls
MT5Service.get_account_summary()
    ↓ calls
MT5Account.account_summary()
    ↓ gRPC protobuf
AccountHelperService.AccountSummary()
    ↓ MT5 Terminal
```

**Что происходит:**

1. **Sugar Layer:** Простой async-метод извлекает поле equity
2. **Service Layer:** Возвращает dataclass AccountSummary
3. **Account Layer:** Вызов gRPC к терминалу
4. **Result:** Баланс + P/L всех открытых позиций

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:396`
- Service: `src/pymt5/mt5_service.py:254`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:540`

---

## Когда использовать

**Управление рисками** — рассчитать уровень маржи и доступные средства

**Мониторинг позиций** — отслеживать стоимость счёта в реальном времени

**Предотвращение stop-out** — следить за средствами (equity), чтобы избежать margin call

**Отслеживание результативности** — видеть общую стоимость счёта, включая открытые сделки

**Перед торговлей** — проверить достаточность средств (equity) для новых позиций

---

## 🔗 Примеры использования

### 1) Базовое использование

```python
equity = await sugar.get_equity()
print(f"Equity: ${equity:.2f}")
# Вывод: Equity: $10250.50
```

---

### 2) Сравнение баланса и средств (equity)

```python
balance = await sugar.get_balance()
equity = await sugar.get_equity()
floating_pl = equity - balance

print(f"Balance:      ${balance:.2f}")
print(f"Equity:       ${equity:.2f}")
print(f"Floating P/L: ${floating_pl:+.2f}")

# Вывод:
# Balance:      $10000.00
# Equity:       $10250.50
# Floating P/L: +$250.50
```

---

### 3) Мониторинг уровня маржи

```python
equity = await sugar.get_equity()
margin = await sugar.get_margin()

if margin > 0:
    margin_level = (equity / margin) * 100
    print(f"Equity:        ${equity:.2f}")
    print(f"Margin:        ${margin:.2f}")
    print(f"Margin Level:  {margin_level:.2f}%")

    if margin_level < 100:
        print("WARNING: Low margin level!")
```

---

## Связанные методы

**Методы стоимости счёта:**

* `get_balance()` — баланс без открытых позиций
* `get_floating_profit()` — только P/L от открытых позиций
* `get_margin()` — используемая маржа
* `get_margin_level()` — уровень маржи в процентах
* `get_account_info()` — все данные счёта за один раз

**Ключевая разница:**
```python
# Баланс: с чего вы начали + закрытые сделки
balance = await sugar.get_balance()

# Средства (equity): баланс + плавающая P/L (проверка реальности)
equity = await sugar.get_equity()

# Разница — это P/L ваших открытых позиций
floating = equity - balance
```

---

## Частые ошибки

### 1) Использование баланса вместо средств (equity) для проверок маржи

```python
# НЕВЕРНО - баланс не отражает открытые позиции
balance = await sugar.get_balance()
if balance < 1000:
    print("Low funds")  # Может быть неверно!

# ВЕРНО - средства (equity) показывают реальную стоимость счёта
equity = await sugar.get_equity()
if equity < 1000:
    print("Low funds")  # Точная проверка
```

### 2) Игнорирование плавающих убытков

```python
# НЕВЕРНО - проверяется только баланс
balance = await sugar.get_balance()
print(f"I have ${balance:.2f}")  # Вводит в заблуждение, если позиции убыточны

# ВЕРНО - проверяйте средства (equity) для реальной картины
equity = await sugar.get_equity()
print(f"Real value: ${equity:.2f}")  # Показывает истинную ситуацию
```

---

## Советы профи

1. **Средства (equity) — это реальность** — всегда используйте средства (equity) для текущей стоимости счёта

2. **Формула уровня маржи** — (Equity / Margin) * 100

3. **Следите за stop-out** — брокеры закрывают позиции, когда уровень маржи падает ниже порога (обычно 20-50%)

4. **Используйте get_account_info()** — получить средства (equity), баланс, маржу за один раз

5. **Отслеживайте изменения средств (equity)** — следите за средствами (equity) во времени для измерения результативности

---

## 📚 См. также

- [get_balance](get_balance.md) — получить текущий баланс счёта
- [get_floating_profit](get_floating_profit.md) — получить текущую плавающую прибыль/убыток
- [get_margin_level](get_margin_level.md) — получить уровень маржи в процентах
