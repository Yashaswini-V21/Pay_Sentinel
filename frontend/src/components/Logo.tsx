export function Logo({ className = "w-10 h-10" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 200 60"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Shield */}
      <path
        d="M30 5 L5 12 V28 C5 40 15 48 30 52 C45 48 55 40 55 28 V12 L30 5Z"
        className="stroke-primary"
        strokeWidth="2"
        fill="none"
      />
      {/* Checkmark */}
      <path
        d="M15 30 L22 37 L40 19"
        className="stroke-accent"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Text */}
      <text
        x="65"
        y="38"
        className="fill-foreground"
        fontSize="18"
        fontFamily="Space Grotesk"
        fontWeight="700"
      >
        PaySentinel
      </text>
    </svg>
  )
}
