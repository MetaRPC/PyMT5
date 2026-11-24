

# Calcular el margen requerido

> **Solicitud:** Calcular el margen necesario para una operación de trading planificada.

**Información de la API:**

- **API de Python:** `MT5Account.order_calc_margin(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.TradeFunctions`
- **Definición Proto:** `OrderCalcMargin` (definido en `mt5-term-api-trade-functions.proto`)
- **Enums de este método:** 1 enum con 9 constantes (1 entrada)

### RPC

- **Servicio:** `mt5_term_api.TradeFunctions`
- **Método:** `OrderCalcMargin(OrderCalcMarginRequest) -> OrderCalcMarginReply`
- **Cliente de bajo nivel (generado):** `TradeFunctionsStub.OrderCalcMargin(request, metadata)`

---

## 💬 Lo esencial

- **Qué es.** Calcula el margen requerido para una operación sin ejecutarla.
- **Para qué sirve.** Planificar el tamaño de las posiciones y gestionar el riesgo.
- **Moneda de la cuenta.** Devuelve el margen en la moneda de la cuenta (USD, EUR, etc.).

---

## 🎯 Propósito

Utilízalo para:

- Calcular los requisitos de margen antes de operar.
- Determinar el tamaño máximo de posición según el margen disponible.
- Planificar varias posiciones.
- Realizar cálculos de gestión de riesgos.
- Analizar el margen de la cartera.
- Comparar los requisitos de margen entre distintos símbolos.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**[OrderCalcMargin - Cómo funciona](../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_margin_HOW.md)**

```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


class MT5Account:
    # ...

    async def order_calc_margin(
        self,
        request: trade_pb2.OrderCalcMarginRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trade_pb2.OrderCalcMarginData:
        """
        Calcula el margen necesario para una operación de trading planificada.

        Returns:
            OrderCalcMarginData: El margen requerido en la moneda de la cuenta.
        """
```

**Mensaje de solicitud:**

```protobuf
message OrderCalcMarginRequest {
  string symbol = 1;            // Nombre del símbolo
  ENUM_ORDER_TYPE_TF order_type = 2;  // Tipo de orden
  double volume = 3;             // Volumen de la operación en lotes
  double open_price = 4;         // Precio de apertura de la orden
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `request` | `OrderCalcMarginRequest` | Solicitud de cálculo del margen |
| `deadline` | `Optional[datetime]` | Límite de tiempo para la operación (opcional) |
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la solicitud (opcional) |

**Campos de OrderCalcMarginRequest:**

| Campo | Tipo | Descripción |
|---|---|---|
| `symbol` | `string` | Nombre del símbolo (por ejemplo, "EURUSD") |
| `order_type` | `ENUM_ORDER_TYPE_TF` | Tipo de orden (enum) |
| `volume` | `double` | Volumen de la operación en lotes |
| `open_price` | `double` | Precio de apertura de la orden |

---

## ⬆️ Salida

Devuelve un objeto `OrderCalcMarginData` con el resultado del cálculo del margen.

**Campos de OrderCalcMarginData:**

| Campo | Tipo | Descripción |
|---|---|---|
| `margin` | `double` | Margen requerido en la moneda de la cuenta |

---

## 🧱 Enums relacionados (del proto)

### `ENUM_ORDER_TYPE_TF`

Se utiliza en `OrderCalcMarginRequest` para especificar el tipo de orden para el cálculo del margen.

| Nombre de la constante | Valor | Descripción |
|---|---:|---|
| `ORDER_TYPE_TF_BUY` | 0 | Orden de compra a mercado |
| `ORDER_TYPE_TF_SELL` | 1 | Orden de venta a mercado |
| `ORDER_TYPE_TF_BUY_LIMIT` | 2 | Orden pendiente Buy Limit |
| `ORDER_TYPE_TF_SELL_LIMIT` | 3 | Orden pendiente Sell Limit |
| `ORDER_TYPE_TF_BUY_STOP` | 4 | Orden pendiente Buy Stop |
| `ORDER_TYPE_TF_SELL_STOP` | 5 | Orden pendiente Sell Stop |
| `ORDER_TYPE_TF_BUY_STOP_LIMIT` | 6 | Orden pendiente Buy Stop Limit |
| `ORDER_TYPE_TF_SELL_STOP_LIMIT` | 7 | Orden pendiente Sell Stop Limit |
| `ORDER_TYPE_TF_CLOSE_BY` | 8 | Cierre mediante una posición opuesta |

**Uso:**

```python
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as trade_pb2

