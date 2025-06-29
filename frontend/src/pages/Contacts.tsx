import { useState, useEffect } from 'react'
import { User, Contact } from '../types'
import { apiService } from '../services/api'
import Navigation from '../components/Navigation'

interface ContactsProps {
  user: User
  onLogout: () => void
}

export default function Contacts({ user, onLogout }: ContactsProps) {
  const [contacts, setContacts] = useState<Contact[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [newContact, setNewContact] = useState({
    name: '',
    email: '',
    company: '',
    title: '',
    notes: ''
  })

  useEffect(() => {
    loadContacts()
  }, [])

  const loadContacts = async () => {
    const response = await apiService.getContacts()
    if (response.success && response.data) {
      setContacts(response.data)
    }
    setLoading(false)
  }

  const handleAddContact = async (e: React.FormEvent) => {
    e.preventDefault()
    const response = await apiService.createContact(newContact)
    if (response.success && response.data) {
      setContacts([...contacts, response.data])
      setNewContact({ name: '', email: '', company: '', title: '', notes: '' })
      setShowAddForm(false)
    }
  }

  const filteredContacts = contacts.filter(contact =>
    contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.company?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getWarmthColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'hot': return 'bg-red-500'
      case 'warm': return 'bg-orange-500'
      case 'cold': return 'bg-blue-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="min-h-screen">
      <Navigation user={user} onLogout={onLogout} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Contacts</h1>
            <p className="text-gray-300">Manage your relationship network</p>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="glass-button"
          >
            <svg className="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add Contact
          </button>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <input
              type="text"
              placeholder="Search contacts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-3 pl-10 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white placeholder-gray-400"
            />
            <svg className="absolute left-3 top-3.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Add Contact Form */}
        {showAddForm && (
          <div className="glass-card p-6 mb-6">
            <h2 className="text-xl font-semibold text-white mb-4">Add New Contact</h2>
            <form onSubmit={handleAddContact} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Name *"
                value={newContact.name}
                onChange={(e) => setNewContact({ ...newContact, name: e.target.value })}
                className="px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white placeholder-gray-400"
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={newContact.email}
                onChange={(e) => setNewContact({ ...newContact, email: e.target.value })}
                className="px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white placeholder-gray-400"
              />
              <input
                type="text"
                placeholder="Company"
                value={newContact.company}
                onChange={(e) => setNewContact({ ...newContact, company: e.target.value })}
                className="px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white placeholder-gray-400"
              />
              <input
                type="text"
                placeholder="Title"
                value={newContact.title}
                onChange={(e) => setNewContact({ ...newContact, title: e.target.value })}
                className="px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white placeholder-gray-400"
              />
              <textarea
                placeholder="Notes"
                value={newContact.notes}
                onChange={(e) => setNewContact({ ...newContact, notes: e.target.value })}
                className="md:col-span-2 px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white placeholder-gray-400 resize-none"
                rows={3}
              />
              <div className="md:col-span-2 flex space-x-4">
                <button
                  type="submit"
                  className="glass-button bg-blue-500/20 hover:bg-blue-500/30"
                >
                  Add Contact
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="glass-button"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Contacts Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
            <p className="text-gray-300 mt-4">Loading contacts...</p>
          </div>
        ) : filteredContacts.length === 0 ? (
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h3 className="text-xl font-semibold text-white mb-2">No contacts found</h3>
            <p className="text-gray-400">
              {searchTerm ? 'Try adjusting your search terms' : 'Start building your relationship network'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredContacts.map((contact) => (
              <div key={contact.id} className="glass-card p-6 hover:bg-white/5 transition-colors">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white">{contact.name}</h3>
                    {contact.title && contact.company && (
                      <p className="text-gray-400 text-sm">
                        {contact.title} at {contact.company}
                      </p>
                    )}
                  </div>
                  <div className={`w-3 h-3 rounded-full ${getWarmthColor(contact.warmth_level)}`} 
                       title={`Warmth: ${contact.warmth_level}`} />
                </div>
                
                {contact.email && (
                  <div className="flex items-center space-x-2 text-gray-300 text-sm mb-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                    </svg>
                    <span className="truncate">{contact.email}</span>
                  </div>
                )}
                
                <div className="flex items-center justify-between text-sm text-gray-400 mt-4">
                  <span>Interactions: {contact.interaction_count}</span>
                  {contact.last_interaction_date && (
                    <span>Last: {new Date(contact.last_interaction_date).toLocaleDateString()}</span>
                  )}
                </div>
                
                {contact.notes && (
                  <p className="text-gray-300 text-sm mt-3 line-clamp-2">{contact.notes}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}