"""
terminal_ui.py  —  InsiderEdge v1.0
Drop-in replacement for all print() calls in agent.py.
Requires: pip install rich
"""

import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.rule import Rule
from rich.live import Live
from rich.layout import Layout
from rich import box
from rich.style import Style
from rich.padding import Padding
from rich.align import Align

console = Console(stderr=True, no_color=False, force_terminal=True)

# ── Colour palette ─────────────────────────────────────────────────────────────
C = {
    "green":      "#00ff88",
    "red":        "#ff4466",
    "yellow":     "#ffd700",
    "blue":       "#00aaff",
    "purple":     "#bf5fff",
    "cyan":       "#00e5ff",
    "white":      "#e8e8e8",
    "dim":        "#555577",
    "bg_dark":    "grey7",
    "orange":     "#ff8c00",
    "pink":       "#ff69b4",
}


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════

def print_banner(eth_balance: float, agent_id: int, block_number: int):
    """Full-width banner printed once at startup."""
    console.print()

    # ASCII logo
    logo_lines = [
        "  ██╗███╗  ██╗███████╗██╗██████╗ ███████╗██████╗ ",
        "  ██║████╗ ██║██╔════╝██║██╔══██╗██╔════╝██╔══██╗",
        "  ██║██╔██╗██║███████╗██║██║  ██║█████╗  ██████╔╝",
        "  ██║██║╚████║╚════██║██║██║  ██║██╔══╝  ██╔══██╗",
        "  ██║██║ ╚███║███████║██║██████╔╝███████╗██║  ██║",
        "  ╚═╝╚═╝  ╚══╝╚══════╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝",
        "",
        "   ███████╗██████╗  ██████╗ ███████╗",
        "   ██╔════╝██╔══██╗██╔════╝ ██╔════╝",
        "   █████╗  ██║  ██║██║  ███╗█████╗  ",
        "   ██╔══╝  ██║  ██║██║   ██║██╔══╝  ",
        "   ███████╗██████╔╝╚██████╔╝███████╗",
        "   ╚══════╝╚═════╝  ╚═════╝ ╚══════╝",
    ]
    logo_text = Text()
    colors = [
        C["cyan"], C["blue"], C["purple"], C["blue"], C["cyan"], C["dim"], C["dim"],
        C["cyan"], C["blue"], C["purple"], C["blue"], C["cyan"], C["dim"],
    ]
    for line, col in zip(logo_lines, colors):
        logo_text.append(line + "\n", style=col)

    console.print(Panel(
        Align.center(logo_text),
        border_style=C["cyan"],
        box=box.DOUBLE_EDGE,
        padding=(0, 2),
    ))

    # Stats bar
    stats = Table.grid(expand=True, padding=(0, 4))
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")

    bal_color = C["green"] if eth_balance > 0.05 else C["red"]
    stats.add_row(
        Text("PAPER TRADING", style=f"bold {C['yellow']}"),
        Text(f"Block #{block_number:,}", style=C["blue"]),
        Text(f"Agent #{agent_id}", style=C["purple"]),
        Text(f"{eth_balance:.4f} ETH", style=f"bold {bal_color}"),
        Text(datetime.now().strftime("%H:%M:%S"), style=C["dim"]),
    )

    console.print(Panel(
        stats,
        border_style=C["dim"],
        box=box.SIMPLE_HEAVY,
        padding=(0, 1),
    ))
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION TABLE
# ══════════════════════════════════════════════════════════════════════════════

def print_config(cfg: dict):
    """
    cfg keys: mode, coins, scan_interval, max_trades, min_confidence,
              max_loss, take_profit, stop_loss
    """
    table = Table(
        title="[bold]Configuration[/bold]",
        box=box.ROUNDED,
        border_style=C["dim"],
        show_header=False,
        padding=(0, 2),
        title_style=f"bold {C['cyan']}",
        expand=False,
        min_width=52,
    )
    table.add_column("Key",   style=C["dim"],   no_wrap=True)
    table.add_column("Value", style=C["white"], no_wrap=True)

    rows = [
        ("Mode",           f"[bold {C['yellow']}]{cfg.get('mode', 'PAPER TRADING')}[/]"),
        ("Watchlist",      f"[{C['cyan']}]{cfg.get('coins', 'BTC, ETH, SOL')}[/]"),
        ("Scan Interval", f"[{C['white']}]{cfg.get('scan_interval', 5)} minutes[/]"),
        ("Max Trades",     f"[{C['white']}]{cfg.get('max_trades', 50)}/day[/]"),
        ("Min Confidence", f"[{C['green']}]{cfg.get('min_confidence', 55)}%[/]"),
        ("Max Loss",       f"[{C['red']}]{cfg.get('max_loss', 5)}%[/]"),
        ("Take Profit",    f"[{C['green']}]{cfg.get('take_profit', 1.2)}%[/]"),
        ("Stop Loss",      f"[{C['red']}]{cfg.get('stop_loss', 0.8)}%[/]"),
    ]
    for k, v in rows:
        table.add_row(k, v)

    console.print(Align.center(table))
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  SCAN CYCLE HEADER
# ══════════════════════════════════════════════════════════════════════════════

