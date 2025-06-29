import React, { useState, useEffect } from 'react';

interface DashboardStats {
  goals: number;
  contacts: number;
  ai_suggestions: number;
  trust_score?: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    goals: 0,
    contacts: 0,
    ai_suggestions: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await fetch('/api/dashboard/analytics');
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Background Effects */}
      <div className="fixed inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 pointer-events-none"></div>
      
      {/* Header */}
      <header className="relative z-10 p-6 border-b border-white/10">
        <nav className="flex justify-between items-center max-w-7xl mx-auto">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
            Rhiz Dashboard
          </div>
          <div className="space-x-4">
            <a href="/app/contacts" className="text-gray-300 hover:text-white transition-colors">Contacts</a>
            <a href="/app/goals" className="text-gray-300 hover:text-white transition-colors">Goals</a>
            <a href="/app/intelligence" className="text-gray-300 hover:text-white transition-colors">Intelligence</a>
            <a href="/logout" className="text-gray-300 hover:text-white transition-colors">Logout</a>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Welcome Section */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold">
              Welcome to your 
              <span className="bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
                {" "}relationship intelligence
              </span>
            </h1>
            <p className="text-xl text-gray-300">
              Track meaningful connections and achieve your goals through strategic relationship building
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-xl">🎯</span>
                </div>
                <div>
                  <h3 className="text-sm text-gray-400">Active Goals</h3>
                  <p className="text-2xl font-bold text-white">{stats.goals}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
                  <span className="text-xl">👥</span>
                </div>
                <div>
                  <h3 className="text-sm text-gray-400">Connections</h3>
                  <p className="text-2xl font-bold text-white">{stats.contacts}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-pink-500 to-red-600 rounded-lg flex items-center justify-center">
                  <span className="text-xl">💡</span>
                </div>
                <div>
                  <h3 className="text-sm text-gray-400">AI Insights</h3>
                  <p className="text-2xl font-bold text-white">{stats.ai_suggestions}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-teal-600 rounded-lg flex items-center justify-center">
                  <span className="text-xl">🤝</span>
                </div>
                <div>
                  <h3 className="text-sm text-gray-400">Trust Score</h3>
                  <p className="text-2xl font-bold text-white">{stats.trust_score || 'N/A'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-3 gap-6">
            <a href="/app/contacts" className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all group">
              <div className="space-y-4">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <span className="text-xl">📇</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Manage Contacts</h3>
                  <p className="text-gray-300">View and organize your professional relationships</p>
                </div>
              </div>
            </a>
            
            <a href="/app/goals" className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all group">
              <div className="space-y-4">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <span className="text-xl">🎯</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Set Goals</h3>
                  <p className="text-gray-300">Define objectives and track progress</p>
                </div>
              </div>
            </a>
            
            <a href="/app/intelligence" className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all group">
              <div className="space-y-4">
                <div className="w-12 h-12 bg-gradient-to-r from-pink-500 to-red-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <span className="text-xl">🧠</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">AI Insights</h3>
                  <p className="text-gray-300">Discover intelligent relationship recommendations</p>
                </div>
              </div>
            </a>
          </div>

          {/* Recent Activity */}
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <h2 className="text-2xl font-bold mb-6">Recent Activity</h2>
            <div className="space-y-4 text-gray-300">
              <p>🎯 Goal created: Raise Series A funding</p>
              <p>👤 Contact added: Sarah Chen (Investor)</p>
              <p>💡 AI suggestion: Connect with Marcus Rivera for partnership opportunities</p>
              <p>📧 Outreach sent to Jessica Thompson regarding senior backend role</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;