/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'neon-cyan': '#00e5ff',
        'neon-green': '#00ff9f',
        'neon-magenta': '#ff00ff',
        'neon-blue': '#0099ff',
        'cyber-dark': '#060b14',
        'cyber-surface': '#0c1624',
        'cyber-border': '#1a2d45',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
        'scan': 'scan 8s linear infinite',
        'ticker': 'ticker 30s linear infinite',
        'pulse-border': 'pulseBorder 2s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #00e5ff, 0 0 10px #00e5ff' },
          '100%': { boxShadow: '0 0 20px #00e5ff, 0 0 30px #00e5ff, 0 0 40px #00e5ff' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        ticker: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        pulseBorder: {
          '0%, 100%': { borderColor: 'rgba(0, 229, 255, 0.3)' },
          '50%': { borderColor: 'rgba(0, 229, 255, 1)' },
        },
      },
    },
  },
  plugins: [],
}