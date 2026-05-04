"""
terminal_ui.py  —  InsiderEdge v1.0
Kali Linux Cyberpunk Aesthetic - Advanced Terminal UI
Inspired by: Kali Linux, Metasploit, Nmap, John the Ripper
"""

import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich import box
from rich.align import Align

# ── FIX 1: Remove stderr=True — was sending ALL output to stderr instead of
#           stdout, meaning nothing appeared in normal terminal / log files.
# ── FIX 2: Remove hardcoded width=120 — use None so Rich auto-detects the
#           real terminal width. 120 overflows 80-col CMD and Kali terminals.
console = Console(force_terminal=True)

# ── Advanced Cyberpunk Color Palette ──────────────────────────────────────────
# ── FIX 3 & 5: Added missing "neon_yellow" and "neon_blue" that were used in
#               print_risk_summary and print_alert but absent from C dict,
#               causing KeyError crashes at runtime.
C = {
    "neon_green":  "#39ff14",   # Matrix green
    "neon_cyan":   "#00ffff",   # Bright cyan
    "neon_pink":   "#ff10f0",   # Cyberpunk pink
    "neon_purple": "#b026ff",   # Electric purple
    "neon_red":    "#ff0000",   # Alert red
    "neon_yellow": "#f1fa8c",   # FIX 3: was missing, used in risk_summary
    "neon_blue":   "#8be9fd",   # FIX 5: was missing, used in print_alert
    "dark_bg":     "#0d0221",
    "green":       "#50fa7b",
    "red":         "#ff5555",
    "yellow":      "#f1fa8c",
    "blue":        "#8be9fd",
    "purple":      "#bd93f9",
    "cyan":        "#00ffff",
    "white":       "#f8f8f2",
    "gray":        "#6272a4",
    "gold":        "#ffd700",
    "orange":      "#ff8c00",
}


def style(text: str, color: str = "white") -> str:
    return f"[{C.get(color, color)}]{text}[/]"


def glow(text: str, color: str = "neon_green") -> str:
    col = C.get(color, color)
    return f"[bold {col}]{text}[/bold {col}]"


# ══════════════════════════════════════════════════════════════════════════════
#  BANNER
# ══════════════════════════════════════════════════════════════════════════════

LOGO_LINES = [
    "  ██╗███╗  ██╗███████╗██╗██████╗ ███████╗██████╗ ",
    "  ██║████╗ ██║██╔════╝██║██╔══██╗██╔════╝██╔══██╗",
    "  ██║██╔██╗██║███████╗██║██║  ██║█████╗  ██████╔╝",
    "  ██║██║╚███║╚════██║██║██║  ██║██╔══╝  ██╔══██╗",
    "  ██║██║ ╚██║███████║██║██████╔╝███████╗██║  ██║",
    "  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝",
    "",
    "   ███████╗██████╗  ██████╗ ███████╗",
    "   ██╔════╝██╔══██╗██╔════╝ ██╔════╝",
    "   █████╗  ██║  ██║██║  ███╗█████╗  ",
    "   ██╔══╝  ██║  ██║██║   ██║██╔══╝  ",
    "   ███████╗██████╔╝╚██████╔╝███████╗",
    "   ╚══════╝╚═════╝  ╚═════╝ ╚══════╝",
]

LOGO_COLORS = [
    "neon_cyan", "neon_cyan", "neon_blue", "neon_purple",
    "neon_cyan", "gray", "gray",
    "neon_pink", "neon_pink", "neon_purple", "neon_pink", "neon_pink", "gray",
]


