/**
 * TypeScript type definitions for Rhiz API
 * Updated to match backend data models and fix compilation errors
 */

export interface User {
  id: string;
  email: string;
  subscription_tier?: string;
  created_at?: string;
}

export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description: string;
  category?: string;
  status?: 'active' | 'completed' | 'paused' | 'archived';
  progress?: number;
  target_date?: string;
  created_at: string;
  updated_at?: string;
}

export interface Contact {
  id: string;
  user_id: string;
  name: string;
  email?: string;
  company?: string;
  title?: string;
  notes?: string;
  source?: string;
  warmth_status?: 'cold' | 'warm' | 'hot';
  created_at: string;
  updated_at?: string;
}

export interface AISuggestion {
  id: string;
  user_id: string;
  goal_id: string;
  contact_id: string;
  contact_name: string;
  confidence_score: number;
  reason: string;
  suggested_action: string;
  outreach_message?: string;
  created_at: string;
}

export interface TrustInsight {
  id: string;
  contact_id: string;
  user_id: string;
  trust_tier: 'rooted' | 'growing' | 'dormant' | 'frayed';
  trust_score: number;
  response_time_avg?: number;
  interaction_frequency?: number;
  last_interaction?: string;
  reciprocity_index: number;
  behavioral_patterns: string[];
  created_at: string;
  updated_at?: string;
}

export interface NetworkNode {
  id: string;
  name: string;
  email?: string;
  company?: string;
  data?: any;
  x?: number;
  y?: number;
}

export interface NetworkEdge {
  source: string;
  target: string;
  strength: number;
}

export interface ContactUploadResponse {
  success: boolean;
  message: string;
  imported_count?: number;
  errors?: string[];
}

export interface ImportProgress {
  step: string;
  progress: number;
  message?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ContactSource {
  platform: string;
  connected: boolean;
  contact_count?: number;
  last_sync?: string;
}

export interface SyncJob {
  id: string;
  source: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message?: string;
  created_at: string;
}

export interface TrustMetric {
  metric: string;
  value: number;
  trend: 'up' | 'down' | 'stable';
}

// Chart.js types
export interface ChartOptions {
  responsive: boolean;
  plugins?: {
    legend?: {
      display: boolean;
    };
  };
}

export interface ChartData {
  labels: string[];
  datasets: Array<{
    data: number[];
    backgroundColor?: string[];
    borderColor?: string;
    borderWidth?: number;
  }>;
}