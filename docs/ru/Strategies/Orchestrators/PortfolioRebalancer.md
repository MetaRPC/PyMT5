# Оркестратор Portfolio Rebalancer

> Удерживает портфель из нескольких символов на целевых весах. Он рассчитывает размер позиций от средств (equity) счёта, следит за долей каждого символа и торгует, чтобы вернуть распределение, когда оно отклоняется за порог.

!!! warning "Только для демонстрации — не готово к продакшену"
    Этот оркестратор показывает идею стратегии и стоящие за ней вызовы API. Реальное развёртывание требует правильного расчёта объёма позиции, контроля проскальзывания, логирования, мониторинга и обширного тестирования. Запускайте его только на **демо-счёте**.

→ Исходник: [`examples/4_orchestrators/15_portfolio_rebalancer.py`](https://github.com/MetaRPC/PyMT5/blob/main/examples/4_orchestrators/15_portfolio_rebalancer.py)

---

## Что он делает

Поддерживает целевое распределение по нескольким символам (напр. EURUSD 40% / GBPUSD 30% / USDJPY 30%). Он вычисляет правильный объём для каждой цели из текущих средств (equity), открывает позиции, затем отслеживает долю каждого символа в средствах. Когда символ отклоняется за пределы `rebalance_threshold`, он торгует, чтобы восстановить цели.

## Как это работает

1. Читает средства (equity) счёта и вычисляет объёмы по символам из целевых процентов.
   *(напр. средства $9,600 → EURUSD 40% ≈ 0.64 лота, GBPUSD 30% ≈ 0.48 лота)*
2. Открывает позиции портфеля (по одной на цель).
3. Стримит P&L через `stream_position_profits()` и пересчитывает текущую долю каждого символа.
4. Когда отклонение любого символа превышает `rebalance_threshold`, запускает ребалансировку — уменьшает перевешенные символы, добавляет к недовешенным.
5. Работает в течение `duration_minutes`, затем закрывает все позиции портфеля на выходе.

## Параметры

| Параметр | Тип | По умолчанию | Значение |
| --- | --- | --- | --- |
| `service` | `MT5Service` | — | Стриминг и котировки. |
| `sugar` | `MT5Sugar` | — | Информация о счёте, позиции, информация о символах, открытие/закрытие. |
| `targets` | `list[PortfolioTarget]` | — | Целевое распределение (см. ниже). |
| `rebalance_threshold` | `float` | `5.0` | Минимальное отклонение %, запускающее ребалансировку. |
| `check_interval_ms` | `int` | `5000` | Как часто перепроверять распределение (мс). |
| `dry_run` | `bool` | `False` | Логировать ребалансировки без исполнения. |

Поля `PortfolioTarget`: `symbol: str`, `target_percent: float` (0–100), `direction: str` (`"BUY"` или `"SELL"`).

`await start(duration_minutes=3.0, cancellation_event=None)` запускает цикл.

## Пример сценария

Цель EURUSD 40% / GBPUSD 30% / USDJPY 30%. После движения цен: EURUSD уходит к 50% (+10%), GBPUSD и USDJPY к 25% каждый (−5%). Ребалансировка → уменьшить EURUSD, добавить к GBPUSD и USDJPY → обратно к 40/30/30.

## Запуск

```bash
cd examples
python main.py rebalancer    # или: portfolio, или пункт меню [15]
```

## Минимальное использование

```python
import asyncio
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from demo_helpers import load_settings, create_and_connect_mt5
# PortfolioTarget находится в модуле оркестратора (15_portfolio_rebalancer.py)

async def main():
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol=config["test_symbol"])

    targets = [
        PortfolioTarget("EURUSD", 40.0, "BUY"),
        PortfolioTarget("GBPUSD", 30.0, "BUY"),
        PortfolioTarget("USDJPY", 30.0, "BUY"),
    ]
    orch = PortfolioRebalancerOrchestrator(
        service, sugar,
        targets=targets,
        rebalance_threshold=5.0,
    )
    await orch.start(duration_minutes=3.0)

    await account.disconnect()

asyncio.run(main())
```

## Используемые методы API

- **MT5Service:** `stream_position_profits()`, `get_symbol_tick()`, `close_order()` (закрытие позиций через `OrderCloseRequest`).
- **MT5Sugar:** `get_account_info()`, `get_open_positions()`, `buy_market()` / `sell_market()`.

## Примечания

- Объёмы вычисляются из средств (equity) и целевых процентов, поэтому демо-позиции могут быть довольно крупными (часто по 0.5–1.0 лота каждая); применяется защитный лимит в 5.0 лотов.
- Демонстрация **совместима с DEMO**: она использует простую оценку маржи (≈ $6,000 за лот) и пропускает `order_check()` / `order_calc_margin()`.
- Все позиции портфеля закрываются автоматически, когда прогон завершается.

## См. также

- [Стратегии — Главный обзор](../Strategies.Master.Overview.md)
- [Grid Trader](GridTrader.md) · [Risk Manager](RiskManager.md)
- [MT5Service](../../MT5Service/MT5Service.Overview.md) · [MT5Sugar](../../MT5Sugar/MT5Sugar.Master.Overview.md)
