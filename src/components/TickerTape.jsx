import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function TickerTape({ trades }) {
  const tickerItems = [
    ...trades,
    ...trades,
    ...trades,
  ]

  return (
    <div className="relative overflow-hidden bg-[#0c1624] border-b border-[#1a2d45] py-2">
      <motion.div 
        className="flex gap-8 whitespace-nowrap"
        animate={{ x: [0, -1000] }}
        transition={{ 
          duration: 30, 
          repeat: Infinity, 
          ease: "linear" 
        }}
      >
        {tickerItems.map((item, index) => (
          <div key={index} className="flex items-center gap-2 text-xs">
            <span className="text-gray-500 font-mono">{item.time}</span>
            <span className="font-bold text-white">{item.symbol}</span>
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${
              item.action === 'BUY' ? 'bg-[#00ff9f]/20 text-[#00ff9f]' :
              item.action === 'SELL' ? 'bg-[#ff4560]/20 text-[#ff4560]' :
              'bg-[#ffb800]/20 text-[#ffb800]'
            }`}>
              {item.action}
            </span>
            <span className="text-gray-400">${item.price.toLocaleString()}</span>
            <span className="text-gray-600">|</span>
          </div>
        ))}
      </motion.div>
      
      <div className="absolute top-0 left-0 w-20 h-full bg-gradient-to-r from-[#0c1624] to-transparent z-10" />
      <div className="absolute top-0 right-0 w-20 h-full bg-gradient-to-l from-[#0c1624] to-transparent z-10" />
    </div>
  )
}