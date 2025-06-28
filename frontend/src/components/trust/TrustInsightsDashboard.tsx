import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Shield, TrendingUp, Clock, Users, AlertTriangle, CheckCircle } from 'lucide-react';

interface TrustInsight {
  contact_id: number;
  contact_name: string;
  trust_tier: string;
  trust_score: number;
  reciprocity_index: number;
  response_time_avg: number;
  interaction_frequency: number;
  last_interaction: string;
  trust_summary: string;
  suggested_actions: string[];
}

interface TrustHealth {
  overall_score: number;
  tier_distribution: Record<string, number>;
  total_contacts: number;
  active_relationships: number;
  health_trends: {
    improving: number;
    stable: number;
    declining: number;
  };
}

const TrustInsightsDashboard: React.FC = () => {
  const { data: trustInsights = [], isLoading: insightsLoading } = useQuery({
    queryKey: ['trust-insights'],
    queryFn: async () => {
      const response = await fetch('/api/trust/insights', {
        credentials: 'include',
      });
      if (!response.ok) return [];
      return response.json();
    },
    staleTime: 5 * 60 * 1000,
  });

  const { data: trustHealth, isLoading: healthLoading } = useQuery({
    queryKey: ['trust-health'],
    queryFn: async () => {
      const response = await fetch('/api/trust/health', {
        credentials: 'include',
      });
      if (!response.ok) return null;
      return response.json();
    },
    staleTime: 5 * 60 * 1000,
  });

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'rooted': return 'text-green-400 bg-green-400/10';
      case 'growing': return 'text-blue-400 bg-blue-400/10';
      case 'dormant': return 'text-yellow-400 bg-yellow-400/10';
      case 'frayed': return 'text-red-400 bg-red-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'rooted': return CheckCircle;
      case 'growing': return TrendingUp;
      case 'dormant': return Clock;
      case 'frayed': return AlertTriangle;
      default: return Shield;
    }
  };

  if (insightsLoading || healthLoading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="glass-card p-6 animate-pulse">
              <div className="h-6 bg-gray-700 rounded mb-4"></div>
              <div className="h-8 bg-gray-700 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Trust Health Overview */}
      <div className="glass-card p-8">
        <div className="flex items-center space-x-3 mb-6">
          <Shield className="w-8 h-8 text-blue-400" />
          <h2 className="text-2xl font-bold text-white">Trust & Relationship Health</h2>
        </div>
        
        {trustHealth && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-400 mb-2">
                {Math.round(trustHealth.overall_score * 100)}%
              </div>
              <div className="text-gray-300">Overall Health</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-green-400 mb-2">
                {trustHealth.active_relationships}
              </div>
              <div className="text-gray-300">Active Relationships</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-400 mb-2">
                {trustHealth.health_trends.improving}
              </div>
              <div className="text-gray-300">Improving</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-400 mb-2">
                {trustHealth.health_trends.declining}
              </div>
              <div className="text-gray-300">Need Attention</div>
            </div>
          </div>
        )}
      </div>

      {/* Trust Tier Distribution */}
      {trustHealth && (
        <div className="glass-card p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Trust Tier Distribution</h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {Object.entries(trustHealth.tier_distribution).map(([tier, count]) => {
              const TierIcon = getTierIcon(tier);
              return (
                <div key={tier} className={`p-4 rounded-xl ${getTierColor(tier)}`}>
                  <div className="flex items-center space-x-3">
                    <TierIcon className="w-6 h-6" />
                    <div>
                      <div className="font-semibold capitalize">{tier}</div>
                      <div className="text-2xl font-bold">{count}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Individual Trust Insights */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold text-white mb-6">Contact Trust Insights</h3>
        
        {trustInsights.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <Shield className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No trust insights available yet. Add contacts and interactions to generate insights.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {trustInsights.slice(0, 10).map((insight: TrustInsight) => {
              const TierIcon = getTierIcon(insight.trust_tier);
              return (
                <div key={insight.contact_id} className="border border-gray-700/50 rounded-xl p-4 hover:border-gray-600/50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      <div className={`p-2 rounded-lg ${getTierColor(insight.trust_tier)}`}>
                        <TierIcon className="w-5 h-5" />
                      </div>
                      
                      <div className="flex-1">
                        <h4 className="font-semibold text-white">{insight.contact_name}</h4>
                        <p className="text-gray-300 text-sm mb-2 capitalize">
                          {insight.trust_tier} • Trust Score: {Math.round(insight.trust_score * 100)}%
                        </p>
                        
                        <div className="grid gap-2 md:grid-cols-3 text-sm text-gray-400 mb-3">
                          <div>
                            <span className="font-medium">Reciprocity:</span> {Math.round(insight.reciprocity_index * 100)}%
                          </div>
                          <div>
                            <span className="font-medium">Response Time:</span> {insight.response_time_avg.toFixed(1)}h
                          </div>
                          <div>
                            <span className="font-medium">Frequency:</span> {insight.interaction_frequency.toFixed(1)}/week
                          </div>
                        </div>
                        
                        {insight.trust_summary && (
                          <p className="text-gray-300 text-sm mb-3">{insight.trust_summary}</p>
                        )}
                        
                        {insight.suggested_actions.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {insight.suggested_actions.slice(0, 2).map((action, idx) => (
                              <span key={idx} className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs">
                                {action}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-xs text-gray-500">
                      Last: {new Date(insight.last_interaction).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Trust Actions */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold text-white mb-4">Recommended Actions</h3>
        <div className="grid gap-4 md:grid-cols-2">
          <button className="p-4 border border-gray-700/50 rounded-xl hover:border-gray-600/50 transition-colors text-left">
            <div className="flex items-center space-x-3">
              <TrendingUp className="w-6 h-6 text-green-400" />
              <div>
                <div className="font-semibold text-white">Update Trust Insights</div>
                <div className="text-gray-400 text-sm">Refresh all contact trust scores</div>
              </div>
            </div>
          </button>
          
          <button className="p-4 border border-gray-700/50 rounded-xl hover:border-gray-600/50 transition-colors text-left">
            <div className="flex items-center space-x-3">
              <Users className="w-6 h-6 text-blue-400" />
              <div>
                <div className="font-semibold text-white">Review Frayed Contacts</div>
                <div className="text-gray-400 text-sm">Address declining relationships</div>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TrustInsightsDashboard;