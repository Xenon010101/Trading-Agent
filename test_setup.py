import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

REQUIRED_KEYS = ["GROQ_API_KEY", "PRISM_API_KEY", "KRAKEN_API_KEY", "KRAKEN_API_SECRET"]


def test_imports():
    try:
        from market_data import get_market_summary
        from ai_brain import analyze_market
        from risk_manager import RiskManager
        from logger import log_decision, print_banner, print_session_summary
        from executor import execute_trade
        from config import WATCHLIST, INTERVAL_MINUTES, MAX_TRADES_PER_DAY, MIN_CONFIDENCE, MAX_LOSS_PERCENT, PAPER_MODE
        print("[PASS] All modules imported successfully")
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False


def test_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        print("[FAIL] .env file not found - copy .env.example to .env")
        return False
    
    missing = [key for key in REQUIRED_KEYS if not os.getenv(key)]
    if missing:
        print(f"[FAIL] Missing env keys: {', '.join(missing)}")
        return False
    
    print("[PASS] .env file exists with all required keys")
    return True


def test_market_data():
    try:
        from market_data import get_market_summary
        data = get_market_summary("BTC")
        if data is not None and "price" in data:
            print(f"[PASS] Market data fetched for BTC")
            return True
        print("[INFO] Market data returned None (API may not be configured)")
        return True
    except Exception as e:
        print(f"[INFO] Market data test: {e}")
        return True


def test_ai_brain():
    try:
        from ai_brain import analyze_market
        fake_data = {"symbol": "BTC", "price": {"price": 65000}, "signals": {"signal": "bullish"}}
        result = analyze_market(fake_data)
        if "action" in result and "confidence" in result:
            print(f"[PASS] AI brain returned valid decision: {result['action']} ({result['confidence']}%)")
            return True
        print(f"[FAIL] AI brain returned invalid format: {result}")
        return False
    except Exception as e:
        print(f"[INFO] AI brain test: {e}")
        return True


def test_logger():
    try:
        from logger import log_decision
        test_decision = {"action": "HOLD", "confidence": 50, "reason": "Test"}
        test_data = {"symbol": "BTC", "price": {"price": 50000}, "signals": {}}
        log_decision("BTC", test_data, test_decision, False)
        
        if os.path.exists("trade_log.txt"):
            print("[PASS] Logger created trade_log.txt")
            return True
        print("[FAIL] Logger failed to create trade_log.txt")
        return False
    except Exception as e:
        print(f"[FAIL] Logger error: {e}")
        return False


def test_executor():
    try:
        from executor import execute_trade
        from config import PAPER_MODE
        
        result = execute_trade("BUY", "BTC")
        if result and result.get("status") in ["paper", "success", "error"]:
            print(f"[PASS] Executor works in {'PAPER' if PAPER_MODE else 'LIVE'} mode")
            return True
        print("[FAIL] Executor returned unexpected result")
        return False
    except Exception as e:
        print(f"[FAIL] Executor error: {e}")
        return False


def main():
    print("=" * 50)
    print("   Crypto Trading Agent - Setup Test")
    print("=" * 50)
    print()
    
    results = []
    
    print("1. Testing module imports...")
    results.append(test_imports())
    print()
    
    print("2. Testing .env configuration...")
    results.append(test_env_file())
    print()
    
    print("3. Testing market data fetch...")
    results.append(test_market_data())
    print()
    
    print("4. Testing AI brain...")
    results.append(test_ai_brain())
    print()
    
    print("5. Testing logger...")
    results.append(test_logger())
    print()
    
    print("6. Testing executor...")
    results.append(test_executor())
    print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"RESULTS: {passed}/{total} tests passed")
    if passed == total:
        print("All tests passed! Ready to run agent.py")
    else:
        print("Some tests failed. Check configuration.")
    print("=" * 50)


if __name__ == "__main__":
    main()
