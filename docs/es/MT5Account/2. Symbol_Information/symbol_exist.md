# Comprobar si existe un símbolo

> **Solicitud:** comprobar si existe en la plataforma de trading un símbolo con el nombre especificado.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_exist(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolExist` (definido en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolExist(SymbolExistRequest) -> SymbolExistReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolExist(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es:** permite comprobar si un símbolo existe y determinar si es estándar o personalizado.
- **Por qué lo necesitas:** valida los nombres de los símbolos antes de realizar operaciones o consultar datos.
- **Cuándo utilizarlo:** antes de operar o suscribirse a los datos de un símbolo.

---

## 🎯 Propósito

Utiliza este método para validar símbolos:

- Comprobar si un símbolo existe en la plataforma.
- Identificar si un símbolo es estándar o personalizado.
- Validar los datos introducidos por el usuario.
- Evitar errores al consultar símbolos inexistentes.
- Realizar validaciones antes de ejecutar operaciones.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea, con ejemplos, consulta:

**-> [symbol_exist - Cómo funciona](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_exist_HOW.md)**

---

## Firma del método

```python
async def symbol_exist(
    self,
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
)
```

**Mensaje de solicitud:**

```protobuf
message SymbolExistRequest {
  string name = 1;
}
```

**Mensaje de respuesta:**

```protobuf
message SymbolExistReply {
  oneof response {
    SymbolExistData data = 1;
    Error error = 2;
  }
}

message SymbolExistData {
  bool exists = 1;
  bool is_custom = 2;
}
```

---

## 🔽 Parámetros de entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `symbol` | `str` (obligatorio) | Nombre del símbolo que se desea comprobar. |
| `deadline` | `datetime` (opcional) | Fecha y hora límite de la llamada gRPC. Debe ser un objeto `datetime` con zona horaria UTC. |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento que permite cancelar la operación. |

**Gestión de `deadline`:**

Para crear un plazo límite válido, utiliza una fecha y hora UTC con zona horaria explícita:

```python
from datetime import datetime, timedelta, timezone

deadline = datetime.now(timezone.utc) + timedelta(seconds=10)
```

No utilices `datetime.now()` sin `timezone.utc`, ya que genera un objeto `datetime` sin información de zona horaria.

Si no necesitas establecer un límite de tiempo explícito, puedes omitir `deadline` y utilizar su valor predeterminado `None`.

---

## ⬆️ Parámetros de salida - `SymbolExistData`

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `exists` | `bool` | `bool` | `True` si el símbolo existe. |
| `is_custom` | `bool` | `bool` | `True` si el símbolo es personalizado y no estándar. |

---

## 🧩 Notas y consejos

- **Reconexión automática:** protección integrada contra errores gRPC transitorios.
- **Distingue mayúsculas y minúsculas:** los nombres de los símbolos distinguen entre mayúsculas y minúsculas.
- **Deadline:** cuando se especifica, debe ser un objeto `datetime` con zona horaria UTC.
- **Cancelación:** `cancellation_event` permite solicitar la cancelación de la operación mediante `asyncio.Event`.

---

## 🔗 Ejemplos de uso

### 1) Comprobar si existe un símbolo

```python
import asyncio
from datetime import datetime, timedelta, timezone

from MetaRpcMT5 import MT5Account


async def main():
    account = MT5Account(...)
    await account.connect_by_server_name("MetaQuotes-Demo")

    deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

    data = await account.symbol_exist(
        symbol="EURUSD",
        deadline=deadline,
    )

    if data.exists:
        symbol_type = "custom" if data.is_custom else "standard"
        print(f"[OK] EURUSD existe ({symbol_type})")
    else:
        print("[ERROR] EURUSD no existe")


if __name__ == "__main__":
    asyncio.run(main())
```

### 2) Validar un símbolo antes de operar

```python
import asyncio
from datetime import datetime, timedelta, timezone

from MetaRpcMT5 import MT5Account


async def validate_symbol(account: MT5Account, symbol: str) -> bool:
    """Valida que el símbolo exista antes de operar."""

    deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

    data = await account.symbol_exist(
        symbol=symbol,
        deadline=deadline,
    )

    if not data.exists:
        print(f"[ERROR] El símbolo {symbol} no existe")
        return False

    print(f"[OK] Símbolo {symbol} validado")
    return True


# Uso:
async def main():
    account = MT5Account(...)
    await account.connect_by_server_name("MetaQuotes-Demo")

    if await validate_symbol(account, "EURUSD"):
        # Ejecutar una operación
        pass


if __name__ == "__main__":
    asyncio.run(main())
```

### 3) Comprobar varios símbolos

```python
import asyncio
from datetime import datetime, timedelta, timezone

from MetaRpcMT5 import MT5Account


async def check_symbols(account: MT5Account, symbols: list[str]):
    """Comprueba qué símbolos existen."""

    results = {}

    for symbol in symbols:
        deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

        data = await account.symbol_exist(
            symbol=symbol,
            deadline=deadline,
        )

        results[symbol] = data.exists

    # Mostrar los resultados
    for symbol, exists in results.items():
        status = "[OK]" if exists else "[ERROR]"
        print(f"{status} {symbol}: {'existe' if exists else 'no encontrado'}")

    return results


# Uso:
async def main():
    account = MT5Account(...)
    await account.connect_by_server_name("MetaQuotes-Demo")

    symbols = ["EURUSD", "GBPUSD", "INVALID"]
    await check_symbols(account, symbols)


if __name__ == "__main__":
    asyncio.run(main())
```

### 4) Filtrar símbolos válidos

```python
import asyncio
from datetime import datetime, timedelta, timezone

from MetaRpcMT5 import MT5Account


async def filter_valid_symbols(
    account: MT5Account,
    symbols: list[str]
) -> list[str]:
    """Filtra los símbolos que no existen."""

    valid_symbols = []

    for symbol in symbols:
        deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

        data = await account.symbol_exist(
            symbol=symbol,
            deadline=deadline,
        )

        if data.exists:
            valid_symbols.append(symbol)

    print(f"[OK] {len(valid_symbols)} de {len(symbols)} símbolos son válidos")

    return valid_symbols


# Uso:
async def main():
    account = MT5Account(...)
    await account.connect_by_server_name("MetaQuotes-Demo")

    symbols = ["EURUSD", "GBPUSD", "INVALID_SYMBOL"]
    valid = await filter_valid_symbols(account, symbols)


if __name__ == "__main__":
    asyncio.run(main())
```

### 5) Identificar símbolos personalizados

```python
import asyncio
from datetime import datetime, timedelta, timezone

from MetaRpcMT5 import MT5Account


async def get_symbol_type(account: MT5Account, symbol: str) -> str:
    """Obtiene el tipo de símbolo (estándar, personalizado o inexistente)."""

    deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

    data = await account.symbol_exist(
        symbol=symbol,
        deadline=deadline,
    )

    if not data.exists:
        return "not_found"

    return "custom" if data.is_custom else "standard"


# Uso:
async def main():
    account = MT5Account(...)
    await account.connect_by_server_name("MetaQuotes-Demo")

    symbol_type = await get_symbol_type(account, "EURUSD")
    print(f"Tipo de EURUSD: {symbol_type}")


if __name__ == "__main__":
    asyncio.run(main())
```

### 6) Cancelar una operación mediante `cancellation_event`

```python
import asyncio
from datetime import datetime, timedelta, timezone

from MetaRpcMT5 import MT5Account


async def check_symbol_with_cancellation(
    account: MT5Account,
    symbol: str,
) -> None:
    """Comprueba un símbolo con posibilidad de cancelar la operación."""

    cancellation_event = asyncio.Event()
    deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

    data = await account.symbol_exist(
        symbol=symbol,
        deadline=deadline,
        cancellation_event=cancellation_event,
    )

    if data.exists:
        print(f"[OK] El símbolo {symbol} existe")
    else:
        print(f"[ERROR] El símbolo {symbol} no existe")


# Uso:
async def main():
    account = MT5Account(...)
    await account.connect_by_server_name("MetaQuotes-Demo")

    await check_symbol_with_cancellation(account, "EURUSD")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Patrones comunes

### Comprobación rápida de existencia

```python
import asyncio

from MetaRpcMT5 import MT5Account


async def symbol_exists(account: MT5Account, symbol: str) -> bool:
    """Comprueba rápidamente si existe un símbolo."""

    data = await account.symbol_exist(symbol=symbol)

    return data.exists
```

---

## 📚 Véase también

- [symbols_total](./symbols_total.md) - Obtener el número total de símbolos.
- [symbol_name](./symbol_name.md) - Obtener el nombre de un símbolo mediante su índice.
- [symbol_select](./symbol_select.md) - Añadir o eliminar un símbolo de Market Watch.