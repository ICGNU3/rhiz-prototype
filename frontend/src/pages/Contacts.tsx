import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Users, Plus, Search, Filter, Network, LogOut, Mail, Building, Calendar } from 'lucide-react'
import axios from 'axios'

interface User {
  id: string
  email: string
}

interface ContactsProps {
  user: User
}

interface Contact {
  id: string
  name: string
  email: string
  phone: string
  company: string
  title: string
  relationship_type: string
  warmth_level: string
  warmth_status: number
  last_interaction_date: string
  interaction_count: number
  notes: string
  location: string
}

const Contacts = ({ user }: ContactsProps) => {
  const [contacts, setContacts] = useState<Contact[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')

  useEffect(() => {
    loadContacts()
  }, [])

  const loadContacts = async () => {
    try {
      const response = await axios.get('/api/contacts')
      setContacts(response.data)
    } catch (error) {
      console.error('Failed to load contacts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout')
      window.location.href = '/'
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const filteredContacts = contacts.filter(contact => {
    const matchesSearch = contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         contact.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         contact.company.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesFilter = filterType === 'all' || contact.warmth_level === filterType
    
    return matchesSearch && matchesFilter
  })

  const getWarmthColor = (warmthLevel: string) => {
    switch (warmthLevel) {
      case 'hot': return 'bg-red-100 text-red-800'
      case 'warm': return 'bg-yellow-100 text-yellow-800'
      case 'cold': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-2">
                <Network className="w-8 h-8 text-indigo-600" />
                <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  Rhiz
                </span>
              </div>
              
              <div className="hidden md:flex items-center space-x-8">
                <Link to="/dashboard" className="text-gray-600 hover:text-indigo-600 transition-colors">
                  Dashboard
                </Link>
                <Link to="/goals" className="text-gray-600 hover:text-indigo-600 transition-colors">
                  Goals
                </Link>
                <Link to="/contacts" className="text-indigo-600 border-b-2 border-indigo-600 pb-1">
                  Contacts
                </Link>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user.email}</span>
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-red-600 transition-colors"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Contacts</h1>
            <p className="text-gray-600">
              Manage your professional relationships and connections
            </p>
          </div>
          <button className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2">
            <Plus className="w-5 h-5" />
            <span>Add Contact</span>
          </button>
        </div>

        {/* Filters and Search */}
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search contacts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent"
              />
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Filter className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="pl-10 pr-8 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent"
                >
                  <option value="all">All Contacts</option>
                  <option value="hot">Hot</option>
                  <option value="warm">Warm</option>
                  <option value="cold">Cold</option>
                </select>
              </div>
              
              <div className="text-sm text-gray-600">
                {filteredContacts.length} contacts
              </div>
            </div>
          </div>
        </div>

        {/* Contacts List */}
        {filteredContacts.length > 0 ? (
          <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <div className="divide-y divide-gray-200">
              {filteredContacts.map((contact) => (
                <div key={contact.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-6">
                    {/* Avatar */}
                    <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
                      {contact.name.charAt(0)}
                    </div>
                    
                    {/* Contact Info */}
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{contact.name}</h3>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getWarmthColor(contact.warmth_level)}`}>
                          {contact.warmth_level}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <Mail className="w-4 h-4" />
                          <span>{contact.email}</span>
                        </div>
                        
                        {contact.company && (
                          <div className="flex items-center space-x-2">
                            <Building className="w-4 h-4" />
                            <span>{contact.company}</span>
                          </div>
                        )}
                        
                        {contact.last_interaction_date && (
                          <div className="flex items-center space-x-2">
                            <Calendar className="w-4 h-4" />
                            <span>Last contact: {new Date(contact.last_interaction_date).toLocaleDateString()}</span>
                          </div>
                        )}
                      </div>
                      
                      {contact.notes && (
                        <p className="mt-3 text-sm text-gray-700 line-clamp-2">
                          {contact.notes}
                        </p>
                      )}
                      
                      <div className="mt-3 flex items-center space-x-4 text-xs text-gray-500">
                        {contact.relationship_type && (
                          <span className="px-2 py-1 bg-gray-100 rounded">
                            {contact.relationship_type}
                          </span>
                        )}
                        <span>{contact.interaction_count} interactions</span>
                        {contact.location && <span>{contact.location}</span>}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border p-12 text-center">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-6" />
            <h3 className="text-xl font-semibold text-gray-900 mb-3">
              {contacts.length === 0 ? 'No contacts yet' : 'No contacts match your search'}
            </h3>
            <p className="text-gray-600 mb-6">
              {contacts.length === 0 
                ? 'Start building your professional network by adding your first contact.' 
                : 'Try adjusting your search or filter criteria.'
              }
            </p>
            {contacts.length === 0 && (
              <button className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors inline-flex items-center space-x-2">
                <Plus className="w-5 h-5" />
                <span>Add Your First Contact</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default Contacts