/**
 * Contacts API service with synced contact management
 */

import { apiClient, handleApiResponse, paginatedRequest } from './apiClient';
import type { Contact, ContactFormData, ContactFilters, ContactImportSource, PaginatedResponse } from '../../types';

export const contactsApi = {
  // Get all contacts with filtering and pagination
  getContacts: (filters: ContactFilters = {}, page: number = 1, limit: number = 50) => {
    return handleApiResponse(
      paginatedRequest<Contact>('/contacts', page, limit, filters)
    );
  },

  // Get single contact by ID
  getContact: (id: string) => {
    return handleApiResponse(
      apiClient.get<Contact>(`/contacts/${id}`)
    );
  },

  // Create new contact
  createContact: (data: ContactFormData) => {
    return handleApiResponse(
      apiClient.post<Contact>('/contacts', data)
    );
  },

  // Update existing contact
  updateContact: (id: string, data: Partial<ContactFormData>) => {
    return handleApiResponse(
      apiClient.put<Contact>(`/contacts/${id}`, data)
    );
  },

  // Delete contact
  deleteContact: (id: string) => {
    return handleApiResponse(
      apiClient.delete<{ success: boolean }>(`/contacts/${id}`)
    );
  },

  // Bulk operations
  bulkUpdateContacts: (contactIds: string[], updates: Partial<ContactFormData>) => {
    return handleApiResponse(
      apiClient.post<{ updated: number }>('/contacts/bulk-update', {
        contact_ids: contactIds,
        updates
      })
    );
  },

  bulkDeleteContacts: (contactIds: string[]) => {
    return handleApiResponse(
      apiClient.post<{ deleted: number }>('/contacts/bulk-delete', {
        contact_ids: contactIds
      })
    );
  },

  // Contact sync and import
  getImportSources: () => {
    return handleApiResponse(
      apiClient.get<ContactImportSource[]>('/contacts/import-sources')
    );
  },

  // Google Contacts sync
  getGoogleAuthUrl: () => {
    return handleApiResponse(
      apiClient.get<{ auth_url: string }>('/contacts/sync/google/auth')
    );
  },

  syncGoogleContacts: () => {
    return handleApiResponse(
      apiClient.post<{ job_id: string }>('/contacts/sync/google')
    );
  },

  // LinkedIn import (manual upload)
  uploadLinkedInContacts: (file: File) => {
    return handleApiResponse(
      apiClient.uploadFile<{ imported: number; skipped: number }>('/contacts/import/linkedin', file)
    );
  },

  // iCloud/CSV import
  uploadCSVContacts: (file: File, mapping?: Record<string, string>) => {
    return handleApiResponse(
      apiClient.uploadFile<{ imported: number; skipped: number; errors: string[] }>(
        '/contacts/import/csv', 
        file, 
        mapping ? { mapping: JSON.stringify(mapping) } : undefined
      )
    );
  },

  // Sync status and management
  getSyncJobs: () => {
    return handleApiResponse(
      apiClient.get<Array<{
        id: string;
        source: string;
        status: 'pending' | 'running' | 'completed' | 'failed';
        created_at: string;
        completed_at?: string;
        imported_count?: number;
        error_message?: string;
      }>>('/contacts/sync-jobs')
    );
  },

  // Duplicate detection and merging
  getMergeCandidates: () => {
    return handleApiResponse(
      apiClient.get<Array<{
        id: string;
        contacts: Contact[];
        confidence: number;
        suggested_primary: string;
      }>>('/contacts/merge-candidates')
    );
  },

  mergeContacts: (primaryId: string, duplicateIds: string[]) => {
    return handleApiResponse(
      apiClient.post<Contact>('/contacts/merge', {
        primary_id: primaryId,
        duplicate_ids: duplicateIds
      })
    );
  },

  // Contact enrichment
  enrichContact: (id: string) => {
    return handleApiResponse(
      apiClient.post<Contact>(`/contacts/${id}/enrich`)
    );
  },

  // Search and filtering helpers
  searchContacts: (query: string, limit: number = 10) => {
    return handleApiResponse(
      apiClient.get<Contact[]>(`/contacts/search?q=${encodeURIComponent(query)}&limit=${limit}`)
    );
  },

  // Tags management
  getContactTags: () => {
    return handleApiResponse(
      apiClient.get<string[]>('/contacts/tags')
    );
  },

  addTagToContact: (contactId: string, tag: string) => {
    return handleApiResponse(
      apiClient.post<Contact>(`/contacts/${contactId}/tags`, { tag })
    );
  },

  removeTagFromContact: (contactId: string, tag: string) => {
    return handleApiResponse(
      apiClient.delete<Contact>(`/contacts/${contactId}/tags/${encodeURIComponent(tag)}`)
    );
  },

  // Interaction tracking
  getContactInteractions: (contactId: string) => {
    return handleApiResponse(
      apiClient.get<Array<{
        id: string;
        type: string;
        notes: string;
        date: string;
        created_at: string;
      }>>(`/contacts/${contactId}/interactions`)
    );
  },

  addContactInteraction: (contactId: string, interaction: {
    type: string;
    notes: string;
    date: string;
  }) => {
    return handleApiResponse(
      apiClient.post<{ id: string }>(`/contacts/${contactId}/interactions`, interaction)
    );
  },

  // Contact statistics
  getContactStats: () => {
    return handleApiResponse(
      apiClient.get<{
        total: number;
        by_warmth: Record<string, number>;
        by_source: Record<string, number>;
        recent_activity: number;
        needs_follow_up: number;
      }>('/contacts/stats')
    );
  }
};