import React from 'react'
import { QueryClient, QueryClientProvider, MutationCache, QueryCache } from '@tanstack/react-query'

// Global error handler for React Query
const handleError = (error: unknown) => {
  let message = 'An unexpected error occurred'
  
  if (error instanceof Error) {
    message = error.message
  } else if (typeof error === 'string') {
    message = error
  } else if (error && typeof error === 'object' && 'message' in error) {
    message = String(error.message)
  }

  // Show user-friendly error messages
  if (message.includes('401') || message.includes('Unauthorized')) {
    console.error('Authentication required')
    // Redirect to login page
    window.location.href = '/login'
    return
  }

  if (message.includes('403') || message.includes('Forbidden')) {
    console.error('Permission denied')
    return
  }

  if (message.includes('404') || message.includes('Not Found')) {
    console.error('Resource not found')
    return
  }

  if (message.includes('500') || message.includes('Internal Server Error')) {
    console.error('Server error occurred')
    return
  }

  if (message.includes('network') || message.includes('fetch')) {
    console.error('Network connection issue')
    return
  }

  // Log error for debugging
  console.error('React Query Error:', error)
}

// Create a client with global error handling
const createQueryClient = () => {
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
      },
    },
    queryCache: new QueryCache({
      onError: handleError,
    }),
    mutationCache: new MutationCache({
      onError: handleError,
    }),
  })
}

interface QueryProviderProps {
  children: React.ReactNode
}

export const QueryProvider: React.FC<QueryProviderProps> = ({ children }) => {
  const [queryClient] = React.useState(() => createQueryClient())

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

export default QueryProvider