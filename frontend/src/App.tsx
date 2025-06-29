import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { User } from './types'
import { apiService } from './services/api'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Contacts from './pages/Contacts'
import Goals from './pages/Goals'
import NotFound from './pages/NotFound'

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const response = await apiService.getCurrentUser()
    if (response.success && response.data) {
      setUser(response.data)
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
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="glass-card p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
          <p className="text-center mt-4 text-gray-300">Loading...</p>
        </div>
      </div>
    )
  }

  return (
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
        <Route path="/404" element={<NotFound />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </div>
  )
}

export default App