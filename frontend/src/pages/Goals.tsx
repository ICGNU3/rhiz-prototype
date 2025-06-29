import { useState, useEffect } from 'react'
import { User, Goal } from '../types'
import { apiService } from '../services/api'
import Navigation from '../components/Navigation'

interface GoalsProps {
  user: User
  onLogout: () => void
}

export default function Goals({ user, onLogout }: GoalsProps) {
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newGoal, setNewGoal] = useState({
    title: '',
    description: '',
    goal_type: 'Professional',
    priority_level: 'Medium',
    target_date: ''
  })

  useEffect(() => {
    loadGoals()
  }, [])

  const loadGoals = async () => {
    try {
      const goals = await apiService.getGoals()
      setGoals(goals)
    } catch (error) {
      console.error('Failed to load goals:', error)
    }
    setLoading(false)
  }

  const handleAddGoal = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const goal = await apiService.createGoal(newGoal)
      setGoals([...goals, goal])
      setNewGoal({ title: '', description: '', goal_type: 'Professional', priority_level: 'Medium', target_date: '' })
      setShowAddForm(false)
    } catch (error) {
      console.error('Failed to create goal:', error)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-500'
      case 'medium': return 'bg-yellow-500'
      case 'low': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'text-green-400'
      case 'in_progress': return 'text-blue-400'
      case 'paused': return 'text-yellow-400'
      case 'not_started': return 'text-gray-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <div className="min-h-screen">
      <Navigation user={user} onLogout={onLogout} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Goals</h1>
            <p className="text-gray-300">Track your relationship and business objectives</p>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="glass-button"
          >
            <svg className="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add Goal
          </button>
        </div>

        {/* Add Goal Form */}
        {showAddForm && (
          <div className="glass-card p-6 mb-6">
            <h2 className="text-xl font-semibold text-white mb-4">Create New Goal</h2>
            <form onSubmit={handleAddGoal} className="space-y-4">
              <input
                type="text"
                placeholder="Goal title *"
                value={newGoal.title}
                onChange={(e) => setNewGoal({ ...newGoal, title: e.target.value })}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white placeholder-gray-400"
                required
              />
              <textarea
                placeholder="Description"
                value={newGoal.description}
                onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white placeholder-gray-400 resize-none"
                rows={3}
              />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <select
                  value={newGoal.goal_type}
                  onChange={(e) => setNewGoal({ ...newGoal, goal_type: e.target.value })}
                  className="px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white"
                >
                  <option value="Professional">Professional</option>
                  <option value="Fundraising">Fundraising</option>
                  <option value="Hiring">Hiring</option>
                  <option value="Partnerships">Partnerships</option>
                  <option value="Personal">Personal</option>
                </select>
                <select
                  value={newGoal.priority_level}
                  onChange={(e) => setNewGoal({ ...newGoal, priority_level: e.target.value })}
                  className="px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white"
                >
                  <option value="High">High Priority</option>
                  <option value="Medium">Medium Priority</option>
                  <option value="Low">Low Priority</option>
                </select>
                <input
                  type="date"
                  value={newGoal.target_date}
                  onChange={(e) => setNewGoal({ ...newGoal, target_date: e.target.value })}
                  className="px-4 py-3 bg-gray-800/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-400 text-white"
                />
              </div>
              <div className="flex space-x-4">
                <button
                  type="submit"
                  className="glass-button bg-blue-500/20 hover:bg-blue-500/30"
                >
                  Create Goal
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="glass-button"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Goals Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
            <p className="text-gray-300 mt-4">Loading goals...</p>
          </div>
        ) : goals.length === 0 ? (
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="text-xl font-semibold text-white mb-2">No goals yet</h3>
            <p className="text-gray-400">Start by creating your first relationship objective</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {goals.map((goal) => (
              <div key={goal.id} className="glass-card p-6 hover:bg-white/5 transition-colors">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-2">{goal.title}</h3>
                    <span className="inline-block px-2 py-1 text-xs rounded-full bg-blue-500/20 text-blue-400 mb-2">
                      {goal.goal_type}
                    </span>
                  </div>
                  <div className={`w-3 h-3 rounded-full ${getPriorityColor(goal.priority_level)}`} 
                       title={`Priority: ${goal.priority_level}`} />
                </div>
                
                {goal.description && (
                  <p className="text-gray-300 text-sm mb-4 line-clamp-3">{goal.description}</p>
                )}
                
                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-400 text-sm">Progress</span>
                    <span className="text-gray-300 text-sm">{goal.progress_percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${goal.progress_percentage}%` }}
                    />
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className={`${getStatusColor(goal.status)} capitalize`}>
                    {goal.status.replace('_', ' ')}
                  </span>
                  {goal.target_date && (
                    <span className="text-gray-400">
                      Due: {new Date(goal.target_date).toLocaleDateString()}
                    </span>
                  )}
                </div>
                
                {goal.timeline && (
                  <div className="mt-3 text-xs text-gray-400">
                    Timeline: {goal.timeline}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}