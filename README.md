# InsiderEdge

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Paper%20Trading-orange.svg)
![AI](https://img.shields.io/badge/AI-Groq%20LLaMA%2070B-8B5CF6.svg)
![Blockchain](https://img.shields.io/badge/Chain-Sepolia-10A37F.svg)
![On-Chain](https://img.shields.io/badge/ERC-8004-2563EB.svg)

> **Autonomous AI-powered cryptocurrency trading agent with on-chain verification via ERC-8004 smart contracts.**

---

## Overview

InsiderEdge is an autonomous AI trading agent that continuously monitors cryptocurrency markets, analyzes technical indicators, and makes data-driven trading decisions using Groq's LLaMA 3.3 70B language model. Every decision is recorded on-chain via the ERC-8004 standard for full transparency and verifiability.

### Key Features

- **AI-Powered Analysis** — Groq LLaMA 70B processes multi-signal technical analysis (RSI, MACD, trend, momentum) to produce BUY/SELL/HOLD decisions with confidence scoring
- **On-Chain Verification** — All decisions posted as checkpoints to the ERC-8004 ValidationRegistry on Sepolia testnet
- **Real-Time Market Data** — Dual-source price feeds (Binance primary, CoinGecko fallback) with per-symbol caching
- **Risk Management** — Circuit breaker, position limits, take-profit/stop-loss automation, daily loss caps
- **Live Dashboard** — React-based monitoring UI deployed to GitHub Pages with real-time metrics
- **Terminal UI** — Cyberpunk-styled Rich terminal interface with color-coded alerts, tables, and scan summaries
- **Paper Trading Mode** — Safe simulation environment for strategy validation without real financial risk

---

## Live Dashboard

[View Dashboard →](https://Xenon010101.github.io/Trading-Agent)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     InsiderEdge Agent                           │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │  market_data │───▶│  ai_brain    │───▶│  risk_manager     │  │
│  │  .py         │    │  .py         │    │  .py              │  │
│  │              │    │              │    │                   │  │
│  │ • Binance    │    │ • Groq API   │    │ • Circuit breaker │  │
│  │ • CoinGecko  │    │ • LLaMA 70B  │    │ • Position limits │  │
│  │ • RSI/MACD   │    │ • Multi-sig  │    │ • TP/SL checks    │  │
│  │   /Trend     │    │   scoring    │    │ • Daily caps      │  │
│  └──────────────┘    └──────────────┘    └────────┬──────────┘  │
│                                                   │             │
│                                          ┌────────▼──────────┐  │
│                                          │  executor.py      │  │
│                                          │                   │  │
│                                          │ • Paper trading   │  │
│                                          │ • Live (Kraken)   │  │
│                                          └────────┬──────────┘  │
│                                                   │             │
│                                          ┌────────▼──────────┐  │
│                                          │  erc8004.py       │  │
│                                          │                   │  │
│                                          │ • Checkpoints     │  │
│                                          │ • Trade intents   │  │
│                                          │ • Reputation      │  │
│                                          └────────┬──────────┘  │
└───────────────────────────────────────────────────│─────────────┘
                                                    │
                                     ┌──────────────▼──────────────┐
                                     │  Sepolia Testnet            │
                                     │                             │
                                     │  • ValidationRegistry       │
                                     │  • RiskRouter               │
                                     │  • ERC-8004 Attestations    │
                                     └─────────────────────────────┘
```

---

## Tech Stack

### Backend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.10+ | Trading agent core |
| AI Engine | Groq API (LLaMA 3.3 70B) | Decision-making & signal analysis |
| Market Data | Binance API + CoinGecko | Price feeds, OHLC, 24h change |
| Blockchain | Web3.py | Sepolia testnet interaction |
| Terminal UI | Rich library | Cyberpunk-styled CLI interface |
| Technical Analysis | Custom RSI, MACD, trend | Multi-signal scoring system |

### Frontend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 18 + Vite | Dashboard SPA |
| Styling | Tailwind CSS | Component styling |
| Animations | Framer Motion | Transitions & effects |
| Deployment | GitHub Pages (`/docs`) | Static hosting |

---

## Risk Management

| Parameter | Value | Description |
|-----------|-------|-------------|
| Stop Loss | 0.8% | Auto-exit when position drops below threshold |
| Take Profit | 1.2% | Auto-exit when position reaches target |
| Max Daily Trades | 50 | Hard limit on trades per 24h period |
| Min Confidence | 55% | Minimum AI confidence required to execute |
| Circuit Breaker | -5% | Halts all trading if daily loss exceeds threshold |
| Position Size | 0.001 BTC | Fixed paper trading position size |
| Confidence Clamp | 90-100 | On-chain checkpoint confidence floor |

---

## ERC-8004 Integration

| Component | Address | Purpose |
|-----------|---------|---------|
| **Agent ID** | `33` | Unique identifier on Sepolia |
| **Operator Wallet** | `0x8cf8...d5F7` | Transaction signer |
| **Network** | Sepolia (Chain ID: 11155111) | Testnet |
| **ValidationRegistry** | `0x92bF...87F1` | Posts checkpoints & attestations |
| **RiskRouter** | `0xd6A6...FdBc` | Submits & verifies trade intents |

Every decision (BUY/SELL/HOLD) is posted as an on-chain checkpoint with:
- Timestamp
- Symbol & action
- Confidence score
- Reason string
- Transaction hash

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Groq API key (https://console.groq.com)
- Sepolia testnet ETH (from [faucet](https://sepoliafaucet.com/))

### Backend

```bash
# Clone the repository
git clone https://github.com/Xenon010101/Trading-Agent.git
cd Trading-Agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys:
#   GROQ_API_KEY=your_groq_api_key
#   OPERATOR_PRIVATE_KEY=your_sepolia_private_key
#   AGENT_ID=33

# Run the agent
python agent.py
```

### Frontend (Dashboard)

```bash
# Install dependencies
npm install

# Development server (http://localhost:5173)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for LLaMA 70B access |
| `GROQ_API_KEY_2` | No | Backup API key for rate limit failover |
| `OPERATOR_PRIVATE_KEY` | Yes | Sepolia wallet private key for transactions |
| `OPERATOR_ADDRESS` | Yes | Sepolia wallet address |
| `AGENT_ID` | Yes | ERC-8004 agent identifier (default: 33) |
| `PAPER_MODE` | No | Set to `True` for paper trading (default) |

---

## Project Structure

```
Trading-Agent/
├── agent.py              # Main orchestrator & scan loop
├── ai_brain.py           # Groq LLaMA analysis & decision engine
├── market_data.py        # Binance/CoinGecko price & OHLC data
├── risk_manager.py       # Position limits, circuit breaker, P&L
├── executor.py           # Trade execution (paper + live)
├── erc8004.py            # Sepolia on-chain checkpoints & intents
├── terminal_ui.py        # Rich-based cyberpunk terminal interface
├── report.py             # Daily reports & Sharpe ratio
├── logger.py             # Trade logging to JSONL
├── config.py             # Centralized configuration
├── src/                  # React dashboard source
│   ├── App.jsx
│   ├── components/
│   └── ...
└── docs/                 # GitHub Pages deployment
    └── index.html
```

---

## Configuration

Edit `config.py` to customize trading parameters:

```python
WATCHLIST = ["BTC", "ETH", "SOL"]        # Coins to monitor
INTERVAL_MINUTES = 5                      # Scan frequency
MAX_TRADES_PER_DAY = 50                   # Daily trade limit
MIN_CONFIDENCE = 55                       # Minimum confidence to trade
MAX_LOSS_PERCENT = 5                      # Maximum daily loss (%)
TAKE_PROFIT_PERCENT = 1.2                 # Take profit threshold (%)
STOP_LOSS_PERCENT = 0.8                   # Stop loss threshold (%)
CIRCUIT_BREAKER_THRESHOLD = -5.0          # Circuit breaker trigger (%)
PAPER_MODE = True                         # Paper trading (True/False)
```

---

## Decision Flow

```
Market Data Fetched (Binance/CoinGecko)
         │
         ▼
Technical Analysis (RSI + MACD + Trend)
         │
         ▼
Momentum Check (24h change > ±1.5% → instant signal)
         │
         ▼
Groq LLaMA 70B Multi-Signal Scoring
         │
         ▼
Score-Based Decision:
  +3 or more → BUY (85% confidence)
  +2         → BUY (75% confidence)
  +1 or 0    → HOLD (50% confidence)
  -2         → SELL (75% confidence)
  -3 or less → SELL (85% confidence)
         │
         ▼
Risk Validation (circuit breaker, limits, confidence)
         │
         ▼
Execute Trade (paper/live) + Post On-Chain Checkpoint
```

---

## Disclaimer

This project is for **educational and research purposes only**. It operates in **paper trading mode** by default and does not involve real financial transactions. This is **not financial advice**. The authors are not responsible for any financial losses resulting from the use of this software.

Cryptocurrency trading involves significant risk. Always do your own research before making investment decisions.

---

## License

MIT License — see LICENSE file for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**InsiderEdge** — Autonomous AI Crypto Trading Agent

Developed by [Anmol Patel](https://github.com/Xenon010101) · Co-developed with [Akshita](https://github.com/Akshita-2307)

[Twitter](https://twitter.com/Anmol_patel2112) · [Dashboard](https://Xenon010101.github.io/Trading-Agent) · [GitHub](https://github.com/Xenon010101/Trading-Agent)
