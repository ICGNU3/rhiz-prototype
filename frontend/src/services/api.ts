// Enhanced API service with comprehensive error handling and React Query integration

export interface User {
  id: string
  email: string
  name: string
  subscription_tier: string
  goals_count: number
  contacts_count: number
  ai_suggestions_used: number
}

export interface Contact {
  id: string
  name: string
  email?: string
  company?: string
  title?: string
  phone?: string
  notes?: string
  warmth_status?: string
  trust_score?: number
  last_interaction?: string
  created_at: string
  updated_at: string
}

export interface Goal {
  id: string
  title: string
  description: string
  goal_type: string
  priority_level: string
  status: string
  progress_percentage: number
  target_date?: string
  created_at: string
  updated_at: string
}

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

class ApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = '/api'
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        credentials: 'same-origin', // Include cookies for authentication
        ...options,
      })

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

      // Handle network errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new ApiRequestError(
          'Network error. Please check your internet connection.',
          0,
          'NETWORK_ERROR'
        )
      }

      // Handle other errors
      throw new ApiRequestError(
        error instanceof Error ? error.message : 'An unexpected error occurred',
        0,
        'UNKNOWN_ERROR'
      )
    }
  }

  // User management
  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me')
  }

  // Dashboard analytics
  async getDashboardAnalytics(): Promise<DashboardAnalytics> {
    return this.request<DashboardAnalytics>('/dashboard/analytics')
  }

  // Contact management
  async getContacts(): Promise<Contact[]> {
    return this.request<Contact[]>('/contacts')
  }

  async getContact(id: string): Promise<Contact> {
    return this.request<Contact>(`/contacts/${id}`)
  }

  async createContact(contactData: Partial<Contact>): Promise<Contact> {
    return this.request<Contact>('/contacts', {
      method: 'POST',
      body: JSON.stringify(contactData),
    })
  }

  async updateContact(id: string, contactData: Partial<Contact>): Promise<Contact> {
    return this.request<Contact>(`/contacts/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(contactData),
    })
  }

  async deleteContact(id: string): Promise<void> {
    return this.request<void>(`/contacts/${id}`, {
      method: 'DELETE',
    })
  }

  // Goal management
  async getGoals(): Promise<Goal[]> {
    return this.request<Goal[]>('/goals')
  }

  async getGoal(id: string): Promise<Goal> {
    return this.request<Goal>(`/goals/${id}`)
  }

  async createGoal(goalData: Partial<Goal>): Promise<Goal> {
    return this.request<Goal>('/goals', {
      method: 'POST',
      body: JSON.stringify(goalData),
    })
  }

  async updateGoal(id: string, goalData: Partial<Goal>): Promise<Goal> {
    return this.request<Goal>(`/goals/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(goalData),
    })
  }

  async deleteGoal(id: string): Promise<void> {
    return this.request<void>(`/goals/${id}`, {
      method: 'DELETE',
    })
  }

  // File uploads
  async uploadFile(file: File, endpoint: string): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)

    return fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      body: formData,
      credentials: 'same-origin',
    }).then(async (response) => {
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new ApiRequestError(
          errorData.message || `Upload failed with status ${response.status}`,
          response.status
        )
      }
      return response.json()
    })
  }

  // Contact import
  async uploadContacts(file: File): Promise<any> {
    return this.uploadFile(file, '/contacts/upload')
  }

  // AI and intelligence features
  async getAiSuggestions(): Promise<any[]> {
    return this.request<any[]>('/ai/suggestions')
  }

  async sendChatMessage(message: string): Promise<any> {
    return this.request<any>('/intelligence/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    })
  }

  // Trust and analytics
  async getTrustInsights(): Promise<any> {
    return this.request<any>('/trust/insights')
  }

  async getNetworkGraph(): Promise<any> {
    return this.request<any>('/network/graph')
  }
}

export const apiService = new ApiService()