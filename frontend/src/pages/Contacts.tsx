import React, { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contactsAPI } from '../services/api';
import { Users, Plus, Search, Filter, Upload, Download, Link, Globe2, Linkedin, Twitter, Mail, Phone, MapPin, Calendar, Tag, Star, ExternalLink, MoreVertical, Merge } from 'lucide-react';

interface ContactFilters {
  search: string;
  source: string;
  status: string;
  tags: string[];
  relationship_type: string;
}

const Contacts: React.FC = () => {
  const [filters, setFilters] = useState<ContactFilters>({
    search: '',
    source: '',
    status: '',
    tags: [],
    relationship_type: ''
  });
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
  const [showSyncModal, setShowSyncModal] = useState(false);
  const [showMergeModal, setShowMergeModal] = useState(false);
  const [selectedContacts, setSelectedContacts] = useState<string[]>([]);

  const queryClient = useQueryClient();

  const { data: contacts = [], isLoading } = useQuery({
    queryKey: ['contacts', filters],
    queryFn: async () => {
      const response = await contactsAPI.getAll(filters);
      return response.data;
    },
  });

  const { data: syncJobs = [], isLoading: syncJobsLoading } = useQuery({
    queryKey: ['sync-jobs'],
    queryFn: async () => {
      try {
        const response = await fetch('/api/contacts/sync-jobs');
        return response.json();
      } catch (error) {
        return [];
      }
    },
    refetchInterval: 5000,
  });

  const { data: mergeCandidates = [], isLoading: mergeCandidatesLoading } = useQuery({
    queryKey: ['merge-candidates'],
    queryFn: async () => {
      try {
        const response = await fetch('/api/contacts/merge-candidates');
        return response.json();
      } catch (error) {
        return [];
      }
    },
  });

  const syncMutation = useMutation({
    mutationFn: async (source: string) => {
      const response = await fetch('/api/contacts/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source })
      });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      queryClient.invalidateQueries({ queryKey: ['sync-jobs'] });
    }
  });

  // Enhanced contact filtering
  const filteredContacts = useMemo(() => {
    return contacts.filter((contact: any) => {
      if (filters.search && !contact.name.toLowerCase().includes(filters.search.toLowerCase()) &&
          !contact.email?.toLowerCase().includes(filters.search.toLowerCase()) &&
          !contact.company?.toLowerCase().includes(filters.search.toLowerCase())) {
        return false;
      }
      if (filters.source && contact.sync_status !== filters.source) return false;
      if (filters.relationship_type && contact.relationship_type !== filters.relationship_type) return false;
      return true;
    });
  }, [contacts, filters]);

  const handleBulkSync = () => {
    setShowSyncModal(true);
  };

  const handleSourceSync = (source: string) => {
    syncMutation.mutate(source);
    setShowSyncModal(false);
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'google': return <Globe2 size={14} className="text-blue-500" />;
      case 'linkedin': return <Linkedin size={14} className="text-blue-600" />;
      case 'twitter': return <Twitter size={14} className="text-blue-400" />;
      case 'gmail': return <Mail size={14} className="text-red-500" />;
      case 'outlook': return <Mail size={14} className="text-blue-600" />;
      case 'csv': return <Upload size={14} className="text-green-500" />;
      default: return <Users size={14} className="text-gray-400" />;
    }
  };

  const getWarmthColor = (warmth: number) => {
    if (warmth >= 4) return 'bg-green-400';
    if (warmth >= 3) return 'bg-yellow-400';
    if (warmth >= 2) return 'bg-orange-400';
    return 'bg-gray-400';
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-gray-700 rounded w-1/3 mb-8 animate-pulse"></div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="glass-card p-6 animate-pulse">
              <div className="h-6 bg-gray-700 rounded mb-4"></div>
              <div className="h-4 bg-gray-700 rounded mb-2"></div>
              <div className="h-4 bg-gray-700 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Enhanced Header */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-white">Network Intelligence</h2>
          <p className="text-gray-400 mt-1">Multi-source contact sync and relationship management</p>
          <div className="flex items-center space-x-4 mt-3">
            <div className="text-sm text-gray-300">
              <span className="font-medium">{contacts.length}</span> total contacts
            </div>
            {mergeCandidates.length > 0 && (
              <div className="text-sm text-yellow-400">
                <span className="font-medium">{mergeCandidates.length}</span> potential duplicates
              </div>
            )}
          </div>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleBulkSync}
            className="glass-button-secondary flex items-center space-x-2"
          >
            <Link size={18} />
            <span>Sync Sources</span>
          </button>
          <button className="glass-button-secondary flex items-center space-x-2">
            <Upload size={18} />
            <span>Import CSV</span>
          </button>
          <button className="glass-button-primary flex items-center space-x-2">
            <Plus size={18} />
            <span>Add Contact</span>
          </button>
        </div>
      </div>

      {/* Sync Status Bar */}
      {syncJobs.length > 0 && (
        <div className="glass-card p-4">
          <h3 className="text-sm font-medium text-white mb-3">Sync Status</h3>
          <div className="space-y-2">
            {syncJobs.slice(0, 3).map((job: any) => (
              <div key={job.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getSourceIcon(job.source)}
                  <span className="text-sm text-gray-300 capitalize">{job.source} sync</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(job.processed_contacts / job.total_contacts) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-gray-400">
                    {job.processed_contacts}/{job.total_contacts}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Enhanced Search and Filters */}
      <div className="glass-card p-6">
        <div className="grid gap-4 md:grid-cols-5">
          {/* Search */}
          <div className="md:col-span-2 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search name, email, company..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="w-full pl-10 pr-4 py-3 bg-dark-card border border-dark-border rounded-lg text-white placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-colors"
            />
          </div>

          {/* Source Filter */}
          <select
            value={filters.source}
            onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value }))}
            className="bg-dark-card border border-dark-border rounded-lg text-white py-3 px-4 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          >
            <option value="">All Sources</option>
            <option value="manual">Manual</option>
            <option value="google">Google</option>
            <option value="linkedin">LinkedIn</option>
            <option value="twitter">Twitter</option>
            <option value="gmail">Gmail</option>
            <option value="outlook">Outlook</option>
            <option value="csv">CSV Import</option>
          </select>

          {/* Status Filter */}
          <select
            value={filters.status}
            onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
            className="bg-dark-card border border-dark-border rounded-lg text-white py-3 px-4 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          >
            <option value="">All Status</option>
            <option value="dormant">Dormant</option>
            <option value="active">Active</option>
            <option value="engaged">Engaged</option>
          </select>

          {/* Relationship Type Filter */}
          <select
            value={filters.relationship_type}
            onChange={(e) => setFilters(prev => ({ ...prev, relationship_type: e.target.value }))}
            className="bg-dark-card border border-dark-border rounded-lg text-white py-3 px-4 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          >
            <option value="">All Types</option>
            <option value="investor">Investor</option>
            <option value="founder">Founder</option>
            <option value="customer">Customer</option>
            <option value="talent">Talent</option>
            <option value="advisor">Advisor</option>
            <option value="partner">Partner</option>
          </select>
        </div>

        {/* View Toggle */}
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-all ${viewMode === 'list' ? 'bg-primary-500 text-white' : 'text-gray-400 hover:text-white'}`}
            >
              <Users size={18} />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-all ${viewMode === 'grid' ? 'bg-primary-500 text-white' : 'text-gray-400 hover:text-white'}`}
            >
              <div className="grid grid-cols-2 gap-1">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="w-1 h-1 bg-current"></div>
                ))}
              </div>
            </button>
          </div>

          {mergeCandidates.length > 0 && (
            <button
              onClick={() => setShowMergeModal(true)}
              className="glass-button-secondary flex items-center space-x-2"
            >
              <Merge size={16} />
              <span>Review Merges ({mergeCandidates.length})</span>
            </button>
          )}
        </div>
      </div>

      {/* Enhanced Contact Display */}
      {filteredContacts.length === 0 ? (
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-500 mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">No contacts found</h3>
          <p className="text-gray-400 mb-6">
            Try adjusting your filters or sync from external sources
          </p>
          <button
            onClick={handleBulkSync}
            className="glass-button-primary"
          >
            Sync Your First Contacts
          </button>
        </div>
      ) : viewMode === 'list' ? (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800/50">
                <tr>
                  <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Contact</th>
                  <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Company</th>
                  <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Source</th>
                  <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Warmth</th>
                  <th className="text-left p-4 text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filteredContacts.map((contact: any) => (
                  <tr key={contact.id} className="hover:bg-gray-800/30 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center space-x-3">
                        {contact.profile_picture_url ? (
                          <img
                            src={contact.profile_picture_url}
                            alt={contact.name}
                            className="w-10 h-10 rounded-full object-cover"
                          />
                        ) : (
                          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-primary-500 to-purple-500 flex items-center justify-center">
                            <span className="text-white font-medium text-sm">
                              {contact.name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        )}
                        <div>
                          <div className="font-medium text-white">{contact.name}</div>
                          <div className="text-sm text-gray-400">{contact.email}</div>
                          {contact.title && (
                            <div className="text-xs text-gray-500">{contact.title}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="text-sm text-gray-300">{contact.company || '—'}</div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center space-x-2">
                        {getSourceIcon(contact.sync_status || 'manual')}
                        <span className="text-sm text-gray-300 capitalize">
                          {contact.sync_status || 'manual'}
                        </span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${getWarmthColor(contact.warmth_status)}`}></div>
                        <span className="text-sm text-gray-300">{contact.warmth_label}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center space-x-2">
                        <button className="text-primary-400 hover:text-primary-300 text-sm">
                          View
                        </button>
                        <button className="text-green-400 hover:text-green-300 text-sm">
                          Message
                        </button>
                        <button className="text-gray-400 hover:text-gray-300">
                          <MoreVertical size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredContacts.map((contact: any) => (
            <div
              key={contact.id}
              className="glass-card p-6 cursor-pointer hover:border-primary-500 transition-all duration-300 group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {contact.profile_picture_url ? (
                    <img
                      src={contact.profile_picture_url}
                      alt={contact.name}
                      className="w-12 h-12 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-12 h-12 rounded-full bg-gradient-to-r from-primary-500 to-purple-500 flex items-center justify-center">
                      <span className="text-white font-medium">
                        {contact.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  )}
                  <div className="flex-1">
                    <h3 className="font-semibold text-white group-hover:text-primary-400 transition-colors">
                      {contact.name}
                    </h3>
                    {contact.title && (
                      <p className="text-sm text-gray-300">{contact.title}</p>
                    )}
                    {contact.company && (
                      <p className="text-sm text-gray-400">{contact.company}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getSourceIcon(contact.sync_status || 'manual')}
                  <div className={`w-2 h-2 rounded-full ${getWarmthColor(contact.warmth_status)}`}></div>
                </div>
              </div>

              {contact.email && (
                <div className="flex items-center space-x-2 text-sm text-gray-400 mb-2">
                  <Mail size={14} />
                  <span>{contact.email}</span>
                </div>
              )}

              {contact.phone && (
                <div className="flex items-center space-x-2 text-sm text-gray-400 mb-2">
                  <Phone size={14} />
                  <span>{contact.phone}</span>
                </div>
              )}

              {contact.notes && (
                <p className="text-sm text-gray-300 line-clamp-2 mb-4">{contact.notes}</p>
              )}

              {/* Social Handles */}
              {contact.social_handles && (
                <div className="flex items-center space-x-2 mb-4">
                  {JSON.parse(contact.social_handles).linkedin && (
                    <a
                      href={JSON.parse(contact.social_handles).linkedin}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-500"
                    >
                      <Linkedin size={16} />
                    </a>
                  )}
                  {JSON.parse(contact.social_handles).twitter && (
                    <a
                      href={JSON.parse(contact.social_handles).twitter}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:text-blue-300"
                    >
                      <Twitter size={16} />
                    </a>
                  )}
                </div>
              )}

              <div className="flex items-center justify-between pt-4 border-t border-dark-border">
                <span className="text-xs text-gray-400 capitalize">{contact.relationship_type}</span>
                <div className="flex space-x-2">
                  <button className="text-xs text-primary-400 hover:text-primary-300">
                    Map to Goal
                  </button>
                  <button className="text-xs text-green-400 hover:text-green-300">
                    Message
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Multi-Source Sync Modal */}
      {showSyncModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="glass-card p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-6">Sync Contacts</h3>
            <div className="space-y-3">
              {[
                { name: 'Google Contacts', id: 'google', icon: Globe2, description: 'Import from Google People API' },
                { name: 'LinkedIn', id: 'linkedin', icon: Linkedin, description: 'Import LinkedIn connections' },
                { name: 'Twitter/X', id: 'twitter', icon: Twitter, description: 'Import followers and following' },
                { name: 'Gmail', id: 'gmail', icon: Mail, description: 'Extract contacts from email headers' },
                { name: 'Outlook', id: 'outlook', icon: Mail, description: 'Import Outlook contacts' }
              ].map((source) => (
                <button
                  key={source.id}
                  onClick={() => handleSourceSync(source.id)}
                  className="w-full p-4 text-left glass-button-secondary hover:border-primary-500 flex items-center space-x-3"
                >
                  <source.icon size={20} />
                  <div>
                    <div className="font-medium text-white">{source.name}</div>
                    <div className="text-sm text-gray-400">{source.description}</div>
                  </div>
                </button>
              ))}
            </div>
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowSyncModal(false)}
                className="flex-1 glass-button-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Contacts;