import React from 'react'
import { motion } from 'framer-motion'

export default function PositionsPanel({ positions }) {
  const totalPnl = positions.reduce((acc, pos) => acc + pos.pnl, 0)
  
  return (
    <div className="rounded-xl bg-[#0c1624] border border-[#1a2d45] overflow-hidden">
      <div className="p-4 border-b border-[#1a2d45] flex items-center justify-between">
        <h3 className="font-bold text-white flex items-center gap-2">
          <motion.span 
            className="w-2 h-2 rounded-full bg-[#00e5ff]"
            animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          OPEN POSITIONS
        </h3>
        <div className="text-right">
          <div className="text-xs text-gray-500">Total PnL</div>
          <motion.div 
            className={`text-lg font-bold ${totalPnl >= 0 ? 'text-[#00ff9f]' : 'text-[#ff4560]'}`}
            key={totalPnl}
            animate={{ 
              textShadow: totalPnl >= 0 ? ['0 0 10px #00ff9f', '0 0 20px #00ff9f', '0 0 10px #00ff9f'] : ['0 0 10px #ff4560', '0 0 20px #ff4560', '0 0 10px #ff4560']
            }}
            transition={{ duration: 1, repeat: Infinity }}
          >
            {totalPnl >= 0 ? '+' : ''}{totalPnl.toFixed(2)}%
          </motion.div>
        </div>
      </div>
      
      <div className="p-4 space-y-3">
        {positions.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <div className="text-4xl mb-2">📊</div>
            <div>No open positions</div>
          </div>
        ) : (
          positions.map((pos, index) => (
            <motion.div
              key={pos.symbol}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`relative rounded-lg p-3 border ${
                pos.pnl >= 0 
                  ? 'border-[#00ff9f]/30 bg-[#00ff9f]/5' 
                  : 'border-[#ff4560]/30 bg-[#ff4560]/5'
              }`}
              style={{
                boxShadow: pos.pnl >= 0 ? '0 0 20px rgba(0, 255, 159, 0.1)' : '0 0 20px rgba(255, 69, 96, 0.1)'
              }}
            >
              {pos.pnl >= 0 && (
                <motion.div 
                  className="absolute inset-0 rounded-lg pointer-events-none"
                  animate={{ 
                    boxShadow: ['0 0 20px rgba(0, 255, 159, 0.1)', '0 0 40px rgba(0, 255, 159, 0.3)', '0 0 20px rgba(0, 255, 159, 0.1)']
                  }}
                  transition={{ 
                    duration: Math.max(1, 3 - pos.pnl * 0.5), 
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />
              )}
              
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white">{pos.symbol}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    pos.side === 'LONG' ? 'bg-[#00e5ff]/20 text-[#00e5ff]' : 'bg-[#ff00ff]/20 text-[#ff00ff]'
                  }`}>
                    {pos.side}
                  </span>
                </div>
                <motion.div 
                  className={`text-sm font-bold ${pos.pnl >= 0 ? 'text-[#00ff9f]' : 'text-[#ff4560]'}`}
                  animate={{ scale: pos.pnl >= 0 ? [1, 1.05, 1] : [1, 0.95, 1] }}
                  transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
                >
                  {pos.pnl >= 0 ? '+' : ''}{pos.pnl.toFixed(2)}%
                </motion.div>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500">Entry</span>
                  <span className="text-white font-mono">${pos.entry.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Current</span>
                  <span className="text-white font-mono">${pos.current.toLocaleString()}</span>
                </div>
              </div>
              
              <div className="mt-2 h-1 bg-[#1a2d45] rounded-full overflow-hidden">
                <motion.div 
                  className={`h-full ${pos.pnl >= 0 ? 'bg-[#00ff9f]' : 'bg-[#ff4560]'}`}
                  initial={{ width: '0%' }}
                  animate={{ width: `${Math.min(Math.abs(pos.pnl) * 20, 100)}%` }}
                  transition={{ duration: 1, delay: 0.5 }}
                />
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  )
}