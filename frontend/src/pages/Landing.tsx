import React from 'react';

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Background Effects */}
      <div className="fixed inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 pointer-events-none"></div>
      
      {/* Header */}
      <header className="relative z-10 p-6">
        <nav className="flex justify-between items-center max-w-7xl mx-auto">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
            Rhiz
          </div>
          <div className="space-x-4">
            <a href="/login" className="text-gray-300 hover:text-white transition-colors">Login</a>
            <a href="/signup" className="bg-gradient-to-r from-blue-500 to-purple-600 px-4 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all">
              Get Started
            </a>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-20">
        <div className="text-center space-y-8">
          <h1 className="text-6xl font-bold leading-tight">
            Strengthen the relationships
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              that matter most
            </span>
          </h1>
          
          <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Rhiz transforms how you build and maintain meaningful professional relationships. 
            Use AI-powered insights to identify the right people, at the right time, 
            for what you're building.
          </p>

          <div className="flex justify-center space-x-4 pt-8">
            <a href="/login" className="bg-gradient-to-r from-blue-500 to-purple-600 px-8 py-4 rounded-lg text-lg font-semibold hover:from-blue-600 hover:to-purple-700 transition-all shadow-lg">
              Try Demo
            </a>
            <a href="/about" className="border border-gray-600 px-8 py-4 rounded-lg text-lg font-semibold hover:border-gray-500 hover:bg-gray-800/50 transition-all">
              Learn More
            </a>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mt-24">
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg mb-4"></div>
            <h3 className="text-xl font-semibold mb-2">Relationship Intelligence</h3>
            <p className="text-gray-300">
              AI analyzes your network to identify the strongest paths to your goals through meaningful connections.
            </p>
          </div>
          
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg mb-4"></div>
            <h3 className="text-xl font-semibold mb-2">Trust Insights</h3>
            <p className="text-gray-300">
              Track relationship health with trust scores, interaction patterns, and engagement depth analysis.
            </p>
          </div>
          
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <div className="w-12 h-12 bg-gradient-to-r from-pink-500 to-red-600 rounded-lg mb-4"></div>
            <h3 className="text-xl font-semibold mb-2">Smart Outreach</h3>
            <p className="text-gray-300">
              Generate personalized messages and timing recommendations based on relationship context.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Landing;