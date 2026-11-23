# Comprobar si el símbolo está sincronizado

> **Solicitud:** comprobar si los datos del símbolo están sincronizados con el servidor.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_is_synchronized(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolIsSynchronized` (definido en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolIsSynchronized(SymbolIsSynchronizedRequest) -> SymbolIsSynchronizedReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolIsSynchronized(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Comprueba si los datos de mercado de un símbolo están sincronizados actualmente con el servidor del bróker.
- **Por qué lo necesitas.** Permite comprobar si los datos del símbolo están sincronizados antes de consultar precios o enviar órdenes.
- **Cuándo utilizarlo.** Después de seleccionar un símbolo, antes de leer los datos de ticks o al validar la disponibilidad del símbolo.

---

## 🎯 Propósito

Utiliza este método para verificar la disponibilidad de los datos del símbolo:

- Comprobar el estado de sincronización del símbolo antes de operar.
- Validar los datos del símbolo después de llamar a `symbol_select()`.
- Garantizar que los datos de ticks sean actuales y válidos.
- Diagnosticar la ausencia de datos de mercado o la presencia de datos obsoletos.
- Implementar una lógica de reintentos para la selección de símbolos.
- Comprobar la disponibilidad de los datos del símbolo antes de realizar operaciones.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [symbol_is_synchronized - Cómo funciona](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_is_synchronized_HOW.md)**

---

## Firma del método

```python
async def symbol_is_synchronized(
    self,
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolIsSynchronizedData
```

**Mensaje de solicitud:**

```protobuf
message SymbolIsSynchronizedRequest {
    string symbol = 1;
}
```

**Mensaje de respuesta:**

```protobuf
message SymbolIsSynchronizedReply {
    oneof response {
        SymbolIsSynchronizedData data = 1;
        Error error = 2;
    }
}

message SymbolIsSynchronizedData {
    bool synchronized = 1;
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `symbol` | `str` (obligatorio) | Nombre del símbolo que se desea comprobar |
| `deadline` | `datetime` (opcional) | Plazo límite para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

---

## ⬆️ Salida

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `synchronized` | `bool` | `bool` | `True` si los datos del símbolo están sincronizados |

**Valor de retorno:** el método devuelve un objeto `SymbolIsSynchronizedData` con el campo booleano `synchronized`.

---

## 🧩 Notas y consejos

- **Reconexión automática:** protección integrada contra errores gRPC transitorios mediante la reconexión automática a través de `execute_with_reconnect`.
- **Tiempo de espera predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca un timeout del servidor).
- **Acceso al valor:** el objeto devuelto tiene un campo `.synchronized` (no `.is_synchronized`).
- **Selección del símbolo:** si `synchronized` es `False`, llama a `symbol_select(symbol, True)` para añadir el símbolo a Market Watch.
- **Retraso de sincronización:** después de seleccionar un símbolo, la sincronización puede tardar entre 1 y 2 segundos.
- **Lógica de reintentos:** implementa consultas periódicas con pausas cuando esperes a que se complete la sincronización.
- **Dependencia de los datos de ticks:** si el símbolo no está sincronizado, `symbol_info_tick()` puede devolver valores cero u obsoletos.
- **No es un error:** devolver `False` es un estado normal, no una condición de error.

---

## 🔗 Ejemplos de uso

### 1) Comprobar si el símbolo está sincronizado

```python

# Comprobar el estado de sincronización
result = await account.symbol_is_synchronized(symbol="EURUSD")

if result.synchronized:
    print("El símbolo está sincronizado")
else:
    print("El símbolo NO está sincronizado")
```

### 2) Garantizar que el símbolo esté sincronizado antes de obtener un tick

```python

async def get_synchronized_tick(account, symbol: str):
    """Obtiene los datos de ticks solo si el símbolo está sincronizado"""

    # Comprobar la sincronización
    sync_status = await account.symbol_is_synchronized(symbol)

    if not sync_status.synchronized:
        print(f"El símbolo {symbol} no está sincronizado, seleccionándolo...")

        # Seleccionar el símbolo
        await account.symbol_select(symbol, True)

        # Esperar un momento para que se complete la sincronización
        import asyncio
        await asyncio.sleep(1)

        # Volver a comprobar
        sync_status = await account.symbol_is_synchronized(symbol)

        if not sync_status.synchronized:
            raise RuntimeError(f"No se pudo sincronizar {symbol}")

    # Ahora es seguro obtener el tick
    tick = await account.symbol_info_tick(symbol)
    return tick


# Uso
tick = await get_synchronized_tick(account, "EURUSD")
print(f"Bid: {tick.bid}, Ask: {tick.ask}")
```

### 3) Esperar a que se complete la sincronización con un timeout

```python
import asyncio

async def wait_for_synchronization(
    account,
    symbol: str,
    timeout: float = 10.0,
    check_interval: float = 0.5
) -> bool:
    """Espera a que el símbolo se sincronice dentro del tiempo establecido"""

    start_time = asyncio.get_event_loop().time()

    while True:
        # Comprobar el estado actual
        result = await account.symbol_is_synchronized(symbol)

        if result.synchronized:
            print(f"{symbol} sincronizado")
            return True

        # Comprobar el timeout
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= timeout:
            print(f"Se agotó el tiempo de espera para la sincronización de {symbol}")
            return False

        # Esperar antes de la siguiente comprobación
        await asyncio.sleep(check_interval)


# Uso
if await wait_for_synchronization(account, "BTCUSD", timeout=10):
    print("Listo para operar")
else:
    print("El símbolo no está disponible")
```

### 4) Comprobar la sincronización de varios símbolos en lote

```python

async def check_symbols_sync(account, symbols: list[str]):
    """Comprueba el estado de sincronización de varios símbolos"""

    results = {}

    for symbol in symbols:
        try:
            sync_status = await account.symbol_is_synchronized(symbol)
            results[symbol] = sync_status.synchronized
        except Exception as e:
            print(f"Error al comprobar {symbol}: {e}")
            results[symbol] = False

    # Mostrar los resultados
    print(f"{'Símbolo':<10} {'Estado':<15}")
    print("=" * 25)
    for symbol, is_synced in results.items():
        status = "Sincronizado" if is_synced else "No sincronizado"
        print(f"{symbol:<10} {status:<15}")

    return results


# Uso
symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
sync_results = await check_symbols_sync(account, symbols)
```

### 5) Seleccionar el símbolo y esperar a que se sincronice

```python
import asyncio

async def ensure_symbol_synchronized(
    account,
    symbol: str,
    max_retries: int = 5
) -> bool:
    """Selecciona el símbolo y espera a que se complete la sincronización"""

    # Primero, comprobar si ya está sincronizado
    result = await account.symbol_is_synchronized(symbol)
    if result.synchronized:
        print(f"{symbol} ya está sincronizado")
        return True

    # Seleccionar el símbolo
    print(f"Seleccionando {symbol}...")
    await account.symbol_select(symbol, True)

    # Reintentar con un intervalo de espera exponencial
    for attempt in range(max_retries):
        await asyncio.sleep(0.5 * (attempt + 1))  # 0.5s, 1s, 1.5s, 2s, 2.5s

        result = await account.symbol_is_synchronized(symbol)
        if result.synchronized:
            print(f"{symbol} sincronizado después de {attempt + 1} intento(s)")
            return True

        print(f"Intento {attempt + 1}/{max_retries}: todavía esperando...")

    print(f"No se pudo sincronizar {symbol} después de {max_retries} intentos")
    return False


# Uso
if await ensure_symbol_synchronized(account, "EURUSD"):
    tick = await account.symbol_info_tick("EURUSD")
    print(f"Tick: {tick.bid}/{tick.ask}")
```

### 6) Comprobar la sincronización con un plazo límite

```python
from datetime import datetime, timedelta, timezone

# Establecer el deadline para la llamada
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    result = await account.symbol_is_synchronized(
        symbol="GBPUSD",
        deadline=deadline
    )

    if result.synchronized:
        print("El símbolo está sincronizado")
    else:
        print("El símbolo necesita sincronización")
except Exception as e:
    print(f"Timeout o error: {e}")
```

### 7) Validar el símbolo antes de realizar una operación de trading

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import asyncio

async def validate_symbol_ready(account, symbol: str) -> bool:
    """
    Comprobación completa de que el símbolo está listo para operar.
    Devuelve True solo si el símbolo existe, está seleccionado y sincronizado.
    """

    # Paso 1: Comprobar si el símbolo existe
    exists = await account.symbol_exist(symbol)
    if not exists.exists:
        print(f"El símbolo {symbol} no existe")
        return False
    print("El símbolo existe")

    # Paso 2: Comprobar si está seleccionado
    select_status = await account.symbol_info_integer(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_SELECT
    )

    if not select_status.value:
        print("El símbolo no está seleccionado, añadiéndolo a Market Watch...")
        await account.symbol_select(symbol, True)
        await asyncio.sleep(1)

    # Paso 3: Comprobar la sincronización
    sync_status = await account.symbol_is_synchronized(symbol)
    if not sync_status.synchronized:
        print("Esperando la sincronización...")

        # Esperar hasta 5 segundos
        for i in range(10):
            await asyncio.sleep(0.5)
            sync_status = await account.symbol_is_synchronized(symbol)
            if sync_status.synchronized:
                break

        if not sync_status.synchronized:
            print(f"No se pudo sincronizar el símbolo {symbol}")
            return False

    print(f"El símbolo {symbol} está listo para operar")
    return True


# Uso
if await validate_symbol_ready(account, "EURUSD"):
    # Seguro para enviar órdenes
    print("Continuando con la operación...")
else:
    print("No se puede operar: el símbolo no está listo")
```

---

## 📚 Véase también

- [symbol_select](./symbol_select.md) - Seleccionar o deseleccionar un símbolo en Market Watch.
- [symbol_exist](./symbol_exist.md) - Comprobar si existe un símbolo.
- [symbol_info_tick](./symbol_info_tick.md) - Obtener los datos actuales de ticks (requiere que el símbolo esté sincronizado).
- [symbol_info_integer](./symbol_info_integer.md) - Obtener las propiedades enteras del símbolo.