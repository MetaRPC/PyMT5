# Cerrar una posición o una orden

> **Solicitud:** Cerrar una posición de mercado o eliminar una orden pendiente.

**Información de la API:**

- **API de Python:** `MT5Account.order_close(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.TradingHelper`
- **Definición Proto:** `OrderClose` (definido en `mt5-term-api-trading-helper.proto`)
- **Enums de este método:** 1 enum con 3 constantes (1 salida)

### RPC

- **Servicio:** `mt5_term_api.TradingHelper`
- **Método:** `OrderClose(OrderCloseRequest) -> OrderCloseReply`
- **Cliente de bajo nivel (generado):** `TradingHelperStub.OrderClose(request, metadata)`

## 💬 Lo esencial

- **Qué es:** Cierra posiciones de mercado o elimina órdenes pendientes.
- **Para qué sirve:** Salir de posiciones o cancelar órdenes pendientes.
- **Cierre parcial:** Establece un volumen inferior al volumen de la posición para cerrarla parcialmente, o 0 para cerrarla por completo.

---

## 🎯 Propósito

Utiliza este método para:

- Cerrar posiciones de mercado total o parcialmente.
- Eliminar órdenes pendientes.
- Salir rápidamente de posiciones con pérdidas.
- Asegurar beneficios en posiciones ganadoras.
- Cancelar órdenes pendientes que todavía no se han ejecutado.

```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


class MT5Account:
    # ...

    async def order_close(
        self,
        request: trading_pb2.OrderCloseRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Cierra una orden de mercado o pendiente de forma asíncrona.

        Returns:
            OrderCloseData: El resultado del cierre y los códigos de retorno.
        """
```

**Mensaje de solicitud:**

```protobuf
OrderCloseRequest {
  uint64 ticket = 1;      // Ticket de la orden/posición que se va a cerrar
  double volume = 2;      // Volumen que se va a cerrar (0 = cerrar todo)
  int32 slippage = 5;     // Deslizamiento máximo en puntos
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `request` | `OrderCloseRequest` | Solicitud de cierre (véanse los campos anteriores) |
| `deadline` | `Optional[datetime]` | Límite de tiempo para la operación (opcional) |
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la solicitud (opcional) |

---

## ⬆️ Salida

Devuelve un objeto `OrderCloseData`.

**Campos de OrderCloseData:**

| Campo | Tipo | Descripción |
|---|---|---|
| `returned_code` | `int32` | Código de retorno (10009 = éxito) |
| `returned_string_code` | `string` | Código de retorno en formato de cadena |
| `returned_code_description` | `string` | Descripción del código de retorno |
| `close_mode` | `int32` | Modo de cierre utilizado |

---

## 🧱 Enums relacionados (de proto)

### `MRPC_ORDER_CLOSE_MODE`

Se utiliza en `OrderCloseData` para indicar el modo de cierre.

| Nombre de la constante | Valor | Descripción |
|---|---:|---|
| `MRPC_MARKET_ORDER_CLOSE` | 0 | Cierre completo de la posición |
| `MRPC_MARKET_ORDER_PARTIAL_CLOSE` | 1 | Cierre parcial de la posición |
| `MRPC_PENDING_ORDER_REMOVE` | 2 | Eliminación de una orden pendiente |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Acceder a los valores del enum
trading_pb2.MRPC_MARKET_ORDER_CLOSE          # = 0
trading_pb2.MRPC_MARKET_ORDER_PARTIAL_CLOSE  # = 1
trading_pb2.MRPC_PENDING_ORDER_REMOVE        # = 2
```

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**[OrderClose - Cómo funciona](../HOW_IT_WORK/5. Trading_Operations_HOW/order_close_HOW.md)**

---

## 🧩 Notas y consejos

- **Reconexión automática:** Todos los métodos de `MT5Account` incluyen protección integrada contra errores gRPC transitorios, con reconexión automática mediante `execute_with_reconnect`.
- **Código de retorno:** Comprueba siempre `returned_code == 10009` para verificar que la operación se ha realizado correctamente.
- **Cerrar todo:** Establece `volume = 0` para cerrar la posición completa.
- **Cierre parcial:** Establece `volume` en una cantidad específica para cerrar parcialmente la posición.
- **Deslizamiento:** Establece un valor de deslizamiento adecuado para las posiciones de mercado, permitiendo movimientos del precio.
- **Órdenes pendientes:** El deslizamiento se ignora al cerrar órdenes pendientes.
- **Número de ticket:** Obtén el ticket de `opened_orders` o guárdalo cuando abras las posiciones.

---

## 🔗 Ejemplos de uso

### 1) Cerrar una posición por completo

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


