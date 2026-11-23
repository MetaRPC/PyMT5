# Obtener propiedades de tipo cadena de la cuenta

> **Solicitud:** Obtener una propiedad específica de tipo cadena del terminal **MT5** mediante el identificador de propiedad.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.account_info_string(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.AccountInformation`
- **Definición Proto:** `AccountInfoString` (definido en `mt5-term-api-account-information.proto`)

### RPC

- **Servicio:** `mt5_term_api.AccountInformation`
- **Método:** `AccountInfoString(AccountInfoStringRequest) -> AccountInfoStringReply`
- **Cliente de bajo nivel (generado):** `AccountInformationStub.AccountInfoString(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Recupera una propiedad específica de tipo cadena de la cuenta mediante su ID (nombre, servidor, divisa, empresa).
- **Por qué lo necesitas.** Permite obtener propiedades de texto individuales de la cuenta sin recuperar todos los datos. Es útil para registros y configuración.
- **Cuándo utilizarlo.** Utiliza `account_summary()` para obtener varias propiedades. Utiliza este método para consultar una sola propiedad.

---

## 🎯 Propósito

Utiliza este método para consultar propiedades específicas de tipo cadena de la cuenta:

- Obtener el nombre del titular de la cuenta.
- Obtener el nombre del servidor de trading.
- Obtener la divisa de la cuenta (USD, EUR, etc.).
- Obtener el nombre del bróker o de la empresa.
- Comprobar que la cuenta está conectada al servidor esperado.
- Registrar los detalles de la cuenta en los logs.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [account_info_string - Cómo funciona](../HOW_IT_WORK/1. Account_information_HOW/account_info_string_HOW.md)**

---

## Firma del método

```python
async def account_info_string(
    self,
    property_id: account_info_pb2.AccountInfoStringPropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> str
```

**Mensaje de solicitud:**

```protobuf
message AccountInfoStringRequest {
    AccountInfoStringPropertyType property_id = 1;
}
```

**Mensaje de respuesta:**

```protobuf
message AccountInfoStringReply {
    oneof response {
        AccountInfoStringData data = 1;
        Error error = 2;
    }
}

message AccountInfoStringData {
    string requested_value = 1;
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
| ------------- | --------------------------------- | ------------------------------------------------------- |
| `property_id` | `AccountInfoStringPropertyType` (enum) | Identificador de la propiedad que especifica qué propiedad se debe recuperar |
| `deadline` | `datetime` (opcional) | Plazo límite para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

**Opciones de plazo:**

```python
from datetime import datetime, timedelta, timezone
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# 1. Con plazo (recomendado)
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
value = await account.account_info_string(
    property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
    deadline=deadline
)

# 2. Con evento de cancelación
cancel_event = asyncio.Event()
value = await account.account_info_string(
    property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
    cancellation_event=cancel_event
)

# 3. Sin plazo (se aplicará el tiempo de espera predeterminado si está configurado)
value = await account.account_info_string(
    property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY
)
```

---

## ⬆️ Salida

| Campo | Tipo | Tipo de Python | Descripción |
| ----------------- | -------- | ----------- | ------------------------------------------------ |
| `requested_value` | `string` | `str` | Valor de la propiedad solicitada de la cuenta |

**Valor de retorno:** El método devuelve directamente un `str` (extraído de `AccountInfoStringData.requested_value`).

---

## 🧱 Enumeraciones relacionadas (del proto)

> **Nota:** En el código Python, se recomienda utilizar la ruta completa de la clase enum para garantizar la seguridad de tipos y una mayor claridad.
>
> **Recomendado:** `account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY`
>
> **También válido:** `account_info_pb2.ACCOUNT_CURRENCY` (acceso directo)
>
> Recomendamos el **formato completo** para mejorar la compatibilidad con el IDE y evitar confusiones entre diferentes tipos de propiedades.

### `AccountInfoStringPropertyType`

Definido en `mt5-term-api-account-information.proto`.

| Constante | Valor | Descripción |
|----------|-------|-------------|
| `ACCOUNT_NAME` | 0 | Nombre del cliente |
| `ACCOUNT_SERVER` | 1 | Nombre del servidor de trading |
| `ACCOUNT_CURRENCY` | 2 | Divisa de la cuenta (USD, EUR, etc.) |
| `ACCOUNT_COMPANY` | 3 | Nombre de la empresa o del bróker de la cuenta |

**Uso en Python:**

```python
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# Recomendado: utilizar la ruta completa de la clase enum
property_id = account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY  # = 2

# También válido: acceso directo (aunque es menos claro)
property_id = account_info_pb2.ACCOUNT_CURRENCY  # = 2
```

---

## 🧩 Notas y consejos

- **Preferir account_summary:** Para obtener varias propiedades, utiliza `account_summary()` en su lugar y evita múltiples viajes de ida y vuelta al servidor.
- **Conexión obligatoria:** Debes llamar a `connect_by_host_port()` o `connect_by_server_name()` antes de utilizar este método.
- **Formato de divisa:** La divisa se devuelve como un código de 3 letras (USD, EUR, GBP, etc.).

---

## 🔗 Ejemplos de uso

### 1) Obtener la divisa de la cuenta

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

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

        # Obtener la divisa
        currency = await account.account_info_string(
            property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
            deadline=deadline
        )

        print(f"Divisa de la cuenta: {currency}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Obtener el nombre del titular de la cuenta

```python
async def get_account_name(account: MT5Account) -> str:
    """Obtener el nombre del titular de la cuenta"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    name = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline=deadline
    )

    return name

# Uso:
name = await get_account_name(account)
print(f"Nombre de la cuenta: {name}")
```

### 3) Obtener el nombre del servidor de trading

```python
async def get_server_name(account: MT5Account) -> str:
    """Obtener el nombre del servidor de trading"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    server = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline=deadline
    )

    return server

# Uso:
server = await get_server_name(account)
print(f"Servidor de trading: {server}")
```

### 4) Obtener el nombre de la empresa del bróker

```python
async def get_broker_name(account: MT5Account) -> str:
    """Obtener el nombre del bróker/empresa"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    company = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline=deadline
    )

    return company

# Uso:
broker = await get_broker_name(account)
print(f"Bróker: {broker}")
```

### 5) Registrar los detalles de la cuenta

```python
async def log_account_details(account: MT5Account):
    """Registrar todas las propiedades de tipo cadena de la cuenta"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

    # Obtener todas las propiedades de tipo cadena
    name = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline
    )

    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline
    )

    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
        deadline
    )

    company = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline
    )

    # Registrar los detalles
    print(f"=" * 50)
    print(f"Detalles de la cuenta:")
    print(f"  Titular: {name}")
    print(f"  Servidor: {server}")
    print(f"  Divisa: {currency}")
    print(f"  Bróker: {company}")
    print(f"=" * 50)

