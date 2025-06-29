import React, { useState } from 'react'
import { useContacts, useCreateContact, useDeleteContact } from '../hooks/useApi'
import LoadingSpinner, { LoadingTable } from './LoadingSpinner'
import { useToast } from './Toast'
import { Contact } from '../services/api'

// Example component demonstrating comprehensive error handling and loading states
export const ContactExample: React.FC = () => {
  const toast = useToast()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    title: ''
  })

  // Query with automatic error handling
  const { 
    data: contacts = [], 
    isLoading, 
    error, 
    refetch 
  } = useContacts()

  // Create mutation with success/error handling
  const createContactMutation = useCreateContact()
  
  // Delete mutation with confirmation
  const deleteContactMutation = useDeleteContact()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      await createContactMutation.mutateAsync(formData)
      
      // Success handled automatically by React Query + Toast
      toast.success('Contact added', `${formData.name} has been added to your network`)
      
      // Reset form
      setFormData({ name: '', email: '', company: '', title: '' })
      setShowForm(false)
      
    } catch (error) {
      // Error handled automatically by React Query + Toast
      console.error('Failed to create contact:', error)
    }
  }

  const handleDelete = async (contact: Contact) => {
    if (!confirm(`Delete ${contact.name}?`)) return
    
    try {
      await deleteContactMutation.mutateAsync(contact.id)
      toast.success('Contact deleted', `${contact.name} has been removed`)
    } catch (error) {
      // Error handled automatically
      console.error('Failed to delete contact:', error)
    }
  }

  // Error state with retry option
  if (error) {
    return (
      <div className="p-6 text-center">
        <div className="text-red-400 mb-4">
          <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-white font-semibold mb-2">Failed to load contacts</h3>
        <p className="text-gray-400 text-sm mb-4">
          There was a problem loading your contacts
        </p>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with loading indicator */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <h2 className="text-xl font-bold text-white">Contacts</h2>
          {isLoading && (
            <LoadingSpinner size="sm" variant="inline" />
          )}
        </div>
        
        <button
          onClick={() => setShowForm(!showForm)}
          disabled={createContactMutation.isPending}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center space-x-2"
        >
          {createContactMutation.isPending ? (
            <LoadingSpinner size="sm" variant="inline" />
          ) : (
            <span>Add Contact</span>
          )}
        </button>
      </div>

      {/* Create form with loading state */}
      {showForm && (
        <form onSubmit={handleSubmit} className="glass-card p-6 space-y-4">
          <h3 className="text-white font-semibold">Add New Contact</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Name"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              required
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            
            <input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            
            <input
              type="text"
              placeholder="Company"
              value={formData.company}
              onChange={(e) => setFormData({...formData, company: e.target.value})}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            
            <input
              type="text"
              placeholder="Title"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={createContactMutation.isPending}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center space-x-2"
            >
              {createContactMutation.isPending ? (
                <>
                  <LoadingSpinner size="sm" variant="inline" />
                  <span>Creating...</span>
                </>
              ) : (
                <span>Create Contact</span>
              )}
            </button>
            
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Contacts list with loading states */}
      <div className="glass-card p-6">
        {isLoading ? (
          <LoadingTable rows={5} />
        ) : contacts.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-400">No contacts yet</p>
            <p className="text-gray-500 text-sm mt-1">Add your first contact to get started</p>
          </div>
        ) : (
          <div className="space-y-3">
            {contacts.map((contact) => (
              <div key={contact.id} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div>
                  <h4 className="text-white font-medium">{contact.name}</h4>
                  <p className="text-gray-400 text-sm">
                    {contact.title && contact.company 
                      ? `${contact.title} at ${contact.company}`
                      : contact.company || contact.email
                    }
                  </p>
                </div>
                
                <button
                  onClick={() => handleDelete(contact)}
                  disabled={deleteContactMutation.isPending}
                  className="px-3 py-1 bg-red-600/20 hover:bg-red-600/30 disabled:opacity-50 text-red-400 text-sm rounded transition-colors"
                >
                  {deleteContactMutation.isPending ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ContactExample