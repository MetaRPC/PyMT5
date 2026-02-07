# Ваш Первый Проект за 10 Минут

> **Практика Перед Теорией** - создайте рабочий торговый проект с MT5 перед погружением в документацию

---

## Зачем Этот Гайд?

Я хочу показать вам на простом примере, насколько легко использовать наш gRPC-шлюз для работы с MetaTrader 5.

**Перед тем как погружаться в изучение основ и фундаментальных концепций проекта - давайте создадим ваш первый проект.**

Мы установим один Python-пакет `MetaRpcMT5`, который содержит:

- ✅ Protobuf-определения всех методов MT5
- ✅ MT5Account - готовый к использованию gRPC-клиент
- ✅ Обработчик ошибок - типы ApiError и коды возврата
- ✅ Всё необходимое для старта

**Это фундамент** для вашей будущей системы алгоритмической торговли.

---

> 💡 После того как получите первые результаты, переходите к [MT5Account.Master.Overview.md](../MT5Account/MT5Account.Master.Overview.md) для глубокого понимания архитектуры SDK.

---

## Шаг 1: Установите Python 3.8 или Выше

Если у вас ещё не установлен Python:

**Скачайте и установите:**

- [Python Download](https://www.python.org/downloads/)

**Проверьте установку:**

```bash
python --version
# Должно показать: Python 3.8.x или выше
```

**На Windows может понадобиться:**
```bash
py --version
# или
python3 --version
```

---

## Шаг 2: Создайте Новый Python-Проект

Откройте терминал (командную строку) и выполните:

```bash
# Создайте папку проекта
mkdir MyMT5Project
cd MyMT5Project

# Создайте виртуальное окружение (рекомендуется)
python -m venv venv

# Активируйте виртуальное окружение
# На Windows:
venv\Scripts\activate
# На Linux/Mac:
source venv/bin/activate
```

**Что произошло:**

- ✅ Создана папка `MyMT5Project`
- ✅ Создано виртуальное окружение `venv` - изолированная среда Python
- ✅ Активировано окружение - теперь можно устанавливать пакеты

---

## Шаг 3: Установите Пакет MetaRpcMT5

Это самый важный шаг - установка **единственного пакета**, который содержит всё необходимое:

```bash
pip install git+https://github.com/MetaRPC/PyMT5.git#subdirectory=package
```

> **📌 Важно для новичков:** После выполнения команды пакет установится в ваше виртуальное окружение напрямую из GitHub.
> Вы можете проверить установку командой `pip list | grep MetaRpcMT5`

**Как проверить, что установка прошла успешно?**

**Метод 1:** Запустите команду проверки:

```bash
pip show MetaRpcMT5
```

Вы увидите информацию о пакете (версия, зависимости и т.д.)

**Метод 2:** Проверьте импорт в Python:

```bash
python -c "from MetaRpcMT5 import MT5Account; print('OK')"
```

Если видите `OK` - **всё установлено корректно!** ✅

---

## Шаг 4: Создайте Конфигурационный Файл settings.json

Создайте файл `settings.json` в корне проекта:

```json
{
  "user": 591129415,
  "password": "YourPassword123",
  "grpc_server": "mt5.mrpc.pro:443",
  "mt_cluster": "YourBroker-MT5 Demo",
  "test_symbol": "EURUSD"
}
```

**Объяснение параметров:**

| Параметр | Описание | Где Взять |
|----------|----------|-----------|
| **user** | Номер вашего MT5-аккаунта (логин) | В терминале MT5: Сервис → Настройки → Логин |
| **password** | Мастер-пароль для MT5-аккаунта | Тот, что вы получили при регистрации |
| **grpc_server** | Адрес gRPC-шлюза | `mt5.mrpc.pro:443` (публичный шлюз) |
| **mt_cluster** | Имя кластера вашего брокера | В терминале MT5: смотрите имя сервера |
| **test_symbol** | Торговый символ для примеров | `EURUSD`, `GBPUSD`, `BTCUSD` и т.д. |

**Замените:**

- `user`, `password`, `mt_cluster` - на данные вашего MT5 демо-аккаунта
- `grpc_server` - можно оставить как есть (публичный шлюз MetaRPC)

---

## Шаг 5: Напишите Код для Подключения и Получения Информации об Аккаунте

Создайте файл `main.py` в корне проекта:

```python
"""
═══════════════════════════════════════════════════════════════════
ВАШ ПЕРВЫЙ ПРОЕКТ С MT5
═══════════════════════════════════════════════════════════════════
Этот скрипт демонстрирует:
  - Создание MT5Account
  - Подключение к MT5 через gRPC
  - Получение информации об аккаунте
═══════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import sys
from uuid import uuid4
from datetime import datetime

# Импортируем MetaRpcMT5
from MetaRpcMT5 import MT5Account


def load_settings():
    """Загрузка настроек из settings.json"""
    with open('settings.json', 'r', encoding='utf-8') as f:
        return json.load(f)


async def main():
    """Основная функция"""

    print("═" * 80)
    print("          ДОБРО ПОЖАЛОВАТЬ В ВАШ ПЕРВЫЙ ПРОЕКТ С MT5")
    print("═" * 80)
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # ШАГ 1: ЗАГРУЗКА КОНФИГУРАЦИИ
    # ═══════════════════════════════════════════════════════════════════════

    print("📋 Загрузка конфигурации...")

    try:
        config = load_settings()
    except FileNotFoundError:
        print("❌ Ошибка: файл settings.json не найден!")
        print("   Создайте settings.json с вашими учётными данными MT5")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка: некорректный JSON в settings.json: {e}")
        sys.exit(1)

    print("✅ Конфигурация загружена:")
    print(f"   Пользователь:    {config['user']}")
    print(f"   Кластер:         {config['mt_cluster']}")
    print(f"   gRPC Сервер:     {config['grpc_server']}")
    print(f"   Тестовый Символ: {config['test_symbol']}")
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # ШАГ 2: СОЗДАНИЕ MT5ACCOUNT
    # ═══════════════════════════════════════════════════════════════════════

    print("🔌 Создание экземпляра MT5Account...")

    # Генерируем уникальный UUID для этого терминала
    terminal_guid = uuid4()

    # Создаём MT5Account с учётными данными
    account = MT5Account(
        user=config['user'],
        password=config['password'],
        grpc_server=config['grpc_server'],
        id_=terminal_guid
    )

    print(f"✅ MT5Account создан (UUID: {terminal_guid})")
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # ШАГ 3: ПОДКЛЮЧЕНИЕ К MT5
    # ═══════════════════════════════════════════════════════════════════════

    print("🔗 Подключение к терминалу MT5...")
    print(f"   Ожидание ответа (таймаут: 120 секунд)...")
    print()

    try:
        # Подключаемся к MT5 используя имя сервера
        # Это РЕКОМЕНДУЕМЫЙ метод - проще чем ConnectEx
        await account.connect_by_server_name(
            server_name=config['mt_cluster'],
            base_chart_symbol=config['test_symbol'],
            timeout_seconds=120
        )

        print(f"✅ Успешно подключено!")
        print(f"   Terminal GUID: {account.id}")
        print()

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print("   Проверьте:")
        print("   - Правильность логина/пароля")
        print("   - Доступность gRPC-сервера")
        print("   - Правильность имени кластера")
        await account.channel.close()
        sys.exit(1)

    # ═══════════════════════════════════════════════════════════════════════
    # ШАГ 4: ПОЛУЧЕНИЕ ИНФОРМАЦИИ ОБ АККАУНТЕ
    # ═══════════════════════════════════════════════════════════════════════

    print("📊 Получение информации об аккаунте...")
    print()

    try:
        # Запрашиваем полную информацию об аккаунте одним вызовом
        summary_data = await account.account_summary()

        # ═══════════════════════════════════════════════════════════════════════
        # ШАГ 5: ВЫВОД РЕЗУЛЬТАТОВ
        # ═══════════════════════════════════════════════════════════════════════

        print()
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║              ИНФОРМАЦИЯ ОБ АККАУНТЕ                            ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print()
        print(f"   Логин:              {summary_data.account_login}")
        print(f"   Имя пользователя:   {summary_data.account_user_name}")
        print(f"   Компания:           {summary_data.account_company_name}")
        print(f"   Валюта:             {summary_data.account_currency}")
        print()
        print(f"💰 Баланс:             {summary_data.account_balance:.2f} {summary_data.account_currency}")
        print(f"💎 Средства:           {summary_data.account_equity:.2f} {summary_data.account_currency}")
        print()
        print(f"   Кредит:             {summary_data.account_credit:.2f} {summary_data.account_currency}")
        print(f"   Кредитное плечо:    1:{summary_data.account_leverage}")
        print(f"   Режим торговли:     {summary_data.account_trade_mode}")
        print()

        # Время сервера - protobuf Timestamp, нужно конвертировать
        if summary_data.server_time:
            server_time = summary_data.server_time.ToDatetime()
            print(f"   Время сервера:      {server_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # UTC смещение: смещение времени сервера от UTC в минутах
        # Например: 120 минут = UTC+2 (сервер на 2 часа впереди UTC)
        utc_shift = summary_data.utc_timezone_server_time_shift_minutes
        print(f"   Смещение UTC:       {utc_shift} минут (UTC{utc_shift/60:+.1f})")

        print()
        print("╚════════════════════════════════════════════════════════════════╝")

    except Exception as e:
        print(f"❌ Ошибка получения данных аккаунта: {e}")
        await account.channel.close()
        sys.exit(1)

    # ═══════════════════════════════════════════════════════════════════════
    # ШАГ 6: ОТКЛЮЧЕНИЕ ОТ MT5
    # ═══════════════════════════════════════════════════════════════════════

    print()
    print("🔌 Отключение от MT5...")

    try:
        await account.channel.close()
        print("✅ Успешно отключено!")
    except Exception as e:
        print(f"⚠️  Предупреждение при отключении: {e}")

    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   🎉 ПОЗДРАВЛЯЕМ! ВАШ ПЕРВЫЙ ПРОЕКТ РАБОТАЕТ! 🎉              ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(main())
```

---

## Шаг 6: Запустите Проект

Сохраните все файлы и выполните:

```bash
python main.py
```

**Ожидаемый результат:**

```
════════════════════════════════════════════════════════════════════════════════
          ДОБРО ПОЖАЛОВАТЬ В ВАШ ПЕРВЫЙ ПРОЕКТ С MT5
════════════════════════════════════════════════════════════════════════════════

📋 Загрузка конфигурации...
✅ Конфигурация загружена:
   Пользователь:    591129415
   Кластер:         FxPro-MT5 Demo
   gRPC Сервер:     mt5.mrpc.pro:443
   Тестовый Символ: EURUSD

🔌 Создание экземпляра MT5Account...
✅ MT5Account создан (UUID: 12345678-90ab-cdef-1234-567890abcdef)

🔗 Подключение к терминалу MT5...
   Ожидание ответа (таймаут: 120 секунд)...

✅ Успешно подключено!
   Terminal GUID: 12345678-90ab-cdef-1234-567890abcdef

📊 Получение информации об аккаунте...

╔════════════════════════════════════════════════════════════════╗
║              ИНФОРМАЦИЯ ОБ АККАУНТЕ                            ║
╚════════════════════════════════════════════════════════════════╝

   Логин:              591129415
   Имя пользователя:   Demo User
   Компания:           FxPro Financial Services Ltd
   Валюта:             USD

💰 Баланс:             10000.00 USD
💎 Средства:           10000.00 USD

   Кредит:             0.00 USD
   Кредитное плечо:    1:100
   Режим торговли:     0

   Время сервера:      2026-02-04 15:30:45
   Смещение UTC:       120 минут (UTC+2.0)

╚════════════════════════════════════════════════════════════════╝

🔌 Отключение от MT5...
✅ Успешно отключено!

╔════════════════════════════════════════════════════════════════╗
║   🎉 ПОЗДРАВЛЯЕМ! ВАШ ПЕРВЫЙ ПРОЕКТ РАБОТАЕТ! 🎉              ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🎉 Поздравляем! Вы Это Сделали!

Вы только что:

✅ Создали новый Python-проект с нуля

✅ Интегрировали **единственный** Python-пакет `MetaRpcMT5` для работы с MT5

✅ Настроили параметры подключения

✅ Подключились к терминалу MT5 через gRPC

✅ Получили полную информацию об аккаунте программным способом

**Это был низкоуровневый подход** с использованием `MT5Account` и protobuf напрямую.

---

## 📁 Структура Вашего Проекта

После выполнения всех шагов структура проекта должна выглядеть так:

```
MyMT5Project/
├── venv/                # Виртуальное окружение Python
├── settings.json        # Конфигурация подключения к MT5
├── main.py              # Основной код приложения
```

**Содержимое requirements.txt (опционально):**

Если хотите сохранить зависимости:

```bash
pip freeze > requirements.txt
```

Содержимое будет примерно таким:

```
MetaRpcMT5 @ git+https://github.com/MetaRPC/PyMT5.git@main#subdirectory=package
grpcio>=1.60.0
grpcio-tools>=1.60.0
googleapis-common-protos>=1.56.0
```

---

## 🚀 Что Дальше?

Теперь, когда у вас есть рабочий проект, вы можете:

### 1. Добавить Больше Функциональности

**Примеры того, что вы можете делать:**

#### Получить Текущие Котировки

```python
# Получаем последний тик для символа
tick_data = await account.symbol_info_tick(symbol=config['test_symbol'])

print(f"Последний тик для {config['test_symbol']}:")
print(f"  Bid: {tick_data.bid:.5f}")
print(f"  Ask: {tick_data.ask:.5f}")
print(f"  Last: {tick_data.last:.5f}")
```

#### Получить Все Открытые Позиции

```python
# Получаем все открытые ордера и позиции
opened_data = await account.opened_orders()

print(f"Открытых позиций: {len(opened_data.position_infos)}")
for pos in opened_data.position_infos:
    print(f"  #{pos.ticket} {pos.symbol} {pos.volume:.2f} лотов, Профит: {pos.profit:.2f}")
```

#### Открыть Рыночный Ордер

```python
import MetaRpcMT5.mt5_term_api_trading_pb2 as trading_pb2

# Создаём запрос на открытие ордера
order_req = trading_pb2.OrderSendRequest(
    symbol=config['test_symbol'],
    operation=trading_pb2.TMT5_ORDER_TYPE_BUY,  # Покупка
    volume=0.01,  # 0.01 лот
    comment="PyMT5 Test Order"
)

# Отправляем ордер
order_result = await account.order_send(order_req)

if order_result.retcode == 10009:  # TRADE_RETCODE_DONE
    print(f"✅ Ордер открыт: Deal #{order_result.deal}, Order #{order_result.order}")
else:
    print(f"❌ Ошибка открытия ордера: код {order_result.retcode}")
```

#### Стриминг Данных

```python
import MetaRpcMT5.mt5_term_api_streaming_pb2 as streaming_pb2

# Подписываемся на тики в реальном времени
tick_req = streaming_pb2.OnSymbolTickRequest(
    symbol_names=[config['test_symbol']]
)

# Получаем генератор событий
tick_stream = account.on_symbol_tick(tick_req)

print(f"🔄 Получение потока тиков для {config['test_symbol']}...")
print("   (Нажмите Ctrl+C для остановки)")

event_count = 0
try:
    async for tick_event in tick_stream:
        event_count += 1
        tick = tick_event.symbol_tick
        print(f"[{event_count}] Bid: {tick.bid:.5f}, Ask: {tick.ask:.5f}")

        # Остановка после 10 событий (для примера)
        if event_count >= 10:
            break

except KeyboardInterrupt:
    print(f"\n✅ Получено {event_count} событий")
```

### 2. Изучить Полную Архитектуру SDK

Репозиторий PyMT5 имеет **три уровня API**:

```
┌─────────────────────────────────────────────
│  MT5Sugar (Уровень 3) - Удобный API
│  examples/3_sugar/
│  sugar.buy_market("EURUSD", 0.01)
└─────────────────────────────────────────────
              ↓ использует
┌─────────────────────────────────────────────
│  MT5Service (Уровень 2) - Обёртки
│  examples/2_service/
│  service.get_balance()
└─────────────────────────────────────────────
              ↓ использует
┌─────────────────────────────────────────────
│  MT5Account (Уровень 1) - Базовый gRPC ⭐
│  package/helpers/mt5_account.py
│  account.account_summary()
└─────────────────────────────────────────────
```

**Вы только что использовали Уровень 1 (MT5Account)** - это основа всего!

Чтобы изучить уровни 2 и 3:

- Изучите примеры в папке `examples/`
- Читайте [MT5Account.Master.Overview.md](../MT5Account/MT5Account.Master.Overview.md)
- Смотрите готовые демонстрации

### 3. Изучить Готовые Примеры

Репозиторий PyMT5 содержит множество примеров:

- `examples/1_lowlevel/` - примеры с MT5Account (то, что вы использовали)
- `examples/2_service/` - примеры с MT5Service
- `examples/3_sugar/` - примеры с MT5Sugar
- `examples/4_orchestrators/` - сложные торговые стратегии

**Запуск примеров:**

```bash
cd examples
python main.py
# Выберите нужный пример из интерактивного меню
```

### 4. Прочитать Документацию

- [MT5Account API Reference](../API_Reference/MT5Account.md) - ⭐ полный справочник по базовому уровню
- [MT5Account.Master.Overview.md](../MT5Account/MT5Account.Master.Overview.md) - карта проекта и архитектура
- [GRPC_STREAM_MANAGEMENT.md](./GRPC_STREAM_MANAGEMENT.md) - работа с потоковыми данными
- [RETURN_CODES_REFERENCE.md](./RETURN_CODES_REFERENCE.md) - коды возврата операций
- [ENUMS_USAGE_REFERENCE.md](./ENUMS_USAGE_REFERENCE.md) - использование перечислений

---

## ❓ Часто Задаваемые Вопросы

### Что Такое Пакет MetaRpcMT5?

`MetaRpcMT5` - это **независимый Python-пакет**, который содержит:

- MT5Account (базовый gRPC-клиент)
- Все protobuf-определения MT5 API
- gRPC-заглушки для всех методов
- Вспомогательные типы и структуры

Это **портативный пакет** - вы можете использовать его в любом Python-проекте!

### Как Работать с Переменными Окружения Вместо settings.json?

Вы можете использовать переменные окружения:

```python
import os

def load_settings_from_env():
    """Загрузка настроек из переменных окружения"""
    return {
        'user': int(os.getenv('MT5_USER')),
        'password': os.getenv('MT5_PASSWORD'),
        'grpc_server': os.getenv('MT5_GRPC_SERVER'),
        'mt_cluster': os.getenv('MT5_CLUSTER'),
        'test_symbol': os.getenv('MT5_TEST_SYMBOL', 'EURUSD')
    }
```

**Установите переменные:**

```bash
# Windows (PowerShell)
$env:MT5_USER="591129415"
$env:MT5_PASSWORD="YourPassword123"
$env:MT5_GRPC_SERVER="mt5.mrpc.pro:443"
$env:MT5_CLUSTER="FxPro-MT5 Demo"
$env:MT5_TEST_SYMBOL="EURUSD"

# Linux/Mac
export MT5_USER="591129415"
export MT5_PASSWORD="YourPassword123"
export MT5_GRPC_SERVER="mt5.mrpc.pro:443"
export MT5_CLUSTER="FxPro-MT5 Demo"
export MT5_TEST_SYMBOL="EURUSD"
```

### Как Использовать Уровень 2 (MT5Service) и Уровень 3 (MT5Sugar)?

Эти уровни находятся в **основном репозитории PyMT5**:

1. Клонируйте репозиторий (или скачайте файлы):

   ```bash
   git clone https://github.com/MetaRPC/PyMT5.git
   ```

2. Скопируйте нужные файлы в ваш проект:

   - Из папки `src/` (или соответствующей)
   - MT5Service и MT5Sugar классы

3. Используйте удобные методы:

   ```python
   from mt5_service import MT5Service
   from mt5_sugar import MT5Sugar

   # Уровень 2 - Service
   service = MT5Service(account)
   balance = await service.get_balance()

   # Уровень 3 - Sugar
   sugar = MT5Sugar(service)
   ticket = await sugar.buy_market("EURUSD", 0.01)
   ```

Смотрите детали в [MT5Account.Master.Overview.md](../MT5Account/MT5Account.Master.Overview.md)

### Что Делать Если Возникают Ошибки?

**Ошибка подключения:**
- Проверьте правильность логина/пароля
- Убедитесь что gRPC-сервер доступен
- Проверьте имя кластера (точное имя сервера MT5)

**Таймаут при подключении:**
- Увеличьте `timeout_seconds` до 180 или 240
- Проверьте интернет-соединение
- Проверьте firewall/антивирус

**Ошибки импорта:**
- Убедитесь что виртуальное окружение активировано
- Переустановите пакет: `pip uninstall MetaRpcMT5 && pip install git+https://github.com/MetaRPC/PyMT5.git#subdirectory=package`

---

## 📝 Итоги: Что Мы Сделали

В этом руководстве вы создали минималистичный проект, который:

1. ✅ **Использует только Python-модули** - не требует клонирования репозитория

2. ✅ **Импортирует пакет MetaRpcMT5** - единственная зависимость для MT5

3. ✅ **Подключается к MT5** через gRPC-шлюз

4. ✅ **Читает конфигурацию** из `settings.json`

5. ✅ **Использует MT5Account** (Уровень 1 - базовый уровень)

6. ✅ **Получает информацию об аккаунте** и выводит в консоль

**Это фундамент** для любых ваших MT5-проектов на Python.

---

**Удачи в разработке торговых систем! 🚀**

"Торгуйте безопасно, пишите чисто, и пусть ваши gRPC-соединения всегда будут стабильны."
