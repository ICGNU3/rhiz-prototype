import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart3, Users, Target, Brain, TrendingUp, MessageSquare, Loader2, AlertCircle } from 'lucide-react';
import { analyticsAPI, contactsAPI, goalsAPI, intelligenceAPI } from '../services/api';

interface DashboardStats {
  totalContacts: number;
  activeGoals: number;
  aiSuggestions: number;
  trustScore: number;
  weeklyInteractions: number;
  pendingFollowUps: number;
}

interface RecentActivity {
  id: string;
  type: 'contact' | 'goal' | 'interaction' | 'ai_suggestion';
  title: string;
  description: string;
  timestamp: string;
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalContacts: 0,
    activeGoals: 0,
    aiSuggestions: 0,
    trustScore: 0,
    weeklyInteractions: 0,
    pendingFollowUps: 0
  });
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);

  useEffect(() => {
    // Fetch dashboard analytics
    fetch('/api/dashboard/analytics')
      .then(res => res.json())
      .then(data => {
        setStats(data.stats || stats);
        setRecentActivity(data.recent_activity || []);
      })
      .catch(err => console.error('Failed to load dashboard:', err));
  }, []);

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    trend?: string;
    color: string;
  }> = ({ title, value, icon, trend, color }) => (
    <div className="glass-card p-6 backdrop-blur-sm border border-white/10 rounded-xl">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className={`text-3xl font-bold mt-2 bg-gradient-to-r ${color} bg-clip-text text-transparent`}>
            {value}
          </p>
          {trend && (
            <p className="text-green-400 text-sm mt-1 flex items-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              {trend}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg bg-gradient-to-r ${color.replace('text-transparent', 'from-blue-500/10 to-purple-500/10')}`}>
          {icon}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <p className="text-gray-300 mt-2">
            Your relationship intelligence overview
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Total Contacts"
            value={stats.totalContacts}
            icon={<Users className="w-6 h-6 text-blue-400" />}
            trend="+12% this week"
            color="from-blue-400 to-blue-600"
          />
          <StatCard
            title="Active Goals"
            value={stats.activeGoals}
            icon={<Target className="w-6 h-6 text-purple-400" />}
            trend="2 new this month"
            color="from-purple-400 to-purple-600"
          />
          <StatCard
            title="AI Suggestions"
            value={stats.aiSuggestions}
            icon={<Brain className="w-6 h-6 text-green-400" />}
            trend="3 pending review"
            color="from-green-400 to-green-600"
          />
          <StatCard
            title="Trust Score"
            value={`${stats.trustScore}%`}
            icon={<BarChart3 className="w-6 h-6 text-yellow-400" />}
            trend="+5% this week"
            color="from-yellow-400 to-yellow-600"
          />
          <StatCard
            title="Weekly Interactions"
            value={stats.weeklyInteractions}
            icon={<MessageSquare className="w-6 h-6 text-pink-400" />}
            color="from-pink-400 to-pink-600"
          />
          <StatCard
            title="Pending Follow-ups"
            value={stats.pendingFollowUps}
            icon={<TrendingUp className="w-6 h-6 text-indigo-400" />}
            color="from-indigo-400 to-indigo-600"
          />
        </div>

        {/* Recent Activity */}
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 backdrop-blur-sm">
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
              <TrendingUp className="w-5 h-5 mr-3 text-blue-400" />
              Recent Activity
            </h3>
            
            {recentActivity.length > 0 ? (
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-4 p-4 bg-gray-800/30 rounded-lg">
                    <div className={`w-3 h-3 rounded-full mt-2 ${
                      activity.type === 'contact' ? 'bg-blue-400' :
                      activity.type === 'goal' ? 'bg-purple-400' :
                      activity.type === 'interaction' ? 'bg-green-400' :
                      'bg-yellow-400'
                    }`} />
                    <div className="flex-1">
                      <h6 className="font-medium text-white">{activity.title}</h6>
                      <p className="text-gray-400 text-sm">{activity.description}</p>
                      <p className="text-gray-500 text-xs mt-1">{activity.timestamp}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No recent activity</p>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="glass-card p-6 backdrop-blur-sm">
            <h3 className="text-xl font-semibold text-white mb-6">Quick Actions</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <button className="glass-button p-4 rounded-lg text-blue-400 border border-blue-400/30 hover:bg-blue-400/10 transition-all duration-300">
                <Users className="w-6 h-6 mx-auto mb-2" />
                <span className="text-sm">Add Contact</span>
              </button>
              
              <button className="glass-button p-4 rounded-lg text-purple-400 border border-purple-400/30 hover:bg-purple-400/10 transition-all duration-300">
                <Target className="w-6 h-6 mx-auto mb-2" />
                <span className="text-sm">Create Goal</span>
              </button>
              
              <button className="glass-button p-4 rounded-lg text-green-400 border border-green-400/30 hover:bg-green-400/10 transition-all duration-300">
                <Brain className="w-6 h-6 mx-auto mb-2" />
                <span className="text-sm">AI Insights</span>
              </button>
              
              <button className="glass-button p-4 rounded-lg text-yellow-400 border border-yellow-400/30 hover:bg-yellow-400/10 transition-all duration-300">
                <MessageSquare className="w-6 h-6 mx-auto mb-2" />
                <span className="text-sm">Send Message</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .glass-card {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-radius: 16px;
        }
        
        .glass-button {
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(10px);
          transition: all 0.3s ease;
          text-align: center;
        }
        
        .glass-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
      `}</style>
    </div>
  );
};

export default DashboardPage;