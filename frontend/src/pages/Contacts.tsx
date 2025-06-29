import React, { useState, useEffect } from 'react';

interface Contact {
  id: string;
  name: string;
  email?: string;
  company?: string;
  title?: string;
  relationship_type?: string;
  warmth_level?: string;
  last_interaction_date?: string;
  notes?: string;
}

const Contacts: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const response = await fetch('/api/contacts');
        if (response.ok) {
          const data = await response.json();
          setContacts(data);
        }
      } catch (error) {
        console.error('Failed to fetch contacts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchContacts();
  }, []);

  const filteredContacts = contacts.filter(contact => {
    const matchesSearch = contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (contact.email?.toLowerCase().includes(searchTerm.toLowerCase())) ||
                         (contact.company?.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesFilter = filterType === 'all' || contact.relationship_type === filterType;
    
    return matchesSearch && matchesFilter;
  });

  const getWarmthColor = (level?: string) => {
    switch (level) {
      case 'warm': return 'bg-green-500';
      case 'cool': return 'bg-yellow-500';
      case 'cold': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Background Effects */}
      <div className="fixed inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 pointer-events-none"></div>
      
      {/* Header */}
      <header className="relative z-10 p-6 border-b border-white/10">
        <nav className="flex justify-between items-center max-w-7xl mx-auto">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
            Contacts
          </div>
          <div className="space-x-4">
            <a href="/app/dashboard" className="text-gray-300 hover:text-white transition-colors">Dashboard</a>
            <a href="/app/goals" className="text-gray-300 hover:text-white transition-colors">Goals</a>
            <a href="/app/intelligence" className="text-gray-300 hover:text-white transition-colors">Intelligence</a>
            <a href="/logout" className="text-gray-300 hover:text-white transition-colors">Logout</a>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Page Header */}
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold">
                Your <span className="bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">Professional Network</span>
              </h1>
              <p className="text-xl text-gray-300 mt-2">
                Manage and strengthen your meaningful relationships
              </p>
            </div>
            <button className="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-3 rounded-lg text-white font-semibold hover:from-blue-600 hover:to-purple-700 transition-all">
              Add Contact
            </button>
          </div>

          {/* Search and Filters */}
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search contacts by name, email, or company..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Relationships</option>
                <option value="investor">Investors</option>
                <option value="partner">Partners</option>
                <option value="mentor">Mentors</option>
                <option value="employee">Team Members</option>
                <option value="customer">Customers</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          {/* Contact Stats */}
          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <h3 className="text-sm text-gray-400">Total Contacts</h3>
              <p className="text-2xl font-bold text-white">{contacts.length}</p>
            </div>
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <h3 className="text-sm text-gray-400">Warm Relationships</h3>
              <p className="text-2xl font-bold text-green-400">
                {contacts.filter(c => c.warmth_level === 'warm').length}
              </p>
            </div>
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <h3 className="text-sm text-gray-400">Recent Interactions</h3>
              <p className="text-2xl font-bold text-blue-400">
                {contacts.filter(c => c.last_interaction_date).length}
              </p>
            </div>
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <h3 className="text-sm text-gray-400">Need Follow-up</h3>
              <p className="text-2xl font-bold text-yellow-400">
                {contacts.filter(c => c.warmth_level === 'cold').length}
              </p>
            </div>
          </div>

          {/* Contacts Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredContacts.map((contact) => (
              <div key={contact.id} className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">
                        {contact.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">{contact.name}</h3>
                      {contact.company && (
                        <p className="text-sm text-gray-400">{contact.title} at {contact.company}</p>
                      )}
                    </div>
                  </div>
                  <div className={`w-3 h-3 rounded-full ${getWarmthColor(contact.warmth_level)}`}></div>
                </div>
                
                {contact.email && (
                  <p className="text-sm text-gray-300 mb-2">📧 {contact.email}</p>
                )}
                
                {contact.relationship_type && (
                  <p className="text-sm text-purple-400 mb-2">
                    🤝 {contact.relationship_type.charAt(0).toUpperCase() + contact.relationship_type.slice(1)}
                  </p>
                )}
                
                {contact.last_interaction_date && (
                  <p className="text-sm text-gray-400 mb-4">
                    💬 Last contact: {new Date(contact.last_interaction_date).toLocaleDateString()}
                  </p>
                )}
                
                {contact.notes && (
                  <p className="text-sm text-gray-300 line-clamp-2">{contact.notes}</p>
                )}
                
                <div className="flex space-x-2 mt-4">
                  <button className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 px-3 py-2 rounded-lg text-sm font-medium hover:from-blue-600 hover:to-purple-700 transition-all">
                    Contact
                  </button>
                  <button className="flex-1 border border-gray-600 px-3 py-2 rounded-lg text-sm font-medium hover:border-gray-500 hover:bg-gray-800/50 transition-all">
                    Edit
                  </button>
                </div>
              </div>
            ))}
          </div>

          {filteredContacts.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">👥</div>
              <h3 className="text-xl font-semibold text-gray-300 mb-2">No contacts found</h3>
              <p className="text-gray-400">
                {searchTerm || filterType !== 'all' 
                  ? 'Try adjusting your search or filters'
                  : 'Start building your network by adding your first contact'
                }
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Contacts;