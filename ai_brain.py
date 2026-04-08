import groq
import os
import json
import time
import re
from dotenv import load_dotenv

load_dotenv()

KEY_1 = os.getenv("GROQ_API_KEY")
KEY_2 = os.getenv("GROQ_API_KEY_2")
API_KEYS = [k for k in [KEY_1, KEY_2] if k]
current_key_index = 0


def get_groq_client(key_index=None):
    """Get Groq client with optional key rotation"""
    if key_index is None:
        key_index = current_key_index
    return groq.Groq(api_key=API_KEYS[key_index % len(API_KEYS)])


def analyze_market(market_data):
    """
    Analyze market data using Groq LLaMA 70B and return trading decision.
    
    Args:
        market_data: Dict containing symbol, price, and signals from PRISM API
    
    Returns:
        Dict with action (BUY/SELL/HOLD), confidence (0-100), and reason
    """
    # Build comprehensive prompt with market data and trading rules
    prompt = f"""You are a conservative cryptocurrency trader using MULTI-SIGNAL SCORING. Calculate the EXACT score and respond ONLY with JSON.

Market Data:
{json.dumps(market_data, indent=2)}

=== SIGNAL SCORING (Add all 4 signals) ===

SIGNAL 1 - TREND:
- Uptrend = +1
- Downtrend = -1
- Consolidation = 0

SIGNAL 2 - MACD:
- Bullish = +1
- Bearish = -1
- Neutral = 0

SIGNAL 3 - RSI:
- RSI < 35 (strongly oversold) = +2
- RSI 35-50 = +1
- RSI 50-60 = 0 (neutral - normal in bull market)
- RSI 60-70 = -1 (slightly overbought)
- RSI > 70 (overbought) = -2

SIGNAL 4 - VOLUME:
- High volume = +1
- Normal/low = 0

=== DECISION RULES ===

TOTAL SCORE = Trend + MACD + RSI + Volume

- Score >= +3 → BUY (confidence 85%)
- Score = +2 → BUY (confidence 75%)
- Score = +1 or 0 or -1 → HOLD (confidence 50%)
- Score = -2 → SELL (confidence 75%)
- Score <= -3 → SELL (confidence 85%)

=== NO-TRADE ZONE ===

If high volatility AND mixed signals → HOLD regardless of score.

=== OUTPUT FORMAT ===

Example: {{"action": "BUY", "confidence": 85, "reason": "Score +3: Trend +1, MACD +1, RSI +2 (oversold), Volume +1"}}

Output ONLY the JSON, nothing else.
"""
    
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a conservative crypto trading expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=200
        )
        
        raw_response = response.choices[0].message.content
        
        start_idx = raw_response.find("{")
        end_idx = raw_response.rfind("}") + 1
        
        if start_idx == -1 or end_idx == 0:
            return {"action": "HOLD", "confidence": 50, "reason": "Failed to parse AI response"}
        
        json_str = raw_response[start_idx:end_idx]
        decision = json.loads(json_str)
        
        action = decision.get("action", "HOLD")
        reason = decision.get("reason", "")
        
        # Extract score from reason
        score = 0
        score_match = re.search(r'[Ss]core\s*([+-]?\d+)', reason)
        if score_match:
            score = int(score_match.group(1))
        
        # Enforce confidence based on score
        if score >= 3:
            decision["action"] = "BUY"
            decision["confidence"] = 85
        elif score == 2:
            decision["action"] = "BUY"
            decision["confidence"] = 75
        elif score == 1:
            decision["action"] = "BUY"
            decision["confidence"] = 65
        elif score <= -3:
            decision["action"] = "SELL"
            decision["confidence"] = 85
        elif score == -2:
            decision["action"] = "SELL"
            decision["confidence"] = 75
        elif score == -1:
            decision["action"] = "SELL"
            decision["confidence"] = 65
        else:
            decision["action"] = "HOLD"
            decision["confidence"] = 50
        
        # Only trade if confidence >= 60 (MIN_CONFIDENCE)
        if decision["confidence"] < 60:
            print(f"  [HOLD] Skipping trade - low confidence ({decision['confidence']}%)")
            decision["action"] = "HOLD"
        
        return decision
    
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e):
            global current_key_index
            if len(API_KEYS) > 1:
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                print(f"  [RATE LIMIT] Switching to backup API key {current_key_index + 1}/{len(API_KEYS)}...")
                try:
                    client = get_groq_client(current_key_index)
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a conservative crypto trading expert."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2,
                        max_tokens=200
                    )
                    raw_response = response.choices[0].message.content
                    start_idx = raw_response.find("{")
                    end_idx = raw_response.rfind("}") + 1
                    if start_idx != -1 and end_idx > 0:
                        json_str = raw_response[start_idx:end_idx]
                        decision = json.loads(json_str)
                        reason = decision.get("reason", "")
                        score_match = re.search(r'[Ss]core\s*([+-]?\d+)', reason)
                        score = int(score_match.group(1)) if score_match else 0
                        
                        if score >= 3:
                            decision["action"] = "BUY"
                            decision["confidence"] = 85
                        elif score == 2:
                            decision["action"] = "BUY"
                            decision["confidence"] = 75
                        elif score == 1:
                            decision["action"] = "BUY"
                            decision["confidence"] = 65
                        elif score <= -3:
                            decision["action"] = "SELL"
                            decision["confidence"] = 85
                        elif score == -2:
                            decision["action"] = "SELL"
                            decision["confidence"] = 75
                        elif score == -1:
                            decision["action"] = "SELL"
                            decision["confidence"] = 65
                        else:
                            decision["action"] = "HOLD"
                            decision["confidence"] = 50
                        
                        if decision["confidence"] < 60:
                            decision["action"] = "HOLD"
                        
                        return decision
                except:
                    print("  [RATE LIMIT] All keys exhausted - waiting 30 seconds...")
                    time.sleep(30)
                    return {"action": "HOLD", "confidence": 50, "reason": "Rate limit - all keys exhausted"}
            else:
                print("  [RATE LIMIT] No backup key - waiting 30 seconds...")
                time.sleep(30)
                return {"action": "HOLD", "confidence": 50, "reason": "Rate limit - no backup key"}
        
        print(f"  AI analysis error: {e}")
        return {"action": "HOLD", "confidence": 50, "reason": "AI error"}


if __name__ == "__main__":
    # Test with fake data when run directly
    fake_data = {"symbol": "BTC", "price": {"price": 65000}, "signals": {"signal": "bullish"}}
    result = analyze_market(fake_data)
    print(result)
