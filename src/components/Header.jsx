import React from 'react'
import { motion } from 'framer-motion'

export default function Header({ connectionStatus }) {
  return (
    <header className="border-b border-[#1a2d45] px-6 py-4 flex items-center justify-between bg-[#060b14]/80 backdrop-blur-sm">
      <div className="flex items-center gap-4">
        <div className="relative">
          <svg viewBox="0 0 100 100" className="w-12 h-12 drop-shadow-lg">
            <defs>
              <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#1e3a5f"/>
                <stop offset="100%" stopColor="#0f172a"/>
              </linearGradient>
              <linearGradient id="tealGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#0d9488"/>
                <stop offset="100%" stopColor="#0891b2"/>
              </linearGradient>
            </defs>
            <path d="M50 5 L90 20 L90 55 Q90 85 50 95 Q10 85 10 55 L10 20 Z" fill="url(#shieldGrad)" stroke="#00e5ff" strokeWidth="2"/>
            <g clipPath="url(#clipLeft)">
              <rect x="10" y="20" width="40" height="65" fill="url(#shieldGrad)"/>
              <rect x="18" y="55" width="6" height="20" fill="#22c55e" rx="1"/>
              <rect x="28" y="45" width="6" height="15" fill="#22c55e" rx="1"/>
              <rect x="38" y="35" width="6" height="25" fill="#22c55e" rx="1"/>
            </g>
            <g clipPath="url(#clipRight)">
              <rect x="50" y="20" width="40" height="65" fill="url(#tealGrad)"/>
              <circle cx="60" cy="40" r="3" fill="white"/>
              <circle cx="75" cy="45" r="2" fill="white"/>
              <circle cx="68" cy="55" r="3" fill="white"/>
              <circle cx="80" cy="60" r="2" fill="white"/>
              <circle cx="58" cy="65" r="2" fill="white"/>
              <circle cx="72" cy="70" r="3" fill="white"/>
              <line x1="60" y1="40" x2="68" y2="55" stroke="white" strokeWidth="1.5"/>
              <line x1="68" y1="55" x2="75" y2="45" stroke="white" strokeWidth="1.5"/>
              <line x1="68" y1="55" x2="80" y2="60" stroke="white" strokeWidth="1.5"/>
              <line x1="68" y1="55" x2="72" y2="70" stroke="white" strokeWidth="1.5"/>
            </g>
            <path d="M25 75 L45 45 L55 55 L75 25" stroke="white" strokeWidth="3" fill="none" strokeLinecap="round"/>
          </svg>
          <motion.div 
            className="absolute -bottom-1 -right-1 w-3 h-3 rounded-full bg-green-500"
            animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        </div>
        
        <div>
          <h1 className="text-2xl font-bold">
            <span className="text-[#1a365d]">Insider</span>
            <span className="text-[#22c55e]">Edge</span>
          </h1>
          <p className="text-xs text-gray-500 tracking-widest">AI CRYPTO TRADING</p>
        </div>
      </div>
      
      <div className="flex items-center gap-6">
        <motion.div 
          className="flex items-center gap-2 px-3 py-1 rounded-full border border-[#1a2d45]"
          animate={{ boxShadow: ['0 0 5px #00e5ff', '0 0 15px #00e5ff', '0 0 5px #00e5ff'] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <motion.div 
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: connectionStatus === 'connected' ? '#00ff9f' : '#ff4560' }}
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
          <span className="text-xs font-mono text-gray-400">
            {connectionStatus === 'connected' ? '● LIVE' : '○ OFFLINE'}
          </span>
        </motion.div>
        
        <div className="text-right">
          <div className="text-xs text-gray-500">AGENT ID</div>
          <div className="text-lg font-bold text-[#00e5ff]">33</div>
        </div>
        
        <motion.div 
          className="w-16 h-16 relative"
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          <svg viewBox="0 0 100 100" className="w-full h-full">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#1a2d45" strokeWidth="4"/>
            <motion.circle 
              cx="50" cy="50" r="45" fill="none" stroke="#00e5ff" strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray="283"
              strokeDashoffset="70"
              animate={{ strokeDashoffset: [70, 40, 70] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              transform="rotate(-90 50 50)"
            />
            <text x="50" y="55" textAnchor="middle" fill="#00e5ff" fontSize="20" fontWeight="bold">AI</text>
          </svg>
        </motion.div>
      </div>
    </header>
  )
}