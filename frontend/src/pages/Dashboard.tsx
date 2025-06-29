import { Link } from 'react-router-dom'
import { User } from '../types'
import { useDashboardAnalytics } from '../hooks/useApi'
import Navigation from '../components/Navigation'
import { LoadingStats } from '../components/LoadingSpinner'
import ErrorBoundary from '../components/ErrorBoundary'

interface DashboardProps {
  user: User
  onLogout: () => void
}

export default function Dashboard({ user, onLogout }: DashboardProps) {
  const { 
    data: analytics, 
    isLoading, 
    error, 
    refetch 
  } = useDashboardAnalytics()

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
        <Navigation user={user} onLogout={onLogout} />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8" role="main">
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="backdrop-blur-xl bg-white/5 border border-red-500/20 rounded-2xl p-8 max-w-md w-full text-center">
              <div className="text-red-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.314 15.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-white font-semibold text-lg mb-2">Unable to load dashboard</h3>
              <p className="text-gray-300 text-sm mb-6">
                We couldn't fetch your analytics data. Please try again.
              </p>
              <button
                onClick={() => refetch()}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  return (
    <ErrorBoundary>
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
          {isLoading ? (
            <LoadingStats />
          ) : (
            <section className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8" aria-label="Dashboard statistics">
              {/* Contacts Card */}
              <div className="glass-card p-4 sm:p-6 focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-900">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
                  <div className="min-w-0 flex-1">
                    <p className="text-gray-400 text-xs sm:text-sm font-medium">Contacts</p>
                    <p className="text-xl sm:text-2xl font-bold text-white" role="status" aria-live="polite">
                      <span aria-label={`${analytics?.contacts || 0} contacts`}>{analytics?.contacts || 0}</span>
                    </p>
                  </div>
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 sm:w-6 sm:h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Goals Card */}
              <div className="glass-card p-4 sm:p-6 focus-within:ring-2 focus-within:ring-purple-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-900">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
                  <div className="min-w-0 flex-1">
                    <p className="text-gray-400 text-xs sm:text-sm font-medium">Goals</p>
                    <p className="text-xl sm:text-2xl font-bold text-white" role="status" aria-live="polite">
                      <span aria-label={`${analytics?.goals || 0} goals`}>{analytics?.goals || 0}</span>
                    </p>
                  </div>
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 sm:w-6 sm:h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Interactions Card */}
              <div className="glass-card p-4 sm:p-6 focus-within:ring-2 focus-within:ring-green-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-900">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
                  <div className="min-w-0 flex-1">
                    <p className="text-gray-400 text-xs sm:text-sm font-medium">Interactions</p>
                    <p className="text-xl sm:text-2xl font-bold text-white" role="status" aria-live="polite">
                      <span aria-label={`${analytics?.interactions || 0} interactions`}>{analytics?.interactions || 0}</span>
                    </p>
                  </div>
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 sm:w-6 sm:h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* AI Suggestions Card */}
              <div className="glass-card p-4 sm:p-6 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-900">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
                  <div className="min-w-0 flex-1">
                    <p className="text-gray-400 text-xs sm:text-sm font-medium">AI Insights</p>
                    <p className="text-xl sm:text-2xl font-bold text-white" role="status" aria-live="polite">
                      <span aria-label={`${analytics?.ai_suggestions || 0} AI suggestions`}>{analytics?.ai_suggestions || 0}</span>
                    </p>
                  </div>
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-indigo-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 sm:w-6 sm:h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Quick Actions */}
          <section className="mb-6 sm:mb-8" aria-label="Quick actions">
            <h2 className="text-lg sm:text-xl font-bold text-white mb-4">Quick Actions</h2>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              <Link
                to="/contacts"
                className="glass-card p-4 sm:p-6 hover:bg-white/10 transition-colors group focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900 rounded-xl"
                aria-label="Add new contact"
              >
                <div className="text-center">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:bg-blue-500/30 transition-colors">
                    <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                  </div>
                  <p className="text-white font-medium text-sm">Add Contact</p>
                </div>
              </Link>

              <Link
                to="/goals"
                className="glass-card p-4 sm:p-6 hover:bg-white/10 transition-colors group focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-gray-900 rounded-xl"
                aria-label="Create new goal"
              >
                <div className="text-center">
                  <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:bg-purple-500/30 transition-colors">
                    <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                  <p className="text-white font-medium text-sm">Create Goal</p>
                </div>
              </Link>

              <button
                className="glass-card p-4 sm:p-6 hover:bg-white/10 transition-colors group focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-gray-900 rounded-xl text-left"
                aria-label="Get AI insights"
              >
                <div className="text-center">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:bg-green-500/30 transition-colors">
                    <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <p className="text-white font-medium text-sm">AI Insights</p>
                </div>
              </button>

              <button
                onClick={() => refetch()}
                className="glass-card p-4 sm:p-6 hover:bg-white/10 transition-colors group focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-900 rounded-xl text-left"
                aria-label="Refresh dashboard data"
              >
                <div className="text-center">
                  <div className="w-10 h-10 bg-indigo-500/20 rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:bg-indigo-500/30 transition-colors">
                    <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </div>
                  <p className="text-white font-medium text-sm">Refresh</p>
                </div>
              </button>
            </div>
          </section>

          {/* Recent Activity */}
          <section aria-label="Recent activity">
            <h2 className="text-lg sm:text-xl font-bold text-white mb-4">Recent Activity</h2>
            
            {analytics?.recent_activity ? (
              <div className="glass-card p-6 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-blue-400">{analytics.recent_activity.contacts_added}</p>
                    <p className="text-gray-400 text-sm">Contacts Added</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-purple-400">{analytics.recent_activity.goals_completed}</p>
                    <p className="text-gray-400 text-sm">Goals Completed</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-green-400">{analytics.recent_activity.messages_sent}</p>
                    <p className="text-gray-400 text-sm">Messages Sent</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="glass-card p-6 text-center">
                <p className="text-gray-400">No recent activity to display</p>
                <p className="text-gray-500 text-sm mt-2">Start by adding contacts or creating goals</p>
              </div>
            )}
          </section>
        </main>
      </div>
    </ErrorBoundary>
  )
}