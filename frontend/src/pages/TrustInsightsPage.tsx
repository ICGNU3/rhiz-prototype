import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Clock, TrendingUp, RotateCcw, Users, Heart, AlertTriangle, 
  Activity, Calendar, MessageCircle, ArrowUpRight, ArrowDownRight,
  BarChart3, PieChart, LineChart
} from 'lucide-react';
import { trustAPI } from '../services/api';

interface TrustMetrics {
  contact_id: string;
  contact_name: string;
  contact_email?: string;
  contact_company?: string;
  
  // Time metrics
  relationship_duration_days: number;
  last_interaction_days_ago: number;
  interaction_frequency_score: number; // interactions per month
  
  // Trust metrics
  trust_score: number; // 0-100
  trust_trend: 'increasing' | 'stable' | 'decreasing';
  trust_tier: 'rooted' | 'growing' | 'dormant' | 'frayed';
  reliability_score: number; // based on response patterns
  
  // Reciprocity metrics
  reciprocity_score: number; // 0-100, balance of give/take
  outreach_balance: number; // who initiates more (-100 to 100)
  response_rate: number; // 0-100, their response rate to your messages
  mutual_value_score: number; // based on interactions quality
  
  // Interaction data
  total_interactions: number;
  recent_interactions: InteractionSummary[];
}

interface InteractionSummary {
  date: string;
  type: 'outbound' | 'inbound';
  channel: 'email' | 'phone' | 'meeting' | 'text' | 'other';
  sentiment_score?: number;
  response_time_hours?: number;
}

interface TrustOverview {
  total_relationships: number;
  avg_trust_score: number;
  avg_reciprocity_score: number;
  relationships_by_tier: Record<string, number>;
  trust_trend_summary: {
    improving: number;
    stable: number;
    declining: number;
  };
}

