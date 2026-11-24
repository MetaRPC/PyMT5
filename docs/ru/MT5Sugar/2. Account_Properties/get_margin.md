# Get Used Margin (`get_margin`)

> **Sugar method:** Возвращает текущую используемую маржу (заблокированные средства) в одну строку.

**Информация об API:**

* **Method:** `sugar.get_margin()`
* **Returns:** Используемая маржа как `float`
* **Layer:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_margin(self) -> float
```

---

## ℹ️ Вход / Выход

| Вход | Тип | Описание |
|-------|------|-------------|
| *Нет* | - | Параметры не требуются |

| Выход | Тип | Описание |
|--------|------|-------------|
| `margin` | `float` | Текущая используемая маржа |

---

## 🏛️ Основы

* **Что это:** Сумма маржи, заблокированной всеми вашими открытыми позициями.
* **Зачем это нужно:** Проверить доступную маржу перед открытием новых сделок, рассчитать уровень маржи.
* **Формула:** Общая маржа, необходимая для поддержания текущих открытых позиций.

---

## ⚡ Под капотом

```
MT5Sugar.get_margin()
    ↓ calls
MT5Service.get_account_double(ACCOUNT_MARGIN)
    ↓ calls
MT5Account.account_info_double(property_id=ACCOUNT_MARGIN)
    ↓ gRPC protobuf
AccountInformationService.AccountInfoDouble(property_id=10)
    ↓ MT5 Terminal
```

**Что происходит:**

1. **Sugar Layer:** Вызывает сервис с константой ACCOUNT_MARGIN
2. **Service Layer:** Вызывает счёт с property_id для маржи
3. **Account Layer:** Вызов gRPC с конкретным enum свойства
4. **Result:** Используемая маржа как float

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:406`
- Service: `src/pymt5/mt5_service.py:298`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:578`

---

## Когда использовать

**Перед торговлей** — проверить, есть ли свободная маржа для новых позиций

**Управление рисками** — мониторить использование маржи относительно размера счёта

**Расчёт уровня маржи** — рассчитать (Equity / Margin) * 100

**Определение размера позиции** — убедиться, что вы не превышаете лимиты маржи

**Несколько позиций** — отслеживать суммарное обязательство по марже

---

## 🔗 Примеры использования

### 1) Базовое использование

```python
margin = await sugar.get_margin()
print(f"Used Margin: ${margin:.2f}")
# Вывод: Used Margin: $500.00
```

---

### 2) Проверка доступной маржи перед торговлей

```python
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = equity - margin

print(f"Equity:        ${equity:.2f}")
print(f"Used Margin:   ${margin:.2f}")
print(f"Free Margin:   ${free_margin:.2f}")

if free_margin < 100:
    print("Not enough free margin to trade")
```

---

### 3) Расчёт уровня маржи

```python
equity = await sugar.get_equity()
margin = await sugar.get_margin()

if margin > 0:
    margin_level = (equity / margin) * 100
    print(f"Margin Level: {margin_level:.2f}%")

    if margin_level < 200:
        print("WARNING: Low margin level")
    elif margin_level < 100:
        print("DANGER: Stop-out risk!")
else:
    print("No open positions")
```

---

## Связанные методы

**Методы, связанные с маржой:**

* `get_free_margin()` — доступная маржа для торговли
* `get_margin_level()` — уровень маржи в процентах
* `get_equity()` — текущая стоимость счёта
* `calculate_required_margin()` — рассчитать маржу для запланированной сделки
* `get_account_info()` — все данные счёта, включая маржу

**Расчёт маржи:**

```python
# Ручной расчёт
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = equity - margin
margin_level = (equity / margin * 100) if margin > 0 else 0

# Или используйте специальные методы
free_margin = await sugar.get_free_margin()
margin_level = await sugar.get_margin_level()
```

---

## Частые ошибки

### 1) Путаница маржи с балансом

```python
# НЕВЕРНО - маржа это не баланс
margin = await sugar.get_margin()
print(f"I have ${margin:.2f}")  # Это заблокировано, а не доступно!

# ВЕРНО - используйте баланс или средства (equity)
balance = await sugar.get_balance()
print(f"Balance: ${balance:.2f}")
```

### 2) Отсутствие проверки маржи перед торговлей

```python
# НЕВЕРНО - открытие сделки без проверки маржи
ticket = await sugar.buy_market("EURUSD", 1.0)  # Может не сработать!

# ВЕРНО - сначала проверьте свободную маржу
free_margin = await sugar.get_free_margin()
required_margin = await sugar.calculate_required_margin("EURUSD", 1.0)

if free_margin >= required_margin:
    ticket = await sugar.buy_market("EURUSD", 1.0)
else:
    print("Insufficient margin")
```

---

## Советы профи

1. **Нулевая маржа = нет позиций** — маржа равна 0, когда нет открытых позиций

2. **Маржа растёт с кредитным плечом** — меньшее кредитное плечо = больше требуемой маржи

3. **Следите за уровнем маржи** — держите уровень маржи выше 200% для безопасности

4. **Используйте get_free_margin()** — проще, чем расчёт equity - margin

5. **Рассчитывайте перед торговлей** — используйте `calculate_required_margin()` для планирования сделок

---

## 📚 См. также

- [get_free_margin](get_free_margin.md) — получить доступную маржу для торговли
- [get_margin_level](get_margin_level.md) — получить уровень маржи в процентах
- [calculate_required_margin](../10.%20Risk_Management/calculate_required_margin.md) — рассчитать требуемую маржу для сделки
