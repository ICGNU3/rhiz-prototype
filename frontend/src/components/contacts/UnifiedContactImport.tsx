import React, { useState, useRef, useCallback } from 'react';
import Papa from 'papaparse';
import { useMutation } from '@tanstack/react-query';
import type { Contact } from '../../types/api';

interface UnifiedContactImportProps {
  isModal?: boolean;
  isOnboarding?: boolean;
  onImportComplete?: (contacts: Contact[], source: string) => void;
  onClose?: () => void;
  className?: string;
}

type ImportSource = 'google' | 'linkedin' | 'apple' | 'csv' | 'manual';

interface ImportProgress {
  percentage: number;
  text: string;
  details: string;
  isActive: boolean;
}

const IMPORT_SOURCES = [
  {
    id: 'google' as ImportSource,
    name: 'Google Contacts',
    description: 'Secure OAuth integration',
    icon: 'bi-google',
    color: 'text-danger',
    available: true
  },
  {
    id: 'linkedin' as ImportSource,
    name: 'LinkedIn',
    description: 'Smart scraper + CSV upload',
    icon: 'bi-linkedin',
    color: 'text-primary',
    available: true
  },
  {
    id: 'apple' as ImportSource,
    name: 'Apple/iCloud',
    description: 'VCF/CSV export upload',
    icon: 'bi-apple',
    color: 'text-light',
    available: true
  },
  {
    id: 'csv' as ImportSource,
    name: 'CSV Upload',
    description: 'Import from any CSV file',
    icon: 'bi-file-earmark-spreadsheet',
    color: 'text-success',
    available: true
  },
  {
    id: 'manual' as ImportSource,
    name: 'Manual Entry',
    description: 'Add contacts one by one',
    icon: 'bi-person-plus',
    color: 'text-info',
    available: true
  }
];