# Uso:
await log_account_details(account)
```

### 6) Comprobar que la cuenta está conectada al servidor esperado

```python
async def verify_server_connection(account: MT5Account, expected_server: str) -> bool:
    """
    Verificar que estamos conectados al servidor esperado.

    Argumentos:
        account: Instancia de MT5Account
        expected_server: Nombre del servidor esperado

    Devuelve:
        True si estamos conectados al servidor correcto
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    server = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline=deadline
    )

    if server.lower() != expected_server.lower():
        print(f"[WARNING] Conectado a {server}, se esperaba {expected_server}")
        return False

    print(f"[OK] Confirmado: Conectado a {server}")
    return True

# Uso:
if not await verify_server_connection(account, "MetaQuotes-Demo"):
    raise RuntimeError("¡Servidor incorrecto!")
```

### 7) Formatear según la divisa

```python
async def format_balance(account: MT5Account, balance: float) -> str:
    """
    Formatear el saldo utilizando el símbolo de la divisa de la cuenta.

    Argumentos:
        account: Instancia de MT5Account
        balance: Importe del saldo

    Devuelve:
        Cadena con el saldo formateado
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
        deadline
    )

    # Asignar códigos de divisa a sus símbolos
    currency_symbols = {
        "USD": "$",
        "EUR": "EUR",
        "GBP": "GBP",
        "JPY": "JPY",
        "CHF": "CHF",
        "AUD": "A$",
        "CAD": "C$"
    }

    symbol = currency_symbols.get(currency, currency + " ")

    # Formatear según la divisa
    if currency == "JPY":
        # JPY no utiliza posiciones decimales
        return f"{symbol}{balance:.0f}"
    else:
        return f"{symbol}{balance:.2f}"

