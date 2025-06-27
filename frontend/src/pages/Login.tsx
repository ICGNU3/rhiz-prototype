import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Mail, Sparkles } from 'lucide-react';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const { sendMagicLink } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      await sendMagicLink(email);
      setMessage('Magic link sent! Check your email to continue.');
    } catch (error: any) {
      setMessage(error.response?.data?.message || 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-xl bg-gradient-to-r from-primary-500 to-purple-500 flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">R</span>
          </div>
          <h1 className="text-3xl font-bold gradient-text">Welcome to Rhiz</h1>
          <p className="text-gray-400 mt-2">Sign in to access your network intelligence</p>
        </div>

        {/* Login Form */}
        <div className="glass-card p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full pl-10 pr-4 py-3 bg-dark-card border border-dark-border rounded-lg text-white placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-colors"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || !email}
              className="w-full glass-button-primary flex items-center justify-center space-x-2 py-3 text-base font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
              ) : (
                <>
                  <Sparkles size={18} />
                  <span>Send Magic Link</span>
                </>
              )}
            </button>

            {message && (
              <div className={`p-4 rounded-lg text-sm ${
                message.includes('sent') 
                  ? 'bg-green-500/20 border border-green-500/30 text-green-300'
                  : 'bg-red-500/20 border border-red-500/30 text-red-300'
              }`}>
                {message}
              </div>
            )}
          </form>

          <div className="mt-8 pt-6 border-t border-dark-border">
            <p className="text-center text-sm text-gray-400">
              New to Rhiz?{' '}
              <a href="/" className="text-primary-400 hover:text-primary-300 transition-colors">
                Learn more about Root Membership
              </a>
            </p>
          </div>
        </div>

        {/* Features Preview */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-400 mb-4">What you'll get access to:</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="text-gray-300">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg mx-auto mb-2 flex items-center justify-center">
                <Sparkles size={16} className="text-white" />
              </div>
              AI-Powered Matching
            </div>
            <div className="text-gray-300">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg mx-auto mb-2 flex items-center justify-center">
                <Mail size={16} className="text-white" />
              </div>
              Smart Outreach
            </div>
            <div className="text-gray-300">
              <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg mx-auto mb-2 flex items-center justify-center">
                <span className="text-white font-bold">∞</span>
              </div>
              Network Intelligence
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;