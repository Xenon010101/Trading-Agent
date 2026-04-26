# InsiderEdge v1.0 - AI Trading Agent
# Author: Anmol Patel

from market_data import get_market_summary_advanced as get_market_summary
from ai_brain import analyze_market
from risk_manager import RiskManager
from logger import log_decision, print_banner, print_session_summary
from executor import execute_trade, verify_kraken_connection
from report import generate_daily_report, calculate_sharpe_ratio
from erc8004 import setup_agent, post_checkpoint, submit_trade_intent, post_reputation
from datetime import date
from config import WATCHLIST, INTERVAL_MINUTES, MAX_TRADES_PER_DAY, MIN_CONFIDENCE, MAX_LOSS_PERCENT, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT, PAPER_MODE
import time
import signal
import sys
import os
from dotenv import load_dotenv

try:
    from terminal_ui import (
        print_banner as ui_banner,
        print_config as ui_print_config,
        print_scan_header as ui_scan_header,
        print_decision as ui_print_decision,
        print_positions as ui_print_positions,
        print_risk_summary as ui_print_risk_summary,
        print_next_scan as ui_print_next_scan,
        print_alert as ui_print_alert,
        print_blockchain_status as ui_blockchain_status,
        print_reputation_ok as ui_reputation_ok,
    )
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

load_dotenv()

# Global risk manager instance - persists across scan cycles
risk = RiskManager()

# Track if we're shutting down to prevent double-exit
shutdown_requested = False
scan_cycle_count = 0


def handle_exit(sig, frame):
    """Clean shutdown handler for Ctrl+C"""
    global shutdown_requested
    if shutdown_requested:
        return  # Prevent double-calls
    shutdown_requested = True
    
    print("\n\n" + "=" * 50)
    print("   Shutting down agent...")
    print("=" * 50 + "\n")
    generate_daily_report()
    print_session_summary()
    sys.exit(0)


def check_env_keys():
    """Verify all required API keys are present before starting"""
    required_keys = ["GROQ_API_KEY", "PRISM_API_KEY", "KRAKEN_API_KEY", "KRAKEN_API_SECRET"]
    missing = [key for key in required_keys if not os.getenv(key)]
    
    if missing:
        print("\n" + "!" * 50)
        print("   WARNING: Missing environment variables:")
        for key in missing:
            print(f"   - {key}")
        print("!" * 50)
        print("\nCopy .env.example to .env and add your API keys.\n")
        return False
    return True


def print_config():
    """Display current configuration at startup"""
    mode = "PAPER TRADING (simulation)" if PAPER_MODE else "LIVE TRADING (real money)"
    
    print("\n" + "-" * 50)
    print("   Configuration")
    print("-" * 50)
    print(f"   Mode         : {mode}")
    print(f"   Watchlist    : {', '.join(WATCHLIST)}")
    print(f"   Scan Interval: {INTERVAL_MINUTES} minutes")
    print(f"   Max Trades   : {MAX_TRADES_PER_DAY}/day")
    print(f"   Min Confidence: {MIN_CONFIDENCE}%")
    print(f"   Max Loss     : {MAX_LOSS_PERCENT}%")
    print(f"   Take Profit  : {TAKE_PROFIT_PERCENT}%")
    print(f"   Stop Loss    : {STOP_LOSS_PERCENT}%")
    print("-" * 50 + "\n")


def check_exit_conditions(symbol, current_price):
    """Check if take profit or stop loss is triggered for open position"""
    if symbol not in risk.positions:
        return None
    
    if current_price is None or current_price == 0:
        return None
    
    buy_price = risk.positions[symbol]["buy_price"]
    if buy_price is None or buy_price == 0:
        return None
    
    pnl = ((current_price - buy_price) / buy_price) * 100
    print(f"  {symbol} PnL: {pnl:.2f}%")
    
    if pnl >= TAKE_PROFIT_PERCENT:
        print(f"  [TP] TAKE PROFIT: {symbol} +{pnl:.2f}%")
        return {"action": "SELL", "confidence": 95, "reason": f"TP hit +{pnl:.2f}%"}
    
    if pnl <= -STOP_LOSS_PERCENT:
        print(f"  [SL] STOP LOSS: {symbol} {pnl:.2f}%")
        return {"action": "SELL", "confidence": 95, "reason": f"SL hit {pnl:.2f}%"}
    
    return None


def scan_coin(symbol):
    """Analyze a single coin and execute if conditions are met"""
    if risk.check_circuit_breaker():
        print(f"   Circuit breaker active - skipping {symbol}")
        return None
    
    data = get_market_summary(symbol)
    
    if data is None:
        print(f"   No data for {symbol}")
        return None
    
    price_data = data.get("price")
    if isinstance(price_data, dict):
        current_price = price_data.get("price")
    else:
        current_price = price_data
    
    change_24h = data.get("change_24h", 0)
    
    if not current_price or current_price == 0:
        print(f"   No price for {symbol}")
        return None
    
    is_holding = symbol in risk.positions
    
    if is_holding:
        print(f"  Holding {symbol} - checking exits")
        exit_decision = check_exit_conditions(symbol, current_price)
        if exit_decision:
            result = execute_trade("SELL", symbol)
            if result is not None:
                risk.record_trade(symbol, "SELL", current_price, exit_decision["confidence"])
                log_decision(symbol, data, exit_decision, True)
                submit_trade_intent("SELL", symbol)
                time.sleep(3)
                post_checkpoint("SELL", symbol, exit_decision["confidence"], exit_decision["reason"])
                post_reputation(exit_decision["confidence"])
                print(f"  Exited {symbol} position")
        return data
    
    decision = analyze_market(data)
    action = decision["action"]
    confidence = decision["confidence"]
    
    if action == "BUY" and risk.can_trade(decision):
        result = execute_trade("BUY", symbol)
        if result is not None:
            risk.record_trade(symbol, "BUY", current_price, confidence)
            log_decision(symbol, data, decision, True)
            submit_trade_intent("BUY", symbol)
            time.sleep(3)
            post_checkpoint("BUY", symbol, confidence, decision["reason"])
            post_reputation(confidence)
            print(f"  Bought {symbol}")
        else:
            post_checkpoint("BUY", symbol, confidence, decision["reason"])
            log_decision(symbol, data, decision, False)
    elif action == "SELL":
        print(f"  No position to sell in {symbol}")
        post_checkpoint("SELL", symbol, confidence, decision["reason"])
        log_decision(symbol, data, decision, False)
    else:
        post_checkpoint("HOLD", symbol, confidence, decision["reason"])
        log_decision(symbol, data, decision, False)
    
    time.sleep(30)
    return data


def main():
    """Main entry point - runs continuous market scan loop"""
    global shutdown_requested, scan_cycle_count, last_reset_date
    
    signal.signal(signal.SIGINT, handle_exit)
    
    print_banner()
    
    if not check_env_keys():
        print("Continuing in limited mode...\n")
    
    print_config()
    
    if not PAPER_MODE:
        verify_kraken_connection()
    
    blockchain_ok = setup_agent()
    post_reputation(95)
    
    print("Starting market scan loop. Press Ctrl+C to stop.\n")
    
    while not shutdown_requested:
        if date.today() > risk.last_reset_date:
            print(f"\n  New day: {date.today()}")
            risk.reset_for_new_day()
            risk.last_reset_date = date.today()
            generate_daily_report()
        
        scan_cycle_count += 1
        current_time = time.strftime("%H:%M:%S")
        
        print("\n" + "=" * 50)
        print(f"  SCAN CYCLE [{current_time}] #{scan_cycle_count}")
        print(f"  Analyzing {len(WATCHLIST)} coins: {', '.join(WATCHLIST)}")
        print("=" * 50)
        
        current_prices = {}
        for symbol in WATCHLIST:
            try:
                data = scan_coin(symbol)
                if data:
                    price_data = data.get("price")
                    if isinstance(price_data, dict):
                        current_prices[symbol] = price_data.get("price")
                    else:
                        current_prices[symbol] = price_data
            except Exception as e:
                print(f"  Error scanning {symbol}: {e}")
        
        risk.get_open_positions(current_prices)
        risk.get_summary()
        
        if scan_cycle_count % 10 == 0:
            generate_daily_report()
            calculate_sharpe_ratio()
        
        sleep_seconds = INTERVAL_MINUTES * 60
        print(f"\n  Next scan in {INTERVAL_MINUTES} minute(s)...")
        print(f"  Press Ctrl+C to stop\n")
        
        while sleep_seconds > 0 and not shutdown_requested:
            time.sleep(min(sleep_seconds, 5))
            sleep_seconds -= 5
        
        post_reputation(95)


if __name__ == "__main__":
    main()
