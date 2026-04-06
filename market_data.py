import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
PRISM_API_KEY = os.getenv("PRISM_API_KEY")


def get_price(symbol):
    url = f"https://api.prismapi.ai/crypto/{symbol}/price"
    headers = {"X-API-Key": PRISM_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None


def get_signals(symbol):
    url = f"https://api.prismapi.ai/signals/{symbol}"
    headers = {"X-API-Key": PRISM_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching signals for {symbol}: {e}")
        return None


def get_market_summary(symbol):
    price_data = get_price(symbol)
    if price_data is None:
        return None
    
    signals_data = get_signals(symbol)
    if signals_data is None:
        return None
    
    return {"symbol": symbol, "price": price_data, "signals": signals_data}


if __name__ == "__main__":
    data = get_market_summary("BTC")
    print(json.dumps(data, indent=2))
