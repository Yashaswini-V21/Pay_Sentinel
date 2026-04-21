import { Outlet } from '@tanstack/react-router'
import { SiteHeader } from '../components/SiteHeader'
import { SiteFooter } from '../components/SiteFooter'
import { SplashScreen } from '../components/SplashScreen'

export default function Root() {
  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <SplashScreen />
      <SiteHeader />
      <main className="flex-1 w-full relative z-0">
        <Outlet />
      </main>
      <SiteFooter />
    </div>
  )
}
