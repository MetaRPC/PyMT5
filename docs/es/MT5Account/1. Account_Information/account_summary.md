# Obtener el resumen completo de la cuenta

> **Solicitud:** obtener una instantánea completa de la cuenta con **todas las propiedades esenciales** en una sola llamada (saldo, patrimonio, apalancamiento, divisa, hora del servidor, etc.).

**Información de la API:**

- **API de bajo nivel:** `MT5Account.account_summary(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.AccountHelper`
- **Definición Proto:** `AccountSummary` (definida en `mt5-term-api-account-helper.proto`)

### RPC

- **Servicio:** `mt5_term_api.AccountHelper`
- **Método:** `AccountSummary(AccountSummaryRequest) -> AccountSummaryReply`
- **Cliente de bajo nivel (generado):** `AccountHelperStub.AccountSummary(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene una instantánea completa de la cuenta con todas las propiedades esenciales en una sola llamada.
- **Por qué lo necesitas.** Es la forma más eficiente de obtener varias propiedades de la cuenta (saldo, patrimonio, apalancamiento, etc.).
- **Cuándo utilizarlo.** Utiliza este método para obtener información general de la cuenta. Utiliza los métodos `account_info_*` únicamente para consultar propiedades específicas individuales.

---

## 🎯 Propósito

Utilízalo para obtener información completa de la cuenta:

- **RECOMENDADO:** método para obtener una descripción general de la cuenta.
- Obtener el saldo, el patrimonio y el crédito en una sola llamada.
- Consultar el login, el nombre, el servidor y la empresa de la cuenta.
- Obtener el apalancamiento y el modo de trading (demo/real).
- Obtener la divisa de la cuenta.
- Obtener la hora del servidor con el desplazamiento UTC.
- Es eficiente: una sola comunicación de ida y vuelta en lugar de varias llamadas.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [account_summary - Cómo funciona](../HOW_IT_WORK/1. Account_information_HOW/account_summary_HOW.md)**

---

## Firma del método

```
async def account_summary(
    self,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
)
```

**Mensaje de solicitud:**

```
message AccountSummaryRequest {
    // No se necesitan parámetros
}
```

**Mensaje de respuesta:**

```
message AccountSummaryReply {
    oneof response {
        AccountSummaryData data = 1;
        Error error = 2;
    }
}

message AccountSummaryData {
    int64 account_login = 1;
    double account_balance = 2;
    double account_equity = 3;
    string account_user_name = 4;
    int64 account_leverage = 5;
    MrpcEnumAccountTradeMode account_trade_mode = 6;
    string account_company_name = 7;
    string account_currency = 8;
    google.protobuf.Timestamp server_time = 9;
    int64 utc_timezone_server_time_shift_minutes = 10;
    double account_credit = 11;
    double account_margin = 12;
    int32 server_utc_offset_seconds = 13;
    google.protobuf.Timestamp server_time_utc = 14;
    double account_margin_free = 15;
    double account_margin_level = 16;
    MrpcEnumAccountMarginMode account_margin_mode = 17;
    bool account_trade_allowed = 18;
    bool account_trade_expert = 19;
    bool terminal_connected = 20;
    bool terminal_trade_allowed = 21;
}
```

---

## 🔽 Entrada

| Parámetro            | Tipo                       | Descripción                                          |
| -------------------- | -------------------------- | ---------------------------------------------------- |
| `deadline`           | `datetime` (opcional)      | Plazo límite para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación                    |

**No se requiere `property_id`**: este método devuelve todas las propiedades disponibles.

**Opciones de deadline:**

```
from datetime import datetime, timedelta, timezone

# 1. Con deadline (recomendado)
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
summary = await account.account_summary(deadline=deadline)

# 2. Con evento de cancelación
cancel_event = asyncio.Event()
summary = await account.account_summary(cancellation_event=cancel_event)

