import { TrendingUp, TrendingDown } from 'lucide-react'

interface KpiCardProps {
  title: string
  value: string | number
  unit?: string
  delta?: number
  sparkline?: number[]
}

export function KpiCard({ title, value, unit, delta }: KpiCardProps) {
  const isPositive = delta && delta > 0

  return (
    <div className="glass p-6 rounded-lg border border-border">
      <h3 className="text-sm font-medium text-muted-foreground mb-3">
        {title}
      </h3>
      <div className="flex items-baseline justify-between mb-4">
        <div>
          <p className="text-2xl md:text-3xl font-bold text-foreground">
            {value}
          </p>
          {unit && (
            <p className="text-xs text-muted-foreground mt-1">{unit}</p>
          )}
        </div>
        {delta !== undefined && (
          <div className={`flex items-center gap-1 text-xs font-semibold ${
            isPositive ? 'text-destructive' : 'text-accent'
          }`}>
            {isPositive ? (
              <TrendingUp size={14} />
            ) : (
              <TrendingDown size={14} />
            )}
            {Math.abs(delta)}%
          </div>
        )}
      </div>
      {/* Simple sparkline placeholder */}
      <div className="h-8 bg-card/50 rounded flex items-end gap-1 px-2 opacity-40">
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className="flex-1 bg-primary rounded-sm"
            style={{ height: `${Math.random() * 100}%` }}
          />
        ))}
      </div>
    </div>
  )
}
