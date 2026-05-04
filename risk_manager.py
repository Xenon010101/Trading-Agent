import json
import time
from datetime import date as datetime
from config import MAX_TRADES_PER_DAY, MIN_CONFIDENCE, MAX_LOSS_PERCENT, CIRCUIT_BREAKER_THRESHOLD, PAPER_BALANCE, MAX_POSITION_PCT, RISK_PER_TRADE


class RiskManager:
    def __init__(self):
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.trade_history = []
        self.positions = {}
        self.start_time = time.time()
        self.last_reset_date = datetime.today()
        self.circuit_broken = False

        self.starting_balance = PAPER_BALANCE
        self.available_cash = PAPER_BALANCE
        self.total_portfolio_value = PAPER_BALANCE

    def check_circuit_breaker(self):
        if self.daily_pnl <= CIRCUIT_BREAKER_THRESHOLD:
            self.circuit_broken = True
            print("\n")
            print("[!!!] CIRCUIT BREAKER TRIGGERED [!!!]")
            print(f"Daily loss {self.daily_pnl:.2f}% exceeded threshold {CIRCUIT_BREAKER_THRESHOLD}%")
            print("All trading halted for today")
            print("Restart agent tomorrow to resume")
            print("\n")
            return True
        return False

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

    def calculate_position_size(self, symbol, price, confidence):
        risk_factor = RISK_PER_TRADE / 100.0
        confidence_factor = (confidence - 50) / 100.0
        risk_amount = self.available_cash * risk_factor * (1 + confidence_factor)
        max_allocation = self.total_portfolio_value * (MAX_POSITION_PCT / 100.0)
        allocation = min(risk_amount, max_allocation)
        allocation = min(allocation, self.available_cash * 0.95)
        if price and price > 0:
            quantity = allocation / price
            return quantity, allocation
        return 0.0, 0.0

    def record_trade(self, symbol, action, price, confidence):
        self.trades_today += 1
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        if action == "BUY":
            quantity, allocation = self.calculate_position_size(symbol, price, confidence)
            if quantity <= 0 or allocation > self.available_cash:
                print(f"BUY rejected: insufficient cash or invalid position size for {symbol}")
                return
            self.positions[symbol] = {
                "buy_price": price,
                "quantity": quantity,
                "cost_basis": allocation,
                "timestamp": timestamp
            }
            self.available_cash -= allocation
            print(f"BUY recorded: {symbol} {quantity:.6f} at ${price:,.2f} (${allocation:.2f})")

        elif action == "SELL":
            if symbol in self.positions:
                pos = self.positions[symbol]
                buy_price = pos["buy_price"]
                quantity = pos["quantity"]
                cost_basis = pos["cost_basis"]
                sell_value = price * quantity
                pnl_amount = sell_value - cost_basis
                pnl_percent = ((price - buy_price) / buy_price) * 100
                self.daily_pnl += pnl_percent
                self.available_cash += sell_value
                print(f"SELL recorded: {symbol}")
                print(f"  Bought: ${buy_price:,.2f} x {quantity:.6f} (cost: ${cost_basis:.2f})")
                print(f"  Sold:   ${price:,.2f} x {quantity:.6f} (value: ${sell_value:.2f})")
                print(f"  Profit/Loss: ${pnl_amount:+.2f} ({pnl_percent:+.2f}%)")
                print(f"  Daily P&L: {self.daily_pnl:+.2f}%")
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

    def update_portfolio_value(self, current_prices=None):
        if current_prices is None:
            current_prices = {}
        positions_value = 0.0
        for symbol, pos in self.positions.items():
            current_price = current_prices.get(symbol, pos["buy_price"])
            positions_value += current_price * pos["quantity"]
        self.total_portfolio_value = self.available_cash + positions_value
        return self.total_portfolio_value

    def get_open_positions(self, current_prices=None):
        print("\n  Open Positions:")

        if not self.positions:
            print("  None")
            return

        if current_prices is None:
            current_prices = {}

        for symbol, pos in self.positions.items():
            buy_price = pos["buy_price"]
            quantity = pos.get("quantity", 0.001)
            current_price = current_prices.get(symbol, buy_price)
            pnl = ((current_price - buy_price) / buy_price) * 100
            pnl_str = f"+{pnl:.2f}%" if pnl >= 0 else f"{pnl:.2f}%"
            pos_value = current_price * quantity
            print(f"  {symbol}: {quantity:.6f} at ${buy_price:,.2f} | current ${current_price:,.2f} | PnL: {pnl_str} | Value: ${pos_value:.2f}")

    def get_summary(self):
        summary = {
            "trades_today": self.trades_today,
            "daily_pnl": self.daily_pnl,
            "total_trades": len(self.trade_history),
            "open_positions": len(self.positions),
            "available_cash": self.available_cash,
            "portfolio_value": self.total_portfolio_value,
        }
        portfolio_pnl = ((self.total_portfolio_value - self.starting_balance) / self.starting_balance) * 100
        print("\n=== Risk Manager Summary ===")
        print(f"Trades today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        print(f"Daily P&L: {self.daily_pnl:+.2f}%")
        print(f"Available cash: ${self.available_cash:,.2f}")
        print(f"Portfolio value: ${self.total_portfolio_value:,.2f} ({portfolio_pnl:+.2f}%)")
        print(f"Open positions: {len(self.positions)}")
        print(f"Total trades: {len(self.trade_history)}")
        print("=============================\n")
        return summary

    def reset_daily_limits(self):
        self.trades_today = 0
        self.daily_pnl = 0
        print("Daily limits reset")

    def reset_for_new_day(self):
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.circuit_broken = False
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