# 3. Sin deadline (utiliza el timeout predeterminado si está configurado)
summary = await account.account_summary()
```

---

## ⬆️ Salida - `AccountSummaryData`

| Campo                                    | Tipo                        | Tipo Python | Descripción                                                                 |
| ---------------------------------------- | --------------------------- | ----------- | --------------------------------------------------------------------------- |
| `account_login`                          | `int64`                     | `int`       | Número de cuenta                                                            |
| `account_balance`                        | `double`                    | `float`     | Saldo de la cuenta en la divisa del depósito                                |
| `account_equity`                         | `double`                    | `float`     | Patrimonio de la cuenta (saldo + beneficio/pérdida flotante)                   |
| `account_user_name`                      | `string`                    | `str`       | Nombre del titular de la cuenta                                             |
| `account_leverage`                       | `int64`                     | `int`       | Apalancamiento de la cuenta (por ejemplo, 100 para 1:100)                   |
| `account_trade_mode`                     | `MrpcEnumAccountTradeMode`  | `int`       | Modo de trading: 0=DEMO, 1=CONTEST, 2=REAL                                  |
| `account_company_name`                   | `string`                    | `str`       | Nombre del bróker/empresa                                                   |
| `account_currency`                       | `string`                    | `str`       | Divisa de la cuenta (USD, EUR, etc.)                                        |
| `server_time`                            | `google.protobuf.Timestamp` | `Timestamp` | Hora actual del servidor                                                    |
| `utc_timezone_server_time_shift_minutes` | `int64`                     | `int`       | Desplazamiento de la zona horaria del servidor respecto a UTC (en minutos)  |
| `account_credit`                         | `double`                    | `float`     | Crédito de la cuenta en la divisa del depósito                              |
| `account_margin`                         | `double`                    | `float`     | Margen utilizado actualmente (en la divisa del depósito)                    |
| `server_utc_offset_seconds`              | `int32`                     | `int`       | Desplazamiento de la zona horaria del servidor respecto a UTC (en segundos) |
| `server_time_utc`                        | `google.protobuf.Timestamp` | `Timestamp` | Hora actual del servidor en UTC                                             |
| `account_margin_free`                    | `double`                    | `float`     | Margen libre disponible (en la divisa del depósito)                         |
| `account_margin_level`                   | `double`                    | `float`     | Nivel de margen en porcentaje                                               |
| `account_margin_mode`                    | `MrpcEnumAccountMarginMode` | `int`       | Modo de cálculo del margen                                                  |
| `account_trade_allowed`                  | `bool`                      | `bool`      | Indica si se permite operar en la cuenta                                    |
| `account_trade_expert`                   | `bool`                      | `bool`      | Indica si se permite operar mediante Expert Advisors                        |
| `terminal_connected`                     | `bool`                      | `bool`      | Indica si el terminal está conectado al servidor                            |
| `terminal_trade_allowed`                 | `bool`                      | `bool`      | Indica si se permite operar en el terminal                                  |

**Valor devuelto:** el método devuelve un objeto `AccountSummaryData` con todos los campos accesibles como atributos.

---

## 🧱 Enums relacionados (de proto)

> **Nota:** las tablas muestran nombres simplificados de las constantes para facilitar su lectura.
>
> En el código Python, utiliza la ruta completa del enum del módulo account_helper.

### `MrpcEnumAccountTradeMode`

Definido en `mt5-term-api-account-helper.proto`.

| Constante                         | Valor | Descripción           |
| --------------------------------- | ----- | --------------------- |
| `MRPC_ACCOUNT_TRADE_MODE_DEMO`    | 0     | Cuenta demo           |
| `MRPC_ACCOUNT_TRADE_MODE_CONTEST` | 1     | Cuenta de competición |
| `MRPC_ACCOUNT_TRADE_MODE_REAL`    | 2     | Cuenta real           |

**Uso en Python:**

```
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Acceder a las constantes
mode = account_helper_pb2.MRPC_ACCOUNT_TRADE_MODE_DEMO  # = 0

# Comprobar el modo de la cuenta
if summary.account_trade_mode == account_helper_pb2.MRPC_ACCOUNT_TRADE_MODE_REAL:
    print("Cuenta real: ¡opera con precaución!")
```

---

## 🧩 Notas y consejos

- **Método RECOMENDADO:** es la forma más eficiente de obtener información de la cuenta; utilízalo en lugar de realizar múltiples llamadas `account_info_*`.
- **Reconexión automática:** todos los métodos de `MT5Account` incluyen protección integrada contra errores gRPC transitorios, con reconexión automática mediante `execute_with_reconnect`.
- **Timeout predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca un timeout del servidor).
- **Conexión obligatoria:** debes llamar a `connect_by_host_port()` o `connect_by_server_name()` antes de utilizar este método.
- **Información del margen incluida:** este método ya devuelve `account_margin`, `account_margin_free` y `account_margin_level` (además de `account_margin_mode`); no se necesitan llamadas independientes a `account_info_double()` para obtener esos datos.
- **Hora del servidor:** el campo `server_time` es un protobuf Timestamp; conviértelo mediante `.ToDatetime()` o `.seconds`.

---

## 🔗 Ejemplos de uso

### 1) Obtener el resumen completo de la cuenta

```
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

