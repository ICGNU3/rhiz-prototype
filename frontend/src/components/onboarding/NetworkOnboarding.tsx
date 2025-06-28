import React, { useState, useEffect } from 'react';
import type { Contact, ContactClassification, TrustScore } from '../../types/api';

interface NetworkOnboardingProps {
  onComplete: (data: NetworkOnboardingData) => void;
  onBack: () => void;
}

interface NetworkOnboardingData {
  contacts: Contact[];
  classifications: Record<string, ContactClassification>;
  trustScores: Record<string, TrustScore>;
  completedSections: string[];
}

interface ContactClassification {
  type: string;
  sentiment: 'positive' | 'neutral' | 'negative';
}

interface ImportProgress {
  percentage: number;
  text: string;
  details: string;
}

type ImportSource = 'google' | 'linkedin' | 'apple' | 'twitter' | 'manual' | 'skip';
type OnboardingSection = 'import' | 'classification' | 'unknown' | 'enrichment' | 'trust' | 'syncSetup' | 'warmup' | 'completion';

const SECTIONS: OnboardingSection[] = ['import', 'classification', 'unknown', 'enrichment', 'trust', 'syncSetup', 'warmup', 'completion'];

const RELATIONSHIP_TYPES = [
  { value: 'friend', label: '👥 Friend', color: 'primary' },
  { value: 'family', label: '👨‍👩‍👧‍👦 Family', color: 'success' },
  { value: 'colleague', label: '💼 Colleague', color: 'info' },
  { value: 'professional', label: '🤝 Professional', color: 'secondary' },
  { value: 'investor', label: '💰 Investor', color: 'warning' },
  { value: 'mentor', label: '🎓 Mentor', color: 'info' },
  { value: 'client', label: '🎯 Client', color: 'success' },
  { value: 'vendor', label: '🛍️ Vendor', color: 'secondary' },
  { value: 'other', label: '❓ Other', color: 'secondary' }
];

