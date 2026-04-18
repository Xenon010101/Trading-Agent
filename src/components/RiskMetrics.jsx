import React from 'react'
import { motion } from 'framer-motion'

export default function RiskMetrics() {
  const metrics = [
    { label: 'Stop Loss', value: '0.8%', color: '#ff4560', icon: '🛑' },
    { label: 'Take Profit', value: '1.2%', color: '#00ff9f', icon: '🎯' },
    { label: 'Min Confidence', value: '55%', color: '#00e5ff', icon: '⚡' },
    { label: 'Max Daily Loss', value: '5%', color: '#ffb800', icon: '⚠️' },
  ]

  return (
    <div className="rounded-xl bg-[#0c1624] border border-[#1a2d45] overflow-hidden">
      <div className="p-4 border-b border-[#1a2d45]">
        <h3 className="font-bold text-white flex items-center gap-2">
          <motion.span 
            className="w-2 h-2 rounded-full bg-[#ffb800]"
            animate={{ scale: [1, 1.3, 1], opacity: [1, 0.5, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
          RISK MANAGEMENT
        </h3>
      </div>
      
      <div className="p-4 grid grid-cols-2 gap-3">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="relative rounded-lg p-3 bg-[#060b14] border border-[#1a2d45]"
          >
            <div className="flex items-center gap-2 mb-1">
              <span>{metric.icon}</span>
              <span className="text-xs text-gray-500">{metric.label}</span>
            </div>
            <motion.div 
              className="text-lg font-bold"
              style={{ color: metric.color }}
              animate={{ 
                textShadow: [`0 0 5px ${metric.color}`, `0 0 15px ${metric.color}`, `0 0 5px ${metric.color}`]
              }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {metric.value}
            </motion.div>
          </motion.div>
        ))}
      </div>
      
      <div className="p-4 pt-0">
        <div className="relative h-2 bg-[#1a2d45] rounded-full overflow-hidden">
          <motion.div 
            className="absolute inset-0 bg-gradient-to-r from-[#00ff9f] via-[#00e5ff] to-[#00ff9f]"
            animate={{ backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'] }}
            transition={{ duration: 3, repeat: Infinity }}
            style={{ backgroundSize: '200% 100%' }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-2">
          <span>Conservative</span>
          <span>Balanced</span>
          <span>Aggressive</span>
        </div>
      </div>
    </div>
  )
}