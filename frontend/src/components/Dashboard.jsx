import React, { useState, useEffect } from 'react';
import { BarChart, CheckCircle, Clock } from 'lucide-react';
import axios from 'axios';
import { format, differenceInDays } from 'date-fns';
import { fr } from 'date-fns/locale';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState({
    stats: { completed: 0, total: 0, average_score: 0, next_deadline: null },
    recent_submissions: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Récupérez le token exactement comme stocké dans le Login
    const token = localStorage.getItem('token'); // Notez que c'est 'token' et non 'access_token'
    const userData = JSON.parse(localStorage.getItem('user'));

    if (!token || !userData) {
      navigate('/login');
      return;
    }

    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/student/dashboard/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        setDashboardData({
          stats: response.data.stats || {
            completed: 0,
            total: 0,
            average_score: 0,
            next_deadline: null
          },
          recent_submissions: response.data.recent_submissions || []
        });
      } catch (err) {
        if (err.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/login');
        } else {
          setError(err.response?.data?.message || "Erreur de chargement des données");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [navigate]);


  // ... (gardez le reste de votre code de rendu tel quel)

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-red-700">
              Erreur: {error}. <button onClick={() => window.location.reload()} className="font-medium underline text-red-700 hover:text-red-600">Réessayer</button>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8 mt-16">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Tableau de bord étudiant</h1>
        <p className="mt-2 text-gray-600">Suivez votre progression et vos soumissions</p>
      </header>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Carte: Exercices complétés */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Exercices complétés</h2>
            <CheckCircle className="h-6 w-6 text-green-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {dashboardData.stats.completed}
          </p>
          <p className="mt-1 text-sm text-gray-600">
            Sur {dashboardData.stats.total} exercices au total
          </p>
        </div>

        {/* Carte: Score moyen */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Score moyen</h2>
            <BarChart className="h-6 w-6 text-blue-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {dashboardData.stats.average_score.toFixed(1)}/20
          </p>
          <p className="mt-1 text-sm text-gray-600">Basé sur toutes les soumissions</p>
        </div>

        {/* Carte: Prochaine échéance */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Prochaine échéance</h2>
            <Clock className="h-6 w-6 text-orange-500" />
          </div>
          {dashboardData.stats.next_deadline ? (
            <>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {differenceInDays(
                  new Date(dashboardData.stats.next_deadline.date_limite), 
                  new Date()
                )} jours
              </p>
              <p className="mt-1 text-sm text-gray-600">
                {dashboardData.stats.next_deadline.exercise_title}
              </p>
            </>
          ) : (
            <p className="mt-2 text-gray-600">Aucune échéance à venir</p>
          )}
        </div>
      </div>

      {/* Section: Soumissions récentes */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Soumissions récentes</h2>
        <div className="space-y-4">
          {dashboardData.recent_submissions.length > 0 ? (
            dashboardData.recent_submissions.map((submission, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h3 className="font-medium text-gray-900">{submission.exercise_title}</h3>
                  <p className="text-sm text-gray-600">
                    Soumis le {format(new Date(submission.submission_date), 'dd MMM yyyy', { locale: fr })}
                  </p>
                </div>
                <div className="flex items-center">
                  {submission.score !== null ? (
                    <span className={`font-semibold ${
                      submission.score >= 10 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {submission.score}/20
                    </span>
                  ) : (
                    <span className="text-gray-500">En attente</span>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">Aucune soumission récente</p>
              <button 
                onClick={() => window.location.reload()}
                className="mt-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200"
              >
                Actualiser
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 