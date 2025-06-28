// API response types for Rhiz platform
export interface Contact {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  notes?: string;
  warmth_status: number;
  warmth_label: string;
  source: string;
  created_at: string;
  updated_at?: string;
}

export interface Goal {
  id: string;
  title: string;
  description?: string;
  category?: string;
  priority: 'low' | 'medium' | 'high';
  status: 'active' | 'completed' | 'paused';
  target_date?: string;
  created_at: string;
  updated_at?: string;
}

export interface User {
  id: string;
  email: string;
  subscription_tier: string;
  created_at: string;
  updated_at?: string;
}

export interface TrustInsight {
  contact_id: string;
  trust_score: number;
  trust_tier: 'rooted' | 'growing' | 'dormant' | 'frayed';
  confidence_score: number;
  insights: string[];
  suggested_actions: string[];
  last_interaction?: string;
  response_time_avg?: number;
  interaction_frequency?: number;
}

export interface ContactUploadResponse {
  success: boolean;
  contacts_imported: number;
  contacts: Contact[];
  message: string;
}

export interface ApiError {
  error: string;
  details?: string;
}

// Contact import related types
export interface ImportProgress {
  percentage: number;
  text: string;
  details: string;
  isActive: boolean;
}

export interface ContactImportData {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  notes?: string;
}

// Network visualization types
export interface NetworkNode {
  id: string;
  name: string;
  type: 'contact' | 'goal' | 'user';
  trust_score?: number;
  trust_tier?: 'rooted' | 'growing' | 'dormant' | 'frayed';
  last_interaction?: string;
  tags?: string[];
  data?: any;
}

export interface NetworkEdge {
  id: string;
  source: string;
  target: string;
  strength: number;
  type?: string;
  label?: string;
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

export interface TrustMetrics {
  contact_id: string;
  metrics: {
    trust_score: number;
    response_time: number;
    interaction_frequency: number;
    reciprocity_score: number;
  }[];
  timestamps: string[];
}