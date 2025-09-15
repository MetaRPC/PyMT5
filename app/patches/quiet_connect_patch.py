# app/patches/quiet_connect_patch.py
"""
╔════════════════════════════════════════════════════╗
║ Quiet connect patch for MT5Service                 ║
╠════════════════════════════════════════════════════╣
║ Purpose  Suppress noisy internal "[connect]" logs  ║
║ Trigger  Active by import. Set MT5_VERBOSE=1 to    ║
║          allow full connect logs.                  ║
║ Safety   Best-effort monkey-patch; restores print  ║
║          after call. No behavior changes otherwise.║
╚════════════════════════════════════════════════════╝
"""
from __future__ import annotations
import os
import builtins

try:
    from app.core.mt5_service import MT5Service  # type: ignore
except Exception:
    MT5Service = None

if MT5Service:
    _old_connect = MT5Service.connect

    async def _connect_quiet(self, *a, **k):
        """
        Wrapper around MT5Service.connect():
        - If MT5_VERBOSE in {"1","true","True"} → passthrough (verbose).
        - Otherwise, temporarily silence lines starting with "[connect]".
        """
        verbose = os.getenv("MT5_VERBOSE", "0") in ("1", "true", "True")
        if verbose:
            return await _old_connect(self, *a, **k)

        # Save original print and replace it with a filter that drops connect-noise.
        orig_print = builtins.print

        def quiet_print(*args, **kwargs):
            # Drop only internal connect traces; keep all other output intact.
            if args and isinstance(args[0], str) and args[0].startswith("[connect]"):
                return
            return orig_print(*args, **kwargs)

        builtins.print = quiet_print
        try:
            return await _old_connect(self, *a, **k)
        finally:
            # Always restore original print, even if connect raises.
            builtins.print = orig_print

    # Monkey-patch the method on import (idempotent overwrite).
    MT5Service.connect = _connect_quiet
