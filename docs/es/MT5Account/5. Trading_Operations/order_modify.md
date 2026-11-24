# Modificar una orden o posición

> **Solicitud:** Modificar el Stop Loss, Take Profit, precio o vencimiento de una orden/posición.

**Información de la API:**

- **API de Python:** `MT5Account.order_modify(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.TradingHelper`
- **Definición Proto:** `OrderModify` (definido en `mt5-term-api-trading-helper.proto`)
- **Enums de este método:** 1 enum con 4 constantes (1 entrada)

### RPC

- **Servicio:** `mt5_term_api.TradingHelper`
- **Método:** `OrderModify(OrderModifyRequest) -> OrderModifyReply`
- **Cliente de bajo nivel (generado):** `TradingHelperStub.OrderModify(request, metadata)`

## 💬 Lo esencial

- **Qué es:** Modifica el SL/TP, el precio o el vencimiento de órdenes/posiciones existentes.
- **Para qué sirve:** Ajustar los niveles de gestión del riesgo o los parámetros de las órdenes pendientes.
- **Establecer en cero:** Utiliza 0 para eliminar el SL o el TP.

---

## 🎯 Propósito

Utiliza este método para:

- Añadir o modificar niveles de Stop Loss.
- Añadir o modificar niveles de Take Profit.
- Cambiar los precios de las órdenes pendientes.
- Actualizar los tiempos de vencimiento de las órdenes.
- Ajustar los trailing stops.
- Eliminar el SL/TP (establecerlo en 0).

```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


class MT5Account:
    # ...

    async def order_modify(
        self,
        request: trading_pb2.OrderModifyRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Modifica una orden o posición existente de forma asíncrona.

        Returns:
            OrderModifyData: Respuesta que contiene información actualizada de la orden/operación.
        """
```

**Mensaje de solicitud:**

```protobuf
OrderModifyRequest {
  uint64 ticket = 1;                              // Ticket de la orden/posición que se va a modificar
  double stop_loss = 2;                           // Nuevo precio de Stop Loss (0 = eliminar)
  double take_profit = 3;                         // Nuevo precio de Take Profit (0 = eliminar)
  double price = 4;                               // Nuevo precio (para órdenes pendientes)
  TMT5_ENUM_ORDER_TYPE_TIME expiration_time_type = 5;  // Nuevo tipo de vencimiento
  google.protobuf.Timestamp expiration_time = 6;       // Nueva fecha y hora de vencimiento
  double stop_limit = 8;                          // Nuevo precio Stop Limit
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `request` | `OrderModifyRequest` | Solicitud de modificación (véanse los campos anteriores) |
| `deadline` | `Optional[datetime]` | Límite de tiempo para la operación (opcional) |
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la solicitud (opcional) |

---

## ⬆️ Salida

Devuelve un objeto `OrderModifyData`.

**Campos de OrderModifyData:**

| Campo | Tipo | Descripción |
|---|---|---|
| `returned_code` | `int32` | Código de retorno (10009 = éxito) |
| `returned_string_code` | `string` | Código de retorno en formato de cadena |
| `returned_code_description` | `string` | Descripción del código de retorno |
| `deal` | `uint64` | Ticket de la operación (si se ejecutó) |
| `order` | `uint64` | Ticket de la orden |
| `volume` | `double` | Volumen |
| `price` | `double` | Precio de ejecución |
| `bid` | `double` | Precio Bid actual |
| `ask` | `double` | Precio Ask actual |
| `comment` | `string` | Comentario del bróker |
| `request_id` | `uint64` | ID de la solicitud |
| `ret_code_external` | `uint32` | Código de retorno externo |

---

## 🧱 Enums relacionados (de proto)

### `TMT5_ENUM_ORDER_TYPE_TIME`

Se utiliza en `OrderModifyRequest` para especificar el tipo de vencimiento.

| Nombre de la constante | Valor | Descripción |
|---|---:|---|
| `TMT5_ORDER_TIME_GTC` | 0 | Válida hasta su cancelación |
| `TMT5_ORDER_TIME_DAY` | 1 | Válida hasta el final del día de negociación actual |
| `TMT5_ORDER_TIME_SPECIFIED` | 2 | Válida hasta la fecha especificada |
| `TMT5_ORDER_TIME_SPECIFIED_DAY` | 3 | Válida hasta el día especificado |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Acceder a los valores del enum
trading_pb2.TMT5_ORDER_TIME_GTC            # = 0
trading_pb2.TMT5_ORDER_TIME_DAY            # = 1
trading_pb2.TMT5_ORDER_TIME_SPECIFIED      # = 2
trading_pb2.TMT5_ORDER_TIME_SPECIFIED_DAY  # = 3
```

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**[OrderModify - Cómo funciona](../HOW_IT_WORK/5. Trading_Operations_HOW/order_modify_HOW.md)**

---

## 🧩 Notas y consejos

- **Reconexión automática:** Todos los métodos de `MT5Account` incluyen protección integrada contra errores gRPC transitorios, con reconexión automática mediante `execute_with_reconnect`.
- **Cero para eliminar:** Establece `stop_loss=0` o `take_profit=0` para eliminarlos.
- **Órdenes pendientes:** Se pueden modificar el precio y el vencimiento de las órdenes pendientes.
- **Posiciones de mercado:** En las posiciones de mercado solo se pueden modificar el SL/TP.
- **Distancia mínima:** El bróker impone una distancia mínima respecto al precio actual para el SL/TP.
- **Nivel de congelación (Freeze Level):** No se pueden modificar órdenes que estén demasiado cerca del precio de mercado (configuración del bróker).

---

## 🔗 Ejemplos de uso

### 1) Añadir Stop Loss a una posición

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2