# Acceder a los valores del enum
trade_pb2.ORDER_TYPE_TF_BUY         # = 0
trade_pb2.ORDER_TYPE_TF_SELL        # = 1
```

---

## 🧩 Notas y consejos

- **Reconexión automática:** todos los métodos de `MT5Account` tienen protección integrada contra errores gRPC transitorios mediante reconexión automática a través de `execute_with_reconnect`.
- **Sin ejecución:** este método solo calcula el margen, NO ejecuta órdenes.
- **Misma solicitud:** utiliza la misma estructura de solicitud que `order_send`.
- **Impacto del apalancamiento:** el resultado depende del apalancamiento del símbolo y de la configuración de la cuenta.
- **Cálculo en tiempo real:** utiliza los precios actuales del mercado para realizar el cálculo.
- **Diferencia respecto a order_check:** este método solo devuelve el margen; `order_check` valida la orden completa.

---

## 🔗 Ejemplos de uso

### 1) Calcular el margen para una operación individual

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


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
        # Calcular el margen para 0.10 lotes de EURUSD
        request = trade_pb2.OrderCalcMarginRequest(
            symbol="EURUSD",
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            volume=0.10,
            open_price=1.0850
        )

        result = await account.order_calc_margin(request)

        print(f"[ÉXITO] Cálculo del margen:")
        print(f"  Símbolo: EURUSD")
        print(f"  Volumen: 0.10 lotes")
        print(f"  Margen requerido: ${result.margin:,.2f}")

    finally:
        await account.channel.close()


asyncio.run(calc_margin())
```

### 2) Comparar el margen entre distintos símbolos

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


async def compare_margin():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
    volume = 0.10

    try:
        print(f"Requisitos de margen para {volume} lotes:\n")
        print(f"{'Símbolo':<10} {'Margen':<15}")
        print("-" * 30)

        for symbol in symbols:
            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)
            print(f"{symbol:<10} ${result.margin:>12,.2f}")

    finally:
        await account.channel.close()


asyncio.run(compare_margin())
```

### 3) Calcular el tamaño máximo de posición

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2


async def calc_max_position(symbol: str, margin_percent: float = 50.0):
    """Calcula el tamaño máximo de posición utilizando el X% del margen libre"""
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
        # Obtener el margen disponible
        summary_req = account_pb2.AccountSummaryRequest()
        summary = await account.account_summary(summary_req)
        available_margin = summary.margin_free * (margin_percent / 100.0)

        print(f"Calculando la posición máxima para {symbol}:")
        print(f"  Margen libre: ${summary.margin_free:,.2f}")
        print(f"  Utilizando {margin_percent}% = ${available_margin:,.2f}\n")

        # Búsqueda binaria del volumen máximo
        min_vol = 0.01
        max_vol = 100.0
        best_volume = 0.01

        while max_vol - min_vol > 0.01:
            test_volume = (min_vol + max_vol) / 2

            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=test_volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)

            if result.margin <= available_margin:
                best_volume = test_volume
                min_vol = test_volume
            else:
                max_vol = test_volume

        print(f"[RESULTADO] Tamaño máximo de posición: {best_volume:.2f} lotes")

        # Verificar el cálculo final
        final_req = trade_pb2.OrderCalcMarginRequest(
            symbol=symbol,
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            volume=best_volume,
            open_price=1.0
        )
        final_result = await account.order_calc_margin(final_req)

        print(f"  Margen requerido: ${final_result.margin:,.2f}")
        print(f"  Uso del margen: {(final_result.margin / available_margin * 100):.1f}%")

    finally:
        await account.channel.close()


asyncio.run(calc_max_position("EURUSD", margin_percent=50.0))
```

### 4) Cálculo del margen de la cartera

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2


async def portfolio_margin():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Cartera planificada
    trades = [
        ("EURUSD", 0.10),
        ("GBPUSD", 0.05),
        ("USDJPY", 0.10),
        ("XAUUSD", 0.01),
    ]

    try:
        # Obtener el estado actual de la cuenta
        summary_req = account_pb2.AccountSummaryRequest()
        summary = await account.account_summary(summary_req)

        print(f"Análisis del margen de la cartera\n")
        print(f"Estado actual:")
        print(f"  Balance: ${summary.balance:,.2f}")
        print(f"  Margen libre: ${summary.margin_free:,.2f}\n")

        print(f"Operaciones planificadas:")
        print(f"{'Símbolo':<10} {'Volumen':<10} {'Margen':<15}")
        print("-" * 40)

        total_margin = 0.0

        for symbol, volume in trades:
            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)

            print(f"{symbol:<10} {volume:<10.2f} ${result.margin:>12,.2f}")
            total_margin += result.margin

        print("-" * 40)
        print(f"{'TOTAL':<10} {'':<10} ${total_margin:>12,.2f}\n")

        # Comprobar si la cartera cabe en el margen disponible
        if total_margin <= summary.margin_free:
            remaining = summary.margin_free - total_margin
            usage_percent = (total_margin / summary.margin_free) * 100
            print(f"[OK] ¡La cartera cabe en el margen disponible!")
            print(f"  Uso del margen: {usage_percent:.1f}%")
            print(f"  Margen libre restante: ${remaining:,.2f}")
        else:
            shortage = total_margin - summary.margin_free
            print(f"[ADVERTENCIA] ¡Margen insuficiente!")
            print(f"  Requerido: ${total_margin:,.2f}")
            print(f"  Disponible: ${summary.margin_free:,.2f}")
            print(f"  Déficit: ${shortage:,.2f}")

    finally:
        await account.channel.close()


