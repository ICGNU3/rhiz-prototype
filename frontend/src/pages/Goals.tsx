import React, { useState, useEffect } from 'react';

interface Goal {
  id: string;
  title: string;
  description?: string;
  goal_type?: string;
  timeline?: string;
  status?: string;
  priority_level?: string;
  progress_percentage?: number;
  created_at?: string;
}

const Goals: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    const fetchGoals = async () => {
      try {
        const response = await fetch('/api/goals');
        if (response.ok) {
          const data = await response.json();
          setGoals(data);
        }
      } catch (error) {
        console.error('Failed to fetch goals:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchGoals();
  }, []);

  const filteredGoals = goals.filter(goal => {
    const matchesStatus = filterStatus === 'all' || goal.status === filterStatus;
    const matchesType = filterType === 'all' || goal.goal_type === filterType;
    return matchesStatus && matchesType;
  });

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'paused': return 'bg-yellow-500';
      case 'completed': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'high': return 'border-red-500';
      case 'medium': return 'border-yellow-500';
      case 'low': return 'border-green-500';
      default: return 'border-gray-500';
    }
  };

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
            Goals
          </div>
          <div className="space-x-4">
            <a href="/app/dashboard" className="text-gray-300 hover:text-white transition-colors">Dashboard</a>
            <a href="/app/contacts" className="text-gray-300 hover:text-white transition-colors">Contacts</a>
            <a href="/app/intelligence" className="text-gray-300 hover:text-white transition-colors">Intelligence</a>
            <a href="/logout" className="text-gray-300 hover:text-white transition-colors">Logout</a>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Page Header */}
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold">
                Your <span className="bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">Strategic Objectives</span>
              </h1>
              <p className="text-xl text-gray-300 mt-2">
                Track progress and achieve meaningful goals through strategic relationship building
              </p>
            </div>
            <button className="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-3 rounded-lg text-white font-semibold hover:from-blue-600 hover:to-purple-700 transition-all">
              Create Goal
            </button>
          </div>

          {/* Filters */}
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
            <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Statuses</option>
                <option value="active">Active</option>
                <option value="paused">Paused</option>
                <option value="completed">Completed</option>
              </select>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Types</option>
                <option value="fundraising">Fundraising</option>
                <option value="hiring">Hiring</option>
                <option value="partnerships">Partnerships</option>
                <option value="product">Product</option>
                <option value="marketing">Marketing</option>
                <option value="sales">Sales</option>
              </select>
            </div>
          </div>

          {/* Goals Stats */}
          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <h3 className="text-sm text-gray-400">Total Goals</h3>
              <p className="text-2xl font-bold text-white">{goals.length}</p>
            </div>
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <h3 className="text-sm text-gray-400">Active Goals</h3>
              <p className="text-2xl font-bold text-green-400">
                {goals.filter(g => g.status === 'active').length}
              </p>
            </div>
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <h3 className="text-sm text-gray-400">Completed</h3>
              <p className="text-2xl font-bold text-blue-400">
                {goals.filter(g => g.status === 'completed').length}
              </p>
            </div>
            <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10">
              <h3 className="text-sm text-gray-400">Avg Progress</h3>
              <p className="text-2xl font-bold text-purple-400">
                {goals.length > 0 
                  ? Math.round(goals.reduce((sum, g) => sum + (g.progress_percentage || 0), 0) / goals.length)
                  : 0}%
              </p>
            </div>
          </div>

          {/* Goals Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            {filteredGoals.map((goal) => (
              <div key={goal.id} className={`bg-white/5 backdrop-blur-lg rounded-xl p-6 border-l-4 border border-white/10 hover:bg-white/10 transition-all ${getPriorityColor(goal.priority_level)}`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-white mb-2">{goal.title}</h3>
                    {goal.description && (
                      <p className="text-gray-300 mb-4">{goal.description}</p>
                    )}
                  </div>
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(goal.status)}`}></div>
                </div>
                
                <div className="space-y-3">
                  {goal.goal_type && (
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-purple-400">🎯</span>
                      <span className="text-sm text-gray-300">
                        {goal.goal_type.charAt(0).toUpperCase() + goal.goal_type.slice(1)}
                      </span>
                    </div>
                  )}
                  
                  {goal.timeline && (
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-blue-400">⏰</span>
                      <span className="text-sm text-gray-300">{goal.timeline}</span>
                    </div>
                  )}
                  
                  {goal.priority_level && (
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-yellow-400">⚡</span>
                      <span className="text-sm text-gray-300">
                        {goal.priority_level.charAt(0).toUpperCase() + goal.priority_level.slice(1)} Priority
                      </span>
                    </div>
                  )}
                  
                  {typeof goal.progress_percentage === 'number' && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Progress</span>
                        <span className="text-white font-medium">{goal.progress_percentage}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all"
                          style={{ width: `${goal.progress_percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="flex space-x-2 mt-6">
                  <button className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 px-3 py-2 rounded-lg text-sm font-medium hover:from-blue-600 hover:to-purple-700 transition-all">
                    View Details
                  </button>
                  <button className="flex-1 border border-gray-600 px-3 py-2 rounded-lg text-sm font-medium hover:border-gray-500 hover:bg-gray-800/50 transition-all">
                    Edit
                  </button>
                </div>
              </div>
            ))}
          </div>

          {filteredGoals.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold text-gray-300 mb-2">No goals found</h3>
              <p className="text-gray-400">
                {filterStatus !== 'all' || filterType !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Start by creating your first strategic objective'
                }
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Goals;