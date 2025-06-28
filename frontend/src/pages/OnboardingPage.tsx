import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UnifiedContactImport } from '../components';
import type { Contact, Goal, User } from '../types/index';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  component: React.ComponentType<any>;
}

interface OnboardingData {
  user: Partial<User>;
  primaryGoal: Partial<Goal>;
  contacts: Contact[];
  preferences: {
    notifications: boolean;
    emailUpdates: boolean;
    dataSharing: boolean;
  };
}

const INTENT_OPTIONS = [
  { value: 'fundraising', label: '💰 Fundraising', description: 'Deepen relationships with aligned investors who share your vision' },
  { value: 'hiring', label: '👥 Hiring', description: 'Find talented people who want to build something meaningful with you' },
  { value: 'partnerships', label: '🤝 Partnerships', description: 'Cultivate strategic relationships that create mutual value' },
  { value: 'customers', label: '🎯 Customer Development', description: 'Connect with early adopters who need what you\'re building' },
  { value: 'mentorship', label: '🎓 Mentorship', description: 'Build relationships with wise guides who\'ve walked similar paths' },
  { value: 'community', label: '🌟 Community Building', description: 'Strengthen bonds within your professional community' }
];

// Step 1: Welcome & Intent Selection
function WelcomeStep({ onNext, data, setData }: any) {
  const [selectedIntent, setSelectedIntent] = useState(data.primaryGoal?.category || '');

  const handleIntentSelect = (intent: string) => {
    setSelectedIntent(intent);
    setData((prev: OnboardingData) => ({
      ...prev,
      primaryGoal: { ...prev.primaryGoal, category: intent }
    }));
  };

  return (
    <div className="text-center">
      <div className="mb-5">
        <h2 className="h3 mb-3">Welcome to Rhiz</h2>
        <p className="text-muted">Let's strengthen the relationships that matter most to what you're building</p>
      </div>

      <div className="mb-5">
        <h4 className="mb-4">What are you working on that could benefit from deeper relationships?</h4>
        <div className="row g-3">
          {INTENT_OPTIONS.map((option) => (
            <div key={option.value} className="col-md-6">
              <div 
                className={`card h-100 cursor-pointer border-2 ${
                  selectedIntent === option.value 
                    ? 'border-primary bg-primary bg-opacity-10' 
                    : 'border-secondary bg-transparent'
                }`}
                onClick={() => handleIntentSelect(option.value)}
                style={{ cursor: 'pointer' }}
              >
                <div className="card-body text-center p-4">
                  <div className="mb-2" style={{ fontSize: '2rem' }}>
                    {option.label.split(' ')[0]}
                  </div>
                  <h6 className="card-title">{option.label.substring(2)}</h6>
                  <p className="card-text small text-muted">{option.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <button 
        className="btn btn-primary btn-lg"
        onClick={onNext}
        disabled={!selectedIntent}
      >
        Continue
      </button>
    </div>
  );
}

// Step 2: Goal Details
function GoalStep({ onNext, onBack, data, setData }: any) {
  const [goal, setGoal] = useState(data.primaryGoal?.title || '');
  const [description, setDescription] = useState(data.primaryGoal?.description || '');

  const selectedIntent = INTENT_OPTIONS.find(opt => opt.value === data.primaryGoal?.category);
  
  const handleSubmit = () => {
    setData((prev: OnboardingData) => ({
      ...prev,
      primaryGoal: { 
        ...prev.primaryGoal, 
        title: goal,
        description: description 
      }
    }));
    onNext();
  };

  return (
    <div>
      <div className="text-center mb-5">
        <h3>Tell us about your {selectedIntent?.label.substring(2)} vision</h3>
        <p className="text-muted">The more specific you are, the better we can identify people who could help make this happen</p>
      </div>

      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="mb-4">
            <label className="form-label">What are you working toward?</label>
            <input 
              type="text"
              className="form-control form-control-lg"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder={`e.g., Building sustainable funding for our climate tech startup`}
            />
          </div>

          <div className="mb-5">
            <label className="form-label">Tell us more about your vision</label>
            <textarea 
              className="form-control"
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What does success look like? Who might be able to help? What kind of relationships would make the biggest difference?"
            />
          </div>

          <div className="d-flex gap-3">
            <button className="btn btn-secondary" onClick={onBack}>
              Back
            </button>
            <button 
              className="btn btn-primary flex-fill"
              onClick={handleSubmit}
              disabled={!goal.trim()}
            >
              Continue
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Step 3: Contact Import (using UnifiedContactImport)
function ContactStep({ onNext, onBack, setData }: any) {
  const handleImportComplete = (contacts: Contact[]) => {
    setData((prev: OnboardingData) => ({
      ...prev,
      contacts: contacts
    }));
    // Auto-advance after successful import
    setTimeout(() => onNext(), 1000);
  };

  return (
    <div>
      <div className="text-center mb-5">
        <h3>Bring Your Relationships Into Rhiz</h3>
        <p className="text-muted">Import your contacts so we can help you identify the people who might be most aligned with what you're building</p>
      </div>

      <UnifiedContactImport 
        isOnboarding={true}
        onImportComplete={handleImportComplete}
        className="bg-transparent"
      />

      <div className="text-center mt-4">
        <button className="btn btn-secondary me-3" onClick={onBack}>
          Back
        </button>
        <button className="btn btn-outline-primary" onClick={onNext}>
          Skip for Now
        </button>
      </div>
    </div>
  );
}

// Step 4: AI Preview & Completion
function CompletionStep({ onBack, data }: any) {
  const navigate = useNavigate();
  const [isCompleting, setIsCompleting] = useState(false);

  const completeOnboarding = async () => {
    setIsCompleting(true);
    
    try {
      // Save goal if provided
      if (data.primaryGoal?.title) {
        await fetch('/api/goals', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            title: data.primaryGoal.title,
            description: data.primaryGoal.description,
            category: data.primaryGoal.category,
            priority: 'high',
            target_date: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] // 90 days
          })
        });
      }

      // Mark onboarding complete
      await fetch('/api/onboarding/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ completed: true })
      });

      // Redirect to dashboard
      navigate('/app/dashboard?onboarding=complete');
      
    } catch (error) {
      console.error('Error completing onboarding:', error);
    } finally {
      setIsCompleting(false);
    }
  };

  return (
    <div className="text-center">
      <div className="mb-5">
        <div className="mb-4">
          <i className="bi bi-check-circle-fill text-success display-1"></i>
        </div>
        <h3>Your relationship intelligence is ready!</h3>
        <p className="text-muted">Rhiz is now analyzing your connections to identify the people who could be most valuable to what you're building.</p>
      </div>

      <div className="card bg-primary bg-opacity-10 border-primary mb-5">
        <div className="card-body">
          <h5 className="card-title">What happens next?</h5>
          <ul className="list-unstyled text-start">
            <li className="mb-2"><i className="bi bi-cpu text-primary me-2"></i> AI identifies people aligned with your vision</li>
            <li className="mb-2"><i className="bi bi-lightbulb text-warning me-2"></i> Relationship insights appear in your dashboard</li>
            <li className="mb-2"><i className="bi bi-graph-up text-success me-2"></i> Track meaningful relationship progress</li>
            <li><i className="bi bi-people text-info me-2"></i> Discover new relationships through your existing connections</li>
          </ul>
        </div>
      </div>

      <div className="d-flex gap-3 justify-content-center">
        <button className="btn btn-secondary" onClick={onBack}>
          Back
        </button>
        <button 
          className="btn btn-primary btn-lg px-5"
          onClick={completeOnboarding}
          disabled={isCompleting}
        >
          {isCompleting ? (
            <>
              <span className="spinner-border spinner-border-sm me-2"></span>
              Setting up...
            </>
          ) : (
            'Enter Your Dashboard'
          )}
        </button>
      </div>
    </div>
  );
}

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [onboardingData, setOnboardingData] = useState<OnboardingData>({
    user: {},
    primaryGoal: {},
    contacts: [],
    preferences: {
      notifications: true,
      emailUpdates: true,
      dataSharing: false
    }
  });

  const steps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Welcome',
      description: 'Set your primary intent',
      component: WelcomeStep
    },
    {
      id: 'goal',
      title: 'Goal',
      description: 'Define your objective',
      component: GoalStep
    },
    {
      id: 'contacts',
      title: 'Relationships',
      description: 'Import your contacts',
      component: ContactStep
    },
    {
      id: 'complete',
      title: 'Complete',
      description: 'Finalize setup',
      component: CompletionStep
    }
  ];

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <div className="min-vh-100 bg-dark">
      {/* Progress Header */}
      <div className="border-bottom border-secondary">
        <div className="container py-4">
          <div className="row align-items-center">
            <div className="col-md-6">
              <h1 className="h4 mb-0">Building Your Relationship Intelligence</h1>
              <p className="text-muted mb-0">Step {currentStep + 1} of {steps.length}</p>
            </div>
            <div className="col-md-6">
              <div className="progress" style={{ height: '6px' }}>
                <div 
                  className="progress-bar bg-primary"
                  style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Step Content */}
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-lg-10 col-xl-8">
            <CurrentStepComponent 
              onNext={nextStep}
              onBack={prevStep}
              data={onboardingData}
              setData={setOnboardingData}
            />
          </div>
        </div>
      </div>

      {/* Step Indicators */}
      <div className="fixed-bottom bg-dark border-top border-secondary">
        <div className="container py-3">
          <div className="d-flex justify-content-center">
            {steps.map((step, index) => (
              <div 
                key={step.id}
                className={`mx-2 ${index === currentStep ? 'text-primary' : 'text-muted'}`}
              >
                <div 
                  className={`rounded-circle d-inline-flex align-items-center justify-content-center ${
                    index === currentStep 
                      ? 'bg-primary text-white' 
                      : index < currentStep 
                        ? 'bg-success text-white'
                        : 'bg-secondary text-muted'
                  }`}
                  style={{ width: '30px', height: '30px', fontSize: '12px' }}
                >
                  {index < currentStep ? (
                    <i className="bi bi-check"></i>
                  ) : (
                    index + 1
                  )}
                </div>
                <div className="small mt-1 text-center">{step.title}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}