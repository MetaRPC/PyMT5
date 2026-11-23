# Get Margin Level (`get_margin_level`)

> **Sugar method:** Возвращает уровень маржи в процентах (Equity/Margin × 100) в одну строку.

**Информация об API:**

* **Method:** `sugar.get_margin_level()`
* **Returns:** Уровень маржи как `float` (проценты)
* **Layer:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_margin_level(self) -> float
```

---

## ℹ️ Вход / Выход

| Вход | Тип | Описание |
|-------|------|-------------|
| *Нет* | - | Параметры не требуются |

| Выход | Тип | Описание |
|--------|------|-------------|
| `margin_level` | `float` | Уровень маржи в процентах |

---

## 🏛️ Основы

* **Что это:** Отношение средств (equity) к используемой марже, выраженное в процентах.
* **Зачем это нужно:** Мониторить здоровье счёта и избегать margin call.
* **Формула:** Margin Level = (Equity / Used Margin) × 100

---

## ⚡ Под капотом

```
MT5Sugar.get_margin_level()
    ↓ calls
MT5Service.get_account_double(ACCOUNT_MARGIN_LEVEL)
    ↓ calls
MT5Account.account_info_double(property_id=ACCOUNT_MARGIN_LEVEL)
    ↓ gRPC protobuf
AccountInformationService.AccountInfoDouble(property_id=12)
    ↓ MT5 Terminal
```

**Что происходит:**

1. **Sugar Layer:** Вызывает сервис с константой ACCOUNT_MARGIN_LEVEL
2. **Service Layer:** Запрашивает свойство уровня маржи
3. **Account Layer:** Вызов gRPC к терминалу
4. **Result:** Предварительно рассчитанный уровень маржи из MT5

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:428`
- Service: `src/pymt5/mt5_service.py:298`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:578`

---

## Когда использовать

**Мониторинг рисков** — непрерывно проверять безопасность счёта

**Предотвращение stop-out** — избегать принудительного закрытия позиций

**Управление позициями** — решать, когда закрывать или сокращать позиции

**Торговые лимиты** — задавать минимальные пороги уровня маржи

**Автоматизированные системы** — запускать оповещения или действия на основе уровня

---

## 🔗 Примеры использования

### 1) Базовая проверка уровня маржи

```python
margin_level = await sugar.get_margin_level()
print(f"Margin Level: {margin_level:.2f}%")

if margin_level < 200:
    print("WARNING: Low margin level")
# Вывод: Margin Level: 450.00%
```

---

### 2) Управление позициями на основе рисков

```python
margin_level = await sugar.get_margin_level()

if margin_level < 100:
    print("CRITICAL: Stop-out imminent!")
    # Закрываем убыточные позиции
    await sugar.close_all_positions()
elif margin_level < 200:
    print("WARNING: Reduce exposure")
    # Закрываем 50% позиций
elif margin_level > 500:
    print("Safe to trade")
```

---

### 3) Полный дашборд маржи

```python
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = await sugar.get_free_margin()
margin_level = await sugar.get_margin_level()

print("=" * 40)
print("MARGIN HEALTH DASHBOARD")
print("=" * 40)
print(f"Equity:        ${equity:>10,.2f}")
print(f"Used Margin:   ${margin:>10,.2f}")
print(f"Free Margin:   ${free_margin:>10,.2f}")
print(f"Margin Level:  {margin_level:>9.2f}%")
print("=" * 40)

if margin_level < 100:
    status = "DANGER"
elif margin_level < 200:
    status = "WARNING"
else:
    status = "HEALTHY"

print(f"Status: {status}")
```

---

## Связанные методы

**Методы анализа маржи:**

* `get_equity()` — общая стоимость счёта
* `get_margin()` — используемая маржа
* `get_free_margin()` — доступная маржа
* `get_balance()` — баланс счёта
* `get_account_info()` — все данные счёта за один раз

**Понимание уровней маржи:**
```python
# Ручной расчёт
equity = await sugar.get_equity()
margin = await sugar.get_margin()
manual_level = (equity / margin * 100) if margin > 0 else 0

# Или получите напрямую из MT5
margin_level = await sugar.get_margin_level()

# Оба должны совпадать
```

---

## Частые ошибки

### 1) Непонимание порогов уровня маржи

```python
# НЕВЕРНО - незнание лимитов брокера
margin_level = await sugar.get_margin_level()
if margin_level < 50:
    print("Need to close positions")  # Слишком поздно!

# ВЕРНО - действуйте заранее
if margin_level < 200:
    print("Reduce exposure now")
elif margin_level < 100:
    print("CRITICAL: Close positions immediately")
```

### 2) Игнорирование случая нулевой маржи

```python
# НЕВЕРНО - деление на ноль при отсутствии позиций
equity = await sugar.get_equity()
margin = await sugar.get_margin()
level = equity / margin * 100  # Ошибка, если margin = 0!

# ВЕРНО - используйте get_margin_level() или сначала проверьте
margin_level = await sugar.get_margin_level()
# Или вручную с проверкой:
level = (equity / margin * 100) if margin > 0 else 0
```

---

## Советы профи

1. **Пороги брокера** — типичные уровни stop-out: 20-50%, margin call: 80-100%

2. **Мониторьте непрерывно** — в реальной торговле проверяйте каждые несколько минут

3. **Настройте оповещения** — запускайте предупреждения на 200%, 150%, 100%

4. **Действуйте заранее** — не ждите margin call — сокращайте позиции на 200%

5. **Ноль = нет позиций** — уровень маржи равен 0, когда нет открытых позиций

---

## 📚 См. также

- [get_margin](get_margin.md) — получить используемую маржу
- [get_free_margin](get_free_margin.md) — получить доступную маржу для торговли
- [get_equity](get_equity.md) — получить средства (equity) (баланс + плавающая P/L)
