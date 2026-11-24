# Стратегии — Главный обзор

> Одна страница для быстрой ориентации: какие оркестраторы поставляются с PyMT5 SDK, как выбрать подходящий, как его запустить, и ссылки на спецификацию каждой стратегии.

---

!!! warning "Только в образовательных и демонстрационных целях"
    Каждый оркестратор здесь — это **демонстрационный пример**, который показывает API PyMT5 и служит шаблоном для построения ваших собственных стратегий. Это **не** готовые к продакшену торговые системы: анализ рынка упрощён, контроль риска минимален, а логика исполнения базовая (без обработки проскальзывания, без обнаружения неблагоприятных условий).

    **Используйте только демо-счета.** Прежде чем переходить к реальной торговле: разберитесь в каждой строке, проведите бэктест, долго тестируйте на демо в форвард-режиме, добавьте настоящий риск-менеджмент и добавьте мониторинг/оповещения. Торговля сопряжена с существенным риском убытков; вы несёте ответственность за свои собственные решения.

---

## Оркестраторы

Все пять находятся в [`examples/4_orchestrators/`](https://github.com/MetaRPC/PyMT5/blob/main/examples/4_orchestrators) и запускаются из интерактивного меню (`examples/main.py`).

| # | Стратегия | Что делает | Лучше всего для | Запуск |
| --- | --- | --- | --- | --- |
| 11 | **[Trailing Stop](Orchestrators/TrailingStop.md)** | Тянет стоп-лосс за прибыльной позицией; автоматически закрывает зависшие/убыточные сделки. | Безопасного наращивания прибыли | `python main.py trailing` |
| 12 | **[Position Scaler](Orchestrators/PositionScaler.md)** | Добавляет объём на уровнях — пирамидинг или усреднение — в рамках лимита объёма. | Наращивания позиции в движении | `python main.py scaler` |
| 13 | **[Grid Trader](Orchestrators/GridTrader.md)** | Сетка отложенных ордеров, пересоздающая уровни по мере их срабатывания. | Диапазонных / колеблющихся рынков | `python main.py grid` |
| 14 | **[Risk Manager](Orchestrators/RiskManager.md)** | Защитник всего счёта; закрывает всё при превышении лимита. | Защиты счёта | `python main.py risk` |
| 15 | **[Portfolio Rebalancer](Orchestrators/PortfolioRebalancer.md)** | Удерживает распределение по нескольким символам на целевых весах. | Портфелей из нескольких символов | `python main.py rebalancer` |

## Выберите по цели

- **Защитить открытую прибыльную позицию** → [Trailing Stop](Orchestrators/TrailingStop.md)
- **Наращивать позицию шаг за шагом** → [Position Scaler](Orchestrators/PositionScaler.md)
- **Автоматически торговать в боковом диапазоне** → [Grid Trader](Orchestrators/GridTrader.md)
- **Соблюдать лимиты риска на уровне счёта** → [Risk Manager](Orchestrators/RiskManager.md)
- **Держать несколько символов на фиксированных весах** → [Portfolio Rebalancer](Orchestrators/PortfolioRebalancer.md)

---

## Как оркестратор вписывается в SDK

Оркестраторы располагаются поверх трёхслойного API — это обычные классы Python, которые управляют `MT5Service` и `MT5Sugar`:

```
ORCHESTRATORS  (examples/4_orchestrators/)
  Trailing Stop · Position Scaler · Grid Trader · Risk Manager · Portfolio Rebalancer
        │  async-цикл, стримит P&L позиции, принимает решения, торгует
        ▼
MT5Sugar      высокоуровневые помощники  (buy_market, close_position, get_symbol_info, …)
        ▼
MT5Service    типизированный фасад        (stream_position_profits, modify_order, place_order, …)
        ▼
MT5Account    низкоуровневый gRPC
```

Каждый оркестратор **асинхронный**, отслеживает позиции через стриминговый метод (в основном `stream_position_profits()`) и корректно завершается по `Ctrl+C` через событие отмены. См. [gRPC Streaming](../All_Guides/GRPC_STREAM_MANAGEMENT.md), чтобы узнать о модели стриминга.

## Общий шаблон запуска

```python
import asyncio
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from demo_helpers import load_settings, create_and_connect_mt5

async def main():
    # 1) подключение
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol=config["test_symbol"])

    # 2) настройка + запуск оркестратора
    orch = TrailingStopOrchestrator(service, sugar, trail_distance_pips=20.0)
    await orch.start(duration_minutes=3.0)

    # 3) отключение
    await account.disconnect()

asyncio.run(main())
```

Быстрее всего попробовать любой из них через меню:

```bash
cd examples
python main.py              # интерактивное меню
python main.py trailing     # или запустить напрямую: trailing / scaler / grid / risk / rebalancer
```

## Общее поведение

- **Безопасно для демо:** каждая демонстрация открывает свои собственные небольшие тестовые позиции и закрывает на выходе **только их**.
- **Пипсы против пунктов:** размер пипса выводится для каждого символа (на символах с 3/5 знаками 1 пипс = 10 пунктов).
- **Сухой прогон:** большинство оркестраторов принимают `dry_run=True`, чтобы логировать предполагаемые сделки, не затрагивая счёт.
- **Корректная остановка:** `Ctrl+C` отменяет стрим и очищает отложенные ордера/позиции.

---

## Связанная документация

- [MT5Account — Главный обзор](../MT5Account/MT5Account.Master.Overview.md) — низкоуровневый gRPC API.
- [MT5Service](../MT5Service/MT5Service.Overview.md) — типизированные методы-обёртки.
- [MT5Sugar — Главный обзор](../MT5Sugar/MT5Sugar.Master.Overview.md) — высокоуровневые помощники.
- [gRPC Streaming](../All_Guides/GRPC_STREAM_MANAGEMENT.md) — подписки и отмена.
- [Sync vs Async](../All_Guides/SYNC_VS_ASYNC.md) — асинхронные паттерны.
- [UserCode Sandbox](../All_Guides/USERCODE_SANDBOX_GUIDE.md) — напишите свою собственную стратегию.

## Быстрый переход

- [Trailing Stop](Orchestrators/TrailingStop.md)
- [Position Scaler](Orchestrators/PositionScaler.md)
- [Grid Trader](Orchestrators/GridTrader.md)
- [Risk Manager](Orchestrators/RiskManager.md)
- [Portfolio Rebalancer](Orchestrators/PortfolioRebalancer.md)
