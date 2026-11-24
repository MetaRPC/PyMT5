

# Añadir o eliminar un símbolo de Market Watch

**Solicitud:** añadir o eliminar un símbolo de la ventana Market Watch para que esté disponible para operar y para las suscripciones de datos.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_select(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolSelect` (definido en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolSelect(SymbolSelectRequest) -> SymbolSelectReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolSelect(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Permite añadir o eliminar un símbolo de la ventana Market Watch (hace que el símbolo esté disponible o no esté disponible para operar y para las suscripciones).
- **Por qué lo necesitas.** Es necesario antes de operar o suscribirse a los datos de un símbolo: MT5 solo permite realizar operaciones con símbolos que están en Market Watch.
- **Cuándo utilizarlo.** Antes de realizar cualquier operación de trading o suscribirse a los datos de un símbolo; también al limpiar los símbolos que ya no se utilizan.

---

## 🎯 Propósito

Utiliza este método para administrar Market Watch:

- Añadir un símbolo a Market Watch antes de operar.
- Habilitar un símbolo para las suscripciones de cotizaciones.
- Eliminar los símbolos que no se utilizan para reducir la carga.
- Preparar el entorno de trading mediante programación.
- Limpiar Market Watch después de una sesión de trading.
- Verificar la disponibilidad de un símbolo para realizar operaciones.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea, con ejemplos, consulta:

**-> [symbol_select - Cómo funciona](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_select_HOW.md)**

---

## Firma del método

```python
async def symbol_select(
    self,
    symbol: str,
    select: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolSelectData
```

**Mensaje de solicitud:**

```protobuf
message SymbolSelectRequest {
  string symbol = 1;
  bool select = 2;
}
```

**Mensaje de respuesta:**

```protobuf
message SymbolSelectReply {
  oneof response {
    SymbolSelectData data = 1;
    Error error = 2;
  }
}

message SymbolSelectData {
  bool success = 1;
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `symbol` | `str` (obligatorio) | Nombre del símbolo (por ejemplo, "EURUSD", "BTCUSD") |
| `select` | `bool` (obligatorio) | `True` = añadir a Market Watch, `False` = eliminar |
| `deadline` | `datetime` (opcional) | Fecha límite para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

---

## ⬆️ Salida

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `success` | `bool` | `bool` | `True` si la operación se realizó correctamente; `False` si falló |

**Valor de retorno:** el método devuelve un objeto `SymbolSelectData` con el estado de éxito de la operación.

---

## 🧱 Enums relacionados

Este método no utiliza enums.

---

## 🧩 Notas y consejos

- **Necesario antes de operar:** el símbolo DEBE estar en Market Watch antes de poder operar con él o suscribirse a sus datos.
- **Operación idempotente:** añadir un símbolo que ya está seleccionado o eliminar uno que ya se ha eliminado devuelve éxito.
- **Símbolos inexistentes:** seleccionar un símbolo que no existe devuelve `success=False`.
- **Administración de Market Watch:** utiliza este método para administrar mediante programación los símbolos visibles en MT5.
- **Rendimiento:** eliminar de Market Watch los símbolos que no se utilizan puede mejorar el rendimiento y reducir el tráfico de red.
- **Grupos de símbolos:** algunos brókeres organizan los símbolos en grupos. Asegúrate de utilizar el nombre exacto, incluidos los sufijos.
- **Distingue entre mayúsculas y minúsculas:** los nombres de los símbolos distinguen entre mayúsculas y minúsculas (normalmente se escriben en mayúsculas).
- **Indicador de éxito:** comprueba siempre `data.success` para verificar que la operación se ha completado correctamente.

---

## 🔗 Ejemplos de uso

### 1) Añadir un símbolo a Market Watch (RECOMENDADO)

```python
from MetaRpcMT5.mt5_account import MT5Account


async def add_to_market_watch(account: MT5Account, symbol: str):
    """Añade un símbolo a Market Watch antes de operar"""

    # Añadir el símbolo
    data = await account.symbol_select(symbol=symbol, select=True)

    if data.success:
        print(f"{symbol} añadido a Market Watch")
        return True
    else:
        print(f"No se pudo añadir {symbol} a Market Watch")
        return False


# Uso
success = await add_to_market_watch(account, "EURUSD")
```

### 2) Eliminar un símbolo de Market Watch

```python
async def remove_from_market_watch(account: MT5Account, symbol: str):
    """Elimina un símbolo de Market Watch para realizar una limpieza"""

    # Eliminar el símbolo
    data = await account.symbol_select(symbol=symbol, select=False)

    if data.success:
        print(f"{symbol} eliminado de Market Watch")
        return True
    else:
        print(f"No se pudo eliminar {symbol}")
        return False


# Uso
await remove_from_market_watch(account, "GBPJPY")
```

### 3) Añadir varios símbolos con gestión de errores

```python
async def add_symbols_batch(account: MT5Account, symbols: list[str]):
    """Añade varios símbolos a Market Watch"""

    results = {'added': [], 'failed': []}

    for symbol in symbols:
        data = await account.symbol_select(symbol=symbol, select=True)

        if data.success:
            results['added'].append(symbol)
            print(f"{symbol}")
        else:
            results['failed'].append(symbol)
            print(f"{symbol}")

    print(f"\nAñadidos: {len(results['added'])}, Fallidos: {len(results['failed'])}")
    return results


# Uso
symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
results = await add_symbols_batch(account, symbols)
```

### 4) Configurar el entorno de trading

```python
async def setup_trading_symbols(account: MT5Account):
    """Configura los símbolos antes de la sesión de trading"""

    # Definir los símbolos necesarios
    required_symbols = [
        "EURUSD", "GBPUSD", "USDJPY",
        "AUDUSD", "USDCAD", "NZDUSD"
    ]

    print("Configurando el entorno de trading...")

    for symbol in required_symbols:
        data = await account.symbol_select(symbol=symbol, select=True)

        if data.success:
            print(f"  {symbol} listo")
        else:
            print(f"  {symbol} ERROR - comprueba el nombre del símbolo")
            return False

    print("¡Todos los símbolos están listos para operar!")
    return True


# Uso
if await setup_trading_symbols(account):
    print("Iniciando la estrategia de trading...")
```

### 5) Limpiar los símbolos que no se utilizan

```python
async def cleanup_market_watch(account: MT5Account, keep_symbols: list[str]):
    """Elimina todos los símbolos excepto los especificados"""

    # Obtener todos los símbolos que están actualmente en Market Watch

    # Obtener el número total de símbolos
    total_data = await account.symbols_total(selected_only=True)
    total = total_data.total

    removed = []
    # Primero recopila todos los nombres: al eliminar, los índices se desplazan,
    # así que no elimines mientras recorres la lista por índice.
    symbols = []
    for i in range(total):
        name_data = await account.symbol_name(index=i, selected=True)
        symbols.append(name_data.name)

    # Después elimina en un bucle aparte los que no están en la lista de conservación
    for symbol in symbols:
        if symbol not in keep_symbols:
            data = await account.symbol_select(symbol=symbol, select=False)
            if data.success:
                removed.append(symbol)
                print(f"Eliminado: {symbol}")

    print(f"\nSe eliminaron {len(removed)} símbolos de Market Watch")
    return removed


# Uso
keep = ["EURUSD", "GBPUSD", "USDJPY"]
await cleanup_market_watch(account, keep)
```

### 6) Verificar la selección de un símbolo con tiempo de espera

```python
from datetime import datetime, timedelta, timezone


async def select_symbol_with_timeout(
    account: MT5Account,
    symbol: str,
    select: bool,
    timeout_seconds: int = 5
):
    """Selecciona un símbolo con un tiempo de espera"""

    # Calcular la fecha límite
    deadline = datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)

    try:
        data = await account.symbol_select(
            symbol=symbol,
            select=select,
            deadline=deadline
        )

        action = "añadido a" if select else "eliminado de"
        verb = "añadir" if select else "eliminar"
        if data.success:
            print(f"{symbol} {action} Market Watch")
        else:
            print(f"No se pudo {verb} {symbol}")

        return data.success

    except Exception as e:
        print(f"Tiempo de espera agotado o error al seleccionar {symbol}: {e}")
        return False


# Uso
success = await select_symbol_with_timeout(account, "EURUSD", True, timeout_seconds=3)
```

### 7) Preparar los símbolos para una estrategia

```python
async def prepare_symbols_for_strategy(
    account: MT5Account,
    strategy_symbols: dict[str, bool]
):
    """
    Prepara Market Watch para la estrategia de trading

    Args:
        strategy_symbols: Diccionario de {symbol: should_select}
    """

    print("Configurando Market Watch para la estrategia...")

    success_count = 0
    fail_count = 0

    for symbol, should_select in strategy_symbols.items():
        action = "Añadiendo" if should_select else "Eliminando"

        data = await account.symbol_select(
            symbol=symbol,
            select=should_select
        )

        if data.success:
            status = "[OK]"
            success_count += 1
        else:
            status = "[FAIL]"
            fail_count += 1

        action_word = "a" if should_select else "de"
        print(f"{status} {action} {symbol} {action_word} Market Watch")

    print(f"\nResultados: {success_count} operaciones correctas, {fail_count} fallidas")

    if fail_count > 0:
        print("ADVERTENCIA: algunos símbolos no se pudieron procesar; comprueba sus nombres")
        return False

    return True


# Uso
strategy_config = {
    "EURUSD": True,   # Añadir
    "GBPUSD": True,   # Añadir
    "USDJPY": True,   # Añadir
    "XAUUSD": False,  # Eliminar
    "BTCUSD": False   # Eliminar
}

if await prepare_symbols_for_strategy(account, strategy_config):
    print("¡Market Watch se ha configurado correctamente!")
```

---

## 📚 Véase también

- [symbol_exist](./symbol_exist.md) - Comprobar si el símbolo existe en el servidor.
- [symbol_name](./symbol_name.md) - Obtener el nombre del símbolo por índice.
- [symbols_total](./symbols_total.md) - Obtener el número total de símbolos.
- [symbol_info_tick](./symbol_info_tick.md) - Obtener los datos de ticks del símbolo (requiere que el símbolo esté seleccionado previamente).

