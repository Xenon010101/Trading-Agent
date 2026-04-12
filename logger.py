import json
import time
import os
from config import WATCHLIST


def log_decision(symbol, market_data, decision, executed):
    price = None
    if market_data and "price" in market_data:
        price_data = market_data["price"]
        if isinstance(price_data, dict):
            price = price_data.get("price", price_data.get("current_price"))
    
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "price": price,
        "action": decision.get("action", "HOLD"),
        "confidence": decision.get("confidence", 0),
        "reason": decision.get("reason", ""),
        "executed": executed
    }
    
    with open("trade_log.txt", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    action = decision.get("action", "HOLD")
    confidence = decision.get("confidence", 0)
    reason = decision.get("reason", "")
    
    print(f"  {symbol}: {action} - conf: {confidence}% | {reason}")


def print_session_summary():
    if not os.path.exists("trade_log.txt"):
        return
    
    with open("trade_log.txt", "r") as f:
        lines = f.readlines()
    
    total = len(lines)
    buys = sum(1 for l in lines if '"action": "BUY"' in l)
    sells = sum(1 for l in lines if '"action": "SELL"' in l)
    
    print(f"\n  Session: {total} decisions ({buys} buys, {sells} sells)\n")


def print_banner():
    coins = ", ".join(WATCHLIST)
    mode = "PAPER TRADING" if os.getenv("PAPER_MODE", "True").lower() == "true" else "LIVE TRADING"
    print("\n=============================================")
    print("           InsiderEdge v1.0")
    print("      Autonomous AI Crypto Trading Agent")
    print("=============================================")
    print(f"     Mode: {mode}")
    print(f"     Coins: {coins}")
    print(f"     ERC-8004: ACTIVE (Sepolia testnet)")
    print("=============================================\n")
