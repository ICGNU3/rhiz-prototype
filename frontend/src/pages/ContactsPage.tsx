/**
 * Enhanced Contacts Page with import functionality, filtering, and trust insights
 */

import React, { useState, useEffect } from 'react';
import { useContacts } from '../context/AppContext';
import { contactsApi } from '../services/api/contactsApi';
import ContactImportModal from '../components/features/ContactImportModal';
import TrustPanel from '../components/features/TrustPanel';
import type { Contact, ContactFilters } from '../types';

const ContactsPage: React.FC = () => {
  const { contacts, selectedContact, filters, actions } = useContacts();
  const [showImportModal, setShowImportModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'list' | 'cards' | 'pipeline'>('cards');
  const [sortBy, setSortBy] = useState<'name' | 'company' | 'last_contact' | 'trust_score'>('name');
  const [filterWarmth, setFilterWarmth] = useState<string[]>([]);

  useEffect(() => {
    loadContacts();
  }, [filters]);

  const loadContacts = async () => {
    setIsLoading(true);
    try {
      const result = await contactsApi.getContacts(filters);
      actions.setContacts(result.data || []);
    } catch (error) {
      console.error('Failed to load contacts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImportComplete = (imported: number, source: string) => {
    setShowImportModal(false);
    loadContacts(); // Refresh contacts after import
    // Show success message
    console.log(`Successfully imported ${imported} contacts from ${source}`);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    actions.setFilters({ ...filters, search: query });
  };

  const handleWarmthFilter = (warmth: string) => {
    const newWarmthFilter = filterWarmth.includes(warmth)
      ? filterWarmth.filter(w => w !== warmth)
      : [...filterWarmth, warmth];
    setFilterWarmth(newWarmthFilter);
    actions.setFilters({ ...filters, warmth: newWarmthFilter });
  };

  const getWarmthColor = (warmth: string) => {
    switch (warmth) {
      case 'cold': return 'text-gray-400 bg-gray-500';
      case 'aware': return 'text-blue-400 bg-blue-500';
      case 'warm': return 'text-orange-400 bg-orange-500';
      case 'active': return 'text-green-400 bg-green-500';
      case 'contributor': return 'text-purple-400 bg-purple-500';
      default: return 'text-gray-400 bg-gray-500';
    }
  };

  const filteredContacts = contacts.filter(contact => {
    const matchesSearch = !searchQuery || 
      contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      contact.company?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      contact.email?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesWarmth = filterWarmth.length === 0 || 
      filterWarmth.includes(contact.warmth);

    return matchesSearch && matchesWarmth;
  });

  const sortedContacts = [...filteredContacts].sort((a, b) => {
    switch (sortBy) {
      case 'name': return a.name.localeCompare(b.name);
      case 'company': return (a.company || '').localeCompare(b.company || '');
      case 'last_contact': return new Date(b.last_contact || '').getTime() - new Date(a.last_contact || '').getTime();
      case 'trust_score': return (b.trust_score || 0) - (a.trust_score || 0);
      default: return 0;
    }
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Contacts</h1>
          <p className="text-gray-400 mt-1">
            Manage your network with intelligent relationship insights
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowImportModal(true)}
            className="btn btn-secondary"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            Import Contacts
          </button>
          <button className="btn btn-primary">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Contact
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="glass-card p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search contacts by name, company, or email..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Warmth Filters */}
          <div className="flex flex-wrap gap-2">
            {['cold', 'aware', 'warm', 'active', 'contributor'].map((warmth) => (
              <button
                key={warmth}
                onClick={() => handleWarmthFilter(warmth)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                  filterWarmth.includes(warmth)
                    ? `${getWarmthColor(warmth)} bg-opacity-30`
                    : 'text-gray-400 bg-white bg-opacity-5 hover:bg-opacity-10'
                }`}
              >
                {warmth.charAt(0).toUpperCase() + warmth.slice(1)}
              </button>
            ))}
          </div>

          {/* View Mode and Sort */}
          <div className="flex items-center space-x-2">
            <div className="flex bg-white bg-opacity-5 rounded-lg p-1">
              {['list', 'cards', 'pipeline'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode as any)}
                  className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                    viewMode === mode
                      ? 'bg-white bg-opacity-10 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </button>
              ))}
            </div>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-3 py-2 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="name">Sort by Name</option>
              <option value="company">Sort by Company</option>
              <option value="last_contact">Sort by Last Contact</option>
              <option value="trust_score">Sort by Trust Score</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex gap-6">
        {/* Contacts List */}
        <div className="flex-1">
          {isLoading ? (
            <div className="glass-card p-8 text-center">
              <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-gray-400">Loading contacts...</p>
            </div>
          ) : sortedContacts.length === 0 ? (
            <div className="glass-card p-8 text-center">
              <div className="text-6xl mb-4">🤝</div>
              <h3 className="text-xl font-semibold text-white mb-2">No contacts found</h3>
              <p className="text-gray-400 mb-6">
                {searchQuery || filterWarmth.length > 0
                  ? 'Try adjusting your search or filters'
                  : 'Start building your network by importing or adding contacts'
                }
              </p>
              {!searchQuery && filterWarmth.length === 0 && (
                <button
                  onClick={() => setShowImportModal(true)}
                  className="btn btn-primary"
                >
                  Import Your First Contacts
                </button>
              )}
            </div>
          ) : (
            <div className={viewMode === 'cards' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-3'}>
              {sortedContacts.map((contact) => (
                <div
                  key={contact.id}
                  onClick={() => actions.selectContact(contact)}
                  className={`glass-card p-4 cursor-pointer transition-all hover:bg-white hover:bg-opacity-10 ${
                    selectedContact?.id === contact.id ? 'ring-2 ring-blue-500' : ''
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold text-white">{contact.name}</h3>
                      {contact.company && (
                        <p className="text-sm text-gray-400">{contact.company}</p>
                      )}
                      {contact.title && (
                        <p className="text-xs text-gray-500">{contact.title}</p>
                      )}
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getWarmthColor(contact.warmth)} bg-opacity-20`}>
                        {contact.warmth}
                      </span>
                      {contact.trust_score && (
                        <div className="text-xs text-gray-400">
                          Trust: {Math.round(contact.trust_score * 100)}%
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-1 text-xs text-gray-400">
                    {contact.email && (
                      <div className="flex items-center">
                        <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                          <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                        </svg>
                        {contact.email}
                      </div>
                    )}
                    {contact.last_contact && (
                      <div className="flex items-center">
                        <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                        </svg>
                        Last contact: {new Date(contact.last_contact).toLocaleDateString()}
                      </div>
                    )}
                  </div>

                  {contact.tags && contact.tags.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {contact.tags.slice(0, 3).map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-1 bg-blue-500 bg-opacity-20 text-blue-300 rounded text-xs"
                        >
                          {tag}
                        </span>
                      ))}
                      {contact.tags.length > 3 && (
                        <span className="px-2 py-1 bg-gray-500 bg-opacity-20 text-gray-400 rounded text-xs">
                          +{contact.tags.length - 3}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Trust Panel */}
        {selectedContact && (
          <div className="w-80">
            <TrustPanel contact={selectedContact} />
          </div>
        )}
      </div>

      {/* Import Modal */}
      <ContactImportModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onImportComplete={handleImportComplete}
      />
    </div>
  );
};

export default ContactsPage;