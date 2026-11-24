# Async в PyMT5 (и как самому сделать sync)

> **PyMT5 работает только асинхронно.** Каждый метод в `MT5Account`, `MT5Service` и `MT5Sugar` — это корутина, которую вы `await` — синхронных вариантов нет. Эта страница объясняет *почему*, и показывает, как самому обернуть async API в синхронный интерфейс, если вашему проекту он нужен.

---

## Почему async?

SDK общается с терминалом по **gRPC**, и нагрузка почти целиком состоит из ожидания сети. `asyncio` подходит под эту форму:

- **Стриминг непрерывен.** Тики, торговые события и обновления прибыли по позициям приходят как нескончаемый поток. Асинхронный генератор (`async for`) позволяет одному потоку обрабатывать этот стрим и оставаться отзывчивым между событиями — блокирующий вызов на каждое обновление заморозил бы программу.
- **Многие вызовы перекрываются.** Котировки, ордера и чтение счёта по нескольким символам можно выполнять одновременно через `asyncio.gather`, а не один за другим, так что их сетевые задержки перекрываются.
- **Никакого потока на соединение.** Один цикл событий мультиплексирует тысячи одновременных вызовов без пула потоков — именно то, что нужно для бота или сервиса.
- **Соответствие транспорту.** `grpc.aio` (асинхронный gRPC) — это то, на чём построен SDK, поэтому сверху донизу действует единая, согласованная модель исполнения.

Поэтому SDK придерживается одной модели — async — вместо того чтобы поставлять два параллельных API.

```python
summary = await service.get_account_summary()   # ✅ await его
summary = service.get_account_summary()          # ❌ это объект-корутина, а не данные
```

### Запуск async из обычного скрипта

Вам не нужен фреймворк — оберните вашу входную корутину в `asyncio.run(...)`:

```python
import asyncio
from pymt5.mt5_service import MT5Service
from demo_helpers import load_settings, create_and_connect_mt5

async def main():
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)

    summary = await service.get_account_summary()
    print(f"Balance: {summary.balance}, Equity: {summary.equity}")

    await account.disconnect()

asyncio.run(main())
```

В Jupyter цикл уже запущен, поэтому вы делаете `await` прямо в ячейке.

---

## Сборка синхронной обёртки своими руками

Иногда вам *необходимо* вызывать из синхронного кода — унаследованная кодовая база, синхронный веб-фреймворк, простой REPL-скрипт или библиотека, которая обязана предоставлять блокирующий API. Вы можете обернуть PyMT5 сами; SDK вам не мешает.

### ⚠️ Почему не стоит просто вызывать `asyncio.run()` на каждый вызов

`asyncio.run()` создаёт **новый цикл событий** каждый раз и закрывает его после. Канал gRPC в SDK привязан к тому циклу, на котором он был создан, поэтому вы **не можете** подключиться под одним `asyncio.run()` и затем переиспользовать этот `account` под более поздним `asyncio.run()` — второй вызов работает на другом цикле, и канал ломается.

Поэтому `asyncio.run()` годится только для **одной самодостаточной** корутины, которая подключается, работает и отключается всё за один заход:

```python
import asyncio
from pymt5.mt5_service import MT5Service
from demo_helpers import load_settings, create_and_connect_mt5

def get_balance_once() -> float:
    async def _run():
        account = await create_and_connect_mt5(load_settings())
        try:
            return (await MT5Service(account).get_account_summary()).balance
        finally:
            await account.disconnect()
    return asyncio.run(_run())   # подключение + чтение + отключение, за один раз

balance = get_balance_once()
```

### ✅ Переиспользуемый паттерн: постоянный цикл в фоновом потоке

Чтобы подключиться один раз и затем делать **много** синхронных вызовов, запустите один цикл событий в потоке-демоне и отправляйте в него корутины через `run_coroutine_threadsafe`. Всё — включая подключение — работает на этом одном цикле, поэтому канал остаётся действительным:

```python
import asyncio
import threading
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from demo_helpers import load_settings, create_and_connect_mt5

class SyncMT5:
    """Управлять асинхронным API PyMT5 из синхронного кода через один фоновый цикл."""

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

    def run(self, coro):
        """Отправить корутину в фоновый цикл и заблокироваться в ожидании её результата."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    def close(self):
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()


# --- использование: выглядит синхронно, SDK остаётся асинхронным под капотом ---
mt5 = SyncMT5()

config = load_settings()
account = mt5.run(create_and_connect_mt5(config))   # подключение НА фоновом цикле
service = MT5Service(account)
sugar = MT5Sugar(service, default_symbol=config["test_symbol"])

summary = mt5.run(service.get_account_summary())     # блокирующий вызов
print(f"Balance: {summary.balance}")

ticket = mt5.run(sugar.buy_market("EURUSD", 0.01))   # ещё один блокирующий вызов
print(f"Opened #{ticket}")

mt5.run(account.disconnect())
mt5.close()
```

Каждый `mt5.run(...)` блокируется, пока корутина не завершится, и возвращает её значение (или повторно выбрасывает её исключение), так что остальная часть вашего кода может быть обычной синхронной.

### Когда это стоит того — а когда нет

- **Стоит:** разовый скрипт, связующий код внутри синхронного приложения или предоставление небольшого блокирующего помощника коллегам, которые не используют `asyncio`.
- **Пропустите для стриминга.** Стримы — это генераторы `async for`; протаскивание их через синхронный фасад означает блокировку вызывающей стороны на каждом событии, что сводит на нет весь смысл. Потребляйте стримы в асинхронном коде.
- **Пропустите для чувствительной к производительности конкурентности.** Выигрыш async — в перекрытии вызовов; синхронная обёртка снова их сериализует. Если вам нужна пропускная способность, пишите асинхронно.

---

## Итог

- SDK работает **только асинхронно** — делайте `await` для всего; синхронных методов для вызова нет.
- Запускайте его из скрипта через **`asyncio.run(main())`**; делайте `await` прямо внутри асинхронного приложения или Jupyter.
- Нужен блокирующий интерфейс? Соберите его сами: `asyncio.run()` для одного самодостаточного вызова, либо **обёртка с постоянным фоновым циклом** (`run_coroutine_threadsafe`), чтобы подключиться один раз и сделать много синхронных вызовов.
- Держите **стриминг и высококонкурентную работу в async** — для этого и создана модель.

## См. также

- [Начало работы](GETTING_STARTED.md) — установка и первое подключение.
- [Стриминг gRPC](GRPC_STREAM_MANAGEMENT.md) — подписки, отмена, переподключение.
- [Ваш первый проект](Your_First_Project.md) — полный запускаемый скрипт.