def print_banner(eth_balance: float, agent_id: int, block_number: int):
    """Kali-style boot banner with system info."""
    console.print()

    logo = Text()
    for line, col in zip(LOGO_LINES, LOGO_COLORS):
        logo.append(line + "\n", style=f"bold {C[col]}")

    console.print(Panel(
        Align.center(logo),
        border_style=C["neon_cyan"],
        box=box.DOUBLE_EDGE,
        padding=(0, 2),
    ))
    console.print()

    bal_col  = "neon_green" if eth_balance > 0.01 else "neon_red"
    bal_icon = "🟢" if eth_balance > 0.01 else "🔴"

    status = Table(box=box.ROUNDED, show_header=False, padding=(0, 3),
                   border_style=C["gray"])
    status.add_column(style=C["neon_purple"], no_wrap=True)
    status.add_column(style=C["white"])

    status.add_row("[BLOCKCHAIN]",
        f"{bal_icon} {glow('ONLINE', bal_col)}  Balance: {glow(f'{eth_balance:.4f}', 'gold')} ETH")
    status.add_row("[NETWORK]",   f"Block #{glow(f'{block_number:,}', 'neon_cyan')}")
    status.add_row("[AGENT ID]",  glow(f"#{agent_id}", "neon_pink"))
    status.add_row("[TIMESTAMP]", glow(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "neon_green"))

    console.print(Align.center(status))
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

def print_config(cfg: dict):
    console.print(glow("▶ SYSTEM CONFIGURATION", "neon_green"))
    console.print()

    t = Table(box=box.HEAVY, show_header=False, padding=(0, 2),
              border_style=C["neon_purple"])
    t.add_column(style=C["neon_purple"], no_wrap=True, width=20)
    t.add_column(width=50)

    coins = cfg.get("coins", [])
    if isinstance(coins, str):
        coins = [c.strip() for c in coins.split(",")]
    coin_str = " + ".join(glow(c, "neon_green") for c in coins)

    mode     = cfg.get("mode", "PAPER")
    mode_col = "neon_red" if str(mode).upper() == "LIVE" else "neon_yellow"

    rows = [
        ("MODE",           glow(str(mode), mode_col)),
        ("WATCHLIST",      coin_str),
        ("SCAN INTERVAL",  glow(f"{cfg.get('scan_interval', 5)}m", "neon_cyan")),
        ("MAX TRADES/DAY", glow(str(cfg.get("max_trades", 50)), "neon_green")),
        ("MIN CONFIDENCE", glow(f"{cfg.get('min_confidence', 55)}%", "neon_green")),
        ("MAX DAILY LOSS", glow(f"{cfg.get('max_loss', 5)}%", "neon_red")),
        ("TAKE PROFIT",    glow(f"+{cfg.get('take_profit', 1.2)}%", "neon_green")),
        ("STOP LOSS",      glow(f"-{cfg.get('stop_loss', 0.8)}%", "neon_red")),
    ]
    for k, v in rows:
        t.add_row(style(k, "neon_purple"), v)

    console.print(t)
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  SCAN HEADER
# ══════════════════════════════════════════════════════════════════════════════

