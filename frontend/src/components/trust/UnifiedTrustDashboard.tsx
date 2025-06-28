import React, { useState, useEffect, useCallback } from 'react';
import type { Contact, TrustInsight } from '../../types/api';

interface UnifiedTrustDashboardProps {
  contacts?: Contact[];
  onTrustUpdate?: (contactId: string, trustScore: number) => void;
  className?: string;
  showHeader?: boolean;
}

interface TrustTier {
  name: string;
  range: [number, number];
  color: string;
  bgColor: string;
  description: string;
  count: number;
}

interface TrustMetrics {
  overallHealth: number;
  averageTrust: number;
  totalContacts: number;
  responseRate: number;
  reciprocityIndex: number;
  dormantContacts: number;
}

export default function UnifiedTrustDashboard({
  contacts = [],
  onTrustUpdate,
  className = '',
  showHeader = true
}: UnifiedTrustDashboardProps) {
  const [trustInsights, setTrustInsights] = useState<TrustInsight[]>([]);
  const [metrics, setMetrics] = useState<TrustMetrics>({
    overallHealth: 0,
    averageTrust: 0,
    totalContacts: 0,
    responseRate: 0,
    reciprocityIndex: 0,
    dormantContacts: 0
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'tiers' | 'insights' | 'actions'>('overview');

  const fetchTrustData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Fetch trust insights
      const insightsResponse = await fetch('/api/trust/insights');
      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setTrustInsights(insightsData.insights || []);
      }

      // Fetch trust health metrics
      const healthResponse = await fetch('/api/trust/health');
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setMetrics(healthData);
      }
    } catch (error) {
      console.error('Failed to fetch trust data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTrustData();
  }, [fetchTrustData]);

  const trustTiers: TrustTier[] = [
    {
      name: 'Rooted',
      range: [4, 5],
      color: '#10b981',
      bgColor: 'rgba(16, 185, 129, 0.1)',
      description: 'Strong, reliable relationships with consistent engagement',
      count: trustInsights.filter(t => t.trust_score >= 4).length
    },
    {
      name: 'Growing',
      range: [3, 4],
      color: '#3b82f6',
      bgColor: 'rgba(59, 130, 246, 0.1)',
      description: 'Developing relationships with positive momentum',
      count: trustInsights.filter(t => t.trust_score >= 3 && t.trust_score < 4).length
    },
    {
      name: 'Neutral',
      range: [2, 3],
      color: '#f59e0b',
      bgColor: 'rgba(245, 158, 11, 0.1)',
      description: 'Stable but limited engagement',
      count: trustInsights.filter(t => t.trust_score >= 2 && t.trust_score < 3).length
    },
    {
      name: 'Dormant',
      range: [1, 2],
      color: '#ef4444',
      bgColor: 'rgba(239, 68, 68, 0.1)',
      description: 'Requires attention and re-engagement',
      count: trustInsights.filter(t => t.trust_score >= 1 && t.trust_score < 2).length
    }
  ];

  const getHealthColor = (score: number) => {
    if (score >= 80) return '#10b981'; // Green
    if (score >= 60) return '#3b82f6'; // Blue
    if (score >= 40) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  const formatPercentage = (value: number) => `${Math.round(value)}%`;

  if (loading) {
    return (
      <div className={`trust-dashboard ${className}`}>
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '300px' }}>
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading trust insights...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`trust-dashboard ${className}`}>
      {showHeader && (
        <div className="trust-header mb-4">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h3 className="text-gradient mb-1">Trust Intelligence</h3>
              <p className="text-muted mb-0">Real-time relationship health and engagement insights</p>
            </div>
            <button 
              className="btn btn-glass btn-sm"
              onClick={fetchTrustData}
              disabled={loading}
            >
              <i className="bi bi-arrow-clockwise me-1" />
              Refresh
            </button>
          </div>

          {/* Navigation Tabs */}
          <div className="trust-tabs mb-4">
            <div className="nav nav-pills" style={{ background: 'rgba(255, 255, 255, 0.05)', borderRadius: '12px', padding: '4px' }}>
              {[
                { id: 'overview', icon: 'bi-speedometer2', label: 'Overview' },
                { id: 'tiers', icon: 'bi-layers', label: 'Trust Tiers' },
                { id: 'insights', icon: 'bi-lightbulb', label: 'Insights' },
                { id: 'actions', icon: 'bi-check-circle', label: 'Actions' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  className={`nav-link ${activeTab === tab.id ? 'active' : ''}`}
                  style={{
                    background: activeTab === tab.id ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
                    border: 'none',
                    borderRadius: '8px',
                    color: activeTab === tab.id ? '#3b82f6' : '#adb5bd'
                  }}
                  onClick={() => setActiveTab(tab.id as any)}
                >
                  <i className={`${tab.icon} me-2`} />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab Content */}
      <div className="trust-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {/* Health Score Card */}
            <div className="row mb-4">
              <div className="col-md-6">
                <div className="glass-card p-4 text-center">
                  <h5 className="text-light mb-3">Relationship Health Score</h5>
                  <div 
                    className="health-score-circle mx-auto mb-3"
                    style={{
                      width: '120px',
                      height: '120px',
                      borderRadius: '50%',
                      background: `conic-gradient(${getHealthColor(metrics.overallHealth)} ${metrics.overallHealth * 3.6}deg, rgba(255, 255, 255, 0.1) 0deg)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative'
                    }}
                  >
                    <div 
                      style={{
                        width: '100px',
                        height: '100px',
                        borderRadius: '50%',
                        background: 'rgba(13, 17, 23, 0.8)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexDirection: 'column'
                      }}
                    >
                      <span className="h3 mb-0 fw-bold" style={{ color: getHealthColor(metrics.overallHealth) }}>
                        {Math.round(metrics.overallHealth)}
                      </span>
                      <small className="text-muted">Health</small>
                    </div>
                  </div>
                  <p className="text-muted mb-0">
                    Your relationship network is{' '}
                    <span style={{ color: getHealthColor(metrics.overallHealth) }}>
                      {metrics.overallHealth >= 80 ? 'excellent' : 
                       metrics.overallHealth >= 60 ? 'good' : 
                       metrics.overallHealth >= 40 ? 'fair' : 'needs attention'}
                    </span>
                  </p>
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="glass-card p-4">
                  <h5 className="text-light mb-3">Key Metrics</h5>
                  <div className="row g-3">
                    <div className="col-6">
                      <div className="metric-item text-center">
                        <div className="h4 mb-1 text-primary">{metrics.totalContacts}</div>
                        <small className="text-muted">Total Contacts</small>
                      </div>
                    </div>
                    <div className="col-6">
                      <div className="metric-item text-center">
                        <div className="h4 mb-1 text-success">{formatPercentage(metrics.responseRate)}</div>
                        <small className="text-muted">Response Rate</small>
                      </div>
                    </div>
                    <div className="col-6">
                      <div className="metric-item text-center">
                        <div className="h4 mb-1 text-info">{metrics.averageTrust.toFixed(1)}</div>
                        <small className="text-muted">Avg Trust Score</small>
                      </div>
                    </div>
                    <div className="col-6">
                      <div className="metric-item text-center">
                        <div className="h4 mb-1 text-warning">{formatPercentage(metrics.reciprocityIndex)}</div>
                        <small className="text-muted">Reciprocity</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'tiers' && (
          <div className="tiers-tab">
            <div className="row">
              {trustTiers.map((tier, index) => (
                <div key={tier.name} className="col-md-6 col-lg-3 mb-4">
                  <div 
                    className="glass-card p-4 h-100"
                    style={{ borderLeft: `4px solid ${tier.color}` }}
                  >
                    <div className="d-flex justify-content-between align-items-center mb-2">
                      <h6 className="mb-0" style={{ color: tier.color }}>{tier.name}</h6>
                      <span className="badge" style={{ backgroundColor: tier.bgColor, color: tier.color }}>
                        {tier.count}
                      </span>
                    </div>
                    <div className="trust-range mb-2">
                      <small className="text-muted">Trust Score: {tier.range[0]} - {tier.range[1]}</small>
                    </div>
                    <p className="small text-light mb-0">{tier.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="insights-tab">
            <div className="row">
              {trustInsights.slice(0, 6).map((insight) => (
                <div key={insight.contact_id} className="col-md-6 col-lg-4 mb-4">
                  <div className="glass-card p-3">
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <div>
                        <h6 className="mb-1">{insight.contact_id}</h6>
                        <small className="text-muted">Contact</small>
                      </div>
                      <div className="trust-score-badge">
                        <span 
                          className="badge"
                          style={{ 
                            backgroundColor: insight.trust_score >= 4 ? '#10b981' : 
                                           insight.trust_score >= 3 ? '#3b82f6' : 
                                           insight.trust_score >= 2 ? '#f59e0b' : '#ef4444',
                            color: 'white'
                          }}
                        >
                          {insight.trust_score.toFixed(1)}
                        </span>
                      </div>
                    </div>
                    <div className="trust-summary">
                      <p className="small text-light mb-2">Trust insight data</p>
                      <div className="trust-factors">
                        <small className="text-muted">
                          Trust Score: {insight.trust_score}
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'actions' && (
          <div className="actions-tab">
            <div className="row">
              <div className="col-lg-8">
                <div className="glass-card p-4">
                  <h5 className="text-light mb-3">Recommended Actions</h5>
                  <div className="action-list">
                    <div className="action-item d-flex align-items-center p-3 mb-3 rounded" style={{ background: 'rgba(239, 68, 68, 0.1)' }}>
                      <div className="action-icon me-3">
                        <i className="bi bi-exclamation-triangle text-warning" style={{ fontSize: '1.5rem' }} />
                      </div>
                      <div className="flex-grow-1">
                        <h6 className="mb-1">Re-engage Dormant Contacts</h6>
                        <p className="small text-muted mb-0">
                          {metrics.dormantContacts} contacts haven't been contacted recently
                        </p>
                      </div>
                      <button className="btn btn-outline-warning btn-sm">
                        <i className="bi bi-arrow-right me-1" />
                        View
                      </button>
                    </div>

                    <div className="action-item d-flex align-items-center p-3 mb-3 rounded" style={{ background: 'rgba(59, 130, 246, 0.1)' }}>
                      <div className="action-icon me-3">
                        <i className="bi bi-graph-up text-primary" style={{ fontSize: '1.5rem' }} />
                      </div>
                      <div className="flex-grow-1">
                        <h6 className="mb-1">Strengthen Growing Relationships</h6>
                        <p className="small text-muted mb-0">
                          Focus on contacts with positive momentum
                        </p>
                      </div>
                      <button className="btn btn-outline-primary btn-sm">
                        <i className="bi bi-arrow-right me-1" />
                        View
                      </button>
                    </div>

                    <div className="action-item d-flex align-items-center p-3 rounded" style={{ background: 'rgba(16, 185, 129, 0.1)' }}>
                      <div className="action-icon me-3">
                        <i className="bi bi-heart text-success" style={{ fontSize: '1.5rem' }} />
                      </div>
                      <div className="flex-grow-1">
                        <h6 className="mb-1">Maintain Strong Relationships</h6>
                        <p className="small text-muted mb-0">
                          Keep your rooted connections engaged
                        </p>
                      </div>
                      <button className="btn btn-outline-success btn-sm">
                        <i className="bi bi-arrow-right me-1" />
                        View
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="col-lg-4">
                <div className="glass-card p-4">
                  <h6 className="text-light mb-3">Quick Stats</h6>
                  <div className="stat-item d-flex justify-content-between mb-2">
                    <span className="text-muted">Contacts Added This Week</span>
                    <span className="text-light">5</span>
                  </div>
                  <div className="stat-item d-flex justify-content-between mb-2">
                    <span className="text-muted">Messages Sent</span>
                    <span className="text-light">12</span>
                  </div>
                  <div className="stat-item d-flex justify-content-between mb-2">
                    <span className="text-muted">Meetings Scheduled</span>
                    <span className="text-light">3</span>
                  </div>
                  <div className="stat-item d-flex justify-content-between">
                    <span className="text-muted">Response Rate</span>
                    <span className="text-success">{formatPercentage(metrics.responseRate)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Additional styles
const styles = `
.trust-dashboard .glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.trust-dashboard .glass-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.trust-dashboard .text-gradient {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.trust-dashboard .btn-glass {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  backdrop-filter: blur(10px);
}

.trust-dashboard .btn-glass:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}
`;

export { styles as UnifiedTrustDashboardStyles };