/**
 * Enhanced Trust Panel with sentiment scores, interaction history, and contribution tracking
 */

import React, { useState, useEffect } from 'react';
import type { Contact, TrustInsight } from '../../types';

interface TrustPanelProps {
  contact: Contact;
  className?: string;
}

interface InteractionHistory {
  id: string;
  type: 'email' | 'meeting' | 'call' | 'message' | 'favor' | 'introduction';
  date: string;
  notes: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  contribution_type?: 'given' | 'received';
}

interface ContributionRecord {
  given: {
    introductions: number;
    favors: number;
    advice: number;
    resources: number;
  };
  received: {
    introductions: number;
    favors: number;
    advice: number;
    resources: number;
  };
}

const TrustPanel: React.FC<TrustPanelProps> = ({ contact, className = '' }) => {
  const [trustInsight, setTrustInsight] = useState<TrustInsight | null>(null);
  const [interactions, setInteractions] = useState<InteractionHistory[]>([]);
  const [contributions, setContributions] = useState<ContributionRecord | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'history' | 'contributions'>('overview');

  useEffect(() => {
    loadTrustData();
  }, [contact.id]);

  const loadTrustData = async () => {
    setIsLoading(true);
    try {
      // Load trust insight
      const trustResponse = await fetch(`/api/trust/insights/${contact.id}`, {
        credentials: 'include'
      });
      if (trustResponse.ok) {
        setTrustInsight(await trustResponse.json());
      }

      // Load interaction history
      const historyResponse = await fetch(`/api/contacts/${contact.id}/interactions`, {
        credentials: 'include'
      });
      if (historyResponse.ok) {
        setInteractions(await historyResponse.json());
      }

      // Load contribution record
      const contributionsResponse = await fetch(`/api/contacts/${contact.id}/contributions`, {
        credentials: 'include'
      });
      if (contributionsResponse.ok) {
        setContributions(await contributionsResponse.json());
      }
    } catch (error) {
      console.error('Failed to load trust data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getTrustTierColor = (tier: string) => {
    switch (tier) {
      case 'rooted': return 'text-green-400 bg-green-500';
      case 'growing': return 'text-blue-400 bg-blue-500';
      case 'dormant': return 'text-yellow-400 bg-yellow-500';
      case 'frayed': return 'text-red-400 bg-red-500';
      default: return 'text-gray-400 bg-gray-500';
    }
  };

  const renderTrustMeter = (score: number, label: string, color: string) => (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-gray-300">{label}</span>
        <span className="text-white font-medium">{Math.round(score * 100)}%</span>
      </div>
      <div className="w-full bg-white bg-opacity-10 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${color}`}
          style={{ width: `${score * 100}%` }}
        />
      </div>
    </div>
  );

  const renderReciprocityMeter = (given: number, received: number) => {
    const total = given + received;
    const givenPercent = total > 0 ? (given / total) * 100 : 50;
    const receivedPercent = total > 0 ? (received / total) * 100 : 50;

    return (
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-300">Reciprocity Balance</span>
          <span className="text-white font-medium">
            {given}:{received}
          </span>
        </div>
        <div className="w-full bg-white bg-opacity-10 rounded-full h-3 relative">
          <div
            className="h-3 bg-blue-500 rounded-l-full absolute left-0"
            style={{ width: `${givenPercent}%` }}
          />
          <div
            className="h-3 bg-green-500 rounded-r-full absolute right-0"
            style={{ width: `${receivedPercent}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-400">
          <span>Given: {given}</span>
          <span>Received: {received}</span>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className={`glass-card p-6 ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-white bg-opacity-20 rounded w-3/4"></div>
          <div className="h-3 bg-white bg-opacity-20 rounded w-1/2"></div>
          <div className="h-20 bg-white bg-opacity-20 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`glass-card p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white">Trust Insights</h3>
        {trustInsight && (
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${getTrustTierColor(trustInsight.trust_tier)} bg-opacity-20`}>
            {trustInsight.trust_tier.charAt(0).toUpperCase() + trustInsight.trust_tier.slice(1)}
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-6 bg-white bg-opacity-5 rounded-lg p-1">
        {[
          { key: 'overview', label: 'Overview', icon: '📊' },
          { key: 'history', label: 'History', icon: '📋' },
          { key: 'contributions', label: 'Contributions', icon: '🤝' }
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`flex-1 py-2 px-3 rounded-md transition-all text-sm ${
              activeTab === tab.key
                ? 'bg-white bg-opacity-10 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && trustInsight && (
        <div className="space-y-6">
          {/* Trust Score */}
          {renderTrustMeter(trustInsight.trust_score, 'Trust Score', 'bg-blue-500')}
          
          {/* Sentiment Score */}
          {renderTrustMeter(trustInsight.sentiment_score, 'Sentiment', 'bg-green-500')}
          
          {/* Responsiveness */}
          {renderTrustMeter(
            Math.min(1, 1 / (trustInsight.response_time_avg / 24)), 
            'Responsiveness', 
            'bg-purple-500'
          )}

          {/* Interaction Frequency */}
          {renderTrustMeter(
            Math.min(1, trustInsight.interaction_frequency / 10), 
            'Interaction Frequency', 
            'bg-orange-500'
          )}

          {/* Suggested Actions */}
          {trustInsight.suggested_actions.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-gray-300">Suggested Actions</h4>
              <div className="space-y-2">
                {trustInsight.suggested_actions.map((action, index) => (
                  <div
                    key={index}
                    className="p-3 bg-white bg-opacity-5 rounded-lg border border-white border-opacity-10"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm text-gray-300">{action}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'history' && (
        <div className="space-y-4">
          {interactions.length > 0 ? (
            <div className="space-y-3">
              {interactions.slice(0, 10).map((interaction) => (
                <div
                  key={interaction.id}
                  className="p-3 bg-white bg-opacity-5 rounded-lg border border-white border-opacity-10"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">
                        {interaction.type === 'email' && '📧'}
                        {interaction.type === 'meeting' && '🤝'}
                        {interaction.type === 'call' && '📞'}
                        {interaction.type === 'message' && '💬'}
                        {interaction.type === 'favor' && '🎁'}
                        {interaction.type === 'introduction' && '👥'}
                      </span>
                      <span className="text-sm font-medium text-white capitalize">
                        {interaction.type}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`w-2 h-2 rounded-full ${
                        interaction.sentiment === 'positive' ? 'bg-green-500' :
                        interaction.sentiment === 'negative' ? 'bg-red-500' : 'bg-yellow-500'
                      }`}></span>
                      <span className="text-xs text-gray-400">
                        {new Date(interaction.date).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-300">{interaction.notes}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <div className="text-4xl mb-2">📝</div>
              <p>No interaction history yet</p>
              <p className="text-sm">Start tracking your communications</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'contributions' && contributions && (
        <div className="space-y-6">
          {/* Reciprocity Overview */}
          <div>
            {renderReciprocityMeter(
              Object.values(contributions.given).reduce((a, b) => a + b, 0),
              Object.values(contributions.received).reduce((a, b) => a + b, 0)
            )}
          </div>

          {/* Detailed Breakdown */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-blue-300 flex items-center">
                <span className="mr-2">📤</span>
                You've Given
              </h4>
              <div className="space-y-2">
                {Object.entries(contributions.given).map(([type, count]) => (
                  <div key={type} className="flex justify-between text-sm">
                    <span className="text-gray-300 capitalize">{type}</span>
                    <span className="text-white font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-green-300 flex items-center">
                <span className="mr-2">📥</span>
                You've Received
              </h4>
              <div className="space-y-2">
                {Object.entries(contributions.received).map(([type, count]) => (
                  <div key={type} className="flex justify-between text-sm">
                    <span className="text-gray-300 capitalize">{type}</span>
                    <span className="text-white font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Add Contribution Button */}
          <button className="w-full py-2 px-4 bg-white bg-opacity-10 hover:bg-opacity-20 rounded-lg transition-all text-sm text-white border border-white border-opacity-20">
            + Add Contribution
          </button>
        </div>
      )}
    </div>
  );
};

export default TrustPanel;