export default function UnifiedContactImport({
  isModal = false,
  isOnboarding = false,
  onImportComplete,
  onClose,
  className = ''
}: UnifiedContactImportProps) {
  const [selectedSource, setSelectedSource] = useState<ImportSource | null>(null);
  const [progress, setProgress] = useState<ImportProgress>({
    percentage: 0,
    text: '',
    details: '',
    isActive: false
  });
  const [importedContacts, setImportedContacts] = useState<Contact[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const updateProgress = useCallback((percentage: number, text: string, details: string) => {
    setProgress({ percentage, text, details, isActive: true });
  }, []);

  const resetProgress = useCallback(() => {
    setProgress({ percentage: 0, text: '', details: '', isActive: false });
  }, []);

  const handleSourceSelect = async (source: ImportSource) => {
    setSelectedSource(source);
    
    switch (source) {
      case 'google':
        await handleGoogleImport();
        break;
      case 'linkedin':
        await handleLinkedInImport();
        break;
      case 'apple':
        await handleAppleImport();
        break;
      case 'csv':
        handleCSVUpload();
        break;
      case 'manual':
        handleManualEntry();
        break;
    }
  };

  const handleGoogleImport = async () => {
    updateProgress(10, 'Connecting to Google...', 'Opening secure OAuth window');
    
    try {
      const response = await fetch('/api/contacts/oauth-url/google');
      if (response.ok) {
        const { oauth_url } = await response.json();
        
        // Open OAuth popup
        const popup = window.open(oauth_url, 'google-oauth', 'width=500,height=600');
        
        const checkOAuth = setInterval(async () => {
          try {
            if (popup?.closed) {
              clearInterval(checkOAuth);
              updateProgress(50, 'Fetching contacts...', 'Downloading your Google contacts');
              
              const contactsResponse = await fetch('/api/contacts/sync', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source: 'google' })
              });
              
              if (contactsResponse.ok) {
                const data = await contactsResponse.json();
                updateProgress(100, 'Import complete!', `Successfully imported ${data.contacts.length} contacts`);
                setImportedContacts(data.contacts);
                
                setTimeout(() => {
                  resetProgress();
                  onImportComplete?.(data.contacts, 'google');
                }, 1500);
              }
            }
          } catch (error) {
            clearInterval(checkOAuth);
            resetProgress();
            alert('Google import failed. Please try again.');
          }
        }, 1000);
      }
    } catch (error) {
      resetProgress();
      alert('Google import failed. Please try again.');
    }
  };

  const handleLinkedInImport = async () => {
    // Redirect to LinkedIn scraper interface
    window.location.href = '/linkedin-scraper';
  };

  const handleAppleImport = () => {
    // Trigger file upload for Apple/iCloud
    if (fileInputRef.current) {
      fileInputRef.current.accept = '.vcf,.csv';
      fileInputRef.current.click();
    }
  };

  // React Query mutation for contact upload
  const uploadContactsMutation = useMutation({
    mutationFn: async ({ contacts, source }: { contacts: any[], source: string }) => {
      const response = await fetch('/api/contacts/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ contacts, source })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Upload failed');
      }

      return response.json();
    },
    onSuccess: (data) => {
      updateProgress(100, 'Import complete!', `Successfully imported ${data.contacts_imported} contacts`);
      
      setTimeout(() => {
        resetProgress();
        onImportComplete?.(data.contacts, selectedSource!);
      }, 1500);
    },
    onError: (error: Error) => {
      resetProgress();
      alert(`Upload failed: ${error.message}`);
    }
  });

  const handleCSVUpload = () => {
    if (fileInputRef.current) {
      fileInputRef.current.accept = '.csv';
      fileInputRef.current.click();
    }
  };

  const handleManualEntry = () => {
    // Open manual contact entry form
    window.location.href = '/contacts?action=add';
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    updateProgress(10, 'Reading file...', 'Processing your CSV file');

    try {
      if (file.name.toLowerCase().endsWith('.csv')) {
        // Use papaparse to parse CSV
        Papa.parse(file, {
          header: true,
          skipEmptyLines: true,
          complete: (results) => {
            updateProgress(50, 'Parsing contacts...', `Found ${results.data.length} potential contacts`);
            
            // Map CSV data to contact format
            const contacts = results.data.map((row: any) => {
              // Handle various CSV formats
              const contact: any = {};
              
              // Try to map common field names
              Object.keys(row).forEach(key => {
                const value = row[key]?.trim();
                if (!value) return;
                
                const lowerKey = key.toLowerCase();
                
                if (lowerKey.includes('first') && lowerKey.includes('name')) {
                  contact.first_name = value;
                } else if (lowerKey.includes('last') && lowerKey.includes('name')) {
                  contact.last_name = value;
                } else if (lowerKey === 'name' || lowerKey === 'full name') {
                  const nameParts = value.split(' ');
                  contact.first_name = nameParts[0];
                  if (nameParts.length > 1) {
                    contact.last_name = nameParts.slice(1).join(' ');
                  }
                } else if (lowerKey.includes('email')) {
                  contact.email = value;
                } else if (lowerKey.includes('phone')) {
                  contact.phone = value;
                } else if (lowerKey.includes('company') || lowerKey.includes('organization')) {
                  contact.company = value;
                } else if (lowerKey.includes('title') || lowerKey.includes('position')) {
                  contact.title = value;
                } else if (lowerKey.includes('note')) {
                  contact.notes = value;
                }
              });
              
              return contact;
            }).filter(contact => 
              // Only include contacts with at least a name or email
              contact.first_name || contact.email
            );

            updateProgress(75, 'Uploading contacts...', `Uploading ${contacts.length} valid contacts`);
            
            // Upload via React Query mutation
            uploadContactsMutation.mutate({
              contacts,
              source: selectedSource === 'apple' ? 'apple' : 'csv'
            });
          },
          error: (error) => {
            resetProgress();
            alert('Failed to parse CSV file. Please check the file format.');
          }
        });
      } else if (file.name.toLowerCase().endsWith('.vcf')) {
        // Handle VCF files with FormData (legacy approach)
        const formData = new FormData();
        formData.append('file', file);
        formData.append('source', 'apple');

        updateProgress(50, 'Uploading file...', 'Processing VCF file');

        const response = await fetch('/api/contacts/upload', {
          method: 'POST',
          credentials: 'include',
          body: formData
        });

        if (response.ok) {
          const data = await response.json();
          updateProgress(100, 'Import complete!', `Successfully imported ${data.contacts_imported} contacts`);
          
          setTimeout(() => {
            resetProgress();
            onImportComplete?.(data.contacts || [], 'apple');
          }, 1500);
        } else {
          throw new Error('VCF import failed');
        }
      } else {
        throw new Error('Unsupported file type');
      }
    } catch (error) {
      resetProgress();
      alert('File import failed. Please check your file format and try again.');
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const containerClass = isModal 
    ? 'modal-dialog modal-lg modal-dialog-centered'
    : isOnboarding 
    ? 'container-fluid'
    : 'container';

  const cardClass = isModal
    ? 'modal-content'
    : 'glass-card p-4';

  const content = (
    <div className={cardClass}>
      {isModal && (
        <div className="modal-header border-0">
          <h5 className="modal-title text-gradient">Import Contacts</h5>
          <button type="button" className="btn-close" onClick={onClose}></button>
        </div>
      )}
      
      <div className={isModal ? 'modal-body' : ''}>
        {!isOnboarding && (
          <div className="text-center mb-4">
            <i className="bi bi-person-plus-fill text-primary mb-3" style={{ fontSize: '2.5rem' }} />
            <h3 className="text-gradient mb-2">Import Your Contacts</h3>
            <p className="text-muted">Choose your preferred method to import existing contacts</p>
          </div>
        )}

        {/* Import Sources Grid */}
        <div 
          className="import-sources-grid mb-4"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem'
          }}
        >
          {IMPORT_SOURCES.map((source) => (
            <div
              key={source.id}
              className={`import-source-card p-3 rounded text-center cursor-pointer ${
                selectedSource === source.id ? 'selected' : ''
              }`}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '2px solid rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                transition: 'all 0.3s ease',
                cursor: source.available ? 'pointer' : 'not-allowed',
                opacity: source.available ? 1 : 0.6
              }}
              onClick={() => source.available && !progress.isActive && handleSourceSelect(source.id)}
              onMouseEnter={(e) => {
                if (source.available && !progress.isActive) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                  e.currentTarget.style.borderColor = '#007bff';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div className="mb-2" style={{ fontSize: '2rem' }}>
                <i className={`${source.icon} ${source.color}`} />
              </div>
              <h6 className="text-white mb-1">{source.name}</h6>
              <small className="text-muted">{source.description}</small>
              {!source.available && (
                <div className="mt-1">
                  <small className="text-warning">Coming Soon</small>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Progress Bar */}
        {progress.isActive && (
          <div className="progress-section mb-4">
            <div className="progress mb-3" style={{ height: '20px' }}>
              <div 
                className="progress-bar bg-primary progress-bar-striped progress-bar-animated" 
                style={{ width: `${progress.percentage}%` }}
              />
            </div>
            <div className="text-center">
              <div className="fw-bold text-light">{progress.text}</div>
              <small className="text-muted">{progress.details}</small>
            </div>
          </div>
        )}

        {/* Import Tips */}
        {!progress.isActive && (
          <div className="import-tips">
            <div className="row">
              <div className="col-md-6">
                <div className="tip-card p-3 rounded" style={{ background: 'rgba(0, 123, 255, 0.1)' }}>
                  <h6 className="text-primary mb-2">
                    <i className="bi bi-lightbulb me-2" />
                    Quick Tip
                  </h6>
                  <small className="text-light">
                    Google Contacts provides the most comprehensive data including photos and detailed contact information.
                  </small>
                </div>
              </div>
              <div className="col-md-6">
                <div className="tip-card p-3 rounded" style={{ background: 'rgba(40, 167, 69, 0.1)' }}>
                  <h6 className="text-success mb-2">
                    <i className="bi bi-shield-check me-2" />
                    Privacy
                  </h6>
                  <small className="text-light">
                    All imports are secure and encrypted. We never store your login credentials.
                  </small>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {isModal && (
        <div className="modal-footer border-0">
          <button type="button" className="btn btn-outline-secondary" onClick={onClose}>
            Cancel
          </button>
        </div>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        style={{ display: 'none' }}
        onChange={handleFileUpload}
      />
    </div>
  );

  if (isModal) {
    return (
      <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
        <div className={containerClass}>
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className={`${containerClass} ${className}`}>
      {content}
    </div>
  );
}

// CSS for styling (to be added to global styles)
const styles = `
.import-source-card.selected {
  background: rgba(0, 123, 255, 0.2) !important;
  border-color: #007bff !important;
}

.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}

.text-gradient {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.cursor-pointer {
  cursor: pointer;
}
`;

// Export styles for use in CSS file
export { styles as UnifiedContactImportStyles };