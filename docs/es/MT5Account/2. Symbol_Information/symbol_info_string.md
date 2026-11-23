# Obtener una propiedad de tipo cadena de un símbolo

> **Solicitud:** obtener el valor de una propiedad de tipo cadena de un símbolo.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_info_string(...)` (definida en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolInfoString` (definida en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolInfoString(SymbolInfoStringRequest) -> SymbolInfoStringReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolInfoString(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene el valor de una única propiedad de tipo cadena de un símbolo (DESCRIPTION, CURRENCY_BASE, PATH, etc.).
- **Por qué lo necesitas.** Permite obtener propiedades de texto específicas de un símbolo, como códigos de divisa, descripciones y metadatos.
- **Cuándo utilizarlo.** Utiliza `symbol_params_many()` para obtener varias propiedades. Utiliza este método para consultar una sola propiedad.

---

## 🎯 Propósito

Utiliza este método para consultar propiedades específicas de tipo cadena de un símbolo:

- Obtener la descripción del símbolo y sus nombres para mostrar.
- Recuperar los códigos de divisa (base, beneficio y margen).
- Comprobar la ruta y la clasificación del símbolo.
- Obtener información sobre la bolsa y el ISIN.
- Consultar la fórmula y los metadatos del símbolo.
- Comprobar la información del banco y del país.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [symbol_info_string - Cómo funciona](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_string_HOW.md)**

---

## Firma del método

```python
async def symbol_info_string(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoStringProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoStringData
```

**Mensaje de solicitud:**

```protobuf
message SymbolInfoStringRequest {
  string symbol = 1;
  SymbolInfoStringProperty type = 2;
}
```

**Mensaje de respuesta:**

```protobuf
message SymbolInfoStringReply {
  oneof response {
    SymbolInfoStringData data = 1;
    Error error = 2;
  }
}

message SymbolInfoStringData {
  string value = 1;
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
| ----------- | -------------------------------- | ---------------------------------------------- |
| `symbol` | `str` (obligatorio) | Nombre del símbolo |
| `property` | `SymbolInfoStringProperty` (enum) | Propiedad que se desea obtener (DESCRIPTION, PATH, etc.) |
| `deadline` | `datetime` (opcional) | Límite de tiempo para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

---

## ⬆️ Salida

| Campo | Tipo | Tipo Python | Descripción |
| ------- | -------- | ----------- | ---------------------------------- |
| `value` | `string` | `str` | Valor de cadena de la propiedad |

**Valor de retorno:** el método devuelve un objeto `SymbolInfoStringData` con el campo `value`, que contiene la propiedad solicitada.

---

## 🧱 Enums relacionados (de proto)

> **Nota:** en el código Python, utiliza la ruta completa del enum del módulo `market_info`.

### `SymbolInfoStringProperty`

Definido en `mt5-term-api-market-info.proto`.

| Constante | Valor | Descripción |
|----------|-------|-------------|
| `SYMBOL_BASIS` | 0 | Base del símbolo |
| `SYMBOL_CATEGORY` | 1 | Categoría del símbolo |
| `SYMBOL_COUNTRY` | 2 | País del símbolo |
| `SYMBOL_SECTOR_NAME` | 3 | Nombre del sector |
| `SYMBOL_INDUSTRY_NAME` | 4 | Nombre de la industria |
| `SYMBOL_CURRENCY_BASE` | 5 | Divisa base |
| `SYMBOL_CURRENCY_PROFIT` | 6 | Divisa en la que se calculan los beneficios |
| `SYMBOL_CURRENCY_MARGIN` | 7 | Divisa de margen |
| `SYMBOL_BANK` | 8 | Banco proveedor de la cotización |
| `SYMBOL_DESCRIPTION` | 9 | Descripción del símbolo |
| `SYMBOL_EXCHANGE` | 10 | Nombre de la bolsa |
| `SYMBOL_FORMULA` | 11 | Fórmula para símbolos personalizados |
| `SYMBOL_ISIN` | 12 | Código ISIN |
| `SYMBOL_PAGE` | 13 | URL de la página web |
| `SYMBOL_PATH` | 14 | Ruta del símbolo en el árbol de símbolos |

**Uso en Python:**

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener la descripción del símbolo
desc = await account.symbol_info_string("EURUSD", market_info_pb2.SYMBOL_DESCRIPTION)
print(f"Descripción: {desc.value}")

# Obtener el par de divisas
base = await account.symbol_info_string("EURUSD", market_info_pb2.SYMBOL_CURRENCY_BASE)
profit = await account.symbol_info_string("EURUSD", market_info_pb2.SYMBOL_CURRENCY_PROFIT)
print(f"Par: {base.value}/{profit.value}")
```

---

## 🧩 Notas y consejos

- **Reconexión automática:** protección integrada contra errores gRPC transitorios mediante la reconexión automática a través de `execute_with_reconnect`.
- **Tiempo de espera predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca un timeout del servidor).
- **Acceso al valor:** el objeto `SymbolInfoStringData` devuelto tiene un campo `.value` que contiene la cadena.
- **Propiedades de divisa:** CURRENCY_BASE, CURRENCY_PROFIT y CURRENCY_MARGIN son esenciales para los cálculos de margen y beneficio.
- **Formato de la ruta:** SYMBOL_PATH utiliza barras invertidas como separadores (por ejemplo, `Forex\Majors\EURUSD`).
- **Valores vacíos:** algunas propiedades pueden devolver cadenas vacías si el bróker no las ha establecido.
- **Códigos ISIN:** solo están disponibles para valores como acciones y bonos.

---

## 🔗 Ejemplos de uso

### 1) Obtener la descripción del símbolo

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener la descripción del símbolo
result = await account.symbol_info_string(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DESCRIPTION
)
print(f"Descripción: {result.value}")  # Salida: Descripción: Euro vs US Dollar
```

### 2) Obtener el conjunto de tres divisas (base, beneficio y margen)

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener los tres códigos de divisa
base = await account.symbol_info_string(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_CURRENCY_BASE
)

profit = await account.symbol_info_string(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_CURRENCY_PROFIT
)

margin = await account.symbol_info_string(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_CURRENCY_MARGIN
)

print(f"Divisas de XAUUSD:")
print(f"  Base: {base.value}")      # XAU (Oro)
print(f"  Beneficio: {profit.value}")  # USD
print(f"  Margen: {margin.value}")  # USD
```

### 3) Obtener la ruta del símbolo y analizar su jerarquía

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_string(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_PATH
)

# Analizar la jerarquía de la ruta
path = result.value
folders = path.split("\\")

print(f"Ruta del símbolo: {path}")
print(f"Jerarquía: {' > '.join(folders)}")
# Salida: Jerarquía: Forex > Majors > EURUSD
```

### 4) Obtener el código ISIN de acciones

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_string(
    symbol="AAPL",
    property=market_info_pb2.SYMBOL_ISIN
)

if result.value:
    print(f"ISIN de AAPL: {result.value}")
else:
    print("ISIN no disponible")
```

### 5) Obtener el nombre de la bolsa

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_string(
    symbol="BTCUSD",
    property=market_info_pb2.SYMBOL_EXCHANGE
)

print(f"Bolsa: {result.value}")
```

### 6) Mostrar los metadatos del símbolo

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def display_symbol_metadata(account, symbol: str):
    """Muestra metadatos completos de tipo cadena para un símbolo"""

    # Obtener la descripción
    desc = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_DESCRIPTION
    )

    # Obtener la ruta
    path = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_PATH
    )

    # Obtener las divisas
    base_curr = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_CURRENCY_BASE
    )

    profit_curr = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_CURRENCY_PROFIT
    )

    print(f"Metadatos del símbolo: {symbol}")
    print(f"  Descripción: {desc.value}")
    print(f"  Ruta: {path.value}")
    print(f"  Divisa base: {base_curr.value}")
    print(f"  Divisa de beneficio: {profit_curr.value}")

# Uso
await display_symbol_metadata(account, "EURUSD")
```

### 7) Obtener un símbolo con tiempo de espera

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone

deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    result = await account.symbol_info_string(
        symbol="GBPUSD",
        property=market_info_pb2.SYMBOL_DESCRIPTION,
        deadline=deadline
    )
    print(f"Descripción: {result.value}")
except Exception as e:
    print(f"Tiempo de espera agotado o error: {e}")
```

---

## 📚 Véase también

- [symbol_info_double](./symbol_info_double.md) - Obtener propiedades de tipo double
- [symbol_info_integer](./symbol_info_integer.md) - Obtener propiedades de tipo integer
- [symbol_params_many](./symbol_params_many.md) - Obtener todos los parámetros del símbolo a la vez