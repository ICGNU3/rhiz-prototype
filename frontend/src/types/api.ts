// API types for React frontend
export interface Contact {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  trust_score?: number;
  warmth_status?: number;
  relationship_type?: string;
  source?: string;
}

export interface Goal {
  id: string;
  title: string;
  description: string;
  created_at: string;
}

export interface TrustInsight {
  id: string;
  contact_id: string;
  trust_score: number;
  summary?: string;
  last_interaction?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export type ContactImportSource = 'google' | 'linkedin' | 'csv' | 'manual' | 'icloud' | 'outlook';