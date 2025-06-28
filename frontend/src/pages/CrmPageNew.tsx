import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { BarChart3, Users, Calendar, TrendingUp, Loader2, AlertCircle, Filter, Search, ChevronRight } from 'lucide-react';
import { crmAPI } from '../services/api';

interface PipelineStage {
  pipeline_stage: string;
  count: number;
}

interface Interaction {
  id: string;
  contact_name: string;
  interaction_type: string;
  status: string;
  timestamp: string;
  subject?: string;
  summary?: string;
}

interface CrmStatistics {
  total_contacts: number;
  warm_contacts: number;
  active_contacts: number;
}

const CrmPage: React.FC = () => {
  const [filterStage, setFilterStage] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const queryClient = useQueryClient();

  // Fetch CRM data with React Query
  const { 
    data: crmData, 
    isLoading: crmLoading, 
    error: crmError, 
    refetch: refetchCrm 
  } = useQuery({
    queryKey: ['crm'],
    queryFn: async () => {
      const response = await crmAPI.getAll();
      return response.data;
    },
    retry: 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Update contact stage mutation
  const updateStageMutation = useMutation({
    mutationFn: ({ contactId, stage }: { contactId: string; stage: string }) => 
      crmAPI.updateContactStage(contactId, stage),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['crm'] });
    },
    onError: (error) => {
      console.error('Failed to update contact stage:', error);
    },
  });

  const pipeline = crmData?.pipeline || [];
  const recentInteractions = crmData?.recent_interactions || [];
  const statistics = crmData?.statistics || {};

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'hot': return 'bg-red-500/20 text-red-400 border-red-400/30';
      case 'warm': return 'bg-yellow-500/20 text-yellow-400 border-yellow-400/30';
      case 'cold': return 'bg-blue-500/20 text-blue-400 border-blue-400/30';
      case 'dormant': return 'bg-gray-500/20 text-gray-400 border-gray-400/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-400/30';
    }
  };

  const getStageIcon = (stage: string) => {
    switch (stage) {
      case 'hot': return '🔥';
      case 'warm': return '☀️';
      case 'cold': return '❄️';
      case 'dormant': return '😴';
      default: return '📊';
    }
  };

  const getInteractionIcon = (type: string) => {
    switch (type) {
      case 'email': return '📧';
      case 'call': return '📞';
      case 'meeting': return '🤝';
      case 'linkedin': return '💼';
      default: return '💬';
    }
  };

  // Loading state
  if (crmLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 flex items-center justify-center">
        <div className="glass-card p-8 flex items-center space-x-4">
          <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
          <span className="text-white text-lg">Loading CRM data...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (crmError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 flex items-center justify-center">
        <div className="glass-card p-8 flex flex-col items-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-400" />
          <div className="text-center">
            <h2 className="text-white text-xl font-semibold mb-2">Failed to load CRM data</h2>
            <p className="text-gray-400 mb-4">Unable to fetch your CRM information</p>
            <button 
              onClick={() => refetchCrm()}
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
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
              CRM Pipeline
            </h1>
            <p className="text-gray-300 mt-2">
              Track contacts through your relationship pipeline
            </p>
          </div>
          <button 
            onClick={() => refetchCrm()}
            className="glass-button px-6 py-3 rounded-lg text-purple-400 border border-purple-400/30 hover:bg-purple-400/10 flex items-center"
          >
            <BarChart3 className="w-5 h-5 mr-2" />
            Refresh Data
          </button>
        </div>

        {/* Statistics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <Users className="w-8 h-8 text-blue-400" />
              <span className="text-2xl font-bold text-blue-400">
                {statistics.total_contacts || 0}
              </span>
            </div>
            <h3 className="text-white font-semibold mb-1">Total Contacts</h3>
            <p className="text-gray-400 text-sm">All contacts in pipeline</p>
          </div>

          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="w-8 h-8 text-green-400" />
              <span className="text-2xl font-bold text-green-400">
                {statistics.warm_contacts || 0}
              </span>
            </div>
            <h3 className="text-white font-semibold mb-1">Warm Contacts</h3>
            <p className="text-gray-400 text-sm">High-value relationships</p>
          </div>

          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <Calendar className="w-8 h-8 text-yellow-400" />
              <span className="text-2xl font-bold text-yellow-400">
                {statistics.active_contacts || 0}
              </span>
            </div>
            <h3 className="text-white font-semibold mb-1">Active This Month</h3>
            <p className="text-gray-400 text-sm">Recently engaged contacts</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Pipeline Stages */}
          <div className="glass-card p-6">
            <h3 className="text-white font-semibold mb-6">Pipeline Distribution</h3>
            <div className="space-y-4">
              {pipeline.length > 0 ? (
                pipeline.map((stage: PipelineStage, index: number) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{getStageIcon(stage.pipeline_stage)}</span>
                        <span className="text-white capitalize font-medium">
                          {stage.pipeline_stage}
                        </span>
                      </div>
                      <span className="text-gray-400 font-semibold">
                        {stage.count}
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          stage.pipeline_stage === 'hot' ? 'bg-red-400' :
                          stage.pipeline_stage === 'warm' ? 'bg-yellow-400' :
                          stage.pipeline_stage === 'cold' ? 'bg-blue-400' :
                          'bg-gray-400'
                        }`}
                        style={{ 
                          width: `${Math.max(10, (stage.count / Math.max(...pipeline.map(p => p.count))) * 100)}%` 
                        }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No pipeline data available</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Interactions */}
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-white font-semibold">Recent Interactions</h3>
              <div className="flex items-center space-x-2">
                <Search className="w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search interactions..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-gray-800/50 border border-gray-600 rounded px-3 py-1 text-white text-sm placeholder-gray-400 focus:outline-none focus:border-blue-400"
                />
              </div>
            </div>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {recentInteractions.length > 0 ? (
                recentInteractions
                  .filter((interaction: Interaction) => 
                    !searchQuery || 
                    interaction.contact_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                    interaction.interaction_type.toLowerCase().includes(searchQuery.toLowerCase())
                  )
                  .map((interaction: Interaction, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-800/30 rounded-lg hover:bg-gray-800/50 transition-colors">
                      <div className="flex items-center space-x-3">
                        <span className="text-lg">
                          {getInteractionIcon(interaction.interaction_type)}
                        </span>
                        <div>
                          <h5 className="text-white font-medium text-sm">
                            {interaction.contact_name}
                          </h5>
                          <p className="text-gray-400 text-xs">
                            {interaction.interaction_type} • {interaction.status}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-gray-400 text-xs">
                          {new Date(interaction.timestamp).toLocaleDateString()}
                        </p>
                        <ChevronRight className="w-4 h-4 text-gray-500 ml-auto" />
                      </div>
                    </div>
                  ))
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Calendar className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No recent interactions</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Pipeline Actions */}
        <div className="mt-8 glass-card p-6">
          <h3 className="text-white font-semibold mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="p-4 bg-blue-500/10 border border-blue-400/30 rounded-lg text-blue-400 hover:bg-blue-500/20 transition-colors">
              <Users className="w-6 h-6 mx-auto mb-2" />
              <span className="text-sm">Add Contact</span>
            </button>
            <button className="p-4 bg-green-500/10 border border-green-400/30 rounded-lg text-green-400 hover:bg-green-500/20 transition-colors">
              <Calendar className="w-6 h-6 mx-auto mb-2" />
              <span className="text-sm">Schedule Follow-up</span>
            </button>
            <button className="p-4 bg-purple-500/10 border border-purple-400/30 rounded-lg text-purple-400 hover:bg-purple-500/20 transition-colors">
              <BarChart3 className="w-6 h-6 mx-auto mb-2" />
              <span className="text-sm">View Analytics</span>
            </button>
            <button className="p-4 bg-yellow-500/10 border border-yellow-400/30 rounded-lg text-yellow-400 hover:bg-yellow-500/20 transition-colors">
              <TrendingUp className="w-6 h-6 mx-auto mb-2" />
              <span className="text-sm">Pipeline Report</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CrmPage;