import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  PenTool, 
  MessageCircle, 
  Heart, 
  Brain, 
  User, 
  Target, 
  Calendar,
  Sparkles,
  Send,
  X,
  Plus
} from 'lucide-react';
import AnimatedButton from '../common/AnimatedButton';

export interface JournalEntry {
  id: string;
  title: string;
  content: string;
  entry_type: 'reflection' | 'gratitude' | 'insight' | 'relationship';
  mood_score?: number;
  energy_level?: number;
  tags: string[];
  ai_reflection?: string;
  created_at: string;
  related_contact_id?: string;
  related_goal_id?: string;
  contact_name?: string;
  goal_title?: string;
}

export interface JournalReflection {
  id: string;
  user_question: string;
  ai_response: string;
  reflection_type: string;
  created_at: string;
}

interface JournalEntryCardProps {
  entry?: JournalEntry;
  onSave?: (entry: Partial<JournalEntry>) => void;
  relatedContactId?: string;
  relatedGoalId?: string;
  contactName?: string;
  goalTitle?: string;
  isCreating?: boolean;
  className?: string;
}

const JournalEntryCard: React.FC<JournalEntryCardProps> = ({
  entry,
  onSave,
  relatedContactId,
  relatedGoalId,
  contactName,
  goalTitle,
  isCreating = false,
  className = ""
}) => {
  const [isEditing, setIsEditing] = useState(isCreating);
  const [title, setTitle] = useState(entry?.title || '');
  const [content, setContent] = useState(entry?.content || '');
  const [entryType, setEntryType] = useState<JournalEntry['entry_type']>(entry?.entry_type || 'reflection');
  const [moodScore, setMoodScore] = useState(entry?.mood_score || 5);
  const [energyLevel, setEnergyLevel] = useState(entry?.energy_level || 5);
  const [tags, setTags] = useState<string[]>(entry?.tags || []);
  const [newTag, setNewTag] = useState('');
  const [showAIReflection, setShowAIReflection] = useState(false);
  const [aiQuestion, setAiQuestion] = useState('');
  const [reflectionType, setReflectionType] = useState<'general' | 'relationship' | 'growth' | 'insight'>('general');

  const queryClient = useQueryClient();

  // Mock API functions - replace with actual API calls
  const journalAPI = {
    create: async (data: Partial<JournalEntry>) => {
      const response = await fetch('/api/journal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Failed to create journal entry');
      return response.json();
    },

    reflectWithAI: async (data: { entry_id: string; user_question: string; reflection_type: string }) => {
      const response = await fetch('/api/journal/reflect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Failed to generate AI reflection');
      return response.json();
    }
  };

  const createEntryMutation = useMutation({
    mutationFn: journalAPI.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['journal-entries'] });
      setIsEditing(false);
      if (onSave) onSave(data);
    }
  });

  const aiReflectionMutation = useMutation({
    mutationFn: journalAPI.reflectWithAI,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['journal-entries'] });
      // Show AI response in the UI
    }
  });

  const handleSave = () => {
    if (!title.trim() || !content.trim()) return;

    const entryData = {
      title: title.trim(),
      content: content.trim(),
      entry_type: entryType,
      mood_score: moodScore,
      energy_level: energyLevel,
      tags,
      related_contact_id: relatedContactId,
      related_goal_id: relatedGoalId
    };

    createEntryMutation.mutate(entryData);
  };

  const handleAIReflection = () => {
    if (!entry?.id) return;
    
    aiReflectionMutation.mutate({
      entry_id: entry.id,
      user_question: aiQuestion.trim() || 'Help me reflect on this entry and find insights.',
      reflection_type: reflectionType
    });
  };

  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const getEntryTypeIcon = (type: string) => {
    switch (type) {
      case 'gratitude': return <Heart className="w-4 h-4" />;
      case 'insight': return <Brain className="w-4 h-4" />;
      case 'relationship': return <User className="w-4 h-4" />;
      default: return <PenTool className="w-4 h-4" />;
    }
  };

  const getEntryTypeColor = (type: string) => {
    switch (type) {
      case 'gratitude': return 'from-pink-500 to-rose-500';
      case 'insight': return 'from-purple-500 to-indigo-500';
      case 'relationship': return 'from-blue-500 to-cyan-500';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  if (isEditing) {
    return (
      <div className={`glass-card p-6 ${className}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">
            {isCreating ? 'New Journal Entry' : 'Edit Entry'}
          </h3>
          <button
            onClick={() => setIsEditing(false)}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700/50 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Related Context */}
        {(contactName || goalTitle) && (
          <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <div className="flex items-center text-blue-400 text-sm">
              {contactName && (
                <div className="flex items-center mr-4">
                  <User className="w-4 h-4 mr-1" />
                  {contactName}
                </div>
              )}
              {goalTitle && (
                <div className="flex items-center">
                  <Target className="w-4 h-4 mr-1" />
                  {goalTitle}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Entry Type */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-2">Entry Type</label>
          <div className="flex space-x-2">
            {[
              { type: 'reflection', label: 'Reflection', icon: PenTool },
              { type: 'gratitude', label: 'Gratitude', icon: Heart },
              { type: 'insight', label: 'Insight', icon: Brain },
              { type: 'relationship', label: 'Relationship', icon: User }
            ].map(({ type, label, icon: Icon }) => (
              <button
                key={type}
                onClick={() => setEntryType(type as JournalEntry['entry_type'])}
                className={`flex items-center px-3 py-2 rounded-lg text-sm transition-colors ${
                  entryType === type
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
                }`}
              >
                <Icon className="w-4 h-4 mr-1" />
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Title */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-2">Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What's on your mind?"
            className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-400"
          />
        </div>

        {/* Content */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-2">Content</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Share your thoughts, reflections, or experiences..."
            rows={6}
            className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-400 resize-none"
          />
        </div>

        {/* Mood and Energy */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Mood Score: {moodScore}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={moodScore}
              onChange={(e) => setMoodScore(Number(e.target.value))}
              className="w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Energy Level: {energyLevel}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={energyLevel}
              onChange={(e) => setEnergyLevel(Number(e.target.value))}
              className="w-full"
            />
          </div>
        </div>

        {/* Tags */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Tags</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-2 py-1 bg-blue-600/20 text-blue-400 text-sm rounded-full"
              >
                {tag}
                <button
                  onClick={() => removeTag(tag)}
                  className="ml-1 text-blue-400 hover:text-blue-300"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
          <div className="flex space-x-2">
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addTag()}
              placeholder="Add a tag..."
              className="flex-1 px-3 py-1 bg-gray-800/50 border border-gray-600 rounded text-white placeholder-gray-400 text-sm focus:outline-none focus:border-blue-400"
            />
            <button
              onClick={addTag}
              className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3">
          <button
            onClick={() => setIsEditing(false)}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <AnimatedButton
            onClick={handleSave}
            disabled={!title.trim() || !content.trim() || createEntryMutation.isPending}
            state={createEntryMutation.isPending ? 'loading' : 'idle'}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {isCreating ? 'Create Entry' : 'Save Changes'}
          </AnimatedButton>
        </div>
      </div>
    );
  }

  // Display mode
  return (
    <div className={`glass-card p-6 hover:shadow-lg transition-shadow ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg bg-gradient-to-r ${getEntryTypeColor(entry?.entry_type || 'reflection')}`}>
            {getEntryTypeIcon(entry?.entry_type || 'reflection')}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">{entry?.title}</h3>
            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                {entry?.created_at ? new Date(entry.created_at).toLocaleDateString() : 'Today'}
              </div>
              {entry?.contact_name && (
                <div className="flex items-center">
                  <User className="w-4 h-4 mr-1" />
                  {entry.contact_name}
                </div>
              )}
              {entry?.goal_title && (
                <div className="flex items-center">
                  <Target className="w-4 h-4 mr-1" />
                  {entry.goal_title}
                </div>
              )}
            </div>
          </div>
        </div>
        <button
          onClick={() => setIsEditing(true)}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-700/50 rounded-lg transition-colors"
        >
          <PenTool className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="mb-4">
        <p className="text-gray-300 leading-relaxed">{entry?.content}</p>
      </div>

      {/* Mood and Energy */}
      {(entry?.mood_score || entry?.energy_level) && (
        <div className="flex items-center space-x-6 mb-4 text-sm">
          {entry.mood_score && (
            <div className="flex items-center text-gray-400">
              <span className="mr-2">Mood:</span>
              <div className="flex space-x-1">
                {[...Array(10)].map((_, i) => (
                  <div
                    key={i}
                    className={`w-2 h-2 rounded-full ${
                      i < entry.mood_score! ? 'bg-blue-400' : 'bg-gray-600'
                    }`}
                  />
                ))}
              </div>
              <span className="ml-2">{entry.mood_score}/10</span>
            </div>
          )}
          {entry.energy_level && (
            <div className="flex items-center text-gray-400">
              <span className="mr-2">Energy:</span>
              <div className="flex space-x-1">
                {[...Array(10)].map((_, i) => (
                  <div
                    key={i}
                    className={`w-2 h-2 rounded-full ${
                      i < entry.energy_level! ? 'bg-green-400' : 'bg-gray-600'
                    }`}
                  />
                ))}
              </div>
              <span className="ml-2">{entry.energy_level}/10</span>
            </div>
          )}
        </div>
      )}

      {/* Tags */}
      {entry?.tags && entry.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {entry.tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 bg-gray-700/50 text-gray-300 text-xs rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* AI Reflection */}
      {entry?.ai_reflection && (
        <div className="mb-4 p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg">
          <div className="flex items-center mb-2">
            <Sparkles className="w-4 h-4 text-purple-400 mr-2" />
            <span className="text-sm font-medium text-purple-400">AI Reflection</span>
          </div>
          <p className="text-gray-300 text-sm leading-relaxed">{entry.ai_reflection}</p>
        </div>
      )}

      {/* AI Reflection Interface */}
      {showAIReflection && (
        <div className="mb-4 p-4 bg-gray-800/50 border border-gray-600 rounded-lg">
          <div className="mb-3">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Reflection Type
            </label>
            <div className="flex space-x-2">
              {[
                { type: 'general', label: 'General' },
                { type: 'relationship', label: 'Relationship' },
                { type: 'growth', label: 'Growth' },
                { type: 'insight', label: 'Insight' }
              ].map(({ type, label }) => (
                <button
                  key={type}
                  onClick={() => setReflectionType(type as any)}
                  className={`px-3 py-1 text-xs rounded transition-colors ${
                    reflectionType === type
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          <div className="mb-3">
            <textarea
              value={aiQuestion}
              onChange={(e) => setAiQuestion(e.target.value)}
              placeholder="Ask a specific question about this entry, or leave blank for general insights..."
              rows={3}
              className="w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded text-white placeholder-gray-400 text-sm focus:outline-none focus:border-purple-400 resize-none"
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setShowAIReflection(false)}
              className="px-3 py-1 text-sm text-gray-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <AnimatedButton
              onClick={handleAIReflection}
              disabled={aiReflectionMutation.isPending}
              state={aiReflectionMutation.isPending ? 'loading' : 'idle'}
              className="bg-purple-600 hover:bg-purple-700 text-white"
              size="sm"
            >
              <Sparkles className="w-4 h-4 mr-1" />
              Reflect with AI
            </AnimatedButton>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end">
        <AnimatedButton
          onClick={() => setShowAIReflection(!showAIReflection)}
          variant="secondary"
          size="sm"
          className="text-purple-400 border-purple-400/30 hover:bg-purple-400/10"
        >
          <MessageCircle className="w-4 h-4 mr-1" />
          Reflect with AI
        </AnimatedButton>
      </div>
    </div>
  );
};

export default JournalEntryCard;