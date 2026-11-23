## market_book_add / market_book_get / market_book_release — Как это работает

---

## 📌 Обзор

Этот пример показывает **полный жизненный цикл работы со стаканом цен (Depth of Market, DOM)**:

1. подписка на DOM для символа
2. периодическое получение текущего состояния стакана
3. отображение уровней ордеров
4. корректное закрытие подписки

Здесь DOM используется как **живое состояние рынка**, которое меняется со временем, а низкоуровневые методы служат источниками данных и операциями управления.

---

## Используемые методы

В этом примере используются три низкоуровневых метода:

```python
market_book_add(symbol)
market_book_get(symbol)
market_book_release(symbol)
```

Их роли:

* `market_book_add` — открывает DOM и регистрирует подписку
* `market_book_get` — возвращает текущий снимок стакана
* `market_book_release` — закрывает DOM и освобождает ресурсы

---

## 🧩 Пример кода — Подписка и мониторинг DOM

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_dom(symbol: str, duration: int = 10):
    """Subscribe and monitor DOM for specified duration"""

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
        # 1. Подписаться на DOM
        result = await account.market_book_add(symbol)

        if not result.opened_successfully:
            print(f"[FAILED] Could not subscribe to {symbol} DOM")
            return

        print(f"[SUBSCRIBED] Monitoring {symbol} DOM for {duration} seconds\n")

        start_time = asyncio.get_event_loop().time()

        # 2. Периодически читать снимок DOM
        while (asyncio.get_event_loop().time() - start_time) < duration:
            dom_data = await account.market_book_get(symbol)

            print("\033[2J\033[H")  # очистить экран

            print(f"=== {symbol} Market Depth ===")
            print(f"Total levels: {len(dom_data.mql_book_infos)}\n")

            print(f"{'Type':<10} {'Price':<15} {'Volume':<15}")
            print("-" * 45)

            for book_entry in dom_data.mql_book_infos[:10]:
                entry_type = "BUY" if book_entry.type in [1, 3] else "SELL"
                print(
                    f"{entry_type:<10} "
                    f"{book_entry.price:<15.5f} "
                    f"{book_entry.volume_real:<15.2f}"
                )

            await asyncio.sleep(1)

        # 3. Отписаться от DOM
        await account.market_book_release(symbol)
        print(f"\n[UNSUBSCRIBED] Stopped monitoring {symbol} DOM")

    finally:
        await account.channel.close()

asyncio.run(monitor_dom("EURUSD", duration=10))
```

---

## 🟢 Подробное объяснение

---

### 1️⃣ Подписка на DOM

```python
result = await account.market_book_add(symbol)
```

На этом шаге:

* терминал открывает стакан цен для символа
* сервер начинает поддерживать состояние DOM
* возвращается флаг успешности операции

Без этого шага `market_book_get` работать не будет.

---

### 2️⃣ Цикл мониторинга

```python
while (asyncio.get_event_loop().time() - start_time) < duration:
```

Цикл:

* выполняется в течение заданного времени
* регулярно запрашивает текущее состояние DOM
* не хранит историю — только текущий снимок

---

### 3️⃣ Получение текущего состояния стакана

```python
dom_data = await account.market_book_get(symbol)
```

Метод возвращает:

* список уровней ордеров
* каждый уровень содержит цену, объём и тип

Это **снимок состояния рынка в текущий момент времени**.

---

### 4️⃣ Отображение уровней

```python
for book_entry in dom_data.mql_book_infos[:10]:
```

Пользовательский код:

* выбирает, сколько уровней отображать
* интерпретирует тип ордера (BUY / SELL)
* форматирует вывод

API не участвует в визуализации.

---

### 5️⃣ Закрытие подписки

```python
await account.market_book_release(symbol)
```

Важно:

* DOM должен закрываться явно
* это освобождает ресурсы на сервере и в терминале
* без этого подписка останется активной

---

## Роль низкоуровневых методов

Чёткая граница ответственности:

**`market_book_add`**:

* открывает DOM
* регистрирует подписку

**`market_book_get`**:

* возвращает текущий снимок стакана
* не стримит данные

**`market_book_release`**:

* закрывает DOM
* освобождает ресурсы

**Пользовательский код**:

* определяет частоту опроса
* форматирует данные
* решает, как долго наблюдать за рынком

---

## Итог

Этот пример иллюстрирует стандартный паттерн работы с DOM:

> **подписаться → регулярно получать состояние → обрабатывать → корректно отписаться**

Низкоуровневые методы управляют доступом к DOM, тогда как вся логика мониторинга и использования данных остаётся на стороне пользователя.
