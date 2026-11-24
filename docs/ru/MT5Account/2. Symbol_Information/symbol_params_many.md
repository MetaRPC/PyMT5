# Получение полного набора параметров символа

> **Запрос:** получить все параметры символа за один вызов (РЕКОМЕНДУЕТСЯ для эффективного получения нескольких свойств).

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_params_many(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.AccountHelper`
* **Proto-определение:** `SymbolParamsMany` (определено в `mt5-term-api-account-helper.proto`)

### RPC

* **Сервис:** `mt5_term_api.AccountHelper`
* **Метод:** `SymbolParamsMany(SymbolParamsManyRequest) -> SymbolParamsManyReply`
* **Низкоуровневый клиент (сгенерированный):** `AccountHelperStub.SymbolParamsMany(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить полный набор параметров символа за один вызов (100+ полей: цены, спреды, маржа, свопы, объёмы).
* **Зачем это нужно.** Самый эффективный способ получить несколько свойств символа — один вызов вместо десятков вызовов `symbol_info_*`.
* **Когда использовать.** Используйте для получения полной информации о символе. Используйте `symbol_info_*` только для отдельных конкретных свойств.

---

## 🎯 Назначение

Используйте для эффективного получения данных о символе:

* Получить все параметры символа за один эффективный вызов
* Получить данные для одного конкретного символа или всех символов
* Построить полные сравнительные таблицы символов
* Эффективно рассчитать торговые издержки и маржу
* Фильтровать и сортировать символы по различным критериям
* Постранично обрабатывать большие списки символов
* Избежать множественных RPC-вызовов для одного символа

---

## 📚 Руководство

Подробное построчное объяснение с примерами см.:
**-> [symbol_params_many - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_params_many_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_params_many(
    self,
    request: account_helper_pb2.SymbolParamsManyRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.SymbolParamsManyData
```

**Сообщение запроса:**

```protobuf
message SymbolParamsManyRequest {
  optional string symbol_name = 1;
  optional AH_SYMBOL_PARAMS_MANY_SORT_TYPE sort_type = 2;
  optional int32 page_number = 3;
  optional int32 items_per_page = 4;
}
```

**Сообщение ответа:**

```protobuf
message SymbolParamsManyReply {
  oneof response {
    SymbolParamsManyData data = 1;
    Error error = 2;
  }
}

message SymbolParamsManyData {
  repeated SymbolParameters symbol_infos = 1;
  int32 symbols_total = 2;
  optional int32 page_number = 3;
  optional int32 items_per_page = 4;
}
```

**Структура SymbolParameters:**

Сообщение `SymbolParameters` содержит **116 полей**, сгруппированных по категориям:

**1. Ценовые данные (9 полей)**

- `bid`, `ask`, `last` - Текущие цены
- `bid_high`, `bid_low` - Диапазон цены bid
- `ask_high`, `ask_low` - Диапазон цены ask
- `last_high`, `last_low` - Диапазон последней цены

**2. Данные объёма (10 полей)**

- `volume`, `volume_high`, `volume_low` - Объём в лотах
- `volume_real`, `volume_high_real`, `volume_low_real` - Реальный объём
- `volume_min`, `volume_max`, `volume_step`, `volume_limit` - Ограничения объёма

**3. Спред и точность (4 поля)**

- `spread` - Текущий спред в пунктах
- `spread_float` - Флаг плавающего спреда
- `digits` - Количество знаков после запятой
- `point` - Значение пункта

**4. Параметры контракта и торговли (10 полей)**

- `trade_contract_size` - Размер контракта
- `trade_tick_size` - Размер тика
- `trade_tick_value`, `trade_tick_value_profit`, `trade_tick_value_loss` - Значения тика

- `trade_accrued_interest` - Накопленный процент
- `trade_face_value` - Номинальная стоимость
- `trade_liquidity_rate` - Коэффициент ликвидности
- `trade_stops_level`, `trade_freeze_level` - Уровни стопов

**5. Требования к марже (4 поля)**

- `margin_initial`, `margin_maintenance` - Начальная и поддерживающая маржа
- `margin_hedged` - Маржа для хеджирования
- `margin_hedged_use_leg` - Использовать ногу для маржи хеджирования

**6. Данные свопов (11 полей)**

- `swap_long`, `swap_short` - Своп по длинным/коротким позициям
- `swap_sunday`, `swap_monday`, `swap_tuesday`, `swap_wednesday`, `swap_thursday`, `swap_friday`, `swap_saturday` - Ежедневные свопы
- `swap_mode` - Режим расчёта свопа
- `swap_rollover_3days` - День тройного свопа

**7. Статистика сессии (14 полей)**

- `session_volume`, `session_turnover`, `session_interest` - Итоги сессии
- `session_buy_orders_volume`, `session_sell_orders_volume` - Объёмы ордеров
- `session_open`, `session_close`, `session_aw` - Цены сессии
- `session_price_settlement` - Расчётная цена
- `session_price_limit_min`, `session_price_limit_max` - Ценовые лимиты
- `session_deals` - Количество сделок
- `session_buy_orders`, `session_sell_orders` - Количество ордеров

**8. Данные опционов (3 поля)**

- `option_strike` - Цена страйк
- `option_mode` - Режим опциона
- `option_right` - Право опциона (call/put)

**9. Греки и ценообразование (8 полей)**

- `price_theoretical` - Теоретическая цена
- `price_delta`, `price_theta`, `price_gamma`, `price_vega`, `price_rho`, `price_omega` - Греки
- `price_sensitivity` - Чувствительность цены

**10. Рыночная статистика (2 поля)**

- `price_change` - Изменение цены
- `price_volatility` - Волатильность

**11. Временные метки (8 полей)**

- `time`, `time_msc` - Время последнего обновления (в часовом поясе сервера брокера)
- `start_time` - Время начала торгов
- `expiration_time` - Время истечения
- `time_utc`, `time_msc_utc` - Время последнего обновления в UTC
- `start_time_utc`, `expiration_time_utc` - Время начала торгов / истечения в UTC

**12. Режимы торговли (9 полей)**

- `trade_calc_mode` - Режим расчёта
- `trade_mode` - Режим торговли
- `trade_exe_mode` - Режим исполнения
- `expiration_mode` - Режим истечения ордера
- `filling_mode` - Режим заполнения ордера
- `order_mode` - Режим ордера
- `order_gtc_mode` - Режим GTC
- `chart_mode` - Режим графика
- `ticks_book_depth` - Глубина стакана

**13. Идентификаторы и описание (11 полей)**

- `name` - Имя символа
- `sym_description` - Описание символа (примечание: имя поля `sym_description`, а не `description`)
- `path` - Путь символа
- `currency_base`, `currency_profit`, `currency_margin` - Валюты
- `isin` - Код ISIN
- `basis` - Базис
- `category` - Категория
- `page` - Страница
- `formula` - Формула

**14. Классификация (6 полей)**

- `sector`, `sector_name` - Сектор
- `industry`, `industry_name` - Отрасль
- `country` - Страна
- `bank` - Банк

**15. Отображение и статус (6 полей)**

- `exist` - Символ существует
- `select` - Символ выбран
- `visible` - Символ виден
- `subscription_delay` - Задержка подписки
- `background_color` - Цвет фона
- `custom` - Пользовательские данные

**16. Биржа (1 поле)**

- `exchange` - Название биржи

**Итого: 116 полей**, предоставляющих полную информацию о символе за один эффективный вызов.

---

## 🔽 Вход

| Параметр      | Тип                                               | Описание                                                        |
| ------------- | ------------------------------------------------- | --------------------------------------------------------------- |
| `request`     | `SymbolParamsManyRequest` (обязательно)           | Объект запроса с параметрами фильтрации/пагинации               |
| `deadline`    | `datetime` (необязательно)                        | Крайний срок для gRPC-вызова (datetime в UTC)                   |
| `cancellation_event` | `asyncio.Event` (необязательно)            | Событие для отмены операции                                     |

### Поля запроса:

| Поле            | Тип                                 | Описание                                         |
| --------------- | ----------------------------------- | ------------------------------------------------ |
| `symbol_name`   | `string` (необязательно)            | Фильтр по имени символа (отсутствует или пусто = все символы) |
| `sort_type`     | `AH_SYMBOL_PARAMS_MANY_SORT_TYPE` (необязательно) | Порядок сортировки результатов          |
| `page_number`   | `int32` (необязательно)             | Номер страницы для пагинации (с нуля, по умолчанию 0)  |
| `items_per_page`| `int32` (необязательно)             | Элементов на страницу (0 или отсутствует = все элементы)           |

---

## ⬆️ Выход

| Поле           | Тип                         | Python-тип               | Описание                                 |
| -------------- | --------------------------- | ------------------------ | ---------------------------------------- |
| `symbol_infos` | `repeated SymbolParameters` | `list[SymbolParameters]` | Список объектов параметров символов       |
| `symbols_total`| `int32`                     | `int`                    | Общее количество символов                |
| `page_number`  | `int32` (необязательно)     | `int`                    | Текущий номер страницы                   |
| `items_per_page`| `int32` (необязательно)    | `int`                    | Элементов на страницу                    |

**Возвращаемое значение:** Метод возвращает объект `SymbolParamsManyData` со списком параметров символов и информацией о пагинации.

---

## 🧱 Связанные enum (из proto)

> **Примечание:** Все enum доступны из модуля `mt5_term_api_account_helper_pb2`. Этот метод использует **14 enum** с **231 константой** в общей сложности.

### `AH_SYMBOL_PARAMS_MANY_SORT_TYPE` (параметр запроса)

| Константа | Значение | Описание |
|----------|-------|-------------|
| `AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_ASC` | 0 | Имя символа по возрастанию (A-Z) |
| `AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_DESC` | 1 | Имя символа по убыванию (Z-A) |
| `AH_PARAMS_MANY_SORT_TYPE_MQL_INDEX_ASC` | 2 | Индекс MQL по возрастанию |
| `AH_PARAMS_MANY_SORT_TYPE_MQL_INDEX_DESC` | 3 | Индекс MQL по убыванию |

### `BMT5_ENUM_SYMBOL_CHART_MODE` (для поля `chart_mode`)

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_SYMBOL_CHART_MODE_BID` | 0 | Бары на основе цен Bid |
| `BMT5_SYMBOL_CHART_MODE_LAST` | 1 | Бары на основе цен Last |

### `BMT5_ENUM_ORDER_TYPE_FILLING` (для поля `filling_mode`)

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_ORDER_FILLING_FOK` | 0 | Fill or Kill - исполнить полностью или отменить |
| `BMT5_ORDER_FILLING_IOC` | 1 | Immediate or Cancel - исполнить доступный объём |
| `BMT5_ORDER_FILLING_RETURN` | 2 | Режим исполнения Return |
| `BMT5_ORDER_FILLING_BOC` | 3 | Book or Cancel - разместить ордер в стакане |

### `BMT5_ENUM_SYMBOL_INDUSTRY` (для поля `industry`)

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_INDUSTRY_UNDEFINED` | 0 | Не определено |
| `BMT5_INDUSTRY_AGRICULTURAL_INPUTS` | 1 | Сельскохозяйственные ресурсы |
| `BMT5_INDUSTRY_ALUMINIUM` | 2 | Алюминий |
| `BMT5_INDUSTRY_BUILDING_MATERIALS` | 3 | Строительные материалы |
| `BMT5_INDUSTRY_CHEMICALS` | 4 | Химическая продукция |
| `BMT5_INDUSTRY_COKING_COAL` | 5 | Коксующийся уголь |
| `BMT5_INDUSTRY_COPPER` | 6 | Медь |
| `BMT5_INDUSTRY_GOLD` | 7 | Золото |
| `BMT5_INDUSTRY_LUMBER_WOOD` | 8 | Пиломатериалы и древесина |
| `BMT5_INDUSTRY_INDUSTRIAL_METALS` | 9 | Промышленные металлы |
| `BMT5_INDUSTRY_PRECIOUS_METALS` | 10 | Драгоценные металлы |
| `BMT5_INDUSTRY_PAPER` | 11 | Бумага |
| `BMT5_INDUSTRY_SILVER` | 12 | Серебро |
| `BMT5_INDUSTRY_SPECIALTY_CHEMICALS` | 13 | Специальная химия |
| `BMT5_INDUSTRY_STEEL` | 14 | Сталь |
| `BMT5_INDUSTRY_ADVERTISING` | 15 | Реклама |
| `BMT5_INDUSTRY_BROADCASTING` | 16 | Вещание |
| `BMT5_INDUSTRY_GAMING_MULTIMEDIA` | 17 | Игры и мультимедиа |
| `BMT5_INDUSTRY_ENTERTAINMENT` | 18 | Развлечения |
| `BMT5_INDUSTRY_INTERNET_CONTENT` | 19 | Интернет-контент |
| `BMT5_INDUSTRY_PUBLISHING` | 20 | Издательское дело |
| `BMT5_INDUSTRY_TELECOM` | 21 | Телекоммуникации |
| `BMT5_INDUSTRY_APPAREL_MANUFACTURING` | 22 | Производство одежды |
| `BMT5_INDUSTRY_APPAREL_RETAIL` | 23 | Розничная торговля одеждой |
| `BMT5_INDUSTRY_AUTO_MANUFACTURERS` | 24 | Производители автомобилей |
| `BMT5_INDUSTRY_AUTO_PARTS` | 25 | Автозапчасти |
| `BMT5_INDUSTRY_AUTO_DEALERSHIP` | 26 | Автодилеры |
| `BMT5_INDUSTRY_DEPARTMENT_STORES` | 27 | Универмаги |
| `BMT5_INDUSTRY_FOOTWEAR_ACCESSORIES` | 28 | Обувь и аксессуары |
| `BMT5_INDUSTRY_FURNISHINGS` | 29 | Мебель и предметы интерьера |
| `BMT5_INDUSTRY_GAMBLING` | 30 | Азартные игры |
| `BMT5_INDUSTRY_HOME_IMPROV_RETAIL` | 31 | Розничная торговля товарами для дома |
| `BMT5_INDUSTRY_INTERNET_RETAIL` | 32 | Интернет-торговля |
| `BMT5_INDUSTRY_LEISURE` | 33 | Досуг |
| `BMT5_INDUSTRY_LODGING` | 34 | Размещение/проживание |
| `BMT5_INDUSTRY_LUXURY_GOODS` | 35 | Товары роскоши |
| `BMT5_INDUSTRY_PACKAGING_CONTAINERS` | 36 | Упаковка и контейнеры |
| `BMT5_INDUSTRY_PERSONAL_SERVICES` | 37 | Персональные услуги |
| `BMT5_INDUSTRY_RECREATIONAL_VEHICLES` | 38 | Транспорт для отдыха |
| `BMT5_INDUSTRY_RESIDENT_CONSTRUCTION` | 39 | Жилищное строительство |
| `BMT5_INDUSTRY_RESORTS_CASINOS` | 40 | Курорты и казино |
| `BMT5_INDUSTRY_RESTAURANTS` | 41 | Рестораны |
| `BMT5_INDUSTRY_SPECIALTY_RETAIL` | 42 | Специализированная розница |
| `BMT5_INDUSTRY_TEXTILE_MANUFACTURING` | 43 | Текстильное производство |
| `BMT5_INDUSTRY_TRAVEL_SERVICES` | 44 | Туристические услуги |
| `BMT5_INDUSTRY_BEVERAGES_BREWERS` | 45 | Напитки - пивовары |
| `BMT5_INDUSTRY_BEVERAGES_NON_ALCO` | 46 | Напитки - безалкогольные |
| `BMT5_INDUSTRY_BEVERAGES_WINERIES` | 47 | Напитки - винодельни |
| `BMT5_INDUSTRY_CONFECTIONERS` | 48 | Кондитеры |
| `BMT5_INDUSTRY_DISCOUNT_STORES` | 49 | Дисконтные магазины |
| `BMT5_INDUSTRY_EDUCATION_TRAINIG` | 50 | Образование и обучение |
| `BMT5_INDUSTRY_FARM_PRODUCTS` | 51 | Фермерская продукция |
| `BMT5_INDUSTRY_FOOD_DISTRIBUTION` | 52 | Дистрибуция продуктов питания |
| `BMT5_INDUSTRY_GROCERY_STORES` | 53 | Продуктовые магазины |
| `BMT5_INDUSTRY_HOUSEHOLD_PRODUCTS` | 54 | Товары для дома |
| `BMT5_INDUSTRY_PACKAGED_FOODS` | 55 | Упакованные продукты питания |
| `BMT5_INDUSTRY_TOBACCO` | 56 | Табак |
| `BMT5_INDUSTRY_OIL_GAS_DRILLING` | 57 | Нефтегазовое бурение |
| `BMT5_INDUSTRY_OIL_GAS_EP` | 58 | Нефть и газ: разведка и добыча |
| `BMT5_INDUSTRY_OIL_GAS_EQUIPMENT` | 59 | Нефтегазовое оборудование |
| `BMT5_INDUSTRY_OIL_GAS_INTEGRATED` | 60 | Нефть и газ: интегрированные |
| `BMT5_INDUSTRY_OIL_GAS_MIDSTREAM` | 61 | Нефть и газ: транспортировка |
| `BMT5_INDUSTRY_OIL_GAS_REFINING` | 62 | Нефть и газ: переработка |
| `BMT5_INDUSTRY_THERMAL_COAL` | 63 | Энергетический уголь |
| `BMT5_INDUSTRY_URANIUM` | 64 | Уран |
| `BMT5_INDUSTRY_EXCHANGE_TRADED_FUND` | 65 | Биржевой фонд (ETF) |
| `BMT5_INDUSTRY_ASSETS_MANAGEMENT` | 66 | Управление активами |
| `BMT5_INDUSTRY_BANKS_DIVERSIFIED` | 67 | Банки - диверсифицированные |
| `BMT5_INDUSTRY_BANKS_REGIONAL` | 68 | Банки - региональные |
| `BMT5_INDUSTRY_CAPITAL_MARKETS` | 69 | Рынки капитала |
| `BMT5_INDUSTRY_CLOSE_END_FUND_DEBT` | 70 | Закрытый фонд - долговой |
| `BMT5_INDUSTRY_CLOSE_END_FUND_EQUITY` | 71 | Закрытый фонд - акционерный |
| `BMT5_INDUSTRY_CLOSE_END_FUND_FOREIGN` | 72 | Закрытый фонд - иностранный |
| `BMT5_INDUSTRY_CREDIT_SERVICES` | 73 | Кредитные услуги |
| `BMT5_INDUSTRY_FINANCIAL_CONGLOMERATE` | 74 | Финансовый конгломерат |
| `BMT5_INDUSTRY_FINANCIAL_DATA_EXCHANGE` | 75 | Финансовые данные и биржи |
| `BMT5_INDUSTRY_INSURANCE_BROKERS` | 76 | Страховые брокеры |
| `BMT5_INDUSTRY_INSURANCE_DIVERSIFIED` | 77 | Страхование - диверсифицированное |
| `BMT5_INDUSTRY_INSURANCE_LIFE` | 78 | Страхование - жизни |
| `BMT5_INDUSTRY_INSURANCE_PROPERTY` | 79 | Страхование - имущества и от несчастных случаев |
| `BMT5_INDUSTRY_INSURANCE_REINSURANCE` | 80 | Страхование - перестрахование |
| `BMT5_INDUSTRY_INSURANCE_SPECIALTY` | 81 | Страхование - специальное |
| `BMT5_INDUSTRY_MORTGAGE_FINANCE` | 82 | Ипотечное финансирование |
| `BMT5_INDUSTRY_SHELL_COMPANIES` | 83 | Компании-оболочки |
| `BMT5_INDUSTRY_BIOTECHNOLOGY` | 84 | Биотехнологии |
| `BMT5_INDUSTRY_DIAGNOSTICS_RESEARCH` | 85 | Диагностика и исследования |
| `BMT5_INDUSTRY_DRUGS_MANUFACTURERS` | 86 | Производители лекарств - общие |
| `BMT5_INDUSTRY_DRUGS_MANUFACTURERS_SPEC` | 87 | Производители лекарств - специальные |
| `BMT5_INDUSTRY_HEALTHCARE_PLANS` | 88 | Планы здравоохранения |
| `BMT5_INDUSTRY_HEALTH_INFORMATION` | 89 | Информационные услуги в здравоохранении |
| `BMT5_INDUSTRY_MEDICAL_FACILITIES` | 90 | Медицинские учреждения |
| `BMT5_INDUSTRY_MEDICAL_DEVICES` | 91 | Медицинские приборы |
| `BMT5_INDUSTRY_MEDICAL_DISTRIBUTION` | 92 | Медицинская дистрибуция |
| `BMT5_INDUSTRY_MEDICAL_INSTRUMENTS` | 93 | Медицинские инструменты и расходные материалы |
| `BMT5_INDUSTRY_PHARM_RETAILERS` | 94 | Фармацевтические ритейлеры |
| `BMT5_INDUSTRY_AEROSPACE_DEFENSE` | 95 | Аэрокосмическая отрасль и оборона |
| `BMT5_INDUSTRY_AIRLINES` | 96 | Авиакомпании |
| `BMT5_INDUSTRY_AIRPORTS_SERVICES` | 97 | Аэропорты и авиауслуги |
| `BMT5_INDUSTRY_BUILDING_PRODUCTS` | 98 | Строительная продукция и оборудование |
| `BMT5_INDUSTRY_BUSINESS_EQUIPMENT` | 99 | Бизнес-оборудование и расходные материалы |
| `BMT5_INDUSTRY_CONGLOMERATES` | 100 | Конгломераты |
| `BMT5_INDUSTRY_CONSULTING_SERVICES` | 101 | Консалтинговые услуги |
| `BMT5_INDUSTRY_ELECTRICAL_EQUIPMENT` | 102 | Электрооборудование и комплектующие |
| `BMT5_INDUSTRY_ENGINEERING_CONSTRUCTION` | 103 | Инжиниринг и строительство |
| `BMT5_INDUSTRY_FARM_HEAVY_MACHINERY` | 104 | Сельскохозяйственная и тяжёлая техника |
| `BMT5_INDUSTRY_INDUSTRIAL_DISTRIBUTION` | 105 | Промышленная дистрибуция |
| `BMT5_INDUSTRY_INFRASTRUCTURE_OPERATIONS` | 106 | Эксплуатация инфраструктуры |
| `BMT5_INDUSTRY_FREIGHT_LOGISTICS` | 107 | Грузоперевозки и логистические услуги |
| `BMT5_INDUSTRY_MARINE_SHIPPING` | 108 | Морские перевозки |
| `BMT5_INDUSTRY_METAL_FABRICATION` | 109 | Металлообработка |
| `BMT5_INDUSTRY_POLLUTION_CONTROL` | 110 | Контроль загрязнений и очистка |
| `BMT5_INDUSTRY_RAILROADS` | 111 | Железные дороги |
| `BMT5_INDUSTRY_RENTAL_LEASING` | 112 | Услуги аренды и лизинга |
| `BMT5_INDUSTRY_SECURITY_PROTECTION` | 113 | Услуги безопасности и охраны |
| `BMT5_INDUSTRY_SPEALITY_BUSINESS_SERVICES` | 114 | Специализированные бизнес-услуги |
| `BMT5_INDUSTRY_SPEALITY_MACHINERY` | 115 | Специализированное промышленное оборудование |
| `BMT5_INDUSTRY_STUFFING_EMPLOYMENT` | 116 | Услуги по подбору персонала и трудоустройству |
| `BMT5_INDUSTRY_TOOLS_ACCESSORIES` | 117 | Инструменты и принадлежности |
| `BMT5_INDUSTRY_TRUCKING` | 118 | Автоперевозки |
| `BMT5_INDUSTRY_WASTE_MANAGEMENT` | 119 | Управление отходами |
| `BMT5_INDUSTRY_REAL_ESTATE_DEVELOPMENT` | 120 | Недвижимость - девелопмент |
| `BMT5_INDUSTRY_REAL_ESTATE_DIVERSIFIED` | 121 | Недвижимость - диверсифицированная |
| `BMT5_INDUSTRY_REAL_ESTATE_SERVICES` | 122 | Услуги в сфере недвижимости |
| `BMT5_INDUSTRY_REIT_DIVERSIFIED` | 123 | REIT - диверсифицированный |
| `BMT5_INDUSTRY_REIT_HEALTCARE` | 124 | REIT - медицинские учреждения |
| `BMT5_INDUSTRY_REIT_HOTEL_MOTEL` | 125 | REIT - отели и мотели |
| `BMT5_INDUSTRY_REIT_INDUSTRIAL` | 126 | REIT - промышленный |
| `BMT5_INDUSTRY_REIT_MORTAGE` | 127 | REIT - ипотечный |
| `BMT5_INDUSTRY_REIT_OFFICE` | 128 | REIT - офисный |
| `BMT5_INDUSTRY_REIT_RESIDENTAL` | 129 | REIT - жилой |
| `BMT5_INDUSTRY_REIT_RETAIL` | 130 | REIT - торговый |
| `BMT5_INDUSTRY_REIT_SPECIALITY` | 131 | REIT - специализированный |
| `BMT5_INDUSTRY_COMMUNICATION_EQUIPMENT` | 132 | Коммуникационное оборудование |
| `BMT5_INDUSTRY_COMPUTER_HARDWARE` | 133 | Компьютерное оборудование |
| `BMT5_INDUSTRY_CONSUMER_ELECTRONICS` | 134 | Потребительская электроника |
| `BMT5_INDUSTRY_ELECTRONIC_COMPONENTS` | 135 | Электронные компоненты |
| `BMT5_INDUSTRY_ELECTRONIC_DISTRIBUTION` | 136 | Дистрибуция электроники и компьютеров |
| `BMT5_INDUSTRY_IT_SERVICES` | 137 | Услуги в сфере информационных технологий |
| `BMT5_INDUSTRY_SCIENTIFIC_INSTRUMENTS` | 138 | Научные и технические приборы |
| `BMT5_INDUSTRY_SEMICONDUCTOR_EQUIPMENT` | 139 | Оборудование и материалы для полупроводников |
| `BMT5_INDUSTRY_SEMICONDUCTORS` | 140 | Полупроводники |
| `BMT5_INDUSTRY_SOFTWARE_APPLICATION` | 141 | ПО - прикладное |
| `BMT5_INDUSTRY_SOFTWARE_INFRASTRUCTURE` | 142 | ПО - инфраструктурное |
| `BMT5_INDUSTRY_SOLAR` | 143 | Солнечная энергетика |
| `BMT5_INDUSTRY_UTILITIES_DIVERSIFIED` | 144 | Коммунальные услуги - диверсифицированные |
| `BMT5_INDUSTRY_UTILITIES_POWERPRODUCERS` | 145 | Коммунальные услуги - независимые производители энергии |
| `BMT5_INDUSTRY_UTILITIES_RENEWABLE` | 146 | Коммунальные услуги - возобновляемые источники |
| `BMT5_INDUSTRY_UTILITIES_REGULATED_ELECTRIC` | 147 | Коммунальные услуги - регулируемое электроснабжение |
| `BMT5_INDUSTRY_UTILITIES_REGULATED_GAS` | 148 | Коммунальные услуги - регулируемое газоснабжение |
| `BMT5_INDUSTRY_UTILITIES_REGULATED_WATER` | 149 | Коммунальные услуги - регулируемое водоснабжение |
| `BMT5_INDUSTRY_UTILITIES_FIRST` | 150 | Коммунальные услуги - первый (маркер диапазона) |
| `BMT5_INDUSTRY_UTILITIES_LAST` | 151 | Коммунальные услуги - последний (маркер диапазона) |

### `BMT5_ENUM_SYMBOL_OPTION_MODE` (для поля `option_mode`)

**Python-константы:**

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_SYMBOL_OPTION_MODE_EUROPEAN` | 0 | Европейский опцион - исполнение только при истечении |
| `BMT5_SYMBOL_OPTION_MODE_AMERICAN` | 1 | Американский опцион - исполнение в любое время |

### `BMT5_ENUM_SYMBOL_OPTION_RIGHT` (для поля `option_right`)

**Python-константы:**

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_SYMBOL_OPTION_RIGHT_CALL` | 0 | Опцион колл - право на покупку |
| `BMT5_SYMBOL_OPTION_RIGHT_PUT` | 1 | Опцион пут - право на продажу |

### `BMT5_ENUM_SYMBOL_ORDER_GTC_MODE` (для поля `order_gtc_mode`)

**Python-константы:**

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_SYMBOL_ORDERS_GTC` | 0 | Разрешены ордера Good Till Cancelled |
| `BMT5_SYMBOL_ORDERS_DAILY` | 1 | Только дневные ордера |
| `BMT5_SYMBOL_ORDERS_DAILY_EXCLUDING_STOPS` | 2 | Дневные, исключая стопы |

### `BMT5_ENUM_ORDER_TYPE` (для поля `order_mode`)

**Python-константы:**

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_ORDER_TYPE_BUY` | 0 | Рыночный ордер Buy |
| `BMT5_ORDER_TYPE_SELL` | 1 | Рыночный ордер Sell |
| `BMT5_ORDER_TYPE_BUY_LIMIT` | 2 | Отложенный ордер Buy Limit |
| `BMT5_ORDER_TYPE_SELL_LIMIT` | 3 | Отложенный ордер Sell Limit |
| `BMT5_ORDER_TYPE_BUY_STOP` | 4 | Отложенный ордер Buy Stop |
| `BMT5_ORDER_TYPE_SELL_STOP` | 5 | Отложенный ордер Sell Stop |
| `BMT5_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Отложенный ордер Buy Stop Limit |
| `BMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Отложенный ордер Sell Stop Limit |
| `BMT5_ORDER_TYPE_CLOSE_BY` | 8 | Ордер Close By |

### `BMT5_ENUM_SYMBOL_SECTOR` (для поля `sector`)

**Python-константы:**

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_SECTOR_UNDEFINED` | 0 | Сектор не определён |
| `BMT5_SECTOR_BASIC_MATERIALS` | 1 | Базовые материалы |
| `BMT5_SECTOR_COMMUNICATION_SERVICES` | 2 | Коммуникационные услуги |
| `BMT5_SECTOR_CONSUMER_CYCLICAL` | 3 | Потребительский цикличный |
| `BMT5_SECTOR_CONSUMER_DEFENSIVE` | 4 | Потребительский защитный |
| `BMT5_SECTOR_CURRENCY` | 5 | Валюта |
| `BMT5_SECTOR_CURRENCY_CRYPTO` | 6 | Криптовалюта |
| `BMT5_SECTOR_ENERGY` | 7 | Энергетика |
| `BMT5_SECTOR_FINANCIAL` | 8 | Финансовый |
| `BMT5_SECTOR_HEALTHCARE` | 9 | Здравоохранение |
| `BMT5_SECTOR_INDUSTRIALS` | 10 | Промышленность |
| `BMT5_SECTOR_REAL_ESTATE` | 11 | Недвижимость |
| `BMT5_SECTOR_TECHNOLOGY` | 12 | Технологии |
| `BMT5_SECTOR_UTILITIES` | 13 | Коммунальные услуги |

### `BMT5_ENUM_SYMBOL_SWAP_MODE` (для поля `swap_mode`)

**Python-константы:**

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_SYMBOL_SWAP_MODE_DISABLED` | 0 | Без свопов |
| `BMT5_SYMBOL_SWAP_MODE_POINTS` | 1 | Свопы в пунктах |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_SYMBOL` | 2 | Свопы в базовой валюте символа |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_MARGIN` | 3 | Свопы в валюте маржи |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT` | 4 | Свопы в валюте депозита |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_PROFIT` | 5 | Свопы в валюте прибыли |
| `BMT5_SYMBOL_SWAP_MODE_INTEREST_CURRENT` | 6 | Годовой процент от текущей цены |
| `BMT5_SYMBOL_SWAP_MODE_INTEREST_OPEN` | 7 | Годовой процент от цены открытия |
| `BMT5_SYMBOL_SWAP_MODE_REOPEN_CURRENT` | 8 | Переоткрытие по текущей цене |
| `BMT5_SYMBOL_SWAP_MODE_REOPEN_BID` | 9 | Переоткрытие по цене Bid |

### `BMT5_ENUM_DAY_OF_WEEK` (для поля `swap_rollover_3days`)

**Python-константы:**

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_SUNDAY` | 0 | Воскресенье |
| `BMT5_MONDAY` | 1 | Понедельник |
| `BMT5_TUESDAY` | 2 | Вторник |
| `BMT5_WEDNESDAY` | 3 | Среда |
| `BMT5_THURSDAY` | 4 | Четверг |
| `BMT5_FRIDAY` | 5 | Пятница |
| `BMT5_SATURDAY` | 6 | Суббота |

### `BMT5_ENUM_SYMBOL_CALC_MODE` (для поля `trade_calc_mode`)

**Python-константы:**

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_SYMBOL_CALC_MODE_FOREX` | 0 | Режим Forex |
| `BMT5_SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE` | 1 | Forex без кредитного плеча |
| `BMT5_SYMBOL_CALC_MODE_FUTURES` | 2 | Фьючерсы |
| `BMT5_SYMBOL_CALC_MODE_CFD` | 3 | CFD |
| `BMT5_SYMBOL_CALC_MODE_CFDINDEX` | 4 | CFD на индекс |
| `BMT5_SYMBOL_CALC_MODE_CFDLEVERAGE` | 5 | CFD с кредитным плечом |
| `BMT5_SYMBOL_CALC_MODE_EXCH_STOCKS` | 6 | Биржевые акции |
| `BMT5_SYMBOL_CALC_MODE_EXCH_FUTURES` | 7 | Биржевые фьючерсы |
| `BMT5_SYMBOL_CALC_MODE_EXCH_FUTURES_FORTS` | 8 | Фьючерсы FORTS |
| `BMT5_SYMBOL_CALC_MODE_EXCH_BONDS` | 9 | Биржевые облигации |
| `BMT5_SYMBOL_CALC_MODE_EXCH_STOCKS_MOEX` | 10 | Акции MOEX |
| `BMT5_SYMBOL_CALC_MODE_EXCH_BONDS_MOEX` | 11 | Облигации MOEX |
| `BMT5_SYMBOL_CALC_MODE_SERV_COLLATERAL` | 12 | Залоговое обеспечение |

### `BMT5_ENUM_SYMBOL_TRADE_EXECUTION` (для поля `trade_exe_mode`)

**Python-константы:**

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_SYMBOL_TRADE_EXECUTION_REQUEST` | 0 | Исполнение по запросу |
| `BMT5_SYMBOL_TRADE_EXECUTION_INSTANT` | 1 | Мгновенное исполнение |
| `BMT5_SYMBOL_TRADE_EXECUTION_MARKET` | 2 | Рыночное исполнение |
| `BMT5_SYMBOL_TRADE_EXECUTION_EXCHANGE` | 3 | Биржевое исполнение |

### `BMT5_ENUM_SYMBOL_TRADE_MODE` (для поля `trade_mode`)

**Python-константы:**

| Константа | Значение | Описание |
|----------|-------|-------------|
| `BMT5_SYMBOL_TRADE_MODE_DISABLED` | 0 | Торговля отключена |
| `BMT5_SYMBOL_TRADE_MODE_LONGONLY` | 1 | Разрешены только длинные позиции |
| `BMT5_SYMBOL_TRADE_MODE_SHORTONLY` | 2 | Разрешены только короткие позиции |
| `BMT5_SYMBOL_TRADE_MODE_CLOSEONLY` | 3 | Только закрытие |
| `BMT5_SYMBOL_TRADE_MODE_FULL` | 4 | Полный режим торговли |

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Тайм-аут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до тайм-аута сервера).
* **РЕКОМЕНДУЕМЫЙ метод:** Это самый эффективный способ получить данные о символе - один вызов возвращает 100+ полей.
* **Производительность:** Получение всех параметров за один вызов значительно быстрее множественных вызовов `symbol_info_*`.
* **Построение запроса:** Создайте объект `SymbolParamsManyRequest` и задайте нужные поля.
* **Запрос одного символа:** Задайте `symbol_name` в запросе, чтобы получить данные для одного конкретного символа.
* **Запрос всех символов:** Оставьте `symbol_name` пустым, чтобы получить все символы.
* **Пагинация:** Используйте `page_number` и `items_per_page` для больших списков символов, чтобы контролировать размер полезной нагрузки.
* **Порядок сортировки:** Используйте `sort_type` для управления порядком результатов (по алфавиту или по индексу MQL).
* **Доступ к полям:** Обращайтесь к полям напрямую из объектов `SymbolParameters` (например, `info.bid`, `info.spread`).
* **Полные данные:** Каждый `SymbolParameters` содержит 112 полей, включая цены, объёмы, маржу, свопы, времена сессий и т. д.
* **Нулевые значения:** Некоторые поля могут быть нулевыми, если они не применимы к типу символа.

---

## 🔗 Примеры использования

### 1) Получить все параметры для одного символа (РЕКОМЕНДУЕТСЯ)

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Создать запрос для одного символа
request = account_helper_pb2.SymbolParamsManyRequest()
request.symbol_name = "EURUSD"

# Получить все параметры EURUSD
data = await account.symbol_params_many(request)

if data.symbol_infos:
    info = data.symbol_infos[0]

    print(f"Symbol: {info.name}")
    print(f"Description: {info.sym_description}")
    print(f"BID: {info.bid}")
    print(f"ASK: {info.ask}")
    print(f"Spread: {info.spread} points")
    print(f"Digits: {info.digits}")
    print(f"Contract Size: {info.trade_contract_size}")
    print(f"Tick Value: {info.trade_tick_value}")
    print(f"Min Volume: {info.volume_min}")
    print(f"Max Volume: {info.volume_max}")
    print(f"Volume Step: {info.volume_step}")
    print(f"Swap Long: {info.swap_long}")
    print(f"Swap Short: {info.swap_short}")
```

### 2) Получить все символы с пагинацией

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Создать запрос с пагинацией
request = account_helper_pb2.SymbolParamsManyRequest()
request.page_number = 0
request.items_per_page = 100
request.sort_type = account_helper_pb2.AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_ASC

# Получить первую страницу
data = await account.symbol_params_many(request)

print(f"Total symbols: {data.symbols_total}")
print(f"Retrieved: {len(data.symbol_infos)} symbols on page {data.page_number}")
print(f"Items per page: {data.items_per_page}")

# Показать первые 10 символов
for info in data.symbol_infos[:10]:
    print(f"{info.name}: BID={info.bid}, ASK={info.ask}, Spread={info.spread}")
```

### 3) Перебрать все страницы

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

async def get_all_symbols(account):
    """Получить все символы с помощью пагинации"""

    all_symbols = []
    page_number = 0
    items_per_page = 100

    while True:
        # Создать запрос для текущей страницы
        request = account_helper_pb2.SymbolParamsManyRequest()
        request.page_number = page_number
        request.items_per_page = items_per_page

        # Получить страницу
        data = await account.symbol_params_many(request)

        # Добавить символы в список
        all_symbols.extend(data.symbol_infos)

        print(f"Page {page_number}: Retrieved {len(data.symbol_infos)} symbols")

        # Проверить, получили ли мы все символы
        if len(all_symbols) >= data.symbols_total:
            break

        # Проверить, была ли эта страница пустой
        if len(data.symbol_infos) == 0:
            break

        page_number += 1

    print(f"Total symbols retrieved: {len(all_symbols)}")
    return all_symbols

# Использование
symbols = await get_all_symbols(account)
```

### 4) Сравнить спреды по символам

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Получить все символы
request = account_helper_pb2.SymbolParamsManyRequest()
data = await account.symbol_params_many(request)

# Отсортировать по спреду (сначала наименьший)
sorted_symbols = sorted(data.symbol_infos, key=lambda x: x.spread)

print("Symbols with lowest spreads:")
print(f"{'Symbol':<10} {'Spread':<8} {'Bid':<10} {'Ask':<10}")
print("=" * 40)

for info in sorted_symbols[:20]:
    print(f"{info.name:<10} {info.spread:<8} {info.bid:<10.5f} {info.ask:<10.5f}")
```

### 5) Найти торгуемые символы по определённым критериям

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Получить все символы
request = account_helper_pb2.SymbolParamsManyRequest()
data = await account.symbol_params_many(request)

# Отфильтровать по критериям
tradeable = []
for info in data.symbol_infos:
    # Проверить, соответствует ли символ торговым критериям
    if (info.spread < 50 and
        info.volume_min <= 0.01 and
        info.volume_max >= 1.0 and
        info.trade_contract_size > 0):

        tradeable.append({
            'name': info.name,
            'spread': info.spread,
            'min_volume': info.volume_min,
            'max_volume': info.volume_max,
            'contract_size': info.trade_contract_size
        })

print(f"Found {len(tradeable)} tradeable symbols:")
for symbol in tradeable[:10]:
    print(f"{symbol['name']}: Spread={symbol['spread']}, "
          f"MinVol={symbol['min_volume']}, MaxVol={symbol['max_volume']}")
```

### 6) Построить сравнительную таблицу символов

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Получить конкретные символы
symbols_to_compare = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]

for symbol in symbols_to_compare:
    request = account_helper_pb2.SymbolParamsManyRequest()
    request.symbol_name = symbol

    data = await account.symbol_params_many(request)

    if data.symbol_infos:
        info = data.symbol_infos[0]

        print(f"\n{info.name} - {info.sym_description}")
        print(f"  Spread: {info.spread} points")
        print(f"  Tick Value: {info.trade_tick_value}")
        print(f"  Contract Size: {info.trade_contract_size}")
        print(f"  Min/Max Volume: {info.volume_min} / {info.volume_max}")
        print(f"  Swap Long/Short: {info.swap_long} / {info.swap_short}")
        print(f"  Margin Initial: {info.margin_initial}")
```

### 7) Получить символы с тайм-аутом

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2
from datetime import datetime, timedelta, timezone

# Создать запрос
request = account_helper_pb2.SymbolParamsManyRequest()
request.symbol_name = "EURUSD"

# Задать крайний срок
deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

try:
    data = await account.symbol_params_many(
        request,
        deadline=deadline
    )

    if data.symbol_infos:
        info = data.symbol_infos[0]
        print(f"{info.name}: Bid={info.bid}, Ask={info.ask}")

except Exception as e:
    print(f"Timeout or error: {e}")
```

### 8) Рассчитать торговые издержки из параметров символа

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

async def calculate_trading_costs(account, symbol: str, volume: float):
    """Рассчитать стоимость спреда и требование к марже"""

    # Получить параметры символа
    request = account_helper_pb2.SymbolParamsManyRequest()
    request.symbol_name = symbol

    data = await account.symbol_params_many(request)

    if not data.symbol_infos:
        print(f"Symbol {symbol} not found")
        return

    info = data.symbol_infos[0]

    # Рассчитать стоимость спреда
    spread_points = info.spread
    tick_value = info.trade_tick_value
    spread_cost = spread_points * tick_value * volume

    # Требование к марже
    margin_initial = info.margin_initial

    print(f"\n{symbol} Trading Costs (Volume: {volume}):")
    print(f"  Spread: {spread_points} points")
    print(f"  Spread Cost: ${spread_cost:.2f}")
    print(f"  Initial Margin: ${margin_initial:.2f}")
    print(f"  Tick Value: ${tick_value:.2f}")
    print(f"  Contract Size: {info.trade_contract_size}")
    print(f"  Currency: {info.currency_base}/{info.currency_profit}")

    return {
        'spread_cost': spread_cost,
        'margin': margin_initial,
        'tick_value': tick_value
    }

# Использование
costs = await calculate_trading_costs(account, "EURUSD", 1.0)
```

---

## 📚 См. также

* [symbol_info_double](./symbol_info_double.md) - Получить одно свойство типа double
* [symbol_info_integer](./symbol_info_integer.md) - Получить одно свойство типа integer
* [symbol_info_string](./symbol_info_string.md) - Получить одно свойство типа string
* [symbol_info_tick](./symbol_info_tick.md) - Получить текущие данные тика
* [symbol_name](./symbol_name.md) - Получить имя символа по индексу
