export interface User {
  id: string;
  email: string;
  subscription_tier: string;
  goals_count: number;
  contacts_count: number;
  ai_suggestions_used: number;
}

export interface Contact {
  id: string;
  user_id: string;
  name: string;
  email?: string;
  phone?: string;
  twitter?: string;
  linkedin?: string;
  handle?: string;
  relationship_type?: string;
  warmth_status: number;
  warmth_label?: string;
  warmth_level: string;
  last_interaction_date?: string;
  last_contact_method?: string;
  interaction_count: number;
  priority_level?: string;
  notes?: string;
  narrative_thread?: string;
  follow_up_action?: string;
  follow_up_due_date?: string;
  tags?: string;
  introduced_by?: string;
  location?: string;
  company?: string;
  title?: string;
  interests?: string;
  source: string;
  created_at?: string;
  updated_at?: string;
}

export interface Goal {
  id: string;
  user_id: string;
  goal_type: string;
  title: string;
  description?: string;
  category?: string;
  priority_level: string;
  target_date?: string;
  timeline?: string;
  metrics?: string;
  progress_percentage: number;
  ai_context?: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface AISuggestion {
  id: string;
  user_id: string;
  goal_id?: string;
  contact_id?: string;
  suggestion_type: string;
  confidence: number;
  reasoning?: string;
  suggested_action?: string;
  outreach_message?: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface DashboardAnalytics {
  contacts: number;
  goals: number;
  interactions: number;
  ai_suggestions: number;
  trust_score?: number;
  network_growth?: number;
  recent_activity?: {
    contacts_added: number;
    goals_completed: number;
    messages_sent: number;
  };
}

export interface AuthResponse {
  success: boolean;
  message: string;
  user?: User;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}