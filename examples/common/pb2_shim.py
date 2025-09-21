# pb2_shim.py
# Purpose: make request classes available under account_helper_pb2 and fix minor aliasing
from __future__ import annotations
import importlib

def _expose(pkg_name: str, attr: str, fqmod: str) -> None:
    """Bind module `fqmod` as attribute `attr` on the package."""
    try:
        pkg = importlib.import_module(pkg_name)
        mod = importlib.import_module(fqmod)
        if getattr(pkg, attr, None) is None:
            setattr(pkg, attr, mod)
    except Exception:
        # Soft-fail: different wheels may not ship all modules
        pass

def apply_patch() -> None:
    """Expose pb2/_grpc modules and re-export request classes onto account_helper_pb2."""
    # 1) Expose most-used modules as attributes of MetaRpcMT5 (best-effort)
    for m in [
        "mt5_term_api_account_helper_pb2",
        "mt5_term_api_account_helper_pb2_grpc",
        "mt5_term_api_market_info_pb2",
        "mt5_term_api_market_info_pb2_grpc",
        "mt5_term_api_account_information_pb2",
        "mt5_term_api_account_information_pb2_grpc",
    ]:
        _expose("MetaRpcMT5", m, f"MetaRpcMT5.{m}")

    # 2) Alias: AccountHelperServiceStub → AccountHelperStub when only the latter exists
    try:
        ah_grpc = importlib.import_module("MetaRpcMT5.mt5_term_api_account_helper_pb2_grpc")
        if not hasattr(ah_grpc, "AccountHelperServiceStub") and hasattr(ah_grpc, "AccountHelperStub"):
            ah_grpc.AccountHelperServiceStub = ah_grpc.AccountHelperStub
    except Exception:
        pass

    # 3) Re-export request classes so callers can import them from account_helper_pb2
    try:
        ah = importlib.import_module("MetaRpcMT5.mt5_term_api_account_helper_pb2")
        mi = importlib.import_module("MetaRpcMT5.mt5_term_api_market_info_pb2")
        ai = importlib.import_module("MetaRpcMT5.mt5_term_api_account_information_pb2")
    except Exception:
        return  # If any is missing, do nothing

    # MarketInfo → AccountHelper request aliases
    market_req_names = [
        "SymbolsTotalRequest", "SymbolExistRequest", "SymbolNameRequest", "SymbolSelectRequest",
        "SymbolInfoTickRequest", "SymbolInfoDoubleRequest", "SymbolInfoIntegerRequest", "SymbolInfoStringRequest",
        "SymbolInfoMarginRateRequest", "SymbolInfoSessionQuoteRequest", "SymbolInfoSessionTradeRequest",
        "SymbolIsSynchronizedRequest", "MarketBookAddRequest", "MarketBookGetRequest", "MarketBookReleaseRequest",
    ]
    for name in market_req_names:
        try:
            if not hasattr(ah, name) and hasattr(mi, name):
                setattr(ah, name, getattr(mi, name))
        except Exception:
            pass

    # AccountInformation → AccountHelper request aliases
    account_info_req_names = [
        "AccountInfoDoubleRequest", "AccountInfoIntegerRequest", "AccountInfoStringRequest",
    ]
    for name in account_info_req_names:
        try:
            if not hasattr(ah, name) and hasattr(ai, name):
                setattr(ah, name, getattr(ai, name))
        except Exception:
            pass
