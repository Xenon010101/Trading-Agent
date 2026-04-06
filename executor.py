import os
import subprocess
from dotenv import load_dotenv
from config import PAPER_MODE

load_dotenv()
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET")


def execute_buy(symbol, amount=0.001):
    if PAPER_MODE:
        print(f"[PAPER] BUY order simulated for {symbol} amount {amount}")
        return {"status": "paper", "symbol": symbol, "action": "BUY", "amount": amount}
    
    try:
        cmd = [
            "kraken-cli", "order", "create",
            "--pair", f"{symbol}USD",
            "--type", "buy",
            "--ordertype", "market",
            "--volume", str(amount)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {"status": "success", "symbol": symbol, "action": "BUY", "output": result.stdout}
        else:
            return {"status": "error", "symbol": symbol, "action": "BUY", "error": result.stderr}
    
    except Exception as e:
        return {"status": "error", "symbol": symbol, "action": "BUY", "error": str(e)}


def execute_sell(symbol, amount=0.001):
    if PAPER_MODE:
        print(f"[PAPER] SELL order simulated for {symbol} amount {amount}")
        return {"status": "paper", "symbol": symbol, "action": "SELL", "amount": amount}
    
    try:
        cmd = [
            "kraken-cli", "order", "create",
            "--pair", f"{symbol}USD",
            "--type", "sell",
            "--ordertype", "market",
            "--volume", str(amount)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {"status": "success", "symbol": symbol, "action": "SELL", "output": result.stdout}
        else:
            return {"status": "error", "symbol": symbol, "action": "SELL", "error": result.stderr}
    
    except Exception as e:
        return {"status": "error", "symbol": symbol, "action": "SELL", "error": str(e)}


def execute_trade(action, symbol):
    if action == "BUY":
        return execute_buy(symbol)
    elif action == "SELL":
        return execute_sell(symbol)
    else:
        print(f"[HOLD] No order placed for {symbol}")
        return None


if __name__ == "__main__":
    print("Testing BUY:")
    result = execute_trade("BUY", "BTC")
    print(f"Result: {result}\n")
    
    print("Testing SELL:")
    result = execute_trade("SELL", "ETH")
    print(f"Result: {result}\n")
    
    print("Testing HOLD:")
    result = execute_trade("HOLD", "SOL")
    print(f"Result: {result}")
