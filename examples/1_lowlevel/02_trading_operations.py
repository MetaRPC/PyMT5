"""══════════════════════════════════════════════════════════════════════════════
FILE: 02_trading_operations.py - LOW-LEVEL TRADING OPERATIONS DEMO

⚠️  DANGER: This demo executes REAL TRADING operations!
            Use ONLY on DEMO accounts! Real money at risk otherwise!

PURPOSE:
  Demonstrates MT5 trading operations: calculations, validation, and execution.
  Shows the complete workflow from order preparation to closing positions.
  CRITICAL: All operations execute REAL trades - verify demo account first!


📚 WHAT THIS DEMO COVERS (4 Steps):

  STEP 1: CREATE MT5ACCOUNT & CONNECT
     • MT5Account() - Initialize account
     • connect_by_server_name() - Connect to MT5 terminal

  STEP 2: ORDER CALCULATIONS (SAFE - READ-ONLY)
     • order_calc_margin() - Calculate required margin for order
     • order_calc_profit() - Calculate potential profit/loss

  STEP 3: ORDER VALIDATION (SAFE - READ-ONLY)
     • order_check() - Validate order parameters before sending

  STEP 4: TRADING OPERATIONS (⚠️ DANGEROUS - REAL TRADES!)
     • order_send() - Place market BUY order
     • order_modify() - Add/modify Stop Loss and Take Profit
     • order_close() - Close opened position

  FINAL: DISCONNECT
     • disconnect() - Close connection to MT5

🚀 HOW TO RUN THIS DEMO:
  cd examples
  python main.py lowlevel02    (or select [2] from interactive menu)

══════════════════════════════════════════════════════════════════════════════"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from MetaRpcMT5 import MT5Account
from package.MetaRpcMT5 import (
    mt5_term_api_market_info_pb2 as market_info_pb2,
    mt5_term_api_account_helper_pb2 as account_helper_pb2,
    mt5_term_api_trading_helper_pb2 as trading_helper_pb2,
    mt5_term_api_trade_functions_pb2 as trade_functions_pb2,
    mt5_term_api_connection_pb2 as connection_pb2,
)

# Fix Windows console encoding for Unicode characters (only if running standalone)
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import common helpers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '0_common'))
from demo_helpers import (
    load_settings,
    create_and_connect_mt5,
    print_if_error,
    print_success,
    check_retcode,
    fatal,
)

# MAIN DEMO FUNCTION

async def run_trading_demo():
    print("═══════════════════════════════════════════════════════════")
    print("MT5 LOWLEVEL DEMO 02: TRADING OPERATIONS (DANGEROUS)")
    print("═══════════════════════════════════════════════════════════")
    print()
    print("⚠️  WARNING: This demo uses REAL TRADING operations!")
    print("    Make sure you are using a DEMO account!")
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # LOAD CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════
    config = load_settings()
    TEST_SYMBOL = config['test_symbol']
    TEST_VOLUME = config['test_volume']

    # ═══════════════════════════════════════════════════════════════════════
    # STEP 1: CREATE MT5ACCOUNT INSTANCE & CONNECT
    # ═══════════════════════════════════════════════════════════════════════
    
    print("STEP 1: Creating MT5Account instance and connecting...")
    print("───────────────────────────────────────────────────────────")

    account = await create_and_connect_mt5(config)
    print()

    try:

        # ═══════════════════════════════════════════════════════════════════════
        # STEP 2: ORDER CALCULATIONS (SAFE - READ-ONLY)
        # ═══════════════════════════════════════════════════════════════════════

        print()
        print("STEP 2: Order Calculations (Safe - Read-Only)")
        print("───────────────────────────────────────────────────────────")

        # ══════════════════════════════════════════════════════════════
        # 2.1. order_calc_margin()
        #      Calculate margin required to open an order.
        #      Call: account.order_calc_margin(request) → gRPC → MT5 Server
        #      Returns: OrderCalcMarginResponse (.margin field)
        #      SAFE operation - calculation only, no trades executed.
        # ══════════════════════════════════════════════════════════════
        print()
        print("2.1. order_calc_margin() - Calculate required margin")

        # Get current price first
        tick_data = await account.symbol_info_tick(symbol=TEST_SYMBOL)

        # Calculate margin for a BUY order
        margin_req = trade_functions_pb2.OrderCalcMarginRequest(
            order_type=market_info_pb2.ORDER_TYPE_BUY,
            symbol=TEST_SYMBOL,
            volume=TEST_VOLUME,
            open_price=tick_data.ask  # Use current Ask price for BUY
        )
        margin_data = await account.order_calc_margin(request=margin_req)

        print(f"  Symbol:                        {TEST_SYMBOL}")
        print(f"  Action:                        BUY")
        print(f"  Volume:                        {TEST_VOLUME:.2f} lots")
        print(f"  Price:                         {tick_data.ask:.5f}")
        print(f"  Required Margin:               {margin_data.margin:.2f}")

        # ══════════════════════════════════════════════════════════════
        # 2.2. order_calc_profit()
        #      Calculate potential profit/loss for an order.
        #      Call: account.order_calc_profit(request) → gRPC → MT5 Server
        #      Returns: OrderCalcProfitResponse (.profit field)
        #      SAFE operation - calculation only, no trades executed.
        # ══════════════════════════════════════════════════════════════
        print()
        print("2.2. order_calc_profit() - Calculate potential profit/loss")

        # Calculate profit if we BUY at Ask and SELL at Bid (immediate loss due to spread)
        profit_req = trade_functions_pb2.OrderCalcProfitRequest(
            order_type=market_info_pb2.ORDER_TYPE_BUY,
            symbol=TEST_SYMBOL,
            volume=TEST_VOLUME,
            open_price=tick_data.ask,   # Entry price
            close_price=tick_data.bid   # Exit price (immediate close = spread loss)
        )
        profit_data = await account.order_calc_profit(request=profit_req)

        print(f"  Symbol:                        {TEST_SYMBOL}")
        print(f"  Action:                        BUY")
        print(f"  Volume:                        {TEST_VOLUME:.2f} lots")
        print(f"  Price Open (Ask):              {tick_data.ask:.5f}")
        print(f"  Price Close (Bid):             {tick_data.bid:.5f}")
        print(f"  Potential Profit/Loss:         {profit_data.profit:.2f} (spread loss)")

        # Calculate profit with 10 pips profit target

        pip_size = 0.0001  # For EURUSD, 1 pip = 0.0001
        target_price = tick_data.ask + (10 * pip_size)

        profit_target_req = trade_functions_pb2.OrderCalcProfitRequest(
            order_type=market_info_pb2.ORDER_TYPE_BUY,
            symbol=TEST_SYMBOL,
            volume=TEST_VOLUME,
            open_price=tick_data.ask,
            close_price=target_price
        )
        profit_target_data = await account.order_calc_profit(request=profit_target_req)

        print()
        print(f"  If price moves +10 pips to {target_price:.5f}:")
        print(f"  Potential Profit:              {profit_target_data.profit:.2f}")


        # ═══════════════════════════════════════════════════════════════════════
        # STEP 3: ORDER VALIDATION (SAFE - READ-ONLY)
        # ═══════════════════════════════════════════════════════════════════════
        print()
        print()
        print("STEP 3: Order Validation (Safe - Read-Only)")
        print("───────────────────────────────────────────────────────────")

        # ══════════════════════════════════════════════════════════════
        # 3.1. order_check()
        #      Validate order parameters BEFORE sending to broker.
        #      Call: account.order_check(request) → gRPC → MT5 Server
        #      Returns: OrderCheckResponse (simulated balance/equity/margin)
        #      SAFE operation - validation only, no trades executed (dry-run).
        #      ⚠️  NOTE: Often fails on DEMO accounts (broker limitation)
        # ══════════════════════════════════════════════════════════════
        print()
        print("3.1. order_check() - Validate order parameters")

        # Create order check request with IOC filling (most compatible)
        try:
            mql_trade_req = trade_functions_pb2.MrpcMqlTradeRequest(
                action=trade_functions_pb2.TRADE_ACTION_DEAL,
                symbol=TEST_SYMBOL,
                volume=TEST_VOLUME,
                order_type=market_info_pb2.ORDER_TYPE_BUY,
                price=tick_data.ask,
                stop_loss=0.0,
                take_profit=0.0,
                deviation=10,
                type_filling=trade_functions_pb2.ORDER_FILLING_IOC,  # IOC - most compatible
                type_time=trade_functions_pb2.ORDER_TIME_GTC,
                comment="OrderCheck validation"
            )
            check_req = trade_functions_pb2.OrderCheckRequest(mql_trade_request=mql_trade_req)
            check_data = await account.order_check(request=check_req)

            # OrderCheck succeeded!
            result = check_data.mrpc_mql_trade_check_result
            print("  ✅ OrderCheck SUCCESS!")
            print(f"     Return Code:        {result.returned_code}")
            print(f"     Comment:            {result.comment}")
            print(f"     Required Margin:    {result.margin:.2f}")
            print(f"     Balance After:      {result.balance_after_deal:.2f}")
            print(f"     Equity After:       {result.equity_after_deal:.2f}")
            print(f"     Free Margin After:  {result.free_margin:.2f}")
            print(f"     Margin Level:       {result.margin_level:.2f}%")
            print()

            if result.returned_code == 0:
                print("  ✓ Order validation PASSED - safe to proceed with order_send()")
            else:
                print(f"  ⚠️  Validation returned code {result.returned_code} - check before trading")

        except Exception as e:

            # OrderCheck failed - this is EXPECTED on demo accounts
            print("  [X] OrderCheck FAILED (expected on demo accounts)")
            print(f"      Error type: {type(e).__name__}")
            print()
            print("  [i] This is a known limitation:")
            print("      • DEMO accounts: OrderCheck often not supported")
            print("      • gRPC gateway: May have Timestamp handling issues")
            print("      • Workaround: Use order_calc_margin() (step 2.1)")
            print("      • order_send() will work despite this failure")
            print()


        # ═══════════════════════════════════════════════════════════════════════
        # STEP 4: TRADING OPERATIONS (DANGEROUS - REAL TRADES!)
        # ═══════════════════════════════════════════════════════════════════════
        print()
        print()
        print("⚠️  STEP 4: Trading Operations (DANGEROUS - Real Trades!)")
        print("───────────────────────────────────────────────────────────")
        print("  The following operations will place REAL orders!")
        print("  Make sure you are on a DEMO account!")
        print()

        # ══════════════════════════════════════════════════════════════
        # 4.1. order_send()
        #      Place a market BUY order on broker.
        #      Call: account.order_send(request) → gRPC → MT5 Server
        #      Returns: OrderSendResponse (ticket, deal, price, volume)
        #      DANGEROUS - Executes REAL trade with REAL money!
        # ══════════════════════════════════════════════════════════════
        print()
        print("4.1. order_send() - Place market BUY order")

        try:
            slippage = 10
            send_req = trading_helper_pb2.OrderSendRequest(
                symbol=TEST_SYMBOL,
                operation=trading_helper_pb2.TMT5_ORDER_TYPE_BUY,
                volume=TEST_VOLUME,
                price=tick_data.ask,
                slippage=slippage
                # StopLoss and TakeProfit can be set here or later via order_modify
            )
            send_data = await account.order_send(request=send_req)
        except Exception as e:
            # Market closed or other trading error
            print(f"  ❌ OrderSend FAILED")
            print(f"     Error: {e}")

            if "MARKET_CLOSED" in str(e) or "10018" in str(e):
                print()
                print("  ℹ️  Market is closed:")
                print("     • Forex market trades 24/5 (Monday 00:00 - Friday 23:59 GMT)")
                print("     • Weekend and holidays: no trading")
                print("     • Run this demo during market hours to see real trades")
                print()
                print("  ✓ Demo completed successfully (market hours check)")
                return
            else:
                # Re-raise if it's not a market closed error
                raise

        print(f"  Order sent result:")
        print(f"    Return Code:                 {send_data.returned_code}")
        print(f"    Deal Ticket:                 {send_data.deal}")
        print(f"    Order Ticket:                {send_data.order}")
        print(f"    Volume:                      {send_data.volume:.2f}")
        print(f"    Execution Price:             {send_data.price:.5f}")

        # Bid/Ask are optional fields, often 0 in response - skip if not provided
        if send_data.bid > 0 and send_data.ask > 0:
            print(f"    Market Bid:                  {send_data.bid:.5f}")
            print(f"    Market Ask:                  {send_data.ask:.5f}")

        print(f"    Comment:                     {send_data.comment}")

        # Check if order executed successfully (10009 = DONE)
        if send_data.returned_code == 10009:
            print(f"    ✓ Order EXECUTED successfully!")
            order_ticket = send_data.order

            # ══════════════════════════════════════════════════════════════
            # 4.2. order_modify()
            #      Modify opened position - add/change SL/TP levels.
            #      Call: account.order_modify(request) → gRPC → MT5 Server
            #      Returns: OrderModifyResponse (modification result)
            #      DANGEROUS - Modifies REAL open position!
            # ══════════════════════════════════════════════════════════════
            print()
            print("4.2. order_modify() - Add Stop Loss and Take Profit")

            # Calculate SL/TP levels (10 pips SL, 20 pips TP)
            stop_loss = send_data.price - (10 * pip_size)
            take_profit = send_data.price + (20 * pip_size)

            modify_req = trading_helper_pb2.OrderModifyRequest(
                ticket=order_ticket,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            modify_data = await account.order_modify(request=modify_req)

            print(f"  Order modify result:")
            print(f"    Return Code:                 {modify_data.returned_code}")
            print(f"    Order Ticket:                {modify_data.order}")
            print(f"    Stop Loss:                   {stop_loss:.5f}")
            print(f"    Take Profit:                 {take_profit:.5f}")
            print(f"    Comment:                     {modify_data.comment}")

            if modify_data.returned_code == 10009:
                print(f"    ✓ Position MODIFIED successfully!")

            # ══════════════════════════════════════════════════════════════
            # 4.3. order_close()
            #      Close opened position at market price.
            #      Call: account.order_close(request) → gRPC → MT5 Server
            #      Returns: OrderCloseResponse (close result with P&L)
            #      DANGEROUS - Closes REAL position, realizes profit/loss!
            # ══════════════════════════════════════════════════════════════
            print()
            print("4.3. order_close() - Close the position")

            close_req = trading_helper_pb2.OrderCloseRequest(
                ticket=order_ticket,
                volume=TEST_VOLUME,
                slippage=10
            )
            close_data = await account.order_close(request=close_req)

            print(f"  Order close result:")
            print(f"    Return Code:                 {close_data.returned_code} ({close_data.returned_string_code})")
            print(f"    Description:                 {close_data.returned_code_description}")
            print(f"    Close Mode:                  {close_data.close_mode}")

            if close_data.returned_code == 10009:
                print(f"    ✓ Position CLOSED successfully!")
        else:
            print(f"    ✗ Order execution FAILED - check return code and comment")

        # ═══════════════════════════════════════════════════════════════════════
        # FINAL: CLEANUP
        # ═══════════════════════════════════════════════════════════════════════
        print()
        print()
        print("Final: Cleanup...")
        print("───────────────────────────────────────────────────────────")
        print("  [i] Connection will be closed automatically")
        print()
        print("═" * 80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("═" * 80)

        print("\nMETHODS DEMONSTRATED (5 total):")
        print("   ORDER CALCULATIONS (2):   order_calc_margin, order_calc_profit")
        print("   ORDER VALIDATION (1):     order_check")
        print("   TRADING OPERATIONS (3):   order_send, order_modify, order_close")

        print("\nLowLevel Trading API Features:")
        print("  • Order calculations: margin and profit estimation before trading")
        print("  • Order validation: dry-run check before execution")
        print("  • Direct trading: order_send/modify/close via gRPC protobuf")
        print("  • Real execution: all trading methods execute REAL trades!")

        print("\nWHAT'S NEXT:")
        print("   [3] Streaming Methods     → python main.py lowlevel03")

        print("\n" + "═" * 80)

    except Exception as e:
        print()
        print_if_error(e, "Error during demo execution")
        import traceback
        traceback.print_exc()

    finally:
        # Clean disconnection
        if account:
            print("\nFINAL: Disconnect")
            print("─" * 59)
            try:
                await account.channel.close()
                print("✓ Disconnected successfully")
            except Exception as e:
                print(f"⚠️  Disconnect warning: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    asyncio.run(run_trading_demo())
