import groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = groq.Groq(api_key=GROQ_API_KEY)


def analyze_market(market_data):
    prompt = f"""You are an expert cryptocurrency trader. Analyze the following market data and make a trading decision.

Market Data:
{json.dumps(market_data, indent=2)}

Rules:
- Only BUY if signals are clearly positive and confident
- SELL if signals are negative or risky
- HOLD if market conditions are unclear or neutral
- Be conservative and prioritize protecting capital

Respond ONLY in this exact JSON format:
{{"action": "BUY", "confidence": 75, "reason": "explanation here"}}
"""
    
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
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
            return {"action": "HOLD", "confidence": 0, "reason": "Failed to parse AI response"}
        
        json_str = raw_response[start_idx:end_idx]
        return json.loads(json_str)
    
    except Exception as e:
        print(f"AI analysis error: {e}")
        return {"action": "HOLD", "confidence": 0, "reason": "AI error"}


if __name__ == "__main__":
    fake_data = {"symbol": "BTC", "price": {"price": 65000}, "signals": {"signal": "bullish"}}
    result = analyze_market(fake_data)
    print(result)
