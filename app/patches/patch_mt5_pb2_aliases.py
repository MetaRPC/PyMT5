"""
╔══════════════════════════════════════════════════════════════╗
║ pb2 alias shim for MetaRpcMT5                                ║
╠══════════════════════════════════════════════════════════════╣
║ Purpose                                                      ║
║   Make pb2/_grpc submodules accessible as attributes of the  ║
║   MetaRpcMT5 package and provide a few compatibility aliases.║
║ What it fixes                                                ║
║   • Enables `from MetaRpcMT5 import mt5_term_api_*_pb2`      ║
║   • Adds AccountHelperServiceStub → AccountHelperStub alias  ║
║   • Re-exports request classes (market/account-info → helper)║
║ Safety                                                       ║
║   Best-effort: all failures are swallowed. No I/O.           ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
import importlib

def _expose(pkg_name: str, attr: str, fqmod: str) -> None:
    """
    Bind module `fqmod` as attribute `attr` on package `pkg_name`, if missing.
    This lets code do: `from MetaRpcMT5 import mt5_term_api_session_pb2`.
    """
    try:
        pkg = importlib.import_module(pkg_name)
        mod = importlib.import_module(fqmod)
        if getattr(pkg, attr, None) is None:
            setattr(pkg, attr, mod)
    except Exception:
        # Soft-fail: different wheels may not ship all modules
        pass

def apply_patch() -> None:
    """Apply all pb2/_grpc exposure and aliasing tweaks."""
    # 1) Expose common pb2/_grpc modules as attributes of MetaRpcMT5
    for m in [
        "mt5_term_api_session_pb2",
        "mt5_term_api_terminal_pb2",
        "mt5_term_api_account_helper_pb2",
        "mt5_term_api_account_helper_pb2_grpc",
        "mt5_term_api_market_info_pb2",
        "mt5_term_api_market_info_pb2_grpc",
        "mt5_term_api_account_information_pb2",
    ]:
        _expose("MetaRpcMT5", m, f"MetaRpcMT5.{m}")

    # 2) Alias: AccountHelperServiceStub → AccountHelperStub (if only the latter exists)
    try:
        ah_grpc = importlib.import_module("MetaRpcMT5.mt5_term_api_account_helper_pb2_grpc")
        if not hasattr(ah_grpc, "AccountHelperServiceStub") and hasattr(ah_grpc, "AccountHelperStub"):
            ah_grpc.AccountHelperServiceStub = ah_grpc.AccountHelperStub
    except Exception:
        # Some builds might miss *_grpc or have different names — ignore
        pass

    # 3) Re-export request classes onto account_helper pb2 for compatibility
    #    (so callers can always import requests from `...account_helper_pb2`)
    try:
        ah = importlib.import_module("MetaRpcMT5.mt5_term_api_account_helper_pb2")
        mi = importlib.import_module("MetaRpcMT5.mt5_term_api_market_info_pb2")
        ai = importlib.import_module("MetaRpcMT5.mt5_term_api_account_information_pb2")
    except Exception:
        return  # If any of these aren't present, we simply stop here

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
