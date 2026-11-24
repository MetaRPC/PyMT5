# Ваш первый проект за 10 минут (Python)

> **Практический быстрый старт** — создайте с нуля рабочий торговый проект на MetaTrader 5 и PyMT5.

---

## Шаг 0: Получите API-ключ

Чтобы подключаться к эндпоинтам MetaRPC (`mt5.mrpc.pro:443`), получите свой API-ключ:

1. Зарегистрируйтесь бесплатно на [https://mrpc.pro/signup](https://mrpc.pro/signup).
2. Сгенерируйте API-токен в личном кабинете на [https://mrpc.pro/my](https://mrpc.pro/my).
3. Держите токен под рукой — передавайте его через переменную окружения `MRPC_API_KEY` (по умолчанию `TRIAL` для первых экспериментов).

---

## Шаг 1: Создайте проект

Создайте новый каталог для торгового бота и установите пакет:

```bash
mkdir my_pymt5_bot
cd my_pymt5_bot
pip install MetaRpcMT5
```

---

## Шаг 2: Напишите торговый код

Создайте файл `main.py` и вставьте в него следующий код. Каждый вызов асинхронный, поэтому всё выполняется внутри `asyncio.run(...)`:

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def main():
    # Создаём клиент (идентификатор сессии генерируется и подставляется автоматически).
    # Конструктор принимает: user, password, grpc_server, id_
    account = MT5Account(
        user=591129415,                  # ваш логин MT5
        password="your_password",
        grpc_server="mt5.mrpc.pro:443",  # адрес шлюза MetaRPC
    )

    # Подключение по имени сервера брокера (рекомендуется)
    await account.connect_by_server_name(
        "MetaQuotes-Demo",               # имя сервера вашего брокера/кластера
        base_chart_symbol="EURUSD",
        timeout_seconds=30,
    )

    # Читаем сводку по счёту
    summary = await account.account_summary()
    print(f"Balance: {summary.account_balance}, Equity: {summary.account_equity}")

    await account.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

> Подставьте свои `user`, `password` и имя сервера из вашего демо-счёта MT5 (как его создать — см. [MT5 для начинающих](MT5_For_Beginners.md)).

---

## Шаг 3: Запустите программу

```bash
python main.py
```

Вы должны увидеть баланс и средства (equity) вашего счёта, например:

```
Balance: 10000.0, Equity: 10000.0
```

---

## 🚀 Дальнейшие шаги

Поздравляем! Вы успешно установили прямое gRPC-соединение с MetaTrader 5. Дальше:

- Изучите **[gRPC-стриминг](GRPC_STREAM_MANAGEMENT.md)**, чтобы слушать живые тики.
- Загляните в **[Справочник API](../MT5Account/MT5Account.Master.Overview.md)** — все 43 доступных метода терминала.
- Узнайте про высокоуровневый риск-менеджмент и авто-нормализацию в **[MT5Sugar](../MT5Sugar/MT5Sugar.Master.Overview.md)**.
