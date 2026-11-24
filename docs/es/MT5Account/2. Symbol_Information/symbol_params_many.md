# Obtener todos los parámetros del símbolo

> **Solicitud:** recuperar todos los parámetros del símbolo de una sola vez (RECOMENDADO para obtener varias propiedades de forma eficiente).

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_params_many(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.AccountHelper`
- **Definición Proto:** `SymbolParamsMany` (definido en `mt5-term-api-account-helper.proto`)

### RPC

- **Servicio:** `mt5_term_api.AccountHelper`
- **Método:** `SymbolParamsMany(SymbolParamsManyRequest) -> SymbolParamsManyReply`
- **Cliente de bajo nivel (generado):** `AccountHelperStub.SymbolParamsMany(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene un conjunto completo de parámetros del símbolo en una sola llamada (más de 100 campos: precios, spreads, márgenes, swaps y volúmenes).
- **Por qué lo necesitas.** Es el método más eficiente para obtener varias propiedades de un símbolo: una sola llamada en lugar de decenas de llamadas a `symbol_info_*`.
- **Cuándo utilizarlo.** Úsalo para obtener información completa del símbolo. Utiliza `symbol_info_*` únicamente para propiedades específicas individuales.

---

## 🎯 Propósito

Utiliza este método para recuperar datos de los símbolos de forma eficiente:

- Obtener todos los parámetros del símbolo en una sola llamada eficiente.
- Recuperar datos de un símbolo específico o de todos los símbolos.
- Crear tablas comparativas completas de símbolos.
- Calcular los costes de trading y los márgenes de forma eficiente.
- Filtrar y ordenar símbolos según distintos criterios.
- Paginar listas grandes de símbolos.
- Evitar múltiples llamadas RPC para un mismo símbolo.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [symbol_params_many - Cómo funciona](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_params_many_HOW.md)**

---

## Firma del método

```python
async def symbol_params_many(
    self,
    request: account_helper_pb2.SymbolParamsManyRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.SymbolParamsManyData
```

**Mensaje de solicitud:**

```protobuf
message SymbolParamsManyRequest {
    optional string symbol_name = 1;
    optional AH_SYMBOL_PARAMS_MANY_SORT_TYPE sort_type = 2;
    optional int32 page_number = 3;
    optional int32 items_per_page = 4;
}
```

**Mensaje de respuesta:**

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

**Estructura `SymbolParameters`:**

El mensaje `SymbolParameters` contiene **116 campos**, agrupados por categorías:

**1. Datos de precios (9 campos)**

- `bid`, `ask`, `last` - Precios actuales.
- `bid_high`, `bid_low` - Rango de precios Bid.
- `ask_high`, `ask_low` - Rango de precios Ask.
- `last_high`, `last_low` - Rango del último precio.

**2. Datos de volumen (10 campos)**

- `volume`, `volume_high`, `volume_low` - Volumen en lotes.
- `volume_real`, `volume_high_real`, `volume_low_real` - Volumen real.
- `volume_min`, `volume_max`, `volume_step`, `volume_limit` - Restricciones de volumen.

**3. Spread y precisión (4 campos)**

- `spread` - Spread actual en puntos.
- `spread_float` - Indicador de spread flotante.
- `digits` - Número de dígitos decimales.
- `point` - Valor del punto.

**4. Parámetros del contrato y del trading (10 campos)**

- `trade_contract_size` - Tamaño del contrato.
- `trade_tick_size` - Tamaño del tick.
- `trade_tick_value`, `trade_tick_value_profit`, `trade_tick_value_loss` - Valores del tick.
- `trade_accrued_interest` - Intereses acumulados.
- `trade_face_value` - Valor nominal.
- `trade_liquidity_rate` - Tasa de liquidez.
- `trade_stops_level`, `trade_freeze_level` - Niveles de stops.

**5. Requisitos de margen (4 campos)**

- `margin_initial`, `margin_maintenance` - Margen inicial y de mantenimiento.
- `margin_hedged` - Margen para posiciones cubiertas.
- `margin_hedged_use_leg` - Usar la posición de mayor tamaño para calcular el margen de posiciones cubiertas.

**6. Datos de swap (11 campos)**

- `swap_long`, `swap_short` - Swap para posiciones largas y cortas.
- `swap_sunday`, `swap_monday`, `swap_tuesday`, `swap_wednesday`, `swap_thursday`, `swap_friday`, `swap_saturday` - Swaps diarios.
- `swap_mode` - Modo de cálculo del swap.
- `swap_rollover_3days` - Día del swap triple.

**7. Estadísticas de sesión (14 campos)**

- `session_volume`, `session_turnover`, `session_interest` - Totales de la sesión.
- `session_buy_orders_volume`, `session_sell_orders_volume` - Volúmenes de órdenes.
- `session_open`, `session_close`, `session_aw` - Precios de la sesión.
- `session_price_settlement` - Precio de liquidación.
- `session_price_limit_min`, `session_price_limit_max` - Límites de precio.
- `session_deals` - Número de operaciones.
- `session_buy_orders`, `session_sell_orders` - Número de órdenes.

**8. Datos de opciones (3 campos)**

- `option_strike` - Precio de ejercicio.
- `option_mode` - Modo de la opción.
- `option_right` - Tipo de opción (call/put).

**9. Griegas y precios (8 campos)**

- `price_theoretical` - Precio teórico.
- `price_delta`, `price_theta`, `price_gamma`, `price_vega`, `price_rho`, `price_omega` - Griegas.
- `price_sensitivity` - Sensibilidad del precio.

**10. Estadísticas del mercado (2 campos)**

- `price_change` - Variación del precio.
- `price_volatility` - Volatilidad.

**11. Marcas de tiempo (8 campos)**

- `time`, `time_msc` - Hora de la última actualización (en la zona horaria del servidor del bróker).
- `start_time` - Hora de inicio de la negociación.
- `expiration_time` - Hora de vencimiento.
- `time_utc`, `time_msc_utc` - Hora de la última actualización en UTC.
- `start_time_utc`, `expiration_time_utc` - Hora de inicio de la negociación / vencimiento en UTC.

**12. Modos de trading (9 campos)**

- `trade_calc_mode` - Modo de cálculo.
- `trade_mode` - Modo de trading.
- `trade_exe_mode` - Modo de ejecución.
- `expiration_mode` - Modo de vencimiento de órdenes.
- `filling_mode` - Modo de ejecución de órdenes.
- `order_mode` - Tipo de orden.
- `order_gtc_mode` - Modo GTC.
- `chart_mode` - Modo del gráfico.
- `ticks_book_depth` - Profundidad del libro de órdenes.

**13. Identificadores y descripción (11 campos)**

- `name` - Nombre del símbolo.
- `sym_description` - Descripción del símbolo (nota: el nombre del campo es `sym_description`, no `description`).
- `path` - Ruta del símbolo.
- `currency_base`, `currency_profit`, `currency_margin` - Divisas.
- `isin` - Código ISIN.
- `basis` - Activo subyacente.
- `category` - Categoría.
- `page` - Página.
- `formula` - Fórmula.

**14. Clasificación (6 campos)**

- `sector`, `sector_name` - Sector.
- `industry`, `industry_name` - Industria.
- `country` - País.
- `bank` - Banco.

**15. Visualización y estado (6 campos)**

- `exist` - El símbolo existe.
- `select` - El símbolo está seleccionado.
- `visible` - El símbolo está visible.
- `subscription_delay` - Retraso de la suscripción.
- `background_color` - Color de fondo.
- `custom` - Indicador de símbolo personalizado.

**16. Bolsa (1 campo)**

- `exchange` - Nombre de la bolsa.

**Total: 116 campos** que proporcionan información completa del símbolo mediante una sola llamada eficiente.

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `request` | `SymbolParamsManyRequest` (obligatorio) | Objeto de solicitud con parámetros de filtrado y paginación. |
| `deadline` | `datetime` (opcional) | Fecha límite para la llamada gRPC (fecha y hora UTC). |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación. |

### Campos de la solicitud

| Campo | Tipo | Descripción |
|---|---|---|
| `symbol_name` | `string` (opcional) | Filtrar por nombre del símbolo (omitirlo o dejarlo vacío = todos los símbolos). |
| `sort_type` | `AH_SYMBOL_PARAMS_MANY_SORT_TYPE` (opcional) | Criterio de ordenación de los resultados. |
| `page_number` | `int32` (opcional) | Número de página para la paginación (base 0, valor predeterminado 0). |
| `items_per_page` | `int32` (opcional) | Elementos por página (0 u omitir = todos los elementos). |

---

## ⬆️ Salida

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `symbol_infos` | `repeated SymbolParameters` | `list[SymbolParameters]` | Lista de objetos con los parámetros de los símbolos. |
| `symbols_total` | `int32` | `int` | Número total de símbolos. |
| `page_number` | `int32` (opcional) | `int` | Número de la página actual. |
| `items_per_page` | `int32` (opcional) | `int` | Número de elementos por página. |

**Valor de retorno:** el método devuelve un objeto `SymbolParamsManyData` con una lista de parámetros de símbolos e información de paginación.

---

## 🧱 Enums relacionados (de proto)

> **Nota:** todos los enums se utilizan desde el módulo `mt5_term_api_account_helper_pb2`. Este método utiliza **14 enums** con un total de **231 constantes**.

### `AH_SYMBOL_PARAMS_MANY_SORT_TYPE` (parámetro de solicitud)

| Constante | Valor | Descripción |
|---|---:|---|
| `AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_ASC` | 0 | Nombre del símbolo en orden ascendente (A-Z). |
| `AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_DESC` | 1 | Nombre del símbolo en orden descendente (Z-A). |
| `AH_PARAMS_MANY_SORT_TYPE_MQL_INDEX_ASC` | 2 | Índice MQL en orden ascendente. |
| `AH_PARAMS_MANY_SORT_TYPE_MQL_INDEX_DESC` | 3 | Índice MQL en orden descendente. |

### `BMT5_ENUM_SYMBOL_CHART_MODE` (para el campo `chart_mode`)

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_SYMBOL_CHART_MODE_BID` | 0 | Barras basadas en precios Bid. |
| `BMT5_SYMBOL_CHART_MODE_LAST` | 1 | Barras basadas en precios Last. |

### `BMT5_ENUM_ORDER_TYPE_FILLING` (para el campo `filling_mode`)

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_ORDER_FILLING_FOK` | 0 | Fill or Kill: ejecutar completamente o cancelar. |
| `BMT5_ORDER_FILLING_IOC` | 1 | Immediate or Cancel: ejecutar el volumen disponible. |
| `BMT5_ORDER_FILLING_RETURN` | 2 | Modo de ejecución Return. |
| `BMT5_ORDER_FILLING_BOC` | 3 | Book or Cancel: colocar la orden en el libro. |

### `BMT5_ENUM_SYMBOL_INDUSTRY` (para el campo `industry`)

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_INDUSTRY_UNDEFINED` | 0 | Sin definir. |
| `BMT5_INDUSTRY_AGRICULTURAL_INPUTS` | 1 | Insumos agrícolas. |
| `BMT5_INDUSTRY_ALUMINIUM` | 2 | Aluminio. |
| `BMT5_INDUSTRY_BUILDING_MATERIALS` | 3 | Materiales de construcción. |
| `BMT5_INDUSTRY_CHEMICALS` | 4 | Productos químicos. |
| `BMT5_INDUSTRY_COKING_COAL` | 5 | Carbón de coque. |
| `BMT5_INDUSTRY_COPPER` | 6 | Cobre. |
| `BMT5_INDUSTRY_GOLD` | 7 | Oro. |
| `BMT5_INDUSTRY_LUMBER_WOOD` | 8 | Madera y productos de madera. |
| `BMT5_INDUSTRY_INDUSTRIAL_METALS` | 9 | Metales industriales. |
| `BMT5_INDUSTRY_PRECIOUS_METALS` | 10 | Metales preciosos. |
| `BMT5_INDUSTRY_PAPER` | 11 | Papel. |
| `BMT5_INDUSTRY_SILVER` | 12 | Plata. |
| `BMT5_INDUSTRY_SPECIALTY_CHEMICALS` | 13 | Productos químicos especializados. |
| `BMT5_INDUSTRY_STEEL` | 14 | Acero. |
| `BMT5_INDUSTRY_ADVERTISING` | 15 | Publicidad. |
| `BMT5_INDUSTRY_BROADCASTING` | 16 | Radiodifusión y televisión. |
| `BMT5_INDUSTRY_GAMING_MULTIMEDIA` | 17 | Videojuegos y multimedia. |
| `BMT5_INDUSTRY_ENTERTAINMENT` | 18 | Entretenimiento. |
| `BMT5_INDUSTRY_INTERNET_CONTENT` | 19 | Contenido de Internet. |
| `BMT5_INDUSTRY_PUBLISHING` | 20 | Edición y publicaciones. |
| `BMT5_INDUSTRY_TELECOM` | 21 | Telecomunicaciones. |
| `BMT5_INDUSTRY_APPAREL_MANUFACTURING` | 22 | Fabricación de prendas de vestir. |
| `BMT5_INDUSTRY_APPAREL_RETAIL` | 23 | Venta minorista de prendas de vestir. |
| `BMT5_INDUSTRY_AUTO_MANUFACTURERS` | 24 | Fabricantes de automóviles. |
| `BMT5_INDUSTRY_AUTO_PARTS` | 25 | Piezas de automóviles. |
| `BMT5_INDUSTRY_AUTO_DEALERSHIP` | 26 | Concesionarios de automóviles. |
| `BMT5_INDUSTRY_DEPARTMENT_STORES` | 27 | Grandes almacenes. |
| `BMT5_INDUSTRY_FOOTWEAR_ACCESSORIES` | 28 | Calzado y accesorios. |
| `BMT5_INDUSTRY_FURNISHINGS` | 29 | Mobiliario y artículos para el hogar. |
| `BMT5_INDUSTRY_GAMBLING` | 30 | Juegos de azar. |
| `BMT5_INDUSTRY_HOME_IMPROV_RETAIL` | 31 | Venta minorista de productos para mejoras del hogar. |
| `BMT5_INDUSTRY_INTERNET_RETAIL` | 32 | Comercio minorista por Internet. |
| `BMT5_INDUSTRY_LEISURE` | 33 | Ocio. |
| `BMT5_INDUSTRY_LODGING` | 34 | Alojamiento. |
| `BMT5_INDUSTRY_LUXURY_GOODS` | 35 | Artículos de lujo. |
| `BMT5_INDUSTRY_PACKAGING_CONTAINERS` | 36 | Envases y embalajes. |
| `BMT5_INDUSTRY_PERSONAL_SERVICES` | 37 | Servicios personales. |
| `BMT5_INDUSTRY_RECREATIONAL_VEHICLES` | 38 | Vehículos recreativos. |
| `BMT5_INDUSTRY_RESIDENT_CONSTRUCTION` | 39 | Construcción residencial. |
| `BMT5_INDUSTRY_RESORTS_CASINOS` | 40 | Resorts y casinos. |
| `BMT5_INDUSTRY_RESTAURANTS` | 41 | Restaurantes. |
| `BMT5_INDUSTRY_SPECIALTY_RETAIL` | 42 | Comercio minorista especializado. |
| `BMT5_INDUSTRY_TEXTILE_MANUFACTURING` | 43 | Fabricación textil. |
| `BMT5_INDUSTRY_TRAVEL_SERVICES` | 44 | Servicios de viajes. |
| `BMT5_INDUSTRY_BEVERAGES_BREWERS` | 45 | Bebidas: cerveceras. |
| `BMT5_INDUSTRY_BEVERAGES_NON_ALCO` | 46 | Bebidas no alcohólicas. |
| `BMT5_INDUSTRY_BEVERAGES_WINERIES` | 47 | Bebidas: bodegas y productores de vino. |
| `BMT5_INDUSTRY_CONFECTIONERS` | 48 | Confitería. |
| `BMT5_INDUSTRY_DISCOUNT_STORES` | 49 | Tiendas de descuento. |
| `BMT5_INDUSTRY_EDUCATION_TRAINIG` | 50 | Educación y formación. |
| `BMT5_INDUSTRY_FARM_PRODUCTS` | 51 | Productos agrícolas. |
| `BMT5_INDUSTRY_FOOD_DISTRIBUTION` | 52 | Distribución de alimentos. |
| `BMT5_INDUSTRY_GROCERY_STORES` | 53 | Tiendas de alimentación. |
| `BMT5_INDUSTRY_HOUSEHOLD_PRODUCTS` | 54 | Productos para el hogar. |
| `BMT5_INDUSTRY_PACKAGED_FOODS` | 55 | Alimentos envasados. |
| `BMT5_INDUSTRY_TOBACCO` | 56 | Tabaco. |
| `BMT5_INDUSTRY_OIL_GAS_DRILLING` | 57 | Perforación de petróleo y gas. |
| `BMT5_INDUSTRY_OIL_GAS_EP` | 58 | Exploración y producción de petróleo y gas. |
| `BMT5_INDUSTRY_OIL_GAS_EQUIPMENT` | 59 | Equipos para petróleo y gas. |
| `BMT5_INDUSTRY_OIL_GAS_INTEGRATED` | 60 | Petróleo y gas integrados. |
| `BMT5_INDUSTRY_OIL_GAS_MIDSTREAM` | 61 | Transporte y almacenamiento intermedio de petróleo y gas. |
| `BMT5_INDUSTRY_OIL_GAS_REFINING` | 62 | Refinación de petróleo y gas. |
| `BMT5_INDUSTRY_THERMAL_COAL` | 63 | Carbón térmico. |
| `BMT5_INDUSTRY_URANIUM` | 64 | Uranio. |
| `BMT5_INDUSTRY_EXCHANGE_TRADED_FUND` | 65 | Fondo cotizado en bolsa (ETF). |
| `BMT5_INDUSTRY_ASSETS_MANAGEMENT` | 66 | Gestión de activos. |
| `BMT5_INDUSTRY_BANKS_DIVERSIFIED` | 67 | Bancos diversificados. |
| `BMT5_INDUSTRY_BANKS_REGIONAL` | 68 | Bancos regionales. |
| `BMT5_INDUSTRY_CAPITAL_MARKETS` | 69 | Mercados de capitales. |
| `BMT5_INDUSTRY_CLOSE_END_FUND_DEBT` | 70 | Fondo cerrado de deuda. |
| `BMT5_INDUSTRY_CLOSE_END_FUND_EQUITY` | 71 | Fondo cerrado de renta variable. |
| `BMT5_INDUSTRY_CLOSE_END_FUND_FOREIGN` | 72 | Fondo cerrado de activos extranjeros. |
| `BMT5_INDUSTRY_CREDIT_SERVICES` | 73 | Servicios de crédito. |
| `BMT5_INDUSTRY_FINANCIAL_CONGLOMERATE` | 74 | Conglomerados financieros. |
| `BMT5_INDUSTRY_FINANCIAL_DATA_EXCHANGE` | 75 | Datos y bolsas financieras. |
| `BMT5_INDUSTRY_INSURANCE_BROKERS` | 76 | Corredores de seguros. |
| `BMT5_INDUSTRY_INSURANCE_DIVERSIFIED` | 77 | Seguros diversificados. |
| `BMT5_INDUSTRY_INSURANCE_LIFE` | 78 | Seguros de vida. |
| `BMT5_INDUSTRY_INSURANCE_PROPERTY` | 79 | Seguros de propiedad y accidentes. |
| `BMT5_INDUSTRY_INSURANCE_REINSURANCE` | 80 | Reaseguros. |
| `BMT5_INDUSTRY_INSURANCE_SPECIALTY` | 81 | Seguros especializados. |
| `BMT5_INDUSTRY_MORTGAGE_FINANCE` | 82 | Financiación hipotecaria. |
| `BMT5_INDUSTRY_SHELL_COMPANIES` | 83 | Sociedades instrumentales. |
| `BMT5_INDUSTRY_BIOTECHNOLOGY` | 84 | Biotecnología. |
| `BMT5_INDUSTRY_DIAGNOSTICS_RESEARCH` | 85 | Diagnóstico e investigación. |
| `BMT5_INDUSTRY_DRUGS_MANUFACTURERS` | 86 | Fabricantes de medicamentos: general. |
| `BMT5_INDUSTRY_DRUGS_MANUFACTURERS_SPEC` | 87 | Fabricantes de medicamentos: especializados. |
| `BMT5_INDUSTRY_HEALTHCARE_PLANS` | 88 | Planes de atención sanitaria. |
| `BMT5_INDUSTRY_HEALTH_INFORMATION` | 89 | Servicios de información sanitaria. |
| `BMT5_INDUSTRY_MEDICAL_FACILITIES` | 90 | Centros de atención médica. |
| `BMT5_INDUSTRY_MEDICAL_DEVICES` | 91 | Dispositivos médicos. |
| `BMT5_INDUSTRY_MEDICAL_DISTRIBUTION` | 92 | Distribución de productos médicos. |
| `BMT5_INDUSTRY_MEDICAL_INSTRUMENTS` | 93 | Instrumentos y suministros médicos. |
| `BMT5_INDUSTRY_PHARM_RETAILERS` | 94 | Comercios minoristas farmacéuticos. |
| `BMT5_INDUSTRY_AEROSPACE_DEFENSE` | 95 | Aeroespacial y defensa. |
| `BMT5_INDUSTRY_AIRLINES` | 96 | Aerolíneas. |
| `BMT5_INDUSTRY_AIRPORTS_SERVICES` | 97 | Aeropuertos y servicios aeroportuarios. |
| `BMT5_INDUSTRY_BUILDING_PRODUCTS` | 98 | Productos y equipos de construcción. |
| `BMT5_INDUSTRY_BUSINESS_EQUIPMENT` | 99 | Equipos y suministros empresariales. |
| `BMT5_INDUSTRY_CONGLOMERATES` | 100 | Conglomerados. |
| `BMT5_INDUSTRY_CONSULTING_SERVICES` | 101 | Servicios de consultoría. |
| `BMT5_INDUSTRY_ELECTRICAL_EQUIPMENT` | 102 | Equipos y componentes eléctricos. |
| `BMT5_INDUSTRY_ENGINEERING_CONSTRUCTION` | 103 | Ingeniería y construcción. |
| `BMT5_INDUSTRY_FARM_HEAVY_MACHINERY` | 104 | Maquinaria agrícola y pesada. |
| `BMT5_INDUSTRY_INDUSTRIAL_DISTRIBUTION` | 105 | Distribución industrial. |
| `BMT5_INDUSTRY_INFRASTRUCTURE_OPERATIONS` | 106 | Operaciones de infraestructura. |
| `BMT5_INDUSTRY_FREIGHT_LOGISTICS` | 107 | Servicios de transporte de mercancías y logística. |
| `BMT5_INDUSTRY_MARINE_SHIPPING` | 108 | Transporte marítimo. |
| `BMT5_INDUSTRY_METAL_FABRICATION` | 109 | Fabricación de productos metálicos. |
| `BMT5_INDUSTRY_POLLUTION_CONTROL` | 110 | Control de la contaminación y tratamiento. |
| `BMT5_INDUSTRY_RAILROADS` | 111 | Ferrocarriles. |
| `BMT5_INDUSTRY_RENTAL_LEASING` | 112 | Servicios de alquiler y arrendamiento. |
| `BMT5_INDUSTRY_SECURITY_PROTECTION` | 113 | Servicios de seguridad y protección. |
| `BMT5_INDUSTRY_SPEALITY_BUSINESS_SERVICES` | 114 | Servicios empresariales especializados. |
| `BMT5_INDUSTRY_SPEALITY_MACHINERY` | 115 | Maquinaria industrial especializada. |
| `BMT5_INDUSTRY_STUFFING_EMPLOYMENT` | 116 | Servicios de contratación y empleo. |
| `BMT5_INDUSTRY_TOOLS_ACCESSORIES` | 117 | Herramientas y accesorios. |
| `BMT5_INDUSTRY_TRUCKING` | 118 | Transporte por carretera en camiones. |
| `BMT5_INDUSTRY_WASTE_MANAGEMENT` | 119 | Gestión de residuos. |
| `BMT5_INDUSTRY_REAL_ESTATE_DEVELOPMENT` | 120 | Bienes raíces: desarrollo. |
| `BMT5_INDUSTRY_REAL_ESTATE_DIVERSIFIED` | 121 | Bienes raíces diversificados. |
| `BMT5_INDUSTRY_REAL_ESTATE_SERVICES` | 122 | Servicios inmobiliarios. |
| `BMT5_INDUSTRY_REIT_DIVERSIFIED` | 123 | REIT diversificado. |
| `BMT5_INDUSTRY_REIT_HEALTCARE` | 124 | REIT de instalaciones sanitarias. |
| `BMT5_INDUSTRY_REIT_HOTEL_MOTEL` | 125 | REIT de hoteles y moteles. |
| `BMT5_INDUSTRY_REIT_INDUSTRIAL` | 126 | REIT industrial. |
| `BMT5_INDUSTRY_REIT_MORTAGE` | 127 | REIT hipotecario. |
| `BMT5_INDUSTRY_REIT_OFFICE` | 128 | REIT de oficinas. |
| `BMT5_INDUSTRY_REIT_RESIDENTAL` | 129 | REIT residencial. |
| `BMT5_INDUSTRY_REIT_RETAIL` | 130 | REIT minorista. |
| `BMT5_INDUSTRY_REIT_SPECIALITY` | 131 | REIT especializado. |
| `BMT5_INDUSTRY_COMMUNICATION_EQUIPMENT` | 132 | Equipos de comunicación. |
| `BMT5_INDUSTRY_COMPUTER_HARDWARE` | 133 | Hardware informático. |
| `BMT5_INDUSTRY_CONSUMER_ELECTRONICS` | 134 | Electrónica de consumo. |
| `BMT5_INDUSTRY_ELECTRONIC_COMPONENTS` | 135 | Componentes electrónicos. |
| `BMT5_INDUSTRY_ELECTRONIC_DISTRIBUTION` | 136 | Distribución de electrónica y equipos informáticos. |
| `BMT5_INDUSTRY_IT_SERVICES` | 137 | Servicios de tecnologías de la información. |
| `BMT5_INDUSTRY_SCIENTIFIC_INSTRUMENTS` | 138 | Instrumentos científicos y técnicos. |
| `BMT5_INDUSTRY_SEMICONDUCTOR_EQUIPMENT` | 139 | Equipos y materiales para semiconductores. |
| `BMT5_INDUSTRY_SEMICONDUCTORS` | 140 | Semiconductores. |
| `BMT5_INDUSTRY_SOFTWARE_APPLICATION` | 141 | Software: aplicaciones. |
| `BMT5_INDUSTRY_SOFTWARE_INFRASTRUCTURE` | 142 | Software: infraestructura. |
| `BMT5_INDUSTRY_SOLAR` | 143 | Energía solar. |
| `BMT5_INDUSTRY_UTILITIES_DIVERSIFIED` | 144 | Servicios públicos diversificados. |
| `BMT5_INDUSTRY_UTILITIES_POWERPRODUCERS` | 145 | Servicios públicos: productores independientes de energía. |
| `BMT5_INDUSTRY_UTILITIES_RENEWABLE` | 146 | Servicios públicos: energías renovables. |
| `BMT5_INDUSTRY_UTILITIES_REGULATED_ELECTRIC` | 147 | Servicios públicos: electricidad regulada. |
| `BMT5_INDUSTRY_UTILITIES_REGULATED_GAS` | 148 | Servicios públicos: gas regulado. |
| `BMT5_INDUSTRY_UTILITIES_REGULATED_WATER` | 149 | Servicios públicos: agua regulada. |
| `BMT5_INDUSTRY_UTILITIES_FIRST` | 150 | Primer valor de servicios públicos (marcador de rango). |
| `BMT5_INDUSTRY_UTILITIES_LAST` | 151 | Último valor de servicios públicos (marcador de rango). |

### `BMT5_ENUM_SYMBOL_OPTION_MODE` (para el campo `option_mode`)

**Constantes de Python:**

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_SYMBOL_OPTION_MODE_EUROPEAN` | 0 | Opción europea: solo puede ejercerse al vencimiento. |
| `BMT5_SYMBOL_OPTION_MODE_AMERICAN` | 1 | Opción americana: puede ejercerse en cualquier momento. |

### `BMT5_ENUM_SYMBOL_OPTION_RIGHT` (para el campo `option_right`)

**Constantes de Python:**

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_SYMBOL_OPTION_RIGHT_CALL` | 0 | Opción Call: derecho a comprar. |
| `BMT5_SYMBOL_OPTION_RIGHT_PUT` | 1 | Opción Put: derecho a vender. |

### `BMT5_ENUM_SYMBOL_ORDER_GTC_MODE` (para el campo `order_gtc_mode`)

**Constantes de Python:**

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_SYMBOL_ORDERS_GTC` | 0 | Se permiten órdenes Good Till Cancelled. |
| `BMT5_SYMBOL_ORDERS_DAILY` | 1 | Solo órdenes diarias. |
| `BMT5_SYMBOL_ORDERS_DAILY_EXCLUDING_STOPS` | 2 | Órdenes diarias, excepto las órdenes Stop. |

### `BMT5_ENUM_ORDER_TYPE` (para el campo `order_mode`)

**Constantes de Python:**

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_ORDER_TYPE_BUY` | 0 | Orden de compra a mercado. |
| `BMT5_ORDER_TYPE_SELL` | 1 | Orden de venta a mercado. |
| `BMT5_ORDER_TYPE_BUY_LIMIT` | 2 | Orden pendiente Buy Limit. |
| `BMT5_ORDER_TYPE_SELL_LIMIT` | 3 | Orden pendiente Sell Limit. |
| `BMT5_ORDER_TYPE_BUY_STOP` | 4 | Orden pendiente Buy Stop. |
| `BMT5_ORDER_TYPE_SELL_STOP` | 5 | Orden pendiente Sell Stop. |
| `BMT5_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Orden pendiente Buy Stop Limit. |
| `BMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Orden pendiente Sell Stop Limit. |
| `BMT5_ORDER_TYPE_CLOSE_BY` | 8 | Orden Close By. |

### `BMT5_ENUM_SYMBOL_SECTOR` (para el campo `sector`)

**Constantes de Python:**

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_SECTOR_UNDEFINED` | 0 | Sector sin definir. |
| `BMT5_SECTOR_BASIC_MATERIALS` | 1 | Materiales básicos. |
| `BMT5_SECTOR_COMMUNICATION_SERVICES` | 2 | Servicios de comunicación. |
| `BMT5_SECTOR_CONSUMER_CYCLICAL` | 3 | Consumo cíclico. |
| `BMT5_SECTOR_CONSUMER_DEFENSIVE` | 4 | Consumo defensivo. |
| `BMT5_SECTOR_CURRENCY` | 5 | Divisas. |
| `BMT5_SECTOR_CURRENCY_CRYPTO` | 6 | Criptomonedas. |
| `BMT5_SECTOR_ENERGY` | 7 | Energía. |
| `BMT5_SECTOR_FINANCIAL` | 8 | Sector financiero. |
| `BMT5_SECTOR_HEALTHCARE` | 9 | Atención sanitaria. |
| `BMT5_SECTOR_INDUSTRIALS` | 10 | Industria. |
| `BMT5_SECTOR_REAL_ESTATE` | 11 | Bienes raíces. |
| `BMT5_SECTOR_TECHNOLOGY` | 12 | Tecnología. |
| `BMT5_SECTOR_UTILITIES` | 13 | Servicios públicos. |

### `BMT5_ENUM_SYMBOL_SWAP_MODE` (para el campo `swap_mode`)

**Constantes de Python:**

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_SYMBOL_SWAP_MODE_DISABLED` | 0 | Sin swaps. |
| `BMT5_SYMBOL_SWAP_MODE_POINTS` | 1 | Swaps en puntos. |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_SYMBOL` | 2 | Swaps en la divisa base del símbolo. |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_MARGIN` | 3 | Swaps en la divisa del margen. |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT` | 4 | Swaps en la divisa del depósito. |
| `BMT5_SYMBOL_SWAP_MODE_CURRENCY_PROFIT` | 5 | Swaps en la divisa de beneficio. |
| `BMT5_SYMBOL_SWAP_MODE_INTEREST_CURRENT` | 6 | Interés anual calculado a partir del precio actual. |
| `BMT5_SYMBOL_SWAP_MODE_INTEREST_OPEN` | 7 | Interés anual calculado a partir del precio de apertura. |
| `BMT5_SYMBOL_SWAP_MODE_REOPEN_CURRENT` | 8 | Reapertura al precio actual. |
| `BMT5_SYMBOL_SWAP_MODE_REOPEN_BID` | 9 | Reapertura al precio Bid. |

### `BMT5_ENUM_DAY_OF_WEEK` (para el campo `swap_rollover_3days`)

**Constantes de Python:**

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_SUNDAY` | 0 | Domingo. |
| `BMT5_MONDAY` | 1 | Lunes. |
| `BMT5_TUESDAY` | 2 | Martes. |
| `BMT5_WEDNESDAY` | 3 | Miércoles. |
| `BMT5_THURSDAY` | 4 | Jueves. |
| `BMT5_FRIDAY` | 5 | Viernes. |
| `BMT5_SATURDAY` | 6 | Sábado. |

### `BMT5_ENUM_SYMBOL_CALC_MODE` (para el campo `trade_calc_mode`)

**Constantes de Python:**

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_SYMBOL_CALC_MODE_FOREX` | 0 | Modo Forex. |
| `BMT5_SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE` | 1 | Forex sin apalancamiento. |
| `BMT5_SYMBOL_CALC_MODE_FUTURES` | 2 | Futuros. |
| `BMT5_SYMBOL_CALC_MODE_CFD` | 3 | CFD. |
| `BMT5_SYMBOL_CALC_MODE_CFDINDEX` | 4 | Índice CFD. |
| `BMT5_SYMBOL_CALC_MODE_CFDLEVERAGE` | 5 | CFD con apalancamiento. |
| `BMT5_SYMBOL_CALC_MODE_EXCH_STOCKS` | 6 | Acciones negociadas en bolsa. |
| `BMT5_SYMBOL_CALC_MODE_EXCH_FUTURES` | 7 | Futuros negociados en bolsa. |
| `BMT5_SYMBOL_CALC_MODE_EXCH_FUTURES_FORTS` | 8 | Futuros FORTS. |
| `BMT5_SYMBOL_CALC_MODE_EXCH_BONDS` | 9 | Bonos negociados en bolsa. |
| `BMT5_SYMBOL_CALC_MODE_EXCH_STOCKS_MOEX` | 10 | Acciones de MOEX. |
| `BMT5_SYMBOL_CALC_MODE_EXCH_BONDS_MOEX` | 11 | Bonos de MOEX. |
| `BMT5_SYMBOL_CALC_MODE_SERV_COLLATERAL` | 12 | Garantía de servicio. |

### `BMT5_ENUM_SYMBOL_TRADE_EXECUTION` (para el campo `trade_exe_mode`)

**Constantes de Python:**

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_SYMBOL_TRADE_EXECUTION_REQUEST` | 0 | Ejecución bajo solicitud. |
| `BMT5_SYMBOL_TRADE_EXECUTION_INSTANT` | 1 | Ejecución instantánea. |
| `BMT5_SYMBOL_TRADE_EXECUTION_MARKET` | 2 | Ejecución a mercado. |
| `BMT5_SYMBOL_TRADE_EXECUTION_EXCHANGE` | 3 | Ejecución en bolsa. |

### `BMT5_ENUM_SYMBOL_TRADE_MODE` (para el campo `trade_mode`)

**Constantes de Python:**

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_SYMBOL_TRADE_MODE_DISABLED` | 0 | Trading deshabilitado. |
| `BMT5_SYMBOL_TRADE_MODE_LONGONLY` | 1 | Solo se permiten posiciones largas. |
| `BMT5_SYMBOL_TRADE_MODE_SHORTONLY` | 2 | Solo se permiten posiciones cortas. |
| `BMT5_SYMBOL_TRADE_MODE_CLOSEONLY` | 3 | Solo se permite cerrar posiciones. |
| `BMT5_SYMBOL_TRADE_MODE_FULL` | 4 | Modo de trading completo. |

---

## 🧩 Notas y consejos

- **Reconexión automática:** protección integrada contra errores gRPC transitorios con reconexión automática mediante `execute_with_reconnect`.
- **Tiempo de espera predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca el timeout del servidor).
- **Método RECOMENDADO:** es la forma más eficiente de obtener datos de los símbolos: una sola llamada devuelve más de 100 campos.
- **Rendimiento:** obtener todos los parámetros en una sola llamada es considerablemente más rápido que realizar múltiples llamadas a `symbol_info_*`.
- **Construcción de la solicitud:** crea un objeto `SymbolParamsManyRequest` y establece los campos deseados.
- **Consulta de un solo símbolo:** establece `symbol_name` en la solicitud para obtener datos de un símbolo específico.
- **Consulta de todos los símbolos:** deja `symbol_name` vacío para obtener todos los símbolos.
- **Paginación:** utiliza `page_number` y `items_per_page` para listas grandes de símbolos y controlar el tamaño del payload.
- **Ordenación:** utiliza `sort_type` para controlar el orden de los resultados (alfabéticamente o por índice MQL).
- **Acceso a los campos:** accede directamente a los campos de los objetos `SymbolParameters` (por ejemplo, `info.bid`, `info.spread`).
- **Datos completos:** cada objeto `SymbolParameters` contiene 112 campos, incluidos precios, volúmenes, márgenes, swaps, horarios de sesión, etc.
- **Valores cero:** algunos campos pueden ser cero si no son aplicables al tipo de símbolo.

---

## 🔗 Ejemplos de uso

### 1) Obtener todos los parámetros de un símbolo (RECOMENDADO)

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Crear una solicitud para un solo símbolo
request = account_helper_pb2.SymbolParamsManyRequest()
request.symbol_name = "EURUSD"

# Obtener todos los parámetros de EURUSD
data = await account.symbol_params_many(request)

if data.symbol_infos:
    info = data.symbol_infos[0]

    print(f"Símbolo: {info.name}")
    print(f"Descripción: {info.sym_description}")
    print(f"BID: {info.bid}")
    print(f"ASK: {info.ask}")
    print(f"Spread: {info.spread} puntos")
    print(f"Dígitos: {info.digits}")
    print(f"Tamaño del contrato: {info.trade_contract_size}")
    print(f"Valor del tick: {info.trade_tick_value}")
    print(f"Volumen mínimo: {info.volume_min}")
    print(f"Volumen máximo: {info.volume_max}")
    print(f"Paso de volumen: {info.volume_step}")
    print(f"Swap Long: {info.swap_long}")
    print(f"Swap Short: {info.swap_short}")
```

### 2) Obtener todos los símbolos con paginación

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Crear una solicitud con paginación
request = account_helper_pb2.SymbolParamsManyRequest()
request.page_number = 0
request.items_per_page = 100
request.sort_type = account_helper_pb2.AH_PARAMS_MANY_SORT_TYPE_SYMBOL_NAME_ASC

# Obtener la primera página
data = await account.symbol_params_many(request)

print(f"Total de símbolos: {data.symbols_total}")
print(f"Recuperados: {len(data.symbol_infos)} símbolos en la página {data.page_number}")
print(f"Elementos por página: {data.items_per_page}")

# Mostrar los primeros 10 símbolos
for info in data.symbol_infos[:10]:
    print(f"{info.name}: BID={info.bid}, ASK={info.ask}, Spread={info.spread}")
```

### 3) Recorrer todas las páginas

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

async def get_all_symbols(account):
    """Recupera todos los símbolos utilizando la paginación"""

    all_symbols = []
    page_number = 0
    items_per_page = 100

    while True:
        # Crear una solicitud para la página actual
        request = account_helper_pb2.SymbolParamsManyRequest()
        request.page_number = page_number
        request.items_per_page = items_per_page

        # Obtener la página
        data = await account.symbol_params_many(request)

        # Añadir los símbolos a la lista
        all_symbols.extend(data.symbol_infos)

        print(f"Página {page_number}: se recuperaron {len(data.symbol_infos)} símbolos")

        # Comprobar si se han obtenido todos los símbolos
        if len(all_symbols) >= data.symbols_total:
            break

        # Comprobar si esta página estaba vacía
        if len(data.symbol_infos) == 0:
            break

        page_number += 1

    print(f"Total de símbolos recuperados: {len(all_symbols)}")
    return all_symbols

# Uso
symbols = await get_all_symbols(account)
```

### 4) Comparar los spreads entre símbolos

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Obtener todos los símbolos
request = account_helper_pb2.SymbolParamsManyRequest()
data = await account.symbol_params_many(request)

# Ordenar por spread (de menor a mayor)
sorted_symbols = sorted(data.symbol_infos, key=lambda x: x.spread)

print("Símbolos con los spreads más bajos:")
print(f"{'Símbolo':<10} {'Spread':<8} {'Bid':<10} {'Ask':<10}")
print("=" * 40)

for info in sorted_symbols[:20]:
    print(f"{info.name:<10} {info.spread:<8} {info.bid:<10.5f} {info.ask:<10.5f}")
```

### 5) Encontrar símbolos negociables que cumplan criterios específicos

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Obtener todos los símbolos
request = account_helper_pb2.SymbolParamsManyRequest()
data = await account.symbol_params_many(request)

# Filtrar según los criterios
tradeable = []
for info in data.symbol_infos:
    # Comprobar si el símbolo cumple los criterios de trading
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

print(f"Se encontraron {len(tradeable)} símbolos negociables:")
for symbol in tradeable[:10]:
    print(f"{symbol['name']}: Spread={symbol['spread']}, "
          f"Volumen mínimo={symbol['min_volume']}, Volumen máximo={symbol['max_volume']}")
```

### 6) Crear una tabla comparativa de símbolos

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Obtener símbolos específicos
symbols_to_compare = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]

for symbol in symbols_to_compare:
    request = account_helper_pb2.SymbolParamsManyRequest()
    request.symbol_name = symbol

    data = await account.symbol_params_many(request)

    if data.symbol_infos:
        info = data.symbol_infos[0]

        print(f"\n{info.name} - {info.sym_description}")
        print(f"  Spread: {info.spread} puntos")
        print(f"  Valor del tick: {info.trade_tick_value}")
        print(f"  Tamaño del contrato: {info.trade_contract_size}")
        print(f"  Volumen mínimo/máximo: {info.volume_min} / {info.volume_max}")
        print(f"  Swap Long/Short: {info.swap_long} / {info.swap_short}")
        print(f"  Margen inicial: {info.margin_initial}")
```

### 7) Obtener símbolos con límite de tiempo

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2
from datetime import datetime, timedelta, timezone

# Crear la solicitud
request = account_helper_pb2.SymbolParamsManyRequest()
request.symbol_name = "EURUSD"

# Establecer la fecha límite
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
    print(f"Tiempo de espera agotado o error: {e}")
```

### 8) Calcular los costes de trading a partir de los parámetros del símbolo

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

async def calculate_trading_costs(account, symbol: str, volume: float):
    """Calcula el coste del spread y el requisito de margen"""

    # Obtener los parámetros del símbolo
    request = account_helper_pb2.SymbolParamsManyRequest()
    request.symbol_name = symbol

    data = await account.symbol_params_many(request)

    if not data.symbol_infos:
        print(f"Símbolo {symbol} no encontrado")
        return

    info = data.symbol_infos[0]

    # Calcular el coste del spread
    spread_points = info.spread
    tick_value = info.trade_tick_value
    spread_cost = spread_points * tick_value * volume

    # Requisito de margen
    margin_initial = info.margin_initial

    print(f"\nCostes de trading de {symbol} (Volumen: {volume}):")
    print(f"  Spread: {spread_points} puntos")
    print(f"  Coste del spread: ${spread_cost:.2f}")
    print(f"  Margen inicial: ${margin_initial:.2f}")
    print(f"  Valor del tick: ${tick_value:.2f}")
    print(f"  Tamaño del contrato: {info.trade_contract_size}")
    print(f"  Divisa: {info.currency_base}/{info.currency_profit}")

    return {
        'spread_cost': spread_cost,
        'margin': margin_initial,
        'tick_value': tick_value
    }

# Uso
costs = await calculate_trading_costs(account, "EURUSD", 1.0)
```

---

## 📚 Véase también

- [symbol_info_double](./symbol_info_double.md) - Obtener una propiedad double individual.
- [symbol_info_integer](./symbol_info_integer.md) - Obtener una propiedad integer individual.
- [symbol_info_string](./symbol_info_string.md) - Obtener una propiedad string individual.
- [symbol_info_tick](./symbol_info_tick.md) - Obtener los datos del tick actual.
- [symbol_name](./symbol_name.md) - Obtener el nombre del símbolo por índice.