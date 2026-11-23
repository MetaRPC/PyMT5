## market_book_get — Как это работает

---

## 📌 Обзор

Этот пример показывает, как использовать низкоуровневый асинхронный метод `market_book_get()` для получения **текущего снимка стакана цен (Depth of Market, DOM)** и выполнения **пользовательских расчётов ликвидности** по сторонам BUY и SELL.

В этом сценарии DOM используется как источник мгновенного состояния рынка, тогда как вся аналитика и интерпретация выполняются на стороне клиента.

---

## Сигнатура метода

```python
async def market_book_get(
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Ключевые моменты:

* метод асинхронный и вызывается с `await`
* возвращает **текущий снимок DOM**, а не поток обновлений
* не агрегирует и не анализирует данные
* предполагает, что подписка на DOM уже открыта

---

## 🧩 Пример кода — Расчёт общей ликвидности

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def calculate_liquidity():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        symbol = "EURUSD"

        # 1. Открыть DOM
        await account.market_book_add(symbol)

        # 2. Получить текущий снимок DOM
        dom_data = await account.market_book_get(symbol)

        # 3. Рассчитать суммарный объём по стороне
        sell_volume = sum(
            e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2]
        )
        buy_volume = sum(
            e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3]
        )
        total_volume = sell_volume + buy_volume

        print(f"[LIQUIDITY] {symbol}")
        print(f"  Total DOM levels: {len(dom_data.mql_book_infos)}")
        print(f"  BUY side volume: {buy_volume:.2f} lots")
        print(f"  SELL side volume: {sell_volume:.2f} lots")
        print(f"  Total volume: {total_volume:.2f} lots")

        if total_volume > 0:
            buy_percent = (buy_volume / total_volume) * 100
            sell_percent = (sell_volume / total_volume) * 100

            print(f"\n  BUY: {buy_percent:.1f}% | SELL: {sell_percent:.1f}%")

            if buy_percent > 60:
                print("  [SIGNAL] Strong BUY side liquidity")
            elif sell_percent > 60:
                print("  [SIGNAL] Strong SELL side liquidity")
            else:
                print("  [SIGNAL] Balanced liquidity")

    finally:
        await account.channel.close()

asyncio.run(calculate_liquidity())
```

Этот пример демонстрирует полный пользовательский расчёт ликвидности на основе данных DOM.

---

## 🟢 Подробное объяснение

---

### 1️⃣ Открытие DOM

```python
await account.market_book_add(symbol)
```

На этом шаге:

* терминал начинает поддерживать стакан цен для символа
* без этого вызова `market_book_get` может вернуть пустые данные

---

### 2️⃣ Получение снимка DOM

```python
dom_data = await account.market_book_get(symbol)
```

Метод возвращает:

* список уровней ордеров `mql_book_infos`
* каждый элемент представляет один уровень стакана

Это **мгновенный снимок**, а не поток.

---

### 3️⃣ Разделение ордеров по сторонам

```python
e.type in [0, 2]  # SELL
e.type in [1, 3]  # BUY
```

Тип ордера определяет сторону рынка:

* SELL — предложения ликвидности
* BUY — спрос на ликвидность

Интерпретация типа выполняется пользователем.

---

### 4️⃣ Агрегация объёмов

```python
sell_volume = sum(...)
buy_volume = sum(...)
```

На этом шаге:

* объёмы суммируются по сторонам
* API не выполняет агрегацию

---

### 5️⃣ Аналитика на стороне пользователя

```python
if buy_percent > 60:
    ...
elif sell_percent > 60:
    ...
```

Пороговые значения:

* выбираются пользователем
* не имеют фиксированных значений в API

---

## Роль низкоуровневого метода

Чёткая граница ответственности:

**`market_book_get()`**:

* возвращает текущее состояние стакана
* не хранит историю
* не рассчитывает ликвидность
* не генерирует сигналы

**Пользовательский код**:

* агрегирует объёмы
* рассчитывает проценты
* интерпретирует баланс спроса и предложения

---

## Итог

Этот пример иллюстрирует паттерн анализа DOM:

> **получить снимок стакана → агрегировать уровни → оценить ликвидность → сделать выводы**

Метод `market_book_get()` предоставляет сырые данные DOM, тогда как вся аналитика и сигналы полностью формируются на стороне пользователя.
