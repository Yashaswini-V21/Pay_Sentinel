import { motion } from 'framer-motion'

/**
 * Animated Fraud Detection Shield Graphic
 */
export function FraudShieldGraphic() {
  return (
    <motion.svg
      viewBox="0 0 200 200"
      className="w-full h-full"
      animate={{ y: [0, -20, 0] }}
      transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
    >
      {/* Shield background glow */}
      <defs>
        <filter id="shield-glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="oklch(0.62 0.22 270)" />
          <stop offset="100%" stopColor="oklch(0.62 0.22 270 / 0.5)" />
        </linearGradient>
      </defs>

      {/* Shield outline with glow */}
      <motion.g filter="url(#shield-glow)">
        <path
          d="M 100 20 L 160 50 L 160 110 Q 100 160 100 160 Q 40 160 40 110 L 40 50 Z"
          fill="url(#shieldGrad)"
          stroke="oklch(0.62 0.22 270)"
          strokeWidth="2"
          opacity="0.8"
        />
      </motion.g>

      {/* Checkmark inside shield */}
      <motion.g
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.4, duration: 0.6, type: 'spring' }}
      >
        <path
          d="M 75 100 L 90 115 L 125 75"
          stroke="oklch(0.72 0.18 155)"
          strokeWidth="4"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </motion.g>

      {/* Animated rings */}
      {[1, 2, 3].map((i) => (
        <motion.circle
          key={i}
          cx="100"
          cy="100"
          r={40 + i * 20}
          fill="none"
          stroke="oklch(0.62 0.22 270)"
          strokeWidth="1"
          opacity={0.3}
          animate={{ r: [40 + i * 20, 60 + i * 20] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
        />
      ))}
    </motion.svg>
  )
}

/**
 * Real-time Transaction Flow Graphic
 */
