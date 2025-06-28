import React, { useState, useEffect } from 'react';
import { Shield, TrendingUp, Users, Heart, AlertTriangle, CheckCircle } from 'lucide-react';

interface TrustInsight {
  contact_id: string;
  contact_name: string;
  trust_score: number;
  tier: 'rooted' | 'growing' | 'dormant' | 'frayed';
  last_interaction: string;
  response_rate: number;
  reciprocity_score: number;
  suggested_action: string;
}

interface TrustTier {
  name: string;
  count: number;
  percentage: number;
  color: string;
  icon: React.ComponentType;
}

const TrustPage: React.FC = () => {
  const [trustInsights, setTrustInsights] = useState<TrustInsight[]>([]);
  const [trustTiers, setTrustTiers] = useState<TrustTier[]>([]);
  const [selectedTier, setSelectedTier] = useState<string>('all');
  const [overallTrustHealth, setOverallTrustHealth] = useState(0);

  useEffect(() => {
    // Load trust insights data
    fetch('/api/trust/insights')
      .then(res => res.json())
      .then(data => setTrustInsights(data.insights || []))
      .catch(err => console.error('Failed to load trust insights:', err));

    // Load trust tier distribution
    fetch('/api/trust/tiers')
      .then(res => res.json())
      .then(data => setTrustTiers(data.tiers || []))
      .catch(err => console.error('Failed to load trust tiers:', err));

    // Load overall trust health
    fetch('/api/trust/health')
      .then(res => res.json())
      .then(data => setOverallTrustHealth(data.health_score || 0))
      .catch(err => console.error('Failed to load trust health:', err));
  }, []);

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'rooted': return 'text-success';
      case 'growing': return 'text-info';
      case 'dormant': return 'text-warning';
      case 'frayed': return 'text-danger';
      default: return 'text-secondary';
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'rooted': return CheckCircle;
      case 'growing': return TrendingUp;
      case 'dormant': return Users;
      case 'frayed': return AlertTriangle;
      default: return Shield;
    }
  };

  const filteredInsights = selectedTier === 'all' 
    ? trustInsights 
    : trustInsights.filter(insight => insight.tier === selectedTier);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Trust Insights
          </h1>
          <p className="text-gray-300 mt-2">
            Real-time relationship intelligence and trust analysis
          </p>
        </div>

        {/* Trust Health Overview */}
        <div className="glass-card p-6 mb-8">
          <div className="row g-4">
            <div className="col-md-4">
              <div className="text-center">
                <div className="d-flex align-items-center justify-content-center mb-3">
                  <Shield className="w-8 h-8 text-primary me-3" />
                  <div>
                    <h3 className="text-white mb-0">{overallTrustHealth}%</h3>
                    <small className="text-muted">Overall Trust Health</small>
                  </div>
                </div>
                <div className="progress" style={{height: '8px'}}>
                  <div 
                    className="progress-bar bg-primary" 
                    style={{width: `${overallTrustHealth}%`}}
                  />
                </div>
              </div>
            </div>
            <div className="col-md-8">
              <h5 className="text-white mb-3">Trust Tier Distribution</h5>
              <div className="row g-3">
                {trustTiers.map((tier, index) => {
                  const Icon = getTierIcon(tier.name.toLowerCase());
                  return (
                    <div key={index} className="col-md-3">
                      <div className="glass-card p-3 text-center">
                        <Icon className={`w-6 h-6 ${getTierColor(tier.name.toLowerCase())} mb-2`} />
                        <h6 className="text-white mb-1">{tier.count}</h6>
                        <small className="text-muted">{tier.name}</small>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Trust Insights List */}
        <div className="row">
          <div className="col-lg-8">
            <div className="glass-card p-6">
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h3 className="text-white mb-0">Relationship Analysis</h3>
                <div className="dropdown">
                  <select 
                    className="form-select bg-dark border-secondary text-white"
                    value={selectedTier}
                    onChange={(e) => setSelectedTier(e.target.value)}
                  >
                    <option value="all">All Relationships</option>
                    <option value="rooted">Rooted</option>
                    <option value="growing">Growing</option>
                    <option value="dormant">Dormant</option>
                    <option value="frayed">Frayed</option>
                  </select>
                </div>
              </div>

              {filteredInsights.length > 0 ? (
                <div className="space-y-4">
                  {filteredInsights.map((insight, index) => {
                    const Icon = getTierIcon(insight.tier);
                    return (
                      <div key={index} className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50">
                        <div className="d-flex justify-content-between align-items-start mb-3">
                          <div className="d-flex align-items-center">
                            <Icon className={`w-5 h-5 ${getTierColor(insight.tier)} me-3`} />
                            <div>
                              <h6 className="text-white mb-1">{insight.contact_name}</h6>
                              <span className={`badge ${getTierColor(insight.tier).replace('text-', 'bg-')}/20`}>
                                {insight.tier.charAt(0).toUpperCase() + insight.tier.slice(1)}
                              </span>
                            </div>
                          </div>
                          <div className="text-end">
                            <div className="text-white font-semibold">{insight.trust_score}%</div>
                            <small className="text-muted">Trust Score</small>
                          </div>
                        </div>

                        <div className="row g-3 mb-3">
                          <div className="col-md-4">
                            <small className="text-muted">Response Rate</small>
                            <div className="progress mt-1" style={{height: '4px'}}>
                              <div 
                                className="progress-bar bg-info" 
                                style={{width: `${insight.response_rate}%`}}
                              />
                            </div>
                            <small className="text-info">{insight.response_rate}%</small>
                          </div>
                          <div className="col-md-4">
                            <small className="text-muted">Reciprocity</small>
                            <div className="progress mt-1" style={{height: '4px'}}>
                              <div 
                                className="progress-bar bg-success" 
                                style={{width: `${insight.reciprocity_score}%`}}
                              />
                            </div>
                            <small className="text-success">{insight.reciprocity_score}%</small>
                          </div>
                          <div className="col-md-4">
                            <small className="text-muted">Last Contact</small>
                            <div className="text-white">{insight.last_interaction}</div>
                          </div>
                        </div>

                        <div className="bg-blue-500/10 rounded-lg p-3">
                          <small className="text-blue-400 font-medium">Suggested Action:</small>
                          <p className="text-blue-300 mb-0 mt-1">{insight.suggested_action}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Heart className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No trust insights available</p>
                  <p className="text-sm">Add contacts and interactions to see relationship analysis</p>
                </div>
              )}
            </div>
          </div>

          {/* Trust Actions Sidebar */}
          <div className="col-lg-4">
            <div className="glass-card p-6 sticky-top">
              <h5 className="text-white mb-4">Trust Actions</h5>
              
              <div className="mb-4">
                <button className="btn btn-primary w-100 mb-3">
                  <TrendingUp className="w-4 h-4 me-2" />
                  Update Trust Signals
                </button>
                <button className="btn btn-outline-info w-100 mb-3">
                  <Users className="w-4 h-4 me-2" />
                  Analyze Network Health
                </button>
                <button className="btn btn-outline-success w-100">
                  <CheckCircle className="w-4 h-4 me-2" />
                  Export Trust Report
                </button>
              </div>

              <div className="bg-gray-800/30 rounded-lg p-4">
                <h6 className="text-white mb-3">Trust Building Tips</h6>
                <ul className="text-gray-300 text-sm space-y-2">
                  <li>• Respond promptly to strengthen growing relationships</li>
                  <li>• Re-engage dormant connections with value-first outreach</li>
                  <li>• Maintain regular contact with rooted relationships</li>
                  <li>• Address frayed relationships with thoughtful communication</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .glass-card {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-radius: 16px;
        }
        
        .space-y-4 > * + * {
          margin-top: 1rem;
        }
        
        .sticky-top {
          position: sticky;
          top: 1.5rem;
        }
        
        .cursor-pointer {
          cursor: pointer;
        }
      `}</style>
    </div>
  );
};

export default TrustPage;