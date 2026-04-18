import React from 'react'
import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

export default function SessionStats() {
  const data = [
    { name: 'BUY', value: 24, color: '#00ff9f' },
    { name: 'SELL', value: 57, color: '#ff4560' },
    { name: 'HOLD', value: 57, color: '#ffb800' },
  ]

  return (
    <div className="rounded-xl bg-[#0c1624] border border-[#1a2d45] overflow-hidden">
      <div className="p-4 border-b border-[#1a2d45]">
        <h3 className="font-bold text-white flex items-center gap-2">
          <motion.span 
            className="w-2 h-2 rounded-full bg-[#00e5ff]"
            animate={{ scale: [1, 1.2, 1], opacity: [1, 0.5, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
          SESSION STATISTICS
        </h3>
      </div>
      
      <div className="p-6 flex items-center justify-around">
        <div className="text-center">
          <div className="text-3xl font-bold text-[#00e5ff]">138</div>
          <div className="text-xs text-gray-500 mt-1">TOTAL DECISIONS</div>
        </div>
        
        <div className="relative w-32 h-32">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={60}
                paddingAngle={2}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.color}
                    stroke="none"
                  />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-lg font-bold text-white">100%</div>
              <div className="text-xs text-gray-500">Complete</div>
            </div>
          </div>
        </div>
        
        <div className="space-y-3">
          {data.map((item, index) => (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-3"
            >
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
              <div className="text-sm">
                <span className="text-gray-400">{item.name}</span>
                <span className="ml-2 font-bold text-white">{item.value}</span>
                <span className="ml-1 text-xs text-gray-500">
                  ({((item.value / 138) * 100).toFixed(0)}%)
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}