Готово. Полный перевод документа на испанский. Названия методов, классов, переменных, API-идентификаторы и технические значения сохранены без изменений.

# MT5Account - Operaciones de trading - Descripción general

> Ejecutar, modificar y gestionar operaciones: enviar órdenes, cerrar posiciones, validar solicitudes y calcular el margen.

## 📁 Contenido de esta sección

### Ejecución de órdenes

- **order_send** - enviar órdenes de mercado o pendientes.
- **order_close** - cerrar posiciones o eliminar órdenes pendientes.
- **order_modify** - modificar SL/TP, el precio o la fecha de expiración.

### Validación y cálculo de órdenes

- **order_check** - validar órdenes antes de ejecutarlas.
- **order_calc_margin** - calcular el margen requerido.
- **order_calc_profit** - calcular el beneficio o la pérdida potenciales.

---

## 📚 Tutoriales paso a paso

**Nota:** Todas las operaciones de trading son métodos asíncronos. Consulta las páginas de cada método para ver ejemplos detallados.

- **[order_send]\(../HOW_IT_WORK/5. Trading_Operations_HOW/order_send_HOW\.md)** - ejemplos de ejecución de órdenes.
- **[order_close]\(../HOW_IT_WORK/5. Trading_Operations_HOW/order_close_HOW\.md)** - patrones para cerrar posiciones.
- **[order_modify]\(../HOW_IT_WORK/5. Trading_Operations_HOW/order_modify_HOW\.md)** - ejemplos de modificación de SL/TP.
- **[order_check]\(../HOW_IT_WORK/5. Trading_Operations_HOW/order_check_HOW\.md)** - patrones de validación de órdenes.
- **[order_calc_margin]\(../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_margin_HOW\.md)** - ejemplos de cálculo del margen.
- **[order_calc_profit]\(../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_profit_HOW\.md)** - ejemplos de cálculo de beneficios y pérdidas.

---

## 🧭 En términos sencillos

- **order_send** -> **abrir posiciones** o colocar órdenes pendientes (BUY, SELL, LIMIT, STOP).
- **order_close** -> **cerrar posiciones** total o parcialmente, o eliminar órdenes pendientes.
- **order_modify** -> **modificar SL/TP** o cambiar los parámetros de las órdenes pendientes.
- **order_check** -> **validar órdenes** antes de enviarlas (comprobar el margen y los parámetros).
- **order_calc_margin** -> **calcular el margen** necesario para las operaciones previstas.
- **order_calc_profit** -> **calcular el beneficio o la pérdida** de las operaciones previstas (análisis de riesgo/recompensa).

> Regla práctica: **abrir** -> `order_send`; **cerrar** -> `order_close`; **ajustar** -> `order_modify`; **validar** -> `order_check`; **planificar el margen** -> `order_calc_margin`; **calcular el beneficio previsto** -> `order_calc_profit`.

---

## Selección rápida

| Si necesitas...                                              | Utiliza             | Devuelve            | Parámetros principales                      |
| ------------------------------------------------------------ | ------------------- | ------------------- | ------------------------------------------- |
| Abrir una posición de mercado (BUY/SELL)                     | `order_send`        | OrderSendData       | symbol, operation, volume, price            |
| Colocar una orden pendiente (LIMIT/STOP)                     | `order_send`        | OrderSendData       | symbol, operation, volume, price            |
| Cerrar una posición por completo                             | `order_close`       | OrderCloseData      | ticket, volume=0, slippage                  |
| Cerrar una posición parcialmente                             | `order_close`       | OrderCloseData      | ticket, volume, slippage                    |
| Eliminar una orden pendiente                                 | `order_close`       | OrderCloseData      | ticket, volume=0                            |
| Añadir o modificar Stop Loss o Take Profit                   | `order_modify`      | OrderModifyData     | ticket, stop_loss, take_profit              |
| Cambiar el precio de una orden pendiente                     | `order_modify`      | OrderModifyData     | ticket, price                               |
| Validar una orden antes de enviarla                          | `order_check`       | OrderCheckData      | OrderSendRequest                            |
| Calcular el margen de una operación prevista                 | `order_calc_margin` | OrderCalcMarginData | symbol, operation, volume                   |
| Calcular el beneficio o la pérdida de una operación prevista | `order_calc_profit` | OrderCalcProfitData | symbol, operation, volume, open/close price |

