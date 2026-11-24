# Семейство SDK MetaRPC

> Где находится PyMT5 — и как он сочетается с **Trade Copier** ([PyCopier](https://github.com/MetaRPC/PyCopier)) для зеркалирования стратегии между счетами.

MetaRPC поставляет два семейства SDK. Они используют **один и тот же API-ключ владельца**, **один и тот же транспорт gRPC-over-TLS** к `*.mrpc.pro`, один и тот же портал [mrpc.pro](https://mrpc.pro/explorer/mt5-client) и один и тот же демо-онбординг — но выполняют разные задачи.

| Семейство | Задача | Конечная точка | SDK |
| ------ | --- | -------- | ---- |
| **Terminal SDKs** | работают с **одним** торговым счётом — подключение, чтение, торговля, стриминг | `mt5.mrpc.pro:443` (MT5) | **PyMT5**, GoMT5, CSharpMT5, CppMT5, NodeMT5, RubyMT5, RustMT5 (+ варианты MT4) |
| **Copier SDKs** | зеркалируют сделки **между** счетами (мастер → последователи) | `copy.mrpc.pro:443` | [PyCopier](https://github.com/MetaRPC/PyCopier), RubyCopier, NodeCopier, GoCopier, CSharpCopier, … |

**PyMT5 — это Terminal SDK.** Когда вам нужно *реплицировать* происходящее на одном счёте на другие, обращайтесь к SDK **Copier** — в Python это **[PyCopier](https://github.com/MetaRPC/PyCopier)** (`pycopier`).

---

## Как связаны PyMT5 и PyCopier

|  | **PyMT5** (этот SDK) | **PyCopier** |
| --- | --- | --- |
| Область | один счёт | **пара** мастер → последователь |
| Делает | `quick_connect`, котировки, `buy_market_with_sltp`, стримы | `start` · `list` · `pause` · `remove` копировщика |
| Конечная точка | `mt5.mrpc.pro:443` | `copy.mrpc.pro:443` |
| Мыслит в терминах | тики, позиции, ордера | расчёт риска, пауза/возобновление, логи копирования |
| Стиль | **async** (`await`) | **async** (`await`) |

**Одним предложением:** PyMT5 — это место, где сделки *производятся и наблюдаются* на счёте; PyCopier — это то, как они *распределяются* последователям.

Оба являются нативными для `asyncio`, поэтому они встраиваются в один и тот же цикл событий — вы можете управлять мастером через PyMT5 и открыть копировщик через PyCopier из одного и того же `async def main()`.

---

## Как копировщик соединяет счета

Копировщик регистрирует **два** счёта — `master` и `slave` — каждый из которых описывается через `pycopier.Account`:

```python
Account(type="MT5", user=12345, password="...", server="Broker-Server", name="", id="")
```

| Поле | Значение |
| ----- | ------- |
| `type` | маршрут счёта — `"MT5"`, `"MT4"`, `"CT"` (cTrader), `"TL"` (TradeLocker), а также варианты `*_MTAPI` / `*_MRPC`. Развёртывание должно поддерживать этот маршрут. |
| `user` | логин (int) |
| `password` | пароль счёта |
| `server` | сервер / кластер брокера |
| `id` | id подключённого терминала/сессии — **требуется только для `CT` / `TL`**; для MT5 оставьте пустым, и копировщик подключится по учётным данным. Сохраняйте точный формат, если всё же передаёте его. |

> В PyCopier **нет вспомогательного GUID-моста** (в отличие от некоторых родственных SDK). Для MT4/MT5 копировщик сам подключает мастера и слейва по `user` / `password` / `server` — вы **не** передаёте ему дескриптор сессии PyMT5.

---

## Установка PyCopier

PyCopier — это **установка из исходников** (без отдельной загрузки среды выполнения), Python **3.10+**:

```bash
git clone https://github.com/MetaRPC/PyCopier.git
cd PyCopier
python -m pip install -e .
```

Затем:

```python
from pycopier import CopierService, StartRequest, Account
```

### Ключ владельца (`user_key`)

Копировщик аутентифицируется с помощью вашего **API-ключа владельца**, передаваемого как `user_key` (отправляется как gRPC-заголовок метаданных `apikey`):

```python
svc = CopierService("copy.mrpc.pro:443", user_key=os.environ["MRPC_API_KEY"])
```

- `manager_key` необязателен и по умолчанию равен `user_key`.
- **`TRIAL` не принимается** копировщиком — ему нужен реальный ключ владельца (печатаемый ASCII, без пробелов). `CopierService.start` с ключом TRIAL/пустым ключом вызывает `ValueError`, а не ответ `ok=False`.

---

## Сквозной сценарий: запустить стратегию на мастере, реплицировать на последователя

```python
import asyncio, os
from pymt5 import MT5Sugar, MT5Service, MT5Account
from pycopier import CopierService, StartRequest, Account

KEY = os.environ["MRPC_API_KEY"]   # ключ владельца — TRIAL НЕ принимается копировщиком

async def main():
    # 1 · Управляем счётом МАСТЕРА через PyMT5 (Terminal SDK, mt5.mrpc.pro)
    account = MT5Account.create(
        user=int(os.environ["MASTER_LOGIN"]),
        password=os.environ["MASTER_PASSWORD"],
        grpc_server="mt5.mrpc.pro:443",
    )
    master = MT5Sugar(MT5Service(account))
    await master.quick_connect("FxPro-MT5 Demo")

    # ... производим/наблюдаем сделки на мастере как обычно, напр.:
    # await master.buy_market_with_sltp("EURUSD", volume=0.1, sl_pips=50, tp_pips=100)

    # 2 · Запускаем копировщик: МАСТЕР -> ПОСЛЕДОВАТЕЛЬ (PyCopier, на copy.mrpc.pro)
    svc = CopierService("copy.mrpc.pro:443", user_key=KEY)
    req = StartRequest(
        risk_type="LotMultiplier",     # или "FixedLot" / "FixedBalanceMultiplier"
        risk_value="1.0",              # десятичная СТРОКА — лоты или множитель
        copy_sl=True,
        copy_tp=True,
        master=Account(type="MT5", user=int(os.environ["MASTER_LOGIN"]),
                       password=os.environ["MASTER_PASSWORD"], server="FxPro-MT5 Demo"),
        slave=Account(type="MT5", user=int(os.environ["SLAVE_LOGIN"]),
                      password=os.environ["SLAVE_PASSWORD"], server="FxPro-MT5 Demo"),
    )
    rep = await svc.start(req)
    if not rep.ok:
        raise SystemExit(f"copier start failed: {rep.error}")
    print(f"copier #{rep.copier_id} running")

    # 3 · Управляем им
    await svc.pause(rep.copier_id, True)    # пауза
    await svc.pause(rep.copier_id, False)   # возобновление (отдельного resume() нет — pause(id, False))
    # await svc.remove(rep.copier_id)       # удалить
    await svc.close()

asyncio.run(main())
```

### То же самое с помощью fluent-билдера (`CopierSugar`)

```python
from pycopier import CopierSugar

rep = await (
    CopierSugar.create()
    .with_credentials(os.environ["MRPC_API_KEY"])
    .from_master(type="MT5", user=int(os.environ["MASTER_LOGIN"]),
                 password=os.environ["MASTER_PASSWORD"], server="FxPro-MT5 Demo")
    .to_slave(type="MT5", user=int(os.environ["SLAVE_LOGIN"]),
              password=os.environ["SLAVE_PASSWORD"], server="FxPro-MT5 Demo")
    .with_lot_multiplier(1.0)   # или .with_fixed_lot(0.10)
    .copy_sl().copy_tp()
    .start()
)
```

---

## Основные операции копировщика

Все методы **асинхронны** и возвращают простые объекты ответа:

| Вызов | Возвращает | Примечания |
| ---- | ------- | ----- |
| `await svc.start(request)` | `StartReply(ok, copier_id, error)` | запускает копирование мастер → слейв; таймаут ~180 с |
| `await svc.list()` | `ListReply(ok, copiers, error)` | у каждого `CopierSummary` есть `id`, `type`/`user`/`server` мастера/слейва, `risk_type`, `risk_value`, `paused`, `pause_reason` |
| `await svc.pause(copier_id, paused)` | `SimpleReply` | `paused=True` ставит на паузу, `paused=False` возобновляет |
| `await svc.remove(copier_id)` | `SimpleReply` | удаляет копировщик |
| `async for log in svc.stream_trade_logs(copier_id)` | поток `TradeLog` | события копирования в реальном времени |
| `await svc.close()` | — | закрывает канал клиента |

### Расчёт риска (`risk_type`)

| `risk_type` | что означает `risk_value` |
| ----------- | ------------------ |
| `LotMultiplier` (по умолчанию) | умножить лот мастера на этот коэффициент |
| `FixedLot` | всегда открывать столько лотов у последователя |
| `FixedBalanceMultiplier` | масштабировать по отношению балансов (установите `fixed_master_balance` в качестве знаменателя) |

(Существуют ещё две политики расчёта размера, но они здесь не задокументированы.)

---

## Подводные камни

- **`start` / `list` / `pause` / `remove` превращают ошибки gRPC в ответы `ok=False`**; ошибки *конфигурации* (неверный/пустой/TRIAL-ключ) вместо этого вызывают исключения — обрабатывайте оба случая.
- **Освобождение клиента не останавливает копировщик на стороне сервера.** Вызовите `remove()`, чтобы действительно его остановить; `close()` лишь закрывает ваш локальный канал.
- **Биллинг может заблокировать возобновление** — `pause(id, False)` может вернуться с `ok=False` и `pause_reason`.
- Обёртка предоставляет **основные** маршруты (`start` / `list` / `pause` / `remove` + поток логов сделок), а не каждый REST-маршрут, который есть у сервиса.

---

### См. также

- **[PyCopier на GitHub](https://github.com/MetaRPC/PyCopier)** — исходники, примеры (`examples/list.py`, `examples/sizing_preview.py`) и справочник.
- [Getting Started](./GETTING_STARTED.md) · [Your First Project](./Your_First_Project.md) — сторона PyMT5 (Terminal SDK).
- [MT5 Client API Explorer](https://mrpc.pro/explorer/mt5-client) — ваш ключ владельца и сырые протоколы.
