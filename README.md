# InsiderEdge

> Autonomous AI Crypto Trading Agent | ERC-8004 Hackathon Submission | lablab.ai × Kraken

## Live Dashboard

- **Vercel**: [trading-agent-peach.vercel.app](https://trading-agent-peach.vercel.app)
- **GitHub Pages**: [Xenon010101.github.io/Trading-Agent](https://Xenon010101.github.io/Trading-Agent)

## Live Stats

| Metric | Value |
|--------|-------|
| Agent ID | 33 (Sepolia Testnet) |
| Network | Sepolia (Chain ID: 11155111) |
| Mode | Paper Trading |
| Coins | BTC, ETH, SOL |
| Scan Interval | 5 minutes |
| Total Decisions | 138 |
| On-Chain Checkpoints | 138 |

## Performance

| Action | Count | Percentage |
|--------|-------|------------|
| BUY | 24 | 17% |
| SELL | 57 | 41% |
| HOLD | 57 | 41% |

## What It Does

InsiderEdge analyzes BTC, ETH, and SOL every 5 minutes using RSI, MACD, and trend signals. Groq LLaMA 70B makes the final trading decision with multi-signal scoring. All decisions are posted to the ERC-8004 ValidationRegistry on Sepolia testnet for transparent verification.

## Architecture

```
CoinGecko API -> market_data.py -> ai_brain.py
                                    |
                                    v
                          Groq LLaMA 70B
                                    |
                                    v
                          Multi-Signal Scoring
                          (RSI + MACD + Trend + Momentum)
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
| Min Confidence | 55% |
| Circuit Breaker | -5% daily loss |

## ERC-8004 Integration

- **Agent ID**: 33
- **Operator**: `0x8cf8480f0f7A87BB966485f55C67cF406159d5F7`
- **Network**: Sepolia Testnet (Chain ID: 11155111)
- **Risk Router**: `0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC`
- **Validation Registry**: `0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1`

Every decision (BUY/SELL/HOLD) is posted as a checkpoint with confidence score ≥90 on-chain.

## Tech Stack

- **Python 3.x** - Trading agent backend
- **React + Vite** - Dashboard frontend
- **Framer Motion** - Animations
- **Tailwind CSS** - Styling
- **Groq API** (LLaMA 3.3 70B) - AI decision making
- **CoinGecko API** - Price & OHLC data
- **Web3.py** - Blockchain interaction
- **Technical Analysis** - RSI, MACD, trend detection

## Setup

### Backend (Trading Agent)
```bash
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
python agent.py
```

### Frontend (Dashboard)
```bash
npm install
npm run dev      # Development server at http://localhost:5173
npm run build    # Production build
npm run preview # Preview production build
```

## Deployment

### GitHub Pages
1. Push to GitHub
2. Settings → Pages → Source: main, folder: `/docs`
3. Dashboard: `https://Xenon010101.github.io/Trading-Agent`

### Vercel
1. Import GitHub repo to Vercel
2. Root directory: `web/`
3. Framework: Other

## Disclaimer

This is a hackathon project. Paper trading only. Not financial advice.

---

**Team Dhurandhar** | lablab.ai × Kraken AI Trading Hackathon

- Anmol Patel — 3rd Year IT
- Akshita — 1st Year CSE

Twitter: [@Anmol_patel2112](https://twitter.com/Anmol_patel2112)
GitHub: [github.com/Xenon010101/Trading-Agent](https://github.com/Xenon010101/Trading-Agent)