asyncio.run(portfolio_margin())
```

### 5) Dimensionamiento de posiciones basado en el riesgo

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2


async def risk_based_sizing(symbol: str, risk_percent: float = 2.0):
    """Calcula el tamaño de la posición en función del porcentaje de riesgo"""
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
        # Obtener el balance de la cuenta
        summary_req = account_pb2.AccountSummaryRequest()
        summary = await account.account_summary(summary_req)

        max_risk_amount = summary.balance * (risk_percent / 100.0)

        print(f"Dimensionamiento de posiciones basado en el riesgo para {symbol}:")
        print(f"  Balance de la cuenta: ${summary.balance:,.2f}")
        print(f"  Riesgo: {risk_percent}% = ${max_risk_amount:,.2f}\n")

        # Probar distintos volúmenes
        volumes = [0.01, 0.05, 0.10, 0.20, 0.50, 1.00]

        print(f"{'Volumen':<10} {'Margen':<15} {'% del balance':<15}")
        print("-" * 45)

        for volume in volumes:
            request = trade_pb2.OrderCalcMarginRequest(
                symbol=symbol,
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                volume=volume,
                open_price=1.0
            )

            result = await account.order_calc_margin(request)

            margin_percent = (result.margin / summary.balance) * 100

            status = "[OK]" if margin_percent <= risk_percent else "[EXCESO]"

            print(f"{volume:<10.2f} ${result.margin:>12,.2f} {margin_percent:>13.2f}% {status}")

    finally:
        await account.channel.close()


asyncio.run(risk_based_sizing("EURUSD", risk_percent=2.0))
```

### 6) Clase auxiliar para calcular el margen

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


class MarginCalculator:
    def __init__(self, account):
        self.account = account
        self.cache = {}  # Caché de cálculos

    async def get_margin(self, symbol: str, volume: float, order_type: int = 0):
        """Obtiene el margen utilizando la caché"""
        cache_key = f"{symbol}_{volume}_{order_type}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        request = trade_pb2.OrderCalcMarginRequest(
            symbol=symbol,
            order_type=order_type,
            volume=volume,
            open_price=1.0
        )

        result = await self.account.order_calc_margin(request)

        self.cache[cache_key] = result.margin
        return result.margin

    async def get_leverage_ratio(self, symbol: str, volume: float = 1.0):
        """Calcula el apalancamiento efectivo del símbolo"""
        import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

        # Obtener el tamaño del contrato
        tick_req = market_pb2.SymbolInfoTickRequest(symbol=symbol)
        tick_data = await self.account.symbol_info_tick(tick_req)

        # Calcular el margen para 1 lote
        margin = await self.get_margin(symbol, volume)

        # Valor del contrato = precio * tamaño del contrato
        contract_value = tick_data.tick.ask * 100000  # Suponiendo un contrato de 100k

        leverage = contract_value / margin if margin > 0 else 0

        return leverage


async def main():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    calc = MarginCalculator(account)

    try:
        # Calcular el margen
        margin = await calc.get_margin("EURUSD", 0.10)
        print(f"Margen para 0.10 lotes de EURUSD: ${margin:,.2f}")

        # Calcular el apalancamiento
        leverage = await calc.get_leverage_ratio("EURUSD", 1.0)
        print(f"Apalancamiento efectivo: 1:{leverage:.0f}")

    finally:
        await account.channel.close()


asyncio.run(main())
```

---

## 📚 Véase también

- [OrderCheck](./order_check.md) - validación completa de órdenes (incluye el margen).
- [OrderCalcProfit](./order_calc_profit.md) - calcular el beneficio o la pérdida potencial.
- [OrderSend](./order_send.md) - ejecutar órdenes.
- [AccountSummary](../1.%20Account_Information/account_summary.md) - obtener información sobre el margen de la cuenta.

