

# Obtener los horarios de las sesiones de cotización de un símbolo

> **Solicitud:** obtener las horas de inicio y finalización de las sesiones de cotización de un símbolo.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_info_session_quote(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolInfoSessionQuote` (definido en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolInfoSessionQuote(SymbolInfoSessionQuoteRequest) -> SymbolInfoSessionQuoteReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolInfoSessionQuote(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene las horas de inicio y finalización de las sesiones de cotización de un símbolo para un día específico de la semana.
- **Por qué lo necesitas.** Permite saber cuándo se pueden recibir cotizaciones de precios de los símbolos y comprender los horarios del mercado.
- **Cuándo utilizarlo.** Para comprobar la disponibilidad de cotizaciones de un símbolo, planificar horarios de trading automatizado y verificar las horas de apertura del mercado.

---

## 🎯 Propósito

Utiliza este método para consultar los horarios de las sesiones de cotización:

- Obtener los horarios de las sesiones de cotización de un símbolo para cada día.
- Comprobar cuándo están disponibles las actualizaciones de precios.
- Verificar las horas de apertura y cierre del mercado.
- Planificar los horarios de supervisión de cotizaciones.
- Comprender las pausas entre sesiones.
- Coordinar las operaciones con las sesiones de trading.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [symbol_info_session_quote - Cómo funciona](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_quote_HOW.md)**

---

## Firma del método

```python
async def symbol_info_session_quote(
    self,
    symbol: str,
    day_of_week: market_info_pb2.DayOfWeek,
    session_index: int,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoSessionQuoteData
```

**Mensaje de solicitud:**

```protobuf
message SymbolInfoSessionQuoteRequest {
    string symbol = 1;
    DayOfWeek day_of_week = 2;
    uint32 session_index = 3;
}
```

**Mensaje de respuesta:**

```protobuf
message SymbolInfoSessionQuoteReply {
    oneof response {
        SymbolInfoSessionQuoteData data = 1;
        Error error = 2;
    }
}

message SymbolInfoSessionQuoteData {
    google.protobuf.Timestamp from = 1;
    google.protobuf.Timestamp to = 2;
}
```

---

## 🔽 Parámetros de entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `symbol` | `str` (obligatorio) | Nombre del símbolo |
| `day_of_week` | `DayOfWeek` (enum) | Día de la semana (SUNDAY, MONDAY, etc.) |
| `session_index` | `int` (obligatorio) | Índice de la sesión (normalmente 0 para la sesión principal) |
| `deadline` | `datetime` (opcional) | Plazo límite para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

---

## ⬆️ Salida

| Campo | Tipo | Tipo de Python | Descripción |
|---|---|---|---|
| `from` | `Timestamp` | `Timestamp` | Hora de inicio de la sesión (`google.protobuf.Timestamp`) |
| `to` | `Timestamp` | `Timestamp` | Hora de finalización de la sesión (`google.protobuf.Timestamp`) |

**Valor devuelto:** el método devuelve un objeto `SymbolInfoSessionQuoteData` con los campos `from` y `to` de tipo `Timestamp`.

---

## 🧱 Enums relacionados (del proto)

> **Nota:** En el código Python, utiliza las constantes directamente desde el módulo `market_info`.

### `DayOfWeek`

Definido en `mt5-term-api-market-info.proto`.

| Constante | Valor | Descripción |
|---|---:|---|
| `SUNDAY` | 0 | Domingo |
| `MONDAY` | 1 | Lunes |
| `TUESDAY` | 2 | Martes |
| `WEDNESDAY` | 3 | Miércoles |
| `THURSDAY` | 4 | Jueves |
| `FRIDAY` | 5 | Viernes |
| `SATURDAY` | 6 | Sábado |

**Uso en Python:**

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener la sesión de cotización del lunes
session = await account.symbol_info_session_quote(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

print(f"Desde: {getattr(session, 'from').seconds}s, Hasta: {session.to.seconds}s")
```

---

## 🧩 Notas y recomendaciones

- **Reconexión automática:** protección integrada contra errores gRPC transitorios mediante la reconexión automática a través de `execute_with_reconnect`.
- **Tiempo de espera predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca un timeout del servidor).
- **Formato de Timestamp:** los campos `from` y `to` son objetos `google.protobuf.Timestamp` con los atributos `seconds` y `nanos`.
- **Interpretación de la hora:** las horas representan los segundos transcurridos desde la medianoche (00:00) del día especificado.
- **Índice de sesión:** la mayoría de los símbolos tienen una sesión principal (índice 0). Algunos pueden tener varias sesiones (por ejemplo, con pausas del mediodía).
- **Varias sesiones:** si un símbolo tiene varias sesiones de cotización al día, utiliza distintos valores de `session_index` (0, 1, 2...).
- **Zona horaria:** las horas corresponden a la zona horaria del servidor del bróker, no a UTC.
- **Ausencia de sesión:** si una sesión no existe, el método puede devolver un error o marcas de tiempo con valor cero.

---

## 🔗 Ejemplos de uso

### 1) Obtener la sesión de cotización del lunes

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener la sesión de cotización del lunes
session = await account.symbol_info_session_quote(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

print(f"Sesión de cotización del lunes:")
print(f"  Desde: {getattr(session, 'from').seconds}s ({getattr(session, 'from').seconds // 3600}h:{(getattr(session, 'from').seconds % 3600) // 60}m)")
print(f"  Hasta: {session.to.seconds}s ({session.to.seconds // 3600}h:{(session.to.seconds % 3600) // 60}m)")
```

### 2) Obtener todas las sesiones de cotización de la semana

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

days = {
    market_info_pb2.SUNDAY: "Domingo",
    market_info_pb2.MONDAY: "Lunes",
    market_info_pb2.TUESDAY: "Martes",
    market_info_pb2.WEDNESDAY: "Miércoles",
    market_info_pb2.THURSDAY: "Jueves",
    market_info_pb2.FRIDAY: "Viernes",
    market_info_pb2.SATURDAY: "Sábado"
}

print("Sesiones de cotización de EURUSD:")
for day_enum, day_name in days.items():
    try:
        session = await account.symbol_info_session_quote(
            symbol="EURUSD",
            day_of_week=day_enum,
            session_index=0
        )

        from_hours = getattr(session, 'from').seconds // 3600
        from_mins = (getattr(session, 'from').seconds % 3600) // 60
        to_hours = session.to.seconds // 3600
        to_mins = (session.to.seconds % 3600) // 60

        print(f"  {day_name:10s} {from_hours:02d}:{from_mins:02d} - {to_hours:02d}:{to_mins:02d}")
    except Exception as e:
        print(f"  {day_name:10s} Sin sesión")
```

### 3) Convertir Timestamp a una hora legible

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import time

def timestamp_to_time(timestamp) -> time:
    """Convierte un Timestamp de protobuf a datetime.time"""
    total_seconds = timestamp.seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return time(hour=hours, minute=minutes, second=seconds)


# Obtener la sesión
session = await account.symbol_info_session_quote(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

# Convertir a objetos time
from_time = timestamp_to_time(getattr(session, 'from'))
to_time = timestamp_to_time(session.to)

print(f"Sesión de cotización: {from_time} - {to_time}")
# Salida: Sesión de cotización: 00:00:00 - 23:59:59
```

### 4) Comprobar si un símbolo tiene una sesión de cotización en un día específico

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def has_quote_session(account, symbol: str, day_of_week: int) -> bool:
    """Comprueba si el símbolo tiene una sesión de cotización en el día especificado"""
    try:
        session = await account.symbol_info_session_quote(
            symbol=symbol,
            day_of_week=day_of_week,
            session_index=0
        )

        # Comprobar si la sesión tiene horas válidas (distintas de cero)
        if getattr(session, 'from').seconds > 0 or session.to.seconds > 0:
            return True
        return False
    except Exception:
        return False


# Uso
if await has_quote_session(account, "EURUSD", market_info_pb2.SATURDAY):
    print("EURUSD tiene cotizaciones el sábado")
else:
    print("EURUSD NO tiene cotizaciones el sábado")
```

### 5) Obtener una sesión con un plazo límite

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone

deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    session = await account.symbol_info_session_quote(
        symbol="GBPUSD",
        day_of_week=market_info_pb2.FRIDAY,
        session_index=0,
        deadline=deadline
    )
    print(f"Sesión obtenida correctamente")
except Exception as e:
    print(f"Timeout o error: {e}")
```

### 6) Comprobar si hay varias sesiones (pausas del mediodía)

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_sessions(account, symbol: str, day_of_week: int):
    """Obtiene todas las sesiones de cotización de un símbolo para un día específico"""
    sessions = []
    session_index = 0

    while session_index < 10:  # Máximo 10 sesiones
        try:
            session = await account.symbol_info_session_quote(
                symbol=symbol,
                day_of_week=day_of_week,
                session_index=session_index
            )

            # Comprobar si la sesión es válida
            if getattr(session, 'from').seconds == 0 and session.to.seconds == 0:
                break

            sessions.append({
                'index': session_index,
                'from': getattr(session, 'from').seconds,
                'to': session.to.seconds
            })
            session_index += 1
        except Exception:
            break

    return sessions


# Uso
sessions = await get_all_sessions(account, "NIKKEI", market_info_pb2.MONDAY)
print(f"Se encontraron {len(sessions)} sesión(es) de cotización:")
for s in sessions:
    from_h = s['from'] // 3600
    from_m = (s['from'] % 3600) // 60
    to_h = s['to'] // 3600
    to_m = (s['to'] % 3600) // 60
    print(f"  Sesión {s['index']}: {from_h:02d}:{from_m:02d} - {to_h:02d}:{to_m:02d}")
```

---

## 📚 Véase también

- [symbol_info_session_trade](./symbol_info_session_trade.md) - Obtener los horarios de las sesiones de trading.
- [symbol_info_integer](./symbol_info_integer.md) - Obtener otras propiedades enteras del símbolo.
- [symbol_info_double](./symbol_info_double.md) - Obtener propiedades `double` del símbolo.

