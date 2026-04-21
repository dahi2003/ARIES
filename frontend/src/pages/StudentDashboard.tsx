import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getStoredRole, logout } from '../auth';
import { apiGet } from '../api';
import '../styles/dashboard.css';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

type StudentResult = {
  copy_id: number;
  subject_id: number;
  subject_name: string | null;
  student_name: string;
  student_email: string | null;
  status: string;
  score: number | null;
  max_score: number | null;
  feedback: string | null;
  report_path: string | null;
  uploaded_at: string;
};

function StudentDashboard() {
  const navigate = useNavigate();
  const role = getStoredRole();
  const [allResults, setAllResults] = useState<StudentResult[]>([]);
  const [searchName, setSearchName] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadResults = async () => {
    setRefreshing(true);
    try {
      // 1. Get Logged-in user's profile
      const profile = await apiGet('/users/me');
      
      // 2. Fetch all results
      const data = await apiGet('/results/evaluated');
      
      if (Array.isArray(data)) {
        
        const userEmail = (profile.email || "").toLowerCase().trim();
        const userName = (profile.full_name || "").toLowerCase().trim();

        const myResults = data.filter(r => {
            const copyEmail = (r.student_email || "").toLowerCase().trim();
            const copyName = (r.student_name || "").toLowerCase().trim();

            const emailMatch = userEmail && copyEmail === userEmail;
            const nameMatch = userName && copyName && (userName.includes(copyName) || copyName.includes(userName));

            return emailMatch || nameMatch;
        });

        setAllResults(myResults);
      }
    } catch (err) {
      console.error("Error fetching results", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (role !== 'student') {
      navigate('/login');
      return;
    }
    loadResults();
  }, [role, navigate]);

  const filteredResults = allResults.filter(r =>
    r.student_name.toLowerCase().includes(searchName.toLowerCase())
  );

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="logo-area" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
          <div className="logo-icon">A</div>
          <span className="logo-text">ARIES <span className="role-badge">Student</span></span>
        </div>
        <button className="btn-logout" onClick={() => { logout(); navigate('/login'); }}>
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
          Logout
        </button>
      </header>

      <main style={{ maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <div className="card animate-fade-in">
          <div className="table-header" style={{ marginBottom: '1.5rem' }}>
            <div>
              <h2 style={{ color: '#fff', margin: 0, fontSize: '1.5rem' }}>Your Exam Results</h2>
              <p className="card-subtitle" style={{ margin: '0.25rem 0 0 0' }}>Track your AI-evaluated academic performance</p>
            </div>
            <button className="btn-secondary" onClick={loadResults} disabled={refreshing || loading}>
              {refreshing || loading ? 'Refreshing...' : 'Refresh Data'}
            </button>
          </div>
          
          {loading ? (
            <div className="empty-state"><p className="text-muted font-medium">Fetching your grades securely...</p></div>
          ) : allResults.length > 0 ? (
            <>
              <div style={{ marginBottom: '1.5rem', position: 'relative' }}>
                <input
                  type="text" className="dark-input" placeholder="Search by your name..."
                  value={searchName} onChange={(e) => setSearchName(e.target.value)}
                  style={{ marginBottom: 0 }}
                />
              </div>

              <div className="table-responsive">
                <table className="dark-table">
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th>Your Name</th>
                      <th>Status</th>
                      <th>Score</th>
                      <th>Professor Feedback</th>
                      <th>Report</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredResults.map((result) => {
                      let percentage = 0;
                      let gradeColor = 'amber';
                      if (result.score !== null && result.max_score) {
                        percentage = parseFloat(((result.score / result.max_score) * 100).toFixed(2));
                        gradeColor = percentage >= 75 ? 'emerald' : percentage >= 50 ? 'amber' : 'red';
                      }

                      return (
                        <tr key={result.copy_id}>
                          <td className="text-muted font-medium">{result.subject_name || 'Unknown'}</td>
                          <td className="font-bold text-white">{result.student_name}</td>
                          <td><span className={`status-badge status-${result.status.toLowerCase()}`}>{result.status}</span></td>
                          <td>
                            {result.score !== null ? (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                {/* 🛠️ FIXED: .toFixed(2) prevents long decimal bugs */}
                                <span className="font-bold text-white">{Number(result.score).toFixed(2)} / {result.max_score}</span>
                                <span className={`score-badge bg-${gradeColor}`}>{percentage}%</span>
                              </div>
                            ) : <span className="text-muted">Evaluating...</span>}
                          </td>
                          <td className="text-sm truncate-text" style={{ maxWidth: '250px' }}>{result.feedback || '-'}</td>
                          <td>
                            {result.report_path ? (
                              <a href={`${API_BASE}/reports/${result.report_path}`} target="_blank" rel="noopener noreferrer" style={{ color: '#00E5FF', fontWeight: 'bold' }}>Download Report</a>
                            ) : '-'}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <h3 style={{ color: '#fff', marginBottom: '0.5rem' }}>No Results Found</h3>
              <p className="text-muted">Your professor hasn't evaluated your copies yet, or they were uploaded under a different email/name.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default StudentDashboard;