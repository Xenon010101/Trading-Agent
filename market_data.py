import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

# Binance API (Primary - unlimited, no key required)
BINANCE_BASE = "https://api.binance.com/api/v3"

# Symbol to Binance pair mapping
BINANCE_MAP = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "SOL": "SOLUSDT",
}

# CoinGecko ID mapping (Fallback)
COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana"
}

# Rate limiting
_last_request_time = 0
REQUEST_INTERVAL = 0.5  # Reduced since Binance has no limits

# Price cache
_price_cache = {}
_price_cache_time = 0
CACHE_DURATION = 5  # Cache prices for 5 seconds


def _rate_limit():
    """Enforce rate limiting between API calls"""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < REQUEST_INTERVAL:
        time.sleep(REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


# ==================== BINANCE FUNCTIONS ====================

def get_binance_price(symbol):
    """Fetch current price from Binance"""
    pair = BINANCE_MAP.get(symbol)
    if not pair:
        return None
    
    try:
        r = requests.get(
            f"{BINANCE_BASE}/ticker/price",
            params={"symbol": pair},
            timeout=5
        )
        if r.status_code == 200:
            return float(r.json()["price"])
    except Exception:
        pass
    return None


def get_binance_24h_change(symbol):
    """Fetch 24h price change % from Binance"""
    pair = BINANCE_MAP.get(symbol)
    if not pair:
        return None
    
    try:
        r = requests.get(
            f"{BINANCE_BASE}/ticker/24hr",
            params={"symbol": pair},
            timeout=5
        )
        if r.status_code == 200:
            return float(r.json()["priceChangePercent"])
    except Exception:
        pass
    return None


def get_binance_ohlc(symbol, interval="1h", limit=168):
    """Fetch OHLC candles from Binance"""
    pair = BINANCE_MAP.get(symbol)
    if not pair:
        return None
    
    try:
        r = requests.get(
            f"{BINANCE_BASE}/klines",
            params={"symbol": pair, "interval": interval, "limit": limit},
            timeout=5
        )
        if r.status_code == 200:
            candles = r.json()
            return [float(c[4]) for c in candles]  # Return close prices
    except Exception:
        pass
    return None


# ==================== COINGECKO FUNCTIONS (FALLBACK) ====================

def get_coingecko_price(symbol):
    """Fetch current price from CoinGecko (fallback)"""
    coin_id = COINGECKO_MAP.get(symbol)
    if not coin_id:
        return None, None
    
    _rate_limit()
    
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            price_info = data.get(coin_id, {})
            price = price_info.get("usd")
            change = price_info.get("usd_24h_change", 0)
            if price:
                return price, change
    except Exception:
        pass
    return None, None


def get_coingecko_ohlc(symbol, days=7):
    """Fetch OHLC from CoinGecko (fallback)"""
    coin_id = COINGECKO_MAP.get(symbol)
    if not coin_id:
        return []
    
    _rate_limit()
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            ohlc_data = response.json()
            return [candle[4] for candle in ohlc_data]
    except Exception:
        pass
    return []


# ==================== UNIFIED FUNCTIONS ====================

def get_current_price(symbol):
    """Get current price - Binance primary, CoinGecko fallback"""
    global _price_cache, _price_cache_time
    
    # Check cache
    current_time = time.time()
    if symbol in _price_cache and (current_time - _price_cache_time) < CACHE_DURATION:
        return _price_cache[symbol]
    
    # Try Binance first (primary)
    price = get_binance_price(symbol)
    change_24h = get_binance_24h_change(symbol) if price else None
    
    if price is not None:
        _price_cache[symbol] = {"price": price, "change_24h": change_24h}, price
        _price_cache_time = current_time
        return _price_cache[symbol]
    
    # Fallback to CoinGecko
    price, change_24h = get_coingecko_price(symbol)
    if price is not None:
        _price_cache[symbol] = {"price": price, "change_24h": change_24h}, price
        _price_cache_time = current_time
        return _price_cache[symbol]
    
    # Return cached value if exists (even if expired)
    if symbol in _price_cache:
        return _price_cache[symbol]
    
    return None, None


def get_price_history(symbol, days=7):
    """Get OHLC price history - Binance primary, CoinGecko fallback"""
    # Map days to Binance interval
    interval_map = {1: "1h", 7: "1h", 30: "4h", 90: "1d"}
    interval = interval_map.get(days, "1h")
    limit = min(days * 24, 168)  # Max 168 candles
    
    # Try Binance first
    prices = get_binance_ohlc(symbol, interval, limit)
    if prices:
        return prices
    
    # Fallback to CoinGecko
    return get_coingecko_ohlc(symbol, days)


# ==================== SIGNAL CALCULATIONS ====================

def calculate_rsi(prices, period=14):
    """Calculate RSI from price list"""
    if len(prices) < period + 1:
        return 50
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 1)


def calculate_macd(prices):
    """Calculate MACD from price list"""
    if len(prices) < 26:
        return "neutral"
    
    def ema(data, period):
        multiplier = 2 / (period + 1)
        ema_val = data[0]
        for price in data[1:]:
            ema_val = (price * multiplier) + (ema_val * (1 - multiplier))
        return ema_val
    
    ema_12 = ema(prices, 12)
    ema_26 = ema(prices, 26)
    macd_line = ema_12 - ema_26
    
    if macd_line > 0:
        return "bullish"
    elif macd_line < 0:
        return "bearish"
    return "neutral"


def calculate_trend(prices):
    """Calculate trend from price list"""
    if len(prices) < 10:
        return "consolidation"
    
    recent_avg = sum(prices[-3:]) / 3
    older_avg = sum(prices[-10:-3]) / 7
    
    if older_avg == 0:
        return "consolidation"
    
    change_pct = ((recent_avg - older_avg) / older_avg) * 100
    
    if change_pct > 0.5:
        return "uptrend"
    elif change_pct < -0.5:
        return "downtrend"
    return "consolidation"


# ==================== UNIFIED MARKET SUMMARY ====================

def get_market_summary(symbol):
    """Get market summary with signals"""
    price_data, current_price = get_current_price(symbol)
    
    if price_data is None:
        return None
    
    prices = get_price_history(symbol, days=7)
    
    if not prices:
        return {
            "symbol": symbol,
            "price": price_data,
            "signals": {"rsi": 50, "macd": "neutral", "trend": "consolidation", "signal": "neutral"}
        }
    
    rsi = calculate_rsi(prices)
    macd = calculate_macd(prices)
    trend = calculate_trend(prices)
    
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
    
    signal = "bullish" if signal_score >= 2 else "bearish" if signal_score <= -2 else "neutral"
    
    return {
        "symbol": symbol,
        "price": price_data,
        "signals": {"rsi": rsi, "macd": macd, "trend": trend, "signal": signal, "momentum": signal_score}
    }


def get_market_summary_advanced(symbol):
    """Same as get_market_summary"""
    return get_market_summary(symbol)


if __name__ == "__main__":
    for sym in ["BTC", "ETH", "SOL"]:
        data = get_market_summary(sym)
        print(f"{sym}: {json.dumps(data, indent=2)}\n")