interface BilingualTextProps {
  en: string
  kn: string
  className?: string
  block?: boolean
}

export function BilingualText({ en, kn, className = '', block = false }: BilingualTextProps) {
  const containerClass = block ? 'flex flex-col gap-1' : 'inline'
  
  return (
    <div className={`${containerClass} ${className}`}>
      <span>{en}</span>
      <span className="font-kannada text-sm opacity-80 block">{kn}</span>
    </div>
  )
}
