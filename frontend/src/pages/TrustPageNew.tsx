import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Shield, TrendingUp, Users, AlertTriangle, Loader2, AlertCircle, Heart, Star, Clock, Activity } from 'lucide-react';
import { trustAPI } from '../services/api';

interface TrustInsight {
  contact_id: string;
  contact_name: string;
  trust_score: number;
  tier: 'rooted' | 'growing' | 'dormant' | 'frayed';
  insights: string[];
  signals: TrustSignal[];
  last_interaction: string;
  response_time_avg: number;
  interaction_frequency: number;
}

interface TrustSignal {
  id: string;
  signal_type: string;
  value: number;
  notes?: string;
  created_at: string;
}

interface TrustHealth {
  health_score: number;
  total_contacts: number;
  trusted_contacts: number;
  at_risk_count: number;
  recommendations: string[];
}

const TrustPage: React.FC = () => {
  const [selectedContact, setSelectedContact] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'tiers' | 'insights' | 'actions'>('overview');
  const queryClient = useQueryClient();

  // Fetch trust data with React Query
  const { 
    data: trustData, 
    isLoading: trustLoading, 
    error: trustError, 
    refetch: refetchTrust 
  } = useQuery({
    queryKey: ['trust'],
    queryFn: async () => {
      const response = await trustAPI.getAll();
      return response.data;
    },
    retry: 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Fetch trust insights
  const { 
    data: insights = [], 
    isLoading: insightsLoading 
  } = useQuery({
    queryKey: ['trust', 'insights'],
    queryFn: async () => {
      const response = await trustAPI.getInsights();
      return response.data?.insights?.top_contacts || [];
    },
    retry: 2,
  });

  // Fetch trust health
  const { 
    data: healthData, 
    isLoading: healthLoading 
  } = useQuery({
    queryKey: ['trust', 'health'],
    queryFn: async () => {
      const response = await trustAPI.getHealth();
      return response.data;
    },
    retry: 2,
  });

  // Record trust signal mutation
  const recordSignalMutation = useMutation({
    mutationFn: trustAPI.recordSignal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trust'] });
    },
    onError: (error) => {
      console.error('Failed to record trust signal:', error);
    },
  });

  // Update trust insights mutation
  const updateInsightsMutation = useMutation({
    mutationFn: trustAPI.updateInsights,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trust'] });
    },
    onError: (error) => {
      console.error('Failed to update insights:', error);
    },
  });

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'rooted': return 'text-green-400 bg-green-500/20';
      case 'growing': return 'text-blue-400 bg-blue-500/20';
      case 'dormant': return 'text-yellow-400 bg-yellow-500/20';
      case 'frayed': return 'text-red-400 bg-red-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'rooted': return <Heart className="w-4 h-4" />;
      case 'growing': return <TrendingUp className="w-4 h-4" />;
      case 'dormant': return <Clock className="w-4 h-4" />;
      case 'frayed': return <AlertTriangle className="w-4 h-4" />;
      default: return <Users className="w-4 h-4" />;
    }
  };

  // Loading state
  if (trustLoading || insightsLoading || healthLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 flex items-center justify-center">
        <div className="glass-card p-8 flex items-center space-x-4">
          <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
          <span className="text-white text-lg">Loading trust insights...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (trustError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 flex items-center justify-center">
        <div className="glass-card p-8 flex flex-col items-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-400" />
          <div className="text-center">
            <h2 className="text-white text-xl font-semibold mb-2">Failed to load trust data</h2>
            <p className="text-gray-400 mb-4">Unable to fetch your trust insights</p>
            <button 
              onClick={() => refetchTrust()}
              className="glass-button px-6 py-2 rounded-lg text-blue-400 border border-blue-400/30 hover:bg-blue-400/10"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
              Trust Insights
            </h1>
            <p className="text-gray-300 mt-2">
              Monitor relationship health and build stronger connections
            </p>
          </div>
          <button 
            onClick={() => updateInsightsMutation.mutate()}
            disabled={updateInsightsMutation.isPending}
            className="glass-button px-6 py-3 rounded-lg text-green-400 border border-green-400/30 hover:bg-green-400/10 flex items-center disabled:opacity-50"
          >
            <Activity className="w-5 h-5 mr-2" />
            {updateInsightsMutation.isPending ? 'Updating...' : 'Refresh Insights'}
          </button>
        </div>

        {/* Trust Health Overview */}
        {healthData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <Shield className="w-8 h-8 text-green-400" />
                <span className="text-2xl font-bold text-green-400">
                  {healthData.health_score || 0}%
                </span>
              </div>
              <h3 className="text-white font-semibold mb-1">Trust Health</h3>
              <p className="text-gray-400 text-sm">Overall network health score</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <Users className="w-8 h-8 text-blue-400" />
                <span className="text-2xl font-bold text-blue-400">
                  {healthData.total_contacts || 0}
                </span>
              </div>
              <h3 className="text-white font-semibold mb-1">Total Contacts</h3>
              <p className="text-gray-400 text-sm">Contacts in your network</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <Star className="w-8 h-8 text-yellow-400" />
                <span className="text-2xl font-bold text-yellow-400">
                  {healthData.trusted_contacts || 0}
                </span>
              </div>
              <h3 className="text-white font-semibold mb-1">Trusted</h3>
              <p className="text-gray-400 text-sm">High-trust connections</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <AlertTriangle className="w-8 h-8 text-red-400" />
                <span className="text-2xl font-bold text-red-400">
                  {healthData.at_risk_count || 0}
                </span>
              </div>
              <h3 className="text-white font-semibold mb-1">At Risk</h3>
              <p className="text-gray-400 text-sm">Relationships needing attention</p>
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="glass-card p-6 mb-8">
          <div className="flex space-x-4">
            {[
              { id: 'overview', label: 'Overview', icon: <Shield className="w-4 h-4" /> },
              { id: 'tiers', label: 'Trust Tiers', icon: <Users className="w-4 h-4" /> },
              { id: 'insights', label: 'AI Insights', icon: <TrendingUp className="w-4 h-4" /> },
              { id: 'actions', label: 'Suggested Actions', icon: <Activity className="w-4 h-4" /> },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                  activeTab === tab.id 
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-400/30' 
                    : 'text-gray-400 hover:text-white hover:bg-gray-700/30'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Trust Distribution */}
            <div className="glass-card p-6">
              <h3 className="text-white font-semibold mb-4">Trust Distribution</h3>
              <div className="space-y-4">
                {trustData?.insights?.trust_tiers && Object.entries(trustData.insights.trust_tiers).map(([tier, count]) => (
                  <div key={tier} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${getTierColor(tier)}`}>
                        {getTierIcon(tier)}
                      </div>
                      <span className="text-white capitalize">{tier}</span>
                    </div>
                    <span className="text-gray-400">{count as number}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="glass-card p-6">
              <h3 className="text-white font-semibold mb-4">Recent Changes</h3>
              <div className="space-y-3">
                {trustData?.insights?.recent_changes?.length > 0 ? (
                  trustData.insights.recent_changes.map((change: any, index: number) => (
                    <div key={index} className="p-3 bg-gray-800/30 rounded-lg">
                      <p className="text-white text-sm">{change.description}</p>
                      <p className="text-gray-400 text-xs mt-1">{change.timestamp}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-400 text-center py-4">No recent changes to display</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {insights.length > 0 ? (
              insights.map((contact: any, index: number) => (
                <div key={index} className="glass-card p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-white font-semibold">{contact.name}</h4>
                    <div className={`px-3 py-1 rounded-full text-xs ${getTierColor(contact.tier)}`}>
                      {contact.tier}
                    </div>
                  </div>
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400 text-sm">Trust Score</span>
                      <span className="text-white font-semibold">{contact.trust_score}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-gradient-to-r from-green-400 to-blue-400"
                        style={{ width: `${contact.trust_score}%` }}
                      />
                    </div>
                  </div>
                  {contact.insights && contact.insights.length > 0 && (
                    <div>
                      <h5 className="text-gray-300 text-sm mb-2">Key Insights:</h5>
                      <ul className="space-y-1">
                        {contact.insights.slice(0, 2).map((insight: string, i: number) => (
                          <li key={i} className="text-gray-400 text-xs">• {insight}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="col-span-full glass-card p-12 text-center">
                <TrendingUp className="w-16 h-16 mx-auto mb-4 text-gray-500" />
                <h3 className="text-white text-xl mb-2">No Insights Available</h3>
                <p className="text-gray-400">Add more contacts to generate trust insights</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'actions' && healthData?.recommendations && (
          <div className="glass-card p-6">
            <h3 className="text-white font-semibold mb-6">Recommended Actions</h3>
            <div className="space-y-4">
              {healthData.recommendations.map((recommendation: string, index: number) => (
                <div key={index} className="flex items-start space-x-4 p-4 bg-gray-800/30 rounded-lg">
                  <Activity className="w-5 h-5 text-blue-400 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-white">{recommendation}</p>
                  </div>
                  <button className="text-blue-400 hover:text-blue-300 text-sm">
                    Take Action
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrustPage;