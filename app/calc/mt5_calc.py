"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE app/mt5_calc.py — Profit & Margin Calculator Patch for MT5Service       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose:                                                                     ║
║   Extend MT5Service with local profit/margin calculation helpers.            ║
║                                                                              ║
║ Provides:                                                                    ║
║   • order_calc_profit      → account-currency profit for a closed trade      ║
║   • order_calc_profit_now  → quick profit check using current bid/ask        ║
║   • order_calc_margin      → required margin estimate for a new trade        ║
║                                                                              ║
║ Logic flow:                                                                  ║
║   1) Try RPC via TradeFunctions (if server supports).                        ║
║   2) Fallback: use tick_size/tick_value (already in account currency).       ║
║   3) Last resort: contract_size × Δprice, converted FX→account currency.     ║
║                                                                              ║
║ Usage:                                                                       ║
║   from app.calc.mt5_calc import patch_mt5_calculator                         ║
║   patch_mt5_calculator(MT5Service)  # attach methods to service class        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional, Union


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Utility: safely remove the field from dict/attr (Taking into account different names/cases)
# ─────────────────────────────────────────────────────────────────────────────────────────────
def _get(obj: Any, *names: str) -> Any:
    if obj is None:
        return None
    for n in names:
        
        if isinstance(obj, dict) and n in obj:
            return obj[n]
        
        if hasattr(obj, n):
            return getattr(obj, n)
    return None


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Patch calculator: attaching methods to MT5Service
# ─────────────────────────────────────────────────────────────────────────────────────────────
def patch_mt5_calculator(MT5Service_cls: type) -> None:
    """
    Monkey-patch MT5Service class with calculation helpers:
      - order_calc_profit
      - order_calc_profit_now
      - order_calc_margin
    """

    async def order_calc_profit(
        self,
        symbol: str,
        volume_lots: float,
        side: Union[str, int],
        *,
        price_open: Optional[float] = None,
        price_close: Optional[float] = None,
    ) -> float:
        """
        Calculate trade profit in account currency.

        Flow:
          1) Try RPC via TradeFunctions.OrderCalcProfit (if available).
          2) Fallback: use tick_size / tick_value (already in account currency).
          3) Final fallback: contract_size × Δprice, converted to account currency.
        """
        # normalize side → BUY=0, SELL=1
        try:
            s = str(side).upper()
            side_code = 0 if s in ("BUY", "B", "LONG", "0") else 1
        except Exception:
            try:
                side_code = int(side)  # type: ignore[arg-type]
            except Exception:
                side_code = 0

        # get current tick to auto-fill prices
        tick = await self.symbol_info_tick(symbol)
        bid = float(_get(tick, "bid", "Bid") or 0.0)
        ask = float(_get(tick, "ask", "Ask") or 0.0)

        # infer open/close prices if not provided
        if price_open is None or price_close is None:
            if side_code == 0:  # BUY: open=ask, close=bid
                price_open = price_open or (ask or bid)
                price_close = price_close or (bid or ask)
            else:               # SELL: open=bid, close=ask
                price_open = price_open or (bid or ask)
                price_close = price_close or (ask or bid)

        po = float(price_open or 0.0)
        pc = float(price_close or 0.0)

        # 1) Try RPC: TradeFunctions.OrderCalcProfit
        try:
            acc = getattr(self, "acc", None)
            if acc and hasattr(acc, "trade_functions_client"):
                try:
                    from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf  
                except Exception:
                    tf = None
                if tf is not None and hasattr(tf, "OrderCalcProfitRequest"):
                    req = tf.OrderCalcProfitRequest()
                    if hasattr(req, "symbol"): req.symbol = symbol
                    if hasattr(req, "order_type"): req.order_type = int(side_code)
                    elif hasattr(req, "type"): req.type = int(side_code)
                    elif hasattr(req, "cmd"): req.cmd = int(side_code)
                    if hasattr(req, "volume"): req.volume = float(volume_lots)
                    elif hasattr(req, "volume_lots"): req.volume_lots = float(volume_lots)
                    if hasattr(req, "price_open"): req.price_open = po
                    if hasattr(req, "price_close"): req.price_close = pc

                    headers = acc.get_headers() if hasattr(acc, "get_headers") else []
                    reply = await acc.trade_functions_client.OrderCalcProfit(  # type: ignore[attr-defined]
                        req, metadata=headers, timeout=5.0
                    )
                    data = getattr(reply, "data", reply)
                    for fld in ("profit", "Profit", "value", "amount"):
                        val = getattr(data, fld, None)
                        if val is not None:
                            return float(val)
        except Exception:
            pass

        # 2) Local fallback: tick_size / tick_value (already account currency per lot)
        info = None
        for nm in ("symbol_info", "get_symbol_info", "symbol_info_get"):
            f = getattr(self, nm, None)
            if callable(f):
                try:
                    info = await f(symbol)
                    break
                except Exception:
                    pass

        tick_size = float(_get(info, "trade_tick_size", "TradeTickSize", "tick_size", "TickSize") or 0.0)
        tick_value = float(_get(info, "trade_tick_value", "TradeTickValue", "tick_value", "TickValue") or 0.0)
        if tick_size > 0.0 and tick_value:
            delta_signed = (pc - po) if side_code == 0 else (po - pc)
            return float((delta_signed / tick_size) * tick_value * float(volume_lots))

        # 3) Last fallback: contract_size × Δprice (in quote currency) → convert to account currency
        contract_size = float(
            _get(info, "trade_contract_size", "TradeContractSize", "contract_size", "ContractSize") or 100000.0
        )
        delta_quote_signed = (pc - po) if side_code == 0 else (po - pc)
        profit_quote = delta_quote_signed * float(volume_lots) * contract_size

        # account currency detection
        acct_ccy = None
        try:
            acc_sum = await self.account_summary()
            acct_ccy = str(
                _get(acc_sum, "account_currency", "AccountCurrency", "currency", "Currency") or ""
            ).upper()
        except Exception:
            pass

        # try direct FX conversion
        base = symbol[:3].upper() if len(symbol) >= 6 else ""
        quote = symbol[3:6].upper() if len(symbol) >= 6 else ""

        if acct_ccy and quote and acct_ccy == quote:
            return float(profit_quote)
        if acct_ccy and base and acct_ccy == base and pc:
            return float(profit_quote / pc)

        # helper: fetch cross-rate for conversion
        async def _pair_price(sym: str) -> float:
            for nm in ("ensure_symbol_visible", "symbol_select"):
                g = getattr(self, nm, None)
                if callable(g):
                    try:
                        r = g(sym) if nm == "symbol_select" else g(sym, True)
                        if hasattr(r, "__await__"):
                            await r
                    except Exception:
                        pass
            t = await self.symbol_info_tick(sym)
            return float(_get(t, "bid", "Bid") or 0.0) or float(_get(t, "ask", "Ask") or 0.0) or 0.0

        if acct_ccy and quote:
            pair1 = f"{quote}{acct_ccy}"
            pair2 = f"{acct_ccy}{quote}"
            try:
                rate = await _pair_price(pair1)
                if rate > 0.0:
                    return float(profit_quote * rate)
                rate = await _pair_price(pair2)
                if rate > 0.0:
                    return float(profit_quote / rate)
            except Exception:
                pass

        return float(profit_quote)

    async def order_calc_profit_now(
        self,
        symbol: str,
        side: Union[str, int],
        volume: float,
        price_open: float,
    ) -> float:
        """
        Quick profit check:
          - Takes given price_open.
          - Uses current bid/ask as close_price (BUY→bid, SELL→ask).
        """
        tick = await self.symbol_info_tick(symbol=symbol)
        bid = float(_get(tick, "bid", "Bid") or 0.0)
        ask = float(_get(tick, "ask", "Ask") or 0.0)
        try:
            s = str(side).upper()
            side_code = 0 if s in ("BUY", "B", "LONG", "0") else 1
        except Exception:
            try:
                side_code = int(side)
            except Exception:
                side_code = 0
        close_price = (bid or ask) if side_code == 0 else (ask or bid)
        if not close_price:
            return 0.0
        return await self.order_calc_profit(
            symbol, float(volume), side_code, price_open=float(price_open), price_close=float(close_price)
        )

    async def order_calc_margin(
        self,
        symbol: str,
        volume_lots: float,
        side: Union[str, int],
        price: Optional[float] = None,
        leverage: Optional[float] = None,
    ) -> float:
        """
        Calculate required margin in account currency.

        Flow:
          1) Try RPC via TradeFunctions.OrderCalcMargin.
          2) Fallback: contract_size × volume / leverage, FX-converted to account currency.
        """
        # normalize side
        try:
            s = str(side).upper()
            side_code = 0 if s in ("BUY", "B", "LONG", "0") else 1
        except Exception:
            try:
                side_code = int(side)
            except Exception:
                side_code = 0

        # auto-pick price if missing
        if price is None:
            t = await self.symbol_info_tick(symbol)
            b = float(_get(t, "bid", "Bid") or 0.0)
            a = float(_get(t, "ask", "Ask") or 0.0)
            price = (a or b or 1.0) if side_code == 0 else (b or a or 1.0)

        # 1) Try RPC: TradeFunctions.OrderCalcMargin
        try:
            acc = getattr(self, "acc", None)
            if acc and hasattr(acc, "trade_functions_client"):
                try:
                    from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf  # type: ignore
                except Exception:
                    tf = None
                if tf is not None and hasattr(tf, "OrderCalcMarginRequest"):
                    req = tf.OrderCalcMarginRequest()
                    if hasattr(req, "symbol"): req.symbol = symbol
                    if hasattr(req, "order_type"): req.order_type = int(side_code)
                    elif hasattr(req, "type"): req.type = int(side_code)
                    elif hasattr(req, "cmd"): req.cmd = int(side_code)
                    if hasattr(req, "volume"): req.volume = float(volume_lots)
                    elif hasattr(req, "volume_lots"): req.volume_lots = float(volume_lots)
                    if hasattr(req, "price"): req.price = float(price)

                    headers = acc.get_headers() if hasattr(acc, "get_headers") else []
                    reply = await acc.trade_functions_client.OrderCalcMargin( 
                        req, metadata=headers, timeout=5.0
                    )
                    data = getattr(reply, "data", reply)
                    for fld in ("margin", "Margin", "value", "amount"):
                        val = getattr(data, fld, None)
                        if val is not None:
                            return float(val)
        except Exception:
            pass

        # 2) Local fallback calculation
        info = None
        for nm in ("symbol_info", "get_symbol_info", "symbol_info_get"):
            f = getattr(self, nm, None)
            if callable(f):
                try:
                    info = await f(symbol)
                    break
                except Exception:
                    pass

        # leverage (fallback to account or default=100)
        if leverage is None:
            try:
                acc_sum = await self.account_summary()
                leverage = float(
                    _get(acc_sum, "account_leverage", "AccountLeverage", "leverage", "Leverage") or 100.0
                )
            except Exception:
                leverage = 100.0
        lev = max(float(leverage or 1.0), 1.0)

        contract_size = float(
            _get(info, "trade_contract_size", "TradeContractSize", "contract_size", "ContractSize") or 100000.0
        )

        # margin in base currency of instrument
        margin_base = (contract_size * float(volume_lots)) / lev

        # try to match account currency
        acct_ccy = None
        try:
            acc_sum = await self.account_summary()
            acct_ccy = str(
                _get(acc_sum, "account_currency", "AccountCurrency", "currency", "Currency") or ""
            ).upper()
        except Exception:
            pass

        base = symbol[:3].upper() if len(symbol) >= 6 else ""
        quote = symbol[3:6].upper() if len(symbol) >= 6 else ""

        if acct_ccy and base and acct_ccy == base:
            return float(margin_base)
        if acct_ccy and quote and acct_ccy == quote:
            return float(margin_base * float(price or 1.0))

        # helper: fetch FX rate for conversion
        async def _pair_price(sym: str) -> float:
            for nm in ("ensure_symbol_visible", "symbol_select"):
                g = getattr(self, nm, None)
                if callable(g):
                    try:
                        r = g(sym) if nm == "symbol_select" else g(sym, True)
                        if hasattr(r, "__await__"):
                            await r
                    except Exception:
                        pass
            t = await self.symbol_info_tick(sym)
            return float(_get(t, "bid", "Bid") or 0.0) or float(_get(t, "ask", "Ask") or 0.0) or 0.0

        if acct_ccy and base:
            pair1 = f"{base}{acct_ccy}"
            pair2 = f"{acct_ccy}{base}"
            try:
                rate = await _pair_price(pair1)
                if rate > 0.0:
                    return float(margin_base * rate)
                rate = await _pair_price(pair2)
                if rate > 0.0:
                    return float(margin_base / rate)
            except Exception:
                pass

        # last resort
        return float(margin_base * float(price or 1.0))

    # attach methods to class
    setattr(MT5Service_cls, "order_calc_profit", order_calc_profit)
    setattr(MT5Service_cls, "order_calc_profit_now", order_calc_profit_now)
    setattr(MT5Service_cls, "order_calc_margin", order_calc_margin)

