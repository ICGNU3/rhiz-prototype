import { User, Contact, Goal, AISuggestion, DashboardAnalytics, ApiResponse } from '../types';

const API_BASE_URL = import.meta.env.PROD ? '' : 'http://localhost:5000';

class ApiService {
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('API request failed:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  }

  // Authentication
  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.request<User>('/api/auth/me');
  }

  async requestMagicLink(email: string): Promise<ApiResponse<{message: string}>> {
    return this.request<{message: string}>('/api/auth/magic-link', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  async demoLogin(): Promise<ApiResponse<User>> {
    return this.request<User>('/api/auth/demo-login', {
      method: 'POST',
    });
  }

  // Dashboard
  async getDashboardAnalytics(): Promise<ApiResponse<DashboardAnalytics>> {
    return this.request<DashboardAnalytics>('/api/dashboard/analytics');
  }

  // Contacts
  async getContacts(): Promise<ApiResponse<Contact[]>> {
    return this.request<Contact[]>('/api/contacts');
  }

  async getContact(id: string): Promise<ApiResponse<Contact>> {
    return this.request<Contact>(`/api/contacts/${id}`);
  }

  async createContact(contact: Partial<Contact>): Promise<ApiResponse<Contact>> {
    return this.request<Contact>('/api/contacts', {
      method: 'POST',
      body: JSON.stringify(contact),
    });
  }

  async updateContact(id: string, contact: Partial<Contact>): Promise<ApiResponse<Contact>> {
    return this.request<Contact>(`/api/contacts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(contact),
    });
  }

  async deleteContact(id: string): Promise<ApiResponse<{message: string}>> {
    return this.request<{message: string}>(`/api/contacts/${id}`, {
      method: 'DELETE',
    });
  }

  // Goals
  async getGoals(): Promise<ApiResponse<Goal[]>> {
    return this.request<Goal[]>('/api/goals');
  }

  async getGoal(id: string): Promise<ApiResponse<Goal>> {
    return this.request<Goal>(`/api/goals/${id}`);
  }

  async createGoal(goal: Partial<Goal>): Promise<ApiResponse<Goal>> {
    return this.request<Goal>('/api/goals', {
      method: 'POST',
      body: JSON.stringify(goal),
    });
  }

  async updateGoal(id: string, goal: Partial<Goal>): Promise<ApiResponse<Goal>> {
    return this.request<Goal>(`/api/goals/${id}`, {
      method: 'PUT',
      body: JSON.stringify(goal),
    });
  }

  async deleteGoal(id: string): Promise<ApiResponse<{message: string}>> {
    return this.request<{message: string}>(`/api/goals/${id}`, {
      method: 'DELETE',
    });
  }

  // AI Suggestions
  async getAISuggestions(): Promise<ApiResponse<AISuggestion[]>> {
    return this.request<AISuggestion[]>('/api/ai-suggestions');
  }

  // Contact Upload
  async uploadContacts(file: File): Promise<ApiResponse<{processed: number, skipped: number}>> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.request<{processed: number, skipped: number}>('/api/contacts/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }

  async uploadContactsJSON(contacts: Partial<Contact>[]): Promise<ApiResponse<{processed: number, skipped: number}>> {
    return this.request<{processed: number, skipped: number}>('/api/contacts/upload', {
      method: 'POST',
      body: JSON.stringify({ contacts }),
    });
  }
}

export const apiService = new ApiService();