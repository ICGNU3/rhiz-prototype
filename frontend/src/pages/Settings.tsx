import React from 'react';
import { Settings as SettingsIcon, User, Bell, Database, Key } from 'lucide-react';

const Settings: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">Settings</h2>
        <p className="text-gray-400 mt-1">Manage your account and preferences</p>
      </div>

      {/* Settings Sections */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Profile Settings */}
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500">
              <User size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white">Profile Settings</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <input
                type="email"
                className="w-full px-4 py-3 bg-dark-card border border-dark-border rounded-lg text-white placeholder-gray-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-colors"
                placeholder="your@email.com"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Subscription Tier
              </label>
              <div className="p-3 bg-dark-card border border-dark-border rounded-lg">
                <span className="text-white capitalize">Explorer (Free)</span>
                <p className="text-xs text-gray-400 mt-1">
                  Upgrade to Founder+ for unlimited features
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500">
              <Bell size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white">Notifications</h3>
          </div>
          
          <div className="space-y-4">
            {[
              { label: 'AI Suggestions', description: 'Get notified of new contact matches' },
              { label: 'Follow-up Reminders', description: 'Reminders for scheduled follow-ups' },
              { label: 'Network Updates', description: 'Updates about your network growth' },
              { label: 'Weekly Digest', description: 'Weekly summary of activity' },
            ].map(({ label, description }) => (
              <div key={label} className="flex items-center justify-between">
                <div>
                  <div className="text-white text-sm font-medium">{label}</div>
                  <div className="text-gray-400 text-xs">{description}</div>
                </div>
                <div className="relative">
                  <input
                    type="checkbox"
                    className="sr-only"
                    defaultChecked
                  />
                  <div className="w-10 h-6 bg-primary-500 rounded-full cursor-pointer">
                    <div className="w-4 h-4 bg-white rounded-full shadow-md transform translate-x-5 translate-y-1 transition-transform"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Data & Privacy */}
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500">
              <Database size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white">Data & Privacy</h3>
          </div>
          
          <div className="space-y-4">
            <button className="w-full text-left p-3 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-gray-600 transition-colors">
              <div className="text-white text-sm font-medium">Export Data</div>
              <div className="text-gray-400 text-xs">Download all your contacts and goals</div>
            </button>
            
            <button className="w-full text-left p-3 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-gray-600 transition-colors">
              <div className="text-white text-sm font-medium">Delete Account</div>
              <div className="text-gray-400 text-xs">Permanently delete your account and data</div>
            </button>
          </div>
        </div>

        {/* API & Integrations */}
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg bg-gradient-to-r from-orange-500 to-red-500">
              <Key size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white">Integrations</h3>
          </div>
          
          <div className="space-y-4">
            <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white text-sm font-medium">Email Integration</div>
                  <div className="text-gray-400 text-xs">Connect email for direct outreach</div>
                </div>
                <button className="glass-button-secondary text-xs px-3 py-1">
                  Configure
                </button>
              </div>
            </div>
            
            <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white text-sm font-medium">LinkedIn Import</div>
                  <div className="text-gray-400 text-xs">Import contacts from LinkedIn</div>
                </div>
                <button className="glass-button-secondary text-xs px-3 py-1">
                  Import
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button className="glass-button-primary">
          Save Changes
        </button>
      </div>
    </div>
  );
};

export default Settings;