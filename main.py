# ============================================================================
# FILE: main.py (MT5Service PLAYBOOK)
# ============================================================================
# Purpose:
#   Entry point of the project. Provides a "playbook"-style demo of MT5Service
#   capabilities: connection, account info, symbols, snapshots, calculations,
#   history, streams, and safe trading presets.
#
# Key Features:
#   • Loads config/env (.env) and applies patches for pb2 compatibility.
#   • Builds MT5Service instance with credentials (login/password/server).
#   • Runs phase-based workflow controlled by RUN[...] toggles.
#   • Safe trading presets (market + pending orders) with dry-run option.
#   • Compact streaming demo (ticks, opened tickets, optional PnL).
#
# RUN[...] Toggles (phases):
#   - PHASE0 : Connectivity & Account
#   - PHASE1 : Symbols & Market Info
#   - PHASE2 : Opened State Snapshot
#   - PHASE3 : Calculations & Dry-run checks
#   - PHASE4 : Charts/Copy & DOM (optional, heavier)
#   - PHASE5 : History & Lookups
#   - PHASE6 : Streaming (compact)
#   - TRADE_PRESET : Execute safe trading scenario
#   - TRADE_DRY_RUN: True = only print, False = send real trades
#
# Notes:
#   • This file is for *demo/testing* — shows how to stitch service phases
#     together in a controlled, readable flow.
#   • Actual trading logic should be built in separate service modules.
#   • For new users: start by enabling PHASE0–PHASE3, keep trading off
#     until you’re confident.
#
# ============================================================================

from dotenv import load_dotenv; load_dotenv()

import os, sys, io, asyncio
from datetime import datetime, timezone

from app.core.config import MT5Config
from app.core.mt5_service import MT5Service
from app.calc.mt5_calc import patch_mt5_calculator
patch_mt5_calculator(MT5Service)

# Side-effect registrations (keep imports, even if unused directly)
from app.services import trading_service    
from app.services import history_service    
from app.patches import mt5_bind_patch      
from app.patches import market_info_patch   
from app.patches import symbol_params_patch 
from app.patches import charts_copy_patch   
from app.patches import quiet_connect_patch
from app.compat.mt5_patch import ORDER_MAP, order_calc_profit, order_calc_margin
from app.services.trading_probe import report_trading_bindings, first_symbol_precheck

# Phase runners
from app.services.phases import (
    run_once,
    phase_connectivity_and_account,
    phase_symbols_and_market_info,
    phase_opened_state_snapshot,
    phase_calculations_and_checks,
    phase_charts_and_dom,
    phase_history_and_lookups,
    show_trading_ops_examples,
    phase_trading_ops_preset,
    TradingPlan,
)

# Streaming
from app.services.streams_service import phase_streams_compact

from MetaRpcMT5 import ConnectExceptionMT5, ApiExceptionMT5

# Optional pb2 alias patch
try:
    from app.patches.patch_mt5_pb2_aliases import apply_patch
    apply_patch()
except Exception:
    pass


# ────────────────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────────────────
USER        = int(os.getenv("MT5_LOGIN",     "5036292718"))
PASSWORD    = os.getenv("MT5_PASSWORD",      "")
GRPC_SERVER = os.getenv("GRPC_SERVER",       "mt5.mrpc.pro:443")
SERVER_NAME = os.getenv("MT5_SERVER",        "MetaQuotes-Demo")

CRYPTO_SYMBOL   = os.getenv("CRYPTO_SYMBOL",   "BTCUSD")
SELECTED_SYMBOL = os.getenv("SELECTED_SYMBOL", "EURUSD")
ALT_SYMBOL      = os.getenv("ALT_SYMBOL",      "GBPUSD")

RUN = {
    "PHASE0": True,   # 0) Connectivity & Account
    "PHASE1": True,   # 1) Symbols & Market info
    "PHASE2": True,   # 2) Opened state snapshot
    "PHASE3": True,   # 3) Calculations & Dry-run
    "PHASE4": False,  # 4) Charts/Copy & DOM
    "PHASE5": True,   # 5) History & Lookups
    "PHASE6": True,   # 6) Streaming (compact)

    # Trading preset (safe scenario)
    "TRADE_PRESET": True,
    "TRADE_DRY_RUN": False,  # True = print only, False = real trades

    # Developer smoke/live test (from playground/live_test.py)
    "LIVE_TEST": False,
}

