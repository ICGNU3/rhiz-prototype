import React from 'react'
import { Loader2 } from 'lucide-react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'default' | 'overlay' | 'inline' | 'card'
  text?: string
  className?: string
  children?: React.ReactNode
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12'
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  variant = 'default',
  text,
  className = '',
  children
}) => {
  const spinnerClasses = `${sizeClasses[size]} animate-spin text-blue-400`

  // Inline spinner for buttons and small spaces
  if (variant === 'inline') {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Loader2 className={spinnerClasses} />
        {text && <span className="text-gray-300 text-sm">{text}</span>}
        {children}
      </div>
    )
  }

  // Card-style loading state
  if (variant === 'card') {
    return (
      <div className={`backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 ${className}`}>
        <div className="flex flex-col items-center justify-center space-y-4">
          <Loader2 className={`${sizeClasses.lg} animate-spin text-blue-400`} />
          <div className="text-center">
            <p className="text-white font-medium">
              {text || 'Loading...'}
            </p>
            <p className="text-gray-400 text-sm mt-1">
              Please wait while we fetch your data
            </p>
          </div>
        </div>
        {children}
      </div>
    )
  }

  // Full screen overlay
  if (variant === 'overlay') {
    return (
      <div className={`fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 ${className}`}>
        <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-8 max-w-sm mx-4">
          <div className="flex flex-col items-center justify-center space-y-4">
            <Loader2 className={`${sizeClasses.xl} animate-spin text-blue-400`} />
            <div className="text-center">
              <p className="text-white font-medium text-lg">
                {text || 'Loading...'}
              </p>
              <p className="text-gray-300 text-sm mt-2">
                This may take a few moments
              </p>
            </div>
          </div>
          {children}
        </div>
      </div>
    )
  }

  // Default centered spinner
  return (
    <div className={`flex flex-col items-center justify-center space-y-3 p-8 ${className}`}>
      <Loader2 className={spinnerClasses} />
      {text && (
        <p className="text-gray-300 text-sm font-medium">
          {text}
        </p>
      )}
      {children}
    </div>
  )
}

// Skeleton loading components for specific UI elements
export const LoadingSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`animate-pulse bg-white/10 rounded-lg ${className}`} />
)

export const LoadingCard: React.FC<{ children?: React.ReactNode }> = ({ children }) => (
  <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6 animate-pulse">
    <div className="space-y-4">
      <div className="h-4 bg-white/10 rounded w-3/4"></div>
      <div className="h-3 bg-white/10 rounded w-1/2"></div>
      <div className="h-8 bg-white/10 rounded w-full"></div>
    </div>
    {children}
  </div>
)

export const LoadingTable: React.FC<{ rows?: number }> = ({ rows = 3 }) => (
  <div className="space-y-3">
    {Array.from({ length: rows }).map((_, index) => (
      <div key={index} className="flex space-x-4 animate-pulse">
        <div className="h-10 bg-white/10 rounded w-12"></div>
        <div className="flex-1 space-y-2 py-1">
          <div className="h-4 bg-white/10 rounded w-3/4"></div>
          <div className="h-3 bg-white/10 rounded w-1/2"></div>
        </div>
        <div className="h-10 bg-white/10 rounded w-20"></div>
      </div>
    ))}
  </div>
)

export const LoadingStats: React.FC = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    {Array.from({ length: 4 }).map((_, index) => (
      <div key={index} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6 animate-pulse">
        <div className="space-y-3">
          <div className="h-4 bg-white/10 rounded w-1/2"></div>
          <div className="h-8 bg-white/10 rounded w-3/4"></div>
          <div className="h-3 bg-white/10 rounded w-full"></div>
        </div>
      </div>
    ))}
  </div>
)

// Hook for managing loading states
export const useLoadingState = (initialState = false) => {
  const [isLoading, setIsLoading] = React.useState(initialState)
  
  const startLoading = React.useCallback(() => setIsLoading(true), [])
  const stopLoading = React.useCallback(() => setIsLoading(false), [])
  const toggleLoading = React.useCallback(() => setIsLoading(prev => !prev), [])
  
  return {
    isLoading,
    startLoading,
    stopLoading,
    toggleLoading,
    setIsLoading
  }
}

export default LoadingSpinner