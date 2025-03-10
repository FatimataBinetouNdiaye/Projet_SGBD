import React from 'react';
import "./App.css";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
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
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/exercices" element={<ExerciceList />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/soumettre" element={<SubmissionForm />} />
        <Route path="/tableau-de-bord" element={<Dashboard />} />
        <Route path="*" element={<h1>Page non trouvée</h1>} />
      </Routes>
      <Footer />
    </Router>
  );
}

export default App;
