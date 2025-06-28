import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Users, Target, Brain, TrendingUp, Plus, Network, LogOut } from 'lucide-react'
import axios from 'axios'

interface User {
  id: string
  email: string
  subscription_tier: string
  goals_count: number
  contacts_count: number
  ai_suggestions_used: number
}

interface DashboardProps {
  user: User
}

interface Goal {
  id: string
  title: string
  description: string
  goal_type: string
  status: string
  progress_percentage: number
}

interface Contact {
  id: string
  name: string
  email: string
  company: string
  warmth_level: string
  last_interaction_date: string
}

interface AISuggestion {
  id: string
  title: string
  content: string
  suggestion_type: string
  confidence_score: number
}

const Dashboard = ({ user }: DashboardProps) => {
  const [goals, setGoals] = useState<Goal[]>([])
  const [contacts, setContacts] = useState<Contact[]>([])
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [goalsRes, contactsRes, suggestionsRes] = await Promise.all([
        axios.get('/api/goals'),
        axios.get('/api/contacts'),
        axios.get('/api/ai-suggestions')
      ])
      
      setGoals(goalsRes.data.slice(0, 3)) // Show latest 3
      setContacts(contactsRes.data.slice(0, 5)) // Show latest 5
      setSuggestions(suggestionsRes.data.slice(0, 3)) // Show latest 3
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
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
                <Link to="/dashboard" className="text-indigo-600 border-b-2 border-indigo-600 pb-1">
                  Dashboard
                </Link>
                <Link to="/goals" className="text-gray-600 hover:text-indigo-600 transition-colors">
                  Goals
                </Link>
                <Link to="/contacts" className="text-gray-600 hover:text-indigo-600 transition-colors">
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
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user.email.split('@')[0]}!
          </h1>
          <p className="text-gray-600">
            Here's what's happening with your relationship intelligence platform.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Target className="w-6 h-6 text-indigo-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Goals</p>
                <p className="text-2xl font-bold text-gray-900">{user.goals_count}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Contacts</p>
                <p className="text-2xl font-bold text-gray-900">{user.contacts_count}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Brain className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">AI Insights</p>
                <p className="text-2xl font-bold text-gray-900">{user.ai_suggestions_used}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Plan</p>
                <p className="text-lg font-bold text-gray-900 capitalize">{user.subscription_tier}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Goals */}
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Recent Goals</h2>
              <Link
                to="/goals"
                className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
              >
                View all
              </Link>
            </div>
            
            <div className="space-y-4">
              {goals.length > 0 ? (
                goals.map((goal) => (
                  <div key={goal.id} className="border-l-4 border-indigo-500 pl-4">
                    <h3 className="font-medium text-gray-900">{goal.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{goal.description}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full">
                        {goal.goal_type}
                      </span>
                      <span className="text-sm text-gray-500">{goal.progress_percentage}% complete</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">No goals yet</p>
                  <Link
                    to="/goals"
                    className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Create your first goal
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Recent Contacts */}
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Recent Contacts</h2>
              <Link
                to="/contacts"
                className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
              >
                View all
              </Link>
            </div>
            
            <div className="space-y-4">
              {contacts.length > 0 ? (
                contacts.map((contact) => (
                  <div key={contact.id} className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                      {contact.name.charAt(0)}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{contact.name}</h3>
                      <p className="text-sm text-gray-600">{contact.company || contact.email}</p>
                    </div>
                    <div className="text-right">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        contact.warmth_level === 'hot' ? 'bg-red-100 text-red-800' :
                        contact.warmth_level === 'warm' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {contact.warmth_level}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">No contacts yet</p>
                  <Link
                    to="/contacts"
                    className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add your first contact
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* AI Suggestions */}
        {suggestions.length > 0 && (
          <div className="mt-8 bg-white rounded-xl p-6 shadow-sm border">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">AI Suggestions</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {suggestions.map((suggestion) => (
                <div key={suggestion.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{suggestion.title}</h3>
                    <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                      {Math.round(suggestion.confidence_score * 100)}%
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{suggestion.content}</p>
                  <span className="text-xs text-indigo-600 mt-2 block">
                    {suggestion.suggestion_type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard