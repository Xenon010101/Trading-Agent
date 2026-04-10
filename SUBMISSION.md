# InsiderEdge — Hackathon Submission Summary

## Project Overview

InsiderEdge is a fully autonomous AI crypto trading agent that combines Groq LLaMA 70B decision-making with ERC-8004 on-chain verification on Ethereum Sepolia testnet.

## Prize Categories Targeting

1. **Best Risk-Adjusted Return** — Sharpe ratio tracking, stop loss, take profit, circuit breaker
2. **Best Compliance & Risk Guardrails** — 6 safety mechanisms including circuit breaker
3. **Best Trustless Trading Agent** — ERC-8004 Agent ID 33, full on-chain audit trail
4. **Social Engagement** — Daily Twitter updates @Anmol_patel2112

## Key Differentiators

- **Multi-signal scoring**: RSI + MACD + Trend must agree before trading
- **Circuit breaker**: Auto-halts at -5% daily loss
- **Every decision on-chain**: All 530+ decisions posted to ValidationRegistry
- **Built by CS student**: Non-professional trader in 4 days
- **Complete audit trail**: checkpoints.jsonl + trade_log.txt + blockchain

## Addresses

| Type | Address |
|------|---------|
| Agent ID | 33 |
| Operator | `0x8cf8480f0f7A87BB966485f55C67cF406159d5F7` |
| Agent Wallet | `0xF7C5fA025b2CF3a943723B087871cA49E92AbA72` |
| Validation Registry | `0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1` |
| Risk Router | `0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC` |

## Risk Management Features

1. **Stop Loss**: 0.8% per position
2. **Take Profit**: 1.2% per position
3. **Max Daily Trades**: 50
4. **Min Confidence**: 60% (AI must be confident)
5. **Circuit Breaker**: Halts at -5% daily loss
6. **Max Loss**: 5% daily cap

## How It Works

1. Collects price data from CoinGecko every 10 minutes
2. Calculates RSI, MACD, and trend signals
3. Groq LLaMA 70B scores all signals
4. Risk manager validates decision
5. Trade executes (paper or live)
6. Checkpoint posted to ValidationRegistry on-chain

## Links

- **GitHub**: [Repository Link]
- **Twitter**: [@Anmol_patel2112](https://twitter.com/Anmol_patel2112)
- **Leaderboard**: https://lablab.ai/ai-hackathons/ai-trading-agents/live

## Team

**Anmol Patel** — 3rd Year Computer Science Student

## Results

- 530+ autonomous decisions logged
- Full on-chain audit trail (Agent ID: 33)
- Circuit breaker tested and functional
- Zero crashes in continuous operation

---

*Built with Groq LLaMA 70B + Web3.py + CoinGecko*
