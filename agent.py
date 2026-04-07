from market_data import get_market_summary_advanced as get_market_summary
from ai_brain import analyze_market
from risk_manager import RiskManager
from logger import log_decision, print_banner, print_session_summary
from executor import execute_trade, verify_kraken_connection
from report import generate_daily_report, calculate_sharpe_ratio
from erc8004 import create_agent_wallet, post_checkpoint, get_checkpoint_summary
from datetime import date
from config import WATCHLIST, INTERVAL_MINUTES, MAX_TRADES_PER_DAY, MIN_CONFIDENCE, MAX_LOSS_PERCENT, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT, PAPER_MODE
import time
import signal
import sys
import os
from dotenv import load_dotenv

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
    get_checkpoint_summary()
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
    
    buy_price = risk.positions[symbol]["buy_price"]
    pnl_percent = ((current_price - buy_price) / buy_price) * 100
    
    if pnl_percent >= TAKE_PROFIT_PERCENT:
        print(f"\n  💰 TAKE PROFIT TRIGGERED for {symbol} — locking in {pnl_percent:.2f}% gain")
        return {"action": "SELL", "confidence": 95, "reason": f"Take profit target hit (+{pnl_percent:.2f}%)"}
    
    if pnl_percent <= -STOP_LOSS_PERCENT:
        print(f"\n  ⚠️ STOP LOSS TRIGGERED for {symbol} — selling at loss of {abs(pnl_percent):.2f}%")
        return {"action": "SELL", "confidence": 95, "reason": f"Stop loss triggered ({pnl_percent:.2f}%)"}
    
    return None


def scan_coin(symbol):
    """Analyze a single coin and execute if conditions are met"""
    # Check circuit breaker first
    if risk.check_circuit_breaker():
        print(f"   [CIRCUIT BREAKER ACTIVE] Skipping {symbol}")
        return None
    
    # Step 1: Fetch market data from PRISM API
    data = get_market_summary(symbol)
    
    if data is None:
        print(f"   [!] Skipping {symbol} - no data received")
        return None
    
    # Get current price
    current_price = data.get("price", {}).get("price")
    
    # Step 2: Check exit conditions BEFORE asking AI
    if current_price:
        exit_decision = check_exit_conditions(symbol, current_price)
        if exit_decision and risk.can_trade(exit_decision):
            result = execute_trade(exit_decision["action"], symbol)
            if result is not None:
                risk.record_trade(symbol, "SELL", current_price, exit_decision["confidence"])
                log_decision(symbol, data, exit_decision, True)
            time.sleep(2)
            return data
    
    # Step 3: Get AI decision from LLaMA 70B
    decision = analyze_market(data)
    
    # Step 4: Check if trade is allowed by risk manager
    if risk.can_trade(decision):
        # Step 5: Execute the trade (or simulate in paper mode)
        executed = False
        result = execute_trade(decision["action"], symbol)
        
        if result is not None:
            executed = True
            # Extract price from market data for logging
            price = data.get("price", {}).get("price") if data.get("price") else None
            risk.record_trade(symbol, decision["action"], price, decision["confidence"])
        
        # Step 6: Log the decision with execution status
        log_decision(symbol, data, decision, executed)
    else:
        # Decision blocked by risk manager - still log it
        log_decision(symbol, data, decision, False)
    
    # Record checkpoint on ERC-8004
    post_checkpoint(
        action=decision.get("action", "HOLD"),
        symbol=symbol,
        confidence=decision.get("confidence", 0),
        reason=decision.get("reason", "No decision")
    )
    
    time.sleep(2)  # Brief pause between coins to avoid rate limits
    return data


def main():
    """Main entry point - runs continuous market scan loop"""
    global shutdown_requested, scan_cycle_count, last_reset_date
    
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handle_exit)
    
    # Show banner
    print_banner()
    
    # Verify environment setup
    if not check_env_keys():
        print("Continuing in limited mode...\n")
    
    # Show current configuration
    print_config()
    
    # Verify Kraken connection if not in paper mode
    if not PAPER_MODE:
        verify_kraken_connection()
    
    # Setup ERC-8004 blockchain integration
    create_agent_wallet()
    print("  ERC-8004 Checkpoints : ACTIVE")
    
    print("Starting market scan loop. Press Ctrl+C to stop.\n")
    
    # Main scanning loop
    while not shutdown_requested:
        # Check if date has changed - reset daily counters for new day
        if date.today() > risk.last_reset_date:
            print(f"\n  [DATE CHANGE] New day detected: {date.today()}")
            risk.reset_for_new_day()
            risk.last_reset_date = date.today()
            generate_daily_report()
        
        scan_cycle_count += 1
        current_time = time.strftime("%H:%M:%S")
        
        # Scan header
        print("\n" + "=" * 50)
        print(f"  SCAN CYCLE [{current_time}] #{scan_cycle_count}")
        print(f"  Analyzing {len(WATCHLIST)} coins: {', '.join(WATCHLIST)}")
        print("=" * 50)
        
        # Analyze each coin in watchlist and collect prices
        current_prices = {}
        for symbol in WATCHLIST:
            data = scan_coin(symbol)
            if data and data.get("price"):
                price = data["price"].get("price")
                if price:
                    current_prices[symbol] = price
        
        # Show open positions with current prices
        risk.get_open_positions(current_prices)
        
        # Show risk manager summary after each cycle
        risk.get_summary()
        
        # Generate daily report every 10 cycles
        if scan_cycle_count % 10 == 0:
            generate_daily_report()
            calculate_sharpe_ratio()
        
        # Calculate sleep time and wait for next cycle
        sleep_seconds = INTERVAL_MINUTES * 60
        print(f"\n  Next scan in {INTERVAL_MINUTES} minute(s)...")
        print(f"  Press Ctrl+C to stop\n")
        
        # Sleep in small increments to allow quick exit on Ctrl+C
        while sleep_seconds > 0 and not shutdown_requested:
            time.sleep(min(sleep_seconds, 5))
            sleep_seconds -= 5


if __name__ == "__main__":
    main()
