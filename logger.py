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
    time_str = time.strftime("%H:%M:%S")
    
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(action, "⚪")
    executed_str = "Yes" if executed else "No"
    
    print("----------------------------------------")
    print(f"[{time_str}] {symbol} Analysis Complete")
    print(f"Action     : {action} {emoji}")
    print(f"Confidence : {confidence}%")
    print(f"Reason     : {reason}")
    print(f"Executed   : {executed_str}")
    print("----------------------------------------")


def print_session_summary():
    if not os.path.exists("trade_log.txt"):
        print("No trade log found.")
        return
    
    with open("trade_log.txt", "r") as f:
        lines = f.readlines()
    
    total = len(lines)
    buys = 0
    sells = 0
    holds = 0
    
    for line in lines:
        try:
            entry = json.loads(line.strip())
            action = entry.get("action", "")
            if action == "BUY":
                buys += 1
            elif action == "SELL":
                sells += 1
            elif action == "HOLD":
                holds += 1
        except:
            pass
    
    print("\n========== SESSION SUMMARY ==========")
    print(f"Total Decisions: {total}")
    print(f"BUY  : {buys}")
    print(f"SELL : {sells}")
    print(f"HOLD : {holds}")
    print("====================================\n")


def print_banner():
    coins = ", ".join(WATCHLIST)
    mode = "PAPER TRADING" if os.getenv("PAPER_MODE", "True").lower() == "true" else "LIVE TRADING"
    print("=============================================")
    print("     InsiderEdge 🤖")
    print("     Autonomous AI Crypto Trading Agent")
    print("     Powered by Groq AI + PRISM + Kraken")
    print("=============================================")
    print(f"     Mode: {mode}")
    print(f"     Coins: {coins}")
    print("     ERC-8004         : ACTIVE (Sepolia testnet)")
    print("=============================================")
