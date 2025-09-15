# Re-exports to keep old imports working:
from .core.config import MT5Config
from .core.mt5_service import MT5Service
from .core.constants import ORDER_MAP  


from .services.trading_service import *   # noqa
from .services.history_service import *   
from .services.streams_service import *   
from .calc.mt5_calc import patch_mt5_calculator  

__all__ = [
    "MT5Config", "MT5Service", "ORDER_MAP",
    "patch_mt5_calculator",
]
