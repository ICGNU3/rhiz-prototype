import React, { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Target, Plus, Brain, Users, Calendar, TrendingUp, Loader2, AlertCircle, Sparkles } from 'lucide-react';
import { goalsAPI, Goal, AISuggestion } from '../services/api';
import { GoalCardSkeleton, AIInsightSkeleton } from '../components/common/SkeletonLoader';
import AnimatedButton, { ButtonState } from '../components/common/AnimatedButton';

interface GoalMatch {
  contact_id: string;
  contact_name: string;
  confidence_score: number;
  reason: string;
  suggested_action: string;
}

const GoalsPage: React.FC = () => {
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createButtonState, setCreateButtonState] = useState<ButtonState>('idle');
  const [newGoalData, setNewGoalData] = useState({ title: '', description: '' });
  const [recentlyCreatedGoalId, setRecentlyCreatedGoalId] = useState<string | null>(null);
  const newGoalRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  // Fetch goals with React Query
  const { 
    data: goals = [], 
    isLoading: goalsLoading, 
    error: goalsError, 
    refetch: refetchGoals 
  } = useQuery({
    queryKey: ['goals'],
    queryFn: async () => {
      const response = await goalsAPI.getAll();
      return response.data || [];
    },
    retry: 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // Fetch goal matches when a goal is selected
  const { 
    data: goalMatches = [], 
    isLoading: matchesLoading, 
    error: matchesError 
  } = useQuery({
    queryKey: ['goalMatches', selectedGoal?.id],
    queryFn: async () => {
      if (!selectedGoal?.id) return [];
      const response = await goalsAPI.getMatches(selectedGoal.id);
      return response.data || [];
    },
    enabled: !!selectedGoal?.id,
    retry: 2,
  });

  // Create goal mutation
  const createGoalMutation = useMutation({
    mutationFn: goalsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      setShowCreateModal(false);
    },
    onError: (error) => {
      console.error('Failed to create goal:', error);
    },
  });

  // Delete goal mutation
  const deleteGoalMutation = useMutation({
    mutationFn: goalsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
      if (selectedGoal) {
        setSelectedGoal(null);
      }
    },
    onError: (error) => {
      console.error('Failed to delete goal:', error);
    },
  });

  const handleGoalSelect = (goal: Goal) => {
    setSelectedGoal(goal);
  };

  const GoalCard: React.FC<{ goal: Goal }> = ({ goal }) => (
    <div 
      className={`glass-card p-6 cursor-pointer transition-all duration-300 hover:scale-105 ${
        selectedGoal?.id === goal.id ? 'border-blue-400/50' : 'border-white/10'
      }`}
      onClick={() => handleGoalSelect(goal)}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`p-2 rounded-lg ${
          goal.category === 'fundraising' ? 'bg-green-500/20 text-green-400' :
          goal.category === 'hiring' ? 'bg-blue-500/20 text-blue-400' :
          goal.category === 'partnerships' ? 'bg-purple-500/20 text-purple-400' :
          'bg-gray-500/20 text-gray-400'
        }`}>
          <Target className="w-5 h-5" />
        </div>
        <span className={`px-3 py-1 rounded-full text-xs ${
          goal.status === 'active' ? 'bg-green-500/20 text-green-400' :
          goal.status === 'completed' ? 'bg-blue-500/20 text-blue-400' :
          'bg-yellow-500/20 text-yellow-400'
        }`}>
          {goal.status.toUpperCase()}
        </span>
      </div>
      
      <h3 className="text-white font-semibold mb-2">{goal.title}</h3>
      <p className="text-gray-400 text-sm mb-4 line-clamp-2">{goal.description}</p>
      
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-gray-400 text-sm">Progress</span>
          <span className="text-white text-sm">{goal.progress}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${
              goal.category === 'fundraising' ? 'bg-green-400' :
              goal.category === 'hiring' ? 'bg-blue-400' :
              goal.category === 'partnerships' ? 'bg-purple-400' :
              'bg-gray-400'
            }`}
            style={{ width: `${goal.progress}%` }}
          />
        </div>
      </div>
      
      {goal.target_date && (
        <div className="flex items-center text-gray-400 text-sm">
          <Calendar className="w-4 h-4 mr-2" />
          Target: {new Date(goal.target_date).toLocaleDateString()}
        </div>
      )}
    </div>
  );

  // Loading and error states
  if (goalsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 flex items-center justify-center">
        <div className="glass-card p-8 flex items-center space-x-4">
          <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
          <span className="text-white text-lg">Loading goals...</span>
        </div>
      </div>
    );
  }

  if (goalsError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 flex items-center justify-center">
        <div className="glass-card p-8 flex flex-col items-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-400" />
          <div className="text-center">
            <h2 className="text-white text-xl font-semibold mb-2">Failed to load goals</h2>
            <p className="text-gray-400 mb-4">Unable to fetch your goals data</p>
            <button 
              onClick={() => refetchGoals()}
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
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Goals
            </h1>
            <p className="text-gray-300 mt-2">
              Track your objectives and find the right connections
            </p>
          </div>
          <button 
            onClick={() => setShowCreateModal(true)}
            disabled={createGoalMutation.isPending}
            className="glass-button px-6 py-3 rounded-lg text-blue-400 border border-blue-400/30 hover:bg-blue-400/10 flex items-center disabled:opacity-50"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create Goal
          </button>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Goals List */}
          <div className="lg:col-span-2">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">Your Goals</h2>
              {goals.length > 0 ? (
                <div className="grid gap-6">
                  {goals.map(goal => (
                    <GoalCard key={goal.id} goal={goal} />
                  ))}
                </div>
              ) : (
                <div className="glass-card p-8 text-center">
                  <Target className="w-16 h-16 mx-auto mb-4 text-gray-500" />
                  <h3 className="text-white text-lg mb-2">No Goals Yet</h3>
                  <p className="text-gray-400 mb-4">Create your first goal to get AI-powered connection suggestions</p>
                  <button 
                    className="glass-button px-6 py-3 rounded-lg text-blue-400 border border-blue-400/30 hover:bg-blue-400/10"
                    onClick={() => setShowCreateModal(true)}
                  >
                    Create Your First Goal
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Goal Matches Sidebar */}
          <div className="lg:col-span-1">
            {selectedGoal ? (
              <div className="glass-card p-6 sticky top-6">
                <div className="flex items-center mb-6">
                  <Brain className="w-5 h-5 text-blue-400 mr-3" />
                  <h3 className="text-white font-semibold">AI Matches</h3>
                </div>
                
                <div className="mb-4 p-4 bg-gray-800/30 rounded-lg">
                  <h4 className="text-white font-medium mb-2">{selectedGoal.title}</h4>
                  <p className="text-gray-400 text-sm">{selectedGoal.description}</p>
                </div>

                {goalMatches.length > 0 ? (
                  <div className="space-y-4">
                    {goalMatches.map((match, index) => (
                      <div key={index} className="p-4 bg-gray-800/30 rounded-lg border border-gray-700/50">
                        <div className="flex justify-between items-start mb-2">
                          <h6 className="font-medium text-white">{match.contact_name}</h6>
                          <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs">
                            {Math.round(match.confidence_score * 100)}%
                          </span>
                        </div>
                        <p className="text-gray-400 text-sm mb-3">{match.reason}</p>
                        <p className="text-blue-400 text-sm font-medium">{match.suggested_action}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No matches found yet</p>
                    <p className="text-sm">AI is analyzing your network...</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="glass-card p-6 sticky top-6">
                <div className="text-center py-8 text-gray-400">
                  <Target className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Select a goal to see AI matches</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Create Goal Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="glass-card p-6 m-4 max-w-md w-full">
              <h3 className="text-white text-lg font-semibold mb-4">Create New Goal</h3>
              
              <form className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm mb-2">Goal Title</label>
                  <input 
                    type="text" 
                    className="w-full bg-gray-800/50 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-400"
                    placeholder="e.g., Raise $250k angel round"
                  />
                </div>
                
                <div>
                  <label className="block text-gray-300 text-sm mb-2">Description</label>
                  <textarea 
                    className="w-full bg-gray-800/50 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-400 h-24"
                    placeholder="Describe your goal in detail..."
                  />
                </div>
                
                <div>
                  <label className="block text-gray-300 text-sm mb-2">Category</label>
                  <select className="w-full bg-gray-800/50 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-400">
                    <option value="fundraising">Fundraising</option>
                    <option value="hiring">Hiring</option>
                    <option value="partnerships">Partnerships</option>
                    <option value="sales">Sales</option>
                    <option value="networking">Networking</option>
                  </select>
                </div>
                
                <div className="flex gap-3 pt-4">
                  <button 
                    type="button"
                    className="flex-1 glass-button px-4 py-2 rounded-lg text-gray-400 border border-gray-600 hover:bg-gray-700/30"
                    onClick={() => setShowCreateModal(false)}
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit"
                    className="flex-1 glass-button px-4 py-2 rounded-lg text-blue-400 border border-blue-400/30 hover:bg-blue-400/10"
                  >
                    Create Goal
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .glass-card {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-radius: 16px;
        }
        
        .glass-button {
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(10px);
          transition: all 0.3s ease;
        }
        
        .glass-button:hover {
          transform: translateY(-1px);
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </div>
  );
};

export default GoalsPage;