import React, { useState, useEffect } from 'react';

interface MissedConnection {
  name: string;
  company: string;
  confidence_score: number;
  reason: string;
}

interface DailyAction {
  type: string;
  priority: string;
  contact_name: string;
  action_text: string;
}

const IntelligencePage: React.FC = () => {
  const [missedConnections, setMissedConnections] = useState<MissedConnection[]>([]);
  const [dailyActions, setDailyActions] = useState<DailyAction[]>([]);

  useEffect(() => {
    // Fetch AI assistant data
    fetch('/api/intelligence/assistant')
      .then(res => res.json())
      .then(data => {
        setMissedConnections(data.missed_connections || []);
        setDailyActions(data.daily_actions || []);
      })
      .catch(err => console.error('Failed to load intelligence data:', err));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              AI Assistant
            </h1>
            <p className="text-gray-300 mt-2">
              Ambient intelligence surfacing missed connections and daily micro-actions
            </p>
          </div>
          <div className="flex gap-3">
            <button className="glass-button px-4 py-2 rounded-lg text-blue-400 border border-blue-400/30 hover:bg-blue-400/10">
              <i className="bi bi-arrow-clockwise me-2"></i>
              Refresh Connections
            </button>
            <button className="glass-button px-4 py-2 rounded-lg text-purple-400 border border-purple-400/30 hover:bg-purple-400/10">
              <i className="bi bi-lightning me-2"></i>
              Refresh Actions
            </button>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Missed Connections */}
          <div className="glass-card p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white flex items-center">
                <i className="bi bi-people me-3 text-blue-400"></i>
                Missed Connections
              </h3>
              <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full text-sm">
                {missedConnections.length}
              </span>
            </div>
            
            {missedConnections.length > 0 ? (
              <div className="space-y-4">
                {missedConnections.map((connection, index) => (
                  <div key={index} className="p-4 bg-gray-800/30 rounded-lg border border-gray-700/50">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h6 className="font-medium text-white">{connection.name}</h6>
                        <p className="text-gray-400 text-sm">{connection.company}</p>
                      </div>
                      <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs">
                        {Math.round(connection.confidence_score * 100)}%
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm">{connection.reason}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <i className="bi bi-search text-3xl mb-3 block"></i>
                <p>No missed connections found</p>
              </div>
            )}
          </div>

          {/* Daily Actions */}
          <div className="glass-card p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white flex items-center">
                <i className="bi bi-lightning me-3 text-purple-400"></i>
                Daily Actions
              </h3>
              <span className="bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full text-sm">
                {dailyActions.length}
              </span>
            </div>
            
            {dailyActions.length > 0 ? (
              <div className="space-y-4">
                {dailyActions.map((action, index) => (
                  <div key={index} className="p-4 bg-gray-800/30 rounded-lg border border-gray-700/50">
                    <div className="flex justify-between items-start mb-2">
                      <span className={`px-2 py-1 rounded text-xs ${
                        action.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                        action.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-green-500/20 text-green-400'
                      }`}>
                        {action.priority.toUpperCase()}
                      </span>
                      <span className="text-gray-400 text-xs">{action.type}</span>
                    </div>
                    <h6 className="font-medium text-white mb-1">{action.contact_name}</h6>
                    <p className="text-gray-300 text-sm">{action.action_text}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <i className="bi bi-check-circle text-3xl mb-3 block"></i>
                <p>All caught up!</p>
              </div>
            )}
          </div>

          {/* Weekly Insights */}
          <div className="glass-card p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white flex items-center">
                <i className="bi bi-graph-up me-3 text-green-400"></i>
                Weekly Insights
              </h3>
            </div>
            
            <div className="space-y-4">
              <div className="p-4 bg-gray-800/30 rounded-lg border border-gray-700/50">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-green-400 text-sm">Network Growth</span>
                  <span className="text-green-400">+12%</span>
                </div>
                <p className="text-gray-300 text-sm">Added 8 meaningful connections this week</p>
              </div>
              
              <div className="p-4 bg-gray-800/30 rounded-lg border border-gray-700/50">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-blue-400 text-sm">Interaction Quality</span>
                  <span className="text-blue-400">Excellent</span>
                </div>
                <p className="text-gray-300 text-sm">Strong trust signals from recent conversations</p>
              </div>
              
              <div className="p-4 bg-gray-800/30 rounded-lg border border-gray-700/50">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-purple-400 text-sm">Goal Progress</span>
                  <span className="text-purple-400">75%</span>
                </div>
                <p className="text-gray-300 text-sm">Fundraising goal is progressing well</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
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
      `}</style>
    </div>
  );
};

export default IntelligencePage;