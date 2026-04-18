import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Sparkline from './Sparkline'

const cryptoIcons = {
  BTC: '₿',
  ETH: 'Ξ',
  SOL: '◎'
}

const cryptoNames = {
  BTC: 'Bitcoin',
  ETH: 'Ethereum',
  SOL: 'Solana'
}

const cryptoColors = {
  BTC: '#f7931a',
  ETH: '#627eea',
  SOL: '#00ffa3'
}

export default function PriceTicker({ prices }) {
  const [hoveredCoin, setHoveredCoin] = useState(null)

  const coins = [
    { symbol: 'BTC', ...prices.BTC },
    { symbol: 'ETH', ...prices.ETH },
    { symbol: 'SOL', ...prices.SOL }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {coins.map((coin, index) => (
        <motion.div
          key={coin.symbol}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="relative group"
          onMouseEnter={() => setHoveredCoin(coin.symbol)}
          onMouseLeave={() => setHoveredCoin(null)}
        >
          <motion.div 
            className={`
              relative overflow-hidden rounded-xl p-4 
              bg-gradient-to-br from-[#0c1624] to-[#060b14]
              border border-[#1a2d45]
              ${coin.change >= 0 ? 'hover:border-[#00ff9f]/50' : 'hover:border-[#ff4560]/50'}
            `}
            whileHover={{ scale: 1.02 }}
            transition={{ type: 'spring', stiffness: 300 }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]" />
            
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <motion.span 
                  className="text-2xl"
                  style={{ color: cryptoColors[coin.symbol] }}
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  {cryptoIcons[coin.symbol]}
                </motion.span>
                <div>
                  <div className="font-bold text-lg">{coin.symbol}</div>
                  <div className="text-xs text-gray-500">{cryptoNames[coin.symbol]}</div>
                </div>
              </div>
              
              <motion.div
                className={`px-2 py-1 rounded-md text-xs font-bold ${
                  coin.change >= 0 ? 'bg-[#00ff9f]/20 text-[#00ff9f]' : 'bg-[#ff4560]/20 text-[#ff4560]'
                }`}
                animate={{ 
                  backgroundColor: coin.change >= 0 ? ['rgba(0,255,159,0.2)','rgba(0,255,159,0.4)','rgba(0,255,159,0.2)'] : ['rgba(255,69,96,0.2)','rgba(255,69,96,0.4)','rgba(255,69,96,0.2)']
                }}
                transition={{ duration: 1, repeat: Infinity }}
              >
                {coin.change >= 0 ? '▲' : '▼'} {Math.abs(coin.change).toFixed(2)}%
              </motion.div>
            </div>
            
            <div className="flex items-end justify-between">
              <motion.div 
                className="text-2xl font-bold font-mono"
                key={coin.price}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                ${coin.symbol === 'SOL' ? coin.price.toFixed(2) : coin.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </motion.div>
              
              <div className="w-20 h-8">
                <Sparkline data={coin.sparkline} color={coin.change >= 0 ? '#00ff9f' : '#ff4560'} />
              </div>
            </div>
            
            <AnimatePresence>
              {hoveredCoin === coin.symbol && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-3 pt-3 border-t border-[#1a2d45]"
                >
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-500">24h High</span>
                      <span className="text-white">${(coin.price * 1.03).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">24h Low</span>
                      <span className="text-white">${(coin.price * 0.97).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Volume</span>
                      <span className="text-white">$2.4B</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Signals</span>
                      <span className="text-[#00e5ff]">BULLISH</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            
            {coin.change >= 0 && (
              <motion.div 
                className="absolute inset-0 rounded-xl pointer-events-none"
                initial={{ opacity: 0 }}
                animate={{ opacity: [0, 0.05, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                style={{ boxShadow: 'inset 0 0 30px rgba(0, 255, 159, 0.1)' }}
              />
            )}
          </motion.div>
        </motion.div>
      ))}
    </div>
  )
}