async def main():
    # Crear una instancia de la cuenta
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="your-server.com:443"
    )

    # Conectarse primero
    await account.connect_by_server_name("MetaQuotes-Demo")

    try:
        # Establecer el deadline
        deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

        # Obtener el resumen
        summary = await account.account_summary(deadline=deadline)

        # Acceder a los campos
        print(f"Resumen de la cuenta:")
        print(f"  Login: {summary.account_login}")
        print(f"  Nombre: {summary.account_user_name}")
        print(f"  Saldo: ${summary.account_balance:.2f}")
        print(f"  Patrimonio: ${summary.account_equity:.2f}")
        print(f"  Crédito: ${summary.account_credit:.2f}")
        print(f"  Divisa: {summary.account_currency}")
        print(f"  Apalancamiento: 1:{summary.account_leverage}")
        print(f"  Bróker: {summary.account_company_name}")

        # Modo de trading
        mode_names = {0: "DEMO", 1: "CONTEST", 2: "REAL"}
        mode = mode_names.get(summary.account_trade_mode, "UNKNOWN")
        print(f"  Modo: {mode}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Mostrar la información de la cuenta con formato

```
async def print_account_info(account: MT5Account):
    """Muestra la información de la cuenta con un formato ordenado"""
    summary = await account.account_summary()

    # Determinar el tipo de cuenta
    mode_names = {
        0: "DEMO",
        1: "CONTEST",
        2: "REAL"
    }
    mode = mode_names.get(summary.account_trade_mode, "UNKNOWN")

    # Calcular el beneficio/pérdida flotante
    floating_pnl = summary.account_equity - summary.account_balance

    print(f"\n{'='*60}")
    print(f"INFORMACIÓN DE LA CUENTA")
    print(f"{'='*60}")
    print(f"Cuenta:      #{summary.account_login} ({summary.account_user_name})")
    print(f"Tipo:        {mode}")
    print(f"Bróker:      {summary.account_company_name}")
    print(f"Divisa:      {summary.account_currency}")
    print(f"Apalancamiento: 1:{summary.account_leverage}")
    print(f"")
    print(f"Saldo:       ${summary.account_balance:,.2f}")
    print(f"Crédito:     ${summary.account_credit:,.2f}")
    print(f"Patrimonio:     ${summary.account_equity:,.2f}")
    print(f"Flotante:    ${floating_pnl:+,.2f}")
    print(f"{'='*60}\n")

# Uso:
await print_account_info(account)
```

### 3) Comprobar el estado de la cuenta

```
async def check_account_health(account: MT5Account) -> dict:
    """
    Realiza una comprobación completa del estado de la cuenta.

    Devuelve:
        Un diccionario con métricas de estado e indicadores
    """
    summary = await account.account_summary()

    # Calcular las métricas
    balance = summary.account_balance
    equity = summary.account_equity
    floating_pnl = equity - balance
    pnl_percent = (floating_pnl / balance * 100) if balance > 0 else 0

    # Determinar el estado de la cuenta
    if summary.account_trade_mode == 0:
        account_type = "DEMO"
    elif summary.account_trade_mode == 2:
        account_type = "REAL"
    else:
        account_type = "CONTEST"

    # Evaluación del estado
    if equity > balance and pnl_percent > 5:
        status = "EXCELLENT"
    elif equity > balance:
        status = "HEALTHY"
    elif abs(pnl_percent) < 5:
        status = "NEUTRAL"
    elif pnl_percent < -10:
        status = "CRITICAL"
    else:
        status = "WARNING"

    health = {
        "status": status,
        "account_type": account_type,
        "balance": balance,
        "equity": equity,
        "floating_pnl": floating_pnl,
        "pnl_percent": pnl_percent,
        "leverage": summary.account_leverage,
        "currency": summary.account_currency
    }

    print(f"Estado de la cuenta: {status}")
    print(f"  Saldo: ${balance:,.2f}")
    print(f"  Patrimonio: ${equity:,.2f}")
    print(f"  B/P: ${floating_pnl:+,.2f} ({pnl_percent:+.2f}%)")

    return health

# Uso:
health = await check_account_health(account)
if "CRITICAL" in health["status"]:
    print("[ADVERTENCIA] ¡La cuenta necesita atención!")
```

### 4) Obtener la hora del servidor

```
async def get_server_time(account: MT5Account):
    """Obtiene la hora del servidor y la información de la zona horaria"""
    summary = await account.account_summary()

    # Hora actual del servidor en UTC (sin ambigüedad, con zona horaria)
    from datetime import timezone, timedelta
    server_utc = summary.server_time_utc.ToDatetime(tzinfo=timezone.utc)

    # Desplazamiento de la zona horaria del servidor respecto a UTC
    tz_offset_minutes = summary.utc_timezone_server_time_shift_minutes
    tz_offset_hours = tz_offset_minutes / 60

    # Hora local del servidor = UTC del servidor + desplazamiento
    server_local = server_utc + timedelta(minutes=tz_offset_minutes)

    print(f"Hora del servidor (UTC): {server_utc}")
    print(f"Desplazamiento UTC: {tz_offset_hours:+.1f} horas")
    print(f"Hora local del servidor: {server_local}")

    return server_utc

# Uso:
server_time = await get_server_time(account)
```

### 5) Validar la cuenta antes de operar

```
async def validate_for_trading(account: MT5Account) -> bool:
    """
    Valida si la cuenta está preparada para operar.

    Devuelve:
        True si la cuenta supera todas las comprobaciones
    """
    summary = await account.account_summary()

    # Comprobación 1: Saldo mínimo
    min_balance = 100
    if summary.account_balance < min_balance:
        print(f"[ERROR] Saldo demasiado bajo: ${summary.account_balance:.2f} < ${min_balance}")
        return False

    # Comprobación 2: Patrimonio > Saldo (sin pérdidas importantes)
    if summary.account_equity < summary.account_balance * 0.5:
        pnl = summary.account_equity - summary.account_balance
        print(f"[ERROR] Pérdidas importantes: ${pnl:.2f}")
        return False

    # Comprobación 3: Apalancamiento razonable
    if summary.account_leverage < 10 or summary.account_leverage > 500:
        print(f"[ADVERTENCIA] Apalancamiento inusual: 1:{summary.account_leverage}")

    # Comprobación 4: Divisa compatible
    supported_currencies = ["USD", "EUR", "GBP"]
    if summary.account_currency not in supported_currencies:
        print(f"[ADVERTENCIA] Divisa no compatible: {summary.account_currency}")

    print(f"[OK] Validación de la cuenta superada:")
    print(f"   Saldo: ${summary.account_balance:.2f}")
    print(f"   Patrimonio: ${summary.account_equity:.2f}")
    print(f"   Apalancamiento: 1:{summary.account_leverage}")

    return True

# Uso:
if await validate_for_trading(account):
    # Iniciar el trading
    pass
else:
    print("No se puede operar con esta cuenta")
```

### 6) Registrar el inicio de la sesión

```
import logging
from datetime import datetime

async def log_session_start(account: MT5Account):
    """Registra el inicio de la sesión con todos los detalles de la cuenta"""
    summary = await account.account_summary()

    # Configurar el registro
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Obtener el nombre del modo
    mode_names = {0: "DEMO", 1: "CONTEST", 2: "REAL"}
    mode = mode_names.get(summary.account_trade_mode, "UNKNOWN")

    # Registrar la información de la sesión
    logging.info("=" * 60)
    logging.info("SESIÓN DE TRADING INICIADA")
    logging.info(f"Cuenta: #{summary.account_login} ({summary.account_user_name})")
    logging.info(f"Bróker: {summary.account_company_name}")
    logging.info(f"Modo: {mode}")
    logging.info(f"Saldo: {summary.account_balance:.2f} {summary.account_currency}")
    logging.info(f"Apalancamiento: 1:{summary.account_leverage}")

    # Hora del servidor
    server_time = summary.server_time.ToDatetime()
    logging.info(f"Hora del servidor: {server_time}")
    logging.info("=" * 60)

# Uso:
await log_session_start(account)
```

### 7) Supervisar el patrimonio de la cuenta

```
async def monitor_equity(account: MT5Account, interval: float = 10.0):
    """
    Supervisa los cambios en el patrimonio de la cuenta.

    Args:
        account: Instancia de MT5Account
        interval: Intervalo de actualización en segundos
    """
    previous_equity = None

    while True:
        try:
            summary = await account.account_summary()

            equity = summary.account_equity
            balance = summary.account_balance
            floating = equity - balance

            # Calcular el cambio
            if previous_equity is not None:
                change = equity - previous_equity
                change_pct = (change / previous_equity * 100) if previous_equity > 0 else 0

                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Patrimonio: ${equity:,.2f} | "
                      f"Flotante: ${floating:+,.2f} | "
                      f"Cambio: ${change:+.2f} ({change_pct:+.2f}%)")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Patrimonio: ${equity:,.2f} | "
                      f"Flotante: ${floating:+,.2f}")

            previous_equity = equity

        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(interval)

# Uso:
# await monitor_equity(account, interval=10.0)  # Actualizar cada 10 segundos
```

### 8) Comparar varias cuentas

```
from dataclasses import dataclass

@dataclass
class AccountSummary:
    login: int
    name: str
    balance: float
    equity: float
    leverage: int
    currency: str
    mode: str

async def compare_accounts(accounts: list[MT5Account]) -> list[AccountSummary]:
    """
    Obtiene los resúmenes de varias cuentas.

    Args:
        accounts: Lista de instancias de MT5Account

    Returns:
        Lista de objetos AccountSummary
    """
    mode_names = {0: "DEMO", 1: "CONTEST", 2: "REAL"}
    summaries = []

    for account in accounts:
        summary = await account.account_summary()

        summaries.append(AccountSummary(
            login=summary.account_login,
            name=summary.account_user_name,
            balance=summary.account_balance,
            equity=summary.account_equity,
            leverage=summary.account_leverage,
            currency=summary.account_currency,
            mode=mode_names.get(summary.account_trade_mode, "UNKNOWN")
        ))

    # Mostrar la comparación
    print("\nComparación de cuentas:")
    print("-" * 80)
    for s in summaries:
        pnl = s.equity - s.balance
        print(f"#{s.login:10} | {s.name:20} | {s.mode:8} | "
              f"${s.balance:10,.2f} | ${s.equity:10,.2f} | ${pnl:+10,.2f}")
    print("-" * 80)

    return summaries

# Uso:
# account1 = MT5Account(...)
# account2 = MT5Account(...)
# summaries = await compare_accounts([account1, account2])
```

---

## Patrones habituales

### Comprobación de inicialización de la cuenta

```
async def initialize_account(account: MT5Account):
    """Inicializa y valida la conexión de la cuenta"""
    # Conectar
    await account.connect_by_server_name("MetaQuotes-Demo")

    # Obtener el resumen para verificar la conexión
    summary = await account.account_summary()

    print(f"[OK] Conectado a la cuenta #{summary.account_login}")
    print(f"   Saldo: ${summary.account_balance:.2f} {summary.account_currency}")

    # Devolver el resumen para su uso posterior
    return summary
```

### Evaluación del riesgo

```
async def assess_trading_risk(account: MT5Account) -> str:
    """Evalúa el nivel de riesgo del trading"""
    summary = await account.account_summary()

    # Calcular los factores de riesgo
    balance = summary.account_balance
    equity = summary.account_equity
    leverage = summary.account_leverage

    # Puntuación de riesgo
    if leverage > 200:
        risk = "HIGH"
    elif leverage > 100:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # Comprobar las pérdidas actuales
    if equity < balance * 0.9:
        risk = "HIGH"

    print(f"Evaluación del riesgo: {risk}")
    print(f"  Apalancamiento: 1:{leverage}")
    print(f"  Saldo: ${balance:.2f}")
    print(f"  Patrimonio: ${equity:.2f}")

    return risk
```

---

## 📚 Véase también

- account_info_double - Obtener propiedades double específicas de la cuenta (margen, etc.).
- account_info_integer - Obtener propiedades integer específicas de la cuenta.
- account_info_string - Obtener propiedades string específicas de la cuenta.

Corrige el manejo del deadline y los importsAclara la conversión de la hora del servidor