/**
 * Centralized TypeScript definitions for Rhiz application
 */

// User & Authentication Types
export interface User {
  id: string;
  email: string;
  subscription_tier: 'explorer' | 'founder_plus';
  first_name?: string;
  last_name?: string;
  profile_image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

// Contact Types
export interface Contact {
  id: string;
  user_id: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  notes?: string;
  tags?: string[];
  warmth: 'cold' | 'aware' | 'warm' | 'active' | 'contributor';
  relationship_type?: string;
  trust_score?: number;
  source?: 'manual' | 'google' | 'linkedin' | 'icloud' | 'csv';
  last_contact?: string;
  created_at: string;
  updated_at: string;
}

export interface ContactImportSource {
  id: string;
  name: string;
  icon: string;
  description: string;
  status: 'connected' | 'disconnected' | 'available';
  last_sync?: string;
}

// Goal Types
export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  status: 'active' | 'completed' | 'paused';
  deadline?: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

// Network & Trust Types
export interface NetworkNode {
  id: string;
  name: string;
  company?: string;
  warmth: Contact['warmth'];
  trust_score: number;
  x?: number;
  y?: number;
}

export interface NetworkEdge {
  source: string;
  target: string;
  strength: number;
  relationship_type?: string;
}

export interface NetworkGraph {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}

export interface TrustInsight {
  contact_id: string;
  trust_tier: 'rooted' | 'growing' | 'dormant' | 'frayed';
  trust_score: number;
  confidence: number;
  reciprocity_index: number;
  response_time_avg: number;
  interaction_frequency: number;
  sentiment_score: number;
  suggested_actions: string[];
  last_analyzed: string;
}

// AI & Intelligence Types
export interface AISuggestion {
  id: string;
  user_id: string;
  contact_id: string;
  goal_id: string;
  contact_name: string;
  goal_title: string;
  confidence: number;
  reason: string;
  outreach_message?: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

// Settings & Preferences Types
export interface NotificationSettings {
  email_enabled: boolean;
  push_enabled: boolean;
  weekly_insights: boolean;
  trust_updates: boolean;
  goal_reminders: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
}

export interface SyncSettings {
  google_contacts: boolean;
  linkedin: boolean;
  icloud: boolean;
  calendar: boolean;
  auto_sync_frequency: 'never' | 'daily' | 'weekly' | 'monthly';
}

export interface UserSettings {
  notifications: NotificationSettings;
  sync: SyncSettings;
  privacy: {
    profile_visibility: 'private' | 'connections' | 'public';
    data_export_enabled: boolean;
    analytics_enabled: boolean;
  };
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

// Form Types
export interface ContactFormData {
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  notes?: string;
  tags?: string[];
  warmth: Contact['warmth'];
  relationship_type?: string;
}

export interface GoalFormData {
  title: string;
  description: string;
  priority: Goal['priority'];
  deadline?: string;
}

// Mass Messaging Types
export interface MessageTemplate {
  id: string;
  title: string;
  content: string;
  variables: string[];
  category: 'check_in' | 'feedback' | 'contribution' | 'custom';
}

export interface MessageCampaign {
  id: string;
  title: string;
  template_id: string;
  recipients: string[];
  status: 'draft' | 'sending' | 'sent' | 'failed';
  scheduled_at?: string;
  sent_count: number;
  delivered_count: number;
  opened_count: number;
  replied_count: number;
  created_at: string;
}

// Component Props Types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

// Filter & Search Types
export interface ContactFilters {
  warmth?: Contact['warmth'][];
  source?: string[];
  tags?: string[];
  search?: string;
  sort_by?: 'name' | 'company' | 'last_contact' | 'trust_score';
  sort_order?: 'asc' | 'desc';
}

export interface GoalFilters {
  status?: Goal['status'][];
  priority?: Goal['priority'][];
  search?: string;
  sort_by?: 'title' | 'priority' | 'deadline' | 'progress';
  sort_order?: 'asc' | 'desc';
}