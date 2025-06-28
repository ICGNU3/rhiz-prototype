/**
 * Enhanced Contact Import Modal with multiple sync options
 */

import React, { useState, useRef } from 'react';
import type { ContactImportSource } from '../../types';

interface ContactImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportComplete: (imported: number, source: string) => void;
}

const ContactImportModal: React.FC<ContactImportModalProps> = ({
  isOpen,
  onClose,
  onImportComplete
}) => {
  const [activeTab, setActiveTab] = useState<'google' | 'linkedin' | 'csv'>('google');
  const [isImporting, setIsImporting] = useState(false);
  const [importStatus, setImportStatus] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const importSources: ContactImportSource[] = [
    {
      id: 'google',
      name: 'Google Contacts',
      icon: '📧',
      description: 'Sync contacts from your Google account',
      status: 'available'
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      icon: '💼',
      description: 'Upload LinkedIn connections CSV',
      status: 'available'
    },
    {
      id: 'icloud',
      name: 'iCloud/CSV',
      icon: '📱',
      description: 'Import contacts from CSV file',
      status: 'available'
    }
  ];

  const handleGoogleImport = async () => {
    setIsImporting(true);
    setImportStatus('Connecting to Google...');
    
    try {
      // Get Google OAuth URL
      const response = await fetch('/api/contacts/sync/google/auth', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const { auth_url } = await response.json();
        window.open(auth_url, 'google-auth', 'width=500,height=600');
        
        // Listen for auth completion
        const handleMessage = (event: MessageEvent) => {
          if (event.data.type === 'google-auth-complete') {
            window.removeEventListener('message', handleMessage);
            initiateGoogleSync();
          }
        };
        
        window.addEventListener('message', handleMessage);
        setImportStatus('Complete authorization in the popup window...');
      }
    } catch (error) {
      setImportStatus('Failed to connect to Google. Please try again.');
      setIsImporting(false);
    }
  };

  const initiateGoogleSync = async () => {
    setImportStatus('Syncing contacts from Google...');
    
    try {
      const response = await fetch('/api/contacts/sync/google', {
        method: 'POST',
        credentials: 'include'
      });
      
      if (response.ok) {
        const result = await response.json();
        setImportStatus(`Successfully imported ${result.imported} contacts!`);
        onImportComplete(result.imported, 'Google');
        setTimeout(() => onClose(), 2000);
      }
    } catch (error) {
      setImportStatus('Sync failed. Please try again.');
    } finally {
      setIsImporting(false);
    }
  };

  const handleFileImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    setImportStatus('Processing file...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const endpoint = activeTab === 'linkedin' 
        ? '/api/contacts/import/linkedin'
        : '/api/contacts/import/csv';

      const response = await fetch(endpoint, {
        method: 'POST',
        credentials: 'include',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setImportStatus(`Successfully imported ${result.imported} contacts! ${result.skipped} duplicates skipped.`);
        onImportComplete(result.imported, activeTab === 'linkedin' ? 'LinkedIn' : 'CSV');
        setTimeout(() => onClose(), 2000);
      } else {
        const error = await response.json();
        setImportStatus(`Import failed: ${error.error}`);
      }
    } catch (error) {
      setImportStatus('Import failed. Please check your file format.');
    } finally {
      setIsImporting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="glass-card p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold gradient-text">Import Contacts</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
            disabled={isImporting}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Import Source Tabs */}
        <div className="flex space-x-1 mb-6 bg-white bg-opacity-5 rounded-lg p-1">
          {importSources.map((source) => (
            <button
              key={source.id}
              onClick={() => setActiveTab(source.id as any)}
              className={`flex-1 py-2 px-4 rounded-md transition-all ${
                activeTab === source.id
                  ? 'bg-white bg-opacity-10 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
              disabled={isImporting}
            >
              <div className="text-center">
                <div className="text-lg mb-1">{source.icon}</div>
                <div className="text-sm font-medium">{source.name}</div>
              </div>
            </button>
          ))}
        </div>

        {/* Import Content */}
        <div className="space-y-6">
          {activeTab === 'google' && (
            <div className="text-center">
              <div className="mb-4">
                <div className="text-4xl mb-2">📧</div>
                <h3 className="text-lg font-semibold mb-2">Sync Google Contacts</h3>
                <p className="text-gray-400 mb-4">
                  Securely connect your Google account to import all your contacts with one click.
                </p>
              </div>
              
              <button
                onClick={handleGoogleImport}
                disabled={isImporting}
                className="btn btn-primary px-8 py-3"
              >
                {isImporting ? (
                  <>
                    <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                    Connecting...
                  </>
                ) : (
                  'Connect Google Account'
                )}
              </button>
            </div>
          )}

          {activeTab === 'linkedin' && (
            <div className="text-center">
              <div className="mb-4">
                <div className="text-4xl mb-2">💼</div>
                <h3 className="text-lg font-semibold mb-2">Upload LinkedIn Connections</h3>
                <p className="text-gray-400 mb-4">
                  Export your LinkedIn connections as CSV and upload here.
                </p>
              </div>

              <div className="space-y-4">
                <div className="bg-blue-500 bg-opacity-10 border border-blue-500 border-opacity-30 rounded-lg p-4 mb-4">
                  <h4 className="font-semibold mb-2 text-blue-300">How to export from LinkedIn:</h4>
                  <ol className="text-sm text-gray-300 space-y-1 text-left">
                    <li>1. Go to LinkedIn Settings & Privacy</li>
                    <li>2. Click "Data Privacy" → "Get a copy of your data"</li>
                    <li>3. Select "Connections" and download</li>
                    <li>4. Upload the CSV file here</li>
                  </ol>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={handleFileImport}
                  disabled={isImporting}
                  className="hidden"
                />
                
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isImporting}
                  className="btn btn-primary px-8 py-3"
                >
                  {isImporting ? 'Processing...' : 'Choose CSV File'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'csv' && (
            <div className="text-center">
              <div className="mb-4">
                <div className="text-4xl mb-2">📱</div>
                <h3 className="text-lg font-semibold mb-2">Upload CSV File</h3>
                <p className="text-gray-400 mb-4">
                  Import contacts from any CSV file. Supports various formats including iCloud exports.
                </p>
              </div>

              <div className="space-y-4">
                <div className="bg-green-500 bg-opacity-10 border border-green-500 border-opacity-30 rounded-lg p-4 mb-4">
                  <h4 className="font-semibold mb-2 text-green-300">Supported CSV columns:</h4>
                  <div className="text-sm text-gray-300 grid grid-cols-2 gap-2 text-left">
                    <div>• Name / Full Name</div>
                    <div>• Email</div>
                    <div>• Phone / Mobile</div>
                    <div>• Company / Organization</div>
                    <div>• Title / Job Title</div>
                    <div>• Notes</div>
                  </div>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={handleFileImport}
                  disabled={isImporting}
                  className="hidden"
                />
                
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isImporting}
                  className="btn btn-primary px-8 py-3"
                >
                  {isImporting ? 'Processing...' : 'Choose CSV File'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Import Status */}
        {importStatus && (
          <div className="mt-6 p-4 bg-white bg-opacity-10 rounded-lg">
            <div className="flex items-center space-x-2">
              {isImporting && (
                <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
              )}
              <span className="text-sm">{importStatus}</span>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-white border-opacity-10">
          <p className="text-xs text-gray-400 text-center">
            <svg className="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
            </svg>
            Your data is processed securely and never stored on external servers.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ContactImportModal;