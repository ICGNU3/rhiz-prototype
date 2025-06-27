import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { intelligenceAPI, networkAPI } from '../services/api';
import RhizomaticGraph from '../components/network/RhizomaticGraph';
import { Brain, Network, Sparkles, TrendingUp } from 'lucide-react';

const Intelligence: React.FC = () => {
  const { data: suggestions = [], isLoading: suggestionsLoading } = useQuery({
    queryKey: ['ai-suggestions'],
    queryFn: async () => {
      const response = await intelligenceAPI.getAISuggestions();
      return response.data;
    },
  });

  const { data: networkData, isLoading: networkLoading } = useQuery({
    queryKey: ['network-graph'],
    queryFn: async () => {
      try {
        const response = await networkAPI.getGraph();
        return response.data;
      } catch (error) {
        return { nodes: [], edges: [] };
      }
    },
  });

  const { data: insights, isLoading: insightsLoading } = useQuery({
    queryKey: ['insights'],
    queryFn: async () => {
      try {
        const response = await intelligenceAPI.getInsights();
        return response.data;
      } catch (error) {
        return null;
      }
    },
  });

  const isLoading = suggestionsLoading || networkLoading || insightsLoading;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-gray-700 rounded w-1/3 mb-8 animate-pulse"></div>
        <div className="grid gap-6 lg:grid-cols-2">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="glass-card p-6 animate-pulse">
              <div className="h-6 bg-gray-700 rounded mb-4"></div>
              <div className="h-32 bg-gray-700 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">Network Intelligence</h2>
        <p className="text-gray-400 mt-1">AI-powered insights and relationship analysis</p>
      </div>

      {/* Intelligence Overview */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500">
              <Brain size={20} className="text-white" />
            </div>
            <h3 className="font-semibold text-white">AI Suggestions</h3>
          </div>
          <div className="text-2xl font-bold text-white mb-2">{suggestions.length}</div>
          <p className="text-sm text-gray-400">Active recommendations</p>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500">
              <Network size={20} className="text-white" />
            </div>
            <h3 className="font-semibold text-white">Network Nodes</h3>
          </div>
          <div className="text-2xl font-bold text-white mb-2">{networkData?.nodes?.length || 0}</div>
          <p className="text-sm text-gray-400">Total connections</p>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500">
              <TrendingUp size={20} className="text-white" />
            </div>
            <h3 className="font-semibold text-white">Intelligence Score</h3>
          </div>
          <div className="text-2xl font-bold text-white mb-2">
            {Math.round(((networkData?.nodes?.length || 0) * 2) + (suggestions.length * 5))}
          </div>
          <p className="text-sm text-gray-400">Network strength</p>
        </div>
      </div>

      {/* AI Suggestions */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500">
              <Sparkles size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white">AI-Powered Suggestions</h3>
          </div>
        </div>

        {suggestions.length > 0 ? (
          <div className="space-y-4">
            {suggestions.slice(0, 5).map((suggestion) => (
              <div key={suggestion.id} className="p-4 rounded-lg bg-gray-800/50 border border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-white">Contact Match</span>
                  <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">
                    {Math.round(suggestion.confidence * 100)}% confidence
                  </span>
                </div>
                <p className="text-sm text-gray-300 mb-3">{suggestion.suggestion}</p>
                <div className="flex space-x-2">
                  <button className="glass-button-primary text-xs px-3 py-1">
                    Send Message
                  </button>
                  <button className="glass-button-secondary text-xs px-3 py-1">
                    View Contact
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Brain className="mx-auto h-12 w-12 text-gray-500 mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No AI suggestions yet</h3>
            <p className="text-gray-400 mb-6">
              Add goals and contacts to get personalized AI recommendations
            </p>
          </div>
        )}
      </div>

      {/* Network Visualization */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500">
              <Network size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white">Network Map</h3>
          </div>
        </div>

        {networkData && networkData.nodes && networkData.nodes.length > 0 ? (
          <RhizomaticGraph
            nodes={networkData.nodes}
            edges={networkData.edges || []}
            height={500}
            onNodeClick={(node) => {
              console.log('Node clicked:', node);
            }}
          />
        ) : (
          <div className="text-center py-12">
            <Network className="mx-auto h-12 w-12 text-gray-500 mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No network data yet</h3>
            <p className="text-gray-400 mb-6">
              Start building connections to see your network visualization
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Intelligence;