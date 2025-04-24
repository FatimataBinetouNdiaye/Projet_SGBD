import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext'
import CorrectionPage from './components/CorrectionPage';
import Navbar from './components/Navbar'; 
import Accueil from './components/Accueil';
import Exercices from './components/Exercices';
import Apropos from './components/Apropos';
import ExerciceList from './components/ExerciceList';
import Footer from './components/footer';
import Login from './components/Login';
import Signup from './components/Signup';
import SubmissionForm from './components/SubmissionForm';
import Dashboard from './components/Dashboard';
import TeacherDashboard from './components/TeacherDashboard';
import LoadingSpinner from './components/LoadingSpinner';
import ProfessorStudentList from './components/ProfessorStudentList';
import StudentSubmissions from './components/StudentSubmissions';
import './App.css';

// Composant de protection de route
const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, isLoading } = useContext(AuthContext);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/" replace />;
  }

  return children;
};

// Composant pour les routes publiques seulement
const PublicOnlyRoute = ({ children }) => {
  const { user, isLoading } = useContext(AuthContext);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (user) {
    return <Navigate to={user.role === 'PR' ? '/dashboard/prof' : '/tableau-de-bord'} replace />;
  }

  return children;
};

function Home() {
  return (
    <>
      <section id="Accueil">
        <Accueil />
      </section>
      <section id="Exercices">
        <Exercices />
      </section>
      <section id="Apropos">
        <Apropos />
      </section>
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/exercices" element={<ExerciceList />} />
          
          {/* Routes publiques seulement (non authentifiées) */}
          <Route path="/login" element={
            <PublicOnlyRoute>
              <Login />
            </PublicOnlyRoute>
          } />
          <Route path="/signup" element={
            <PublicOnlyRoute>
              <Signup />
            </PublicOnlyRoute>
          } />
          
          {/* Routes protégées */}
          <Route path="/soumettre" element={
            <ProtectedRoute>
              <SubmissionForm />
            </ProtectedRoute>
          } />
          <Route path="/tableau-de-bord" element={
            <ProtectedRoute requiredRole="ET">
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/dashboard/prof" element={
            <ProtectedRoute requiredRole="PR">
              <TeacherDashboard />
            </ProtectedRoute>
          } />
          <Route path="/corrections" element={
            <ProtectedRoute requiredRole="ET">
              <CorrectionPage />
            </ProtectedRoute>
          } />
                      <Route 
              path="/liste-classes" 
              element={
                <ProtectedRoute allowedRoles={['PR']}>
                  <ProfessorStudentList />
                </ProtectedRoute>
              } 
            />
            <Route 
    path="/soumissions/etudiant/:studentId" 
    element={
        <ProtectedRoute allowedRoles={['PR']}>
            <StudentSubmissions />
        </ProtectedRoute>
    } 
/>
          
          
          <Route path="*" element={<h1>Page non trouvée</h1>} />
        </Routes>
        <Footer />
      </Router>
    </AuthProvider>
  );
}

export default App;