import os
import subprocess
from dotenv import load_dotenv
from config import PAPER_MODE

load_dotenv()
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET")

# Map symbols to Kraken format
SYMBOL_MAP = {
    "BTC": "BTCUSD",
    "ETH": "ETHUSD",
    "SOL": "SOLUSD"
}


def is_kraken_available():
    """Check if kraken CLI is installed"""
    try:
        result = subprocess.run(["kraken", "--version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False


KRAKEN_AVAILABLE = is_kraken_available()


def verify_kraken_connection():
    """Verify Kraken API connection is working"""
    if not KRAKEN_AVAILABLE:
        if PAPER_MODE:
            print("✅ Kraken CLI not installed - using simulated paper trading")
        else:
            print("❌ Kraken CLI not installed - cannot execute live trades")
        return KRAKEN_AVAILABLE
    
    try:
        if PAPER_MODE:
            result = subprocess.run(
                ["kraken", "-o", "json", "paper", "balance"],
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            result = subprocess.run(
                ["kraken", "-o", "json", "balance"],
                capture_output=True,
                text=True,
                timeout=10
            )
        
        if result.returncode == 0:
            print("✅ Kraken connected")
            return True
        else:
            print("❌ Kraken connection failed - check API keys")
            return False
    except Exception:
        print("❌ Kraken connection failed - check API keys")
        return False


def execute_buy(symbol, amount=0.001):
    pair = SYMBOL_MAP.get(symbol, f"{symbol}USD")
    
    if PAPER_MODE:
        # Use simulated paper trading
        print(f"[PAPER] BUY order simulated for {symbol} ({pair}) amount {amount}")
        return {"status": "paper", "symbol": symbol, "action": "BUY", "amount": amount, "pair": pair}
    
    # Live trading with kraken CLI
    if not KRAKEN_AVAILABLE:
        print(f"❌ Kraken CLI not installed - cannot execute live BUY for {symbol}")
        return {"status": "error", "symbol": symbol, "action": "BUY", "error": "Kraken CLI not installed"}
    
    try:
        exit_code = os.system(f'kraken order buy {pair} {amount} --type market')
        if exit_code == 0:
            print(f"✅ BUY executed: {symbol} {amount}")
            return {"status": "success", "symbol": symbol, "action": "BUY", "amount": amount}
        else:
            print("Trade execution failed")
            return {"status": "error", "symbol": symbol, "action": "BUY", "error": "Non-zero exit code"}
    except Exception as e:
        print("Trade execution failed")
        return {"status": "error", "symbol": symbol, "action": "BUY", "error": str(e)}


def execute_sell(symbol, amount=0.001):
    pair = SYMBOL_MAP.get(symbol, f"{symbol}USD")
    
    if PAPER_MODE:
        # Use simulated paper trading
        print(f"[PAPER] SELL order simulated for {symbol} ({pair}) amount {amount}")
        return {"status": "paper", "symbol": symbol, "action": "SELL", "amount": amount, "pair": pair}
    
    # Live trading with kraken CLI
    if not KRAKEN_AVAILABLE:
        print(f"❌ Kraken CLI not installed - cannot execute live SELL for {symbol}")
        return {"status": "error", "symbol": symbol, "action": "SELL", "error": "Kraken CLI not installed"}
    
    try:
        exit_code = os.system(f'kraken order sell {pair} {amount} --type market')
        if exit_code == 0:
            print(f"✅ SELL executed: {symbol} {amount}")
            return {"status": "success", "symbol": symbol, "action": "SELL", "amount": amount}
        else:
            print("Trade execution failed")
            return {"status": "error", "symbol": symbol, "action": "SELL", "error": "Non-zero exit code"}
    except Exception as e:
        print("Trade execution failed")
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