# Uso:
balance = 10000.50
formatted = await format_balance(account, balance)
print(f"Saldo: {formatted}")  # Salida: Saldo: $10000.50
```

### 8) Generar la cabecera de sesión

```python
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class SessionInfo:
    timestamp: str
    account_name: str
    broker: str
    server: str
    currency: str

async def get_session_info(account: MT5Account) -> SessionInfo:
    """Obtener información completa de la sesión para los registros"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

    # Obtener todas las propiedades de tipo cadena
    name = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline
    )

    company = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline
    )

    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline
    )

    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
        deadline
    )

    return SessionInfo(
        timestamp=datetime.now().isoformat(),
        account_name=name,
        broker=company,
        server=server,
        currency=currency
    )

# Uso:
session = await get_session_info(account)
print(f"Sesión iniciada: {session.timestamp}")
print(f"Cuenta: {session.account_name}")
print(f"Bróker: {session.broker} ({session.server})")
print(f"Divisa: {session.currency}")
```

---

## Patrones comunes

### Identificación de la cuenta

```python
async def get_account_identifier(account: MT5Account) -> str:
    """
    Generar un identificador único de cuenta para los registros.

    Devuelve:
        Cadena identificadora: "name@server (broker)"
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

    name = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline
    )

    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline
    )

    company = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline
    )

    identifier = f"{name}@{server} ({company})"
    return identifier

# Uso:
account_id = await get_account_identifier(account)
print(f"Operando como: {account_id}")
# Salida: Operando como: John Doe@MetaQuotes-Demo (MetaQuotes Software Corp.)
```

### Validador de divisa

```python
async def validate_account_currency(
    account: MT5Account,
    allowed_currencies: list[str]
) -> bool:
    """
    Validar que la divisa de la cuenta esté incluida en la lista de divisas permitidas.

    Argumentos:
        account: Instancia de MT5Account
        allowed_currencies: Lista de códigos de divisa permitidos (por ejemplo, ["USD", "EUR"])

    Devuelve:
        True si la divisa está permitida
    """
    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY
    )

    if currency not in allowed_currencies:
        print(f"[ERROR] Divisa {currency} no permitida. Permitidas: {allowed_currencies}")
        return False

    print(f"[OK] La divisa {currency} es válida")
    return True

# Uso:
if not await validate_account_currency(account, ["USD", "EUR"]):
    raise ValueError("La divisa de la cuenta no es compatible")
```

### Comprobador del entorno del servidor

```python
async def get_environment(account: MT5Account) -> str:
    """
    Determinar el entorno (producción/demo) según el nombre del servidor.

    Devuelve:
        "PRODUCTION", "DEMO" o "UNKNOWN"
    """
    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER
    )

    server_lower = server.lower()

    if "demo" in server_lower:
        return "DEMO"
    elif "real" in server_lower or "live" in server_lower:
        return "PRODUCTION"
    else:
        return "UNKNOWN"

# Uso:
env = await get_environment(account)
print(f"Entorno: {env}")

if env == "PRODUCTION":
    print("[WARNING] ¡Operando en un servidor de PRODUCCIÓN!")
```

---

## 📚 Véase también

- [account_summary](./account_summary.md) - Obtener todas las propiedades de la cuenta en una sola llamada (RECOMENDADO).
- [account_info_double](./account_info_double.md) - Obtener propiedades específicas de tipo double de la cuenta.
- [account_info_integer](./account_info_integer.md) - Obtener propiedades específicas de tipo integer de la cuenta.