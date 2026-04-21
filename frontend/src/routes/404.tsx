import { Link } from '@tanstack/react-router'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-primary mb-4">404</h1>
        <p className="text-xl text-muted-foreground mb-8">Page not found</p>
        <Link to="/" className="btn-primary">
          Back to home
        </Link>
      </div>
    </div>
  )
}