def print_scan_header(cycle: int, coins: list[str]):
    """
    FIX 4: Was using  string + Align.center() + string  which throws TypeError
    because Align.center() returns a Rich Renderable, not a plain string.
    Now uses Rule which renders cleanly at any terminal width.
    """
    ts       = datetime.now().strftime("%H:%M:%S")
    coin_str = "  •  ".join(glow(c, "neon_cyan") for c in coins)

    console.print()
    console.print(Rule(
        title=f"{glow(f'SCAN #{cycle}', 'neon_pink')}  {style(ts, 'gray')}  {coin_str}",
        style=C["neon_purple"],
        characters="═",
    ))
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  TRADING DECISION
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

    sym_map = {"BUY": "▲▲▲", "SELL": "▼▼▼", "HOLD": "◆◆◆"}
    col_map = {"BUY": "neon_green", "SELL": "neon_red", "HOLD": "neon_purple"}
    sym = sym_map.get(action, action)
    col = col_map.get(action, "neon_cyan")

    filled  = round(confidence / 5)
    meter   = "█" * filled + "░" * (20 - filled)
    chg_str = f"{'+' if change_24h >= 0 else ''}{change_24h:.2f}%"
    chg_col = "neon_green" if change_24h >= 0 else "neon_red"

    if checkpoint_tx:
        ckpt = (glow("✓ ON-CHAIN", "neon_green") if checkpoint_ok
                else glow("✗ FAILED", "neon_red"))
    else:
        ckpt = style("(no tx)", "gray")

    # Build as Text — avoids FIX 4 Renderable concat issue
    line = Text()
    line.append(f"  {sym}  ", style=f"bold {C[col]}")
    line.append(f"{symbol:<4}", style=f"bold {C['white']}")
    line.append(f"  ${price:>12,.2f}  ", style=C["gray"])
    line.append(f"{chg_str:>8}  ", style=f"bold {C[chg_col]}")
    line.append("[", style=C["gray"])
    line.append(meter, style=f"bold {C[col]}")
    line.append("]  ", style=C["gray"])
    line.append(f"conf: {confidence}%  ", style=f"bold {C[col]}")

    console.print(line, end="")
    console.print(ckpt)

    if reason:
        console.print(f"     ├─ [{C['gray']}]{reason[:100]}[/]")


# ══════════════════════════════════════════════════════════════════════════════
#  POSITIONS TABLE
# ══════════════════════════════════════════════════════════════════════════════

def print_positions(positions: list[dict]):
    if not positions:
        console.print(f"  {glow('[POSITIONS]', 'neon_cyan')} {style('None open', 'gray')}")
        return

    console.print(glow("▶ ACTIVE POSITIONS", "neon_cyan"))
    console.print()

    t = Table(box=box.HEAVY, padding=(0, 2), border_style=C["neon_cyan"])
    t.add_column(glow("SYMBOL",  "neon_purple"), style=C["neon_green"], width=10)
    t.add_column(glow("ENTRY",   "neon_purple"), style=C["white"],      width=14, justify="right")
    t.add_column(glow("CURRENT", "neon_purple"), style=C["white"],      width=14, justify="right")
    t.add_column(glow("P&L $",   "neon_purple"),                        width=12, justify="right")
    t.add_column(glow("P&L %",   "neon_purple"),                        width=10, justify="right")

    for p in positions:
        pnl_pct = p.get("pnl_pct", 0.0)
        pnl_amt = p.get("pnl_amount", p.get("pnl_usd", 0.0))
        col     = "neon_green" if pnl_pct >= 0 else "neon_red"
        arrow   = "↑" if pnl_pct >= 0 else "↓"

        t.add_row(
            glow(p["symbol"], "neon_cyan"),
            f"${p['entry_price']:,.2f}",
            f"${p['current_price']:,.2f}",
            f"[{C[col]}]{arrow} ${pnl_amt:+.2f}[/]",
            glow(f"{pnl_pct:+.2f}%", col),
        )

    console.print(t)
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  RISK SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def print_risk_summary(
    trades_today: int,
    max_trades: int,
    daily_pnl_pct: float,
    open_positions: int,
    total_trades: int,
    portfolio_value: float = 0,
    portfolio_pnl: float = 0,
):
    console.print(glow("▶ RISK ASSESSMENT", "neon_purple"))
    console.print()

    t = Table(box=box.HEAVY, show_header=False, padding=(0, 2),
              border_style=C["neon_purple"])
    t.add_column(style=C["neon_purple"], width=20)
    t.add_column()

    pct     = (trades_today / max(max_trades, 1)) * 100
    t_col   = "neon_green" if pct < 50 else "neon_yellow" if pct < 80 else "neon_red"
    t_bar   = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    pnl_col = "neon_green" if daily_pnl_pct >= 0 else "neon_red"
    pnl_str = f"{'+' if daily_pnl_pct >= 0 else ''}{daily_pnl_pct:.2f}%"

    t.add_row("TRADES TODAY",   f"{glow(f'{trades_today}/{max_trades}', t_col)}  [{glow(t_bar, t_col)}]")
    t.add_row("DAILY P&L",      glow(pnl_str, pnl_col))
    t.add_row("OPEN POSITIONS", glow(str(open_positions), "neon_cyan"))
    t.add_row("TOTAL TRADES",   glow(str(total_trades), "neon_green"))

    if portfolio_value > 0:
        pv_col = "neon_green" if portfolio_pnl >= 0 else "neon_red"
        pv_str = f"${portfolio_value:,.2f} ({'+' if portfolio_pnl >= 0 else ''}{portfolio_pnl:.2f}%)"
        t.add_row("PORTFOLIO",      glow(pv_str, pv_col))

    console.print(t)
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  NEXT SCAN
# ══════════════════════════════════════════════════════════════════════════════

