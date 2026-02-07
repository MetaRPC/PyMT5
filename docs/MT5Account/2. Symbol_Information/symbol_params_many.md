# Get Comprehensive Symbol Parameters

> **Request:** retrieve all symbol parameters at once (RECOMMENDED for getting multiple properties efficiently).

**API Information:**

* **Low-level API:** `MT5Account.symbol_params_many(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.AccountHelper`
* **Proto definition:** `SymbolParamsMany` (defined in `mt5-term-api-account-helper.proto`)

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `SymbolParamsMany(SymbolParamsManyRequest) -> SymbolParamsManyReply`
* **Low-level client (generated):** `AccountHelperStub.SymbolParamsMany(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Get comprehensive symbol parameters in one call (100+ fields: prices, spreads, margins, swaps, volumes).
* **Why you need it.** Most efficient method to get multiple symbol properties - single call instead of dozens of `symbol_info_*` calls.
* **When to use.** Use this for getting complete symbol information. Use `symbol_info_*` only for single specific properties.

---

## 🎯 Purpose

Use it to efficiently retrieve symbol data:

* Get all symbol parameters in a single efficient call
* Retrieve data for one specific symbol or all symbols
* Build comprehensive symbol comparison tables
* Calculate trading costs and margins efficiently
* Filter and sort symbols by various criteria
* Paginate through large symbol lists
* Avoid multiple RPC calls for the same symbol

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [symbol_params_many - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_params_many_HOW.md)**

---

## Method Signature

```python
async def symbol_params_many(
    self,
    request: account_helper_pb2.SymbolParamsManyRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.SymbolParamsManyData
```

**Request message:**

```protobuf
message SymbolParamsManyRequest {
  optional string symbol_name = 1;
  optional AH_SYMBOL_PARAMS_MANY_SORT_TYPE sort_type = 2;
  optional int32 page_number = 3;
  optional int32 items_per_page = 4;
}
```

**Reply message:**

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

**SymbolParameters structure:**

The `SymbolParameters` message contains **112 fields** grouped by category:

**1. Price Data (9 fields)**

- `bid`, `ask`, `last` - Current prices
- `bid_high`, `bid_low` - Bid price range
- `ask_high`, `ask_low` - Ask price range
- `last_high`, `last_low` - Last price range

**2. Volume Data (10 fields)**

- `volume`, `volume_high`, `volume_low` - Volume in lots
- `volume_real`, `volume_high_real`, `volume_low_real` - Real volume
- `volume_min`, `volume_max`, `volume_step`, `volume_limit` - Volume constraints

**3. Spread & Precision (4 fields)**

- `spread` - Current spread in points
- `spread_float` - Floating spread flag
- `digits` - Decimal digits
- `point` - Point value

**4. Contract & Trade Parameters (9 fields)**

- `trade_contract_size` - Contract size
- `trade_tick_size` - Tick size
- `trade_tick_value`, `trade_tick_value_profit`, `trade_tick_value_loss` - Tick values

- `trade_accrued_interest` - Accrued interest
- `trade_face_value` - Face value
- `trade_liquidity_rate` - Liquidity rate
- `trade_stops_level`, `trade_freeze_level` - Stop levels

**5. Margin Requirements (4 fields)**

- `margin_initial`, `margin_maintenance` - Initial and maintenance margins
- `margin_hedged` - Hedged margin
- `margin_hedged_use_leg` - Use leg for hedged margin

**6. Swap Data (12 fields)**

- `swap_long`, `swap_short` - Long/short swap
- `swap_sunday`, `swap_monday`, `swap_tuesday`, `swap_wednesday`, `swap_thursday`, `swap_friday`, `swap_saturday` - Daily swaps
- `swap_mode` - Swap calculation mode
- `swap_rollover_3days` - Triple swap day

**7. Session Statistics (16 fields)**

- `session_volume`, `session_turnover`, `session_interest` - Session totals
- `session_buy_orders_volume`, `session_sell_orders_volume` - Order volumes
- `session_open`, `session_close`, `session_aw` - Session prices
- `session_price_settlement` - Settlement price
- `session_price_limit_min`, `session_price_limit_max` - Price limits
- `session_deals` - Number of deals
- `session_buy_orders`, `session_sell_orders` - Order counts

**8. Options Data (3 fields)**

- `option_strike` - Strike price
- `option_mode` - Option mode
- `option_right` - Option right (call/put)

**9. Greeks & Pricing (8 fields)**

- `price_theoretical` - Theoretical price
- `price_delta`, `price_theta`, `price_gamma`, `price_vega`, `price_rho`, `price_omega` - Greeks
- `price_sensitivity` - Price sensitivity

**10. Market Statistics (2 fields)**

- `price_change` - Price change
- `price_volatility` - Volatility

**11. Timestamps (4 fields)**

- `time`, `time_msc` - Last update time
- `start_time` - Trading start time
- `expiration_time` - Expiration time

**12. Trading Modes (10 fields)**

- `trade_calc_mode` - Calculation mode
- `trade_mode` - Trading mode
- `trade_exe_mode` - Execution mode
- `expiration_mode` - Order expiration mode
- `filling_mode` - Order filling mode
- `order_mode` - Order mode
- `order_gtc_mode` - GTC mode
- `chart_mode` - Chart mode
- `ticks_book_depth` - Book depth

**13. Identifiers & Description (11 fields)**

- `name` - Symbol name
- `sym_description` - Symbol description (note: field name is `sym_description` not `description`)
- `path` - Symbol path
- `currency_base`, `currency_profit`, `currency_margin` - Currencies
- `isin` - ISIN code
- `basis` - Basis
- `category` - Category
- `page` - Page
- `formula` - Formula

**14. Classification (6 fields)**

- `sector`, `sector_name` - Sector
- `industry`, `industry_name` - Industry
- `country` - Country
- `bank` - Bank

**15. Display & Status (6 fields)**

- `exist` - Symbol exists
- `select` - Symbol selected
- `visible` - Symbol visible
- `subscription_delay` - Subscription delay
- `background_color` - Background color
- `custom` - Custom data

**16. Exchange (1 field)**

- `exchange` - Exchange name

**Total: 112 fields** providing comprehensive symbol information in a single efficient call.

---

## 🔽 Input

| Parameter     | Type                                              | Description                                                     |
| ------------- | ------------------------------------------------- | --------------------------------------------------------------- |
| `request`     | `SymbolParamsManyRequest` (required)              | Request object with filter/pagination parameters                |
| `deadline`    | `datetime` (optional)                             | Deadline for the gRPC call (UTC datetime)                       |
| `cancellation_event` | `asyncio.Event` (optional)                 | Event to cancel the operation                                   |

### Request Fields:

| Field           | Type                                | Description                                      |
| --------------- | ----------------------------------- | ------------------------------------------------ |
| `symbol_name`   | `string` (optional)                 | Filter by symbol name (omit or empty = all symbols) |
| `sort_type`     | `AH_SYMBOL_PARAMS_MANY_SORT_TYPE` (optional) | Sort order for results                  |
| `page_number`   | `int32` (optional)                  | Page number for pagination (0-based, default 0)  |
| `items_per_page`| `int32` (optional)                  | Items per page (0 or omit = all items)           |

---

## ⬆️ Output

| Field          | Type                        | Python Type              | Description                              |
| -------------- | --------------------------- | ------------------------ | ---------------------------------------- |
| `symbol_infos` | `repeated SymbolParameters` | `list[SymbolParameters]` | List of symbol parameter objects         |
| `symbols_total`| `int32`                     | `int`                    | Total number of symbols                  |
| `page_number`  | `int32` (optional)          | `int`                    | Current page number                      |
| `items_per_page`| `int32` (optional)         | `int`                    | Items per page                           |

**Return value:** The method returns `SymbolParamsManyData` object with list of symbol parameters and pagination info.

---

## 🧱 Related enums (from proto)

> **Note:** All enums are accessed from `mt5_term_api_account_helper_pb2` module. This method uses **14 enums** with **231 total constants**.

### `AH_SYMBOL_PARAMS_MANY_SORT_TYPE` (request parameter)

| Constant | Value | Description |
|----------|-------|-------------|
| `AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_ASC` | 0 | Symbol name ascending (A-Z) |
| `AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_DESC` | 1 | Symbol name descending (Z-A) |
| `AH_PARAMS_MANY_SORT_TYPE_MQL_INDEX_ASC` | 2 | MQL index ascending |
| `AH_PARAMS_MANY_SORT_TYPE_MQL_INDEX_DESC` | 3 | MQL index descending |

### `BMT5_ENUM_SYMBOL_CHART_MODE` (for field `chart_mode`)

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_SYMBOL_CHART_MODE_BID` | 0 | Bars based on Bid prices |
| `BMT5_SYMBOL_CHART_MODE_LAST` | 1 | Bars based on Last prices |

### `BMT5_ENUM_ORDER_TYPE_FILLING` (for field `filling_mode`)

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_ORDER_FILLING_FOK` | 0 | Fill or Kill - fill completely or cancel |
| `BMT5_ORDER_FILLING_IOC` | 1 | Immediate or Cancel - fill available volume |
| `BMT5_ORDER_FILLING_RETURN` | 2 | Return execution mode |
| `BMT5_ORDER_FILLING_BOC` | 3 | Book or Cancel - place order in book |

### `BMT5_ENUM_SYMBOL_INDUSTRY` (for field `industry`)

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_INDUSTRY_UNDEFINED` | 0 | Undefined |
| `BMT5_INDUSTRY_AGRICULTURAL_INPUTS` | 1 | Agricultural Inputs |
| `BMT5_INDUSTRY_ALUMINIUM` | 2 | Aluminium |
| `BMT5_INDUSTRY_BUILDING_MATERIALS` | 3 | Building Materials |
| `BMT5_INDUSTRY_CHEMICALS` | 4 | Chemicals |
| `BMT5_INDUSTRY_COKING_COAL` | 5 | Coking Coal |
| `BMT5_INDUSTRY_COPPER` | 6 | Copper |
| `BMT5_INDUSTRY_GOLD` | 7 | Gold |
| `BMT5_INDUSTRY_LUMBER_WOOD` | 8 | Lumber & Wood |
| `BMT5_INDUSTRY_INDUSTRIAL_METALS` | 9 | Industrial Metals |
| `BMT5_INDUSTRY_PRECIOUS_METALS` | 10 | Precious Metals |
| `BMT5_INDUSTRY_PAPER` | 11 | Paper |
| `BMT5_INDUSTRY_SILVER` | 12 | Silver |
| `BMT5_INDUSTRY_SPECIALTY_CHEMICALS` | 13 | Specialty Chemicals |
| `BMT5_INDUSTRY_STEEL` | 14 | Steel |
| `BMT5_INDUSTRY_ADVERTISING` | 15 | Advertising |
| `BMT5_INDUSTRY_BROADCASTING` | 16 | Broadcasting |
| `BMT5_INDUSTRY_GAMING_MULTIMEDIA` | 17 | Gaming & Multimedia |
| `BMT5_INDUSTRY_ENTERTAINMENT` | 18 | Entertainment |
| `BMT5_INDUSTRY_INTERNET_CONTENT` | 19 | Internet Content |
| `BMT5_INDUSTRY_PUBLISHING` | 20 | Publishing |
| `BMT5_INDUSTRY_TELECOM` | 21 | Telecommunications |
| `BMT5_INDUSTRY_APPAREL_MANUFACTURING` | 22 | Apparel Manufacturing |
| `BMT5_INDUSTRY_APPAREL_RETAIL` | 23 | Apparel Retail |
| `BMT5_INDUSTRY_AUTO_MANUFACTURERS` | 24 | Auto Manufacturers |
| `BMT5_INDUSTRY_AUTO_PARTS` | 25 | Auto Parts |
| `BMT5_INDUSTRY_AUTO_DEALERSHIP` | 26 | Auto Dealerships |
| `BMT5_INDUSTRY_DEPARTMENT_STORES` | 27 | Department Stores |
| `BMT5_INDUSTRY_FOOTWEAR_ACCESSORIES` | 28 | Footwear & Accessories |
| `BMT5_INDUSTRY_FURNISHINGS` | 29 | Furnishings |
| `BMT5_INDUSTRY_GAMBLING` | 30 | Gambling |
| `BMT5_INDUSTRY_HOME_IMPROV_RETAIL` | 31 | Home Improvement Retail |
| `BMT5_INDUSTRY_INTERNET_RETAIL` | 32 | Internet Retail |
| `BMT5_INDUSTRY_LEISURE` | 33 | Leisure |
| `BMT5_INDUSTRY_LODGING` | 34 | Lodging |
| `BMT5_INDUSTRY_LUXURY_GOODS` | 35 | Luxury Goods |
| `BMT5_INDUSTRY_PACKAGING_CONTAINERS` | 36 | Packaging & Containers |
| `BMT5_INDUSTRY_PERSONAL_SERVICES` | 37 | Personal Services |
| `BMT5_INDUSTRY_RECREATIONAL_VEHICLES` | 38 | Recreational Vehicles |
| `BMT5_INDUSTRY_RESIDENT_CONSTRUCTION` | 39 | Residential Construction |
| `BMT5_INDUSTRY_RESORTS_CASINOS` | 40 | Resorts & Casinos |
| `BMT5_INDUSTRY_RESTAURANTS` | 41 | Restaurants |
| `BMT5_INDUSTRY_SPECIALTY_RETAIL` | 42 | Specialty Retail |
| `BMT5_INDUSTRY_TEXTILE_MANUFACTURING` | 43 | Textile Manufacturing |
| `BMT5_INDUSTRY_TRAVEL_SERVICES` | 44 | Travel Services |
| `BMT5_INDUSTRY_BEVERAGES_BREWERS` | 45 | Beverages - Brewers |
| `BMT5_INDUSTRY_BEVERAGES_NON_ALCO` | 46 | Beverages - Non-Alcoholic |
| `BMT5_INDUSTRY_BEVERAGES_WINERIES` | 47 | Beverages - Wineries |
| `BMT5_INDUSTRY_CONFECTIONERS` | 48 | Confectioners |
| `BMT5_INDUSTRY_DISCOUNT_STORES` | 49 | Discount Stores |
| `BMT5_INDUSTRY_EDUCATION_TRAINIG` | 50 | Education & Training |
| `BMT5_INDUSTRY_FARM_PRODUCTS` | 51 | Farm Products |
| `BMT5_INDUSTRY_FOOD_DISTRIBUTION` | 52 | Food Distribution |
| `BMT5_INDUSTRY_GROCERY_STORES` | 53 | Grocery Stores |
| `BMT5_INDUSTRY_HOUSEHOLD_PRODUCTS` | 54 | Household Products |
| `BMT5_INDUSTRY_PACKAGED_FOODS` | 55 | Packaged Foods |
| `BMT5_INDUSTRY_TOBACCO` | 56 | Tobacco |
| `BMT5_INDUSTRY_OIL_GAS_DRILLING` | 57 | Oil & Gas Drilling |
| `BMT5_INDUSTRY_OIL_GAS_EP` | 58 | Oil & Gas E&P |
| `BMT5_INDUSTRY_OIL_GAS_EQUIPMENT` | 59 | Oil & Gas Equipment |
| `BMT5_INDUSTRY_OIL_GAS_INTEGRATED` | 60 | Oil & Gas Integrated |
| `BMT5_INDUSTRY_OIL_GAS_MIDSTREAM` | 61 | Oil & Gas Midstream |
| `BMT5_INDUSTRY_OIL_GAS_REFINING` | 62 | Oil & Gas Refining |
| `BMT5_INDUSTRY_THERMAL_COAL` | 63 | Thermal Coal |
| `BMT5_INDUSTRY_URANIUM` | 64 | Uranium |
| `BMT5_INDUSTRY_EXCHANGE_TRADED_FUND` | 65 | Exchange Traded Fund |
| `BMT5_INDUSTRY_ASSETS_MANAGEMENT` | 66 | Asset Management |
| `BMT5_INDUSTRY_BANKS_DIVERSIFIED` | 67 | Banks - Diversified |
| `BMT5_INDUSTRY_BANKS_REGIONAL` | 68 | Banks - Regional |
| `BMT5_INDUSTRY_CAPITAL_MARKETS` | 69 | Capital Markets |
| `BMT5_INDUSTRY_CLOSE_END_FUND_DEBT` | 70 | Closed-End Fund - Debt |
| `BMT5_INDUSTRY_CLOSE_END_FUND_EQUITY` | 71 | Closed-End Fund - Equity |
| `BMT5_INDUSTRY_CLOSE_END_FUND_FOREIGN` | 72 | Closed-End Fund - Foreign |
| `BMT5_INDUSTRY_CREDIT_SERVICES` | 73 | Credit Services |
| `BMT5_INDUSTRY_FINANCIAL_CONGLOMERATE` | 74 | Financial Conglomerate |
| `BMT5_INDUSTRY_FINANCIAL_DATA_EXCHANGE` | 75 | Financial Data & Exchanges |
| `BMT5_INDUSTRY_INSURANCE_BROKERS` | 76 | Insurance Brokers |
| `BMT5_INDUSTRY_INSURANCE_DIVERSIFIED` | 77 | Insurance - Diversified |
| `BMT5_INDUSTRY_INSURANCE_LIFE` | 78 | Insurance - Life |
| `BMT5_INDUSTRY_INSURANCE_PROPERTY` | 79 | Insurance - Property & Casualty |
| `BMT5_INDUSTRY_INSURANCE_REINSURANCE` | 80 | Insurance - Reinsurance |
| `BMT5_INDUSTRY_INSURANCE_SPECIALTY` | 81 | Insurance - Specialty |
| `BMT5_INDUSTRY_MORTGAGE_FINANCE` | 82 | Mortgage Finance |
| `BMT5_INDUSTRY_SHELL_COMPANIES` | 83 | Shell Companies |
| `BMT5_INDUSTRY_BIOTECHNOLOGY` | 84 | Biotechnology |
| `BMT5_INDUSTRY_DIAGNOSTICS_RESEARCH` | 85 | Diagnostics & Research |
| `BMT5_INDUSTRY_DRUGS_MANUFACTURERS` | 86 | Drug Manufacturers - General |
| `BMT5_INDUSTRY_DRUGS_MANUFACTURERS_SPEC` | 87 | Drug Manufacturers - Specialty |
| `BMT5_INDUSTRY_HEALTHCARE_PLANS` | 88 | Healthcare Plans |
| `BMT5_INDUSTRY_HEALTH_INFORMATION` | 89 | Health Information Services |
| `BMT5_INDUSTRY_MEDICAL_FACILITIES` | 90 | Medical Care Facilities |
| `BMT5_INDUSTRY_MEDICAL_DEVICES` | 91 | Medical Devices |
| `BMT5_INDUSTRY_MEDICAL_DISTRIBUTION` | 92 | Medical Distribution |
| `BMT5_INDUSTRY_MEDICAL_INSTRUMENTS` | 93 | Medical Instruments & Supplies |
| `BMT5_INDUSTRY_PHARM_RETAILERS` | 94 | Pharmaceutical Retailers |
| `BMT5_INDUSTRY_AEROSPACE_DEFENSE` | 95 | Aerospace & Defense |
| `BMT5_INDUSTRY_AIRLINES` | 96 | Airlines |
| `BMT5_INDUSTRY_AIRPORTS_SERVICES` | 97 | Airports & Air Services |
| `BMT5_INDUSTRY_BUILDING_PRODUCTS` | 98 | Building Products & Equipment |
| `BMT5_INDUSTRY_BUSINESS_EQUIPMENT` | 99 | Business Equipment & Supplies |
| `BMT5_INDUSTRY_CONGLOMERATES` | 100 | Conglomerates |
| `BMT5_INDUSTRY_CONSULTING_SERVICES` | 101 | Consulting Services |
| `BMT5_INDUSTRY_ELECTRICAL_EQUIPMENT` | 102 | Electrical Equipment & Parts |
| `BMT5_INDUSTRY_ENGINEERING_CONSTRUCTION` | 103 | Engineering & Construction |
| `BMT5_INDUSTRY_FARM_HEAVY_MACHINERY` | 104 | Farm & Heavy Machinery |
| `BMT5_INDUSTRY_INDUSTRIAL_DISTRIBUTION` | 105 | Industrial Distribution |
| `BMT5_INDUSTRY_INFRASTRUCTURE_OPERATIONS` | 106 | Infrastructure Operations |
| `BMT5_INDUSTRY_FREIGHT_LOGISTICS` | 107 | Freight & Logistics Services |
| `BMT5_INDUSTRY_MARINE_SHIPPING` | 108 | Marine Shipping |
| `BMT5_INDUSTRY_METAL_FABRICATION` | 109 | Metal Fabrication |
| `BMT5_INDUSTRY_POLLUTION_CONTROL` | 110 | Pollution & Treatment Controls |
| `BMT5_INDUSTRY_RAILROADS` | 111 | Railroads |
| `BMT5_INDUSTRY_RENTAL_LEASING` | 112 | Rental & Leasing Services |
| `BMT5_INDUSTRY_SECURITY_PROTECTION` | 113 | Security & Protection Services |
| `BMT5_INDUSTRY_SPEALITY_BUSINESS_SERVICES` | 114 | Specialty Business Services |
| `BMT5_INDUSTRY_SPEALITY_MACHINERY` | 115 | Specialty Industrial Machinery |
| `BMT5_INDUSTRY_STUFFING_EMPLOYMENT` | 116 | Staffing & Employment Services |
| `BMT5_INDUSTRY_TOOLS_ACCESSORIES` | 117 | Tools & Accessories |
| `BMT5_INDUSTRY_TRUCKING` | 118 | Trucking |
| `BMT5_INDUSTRY_WASTE_MANAGEMENT` | 119 | Waste Management |
| `BMT5_INDUSTRY_REAL_ESTATE_DEVELOPMENT` | 120 | Real Estate - Development |
| `BMT5_INDUSTRY_REAL_ESTATE_DIVERSIFIED` | 121 | Real Estate - Diversified |
| `BMT5_INDUSTRY_REAL_ESTATE_SERVICES` | 122 | Real Estate Services |
| `BMT5_INDUSTRY_REIT_DIVERSIFIED` | 123 | REIT - Diversified |
| `BMT5_INDUSTRY_REIT_HEALTCARE` | 124 | REIT - Healthcare Facilities |
| `BMT5_INDUSTRY_REIT_HOTEL_MOTEL` | 125 | REIT - Hotel & Motel |
| `BMT5_INDUSTRY_REIT_INDUSTRIAL` | 126 | REIT - Industrial |
| `BMT5_INDUSTRY_REIT_MORTAGE` | 127 | REIT - Mortgage |
| `BMT5_INDUSTRY_REIT_OFFICE` | 128 | REIT - Office |
| `BMT5_INDUSTRY_REIT_RESIDENTAL` | 129 | REIT - Residential |
| `BMT5_INDUSTRY_REIT_RETAIL` | 130 | REIT - Retail |
| `BMT5_INDUSTRY_REIT_SPECIALITY` | 131 | REIT - Specialty |
| `BMT5_INDUSTRY_COMMUNICATION_EQUIPMENT` | 132 | Communication Equipment |
| `BMT5_INDUSTRY_COMPUTER_HARDWARE` | 133 | Computer Hardware |
| `BMT5_INDUSTRY_CONSUMER_ELECTRONICS` | 134 | Consumer Electronics |
| `BMT5_INDUSTRY_ELECTRONIC_COMPONENTS` | 135 | Electronic Components |
| `BMT5_INDUSTRY_ELECTRONIC_DISTRIBUTION` | 136 | Electronics & Computer Distribution |
| `BMT5_INDUSTRY_IT_SERVICES` | 137 | Information Technology Services |
| `BMT5_INDUSTRY_SCIENTIFIC_INSTRUMENTS` | 138 | Scientific & Technical Instruments |
| `BMT5_INDUSTRY_SEMICONDUCTOR_EQUIPMENT` | 139 | Semiconductor Equipment & Materials |
| `BMT5_INDUSTRY_SEMICONDUCTORS` | 140 | Semiconductors |
| `BMT5_INDUSTRY_SOFTWARE_APPLICATION` | 141 | Software - Application |
| `BMT5_INDUSTRY_SOFTWARE_INFRASTRUCTURE` | 142 | Software - Infrastructure |
| `BMT5_INDUSTRY_SOLAR` | 143 | Solar |
| `BMT5_INDUSTRY_UTILITIES_DIVERSIFIED` | 144 | Utilities - Diversified |
| `BMT5_INDUSTRY_UTILITIES_POWERPRODUCERS` | 145 | Utilities - Independent Power Producers |
| `BMT5_INDUSTRY_UTILITIES_RENEWABLE` | 146 | Utilities - Renewable |
| `BMT5_INDUSTRY_UTILITIES_REGULATED_ELECTRIC` | 147 | Utilities - Regulated Electric |
| `BMT5_INDUSTRY_UTILITIES_REGULATED_GAS` | 148 | Utilities - Regulated Gas |
| `BMT5_INDUSTRY_UTILITIES_REGULATED_WATER` | 149 | Utilities - Regulated Water |
| `BMT5_INDUSTRY_UTILITIES_FIRST` | 150 | Utilities First (range marker) |
| `BMT5_INDUSTRY_UTILITIES_LAST` | 151 | Utilities Last (range marker) |

### `BMT5_ENUM_SYMBOL_OPTION_MODE` (for field `option_mode`)

**Python constants:**

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_SYMBOL_OPTION_MODE_EUROPEAN` | 0 | European option - exercise only at expiration |
| `BMT5_SYMBOL_OPTION_MODE_AMERICAN` | 1 | American option - exercise any time |

### `BMT5_ENUM_SYMBOL_OPTION_RIGHT` (for field `option_right`)

**Python constants:**

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_SYMBOL_OPTION_RIGHT_CALL` | 0 | Call option - right to buy |
| `BMT5_SYMBOL_OPTION_RIGHT_PUT` | 1 | Put option - right to sell |

### `BMT5_ENUM_SYMBOL_ORDER_GTC_MODE` (for field `order_gtc_mode`)

**Python constants:**

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_SYMBOL_ORDERS_GTC` | 0 | Good Till Cancelled orders allowed |
| `BMT5_SYMBOL_ORDERS_DAILY` | 1 | Daily orders only |
| `BMT5_SYMBOL_ORDERS_DAILY_EXCLUDING_STOPS` | 2 | Daily excluding stops |

### `BMT5_ENUM_ORDER_TYPE` (for field `order_mode`)

**Python constants:**

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_ORDER_TYPE_BUY` | 0 | Market Buy order |
| `BMT5_ORDER_TYPE_SELL` | 1 | Market Sell order |
| `BMT5_ORDER_TYPE_BUY_LIMIT` | 2 | Buy Limit pending order |
| `BMT5_ORDER_TYPE_SELL_LIMIT` | 3 | Sell Limit pending order |
| `BMT5_ORDER_TYPE_BUY_STOP` | 4 | Buy Stop pending order |
| `BMT5_ORDER_TYPE_SELL_STOP` | 5 | Sell Stop pending order |
| `BMT5_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Buy Stop Limit pending order |
| `BMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Sell Stop Limit pending order |
| `BMT5_ORDER_TYPE_CLOSE_BY` | 8 | Close By order |

### `BMT5_ENUM_SYMBOL_SECTOR` (for field `sector`)

**Python constants:**

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_SECTOR_UNDEFINED` | 0 | Undefined sector |
| `BMT5_SECTOR_BASIC_MATERIALS` | 1 | Basic Materials |
| `BMT5_SECTOR_COMMUNICATION_SERVICES` | 2 | Communication Services |
| `BMT5_SECTOR_CONSUMER_CYCLICAL` | 3 | Consumer Cyclical |
| `BMT5_SECTOR_CONSUMER_DEFENSIVE` | 4 | Consumer Defensive |
| `BMT5_SECTOR_CURRENCY` | 5 | Currency |
| `BMT5_SECTOR_CURRENCY_CRYPTO` | 6 | Cryptocurrency |
| `BMT5_SECTOR_ENERGY` | 7 | Energy |
| `BMT5_SECTOR_FINANCIAL` | 8 | Financial |
| `BMT5_SECTOR_HEALTHCARE` | 9 | Healthcare |
| `BMT5_SECTOR_INDUSTRIALS` | 10 | Industrials |
| `BMT5_SECTOR_REAL_ESTATE` | 11 | Real Estate |
| `BMT5_SECTOR_TECHNOLOGY` | 12 | Technology |
| `BMT5_SECTOR_UTILITIES` | 13 | Utilities |

### `BMT5_ENUM_SYMBOL_SWAP_MODE` (for field `swap_mode`)

**Python constants:**

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_SYMBOL_SWAP_MODE_DISABLED` | 0 | No swaps |
| `BMT5_SYMBOL_SWAP_MODE_POINTS` | 1 | Swaps in points |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_SYMBOL` | 2 | Swaps in symbol base currency |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_MARGIN` | 3 | Swaps in margin currency |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT` | 4 | Swaps in deposit currency |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_PROFIT` | 5 | Swaps in profit currency |
| `BMT5_SYMBOL_SWAP_MODE_INTEREST_CURRENT` | 6 | Annual interest from current price |
| `BMT5_SYMBOL_SWAP_MODE_INTEREST_OPEN` | 7 | Annual interest from open price |
| `BMT5_SYMBOL_SWAP_MODE_REOPEN_CURRENT` | 8 | Reopen by current price |
| `BMT5_SYMBOL_SWAP_MODE_REOPEN_BID` | 9 | Reopen by Bid price |

### `BMT5_ENUM_DAY_OF_WEEK` (for field `swap_rollover_3days`)

**Python constants:**

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_SUNDAY` | 0 | Sunday |
| `BMT5_MONDAY` | 1 | Monday |
| `BMT5_TUESDAY` | 2 | Tuesday |
| `BMT5_WEDNESDAY` | 3 | Wednesday |
| `BMT5_THURSDAY` | 4 | Thursday |
| `BMT5_FRIDAY` | 5 | Friday |
| `BMT5_SATURDAY` | 6 | Saturday |

### `BMT5_ENUM_SYMBOL_CALC_MODE` (for field `trade_calc_mode`)

**Python constants:**

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_SYMBOL_CALC_MODE_FOREX` | 0 | Forex mode |
| `BMT5_SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE` | 1 | Forex no leverage |
| `BMT5_SYMBOL_CALC_MODE_FUTURES` | 2 | Futures |
| `BMT5_SYMBOL_CALC_MODE_CFD` | 3 | CFD |
| `BMT5_SYMBOL_CALC_MODE_CFDINDEX` | 4 | CFD index |
| `BMT5_SYMBOL_CALC_MODE_CFDLEVERAGE` | 5 | CFD leverage |
| `BMT5_SYMBOL_CALC_MODE_EXCH_STOCKS` | 6 | Exchange stocks |
| `BMT5_SYMBOL_CALC_MODE_EXCH_FUTURES` | 7 | Exchange futures |
| `BMT5_SYMBOL_CALC_MODE_EXCH_FUTURES_FORTS` | 8 | FORTS futures |
| `BMT5_SYMBOL_CALC_MODE_EXCH_BONDS` | 9 | Exchange bonds |
| `BMT5_SYMBOL_CALC_MODE_EXCH_STOCKS_MOEX` | 10 | MOEX stocks |
| `BMT5_SYMBOL_CALC_MODE_EXCH_BONDS_MOEX` | 11 | MOEX bonds |
| `BMT5_SYMBOL_CALC_MODE_SERV_COLLATERAL` | 12 | Service collateral |

### `BMT5_ENUM_SYMBOL_TRADE_EXECUTION` (for field `trade_exe_mode`)

**Python constants:**

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_SYMBOL_TRADE_EXECUTION_REQUEST` | 0 | Execution by request |
| `BMT5_SYMBOL_TRADE_EXECUTION_INSTANT` | 1 | Instant execution |
| `BMT5_SYMBOL_TRADE_EXECUTION_MARKET` | 2 | Market execution |
| `BMT5_SYMBOL_TRADE_EXECUTION_EXCHANGE` | 3 | Exchange execution |

### `BMT5_ENUM_SYMBOL_TRADE_MODE` (for field `trade_mode`)

**Python constants:**

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_SYMBOL_TRADE_MODE_DISABLED` | 0 | Trade disabled |
| `BMT5_SYMBOL_TRADE_MODE_LONGONLY` | 1 | Long only allowed |
| `BMT5_SYMBOL_TRADE_MODE_SHORTONLY` | 2 | Short only allowed |
| `BMT5_SYMBOL_TRADE_MODE_CLOSEONLY` | 3 | Close only |
| `BMT5_SYMBOL_TRADE_MODE_FULL` | 4 | Full trade mode |

---

## 🧩 Notes & Tips

* **Automatic reconnection:** Built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **RECOMMENDED method:** This is the most efficient way to get symbol data - single call returns 100+ fields.
* **Performance:** Getting all parameters in one call is significantly faster than multiple `symbol_info_*` calls.
* **Request construction:** Create `SymbolParamsManyRequest` object and set desired fields.
* **Single symbol query:** Set `symbol_name` in request to get data for one specific symbol.
* **All symbols query:** Leave `symbol_name` empty to get all symbols.
* **Pagination:** Use `page_number` and `items_per_page` for large symbol lists to control payload size.
* **Sort order:** Use `sort_type` to control ordering of results (alphabetical or by MQL index).
* **Field access:** Access fields directly from `SymbolParameters` objects (e.g., `info.bid`, `info.spread`).
* **Comprehensive data:** Each `SymbolParameters` contains 112 fields including prices, volumes, margins, swaps, session times, etc.
* **Zero values:** Some fields may be zero if not applicable to the symbol type.

---

## 🔗 Usage Examples

### 1) Get all parameters for one symbol (RECOMMENDED)

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Create request for single symbol
request = account_helper_pb2.SymbolParamsManyRequest()
request.symbol_name = "EURUSD"

# Get all EURUSD parameters
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

### 2) Get all symbols with pagination

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Create request with pagination
request = account_helper_pb2.SymbolParamsManyRequest()
request.page_number = 0
request.items_per_page = 100
request.sort_type = account_helper_pb2.AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_ASC

# Get first page
data = await account.symbol_params_many(request)

print(f"Total symbols: {data.symbols_total}")
print(f"Retrieved: {len(data.symbol_infos)} symbols on page {data.page_number}")
print(f"Items per page: {data.items_per_page}")

# Display first 10 symbols
for info in data.symbol_infos[:10]:
    print(f"{info.name}: BID={info.bid}, ASK={info.ask}, Spread={info.spread}")
```

### 3) Iterate through all pages

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

async def get_all_symbols(account):
    """Retrieve all symbols using pagination"""

    all_symbols = []
    page_number = 0
    items_per_page = 100

    while True:
        # Create request for current page
        request = account_helper_pb2.SymbolParamsManyRequest()
        request.page_number = page_number
        request.items_per_page = items_per_page

        # Get page
        data = await account.symbol_params_many(request)

        # Add symbols to list
        all_symbols.extend(data.symbol_infos)

        print(f"Page {page_number}: Retrieved {len(data.symbol_infos)} symbols")

        # Check if we got all symbols
        if len(all_symbols) >= data.symbols_total:
            break

        # Check if this page was empty
        if len(data.symbol_infos) == 0:
            break

        page_number += 1

    print(f"Total symbols retrieved: {len(all_symbols)}")
    return all_symbols

# Usage
symbols = await get_all_symbols(account)
```

### 4) Compare spreads across symbols

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Get all symbols
request = account_helper_pb2.SymbolParamsManyRequest()
data = await account.symbol_params_many(request)

# Sort by spread (lowest first)
sorted_symbols = sorted(data.symbol_infos, key=lambda x: x.spread)

print("Symbols with lowest spreads:")
print(f"{'Symbol':<10} {'Spread':<8} {'Bid':<10} {'Ask':<10}")
print("=" * 40)

for info in sorted_symbols[:20]:
    print(f"{info.name:<10} {info.spread:<8} {info.bid:<10.5f} {info.ask:<10.5f}")
```

### 5) Find tradeable symbols with specific criteria

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Get all symbols
request = account_helper_pb2.SymbolParamsManyRequest()
data = await account.symbol_params_many(request)

# Filter by criteria
tradeable = []
for info in data.symbol_infos:
    # Check if symbol meets trading criteria
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

### 6) Build symbol comparison table

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Get specific symbols
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

### 7) Get symbols with timeout

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2
from datetime import datetime, timedelta

# Create request
request = account_helper_pb2.SymbolParamsManyRequest()
request.symbol_name = "EURUSD"

# Set deadline
deadline = datetime.utcnow() + timedelta(seconds=5)

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

### 8) Calculate trading costs from symbol parameters

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

async def calculate_trading_costs(account, symbol: str, volume: float):
    """Calculate spread cost and margin requirement"""

    # Get symbol parameters
    request = account_helper_pb2.SymbolParamsManyRequest()
    request.symbol_name = symbol

    data = await account.symbol_params_many(request)

    if not data.symbol_infos:
        print(f"Symbol {symbol} not found")
        return

    info = data.symbol_infos[0]

    # Calculate spread cost
    spread_points = info.spread
    tick_value = info.trade_tick_value
    spread_cost = spread_points * tick_value * volume

    # Margin requirement
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

# Usage
costs = await calculate_trading_costs(account, "EURUSD", 1.0)
```

---

## 📚 See also

* [symbol_info_double](./symbol_info_double.md) - Get single double property
* [symbol_info_integer](./symbol_info_integer.md) - Get single integer property
* [symbol_info_string](./symbol_info_string.md) - Get single string property
* [symbol_info_tick](./symbol_info_tick.md) - Get current tick data
* [symbol_name](./symbol_name.md) - Get symbol name by index
