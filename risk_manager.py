import json
import time
from config import MAX_TRADES_PER_DAY, MIN_CONFIDENCE, MAX_LOSS_PERCENT


class RiskManager:
    def __init__(self):
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.trade_history = []
        self.start_time = time.time()
    
    def can_trade(self, decision):
        if self.trades_today >= MAX_TRADES_PER_DAY:
            print(f"Cannot trade: Daily trade limit reached ({MAX_TRADES_PER_DAY})")
            return False
        
        confidence = decision.get("confidence", 0)
        if confidence < MIN_CONFIDENCE:
            print(f"Cannot trade: Confidence {confidence} below minimum {MIN_CONFIDENCE}")
            return False
        
        if self.daily_pnl < -MAX_LOSS_PERCENT:
            print(f"Cannot trade: Daily loss {self.daily_pnl}% exceeds max {MAX_LOSS_PERCENT}%")
            return False
        
        return True
    
    def record_trade(self, symbol, action, price, confidence):
        self.trades_today += 1
        trade = {
            "symbol": symbol,
            "action": action,
            "price": price,
            "confidence": confidence,
            "timestamp": time.time()
        }
        self.trade_history.append(trade)
        print(f"Trade recorded: {action} {symbol} at {price} (confidence: {confidence})")
    
    def get_summary(self):
        summary = {
            "trades_today": self.trades_today,
            "daily_pnl": self.daily_pnl,
            "total_trades": len(self.trade_history)
        }
        print("\n=== Risk Manager Summary ===")
        print(f"Trades today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        print(f"Daily P&L: {self.daily_pnl}%")
        print(f"Total trades: {len(self.trade_history)}")
        print("=============================\n")
        return summary
    
    def reset_daily_limits(self):
        self.trades_today = 0
        self.daily_pnl = 0
        print("Daily limits reset")


if __name__ == "__main__":
    rm = RiskManager()
    
    decision = {"action": "BUY", "confidence": 75, "reason": "Test"}
    print(f"Can trade: {rm.can_trade(decision)}")
    
    rm.record_trade("BTC", "BUY", 65000, 75)
    rm.record_trade("ETH", "SELL", 3500, 80)
    
    rm.get_summary()
    rm.reset_daily_limits()
    rm.get_summary()
