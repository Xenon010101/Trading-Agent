import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

# Symbol to CoinGecko ID mapping
COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana"
}

# Rate limiting
_last_request_time = 0
REQUEST_INTERVAL = 1.5  # seconds between requests


def _rate_limit():
    """Enforce rate limiting between API calls"""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < REQUEST_INTERVAL:
        time.sleep(REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def get_price_history(symbol, days=7):
    """Get OHLC price history from CoinGecko"""
    coin_id = COINGECKO_MAP.get(symbol)
    if not coin_id:
        return []
    
    _rate_limit()
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 429:
            print(f"[WARN] CoinGecko rate limited on OHLC - waiting...")
            time.sleep(30)
            return []
        
        if response.status_code == 200:
            ohlc_data = response.json()
            closes = [candle[4] for candle in ohlc_data]
            return closes
    except Exception:
        pass
    return []


def calculate_rsi(prices, period=14):
    """Calculate RSI from price list"""
    if len(prices) < period + 1:
        return 50  # Default neutral RSI if not enough data
    
    # Calculate price changes
    deltas = []
    for i in range(1, len(prices)):
        deltas.append(prices[i] - prices[i-1])
    
    # Separate gains and losses
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    
    # Calculate averages
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    
    # Calculate RS and RSI
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 1)


def calculate_macd(prices):
    """Calculate MACD from price list"""
    if len(prices) < 26:
        return "neutral"
    
    # Calculate EMAs
    def ema(prices, period):
        multiplier = 2 / (period + 1)
        ema_value = prices[0]
        for price in prices[1:]:
            ema_value = (price * multiplier) + (ema_value * (1 - multiplier))
        return ema_value
    
    ema_12 = ema(prices, 12)
    ema_26 = ema(prices, 26)
    
    macd_line = ema_12 - ema_26
    
    if macd_line > 0:
        return "bullish"
    elif macd_line < 0:
        return "bearish"
    else:
        return "neutral"


def calculate_trend(prices):
    """Calculate trend from price list"""
    if len(prices) < 10:
        return "consolidation"
    
    # Compare recent 3 vs previous 7
    recent_avg = sum(prices[-3:]) / 3
    older_avg = sum(prices[-10:-3]) / 7
    
    if older_avg == 0:
        return "consolidation"
    
    change_pct = ((recent_avg - older_avg) / older_avg) * 100
    
    if change_pct > 0.5:
        return "uptrend"
    elif change_pct < -0.5:
        return "downtrend"
    else:
        return "consolidation"


def get_current_price(symbol):
    """Get current price from CoinGecko"""
    coin_id = COINGECKO_MAP.get(symbol)
    if not coin_id:
        return None, None
    
    _rate_limit()
    
    price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
    try:
        response = requests.get(price_url, timeout=15)
        
        if response.status_code == 429:
            print(f"[WARN] CoinGecko rate limited - waiting 30s...")
            time.sleep(30)
            return None, None
        
        if response.status_code == 200:
            data = response.json()
            price_info = data.get(coin_id, {})
            price = price_info.get("usd")
            change_24h = price_info.get("usd_24h_change", 0)
            
            if price is None or price == 0:
                return None, None
            
            return {"price": price, "change_24h": change_24h}, price
    except Exception:
        pass
    
    return None, None


def get_market_summary(symbol):
    """Get market summary with real calculated signals"""
    # Get current price
    price_data, current_price = get_current_price(symbol)
    
    if price_data is None:
        return None
    
    # Get price history for signal calculation
    prices = get_price_history(symbol, days=7)
    
    if not prices:
        # No history - use neutral signals
        return {
            "symbol": symbol,
            "price": price_data,
            "signals": {
                "rsi": 50,
                "macd": "neutral",
                "trend": "consolidation",
                "signal": "neutral"
            }
        }
    
    # Calculate real signals
    rsi = calculate_rsi(prices)
    macd = calculate_macd(prices)
    trend = calculate_trend(prices)
    
    # Determine overall signal
    signal_score = 0
    if rsi < 40:
        signal_score += 1
    elif rsi > 60:
        signal_score -= 1
    
    if macd == "bullish":
        signal_score += 1
    elif macd == "bearish":
        signal_score -= 1
    
    if trend == "uptrend":
        signal_score += 1
    elif trend == "downtrend":
        signal_score -= 1
    
    if signal_score >= 2:
        signal = "bullish"
    elif signal_score <= -2:
        signal = "bearish"
    else:
        signal = "neutral"
    
    return {
        "symbol": symbol,
        "price": price_data,
        "signals": {
            "rsi": rsi,
            "macd": macd,
            "trend": trend,
            "signal": signal,
            "momentum": signal_score
        }
    }


def get_market_summary_advanced(symbol):
    """Same as get_market_summary - unified function"""
    return get_market_summary(symbol)


if __name__ == "__main__":
    for sym in ["BTC", "ETH", "SOL"]:
        data = get_market_summary(sym)
        print(f"{sym}: {json.dumps(data, indent=2)}\n")
