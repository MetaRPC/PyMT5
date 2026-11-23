## order_history — Как это работает

---

## 📌 Обзор

Этот пример показывает, как использовать низкоуровневый асинхронный метод `order_history()` для получения **исторических торговых данных за заданный период времени** и выполнения **собственного анализа сделок** на стороне клиента.

В этом сценарии метод используется как источник сырых данных для расчёта:

* количества прибыльных сделок
* количества убыточных сделок
* процента выигрышных сделок (win rate)
* суммарной прибыли и убытка

Вся аналитическая логика реализована в пользовательском коде.

---

## Сигнатура метода

```python
async def order_history(
    from_dt: datetime,
    to_dt: datetime,
    sort_mode: BMT5_ENUM_ORDER_HISTORY_SORT_TYPE = BMT5_SORT_BY_CLOSE_TIME_ASC,
    page_number: int = 0,
    items_per_page: int = 0,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Ключевые моменты:

* Метод асинхронный и вызывается с `await`
* `from_dt` / `to_dt` задают временной диапазон для получения истории
* `items_per_page=0` отключает пагинацию и возвращает все данные сразу
* Метод возвращает исторические записи без какого-либо анализа

---

## 🧩 Пример кода — Анализ прибыльных и убыточных сделок

```python
async def analyze_win_loss(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> dict:
    """Analyze winning vs losing trades"""

    data = await account.order_history(
        from_dt=from_dt,
        to_dt=to_dt,
        items_per_page=0
    )

    wins = 0
    losses = 0
    total_win_profit = 0.0
    total_loss_profit = 0.0

    for item in data.history_data:
        if item.history_deal:
            profit = item.history_deal.profit
            if profit > 0:
                wins += 1
                total_win_profit += profit
            elif profit < 0:
                losses += 1
                total_loss_profit += profit

    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

    result = {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_win_profit": total_win_profit,
        "total_loss_profit": total_loss_profit,
        "net_profit": total_win_profit + total_loss_profit
    }

    print("Trading Statistics:")
    print(f"  Total trades: {total_trades}")
    print(f"  Wins: {wins} ({win_rate:.1f}%)")
    print(f"  Losses: {losses}")
    print(f"  Win profit: ${total_win_profit:.2f}")
    print(f"  Loss profit: ${total_loss_profit:.2f}")
    print(f"  Net profit: ${result['net_profit']:+.2f}")

    return result
```

Этот пример демонстрирует полный рабочий процесс анализа на уровне пользователя, построенный поверх сырых исторических данных.

---

## 🟢 Подробное объяснение

---

### 1️⃣ Вызов метода order_history

```python
data = await account.order_history(
    from_dt=from_dt,
    to_dt=to_dt,
    items_per_page=0
)
```

На этом шаге:

* выполняется один асинхронный запрос
* сервер возвращает все исторические записи в заданном временном диапазоне
* никакая фильтрация, агрегация или классификация не применяется

Результат представляет собой **сырые исторические торговые данные**.

---

### 2️⃣ Инициализация счётчиков и накопителей

```python
wins = 0
losses = 0
total_win_profit = 0.0
total_loss_profit = 0.0
```

Эти переменные являются частью пользовательской логики:

* API не ведёт статистику выигрышей/проигрышей
* все счётчики инициализируются вручную

---

### 3️⃣ Перебор исторических записей

```python
for item in data.history_data:
```

`history_data` — это список исторических записей.

Каждая запись может представлять разные сущности (ордера, сделки и т. д.), поэтому пользовательский код должен сам решать, что обрабатывать.

---

### 4️⃣ Фильтрация только исполненных сделок

```python
if item.history_deal:
```

В этом примере:

* анализируются только исполненные сделки
* записи без сделки пропускаются

Это правило фильтрации полностью определяется пользователем.

---

### 5️⃣ Классификация сделок по прибыли

```python
profit = item.history_deal.profit
```

Затем значение прибыли классифицируется:

```python
if profit > 0:
    wins += 1
    total_win_profit += profit
elif profit < 0:
    losses += 1
    total_loss_profit += profit
```

API не определяет, что считается выигрышем или проигрышем.

---

### 6️⃣ Расчёт итоговой статистики

```python
total_trades = wins + losses
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
```

Все статистические расчёты выполняются в пользовательском коде, включая обработку граничных случаев.

---

### 7️⃣ Построение объекта результата

```python
result = {
    "total_trades": total_trades,
    "wins": wins,
    "losses": losses,
    "win_rate": win_rate,
    "net_profit": total_win_profit + total_loss_profit
}
```

Итоговый аналитический результат — это чисто клиентская конструкция.

---

## Роль низкоуровневого метода

Чёткая граница ответственности:

**`order_history()`**:

* получает исторические торговые записи
* фильтрует по временному диапазону
* поддерживает сортировку и пагинацию
* не анализирует и не агрегирует данные

**Пользовательский код**:

* выбирает, какие записи обрабатывать
* определяет логику выигрыша/проигрыша
* вычисляет статистику
* формирует аналитический вывод

---

## Итог

Этот пример иллюстрирует стандартный паттерн работы с историческими данными:

> **получить сырую историю → отфильтровать записи → проанализировать результаты → построить статистику**

Метод `order_history()` предоставляет доступ к историческим данным, а вся аналитическая логика и логика принятия решений остаётся на стороне пользователя.