TIMEOUT_SECONDS        = int(os.getenv("TIMEOUT_SECONDS",        "90"))
STREAM_TIMEOUT_SECONDS = int(os.getenv("STREAM_TIMEOUT_SECONDS", "45"))
HISTORY_DAYS           = int(os.getenv("HISTORY_DAYS",           "7"))

PHASE4_OPTS = {
    "bars_lookback_days": 7,
    "ticks_lookback_days": 2,
    "rates_timeframes":   ("H1", "M15"),
    "max_rates":          800,
    "max_ticks":          20000,
    "tick_flags":         (3,),
    "do_dom":             True,
}

def now_unix() -> int:
    return int(datetime.now(timezone.utc).timestamp())


# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────
async def main() -> None:
    # Force UTF-8 for Windows console
    if os.name == "nt":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    cfg = MT5Config(
        user=USER,
        password=PASSWORD,
        grpc_server=GRPC_SERVER,
        server_name=SERVER_NAME,
        base_chart_symbol=SELECTED_SYMBOL,
        timeout_seconds=TIMEOUT_SECONDS,
    )
    svc = MT5Service(cfg)

    try:
        print("▶ Connecting…")
        await svc.connect()
        print("✅ Connected")

        # Bootstrap symbols
        await svc.symbol_select(SELECTED_SYMBOL, True); await asyncio.sleep(0.2)
        if ALT_SYMBOL and ALT_SYMBOL != SELECTED_SYMBOL:
            await svc.symbol_select(ALT_SYMBOL, True); await asyncio.sleep(0.1)

        # Analytical phases
        if RUN["PHASE0"]: await phase_connectivity_and_account(svc)
        if RUN["PHASE1"]: await phase_symbols_and_market_info(svc, SELECTED_SYMBOL)
        if RUN["PHASE2"]: await phase_opened_state_snapshot(svc, SELECTED_SYMBOL)
        if RUN["PHASE3"]: await run_once("PHASE3", lambda: phase_calculations_and_checks(svc, SELECTED_SYMBOL))
        if RUN["PHASE4"]: await phase_charts_and_dom(svc, SELECTED_SYMBOL)
        if RUN["PHASE5"]: await phase_history_and_lookups(svc)

        # Trading preset
        if RUN["TRADE_PRESET"]:
            plan = TradingPlan(
                symbol=SELECTED_SYMBOL,
                volume=0.01,
                side="BUY",
                dry_run=RUN["TRADE_DRY_RUN"],
                do_market=True,
                do_market_modify=True,
                do_market_close=True,
                do_buy_limit=True,
                do_pending_modify=True,
                do_pending_cancel=True,
                price_offset_points=30,
                sl=None,
                tp=None,
                expiration_ts=None,
            )
            await phase_trading_ops_preset(svc, plan)

        # Streams
        if RUN["PHASE6"]:
            await phase_streams_compact(
                svc,
                [SELECTED_SYMBOL, ALT_SYMBOL] if ALT_SYMBOL else [SELECTED_SYMBOL],
                enable_ticks=True,
                enable_opened=True,
                enable_pnl=False,
                duration_ticks=6,
                duration_opened=4,
                throttle=1.0,
                bootstrap_timeout=0.4,
            )

        # Developer smoke/live test
        if RUN["LIVE_TEST"]:
            from app.playground.live_test import phase_live_minimal_trades
            await phase_live_minimal_trades(svc, SELECTED_SYMBOL)

    except (ConnectExceptionMT5, ApiExceptionMT5) as e:
        print("❌ API/Connect error:", e)
    except KeyboardInterrupt:
        print("⛔ Interrupted")
    finally:
        await svc.disconnect()
        print("↩ disconnected")


if __name__ == "__main__":
    print("boot…")
    asyncio.run(main())
