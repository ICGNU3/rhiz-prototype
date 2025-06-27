import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { goalsAPI, contactsAPI, intelligenceAPI, analyticsAPI } from '../services/api';
import { Target, Users, Brain, TrendingUp, Plus, Sparkles } from 'lucide-react';
import RhizomaticGraph from '../components/network/RhizomaticGraph';

const Dashboard: React.FC = () => {
  const { data: goals = [], isLoading: goalsLoading } = useQuery({
    queryKey: ['goals'],
    queryFn: async () => {
      const response = await goalsAPI.getAll();
      return response.data;
    },
  });

  const { data: contacts = [], isLoading: contactsLoading } = useQuery({
    queryKey: ['contacts'],
    queryFn: async () => {
      const response = await contactsAPI.getAll();
      return response.data;
    },
  });

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
      const response = await fetch('/api/network/graph');
      if (!response.ok) {
        // Return empty network if API not available yet
        return { nodes: [], edges: [] };
      }
      return response.json();
    },
  });

  const isLoading = goalsLoading || contactsLoading || suggestionsLoading;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-gray-700 rounded w-1/3 mb-8 animate-pulse"></div>
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

  const stats = [
    {
      label: 'Active Goals',
      value: goals.length,
      icon: Target,
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      action: () => window.location.href = '/goals',
      actionLabel: 'View Goals'
    },
    {
      label: 'Total Contacts',
      value: contacts.length,
      icon: Users,
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      action: () => window.location.href = '/contacts',
      actionLabel: 'View Contacts'
    },
    {
      label: 'AI Suggestions',
      value: suggestions.length,
      icon: Brain,
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      action: () => window.location.href = '/intelligence',
      actionLabel: 'View Intelligence'
    },
    {
      label: 'Network Score',
      value: Math.round((contacts.length * 2.5) + (goals.length * 10)),
      icon: TrendingUp,
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      action: () => window.location.href = '/intelligence',
      actionLabel: 'View Analytics'
    },
  ];

  const recentGoals = goals.slice(0, 3);
  const warmContacts = contacts.filter(c => c.warmth_status >= 3).slice(0, 3);
  const highConfidenceSuggestions = suggestions.filter(s => s.confidence > 0.7).slice(0, 3);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Welcome to Rhiz</h1>
          <p className="text-gray-400 mt-2">Your intelligent relationship network at a glance</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => window.location.href = '/goals'}
            className="glass-button-primary flex items-center space-x-2"
          >
            <Plus size={18} />
            <span>New Goal</span>
          </button>
          <button
            onClick={() => window.location.href = '/contacts'}
            className="glass-button-secondary flex items-center space-x-2"
          >
            <Users size={18} />
            <span>Add Contact</span>
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map(({ label, value, icon: Icon, color, action, actionLabel }) => (
          <div key={label} className="glass-card p-6 group hover:border-primary-500 transition-all">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-lg bg-gradient-to-r ${color}`}>
                <Icon size={24} className="text-white" />
              </div>
              <button
                onClick={action}
                className="text-xs text-primary-400 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {actionLabel} →
              </button>
            </div>
            <div className="text-2xl font-bold text-white mb-1">{value}</div>
            <div className="text-sm text-gray-400">{label}</div>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Recent Goals */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Recent Goals</h3>
            <button
              onClick={() => window.location.href = '/goals'}
              className="text-sm text-primary-400 hover:text-primary-300"
            >
              View all →
            </button>
          </div>
          {recentGoals.length > 0 ? (
            <div className="space-y-4">
              {recentGoals.map((goal) => (
                <div key={goal.id} className="p-4 rounded-lg bg-gray-800/50 border border-gray-700">
                  <h4 className="font-medium text-white mb-2">{goal.title}</h4>
                  <p className="text-sm text-gray-400 line-clamp-2">{goal.description}</p>
                  <div className="flex items-center justify-between mt-3">
                    <span className="text-xs text-gray-500">
                      {new Date(goal.created_at).toLocaleDateString()}
                    </span>
                    <div className="flex items-center space-x-1">
                      <Sparkles size={12} className="text-yellow-400" />
                      <span className="text-xs text-yellow-400">
                        {suggestions.filter(s => s.goal_id === goal.id).length} matches
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Target className="mx-auto h-8 w-8 text-gray-500 mb-3" />
              <p className="text-gray-400 mb-4">No goals yet</p>
              <button
                onClick={() => window.location.href = '/goals'}
                className="text-sm text-primary-400 hover:text-primary-300"
              >
                Create your first goal →
              </button>
            </div>
          )}
        </div>

        {/* Warm Contacts */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Warm Contacts</h3>
            <button
              onClick={() => window.location.href = '/contacts'}
              className="text-sm text-primary-400 hover:text-primary-300"
            >
              View all →
            </button>
          </div>
          {warmContacts.length > 0 ? (
            <div className="space-y-4">
              {warmContacts.map((contact) => (
                <div key={contact.id} className="p-4 rounded-lg bg-gray-800/50 border border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-white">{contact.name}</h4>
                      <p className="text-sm text-gray-400">{contact.company} {contact.title && `• ${contact.title}`}</p>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span className="text-xs text-green-400">{contact.warmth_label}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Users className="mx-auto h-8 w-8 text-gray-500 mb-3" />
              <p className="text-gray-400 mb-4">No warm contacts yet</p>
              <button
                onClick={() => window.location.href = '/contacts'}
                className="text-sm text-primary-400 hover:text-primary-300"
              >
                Add contacts →
              </button>
            </div>
          )}
        </div>

        {/* AI Suggestions */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">AI Suggestions</h3>
            <button
              onClick={() => window.location.href = '/intelligence'}
              className="text-sm text-primary-400 hover:text-primary-300"
            >
              View all →
            </button>
          </div>
          {highConfidenceSuggestions.length > 0 ? (
            <div className="space-y-4">
              {highConfidenceSuggestions.map((suggestion) => {
                const contact = contacts.find(c => c.id === suggestion.contact_id);
                const goal = goals.find(g => g.id === suggestion.goal_id);
                return (
                  <div key={suggestion.id} className="p-4 rounded-lg bg-gray-800/50 border border-gray-700">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-white">{contact?.name || 'Unknown Contact'}</span>
                      <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">
                        {Math.round(suggestion.confidence * 100)}% match
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mb-2">For: {goal?.title || 'Unknown Goal'}</p>
                    <p className="text-xs text-gray-300">{suggestion.suggestion}</p>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8">
              <Brain className="mx-auto h-8 w-8 text-gray-500 mb-3" />
              <p className="text-gray-400 mb-4">No AI suggestions yet</p>
              <button
                onClick={() => window.location.href = '/intelligence'}
                className="text-sm text-primary-400 hover:text-primary-300"
              >
                Explore intelligence →
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Network Visualization */}
      {networkData && (networkData.nodes.length > 0) && (
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Network Map</h3>
            <button
              onClick={() => window.location.href = '/intelligence'}
              className="text-sm text-primary-400 hover:text-primary-300"
            >
              Explore network →
            </button>
          </div>
          <RhizomaticGraph
            nodes={networkData.nodes}
            edges={networkData.edges}
            height={400}
            onNodeClick={(node) => {
              if (node.type === 'contact') {
                window.location.href = `/contacts?id=${node.id}`;
              } else if (node.type === 'goal') {
                window.location.href = `/goals?id=${node.id}`;
              }
            }}
          />
        </div>
      )}
    </div>
  );
};

export default Dashboard;