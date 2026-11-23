

# Obtener los horarios de las sesiones de trading de un símbolo

> **Solicitud:** obtener las horas de inicio y finalización de las sesiones de trading de un símbolo.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_info_session_trade(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolInfoSessionTrade` (definido en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolInfoSessionTrade(SymbolInfoSessionTradeRequest) -> SymbolInfoSessionTradeReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolInfoSessionTrade(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene las horas de inicio y finalización de las sesiones de trading de un símbolo para un día específico de la semana.
- **Por qué lo necesitas.** Permite saber cuándo se pueden colocar órdenes para los símbolos y comprender las diferencias entre los horarios de trading y los horarios de cotización.
- **Cuándo utilizarlo.** Para comprobar cuándo está permitido operar, verificar los horarios de envío de órdenes y planificar horarios de trading automatizado.

---

## 🎯 Propósito

Utiliza este método para consultar los horarios de las sesiones de trading:

- Obtener los horarios de las sesiones de trading de un símbolo para cada día.
- Comprobar cuándo está permitido colocar órdenes.
- Verificar las diferencias entre los horarios de trading y los horarios de cotización.
- Planificar horarios de trading automatizado.
- Comprender las pausas entre sesiones.
- Coordinar las operaciones con los horarios del mercado.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [symbol_info_session_trade - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_trade_HOW\.md)**

---

## Firma del método

```
async def symbol_info_session_trade(
    self,
    symbol: str,
    day_of_week: market_info_pb2.DayOfWeek,
    session_index: int,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoSessionTradeData
```

**Mensaje de solicitud:**

```
message SymbolInfoSessionTradeRequest {
    string symbol = 1;
    DayOfWeek day_of_week = 2;
    uint32 session_index = 3;
}
```

**Mensaje de respuesta:**

```
message SymbolInfoSessionTradeReply {
    oneof response {
        SymbolInfoSessionTradeData data = 1;
        Error error = 2;
    }
}

message SymbolInfoSessionTradeData {
    google.protobuf.Timestamp from = 1;
    google.protobuf.Timestamp to = 2;
}
```

---

## 🔽 Parámetros de entrada

| Parámetro            | Tipo                       | Descripción                                                  |
| -------------------- | -------------------------- | ------------------------------------------------------------ |
| `symbol`             | `str` (obligatorio)        | Nombre del símbolo                                           |
| `day_of_week`        | `DayOfWeek` (enum)         | Día de la semana (SUNDAY, MONDAY, etc.)                      |
| `session_index`      | `int` (obligatorio)        | Índice de la sesión (normalmente 0 para la sesión principal) |
| `deadline`           | `datetime` (opcional)      | Plazo límite para la llamada gRPC (fecha y hora UTC)         |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación                            |

---

## ⬆️ Salida

| Campo  | Tipo        | Tipo de Python | Descripción                                                     |
| ------ | ----------- | -------------- | --------------------------------------------------------------- |
| `from` | `Timestamp` | `Timestamp`    | Hora de inicio de la sesión (`google.protobuf.Timestamp`)       |
| `to`   | `Timestamp` | `Timestamp`    | Hora de finalización de la sesión (`google.protobuf.Timestamp`) |

**Valor devuelto:** el método devuelve un objeto `SymbolInfoSessionTradeData` con los campos `from` y `to` de tipo `Timestamp`.

---

## 🧱 Enums relacionados (del proto)

> **Nota:** En el código Python, utiliza las constantes directamente desde el módulo `market_info`.

### `DayOfWeek`

Definido en `mt5-term-api-market-info.proto`.

| Constante   | Valor | Descripción |
| ----------- | ----- | ----------- |
| `SUNDAY`    | 0     | Domingo     |
| `MONDAY`    | 1     | Lunes       |
| `TUESDAY`   | 2     | Martes      |
| `WEDNESDAY` | 3     | Miércoles   |
| `THURSDAY`  | 4     | Jueves      |
| `FRIDAY`    | 5     | Viernes     |
| `SATURDAY`  | 6     | Sábado      |

**Uso en Python:**

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener la sesión de trading del lunes
session = await account.symbol_info_session_trade(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

print(f"Horario de trading: {getattr(session, 'from').seconds}s - {session.to.seconds}s")
```

---

## 🧩 Notas y recomendaciones

- **Reconexión automática:** protección integrada contra errores gRPC transitorios mediante la reconexión automática a través de `execute_with_reconnect`.
- **Tiempo de espera predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca un timeout del servidor).
- **Formato de Timestamp:** los campos `from` y `to` son objetos `google.protobuf.Timestamp` con los atributos `seconds` y `nanos`.
- **Interpretación de la hora:** las horas representan los segundos transcurridos desde la medianoche (00:00) del día especificado.
- **Índice de sesión:** la mayoría de los símbolos tienen una sesión principal (índice 0). Algunos pueden tener varias sesiones (por ejemplo, con pausas para comer).
- **Varias sesiones:** si un símbolo tiene varias sesiones de trading al día, utiliza distintos valores de `session_index` (0, 1, 2...).
- **Zona horaria:** las horas corresponden a la zona horaria del servidor del bróker, no a UTC.
- **Ausencia de sesión:** si una sesión no existe, el método puede devolver un error o marcas de tiempo con valor cero.
- **Sesiones de trading frente a sesiones de cotización:** las sesiones de trading (cuando se pueden colocar órdenes) pueden diferir de las sesiones de cotización (cuando se actualizan los precios). Utiliza ambos métodos para conocer el horario completo del mercado.

---

## 🔗 Ejemplos de uso

### 1) Obtener la sesión de trading del lunes

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener la sesión de trading del lunes
session = await account.symbol_info_session_trade(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

print(f"Sesión de trading del lunes:")
print(f"  Desde: {getattr(session, 'from').seconds}s ({getattr(session, 'from').seconds // 3600}h:{(getattr(session, 'from').seconds % 3600) // 60}m)")
print(f"  Hasta: {session.to.seconds}s ({session.to.seconds // 3600}h:{(session.to.seconds % 3600) // 60}m)")
```

### 2) Obtener todas las sesiones de trading de la semana

```
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

print("Sesiones de trading de EURUSD:")
for day_enum, day_name in days.items():
    try:
        session = await account.symbol_info_session_trade(
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

### 3) Comparar las sesiones de trading y de cotización

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener la sesión de trading
trade_session = await account.symbol_info_session_trade(
    symbol="XAUUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

# Obtener la sesión de cotización
quote_session = await account.symbol_info_session_quote(
    symbol="XAUUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

print(f"Sesiones del lunes para XAUUSD:")
print(f"  Trading: {getattr(trade_session, "from").seconds // 3600:02d}:{(getattr(trade_session, "from").seconds % 3600) // 60:02d} - {trade_session.to.seconds // 3600:02d}:{(trade_session.to.seconds % 3600) // 60:02d}")
print(f"  Cotización: {getattr(quote_session, "from").seconds // 3600:02d}:{(getattr(quote_session, "from").seconds % 3600) // 60:02d} - {quote_session.to.seconds // 3600:02d}:{(quote_session.to.seconds % 3600) // 60:02d}")

if getattr(trade_session, "from").seconds != getattr(quote_session, "from").seconds:
    print("  ¡Las sesiones de trading y de cotización son diferentes!")
```

### 4) Comprobar si se permite operar en este momento

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

async def is_trading_allowed(account, symbol: str) -> bool:
    """Comprueba si se permite operar en el momento actual"""
    now = datetime.now(timezone.utc)
    day_of_week = now.weekday() + 1  # Monday=1 en datetime, Monday=1 en el enum
    if day_of_week == 7:  # Sunday
        day_of_week = 0

    try:
        session = await account.symbol_info_session_trade(
            symbol=symbol,
            day_of_week=day_of_week,
            session_index=0
        )

        # Hora actual expresada en segundos desde la medianoche
        current_seconds = now.hour * 3600 + now.minute * 60 + now.second

        # Comprobar si estamos dentro de la sesión de trading
        if getattr(session, 'from').seconds <= current_seconds <= session.to.seconds:
            return True
        return False
    except Exception:
        return False


# Uso
if await is_trading_allowed(account, "EURUSD"):
    print("Se PERMITE operar")
else:
    print("El trading está CERRADO")
```

### 5) Obtener todas las sesiones de un día (varias sesiones)

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_trade_sessions(account, symbol: str, day_of_week: int):
    """Obtiene todas las sesiones de trading de un símbolo para un día específico"""
    sessions = []
    session_index = 0

    while session_index < 10:  # Máximo 10 sesiones
        try:
            session = await account.symbol_info_session_trade(
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
sessions = await get_all_trade_sessions(account, "NIKKEI", market_info_pb2.MONDAY)
print(f"Se encontraron {len(sessions)} sesión(es) de trading:")
for s in sessions:
    from_h = s['from'] // 3600
    from_m = (s['from'] % 3600) // 60
    to_h = s['to'] // 3600
    to_m = (s['to'] % 3600) // 60
    print(f"  Sesión {s['index']}: {from_h:02d}:{from_m:02d} - {to_h:02d}:{to_m:02d}")
```

### 6) Obtener una sesión con un tiempo de espera límite

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone

deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    session = await account.symbol_info_session_trade(
        symbol="GBPUSD",
        day_of_week=market_info_pb2.FRIDAY,
        session_index=0,
        deadline=deadline
    )
    print(f"Sesión obtenida correctamente")
except Exception as e:
    print(f"Timeout o error: {e}")
```

---

## 📚 Véase también

- symbol_info_session_quote - Obtener los horarios de las sesiones de cotización.
- symbol_info_integer - Obtener otras propiedades enteras del símbolo.
- symbol_info_double - Obtener propiedades `double` del símbolo.



Corrige la sintaxis de las comillas en Python