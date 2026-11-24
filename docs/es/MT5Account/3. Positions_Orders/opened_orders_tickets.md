

# Obtener los identificadores de ticket de las órdenes pendientes y posiciones abiertas

**Solicitud:** obtener los identificadores de ticket de todas las órdenes pendientes y posiciones abiertas actualmente (una alternativa ligera a la obtención de todos los detalles).

**Información de la API:**

- **API de bajo nivel:** `MT5Account.opened_orders_tickets(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.AccountHelper`
- **Definición Proto:** `OpenedOrdersTickets` (definido en `mt5-term-api-account-helper.proto`)

### RPC

- **Servicio:** `mt5_term_api.AccountHelper`
- **Método:** `OpenedOrdersTickets(OpenedOrdersTicketsRequest) -> OpenedOrdersTicketsReply`
- **Cliente de bajo nivel (generado):** `AccountHelperStub.OpenedOrdersTickets(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Permite obtener únicamente los identificadores de ticket de las órdenes pendientes y posiciones abiertas, sin recuperar todos sus detalles.
- **Por qué lo necesitas.** Permite comprobar de forma ligera qué órdenes pendientes y posiciones abiertas existen. Es más eficiente que utilizar `opened_orders()`.
- **Cuándo utilizarlo.** Utiliza este método cuando solo necesites los identificadores de ticket. Para obtener todos los detalles, utiliza `opened_orders()`.

---

## 🎯 Propósito

Utiliza este método para obtener únicamente los identificadores de ticket:

- Comprobar qué órdenes pendientes y posiciones abiertas hay actualmente.
- Guardar los identificadores de ticket para realizar consultas posteriores.
- Supervisar de forma eficiente las órdenes nuevas y cerradas.
- Obtener una respuesta más ligera que con `opened_orders()`.
- Comprobar rápidamente la existencia de una orden o posición antes de solicitar todos sus detalles.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea, con ejemplos, consulta:

**-> [opened_orders_tickets - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_tickets_HOW.md)**

---

## Firma del método

```python
async def opened_orders_tickets(
    self,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.OpenedOrdersTicketsData
```

**Mensaje de solicitud:**

```protobuf
message OpenedOrdersTicketsRequest {
  // Vacío: no se necesitan parámetros
}
```

**Mensaje de respuesta:**

```protobuf
message OpenedOrdersTicketsReply {
  oneof response {
    OpenedOrdersTicketsData data = 1;
    Error error = 2;
  }
}

message OpenedOrdersTicketsData {
  repeated int64 opened_orders_tickets = 1;
  repeated int64 opened_position_tickets = 2;
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `deadline` | `datetime` (opcional) | Fecha límite para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

**No hay parámetros adicionales:** este método devuelve únicamente los identificadores de ticket.

**Opciones de plazo límite:**

```python
from datetime import datetime, timedelta, timezone

# Con deadline
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
data = await account.opened_orders_tickets(deadline=deadline)

# Sin deadline
data = await account.opened_orders_tickets()
```

---

## ⬆️ Salida - `OpenedOrdersTicketsData`

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `opened_orders_tickets` | `repeated int64` | `list[int]` | Lista de identificadores de ticket de las órdenes pendientes |
| `opened_position_tickets` | `repeated int64` | `list[int]` | Lista de identificadores de ticket de las posiciones abiertas |

**Valor de retorno:** el método devuelve un objeto `OpenedOrdersTicketsData` con ambas listas disponibles como atributos.

---

## 🧱 Enums relacionados (de proto)

Este método no utiliza enums.

---

## 🧩 Notas y consejos

- **Reconexión automática:** todos los métodos de `MT5Account` tienen protección integrada contra errores gRPC transitorios.
- **Ligero:** solo se devuelven los identificadores de ticket; el volumen de datos es mucho menor que con `opened_orders()`.
- **Dos listas separadas:** los identificadores de las órdenes y los de las posiciones se devuelven en listas independientes.
- **Conexión obligatoria:** primero debes llamar a `connect_by_host_port()` o `connect_by_server_name()`.
- **Seguridad entre hilos:** es seguro llamar al método simultáneamente desde varias tareas de asyncio.
- **Gestión de UUID:** el UUID de la instancia del terminal se genera automáticamente en el servidor si no se proporciona. Para tener un control explícito (por ejemplo, en escenarios de streaming), pasa `id_=uuid4()` al constructor.

---

## 🔗 Ejemplos de uso

### 1) Obtener todos los identificadores de ticket

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import MT5Account


async def main():
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
        data = await account.opened_orders_tickets(deadline=deadline)

        print(f"Tickets de órdenes: {data.opened_orders_tickets}")
        print(f"Tickets de posiciones: {data.opened_position_tickets}")

    finally:
        await account.channel.close()


asyncio.run(main())
```

### 2) Comprobar si existe un ticket

```python
async def ticket_exists(account: MT5Account, ticket: int) -> bool:
    """Comprueba si el identificador de ticket existe entre las órdenes o posiciones abiertas"""
    data = await account.opened_orders_tickets()

    exists = (
        ticket in data.opened_orders_tickets or
        ticket in data.opened_position_tickets
    )

    if exists:
        print(f"[OK] Ticket #{ticket} encontrado")
    else:
        print(f"[INFO] Ticket #{ticket} no encontrado")

    return exists


# Uso:
if await ticket_exists(account, 123456):
    print("La orden/posición sigue abierta")
```

### 3) Supervisar los cambios en los tickets

```python
async def monitor_tickets(account: MT5Account, interval: float = 5.0):
    """Supervisa los cambios en los identificadores de ticket"""
    previous_tickets = set()

    while True:
        try:
            data = await account.opened_orders_tickets()

            current_tickets = set(data.opened_orders_tickets + data.opened_position_tickets)

            if previous_tickets:
                new = current_tickets - previous_tickets
                closed = previous_tickets - current_tickets

                for ticket in new:
                    print(f"[+] Nuevo ticket: #{ticket}")
                for ticket in closed:
                    print(f"[-] Ticket cerrado: #{ticket}")

            previous_tickets = current_tickets

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)


# Uso:
# await monitor_tickets(account, interval=5.0)
```

### 4) Obtener todos los tickets combinados

```python
async def get_all_tickets(account: MT5Account) -> list[int]:
    """Obtiene conjuntamente todos los tickets de órdenes pendientes y posiciones abiertas"""
    data = await account.opened_orders_tickets()

    all_tickets = list(data.opened_orders_tickets) + list(data.opened_position_tickets)

    print(f"[OK] Número total de tickets: {len(all_tickets)}")
    return all_tickets


# Uso:
tickets = await get_all_tickets(account)
print(f"Todos los tickets: {tickets}")
```

### 5) Comparar con una instantánea anterior

```python
async def compare_tickets(
    account: MT5Account,
    previous_orders: list[int],
    previous_positions: list[int]
) -> dict:
    """Compara los tickets actuales con una instantánea anterior"""
    data = await account.opened_orders_tickets()

    result = {
        "new_orders": list(set(data.opened_orders_tickets) - set(previous_orders)),
        "closed_orders": list(set(previous_orders) - set(data.opened_orders_tickets)),
        "new_positions": list(set(data.opened_position_tickets) - set(previous_positions)),
        "closed_positions": list(set(previous_positions) - set(data.opened_position_tickets))
    }

    if result["new_orders"]:
        print(f"[+] Órdenes nuevas: {result['new_orders']}")
    if result["closed_orders"]:
        print(f"[-] Órdenes cerradas: {result['closed_orders']}")
    if result["new_positions"]:
        print(f"[+] Posiciones nuevas: {result['new_positions']}")
    if result["closed_positions"]:
        print(f"[-] Posiciones cerradas: {result['closed_positions']}")

    return result


# Uso:
# prev_orders = [12345, 12346]
# prev_positions = [12347]
# changes = await compare_tickets(account, prev_orders, prev_positions)
```

---

## Patrones habituales

### Comprobación rápida del número de tickets

```python
async def get_tickets_count(account: MT5Account) -> dict:
    """Obtiene el número de órdenes pendientes y posiciones abiertas"""
    data = await account.opened_orders_tickets()
    return {
        "orders": len(data.opened_orders_tickets),
        "positions": len(data.opened_position_tickets),
        "total": len(data.opened_orders_tickets) + len(data.opened_position_tickets)
    }
```

### Operaciones con conjuntos de tickets

```python
async def get_ticket_sets(account: MT5Account) -> tuple:
    """Obtiene los identificadores de ticket como conjuntos para facilitar su comparación"""
    data = await account.opened_orders_tickets()
    return (
        set(data.opened_orders_tickets),
        set(data.opened_position_tickets)
    )
```

---

## 📚 Véase también

- [opened_orders](./opened_orders.md) - Obtener todos los detalles de las órdenes pendientes y posiciones abiertas.
- [positions_total](./positions_total.md) - Obtener únicamente el recuento (una opción aún más ligera).
- [positions_history](./positions_history.md) - Obtener el historial de posiciones cerradas.

