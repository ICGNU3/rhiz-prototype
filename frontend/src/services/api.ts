// Enhanced API service with comprehensive error handling and React Query integration

import { User, Contact, Goal } from '../types'

export { User, Contact, Goal }

export interface DashboardAnalytics {
  contacts: number
  goals: number
  interactions: number
  ai_suggestions: number
  recent_activity?: {
    contacts_added: number
    goals_completed: number
    messages_sent: number
  }
}

export interface ApiError {
  message: string
  status?: number
  code?: string
}

export interface ApiResponse<T> {
  success: boolean
  data: T | null
  error?: string
}

// Custom error class for API errors
export class ApiRequestError extends Error {
  status: number
  code?: string

  constructor(message: string, status: number, code?: string) {
    super(message)
    this.name = 'ApiRequestError'
    this.status = status
    this.code = code
  }
}

// Enhanced request function with retry logic and comprehensive error handling
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const baseURL = window.location.origin
  const url = `${baseURL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`

  // Default headers
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }

  // Merge headers
  const headers = {
    ...defaultHeaders,
    ...options.headers
  }

  const config: RequestInit = {
    credentials: 'same-origin', // Include cookies for session-based auth
    ...options,
    headers
  }

  const maxRetries = 2
  let lastError: Error

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, config)

      // Handle non-JSON responses (like redirects or HTML error pages)
      const contentType = response.headers.get('content-type')
      if (!contentType?.includes('application/json')) {
        if (response.status === 401) {
          window.location.href = '/login'
          throw new ApiRequestError('Authentication required', 401)
        }
        throw new ApiRequestError(`Unexpected response type: ${contentType}`, response.status)
      }

      // Handle HTTP errors
      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`
        
        try {
          const errorData = await response.json()
          errorMessage = errorData.message || errorData.error || errorMessage
        } catch {
          // If JSON parsing fails, use status-based messages
          switch (response.status) {
            case 401:
              errorMessage = 'Authentication required. Please log in.'
              break
            case 403:
              errorMessage = 'You do not have permission to perform this action.'
              break
            case 404:
              errorMessage = 'The requested resource was not found.'
              break
            case 422:
              errorMessage = 'Invalid data provided. Please check your input.'
              break
            case 429:
              errorMessage = 'Too many requests. Please try again later.'
              break
            case 500:
              errorMessage = 'Server error. Please try again later.'
              break
            case 503:
              errorMessage = 'Service temporarily unavailable. Please try again later.'
              break
            default:
              errorMessage = `Request failed with status ${response.status}`
          }
        }

        throw new ApiRequestError(errorMessage, response.status)
      }

      const data = await response.json()
      
      // Handle legacy API response format
      if (data && typeof data === 'object' && 'success' in data) {
        if (!data.success) {
          throw new ApiRequestError(data.error || 'Request failed', 400)
        }
        return data.data
      }

      return data
    } catch (error) {
      if (error instanceof ApiRequestError) {
        throw error
      }

      lastError = error as Error

      // Don't retry on network errors for the last attempt
      if (attempt === maxRetries) {
        break
      }

      // Exponential backoff for retries
      const delay = Math.pow(2, attempt) * 1000
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }

  // If we get here, all attempts failed
  throw new ApiRequestError(
    lastError?.message || 'Network error occurred', 
    0
  )
}

// API service class with all endpoints
class ApiService {
  // Authentication
  async getCurrentUser(): Promise<User> {
    return apiRequest<User>('/api/auth/me')
  }

  async logout(): Promise<void> {
    return apiRequest<void>('/api/auth/logout', { method: 'POST' })
  }

  // Dashboard Analytics
  async getDashboardAnalytics(): Promise<DashboardAnalytics> {
    return apiRequest<DashboardAnalytics>('/api/dashboard/analytics')
  }

  // Contacts
  async getContacts(): Promise<Contact[]> {
    return apiRequest<Contact[]>('/api/contacts')
  }

  async createContact(contact: Partial<Contact>): Promise<Contact> {
    return apiRequest<Contact>('/api/contacts', {
      method: 'POST',
      body: JSON.stringify(contact)
    })
  }

  async updateContact(id: string, contact: Partial<Contact>): Promise<Contact> {
    return apiRequest<Contact>(`/api/contacts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(contact)
    })
  }

  async deleteContact(id: string): Promise<void> {
    return apiRequest<void>(`/api/contacts/${id}`, { method: 'DELETE' })
  }

  // Goals
  async getGoals(): Promise<Goal[]> {
    return apiRequest<Goal[]>('/api/goals')
  }

  async createGoal(goal: Partial<Goal>): Promise<Goal> {
    return apiRequest<Goal>('/api/goals', {
      method: 'POST',
      body: JSON.stringify(goal)
    })
  }

  async updateGoal(id: string, goal: Partial<Goal>): Promise<Goal> {
    return apiRequest<Goal>(`/api/goals/${id}`, {
      method: 'PUT',
      body: JSON.stringify(goal)
    })
  }

  async deleteGoal(id: string): Promise<void> {
    return apiRequest<void>(`/api/goals/${id}`, { method: 'DELETE' })
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return apiRequest<{ status: string; timestamp: string }>('/api/health')
  }
}

// Export singleton instance
export const apiService = new ApiService()