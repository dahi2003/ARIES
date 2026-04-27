import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiPost } from '../api';
import '../styles/login.css'; // 

function RegisterPage() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('professor');
  
  // UI States
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const result = await apiPost('/auth/register', {
        email,
        full_name: fullName,
        password,
        role,
      });

      if ((result as any).id) {
        setSuccess('Registration successful! Redirecting to login...');
        window.setTimeout(() => navigate('/login'), 1500);
      } else {
        setError((result as any).detail || 'Registration failed. Please try again.');
        setIsLoading(false);
      }
    } catch (err) {
      console.error("Registration Error:", err);
      setError('An unexpected error occurred.');
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

      {/*  Main Register Card */}
      <div className="login-card" style={{ maxWidth: '500px' }}> {/* Thoda choda rakha hai forms ke liye */}
        
        {/*  ARIES Logo & Header */}
        <div className="login-header">
          <div className="logo-container" onClick={() => navigate("/")}>
            <div className="logo-icon">A</div>
            <span className="logo-text">ARIES</span>
          </div>
          <h1>Join the Future</h1>
          <p>Create your account to start evaluating</p>
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

        {/*  Success Alert Box */}
        {success && (
          <div className="error-box" style={{ backgroundColor: 'rgba(0, 229, 255, 0.1)', borderColor: 'rgba(0, 229, 255, 0.3)', color: '#00E5FF' }}>
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{success}</span>
          </div>
        )}

        {/*  Form */}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <label>Full Name</label>
            <input 
              value={fullName} 
              onChange={(e) => setFullName(e.target.value)} 
              type="text" 
              required 
              disabled={isLoading || !!success}
              placeholder="Dr. Evelyn Reed"
            />
          </div>

          <div className="input-group">
            <label>Email Address</label>
            <input 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              type="email" 
              required 
              disabled={isLoading || !!success}
              placeholder="professor@university.edu"
            />
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <div className="input-group" style={{ flex: 1 }}>
              <label>Password</label>
              <input 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                type="password" 
                required 
                minLength={8}
                maxLength={128}
                disabled={isLoading || !!success}
                placeholder="••••••••"
              />
            </div>

            <div className="input-group" style={{ flex: 1 }}>
              <label>Role</label>
              <select 
                value={role} 
                onChange={(e) => setRole(e.target.value)}
                disabled={isLoading || !!success}
              >
                <option value="professor">Professor</option>
                <option value="student">Student</option>
                {/* <option value="superadmin">Super Admin</option> */}
              </select>
            </div>
          </div>
          
          <button type="submit" disabled={isLoading || !!success} className={`submit-btn ${(isLoading || success) ? 'loading' : ''}`}>
            {isLoading ? (
              <>
                <div className="spinner"></div>
                Creating Account...
              </>
            ) : success ? (
              'Success!'
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        {/* 🔗 Footer Link */}
        <div className="login-footer">
          Already have an account? <Link to="/login">Sign In</Link>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