---

## ℹ️ Referencias cruzadas y aspectos importantes

- **Códigos de retorno:** comprueba siempre `returned_code == 10009` para confirmar el éxito de las operaciones (order_send/close) y `== 0` para los métodos de validación.
- **Métodos asíncronos:** todas las operaciones de trading son asíncronas; utiliza `await`.
- **Reconexión automática:** todos los métodos incorporan reconexión automática mediante `execute_with_reconnect`.
- **Volume = 0:** en `order_close`, volume=0 significa cerrar toda la posición.
- **Slippage:** establece un deslizamiento adecuado para las órdenes de mercado (por ejemplo, 20 puntos).
- **SL/TP = 0:** en `order_modify`, utiliza 0 para eliminar el SL o el TP.
- **Comprobar antes de enviar:** utiliza siempre `order_check` antes de `order_send` para las órdenes grandes.
- **Cálculo del margen:** `order_check` incluye el margen, mientras que `order_calc_margin` solo calcula el margen.
- **Cálculo del beneficio:** `order_calc_profit` calcula el beneficio o la pérdida potenciales para el análisis de riesgo/recompensa.
- **Freeze level:** no es posible modificar órdenes demasiado cerca del precio de mercado (configuración del bróker).
- **Distancia mínima:** el bróker aplica una distancia mínima respecto al precio actual para SL/TP.

---

## 🟢 Ejemplos mínimos

```
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Enviar una orden de mercado BUY
async def market_buy():
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
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=0,  # 0 = BUY
            volume=0.01,
            price=0,
            slippage=20,
            comment="Market BUY"
        )

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[ÉXITO] Deal: #{result.deal}, Precio: {result.price}")
        else:
            print(f"[ERROR] {result.returned_code_description}")

    finally:
        await account.channel.close()


asyncio.run(market_buy())
```

```
# Cerrar una posición
async def close_position(ticket):
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
        request = trading_pb2.OrderCloseRequest(
            ticket=ticket,
            volume=0,  # Cerrar todo
            slippage=20
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[ÉXITO] Posición cerrada")
        else:
            print(f"[ERROR] {result.returned_code_description}")

    finally:
        await account.channel.close()


asyncio.run(close_position(123456))
```

```
# Modificar Stop Loss
async def modify_sl(ticket, new_sl):
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
        request = trading_pb2.OrderModifyRequest(
            ticket=ticket,
            stop_loss=new_sl,
            take_profit=0,  # Mantener el valor existente
            price=0
        )

        result = await account.order_modify(request)
        print(f"[ÉXITO] SL modificado a {new_sl}")

    finally:
        await account.channel.close()


asyncio.run(modify_sl(123456, 1.08500))
```

```
# Comprobar una orden antes de enviarla
async def check_and_send():
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
        import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

        # Crear una solicitud de operación
        trade_request = trade_pb2.MrpcMqlTradeRequest(
            action=0,  # TRADE_ACTION_DEAL
            symbol="EURUSD",
            volume=0.10,
            order_type=0,  # ORDER_TYPE_BUY
            type_filling=2,  # ORDER_FILLING_RETURN
            type_time=0  # ORDER_TIME_GTC
        )

        check_req = trade_pb2.OrderCheckRequest(mql_trade_request=trade_request)

        # Comprobar primero
        check_result = await account.order_check(check_req)

        if check_result.returned_code == 0:
            print(f"[VÁLIDO] Margen: ${check_result.margin:.2f}")

            # Enviar la orden
            send_request = trading_pb2.OrderSendRequest(
                symbol="EURUSD",
                operation=0,
                volume=0.10,
                price=0,
                slippage=20
            )

            send_result = await account.order_send(send_request)

            if send_result.returned_code == 10009:
                print(f"[ÉXITO] Deal: #{send_result.deal}")
        else:
            print(f"[NO VÁLIDO] {check_result.returned_code_description}")

    finally:
        await account.channel.close()


asyncio.run(check_and_send())
```

