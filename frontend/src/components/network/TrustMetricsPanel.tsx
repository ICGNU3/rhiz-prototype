import React, { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Contact, TrustInsight, TrustMetric } from '../../types/api';
import { 
  Heart, TrendingUp, Clock, MessageCircle, Calendar, 
  Mail, Phone, Building, User, X, RefreshCw 
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TrustMetricsPanelProps {
  contactId: string | null;
  contact: Contact | null;
  trustInsights: TrustInsight[];
  onClose: () => void;
}

const TrustMetricsPanel: React.FC<TrustMetricsPanelProps> = ({
  contactId,
  contact,
  trustInsights,
  onClose
}) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  // Get trust insight for the selected contact
  const contactTrustInsight = trustInsights.find(insight => insight.contact_id === contactId);

  // Fetch detailed trust metrics for charts
  const { data: trustMetrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['trust-metrics', contactId, selectedTimeRange],
    queryFn: async (): Promise<TrustMetrics | null> => {
      if (!contactId) return null;
      
      const response = await fetch(`/api/trust/metrics/${contactId}?range=${selectedTimeRange}`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        // Return mock data for demonstration
        return {
          contact_id: contactId,
          metrics: Array.from({ length: 10 }, (_, i) => ({
            trust_score: Math.random() * 100,
            response_time: Math.random() * 24,
            interaction_frequency: Math.random() * 10,
            reciprocity_score: Math.random() * 100,
          })),
          timestamps: Array.from({ length: 10 }, (_, i) => 
            new Date(Date.now() - (9 - i) * 24 * 60 * 60 * 1000).toISOString()
          )
        };
      }
      
      const result = await response.json();
      return result.data || result;
    },
    enabled: !!contactId
  });

  // Create/update chart
  useEffect(() => {
    if (!chartRef.current || !trustMetrics || !contactTrustInsight) return;

    // Destroy existing chart
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: trustMetrics.timestamps.map(timestamp => 
          new Date(timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        ),
        datasets: [
          {
            label: 'Trust Score',
            data: trustMetrics.metrics.map(m => m.trust_score),
            borderColor: '#4facfe',
            backgroundColor: 'rgba(79, 172, 254, 0.1)',
            tension: 0.4,
            fill: true,
          },
          {
            label: 'Response Time (hrs)',
            data: trustMetrics.metrics.map(m => m.response_time),
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            tension: 0.4,
            yAxisID: 'y1',
          },
          {
            label: 'Interaction Frequency',
            data: trustMetrics.metrics.map(m => m.interaction_frequency),
            borderColor: '#ec4899',
            backgroundColor: 'rgba(236, 72, 153, 0.1)',
            tension: 0.4,
            yAxisID: 'y1',
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#ffffff'
            }
          }
        },
        scales: {
          x: {
            ticks: { color: '#9ca3af' },
            grid: { color: 'rgba(156, 163, 175, 0.1)' }
          },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            ticks: { color: '#9ca3af' },
            grid: { color: 'rgba(156, 163, 175, 0.1)' },
            title: {
              display: true,
              text: 'Trust Score',
              color: '#ffffff'
            }
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            ticks: { color: '#9ca3af' },
            grid: { drawOnChartArea: false },
            title: {
              display: true,
              text: 'Time/Frequency',
              color: '#ffffff'
            }
          }
        }
      }
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [trustMetrics, contactTrustInsight]);

  if (!contactId || !contact) {
    return (
      <div className="glass-card p-6">
        <div className="text-center text-gray-400">
          <Heart className="w-12 h-12 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">Trust Insights</h3>
          <p>Click on a contact in the network to view detailed trust metrics and relationship intelligence.</p>
        </div>
      </div>
    );
  }

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'rooted': return 'text-green-400';
      case 'growing': return 'text-blue-400';
      case 'dormant': return 'text-yellow-400';
      case 'frayed': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'rooted': return '🌳';
      case 'growing': return '🌱';
      case 'dormant': return '😴';
      case 'frayed': return '💔';
      default: return '❓';
    }
  };

  return (
    <div className="glass-card p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-white">Trust Insights</h3>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-700/50 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-gray-400" />
        </button>
      </div>

      {/* Contact Info */}
      <div className="border-b border-gray-700/50 pb-4">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-blue-400 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-white" />
          </div>
          <div>
            <h4 className="text-lg font-semibold text-white">{contact.name}</h4>
            <p className="text-sm text-gray-400">{contact.title} at {contact.company}</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 gap-2 text-sm">
          {contact.email && (
            <div className="flex items-center space-x-2 text-gray-300">
              <Mail className="w-4 h-4" />
              <span>{contact.email}</span>
            </div>
          )}
          {contact.phone && (
            <div className="flex items-center space-x-2 text-gray-300">
              <Phone className="w-4 h-4" />
              <span>{contact.phone}</span>
            </div>
          )}
          {contact.company && (
            <div className="flex items-center space-x-2 text-gray-300">
              <Building className="w-4 h-4" />
              <span>{contact.company}</span>
            </div>
          )}
        </div>
      </div>

      {/* Trust Metrics Summary */}
      {contactTrustInsight && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Trust Tier</span>
            <div className={`flex items-center space-x-2 ${getTierColor(contactTrustInsight.trust_tier)}`}>
              <span className="text-lg">{getTierIcon(contactTrustInsight.trust_tier)}</span>
              <span className="font-semibold capitalize">{contactTrustInsight.trust_tier}</span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Trust Score</span>
            <div className="flex items-center space-x-2">
              <div className="w-20 h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-primary-500 to-blue-400 transition-all duration-300"
                  style={{ width: `${contactTrustInsight.trust_score}%` }}
                />
              </div>
              <span className="text-white font-semibold">{Math.round(contactTrustInsight.trust_score)}</span>
            </div>
          </div>

          {contactTrustInsight.response_time_avg && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Avg Response Time</span>
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-yellow-400" />
                <span className="text-white">{Math.round(contactTrustInsight.response_time_avg)}h</span>
              </div>
            </div>
          )}

          {contactTrustInsight.interaction_frequency && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Interaction Frequency</span>
              <div className="flex items-center space-x-2">
                <MessageCircle className="w-4 h-4 text-blue-400" />
                <span className="text-white">{contactTrustInsight.interaction_frequency}/week</span>
              </div>
            </div>
          )}

          {contactTrustInsight.last_interaction && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Last Interaction</span>
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-green-400" />
                <span className="text-white">
                  {new Date(contactTrustInsight.last_interaction).toLocaleDateString()}
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Time Range Selector */}
      <div className="flex space-x-2">
        {(['7d', '30d', '90d'] as const).map((range) => (
          <button
            key={range}
            onClick={() => setSelectedTimeRange(range)}
            className={`px-3 py-1 rounded-lg text-sm transition-colors ${
              selectedTimeRange === range
                ? 'bg-primary-600 text-white'
                : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
            }`}
          >
            {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
          </button>
        ))}
      </div>

      {/* Trust Metrics Chart */}
      <div className="relative">
        <h5 className="text-lg font-semibold text-white mb-3">Trust Metrics Over Time</h5>
        {metricsLoading ? (
          <div className="h-64 flex items-center justify-center">
            <RefreshCw className="w-6 h-6 text-primary-400 animate-spin" />
          </div>
        ) : (
          <div className="h-64">
            <canvas ref={chartRef} />
          </div>
        )}
      </div>

      {/* Suggested Actions */}
      {contactTrustInsight?.suggested_actions && contactTrustInsight.suggested_actions.length > 0 && (
        <div className="space-y-3">
          <h5 className="text-lg font-semibold text-white">Suggested Actions</h5>
          <div className="space-y-2">
            {contactTrustInsight.suggested_actions.map((action, index) => (
              <div key={index} className="p-3 bg-gray-700/30 rounded-lg">
                <p className="text-sm text-gray-300">{action}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Insights */}
      {contactTrustInsight?.insights && contactTrustInsight.insights.length > 0 && (
        <div className="space-y-3">
          <h5 className="text-lg font-semibold text-white">AI Insights</h5>
          <div className="space-y-2">
            {contactTrustInsight.insights.map((insight, index) => (
              <div key={index} className="p-3 bg-blue-900/20 border border-blue-700/30 rounded-lg">
                <p className="text-sm text-blue-200">{insight}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TrustMetricsPanel;