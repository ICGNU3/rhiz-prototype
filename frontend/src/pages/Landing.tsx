import { useState } from 'react'
import { ArrowRight, Network, Brain, Shield, Zap } from 'lucide-react'
import axios from 'axios'

const Landing = () => {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleMagicLink = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setMessage('')

    try {
      await axios.post('/api/auth/request-link', { email })
      setMessage('Magic link sent! Check your email to sign in.')
      setEmail('')
    } catch (error: any) {
      setMessage(error.response?.data?.error || 'Something went wrong. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="relative">
        {/* Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-gradient-to-br from-purple-400 to-indigo-600 opacity-20 blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full bg-gradient-to-br from-indigo-400 to-purple-600 opacity-20 blur-3xl"></div>
        </div>

        {/* Navigation */}
        <nav className="relative z-10 flex justify-between items-center p-6 max-w-7xl mx-auto">
          <div className="flex items-center space-x-2">
            <Network className="w-8 h-8 text-indigo-600" />
            <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Rhiz
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <a href="#features" className="text-gray-600 hover:text-indigo-600 transition-colors">
              Features
            </a>
            <a href="#about" className="text-gray-600 hover:text-indigo-600 transition-colors">
              About
            </a>
          </div>
        </nav>

        {/* Hero Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-6 py-24">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-8">
              Your{' '}
              <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Relationship
              </span>{' '}
              Intelligence Platform
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-600 mb-12 leading-relaxed">
              Transform how you build and maintain professional relationships with AI-powered insights, 
              smart introductions, and purposeful networking that drives real results.
            </p>

            {/* Magic Link Form */}
            <div className="max-w-md mx-auto">
              <form onSubmit={handleMagicLink} className="space-y-4">
                <div className="relative">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email address"
                    className="w-full px-6 py-4 text-lg border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition-all"
                    required
                  />
                </div>
                
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 px-8 rounded-xl text-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transform hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {isLoading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <span>Get Magic Link</span>
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </button>
              </form>

              {message && (
                <p className={`mt-4 text-sm ${message.includes('sent') ? 'text-green-600' : 'text-red-600'}`}>
                  {message}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <section id="features" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Intelligent Relationship Management
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need to build, maintain, and leverage your professional network
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-8 hover:shadow-lg transition-all">
              <Brain className="w-12 h-12 text-indigo-600 mb-6" />
              <h3 className="text-xl font-semibold text-gray-900 mb-4">AI-Powered Insights</h3>
              <p className="text-gray-600">
                Get intelligent recommendations on who to contact, when to follow up, and how to strengthen relationships.
              </p>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-8 hover:shadow-lg transition-all">
              <Network className="w-12 h-12 text-purple-600 mb-6" />
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Smart Networking</h3>
              <p className="text-gray-600">
                Discover mutual connections, identify warm introductions, and expand your network strategically.
              </p>
            </div>

            <div className="bg-gradient-to-br from-pink-50 to-indigo-50 rounded-xl p-8 hover:shadow-lg transition-all">
              <Shield className="w-12 h-12 text-pink-600 mb-6" />
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Trust Analytics</h3>
              <p className="text-gray-600">
                Track relationship strength, interaction patterns, and trust metrics to optimize your networking approach.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-indigo-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center px-6">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Transform Your Professional Network?
          </h2>
          <p className="text-xl text-indigo-100 mb-8">
            Join thousands of professionals who are building stronger relationships with Rhiz.
          </p>
          <div className="flex items-center justify-center space-x-2 text-indigo-100">
            <Zap className="w-5 h-5" />
            <span>No credit card required • Get started in 30 seconds</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center space-x-2 mb-6">
            <Network className="w-6 h-6" />
            <span className="text-xl font-bold">Rhiz</span>
          </div>
          <p className="text-gray-400">
            © 2025 Rhiz. All rights reserved. Building better relationships through intelligence.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Landing