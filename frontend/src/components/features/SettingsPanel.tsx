/**
 * Comprehensive Settings Panel with profile, notifications, sync, and privacy controls
 */

import React, { useState, useEffect } from 'react';
import type { User, UserSettings, NotificationSettings, SyncSettings } from '../../types';

interface SettingsPanelProps {
  user: User;
  onUserUpdate: (user: User) => void;
  className?: string;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({ user, onUserUpdate, className = '' }) => {
  const [activeTab, setActiveTab] = useState<'profile' | 'notifications' | 'sync' | 'privacy' | 'subscription'>('profile');
  const [settings, setSettings] = useState<UserSettings>({
    notifications: {
      email_enabled: true,
      push_enabled: true,
      weekly_insights: true,
      trust_updates: true,
      goal_reminders: true,
      quiet_hours_start: '22:00',
      quiet_hours_end: '08:00'
    },
    sync: {
      google_contacts: false,
      linkedin: false,
      icloud: false,
      calendar: false,
      auto_sync_frequency: 'weekly'
    },
    privacy: {
      profile_visibility: 'private',
      data_export_enabled: true,
      analytics_enabled: true
    }
  });
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<string>('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch('/api/user/settings', { credentials: 'include' });
      if (response.ok) {
        const userSettings = await response.json();
        setSettings(userSettings);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const saveSettings = async (newSettings: Partial<UserSettings>) => {
    setIsSaving(true);
    setSaveStatus('');
    
    try {
      const response = await fetch('/api/user/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(newSettings)
      });

      if (response.ok) {
        setSaveStatus('Settings saved successfully');
        setTimeout(() => setSaveStatus(''), 3000);
      } else {
        setSaveStatus('Failed to save settings');
      }
    } catch (error) {
      setSaveStatus('Error saving settings');
    } finally {
      setIsSaving(false);
    }
  };

  const updateNotifications = (updates: Partial<NotificationSettings>) => {
    const newSettings = {
      ...settings,
      notifications: { ...settings.notifications, ...updates }
    };
    setSettings(newSettings);
    saveSettings({ notifications: newSettings.notifications });
  };

  const updateSync = (updates: Partial<SyncSettings>) => {
    const newSettings = {
      ...settings,
      sync: { ...settings.sync, ...updates }
    };
    setSettings(newSettings);
    saveSettings({ sync: newSettings.sync });
  };

  const updatePrivacy = (updates: Partial<typeof settings.privacy>) => {
    const newSettings = {
      ...settings,
      privacy: { ...settings.privacy, ...updates }
    };
    setSettings(newSettings);
    saveSettings({ privacy: newSettings.privacy });
  };

  const tabs = [
    { key: 'profile', label: 'Profile', icon: '👤' },
    { key: 'notifications', label: 'Notifications', icon: '🔔' },
    { key: 'sync', label: 'Sync & Import', icon: '🔄' },
    { key: 'privacy', label: 'Privacy & Security', icon: '🔒' },
    { key: 'subscription', label: 'Subscription', icon: '💳' }
  ];

  return (
    <div className={`glass-card p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold gradient-text">Settings</h2>
        {saveStatus && (
          <div className={`px-3 py-1 rounded-lg text-sm ${
            saveStatus.includes('success') ? 'bg-green-500 bg-opacity-20 text-green-300' : 'bg-red-500 bg-opacity-20 text-red-300'
          }`}>
            {saveStatus}
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-6 bg-white bg-opacity-5 rounded-lg p-1 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`flex-shrink-0 py-2 px-4 rounded-md transition-all text-sm ${
              activeTab === tab.key
                ? 'bg-white bg-opacity-10 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'profile' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Profile Information</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">First Name</label>
                    <input
                      type="text"
                      defaultValue={user.first_name || ''}
                      className="w-full px-3 py-2 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter first name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Last Name</label>
                    <input
                      type="text"
                      defaultValue={user.last_name || ''}
                      className="w-full px-3 py-2 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter last name"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                  <input
                    type="email"
                    value={user.email}
                    readOnly
                    className="w-full px-3 py-2 bg-white bg-opacity-5 border border-white border-opacity-10 rounded-lg text-gray-400 cursor-not-allowed"
                  />
                  <p className="text-xs text-gray-400 mt-1">Email cannot be changed. Contact support if needed.</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Profile Picture</label>
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-white bg-opacity-10 rounded-full flex items-center justify-center">
                      {user.profile_image_url ? (
                        <img src={user.profile_image_url} alt="Profile" className="w-16 h-16 rounded-full object-cover" />
                      ) : (
                        <span className="text-2xl text-gray-400">👤</span>
                      )}
                    </div>
                    <button className="px-4 py-2 bg-white bg-opacity-10 hover:bg-opacity-20 rounded-lg transition-all text-sm text-white border border-white border-opacity-20">
                      Upload New Photo
                    </button>
                  </div>
                </div>

                <button className="px-6 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition-all text-white font-medium">
                  Save Profile Changes
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Notification Preferences</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-white bg-opacity-5 rounded-lg">
                  <div>
                    <h4 className="font-medium text-white">Email Notifications</h4>
                    <p className="text-sm text-gray-400">Receive updates via email</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.notifications.email_enabled}
                      onChange={(e) => updateNotifications({ email_enabled: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between p-4 bg-white bg-opacity-5 rounded-lg">
                  <div>
                    <h4 className="font-medium text-white">Weekly Insights</h4>
                    <p className="text-sm text-gray-400">Receive weekly network analysis</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.notifications.weekly_insights}
                      onChange={(e) => updateNotifications({ weekly_insights: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between p-4 bg-white bg-opacity-5 rounded-lg">
                  <div>
                    <h4 className="font-medium text-white">Trust Updates</h4>
                    <p className="text-sm text-gray-400">Get notified about relationship changes</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.notifications.trust_updates}
                      onChange={(e) => updateNotifications({ trust_updates: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                  </label>
                </div>

                <div>
                  <h4 className="font-medium text-white mb-3">Quiet Hours</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Start</label>
                      <input
                        type="time"
                        value={settings.notifications.quiet_hours_start}
                        onChange={(e) => updateNotifications({ quiet_hours_start: e.target.value })}
                        className="w-full px-3 py-2 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">End</label>
                      <input
                        type="time"
                        value={settings.notifications.quiet_hours_end}
                        onChange={(e) => updateNotifications({ quiet_hours_end: e.target.value })}
                        className="w-full px-3 py-2 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'sync' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Contact Sync & Import</h3>
              <div className="space-y-4">
                {[
                  { key: 'google_contacts', label: 'Google Contacts', icon: '📧', description: 'Sync contacts from Google' },
                  { key: 'linkedin', label: 'LinkedIn', icon: '💼', description: 'Import LinkedIn connections' },
                  { key: 'icloud', label: 'iCloud Contacts', icon: '📱', description: 'Sync contacts from iCloud' },
                  { key: 'calendar', label: 'Calendar Events', icon: '📅', description: 'Import meeting attendees' }
                ].map((integration) => (
                  <div key={integration.key} className="flex items-center justify-between p-4 bg-white bg-opacity-5 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{integration.icon}</span>
                      <div>
                        <h4 className="font-medium text-white">{integration.label}</h4>
                        <p className="text-sm text-gray-400">{integration.description}</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.sync[integration.key as keyof SyncSettings] as boolean}
                        onChange={(e) => updateSync({ [integration.key]: e.target.checked } as any)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                    </label>
                  </div>
                ))}

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Auto-sync Frequency</label>
                  <select
                    value={settings.sync.auto_sync_frequency}
                    onChange={(e) => updateSync({ auto_sync_frequency: e.target.value as any })}
                    className="w-full px-3 py-2 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="never">Never</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'privacy' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Privacy & Security</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Profile Visibility</label>
                  <select
                    value={settings.privacy.profile_visibility}
                    onChange={(e) => updatePrivacy({ profile_visibility: e.target.value as any })}
                    className="w-full px-3 py-2 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="private">Private</option>
                    <option value="connections">Connections Only</option>
                    <option value="public">Public</option>
                  </select>
                </div>

                <div className="flex items-center justify-between p-4 bg-white bg-opacity-5 rounded-lg">
                  <div>
                    <h4 className="font-medium text-white">Data Export</h4>
                    <p className="text-sm text-gray-400">Allow data export for backup</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.privacy.data_export_enabled}
                      onChange={(e) => updatePrivacy({ data_export_enabled: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between p-4 bg-white bg-opacity-5 rounded-lg">
                  <div>
                    <h4 className="font-medium text-white">Usage Analytics</h4>
                    <p className="text-sm text-gray-400">Help improve the app with anonymous usage data</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.privacy.analytics_enabled}
                      onChange={(e) => updatePrivacy({ analytics_enabled: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                  </label>
                </div>

                <div className="space-y-3">
                  <button className="w-full py-2 px-4 bg-blue-500 hover:bg-blue-600 rounded-lg transition-all text-white font-medium">
                    Change Password
                  </button>
                  <button className="w-full py-2 px-4 bg-white bg-opacity-10 hover:bg-opacity-20 rounded-lg transition-all text-white border border-white border-opacity-20">
                    Export My Data
                  </button>
                  <button className="w-full py-2 px-4 bg-red-500 hover:bg-red-600 rounded-lg transition-all text-white font-medium">
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'subscription' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Subscription & Billing</h3>
              <div className="space-y-4">
                <div className="p-4 bg-white bg-opacity-5 rounded-lg border border-white border-opacity-10">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-white">Current Plan</h4>
                    <span className="px-3 py-1 bg-blue-500 bg-opacity-20 text-blue-300 rounded-full text-sm font-medium">
                      {user.subscription_tier === 'founder_plus' ? 'Founder+' : 'Explorer'}
                    </span>
                  </div>
                  <p className="text-gray-400 mb-4">
                    {user.subscription_tier === 'founder_plus' 
                      ? 'Advanced relationship intelligence with unlimited contacts and AI features.'
                      : 'Basic plan with limited contacts and essential features.'
                    }
                  </p>
                  {user.subscription_tier === 'explorer' && (
                    <button className="w-full py-2 px-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-lg transition-all text-white font-medium">
                      Upgrade to Founder+
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-white bg-opacity-5 rounded-lg">
                    <h4 className="font-medium text-white mb-2">Usage This Month</h4>
                    <div className="space-y-2 text-sm text-gray-300">
                      <div className="flex justify-between">
                        <span>Contacts</span>
                        <span>42 / {user.subscription_tier === 'founder_plus' ? '∞' : '100'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>AI Suggestions</span>
                        <span>127 / {user.subscription_tier === 'founder_plus' ? '∞' : '50'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Trust Insights</span>
                        <span>{user.subscription_tier === 'founder_plus' ? 'Unlimited' : 'Limited'}</span>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-white bg-opacity-5 rounded-lg">
                    <h4 className="font-medium text-white mb-2">Billing</h4>
                    <div className="space-y-2 text-sm text-gray-300">
                      <div className="flex justify-between">
                        <span>Next billing date</span>
                        <span>Jan 15, 2025</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Amount</span>
                        <span>${user.subscription_tier === 'founder_plus' ? '19.00' : '0.00'}</span>
                      </div>
                    </div>
                    <button className="w-full mt-3 py-2 px-4 bg-white bg-opacity-10 hover:bg-opacity-20 rounded-lg transition-all text-white text-sm border border-white border-opacity-20">
                      Manage Billing
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsPanel;