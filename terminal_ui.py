"""
terminal_ui.py  —  InsiderEdge v1.0
Linux terminal aesthetic - clean, minimal, functional
"""

import sys
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich import box
from rich.align import Align

console = Console(stderr=True, force_terminal=True)

# ── Linux/Terminal color palette ───────────────────────────────────────────────
C = {
    "default":   "#cccccc",
    "green":     "#50fa7b",
    "red":       "#ff5555",
    "yellow":    "#f1fa8c",
    "blue":      "#8be9fd",
    "purple":    "#bd93f9",
    "cyan":      "#8be9fd",
    "white":     "#f8f8f2",
    "gray":      "#6272a4",
    "dark":      "#282a36",
    "gold":      "#f1fa8c",
}

# Style helpers
def style(text: str, color: str = "default") -> str:
    return f"[{C.get(color, color)}]{text}[/]"


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN HEADER
# ══════════════════════════════════════════════════════════════════════════════

def print_banner(eth_balance: float, agent_id: int, block_number: int):
    """Clean terminal-style banner."""
    console.print()
    
    # Simple text logo (terminal style)
    console.print(f"""
   ___ Ins1d3r3dg3 ___   
  |_ _| __| |/ _ \\ __/ __/ _ \\
   | | | _|   |  _| _| (   | |
  |___|___|_|_|\\_|___\\___|_|  {C['gray']}v1.0{C['default']}
""")
    console.print()
    
    # Status bar - minimal
    console.print(f"  {style('●', 'green' if eth_balance > 0.01 else 'red')} balance: {eth_balance:.4f} ETH  {style('│', 'gray')}  block: #{block_number:,}  {style('│', 'gray')}  agent: #{agent_id}  {style('│', 'gray')}  sep0l1a")
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

def print_config(cfg: dict):
    """Minimal two-column config display."""
    table = Table(box=None, show_header=False, padding=(0, 2))
    table.add_column(style=C["gray"], no_wrap=True)
    table.add_column(style=C["default"])
    
    rows = [
        (style("mode", "gray"), style(cfg.get("mode", "PAPER"), "yellow")),
        (style("coins", "gray"), style(", ".join(cfg.get("coins", [])), "cyan")),
        (style("interval", "gray"), style(f"{cfg.get('scan_interval', 5)}m", "default")),
        (style("max_trades", "gray"), style(f"{cfg.get('max_trades', 50)}/day", "default")),
        (style("min_conf", "gray"), style(f"{cfg.get('min_confidence', 55)}%", "green")),
        (style("max_loss", "gray"), style(f"{cfg.get('max_loss', 5)}%", "red")),
        (style("take_profit", "gray"), style(f"{cfg.get('take_profit', 1.2)}%", "green")),
        (style("stop_loss", "gray"), style(f"{cfg.get('stop_loss', 0.8)}%", "red")),
    ]
    
    for k, v in rows:
        table.add_row(k, v)
    
    console.print(Align.left(table))
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  SCAN HEADER  
# ══════════════════════════════════════════════════════════════════════════════

def print_scan_header(cycle: int, coins: list[str]):
    """Clean scan separator."""
    ts = datetime.now().strftime("%H:%M:%S")
    console.print(Rule(
        title=f" scan #{cycle}  [{ts}]  {' + '.join(coins)} ",
        style=C["gray"],
        characters="─",
    ))


# ══════════════════════════════════════════════════════════════════════════════
#  DECISION DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

def print_decision(
    symbol: str,
    action: str,
    confidence: int,
    price: float,
    change_24h: float,
    reason: str,
    checkpoint_tx: str | None = None,
    checkpoint_ok: bool = False,
):
    action = action.upper()
    
    # Action symbol
    action_symbols = {"BUY": "▲", "SELL": "▼", "HOLD": "○"}
    sym = action_symbols.get(action, action[0])
    
    # Colors
    action_colors = {"BUY": "green", "SELL": "red", "HOLD": "gray"}
    col = action_colors.get(action, "default")
    
    # Confidence bar
    filled = round(confidence / 10)
    bar = "▓" * filled + "░" * (10 - filled)
    
    # Change
    change_str = f"{'+' if change_24h >= 0 else ''}{change_24h:.2f}%"
    change_col = "green" if change_24h >= 0 else "red"
    
    # Checkpoint status
    if checkpoint_tx:
        if checkpoint_ok:
            ckpt = style("●", "green") + " on-chain"
        else:
            ckpt = style("○", "red") + " failed"
    else:
        ckpt = ""
    
    # Price and action on one line
    console.print(f"  {style(sym, col)} {style(symbol, 'white')}  ${price:>10,.2f}  {style(change_str, change_col)}  conf {confidence}% [{bar}]  {ckpt}")
    
    # Reason on next line (truncated)
    if reason:
        console.print(f"     {style(reason[:80], 'gray')}")


