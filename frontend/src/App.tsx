import { Navigate, Route, Routes } from 'react-router-dom';
import Home from './pages/HomePage'; 
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfessorDashboard from './pages/ProfessorDashboard';
import StudentDashboard from './pages/StudentDashboard';
import { getStoredRole } from './auth';

function App() {
  const currentRole = getStoredRole();

  return (
    <div className="app-shell">
      <Routes>
       
        <Route path="/" element={<Home />} />
        
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/professor" element={<ProfessorDashboard />} />
        <Route path="/student" element={<StudentDashboard />} />
        <Route path="*" element={<div className="page"><h2>Page not found</h2></div>} />
      </Routes>
    </div>
  );
}

export default App;