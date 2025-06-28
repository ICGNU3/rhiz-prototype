/**
 * API Type Definitions for Rhiz
 * Comprehensive TypeScript interfaces for all API endpoints
 */

// Core data types
export interface Contact {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  notes?: string;
  source?: string;
  trust_score?: number;
  trust_tier?: 'rooted' | 'growing' | 'dormant' | 'frayed';
  created_at?: string;
  updated_at?: string;
}

export interface Goal {
  id: string;
  title: string;
  description: string;
  status: 'active' | 'completed' | 'paused';
  priority: 'high' | 'medium' | 'low';
  target_date?: string;
  created_at?: string;
  updated_at?: string;
}

export interface TrustInsight {
  id: string;
  contact_id: string;
  trust_score: number;
  trust_tier: 'rooted' | 'growing' | 'dormant' | 'frayed';
  confidence: number;
  summary: string;
  insights: string[];
  last_interaction?: string;
  reciprocity_score?: number;
  response_time_avg?: number;
}

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  profile_image_url?: string;
  subscription_tier?: string;
  created_at?: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ContactsResponse extends ApiResponse<Contact[]> {}
export interface GoalsResponse extends ApiResponse<Goal[]> {}
export interface TrustInsightsResponse extends ApiResponse<TrustInsight[]> {}

// Trust dashboard specific types
export interface TrustTierStats {
  rooted: number;
  growing: number;
  dormant: number;
  frayed: number;
}

export interface TrustHealthData {
  overall_score: number;
  tier_distribution: TrustTierStats;
  recent_changes: Array<{
    contact_name: string;
    old_tier: string;
    new_tier: string;
    change_date: string;
  }>;
  recommendations: string[];
}

// Sync and import types
export interface SyncJob {
  id: string;
  source: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  results?: {
    imported: number;
    duplicates: number;
    errors: number;
  };
  created_at: string;
}

export interface ContactSource {
  id: string;
  name: string;
  enabled: boolean;
  last_sync?: string;
  oauth_url?: string;
}

// Contact intelligence types
export interface AISuggestion {
  id: string;
  contact_id: string;
  goal_id: string;
  suggestion_type: 'outreach' | 'follow_up' | 'introduction';
  confidence: number;
  message: string;
  reasoning: string;
  created_at: string;
}

// Network graph types
export interface NetworkNode {
  id: string;
  name: string;
  type: 'contact' | 'goal' | 'user';
  trust_score?: number;
  company?: string;
}

export interface NetworkEdge {
  source: string;
  target: string;
  relationship: string;
  strength: number;
}

export interface NetworkGraph {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}

// Form and input types
export interface ContactFormData {
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  notes?: string;
}

export interface GoalFormData {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  target_date?: string;
}

// Dashboard analytics types
export interface DashboardStats {
  total_contacts: number;
  total_goals: number;
  active_goals: number;
  trust_score_avg: number;
  recent_interactions: number;
}

// Error types
export interface ApiError {
  error: string;
  details?: string;
  status: number;
}

// Authentication types
export interface AuthUser {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  profile_image_url?: string;
  is_authenticated: boolean;
}

export interface LoginRequest {
  email: string;
  type?: 'magic_link' | 'demo';
}

export interface RegisterRequest {
  email: string;
  first_name?: string;
  last_name?: string;
}