// API service for making requests to the backend

export interface User {
  id: string
  email: string
  name: string
  subscription_tier: string
  goals_count: number
  contacts_count: number
  ai_suggestions_used: number
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

export interface ApiResponse<T> {
  success: boolean
  data: T | null
  error?: string
}

class ApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = '/api'
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return { success: true, data }
    } catch (error) {
      console.error('API request failed:', error)
      return {
        success: false,
        data: null,
        error: error instanceof Error ? error.message : 'Unknown error',
      }
    }
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.request<User>('/auth/me')
  }

  async getDashboardAnalytics(): Promise<ApiResponse<DashboardAnalytics>> {
    return this.request<DashboardAnalytics>('/dashboard/analytics')
  }

  async getContacts(): Promise<ApiResponse<any[]>> {
    return this.request<any[]>('/contacts')
  }

  async getGoals(): Promise<ApiResponse<any[]>> {
    return this.request<any[]>('/goals')
  }

  async createContact(contactData: any): Promise<ApiResponse<any>> {
    return this.request<any>('/contacts', {
      method: 'POST',
      body: JSON.stringify(contactData),
    })
  }

  async createGoal(goalData: any): Promise<ApiResponse<any>> {
    return this.request<any>('/goals', {
      method: 'POST',
      body: JSON.stringify(goalData),
    })
  }
}

export const apiService = new ApiService()