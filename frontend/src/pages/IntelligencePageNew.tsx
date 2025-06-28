import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Brain, MessageCircle, Send, Loader2, AlertCircle, Lightbulb, TrendingUp, Users } from 'lucide-react';
import { intelligenceAPI } from '../services/api';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface AIInsight {
  id: string;
  type: string;
  title: string;
  description: string;
  confidence: number;
  created_at: string;
}

const IntelligencePage: React.FC = () => {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const queryClient = useQueryClient();

  // Fetch AI suggestions
  const { 
    data: suggestions = [], 
    isLoading: suggestionsLoading, 
    error: suggestionsError, 
    refetch: refetchSuggestions 
  } = useQuery({
    queryKey: ['ai-suggestions'],
    queryFn: async () => {
      const response = await intelligenceAPI.getAISuggestions();
      return response.data || [];
    },
    retry: 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Fetch insights
  const { 
    data: insights = [], 
    isLoading: insightsLoading, 
    error: insightsError 
  } = useQuery({
    queryKey: ['insights'],
    queryFn: async () => {
      const response = await intelligenceAPI.getInsights();
      return response.data || [];
    },
    retry: 2,
  });

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const response = await intelligenceAPI.processNLQuery(message);
      return response.data;
    },
    onSuccess: (data) => {
      const assistantMessage: ChatMessage = {
        id: Date.now().toString() + '_assistant',
        role: 'assistant',
        content: data.response || 'I understand your question, but I need more context to provide a helpful response.',
        timestamp: new Date().toISOString(),
      };
      setChatMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
    },
    onError: (error) => {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: Date.now().toString() + '_error',
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setChatMessages(prev => [...prev, errorMessage]);
      setIsTyping(false);
    },
  });

  const handleSendMessage = () => {
    if (!inputMessage.trim() || chatMutation.isPending) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
    };

    setChatMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    chatMutation.mutate(inputMessage.trim());
    setInputMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Loading state
  if (suggestionsLoading || insightsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 flex items-center justify-center">
        <div className="glass-card p-8 flex items-center space-x-4">
          <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
          <span className="text-white text-lg">Loading intelligence data...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (suggestionsError || insightsError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 flex items-center justify-center">
        <div className="glass-card p-8 flex flex-col items-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-400" />
          <div className="text-center">
            <h2 className="text-white text-xl font-semibold mb-2">Failed to load intelligence data</h2>
            <p className="text-gray-400 mb-4">Unable to fetch AI insights and suggestions</p>
            <button 
              onClick={() => refetchSuggestions()}
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
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Intelligence
            </h1>
            <p className="text-gray-300 mt-2">
              AI-powered insights and relationship intelligence
            </p>
          </div>
          <button 
            onClick={() => refetchSuggestions()}
            className="glass-button px-6 py-3 rounded-lg text-purple-400 border border-purple-400/30 hover:bg-purple-400/10 flex items-center"
          >
            <Brain className="w-5 h-5 mr-2" />
            Refresh Intelligence
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* AI Chat Interface */}
          <div className="glass-card p-6">
            <div className="flex items-center mb-6">
              <MessageCircle className="w-6 h-6 text-blue-400 mr-3" />
              <h3 className="text-white font-semibold">AI Assistant</h3>
            </div>

            {/* Chat Messages */}
            <div className="h-96 overflow-y-auto mb-4 space-y-4 pr-2">
              {chatMessages.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  <Brain className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p className="mb-2">Ask me about your contacts and relationships</p>
                  <p className="text-sm">Try: "Who should I follow up with this week?"</p>
                </div>
              )}
              
              {chatMessages.map(message => (
                <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-sm px-4 py-2 rounded-lg ${
                    message.role === 'user' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-700 text-gray-100'
                  }`}>
                    <p className="text-sm">{message.content}</p>
                    <p className={`text-xs mt-1 ${
                      message.role === 'user' ? 'text-blue-100' : 'text-gray-400'
                    }`}>
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-gray-700 text-gray-100 px-4 py-2 rounded-lg">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about your relationships..."
                disabled={chatMutation.isPending}
                className="flex-1 bg-gray-800/50 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-400 disabled:opacity-50"
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || chatMutation.isPending}
                className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {chatMutation.isPending ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* AI Suggestions & Insights */}
          <div className="space-y-6">
            {/* AI Suggestions */}
            <div className="glass-card p-6">
              <div className="flex items-center mb-4">
                <Lightbulb className="w-6 h-6 text-yellow-400 mr-3" />
                <h3 className="text-white font-semibold">AI Suggestions</h3>
              </div>
              
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {suggestions.length > 0 ? (
                  suggestions.map((suggestion: any) => (
                    <div key={suggestion.id} className="p-4 bg-gray-800/30 rounded-lg border border-gray-700/50">
                      <div className="flex justify-between items-start mb-2">
                        <h5 className="text-white font-medium text-sm">
                          {suggestion.contact_name || 'General Suggestion'}
                        </h5>
                        <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs">
                          {Math.round((suggestion.confidence || 0) * 100)}%
                        </span>
                      </div>
                      <p className="text-gray-400 text-sm">{suggestion.suggestion}</p>
                      {suggestion.goal_title && (
                        <p className="text-blue-400 text-xs mt-2">Related to: {suggestion.goal_title}</p>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-center py-6 text-gray-400">
                    <Lightbulb className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No suggestions available</p>
                  </div>
                )}
              </div>
            </div>

            {/* Insights */}
            <div className="glass-card p-6">
              <div className="flex items-center mb-4">
                <TrendingUp className="w-6 h-6 text-green-400 mr-3" />
                <h3 className="text-white font-semibold">Recent Insights</h3>
              </div>
              
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {insights.length > 0 ? (
                  insights.slice(0, 5).map((insight: any, index: number) => (
                    <div key={index} className="p-3 bg-gray-800/30 rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <h5 className="text-white font-medium text-sm">
                          {insight.title || 'Network Insight'}
                        </h5>
                        <Users className="w-4 h-4 text-blue-400" />
                      </div>
                      <p className="text-gray-400 text-sm">
                        {insight.description || insight.content || 'New relationship insight available'}
                      </p>
                      <p className="text-gray-500 text-xs mt-2">
                        {insight.created_at ? new Date(insight.created_at).toLocaleDateString() : 'Recent'}
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-6 text-gray-400">
                    <TrendingUp className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No insights available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 glass-card p-6">
          <h3 className="text-white font-semibold mb-4">Quick Intelligence Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button 
              onClick={() => setInputMessage("Who should I follow up with this week?")}
              className="p-4 bg-blue-500/10 border border-blue-400/30 rounded-lg text-blue-400 hover:bg-blue-500/20 transition-colors text-left"
            >
              <Users className="w-6 h-6 mb-2" />
              <h4 className="font-medium mb-1">Weekly Follow-ups</h4>
              <p className="text-sm text-gray-400">Get priority contacts to reach out to</p>
            </button>
            
            <button 
              onClick={() => setInputMessage("Analyze my strongest relationships")}
              className="p-4 bg-green-500/10 border border-green-400/30 rounded-lg text-green-400 hover:bg-green-500/20 transition-colors text-left"
            >
              <TrendingUp className="w-6 h-6 mb-2" />
              <h4 className="font-medium mb-1">Relationship Analysis</h4>
              <p className="text-sm text-gray-400">Understand your network strengths</p>
            </button>
            
            <button 
              onClick={() => setInputMessage("What opportunities should I explore?")}
              className="p-4 bg-purple-500/10 border border-purple-400/30 rounded-lg text-purple-400 hover:bg-purple-500/20 transition-colors text-left"
            >
              <Lightbulb className="w-6 h-6 mb-2" />
              <h4 className="font-medium mb-1">Opportunities</h4>
              <p className="text-sm text-gray-400">Discover potential collaborations</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntelligencePage;