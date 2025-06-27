import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { goalsAPI, intelligenceAPI } from '../services/api';
import GoalList from '../components/goals/GoalList';
import { Target, Plus, X } from 'lucide-react';

const Goals: React.FC = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const { data: goals = [], isLoading, refetch } = useQuery({
    queryKey: ['goals'],
    queryFn: async () => {
      const response = await goalsAPI.getAll();
      return response.data;
    },
  });

  const { data: suggestions = [] } = useQuery({
    queryKey: ['ai-suggestions'],
    queryFn: async () => {
      const response = await intelligenceAPI.getAISuggestions();
      return response.data;
    },
  });

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);

    try {
      await goalsAPI.create({ title, description });
      setTitle('');
      setDescription('');
      setShowCreateModal(false);
      refetch();
    } catch (error) {
      console.error('Failed to create goal:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleGoalClick = (goal: any) => {
    // In a real implementation, this would open a detailed view
    console.log('Goal clicked:', goal);
  };

  return (
    <div className="space-y-6">
      <GoalList
        goals={goals}
        suggestions={suggestions}
        onGoalClick={handleGoalClick}
        onCreateGoal={() => setShowCreateModal(true)}
        isLoading={isLoading}
      />

      {/* Create Goal Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="glass-card p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-primary-500 to-purple-500">
                  <Target size={18} className="text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white">Create New Goal</h3>
              </div>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateGoal} className="space-y-4">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-300 mb-2">
                  Goal Title
                </label>
                <input
                  id="title"
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-dark-card border border-dark-border rounded-lg text-white placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-colors"
                  placeholder="e.g., Raise a $250k angel round"
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  required
                  rows={4}
                  className="w-full px-4 py-3 bg-dark-card border border-dark-border rounded-lg text-white placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-colors resize-none"
                  placeholder="Describe your goal in detail. The more context you provide, the better our AI can match you with relevant contacts."
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 glass-button-secondary"
                  disabled={isCreating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreating || !title.trim() || !description.trim()}
                  className="flex-1 glass-button-primary flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {isCreating ? (
                    <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  ) : (
                    <>
                      <Plus size={16} />
                      <span>Create Goal</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Goals;