async def add_stop_loss():
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
        # Obtener el precio actual
        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)
        current_bid = tick_data.tick.bid

        # Establecer el SL 50 pips por debajo del precio actual
        pip_size = 0.0001
        sl_price = current_bid - (50 * pip_size)

        # Modificar la posición para añadir el SL
        request = trading_pb2.OrderModifyRequest(
            ticket=123456,
            stop_loss=sl_price,
            take_profit=0,  # Mantener el TP existente o no establecer TP
            price=0         # No se utiliza para posiciones de mercado
        )

        result = await account.order_modify(request)
        print(f"[ÉXITO] Stop Loss añadido en {sl_price:.5f}")

    finally:
        await account.channel.close()


asyncio.run(add_stop_loss())
```

### 2) Modificar tanto el SL como el TP

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2


async def modify_sl_tp():
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
        # Obtener el precio actual
        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)
        current_bid = tick_data.tick.bid

        pip_size = 0.0001
        new_sl = current_bid - (30 * pip_size)  # SL de 30 pips
        new_tp = current_bid + (60 * pip_size)  # TP de 60 pips (R:R de 2:1)

        request = trading_pb2.OrderModifyRequest(
            ticket=123456,
            stop_loss=new_sl,
            take_profit=new_tp,
            price=0
        )

        result = await account.order_modify(request)
        print(f"[ÉXITO] ¡SL/TP modificados!")
        print(f"  Nuevo SL: {new_sl:.5f}")
        print(f"  Nuevo TP: {new_tp:.5f}")

    finally:
        await account.channel.close()


asyncio.run(modify_sl_tp())
```

### 3) Eliminar Stop Loss

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


async def remove_stop_loss():
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
        # Establecer el SL en 0 para eliminarlo
        request = trading_pb2.OrderModifyRequest(
            ticket=123456,
            stop_loss=0,     # Eliminar SL
            take_profit=0,   # Mantener el TP existente
            price=0
        )

        result = await account.order_modify(request)
        print(f"[ÉXITO] ¡Stop Loss eliminado!")

    finally:
        await account.channel.close()


asyncio.run(remove_stop_loss())
```

### 4) Modificar el precio de una orden pendiente

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2


async def modify_pending_order_price():
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
        # Obtener el precio actual
        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)
        current_bid = tick_data.tick.bid

        # Nuevo precio BUY LIMIT (15 pips por debajo del precio actual)
        pip_size = 0.0001
        new_price = current_bid - (15 * pip_size)

        request = trading_pb2.OrderModifyRequest(
            ticket=789012,  # Ticket de la orden pendiente
            stop_loss=0,
            take_profit=0,
            price=new_price  # Nuevo precio de entrada
        )

        result = await account.order_modify(request)
        print(f"[ÉXITO] Precio de la orden pendiente actualizado a {new_price:.5f}")

    finally:
        await account.channel.close()


asyncio.run(modify_pending_order_price())
```

### 5) Implementación de trailing stop

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2


async def trailing_stop(ticket: int, trail_distance_pips: int):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    pip_size = 0.0001
    last_sl = None

    try:
        while True:
            # Obtener el precio actual
            tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
            tick_data = await account.symbol_info_tick(tick_req)
            current_bid = tick_data.tick.bid

            # Calcular el nuevo SL
            new_sl = current_bid - (trail_distance_pips * pip_size)

            # Actualizar solo si el nuevo SL es más alto (para BUY)
            if last_sl is None or new_sl > last_sl:
                request = trading_pb2.OrderModifyRequest(
                    ticket=ticket,
                    stop_loss=new_sl,
                    take_profit=0,
                    price=0
                )

                result = await account.order_modify(request)
                print(f"[TRAIL] SL actualizado a {new_sl:.5f}")
                last_sl = new_sl

            await asyncio.sleep(1)  # Comprobar cada segundo

    except KeyboardInterrupt:
        print("\nTrailing stop detenido")

    finally:
        await account.channel.close()


# Mantener el trailing stop a 30 pips del precio
asyncio.run(trailing_stop(123456, 30))
```

### 6) Stop Loss en el punto de equilibrio (Break-even)

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2


async def move_to_breakeven(ticket: int, breakeven_trigger_pips: int):
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
        # Obtener los detalles de la posición
        positions_req = account_pb2.OpenedOrdersRequest()
        positions_data = await account.opened_orders(positions_req)

        position = next((p for p in positions_data.positions if p.ticket == ticket), None)

        if not position:
            print(f"[ERROR] Posición #{ticket} no encontrada")
            return

        entry_price = position.price_open
        pip_size = 0.0001

        # Comprobar si el beneficio ha alcanzado el nivel de activación
        profit_pips = (position.price_current - entry_price) / pip_size

        if profit_pips >= breakeven_trigger_pips:
            # Mover el SL al punto de equilibrio
            request = trading_pb2.OrderModifyRequest(
                ticket=ticket,
                stop_loss=entry_price,  # Establecer el SL en el precio de entrada
                take_profit=0,
                price=0
            )

            result = await account.order_modify(request)
            print(f"[BREAKEVEN] SL movido al precio de entrada {entry_price:.5f}")
            print(f"  Beneficio actual: {profit_pips:.1f} pips")
        else:
            print(f"[ESPERANDO] Beneficio {profit_pips:.1f} pips < nivel de activación {breakeven_trigger_pips} pips")

    finally:
        await account.channel.close()


# Mover al punto de equilibrio cuando el beneficio alcance 20 pips
asyncio.run(move_to_breakeven(123456, 20))
```

---

## 📚 Véase también

- [OrderSend](./order_send.md) - Abrir posiciones.
- [OrderClose](./order_close.md) - Cerrar posiciones.
- [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Obtener detalles de las posiciones.