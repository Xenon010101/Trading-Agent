from market_data import get_market_summary
from ai_brain import analyze_market
from risk_manager import RiskManager
from logger import log_decision, print_banner, print_session_summary
from executor import execute_trade
from config import WATCHLIST, INTERVAL_MINUTES
import time
import signal
import sys

risk = RiskManager()


def handle_exit(sig, frame):
    print("Shutting down agent...")
    print_session_summary()
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)


def scan_coin(symbol):
    print(f"Analyzing {symbol}...")
    data = get_market_summary(symbol)
    
    if data is None:
        print(f"Skipping {symbol} - no data")
        return
    
    decision = analyze_market(data)
    
    if risk.can_trade(decision):
        executed = False
        result = execute_trade(decision["action"], symbol)
        if result is not None:
            executed = True
            price = data.get("price", {}).get("price") if data.get("price") else None
            risk.record_trade(symbol, decision["action"], price, decision["confidence"])
        log_decision(symbol, data, decision, executed)
    else:
        log_decision(symbol, data, decision, False)
    
    time.sleep(2)


def main():
    print_banner()
    print("Starting market scan loop. Press Ctrl+C to stop.\n")
    
    while True:
        current_time = time.strftime("%H:%M:%S")
        print(f"\n{'='*50}")
        print(f"[{current_time}] Starting scan of {len(WATCHLIST)} coins...")
        print(f"{'='*50}\n")
        
        for symbol in WATCHLIST:
            scan_coin(symbol)
        
        risk.get_summary()
        print(f"Next scan in {INTERVAL_MINUTES} minutes... (Press Ctrl+C to stop)\n")
        time.sleep(INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
