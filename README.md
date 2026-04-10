# InsiderEdge 🤖

> Autonomous AI Crypto Trading Agent | ERC-8004 Hackathon Submission

## Live Stats

| Metric | Value |
|--------|-------|
| Agent ID | 33 (Sepolia Testnet) |
| Network | Sepolia (Chain ID: 11155111) |
| Mode | Paper Trading |
| Coins | BTC, ETH, SOL |
| Scan Interval | 10 minutes |

## What It Does

InsiderEdge analyzes BTC, ETH, and SOL every 10 minutes using RSI, MACD, and trend signals. Groq LLaMA 70B makes the final trading decision with multi-signal scoring. All trades are verified on Ethereum Sepolia testnet via ERC-8004 smart contracts.

## Architecture

```
CoinGecko API -> market_data.py -> ai_brain.py
                                    |
                                    v
                          Groq LLaMA 70B
                                    |
                                    v
                         Multi-Signal Scoring
                         (RSI + MACD + Trend)
                                    |
                                    v
                          risk_manager.py
                                    |
                                    v
                           executor.py
                                    |
                                    v
                    ERC-8004 On-chain Verification
                    (ValidationRegistry Agent ID: 33)
```

## Risk Management

| Feature | Value |
|---------|-------|
| Stop Loss | 0.8% per position |
| Take Profit | 1.2% per position |
| Max Daily Trades | 50 |
| Min Confidence | 60% |
| Circuit Breaker | -5% daily loss |
| Max Loss | 5% |

## ERC-8004 Integration

- **Agent Registry**: `0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3`
- **Agent ID**: 33
- **Operator**: `0x8cf8480f0f7A87BB966485f55C67cF406159d5F7`
- **Network**: Sepolia Testnet (Chain ID: 11155111)
- **Risk Router**: `0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC`
- **Validation Registry**: `0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1`

Every trade is posted as a signed EIP-712 checkpoint on-chain.

## Tech Stack

- **Python 3.x**
- **Groq API** (LLaMA 3.3 70B)
- **CoinGecko API** (price data)
- **Web3.py** (blockchain)
- **Kraken CLI** (execution)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
python agent.py
```

## Configuration

Edit `config.py`:

```python
WATCHLIST = ["BTC", "ETH", "SOL"]
INTERVAL_MINUTES = 10
MAX_TRADES_PER_DAY = 50
MIN_CONFIDENCE = 60
MAX_LOSS_PERCENT = 5
TAKE_PROFIT_PERCENT = 1.2
STOP_LOSS_PERCENT = 0.8
PAPER_MODE = True
```

## Disclaimer

This is a hackathon project. Paper trading only. Not financial advice.

---

Built by **Anmol Patel** — 3rd Year CS Student  
Twitter: [@Anmol_patel2112](https://twitter.com/Anmol_patel2112)
