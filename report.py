import json
import os
import math
from datetime import datetime


def generate_daily_report():
    """Generate and display a daily trading report from trade_log.txt"""
    
    if not os.path.exists("trade_log.txt"):
        print("\n  No trade log found.")
        return None
    
    with open("trade_log.txt", "r") as f:
        lines = f.readlines()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    today_trades = []
    for line in lines:
        try:
            entry = json.loads(line.strip())
            if entry.get("timestamp", "").startswith(today):
                today_trades.append(entry)
        except:
            pass
    
    if not today_trades:
        print("\n  No trades recorded today.")
        return None
    
    total_trades = len(today_trades)
    buys = sum(1 for t in today_trades if t.get("action") == "BUY")
    sells = sum(1 for t in today_trades if t.get("action") == "SELL")
    holds = sum(1 for t in today_trades if t.get("action") == "HOLD")
    
    win_count = 0
    total_completed_pairs = 0
    best_trade = None
    worst_trade = None
    best_pnl = float('-inf')
    worst_pnl = float('inf')
    total_pnl = 0.0
    
    coin_stats = {}
    pending_buys = {}
    
    for trade in today_trades:
        symbol = trade.get("symbol", "UNKNOWN")
        action = trade.get("action")
        price = trade.get("price", 0)
        
        if action == "BUY":
            pending_buys[symbol] = price
            coin_stats[symbol] = {"count": coin_stats.get(symbol, {}).get("count", 0) + 1}
        elif action == "SELL":
            if symbol in pending_buys:
                buy_price = pending_buys[symbol]
                del pending_buys[symbol]
                total_completed_pairs += 1
                
                pnl = ((price - buy_price) / buy_price) * 100
                total_pnl += pnl
                
                if price > buy_price:
                    win_count += 1
                
                if pnl > best_pnl:
                    best_pnl = pnl
                    best_trade = symbol
                if pnl < worst_pnl:
                    worst_pnl = pnl
                    worst_trade = symbol
    
    most_traded = max(coin_stats.items(), key=lambda x: x[1]["count"])[0] if coin_stats else "N/A"
    win_rate = (win_count / total_completed_pairs * 100) if total_completed_pairs > 0 else 0
    
    report_lines = [
        "+--------------------------------------------+",
        "|         DAILY TRADING REPORT               |",
        f"|         Date: {today}                |",
        "+--------------------------------------------+",
        f"|  Total Trades    : {str(total_trades):<17} |",
        f"|  BUY Orders      : {str(buys):<17} |",
        f"|  SELL Orders     : {str(sells):<17} |",
        f"|  HOLD Decisions  : {str(holds):<17} |",
        f"|  Completed Pairs : {str(total_completed_pairs):<17} |",
        f"|  Win Rate        : {f'{win_rate:.1f}%':<17} |",
        f"|  Daily PnL       : {f'{total_pnl:+.2f}%':<17} |",
    ]
    
    if best_trade:
        report_lines.append(f"|  Best Trade      : {f'{best_trade} {best_pnl:+.2f}%':<21} |")
    if worst_trade and worst_pnl < 0:
        report_lines.append(f"|  Worst Trade     : {f'{worst_trade} {worst_pnl:.2f}%':<21} |")
    
    report_lines.append(f"|  Most Traded     : {most_traded:<17} |")
    report_lines.append("+--------------------------------------------+")
    
    report_text = "\n".join(report_lines)
    print(f"\n{report_text}\n")
    
    with open("daily_report.txt", "w") as f:
        f.write(f"Daily Trading Report - {today}\n")
        f.write("=" * 40 + "\n")
        f.write(f"Total Trades: {total_trades}\n")
        f.write(f"BUY Orders: {buys}\n")
        f.write(f"SELL Orders: {sells}\n")
        f.write(f"HOLD Decisions: {holds}\n")
        f.write(f"Completed Pairs: {total_completed_pairs}\n")
        f.write(f"Win Rate: {win_rate:.1f}%\n")
        f.write(f"Daily PnL: {total_pnl:+.2f}%\n")
        f.write(f"Most Traded: {most_traded}\n")
        if best_trade:
            f.write(f"Best Trade: {best_trade} {best_pnl:+.2f}%\n")
        if worst_trade and worst_pnl < 0:
            f.write(f"Worst Trade: {worst_trade} {worst_pnl:.2f}%\n")
    
    return {
        "total_trades": total_trades,
        "buys": buys,
        "sells": sells,
        "holds": holds,
        "total_completed_pairs": total_completed_pairs,
        "win_count": win_count,
        "win_rate": win_rate,
        "total_pnl": total_pnl,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "most_traded": most_traded
    }


def calculate_sharpe_ratio():
    """Calculate Sharpe ratio from completed trades in trade_log.txt"""
    
    if not os.path.exists("trade_log.txt"):
        print("  Sharpe Ratio: N/A (no trade log)")
        return None
    
    with open("trade_log.txt", "r") as f:
        lines = f.readlines()
    
    trades = []
    for line in lines:
        try:
            trades.append(json.loads(line.strip()))
        except:
            pass
    
    if len(trades) < 2:
        print("  Sharpe Ratio: N/A (need more trades)")
        return None
    
    positions = {}
    completed_trades = []
    
    for trade in trades:
        symbol = trade.get("symbol")
        action = trade.get("action")
        price = trade.get("price", 0)
        
        if action == "BUY":
            positions[symbol] = price
        elif action == "SELL" and symbol in positions:
            buy_price = positions[symbol]
            pnl_percent = ((price - buy_price) / buy_price) * 100
            completed_trades.append(pnl_percent / 100)
            del positions[symbol]
    
    if len(completed_trades) < 2:
        print("  Sharpe Ratio: N/A (need more completed trades)")
        return None
    
    avg_return = sum(completed_trades) / len(completed_trades)
    
    variance = sum((r - avg_return) ** 2 for r in completed_trades) / len(completed_trades)
    std_dev = math.sqrt(variance)
    
    if std_dev == 0:
        print("  Sharpe Ratio: N/A (no variance in returns)")
        return None
    
    risk_free_rate = 0.02
    sharpe = (avg_return - risk_free_rate) / std_dev
    
    if sharpe >= 2.0:
        rating = "excellent"
    elif sharpe >= 1.0:
        rating = "good"
    else:
        rating = "below average"
    
    print(f"\n  Sharpe Ratio: {sharpe:.2f} ({rating})")
    print(f"  (above 1.0 = good, above 2.0 = excellent)")
    print(f"  Avg Return: {avg_return*100:+.2f}% | Std Dev: {std_dev*100:.2f}% | Trades: {len(completed_trades)}")
    
    return sharpe


if __name__ == "__main__":
    generate_daily_report()
    calculate_sharpe_ratio()
