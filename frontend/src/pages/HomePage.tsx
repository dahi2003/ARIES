import { useNavigate } from 'react-router-dom';
import '../styles/home.css';

function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      
      {/* 🌌 DARK SECTION: Navbar & Hero */}
      <div className="hero-section">
        {/* Subtle Glow */}
        <div className="hero-glow"></div>

        {/*  Navbar */}
        <nav className="navbar">
          <div className="logo-area">
            <div className="logo-icon">A</div>
            <span className="logo-text">ARIES</span>
          </div>
          
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#security">Security</a>
          </div>

          <div className="nav-actions">
            <button className="btn-nav-login" onClick={() => navigate('/login')}>Login</button>
            <button className="btn-nav-demo" onClick={() => navigate('/register')}>Request Demo</button>
          </div>
        </nav>

        <main className="hero-content">
          <div className="hero-text">
            <h1>Automate Grading.<br/>Amplify Insight.<br/><span>The Future of Evaluation is Here.</span></h1>
            <p>Meet ARIES, the trusted intelligent system that evaluates student work with unparalleled accuracy and efficiency, while professors maintain full control.</p>
            <div className="hero-buttons">
              <button className="btn-primary-large" onClick={() => navigate('/register')}>Get Started for Free</button>
              <button className="btn-outline-large">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                Watch Overview
              </button>
            </div>
          </div>
          
          <div className="hero-graphic animate-float">
            <div className="mock-window">
              <div className="mock-header">
                <span className="dot red"></span>
                <span className="dot yellow"></span>
                <span className="dot green"></span>
                <span className="terminal-title">aries-ai-engine.exe</span>
              </div>
              <div className="mock-body terminal-text">
                <div className="type-line" style={{ animationDelay: '0.5s' }}>
                  <span className="log-tag">[System]</span> Initializing Vision Engine... <span className="log-success">OK</span>
                </div>
                <div className="type-line" style={{ animationDelay: '1.5s' }}>
                  <span className="log-tag">[Analyze]</span> Scanning Student Sheet S102...
                </div>
                <div className="type-line" style={{ animationDelay: '2.5s' }}>
                  <span className="log-tag">[Logic]</span> Q1: Matches Master Key definition. <span className="log-success">+10 Marks</span>
                </div>
                <div className="type-line" style={{ animationDelay: '4.0s' }}>
                  <span className="log-tag">[Logic]</span> Q2: Missing primary key concept. <span className="log-warning">-3 Marks</span>
                </div>
                <div className="type-line" style={{ animationDelay: '5.0s' }}>
                  <span className="log-tag">[Result]</span> Evaluation Complete.
                </div>
                <div className="mock-badge result-badge" style={{ animationDelay: '6.0s' }}>
                  Final Score: 85% (Grade B)
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>

      <section className="features-section" id="features">
        <h2 className="section-title">Features at a Glance</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon bg-cyan">🤖</div>
            <h3>98% Automated Accuracy</h3>
            <p>AI grades standard copies instantly, matching professor logic.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon bg-purple">📊</div>
            <h3>In-Depth Analytics</h3>
            <p>Track student performance trends and identify weak areas.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon bg-green">🧑‍🏫</div>
            <h3>Human-in-the-Loop</h3>
            <p>Professors easily verify flagged questions and maintain control.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon bg-blue">🛡️</div>
            <h3>Enterprise Security</h3>
            <p>Advanced data protection and strict academic compliance.</p>
          </div>
        </div>

        {/* Workflow */}
        <div className="workflow-section" id="how-it-works">
          <h3>How It Works:</h3>
          <div className="workflow-steps">
            <div className="step"><span>1</span> Upload</div>
            <div className="arrow">→</div>
            <div className="step"><span>2</span> Analyze</div>
            <div className="arrow">→</div>
            <div className="step"><span>3</span> Verify</div>
            <div className="arrow">→</div>
            <div className="step"><span>4</span> Publish</div>
          </div>
        </div>
      </section>

      {/*  Footer */}
      <footer className="footer">
        <div className="footer-grid">
          <div className="footer-brand">
            <div className="logo-area mb-4">
              <div className="logo-icon">A</div>
              <span className="logo-text">ARIES</span>
            </div>
            <p>Automated, AI-powered exam copy evaluation system, designed for educational institutions.</p>
          </div>
          <div className="footer-links">
            <h4>Product</h4>
            <a href="#">Features</a>
            <a href="#">Security</a>
          </div>
          <div className="footer-links">
            <h4>Company</h4>
            <a href="#">About Us</a>
            <a href="#">Careers</a>
          </div>
          <div className="footer-links">
            <h4>Resources</h4>
            <a href="#">Blog</a>
            <a href="#">Support</a>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2026 ARIES Systems, Inc. | Privacy Policy | Terms of Service</p>
        </div>
      </footer>
    </div>
  );
}

export default Home;