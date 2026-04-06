from market_data import get_market_summary
from ai_brain import analyze_market
from risk_manager import RiskManager
from logger import log_decision, print_banner, print_session_summary
from executor import execute_trade
from config import WATCHLIST, INTERVAL_MINUTES, MAX_TRADES_PER_DAY, MIN_CONFIDENCE, MAX_LOSS_PERCENT, PAPER_MODE
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


def handle_exit(sig, frame):
    """Clean shutdown handler for Ctrl+C"""
    global shutdown_requested
    if shutdown_requested:
        return  # Prevent double-calls
    shutdown_requested = True
    
    print("\n\n" + "=" * 50)
    print("   Shutting down agent...")
    print("=" * 50 + "\n")
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
    print("-" * 50 + "\n")


def scan_coin(symbol):
    """Analyze a single coin and execute if conditions are met"""
    # Step 1: Fetch market data from PRISM API
    data = get_market_summary(symbol)
    
    if data is None:
        print(f"   [!] Skipping {symbol} - no data received")
        return None
    
    # Step 2: Get AI decision from LLaMA 70B
    decision = analyze_market(data)
    
    # Step 3: Check if trade is allowed by risk manager
    if risk.can_trade(decision):
        # Step 4: Execute the trade (or simulate in paper mode)
        executed = False
        result = execute_trade(decision["action"], symbol)
        
        if result is not None:
            executed = True
            # Extract price from market data for logging
            price = data.get("price", {}).get("price") if data.get("price") else None
            risk.record_trade(symbol, decision["action"], price, decision["confidence"])
        
        # Step 5: Log the decision with execution status
        log_decision(symbol, data, decision, executed)
    else:
        # Decision blocked by risk manager - still log it
        log_decision(symbol, data, decision, False)
    
    time.sleep(2)  # Brief pause between coins to avoid rate limits
    return data


def main():
    """Main entry point - runs continuous market scan loop"""
    global shutdown_requested
    
    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handle_exit)
    
    # Show banner
    print_banner()
    
    # Verify environment setup
    if not check_env_keys():
        print("Continuing in limited mode...\n")
    
    # Show current configuration
    print_config()
    
    print("Starting market scan loop. Press Ctrl+C to stop.\n")
    
    # Main scanning loop
    while not shutdown_requested:
        current_time = time.strftime("%H:%M:%S")
        
        # Scan header
        print("\n" + "=" * 50)
        print(f"  SCAN CYCLE [{current_time}]")
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
