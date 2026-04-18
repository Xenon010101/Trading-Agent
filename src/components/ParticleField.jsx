import React, { useEffect, useState, useRef } from 'react'
import { motion } from 'framer-motion'

export default function ParticleField({ pnl = 0 }) {
  const canvasRef = useRef(null)
  const [particles, setParticles] = useState([])
  
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    
    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン'
    const charArray = chars.split('')
    
    const newParticles = []
    const columns = Math.floor(canvas.width / 20)
    
    for (let i = 0; i < columns; i++) {
      newParticles.push({
        x: i * 20,
        y: Math.random() * canvas.height,
        speed: 1 + Math.random() * 3,
        char: charArray[Math.floor(Math.random() * charArray.length)],
        opacity: Math.random() * 0.5 + 0.1
      })
    }
    
    setParticles(newParticles)
    
    let animationId
    const animate = () => {
      ctx.fillStyle = 'rgba(6, 11, 20, 0.05)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      
      setParticles(prev => prev.map(p => ({
        ...p,
        y: p.y > canvas.height ? 0 : p.y + p.speed,
        char: Math.random() > 0.95 ? charArray[Math.floor(Math.random() * charArray.length)] : p.char,
        opacity: pnl >= 0 ? Math.min(p.opacity + 0.01, 0.6) : p.opacity
      })))
      
      setParticles(current => {
        current.forEach(p => {
          ctx.font = '14px monospace'
          ctx.fillStyle = pnl >= 0 
            ? `rgba(0, 255, 159, ${p.opacity})`
            : `rgba(255, 69, 96, ${p.opacity})`
          ctx.fillText(p.char, p.x, p.y)
        })
        return current
      })
      
      animationId = requestAnimationFrame(animate)
    }
    
    animate()
    
    const handleResize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    
    window.addEventListener('resize', handleResize)
    
    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('resize', handleResize)
    }
  }, [pnl])
  
  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ opacity: 0.3 }}
    />
  )
}