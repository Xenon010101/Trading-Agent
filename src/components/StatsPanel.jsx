import React from 'react'
import { motion } from 'framer-motion'
import { LineChart, Line, ResponsiveContainer } from 'recharts'

const mockChartData = [
  { value: 0 }, { value: 2 }, { value: -1 }, { value: 3 }, { value: 1 },
  { value: 4 }, { value: 2 }, { value: 5 }, { value: 3 }, { value: 2.35 }
]

export default function StatsPanel({ dailyPnl, decisions, tradesToday, maxTrades }) {
  const tradeProgress = (tradesToday / maxTrades) * 100

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative overflow-hidden rounded-xl p-4 bg-[#0c1624] border border-[#1a2d45]"
      >
        <div className="absolute top-0 right-0 w-16 h-16 opacity-10">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockChartData}>
              <Line type="monotone" dataKey="value" stroke="#00ff9f" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="text-xs text-gray-500 mb-1">DAILY PnL</div>
        <motion.div 
          className={`text-2xl font-bold ${dailyPnl >= 0 ? 'text-[#00ff9f]' : 'text-[#ff4560]'}`}
          key={dailyPnl}
          initial={{ scale: 1.2 }}
          animate={{ scale: 1 }}
        >
          {dailyPnl >= 0 ? '+' : ''}{dailyPnl.toFixed(2)}%
        </motion.div>
        <motion.div 
          className="text-xs text-gray-500 mt-1"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          ▲ +$1,847.32
        </motion.div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
        className="relative overflow-hidden rounded-xl p-4 bg-[#0c1624] border border-[#1a2d45]"
      >
        <div className="text-xs text-gray-500 mb-1">TOTAL DECISIONS</div>
        <motion.div 
          className="text-2xl font-bold text-[#00e5ff]"
          key={decisions}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {decisions}
        </motion.div>
        <div className="text-xs text-gray-500 mt-1">All time</div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="relative overflow-hidden rounded-xl p-4 bg-[#0c1624] border border-[#1a2d45]"
      >
        <div className="text-xs text-gray-500 mb-1">TRADES TODAY</div>
        <div className="text-2xl font-bold text-white">
          {tradesToday}<span className="text-lg text-gray-500">/{maxTrades}</span>
        </div>
        
        <div className="mt-3 h-2 bg-[#1a2d45] rounded-full overflow-hidden">
          <motion.div 
            className="h-full bg-gradient-to-r from-[#00e5ff] to-[#00ff9f]"
            initial={{ width: 0 }}
            animate={{ width: `${tradeProgress}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </div>
        
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{tradeProgress.toFixed(0)}% used</span>
          <span>{maxTrades - tradesToday} left</span>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
        className="relative overflow-hidden rounded-xl p-4 bg-[#0c1624] border"
        style={{ 
          borderColor: '#00ff9f',
          boxShadow: '0 0 20px rgba(0, 255, 159, 0.2)'
        }}
      >
        <div className="flex items-center gap-2 mb-1">
          <motion.div 
            className="w-2 h-2 rounded-full bg-[#00ff9f]"
            animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
          <div className="text-xs text-gray-500">CIRCUIT BREAKER</div>
        </div>
        <motion.div 
          className="text-2xl font-bold text-[#00ff9f]"
          animate={{ textShadow: ['0 0 10px #00ff9f', '0 0 20px #00ff9f', '0 0 10px #00ff9f'] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          SAFE
        </motion.div>
        <div className="text-xs text-gray-500 mt-1">-2.1% max daily loss</div>
      </motion.div>
    </div>
  )
}