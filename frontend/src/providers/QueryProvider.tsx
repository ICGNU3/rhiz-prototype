import React from 'react'
import { QueryClient, QueryClientProvider, MutationCache, QueryCache } from '@tanstack/react-query'
import { ToastProvider, useToast } from '../components/Toast'

// Global error handler for React Query (will be used inside ToastProvider)
const createErrorHandler = (toast?: ReturnType<typeof useToast>) => (error: unknown) => {
  let message = 'An unexpected error occurred'
  
  if (error instanceof Error) {
    message = error.message
  } else if (typeof error === 'string') {
    message = error
  } else if (error && typeof error === 'object' && 'message' in error) {
    message = String(error.message)
  }

  // Handle authentication errors
  if (message.includes('401') || message.includes('Unauthorized')) {
    toast?.error('Session expired', 'Please log in again to continue')
    setTimeout(() => {
      window.location.href = '/login'
    }, 2000)
    return
  }

  if (message.includes('403') || message.includes('Forbidden')) {
    toast?.error('Access denied', 'You do not have permission to perform this action')
    return
  }

  if (message.includes('404') || message.includes('Not Found')) {
    toast?.error('Not found', 'The requested resource could not be found')
    return
  }

  if (message.includes('500') || message.includes('Internal Server Error')) {
    toast?.error('Server error', 'Please try again in a few moments')
    return
  }

  if (message.includes('network') || message.includes('fetch')) {
    toast?.error('Connection issue', 'Please check your internet connection')
    return
  }

  // Default error message
  toast?.error('Something went wrong', message)
  
  // Log error for debugging
  console.error('React Query Error:', error)
}

// Inner Query Provider component that has access to toast
const QueryProviderInner: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const toast = useToast()
  
  const [queryClient] = React.useState(() => {
    const errorHandler = createErrorHandler(toast)
    
    return new QueryClient({
      defaultOptions: {
        queries: {
          retry: (failureCount, error) => {
            // Don't retry on 4xx errors (client errors)
            if (error instanceof Error && error.message.includes('4')) {
              return false
            }
            // Retry up to 2 times for other errors
            return failureCount < 2
          },
          staleTime: 5 * 60 * 1000, // 5 minutes
          refetchOnWindowFocus: false,
          refetchOnReconnect: true,
        },
        mutations: {
          retry: false, // Don't retry mutations by default
          onSuccess: () => {
            // Show success message for mutations
            toast.success('Action completed successfully')
          },
        },
      },
      queryCache: new QueryCache({
        onError: errorHandler,
      }),
      mutationCache: new MutationCache({
        onError: errorHandler,
      }),
    })
  })

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

interface QueryProviderProps {
  children: React.ReactNode
}

export const QueryProvider: React.FC<QueryProviderProps> = ({ children }) => {
  return (
    <ToastProvider>
      <QueryProviderInner>
        {children}
      </QueryProviderInner>
    </ToastProvider>
  )
}

export default QueryProvider