import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'oklch(0.08 0.012 260)',
        foreground: 'oklch(0.97 0.01 250)',
        card: 'oklch(0.11 0.015 260)',
        'card-foreground': 'oklch(0.97 0.01 250)',
        primary: 'oklch(0.62 0.22 270)',
        'primary-foreground': 'oklch(0.98 0 0)',
        accent: 'oklch(0.72 0.18 155)',
        'accent-foreground': 'oklch(0.08 0.012 260)',
        destructive: 'oklch(0.62 0.24 25)',
        'destructive-foreground': 'oklch(0.98 0 0)',
        warning: 'oklch(0.78 0.17 75)',
        'warning-foreground': 'oklch(0.08 0.012 260)',
        muted: 'oklch(0.15 0.015 260)',
        'muted-foreground': 'oklch(0.65 0.02 260)',
        border: 'oklch(0.22 0.015 260 / 50%)',
        input: 'oklch(0.13 0.015 260)',
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, oklch(0.62 0.22 270), oklch(0.72 0.18 155))',
        'gradient-aurora': 'radial-gradient(ellipse at top, oklch(0.62 0.22 270 / 0.35), transparent 60%)',
      },
      boxShadow: {
        'elevated': '0 24px 70px -20px oklch(0.62 0.22 270 / 0.35)',
        'glow': '0 0 0 1px oklch(0.62 0.22 270 / 0.4), 0 0 40px oklch(0.62 0.22 270 / 0.25)',
      },
    },
  },
  plugins: [],
} satisfies Config
