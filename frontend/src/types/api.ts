// API Response Types for Rhiz Platform

export interface User {
  id: string;
  email: string;
  subscription_tier: string;
  first_name?: string;
  last_name?: string;
  profile_image_url?: string;
  created_at: string;
}

export interface Contact {
  id: string;
  user_id: string;
  name: string;
  email?: string;
  company?: string;
  title?: string;
  phone?: string;
  notes?: string;
  tags?: string[];
  trust_score?: number;
  trust_tier?: 'rooted' | 'growing' | 'dormant' | 'frayed';
  source?: string;
  last_interaction?: string;
  created_at: string;
  updated_at: string;
}

export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description: string;
  category?: string;
  target_date?: string;
  status: 'active' | 'completed' | 'paused';
  priority: 'high' | 'medium' | 'low';
  progress?: number;
  created_at: string;
  updated_at: string;
}

export interface TrustInsight {
  id: string;
  contact_id: string;
  user_id: string;
  trust_score: number;
  trust_tier: 'rooted' | 'growing' | 'dormant' | 'frayed';
  confidence_score: number;
  insights: string[];
  suggested_actions: string[];
  created_at: string;
}

export interface ContactInteraction {
  id: string;
  contact_id: string;
  user_id: string;
  interaction_type: 'email' | 'call' | 'meeting' | 'message' | 'social' | 'other';
  description: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
  response_time_hours?: number;
  created_at: string;
}

export interface NetworkNode {
  id: string;
  name: string;
  type: 'user' | 'contact' | 'goal';
  trust_score?: number;
  trust_tier?: 'rooted' | 'growing' | 'dormant' | 'frayed';
  email?: string;
  company?: string;
  title?: string;
  tags?: string[];
  last_interaction?: string;
  x?: number;
  y?: number;
}

export interface NetworkEdge {
  id: string;
  source: string;
  target: string;
  type: 'interaction' | 'relationship' | 'goal_match';
  strength: number;
  interaction_count?: number;
  last_interaction?: string;
}

export interface TrustMetric {
  timestamp: string;
  trust_score: number;
  response_time: number;
  interaction_frequency: number;
  reciprocity_score: number;
}

export interface NetworkGraph {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  stats: {
    total_contacts: number;
    total_relationships: number;
    avg_connections: number;
  };
}

export interface AIInsight {
  id: string;
  user_id: string;
  contact_id?: string;
  goal_id?: string;
  insight_type: 'relationship' | 'opportunity' | 'outreach' | 'priority';
  title: string;
  description: string;
  confidence_score: number;
  action_items: string[];
  priority: 'high' | 'medium' | 'low';
  created_at: string;
}

export interface SyncJob {
  id: string;
  user_id: string;
  source: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  total_items?: number;
  processed_items?: number;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface MergeCandidate {
  id: string;
  user_id: string;
  contact_1_id: string;
  contact_2_id: string;
  similarity_score: number;
  suggested_merge: boolean;
  status: 'pending' | 'merged' | 'dismissed';
  created_at: string;
}

export interface ContactUploadResponse {
  success: boolean;
  message: string;
  contacts_created: number;
  contacts_updated: number;
  errors: string[];
}

export interface ImportProgress {
  stage: 'reading' | 'parsing' | 'validation' | 'uploading' | 'complete';
  progress: number;
  message: string;
  errors?: string[];
}

export interface TrustHealth {
  overall_score: number;
  tier_distribution: {
    rooted: number;
    growing: number;
    dormant: number;
    frayed: number;
  };
  trends: {
    improving: number;
    declining: number;
    stable: number;
  };
  recommendations: string[];
}

export interface NotificationPreferences {
  email_digest: boolean;
  trust_alerts: boolean;
  goal_reminders: boolean;
  sync_notifications: boolean;
  weekly_reports: boolean;
  digest_frequency: 'daily' | 'weekly' | 'monthly';
  quiet_hours_start?: string;
  quiet_hours_end?: string;
}

export interface IntegrationStatus {
  linkedin: boolean;
  google_contacts: boolean;
  calendar: boolean;
  email: boolean;
  slack: boolean;
}

// API Response wrapper types
export interface APIResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

// Form types
export interface ContactForm {
  name: string;
  email?: string;
  company?: string;
  title?: string;
  phone?: string;
  notes?: string;
  tags?: string[];
}

export interface GoalForm {
  title: string;
  description: string;
  category?: string;
  target_date?: string;
  priority: 'high' | 'medium' | 'low';
}

export interface OnboardingData {
  intent: string;
  goals: GoalForm[];
  contacts_uploaded: boolean;
}

// Filter and query types
export interface ContactFilters {
  search?: string;
  trust_tier?: string[];
  source?: string[];
  company?: string;
  tags?: string[];
  last_interaction_days?: number;
}

export interface GoalFilters {
  search?: string;
  category?: string[];
  status?: string[];
  priority?: string[];
}

// Chart and visualization types
export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface TimeSeriesPoint {
  timestamp: string;
  value: number;
}

export interface TrustDistribution {
  rooted: number;
  growing: number;
  dormant: number;
  frayed: number;
}

// Error types
export interface APIError {
  message: string;
  code?: string;
  details?: any;
}

// Auth types
export interface LoginResponse {
  success: boolean;
  user?: User;
  message?: string;
  redirect_url?: string;
}

export interface MagicLinkRequest {
  email: string;
}

export interface MagicLinkResponse {
  success: boolean;
  message: string;
}

export default {};