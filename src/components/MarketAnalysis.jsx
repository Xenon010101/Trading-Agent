import React from 'react'
import { motion } from 'framer-motion'
import Sparkline from './Sparkline'

export default function MarketAnalysis({ prices }) {
  const coins = [
    { symbol: 'BTC', name: 'Bitcoin', signals: { macd: 'BULLISH', rsi: 58, trend: 'UP', momentum: '+5.16%' } },
    { symbol: 'ETH', name: 'Ethereum', signals: { macd: 'NEUTRAL', rsi: 52, trend: 'FLAT', momentum: '-0.87%' } },
    { symbol: 'SOL', name: 'Solana', signals: { macd: 'BULLISH', rsi: 65, trend: 'UP', momentum: '+5.16%' } },
  ]

  const getAction = (signals) => {
    if (signals.macd === 'BULLISH' && signals.momentum.includes('+')) return 'BUY'
    if (signals.macd === 'BEARISH' || signals.momentum.includes('-')) return 'SELL'
    return 'HOLD'
  }

  const getActionColor = (action) => {
    switch (action) {
      case 'BUY': return '#00ff9f'
      case 'SELL': return '#ff4560'
      default: return '#ffb800'
    }
  }

  return (
    <div className="rounded-xl bg-[#0c1624] border border-[#1a2d45] overflow-hidden">
      <div className="p-4 border-b border-[#1a2d45] flex items-center justify-between">
        <h3 className="font-bold text-white flex items-center gap-2">
          <motion.span 
            className="w-2 h-2 rounded-full bg-[#00e5ff]"
            animate={{ scale: [1, 1.2, 1], opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
          LIVE MARKET ANALYSIS
        </h3>
        <span className="text-xs text-gray-500">● REAL-TIME</span>
      </div>

      <div className="divide-y divide-[#1a2d45]">
        {coins.map((coin, index) => {
          const action = getAction(coin.signals)
          const priceData = prices[coin.symbol]
          
          return (
            <motion.div
              key={coin.symbol}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 hover:bg-[#0c1624]/50 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-[#1a2d45] flex items-center justify-center font-bold text-lg"
                       style={{ color: coin.symbol === 'BTC' ? '#f7931a' : coin.symbol === 'ETH' ? '#627eea' : '#00ffa3' }}>
                    {coin.symbol.charAt(0)}
                  </div>
                  <div>
                    <div className="font-bold">{coin.symbol}</div>
                    <div className="text-xs text-gray-500">{coin.name}</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  {['MACD', 'RSI', 'Trend'].map((signal) => (
                    <div key={signal} className="text-center">
                      <div className="text-[10px] text-gray-500">{signal}</div>
                      <div className={`text-xs font-bold ${
                        coin.signals[signal.toLowerCase()] === 'BULLISH' || coin.signals[signal.toLowerCase()] > 50
                          ? 'text-[#00ff9f]' 
                          : coin.signals[signal.toLowerCase()] === 'BEARISH' || coin.signals[signal.toLowerCase()] < 40
                          ? 'text-[#ff4560]'
                          : 'text-gray-400'
                      }`}>
                        {signal === 'RSI' ? coin.signals.rsi : coin.signals[signal.toLowerCase()]}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  <span className={`px-3 py-1 rounded-md text-xs font-bold ${
                    action === 'BUY' ? 'bg-[#00ff9f]/20 text-[#00ff9f]' :
                    action === 'SELL' ? 'bg-[#ff4560]/20 text-[#ff4560]' :
                    'bg-[#ffb800]/20 text-[#ffb800]'
                  }`}>
                    {action}
                  </span>
                  <span className={`px-2 py-1 rounded-md text-xs ${
                    coin.signals.momentum.startsWith('+') ? 'text-[#00ff9f] bg-[#00ff9f]/10' : 'text-[#ff4560] bg-[#ff4560]/10'
                  }`}>
                    {coin.signals.momentum}
                  </span>
                </div>
                
                <div className="w-16 h-6">
                  <Sparkline 
                    data={priceData?.sparkline || []} 
                    color={coin.signals.momentum.startsWith('+') ? '#00ff9f' : '#ff4560'} 
                  />
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}