# Get Floating Profit (`get_floating_profit`)

> **Sugar method:** Возвращает суммарную нереализованную P/L по всем открытым позициям.

**Информация об API:**

* **Method:** `sugar.get_floating_profit()`
* **Returns:** Плавающая прибыль/убыток как `float`
* **Layer:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_floating_profit(self) -> float
```

---

## ℹ️ Вход / Выход

| Вход | Тип | Описание |
|-------|------|-------------|
| *Нет* | - | Параметры не требуются |

| Выход | Тип | Описание |
|--------|------|-------------|
| `profit` | `float` | Суммарная плавающая прибыль (положительная) или убыток (отрицательный) |

---

## 🏛️ Основы

* **Что это:** Сумма нереализованной прибыли/убытка по всем открытым позициям.
* **Зачем это нужно:** Отслеживать результативность в реальном времени без закрытия позиций.
* **Формула:** Floating P/L = Equity - Balance

---

## ⚡ Под капотом

```
MT5Sugar.get_floating_profit()
    ↓ calls
MT5Service.get_account_double(ACCOUNT_PROFIT)
    ↓ calls
MT5Account.account_info_double(property_id=ACCOUNT_PROFIT)
    ↓ gRPC protobuf
AccountInformationService.AccountInfoDouble(property_id=13)
    ↓ MT5 Terminal
```

**Что происходит:**

1. **Sugar Layer:** Вызывает сервис с константой ACCOUNT_PROFIT
2. **Service Layer:** Запрашивает свойство profit у счёта
3. **Account Layer:** Вызов gRPC к терминалу
4. **Result:** Сумма P/L всех открытых позиций, обновляется с каждым тиком

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:439`
- Service: `src/pymt5/mt5_service.py:298`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:578`

---

## Когда использовать

**Отслеживание результативности** — мониторинг прибыли без закрытия

**Управление рисками** — проверка, не превышают ли убытки лимиты

**Решения о тейк-профите** — решать, когда закрывать прибыльные позиции

**Мониторинг стоп-лосса** — отслеживать, приемлемы ли убытки

**Отображение на дашборде** — показывать P/L счёта в реальном времени

---

## 🔗 Примеры использования

### 1) Базовая проверка плавающей P/L

```python
profit = await sugar.get_floating_profit()

if profit > 0:
    print(f"Profit: +${profit:.2f}")
else:
    print(f"Loss: ${profit:.2f}")

# Вывод: Profit: +$125.50
```

---

### 2) Отслеживание результативности относительно баланса

```python
balance = await sugar.get_balance()
equity = await sugar.get_equity()
floating_pl = await sugar.get_floating_profit()

# Проверка: equity должно равняться balance + floating_pl
assert abs(equity - (balance + floating_pl)) < 0.01

print(f"Starting Balance: ${balance:.2f}")
print(f"Floating P/L:     ${floating_pl:+.2f}")
print(f"Current Equity:   ${equity:.2f}")

profit_percent = (floating_pl / balance) * 100
print(f"Return:           {profit_percent:+.2f}%")
```

---

### 3) Управление рисками — закрыть при превышении лимита убытка

```python
balance = await sugar.get_balance()
floating_pl = await sugar.get_floating_profit()

max_loss_percent = 5.0
max_loss = balance * max_loss_percent / 100

print(f"Balance:      ${balance:.2f}")
print(f"Floating P/L: ${floating_pl:+.2f}")
print(f"Max Loss:     -${max_loss:.2f}")

if floating_pl < -max_loss:
    print("Loss limit exceeded - closing all positions")
    await sugar.close_all_positions()
```

---

## Связанные методы

**Методы отслеживания P/L:**

* `get_balance()` — стартовый капитал + закрытые сделки
* `get_equity()` — баланс + плавающая P/L
* `get_total_profit()` — псевдоним для get_floating_profit()
* `get_profit_by_symbol()` — P/L для конкретного символа
* `get_profit()` — историческая прибыль за период

**Взаимосвязи P/L:**
```python
balance = await sugar.get_balance()
floating_pl = await sugar.get_floating_profit()
equity = await sugar.get_equity()

# Это эквивалентно:
assert abs(equity - (balance + floating_pl)) < 0.01
```

---

## Частые ошибки

### 1) Путаница плавающей и реализованной прибыли

```python
# НЕВЕРНО - плавающая прибыль НЕ реализована
floating_pl = await sugar.get_floating_profit()
print(f"I made ${floating_pl:.2f}")  # Ещё нет!

# ВЕРНО - только когда позиции закрыты
balance_before = await sugar.get_balance()
# ... закрываем позиции ...
balance_after = await sugar.get_balance()
realized_profit = balance_after - balance_before
print(f"Realized profit: ${realized_profit:.2f}")
```

### 2) Необработанные отрицательные значения

```python
# НЕВЕРНО - предполагаем, что прибыль всегда положительна
profit = await sugar.get_floating_profit()
print(f"Profit: ${profit:.2f}")  # Сбивает с толку, если отрицательна!

# ВЕРНО - показывайте знак явно
profit = await sugar.get_floating_profit()
if profit >= 0:
    print(f"Profit: +${profit:.2f}")
else:
    print(f"Loss: ${profit:.2f}")
```

---

## Советы профи

1. **Обновляется в реальном времени** — плавающая P/L меняется с каждым ценовым тиком

2. **Не реализована до закрытия** — плавающая прибыль может исчезнуть до закрытия

3. **Используйте для мониторинга** — отслеживайте, но не полагайтесь на неё при принятии решений

4. **Формула средств (equity)** — Equity = Balance + Floating P/L (всегда)

5. **Отслеживание по символам** — используйте `get_profit_by_symbol()` для отдельных символов

---

## 📚 См. также

- [get_equity](get_equity.md) — получить средства (equity) (баланс + плавающая P/L)
- [get_balance](get_balance.md) — получить текущий баланс счёта
- [get_profit_by_symbol](../7.%20Position_Information/get_profit_by_symbol.md) — получить прибыль для конкретного символа
