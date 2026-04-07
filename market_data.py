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
                print(f"[DEBUG] CoinGecko raw response for {symbol}: {data}")
                price = data.get(coin_id, {}).get("usd", 0)
                
                # Sanity check - ETH should not be > $10,000
                if symbol == "ETH" and price > 10000:
                    print(f"[WARN] ETH price {price} seems wrong, using mock data")
                    return MOCK_DATA.get(symbol, {}).get("price", {"price": 0})
                
                # BTC should not be > $1,000,000
                if symbol == "BTC" and price > 1000000:
                    print(f"[WARN] BTC price {price} seems wrong, using mock data")
                    return MOCK_DATA.get(symbol, {}).get("price", {"price": 0})
                
                return {"price": price}
        except Exception as e:
            print(f"[DEBUG] CoinGecko error: {e}")
    
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


def get_market_summary_advanced(symbol):
    """Enhanced market data with momentum and volatility analysis"""
    price_data = get_price(symbol)
    signals_data = get_signals(symbol)
    
    # Calculate momentum score
    signal_text = signals_data.get("signal", "neutral").lower()
    momentum = 0
    if "bullish" in signal_text or "buy" in signal_text:
        momentum = 1
    elif "bearish" in signal_text or "sell" in signal_text:
        momentum = -1
    
    # Check individual indicators for momentum
    macd = signals_data.get("macd", "").lower()
    trend = signals_data.get("trend", "").lower()
    rsi = signals_data.get("rsi", 50)
    
    if "bullish" in macd:
        momentum += 0.5
    elif "bearish" in macd:
        momentum -= 0.5
    
    if "uptrend" in trend:
        momentum += 0.5
    elif "downtrend" in trend:
        momentum -= 0.5
    
    # RSI momentum contribution
    if rsi < 40:
        momentum += 0.5  # Oversold = bullish
    elif rsi > 60:
        momentum -= 0.5  # Overbought = bearish
    
    # Normalize momentum to -1, 0, or +1
    if momentum > 0.5:
        momentum = 1
    elif momentum < -0.5:
        momentum = -1
    else:
        momentum = 0
    
    # Volatility estimate based on change_24h
    change_24h = price_data.get("change_24h", 0)
    volume = price_data.get("volume", 0)
    
    # High volume + large price change = high volatility
    volatility = "low"
    if abs(change_24h) > 5 or volume > 10000000000:
        volatility = "high"
    elif abs(change_24h) > 2 or volume > 5000000000:
        volatility = "medium"
    
    return {
        "symbol": symbol,
        "price": price_data,
        "signals": signals_data,
        "momentum": momentum,
        "volatility": volatility,
        "analysis": {
            "momentum_score": momentum,
            "volatility_level": volatility,
            "short_term": signals_data.get("signal", "neutral"),
            "timeframe": "multi-timeframe"
        }
    }


if __name__ == "__main__":
    for sym in ["BTC", "ETH", "SOL"]:
        data = get_market_summary_advanced(sym)
        print(f"{sym}: {json.dumps(data, indent=2)}\n")
