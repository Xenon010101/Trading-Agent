import json
import time
from datetime import date as datetime
from config import MAX_TRADES_PER_DAY, MIN_CONFIDENCE, MAX_LOSS_PERCENT


class RiskManager:
    def __init__(self):
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.trade_history = []
        self.positions = {}
        self.start_time = time.time()
        self.last_reset_date = datetime.today()
    
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
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        if action == "BUY":
            self.positions[symbol] = {
                "buy_price": price,
                "amount": 0.001,
                "timestamp": timestamp
            }
            print(f"BUY recorded: {symbol} at ${price}")
        
        elif action == "SELL":
            if symbol in self.positions:
                buy_price = self.positions[symbol]["buy_price"]
                pnl_percent = ((price - buy_price) / buy_price) * 100
                self.daily_pnl += pnl_percent
                print(f"SELL recorded: {symbol} at ${price} | PnL: {pnl_percent:+.2f}%")
                del self.positions[symbol]
            else:
                print(f"SELL recorded: {symbol} at ${price} (no open position)")
        
        trade = {
            "symbol": symbol,
            "action": action,
            "price": price,
            "confidence": confidence,
            "timestamp": timestamp
        }
        self.trade_history.append(trade)
        print(f"Trade recorded: {action} {symbol} at ${price} (confidence: {confidence}%)")
    
    def get_open_positions(self, current_prices=None):
        print("\n  Open Positions:")
        
        if not self.positions:
            print("  None")
            return
        
        if current_prices is None:
            current_prices = {}
        
        for symbol, pos in self.positions.items():
            buy_price = pos["buy_price"]
            current_price = current_prices.get(symbol, buy_price)
            pnl = ((current_price - buy_price) / buy_price) * 100
            pnl_str = f"+{pnl:.2f}%" if pnl >= 0 else f"{pnl:.2f}%"
            print(f"  {symbol}: bought at ${buy_price:,.2f} | current ${current_price:,.2f} | PnL: {pnl_str}")
    
    def get_summary(self):
        summary = {
            "trades_today": self.trades_today,
            "daily_pnl": self.daily_pnl,
            "total_trades": len(self.trade_history),
            "open_positions": len(self.positions)
        }
        print("\n=== Risk Manager Summary ===")
        print(f"Trades today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        print(f"Daily P&L: {self.daily_pnl:+.2f}%")
        print(f"Open positions: {len(self.positions)}")
        print(f"Total trades: {len(self.trade_history)}")
        print("=============================\n")
        return summary
    
    def reset_daily_limits(self):
        self.trades_today = 0
        self.daily_pnl = 0
        print("Daily limits reset")
    
    def reset_for_new_day(self):
        """Reset daily counters for a new trading day"""
        self.trades_today = 0
        self.daily_pnl = 0.0
        print("\n  [NEW DAY] Daily counters reset")


if __name__ == "__main__":
    rm = RiskManager()
    
    decision = {"action": "BUY", "confidence": 75, "reason": "Test"}
    print(f"Can trade: {rm.can_trade(decision)}")
    
    rm.record_trade("BTC", "BUY", 65000, 75)
    rm.record_trade("ETH", "BUY", 3500, 80)
    
    rm.get_open_positions({"BTC": 65500, "ETH": 3400})
    rm.get_summary()
    
    rm.record_trade("BTC", "SELL", 66000, 85)
    rm.get_open_positions()
    rm.get_summary()
