

# Obtener el número total de símbolos

**Solicitud:** obtener el número total de símbolos disponibles en la plataforma de trading.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbols_total(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolsTotal` (definido en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolsTotal(SymbolsTotalRequest) -> SymbolsTotalReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolsTotal(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Permite obtener el número total de símbolos disponibles en la plataforma.
- **Por qué lo necesitas.** Permite comprobar cuántos símbolos están disponibles: todos los símbolos o únicamente los que aparecen en Market Watch.
- **Cuándo utilizarlo.** Para obtener rápidamente el número de símbolos. Para recorrer los símbolos, es preferible utilizar `symbol_params_many()` (una sola llamada) en lugar de realizar múltiples llamadas a `symbol_name()`.

---

## 🎯 Propósito

Utiliza este método para obtener el número de símbolos:

- Comprobar el número total de símbolos de la plataforma.
- Contar los símbolos de Market Watch.
- Validar la disponibilidad de símbolos.
- Realizar una comprobación rápida antes de recorrer los símbolos.
- Supervisar los cambios en la lista de símbolos.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea, con ejemplos, consulta:

**-> [symbols_total - Cómo funciona](../HOW_IT_WORK/2. Symbol_information_HOW/symbols_total_HOW.md)**

---

## Firma del método

```python
async def symbols_total(
    self,
    selected_only: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolsTotalData
```

**Mensaje de solicitud:**

```protobuf
message SymbolsTotalRequest {
  bool mode = 1;
}
```

**Mensaje de respuesta:**

```protobuf
message SymbolsTotalReply {
  oneof response {
    SymbolsTotalData data = 1;
    Error error = 2;
  }
}

message SymbolsTotalData {
  int32 total = 1;
}
```

**Correspondencia de parámetros:**

- El parámetro de Python `selected_only` corresponde al campo protobuf `mode`.

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `selected_only` | `bool` (obligatorio) | `True` = contar únicamente los símbolos de Market Watch; `False` = contar todos los símbolos |
| `deadline` | `datetime` (opcional) | Fecha límite para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

**Uso:**

```python
from datetime import datetime, timedelta

# Contar todos los símbolos
data = await account.symbols_total(selected_only=False)

# Contar únicamente los símbolos de Market Watch
data = await account.symbols_total(selected_only=True)
```

---

## ⬆️ Salida - `SymbolsTotalData`

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `total` | `int32` | `int` | Número total de símbolos |

**Valor de retorno:** el método devuelve un objeto `SymbolsTotalData` con el campo `total`.

---

## 🧱 Enums relacionados (de proto)

Este método no utiliza enums.

---

## 🧩 Notas y consejos

- **Reconexión automática:** protección integrada contra errores gRPC transitorios.
- **Market Watch frente a todos los símbolos:** `selected_only=True` cuenta únicamente los símbolos visibles en Market Watch; `False` cuenta todos los símbolos disponibles.
- **Conexión obligatoria:** primero debes llamar a `connect_by_host_port()` o `connect_by_server_name()`.
- **Seguridad entre hilos:** es seguro llamar al método simultáneamente desde varias tareas de asyncio.
- **Rendimiento:** es una llamada ligera; puedes utilizarla libremente para realizar validaciones antes de las operaciones.
- **Tipo de retorno:** el método devuelve un objeto protobuf `SymbolsTotalData` (el tipo Python coincide con los tipos de sus campos).

---

## 🔗 Ejemplos de uso

### 1) Obtener el número total de símbolos

```python
import asyncio
from datetime import datetime, timedelta
from MetaRpcMT5.mt5_account import MT5Account


async def main():
    account = MT5Account(
        account_number=12345678,
        password="your_password",
        host="your-server.com:443"
    )

    await account.connect_by_server_name("MetaQuotes-Demo")

    try:
        # Contar todos los símbolos
        data_all = await account.symbols_total(selected_only=False)
        print(f"Total de símbolos disponibles: {data_all.total}")

        # Contar los símbolos de Market Watch
        data_mw = await account.symbols_total(selected_only=True)
        print(f"Símbolos de Market Watch: {data_mw.total}")

    finally:
        await account.channel.close()


asyncio.run(main())
```

### 2) Comparar Market Watch con todos los símbolos

```python
async def compare_symbol_counts(account: MT5Account):
    """Compara Market Watch con todos los símbolos disponibles"""
    # Obtener los recuentos
    all_symbols = await account.symbols_total(selected_only=False)
    mw_symbols = await account.symbols_total(selected_only=True)

    print(f"\nEstadísticas de símbolos:")
    print(f"  Todos los disponibles: {all_symbols.total}")
    print(f"  Market Watch: {mw_symbols.total}")
    print(f"  Fuera de Market Watch: {all_symbols.total - mw_symbols.total}")

    return {
        "all": all_symbols.total,
        "market_watch": mw_symbols.total,
        "hidden": all_symbols.total - mw_symbols.total
    }


# Uso:
stats = await compare_symbol_counts(account)
```

### 3) Comprobar si hay símbolos disponibles

```python
async def has_symbols(account: MT5Account) -> bool:
    """Comprueba si hay símbolos disponibles"""
    data = await account.symbols_total(selected_only=False)

    if data.total > 0:
        print(f"[OK] {data.total} símbolos disponibles")
        return True
    else:
        print("[ADVERTENCIA] No hay símbolos disponibles")
        return False


# Uso:
if await has_symbols(account):
    print("Listo para operar")
```

### 4) Supervisar los cambios en el número de símbolos

```python
async def monitor_symbol_count(account: MT5Account, interval: float = 60.0):
    """Supervisa los cambios en el número de símbolos"""
    previous_count = None

    while True:
        try:
            data = await account.symbols_total(selected_only=True)
            count = data.total

            if previous_count is not None and count != previous_count:
                if count > previous_count:
                    print(f"[+] Símbolo añadido a Market Watch: {count} en total")
                else:
                    print(f"[-] Símbolo eliminado de Market Watch: {count} en total")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Market Watch: {count} símbolos")

            previous_count = count

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)


# Uso:
# await monitor_symbol_count(account, interval=60.0)
```

### 5) Validar antes de recorrer los símbolos

```python
async def iterate_symbols_safe(account: MT5Account):
    """Recorre los símbolos de forma segura con validación"""
    # Comprobar primero el número de símbolos
    data = await account.symbols_total(selected_only=True)

    if data.total == 0:
        print("[ADVERTENCIA] No hay símbolos en Market Watch")
        return []

    print(f"[OK] Se encontraron {data.total} símbolos")

    # Ahora es seguro recorrerlos
    symbols = []
    for i in range(data.total):
        symbol_name = await account.symbol_name(index=i, selected=True)
        symbols.append(symbol_name.name)

    return symbols


# Uso:
symbols = await iterate_symbols_safe(account)
print(f"Símbolos: {symbols}")
```

### 6) Calcular el uso de Market Watch

```python
async def calculate_mw_usage(account: MT5Account) -> dict:
    """Calcula las estadísticas de uso de Market Watch"""
    all_data = await account.symbols_total(selected_only=False)
    mw_data = await account.symbols_total(selected_only=True)

    total = all_data.total
    used = mw_data.total
    usage_pct = (used / total * 100) if total > 0 else 0

    result = {
        "total_available": total,
        "in_market_watch": used,
        "usage_percent": usage_pct
    }

    print(f"\nUso de Market Watch:")
    print(f"  Se utilizan {used} de {total} símbolos ({usage_pct:.1f}%)")

    return result


# Uso:
usage = await calculate_mw_usage(account)
```

### 7) Esperar a que se carguen los símbolos

```python
async def wait_for_symbols(
    account: MT5Account,
    min_symbols: int = 1,
    timeout_seconds: int = 30,
    check_interval: float = 1.0
):
    """Espera hasta que esté disponible el número mínimo de símbolos"""
    import time
    start_time = time.time()

    print(f"Esperando al menos {min_symbols} símbolo(s)...")

    while True:
        # Comprobar el tiempo de espera
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Tiempo de espera agotado: los símbolos no se cargaron después de {timeout_seconds}s")

        # Comprobar el número de símbolos
        data = await account.symbols_total(selected_only=False)
        count = data.total

        if count >= min_symbols:
            print(f"[OK] Se cargaron {count} símbolos")
            return count

        print(f"[INFO] Esperando... ({count} símbolos)")
        await asyncio.sleep(check_interval)


# Uso:
try:
    count = await wait_for_symbols(account, min_symbols=10)
except TimeoutError as e:
    print(f"[ERROR] {e}")
```

### 8) Registrar las estadísticas de símbolos en el log

```python
import logging


async def log_symbol_statistics(account: MT5Account):
    """Registra estadísticas completas de los símbolos"""
    logging.basicConfig(level=logging.INFO)

    all_data = await account.symbols_total(selected_only=False)
    mw_data = await account.symbols_total(selected_only=True)

    logging.info("=" * 60)
    logging.info("ESTADÍSTICAS DE SÍMBOLOS")
    logging.info("=" * 60)
    logging.info(f"Total de símbolos disponibles: {all_data.total}")
    logging.info(f"Símbolos de Market Watch: {mw_data.total}")
    logging.info(f"Símbolos ocultos: {all_data.total - mw_data.total}")
    logging.info("=" * 60)


# Uso:
await log_symbol_statistics(account)
```

---

## Patrones habituales

### Comprobación rápida del número de símbolos

```python
async def get_mw_symbol_count(account: MT5Account) -> int:
    """Obtiene el número de símbolos de Market Watch"""
    data = await account.symbols_total(selected_only=True)
    return data.total
```

### Validar que los símbolos se han cargado

```python
async def symbols_loaded(account: MT5Account) -> bool:
    """Comprueba si los símbolos se han cargado"""
    data = await account.symbols_total(selected_only=False)
    return data.total > 0
```

---

## 📚 Véase también

- [symbol_params_many](./symbol_params_many.md) - Obtener parámetros completos de todos los símbolos (RECOMENDADO para recorrerlos).
- [symbol_name](./symbol_name.md) - Obtener el nombre del símbolo por índice.
- [symbol_exist](./symbol_exist.md) - Comprobar si existe un símbolo específico.
- [symbol_select](./symbol_select.md) - Añadir o eliminar un símbolo de Market Watch.

