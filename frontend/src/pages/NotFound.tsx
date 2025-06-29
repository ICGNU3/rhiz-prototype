import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center">
        <div className="glass-card p-8 max-w-md mx-auto">
          <div className="mb-8">
            <svg className="w-24 h-24 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.463.644-6.31 1.76C5.966 15.621 6 14.819 6 14H4a9 9 0 0018 0h-2c0 .819.034 1.621.31 2.76" />
            </svg>
            <h1 className="text-6xl font-bold gradient-text mb-4">404</h1>
            <h2 className="text-2xl font-semibold text-white mb-2">Page Not Found</h2>
            <p className="text-gray-300 mb-6">
              The page you're looking for doesn't exist or has been moved.
            </p>
          </div>
          
          <div className="space-y-4">
            <Link 
              to="/" 
              className="block w-full glass-button text-center"
            >
              Go Home
            </Link>
            <button 
              onClick={() => window.history.back()}
              className="block w-full glass-button text-center"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}