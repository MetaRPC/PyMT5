"""
╔══════════════════════════════════════════════════════════════╗
║ phase_live_minimal_trades — tiny live ops smoke (safe demo)  ║
╠══════════════════════════════════════════════════════════════╣
║ Purpose  One-pass live test:                                 ║
║          1) BUY market 0.01 → position_modify → close        ║
║          2) Place far BUY_LIMIT → pending_modify → cancel    ║
║ Notes    Uses delta of open tickets to detect new position   ║
║ Safety   Prices pushed far from market to avoid instant fill ║
║ Inputs   svc: MT5Service, symbol: str                        ║
╚══════════════════════════════════════════════════════════════╝
"""

import asyncio

async def phase_live_minimal_trades(svc: MT5Service, symbol: str) -> None:
    from datetime import datetime, timezone, timedelta

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║ LIVE: tiny real ops (market & pending)                      ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    # helpers
    async def _get_open_tickets():
        """
        Snapshot open tickets.
        Returns:
          pos:  set[int]  — open position tickets
          pend: set[int]  — open pending order tickets
        """
        try:
            tmsg = await svc.opened_orders_tickets()
            pos  = {int(x) for x in getattr(tmsg, "opened_position_tickets", []) or []}
            pend = {int(x) for x in (getattr(tmsg, "opened_pending_tickets", None)
                                      or getattr(tmsg, "opened_order_tickets", None) or [])}
            return pos, pend
        except Exception:
            return set(), set()

    def _extract_ticket(obj):
        """
        Best-effort ticket extraction from gRPC reply.
        Prefers 'ticket' then 'order' (pending), falling back to id/position.
        """
        try:
            from google.protobuf.json_format import MessageToDict
            d = MessageToDict(obj, preserving_proto_field_name=True)
        except Exception:
            d = obj if isinstance(obj, dict) else {"repr": repr(obj)}
        # order of preference: pending prefers "order"; positions detected via Δ anyway
        for k in ("ticket","order","id","position","order_ticket"):
            if k in d and d[k]:
                try: return int(d[k])
                except Exception: pass
        return None

    # Preflight: ensure symbol is visible; grab a tick for bid/ask
    await svc.symbol_select(symbol, True)
    tick = await svc.symbol_info_tick(symbol)
    print("tick?", getattr(tick, "bid", None), "/", getattr(tick, "ask", None))

    # ===== 1) MARKET BUY 0.01 → modify → close =====
    pos_before, pend_before = await _get_open_tickets()

    r_buy = await svc.buy_market(symbol, 0.01, sl=None, tp=None)
    print("BUY result:", r_buy)

    # Detect new position ticket by Δ between snapshots
    await asyncio.sleep(0.4)
    pos_after, _ = await _get_open_tickets()
    new_pos = list(pos_after - pos_before)
    pos_ticket = new_pos[0] if len(new_pos) == 1 else None

    if pos_ticket:
        # Soft modify (keep SL/TP None)
        try:
            await svc.position_modify(ticket=pos_ticket, sl=None, tp=None)
            print("position_modify OK:", pos_ticket)
        except Exception as e:
            print("position_modify skipped/error:", e)
        # Close position (preferred) or fall back to cancel_order if the build behaves that way
        try:
            await svc.position_close(ticket=pos_ticket)
            print("position_close OK:", pos_ticket)
        except Exception as e:
            # fallback: on some builds OrderClose cancels a position as well
            try:
                await svc.cancel_order(ticket=pos_ticket)
                print("cancel_order (position) OK:", pos_ticket)
            except Exception as e2:
                print("close position failed:", e2)
    else:
        print("no new position ticket detected (already had positions?)")

    # ===== 2) PENDING: BuyLimit far away → modify → cancel =====
    _, pend_before = await _get_open_tickets()

    bid = getattr(tick, "bid", None) or getattr(tick, "Bid", None) or 1.0
    px  = round(float(bid) - 0.01000, 5)  # far enough to avoid instant fill
    exp_ts = int((datetime.now(timezone.utc) + timedelta(hours=12)).timestamp())

    r_pl = await svc.place_buy_limit(symbol, 0.01, px, sl=None, tp=None, expiration=exp_ts)
    print("BUY_LIMIT result:", r_pl)

    await asyncio.sleep(0.4)
    _, pend_after = await _get_open_tickets()
    new_pend = list(pend_after - pend_before)
    pend_ticket = new_pend[0] if len(new_pend) == 1 else _extract_ticket(r_pl)

    if pend_ticket:
        try:
            await svc.pending_modify(ticket=pend_ticket, price=round(px * 0.999, 5))
            print("pending_modify OK:", pend_ticket)
        except Exception as e:
            print("pending_modify skipped/error:", e)
        try:
            await svc.cancel_order(ticket=pend_ticket)
            print("cancel_order OK:", pend_ticket)
        except Exception as e:
            print("cancel_order failed:", e)
    else:
        print("no pending ticket detected")

    print("LIVE: done")
