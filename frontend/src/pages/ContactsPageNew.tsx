import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Users, Search, Filter, Plus, Mail, Phone, Building, MapPin, Calendar, Loader2, AlertCircle, Edit, Trash2 } from 'lucide-react';
import { contactsAPI, Contact } from '../services/api';

const ContactsPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterWarmth, setFilterWarmth] = useState<number | null>(null);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const queryClient = useQueryClient();

  // Fetch contacts with React Query
  const { 
    data: contacts = [], 
    isLoading: contactsLoading, 
    error: contactsError, 
    refetch: refetchContacts 
  } = useQuery({
    queryKey: ['contacts', { search: searchQuery, warmth: filterWarmth }],
    queryFn: async () => {
      const filters: any = {};
      if (searchQuery) filters.search = searchQuery;
      if (filterWarmth !== null) filters.warmth = filterWarmth;
      
      const response = await contactsAPI.getAll(filters);
      return response.data || [];
    },
    retry: 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Create contact mutation
  const createContactMutation = useMutation({
    mutationFn: contactsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      setShowCreateModal(false);
    },
    onError: (error) => {
      console.error('Failed to create contact:', error);
    },
  });

  // Update contact mutation
  const updateContactMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Contact> }) => 
      contactsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      setSelectedContact(null);
    },
    onError: (error) => {
      console.error('Failed to update contact:', error);
    },
  });

  // Delete contact mutation
  const deleteContactMutation = useMutation({
    mutationFn: contactsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      setSelectedContact(null);
    },
    onError: (error) => {
      console.error('Failed to delete contact:', error);
    },
  });

  const ContactCard: React.FC<{ contact: Contact }> = ({ contact }) => (
    <div 
      className="glass-card p-6 cursor-pointer transition-all duration-300 hover:scale-105 border border-white/10"
      onClick={() => setSelectedContact(contact)}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold text-lg">
              {contact.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h3 className="text-white font-semibold">{contact.name}</h3>
            {contact.title && (
              <p className="text-gray-400 text-sm">{contact.title}</p>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`px-3 py-1 rounded-full text-xs ${
            contact.warmth_status >= 8 ? 'bg-green-500/20 text-green-400' :
            contact.warmth_status >= 6 ? 'bg-yellow-500/20 text-yellow-400' :
            contact.warmth_status >= 3 ? 'bg-blue-500/20 text-blue-400' :
            'bg-gray-500/20 text-gray-400'
          }`}>
            {contact.warmth_label || 'Unknown'}
          </span>
        </div>
      </div>

      {contact.company && (
        <div className="flex items-center text-gray-400 text-sm mb-2">
          <Building className="w-4 h-4 mr-2" />
          {contact.company}
        </div>
      )}

      {contact.email && (
        <div className="flex items-center text-gray-400 text-sm mb-2">
          <Mail className="w-4 h-4 mr-2" />
          {contact.email}
        </div>
      )}

      {contact.location && (
        <div className="flex items-center text-gray-400 text-sm mb-4">
          <MapPin className="w-4 h-4 mr-2" />
          {contact.location}
        </div>
      )}

      <div className="flex items-center justify-between">
        <span className="text-gray-400 text-sm">
          Warmth: {contact.warmth_status}/10
        </span>
        <div className="flex space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedContact(contact);
            }}
            className="p-1 text-blue-400 hover:bg-blue-400/10 rounded"
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (confirm('Are you sure you want to delete this contact?')) {
                deleteContactMutation.mutate(contact.id);
              }
            }}
            className="p-1 text-red-400 hover:bg-red-400/10 rounded"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  // Loading state
  if (contactsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 flex items-center justify-center">
        <div className="glass-card p-8 flex items-center space-x-4">
          <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
          <span className="text-white text-lg">Loading contacts...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (contactsError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 flex items-center justify-center">
        <div className="glass-card p-8 flex flex-col items-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-400" />
          <div className="text-center">
            <h2 className="text-white text-xl font-semibold mb-2">Failed to load contacts</h2>
            <p className="text-gray-400 mb-4">Unable to fetch your contacts data</p>
            <button 
              onClick={() => refetchContacts()}
              className="glass-button px-6 py-2 rounded-lg text-blue-400 border border-blue-400/30 hover:bg-blue-400/10"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Contacts
            </h1>
            <p className="text-gray-300 mt-2">
              Manage your professional relationships
            </p>
          </div>
          <button 
            onClick={() => setShowCreateModal(true)}
            disabled={createContactMutation.isPending}
            className="glass-button px-6 py-3 rounded-lg text-blue-400 border border-blue-400/30 hover:bg-blue-400/10 flex items-center disabled:opacity-50"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add Contact
          </button>
        </div>

        {/* Filters */}
        <div className="glass-card p-6 mb-8">
          <div className="flex flex-wrap items-center space-x-4 space-y-2">
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search contacts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-400"
                />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={filterWarmth || ''}
                onChange={(e) => setFilterWarmth(e.target.value ? Number(e.target.value) : null)}
                className="bg-gray-800/50 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-400"
              >
                <option value="">All Warmth Levels</option>
                <option value="8">Hot (8-10)</option>
                <option value="6">Warm (6-7)</option>
                <option value="3">Cold (3-5)</option>
                <option value="1">Dormant (1-2)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Contacts Grid */}
        {contacts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {contacts.map(contact => (
              <ContactCard key={contact.id} contact={contact} />
            ))}
          </div>
        ) : (
          <div className="glass-card p-12 text-center">
            <Users className="w-16 h-16 mx-auto mb-4 text-gray-500" />
            <h3 className="text-white text-xl mb-2">No Contacts Found</h3>
            <p className="text-gray-400 mb-6">
              {searchQuery || filterWarmth ? 'Try adjusting your filters' : 'Add your first contact to get started'}
            </p>
            <button 
              onClick={() => setShowCreateModal(true)}
              className="glass-button px-6 py-3 rounded-lg text-blue-400 border border-blue-400/30 hover:bg-blue-400/10"
            >
              Add Your First Contact
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContactsPage;