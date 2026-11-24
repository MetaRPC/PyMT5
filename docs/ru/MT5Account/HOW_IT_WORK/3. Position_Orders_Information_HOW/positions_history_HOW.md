## positions_history — Как это работает

---

## 📌 Обзор

Этот пример показывает, как использовать низкоуровневый асинхронный метод `positions_history()` для получения **истории закрытых позиций за заданный период** и использования её для **экспорта данных во внешний формат (CSV)**.

В этом сценарии метод служит источником исторических данных, а вся логика форматирования, расчётов и сохранения результата реализуется на стороне пользовательского кода.

---

## Сигнатура метода

```python
async def positions_history(
    sort_type: AH_ENUM_POSITIONS_HISTORY_SORT_TYPE,
    open_from: Optional[datetime] = None,
    open_to: Optional[datetime] = None,
    page: int = 0,
    size: int = 0,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Ключевые моменты:

* метод асинхронный и вызывается с `await`
* `open_from` / `open_to` задают диапазон времени открытия позиций
* `size=0` означает, что все записи возвращаются в одном ответе
* метод возвращает только исторические данные без какой-либо агрегации

---

## 🧩 Пример кода — Экспорт истории позиций в CSV

```python
import csv

async def export_positions_to_csv(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    filename: str = "positions_history.csv"
):
    """Export closed positions to CSV"""

    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Ticket', 'Symbol', 'Open Time', 'Close Time',
            'Volume', 'Open Price', 'Close Price',
            'Profit', 'Commission', 'Swap', 'Total'
        ])

        for pos in data.history_positions:
            open_time = pos.open_time.ToDatetime()
            close_time = pos.close_time.ToDatetime()
            total = pos.profit - pos.commission + pos.swap

            writer.writerow([
                pos.position_ticket,
                pos.symbol,
                open_time.strftime('%Y-%m-%d %H:%M:%S'),
                close_time.strftime('%Y-%m-%d %H:%M:%S'),
                pos.volume,
                pos.open_price,
                pos.close_price,
                pos.profit,
                pos.commission,
                pos.swap,
                total
            ])

    print(f"[OK] Exported {len(data.history_positions)} positions to {filename}")
```

Этот пример демонстрирует полный сценарий экспорта данных на уровне пользователя, построенный поверх низкоуровневого метода.

---

## 🟢 Подробное объяснение

---

### 1️⃣ Вызов метода positions_history

```python
data = await account.positions_history(
    sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
    open_from=from_dt,
    open_to=to_dt
)
```

На этом шаге:

* к серверу выполняется один асинхронный запрос
* сервер фильтрует исторические позиции по времени открытия
* данные возвращаются в виде списка `history_positions`

Метод не выполняет никаких расчётов и не изменяет данные.

---

### 2️⃣ Подготовка CSV-файла

```python
with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
```

Это полностью пользовательская логика:

* выбор формата (CSV)
* кодировка
* способ записи данных

API не участвует в этом процессе.

---

### 3️⃣ Запись заголовка

```python
writer.writerow([
    'Ticket', 'Symbol', 'Open Time', 'Close Time',
    'Volume', 'Open Price', 'Close Price',
    'Profit', 'Commission', 'Swap', 'Total'
])
```

Заголовки столбцов:

* определяются пользователем
* отражают выбранный набор полей

---

### 4️⃣ Перебор исторических позиций

```python
for pos in data.history_positions:
```

Каждый элемент `pos` представляет одну закрытую позицию и содержит:

* идентификаторы
* цены открытия и закрытия
* финансовые показатели

---

### 5️⃣ Преобразование времени

```python
open_time = pos.open_time.ToDatetime()
close_time = pos.close_time.ToDatetime()
```

Значения времени:

* приходят в формате protobuf
* преобразуются в `datetime` для удобного форматирования

---

### 6️⃣ Пользовательские расчёты

```python
total = pos.profit - pos.commission + pos.swap
```

Расчёт итогового результата позиции:

* выполняется на стороне клиента
* API не вычисляет агрегированные значения

---

### 7️⃣ Запись строки в CSV

```python
writer.writerow([...])
```

На этом шаге:

* выбираются нужные поля позиции
* данные преобразуются в строковый формат
* формируется одна строка CSV-файла

---

## Роль низкоуровневого метода

Чёткая граница ответственности:

**`positions_history()`**:

* возвращает историю позиций на основе заданных фильтров
* выполняет сортировку и фильтрацию по времени
* не анализирует и не форматирует данные

**Пользовательский код**:

* определяет формат экспорта
* выполняет расчёты
* управляет выводом данных

---

## Итог

Этот пример иллюстрирует стандартный паттерн работы с историческими данными:

> **получить историю → преобразовать данные → сохранить во внешний формат**

Метод `positions_history()` предоставляет доступ к историческим позициям, а вся логика экспорта и обработки данных полностью реализуется на стороне пользователя.
