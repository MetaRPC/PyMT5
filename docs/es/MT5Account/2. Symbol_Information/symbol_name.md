# Obtener el nombre del símbolo por índice

> **Solicitud:** obtener el nombre del símbolo por su índice.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_name(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolName` (definido en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolName(SymbolNameRequest) -> SymbolNameReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolName(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene el nombre de un símbolo según su posición numérica en la lista de símbolos.
- **Por qué lo necesitas.** Permite enumerar los símbolos secuencialmente e iterar programáticamente por los símbolos disponibles.
- **Cuándo utilizarlo.** Utilízalo junto con `symbols_total()` para recorrer todos los símbolos o los símbolos de Market Watch.

---

## 🎯 Propósito

Utiliza este método para enumerar símbolos:

- Recorrer todos los símbolos disponibles.
- Obtener los símbolos de Market Watch según su posición.
- Crear listas de símbolos mediante programación.
- Implementar una interfaz de selección de símbolos.
- Descubrir los instrumentos de trading disponibles.
- Relacionar las posiciones de los índices con los nombres de los símbolos.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [symbol_name - Cómo funciona](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_name_HOW.md)**

---

## Firma del método

```python
async def symbol_name(
    self,
    index: int,
    selected: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolNameData
```

**Mensaje de solicitud:**

```protobuf
message SymbolNameRequest {
    uint32 index = 1;
    bool selected = 2;
}
```

**Mensaje de respuesta:**

```protobuf
message SymbolNameReply {
    oneof response {
        SymbolNameData data = 1;
        Error error = 2;
    }
}

message SymbolNameData {
    string name = 1;
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `index` | `int` (obligatorio) | Índice del símbolo (basado en cero, comienza en 0) |
| `selected` | `bool` (obligatorio) | `True` = solo Market Watch, `False` = todos los símbolos disponibles |
| `deadline` | `datetime` (opcional) | Plazo límite para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

---

## ⬆️ Salida

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `name` | `string` | `str` | Nombre del símbolo en el índice especificado |

**Valor de retorno:** el método devuelve un objeto `SymbolNameData` con el campo `name`, que contiene el nombre del símbolo.

---

## 🧩 Notas y consejos

- **Reconexión automática:** protección integrada contra errores gRPC transitorios mediante la reconexión automática a través de `execute_with_reconnect`.
- **Tiempo de espera predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca un timeout del servidor).
- **Acceso al valor:** el objeto devuelto tiene un campo `.name` que contiene la cadena con el nombre del símbolo.
- **Rango de índices:** los índices válidos van de 0 a `symbols_total() - 1`. Los índices fuera de este rango provocarán un error.
- **Símbolos seleccionados frente al total:** utiliza `selected=True` para los símbolos de Market Watch y `selected=False` para todos los símbolos del bróker.
- **Dependencia del orden:** el orden de los símbolos puede cambiar entre llamadas si se modifica Market Watch.
- **Indexación basada en cero:** el primer símbolo está en el índice 0, no en el 1.
- **Combinar con symbols_total:** llama siempre primero a `symbols_total()` para obtener el rango válido de índices.

---

## 🔗 Ejemplos de uso

### 1) Obtener todos los símbolos de Market Watch

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_market_watch_symbols(account) -> list[str]:
    """Obtiene la lista de todos los símbolos de Market Watch"""

    # Obtener el número total de símbolos de Market Watch
    count_data = await account.symbols_total(selected_only=True)
    total = count_data.total

    print(f"Se encontraron {total} símbolos en Market Watch")

    # Recorrer y recopilar todos los nombres de los símbolos
    symbols = []
    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=True)
        symbols.append(symbol_data.name)

    return symbols


# Uso
mw_symbols = await get_all_market_watch_symbols(account)
print(f"Símbolos de Market Watch: {mw_symbols}")
```

### 2) Obtener todos los símbolos disponibles del bróker

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_broker_symbols(account) -> list[str]:
    """Obtiene TODOS los símbolos disponibles del bróker"""

    # Obtener el número total de todos los símbolos
    count_data = await account.symbols_total(selected_only=False)
    total = count_data.total

    print(f"Se encontraron {total} símbolos en total en el bróker")

    # Recorrer y recopilar todos los nombres de los símbolos
    symbols = []
    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=False)
        symbols.append(symbol_data.name)

    return symbols


# Uso
all_symbols = await get_all_broker_symbols(account)
print(f"Total de símbolos disponibles: {len(all_symbols)}")
```

### 3) Mostrar los primeros 10 símbolos de Market Watch

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def print_first_symbols(account, count: int = 10):
    """Muestra los primeros N símbolos de Market Watch"""

    print(f"Primeros {count} símbolos de Market Watch:")
    print("=" * 40)

    for i in range(count):
        try:
            symbol_data = await account.symbol_name(index=i, selected=True)
            print(f"{i+1:3d}. {symbol_data.name}")
        except Exception as e:
            print(f"[ERROR] Índice {i}: {e}")
            break


# Uso
await print_first_symbols(account, count=10)
```

### 4) Buscar símbolos que coincidan con un patrón

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def find_symbols_by_pattern(account, pattern: str, selected_only: bool = True) -> list[str]:
    """Busca símbolos que coincidan con un patrón de texto"""

    # Obtener el número total
    count_data = await account.symbols_total(selected_only=selected_only)
    total = count_data.total

    # Buscar los símbolos que coincidan
    matching_symbols = []
    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=selected_only)

        if pattern.upper() in symbol_data.name.upper():
            matching_symbols.append(symbol_data.name)

    return matching_symbols


# Uso
usd_symbols = await find_symbols_by_pattern(account, "USD")
print(f"Se encontraron {len(usd_symbols)} símbolos que contienen 'USD': {usd_symbols}")
```

### 5) Comparar Market Watch con todos los símbolos disponibles

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def compare_symbol_lists(account):
    """Compara los símbolos de Market Watch con todos los símbolos disponibles"""

    # Obtener los símbolos de Market Watch
    mw_count = await account.symbols_total(selected_only=True)
    mw_total = mw_count.total

    # Obtener todos los símbolos del bróker
    all_count = await account.symbols_total(selected_only=False)
    all_total = all_count.total

    print(f"Estadísticas de símbolos:")
    print(f"  Market Watch: {mw_total} símbolos")
    print(f"  Disponibles en el bróker: {all_total} símbolos")
    print(f"  No incluidos en Market Watch: {all_total - mw_total} símbolos")


# Uso
await compare_symbol_lists(account)
```

### 6) Obtener símbolos con gestión de errores

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_symbols_safe(account, selected_only: bool = True) -> list[str]:
    """Obtiene símbolos con una gestión de errores robusta"""

    symbols = []

    try:
        # Obtener el número total
        count_data = await account.symbols_total(selected_only=selected_only)
        total = count_data.total

        # Recorrer con gestión de errores
        for i in range(total):
            try:
                symbol_data = await account.symbol_name(index=i, selected=selected_only)
                symbols.append(symbol_data.name)
            except Exception as e:
                print(f"Error al obtener el símbolo en el índice {i}: {e}")
                # Continuar con el siguiente símbolo
                continue

        print(f"Se obtuvieron correctamente {len(symbols)} de {total} símbolos")

    except Exception as e:
        print(f"Error al obtener el número de símbolos: {e}")

    return symbols


# Uso
symbols = await get_symbols_safe(account, selected_only=True)
```

### 7) Obtener el nombre del símbolo con un plazo límite

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone

# Establecer el plazo límite
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    symbol_data = await account.symbol_name(
        index=0,
        selected=True,
        deadline=deadline
    )
    print(f"Primer símbolo: {symbol_data.name}")
except Exception as e:
    print(f"Timeout o error: {e}")
```

### 8) Crear un diccionario de símbolos con metadatos

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def build_symbol_dict(account) -> dict:
    """Crea un diccionario que relaciona los índices con la información de los símbolos"""

    count_data = await account.symbols_total(selected_only=True)
    total = count_data.total

    symbol_dict = {}

    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=True)
        symbol_name = symbol_data.name

        # Obtener información adicional
        digits_data = await account.symbol_info_integer(
            symbol=symbol_name,
            property=market_info_pb2.SYMBOL_DIGITS
        )

        symbol_dict[i] = {
            'name': symbol_name,
            'index': i,
            'digits': digits_data.value
        }

    return symbol_dict


# Uso
symbols_info = await build_symbol_dict(account)
for idx, info in symbols_info.items():
    print(f"{idx}: {info['name']} (digits={info['digits']})")
```

---

## 📚 Véase también

- [symbols_total](./symbols_total.md) - Obtener el número total de símbolos (utilizar antes de llamar a `symbol_name`).
- [symbol_exist](./symbol_exist.md) - Comprobar si existe un símbolo específico.
- [symbol_select](./symbol_select.md) - Añadir o eliminar símbolos de Market Watch.