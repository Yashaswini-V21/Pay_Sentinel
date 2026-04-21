import { RootRoute, Router } from '@tanstack/react-router'
import Root from './routes/__root'
import Landing from './routes/landing-premium'
import Dashboard from './routes/dashboard'
import Settings from './routes/settings'
import NotFound from './routes/404'

const rootRoute = new RootRoute({
  component: Root,
  notFoundComponent: NotFound,
})

const indexRoute = new RootRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: Landing,
})

const dashboardRoute = new RootRoute({
  getParentRoute: () => rootRoute,
  path: '/dashboard',
  component: Dashboard,
})

const settingsRoute = new RootRoute({
  getParentRoute: () => rootRoute,
  path: '/settings',
  component: Settings,
})

const routeTree = rootRoute.addChildren([
  indexRoute,
  dashboardRoute,
  settingsRoute,
])

export const router = new Router({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
