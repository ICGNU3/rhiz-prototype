/**
 * Enhanced API client with proper error handling and type safety
 */

import { ApiResponse, PaginatedResponse } from '../../types';

// API configuration
const API_BASE_URL = '/api';

// Custom error class for API errors
export class ApiError extends Error {
  constructor(
    public status: number,
    public message: string,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Generic API client class
class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      // Handle non-JSON responses (like redirects)
      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('application/json')) {
        if (response.ok) {
          return {} as T; // Empty success response
        } else {
          throw new ApiError(response.status, 'Non-JSON response received');
        }
      }

      const data = await response.json();

      if (!response.ok) {
        throw new ApiError(
          response.status,
          data.error || data.message || 'Request failed',
          data.code
        );
      }

      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Handle network errors
      throw new ApiError(0, 'Network error occurred');
    }
  }

  // HTTP method helpers
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // File upload helper
  async uploadFile<T>(endpoint: string, file: File, additionalData?: Record<string, any>): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    return this.request<T>(endpoint, {
      method: 'POST',
      headers: {}, // Let browser set content-type for FormData
      body: formData,
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Helper function for handling API responses
export const handleApiResponse = <T>(
  apiCall: Promise<T>
): Promise<T> => {
  return apiCall.catch((error: ApiError) => {
    // Log error for debugging
    console.error('API Error:', {
      status: error.status,
      message: error.message,
      code: error.code
    });
    
    // Re-throw for component handling
    throw error;
  });
};

// Helper for paginated requests
export const paginatedRequest = <T>(
  endpoint: string,
  page: number = 1,
  limit: number = 20,
  params: Record<string, any> = {}
): Promise<PaginatedResponse<T>> => {
  const searchParams = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
    ...Object.fromEntries(
      Object.entries(params).map(([key, value]) => [key, String(value)])
    )
  });

  return apiClient.get<PaginatedResponse<T>>(`${endpoint}?${searchParams}`);
};

// Request retry helper
export const retryRequest = async <T>(
  apiCall: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: Error;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiCall();
    } catch (error) {
      lastError = error as Error;
      
      // Don't retry on client errors (4xx)
      if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
        throw error;
      }
      
      // Wait before retrying
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
      }
    }
  }

  throw lastError!;
};