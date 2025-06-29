import { useState } from 'react'
import { User } from '../types'
import { apiService } from '../services/api'

interface LandingPageProps {
  onAuth: (user: User) => void
}

export default function LandingPage({ onAuth }: LandingPageProps) {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleMagicLink = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return

    setIsLoading(true)
    setMessage('')

    const response = await apiService.requestMagicLink(email)
    
    if (response.success) {
      setMessage('Magic link sent! Check your email.')
    } else {
      setMessage('Failed to send magic link. Please try again.')
    }
    
    setIsLoading(false)
  }

  const handleDemoLogin = async () => {
    setIsLoading(true)
    setMessage('')

    const response = await apiService.demoLogin()
    
    if (response.success && response.user) {
      onAuth(response.user)
    } else {
      setMessage('Demo login failed. Please try again.')
    }
    
    setIsLoading(false)
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center px-4">
      <div className="max-w-4xl mx-auto text-center space-y-12">
        {/* Hero Section */}
        <div className="space-y-6">
          <h1 className="text-6xl md:text-7xl font-bold">
            <span className="gradient-text">Rhiz</span>
          </h1>
          <h2 className="text-2xl md:text-3xl font-light text-gray-200">
            Relationship Intelligence Platform
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Transform your professional relationships with AI-driven insights and strategic connection building. 
            Strengthen the relationships that matter most to what you're building.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 my-16">
          <div className="glass-card p-6 space-y-4">
            <div className="w-12 h-12 bg-blue-500 rounded-lg mx-auto flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white">AI-Powered Insights</h3>
            <p className="text-gray-300">
              Discover meaningful connections and get personalized recommendations for strengthening relationships.
            </p>
          </div>

          <div className="glass-card p-6 space-y-4">
            <div className="w-12 h-12 bg-purple-500 rounded-lg mx-auto flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white">Smart Relationship Tracking</h3>
            <p className="text-gray-300">
              Track interaction history, trust signals, and relationship depth with intelligent analytics.
            </p>
          </div>

          <div className="glass-card p-6 space-y-4">
            <div className="w-12 h-12 bg-indigo-500 rounded-lg mx-auto flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white">Goal-Driven Connections</h3>
            <p className="text-gray-300">
              Connect your relationship building with your professional goals and vision.
            </p>
          </div>
        </div>

        {/* Auth Section */}
        <div className="glass-card p-8 max-w-md mx-auto space-y-6">
          <h3 className="text-2xl font-semibold text-white">Get Started</h3>
          
          <form onSubmit={handleMagicLink} className="space-y-4">
            <div>
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white placeholder-gray-400"
                required
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full glass-button py-3 text-white font-medium disabled:opacity-50"
            >
              {isLoading ? 'Sending...' : 'Send Magic Link'}
            </button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-600"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-900 text-gray-400">or</span>
            </div>
          </div>

          <button
            onClick={handleDemoLogin}
            disabled={isLoading}
            className="w-full glass-button py-3 text-white font-medium disabled:opacity-50"
          >
            {isLoading ? 'Loading...' : 'Try Demo'}
          </button>

          {message && (
            <p className={`text-center text-sm ${
              message.includes('sent') ? 'text-green-400' : 'text-red-400'
            }`}>
              {message}
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="text-center text-gray-400">
          <p>&copy; 2025 Rhiz. Transform your relationships.</p>
        </div>
      </div>
    </div>
  )
}