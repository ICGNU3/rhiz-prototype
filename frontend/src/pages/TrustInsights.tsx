import React, { useState, useEffect } from 'react';
import { Heart, TrendingUp, Clock, Users, Eye, RefreshCw, AlertTriangle } from 'lucide-react';

interface TrustSignal {
  contact_id: number;
  signal_type: string;
  value: number;
  timestamp: string;
  context?: any;
}

interface TrustInsight {
  contact_id: number;
  trust_tier: string;
  trust_score: number;
  reciprocity_index: number;
  response_time_avg: number;
  interaction_frequency: number;
  last_interaction: string;
  trust_summary: string;
  suggested_actions: string[];
  trust_signals: TrustSignal[];
  updated_at: string;
}

interface TrustHealth {
  health_score: number;
  insights_summary: string;
  behavioral_patterns: string[];
  recommendations: string[];
  trust_tier_distribution: Record<string, number>;
  avg_reciprocity: number;
}

const TrustInsights: React.FC = () => {
  const [insights, setInsights] = useState<TrustInsight[]>([]);
  const [health, setHealth] = useState<TrustHealth | null>(null);
  const [tiers, setTiers] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [selectedTier, setSelectedTier] = useState<string>('all');
  const [updating, setUpdating] = useState(false);

  const trustTierConfig = {
    rooted: {
      color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
      icon: '🌱',
      title: 'Rooted',
      description: 'Deep trust, frequent reciprocity'
    },
    growing: {
      color: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
      icon: '📈',
      title: 'Growing',
      description: 'Promising, recent interactions'
    },
    dormant: {
      color: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
      icon: '😴',
      title: 'Dormant',
      description: 'Needs reconnection'
    },
    frayed: {
      color: 'bg-red-500/20 text-red-300 border-red-500/30',
      icon: '⚡',
      title: 'Frayed',
      description: 'Low response, unreciprocated'
    }
  };

  useEffect(() => {
    fetchTrustData();
  }, []);

  const fetchTrustData = async () => {
    setLoading(true);
    try {
      const [insightsRes, healthRes, tiersRes] = await Promise.all([
        fetch('/api/trust/insights'),
        fetch('/api/trust/health'),
        fetch('/api/trust/tiers')
      ]);

      if (insightsRes.ok) {
        const insightsData = await insightsRes.json();
        setInsights(insightsData.insights || []);
      }

      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setHealth(healthData.health);
      }

      if (tiersRes.ok) {
        const tiersData = await tiersRes.json();
        setTiers(tiersData.tiers || {});
      }
    } catch (error) {
      console.error('Failed to fetch trust data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateTrustInsights = async () => {
    setUpdating(true);
    try {
      const response = await fetch('/api/trust/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        await fetchTrustData();
      }
    } catch (error) {
      console.error('Failed to update trust insights:', error);
    } finally {
      setUpdating(false);
    }
  };

  const filteredInsights = selectedTier === 'all' 
    ? insights 
    : insights.filter(insight => insight.trust_tier === selectedTier);

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString();
  };

  const getTrustScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-emerald-400';
    if (score >= 0.6) return 'text-blue-400';
    if (score >= 0.4) return 'text-yellow-400';
    return 'text-red-400';
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-white/10 rounded-lg w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-white/10 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">Trust Insights</h1>
          <p className="text-gray-400 mt-1">Real-time relationship intelligence and health indicators</p>
        </div>
        <button
          onClick={updateTrustInsights}
          disabled={updating}
          className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 
                   disabled:bg-purple-600/50 text-white rounded-lg transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${updating ? 'animate-spin' : ''}`} />
          <span>{updating ? 'Updating...' : 'Refresh Insights'}</span>
        </button>
      </div>

      {/* Trust Health Overview */}
      {health && (
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Heart className="w-6 h-6 text-pink-400" />
            <h2 className="text-xl font-semibold text-white">Trust Health Overview</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Health Score */}
            <div className="text-center">
              <div className={`text-3xl font-bold ${getTrustScoreColor(health.health_score)}`}>
                {(health.health_score * 100).toFixed(0)}%
              </div>
              <div className="text-gray-400 text-sm">Overall Trust Health</div>
            </div>

            {/* Reciprocity Index */}
            <div className="text-center">
              <div className={`text-3xl font-bold ${getTrustScoreColor(health.avg_reciprocity)}`}>
                {(health.avg_reciprocity * 100).toFixed(0)}%
              </div>
              <div className="text-gray-400 text-sm">Reciprocity Balance</div>
            </div>

            {/* Total Contacts */}
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-400">
                {Object.values(health.trust_tier_distribution).reduce((a, b) => a + b, 0)}
              </div>
              <div className="text-gray-400 text-sm">Analyzed Contacts</div>
            </div>
          </div>

          {/* AI Summary */}
          <div className="mt-6 p-4 bg-white/5 rounded-lg">
            <h3 className="text-sm font-medium text-gray-300 mb-2">AI Insights Summary</h3>
            <p className="text-gray-300 text-sm leading-relaxed">{health.insights_summary}</p>
          </div>

          {/* Recommendations */}
          {health.recommendations.length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-300 mb-2">Recommendations</h3>
              <div className="space-y-1">
                {health.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start space-x-2 text-sm text-gray-400">
                    <span className="text-blue-400">•</span>
                    <span>{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Trust Tier Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Object.entries(trustTierConfig).map(([tier, config]) => {
          const count = tiers[tier]?.count || 0;
          const isSelected = selectedTier === tier;
          
          return (
            <button
              key={tier}
              onClick={() => setSelectedTier(isSelected ? 'all' : tier)}
              className={`p-4 rounded-lg border transition-all ${config.color} 
                         ${isSelected ? 'ring-2 ring-white/30' : 'hover:bg-white/10'}`}
            >
              <div className="text-center">
                <div className="text-2xl mb-2">{config.icon}</div>
                <div className="font-semibold">{config.title}</div>
                <div className="text-2xl font-bold mt-1">{count}</div>
                <div className="text-xs opacity-80 mt-1">{config.description}</div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Filter Buttons */}
      <div className="flex space-x-2">
        <button
          onClick={() => setSelectedTier('all')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            selectedTier === 'all' 
              ? 'bg-purple-600 text-white' 
              : 'bg-white/10 text-gray-300 hover:bg-white/20'
          }`}
        >
          All Contacts ({insights.length})
        </button>
        {Object.entries(trustTierConfig).map(([tier, config]) => (
          <button
            key={tier}
            onClick={() => setSelectedTier(tier)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              selectedTier === tier 
                ? 'bg-purple-600 text-white' 
                : 'bg-white/10 text-gray-300 hover:bg-white/20'
            }`}
          >
            {config.title} ({tiers[tier]?.count || 0})
          </button>
        ))}
      </div>

      {/* Trust Insights List */}
      <div className="space-y-4">
        {filteredInsights.map((insight) => {
          const tierConfig = trustTierConfig[insight.trust_tier as keyof typeof trustTierConfig];
          
          return (
            <div 
              key={insight.contact_id}
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-colors"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`px-3 py-1 rounded-full text-xs font-medium border ${tierConfig?.color || ''}`}>
                    {tierConfig?.icon} {tierConfig?.title}
                  </div>
                  <div className={`text-2xl font-bold ${getTrustScoreColor(insight.trust_score)}`}>
                    {(insight.trust_score * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="text-right text-sm text-gray-400">
                  <div>Last interaction: {insight.last_interaction ? formatTimestamp(insight.last_interaction) : 'Never'}</div>
                  <div>Updated: {formatTimestamp(insight.updated_at)}</div>
                </div>
              </div>

              {/* Trust Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4 text-blue-400" />
                  <span className="text-sm text-gray-300">
                    Reciprocity: {(insight.reciprocity_index * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-green-400" />
                  <span className="text-sm text-gray-300">
                    Response: {insight.response_time_avg.toFixed(1)}h avg
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4 text-purple-400" />
                  <span className="text-sm text-gray-300">
                    Frequency: {insight.interaction_frequency.toFixed(1)}/week
                  </span>
                </div>
              </div>

              {/* AI Summary */}
              {insight.trust_summary && (
                <div className="mb-4 p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Eye className="w-4 h-4 text-blue-400" />
                    <span className="text-sm font-medium text-gray-300">AI Insight</span>
                  </div>
                  <p className="text-sm text-gray-300 leading-relaxed">{insight.trust_summary}</p>
                </div>
              )}

              {/* Suggested Actions */}
              {insight.suggested_actions && insight.suggested_actions.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Suggested Actions</h4>
                  <div className="flex flex-wrap gap-2">
                    {insight.suggested_actions.map((action, index) => (
                      <span 
                        key={index}
                        className="px-3 py-1 bg-purple-600/20 text-purple-300 rounded-full text-xs border border-purple-500/30"
                      >
                        {action}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredInsights.length === 0 && (
        <div className="text-center py-12">
          <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-300 mb-2">
            {selectedTier === 'all' ? 'No Trust Insights Available' : `No ${trustTierConfig[selectedTier as keyof typeof trustTierConfig]?.title} Contacts`}
          </h3>
          <p className="text-gray-400 mb-4">
            {selectedTier === 'all' 
              ? 'Start by adding contacts and logging interactions to generate trust insights.'
              : 'No contacts found in this trust tier.'}
          </p>
          <button
            onClick={updateTrustInsights}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
          >
            Generate Insights
          </button>
        </div>
      )}
    </div>
  );
};

export default TrustInsights;