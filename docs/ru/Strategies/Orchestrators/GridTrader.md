# Оркестратор Grid Trading

> Размещает сеть отложенных стоп-ордеров с фиксированным ценовым шагом вокруг текущей цены, затем пересоздаёт уровень всякий раз, когда его ордер срабатывает и закрывается, — сохраняя сетку целостной на протяжении всего прогона.

!!! warning "Только для демонстрации — не готово к продакшену"
    Этот оркестратор показывает идею стратегии и стоящие за ней вызовы API. Реальное развёртывание требует правильного расчёта объёма позиции, контроля проскальзывания, логирования, мониторинга и обширного тестирования. Запускайте его только на **демо-счёте**.

→ Исходник: [`examples/4_orchestrators/13_grid_trader.py`](https://github.com/MetaRPC/PyMT5/blob/main/examples/4_orchestrators/13_grid_trader.py)

---

## Что он делает

Строит сетку отложенных ордеров с фиксированным шагом в пипсах выше и ниже центральной цены, каждый с тейк-профитом, установленным на следующем уровне. Когда сработавшие ордера закрываются по своему TP, он размещает свежий ордер обратно на этот уровень, так что сетка продолжает работать — идеально для диапазонных, колеблющихся рынков.

## Как это работает

1. Читает текущую цену и вычисляет уровни сетки вокруг неё (центр).
2. Размещает отложенные ордера — `BUY_STOP` выше и `SELL_STOP` ниже для хеджирующей сетки.
3. Опрашивает тикеты ордеров/позиций через `stream_opened_tickets()`.
4. Когда ордер уровня срабатывает и закрывается по TP, размещает новый ордер обратно на этот уровень.
5. Поддерживает структуру в течение `duration_minutes`, затем при завершении отменяет все отложенные ордера.

### Два режима

- **Хеджирование** (двунаправленный): `BUY_STOP` выше + `SELL_STOP` ниже — прибыль от колебаний в обе стороны.
- **Направленный** (односторонний): только `BUY_STOP` или только `SELL_STOP` — следует за явным трендом, ниже активность.

## Параметры

| Параметр | Тип | По умолчанию | Значение |
| --- | --- | --- | --- |
| `service` | `MT5Service` | — | Размещение ордеров, стрим тикетов, котировки. |
| `sugar` | `MT5Sugar` | — | `get_symbol_info()` для пункта/знаков. |
| `grid_type` | `GridType` | `HEDGING` | `HEDGING` или `DIRECTIONAL`. |
| `grid_step_pips` | `float` | `20.0` | Расстояние между уровнями. |
| `levels_above` | `int` | `3` | Число уровней выше центра. |
| `levels_below` | `int` | `3` | Число уровней ниже центра. |
| `volume_per_level` | `float` | `0.01` | Объём каждого ордера. |
| `take_profit_pips` | `float \| None` | `None` | Расстояние TP (`None` → использовать `grid_step_pips`). |
| `update_interval_ms` | `int` | `1000` | Интервал опроса (мс). |
| `dry_run` | `bool` | `False` | Симулировать без размещения реальных ордеров. |

`await start(symbol, duration_minutes=3.0, cancellation_event=None)` запускает цикл.

## Пример сетки

EURUSD, центр 1.2000, шаг 20 пипсов, 3 выше / 3 ниже (хеджирование):

```
1.2060 → BUY_STOP  (TP 1.2080)
1.2040 → BUY_STOP  (TP 1.2060)
1.2020 → BUY_STOP  (TP 1.2040)
1.2000 → CENTER
1.1980 → SELL_STOP (TP 1.1960)
1.1960 → SELL_STOP (TP 1.1940)
1.1940 → SELL_STOP (TP 1.1920)
```

Когда BUY на 1.2020 срабатывает и закрывается по своему TP (1.2040), новый `BUY_STOP` размещается обратно на 1.2020.

## Запуск

```bash
cd examples
python main.py grid          # или: gridtrading, или пункт меню [13]
```

## Минимальное использование

```python
import asyncio
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from demo_helpers import load_settings, create_and_connect_mt5
# GridType находится в модуле оркестратора (13_grid_trader.py)

async def main():
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol=config["test_symbol"])

    orch = GridTradingOrchestrator(
        service, sugar,
        grid_type=GridType.HEDGING,
        grid_step_pips=20.0,
        levels_above=3,
        levels_below=3,
        volume_per_level=0.01,
    )
    await orch.start(symbol=config["test_symbol"], duration_minutes=3.0)

    await account.disconnect()

asyncio.run(main())
```

## Используемые методы API

- **MT5Service:** `stream_opened_tickets()` (основной, опрос), `place_order()`, `close_order()`, `get_symbol_tick()`.
- **MT5Sugar:** `get_symbol_info()`, `get_balance()`, `get_price_info()`.

## Примечания

- Лучше всего работает на **диапазонных** рынках; сильный односторонний тренд будет постоянно пробивать стопы на неправильной стороне (тогда используйте `DIRECTIONAL`).
- Использует `TMT5_ORDER_TYPE_BUY_STOP` / `TMT5_ORDER_TYPE_SELL_STOP` с `OrderSendRequest`; отложенные ордера отменяются через `close_order()`.
- Отслеживание тикетов основано на **опросе** (`stream_opened_tickets()`), а не на событийном `stream_trade_updates()`.
- Корректное завершение отменяет каждый отложенный ордер, созданный сеткой.

## См. также

- [Стратегии — Главный обзор](../Strategies.Master.Overview.md)
- [Trailing Stop](TrailingStop.md) · [Portfolio Rebalancer](PortfolioRebalancer.md)
- [gRPC Streaming](../../All_Guides/GRPC_STREAM_MANAGEMENT.md) · [MT5Service](../../MT5Service/MT5Service.Overview.md)
