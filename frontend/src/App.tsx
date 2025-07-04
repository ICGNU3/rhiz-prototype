import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { User } from './types'
import { apiService } from './services/api'
import ErrorBoundary from './components/ErrorBoundary'
import LoadingSpinner from './components/LoadingSpinner'
import QueryProvider from './providers/QueryProvider'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Contacts from './pages/Contacts'
import Goals from './pages/Goals'
import ContactUploadTest from './pages/ContactUploadTest'
import NotFound from './pages/NotFound'

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const userData = await apiService.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.log('User not authenticated')
      // User not authenticated, this is fine
    }
    setLoading(false)
  }

  const handleAuth = (userData: User) => {
    setUser(userData)
  }

  const handleLogout = () => {
    setUser(null)
    // Clear any client-side session data
    window.location.href = '/'
  }

  if (loading) {
    return (
      <ErrorBoundary>
        <LoadingSpinner 
          variant="overlay" 
          text="Initializing Rhiz..." 
        />
      </ErrorBoundary>
    )
  }

  return (
    <ErrorBoundary>
      <QueryProvider>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
          {/* Floating background orbs */}
          <div className="fixed inset-0 overflow-hidden pointer-events-none">
            <div className="floating-orb w-64 h-64 bg-blue-500 top-1/4 left-1/4"></div>
            <div className="floating-orb w-48 h-48 bg-purple-500 top-3/4 right-1/4" style={{animationDelay: '2s'}}></div>
            <div className="floating-orb w-32 h-32 bg-indigo-500 top-1/2 right-1/3" style={{animationDelay: '4s'}}></div>
          </div>

          <Routes>
            <Route 
              path="/" 
              element={
                user ? <Navigate to="/dashboard" replace /> : <LandingPage onAuth={handleAuth} />
              } 
            />
            <Route 
              path="/login" 
              element={
                user ? <Navigate to="/dashboard" replace /> : <Login />
              } 
            />
            {/* Main app routes with /app prefix for Flask serving */}
            <Route 
              path="/dashboard" 
              element={
                user ? <Dashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" replace />
              } 
            />
            <Route 
              path="/contacts" 
              element={
                user ? <Contacts user={user} onLogout={handleLogout} /> : <Navigate to="/login" replace />
              } 
            />
            <Route 
              path="/goals" 
              element={
                user ? <Goals user={user} onLogout={handleLogout} /> : <Navigate to="/login" replace />
              } 
            />
            <Route 
              path="/upload-test" 
              element={
                user ? <ContactUploadTest /> : <Navigate to="/login" replace />
              } 
            />
            <Route path="/404" element={<NotFound />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>
        </div>
      </QueryProvider>
    </ErrorBoundary>
  )
}

export default App