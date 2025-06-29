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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      <Navigation user={user} onLogout={onLogout} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8" role="main">
        {/* Header */}
        <header className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6 sm:mb-8">
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-2">
              Contacts
            </h1>
            <p className="text-gray-300 text-sm sm:text-base">
              Manage your relationship network
            </p>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="glass-button interactive-element flex items-center justify-center space-x-2 whitespace-nowrap"
            aria-label={showAddForm ? 'Cancel adding contact' : 'Add new contact'}
            aria-expanded={showAddForm}
          >
            <svg 
              className="w-5 h-5 flex-shrink-0" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24" 
              aria-hidden="true"
            >
              {showAddForm ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              )}
            </svg>
            <span className="hidden xs:inline">{showAddForm ? 'Cancel' : 'Add Contact'}</span>
          </button>
        </header>

        {/* Search */}
        <section className="mb-6" aria-label="Search contacts">
          <div className="relative">
            <label htmlFor="contact-search" className="sr-only">
              Search contacts by name, email, or company
            </label>
            <input
              id="contact-search"
              type="text"
              placeholder="Search contacts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-input pl-10"
              aria-describedby="search-help"
              autoComplete="off"
            />
            <svg 
              className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24" 
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <div id="search-help" className="sr-only">
              Search by contact name, email address, or company name
            </div>
          </div>
          {searchTerm && (
            <div className="mt-2 text-sm text-gray-400" role="status" aria-live="polite">
              {filteredContacts.length === 0 
                ? `No contacts found for "${searchTerm}"`
                : `${filteredContacts.length} contact${filteredContacts.length === 1 ? '' : 's'} found`
              }
            </div>
          )}
        </section>

        {/* Add Contact Form */}
        {showAddForm && (
          <section className="glass-card p-4 sm:p-6 mb-6" aria-label="Add new contact form">
            <h2 className="text-lg sm:text-xl font-semibold text-white mb-4 sm:mb-6">Add New Contact</h2>
            <form onSubmit={handleAddContact} className="space-y-4" noValidate>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="contact-name" className="block text-sm font-medium text-gray-300 mb-2">
                    Name <span className="text-red-400" aria-label="required">*</span>
                  </label>
                  <input
                    id="contact-name"
                    type="text"
                    value={newContact.name}
                    onChange={(e) => setNewContact({ ...newContact, name: e.target.value })}
                    className="form-input"
                    required
                    aria-required="true"
                    aria-describedby="name-error"
                    autoComplete="name"
                  />
                  <div id="name-error" className="sr-only" role="alert">
                    {!newContact.name.trim() && 'Name is required'}
                  </div>
                </div>

                <div>
                  <label htmlFor="contact-email" className="block text-sm font-medium text-gray-300 mb-2">
                    Email
                  </label>
                  <input
                    id="contact-email"
                    type="email"
                    value={newContact.email}
                    onChange={(e) => setNewContact({ ...newContact, email: e.target.value })}
                    className="form-input"
                    autoComplete="email"
                    aria-describedby="email-help"
                  />
                  <div id="email-help" className="sr-only">
                    Optional: Contact's email address for communication
                  </div>
                </div>

                <div>
                  <label htmlFor="contact-company" className="block text-sm font-medium text-gray-300 mb-2">
                    Company
                  </label>
                  <input
                    id="contact-company"
                    type="text"
                    value={newContact.company}
                    onChange={(e) => setNewContact({ ...newContact, company: e.target.value })}
                    className="form-input"
                    autoComplete="organization"
                  />
                </div>

                <div>
                  <label htmlFor="contact-title" className="block text-sm font-medium text-gray-300 mb-2">
                    Job Title
                  </label>
                  <input
                    id="contact-title"
                    type="text"
                    value={newContact.title}
                    onChange={(e) => setNewContact({ ...newContact, title: e.target.value })}
                    className="form-input"
                    autoComplete="organization-title"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="contact-notes" className="block text-sm font-medium text-gray-300 mb-2">
                  Notes
                </label>
                <textarea
                  id="contact-notes"
                  value={newContact.notes}
                  onChange={(e) => setNewContact({ ...newContact, notes: e.target.value })}
                  className="form-input resize-none"
                  rows={3}
                  aria-describedby="notes-help"
                />
                <div id="notes-help" className="text-xs text-gray-500 mt-1">
                  Optional: Add any additional information about this contact
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 pt-2">
                <button
                  type="submit"
                  className="glass-button interactive-element bg-blue-500/20 hover:bg-blue-500/30 border-blue-500/30 order-2 sm:order-1"
                  disabled={!newContact.name.trim()}
                  aria-describedby="submit-help"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add Contact
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowAddForm(false)
                    setNewContact({ name: '', email: '', company: '', title: '', notes: '' })
                  }}
                  className="glass-button interactive-element order-1 sm:order-2"
                  aria-label="Cancel adding contact and close form"
                >
                  Cancel
                </button>
                <div id="submit-help" className="sr-only">
                  {!newContact.name.trim() ? 'Please enter a name to add the contact' : 'Click to add this contact to your network'}
                </div>
              </div>
            </form>
          </section>
        )}

        {/* Contacts Grid */}
        <section aria-label="Contacts list" aria-live="polite">
          {loading ? (
            <div className="text-center py-12" role="status" aria-label="Loading contacts">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto" aria-hidden="true"></div>
              <p className="text-gray-300 mt-4">Loading contacts...</p>
            </div>
          ) : filteredContacts.length === 0 ? (
            <div className="text-center py-12">
              <svg 
                className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24" 
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <h3 className="text-lg sm:text-xl font-semibold text-white mb-2">No contacts found</h3>
              <p className="text-gray-400 text-sm sm:text-base">
                {searchTerm ? 'Try adjusting your search terms' : 'Start building your relationship network'}
              </p>
              {!searchTerm && (
                <button
                  onClick={() => setShowAddForm(true)}
                  className="glass-button interactive-element mt-4 bg-blue-500/20 hover:bg-blue-500/30"
                  aria-label="Add your first contact"
                >
                  Add Your First Contact
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {filteredContacts.map((contact) => (
                <article 
                  key={contact.id} 
                  className="glass-card p-4 sm:p-6 hover:bg-white/5 transition-all duration-200 focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-900"
                  role="article"
                  aria-labelledby={`contact-name-${contact.id}`}
                  tabIndex={0}
                >
                  <header className="flex items-start justify-between mb-3 sm:mb-4">
                    <div className="flex-1 min-w-0">
                      <h3 
                        id={`contact-name-${contact.id}`}
                        className="text-base sm:text-lg font-semibold text-white truncate"
                      >
                        {contact.name}
                      </h3>
                      {(contact.title || contact.company) && (
                        <p className="text-gray-400 text-xs sm:text-sm mt-1 truncate" title={`${contact.title || ''} ${contact.title && contact.company ? 'at' : ''} ${contact.company || ''}`}>
                          {contact.title && contact.company 
                            ? `${contact.title} at ${contact.company}`
                            : contact.title || contact.company
                          }
                        </p>
                      )}
                    </div>
                    <div 
                      className={`w-3 h-3 rounded-full ${getWarmthColor(contact.warmth_level)} flex-shrink-0 ml-2`}
                      role="img"
                      aria-label={`Relationship warmth: ${contact.warmth_level}`}
                      title={`Warmth level: ${contact.warmth_level}`}
                    />
                  </header>
                  
                  {contact.email && (
                    <div className="flex items-center space-x-2 text-gray-300 text-xs sm:text-sm mb-3">
                      <svg 
                        className="w-4 h-4 flex-shrink-0" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24" 
                        aria-hidden="true"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                      </svg>
                      <a 
                        href={`mailto:${contact.email}`}
                        className="truncate hover:text-blue-400 transition-colors focus:outline-none focus:text-blue-400"
                        aria-label={`Send email to ${contact.name} at ${contact.email}`}
                      >
                        {contact.email}
                      </a>
                    </div>
                  )}
                  
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between text-xs sm:text-sm text-gray-400 gap-1 sm:gap-2 mt-3 sm:mt-4 pt-3 border-t border-gray-700/50">
                    <span aria-label={`${contact.interaction_count} interactions with this contact`}>
                      {contact.interaction_count} interaction{contact.interaction_count !== 1 ? 's' : ''}
                    </span>
                    {contact.last_interaction_date && (
                      <span className="truncate" title={`Last interaction: ${new Date(contact.last_interaction_date).toLocaleDateString()}`}>
                        Last: {new Date(contact.last_interaction_date).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  
                  {contact.notes && (
                    <div className="mt-3">
                      <p 
                        className="text-gray-300 text-xs sm:text-sm line-clamp-2"
                        title={contact.notes}
                        aria-label={`Notes about ${contact.name}: ${contact.notes}`}
                      >
                        {contact.notes}
                      </p>
                    </div>
                  )}

                  <div className="flex gap-2 mt-4 pt-3 border-t border-gray-700/30">
                    <button
                      className="flex-1 glass-button interactive-element text-xs sm:text-sm py-2 px-3 bg-blue-500/10 hover:bg-blue-500/20"
                      aria-label={`View details for ${contact.name}`}
                    >
                      View
                    </button>
                    <button
                      className="flex-1 glass-button interactive-element text-xs sm:text-sm py-2 px-3 bg-green-500/10 hover:bg-green-500/20"
                      aria-label={`Contact ${contact.name}`}
                    >
                      Contact
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}