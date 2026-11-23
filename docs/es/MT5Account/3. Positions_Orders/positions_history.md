# Obtener posiciones históricas cerradas

**Solicitud:** obtener posiciones históricas cerradas dentro de un intervalo de tiempo, con soporte para ordenación y paginación.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.positions_history(...)` (definida en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.AccountHelper`
- **Definición Proto:** `PositionsHistory` (definida en `mt5-term-api-account-helper.proto`)
- **Enums de este método:** 2 enums con 13 constantes en total (1 de entrada, 1 de salida)

### RPC

- **Servicio:** `mt5_term_api.AccountHelper`
- **Método:** `PositionsHistory(PositionsHistoryRequest) -> PositionsHistoryReply`
- **Cliente de bajo nivel (generado):** `AccountHelperStub.PositionsHistory(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene posiciones históricas cerradas filtradas por intervalo de tiempo de apertura.
- **Para qué lo necesitas.** Analizar el rendimiento de las operaciones y calcular estadísticas de las posiciones cerradas.
- **Cuándo utilizarlo.** Utiliza este método para consultar posiciones cerradas. Utiliza `order_history()` para consultar el historial de órdenes y operaciones.

---

## 🎯 Propósito

Utiliza este método para recuperar posiciones históricas cerradas:

- Obtener posiciones cerradas dentro de un intervalo de fechas.
- Analizar el rendimiento de las posiciones.
- Calcular las ganancias y pérdidas por posición.
- Revisar las operaciones cerradas.
- Filtrar por hora de apertura.
- Utilizar la paginación para grandes conjuntos de datos.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [positions_history - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_history_HOW.md)**

---

## Firma del método

```python
async def positions_history(
    self,
    sort_type: account_helper_pb2.AH_ENUM_POSITIONS_HISTORY_SORT_TYPE,
    open_from: Optional[datetime] = None,
    open_to: Optional[datetime] = None,
    page: int = 0,
    size: int = 0,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.PositionsHistoryData
```

**Mensaje de solicitud:**

```protobuf
message PositionsHistoryRequest {
  AH_ENUM_POSITIONS_HISTORY_SORT_TYPE sort_type = 1;
  optional google.protobuf.Timestamp position_open_time_from = 2;
  optional google.protobuf.Timestamp position_open_time_to = 3;
  optional int32 page_number = 4;
  optional int32 items_per_page = 5;
}
```

**Mensaje de respuesta:**

```protobuf
message PositionsHistoryReply {
  oneof response {
    PositionsHistoryData data = 1;
    Error error = 2;
  }
}

message PositionsHistoryData {
  repeated PositionHistoryInfo history_positions = 1;
  int32 total_count = 2;
  string next_page_token = 3;
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `sort_type` | `AH_ENUM_POSITIONS_HISTORY_SORT_TYPE` (enum, obligatorio) | Modo de ordenación de las posiciones |
| `open_from` | `datetime` (opcional) | Inicio del filtro por hora de apertura (UTC) |
| `open_to` | `datetime` (opcional) | Fin del filtro por hora de apertura (UTC) |
| `page` | `int` (opcional) | Número de página para la paginación (valor predeterminado: 0) |
| `size` | `int` (opcional) | Número de elementos por página (valor predeterminado: 0 = todos) |
| `deadline` | `datetime` (opcional) | Fecha y hora límite de la llamada gRPC (UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

**Uso:**

```python
from datetime import datetime, timedelta, timezone
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Obtener las posiciones abiertas durante los últimos 7 días
to_dt = datetime.now(timezone.utc)
from_dt = to_dt - timedelta(days=7)

data = await account.positions_history(
    sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_DESC,
    open_from=from_dt,
    open_to=to_dt,
    page=0,
    size=100
)
```

---

## ⬆️ Salida - `PositionsHistoryData`

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `history_positions` | `repeated PositionHistoryInfo` | `list[PositionHistoryInfo]` | Lista de registros históricos de posiciones |
| `total_count` | `int32` | `int` | Número total de posiciones coincidentes en todas las páginas |
| `next_page_token` | `string` | `str` | Cursor para la página siguiente (vacío si es la última) |

**Cada `PositionHistoryInfo` contiene:**

| Campo | Tipo | Descripción |
|---|---|---|
| `index` | `int32` | Índice en el conjunto de resultados |
| `position_ticket` | `uint64` | ID del ticket de la posición |
| `order_type` | `AH_ENUM_POSITIONS_HISTORY_ORDER_TYPE` | Tipo de orden (BUY, SELL, etc.) |
| `open_time` | `Timestamp` | Hora de apertura de la posición (hora del servidor) |
| `open_time_utc` | `Timestamp` | Hora de apertura de la posición (UTC) |
| `close_time` | `Timestamp` | Hora de cierre de la posición (hora del servidor) |
| `close_time_utc` | `Timestamp` | Hora de cierre de la posición (UTC) |
| `volume` | `double` | Volumen de la posición en lotes |
| `open_price` | `double` | Precio de apertura |
| `close_price` | `double` | Precio de cierre |
| `stop_loss` | `double` | Nivel de Stop Loss |
| `take_profit` | `double` | Nivel de Take Profit |
| `market_value` | `double` | Valor de mercado |
| `commission` | `double` | Comisión cobrada |
| `fee` | `double` | Comisiones adicionales |
| `profit` | `double` | Ganancia/pérdida de la posición |
| `swap` | `double` | Swap (cargo por rollover) |
| `comment` | `string` | Comentario |
| `symbol` | `string` | Nombre del símbolo |
| `magic` | `int64` | Número Magic (identificador del EA) |

---

## 🧱 Enums relacionados (de Proto)

### `AH_ENUM_POSITIONS_HISTORY_SORT_TYPE`

Definido en `mt5-term-api-account-helper.proto`.

| Constante | Valor | Descripción |
|---|---:|---|
| `AH_POSITION_OPEN_TIME_ASC` | 0 | Ordenar por hora de apertura ascendente |
| `AH_POSITION_OPEN_TIME_DESC` | 1 | Ordenar por hora de apertura descendente |
| `AH_POSITION_TICKET_ASC` | 2 | Ordenar por ID del ticket ascendente |
| `AH_POSITION_TICKET_DESC` | 3 | Ordenar por ID del ticket descendente |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

data = await account.positions_history(
    sort_type=pb2.AH_POSITION_OPEN_TIME_DESC,
    open_from=from_dt,
    open_to=to_dt
)
```

### `AH_ENUM_POSITIONS_HISTORY_ORDER_TYPE`

Definido en `mt5-term-api-account-helper.proto`. Se utiliza en `PositionHistoryInfo` para indicar el tipo de orden.

| Constante | Valor | Descripción |
|---|---:|---|
| `AH_ORDER_TYPE_BUY` | 0 | Orden de compra a mercado |
| `AH_ORDER_TYPE_SELL` | 1 | Orden de venta a mercado |
| `AH_ORDER_TYPE_BUY_LIMIT` | 2 | Orden pendiente Buy Limit |
| `AH_ORDER_TYPE_SELL_LIMIT` | 3 | Orden pendiente Sell Limit |
| `AH_ORDER_TYPE_BUY_STOP` | 4 | Orden pendiente Buy Stop |
| `AH_ORDER_TYPE_SELL_STOP` | 5 | Orden pendiente Sell Stop |
| `AH_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Orden pendiente Buy Stop Limit |
| `AH_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Orden pendiente Sell Stop Limit |
| `AH_ORDER_TYPE_CLOSE_BY` | 8 | Cierre mediante una posición opuesta |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Filtrar posiciones de compra
for pos in data.history_positions:
    if pos.order_type == pb2.AH_ORDER_TYPE_BUY:
        print(f"Posición de compra: {pos.position_ticket}")
```

---

## 🧩 Notas y consejos

- **Filtrar por hora de apertura:** `open_from` y `open_to` filtran las posiciones según el momento en que se abrieron, no según el momento en que se cerraron.
- **Paginación:** utiliza `page` y `size` para conjuntos de datos grandes. Establece `size=0` para obtener todos los resultados.
- **Reconexión automática:** protección integrada contra errores gRPC transitorios.
- **Conexión obligatoria:** primero llama a `connect_by_host_port()` o `connect_by_server_name()`.
- **Seguridad de subprocesos:** es seguro realizar llamadas simultáneas desde varias tareas de asyncio.
- **Gestión de UUID:** el UUID de la instancia del terminal se genera automáticamente en el servidor si no se proporciona. Para tener un control explícito (por ejemplo, en escenarios de streaming), pasa `id_=uuid4()` al constructor.

---

## 🔗 Ejemplos de uso

### 1) Obtener las posiciones cerradas de los últimos 30 días

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

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
        # Últimos 30 días
        to_dt = datetime.now(timezone.utc)
        from_dt = to_dt - timedelta(days=30)

        data = await account.positions_history(
            sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_DESC,
            open_from=from_dt,
            open_to=to_dt,
            size=100
        )

        print(f"Posiciones cerradas: {len(data.history_positions)}")

        for pos in data.history_positions:
            open_time = pos.open_time.ToDatetime()
            close_time = pos.close_time.ToDatetime()
            print(f"#{pos.position_ticket} {pos.symbol}: "
                  f"${pos.profit:+.2f} "
                  f"({open_time.date()} - {close_time.date()})")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Calcular la ganancia total de las posiciones cerradas

```python
async def calculate_closed_profit(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> float:
    """Calcular la ganancia total de las posiciones cerradas"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt,
        size=0  # Obtener todas
    )

    total_profit = sum(pos.profit for pos in data.history_positions)
    total_commission = sum(pos.commission for pos in data.history_positions)
    total_swap = sum(pos.swap for pos in data.history_positions)

    net_profit = total_profit - total_commission + total_swap

    print(f"Estadísticas de posiciones cerradas:")
    print(f"  Número total de posiciones: {len(data.history_positions)}")
    print(f"  Ganancia bruta: ${total_profit:+.2f}")
    print(f"  Comisión: ${total_commission:.2f}")
    print(f"  Swap: ${total_swap:+.2f}")
    print(f"  Ganancia neta: ${net_profit:+.2f}")

    return net_profit

# Uso:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
profit = await calculate_closed_profit(account, from_dt, to_dt)
```

### 3) Analizar la tasa de operaciones ganadoras

```python
async def analyze_closed_positions(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> dict:
    """Analizar el rendimiento de las posiciones cerradas"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    wins = 0
    losses = 0
    total_win_profit = 0.0
    total_loss_profit = 0.0

    for pos in data.history_positions:
        if pos.profit > 0:
            wins += 1
            total_win_profit += pos.profit
        elif pos.profit < 0:
            losses += 1
            total_loss_profit += pos.profit

    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0
    avg_win = total_win_profit / wins if wins > 0 else 0
    avg_loss = total_loss_profit / losses if losses > 0 else 0

    result = {
        "total_positions": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": abs(total_win_profit / total_loss_profit) if total_loss_profit != 0 else 0
    }

    print(f"\nAnálisis de posiciones:")
    print(f"  Total: {total}")
    print(f"  Ganadoras: {wins} ({win_rate:.1f}%)")
    print(f"  Perdedoras: {losses}")
    print(f"  Ganancia media: ${avg_win:.2f}")
    print(f"  Pérdida media: ${avg_loss:.2f}")
    print(f"  Factor de beneficio: {result['profit_factor']:.2f}")

    return result

# Uso:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
stats = await analyze_closed_positions(account, from_dt, to_dt)
```

### 4) Obtener las mejores y peores posiciones

```python
async def get_best_worst_positions(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    limit: int = 5
):
    """Obtener las posiciones con mejor y peor rendimiento"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    # Ordenar por ganancia
    sorted_positions = sorted(data.history_positions, key=lambda p: p.profit, reverse=True)

    best = sorted_positions[:limit]
    worst = sorted_positions[-limit:]

    print(f"\nLas {limit} mejores posiciones:")
    for i, pos in enumerate(best, 1):
        print(f"  {i}. #{pos.position_ticket} {pos.symbol}: ${pos.profit:+.2f}")

    print(f"\nLas {limit} peores posiciones:")
    for i, pos in enumerate(worst, 1):
        print(f"  {i}. #{pos.position_ticket} {pos.symbol}: ${pos.profit:+.2f}")

    return {"best": best, "worst": worst}

# Uso:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
results = await get_best_worst_positions(account, from_dt, to_dt)
```

### 5) Obtener posiciones por símbolo

```python
async def get_symbol_closed_positions(
    account: MT5Account,
    symbol: str,
    from_dt: datetime,
    to_dt: datetime
):
    """Obtener las posiciones cerradas de un símbolo específico"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_DESC,
        open_from=from_dt,
        open_to=to_dt
    )

    symbol_positions = [
        pos for pos in data.history_positions
        if pos.symbol == symbol
    ]

    total_profit = sum(pos.profit for pos in symbol_positions)

    print(f"\nPosiciones cerradas de {symbol}: {len(symbol_positions)}")
    print(f"Ganancia total: ${total_profit:+.2f}")

    return symbol_positions

# Uso:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
eurusd_positions = await get_symbol_closed_positions(account, "EURUSD", from_dt, to_dt)
```

### 6) Exportar a CSV

```python
import csv

async def export_positions_to_csv(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    filename: str = "positions_history.csv"
):
    """Exportar las posiciones cerradas a CSV"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Ticket', 'Symbol', 'Hora de apertura', 'Hora de cierre',
            'Volumen', 'Precio de apertura', 'Precio de cierre',
            'Ganancia', 'Comisión', 'Swap', 'Total'
        ])

        for pos in data.history_positions:
            open_time = pos.open_time.ToDatetime()
            close_time = pos.close_time.ToDatetime()
            total = pos.profit - pos.commission + pos.swap

            writer.writerow([
                pos.position_ticket,
                pos.symbol,
                open_time.strftime('%Y-%m-%d %H:%M:%S'),
                close_time.strftime('%Y-%m-%d %H:%M:%S'),
                pos.volume,
                pos.open_price,
                pos.close_price,
                pos.profit,
                pos.commission,
                pos.swap,
                total
            ])

    print(f"[OK] Se exportaron {len(data.history_positions)} posiciones a {filename}")

# Uso:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
await export_positions_to_csv(account, from_dt, to_dt)
```

---

## Patrones comunes

### Calcular la ganancia diaria

```python
from collections import defaultdict

async def get_daily_profit(account: MT5Account, from_dt: datetime, to_dt: datetime):
    """Calcular la ganancia diaria a partir de las posiciones cerradas"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    daily_profit = defaultdict(float)

    for pos in data.history_positions:
        close_date = pos.close_time.ToDatetime().date()
        daily_profit[close_date] += pos.profit

    return dict(daily_profit)
```

### Obtener posiciones mediante paginación

```python
async def get_all_positions_paginated(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    page_size: int = 100
):
    """Obtener todas las posiciones mediante paginación"""
    all_positions = []
    page = 0

    while True:
        data = await account.positions_history(
            sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
            open_from=from_dt,
            open_to=to_dt,
            page=page,
            size=page_size
        )

        if not data.history_positions:
            break

        all_positions.extend(data.history_positions)
        page += 1

    return all_positions
```

---

## 📚 Véase también

- [order_history](./order_history.md) - Obtener órdenes y operaciones históricas.
- [opened_orders](./opened_orders.md) - Obtener las posiciones actualmente abiertas.
- [positions_total](./positions_total.md) - Obtener el número de posiciones abiertas.