export default function NetworkOnboarding({ onComplete, onBack }: NetworkOnboardingProps) {
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [importedContacts, setImportedContacts] = useState<Contact[]>([]);
  const [classifications, setClassifications] = useState<Record<string, ContactClassification>>({});
  const [trustScores, setTrustScores] = useState<Record<string, TrustScore>>({});
  const [selectedContacts, setSelectedContacts] = useState<Set<string>>(new Set());
  const [importProgress, setImportProgress] = useState<ImportProgress | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const currentSection = SECTIONS[currentSectionIndex];

  useEffect(() => {
    loadExistingContacts();
  }, []);

  const loadExistingContacts = async () => {
    try {
      const response = await fetch('/api/contacts');
      if (response.ok) {
        const data = await response.json();
        if (data.contacts && data.contacts.length > 0) {
          setImportedContacts(data.contacts);
          // Skip import section if we have contacts
          setCurrentSectionIndex(1);
        }
      }
    } catch (error) {
      console.log('No existing contacts found, starting fresh');
    }
  };

  const selectImportSource = (source: ImportSource) => {
    switch (source) {
      case 'google':
        initiateGoogleImport();
        break;
      case 'linkedin':
        initiateLinkedInImport();
        break;
      case 'apple':
        initiateAppleImport();
        break;
      case 'twitter':
        showTwitterNotAvailable();
        break;
      case 'manual':
        showManualAddForm();
        break;
      case 'skip':
        skipImport();
        break;
    }
  };

  const initiateGoogleImport = async () => {
    setImportProgress({ percentage: 10, text: 'Connecting to Google...', details: 'Opening secure OAuth window' });
    setIsProcessing(true);

    try {
      // Real Google OAuth integration
      const response = await fetch('/api/oauth/google');
      if (response.ok) {
        const { oauth_url } = await response.json();
        
        // Open OAuth popup
        const popup = window.open(oauth_url, 'google-oauth', 'width=500,height=600');
        
        // Wait for OAuth completion
        const checkOAuth = setInterval(async () => {
          try {
            if (popup?.closed) {
              clearInterval(checkOAuth);
              setImportProgress({ percentage: 50, text: 'Fetching contacts...', details: 'Downloading your Google contacts' });
              
              const contactsResponse = await fetch('/api/sync/google');
              if (contactsResponse.ok) {
                const contactsData = await contactsResponse.json();
                setImportProgress({ percentage: 100, text: 'Import complete!', details: `Successfully imported ${contactsData.contacts.length} contacts` });
                setImportedContacts(contactsData.contacts);
                
                setTimeout(() => {
                  setImportProgress(null);
                  setIsProcessing(false);
                  nextSection();
                }, 1500);
              }
            }
          } catch (error) {
            clearInterval(checkOAuth);
            setImportProgress(null);
            setIsProcessing(false);
            alert('Google import failed. Please try again.');
          }
        }, 1000);
      }
    } catch (error) {
      setImportProgress(null);
      setIsProcessing(false);
      alert('Google import failed. Please try again or use CSV upload.');
    }
  };

  const initiateLinkedInImport = async () => {
    window.location.href = '/linkedin-scraper';
  };

  const initiateAppleImport = async () => {
    // Trigger file upload for Apple/iCloud CSV
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv,.vcf';
    input.onchange = async (event) => {
      const file = (event.target as HTMLInputElement).files?.[0];
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('source', 'apple');
        
        setImportProgress({ percentage: 20, text: 'Uploading file...', details: 'Processing your Apple/iCloud contacts' });
        setIsProcessing(true);
        
        try {
          const response = await fetch('/api/import/csv', {
            method: 'POST',
            body: formData
          });
          
          if (response.ok) {
            const data = await response.json();
            setImportProgress({ percentage: 100, text: 'Import complete!', details: `Successfully imported ${data.contacts.length} contacts` });
            setImportedContacts(data.contacts);
            
            setTimeout(() => {
              setImportProgress(null);
              setIsProcessing(false);
              nextSection();
            }, 1500);
          }
        } catch (error) {
          setImportProgress(null);
          setIsProcessing(false);
          alert('Apple import failed. Please check your file format.');
        }
      }
    };
    input.click();
  };

  const showTwitterNotAvailable = () => {
    alert('Twitter/X import is coming soon! For now, you can add contacts manually or use other import methods.');
  };

  const showManualAddForm = () => {
    // For now, redirect to manual add page
    window.location.href = '/contacts?action=add';
  };

  const skipImport = () => {
    if (confirm('Are you sure you want to skip importing contacts? You can always add them later.')) {
      nextSection();
    }
  };

  const updateContactClassification = (contactIndex: number, type: string) => {
    setClassifications(prev => ({
      ...prev,
      [contactIndex]: {
        ...prev[contactIndex],
        type
      }
    }));
  };

  const setSentiment = (contactIndex: number, sentiment: 'positive' | 'neutral' | 'negative') => {
    setClassifications(prev => ({
      ...prev,
      [contactIndex]: {
        ...prev[contactIndex],
        sentiment
      }
    }));
  };

  const updateTrustScore = (contactIndex: number, score: number) => {
    setTrustScores(prev => ({
      ...prev,
      [contactIndex]: score
    }));
  };

  const batchTag = (type: string) => {
    selectedContacts.forEach(contactId => {
      const index = parseInt(contactId);
      updateContactClassification(index, type);
    });
  };

  const toggleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedContacts(new Set(importedContacts.map((_, index) => index.toString())));
    } else {
      setSelectedContacts(new Set());
    }
  };

  const nextSection = () => {
    if (currentSectionIndex < SECTIONS.length - 1) {
      setCurrentSectionIndex(prev => prev + 1);
    }
  };

  const prevSection = () => {
    if (currentSectionIndex > 0) {
      setCurrentSectionIndex(prev => prev - 1);
    } else {
      onBack();
    }
  };

  const skipSection = () => {
    nextSection();
  };

  const completeOnboarding = async () => {
    const networkData: NetworkOnboardingData = {
      contacts: importedContacts,
      classifications,
      trustScores,
      completedSections: SECTIONS.slice(0, currentSectionIndex + 1)
    };

    try {
      const response = await fetch('/api/onboarding/network', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(networkData)
      });

      if (response.ok) {
        onComplete(networkData);
      } else {
        throw new Error('Failed to save network data');
      }
    } catch (error) {
      console.error('Failed to save network data:', error);
      alert('Failed to save network data. Please try again.');
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center position-relative">
      {/* Background Gradient */}
      <div 
        className="position-absolute w-100 h-100"
        style={{
          background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)',
          zIndex: -2
        }}
      />

      {/* Background Orbs */}
      <div 
        className="position-absolute rounded-circle"
        style={{
          width: '500px',
          height: '500px',
          background: 'radial-gradient(circle, rgba(0, 123, 255, 0.1) 0%, rgba(0, 123, 255, 0.05) 40%, transparent 70%)',
          filter: 'blur(40px)',
          animation: 'float 20s ease-in-out infinite',
          top: '10%',
          left: '10%',
          zIndex: -1
        }}
      />

      <div className="container-fluid py-5">
        <div className="row justify-content-center">
          <div className="col-xl-10 col-lg-11">
            <div 
              className="p-5 rounded"
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}
            >
              {/* Header */}
              <div className="text-center mb-5">
                <div className="mb-4">
                  <i className="bi bi-diagram-3 text-primary mb-3" style={{ fontSize: '3rem' }} />
                  <h1 className="display-5 fw-bold mb-3" style={{ 
                    background: 'linear-gradient(135deg, #007bff 0%, #0056b3 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent'
                  }}>
                    Build Your Living Network
                  </h1>
                  <p className="lead text-light mb-0">Transform your contact list into intelligent relationship insights</p>
                </div>
                
                {/* Progress indicator */}
                <div className="mx-auto mb-4" style={{ maxWidth: '400px' }}>
                  <div className="progress" style={{ height: '8px', background: 'rgba(255,255,255,0.1)' }}>
                    <div 
                      className="progress-bar bg-primary" 
                      style={{ 
                        width: `${((currentSectionIndex + 1) / SECTIONS.length) * 100}%`,
                        transition: 'width 0.5s ease'
                      }}
                    />
                  </div>
                  <small className="text-muted mt-2 d-block">Step 3 of 4: Network Mapping</small>
                </div>
              </div>

              {/* Import Section */}
              {currentSection === 'import' && (
                <div className="row">
                  <div className="col-lg-8 mx-auto">
                    <div className="text-center mb-4">
                      <h3 className="text-primary">Import Your Contacts</h3>
                      <p className="text-light">Choose your preferred method to import existing contacts</p>
                    </div>
                    
                    <div 
                      style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                        gap: '1.5rem',
                        marginBottom: '2rem'
                      }}
                    >
                      {[
                        { source: 'google' as ImportSource, icon: 'bi-google', name: 'Google Contacts', desc: 'Secure OAuth integration', color: 'text-danger' },
                        { source: 'linkedin' as ImportSource, icon: 'bi-linkedin', name: 'LinkedIn', desc: 'Smart scraper + CSV upload', color: 'text-primary' },
                        { source: 'apple' as ImportSource, icon: 'bi-apple', name: 'Apple/iCloud', desc: 'CSV export upload', color: 'text-light' },
                        { source: 'twitter' as ImportSource, icon: 'bi-twitter-x', name: 'Twitter/X', desc: '@handle input', color: 'text-light', badge: 'Coming soon' },
                        { source: 'manual' as ImportSource, icon: 'bi-person-plus', name: 'Manual Add', desc: 'Add contacts one by one', color: 'text-success' },
                        { source: 'skip' as ImportSource, icon: 'bi-arrow-right', name: 'Skip for Now', desc: 'Continue without importing', color: 'text-secondary' }
                      ].map((option) => (
                        <div
                          key={option.source}
                          className="text-center p-4 rounded cursor-pointer"
                          style={{
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '2px solid rgba(255, 255, 255, 0.1)',
                            backdropFilter: 'blur(10px)',
                            transition: 'all 0.3s ease',
                            cursor: 'pointer'
                          }}
                          onClick={() => !isProcessing && selectImportSource(option.source)}
                          onMouseEnter={(e) => {
                            if (!isProcessing) {
                              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                              e.currentTarget.style.borderColor = '#007bff';
                              e.currentTarget.style.transform = 'translateY(-4px)';
                            }
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                            e.currentTarget.style.transform = 'translateY(0)';
                          }}
                        >
                          <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
                            <i className={`${option.icon} ${option.color}`} />
                          </div>
                          <h5 className="text-white mb-2">{option.name}</h5>
                          <p className="text-muted mb-0" style={{ fontSize: '0.9rem' }}>{option.desc}</p>
                          {option.badge && (
                            <small className="text-warning d-block mt-1">{option.badge}</small>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Import Progress */}
                    {importProgress && (
                      <div className="mt-4">
                        <div className="progress mb-3" style={{ height: '20px' }}>
                          <div 
                            className="progress-bar bg-primary progress-bar-striped progress-bar-animated" 
                            style={{ width: `${importProgress.percentage}%` }}
                          />
                        </div>
                        <div className="text-center">
                          <div className="fw-bold">{importProgress.text}</div>
                          <small className="text-muted">{importProgress.details}</small>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Classification Section */}
              {currentSection === 'classification' && (
                <div>
                  <div className="text-center mb-4">
                    <h3 className="text-primary">Classify Your Relationships</h3>
                    <p className="text-light">Help us understand your network by tagging relationship types</p>
                  </div>

                  {/* Batch Actions */}
                  <div 
                    className="mb-4 p-3 rounded"
                    style={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      backdropFilter: 'blur(10px)'
                    }}
                  >
                    <div className="row align-items-center">
                      <div className="col-md-6">
                        <div className="form-check">
                          <input 
                            className="form-check-input" 
                            type="checkbox" 
                            id="selectAll"
                            onChange={(e) => toggleSelectAll(e.target.checked)}
                          />
                          <label className="form-check-label text-light" htmlFor="selectAll">
                            Select All ({importedContacts.length} contacts)
                          </label>
                        </div>
                      </div>
                      <div className="col-md-6 text-end">
                        <div className="btn-group">
                          <button className="btn btn-outline-primary btn-sm" onClick={() => batchTag('friend')}>
                            <i className="bi bi-heart me-1" />Tag as Friends
                          </button>
                          <button className="btn btn-outline-success btn-sm" onClick={() => batchTag('professional')}>
                            <i className="bi bi-briefcase me-1" />Professional
                          </button>
                          <button className="btn btn-outline-warning btn-sm" onClick={() => batchTag('investor')}>
                            <i className="bi bi-currency-dollar me-1" />Investors
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Contact Grid */}
                  <div 
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                      gap: '1rem',
                      maxHeight: '500px',
                      overflowY: 'auto',
                      padding: '1rem',
                      background: 'rgba(255, 255, 255, 0.02)',
                      borderRadius: '12px'
                    }}
                  >
                    {importedContacts.map((contact, index) => (
                      <div
                        key={index}
                        className="p-3 rounded"
                        style={{
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          transition: 'all 0.3s ease'
                        }}
                      >
                        <div className="d-flex align-items-center mb-3">
                          <input 
                            type="checkbox" 
                            className="form-check-input me-3" 
                            checked={selectedContacts.has(index.toString())}
                            onChange={(e) => {
                              const newSelected = new Set(selectedContacts);
                              if (e.target.checked) {
                                newSelected.add(index.toString());
                              } else {
                                newSelected.delete(index.toString());
                              }
                              setSelectedContacts(newSelected);
                            }}
                          />
                          <div className="contact-avatar me-3">
                            <div 
                              className="rounded-circle d-flex align-items-center justify-content-center"
                              style={{ width: '40px', height: '40px', background: '#007bff', color: 'white' }}
                            >
                              {contact.name?.charAt(0) || '?'}
                            </div>
                          </div>
                          <div className="flex-grow-1">
                            <h6 className="mb-1 text-light">{contact.name || 'Unknown'}</h6>
                            <small className="text-muted">{contact.title || ''}</small>
                            {contact.company && <small className="d-block text-muted">{contact.company}</small>}
                          </div>
                        </div>
                        
                        <div>
                          <select 
                            className="form-select form-select-sm bg-dark text-light border-secondary mb-2"
                            value={classifications[index]?.type || ''}
                            onChange={(e) => updateContactClassification(index, e.target.value)}
                          >
                            <option value="">Select relationship type</option>
                            {RELATIONSHIP_TYPES.map(type => (
                              <option key={type.value} value={type.value}>{type.label}</option>
                            ))}
                          </select>
                          
                          <div>
                            <small className="text-muted d-block mb-1">Relationship sentiment:</small>
                            <div className="btn-group btn-group-sm w-100">
                              {[
                                { value: 'positive', emoji: '😊', color: 'success' },
                                { value: 'neutral', emoji: '😐', color: 'warning' },
                                { value: 'negative', emoji: '😕', color: 'danger' }
                              ].map(sentiment => (
                                <button 
                                  key={sentiment.value}
                                  type="button" 
                                  className={`btn btn-outline-${sentiment.color} ${
                                    classifications[index]?.sentiment === sentiment.value ? 'active' : ''
                                  }`}
                                  onClick={() => setSentiment(index, sentiment.value as any)}
                                >
                                  {sentiment.emoji}
                                </button>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Trust Section */}
              {currentSection === 'trust' && (
                <div>
                  <div className="text-center mb-4">
                    <h3 className="text-info">Trust Calibration</h3>
                    <p className="text-light">Rate your trust level for key relationships</p>
                  </div>

                  <div>
                    {importedContacts
                      .filter((_, index) => {
                        const classification = classifications[index];
                        return classification && ['professional', 'investor', 'mentor', 'client'].includes(classification.type);
                      })
                      .map((contact, originalIndex) => (
                        <div 
                          key={originalIndex}
                          className="mb-4 p-4 rounded"
                          style={{
                            background: 'rgba(255, 255, 255, 0.05)',
                            borderRadius: '12px'
                          }}
                        >
                          <div className="row align-items-center">
                            <div className="col-md-6">
                              <div className="d-flex align-items-center">
                                <div 
                                  className="rounded-circle d-flex align-items-center justify-content-center me-3"
                                  style={{ width: '50px', height: '50px', background: '#007bff', color: 'white' }}
                                >
                                  {contact.name?.charAt(0) || '?'}
                                </div>
                                <div>
                                  <h6 className="mb-1 text-light">{contact.name}</h6>
                                  <small className="text-muted">{contact.title || ''}</small>
                                  {contact.company && <small className="d-block text-muted">{contact.company}</small>}
                                </div>
                              </div>
                            </div>
                            <div className="col-md-6">
                              <label className="form-label text-light">Trust Level</label>
                              <input 
                                type="range" 
                                className="form-range" 
                                min="1" 
                                max="5" 
                                value={trustScores[originalIndex] || 3}
                                onChange={(e) => updateTrustScore(originalIndex, parseInt(e.target.value))}
                              />
                              <div className="d-flex justify-content-between">
                                <span className="small">😟 Low</span>
                                <span className="small">😐 Medium</span>
                                <span className="small">😊 High</span>
                              </div>
                              <div className="text-center mt-2">
                                <span 
                                  className={`badge bg-${
                                    (trustScores[originalIndex] || 3) <= 2 ? 'danger' : 
                                    (trustScores[originalIndex] || 3) <= 3 ? 'warning' : 'success'
                                  }`}
                                >
                                  {trustScores[originalIndex] || 3}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Completion Section */}
              {currentSection === 'completion' && (
                <div className="text-center">
                  <div className="mb-4">
                    <i className="bi bi-check-circle text-success mb-3" style={{ fontSize: '4rem' }} />
                    <h2 className="mb-3" style={{ 
                      background: 'linear-gradient(135deg, #007bff 0%, #0056b3 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent'
                    }}>
                      Your Network is Now Alive Inside Rhiz
                    </h2>
                    <p className="lead text-light mb-4">Let's make it meaningful.</p>
                  </div>

                  <div className="row mb-4">
                    <div className="col-md-4">
                      <div 
                        className="p-3 rounded text-center"
                        style={{
                          background: 'rgba(255, 255, 255, 0.05)',
                          backdropFilter: 'blur(10px)'
                        }}
                      >
                        <div className="h2 fw-bold text-primary">{importedContacts.length}</div>
                        <div className="text-white">Contacts Added</div>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div 
                        className="p-3 rounded text-center"
                        style={{
                          background: 'rgba(255, 255, 255, 0.05)',
                          backdropFilter: 'blur(10px)'
                        }}
                      >
                        <div className="h2 fw-bold text-primary">{Object.keys(classifications).length}</div>
                        <div className="text-white">Relationships Classified</div>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div 
                        className="p-3 rounded text-center"
                        style={{
                          background: 'rgba(255, 255, 255, 0.05)',
                          backdropFilter: 'blur(10px)'
                        }}
                      >
                        <div className="h2 fw-bold text-primary">{Object.keys(trustScores).length}</div>
                        <div className="text-white">Trust Scores Set</div>
                      </div>
                    </div>
                  </div>

                  <button 
                    className="btn btn-primary btn-lg px-5" 
                    onClick={completeOnboarding}
                    style={{
                      background: 'linear-gradient(135deg, #007bff 0%, #0056b3 100%)',
                      border: 'none'
                    }}
                  >
                    Continue to Goals <i className="bi bi-arrow-right ms-2" />
                  </button>
                </div>
              )}

              {/* Navigation Footer */}
              <div className="d-flex justify-content-between align-items-center mt-5">
                <button className="btn btn-outline-secondary" onClick={prevSection}>
                  <i className="bi bi-arrow-left me-2" />Back
                </button>
                
                <div>
                  {currentSection !== 'completion' && (
                    <>
                      <button className="btn btn-outline-light me-3" onClick={skipSection}>
                        Skip This Step
                      </button>
                      <button 
                        className="btn btn-primary" 
                        onClick={nextSection}
                        disabled={currentSection === 'import' && importedContacts.length === 0}
                      >
                        Next <i className="bi bi-arrow-right ms-2" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          33% { transform: translate(30px, -30px) rotate(120deg); }
          66% { transform: translate(-20px, 20px) rotate(240deg); }
        }
      `}</style>
    </div>
  );
}