# Obtener el tick actual de un símbolo

> **Solicitud:** obtener los datos del tick actual de un símbolo (bid, ask, last, volumen y hora).

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_info_tick(...)` (definida en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolInfoTick` (definida en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolInfoTick(SymbolInfoTickRequest) -> SymbolInfoTickRequestReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolInfoTick(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene la instantánea más reciente del tick de un símbolo, con precios bid/ask, volumen y marcas de tiempo.
- **Por qué lo necesitas.** Permite obtener datos de precios en tiempo real para cotizaciones, cálculos del spread y comprobaciones de actualidad antes de operar.
- **Cuándo utilizarlo.** Utilízalo para consultas de un solo tick. Para recibir actualizaciones continuas, utiliza el método de streaming `on_symbol_tick()`.

---

## 🎯 Propósito

Utiliza este método para obtener datos actuales del mercado:

- Mostrar los precios bid/ask en tiempo real en la interfaz de usuario.
- Calcular el spread actual.
- Comprobar la actualidad de las cotizaciones (antigüedad del tick).
- Obtener el precio de la última operación y los volúmenes.
- Validar los datos de mercado antes de enviar una orden.
- Supervisar las marcas de tiempo de los ticks para medir la latencia.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [symbol_info_tick - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_tick_HOW\.md)**

---

## Firma del método

```
async def symbol_info_tick(
    self,
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.MrpcMqlTick
```

**Mensaje de solicitud:**

```
message SymbolInfoTickRequest {
  string symbol = 1;
}
```

**Mensaje de respuesta:**

```
message SymbolInfoTickRequestReply {
  oneof response {
    MrpcMqlTick data = 1;
    Error error = 2;
  }
}

message MrpcMqlTick {
  int64 time = 1;
  double bid = 2;
  double ask = 3;
  double last = 4;
  uint64 volume = 5;
  int64 time_msc = 6;
  uint32 flags = 7;
  double volume_real = 8;
}
```

---

## 🔽 Entrada

| Parámetro            | Tipo                       | Descripción                                              |
| -------------------- | -------------------------- | -------------------------------------------------------- |
| `symbol`             | `str` (obligatorio)        | Nombre del símbolo                                       |
| `deadline`           | `datetime` (opcional)      | Límite de tiempo para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación                        |

---

## ⬆️ Salida

| Campo          | Tipo     | Tipo Python | Descripción                                                     |
| -------------- | -------- | ----------- | --------------------------------------------------------------- |
| `time`         | `int64`  | `int`       | Hora del tick, Unix, en la zona horaria del servidor del bróker (segundos)                  |
| `time_utc`     | `int64`  | `int`       | `time` expresado en UTC (el mismo instante)       |
| `bid`          | `double` | `float`     | Mejor precio bid actual                                         |
| `ask`          | `double` | `float`     | Mejor precio ask actual                                         |
| `last`         | `double` | `float`     | Precio de la última operación (si corresponde)                  |
| `volume`       | `uint64` | `int`       | Volumen del tick (número de ticks)                              |
| `time_msc`     | `int64`  | `int`       | Hora del tick en la zona horaria del servidor del bróker (milisegundos)              |
| `time_msc_utc` | `int64`  | `int`       | `time_msc` expresado en UTC (el mismo instante)   |
| `flags`        | `uint32` | `int`       | Máscara de bits de indicadores del tick (flags de ticks de MT5) |
| `volume_real`  | `double` | `float`     | Volumen real (si lo proporciona el bróker)                      |

**Valor de retorno:** el método devuelve un objeto `MrpcMqlTick` con todos los campos de datos del tick.

---

## 🧩 Notas y consejos

- **Reconexión automática:** protección integrada contra errores gRPC transitorios mediante la reconexión automática a través de `execute_with_reconnect`.
- **Tiempo de espera predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca un timeout del servidor).
- **Sincronización del símbolo:** el símbolo debe estar seleccionado y sincronizado para que los datos sean válidos. Si bid/ask son cero, llama primero a `symbol_select()` y `symbol_is_synchronized()`.
- **Campos de tiempo:** `time` (segundos) y `time_msc` (milisegundos) son marcas de tiempo Unix en la zona horaria del servidor del bróker. Usa `time_utc` / `time_msc_utc` para los mismos instantes en UTC.
- **Cálculo del spread:** Spread = `ask - bid`. Precio medio = `(ask + bid) / 2`.
- **Campos de volumen:** `volume` es el número de ticks (`uint64`), mientras que `volume_real` es el volumen real negociado (`double`).
- **Campo flags:** máscara de bits que indica las propiedades del tick (cambio de bid, cambio de ask, cambio de last o cambio de volumen).
- **Comprobación de actualidad:** compara `time` con la marca de tiempo actual para detectar datos obsoletos.
- **Valores cero:** si los datos del tick son ceros, es posible que el símbolo no esté sincronizado o seleccionado.

---

## 🔗 Ejemplos de uso

### 1) Obtener el bid/ask actual y el spread

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener el tick actual
tick = await account.symbol_info_tick(symbol="EURUSD")

print(f"Símbolo: EURUSD")
print(f"  Bid: {tick.bid}")
print(f"  Ask: {tick.ask}")
print(f"  Spread: {tick.ask - tick.bid}")
print(f"  Precio medio: {(tick.bid + tick.ask) / 2}")
```

### 2) Comprobar la actualidad del tick

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

# Obtener el tick y comprobar su antigüedad
tick = await account.symbol_info_tick(symbol="XAUUSD")

if tick.time_utc > 0:
    current_time = datetime.now(timezone.utc).timestamp()
    age_seconds = int(current_time - tick.time_utc)

    print(f"Antigüedad del tick: {age_seconds} segundos")

    if age_seconds > 5:
        print("Advertencia: ¡Los datos del tick pueden estar obsoletos!")
    else:
        print("Los datos del tick están actualizados")
else:
    print("No hay información de hora del tick disponible")
```

### 3) Asegurarse de que el símbolo esté sincronizado antes de obtener el tick

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

symbol = "BTCUSD"

# Comprobar si el símbolo está sincronizado
sync_status = await account.symbol_is_synchronized(symbol)

if not sync_status.is_synchronized:
    print(f"El símbolo {symbol} no está sincronizado, seleccionándolo...")

    # Seleccionar el símbolo
    await account.symbol_select(symbol, True)

    # Esperar a que se complete la sincronización
    sync_status = await account.symbol_is_synchronized(symbol)
    print(f"Sincronizado: {sync_status.is_synchronized}")

# Ahora obtener el tick
tick = await account.symbol_info_tick(symbol)
print(f"{symbol} - Bid: {tick.bid}, Ask: {tick.ask}")
```

### 4) Mostrar información sobre el volumen

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener el tick con datos de volumen
tick = await account.symbol_info_tick(symbol="EURUSD")

print(f"Información del volumen:")
print(f"  Volumen de ticks (cantidad): {tick.volume}")
print(f"  Volumen real: {tick.volume_real}")
print(f"  Precio de la última operación: {tick.last}")
```

### 5) Convertir las marcas de tiempo a un formato legible

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

# Obtener el tick
tick = await account.symbol_info_tick(symbol="GBPUSD")

# Convertir las marcas de tiempo
if tick.time_utc > 0:
    time_dt = datetime.fromtimestamp(tick.time_utc, tz=timezone.utc)
    print(f"Hora del tick: {time_dt.isoformat()}")

if tick.time_msc_utc > 0:
    time_msc_dt = datetime.fromtimestamp(tick.time_msc_utc / 1000, tz=timezone.utc)
    print(f"Hora del tick (ms): {time_msc_dt.isoformat()}")
    print(f"Precisión en milisegundos: {tick.time_msc_utc % 1000}ms")
```

### 6) Obtener el tick con tiempo de espera

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone
import asyncio

# Crear el evento de cancelación
cancel_event = asyncio.Event()

# Establecer el límite de tiempo
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    tick = await account.symbol_info_tick(
        symbol="EURUSD",
        deadline=deadline,
        cancellation_event=cancel_event
    )
    print(f"Tick obtenido: Bid={tick.bid}, Ask={tick.ask}")
except Exception as e:
    print(f"Tiempo de espera agotado o error: {e}")
```

### 7) Validar los datos del tick antes de operar

```
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

async def validate_tick(account, symbol: str) -> bool:
    """Valida que los datos del tick sean actuales y válidos para operar"""
    try:
        tick = await account.symbol_info_tick(symbol)

        # Comprobar que bid/ask no sean cero
        if tick.bid <= 0 or tick.ask <= 0:
            print(f"Precios no válidos: bid={tick.bid}, ask={tick.ask}")
            return False

        # Comprobar que el spread sea razonable (no sea cero ni demasiado amplio)
        spread = tick.ask - tick.bid
        if spread <= 0:
            print(f"Spread no válido: {spread}")
            return False

        # Comprobar la actualidad del tick (menos de 10 segundos)
        if tick.time_utc > 0:
            current_time = datetime.now(timezone.utc).timestamp()
            age = current_time - tick.time_utc

            if age > 10:
                print(f"Tick demasiado antiguo: {age} segundos")
                return False

        print(f"Validación del tick superada")
        return True

    except Exception as e:
        print(f"Error de validación: {e}")
        return False

# Uso
if await validate_tick(account, "EURUSD"):
    print("Listo para enviar la orden")
else:
    print("La validación del tick ha fallado, no se puede operar")
```

---

## 📚 Véase también

- symbol_is_synchronized - Comprobar el estado de sincronización del símbolo
- symbol_select - Seleccionar o quitar un símbolo de Observación del mercado (Market Watch)
- [on_symbol_tick]\(../6. Streaming_Methods/on_symbol_tick.md) - Suscribirse a las actualizaciones de ticks en tiempo real
- symbol_info_double - Obtener propiedades double del símbolo

Corrige los campos de tiempo de salidaElimina imports no utilizados