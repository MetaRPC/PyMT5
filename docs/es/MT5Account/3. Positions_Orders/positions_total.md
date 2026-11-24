# Obtener el número total de posiciones abiertas

> **Solicitud:** obtener el número total de posiciones abiertas actualmente en la cuenta de trading.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.positions_total(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.TradeFunctions`
- **Definición Proto:** `PositionsTotal` (definido en `mt5-term-api-trade-functions.proto`)
- **Enums de este método:** 0 enums (solo un recuento simple)

### RPC

- **Servicio:** `mt5_term_api.TradeFunctions`
- **Método:** `PositionsTotal(Empty) -> PositionsTotalReply`
- **Cliente de bajo nivel (generado):** `TradeFunctionsStub.PositionsTotal(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene el número total de posiciones abiertas sin recuperar los datos detallados de cada posición.
- **Por qué lo necesitas.** Permite comprobar rápidamente si hay posiciones abiertas. Es útil para la gestión de riesgos y la lógica de trading.
- **Cuándo utilizarlo.** Utiliza este método cuando solo necesites conocer el número de posiciones. Utiliza `opened_orders()` para obtener todos los detalles de las posiciones.

---

## 🎯 Propósito

Utiliza este método para obtener un recuento sencillo de las posiciones abiertas:

- Comprobar si hay posiciones abiertas.
- Supervisar el número de posiciones antes de realizar nuevas operaciones.
- Implementar límites de posiciones (máximo de posiciones simultáneas).
- Comprobar rápidamente el estado sin cargar todos los datos de las posiciones.
- Operación eficiente: transferencia mínima de datos.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [positions_total - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_total_HOW.md)**

---

## Firma del método

```python
async def positions_total(
    self,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> trade_functions_pb2.PositionsTotalData
```

**Mensaje de solicitud:**

```protobuf
message Empty {
    // No se necesitan parámetros
}
```

**Mensaje de respuesta:**

```protobuf
message PositionsTotalReply {
    oneof response {
        PositionsTotalData data = 1;
        Error error = 2;
    }
}

message PositionsTotalData {
    int32 total_positions = 1;
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `deadline` | `datetime` (opcional) | Fecha límite para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

**No se necesitan parámetros adicionales**: este método devuelve únicamente el número total de posiciones.

**Opciones de plazo límite:**

```python
from datetime import datetime, timedelta, timezone

# 1. Con plazo límite (recomendado)
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
result = await account.positions_total(deadline=deadline)

# 2. Con un evento de cancelación
cancel_event = asyncio.Event()
result = await account.positions_total(cancellation_event=cancel_event)

# 3. Sin plazo límite (utiliza el timeout predeterminado si está configurado)
result = await account.positions_total()
```

---

## ⬆️ Salida - `PositionsTotalData`

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `total_positions` | `int32` | `int` | Número total de posiciones abiertas actualmente |

**Valor devuelto:** el método devuelve un objeto `PositionsTotalData` con el campo `total_positions` accesible como atributo.

**Acceder al recuento:**

```python
data = await account.positions_total()
count = data.total_positions
print(f"Posiciones abiertas: {count}")
```

---

## 🧩 Notas y consejos

- **Reconexión automática:** todos los métodos de `MT5Account` cuentan con protección integrada contra errores gRPC transitorios, con reconexión automática mediante `execute_with_reconnect`.
- **Timeout predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca un timeout del servidor).
- **Ligero:** este método solo devuelve un recuento. Utiliza `opened_orders()` para obtener todos los detalles de las posiciones.
- **Se requiere conexión:** debes llamar a `connect_by_host_port()` o `connect_by_server_name()` antes de utilizar este método.
- **Recuento en tiempo real:** el recuento refleja el estado actual en el momento de realizar la llamada.
- **Seguridad de hilos:** todos los métodos asíncronos se pueden ejecutar simultáneamente de forma segura desde varias tareas de asyncio.
- **Gestión de UUID:** el UUID de la instancia del terminal se genera automáticamente en el servidor si no se proporciona. Para controlarlo explícitamente (por ejemplo, en escenarios de streaming), pasa `id_=uuid4()` al constructor.

---

## 🔗 Ejemplos de uso

### 1) Obtener el número total de posiciones abiertas

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import MT5Account


async def main():
    # Crear una instancia de la cuenta
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    # Conectarse primero
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # Establecer el plazo límite
        deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

        # Obtener el número total de posiciones
        data = await account.positions_total(deadline=deadline)

        print(f"Total de posiciones abiertas: {data.total_positions}")

    finally:
        await account.channel.close()


asyncio.run(main())
```

### 2) Comprobar si hay posiciones abiertas

```python
async def has_open_positions(account: MT5Account) -> bool:
    """
    Comprueba si hay posiciones abiertas.

    Returns:
        True si hay posiciones abiertas
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    data = await account.positions_total(deadline=deadline)

    has_positions = data.total_positions > 0

    if has_positions:
        print(f"[OK] {data.total_positions} posición(es) abierta(s)")
    else:
        print("[OK] No hay posiciones abiertas")

    return has_positions


# Uso:
if await has_open_positions(account):
    print("La cuenta tiene posiciones activas")
else:
    print("La cuenta no tiene posiciones abiertas")
```

### 3) Comprobador del límite de posiciones

```python
async def check_position_limit(account: MT5Account, max_positions: int = 5) -> bool:
    """
    Comprueba si el número actual de posiciones está por debajo del límite.

    Args:
        account: instancia de MT5Account
        max_positions: número máximo permitido de posiciones abiertas

    Returns:
        True si se pueden abrir más posiciones
    """
    data = await account.positions_total()

    current = data.total_positions

    if current >= max_positions:
        print(f"[ADVERTENCIA] Se ha alcanzado el límite de posiciones: {current}/{max_positions}")
        return False

    remaining = max_positions - current
    print(f"[OK] Se pueden abrir {remaining} posición(es) más")
    return True


# Uso:
if await check_position_limit(account, max_positions=5):
    # Colocar una nueva orden
    pass
else:
    print("No se puede abrir una nueva posición: se ha alcanzado el límite")
```

### 4) Supervisar el número de posiciones

```python
async def monitor_positions(account: MT5Account, interval: float = 5.0):
    """
    Supervisa el número de posiciones cada N segundos.

    Args:
        account: instancia de MT5Account
        interval: intervalo de actualización en segundos
    """
    previous_count = None

    while True:
        try:
            deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
            data = await account.positions_total(deadline=deadline)

            count = data.total_positions

            if previous_count is not None and count != previous_count:
                if count > previous_count:
                    print(f"[+] Posición abierta: {count} en total")
                else:
                    print(f"[-] Posición cerrada: {count} en total")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Posiciones: {count}")

            previous_count = count

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)


# Uso:
# await monitor_positions(account, interval=5.0)  # Actualizar cada 5 segundos
```

### 5) Validación previa a la operación

```python
async def validate_can_trade(account: MT5Account, max_positions: int = 10) -> bool:
    """
    Valida si la cuenta puede aceptar nuevas posiciones.

    Args:
        account: instancia de MT5Account
        max_positions: número máximo de posiciones simultáneas permitidas

    Returns:
        True si se permite operar
    """
    # Obtener el número de posiciones
    data = await account.positions_total()
    count = data.total_positions

    # Comprobar el límite de posiciones
    if count >= max_positions:
        print(f"[ERROR] Se ha superado el límite de posiciones: {count}/{max_positions}")
        return False

    print(f"[OK] Posiciones actuales: {count}/{max_positions}")
    return True


# Uso:
if await validate_can_trade(account, max_positions=10):
    # Colocar una orden
    pass
else:
    print("Trading bloqueado: hay demasiadas posiciones")
```

### 6) Esperar a que se cierren todas las posiciones

```python
async def wait_for_all_closed(
    account: MT5Account,
    timeout_seconds: int = 300,
    check_interval: float = 2.0
):
    """
    Espera hasta que se cierren todas las posiciones.

    Args:
        account: instancia de MT5Account
        timeout_seconds: tiempo máximo de espera
        check_interval: frecuencia de las comprobaciones

    Raises:
        TimeoutError: si las posiciones no se cierran dentro del tiempo límite
    """
    import time
    start_time = time.time()

    print("Esperando a que se cierren todas las posiciones...")

    while True:
        # Comprobar el timeout
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            data = await account.positions_total()
            raise TimeoutError(
                f"Timeout: todavía hay {data.total_positions} posición(es) abierta(s) después de {timeout_seconds}s"
            )

        # Obtener el número de posiciones
        data = await account.positions_total()
        count = data.total_positions

        if count == 0:
            print("[OK] Todas las posiciones están cerradas")
            return

        print(f"[INFO] Esperando... todavía hay {count} posición(es) abierta(s)")
        await asyncio.sleep(check_interval)


# Uso:
try:
    await wait_for_all_closed(account, timeout_seconds=300)
except TimeoutError as e:
    print(f"[ERROR] {e}")
```

### 7) Sistema de alertas sobre el número de posiciones

```python
async def position_alert_system(
    account: MT5Account,
    warning_threshold: int = 8,
    critical_threshold: int = 10,
    interval: float = 10.0
):
    """
    Genera una alerta cuando el número de posiciones alcanza determinados umbrales.

    Args:
        account: instancia de MT5Account
        warning_threshold: umbral a partir del cual se muestra una advertencia
        critical_threshold: umbral crítico
        interval: intervalo entre comprobaciones en segundos
    """
    while True:
        try:
            data = await account.positions_total()
            count = data.total_positions

            if count >= critical_threshold:
                print(f"[CRÍTICO] {count} posiciones: ¡se ha alcanzado el límite!")
            elif count >= warning_threshold:
                print(f"[ADVERTENCIA] {count} posiciones: se está alcanzando el límite")
            else:
                print(f"[OK] {count} posiciones")

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)


# Uso:
# await position_alert_system(account, warning_threshold=8, critical_threshold=10)
```

### 8) Comparar el número de posiciones con el objetivo

```python
async def compare_with_target(
    account: MT5Account,
    target_positions: int
) -> dict:
    """
    Compara el número actual de posiciones con el objetivo.

    Args:
        account: instancia de MT5Account
        target_positions: número objetivo de posiciones

    Returns:
        Diccionario con los datos de comparación
    """
    data = await account.positions_total()
    current = data.total_positions

    difference = current - target_positions

    result = {
        "current": current,
        "target": target_positions,
        "difference": difference,
        "status": "exact" if difference == 0 else "above" if difference > 0 else "below"
    }

    if difference == 0:
        print(f"[OK] Exactamente en el objetivo: {current} posiciones")
    elif difference > 0:
        print(f"[INFO] {abs(difference)} por encima del objetivo ({current}/{target_positions})")
    else:
        print(f"[INFO] {abs(difference)} por debajo del objetivo ({current}/{target_positions})")

    return result


# Uso:
result = await compare_with_target(account, target_positions=5)
print(f"Estado: {result['status']}")
```

---

## Patrones comunes

### Comprobación rápida de posiciones

```python
async def is_flat(account: MT5Account) -> bool:
    """Comprueba si la cuenta no tiene posiciones abiertas"""
    data = await account.positions_total()
    return data.total_positions == 0
```

### Protección del límite de posiciones

```python
async def can_open_position(
    account: MT5Account,
    max_concurrent: int = 10
) -> bool:
    """Comprueba si se puede abrir otra posición"""
    data = await account.positions_total()
    return data.total_positions < max_concurrent
```

### Comprobación de riesgos antes de operar

```python
async def pre_trade_risk_check(account: MT5Account) -> bool:
    """Comprobación integral de riesgos antes de operar"""
    data = await account.positions_total()

    # No más de 10 posiciones simultáneas
    if data.total_positions >= 10:
        print("[ERROR] Hay demasiadas posiciones abiertas")
        return False

    print(f"[OK] Comprobación de riesgos superada ({data.total_positions} posiciones)")
    return True
```

---

## 📚 Véase también

- [opened_orders](./opened_orders.md) - Obtener todos los detalles de las órdenes y posiciones abiertas
- [opened_orders_tickets](./opened_orders_tickets.md) - Obtener únicamente los ID de los tickets (más ligero que `opened_orders`)
- [positions_history](./positions_history.md) - Obtener el historial de posiciones cerradas