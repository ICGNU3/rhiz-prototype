import React, { useState, useEffect } from 'react';
import { 
  User, 
  Bell, 
  Database, 
  Link2, 
  Download, 
  Save,
  Clock,
  Mail,
  MessageSquare,
  Linkedin,
  Chrome,
  Twitter,
  Key
} from 'lucide-react';

interface UserProfile {
  id: string;
  name: string;
  email: string;
  timezone: string;
  subscription_tier: string;
}

interface NotificationPreferences {
  email_notifications: boolean;
  push_notifications: boolean;
  weekly_digest: boolean;
  relationship_updates: boolean;
  goal_reminders: boolean;
}

interface IntegrationStatus {
  linkedin: boolean;
  google: boolean;
  twitter: boolean;
}

const Settings: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile>({
    id: '',
    name: '',
    email: '',
    timezone: 'America/New_York',
    subscription_tier: 'free'
  });
  
  const [notifications, setNotifications] = useState<NotificationPreferences>({
    email_notifications: true,
    push_notifications: false,
    weekly_digest: true,
    relationship_updates: true,
    goal_reminders: false
  });
  
  const [integrations, setIntegrations] = useState<IntegrationStatus>({
    linkedin: false,
    google: false,
    twitter: false
  });
  
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Load current settings
    fetchUserProfile();
    fetchNotificationPreferences();
    fetchIntegrationStatus();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch('/api/settings/profile');
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    }
  };

  const fetchNotificationPreferences = async () => {
    try {
      const response = await fetch('/api/settings/notifications');
      if (response.ok) {
        const data = await response.json();
        setNotifications(data);
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const fetchIntegrationStatus = async () => {
    try {
      const response = await fetch('/api/settings/integrations');
      if (response.ok) {
        const data = await response.json();
        setIntegrations(data);
      }
    } catch (error) {
      console.error('Failed to fetch integrations:', error);
    }
  };

  const saveProfile = async () => {
    setSaving(true);
    try {
      const response = await fetch('/api/settings/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile)
      });
      
      if (response.ok) {
        setMessage('Profile updated successfully');
        setTimeout(() => setMessage(''), 3000);
      }
    } catch (error) {
      console.error('Failed to save profile:', error);
      setMessage('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const saveNotifications = async () => {
    setSaving(true);
    try {
      const response = await fetch('/api/settings/notifications', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(notifications)
      });
      
      if (response.ok) {
        setMessage('Notification preferences updated');
        setTimeout(() => setMessage(''), 3000);
      }
    } catch (error) {
      console.error('Failed to save notifications:', error);
      setMessage('Failed to update notifications');
    } finally {
      setSaving(false);
    }
  };

  const toggleIntegration = async (platform: keyof IntegrationStatus) => {
    try {
      if (integrations[platform]) {
        // Disconnect
        const response = await fetch(`/api/settings/integrations/${platform}/disconnect`, {
          method: 'POST'
        });
        if (response.ok) {
          setIntegrations(prev => ({ ...prev, [platform]: false }));
          setMessage(`${platform} disconnected`);
        }
      } else {
        // Connect - redirect to OAuth
        const response = await fetch(`/api/settings/integrations/${platform}/connect`);
        if (response.ok) {
          const { oauth_url } = await response.json();
          window.open(oauth_url, '_blank', 'width=600,height=600');
        }
      }
    } catch (error) {
      console.error(`Failed to toggle ${platform}:`, error);
      setMessage(`Failed to update ${platform} connection`);
    }
    setTimeout(() => setMessage(''), 3000);
  };

  const exportData = async () => {
    try {
      const response = await fetch('/api/settings/export');
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `rhiz-data-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        setMessage('Data export downloaded');
        setTimeout(() => setMessage(''), 3000);
      }
    } catch (error) {
      console.error('Failed to export data:', error);
      setMessage('Failed to export data');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const timezones = [
    'America/New_York',
    'America/Chicago', 
    'America/Denver',
    'America/Los_Angeles',
    'Europe/London',
    'Europe/Paris',
    'Asia/Tokyo',
    'Asia/Shanghai',
    'Australia/Sydney'
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">Settings</h2>
        <p className="text-gray-400 mt-1">Manage your account and preferences</p>
        {message && (
          <div className="mt-2 p-3 bg-green-500/20 border border-green-500/30 rounded-lg">
            <p className="text-green-300 text-sm">{message}</p>
          </div>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Profile Settings */}
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500">
              <User size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white">Profile</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Name
              </label>
              <input
                type="text"
                value={profile.name}
                onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                placeholder="Your name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email
              </label>
              <input
                type="email"
                value={profile.email}
                onChange={(e) => setProfile(prev => ({ ...prev, email: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                placeholder="your@email.com"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <Clock size={16} className="inline mr-1" />
                Timezone
              </label>
              <select
                value={profile.timezone}
                onChange={(e) => setProfile(prev => ({ ...prev, timezone: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
              >
                {timezones.map(tz => (
                  <option key={tz} value={tz}>{tz.replace('_', ' ')}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Subscription
              </label>
              <div className="p-3 bg-gray-800/30 border border-gray-700 rounded-lg">
                <span className="text-white capitalize">{profile.subscription_tier}</span>
                <p className="text-xs text-gray-400 mt-1">
                  {profile.subscription_tier === 'free' ? 'Upgrade to Founder+ for unlimited features' : 'Premium subscription active'}
                </p>
              </div>
            </div>
            
            <button
              onClick={saveProfile}
              disabled={saving}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
            >
              <Save size={16} />
              <span>{saving ? 'Saving...' : 'Save Profile'}</span>
            </button>
          </div>
        </div>

        {/* Integrations */}
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500">
              <Link2 size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white">Connect Integrations</h3>
          </div>
          
          <div className="space-y-4">
            {/* LinkedIn */}
            <div className="flex items-center justify-between p-4 bg-gray-800/30 border border-gray-700 rounded-lg">
              <div className="flex items-center space-x-3">
                <Linkedin size={24} className="text-blue-500" />
                <div>
                  <h4 className="text-white font-medium">LinkedIn</h4>
                  <p className="text-sm text-gray-400">Sync professional connections</p>
                </div>
              </div>
              <button
                onClick={() => toggleIntegration('linkedin')}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  integrations.linkedin ? 'bg-blue-600' : 'bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    integrations.linkedin ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Google */}
            <div className="flex items-center justify-between p-4 bg-gray-800/30 border border-gray-700 rounded-lg">
              <div className="flex items-center space-x-3">
                <Chrome size={24} className="text-red-500" />
                <div>
                  <h4 className="text-white font-medium">Google Contacts</h4>
                  <p className="text-sm text-gray-400">Import contact information</p>
                </div>
              </div>
              <button
                onClick={() => toggleIntegration('google')}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  integrations.google ? 'bg-blue-600' : 'bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    integrations.google ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* X/Twitter */}
            <div className="flex items-center justify-between p-4 bg-gray-800/30 border border-gray-700 rounded-lg">
              <div className="flex items-center space-x-3">
                <Twitter size={24} className="text-blue-400" />
                <div>
                  <h4 className="text-white font-medium">X (Twitter)</h4>
                  <p className="text-sm text-gray-400">Track social interactions</p>
                </div>
              </div>
              <button
                onClick={() => toggleIntegration('twitter')}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  integrations.twitter ? 'bg-blue-600' : 'bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    integrations.twitter ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Notification Preferences */}
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500">
              <Bell size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white">Notifications</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Mail size={16} className="text-gray-400" />
                <div>
                  <p className="text-white font-medium">Email Notifications</p>
                  <p className="text-sm text-gray-400">Receive updates via email</p>
                </div>
              </div>
              <button
                onClick={() => setNotifications(prev => ({ ...prev, email_notifications: !prev.email_notifications }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  notifications.email_notifications ? 'bg-blue-600' : 'bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    notifications.email_notifications ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <MessageSquare size={16} className="text-gray-400" />
                <div>
                  <p className="text-white font-medium">Push Notifications</p>
                  <p className="text-sm text-gray-400">Browser notifications</p>
                </div>
              </div>
              <button
                onClick={() => setNotifications(prev => ({ ...prev, push_notifications: !prev.push_notifications }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  notifications.push_notifications ? 'bg-blue-600' : 'bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    notifications.push_notifications ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Weekly Digest</p>
                <p className="text-sm text-gray-400">Summary of relationship activity</p>
              </div>
              <button
                onClick={() => setNotifications(prev => ({ ...prev, weekly_digest: !prev.weekly_digest }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  notifications.weekly_digest ? 'bg-blue-600' : 'bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    notifications.weekly_digest ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Relationship Updates</p>
                <p className="text-sm text-gray-400">Contact interaction reminders</p>
              </div>
              <button
                onClick={() => setNotifications(prev => ({ ...prev, relationship_updates: !prev.relationship_updates }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  notifications.relationship_updates ? 'bg-blue-600' : 'bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    notifications.relationship_updates ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Goal Reminders</p>
                <p className="text-sm text-gray-400">Progress tracking alerts</p>
              </div>
              <button
                onClick={() => setNotifications(prev => ({ ...prev, goal_reminders: !prev.goal_reminders }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  notifications.goal_reminders ? 'bg-blue-600' : 'bg-gray-600'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    notifications.goal_reminders ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
            
            <button
              onClick={saveNotifications}
              disabled={saving}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded-lg transition-colors"
            >
              <Save size={16} />
              <span>{saving ? 'Saving...' : 'Save Preferences'}</span>
            </button>
          </div>
        </div>

        {/* Data Management */}
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg bg-gradient-to-r from-orange-500 to-red-500">
              <Database size={20} className="text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white">Data Management</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <h4 className="text-white font-medium mb-2">Export Your Data</h4>
              <p className="text-sm text-gray-400 mb-4">
                Download all your contacts, goals, and interactions in JSON format
              </p>
              <button
                onClick={exportData}
                className="flex items-center space-x-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
              >
                <Download size={16} />
                <span>Export Data (JSON)</span>
              </button>
            </div>
            
            <div className="pt-4 border-t border-gray-700">
              <h4 className="text-white font-medium mb-2">Privacy</h4>
              <p className="text-sm text-gray-400">
                Your relationship data is private and encrypted. Only you can access your network insights.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
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

      </div>
    </div>
  );
};

export default Settings;