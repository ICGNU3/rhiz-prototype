import React from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
  errorInfo?: React.ErrorInfo
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<ErrorFallbackProps>
}

interface ErrorFallbackProps {
  error?: Error
  resetError: () => void
  errorInfo?: React.ErrorInfo
}

const DefaultErrorFallback: React.FC<ErrorFallbackProps> = ({ 
  error, 
  resetError,
  errorInfo 
}) => {
  const isDevelopment = process.env.NODE_ENV === 'development'

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Glass card with error styling */}
        <div className="relative backdrop-blur-xl bg-white/5 border border-red-500/20 rounded-2xl p-8 shadow-2xl">
          {/* Error icon */}
          <div className="flex justify-center mb-6">
            <div className="p-4 rounded-full bg-red-500/10 border border-red-500/20">
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
          </div>

          {/* Error message */}
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold text-white mb-2">
              Something went wrong
            </h1>
            <p className="text-gray-300 text-sm leading-relaxed">
              We apologize for the inconvenience. An unexpected error occurred 
              while loading this page.
            </p>
          </div>

          {/* Development error details */}
          {isDevelopment && error && (
            <div className="mb-6 p-4 bg-red-900/20 border border-red-500/30 rounded-lg">
              <h3 className="text-red-400 font-semibold text-sm mb-2">
                Error Details (Development)
              </h3>
              <p className="text-red-300 text-xs font-mono break-all">
                {error.message}
              </p>
              {errorInfo?.componentStack && (
                <details className="mt-2">
                  <summary className="text-red-400 text-xs cursor-pointer hover:text-red-300">
                    Component Stack
                  </summary>
                  <pre className="text-red-300 text-xs mt-1 overflow-auto max-h-32">
                    {errorInfo.componentStack}
                  </pre>
                </details>
              )}
            </div>
          )}

          {/* Action buttons */}
          <div className="flex flex-col gap-3">
            <button
              onClick={resetError}
              className="flex items-center justify-center gap-2 w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900"
            >
              <RefreshCw className="w-4 h-4" />
              Try Again
            </button>
            
            <button
              onClick={() => window.location.href = '/'}
              className="flex items-center justify-center gap-2 w-full px-4 py-3 bg-white/10 hover:bg-white/20 text-white font-medium rounded-lg border border-white/20 transition-colors focus:outline-none focus:ring-2 focus:ring-white/50 focus:ring-offset-2 focus:ring-offset-gray-900"
            >
              <Home className="w-4 h-4" />
              Go Home
            </button>
          </div>

          {/* Support message */}
          <div className="mt-6 pt-4 border-t border-white/10 text-center">
            <p className="text-gray-400 text-xs">
              If this problem persists, please contact support
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    // Update state with error info for development
    this.setState({
      error,
      errorInfo
    })

    // Log to external error reporting service in production
    if (process.env.NODE_ENV === 'production') {
      // TODO: Integrate with error reporting service (e.g., Sentry)
      console.error('Production error caught by ErrorBoundary:', {
        error: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack
      })
    }
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback
      return (
        <FallbackComponent
          error={this.state.error}
          resetError={this.resetError}
          errorInfo={this.state.errorInfo}
        />
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
export type { ErrorBoundaryProps, ErrorFallbackProps }