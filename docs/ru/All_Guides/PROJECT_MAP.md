# 🗺️ Карта проекта PyMT5

> Весь проект в виде одного аннотированного дерева со ссылками. **Ссылки ведут на *обзоры* разделов, а не на страницы отдельных методов** — откройте обзор, чтобы углубиться в его методы.

---

## 🧱 Три уровня

PyMT5 построен из трёх развязанных уровней. Ваш код может войти на любом уровне.

| Уровень | Исходник | Что он делает | Обзор |
| ----- | ------ | ------------ | -------- |
| **3 · MT5Sugar** | `src/pymt5/mt5_sugar.py` | Удобства поверх Service: расчёт размера на основе риска, нормализация цены/объёма, помощники со смещением в пунктах, пакетное закрытие/отмена. | [Обзор MT5Sugar](https://metarpc.github.io/PyMT5/MT5Sugar/MT5Sugar.Master.Overview/) |
| **2 · MT5Service** | `src/pymt5/mt5_service.py` | Типизированный фасад: чистые сигнатуры, возвращающие готовые данные Python (без сырого proto). То, что использует большинство кода. | [Обзор MT5Service](https://metarpc.github.io/PyMT5/MT5Service/MT5Service.Overview/) |
| **1 · MT5Account** | `package/MetaRpcMT5/mt5_account.py` | Низкоуровневый gRPC: proto-запрос/ответ, подключение/сессия, авто-переподключение, стриминг. Всё остальное строится на нём. | [Обзор MT5Account](https://metarpc.github.io/PyMT5/MT5Account/MT5Account.Master.Overview/) |

```
Ваш код  →  MT5Sugar  →  MT5Service  →  MT5Account  →  gRPC  →  шлюз MetaRPC → терминал MT5
```

---

## 🌳 Дерево репозитория

- **`PyMT5/`** — корень репозитория (демо-проект с примерами; сам SDK — это импортируемый пакет `pymt5`)
  - **`src/pymt5/`** — пакет, который вы `import`
    - `mt5_service.py` — исходник **уровня 2** → [Обзор MT5Service](https://metarpc.github.io/PyMT5/MT5Service/MT5Service.Overview/)
    - `mt5_sugar.py` — исходник **уровня 3** → [Обзор MT5Sugar](https://metarpc.github.io/PyMT5/MT5Sugar/MT5Sugar.Master.Overview/)
  - **`package/MetaRpcMT5/`** — низкоуровневый слой gRPC
    - `mt5_account.py` — исходник **уровня 1** → [Обзор MT5Account](https://metarpc.github.io/PyMT5/MT5Account/MT5Account.Master.Overview/)
    - **`helpers/`** — `errors.py`, помощники подключения и повторных попыток
    - `*_pb2.py` / `*_pb2_grpc.py` — сгенерированные заглушки gRPC / protobuf (сырой контракт)
  - **`examples/`** — запускаемые демо (нумерованное меню), запускаются из `main.py`
    - `main.py` — интерактивное меню / запуск из CLI → [Начало работы](GETTING_STARTED.md)
    - **`0_common/`** — общие помощники (`demo_helpers.py`, `progress_bar.py`) + `settings.json` (ваши учётные данные MT5) · инспектор protobuf (16) → [Инспектор Protobuf](PROTOBUF_INSPECTOR_GUIDE.md)
    - **`1_lowlevel/`** — `01`–`03` → [Обзор MT5Account](https://metarpc.github.io/PyMT5/MT5Account/MT5Account.Master.Overview/)
    - **`2_service/`** — `04`–`05` → [Обзор MT5Service](https://metarpc.github.io/PyMT5/MT5Service/MT5Service.Overview/)
    - **`3_sugar/`** — `06`–`10` → [Обзор MT5Sugar](https://metarpc.github.io/PyMT5/MT5Sugar/MT5Sugar.Master.Overview/)
    - **`4_orchestrators/`** — `11`–`15` → [Обзор Strategies](https://metarpc.github.io/PyMT5/Strategies/Strategies.Master.Overview/)
    - **`5_usercode/`** — `17` → [Песочница UserCode](USERCODE_SANDBOX_GUIDE.md)
  - **`docs/`** — этот сайт документации (см. карту ниже)
  - **`tests/`** — модульные тесты
  - `mkdocs.yml` — конфигурация сайта документации · `.github/workflows/` — CI

---

## 📚 Дерево документации

- **`docs/`**
  - [Главная](../index.md) — стартовая страница
  - **`All_Guides/`** — руководства (Начало работы, Ваш первый проект, Глоссарий, Sync vs Async, Стриминг gRPC, ENUM-ы, Коды возврата, …); просматривайте их в левой навигации или на [сайте документации](https://metarpc.github.io/PyMT5/)
  - **`MT5Account/`** — документация низкоуровневого gRPC → [обзор](https://metarpc.github.io/PyMT5/MT5Account/MT5Account.Master.Overview/) *(внутри — страницы по методам)*
  - **`MT5Service/`** — документация типизированного фасада → [обзор](https://metarpc.github.io/PyMT5/MT5Service/MT5Service.Overview/) *(внутри — страницы по методам)*
  - **`MT5Sugar/`** — документация удобного API → [обзор](https://metarpc.github.io/PyMT5/MT5Sugar/MT5Sugar.Master.Overview/) *(внутри — страницы по методам)*
  - **`Strategies/`** — пять оркестраторов → [обзор](https://metarpc.github.io/PyMT5/Strategies/Strategies.Master.Overview/) *(внутри — страницы по стратегиям)*
  - `Guide_Images/` · `styles/` · `javascripts/` · `includes/` — ресурсы и тема

> Папки `MT5Account/`, `MT5Service/`, `MT5Sugar/` и `Strategies/` содержат страницы по методам / по стратегиям. По замыслу эта карта ссылается только на их **обзоры** — каждый обзор является указателем на свои детальные страницы.

---

## 🎯 Какой уровень вам использовать?

- **Большинство торговых приложений → [MT5Sugar](https://metarpc.github.io/PyMT5/MT5Sugar/MT5Sugar.Master.Overview/).** Расчёт размера по риску и авто-нормализация защищают вас от отказов из-за off-quote и неверного объёма.
- **Собственное исполнение → [MT5Service](https://metarpc.github.io/PyMT5/MT5Service/MT5Service.Overview/).** Типизированные вызовы, когда вы сами управляете расчётом размера/нормализацией.
- **Контроль на уровне протокола → [MT5Account](https://metarpc.github.io/PyMT5/MT5Account/MT5Account.Master.Overview/).** Сырые proto-структуры и потоки.
