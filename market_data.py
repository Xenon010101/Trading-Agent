import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()

# ── API endpoints ──────────────────────────────────────────────────────────────
BINANCE_BASE   = "https://api.binance.com/api/v3"
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# ── Symbol maps ────────────────────────────────────────────────────────────────
BINANCE_MAP = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "SOL": "SOLUSDT",
}

COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
}

# ── Cache — per-symbol so each coin has its own expiry ─────────────────────────
# FIX 2: was a single global timestamp shared across all symbols
_cache: dict[str, dict] = {}   # { "BTC": {"price": ..., "change_24h": ..., "ts": ...} }
CACHE_DURATION = 10            # seconds — fine for a 5-min scan loop

REQUEST_INTERVAL = 0.5         # minimum gap between any two HTTP calls
_last_request_time = 0.0


def _rate_limit():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < REQUEST_INTERVAL:
        time.sleep(REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


# ══════════════════════════════════════════════════════════════════════════════
#  BINANCE  (primary — no API key, no monthly cap)
# ══════════════════════════════════════════════════════════════════════════════

def get_binance_price(symbol: str) -> float | None:
    """Current price from Binance ticker."""
    pair = BINANCE_MAP.get(symbol)
    if not pair:
        return None
    try:
        r = requests.get(f"{BINANCE_BASE}/ticker/price",
                         params={"symbol": pair}, timeout=5)
        if r.status_code == 200:
            return float(r.json()["price"])
    except Exception:
        pass
    return None


def get_binance_24h_ticker(symbol: str) -> dict | None:
    """Full 24hr ticker from Binance (price, change%, volume)."""
    pair = BINANCE_MAP.get(symbol)
    if not pair:
        return None
    try:
        r = requests.get(f"{BINANCE_BASE}/ticker/24hr",
                         params={"symbol": pair}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return {
                "price": float(data["lastPrice"]),
                "change_pct": float(data["priceChangePercent"]),
                "volume": float(data["quoteVolume"]),
            }
    except Exception:
        pass
    return None


def get_binance_24h_change(symbol: str) -> float | None:
    """24 h price-change % from Binance."""
    ticker = get_binance_24h_ticker(symbol)
    if ticker:
        return ticker["change_pct"]
    return None


def get_binance_volume(symbol: str) -> float | None:
    """24h trading volume in USDT from Binance."""
    ticker = get_binance_24h_ticker(symbol)
    if ticker:
        return ticker["volume"]
    return None


def get_binance_ohlc(symbol: str, interval: str = "1h", limit: int = 168) -> list[float] | None:
    """Close prices from Binance klines."""
    pair = BINANCE_MAP.get(symbol)
    if not pair:
        return None
    try:
        r = requests.get(f"{BINANCE_BASE}/klines",
                         params={"symbol": pair, "interval": interval, "limit": limit},
                         timeout=5)
        if r.status_code == 200:
            return [float(c[4]) for c in r.json()]   # index 4 = close price
    except Exception:
        pass
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  COINGECKO  (fallback — 30 req/min, 10 k/month free)
# ══════════════════════════════════════════════════════════════════════════════

def get_coingecko_price(symbol: str) -> tuple[float | None, float | None]:
    """Returns (price, change_24h) or (None, None)."""
    coin_id = COINGECKO_MAP.get(symbol)
    if not coin_id:
        return None, None
    _rate_limit()
    try:
        r = requests.get(
            f"{COINGECKO_BASE}/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=10,
        )
        if r.status_code == 200:
            info = r.json().get(coin_id, {})
            price  = info.get("usd")
            change = info.get("usd_24h_change", 0.0)
            if price:
                return float(price), float(change)
    except Exception:
        pass
    return None, None


def get_coingecko_ohlc(symbol: str, days: int = 7) -> list[float]:
    """Close prices from CoinGecko OHLC endpoint."""
    coin_id = COINGECKO_MAP.get(symbol)
    if not coin_id:
        return []
    _rate_limit()
    try:
        r = requests.get(
            f"{COINGECKO_BASE}/coins/{coin_id}/ohlc",
            params={"vs_currency": "usd", "days": days},
            timeout=10,
        )
        if r.status_code == 200:
            return [float(c[4]) for c in r.json()]   # index 4 = close
    except Exception:
        pass
    return []


# ══════════════════════════════════════════════════════════════════════════════
#  UNIFIED  — always call these from agent.py / ai_brain.py
# ══════════════════════════════════════════════════════════════════════════════

def get_current_price(symbol: str) -> tuple[float | None, float | None, float]:
    """
    Returns (price: float, change_24h: float, volume: float) or (None, None, 0.0).

    FIX 1 + 2: was returning a (dict, float) tuple and used a shared
    cache timestamp for all symbols. Now each symbol has its own cache
    entry and this function always returns three plain floats.
    """
    now = time.time()

    # Per-symbol cache hit
    cached = _cache.get(symbol)
    if cached and (now - cached["ts"]) < CACHE_DURATION:
        return cached["price"], cached["change_24h"], cached.get("volume", 0.0)

    # ── Primary: Binance ──────────────────────────────────────────────
    ticker = get_binance_24h_ticker(symbol)
    if ticker is not None:
        price = ticker["price"]
        change = ticker["change_pct"]
        volume = ticker["volume"]
        _cache[symbol] = {"price": price, "change_24h": change, "volume": volume, "ts": now}
        return price, change, volume

    # ── Fallback: CoinGecko ───────────────────────────────────────────
    price, change = get_coingecko_price(symbol)
    if price is not None:
        volume = 0.0
        _cache[symbol] = {"price": price, "change_24h": change or 0.0, "volume": volume, "ts": now}
        return price, change or 0.0, volume

    # ── Last resort: return stale cache rather than None ─────────────
    if cached:
        return cached["price"], cached["change_24h"], cached.get("volume", 0.0)

    return None, None, 0.0


def get_price_history(symbol: str, days: int = 7) -> list[float]:
    """
    Returns a list of close prices (floats), newest last.
    Binance primary, CoinGecko fallback.
    """
    interval_map = {1: ("1h", 24), 7: ("1h", 168), 30: ("4h", 180), 90: ("1d", 90)}
    interval, limit = interval_map.get(days, ("1h", 168))

    prices = get_binance_ohlc(symbol, interval, limit)
    if prices:
        return prices

    return get_coingecko_ohlc(symbol, days)


# ══════════════════════════════════════════════════════════════════════════════
#  TECHNICAL INDICATORS
# ══════════════════════════════════════════════════════════════════════════════

def calculate_rsi(prices: list[float], period: int = 14) -> float:
    """Wilder RSI with proper exponential smoothing. Returns 50 if insufficient data."""
    if len(prices) < period + 1:
        return 50.0

    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]

    avg_gain = 0.0
    avg_loss = 0.0
    for i, d in enumerate(deltas):
        gain = d if d > 0 else 0.0
        loss = -d if d < 0 else 0.0
        if i < period:
            avg_gain += gain
            avg_loss += loss
        else:
            if i == period:
                avg_gain /= period
                avg_loss /= period
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 1)