def print_next_scan(minutes: int, seconds: int = 0):
    """FIX 4 applied: Rule instead of string + Align.center() concatenation."""
    time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
    console.print()
    console.print(Rule(
        title=f"{glow(f'⏱  NEXT SCAN IN {time_str}', 'neon_cyan')}  {style('[Ctrl+C to exit]', 'gray')}",
        style=C["neon_cyan"],
        characters="─",
    ))
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  ALERTS & STATUS
# ══════════════════════════════════════════════════════════════════════════════

def print_alert(message: str, level: str = "warn"):
    icons  = {"warn": "⚠", "error": "✗", "info": "ℹ", "success": "✓", "critical": "!!!"}
    colors = {"warn": "neon_yellow", "error": "neon_red", "info": "neon_blue",
              "success": "neon_green", "critical": "neon_red"}
    icon = icons.get(level, "•")
    col  = colors.get(level, "neon_cyan")
    console.print(f"  {glow(icon, col)} {style(message, col)}")


def print_blockchain_status(ok: bool, tx_hash: str | None = None, label: str = ""):
    if ok and tx_hash:
        console.print(f"  {glow('✓', 'neon_green')}  {style(label, 'gray')} → {glow(tx_hash[:16] + '…', 'neon_cyan')}")
    elif tx_hash:
        console.print(f"  {glow('✗', 'neon_red')}  {style(label, 'gray')} reverted")
    else:
        console.print(f"  {glow('✗', 'neon_red')}  {style(label, 'gray')} failed (no TX)")


def print_reputation_ok():
    console.print(f"  {glow('★', 'neon_pink')}  {style('Reputation confirmed', 'gray')}")


# ══════════════════════════════════════════════════════════════════════════════
#  DEMO
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print_banner(eth_balance=0.1484, agent_id=33, block_number=10_738_695)

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

    print_decision("BTC", "BUY",  85, 78_696.00, +1.51,
                   "Score +3: Trend +1, MACD +1, RSI oversold",
                   checkpoint_tx="0x48298fad516acd70", checkpoint_ok=True)
    print_decision("ETH", "HOLD", 50,  2_374.72, -0.87,
                   "Mixed signals — consolidation phase")
    print_decision("SOL", "BUY",  75,     86.67, +3.21,
                   "Score +2: bullish momentum",
                   checkpoint_tx="0x2928bb91856fc555", checkpoint_ok=False)

    print_positions([
        {"symbol": "BTC", "entry_price": 78_400, "current_price": 78_696,
         "pnl_pct": 0.38, "pnl_amount": 296},
        {"symbol": "SOL", "entry_price": 85.00,  "current_price": 86.67,
         "pnl_pct": 1.96, "pnl_amount": 1.67},
    ])

    print_risk_summary(trades_today=2, max_trades=50, daily_pnl_pct=2.34,
                       open_positions=2, total_trades=15)

    print_reputation_ok()
    print_next_scan(minutes=5, seconds=0)
    print_alert("Circuit breaker threshold approaching!", "critical")
    print_blockchain_status(ok=True, tx_hash="0x1234567890abcdef", label="Checkpoint")