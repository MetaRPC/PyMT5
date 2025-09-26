# pb2_shim.py
# Purpose: make request classes available under account_helper_pb2 and fix minor aliasing
from __future__ import annotations

import importlib
from types import ModuleType
from typing import Iterable, Optional


def _try_import(fqmod: str) -> Optional[ModuleType]:
    """Import module by fully qualified name. Return None if not available."""
    try:
        return importlib.import_module(fqmod)
    except Exception:
        return None


def _expose(pkg_name: str, attr: str, fqmod: str) -> None:
    """
    Bind module `fqmod` as attribute `attr` on package `pkg_name`, if not already set.
    Soft-fails if the package or module is missing.
    """
    try:
        pkg = importlib.import_module(pkg_name)
        mod = importlib.import_module(fqmod)
        if getattr(pkg, attr, None) is None:
            setattr(pkg, attr, mod)
    except Exception:
        # Soft-fail: different wheels may not ship all modules
        pass


def _alias_list(dst_mod: ModuleType, src_mod: ModuleType, names: Iterable[str]) -> None:
    """
    For each name in `names`: if absent in dst_mod and present in src_mod, copy it.
    Never overwrites existing attributes.
    """
    if dst_mod is None or src_mod is None:
        return
    for name in names:
        try:
            if not hasattr(dst_mod, name) and hasattr(src_mod, name):
                setattr(dst_mod, name, getattr(src_mod, name))
        except Exception:
            # Keep going even if a single attribute copy fails
            pass


def apply_patch() -> None:
    """
    Expose pb2/_grpc modules under MetaRpcMT5 and re-export request classes
    onto account_helper_pb2 so code can do:
        from MetaRpcMT5.mt5_term_api_account_helper_pb2 import SymbolSelectRequest
    even when the request types actually live in market_info_pb2.
    """
    # 1) Expose commonly used modules as attributes of MetaRpcMT5 (best-effort)
    for m in [
        "mt5_term_api_account_helper_pb2",
        "mt5_term_api_account_helper_pb2_grpc",
        "mt5_term_api_market_info_pb2",
        "mt5_term_api_market_info_pb2_grpc",
        "mt5_term_api_account_information_pb2",
        "mt5_term_api_account_information_pb2_grpc",
        # keep trading helper visible as well; not strictly needed for aliasing below
        "mt5_term_api_trading_helper_pb2",
        "mt5_term_api_trading_helper_pb2_grpc",
    ]:
        _expose("MetaRpcMT5", m, f"MetaRpcMT5.{m}")

    # 2) Stub aliasing variations (AccountHelperServiceStub vs AccountHelperStub)
    try:
        ah_grpc = importlib.import_module("MetaRpcMT5.mt5_term_api_account_helper_pb2_grpc")
        # If only AccountHelperStub exists, alias ServiceStub to it
        if not hasattr(ah_grpc, "AccountHelperServiceStub") and hasattr(ah_grpc, "AccountHelperStub"):
            ah_grpc.AccountHelperServiceStub = ah_grpc.AccountHelperStub
        # If only AccountHelperServiceStub exists, alias Stub to it (reverse case)
        if not hasattr(ah_grpc, "AccountHelperStub") and hasattr(ah_grpc, "AccountHelperServiceStub"):
            ah_grpc.AccountHelperStub = ah_grpc.AccountHelperServiceStub
    except Exception:
        pass

    # 3) Re-export request classes so callers can import them from account_helper_pb2
    # Do not bail out if some modules are missing — alias whatever is available.
    ah = _try_import("MetaRpcMT5.mt5_term_api_account_helper_pb2")
    if ah is None:
        # Nothing we can alias onto; exit quietly
        return

    mi = _try_import("MetaRpcMT5.mt5_term_api_market_info_pb2")
    ai = _try_import("MetaRpcMT5.mt5_term_api_account_information_pb2")

    # MarketInfo → AccountHelper request aliases
    _alias_list(
        ah,
        mi,
        names=[
            "SymbolsTotalRequest",
            "SymbolExistRequest",
            "SymbolNameRequest",
            "SymbolSelectRequest",
            "SymbolInfoTickRequest",
            "SymbolInfoDoubleRequest",
            "SymbolInfoIntegerRequest",
            "SymbolInfoStringRequest",
            "SymbolInfoMarginRateRequest",
            "SymbolInfoSessionQuoteRequest",
            "SymbolInfoSessionTradeRequest",
            "SymbolIsSynchronizedRequest",
            "MarketBookAddRequest",
            "MarketBookGetRequest",
            "MarketBookReleaseRequest",
        ],
    )

    # AccountInformation → AccountHelper request aliases
    _alias_list(
        ah,
        ai,
        names=[
            "AccountInfoDoubleRequest",
            "AccountInfoIntegerRequest",
            "AccountInfoStringRequest",
        ],
    )

    # Done. This function is idempotent and safe to call repeatedly.
