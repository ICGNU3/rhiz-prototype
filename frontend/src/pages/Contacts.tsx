import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { contactsAPI } from '../services/api';
import { Users, Plus, Search, Filter } from 'lucide-react';

const Contacts: React.FC = () => {
  const { data: contacts = [], isLoading } = useQuery({
    queryKey: ['contacts'],
    queryFn: async () => {
      const response = await contactsAPI.getAll();
      return response.data;
    },
  });

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
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Your Network</h2>
          <p className="text-gray-400 mt-1">Manage and organize your professional connections</p>
        </div>
        <button className="glass-button-primary flex items-center space-x-2">
          <Plus size={18} />
          <span>Add Contact</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex space-x-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search contacts..."
            className="w-full pl-10 pr-4 py-3 bg-dark-card border border-dark-border rounded-lg text-white placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-colors"
          />
        </div>
        <button className="glass-button-secondary flex items-center space-x-2">
          <Filter size={18} />
          <span>Filter</span>
        </button>
      </div>

      {/* Contacts Grid */}
      {contacts.length === 0 ? (
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-500 mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">No contacts yet</h3>
          <p className="text-gray-400 mb-6">
            Start building your network by adding your first contact
          </p>
          <button className="glass-button-primary">
            Add Your First Contact
          </button>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {contacts.map((contact) => (
            <div
              key={contact.id}
              className="glass-card p-6 cursor-pointer hover:border-primary-500 transition-all duration-300"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-white mb-1">{contact.name}</h3>
                  {contact.title && (
                    <p className="text-sm text-gray-300">{contact.title}</p>
                  )}
                  {contact.company && (
                    <p className="text-sm text-gray-400">{contact.company}</p>
                  )}
                </div>
                <div className="flex items-center space-x-1">
                  <div className={`w-2 h-2 rounded-full ${
                    contact.warmth_status >= 4 ? 'bg-green-400' :
                    contact.warmth_status >= 3 ? 'bg-yellow-400' :
                    contact.warmth_status >= 2 ? 'bg-orange-400' : 'bg-gray-400'
                  }`}></div>
                  <span className="text-xs text-gray-400">{contact.warmth_label}</span>
                </div>
              </div>

              {contact.email && (
                <p className="text-sm text-gray-400 mb-2">{contact.email}</p>
              )}

              {contact.notes && (
                <p className="text-sm text-gray-300 line-clamp-2 mb-4">{contact.notes}</p>
              )}

              <div className="flex items-center justify-between pt-4 border-t border-dark-border">
                <span className="text-xs text-gray-400 capitalize">{contact.relationship_type}</span>
                <span className="text-xs text-primary-400">View details →</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Contacts;