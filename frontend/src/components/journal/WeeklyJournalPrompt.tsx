import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Calendar, Heart, Users, Sparkles, PenTool, X } from 'lucide-react';
import AnimatedButton from '../common/AnimatedButton';
import JournalEntryCard from './JournalEntryCard';

interface WeeklyPrompt {
  prompt: string;
  weekly_insights: {
    weekly_stats: any;
    top_contacts: Array<{ name: string; mention_count: number }>;
  };
}

interface WeeklyJournalPromptProps {
  className?: string;
  onComplete?: () => void;
}

const WeeklyJournalPrompt: React.FC<WeeklyJournalPromptProps> = ({
  className = "",
  onComplete
}) => {
  const [showJournalEntry, setShowJournalEntry] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);
  const queryClient = useQueryClient();

  // API functions
  const journalAPI = {
    getWeeklyPrompt: async (): Promise<WeeklyPrompt> => {
      const response = await fetch('/api/journal/weekly-prompt');
      if (!response.ok) throw new Error('Failed to get weekly prompt');
      return response.json();
    }
  };

  const { data: weeklyPrompt, isLoading } = useQuery({
    queryKey: ['weekly-prompt'],
    queryFn: journalAPI.getWeeklyPrompt,
    staleTime: 1000 * 60 * 60, // 1 hour
    retry: 1
  });

  const handleStartJournal = () => {
    setShowJournalEntry(true);
  };

  const handleJournalComplete = () => {
    setShowJournalEntry(false);
    setIsDismissed(true);
    if (onComplete) onComplete();
  };

  const handleDismiss = () => {
    setIsDismissed(true);
  };

  // Don't show if dismissed or no prompt data
  if (isDismissed || !weeklyPrompt) {
    return null;
  }

  // Show journal entry creation mode
  if (showJournalEntry) {
    return (
      <div className={`${className}`}>
        <JournalEntryCard
          isCreating={true}
          onSave={handleJournalComplete}
          className="border-2 border-purple-500/30"
        />
      </div>
    );
  }

  return (
    <div className={`glass-card p-6 border-2 border-purple-500/30 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500">
            <Heart className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Weekly Reflection</h3>
            <p className="text-sm text-gray-400">Take a moment to appreciate your connections</p>
          </div>
        </div>
        <button
          onClick={handleDismiss}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-700/50 rounded-lg transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Weekly Insights */}
      {weeklyPrompt.weekly_insights?.top_contacts && weeklyPrompt.weekly_insights.top_contacts.length > 0 && (
        <div className="mb-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
          <div className="flex items-center mb-2">
            <Users className="w-4 h-4 text-blue-400 mr-2" />
            <span className="text-sm font-medium text-blue-400">People You've Mentioned This Week</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {weeklyPrompt.weekly_insights.top_contacts.slice(0, 5).map((contact, index) => (
              <span
                key={contact.name}
                className="inline-flex items-center px-2 py-1 bg-blue-600/20 text-blue-300 text-xs rounded-full"
              >
                {contact.name}
                <span className="ml-1 text-blue-400">({contact.mention_count})</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Prompt */}
      <div className="mb-6">
        <div className="flex items-start space-x-3">
          <div className="p-2 rounded-lg bg-purple-500/20">
            <Sparkles className="w-4 h-4 text-purple-400" />
          </div>
          <div className="flex-1">
            <p className="text-white text-lg leading-relaxed">
              {weeklyPrompt.prompt}
            </p>
          </div>
        </div>
      </div>

      {/* Weekly Stats */}
      {weeklyPrompt.weekly_insights?.weekly_stats && (
        <div className="mb-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {weeklyPrompt.weekly_insights.weekly_stats[0] > 0 && (
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">
                  {weeklyPrompt.weekly_insights.weekly_stats[0]}
                </div>
                <div className="text-xs text-gray-400">Journal Entries</div>
              </div>
            )}
            {weeklyPrompt.weekly_insights.weekly_stats[1] && (
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">
                  {Math.round(weeklyPrompt.weekly_insights.weekly_stats[1] * 10) / 10}
                </div>
                <div className="text-xs text-gray-400">Avg Mood</div>
              </div>
            )}
            {weeklyPrompt.weekly_insights.weekly_stats[2] && (
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">
                  {Math.round(weeklyPrompt.weekly_insights.weekly_stats[2] * 10) / 10}
                </div>
                <div className="text-xs text-gray-400">Avg Energy</div>
              </div>
            )}
            {weeklyPrompt.weekly_insights.weekly_stats[4] > 0 && (
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-400">
                  {weeklyPrompt.weekly_insights.weekly_stats[4]}
                </div>
                <div className="text-xs text-gray-400">People Mentioned</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between items-center">
        <div className="flex items-center text-sm text-gray-400">
          <Calendar className="w-4 h-4 mr-1" />
          Week of {new Date().toLocaleDateString()}
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleDismiss}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
          >
            Skip This Week
          </button>
          <AnimatedButton
            onClick={handleStartJournal}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
          >
            <PenTool className="w-4 h-4 mr-2" />
            Start Reflecting
          </AnimatedButton>
        </div>
      </div>
    </div>
  );
};

export default WeeklyJournalPrompt;