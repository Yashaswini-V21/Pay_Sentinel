import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react'

interface RiskBadgeProps {
  variant: 'safe' | 'warn' | 'fraud'
  label: string
  value?: string | number
}

export function RiskBadge({ variant, label, value }: RiskBadgeProps) {
  const baseClasses = 'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold'

  const variantClasses = {
    safe: 'badge-safe',
    warn: 'badge-warn',
    fraud: 'badge-fraud',
  }

  const iconProps = { size: 14 }

  return (
    <div className={`${baseClasses} ${variantClasses[variant]}`}>
      {variant === 'safe' && <CheckCircle {...iconProps} />}
      {variant === 'warn' && <AlertTriangle {...iconProps} />}
      {variant === 'fraud' && <AlertCircle {...iconProps} />}
      <span>{label}</span>
      {value && <span className="font-mono ml-1">{value}</span>}
    </div>
  )
}
