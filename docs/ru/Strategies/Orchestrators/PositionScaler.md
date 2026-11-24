# Оркестратор Position Scaler

> Добавляет объём к существующей позиции на заранее заданных ценовых уровнях — либо **пирамидингом** в прибыльную позицию, либо **усреднением** в убыточную — соблюдая при этом жёсткий лимит суммарного объёма.

!!! warning "Только для демонстрации — не готово к продакшену"
    Этот оркестратор показывает идею стратегии и стоящие за ней вызовы API. Реальное развёртывание требует правильного расчёта объёма позиции, контроля проскальзывания, логирования, мониторинга и обширного тестирования. Запускайте его только на **демо-счёте**.

→ Исходник: [`examples/4_orchestrators/12_position_scaler.py`](https://github.com/MetaRPC/PyMT5/blob/main/examples/4_orchestrators/12_position_scaler.py)

---

## Что он делает

Наращивает одну базовую позицию поэтапно. Каждый раз, когда цена достигает следующего настроенного уровня, он добавляет часть объёма и фиксирует, что уровень сработал (поэтому он никогда не удваивается на одном и том же уровне). Суммарная экспозиция всегда ограничена значением `max_total_volume`.

## Как это работает

1. Выбирает базовую позицию (открывает тестовые позиции, если ни одна не передана) и стримит её P&L через `stream_position_profits()`.
2. При каждом обновлении измеряет прибыль/убыток в пипсах относительно настроенных `scale_levels_pips`.
3. Когда уровень достигнут, добавляет `scale_volume_percent` от базового объёма — пока новый суммарный объём остаётся ниже `max_total_volume` и позволяет маржа.
4. Каждый уровень срабатывает **один раз**. Живой индикатор прогресса и периодический статус показывают суммарный объём и число наращиваний.

### Два режима

- **Пирамидинг** (следование за трендом): добавляет к **прибыльным** позициям на `+30/+60/+90` пипсах. Ниже риск, нужен настоящий тренд.
- **Усреднение** (возврат к среднему): добавляет к **убыточным** позициям на `−30/−60/−90` пипсах. Выше риск — используйте строгие лимиты.

## Параметры

| Параметр | Тип | По умолчанию | Значение |
| --- | --- | --- | --- |
| `service` | `MT5Service` | — | Стриминг, котировки, сводка по счёту. |
| `sugar` | `MT5Sugar` | — | `buy_market`/`sell_market`, помощники по марже и символам, `close_position`. |
| `scale_type` | `ScaleType` | `PYRAMIDING` | `PYRAMIDING` или `AVERAGING`. |
| `scale_levels_pips` | `list[float]` | `[30, 60, 90]` | Уровни в пипсах, на которых добавлять объём. |
| `scale_volume_percent` | `float` | `50.0` | Процент от базового объёма, добавляемый на каждом уровне. |
| `max_total_volume` | `float` | `0.50` | Жёсткий лимит суммарного объёма (лоты). |
| `update_interval_ms` | `int` | `1000` | Интервал стрима позиции (мс). |
| `dry_run` | `bool` | `False` | Симулировать добавления без исполнения. |

`await start(symbol, base_ticket=None, duration_minutes=3.0, cancellation_event=None)` запускает цикл. Если `base_ticket` опущен, демонстрация открывает собственные тестовые позиции.

## Пример сценария (пирамидинг)

BUY EURUSD по 1.2000, базовый объём `0.10`, уровни `+30/+60/+90`, добавлять 50% (`0.05`) на уровень, лимит `0.30`:

- цена → 1.2030 (+30п) → добавить 0.05 → всего 0.15
- цена → 1.2060 (+60п) → добавить 0.05 → всего 0.20
- цена → 1.2090 (+90п) → добавить 0.05 → всего 0.25

## Запуск

```bash
cd examples
python main.py scaler        # или: positionscaler, или пункт меню [12]
```

## Минимальное использование

```python
import asyncio
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from demo_helpers import load_settings, create_and_connect_mt5
# ScaleType находится в модуле оркестратора (12_position_scaler.py)

async def main():
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol=config["test_symbol"])

    orch = PositionScalerOrchestrator(
        service, sugar,
        scale_type=ScaleType.PYRAMIDING,
        scale_levels_pips=[30.0, 60.0, 90.0],
        scale_volume_percent=50.0,
        max_total_volume=0.30,
    )
    await orch.start(symbol=config["test_symbol"], duration_minutes=3.0)

    await account.disconnect()

asyncio.run(main())
```

## Используемые методы API

- **MT5Service:** `stream_position_profits()` (основной), `get_opened_orders()`, `get_symbol_tick()`, `get_account_summary()`.
- **MT5Sugar:** `buy_market()` / `sell_market()`, `calculate_required_margin()`, `get_account_info()`, `get_symbol_info()`, `close_position()`.

## Примечания

- Всегда соблюдает `max_total_volume` и проверяет свободную маржу перед добавлением.
- **Усреднение** добавляет к убыточным позициям — это режим с повышенным риском; держите `max_total_volume` небольшим.
- Демонстрация открывает 2 небольшие тестовые позиции, использует первую как базовую, а вторую как резервную, и закрывает на выходе **только** свои тестовые позиции.

## См. также

- [Стратегии — Главный обзор](../Strategies.Master.Overview.md)
- [Trailing Stop](TrailingStop.md) · [Risk Manager](RiskManager.md)
- [MT5Service](../../MT5Service/MT5Service.Overview.md) · [MT5Sugar](../../MT5Sugar/MT5Sugar.Master.Overview.md)
