from __future__ import annotations
import json
from typing import Any, Callable, Awaitable, Optional

def title(s: str) -> None:
    print("\n" + "=" * 20, s, "=" * 20)

def pprint(obj: Any) -> None:
    try:
        print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))
    except TypeError:
        print(obj)

async def safe_async(name: str, fn: Callable[..., Awaitable], *args, **kwargs) -> Optional[Any]:
    print(f"\n> {name}(" + ", ".join(
        [*(repr(a) for a in args), *(f"{k}={v!r}" for k, v in kwargs.items())]
    ) + ")")
    try:
        res = await fn(*args, **kwargs)
        if res is not None:
            pprint(res)
        else:
            print("OK (no return)")
        return res
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return None


"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/common/utils.py — Utility functions for logging and async calls║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose:                                                                     ║
║   Helpers for readable console output and safe execution of async functions. ║
║                                                                              ║
║ Exposes:                                                                     ║
║   1) title(s)       — prints a simple section header line.                   ║
║   2) pprint(obj)    — pretty-prints objects via JSON (utf-8),                ║
║                       non-serializable fields are coerced with str().        ║
║   3) safe_async(...)— logs call name+args, awaits the async fn,              ║
║                       pretty-prints result, catches errors.                  ║
║                                                                              ║
║ Behavior details:                                                            ║
║   - safe_async returns the function's result; on exception returns None.     ║
║   - If the result is None, prints 'OK (no return)'.                          ║
║   - Errors are printed as '[ERROR] <ExceptionType>: <message>'.              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""