export function TransactionFlowGraphic() {
  const packets = Array.from({ length: 5 }, (_, i) => i)

  return (
    <motion.svg
      viewBox="0 0 300 200"
      className="w-full h-full"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.2 }}
    >
      <defs>
        <linearGradient id="flowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="oklch(0.62 0.22 270)" />
          <stop offset="100%" stopColor="oklch(0.72 0.18 155)" />
        </linearGradient>
      </defs>

      {/* Left device */}
      <rect x="20" y="60" width="50" height="80" rx="4" fill="oklch(0.11 0.015 260)" stroke="oklch(0.72 0.18 155)" strokeWidth="2" />
      <circle cx="45" cy="85" r="3" fill="oklch(0.72 0.18 155)" />
      <line x1="30" y1="95" x2="60" y2="95" stroke="oklch(0.72 0.18 155)" strokeWidth="1" opacity="0.6" />
      <line x1="30" y1="105" x2="60" y2="105" stroke="oklch(0.72 0.18 155)" strokeWidth="1" opacity="0.6" />

      {/* Transaction flow lines */}
      {packets.map((i) => (
        <motion.g key={i}>
          {/* Packet circle flowing */}
          <motion.circle
            cx="20"
            cy="100"
            r="4"
            fill="oklch(0.72 0.18 155)"
            animate={{ x: [0, 220] }}
            transition={{
              duration: 2,
              delay: i * 0.2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          {/* Trail effect */}
          <motion.line
            x1="20"
            y1="100"
            x2="220"
            y2="100"
            stroke="url(#flowGrad)"
            strokeWidth="2"
            opacity="0.3"
            strokeDasharray="4 4"
            animate={{ x: [0, 220] }}
            transition={{
              duration: 2,
              delay: i * 0.2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        </motion.g>
      ))}

      {/* Center analyze icon */}
      <motion.g
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
      >
        <circle cx="150" cy="100" r="15" fill="oklch(0.11 0.015 260)" stroke="oklch(0.62 0.22 270)" strokeWidth="2" />
        <line x1="145" y1="95" x2="155" y2="105" stroke="oklch(0.62 0.22 270)" strokeWidth="2" />
        <line x1="155" y1="95" x2="145" y2="105" stroke="oklch(0.62 0.22 270)" strokeWidth="2" />
      </motion.g>

      {/* Right result */}
      <rect x="230" y="60" width="50" height="80" rx="4" fill="oklch(0.11 0.015 260)" stroke="oklch(0.62 0.22 270)" strokeWidth="2" />
      <circle cx="255" cy="85" r="3" fill="oklch(0.62 0.22 270)" />
      <line x1="240" y1="95" x2="270" y2="95" stroke="oklch(0.62 0.22 270)" strokeWidth="1" opacity="0.6" />
      <line x1="240" y1="105" x2="270" y2="105" stroke="oklch(0.62 0.22 270)" strokeWidth="1" opacity="0.6" />

      {/* Labels */}
      <text x="45" y="165" textAnchor="middle" className="text-xs fill-muted-foreground">
        UPI
      </text>
      <text x="150" y="165" textAnchor="middle" className="text-xs fill-primary">
        AI Check
      </text>
      <text x="255" y="165" textAnchor="middle" className="text-xs fill-primary">
        Result
      </text>
    </motion.svg>
  )
}

/**
 * Risk Meter Gauge Graphic
 */
export function RiskMeterGraphic({ value = 23 }: { value?: number }) {
  const angle = (value / 100) * 180 - 90

  return (
    <motion.svg viewBox="0 0 200 140" className="w-full h-full">
      <defs>
        <linearGradient id="meterGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="oklch(0.72 0.18 155)" />
          <stop offset="50%" stopColor="oklch(0.78 0.25 80)" />
          <stop offset="100%" stopColor="oklch(0.62 0.27 30)" />
        </linearGradient>
      </defs>

      {/* Gauge background */}
      <circle cx="100" cy="100" r="80" fill="none" stroke="oklch(0.22 0.015 260 / 50%)" strokeWidth="8" />

      {/* Gauge gradient arc */}
      <circle cx="100" cy="100" r="80" fill="none" stroke="url(#meterGrad)" strokeWidth="8" strokeDasharray="251 251" strokeDashoffset={251 - (value / 100) * 251} opacity="0.7" />

      {/* Needle */}
      <motion.g animate={{ rotate: angle }} transition={{ duration: 0.8, type: 'spring' }}>
        <line x1="100" y1="100" x2="100" y2="30" stroke="oklch(0.97 0.01 250)" strokeWidth="3" strokeLinecap="round" />
      </motion.g>

      {/* Center dot */}
      <circle cx="100" cy="100" r="6" fill="oklch(0.97 0.01 250)" />

      {/* Value text */}
      <motion.text
        x="100"
        y="125"
        textAnchor="middle"
        className="text-lg font-bold fill-primary"
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        {value}%
      </motion.text>

      {/* Labels */}
      <text x="30" y="110" className="text-xs fill-muted-foreground" textAnchor="middle">
        Safe
      </text>
      <text x="170" y="110" className="text-xs fill-muted-foreground" textAnchor="middle">
        High Risk
      </text>
    </motion.svg>
  )
}

/**
 * Animated Data Points Graphic
 */
export function DataPointsGraphic() {
  const points = Array.from({ length: 12 }, (_, i) => ({
    id: i,
    x: 30 + Math.cos((i / 12) * Math.PI * 2) * 60,
    y: 60 + Math.sin((i / 12) * Math.PI * 2) * 40,
  }))

  return (
    <motion.svg viewBox="0 0 200 160" className="w-full h-full">
      {/* Center glow */}
      <circle cx="100" cy="80" r="50" fill="oklch(0.62 0.22 270 / 0.1)" />

      {/* Connecting lines */}
      {points.map((p, i) => (
        <motion.line
          key={`line-${i}`}
          x1="100"
          y1="80"
          x2={p.x}
          y2={p.y}
          stroke="oklch(0.62 0.22 270)"
          strokeWidth="1"
          opacity="0.3"
          animate={{ opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 2, delay: i * 0.1, repeat: Infinity }}
        />
      ))}

      {/* Animated data points */}
      {points.map((p, i) => (
        <motion.g key={`point-${i}`}>
          <motion.circle
            cx={p.x}
            cy={p.y}
            r="3"
            fill="oklch(0.72 0.18 155)"
            animate={{ r: [3, 5, 3], opacity: [0.6, 1, 0.6] }}
            transition={{ duration: 1.5, delay: i * 0.1, repeat: Infinity }}
          />
          <motion.circle
            cx={p.x}
            cy={p.y}
            r="3"
            fill="none"
            stroke="oklch(0.72 0.18 155)"
            strokeWidth="1"
            animate={{ r: [3, 8] }}
            transition={{ duration: 1.5, delay: i * 0.1, repeat: Infinity }}
          />
        </motion.g>
      ))}

      {/* Center pulse */}
      <motion.circle
        cx="100"
        cy="80"
        r="3"
        fill="oklch(0.62 0.22 270)"
        animate={{ r: [3, 8], opacity: [1, 0] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      />
    </motion.svg>
  )
}

/**
 * Merchant Shield Graphic
 */
export function MerchantShieldGraphic() {
  return (
    <motion.svg viewBox="0 0 200 200" className="w-full h-full">
      {/* Outer ring */}
      <motion.circle
        cx="100"
        cy="100"
        r="90"
        fill="none"
        stroke="oklch(0.62 0.22 270)"
        strokeWidth="2"
        opacity="0.3"
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
      />

      {/* Shield */}
      <motion.path
        d="M 100 40 L 150 70 L 150 120 Q 100 160 100 160 Q 50 160 50 120 L 50 70 Z"
        fill="oklch(0.62 0.22 270 / 0.1)"
        stroke="oklch(0.62 0.22 270)"
        strokeWidth="2"
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Merchant icon (building) */}
      <g>
        <rect x="85" y="75" width="30" height="45" fill="oklch(0.72 0.18 155)" />
        <circle cx="92" cy="90" r="3" fill="oklch(0.08 0.012 260)" />
        <circle cx="108" cy="90" r="3" fill="oklch(0.08 0.012 260)" />
        <circle cx="92" cy="108" r="3" fill="oklch(0.08 0.012 260)" />
        <circle cx="108" cy="108" r="3" fill="oklch(0.08 0.012 260)" />
        <polygon points="85,75 100,60 115,75" fill="oklch(0.72 0.18 155)" />
      </g>

      {/* Lock badge */}
      <motion.g
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
      >
        <circle cx="140" cy="50" r="18" fill="oklch(0.72 0.18 155)" />
        <g transform="translate(140, 50)">
          <rect x="-6" y="-2" width="12" height="8" rx="1" fill="oklch(0.08 0.012 260)" />
          <path d="M -8 4 L 8 4 L 8 10 L -8 10 Z" fill="oklch(0.08 0.012 260)" />
          <circle cx="0" cy="7" r="1.5" fill="oklch(0.72 0.18 155)" />
        </g>
      </motion.g>
    </motion.svg>
  )
}
