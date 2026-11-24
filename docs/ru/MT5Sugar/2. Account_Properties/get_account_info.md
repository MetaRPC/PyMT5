# Get Account Info (`get_account_info`)

> **Sugar method:** Возвращает полную информацию о счёте в виде структурированного dataclass.

**Информация об API:**

* **Method:** `sugar.get_account_info()`
* **Returns:** dataclass `AccountInfo` с 10 полями
* **Layer:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_account_info(self) -> AccountInfo
```

---

## ℹ️ Вход / Выход

| Вход | Тип | Описание |
|-------|------|-------------|
| *Нет* | - | Параметры не требуются |

| Выход | Тип | Описание |
|--------|------|-------------|
| `AccountInfo` | `dataclass` | Полная информация о счёте |

**Поля AccountInfo:**

- `login` (int) — номер счёта
- `balance` (float) — баланс счёта
- `equity` (float) — текущие средства (equity)
- `profit` (float) — плавающая P/L
- `margin` (float) — используемая маржа
- `free_margin` (float) — свободная маржа
- `margin_level` (float) — уровень маржи %
- `leverage` (int) — кредитное плечо счёта
- `currency` (str) — валюта счёта
- `company` (str) — название брокера

---

## 🏛️ Основы

* **Что это:** Единственный метод для получения ВСЕХ данных счёта за один раз.
* **Зачем это нужно:** Эффективнее, чем вызов 10+ отдельных методов.
* **Преимущество:** Один вызов API вместо нескольких запросов.

---

## ⚡ Под капотом

```
MT5Sugar.get_account_info()
    ↓ calls
MT5Service.get_account_summary()
    ↓ calls multiple
MT5Account.account_summary() + account_info_double() × 4
    ↓ gRPC protobuf (5 calls internally)
AccountHelperService + AccountInformationService
    ↓ MT5 Terminal
```

**Что происходит:**

1. **Sugar Layer:** Вызывает сервис, оборачивает результат в dataclass AccountInfo
2. **Service Layer:** Делает 5 внутренних вызовов gRPC, возвращает AccountSummary
3. **Account Layer:** Объединяет account_summary() + 4 вызова account_info_double()
4. **Result:** Полный снимок счёта в одном dataclass

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:2031`
- Service: `src/pymt5/mt5_service.py:254`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:540`

---

## Когда использовать

**Дашборд счёта** — отображение всех метрик счёта

**Проверки рисков** — проверка нескольких параметров за один раз

**Логирование** — запись полного состояния счёта

**Принятие решений** — доступ ко всем данным для торговой логики

**Эффективность** — замена нескольких отдельных вызовов

---

## 🔗 Примеры использования

### 1) Получить все данные счёта за один раз

```python
info = await sugar.get_account_info()

print(f"Account:      {info.login}")
print(f"Balance:      ${info.balance:.2f}")
print(f"Equity:       ${info.equity:.2f}")
print(f"Profit:       ${info.profit:+.2f}")
print(f"Free Margin:  ${info.free_margin:.2f}")
print(f"Margin Level: {info.margin_level:.2f}%")
print(f"Leverage:     1:{info.leverage}")
print(f"Currency:     {info.currency}")
```

---

### 2) Эффективный против неэффективного подхода

```python
# НЕЭФФЕКТИВНО - 6 отдельных вызовов
balance = await sugar.get_balance()
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = await sugar.get_free_margin()
margin_level = await sugar.get_margin_level()
profit = await sugar.get_floating_profit()

# ЭФФЕКТИВНО - 1 вызов получает всё
info = await sugar.get_account_info()
# Доступ: info.balance, info.equity, info.margin и т.д.
```

---

### 3) Полная проверка здоровья счёта

```python
info = await sugar.get_account_info()

print("=" * 50)
print("ACCOUNT HEALTH REPORT")
print("=" * 50)
print(f"Broker:        {info.company}")
print(f"Account:       {info.login}")
print(f"Currency:      {info.currency}")
print(f"Leverage:      1:{info.leverage}")
print("-" * 50)
print(f"Balance:       ${info.balance:>12,.2f}")
print(f"Equity:        ${info.equity:>12,.2f}")
print(f"Profit/Loss:   ${info.profit:>12,.2f}")
print("-" * 50)
print(f"Used Margin:   ${info.margin:>12,.2f}")
print(f"Free Margin:   ${info.free_margin:>12,.2f}")
print(f"Margin Level:  {info.margin_level:>11.2f}%")
print("=" * 50)

# Оценка здоровья
if info.margin_level < 100:
    status = "CRITICAL"
elif info.margin_level < 200:
    status = "WARNING"
elif info.free_margin < 100:
    status = "LOW MARGIN"
else:
    status = "HEALTHY"

print(f"Status: {status}")
```

---

## Связанные методы

**Отдельные геттеры (менее эффективны):**

* `get_balance()` — только баланс
* `get_equity()` — только средства (equity)
* `get_margin()` — только маржа
* `get_free_margin()` — только свободная маржа
* `get_margin_level()` — только уровень маржи
* `get_floating_profit()` — только плавающая P/L

**Лучшая практика:**

```python
# Если нужно 1-2 значения:
balance = await sugar.get_balance()
equity = await sugar.get_equity()

# Если нужно 3+ значений:
info = await sugar.get_account_info()
# Используйте info.balance, info.equity, info.margin и т.д.
```

---

## Частые ошибки

### 1) Несколько вызовов, когда достаточно одного

```python
# НЕВЕРНО - расточительно
balance = await sugar.get_balance()
equity = await sugar.get_equity()
margin = await sugar.get_margin()
free_margin = await sugar.get_free_margin()
# 4 отдельных обхода gRPC!

# ВЕРНО - эффективно
info = await sugar.get_account_info()
# 1 вызов, доступ ко всем полям
```

### 2) Неправильное использование dataclass

```python
# НЕВЕРНО - воссоздаём то, что уже есть
info = await sugar.get_account_info()
my_balance = info.balance
my_equity = info.equity
# Просто используйте info напрямую!

# ВЕРНО - используйте dataclass как есть
info = await sugar.get_account_info()
print(f"Balance: ${info.balance:.2f}")
print(f"Equity: ${info.equity:.2f}")
```

---

## Советы профи

1. **Используйте для дашбордов** — идеально для отображения полного состояния счёта

2. **Кэшируйте для эффективности** — если нужно несколько полей, вызовите один раз и переиспользуйте

3. **Преимущества dataclass** — подсказки типов, автодополнение в IDE

4. **Проверяйте здоровье маржи** — используйте `margin_level` и `free_margin` для мониторинга рисков

5. **Преимущество одного вызова** — эффективнее, чем несколько отдельных вызовов методов

---

## 📚 См. также

- [get_balance](get_balance.md) — получить текущий баланс счёта
- [get_equity](get_equity.md) — получить средства (equity) (баланс + плавающая P/L)
- [get_margin](get_margin.md) — получить используемую маржу
