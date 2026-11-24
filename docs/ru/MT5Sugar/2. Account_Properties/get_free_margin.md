# Get Free Margin (`get_free_margin`)

> **Sugar method:** Возвращает доступную маржу для новых позиций в одну строку.

**Информация об API:**

* **Method:** `sugar.get_free_margin()`
* **Returns:** Свободная маржа как `float`
* **Layer:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_free_margin(self) -> float
```

---

## ℹ️ Вход / Выход

| Вход | Тип | Описание |
|-------|------|-------------|
| *Нет* | - | Параметры не требуются |

| Выход | Тип | Описание |
|--------|------|-------------|
| `free_margin` | `float` | Доступная маржа для торговли |

---

## 🏛️ Основы

* **Что это:** Средства (equity) минус используемая маржа — средства, доступные для открытия новых позиций.
* **Зачем это нужно:** Убедиться, что у вас достаточно маржи перед открытием сделок.
* **Формула:** Free Margin = Equity - Used Margin

---

## ⚡ Под капотом

```
MT5Sugar.get_free_margin()
    ↓ calls
MT5Service.get_account_double(ACCOUNT_MARGIN_FREE)
    ↓ calls
MT5Account.account_info_double(property_id=ACCOUNT_MARGIN_FREE)
    ↓ gRPC protobuf
AccountInformationService.AccountInfoDouble(property_id=11)
    ↓ MT5 Terminal
```

**Что происходит:**

1. **Sugar Layer:** Вызывает сервис с константой ACCOUNT_MARGIN_FREE
2. **Service Layer:** Запрашивает конкретное свойство у счёта
3. **Account Layer:** Вызов gRPC с enum свойства
4. **Result:** Доступная маржа, рассчитанная MT5

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:417`
- Service: `src/pymt5/mt5_service.py:298`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:578`

---

## Когда использовать

**Перед торговлей** — всегда проверяйте перед открытием новых позиций

**Определение размера позиции** — рассчитать максимальный безопасный объём

**Управление рисками** — обеспечить достаточный буфер маржи

**Несколько ордеров** — проверить маржу для запланированных сделок

**Предотвращение сбоев** — избежать ошибок «not enough money»

---

## 🔗 Примеры использования

### 1) Проверка перед открытием позиции

```python
free_margin = await sugar.get_free_margin()

if free_margin < 100:
    print("Insufficient margin to trade")
    return

# Можно безопасно продолжать
ticket = await sugar.buy_market("EURUSD", 0.1)
```

---

### 2) Расчёт максимального размера позиции

```python
free_margin = await sugar.get_free_margin()
# Предположим, 1 лот требует ~1000 маржи
max_lots = free_margin / 1000

print(f"Free Margin:  ${free_margin:.2f}")
print(f"Max Lots:     {max_lots:.2f}")

# Лучше: используйте calculate_position_size()
lot_size = await sugar.calculate_position_size("EURUSD", 2.0, 50)
```

---

### 3) Мониторинг здоровья маржи

```python
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = await sugar.get_free_margin()

margin_level = (equity / margin * 100) if margin > 0 else 0

print(f"Equity:       ${equity:.2f}")
print(f"Used Margin:  ${margin:.2f}")
print(f"Free Margin:  ${free_margin:.2f}")
print(f"Margin Level: {margin_level:.0f}%")

if free_margin < 500:
    print("WARNING: Low free margin!")
```

---

## Связанные методы

**Методы, связанные с маржой:**

* `get_margin()` — текущая используемая маржа
* `get_equity()` — общая стоимость счёта
* `get_margin_level()` — уровень маржи в процентах
* `calculate_required_margin()` — рассчитать маржу для запланированной сделки
* `can_open_position()` — проверить, возможна ли сделка

**Паттерн проверки маржи:**
```python
# Ручная проверка
free_margin = await sugar.get_free_margin()
required_margin = await sugar.calculate_required_margin("EURUSD", 1.0)

if free_margin >= required_margin:
    # Можно безопасно торговать
    pass

# Или используйте хелпер
can_trade = await sugar.can_open_position("EURUSD", 1.0)
```

---

## Частые ошибки

### 1) Отсутствие проверки маржи перед торговлей

```python
# НЕВЕРНО - торговля без проверки маржи
ticket = await sugar.buy_market("EURUSD", 1.0)  # Может не сработать!

# ВЕРНО - сначала проверьте свободную маржу
free_margin = await sugar.get_free_margin()
if free_margin >= 1000:  # Грубая оценка
    ticket = await sugar.buy_market("EURUSD", 1.0)
```

### 2) Использование устаревшего значения маржи

```python
# НЕВЕРНО - проверка один раз и переиспользование
free_margin = await sugar.get_free_margin()
# ... позже ...
ticket = await sugar.buy_market("EURUSD", 0.1)  # Маржа могла измениться!

# ВЕРНО - проверяйте перед каждой сделкой
free_margin = await sugar.get_free_margin()
if free_margin >= 100:
    ticket = await sugar.buy_market("EURUSD", 0.1)
```

---

## Советы профи

1. **Всегда проверяйте** — никогда не торгуйте без проверки свободной маржи

2. **Используйте calculate_required_margin()** — точнее, чем грубые оценки

3. **Держите буфер** — не используйте 100% свободной маржи (оставьте 20-30% запаса)

4. **Маржа меняется** — свободная маржа обновляется с каждым ценовым тиком

5. **Используйте can_open_position()** — объединяет проверку маржи с другими проверками

---

## 📚 См. также

- [get_margin](get_margin.md) — получить используемую маржу
- [get_margin_level](get_margin_level.md) — получить уровень маржи в процентах
- [calculate_required_margin](../10.%20Risk_Management/calculate_required_margin.md) — рассчитать требуемую маржу для сделки
