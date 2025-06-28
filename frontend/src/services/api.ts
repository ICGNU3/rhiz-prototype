import axios from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for session management
});

// Request interceptor for auth tokens
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface User {
  id: string;
  email: string;
  subscription_tier: string;
  created_at: string;
}

export interface Contact {
  id: string;
  user_id: string;
  name: string;
  email?: string;
  phone?: string;
  linkedin?: string;
  company?: string;
  title?: string;
  relationship_type: string;
  warmth_status: number;
  warmth_label: string;
  priority_level: string;
  notes?: string;
  tags?: string;
  location?: string;
  interests?: string;
  created_at: string;
  updated_at: string;
}

export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description: string;
  created_at: string;
}

export interface AISuggestion {
  id: string;
  contact_id: string;
  goal_id: string;
  suggestion: string;
  confidence: number;
  created_at: string;
}

export interface ContactInteraction {
  id: string;
  contact_id: string;
  user_id: string;
  interaction_type: string;
  status: string;
  direction: string;
  subject?: string;
  summary?: string;
  notes?: string;
  timestamp: string;
}

export interface NetworkNode {
  id: string;
  name: string;
  type: 'contact' | 'goal' | 'user';
  data: Contact | Goal | User;
}

export interface NetworkEdge {
  id: string;
  source: string;
  target: string;
  type: 'relationship' | 'goal_match' | 'interaction';
  strength: number;
}

// Auth API - Updated to match real Flask routes
export const authAPI = {
  login: (email: string, password?: string) =>
    api.post('/api/login', { email, password }),
  
  magicLink: (email: string) =>
    api.post('/auth/magic-link', { email }),
  
  logout: () =>
    api.post('/api/logout'),
  
  signup: (email: string, subscription_tier: string = 'explorer') =>
    api.post('/api/signup', { email, subscription_tier }),
  
  getCurrentUser: () =>
    api.get<User>('/api/current-user'),
  
  demoLogin: () =>
    api.get('/demo-login'),
};

// Goals API - Updated to match real Flask routes
export const goalsAPI = {
  getAll: () =>
    api.get<Goal[]>('/api/goals'),
  
  getById: (id: string) =>
    api.get<Goal>(`/api/goals/${id}`),
  
  create: (data: Omit<Goal, 'id' | 'user_id' | 'created_at'>) =>
    api.post<Goal>('/api/goals', data),
  
  update: (id: string, data: Partial<Goal>) =>
    api.put<Goal>(`/api/goals/${id}`, data),
  
  delete: (id: string) =>
    api.delete(`/api/goals/${id}`),
  
  getMatches: (goalId: string) =>
    api.get<AISuggestion[]>(`/api/goals/${goalId}/matches`),
};

// Contacts API
export const contactsAPI = {
  getAll: (filters?: { search?: string; warmth?: number; relationship_type?: string }) =>
    api.get<Contact[]>('/api/contacts', { params: filters }),
  
  getById: (id: string) =>
    api.get<Contact>(`/api/contacts/${id}`),
  
  create: (data: Omit<Contact, 'id' | 'user_id' | 'created_at' | 'updated_at'>) =>
    api.post<Contact>('/api/contacts', data),
  
  update: (id: string, data: Partial<Contact>) =>
    api.put<Contact>(`/api/contacts/${id}`, data),
  
  delete: (id: string) =>
    api.delete(`/api/contacts/${id}`),
  
  updateWarmth: (id: string, warmth_status: number) =>
    api.patch(`/api/contacts/${id}/warmth`, { warmth_status }),
  
  getInteractions: (id: string) =>
    api.get<ContactInteraction[]>(`/api/contacts/${id}/interactions`),
  
  addInteraction: (id: string, interaction: Omit<ContactInteraction, 'id' | 'timestamp'>) =>
    api.post<ContactInteraction>(`/api/contacts/${id}/interactions`, interaction),
  
  importCSV: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/contacts/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// Network API
export const networkAPI = {
  getGraph: () =>
    api.get<{ nodes: NetworkNode[]; edges: NetworkEdge[] }>('/api/network/graph'),
  
  getMetrics: () =>
    api.get('/api/network/metrics'),
  
  getRelationships: (contactId: string) =>
    api.get(`/api/network/relationships/${contactId}`),
  
  createRelationship: (data: { contact_a_id: string; contact_b_id: string; relationship_type: string; strength: number }) =>
    api.post('/api/network/relationships', data),
};

// Intelligence API - Updated to match real Flask routes
export const intelligenceAPI = {
  getAISuggestions: () =>
    api.get<AISuggestion[]>('/api/ai-suggestions'),
  
  processNLQuery: (query: string) =>
    api.post('/api/intelligence/nlp', { query }),
  
  getUnknownContacts: () =>
    api.get('/api/intelligence/unknown-contacts'),
  
  getInsights: () =>
    api.get('/api/insights'),
  
  generateOutreach: (contactId: string, goalId: string) =>
    api.post('/api/intelligence/outreach', { contact_id: contactId, goal_id: goalId }),
};

// Analytics API
export const analyticsAPI = {
  getDashboardData: () =>
    api.get('/api/analytics/dashboard'),
  
  getOutreachMetrics: () =>
    api.get('/api/analytics/outreach'),
  
  getNetworkGrowth: () =>
    api.get('/api/analytics/network-growth'),
  
  getContactEffectiveness: () =>
    api.get('/api/analytics/contact-effectiveness'),
};

// Gamification API
export const gamificationAPI = {
  getUserProgress: () =>
    api.get('/api/gamification/progress'),
  
  getDailyQuests: () =>
    api.get('/api/gamification/quests'),
  
  completeQuest: (questId: string) =>
    api.post(`/api/gamification/quests/${questId}/complete`),
  
  getAchievements: () =>
    api.get('/api/gamification/achievements'),
};

// Email API
export const emailAPI = {
  sendEmail: (data: { to: string; subject: string; message: string; contact_id?: string }) =>
    api.post('/api/email/send', data),
  
  getTemplates: () =>
    api.get('/api/email/templates'),
  
  generateSubject: (message: string) =>
    api.post('/api/email/generate-subject', { message }),
  
  adjustTone: (message: string, tone: string) =>
    api.post('/api/email/adjust-tone', { message, tone }),
};

export default api;