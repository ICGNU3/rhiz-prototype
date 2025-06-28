import React, { useState, useEffect } from 'react';
import { Calendar, CheckSquare, FileText, Paperclip, Plus, Clock, User } from 'lucide-react';

interface Task {
  id: string;
  title: string;
  description: string;
  due_date: string;
  priority: 'high' | 'medium' | 'low';
  completed: boolean;
  contact_id?: string;
  contact_name?: string;
}

interface Reminder {
  id: string;
  title: string;
  description: string;
  reminder_time: string;
  contact_id?: string;
  contact_name?: string;
}

interface JournalEntry {
  id: string;
  title: string;
  content: string;
  created_at: string;
  contact_id?: string;
  contact_name?: string;
}

const CrmPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('tasks');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [journalEntries, setJournalEntries] = useState<JournalEntry[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    // Load tasks
    fetch('/api/crm/tasks')
      .then(res => res.json())
      .then(data => setTasks(data.tasks || []))
      .catch(err => console.error('Failed to load tasks:', err));

    // Load reminders
    fetch('/api/crm/reminders')
      .then(res => res.json())
      .then(data => setReminders(data.reminders || []))
      .catch(err => console.error('Failed to load reminders:', err));

    // Load journal entries
    fetch('/api/crm/journal')
      .then(res => res.json())
      .then(data => setJournalEntries(data.entries || []))
      .catch(err => console.error('Failed to load journal entries:', err));
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-danger';
      case 'medium': return 'text-warning';
      case 'low': return 'text-success';
      default: return 'text-secondary';
    }
  };

  const TasksTab = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="text-white">Tasks & Follow-ups</h4>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus className="w-4 h-4 me-2" />
          New Task
        </button>
      </div>

      {tasks.length > 0 ? (
        <div className="space-y-3">
          {tasks.map((task) => (
            <div key={task.id} className="glass-card p-4">
              <div className="d-flex justify-content-between align-items-start mb-3">
                <div className="d-flex align-items-center">
                  <input 
                    type="checkbox" 
                    checked={task.completed}
                    className="form-check-input me-3"
                    onChange={() => {
                      // Toggle task completion
                      setTasks(tasks.map(t => 
                        t.id === task.id ? {...t, completed: !t.completed} : t
                      ));
                    }}
                  />
                  <div>
                    <h6 className={`mb-1 ${task.completed ? 'text-decoration-line-through text-muted' : 'text-white'}`}>
                      {task.title}
                    </h6>
                    {task.contact_name && (
                      <small className="text-info">
                        <User className="w-3 h-3 me-1" />
                        {task.contact_name}
                      </small>
                    )}
                  </div>
                </div>
                <div className="d-flex align-items-center">
                  <span className={`badge me-2 ${getPriorityColor(task.priority)}`}>
                    {task.priority.toUpperCase()}
                  </span>
                  <small className="text-muted">
                    <Calendar className="w-3 h-3 me-1" />
                    {new Date(task.due_date).toLocaleDateString()}
                  </small>
                </div>
              </div>
              
              {task.description && (
                <p className="text-gray-300 text-sm mb-0">{task.description}</p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <CheckSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No tasks yet</p>
          <button 
            className="btn btn-outline-primary"
            onClick={() => setShowCreateModal(true)}
          >
            Create your first task
          </button>
        </div>
      )}
    </div>
  );

  const RemindersTab = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="text-white">Reminders</h4>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus className="w-4 h-4 me-2" />
          New Reminder
        </button>
      </div>

      {reminders.length > 0 ? (
        <div className="space-y-3">
          {reminders.map((reminder) => (
            <div key={reminder.id} className="glass-card p-4">
              <div className="d-flex justify-content-between align-items-start mb-2">
                <h6 className="text-white mb-1">{reminder.title}</h6>
                <small className="text-muted">
                  <Clock className="w-3 h-3 me-1" />
                  {new Date(reminder.reminder_time).toLocaleString()}
                </small>
              </div>
              
              {reminder.contact_name && (
                <small className="text-info d-block mb-2">
                  <User className="w-3 h-3 me-1" />
                  {reminder.contact_name}
                </small>
              )}
              
              {reminder.description && (
                <p className="text-gray-300 text-sm mb-0">{reminder.description}</p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No reminders set</p>
          <button 
            className="btn btn-outline-primary"
            onClick={() => setShowCreateModal(true)}
          >
            Create your first reminder
          </button>
        </div>
      )}
    </div>
  );

  const JournalTab = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="text-white">Journal Entries</h4>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus className="w-4 h-4 me-2" />
          New Entry
        </button>
      </div>

      {journalEntries.length > 0 ? (
        <div className="space-y-4">
          {journalEntries.map((entry) => (
            <div key={entry.id} className="glass-card p-4">
              <div className="d-flex justify-content-between align-items-start mb-3">
                <h6 className="text-white">{entry.title}</h6>
                <small className="text-muted">
                  {new Date(entry.created_at).toLocaleDateString()}
                </small>
              </div>
              
              {entry.contact_name && (
                <small className="text-info d-block mb-2">
                  <User className="w-3 h-3 me-1" />
                  {entry.contact_name}
                </small>
              )}
              
              <p className="text-gray-300 text-sm mb-0">{entry.content}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No journal entries yet</p>
          <button 
            className="btn btn-outline-primary"
            onClick={() => setShowCreateModal(true)}
          >
            Write your first entry
          </button>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            CRM Tools
          </h1>
          <p className="text-gray-300 mt-2">
            Manage tasks, reminders, and relationship notes
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="glass-card p-2 mb-6">
          <nav className="nav nav-pills">
            <button 
              className={`nav-link ${activeTab === 'tasks' ? 'active bg-primary' : 'text-gray-300'}`}
              onClick={() => setActiveTab('tasks')}
            >
              <CheckSquare className="w-4 h-4 me-2" />
              Tasks
            </button>
            <button 
              className={`nav-link ${activeTab === 'reminders' ? 'active bg-primary' : 'text-gray-300'}`}
              onClick={() => setActiveTab('reminders')}
            >
              <Clock className="w-4 h-4 me-2" />
              Reminders
            </button>
            <button 
              className={`nav-link ${activeTab === 'journal' ? 'active bg-primary' : 'text-gray-300'}`}
              onClick={() => setActiveTab('journal')}
            >
              <FileText className="w-4 h-4 me-2" />
              Journal
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="glass-card p-6">
          {activeTab === 'tasks' && <TasksTab />}
          {activeTab === 'reminders' && <RemindersTab />}
          {activeTab === 'journal' && <JournalTab />}
        </div>

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed-top d-flex align-items-center justify-content-center h-100" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
            <div className="glass-card p-6 m-4" style={{maxWidth: '500px', width: '100%'}}>
              <h5 className="text-white mb-4">
                Create {activeTab === 'tasks' ? 'Task' : activeTab === 'reminders' ? 'Reminder' : 'Journal Entry'}
              </h5>
              
              <form className="space-y-4">
                <div className="mb-3">
                  <label className="form-label text-gray-300">Title</label>
                  <input 
                    type="text" 
                    className="form-control bg-gray-800/50 border-gray-600 text-white"
                    placeholder="Enter title..."
                  />
                </div>
                
                <div className="mb-3">
                  <label className="form-label text-gray-300">Description</label>
                  <textarea 
                    className="form-control bg-gray-800/50 border-gray-600 text-white"
                    rows={3}
                    placeholder="Enter description..."
                  />
                </div>
                
                {activeTab === 'tasks' && (
                  <>
                    <div className="mb-3">
                      <label className="form-label text-gray-300">Due Date</label>
                      <input 
                        type="date" 
                        className="form-control bg-gray-800/50 border-gray-600 text-white"
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label text-gray-300">Priority</label>
                      <select className="form-select bg-gray-800/50 border-gray-600 text-white">
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>
                    </div>
                  </>
                )}
                
                {activeTab === 'reminders' && (
                  <div className="mb-3">
                    <label className="form-label text-gray-300">Reminder Time</label>
                    <input 
                      type="datetime-local" 
                      className="form-control bg-gray-800/50 border-gray-600 text-white"
                    />
                  </div>
                )}
                
                <div className="d-flex gap-3 pt-3">
                  <button 
                    type="button"
                    className="btn btn-outline-secondary flex-1"
                    onClick={() => setShowCreateModal(false)}
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit"
                    className="btn btn-primary flex-1"
                  >
                    Create
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
        
        .space-y-3 > * + * {
          margin-top: 0.75rem;
        }
        
        .space-y-4 > * + * {
          margin-top: 1rem;
        }
        
        .nav-link {
          border-radius: 8px;
          padding: 0.5rem 1rem;
          margin: 0 0.25rem;
          display: flex;
          align-items: center;
          border: none;
          background: none;
        }
        
        .nav-link:hover {
          background: rgba(255, 255, 255, 0.1);
        }
      `}</style>
    </div>
  );
};

export default CrmPage;