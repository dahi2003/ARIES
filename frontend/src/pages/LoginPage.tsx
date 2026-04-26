import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiPost, apiGet } from '../api';
import { saveAuth } from '../auth';
import '../styles/login.css'; // 

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const formData = new URLSearchParams({ username: email, password }).toString();
      const result = await apiPost('/auth/login', formData, 'application/x-www-form-urlencoded');

      if (result.access_token) {
        localStorage.setItem('access_token', result.access_token);
        
        const profile = await apiGet('/users/me');
        saveAuth(result.access_token, profile.role || 'student');
        
        navigate(profile.role === 'professor' ? '/professor' : '/student');
      } else if (result.detail) {
        setError(result.detail);
      } else {
        setError('Login failed. Please check your credentials.');
      }
    } catch (err) {
      console.error("Login Error:", err);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="neon-glow"></div>

      {/*  Back Button */}
      <button onClick={() => navigate("/")} className="back-btn">
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to Home
      </button>

      {/*  Main Login Card */}
      <div className="login-card">
        
        {/*  ARIES Logo & Header */}
        <div className="login-header">
          <div className="logo-container" onClick={() => navigate("/")}>
            <div className="logo-icon">A</div>
            <span className="logo-text">ARIES</span>
          </div>
          <h1>Welcome Back</h1>
          <p>Securely sign in to your AI Dashboard</p>
        </div>

        {/*  Error Alert Box */}
        {error && (
          <div className="error-box">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {/*  Form */}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <label>Email Address</label>
            <input 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              type="email" 
              required 
              disabled={isLoading}
              placeholder="professor@university.edu"
            />
          </div>

          <div className="input-group">
            <div className="password-header">
              <label>Password</label>
              <a href="#">Forgot password?</a>
            </div>
            <input 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              type="password" 
              required 
              disabled={isLoading}
              placeholder="••••••••"
            />
          </div>
          
          <button type="submit" disabled={isLoading} className={`submit-btn ${isLoading ? 'loading' : ''}`}>
            {isLoading ? (
              <>
                <div className="spinner"></div>
                Authenticating...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* 🔗 Footer Link */}
        <div className="login-footer">
          {/* Don't have an account? <a href="/register">Register as Professor</a> */}
         Don't have an account? <span style={{color: '#00e5ff', cursor: 'pointer', textDecoration: 'underline'}} onClick={() => navigate('/register')}>Register as Professor</span>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
