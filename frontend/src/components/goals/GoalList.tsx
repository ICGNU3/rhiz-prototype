import React, { useState } from 'react';
import type { Goal, AISuggestion } from '../../services/api';
import { Target, Users, Plus, Sparkles, Calendar } from 'lucide-react';

interface GoalListProps {
  goals: Goal[];
  suggestions: AISuggestion[];
  onGoalClick: (goal: Goal) => void;
  onCreateGoal: () => void;
  isLoading?: boolean;
}

const GoalList: React.FC<GoalListProps> = ({
  goals,
  suggestions,
  onGoalClick,
  onCreateGoal,
  isLoading = false,
}) => {
  const [filter, setFilter] = useState<'all' | 'recent' | 'matched'>('all');

  const getGoalSuggestions = (goalId: string) => {
    return suggestions.filter(s => s.goal_id === goalId);
  };

  const filteredGoals = goals.filter(goal => {
    switch (filter) {
      case 'recent':
        const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
        return new Date(goal.created_at) > oneWeekAgo;
      case 'matched':
        return getGoalSuggestions(goal.id).length > 0;
      default:
        return true;
    }
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="glass-card p-6 animate-pulse">
            <div className="h-6 bg-gray-700 rounded w-3/4 mb-3"></div>
            <div className="h-4 bg-gray-700 rounded w-full mb-2"></div>
            <div className="h-4 bg-gray-700 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Your Goals</h2>
          <p className="text-gray-400 mt-1">Track progress and find relevant connections</p>
        </div>
        <button
          onClick={onCreateGoal}
          className="glass-button-primary flex items-center space-x-2"
        >
          <Plus size={18} />
          <span>New Goal</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex space-x-2">
        {[
          { key: 'all', label: 'All Goals', count: goals.length },
          { key: 'recent', label: 'Recent', count: filteredGoals.length },
          { key: 'matched', label: 'With Matches', count: goals.filter(g => getGoalSuggestions(g.id).length > 0).length },
        ].map(({ key, label, count }) => (
          <button
            key={key}
            onClick={() => setFilter(key as any)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
              filter === key
                ? 'bg-primary-500 text-white'
                : 'glass-button-secondary text-gray-300'
            }`}
          >
            {label} ({count})
          </button>
        ))}
      </div>

      {/* Goals Grid */}
      {filteredGoals.length === 0 ? (
        <div className="text-center py-12">
          <Target className="mx-auto h-12 w-12 text-gray-500 mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">
            {filter === 'all' ? 'No goals yet' : 'No goals match this filter'}
          </h3>
          <p className="text-gray-400 mb-6">
            {filter === 'all' 
              ? 'Create your first goal to start building meaningful connections'
              : 'Try adjusting your filter or create a new goal'
            }
          </p>
          {filter === 'all' && (
            <button
              onClick={onCreateGoal}
              className="glass-button-primary"
            >
              Create Your First Goal
            </button>
          )}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredGoals.map((goal) => {
            const goalSuggestions = getGoalSuggestions(goal.id);
            const highConfidenceMatches = goalSuggestions.filter(s => s.confidence > 0.7);
            
            return (
              <div
                key={goal.id}
                onClick={() => onGoalClick(goal)}
                className="glass-card p-6 cursor-pointer hover:border-primary-500 transition-all duration-300 group"
              >
                {/* Goal Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-gradient-to-r from-primary-500 to-purple-500">
                      <Target size={18} className="text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-white group-hover:text-primary-400 transition-colors">
                        {goal.title}
                      </h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <Calendar size={12} className="text-gray-400" />
                        <span className="text-xs text-gray-400">
                          {new Date(goal.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Goal Description */}
                <p className="text-gray-300 text-sm mb-4 line-clamp-3">
                  {goal.description}
                </p>

                {/* Matches Summary */}
                <div className="space-y-3">
                  {goalSuggestions.length > 0 && (
                    <div className="flex items-center justify-between p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                      <div className="flex items-center space-x-2">
                        <Sparkles size={16} className="text-emerald-400" />
                        <span className="text-sm text-emerald-300">
                          {goalSuggestions.length} potential matches found
                        </span>
                      </div>
                      {highConfidenceMatches.length > 0 && (
                        <div className="text-xs text-emerald-400 font-medium">
                          {highConfidenceMatches.length} high confidence
                        </div>
                      )}
                    </div>
                  )}

                  {goalSuggestions.length === 0 && (
                    <div className="flex items-center space-x-2 p-3 rounded-lg bg-gray-500/10 border border-gray-500/20">
                      <Users size={16} className="text-gray-400" />
                      <span className="text-sm text-gray-400">
                        No matches yet - add contacts to find connections
                      </span>
                    </div>
                  )}
                </div>

                {/* Quick Stats */}
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-dark-border">
                  <div className="text-xs text-gray-400">
                    {goalSuggestions.length > 0 && (
                      <span>
                        Avg confidence: {(goalSuggestions.reduce((acc, s) => acc + s.confidence, 0) / goalSuggestions.length * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-primary-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    Click to explore →
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default GoalList;