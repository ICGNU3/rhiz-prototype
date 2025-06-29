import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { User, DashboardAnalytics } from '../types'
import { apiService } from '../services/api'
import Navigation from '../components/Navigation'

interface DashboardProps {
  user: User
  onLogout: () => void
}

export default function Dashboard({ user, onLogout }: DashboardProps) {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    const response = await apiService.getDashboardAnalytics()
    if (response.success && response.data) {
      setAnalytics(response.data)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      <Navigation user={user} onLogout={onLogout} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8" role="main">
        {/* Header */}
        <header className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-2">
            Welcome back, <span className="gradient-text">{user.email.split('@')[0]}</span>
          </h1>
          <p className="text-gray-300 text-sm sm:text-base">
            Here's your relationship intelligence overview
          </p>
        </header>

        {/* Stats Grid */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8" aria-label="Dashboard statistics">
          <div className="glass-card p-4 sm:p-6 focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-900">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
              <div className="min-w-0 flex-1">
                <p className="text-gray-400 text-xs sm:text-sm font-medium">Contacts</p>
                <p className="text-xl sm:text-2xl font-bold text-white" role="status" aria-live="polite">
                  {loading ? (
                    <span className="inline-block w-8 h-6 bg-gray-600 rounded animate-pulse" aria-label="Loading contacts count"></span>
                  ) : (
                    <span aria-label={`${analytics?.contacts || 0} contacts`}>{analytics?.contacts || 0}</span>
                  )}
                </p>
              </div>
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="glass-card p-4 sm:p-6 focus-within:ring-2 focus-within:ring-purple-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-900">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
              <div className="min-w-0 flex-1">
                <p className="text-gray-400 text-xs sm:text-sm font-medium">Goals</p>
                <p className="text-xl sm:text-2xl font-bold text-white" role="status" aria-live="polite">
                  {loading ? (
                    <span className="inline-block w-8 h-6 bg-gray-600 rounded animate-pulse" aria-label="Loading goals count"></span>
                  ) : (
                    <span aria-label={`${analytics?.goals || 0} goals`}>{analytics?.goals || 0}</span>
                  )}
                </p>
              </div>
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="glass-card p-4 sm:p-6 focus-within:ring-2 focus-within:ring-green-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-900">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
              <div className="min-w-0 flex-1">
                <p className="text-gray-400 text-xs sm:text-sm font-medium">Interactions</p>
                <p className="text-xl sm:text-2xl font-bold text-white" role="status" aria-live="polite">
                  {loading ? (
                    <span className="inline-block w-8 h-6 bg-gray-600 rounded animate-pulse" aria-label="Loading interactions count"></span>
                  ) : (
                    <span aria-label={`${analytics?.interactions || 0} interactions`}>{analytics?.interactions || 0}</span>
                  )}
                </p>
              </div>
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="glass-card p-4 sm:p-6 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-900">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
              <div className="min-w-0 flex-1">
                <p className="text-gray-400 text-xs sm:text-sm font-medium">AI Suggestions</p>
                <p className="text-xl sm:text-2xl font-bold text-white" role="status" aria-live="polite">
                  {loading ? (
                    <span className="inline-block w-8 h-6 bg-gray-600 rounded animate-pulse" aria-label="Loading AI suggestions count"></span>
                  ) : (
                    <span aria-label={`${analytics?.ai_suggestions || 0} AI suggestions`}>{analytics?.ai_suggestions || 0}</span>
                  )}
                </p>
              </div>
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-indigo-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Actions */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8" aria-label="Quick actions">
          <Link 
            to="/contacts" 
            className="glass-card p-4 sm:p-6 hover:bg-white/5 active:scale-[0.98] transition-all duration-200 group focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900 rounded-xl"
            aria-label="Go to contacts page to add new contacts"
          >
            <div className="flex items-center space-x-3 sm:space-x-4">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-500 rounded-lg flex items-center justify-center group-hover:bg-blue-400 group-active:scale-95 transition-all duration-200 flex-shrink-0">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-base sm:text-lg font-semibold text-white group-hover:text-blue-200 transition-colors">Add Contact</h3>
                <p className="text-gray-400 text-sm sm:text-base">Expand your network</p>
              </div>
            </div>
          </Link>

          <Link 
            to="/goals" 
            className="glass-card p-4 sm:p-6 hover:bg-white/5 active:scale-[0.98] transition-all duration-200 group focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900 rounded-xl"
            aria-label="Go to goals page to create new goals"
          >
            <div className="flex items-center space-x-3 sm:space-x-4">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-purple-500 rounded-lg flex items-center justify-center group-hover:bg-purple-400 group-active:scale-95 transition-all duration-200 flex-shrink-0">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-base sm:text-lg font-semibold text-white group-hover:text-purple-200 transition-colors">Create Goal</h3>
                <p className="text-gray-400 text-sm sm:text-base">Set new objectives</p>
              </div>
            </div>
          </Link>

          <Link 
            to="/intelligence" 
            className="glass-card p-4 sm:p-6 hover:bg-white/5 active:scale-[0.98] transition-all duration-200 group cursor-pointer focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-gray-900 rounded-xl"
            aria-label="Go to AI intelligence page for recommendations"
          >
            <div className="flex items-center space-x-3 sm:space-x-4">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-500 rounded-lg flex items-center justify-center group-hover:bg-green-400 group-active:scale-95 transition-all duration-200 flex-shrink-0">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="text-base sm:text-lg font-semibold text-white group-hover:text-green-200 transition-colors">AI Insights</h3>
                <p className="text-gray-400 text-sm sm:text-base">Get recommendations</p>
              </div>
            </div>
          </Link>
        </section>

        {/* Recent Activity */}
        <section className="glass-card p-4 sm:p-6" aria-label="Recent activity">
          <h2 className="text-lg sm:text-xl font-semibold text-white mb-4 sm:mb-6">Recent Activity</h2>
          <div className="space-y-3 sm:space-y-4">
            {analytics?.recent_activity ? (
              <>
                <div className="flex items-center justify-between py-3 border-b border-gray-700/50 last:border-b-0">
                  <div className="flex items-center space-x-3 min-w-0 flex-1">
                    <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <span className="text-gray-300 text-sm sm:text-base truncate">
                      Added {analytics.recent_activity.contacts_added} new contacts
                    </span>
                  </div>
                  <span className="text-gray-500 text-xs sm:text-sm flex-shrink-0 ml-2">Today</span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-gray-700/50 last:border-b-0">
                  <div className="flex items-center space-x-3 min-w-0 flex-1">
                    <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <span className="text-gray-300 text-sm sm:text-base truncate">
                      Completed {analytics.recent_activity.goals_completed} goals
                    </span>
                  </div>
                  <span className="text-gray-500 text-xs sm:text-sm flex-shrink-0 ml-2">This week</span>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <svg className="w-12 h-12 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p className="text-gray-400 text-sm sm:text-base">No recent activity to display</p>
                <p className="text-gray-500 text-xs sm:text-sm mt-1">Start by adding contacts or creating goals</p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}