def print_scan_header(cycle: int, coins: list[str]):
    ts = datetime.now().strftime("%H:%M:%S")
    console.print(Rule(
        title=f"[bold {C['cyan']}] SCAN #{cycle}  [{ts}]  Analyzing: {', '.join(coins)} [/]",
        style=C["dim"],
        characters="─",
    ))
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  DECISION ROW
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
    action_styles = {
        "BUY":  (C["green"],  "▲ BUY "),
        "SELL": (C["red"],    "▼ SELL"),
        "HOLD": (C["yellow"], "◆ HOLD"),
    }
    col, label = action_styles.get(action, (C["white"], action))

    # confidence bar (20 chars wide)
    filled = round(confidence / 5)
    bar = "█" * filled + "░" * (20 - filled)
    bar_col = C["green"] if confidence >= 70 else C["yellow"] if confidence >= 55 else C["red"]

    change_col = C["green"] if change_24h >= 0 else C["red"]
    change_str = f"{'+' if change_24h >= 0 else ''}{change_24h:.2f}%"

    # Checkpoint badge
    if checkpoint_tx:
        ckpt_badge = (
            f"  [{C['green']}]TX {checkpoint_tx[:12]}…[/]"
            if checkpoint_ok
            else f"  [{C['red']}]checkpoint failed[/]"
        )
    else:
        ckpt_badge = ""

    content = (
        f"[bold {col}]{label}[/]  "
        f"[bold {C['white']}]{symbol:>3}[/]  "
        f"[{C['dim']}]${price:>10,.2f}[/]  "
        f"[{change_col}]{change_str:>7}[/]  "
        f"conf [bold {bar_col}]{confidence:>3}%[/] [{bar_col}]{bar}[/]"
        f"{ckpt_badge}\n"
        f"    [{C['dim']}]{reason[:120]}[/]"
    )

    border = col
    console.print(Panel(
        content,
        border_style=border,
        box=box.SIMPLE,
        padding=(0, 1),
    ))


# ══════════════════════════════════════════════════════════════════════════════
#  POSITIONS TABLE
# ══════════════════════════════════════════════════════════════════════════════

def print_positions(positions: list[dict]):
    """
    Each position dict: symbol, entry_price, current_price, pnl_pct, pnl_usd
    """
    if not positions:
        console.print(f"  [{C['dim']}]No open positions[/]")
        return

    table = Table(
        title=f"[bold {C['cyan']}]Open Positions[/]",
        box=box.SIMPLE_HEAVY,
        border_style=C["dim"],
        show_lines=False,
        padding=(0, 2),
        expand=False,
        min_width=70,
    )
    table.add_column("Symbol",  style=f"bold {C['white']}", justify="center", width=8)
    table.add_column("Entry",   style=C["dim"],             justify="right",  width=14)
    table.add_column("Current", style=C["white"],           justify="right",  width=14)
    table.add_column("PnL %",                               justify="right",  width=10)
    table.add_column("PnL $",                               justify="right",  width=12)
    table.add_column("Status",                              justify="center", width=10)

    for p in positions:
        pnl_pct = p.get("pnl_pct", 0.0)
        pnl_usd = p.get("pnl_usd", 0.0)
        col = C["green"] if pnl_pct >= 0 else C["red"]
        arrow = "▲" if pnl_pct >= 0 else "▼"
        status = f"[{col}]{arrow}[/]"

        table.add_row(
            p["symbol"],
            f"${p['entry_price']:,.2f}",
            f"${p['current_price']:,.2f}",
            f"[{col}]{'+' if pnl_pct >= 0 else ''}{pnl_pct:.2f}%[/]",
            f"[{col}]{'+' if pnl_usd >= 0 else ''}{pnl_usd:.2f}%[/]",
            status,
        )

    console.print(Align.center(table))


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
    grid = Table.grid(expand=False, padding=(0, 3))
    grid.add_column(justify="left")
    grid.add_column(justify="left")
    grid.add_column(justify="left")
    grid.add_column(justify="left")

    trade_col = C["red"] if trades_today >= max_trades * 0.8 else C["green"]
    pnl_col   = C["green"] if daily_pnl_pct >= 0 else C["red"]
    pnl_str   = f"{'+' if daily_pnl_pct >= 0 else ''}{daily_pnl_pct:.2f}%"

    grid.add_row(
        f"[{C['dim']}]Trades today[/] [{trade_col}]{trades_today}/{max_trades}[/]",
        f"[{C['dim']}]Daily PnL[/] [{pnl_col}]{pnl_str}[/]",
        f"[{C['dim']}]Open positions[/] [{C['cyan']}]{open_positions}[/]",
        f"[{C['dim']}]Total trades[/] [{C['white']}]{total_trades}[/]",
    )

    console.print(Panel(
        Align.center(grid),
        title=f"[bold {C['cyan']}]Risk Manager[/]",
        border_style=C["dim"],
        box=box.ROUNDED,
        padding=(0, 2),
    ))


# ══════════════════════════════════════════════════════════════════════════════
#  BLOCKCHAIN STATUS
# ══════════════════════════════════════════════════════════════════════════════

def print_blockchain_status(ok: bool, tx_hash: str | None = None, label: str = "Checkpoint"):
    if ok and tx_hash:
        console.print(f"  [{C['green']}]✓[/]  [{C['dim']}]{label} TX:[/] [{C['green']}]{tx_hash[:20]}…[/]")
    elif tx_hash:
        console.print(f"  [{C['red']}]✘[/]  [{C['dim']}]{label} reverted:[/] [{C['red']}]{tx_hash[:20]}…[/]")
    else:
        console.print(f"  [{C['red']}]✘[/]  [{C['dim']}]{label} failed (no TX)[/]")

def print_reputation_ok():
    console.print(f"  [{C['purple']}]★[/]  [{C['dim']}]Reputation confirmed[/]")


# ══════════════════════════════════════════════════════════════════════════════
#  NEXT SCAN COUNTDOWN
# ══════════════════════════════════════════════════════════════════════════════

def print_next_scan(minutes: int):
    console.print()
    console.print(Rule(style=C["dim"]))
    console.print(Align.center(
        f"[{C['dim']}]Next scan in [bold {C['cyan']}]{minutes}m[/] — Press [bold]Ctrl+C[/] to stop[/]"
    ))
    console.print()


# ══════════════════════════════════════════════════════════════════════════════
#  ALERT / ERROR
# ══════════════════════════════════════════════════════════════════════════════

def print_alert(message: str, level: str = "warn"):
    """level: 'warn' | 'error' | 'info'"""
    icons  = {"warn": "⚠", "error": "✘", "info": "ℹ"}
    colors = {"warn": C["yellow"], "error": C["red"], "info": C["blue"]}
    col  = colors.get(level, C["white"])
    icon = icons.get(level, "•")
    console.print(f"  [{col}]{icon}  {message}[/]")


# ══════════════════════════════════════════════════════════════════════════════
#  QUICK DEMO  (python terminal_ui.py)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print_banner(eth_balance=0.1484, agent_id=33, block_number=10_738_695)

    print_config({
        "mode": "PAPER TRADING (simulation)",
        "coins": "BTC, ETH, SOL",
        "scan_interval": 5,
        "max_trades": 50,
        "min_confidence": 55,
        "max_loss": 5,
        "take_profit": 1.2,
        "stop_loss": 0.8,
    })

    print_scan_header(cycle=1, coins=["BTC", "ETH", "SOL"])

    print_decision(
        symbol="BTC", action="BUY", confidence=70,
        price=78_696.00, change_24h=1.51,
        reason="BUY: +1.51% 24h momentum above +1.5% threshold",
        checkpoint_tx="48298fad516acd700c31", checkpoint_ok=False,
    )
    print_decision(
        symbol="ETH", action="BUY", confidence=70,
        price=2_374.72, change_24h=2.53,
        reason="BUY: +2.53% 24h momentum above +1.5% threshold",
        checkpoint_tx="2928bb91856fc555ed83", checkpoint_ok=False,
    )
    print_decision(
        symbol="SOL", action="HOLD", confidence=50,
        price=148.20, change_24h=1.37,
        reason="Score 0: Trend 0, MACD +1, RSI -1, Volume 0 — low confidence",
        checkpoint_tx=None,
    )

    print_reputation_ok()

    print_positions([
        {"symbol": "BTC", "entry_price": 78_696, "current_price": 78_900, "pnl_pct": 0.26,  "pnl_usd": 2.04},
        {"symbol": "ETH", "entry_price": 2_374.72, "current_price": 2_360, "pnl_pct": -0.62, "pnl_usd": -0.15},
    ])

    print_risk_summary(
        trades_today=2, max_trades=50,
        daily_pnl_pct=0.00, open_positions=2, total_trades=2,
    )

    print_next_scan(minutes=5)