"""
╔══════════════════════════════════════════════════════════════╗
║ FILE app/mt5_bind_patch.py                                   ║
╠══════════════════════════════════════════════════════════════╣
║ Purpose                                                      ║
║   Centralized binder/patcher that runs on import.            ║
║   • Adds calculator helpers to MT5Service (order_calc_*).    ║
║   • Binds selected module-level helpers onto MT5Service.     ║
║                                                              ║
║ When                                                         ║
║   Imported once by main.py; effects are immediate.           ║
║                                                              ║
║ Behavior & Safety                                            ║
║   • Idempotent: re-import just reassigns attributes.         ║
║   • Missing helpers are skipped silently (callable check).   ║
║   • May overwrite same-named MT5Service methods (by design). ║
║   • No I/O; only mutates the class shape.                    ║
║                                                              ║
║ Usage                                                        ║
║   from app.patches import mt5_bind_patch  # side-effects only║
╚══════════════════════════════════════════════════════════════╝
"""

# comments in English only
from __future__ import annotations

# correct class import from core
from ..core.mt5_service import MT5Service

# calculator patch is optional — don't crash if missing
try:
    # ✅ real location is app/calc/mt5_calc.py
    from ..calc.mt5_calc import patch_mt5_calculator
except Exception:
    patch_mt5_calculator = None

# attach calc helpers if present
if callable(patch_mt5_calculator):
    patch_mt5_calculator(MT5Service)

# re-importing the module with helpers (copy_* / market_book_get / symbol_select)
# ✅ module is app/core/mt5_service.py
from ..core import mt5_service as _mod

# Bind selected module-level helpers (monkey-patch if present)
for _name in ("copy_rates_range", "copy_rates_from_pos", "copy_ticks_range",
              "market_book_get", "symbol_select"):
    _fn = getattr(_mod, _name, None)
    if callable(_fn):
        setattr(MT5Service, _name, _fn)  # overwrites if already defined





