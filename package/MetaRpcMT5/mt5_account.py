# MT5Account public entry point.
#
# The maintained implementation lives in MetaRpcMT5.helpers.mt5_account and is the
# single source of truth. This module previously held a second, standalone copy of
# MT5Account that had drifted out of sync with the generated protobuf types (wrong
# modules/field names, missing api_key, missing methods), so it is now a thin
# re-export of the helpers implementation to avoid any divergence.
from .helpers.mt5_account import MT5Account, ConnectExceptionMT5, ApiExceptionMT5

__all__ = ["MT5Account", "ConnectExceptionMT5", "ApiExceptionMT5"]
