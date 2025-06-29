// React Query hooks for API operations with comprehensive error handling

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiService, Contact, Goal } from '../services/api'

// Query keys for consistent cache management
export const queryKeys = {
  user: ['user'] as const,
  contacts: ['contacts'] as const,
  contact: (id: string) => ['contacts', id] as const,
  goals: ['goals'] as const,
  goal: (id: string) => ['goals', id] as const,
  dashboardAnalytics: ['dashboard', 'analytics'] as const,
  aiSuggestions: ['ai', 'suggestions'] as const,
  trustInsights: ['trust', 'insights'] as const,
  networkGraph: ['network', 'graph'] as const,
}

// User hooks
export const useCurrentUser = () => {
  return useQuery({
    queryKey: queryKeys.user,
    queryFn: () => apiService.getCurrentUser(),
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: (failureCount, error: any) => {
      // Don't retry on authentication errors
      if (error?.status === 401) return false
      return failureCount < 2
    },
  })
}

// Dashboard hooks
export const useDashboardAnalytics = () => {
  return useQuery({
    queryKey: queryKeys.dashboardAnalytics,
    queryFn: () => apiService.getDashboardAnalytics(),
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  })
}

// Contact hooks
export const useContacts = () => {
  return useQuery({
    queryKey: queryKeys.contacts,
    queryFn: () => apiService.getContacts(),
  })
}

export const useContact = (id: string) => {
  return useQuery({
    queryKey: queryKeys.contact(id),
    queryFn: () => apiService.getContact(id),
    enabled: !!id, // Only run if id is provided
  })
}

export const useCreateContact = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (contactData: Partial<Contact>) => 
      apiService.createContact(contactData),
    onSuccess: () => {
      // Invalidate contacts list to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.contacts })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboardAnalytics })
    },
  })
}

export const useUpdateContact = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Contact> }) =>
      apiService.updateContact(id, data),
    onSuccess: (data, variables) => {
      // Update specific contact in cache
      queryClient.setQueryData(queryKeys.contact(variables.id), data)
      // Invalidate contacts list
      queryClient.invalidateQueries({ queryKey: queryKeys.contacts })
    },
  })
}

export const useDeleteContact = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => apiService.deleteContact(id),
    onSuccess: (_, id) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: queryKeys.contact(id) })
      // Invalidate contacts list
      queryClient.invalidateQueries({ queryKey: queryKeys.contacts })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboardAnalytics })
    },
  })
}

// Goal hooks
export const useGoals = () => {
  return useQuery({
    queryKey: queryKeys.goals,
    queryFn: () => apiService.getGoals(),
  })
}

export const useGoal = (id: string) => {
  return useQuery({
    queryKey: queryKeys.goal(id),
    queryFn: () => apiService.getGoal(id),
    enabled: !!id,
  })
}

export const useCreateGoal = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (goalData: Partial<Goal>) => 
      apiService.createGoal(goalData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.goals })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboardAnalytics })
    },
  })
}

export const useUpdateGoal = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Goal> }) =>
      apiService.updateGoal(id, data),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(queryKeys.goal(variables.id), data)
      queryClient.invalidateQueries({ queryKey: queryKeys.goals })
    },
  })
}

export const useDeleteGoal = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => apiService.deleteGoal(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.goal(id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.goals })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboardAnalytics })
    },
  })
}

// File upload hooks
export const useUploadContacts = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (file: File) => apiService.uploadContacts(file),
    onSuccess: () => {
      // Refresh contacts and analytics after upload
      queryClient.invalidateQueries({ queryKey: queryKeys.contacts })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboardAnalytics })
    },
  })
}

// AI and intelligence hooks
export const useAiSuggestions = () => {
  return useQuery({
    queryKey: queryKeys.aiSuggestions,
    queryFn: () => apiService.getAiSuggestions(),
    refetchInterval: 15 * 60 * 1000, // Refetch every 15 minutes
  })
}

export const useSendChatMessage = () => {
  return useMutation({
    mutationFn: (message: string) => apiService.sendChatMessage(message),
  })
}

// Trust and network hooks
export const useTrustInsights = () => {
  return useQuery({
    queryKey: queryKeys.trustInsights,
    queryFn: () => apiService.getTrustInsights(),
    refetchInterval: 10 * 60 * 1000, // Refetch every 10 minutes
  })
}

export const useNetworkGraph = () => {
  return useQuery({
    queryKey: queryKeys.networkGraph,
    queryFn: () => apiService.getNetworkGraph(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Utility hooks
export const useRefreshAll = () => {
  const queryClient = useQueryClient()
  
  const refreshAll = () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.contacts })
    queryClient.invalidateQueries({ queryKey: queryKeys.goals })
    queryClient.invalidateQueries({ queryKey: queryKeys.dashboardAnalytics })
    queryClient.invalidateQueries({ queryKey: queryKeys.aiSuggestions })
    queryClient.invalidateQueries({ queryKey: queryKeys.trustInsights })
    queryClient.invalidateQueries({ queryKey: queryKeys.networkGraph })
  }
  
  return { refreshAll }
}

// Error handling utility
export const useErrorHandler = () => {
  const handleError = (error: any) => {
    console.error('API Error:', error)
    
    // You can add global error handling logic here
    // such as showing toast notifications, logging to external services, etc.
    
    return error
  }
  
  return { handleError }
}