```
# Calcular el margen
async def calc_margin():
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
        import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

        request = trade_pb2.OrderCalcMarginRequest(
            symbol="EURUSD",
            order_type=0,  # ORDER_TYPE_BUY
            volume=0.10,
            open_price=1.10000
        )

        result = await account.order_calc_margin(request)

        if result.returned_code == 0:
            print(f"Margen requerido: ${result.margin:,.2f}")
        else:
            print(f"[ERROR] {result.returned_code_description}")

    finally:
        await account.channel.close()


asyncio.run(calc_margin())
```

```
# Flujo completo de trading
async def trading_workflow():
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
        import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

        # 1. Calcular el margen
        margin_req = trade_pb2.OrderCalcMarginRequest(
            symbol="EURUSD",
            order_type=0,
            volume=0.10,
            open_price=1.10000
        )

        margin_result = await account.order_calc_margin(margin_req)
        print(f"[1] Margen: ${margin_result.margin:.2f}")

        # 2. Comprobar la orden
        trade_request = trade_pb2.MrpcMqlTradeRequest(
            action=0,
            symbol="EURUSD",
            volume=0.10,
            order_type=0,
            type_filling=2,
            type_time=0
        )

        check_req = trade_pb2.OrderCheckRequest(mql_trade_request=trade_request)
        check_result = await account.order_check(check_req)
        if check_result.returned_code != 0:
            print(f"[2] Error en la comprobación: {check_result.returned_code_description}")
            return

        print(f"[2] Orden válida, margen libre después de la operación: ${check_result.margin_free:.2f}")

        # 3. Enviar la orden
        send_req = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=0,
            volume=0.10,
            price=0,
            slippage=20
        )

        send_result = await account.order_send(send_req)
        if send_result.returned_code != 10009:
            print(f"[3] Error al enviar la orden: {send_result.returned_code_description}")
            return

        print(f"[3] ¡Orden enviada! Deal: #{send_result.deal}")
        ticket = send_result.deal

        # 4. Modificar para añadir SL/TP
        await asyncio.sleep(1)  # Esperar un momento

        import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick = await account.symbol_info_tick(tick_req)

        pip_size = 0.0001
        sl = tick.tick.bid - (50 * pip_size)
        tp = tick.tick.bid + (100 * pip_size)

        modify_req = trading_pb2.OrderModifyRequest(
            ticket=ticket,
            stop_loss=sl,
            take_profit=tp,
            price=0
        )

        await account.order_modify(modify_req)
        print(f"[4] SL/TP añadidos: SL={sl:.5f}, TP={tp:.5f}")

        # 5. Más tarde... cerrar la posición
        await asyncio.sleep(5)

        close_req = trading_pb2.OrderCloseRequest(
            ticket=ticket,
            volume=0,
            slippage=20
        )

        close_result = await account.order_close(close_req)
        if close_result.returned_code == 10009:
            print(f"[5] Posición cerrada")

    finally:
        await account.channel.close()


asyncio.run(trading_workflow())
```

```
# Operaciones por lotes
async def batch_operations():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbols = ["EURUSD", "GBPUSD", "USDJPY"]

    try:
        # Abrir varias posiciones
        deals = []

        for symbol in symbols:
            request = trading_pb2.OrderSendRequest(
                symbol=symbol,
                operation=0,
                volume=0.01,
                price=0,
                slippage=20,
                comment=f"Posición {symbol}"
            )

            result = await account.order_send(request)

            if result.returned_code == 10009:
                deals.append(result.deal)
                print(f"[ABIERTA] {symbol}: #{result.deal}")

        # Esperar...
        await asyncio.sleep(10)

        # Cerrar todas las posiciones
        for deal in deals:
            close_req = trading_pb2.OrderCloseRequest(
                ticket=deal,
                volume=0,
                slippage=20
            )

            result = await account.order_close(close_req)

            if result.returned_code == 10009:
                print(f"[CERRADA] #{deal}")

    finally:
        await account.channel.close()


asyncio.run(batch_operations())
```

---

## 📚 Véase también

- **Posiciones:** opened_orders - obtener las posiciones actuales.
- **Historial:** order_history - obtener el historial de órdenes.
- **Cuenta:** account_summary - obtener el estado de la cuenta.
- **Precios:** symbol_info_tick - obtener los precios actuales.

Corrige la semántica de \`order_modify\`Aclara tickets de posiciones y órdenes