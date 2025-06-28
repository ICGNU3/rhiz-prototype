import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface LoginProps {
  onSuccess?: () => void;
}

const Login: React.FC<LoginProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    try {
      const response = await fetch('/api/auth/magic-link', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const result = await response.json();

      if (response.ok) {
        setMessage({
          type: 'success',
          text: result.message || 'Magic link sent! Check your email.'
        });
        setEmail('');
        
        // Auto-redirect to demo after 3 seconds
        setTimeout(() => {
          handleDemoLogin();
        }, 3000);
      } else {
        setMessage({
          type: 'error',
          text: result.error || 'Failed to send magic link'
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Network error. Please try again.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    try {
      const response = await fetch('/demo-login', {
        method: 'GET',
        credentials: 'include'
      });

      if (response.ok) {
        if (onSuccess) {
          onSuccess();
        } else {
          navigate('/app/dashboard');
        }
      } else {
        setMessage({
          type: 'error',
          text: 'Demo login failed. Please try again.'
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Demo login error. Please try again.'
      });
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center position-relative">
      {/* Background Orbs */}
      <div className="background-orbs">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-6 col-lg-4">
            <div className="glass-card p-5">
              <div className="text-center mb-4">
                <div className="brand-logo mb-3">
                  <span className="gradient-text h2 fw-bold">Rhiz</span>
                </div>
                <h3 className="mb-2 gradient-text">Welcome Back</h3>
                <p className="text-muted">Enter your email to receive a magic link</p>
              </div>

              {/* Flash Messages */}
              {message && (
                <div className={`alert alert-${message.type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`} role="alert">
                  <i className={`bi bi-${message.type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2`}></i>
                  {message.text}
                  <button 
                    type="button" 
                    className="btn-close" 
                    onClick={() => setMessage(null)}
                    aria-label="Close"
                  ></button>
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="email" className="form-label">Email Address</label>
                  <input
                    type="email"
                    className="form-control"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="founder@example.com"
                    style={{
                      background: 'rgba(255,255,255,0.05)',
                      border: '1px solid rgba(255,255,255,0.1)'
                    }}
                  />
                </div>
                
                <button
                  type="submit"
                  className="btn btn-primary w-100 mb-3 position-relative overflow-hidden"
                  disabled={isLoading}
                >
                  <span className="position-relative z-index-1">
                    <i className={`bi bi-${isLoading ? 'hourglass' : 'envelope'} me-2`}></i>
                    {isLoading ? 'Sending...' : 'Send Magic Link'}
                  </span>
                </button>
              </form>

              <div className="text-center mb-3">
                <div className="small text-muted mb-2">or</div>
                <button
                  onClick={handleDemoLogin}
                  className="btn btn-glass btn-sm"
                  disabled={isLoading}
                >
                  <i className="bi bi-play-circle me-2"></i>Quick Demo Access
                </button>
              </div>

              <div className="text-center">
                <p className="small text-muted mb-2">Don't have an account?</p>
                <button
                  onClick={() => navigate('/')}
                  className="btn btn-glass btn-sm"
                >
                  <i className="bi bi-person-plus me-1"></i>Join Rhiz
                </button>
              </div>

              <div className="text-center mt-4">
                <small className="text-muted">
                  <i className="bi bi-shield-check me-1"></i>
                  Secure passwordless authentication
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;