import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Header from './components/Header'
import PriceTicker from './components/PriceTicker'
import StatsPanel from './components/StatsPanel'
import PositionsPanel from './components/PositionsPanel'
import RiskMetrics from './components/RiskMetrics'
import MarketAnalysis from './components/MarketAnalysis'
import TickerTape from './components/TickerTape'
import ParticleField from './components/ParticleField'
import SessionStats from './components/SessionStats'

const mockPrices = {
  BTC: { price: 74123.45, change: 2.35, sparkline: [72000, 72500, 73100, 72800, 73500, 74200, 74123] },
  ETH: { price: 2218.67, change: -0.87, sparkline: [2250, 2230, 2245, 2220, 2210, 2225, 2218] },
  SOL: { price: 84.52, change: 5.16, sparkline: [78, 80, 82, 81, 83, 85, 84] }
}

const mockPositions = [
  { symbol: 'BTC', side: 'LONG', entry: 71245, current: 74415, pnl: 4.44 },
  { symbol: 'ETH', side: 'LONG', entry: 2180, current: 2218.67, pnl: 1.77 }
]

const mockTrades = [
  { time: '14:32:15', symbol: 'BTC', action: 'BUY', price: 74123, conf: 70 },
  { time: '14:31:42', symbol: 'ETH', action: 'HOLD', price: 2218, conf: 50 },
  { time: '14:30:18', symbol: 'SOL', action: 'BUY', price: 83.50, conf: 65 },
  { time: '14:29:55', symbol: 'BTC', action: 'SELL', price: 73950, conf: 95 },
  { time: '14:28:22', symbol: 'ETH', action: 'BUY', price: 2205, conf: 70 },
]

function App() {
  const [prices, setPrices] = useState(mockPrices)
  const [dailyPnl, setDailyPnl] = useState(2.35)
  const [decisions, setDecisions] = useState(138)
  const [tradesToday, setTradesToday] = useState(12)
  const [connectionStatus, setConnectionStatus] = useState('connected')

  useEffect(() => {
    const interval = setInterval(() => {
      setPrices(prev => ({
        BTC: { ...prev.BTC, price: prev.BTC.price + (Math.random() - 0.5) * 100, sparkline: [...prev.BTC.sparkline.slice(1), prev.BTC.price + (Math.random() - 0.5) * 100] },
        ETH: { ...prev.ETH, price: prev.ETH.price + (Math.random() - 0.5) * 10, sparkline: [...prev.ETH.sparkline.slice(1), prev.ETH.price + (Math.random() - 0.5) * 10] },
        SOL: { ...prev.SOL, price: prev.SOL.price + (Math.random() - 0.5) * 0.5, sparkline: [...prev.SOL.sparkline.slice(1), prev.SOL.price + (Math.random() - 0.5) * 0.5] }
      }))
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-[#060b14] text-white overflow-hidden relative">
      <ParticleField pnl={dailyPnl} />
      
      <div className="relative z-10">
        <TickerTape trades={mockTrades} />
        
        <Header connectionStatus={connectionStatus} />
        
        <main className="p-6 space-y-6">
          <PriceTicker prices={prices} />
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <StatsPanel dailyPnl={dailyPnl} decisions={decisions} tradesToday={tradesToday} maxTrades={50} />
              <MarketAnalysis prices={prices} />
            </div>
            
            <div className="space-y-6">
              <PositionsPanel positions={mockPositions} />
              <RiskMetrics />
            </div>
          </div>
          
          <SessionStats />
        </main>
        
        <footer className="border-t border-[#1a2d45] p-4 text-center text-sm text-gray-500">
          <span className="text-[#00e5ff]">INSIDEREDGE</span> v2.0 | AI Crypto Trading | Team Dhurandhar | lablab.ai × Kraken
        </footer>
      </div>
    </div>
  )
}

export default App