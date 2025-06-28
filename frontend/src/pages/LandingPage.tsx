import React from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      <style>{`
        :root {
          --bg-primary: #0A0A0F;
          --bg-secondary: #1A1A24;
          --text-primary: #F8FAFC;
          --text-secondary: #94A3B8;
          --text-accent: #E2E8F0;
          --accent-purple: #8B5CF6;
          --accent-blue: #06B6D4;
          --accent-pink: #EC4899;
          --accent-emerald: #10B981;
          --glass-bg: rgba(255, 255, 255, 0.05);
          --glass-border: rgba(255, 255, 255, 0.1);
          --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          --gradient-accent: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          --shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.3);
          --shadow-intense: 0 20px 60px rgba(0, 0, 0, 0.4);
        }
        
        * {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
          box-sizing: border-box;
        }
        
        .landing-page {
          background: var(--bg-primary);
          background-image: 
            radial-gradient(circle at 20% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(6, 182, 212, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(236, 72, 153, 0.05) 0%, transparent 50%);
          color: var(--text-primary);
          line-height: 1.6;
          min-height: 100vh;
          overflow-x: hidden;
        }
        
        .glass-morphism {
          background: var(--glass-bg);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid var(--glass-border);
          border-radius: 20px;
          box-shadow: var(--shadow-glass);
        }
        
        .gradient-text {
          background: var(--gradient-primary);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          font-weight: 800;
        }
        
        .btn-primary-gradient {
          background: var(--gradient-primary);
          border: none;
          color: white;
          padding: 16px 32px;
          border-radius: 12px;
          font-weight: 600;
          text-decoration: none;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: all 0.3s ease;
          box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-primary-gradient:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
          color: white;
        }
        
        .btn-secondary-gradient {
          background: var(--gradient-secondary);
          border: none;
          color: white;
          padding: 16px 32px;
          border-radius: 12px;
          font-weight: 600;
          text-decoration: none;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: all 0.3s ease;
          box-shadow: 0 4px 20px rgba(240, 147, 251, 0.3);
        }
        
        .btn-secondary-gradient:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 30px rgba(240, 147, 251, 0.4);
          color: white;
        }
        
        .floating-orb {
          position: fixed;
          border-radius: 50%;
          filter: blur(60px);
          opacity: 0.7;
          animation: float 8s ease-in-out infinite;
          z-index: -1;
        }
        
        .orb-1 {
          width: 300px;
          height: 300px;
          background: radial-gradient(circle, var(--accent-purple) 0%, transparent 70%);
          top: 10%;
          left: 5%;
          animation-delay: 0s;
        }
        
        .orb-2 {
          width: 200px;
          height: 200px;
          background: radial-gradient(circle, var(--accent-blue) 0%, transparent 70%);
          top: 70%;
          right: 10%;
          animation-delay: 3s;
        }
        
        .orb-3 {
          width: 250px;
          height: 250px;
          background: radial-gradient(circle, var(--accent-pink) 0%, transparent 70%);
          bottom: 20%;
          left: 60%;
          animation-delay: 6s;
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          33% { transform: translateY(-30px) rotate(120deg); }
          66% { transform: translateY(15px) rotate(240deg); }
        }
        
        .hero-section {
          min-height: 100vh;
          display: flex;
          align-items: center;
          padding: 2rem;
          position: relative;
        }
        
        .feature-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
          margin: 4rem 0;
        }
        
        .feature-card {
          padding: 2rem;
          text-align: center;
          transition: transform 0.3s ease;
        }
        
        .feature-card:hover {
          transform: translateY(-5px);
        }
        
        .feature-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
          background: var(--gradient-accent);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        
        @media (max-width: 768px) {
          .hero-section {
            padding: 1rem;
            text-align: center;
          }
          
          .hero-content h1 {
            font-size: 2.5rem;
          }
          
          .feature-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
          }
        }
      `}</style>

      {/* Floating Background Orbs */}
      <div className="floating-orb orb-1"></div>
      <div className="floating-orb orb-2"></div>
      <div className="floating-orb orb-3"></div>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center">
            <h1 className="text-6xl font-black mb-6 leading-tight">
              <span className="gradient-text">Rhiz</span>
              <br />
              <span className="text-white">High-context relationship intelligence</span>
              <br />
              <span className="text-2xl font-normal text-gray-400">for builders who activate meaningful connections</span>
            </h1>
            
            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              Transform professional relationships through AI-driven insights. Build meaningful connections, 
              track relationship health, and unlock the strategic power of your network with relationship intelligence 
              that actually understands context.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <button 
                onClick={() => navigate('/login')}
                className="btn-primary-gradient text-lg"
              >
                <i className="bi bi-lightning-fill"></i>
                Start Building Your Network
              </button>
              <button 
                onClick={() => navigate('/login')}
                className="btn-secondary-gradient text-lg"
              >
                <i className="bi bi-play-circle"></i>
                Experience Demo
              </button>
            </div>

            {/* Feature Grid */}
            <div className="feature-grid">
              <div className="feature-card glass-morphism">
                <div className="feature-icon">
                  <i className="bi bi-graph-up"></i>
                </div>
                <h3 className="text-xl font-bold mb-3 text-white">Trust Insights</h3>
                <p className="text-gray-300">
                  Real-time relationship intelligence with trust scoring, interaction patterns, 
                  and personalized engagement recommendations.
                </p>
              </div>

              <div className="feature-card glass-morphism">
                <div className="feature-icon">
                  <i className="bi bi-people"></i>
                </div>
                <h3 className="text-xl font-bold mb-3 text-white">Smart CRM</h3>
                <p className="text-gray-300">
                  AI-powered contact management with intelligent contact syncing, 
                  relationship pipeline tracking, and context-aware suggestions.
                </p>
              </div>

              <div className="feature-card glass-morphism">
                <div className="feature-icon">
                  <i className="bi bi-chat-dots"></i>
                </div>
                <h3 className="text-xl font-bold mb-3 text-white">AI Assistant</h3>
                <p className="text-gray-300">
                  Natural language queries about your network. Ask "Who should I talk to about fundraising?" 
                  and get intelligent, contextual recommendations.
                </p>
              </div>

              <div className="feature-card glass-morphism">
                <div className="feature-icon">
                  <i className="bi bi-shield-check"></i>
                </div>
                <h3 className="text-xl font-bold mb-3 text-white">Privacy First</h3>
                <p className="text-gray-300">
                  Your relationship data stays completely private. No public profiles, 
                  no social sharing - just intelligent insights for your eyes only.
                </p>
              </div>

              <div className="feature-card glass-morphism">
                <div className="feature-icon">
                  <i className="bi bi-lightning"></i>
                </div>
                <h3 className="text-xl font-bold mb-3 text-white">Smart Sync</h3>
                <p className="text-gray-300">
                  Seamlessly sync contacts from Google, LinkedIn, iCloud and more. 
                  Intelligent deduplication and enrichment keeps your network organized.
                </p>
              </div>

              <div className="feature-card glass-morphism">
                <div className="feature-icon">
                  <i className="bi bi-target"></i>
                </div>
                <h3 className="text-xl font-bold mb-3 text-white">Goal Matching</h3>
                <p className="text-gray-300">
                  Set relationship goals and get AI-powered suggestions for who to reach out to, 
                  when to follow up, and how to strengthen key connections.
                </p>
              </div>
            </div>

            {/* Call to Action */}
            <div className="glass-morphism p-8 text-center mt-16">
              <h2 className="text-3xl font-bold mb-4 text-white">
                Ready to transform your professional relationships?
              </h2>
              <p className="text-gray-300 mb-6">
                Join builders who are already activating meaningful connections with relationship intelligence.
              </p>
              <button 
                onClick={() => navigate('/login')}
                className="btn-primary-gradient text-lg"
              >
                <i className="bi bi-arrow-right"></i>
                Get Started Today
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;