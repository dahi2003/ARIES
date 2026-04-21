import { FormEvent, useEffect, useState } from 'react';
import { logout, getStoredRole } from '../auth';
import { useNavigate } from 'react-router-dom';
import { apiGet, apiPost, apiPostForm } from '../api';
import '../styles/dashboard.css';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

interface Subject {
  id: number;
  name: string;
  professor_id: number;
  created_at: string;
}

interface CopyInfo {
  id: number;
  subject_id: number;
  student_name: string;
  student_email: string;
  roll_number?: string;
  filename: string;
  status: string;
  uploaded_at: string;
}

interface StudentResult {
  id?: number;
  copy_id?: number;
  student_copy_id?: number;
  score: number;
  max_score: number;
  feedback?: string;
  student_name?: string;
  roll_number?: string;
  status?: string;
}

function ProfessorDashboard() {
  const [subject, setSubject] = useState('');
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [selectedSubjectName, setSelectedSubjectName] = useState('');
  const [copies, setCopies] = useState<CopyInfo[]>([]);
  const [answerKeyFile, setAnswerKeyFile] = useState<File | null>(null);
  const [studentName, setStudentName] = useState('');
  const [studentEmail, setStudentEmail] = useState('');
  const [studentRollNumber, setStudentRollNumber] = useState('');
  const [studentFiles, setStudentFiles] = useState<FileList | null>(null);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('success');
  const navigate = useNavigate();
  const [studentResults, setStudentResults] = useState<StudentResult[]>([]);
  const [showMarksTab, setShowMarksTab] = useState(false);
  const [sortBy, setSortBy] = useState<'roll_number' | 'name' | 'score'>('roll_number');

  const role = getStoredRole();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token || role !== 'professor') navigate('/login');
    else loadSubjects();
  }, [role, navigate]);

  const showMessage = (msg: string, type: 'success' | 'error' = 'success') => {
    setMessage(msg); setMessageType(type);
    if (type === 'success') setTimeout(() => setMessage(''), 4000);
  };

  const loadSubjects = async () => {
    try {
      const data = await apiGet('/uploads/subjects');
      if (Array.isArray(data)) setSubjects(data);
    } catch (error) { showMessage('Error loading subjects.', 'error'); }
  };

  const loadCopies = async (subjectId: number, subjectName: string) => {
    try {
      const data = await apiGet(`/uploads/subject/${subjectId}/copies`);
      if (Array.isArray(data)) {
        setCopies(data);
        setSelectedSubjectId(subjectId);
        setSelectedSubjectName(subjectName);
        setShowMarksTab(false);
        loadStudentResults(subjectId);
      }
    } catch (error) { showMessage('Error loading copies.', 'error'); }
  };

  const loadStudentResults = async (subjectId: number) => {
    try {
      const data = await apiGet(`/results/subject/${subjectId}`);
      if (Array.isArray(data)) setStudentResults(data);
    } catch (error) { setStudentResults([]); }
  };

  const handleCreateSubject = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      const result = await apiPost('/uploads/subject', new URLSearchParams({ name: subject }).toString(), 'application/x-www-form-urlencoded');
      if (result && result.id) {
        setSubject(''); showMessage('Workspace created successfully!'); loadSubjects();
      }
    } catch (error) { showMessage('Error creating subject.', 'error'); }
  };

  const handleUploadAnswerKey = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!answerKeyFile || !selectedSubjectId) return;
    try {
      const formData = new FormData();
      formData.append('file', answerKeyFile);
      formData.append('subject_id', selectedSubjectId.toString());
      const result = await apiPostForm('/uploads/answer-key', formData);
      if (result && result.id) {
        setAnswerKeyFile(null); showMessage('Master Answer Key uploaded!');
      }
    } catch (error) { showMessage('Error uploading answer key.', 'error'); }
  };

  const handleUploadStudentCopies = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!studentFiles || !selectedSubjectId) return;
    try {
      const formData = new FormData();
      for (let i = 0; i < studentFiles.length; i++) formData.append('files', studentFiles[i]);
      formData.append('subject_id', selectedSubjectId.toString());
      formData.append('student_name', studentName);
      formData.append('student_email', studentEmail);
      formData.append('roll_number', studentRollNumber);

      const result = await apiPostForm('/uploads/student-copies', formData);
      if (result && result.uploaded) {
        setStudentFiles(null); setStudentName(''); setStudentEmail(''); setStudentRollNumber('');
        showMessage('Copies uploaded successfully!'); loadCopies(selectedSubjectId, selectedSubjectName);
      }
    } catch (error) { showMessage('Error uploading student copies.', 'error'); }
  };

  const handleTriggerEvaluation = async () => {
    if (!selectedSubjectId) return;
    try {
      const result = await apiPost('/evaluations/trigger', { subject_id: selectedSubjectId, max_score: 100 });
      if (result && !result.error) {
        showMessage('AI Engine started! Processing copies...');
        setTimeout(() => {
          loadCopies(selectedSubjectId, selectedSubjectName);
          loadStudentResults(selectedSubjectId);
        }, 3000);
      }
    } catch (error) { showMessage('Error starting AI.', 'error'); }
  };

  const getSortedResults = () => {
    return [...studentResults].sort((a, b) => {
      return (b.score || 0) - (a.score || 0); // Default sort by highest score
    });
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="logo-area">
          <div className="logo-icon">A</div>
          <span className="logo-text">ARIES <span className="role-badge">Professor</span></span>
        </div>
        <button className="btn-logout" onClick={() => { logout(); navigate('/login'); }}>Logout</button>
      </header>

      {message && <div className={`alert-box ${messageType === 'success' ? 'alert-success' : 'alert-error'}`}><span>{message}</span></div>}

      <div className="dashboard-grid">
        <div className="dashboard-sidebar">
          <div className="card">
            <h3>Select Subject Area</h3>
            <select className="dark-select" onChange={(e) => {
              const subj = subjects.find((s) => s.id === parseInt(e.target.value));
              if (subj) loadCopies(subj.id, subj.name);
            }}>
              <option value="">-- Choose Workspace --</option>
              {subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>

            {!selectedSubjectId && (
              <form onSubmit={handleCreateSubject} className="create-subject-form">
                <hr className="divider" />
                <h3>Create Workspace</h3>
                <input type="text" className="dark-input" placeholder="e.g. CS101" value={subject} onChange={(e) => setSubject(e.target.value)} required />
                <button type="submit" className="btn-primary w-full">Create</button>
              </form>
            )}
          </div>
        </div>

        <div className="dashboard-main">
          {!selectedSubjectId ? (
            <div className="empty-state">
              <h2>No Subject Selected</h2>
              <p>Select a workspace from the left panel.</p>
            </div>
          ) : (
            <>
              <div className="tabs-container">
                <button className={`tab-btn ${!showMarksTab ? 'active' : ''}`} onClick={() => setShowMarksTab(false)}>Manage Uploads</button>
                <button className={`tab-btn ${showMarksTab ? 'active' : ''}`} onClick={() => setShowMarksTab(true)}>Results & Analytics</button>
              </div>

              {!showMarksTab ? (
                <div className="tab-content animate-fade-in">
                  {/* ... Upload Cards ... */}
                  <div className="upload-grid">
                    <div className="card">
                      <h3>1. Master Answer Key</h3>
                      <form onSubmit={handleUploadAnswerKey} className="upload-form">
                        <input type="file" className="file-input" onChange={(e) => setAnswerKeyFile(e.target.files?.[0] || null)} />
                        <button type="submit" className="btn-secondary w-full">Upload Key</button>
                      </form>
                    </div>
                    <div className="card">
                      <h3>2. Student Responses</h3>
                      <form onSubmit={handleUploadStudentCopies} className="upload-form">
                        <input type="text" className="dark-input" placeholder="Student Name" value={studentName} onChange={(e) => setStudentName(e.target.value)} required />
                        <div className="input-row">
                          <input type="text" className="dark-input" placeholder="Roll No." value={studentRollNumber} onChange={(e) => setStudentRollNumber(e.target.value)} />
                          <input type="email" className="dark-input" placeholder="Email" value={studentEmail} onChange={(e) => setStudentEmail(e.target.value)} />
                        </div>
                        <input type="file" multiple className="file-input" onChange={(e) => setStudentFiles(e.target.files)} />
                        <button type="submit" className="btn-secondary w-full">Upload Copy</button>
                      </form>
                    </div>
                  </div>

                  <div className="card highlight-card">
                    <div className="highlight-content">
                      <div>
                        <h3>3. Run AI Evaluation</h3>
                        <p className="card-subtitle">Grade all pending copies.</p>
                      </div>
                      <button onClick={handleTriggerEvaluation} className="btn-glow">Trigger AI Engine</button>
                    </div>
                  </div>

                  <div className="card" style={{ marginTop: '1.5rem' }}>
                    <h3>Uploaded Copies ({copies.length})</h3>
                    <div className="table-responsive">
                      <table className="dark-table">
                        <thead>
                          <tr>
                            <th>Student Name</th>
                            <th>Roll Number</th>
                            <th>Status</th>
                            <th>Upload Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {copies.length > 0 ? copies.map((copy) => {
                            const statusText = copy.status || 'Pending';
                            return (
                              <tr key={copy.id}>
                                <td className="font-bold text-white">{copy.student_name}</td>
                                <td>{copy.roll_number || '-'}</td>
                                <td><span className={`status-badge status-${statusText.toLowerCase()}`}>{statusText}</span></td>
                                <td>{new Date(copy.uploaded_at).toLocaleDateString()}</td>
                              </tr>
                            );
                          }) : (
                            <tr><td colSpan={4} className="text-center text-muted py-8">No copies uploaded yet.</td></tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="tab-content animate-fade-in">
                  <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <div className="table-header" style={{ padding: '1.5rem', marginBottom: 0 }}>
                      <h3>Final Grades</h3>
                    </div>

                    <div className="table-responsive">
                      <table className="dark-table">
                        <thead>
                          <tr>
                            <th>Roll No.</th>
                            <th>Student</th>
                            <th>Score</th>
                            <th>Accuracy</th>
                            <th>Status</th>
                            <th>AI Remarks</th>
                          </tr>
                        </thead>
                        <tbody>
                          {studentResults.length > 0 ? getSortedResults().map((result, index) => {
                            
                            // 🛡️ ULTIMATE BULLETPROOF MATCHER
                            const possibleCopyId = result.copy_id || result.student_copy_id || result.id;
                            let matchedCopy = copies.find(c => String(c.id) === String(possibleCopyId));
                            
                            // Last Resort Fallback: Match by Array Index
                            if (!matchedCopy && copies[index]) {
                                matchedCopy = copies[index];
                            }
                            
                            const actualName = matchedCopy?.student_name || result.student_name || 'Unknown Student';
                            const actualRoll = matchedCopy?.roll_number || result.roll_number || '-';
                            
                            const validScore = result.score !== null && result.score !== undefined ? result.score : 0;
                            const validMax = result.max_score || 100;
                            const percentage = result.score !== null && result.score !== undefined ? parseFloat(((validScore / validMax) * 100).toFixed(2)) : 0;
                            const gradeColor = percentage >= 75 ? 'emerald' : percentage >= 50 ? 'amber' : 'red';
                            
                            let actualStatus = result.status || matchedCopy?.status || 'Pending';
                            if (result.score !== null && result.score !== undefined) actualStatus = 'Completed';
                            
                            return (
                              <tr key={index}>
                                <td className="text-muted">{actualRoll}</td>
                                <td className="font-bold text-white">{actualName}</td>
                                <td className="font-bold text-white">
                                  {result.score !== null && result.score !== undefined 
                                    ? `${validScore.toFixed(2)} / ${validMax}` 
                                    : <span className="text-muted">Evaluating...</span>}
                                </td>
                                <td>
                                  {result.score !== null && result.score !== undefined 
                                    ? <span className={`score-badge bg-${gradeColor}`}>{percentage}%</span>
                                    : <span className="text-muted">-</span>}
                                </td>
                                <td><span className={`status-badge status-${actualStatus.toLowerCase()}`}>{actualStatus}</span></td>
                                <td className="text-sm truncate-text" title={result.feedback}>{result.feedback ? result.feedback.substring(0, 60) + '...' : '-'}</td>
                              </tr>
                            );
                          }) : (
                            <tr><td colSpan={6} className="text-center text-muted py-8">No results found. Trigger the AI Evaluation first.</td></tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProfessorDashboard;