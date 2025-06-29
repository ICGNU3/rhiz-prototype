import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import axios from 'axios'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import Contacts from './pages/Contacts'
import Goals from './pages/Goals'
import Intelligence from './pages/Intelligence'
import './App.css'

// Types
interface User {
  id: string
  email: string
  subscription_tier: string
  goals_count: number
  contacts_count: number
  ai_suggestions_used: number
}

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/auth/me')
      setUser(response.data.user)
    } catch (error) {
      console.log('Not authenticated')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Loading Rhiz...</p>
      </div>
    )
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route 
            path="/app/dashboard" 
            element={user ? <Dashboard /> : <Navigate to="/" />} 
          />
          <Route 
            path="/app/contacts" 
            element={user ? <Contacts /> : <Navigate to="/" />} 
          />
          <Route 
            path="/app/goals" 
            element={user ? <Goals /> : <Navigate to="/" />} 
          />
          <Route 
            path="/app/intelligence" 
            element={user ? <Intelligence /> : <Navigate to="/" />} 
          />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App