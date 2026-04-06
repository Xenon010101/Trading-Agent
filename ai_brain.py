import groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def get_groq_client():
    """Lazy initialization of Groq client to avoid import-time errors"""
    return groq.Groq(api_key=GROQ_API_KEY)


def analyze_market(market_data):
    """
    Analyze market data using Groq LLaMA 70B and return trading decision.
    
    Args:
        market_data: Dict containing symbol, price, and signals from PRISM API
    
    Returns:
        Dict with action (BUY/SELL/HOLD), confidence (0-100), and reason
    """
    # Build comprehensive prompt with market data and trading rules
    prompt = f"""You are an expert cryptocurrency trader. Analyze the following market data and make a trading decision.

Market Data:
{json.dumps(market_data, indent=2)}

Analyze these factors in order:
1. Trend direction (uptrend/downtrend/consolidation)
2. MACD signal (bullish/bearish crossover)
3. RSI level (below 30 = oversold = buy opportunity, above 70 = overbought = sell signal)
4. Overall signal strength

Strict Trading Rules:
- STRONG BUY: RSI below 40 + MACD bullish + uptrend → confidence 80-90%
- BUY: MACD bullish + uptrend → confidence 65-75%
- STRONG SELL: RSI above 70 + MACD bearish → confidence 80-90%
- SELL: MACD bearish + downtrend → confidence 65-75%
- HOLD: mixed or unclear signals → confidence 50-60%

Requirements:
- Always mention specific numbers from the data in your reason
- Be consistent - same data should give same decision
- Be decisive - avoid sitting on the fence
- Only use HOLD when signals are truly unclear or contradictory
- Confidence scores should reflect actual signal strength

Respond ONLY in this exact JSON format:
{{"action": "BUY", "confidence": 75, "reason": "explanation here"}}
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
        return json.loads(json_str)
    
    except Exception as e:
        # On any error (API, network, parsing), default to HOLD
        print(f"AI analysis error: {e}")
        return {"action": "HOLD", "confidence": 0, "reason": "AI error"}


if __name__ == "__main__":
    # Test with fake data when run directly
    fake_data = {"symbol": "BTC", "price": {"price": 65000}, "signals": {"signal": "bullish"}}
    result = analyze_market(fake_data)
    print(result)