def calculate_macd(prices: list[float]) -> str:
    """Returns 'bullish', 'bearish', or 'neutral'."""
    if len(prices) < 26:
        return "neutral"

    def ema(data: list[float], period: int) -> float:
        k = 2 / (period + 1)
        val = data[0]
        for p in data[1:]:
            val = p * k + val * (1 - k)
        return val

    macd_line = ema(prices, 12) - ema(prices, 26)
    if macd_line > 0:
        return "bullish"
    if macd_line < 0:
        return "bearish"
    return "neutral"


def calculate_trend(prices: list[float]) -> str:
    """Returns 'uptrend', 'downtrend', or 'consolidation'."""
    if len(prices) < 10:
        return "consolidation"

    recent_avg = sum(prices[-3:]) / 3
    older_avg  = sum(prices[-10:-3]) / 7

    if older_avg == 0:
        return "consolidation"

    change_pct = (recent_avg - older_avg) / older_avg * 100
    if change_pct > 0.5:
        return "uptrend"
    if change_pct < -0.5:
        return "downtrend"
    return "consolidation"


# ══════════════════════════════════════════════════════════════════════════════
#  MARKET SUMMARY  — main entry point for agent.py / ai_brain.py
# ══════════════════════════════════════════════════════════════════════════════

def get_market_summary(symbol: str) -> dict | None:
    """
    Returns a dict with keys:
      symbol, price, change_24h, signals{rsi, macd, trend, signal, momentum}

    FIX 3: was storing a dict inside 'price' — now always a plain float.
    """
    price, change_24h, volume = get_current_price(symbol)

    if price is None:
        return None

    prices = get_price_history(symbol, days=7)

    rsi   = calculate_rsi(prices)   if prices else 50.0
    macd  = calculate_macd(prices)  if prices else "neutral"
    trend = calculate_trend(prices) if prices else "consolidation"

    score = 0
    if rsi < 35:
        score += 2
    elif rsi < 50:
        score += 1
    elif rsi > 70:
        score -= 2
    elif rsi > 60:
        score -= 1
    if macd == "bullish":
        score += 1
    elif macd == "bearish":
        score -= 1
    if trend == "uptrend":
        score += 1
    elif trend == "downtrend":
        score -= 1
    if volume > 0:
        score += 1

    signal = "bullish" if score >= 2 else "bearish" if score <= -2 else "neutral"

    return {
        "symbol":    symbol,
        "price":     price,
        "change_24h": change_24h,
        "volume":    volume,
        "signals": {
            "rsi":      rsi,
            "macd":     macd,
            "trend":    trend,
            "signal":   signal,
            "momentum": score,
            "volume":   volume,
        },
    }


# Alias kept so existing imports don't break
get_market_summary_advanced = get_market_summary


# ══════════════════════════════════════════════════════════════════════════════
#  Quick smoke-test
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    for sym in ["BTC", "ETH", "SOL"]:
        data = get_market_summary(sym)
        print(f"\n{sym}:")
        print(json.dumps(data, indent=2))