# ══════════════════════════════════════════════════════════════════════════════
#  POSITIONS
# ══════════════════════════════════════════════════════════════════════════════

def print_positions(positions: list[dict]):
    if not positions:
        console.print(f"  {style('○', 'gray')} no positions")
        return

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column(style=C["gray"], width=8)
    table.add_column(style=C["default"], justify="right")
    table.add_column(style=C["default"], justify="right")
    table.add_column(style=C["default"], justify="right")

    for p in positions:
        pnl_pct = p.get("pnl_pct", 0)
        pnl_col = "green" if pnl_pct >= 0 else "red"
        arrow = "+" if pnl_pct >= 0 else ""
        
        table.add_row(
            style(p["symbol"], "white"),
            f"${p['entry_price']:,.2f}",
            f"${p['current_price']:,.2f}",
            style(f"{arrow}{pnl_pct:.2f}%", pnl_col),
        )

    console.print(table)


# ══════════════════════════════════════════════════════════════════════════════
#  RISK SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def print_risk_summary(
    trades_today: int,
    max_trades: int,
    daily_pnl_pct: float,
    open_positions: int,
    total_trades: int,
):
    trade_col = "red" if trades_today >= max_trades * 0.8 else "default"
    pnl_col = "green" if daily_pnl_pct >= 0 else "red"
    pnl_str = f"{'+' if daily_pnl_pct >= 0 else ''}{daily_pnl_pct:.2f}%"
    
    console.print(f"  trades: {style(f'{trades_today}/{max_trades}', trade_col)}  {style('│', 'gray')}  pnl: {style(pnl_str, pnl_col)}  {style('│', 'gray')}  positions: {style(str(open_positions), 'cyan')}  {style('│', 'gray')}  total: {style(str(total_trades), 'default')}")


# ══════════════════════════════════════════════════════════════════════════════
#  NEXT SCAN
# ══════════════════════════════════════════════════════════════════════════════

def print_next_scan(minutes: int):
    console.print()
    console.print(Rule(style=C["dark"]))
    console.print(f"  next scan in {style(str(minutes), 'cyan')}m  {style('│', 'gray')}  ctrl+c to stop")


# ══════════════════════════════════════════════════════════════════════════════
#  ALERTS
# ══════════════════════════════════════════════════════════════════════════════

def print_alert(message: str, level: str = "warn"):
    icons = {"warn": "⚠", "error": "✕", "info": "ℹ", "success": "✓"}
    colors = {"warn": "yellow", "error": "red", "info": "blue", "success": "green"}
    icon = icons.get(level, "•")
    col = colors.get(level, "default")
    console.print(f"  {style(icon, col)}  {message}")


def print_blockchain_status(ok: bool, tx_hash: str | None = None, label: str = ""):
    if ok and tx_hash:
        console.print(f"  {style('✓', 'green')}  {label} tx: {tx_hash[:16]}...")
    elif tx_hash:
        console.print(f"  {style('✕', 'red')}  {label} reverted")
    else:
        console.print(f"  {style('✕', 'red')}  {label} failed")


def print_reputation_ok():
    console.print(f"  {style('★', 'purple')}  reputation confirmed")


# ══════════════════════════════════════════════════════════════════════
#  DEMO
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print_banner(eth_balance=0.1484, agent_id=33, block_number=10738695)
    
    print_config({
        "mode": "PAPER",
        "coins": ["BTC", "ETH", "SOL"],
        "scan_interval": 5,
        "max_trades": 50,
        "min_confidence": 55,
        "max_loss": 5,
        "take_profit": 1.2,
        "stop_loss": 0.8,
    })
    
    print_scan_header(cycle=1, coins=["BTC", "ETH", "SOL"])
    
    print_decision("BTC", "BUY", 75, 78696.00, 1.51, "momentum above threshold", checkpoint_ok=True)
    print_decision("ETH", "HOLD", 50, 2374.72, -0.87, "low confidence")
    print_decision("SOL", "BUY", 65, 86.67, 3.21, "bullish signal", checkpoint_ok=False)
    
    print_positions([
        {"symbol": "BTC", "entry_price": 78400, "current_price": 78696, "pnl_pct": 0.38},
        {"symbol": "SOL", "entry_price": 85.00, "current_price": 86.67, "pnl_pct": 1.96},
    ])
    
    print_risk_summary(trades_today=2, max_trades=50, daily_pnl_pct=2.34, open_positions=2, total_trades=15)
    print_next_scan(minutes=5)