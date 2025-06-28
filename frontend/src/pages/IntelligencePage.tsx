import React, { useState, useEffect } from 'react';

interface Insight {
  contact_name?: string;
  days_since_contact?: number;
  description: string;
  priority: string;
  suggested_action: string;
  title: string;
  type: string;
}

interface TrustData {
  trust_summary: {
    total_contacts: number;
    rooted_count: number;
    growing_count: number;
    dormant_count: number;
    frayed_count: number;
    trust_health_score: number;
  };
  trust_insights: Array<{
    type: string;
    title: string;
    description: string;
    priority: string;
    actionable_steps: string[];
  }>;
  relationship_maintenance: Array<{
    contact_name: string;
    priority: string;
    recommended_action: string;
    reason: string;
  }>;
}

const IntelligencePage: React.FC = () => {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [trustData, setTrustData] = useState<TrustData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'insights' | 'trust'>('insights');

  useEffect(() => {
    const fetchIntelligence = async () => {
      try {
        setLoading(true);
        
        // Fetch both insights and trust data
        const [insightsResponse, trustResponse] = await Promise.all([
          fetch('/api/insights', { credentials: 'include' }),
          fetch('/api/trust', { credentials: 'include' })
        ]);

        if (insightsResponse.ok) {
          const insightsData = await insightsResponse.json();
          setInsights(insightsData.insights || []);
        }

        if (trustResponse.ok) {
          const trustResponseData = await trustResponse.json();
          setTrustData(trustResponseData.trust_data || null);
        }
      } catch (error) {
        console.error('Error fetching intelligence data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchIntelligence();
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
      case 'urgent':
        return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'medium':
      case 'important':
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      default:
        return 'text-green-400 bg-green-500/10 border-green-500/20';
    }
  };

  const getTrustTierColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto"></div>
            <p className="text-white/70 mt-4">Generating AI insights...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      {/* Background orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent mb-4">
            AI Intelligence
          </h1>
          <p className="text-white/70 text-lg">
            AI-powered insights to strengthen your relationships and achieve your goals
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-8">
          <button
            onClick={() => setActiveTab('insights')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'insights'
                ? 'bg-purple-500/20 text-white border border-purple-500/30 backdrop-blur-sm'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            Relationship Insights
          </button>
          <button
            onClick={() => setActiveTab('trust')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'trust'
                ? 'bg-purple-500/20 text-white border border-purple-500/30 backdrop-blur-sm'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            Trust Analysis
          </button>
        </div>

        {/* Content */}
        {activeTab === 'insights' && (
          <div className="space-y-6">
            {insights.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-white/70">No insights available</p>
              </div>
            ) : (
              insights.map((insight, index) => (
                <div
                  key={index}
                  className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all"
                >
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-xl font-semibold text-white">{insight.title}</h3>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(
                        insight.priority
                      )}`}
                    >
                      {insight.priority.toUpperCase()}
                    </span>
                  </div>
                  
                  <p className="text-white/80 mb-4">{insight.description}</p>
                  
                  <div className="bg-purple-500/10 rounded-lg p-4 border border-purple-500/20">
                    <h4 className="text-purple-200 font-medium mb-2">Suggested Action:</h4>
                    <p className="text-white/90">{insight.suggested_action}</p>
                  </div>

                  {insight.contact_name && (
                    <div className="mt-4 text-sm text-white/60">
                      Contact: <span className="text-white">{insight.contact_name}</span>
                      {insight.days_since_contact && (
                        <span className="ml-4">
                          Last contact: {insight.days_since_contact} days ago
                        </span>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'trust' && trustData && (
          <div className="space-y-6">
            {/* Trust Summary */}
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
              <h3 className="text-xl font-semibold text-white mb-4">Trust Health Overview</h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">{trustData.trust_summary.rooted_count}</div>
                  <div className="text-white/60 text-sm">Rooted</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-400">{trustData.trust_summary.growing_count}</div>
                  <div className="text-white/60 text-sm">Growing</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-400">{trustData.trust_summary.dormant_count}</div>
                  <div className="text-white/60 text-sm">Dormant</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-400">{trustData.trust_summary.frayed_count}</div>
                  <div className="text-white/60 text-sm">Frayed</div>
                </div>
              </div>

              <div className="text-center">
                <div className={`text-3xl font-bold ${getTrustTierColor(trustData.trust_summary.trust_health_score)}`}>
                  {trustData.trust_summary.trust_health_score}%
                </div>
                <div className="text-white/60">Overall Trust Health Score</div>
              </div>
            </div>

            {/* Trust Insights */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-white">Trust Insights</h3>
              {trustData.trust_insights.map((insight, index) => (
                <div
                  key={index}
                  className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10"
                >
                  <div className="flex items-start justify-between mb-4">
                    <h4 className="text-lg font-semibold text-white">{insight.title}</h4>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(
                        insight.priority
                      )}`}
                    >
                      {insight.priority.toUpperCase()}
                    </span>
                  </div>
                  
                  <p className="text-white/80 mb-4">{insight.description}</p>
                  
                  <div className="bg-blue-500/10 rounded-lg p-4 border border-blue-500/20">
                    <h5 className="text-blue-200 font-medium mb-2">Action Steps:</h5>
                    <ul className="text-white/90 space-y-1">
                      {insight.actionable_steps.map((step, stepIndex) => (
                        <li key={stepIndex} className="flex items-start">
                          <span className="text-blue-400 mr-2">•</span>
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>

            {/* Relationship Maintenance */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-white">Relationship Maintenance</h3>
              {trustData.relationship_maintenance.map((item, index) => (
                <div
                  key={index}
                  className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10"
                >
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="text-lg font-semibold text-white">{item.contact_name}</h4>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(
                        item.priority
                      )}`}
                    >
                      {item.priority.toUpperCase()}
                    </span>
                  </div>
                  
                  <p className="text-white/80 mb-3">{item.reason}</p>
                  
                  <div className="bg-green-500/10 rounded-lg p-4 border border-green-500/20">
                    <h5 className="text-green-200 font-medium mb-2">Recommended Action:</h5>
                    <p className="text-white/90">{item.recommended_action}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IntelligencePage;