const TrustInsightsPage: React.FC = () => {
  const [selectedContact, setSelectedContact] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'overview' | 'details' | 'analytics'>('overview');
  const [sortBy, setSortBy] = useState<'trust' | 'time' | 'reciprocity'>('trust');
  const [filterTier, setFilterTier] = useState<string>('all');

  // Fetch trust metrics data
  const { 
    data: trustMetrics = [], 
    isLoading,
    error 
  } = useQuery({
    queryKey: ['trust-metrics'],
    queryFn: async () => {
      const response = await trustAPI.getTrustMetrics();
      return response.data?.metrics || [];
    },
    retry: 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Fetch overview data
  const { 
    data: overview,
    isLoading: overviewLoading
  } = useQuery({
    queryKey: ['trust-overview'],
    queryFn: async () => {
      const response = await trustAPI.getTrustOverview();
      return response.data;
    },
    retry: 2,
  });

  // Process and sort data
  const processedMetrics = useMemo(() => {
    let filtered = trustMetrics;
    
    // Filter by tier
    if (filterTier !== 'all') {
      filtered = filtered.filter((contact: TrustMetrics) => contact.trust_tier === filterTier);
    }
    
    // Sort by selected metric
    filtered.sort((a: TrustMetrics, b: TrustMetrics) => {
      switch (sortBy) {
        case 'trust':
          return b.trust_score - a.trust_score;
        case 'time':
          return a.last_interaction_days_ago - b.last_interaction_days_ago;
        case 'reciprocity':
          return b.reciprocity_score - a.reciprocity_score;
        default:
          return b.trust_score - a.trust_score;
      }
    });
    
    return filtered;
  }, [trustMetrics, sortBy, filterTier]);

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'rooted': return 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30';
      case 'growing': return 'text-blue-400 bg-blue-500/20 border-blue-500/30';
      case 'dormant': return 'text-amber-400 bg-amber-500/20 border-amber-500/30';
      case 'frayed': return 'text-red-400 bg-red-500/20 border-red-500/30';
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    }
  };

  const getTrustTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return <ArrowUpRight className="w-4 h-4 text-green-400" />;
      case 'decreasing':
        return <ArrowDownRight className="w-4 h-4 text-red-400" />;
      default:
        return <Activity className="w-4 h-4 text-gray-400" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400';
    if (score >= 60) return 'text-blue-400';
    if (score >= 40) return 'text-amber-400';
    return 'text-red-400';
  };

  const formatDuration = (days: number) => {
    if (days < 30) return `${days} days`;
    if (days < 365) return `${Math.floor(days / 30)} months`;
    return `${Math.floor(days / 365)} years`;
  };

  if (isLoading || overviewLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 flex items-center justify-center">
        <div className="glass-card p-8 flex items-center space-x-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
          <span className="text-white text-lg">Loading trust analytics...</span>
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
            <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
              Trust Analytics
            </h1>
            <p className="text-gray-300 mt-2">
              Visualize time, trust, and reciprocity in your relationships
            </p>
          </div>
          
          <div className="flex space-x-3">
            {['overview', 'details', 'analytics'].map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode as any)}
                className={`px-4 py-2 rounded-lg transition-all capitalize ${
                  viewMode === mode
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-400/30'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700/30'
                }`}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>

        {/* Overview Mode */}
        {viewMode === 'overview' && overview && (
          <>
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <Users className="w-8 h-8 text-blue-400" />
                  <span className="text-2xl font-bold text-blue-400">
                    {overview.total_relationships}
                  </span>
                </div>
                <h3 className="text-white font-semibold mb-1">Total Relationships</h3>
                <p className="text-gray-400 text-sm">Active connections tracked</p>
              </div>

              <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <Heart className="w-8 h-8 text-emerald-400" />
                  <span className="text-2xl font-bold text-emerald-400">
                    {Math.round(overview.avg_trust_score)}%
                  </span>
                </div>
                <h3 className="text-white font-semibold mb-1">Average Trust</h3>
                <p className="text-gray-400 text-sm">Network trust health</p>
              </div>

              <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <RotateCcw className="w-8 h-8 text-purple-400" />
                  <span className="text-2xl font-bold text-purple-400">
                    {Math.round(overview.avg_reciprocity_score)}%
                  </span>
                </div>
                <h3 className="text-white font-semibold mb-1">Reciprocity</h3>
                <p className="text-gray-400 text-sm">Balance of give and take</p>
              </div>

              <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <TrendingUp className="w-8 h-8 text-amber-400" />
                  <span className="text-2xl font-bold text-emerald-400">
                    {overview.trust_trend_summary.improving}
                  </span>
                </div>
                <h3 className="text-white font-semibold mb-1">Improving</h3>
                <p className="text-gray-400 text-sm">Relationships getting stronger</p>
              </div>
            </div>

            {/* Trust Tier Distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="glass-card p-6">
                <h3 className="text-white font-semibold mb-6 flex items-center">
                  <PieChart className="w-5 h-5 mr-2 text-blue-400" />
                  Trust Tier Distribution
                </h3>
                <div className="space-y-4">
                  {Object.entries(overview.relationships_by_tier).map(([tier, count]) => (
                    <div key={tier} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`px-3 py-1 rounded-full text-xs border ${getTierColor(tier)}`}>
                          {tier.charAt(0).toUpperCase() + tier.slice(1)}
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="text-gray-400">{count}</span>
                        <div className="w-20 bg-gray-700 rounded-full h-2">
                          <div 
                            className="h-2 rounded-full bg-gradient-to-r from-blue-400 to-purple-400"
                            style={{ width: `${(count as number / overview.total_relationships) * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="glass-card p-6">
                <h3 className="text-white font-semibold mb-6 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-emerald-400" />
                  Trust Trends
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                      <span className="text-white">Improving</span>
                    </div>
                    <span className="text-emerald-400 font-semibold">
                      {overview.trust_trend_summary.improving}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Activity className="w-4 h-4 text-blue-400" />
                      <span className="text-white">Stable</span>
                    </div>
                    <span className="text-blue-400 font-semibold">
                      {overview.trust_trend_summary.stable}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <ArrowDownRight className="w-4 h-4 text-red-400" />
                      <span className="text-white">Declining</span>
                    </div>
                    <span className="text-red-400 font-semibold">
                      {overview.trust_trend_summary.declining}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Details Mode */}
        {viewMode === 'details' && (
          <>
            {/* Filters and Sorting */}
            <div className="glass-card p-6 mb-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center space-x-4">
                  <label className="text-gray-300 text-sm">Sort by:</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className="bg-gray-800 border border-gray-600 rounded-lg px-3 py-1 text-white"
                  >
                    <option value="trust">Trust Score</option>
                    <option value="time">Last Interaction</option>
                    <option value="reciprocity">Reciprocity</option>
                  </select>
                </div>
                
                <div className="flex items-center space-x-4">
                  <label className="text-gray-300 text-sm">Filter tier:</label>
                  <select
                    value={filterTier}
                    onChange={(e) => setFilterTier(e.target.value)}
                    className="bg-gray-800 border border-gray-600 rounded-lg px-3 py-1 text-white"
                  >
                    <option value="all">All Tiers</option>
                    <option value="rooted">Rooted</option>
                    <option value="growing">Growing</option>
                    <option value="dormant">Dormant</option>
                    <option value="frayed">Frayed</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Contact Cards with Trust Metrics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {processedMetrics.map((contact: any) => (
                <div 
                  key={contact.contact_id} 
                  className="glass-card p-6 cursor-pointer hover:border-blue-400/50 transition-all"
                  onClick={() => setSelectedContact(
                    selectedContact === contact.contact_id ? null : contact.contact_id
                  )}
                >
                  {/* Contact Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="text-white font-semibold">{contact.contact_name}</h4>
                      {contact.contact_company && (
                        <p className="text-gray-400 text-sm">{contact.contact_company}</p>
                      )}
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs border ${getTierColor(contact.trust_tier)}`}>
                      {contact.trust_tier}
                    </div>
                  </div>

                  {/* Three Key Metrics */}
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    {/* Time Metric */}
                    <div className="text-center">
                      <Clock className="w-5 h-5 mx-auto mb-1 text-blue-400" />
                      <div className="text-white font-semibold text-sm">
                        {formatDuration(contact.relationship_duration_days)}
                      </div>
                      <div className="text-gray-400 text-xs">Duration</div>
                    </div>

                    {/* Trust Metric */}
                    <div className="text-center">
                      <Heart className={`w-5 h-5 mx-auto mb-1 ${getScoreColor(contact.trust_score)}`} />
                      <div className={`font-semibold text-sm ${getScoreColor(contact.trust_score)}`}>
                        {contact.trust_score}%
                      </div>
                      <div className="text-gray-400 text-xs">Trust</div>
                    </div>

                    {/* Reciprocity Metric */}
                    <div className="text-center">
                      <RotateCcw className={`w-5 h-5 mx-auto mb-1 ${getScoreColor(contact.reciprocity_score)}`} />
                      <div className={`font-semibold text-sm ${getScoreColor(contact.reciprocity_score)}`}>
                        {contact.reciprocity_score}%
                      </div>
                      <div className="text-gray-400 text-xs">Balance</div>
                    </div>
                  </div>

                  {/* Additional Details */}
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-400">
                        {contact.last_interaction_days_ago === 0 
                          ? 'Today' 
                          : `${contact.last_interaction_days_ago}d ago`
                        }
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getTrustTrendIcon(contact.trust_trend)}
                      <span className="text-gray-400">{contact.total_interactions}</span>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {selectedContact === contact.contact_id && (
                    <div className="mt-4 pt-4 border-t border-gray-700">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">Response Rate:</span>
                          <span className={`ml-2 ${getScoreColor(contact.response_rate)}`}>
                            {contact.response_rate}%
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400">Reliability:</span>
                          <span className={`ml-2 ${getScoreColor(contact.reliability_score)}`}>
                            {contact.reliability_score}%
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400">Frequency:</span>
                          <span className="text-white ml-2">
                            {contact.interaction_frequency_score}/mo
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400">Initiates:</span>
                          <span className={`ml-2 ${
                            contact.outreach_balance > 0 ? 'text-emerald-400' : 
                            contact.outreach_balance < 0 ? 'text-amber-400' : 'text-gray-400'
                          }`}>
                            {contact.outreach_balance > 0 ? 'They do' : 
                             contact.outreach_balance < 0 ? 'You do' : 'Balanced'}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}

        {/* Analytics Mode */}
        {viewMode === 'analytics' && (
          <div className="glass-card p-6">
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <LineChart className="w-16 h-16 mx-auto mb-4 text-gray-500" />
                <h3 className="text-white text-xl mb-2">Advanced Analytics</h3>
                <p className="text-gray-400">
                  Detailed trust analytics charts and trends coming soon
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {processedMetrics.length === 0 && viewMode === 'details' && (
          <div className="glass-card p-12 text-center">
            <Users className="w-16 h-16 mx-auto mb-4 text-gray-500" />
            <h3 className="text-white text-xl mb-2">No Relationships Found</h3>
            <p className="text-gray-400">
              {filterTier === 'all' 
                ? 'Add contacts to start tracking trust metrics'
                : `No contacts found in the ${filterTier} tier`
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrustInsightsPage;