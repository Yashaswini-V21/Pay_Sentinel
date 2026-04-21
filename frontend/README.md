# PaySentinel Frontend

Production-grade React 19 + Vite SaaS web app for UPI fraud detection with bilingual Kannada support.

## Tech Stack

- **Framework:** React 19 + TanStack Start v1
- **Build:** Vite 7
- **Styling:** Tailwind CSS v4 (oklch tokens, dark SaaS design)
- **Animations:** framer-motion
- **Icons:** lucide-react
- **Charts:** recharts
- **UI:** shadcn/ui inspired components
- **TypeScript:** Strict mode

## Getting Started

### Prerequisites

- Node.js 18+
- npm or pnpm

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Opens at `http://localhost:3000` with Vite HMR.

### Build

```bash
npm run build
```

Outputs to `dist/` ready for production deployment.

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx              # React entry point
│   ├── router.tsx            # TanStack Router setup
│   ├── styles.css            # Design tokens & Tailwind
│   ├── routes/
│   │   ├── __root.tsx        # Root layout
│   │   ├── index.tsx         # Landing page
│   │   ├── dashboard.tsx     # Merchant dashboard
│   │   ├── settings.tsx      # Merchant fingerprint settings
│   │   └── 404.tsx           # 404 page
│   ├── components/
│   │   ├── Logo.tsx
│   │   ├── SiteHeader.tsx    # Sticky header with mobile menu
│   │   ├── SiteFooter.tsx
│   │   ├── SplashScreen.tsx  # 2.4s onboarding splash
│   │   ├── RiskBadge.tsx     # safe/warn/fraud badges
│   │   ├── KpiCard.tsx       # Dashboard KPI cards
│   │   ├── BilingualText.tsx # EN + Kannada text helper
│   │   └── ui/               # Reusable UI primitives
│   │       └── tabs.tsx
│   └── index.html            # HTML entry
├── index.html                # Vite HTML template
├── vite.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

## Design System

### Color Tokens (oklch)

All colors defined in `src/styles.css`:

- `--background`: `oklch(0.08 0.012 260)` — Near-black indigo
- `--primary`: `oklch(0.62 0.22 270)` — Electric indigo (CTAs)
- `--accent`: `oklch(0.72 0.18 155)` — Emerald pulse (safe/live)
- `--destructive`: `oklch(0.62 0.24 25)` — Fraud red
- `--warning`: `oklch(0.78 0.17 75)` — Amber

### Fonts

- **Display/UI:** Space Grotesk 300–800
- **Mono:** JetBrains Mono 300–600
- **Kannada:** Noto Sans Kannada 400–700

All loaded from Google Fonts in `index.html`.

### Utilities

Custom CSS classes for common patterns:

```css
.glass              /* Glassmorphic card with backdrop blur */
.glass-elevated     /* Glass + elevated shadow */
.glow-border        /* Glowing border for highlights */
.pulse-glow         /* Animated glow pulse */
.text-gradient      /* Brand gradient text */
.badge-safe         /* Safe/green badge */
.badge-warn         /* Warning/amber badge */
.badge-fraud        /* Fraud/red badge */
.btn-primary        /* Primary button */
.btn-secondary      /* Secondary button */
.btn-ghost          /* Ghost button */
```

## Features

### Pages

1. **Landing (/)** — Hero, features bento, pricing, FAQ, CTA
2. **Dashboard (/dashboard)** — Live transaction feed, KPIs, anomaly charts, voice alerts
3. **Settings (/settings)** — ML tuning, operating hours, language selection, notifications
4. **404** — Brand-aligned error page

### Components

- **SiteHeader** — Sticky top bar with mobile drawer menu
- **SiteFooter** — 4-column footer with bilingual tagline
- **SplashScreen** — 2.4s onboarding with progress bar & Kannada messages
- **RiskBadge** — Risk level indicators (safe/warn/fraud)
- **KpiCard** — Dashboard KPI with sparkline
- **BilingualText** — English + Kannada text helper
- **Logo** — SVG logo component using current color

### Mobile Responsiveness

- **390px:** Mobile-first design (iPhone SE)
- **768px:** Tablet layout (iPad)
- **1280px:** Desktop layout
- **1536px:** 4K/ultrawide

No horizontal scroll at any breakpoint. Tested with:
- Hidden scrollbars in DevTools
- `overflow: hidden` verification
- Touch-friendly tap targets (48px minimum)

## Accessibility

- **Semantic HTML:** One `<h1>` per page, proper nav/main/footer
- **Focus Rings:** All interactive elements with `focus-visible`
- **ARIA Labels:** Icon buttons, landmark regions
- **Alt Text:** All images with descriptive alt text
- **Motion:** Respects `prefers-reduced-motion` media query
- **Contrast:** WCAG AA compliant colors (okch saturation-aware)

## Performance

- **Lighthouse Score:** Target ≥ 90 (Performance), ≥ 95 (Accessibility), ≥ 95 (SEO)
- **Code Splitting:** Route-based lazy loading via TanStack Start
- **Tree-shaking:** Zero unused imports, terser minification
- **Fonts:** Google Fonts with `font-display: swap`

## Type Safety

- **Strict TypeScript Mode:** No `any` types
- **React 19:** Latest hooks API
- **TanStack Router:** Type-safe routing with path inference

## Development Tips

### Adding New Components

```tsx
// src/components/MyComponent.tsx
export function MyComponent() {
  return <div className="glass p-6 rounded-lg">Hello</div>
}
```

Always use semantic Tailwind tokens (never raw hex):

```tsx
// ✅ Correct
className="bg-primary text-foreground"

// ❌ Wrong
className="bg-[#9d4edd] text-[#f0f0f0]"
```

### Adding New Routes

1. Create file: `src/routes/new-page.tsx`
2. Update `src/router.tsx` to add route
3. Link from navigation: `<Link to="/new-page">`

### Bilingual Content

Always wrap Kannada text in `<span className="font-kannada">`:

```tsx
<BilingualText 
  en="Start free"
  kn="ಉಚಿತ ಪ್ರಾರಂಭ ಮಾಡಿ"
/>
```

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### GitHub Pages

```bash
npm run build
# Push dist/ to gh-pages branch
```

### Docker

```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## Testing

- **ESLint:** No console errors or unused imports
- **TypeScript:** `npm run type-check` (no type errors)
- **Manual:** Lighthouse audit on production build

## Browser Support

- Chrome/Edge: Latest
- Firefox: Latest
- Safari: Latest 2 versions
- Mobile: iOS 13+, Android 12+

## License

MIT — Built for BluePrint 2026 Hackathon
