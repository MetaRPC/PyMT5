# app/symbol_params_patch.py
"""
╔══════════════════════════════════════════════════════════╗
║ Symbol params patch for MT5Service                       ║
╠══════════════════════════════════════════════════════════╣
║ Purpose  Add MT5Service.symbol_params_many(symbols)      ║
║ Output   {SYMBOL: {"digits": int|None, "contract_size":  ║
║          float|None}, ...} (keys uppercased)             ║
║ Strategy 1) Batch via AccountHelper gRPC (several RPC    ║
║             name/layout variants)                        ║
║          2) Fallback per-symbol via symbol_info* and     ║
║             symbol_info_double/integer                   ║
║ Safety   Best-effort; tolerant to different pb2 names.   ║
╚══════════════════════════════════════════════════════════╝
"""
from __future__ import annotations
from typing import Any, Optional, Dict, List

import asyncio

# Try to import helper pb2 (names differ across builds)
try:
    from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2  # type: ignore
except Exception:
    try:
        import MetaRpcMT5.mt5_term_api_account_helper_pb2 as ah_pb2  # type: ignore
    except Exception:
        ah_pb2 = None  # type: ignore


def _unbox_num(v: Any) -> float | None:
    """Best-effort numeric extractor from proto wrappers / objects / str."""
    try:
        # Common wrapper fields
        for k in ("value", "double", "number", "val", "Value"):
            if hasattr(v, k):
                v = getattr(v, k)
                break
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            s = v.strip()
            return float(s) if s else None
    except Exception:
        return None
    return None


def _gx(o: Any, *names: str):
    """Get first available attribute/key by a list of candidate names."""
    for n in names:
        if o is None:
            break
        if isinstance(o, dict):
            if n in o:
                return o[n]
        elif hasattr(o, n):
            return getattr(o, n)
    return None


async def symbol_params_many(self, symbols: List[str]) -> Dict[str, Dict]:
    """
    MT5Service API: return minimal per-symbol params {'digits','contract_size'}.
    Plan:
      (1) Try AccountHelper batch RPC (several request/field/method variants).
      (2) Fallback per-symbol via symbol_info* and symbol_info_double/integer.
    """
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")

    # Normalize keys to UPPER for output; input may be any case
    syms_upper = [s.upper() for s in symbols]
    out: Dict[str, Dict] = {s: {"digits": None, "contract_size": None} for s in syms_upper}

    # 1) Batch via AccountHelper, if available
    if ah_pb2 is not None and getattr(acc, "account_helper_client", None):
        # Variants: (request class, list field name, RPC method)
        variants = [
            ("SymbolParamsManyRequest", "symbol_names", "SymbolParamsMany"),
            ("SymbolsParamsRequest",    "symbols",      "SymbolsParams"),
            ("SymbolParamsRequest",     "symbols",      "SymbolParams"),
        ]
        for ctor_name, list_field, rpc_name in variants:
            try:
                Req = getattr(ah_pb2, ctor_name)
            except Exception:
                continue

            try:
                req = Req()
                arr = getattr(req, list_field, None)
                if hasattr(arr, "extend"):
                    arr.extend(syms_upper)
                else:
                    setattr(req, list_field, list(syms_upper))

                stub = getattr(acc, "account_helper_client", None)
                call = getattr(stub, rpc_name, None)
                if not callable(call):
                    # Probe alternative method names when the expected one is missing
                    for alt in ("SymbolParamsMany", "SymbolsParams", "SymbolParams"):
                        call = getattr(stub, alt, None)
                        if callable(call):
                            break
                if not callable(call):
                    continue

                res = await call(req, metadata=getattr(acc, "get_headers", lambda: [])(), timeout=5.0)

                items = _gx(res, "items") or _gx(res, "symbols") or _gx(res, "data") or []
                if isinstance(items, (list, tuple)):
                    for it in items:
                        name = (_gx(it, "name", "symbol", "symbol_name") or "").upper()
                        if not name:
                            continue
                        # digits may be number/string/wrapper
                        d_raw = _gx(it, "digits", "Digits")
                        d_num = _unbox_num(d_raw)
                        digits = int(d_num) if d_num is not None else None

                        c_raw = _gx(it, "trade_contract_size", "contract_size",
                                    "TradeContractSize", "ContractSize", "contractSize")
                        csize = _unbox_num(c_raw)

                        if name in out:
                            out[name]["digits"] = digits
                            out[name]["contract_size"] = csize

                # If we got anything at all, return it; remaining gaps can be filled elsewhere if needed
                if any(v.get("digits") is not None or v.get("contract_size") is not None for v in out.values()):
                    return out
            except Exception:
                # Try next ctor/method variant
                continue

    # 2) Fallback: fetch one symbol at a time
    async def _one(sym: str) -> Dict:
        # Try high-level symbol_info*
        info = None
        for nm in ("symbol_info", "get_symbol_info", "symbol_info_get"):
            fn = getattr(self, nm, None)
            if callable(fn):
                try:
                    info = await fn(sym)
                    break
                except Exception:
                    pass

        dig = None
        csz = None
        if info is not None:
            try:
                d_raw = _gx(info, "digits", "Digits")
                d_num = _unbox_num(d_raw)
                dig = int(d_num) if d_num is not None else None
            except Exception:
                dig = None
            csz = _unbox_num(
                _gx(info, "trade_contract_size", "TradeContractSize", "contract_size", "ContractSize")
            )

        # If still missing, query by low-level doubles/integers
        if dig is None:
            try:
                val = await acc.symbol_info_integer(sym, "SYMBOL_DIGITS")
                d_num = _unbox_num(val)
                if d_num is not None:
                    dig = int(d_num)
            except Exception:
                pass

        if csz is None:
            # Prefer double; fall back to integer if needed
            try:
                csz = _unbox_num(await acc.symbol_info_double(sym, "SYMBOL_TRADE_CONTRACT_SIZE"))
            except Exception:
                try:
                    csz = _unbox_num(await acc.symbol_info_integer(sym, "SYMBOL_TRADE_CONTRACT_SIZE"))
                except Exception:
                    pass

        return {"digits": dig, "contract_size": csz}

    try:
        results = await asyncio.gather(*[_one(s) for s in syms_upper], return_exceptions=True)
        for s, r in zip(syms_upper, results):
            if isinstance(r, Exception):
                continue
            out[s]["digits"] = r.get("digits")
            out[s]["contract_size"] = r.get("contract_size")
    except Exception:
        pass

    return out


# Attach to MT5Service (on import)
try:
    from app.core.mt5_service import MT5Service  # type: ignore
    setattr(MT5Service, "symbol_params_many", symbol_params_many)
except Exception:
    pass
