import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
PRISM_API_KEY = os.getenv("PRISM_API_KEY")

# Symbol to CoinGecko ID mapping
COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana"
}

# Fallback mock data when all APIs are unavailable
MOCK_DATA = {
    "BTC": {
        "price": {"price": 67450.00, "change_24h": 2.3, "volume": 28500000000},
        "signals": {"rsi": 58, "macd": "bullish", "trend": "uptrend", "signal": "neutral"}
    },
    "ETH": {
        "price": {"price": 3520.00, "change_24h": 1.8, "volume": 15200000000},
        "signals": {"rsi": 62, "macd": "bullish", "trend": "uptrend", "signal": "bullish"}
    },
    "SOL": {
        "price": {"price": 178.50, "change_24h": -0.5, "volume": 3200000000},
        "signals": {"rsi": 45, "macd": "bearish", "trend": "consolidation", "signal": "neutral"}
    }
}


def get_price(symbol):
    headers = {"X-API-Key": PRISM_API_KEY, "Content-Type": "application/json"}
    
    # Try PRISM API first
    url = f"https://api.prismapi.ai/v1/crypto/{symbol}/quote"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    # Fallback to CoinGecko
    coin_id = COINGECKO_MAP.get(symbol)
    if coin_id:
        cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        try:
            response = requests.get(cg_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                price = data.get(coin_id, {}).get("usd", 0)
                return {"price": price}
        except:
            pass
    
    # Last resort: mock data
    return MOCK_DATA.get(symbol, {}).get("price", {"price": 0})


def get_signals(symbol):
    headers = {"X-API-Key": PRISM_API_KEY, "Content-Type": "application/json"}
    
    url = f"https://api.prismapi.ai/v1/signals/{symbol}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    return MOCK_DATA.get(symbol, {}).get("signals", {"signal": "neutral"})


def get_market_summary(symbol):
    price_data = get_price(symbol)
    signals_data = get_signals(symbol)
    
    return {
        "symbol": symbol,
        "price": price_data,
        "signals": signals_data
    }


if __name__ == "__main__":
    for sym in ["BTC", "ETH", "SOL"]:
        data = get_market_summary(sym)
        print(f"{sym}: {json.dumps(data, indent=2)}\n")
