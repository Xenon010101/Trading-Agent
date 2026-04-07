# InsiderEdge
## Hackathon Submission

**Run:** `python agent.py`

InsiderEdge is an autonomous cryptocurrency trading agent that combines real-time market data with AI-powered decision making. The agent continuously monitors multiple cryptocurrencies, analyzes market conditions through an LLaMA 70B model, and executes trades—either in safe paper trading mode or live via Kraken CLI.

---

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  PRISM API  │───▶│ market_data  │───▶│   ai_brain   │
│  (Prices &  │    │    .py       │    │     .py      │
│   Signals)  │    └──────────────┘    │  (LLaMA 70B) │
└─────────────┘         │              └──────┬───────┘
                        │                      │
                        ▼                      ▼
                ┌──────────────┐    ┌──────────────┐
                │   logger     │◀───│ risk_manager  │
                │     .py      │    │     .py       │
                └──────────────┘    └──────┬───────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │  executor    │
                                   │     .py      │
                                   │ (Kraken CLI) │
                                   └──────────────┘
```

**Data Flow:**
1. **PRISM API** fetches current prices and trading signals
2. **market_data.py** aggregates market summary
3. **ai_brain.py** sends data to Groq for AI analysis
4. **risk_manager.py** validates the decision against safety rules
5. **executor.py** executes the trade or simulates in paper mode
6. **logger.py** records all decisions to trade_log.txt

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Coin Analysis** | Monitors BTC, ETH, and SOL simultaneously |
| **AI-Powered Decisions** | Leverages LLaMA 70B via Groq API for intelligent trading signals |
| **Risk Management** | Enforces daily trade limits, confidence thresholds, and max loss caps |
| **Decision Logging** | Complete audit trail of all analysis and executions |
| **Paper Trading** | Safe testing mode with simulated trades and no real capital |
| **Live Trading** | Real order execution through Kraken CLI integration |

---

## Setup

### Prerequisites

- Python 3.8+
- API keys for PRISM, Groq, and Kraken

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd trading-agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

### Environment Variables

Edit `.env` with your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
PRISM_API_KEY=your_prism_api_key_here
KRAKEN_API_KEY=your_kraken_api_key_here
KRAKEN_API_SECRET=your_kraken_api_secret_here
```

### Configuration

Adjust settings in `config.py`:

```python
WATCHLIST = ["BTC", "ETH", "SOL"]      # Coins to monitor
INTERVAL_MINUTES = 5                    # Scan frequency
MAX_TRADES_PER_DAY = 5                  # Daily trade limit
MIN_CONFIDENCE = 70                     # Minimum AI confidence
MAX_LOSS_PERCENT = 5                    # Max daily loss %
PAPER_MODE = True                       # True = simulation, False = live
```

### Run

```bash
# Test setup
python test_setup.py

# Start the agent
python agent.py
```

---

## How It Works

### Module Overview

| Module | Purpose |
|--------|---------|
| `agent.py` | Main loop orchestrating all components |
| `market_data.py` | Fetches price and signal data from PRISM API |
| `ai_brain.py` | Analyzes market data using Groq LLaMA 70B |
| `risk_manager.py` | Enforces trading rules and limits |
| `executor.py` | Executes trades via Kraken CLI (or simulates) |
| `logger.py` | Records all decisions and generates reports |
| `config.py` | Centralized configuration constants |

### Decision Process

1. **Fetch** — Collects price and signal data for each coin
2. **Analyze** — Sends data to LLaMA 70B with strict trading rules
3. **Validate** — Risk manager checks confidence, limits, and P&L
4. **Execute** — Places order (paper or live) if all checks pass
5. **Log** — Records the complete decision chain for review

---

## ⚠️ Risk Disclaimer

**This software is provided for educational and experimental purposes only.**

- Trading cryptocurrencies carries substantial risk of financial loss
- Backtested performance does not guarantee future results
- Always use paper trading mode before risking real capital
- The developers accept no liability for losses incurred through use of this software
- Ensure you understand the risks and comply with local regulations before trading

**Never invest more than you can afford to lose.**