async def close_position():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # Cerrar la posición con el ticket 123456
        request = trading_pb2.OrderCloseRequest(
            ticket=123456,
            volume=0,  # 0 = cerrar todo
            slippage=20  # Deslizamiento máximo de 20 puntos
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[ÉXITO] ¡Posición cerrada!")
            print(f"  Modo: {result.close_mode}")
        else:
            print(f"[ERROR] Código: {result.returned_code}")
            print(f"  Descripción: {result.returned_code_description}")

    finally:
        await account.channel.close()


asyncio.run(close_position())
```

### 2) Cerrar todas las posiciones abiertas

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2


async def close_all_positions():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # Obtener todas las posiciones abiertas
        request = account_pb2.OpenedOrdersRequest()
        positions_data = await account.opened_orders(request)

        closed_count = 0
        failed_count = 0

        # Cerrar cada posición
        for position in positions_data.positions:
            close_req = trading_pb2.OrderCloseRequest(
                ticket=position.ticket,
                volume=0,  # Cerrar todo
                slippage=20
            )

            result = await account.order_close(close_req)

            if result.returned_code == 10009:
                closed_count += 1
                print(f"[CERRADA] Posición #{position.ticket}")
            else:
                failed_count += 1
                print(f"[ERROR] Posición #{position.ticket}: "
                      f"{result.returned_code_description}")

        print(f"\n[RESUMEN] Cerradas: {closed_count}, Fallidas: {failed_count}")

    finally:
        await account.channel.close()


asyncio.run(close_all_positions())
```

### 3) Cierre parcial de una posición

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


async def partial_close():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # Cerrar la mitad de una posición de 0.10 lotes
        request = trading_pb2.OrderCloseRequest(
            ticket=123456,
            volume=0.05,  # Cerrar 0.05 lotes
            slippage=20
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[ÉXITO] ¡Cierre parcial ejecutado!")
            print(f"  Volumen cerrado: 0.05 lotes")
            print(f"  Volumen restante: 0.05 lotes")
        else:
            print(f"[ERROR] {result.returned_code_description}")

    finally:
        await account.channel.close()


asyncio.run(partial_close())
```

### 4) Eliminar una orden pendiente

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


async def delete_pending_order():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # Eliminar una orden pendiente
        request = trading_pb2.OrderCloseRequest(
            ticket=789012,
            volume=0,
            slippage=0  # El deslizamiento no se utiliza para órdenes pendientes
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[ÉXITO] ¡Orden pendiente eliminada!")
        else:
            print(f"[ERROR] {result.returned_code_description}")

    finally:
        await account.channel.close()


asyncio.run(delete_pending_order())
```

### 5) Cerrar posiciones por símbolo

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2


async def close_by_symbol(symbol: str):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # Obtener todas las posiciones abiertas
        request = account_pb2.OpenedOrdersRequest()
        positions_data = await account.opened_orders(request)

        closed = []
        failed = []

        # Cerrar las posiciones de un símbolo específico
        for position in positions_data.positions:
            if position.symbol == symbol:
                close_req = trading_pb2.OrderCloseRequest(
                    ticket=position.ticket,
                    volume=0,
                    slippage=20
                )

                result = await account.order_close(close_req)

                if result.returned_code == 10009:
                    closed.append(position.ticket)
                    print(f"[CERRADA] Posición {symbol} #{position.ticket}")
                else:
                    failed.append(position.ticket)
                    print(f"[ERROR] #{position.ticket}: "
                          f"{result.returned_code_description}")

        print(f"\n[{symbol}] Cerradas: {len(closed)}, Fallidas: {len(failed)}")

    finally:
        await account.channel.close()


# Cerrar todas las posiciones de EURUSD
asyncio.run(close_by_symbol("EURUSD"))
```

### 6) Cerrar con reintentos y gestión de errores

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


async def close_with_retry(ticket: int, max_retries=3):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        for attempt in range(1, max_retries + 1):
            print(f"[INTENTO {attempt}/{max_retries}]")

            request = trading_pb2.OrderCloseRequest(
                ticket=ticket,
                volume=0,
                slippage=30  # Permitir un mayor deslizamiento en los reintentos
            )

            try:
                result = await account.order_close(request)

                if result.returned_code == 10009:
                    print(f"[ÉXITO] ¡Posición cerrada en el intento {attempt}!")
                    return True
                else:
                    print(f"[ERROR] Código: {result.returned_code}")
                    print(f"  Descripción: {result.returned_code_description}")

                    if attempt < max_retries:
                        print(f"  Reintentando en 1 segundo...")
                        await asyncio.sleep(1)

            except Exception as e:
                print(f"[ERROR] {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1)

        print(f"[ABANDONADO] No se pudo cerrar la posición después de {max_retries} intentos")
        return False

    finally:
        await account.channel.close()


asyncio.run(close_with_retry(123456))
```

---

## 📚 Véase también

- [OrderSend](./order_send.md) - Abrir posiciones.
- [OrderModify](./order_modify.md) - Modificar posiciones/órdenes.
- [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Obtener posiciones abiertas.