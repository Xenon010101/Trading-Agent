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
    prompt = f"""You are a conservative cryptocurrency trader using MULTI-CONFIRMATION strategy.

Market Data:
{json.dumps(market_data, indent=2)}

=== SCORING SYSTEM (ALL THREE signals must agree) ===

SIGNAL 1 - Trend Direction:
- Uptrend = +1 point
- Downtrend = -1 point
- Consolidation = 0 points

SIGNAL 2 - MACD:
- Bullish crossover = +1 point
- Bearish crossover = -1 point
- Neutral = 0 points

SIGNAL 3 - RSI:
- Below 35 (strongly oversold) = +2 points
- 35-45 (oversold) = +1 point
- 45-55 (neutral) = 0 points
- 55-65 (slightly overbought) = -1 point
- Above 65 (overbought) = -2 points

=== DECISION RULES ===

CALCULATE YOUR SCORE:
Total = Trend_points + MACD_points + RSI_points

THEN DECIDE:
- Score +3 = STRONG BUY (confidence 88%)
- Score +2 = BUY (confidence 75%)
- Score +1 = BUY (confidence 60%)
- Score -1 = SELL (confidence 60%)
- Score -2 = SELL (confidence 75%)
- Score -3 = STRONG SELL (confidence 88%)
- Score 0 = HOLD (confidence 50%)

=== CRITICAL RULES ===

1. Calculate the score EXPLICITLY in your reasoning
2. Only BUY when score is +2 or higher
3. Only SELL when score is -2 or lower
4. HOLD everything else - protect capital above all
5. NEVER force a trade when signals are unclear

REQUIREMENTS:
- Always mention the EXACT SCORE in your reason
- Example: "Score +3: RSI 32 (oversold +2), MACD bullish (+1), uptrend (+1) = STRONG BUY"
- Be conservative - when in doubt, HOLD
- Use specific numbers from the data

Respond ONLY in this exact JSON format (no extra text):
{{"action": "STRONG BUY", "confidence": 87, "reason": "Score +3: RSI 30 (+2), MACD bullish (+1), uptrend (+1)"}}
"""
    
    try:
        # Initialize client and send request to LLaMA 70B
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
        
        # Extract JSON response from LLaMA output
        raw_response = response.choices[0].message.content
        
        # Find JSON boundaries (LLaMA may wrap in markdown or add text)
        start_idx = raw_response.find("{")
        end_idx = raw_response.rfind("}") + 1
        
        # Validate we found both braces
        if start_idx == -1 or end_idx == 0:
            return {"action": "HOLD", "confidence": 0, "reason": "Failed to parse AI response"}
        
        # Extract and parse the JSON
        json_str = raw_response[start_idx:end_idx]
        decision = json.loads(json_str)
        
        # Validate and enforce confidence rules based on action
        action = decision.get("action", "HOLD")
        reason = decision.get("reason", "")
        
        # Extract score from reason if present
        score = 0
        import re
        score_match = re.search(r'[Ss]core\s*([+-]?\d+)', reason)
        if score_match:
            score = int(score_match.group(1))
        
        # Enforce confidence based on score/action
        if "BUY" in action.upper() and "STRONG" not in action.upper():
            if score == 1:
                decision["confidence"] = 60
            elif score == 2:
                decision["confidence"] = 75
        elif "STRONG BUY" in action.upper():
            decision["confidence"] = 88
        elif "SELL" in action.upper() and "STRONG" not in action.upper():
            if score == -1:
                decision["confidence"] = 60
            elif score == -2:
                decision["confidence"] = 75
        elif "STRONG SELL" in action.upper():
            decision["confidence"] = 88
        else:
            decision["confidence"] = 50
        
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
                        return json.loads(json_str)
                except:
                    print("  [RATE LIMIT] All keys exhausted - waiting 30 seconds...")
                    time.sleep(30)
                    return {"action": "HOLD", "confidence": 0, "reason": "Rate limit - all keys exhausted"}
            else:
                print("  [RATE LIMIT] No backup key - waiting 30 seconds...")
                time.sleep(30)
                return {"action": "HOLD", "confidence": 0, "reason": "Rate limit - no backup key"}
        
        print(f"  AI analysis error: {e}")
        return {"action": "HOLD", "confidence": 0, "reason": "AI error"}


if __name__ == "__main__":
    # Test with fake data when run directly
    fake_data = {"symbol": "BTC", "price": {"price": 65000}, "signals": {"signal": "bullish"}}
    result = analyze_market(fake_data)
    print(result)
