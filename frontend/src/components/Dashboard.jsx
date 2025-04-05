import React, { useEffect, useState } from 'react';
import { BarChart, CheckCircle, Clock, FileText, AlertCircle, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const [stats, setStats] = useState({
    completedExercises: 0,
    totalExercises: 0,
    averageScore: 0,
    pendingSubmissions: 0,
    nextDeadline: null,
    recentSubmissions: []
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fonction pour récupérer les données du backend
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await fetch('/api/student/dashboard/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          if (response.status === 401) {
            localStorage.removeItem('access_token');
            navigate('/login');
            return;
          }
          throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Transformation des données pour correspondre à l'état local
        setStats({
          completedExercises: data.completed_exercises || 0,
          totalExercises: data.total_exercises || 0,
          averageScore: parseFloat(data.average_score) || 0,
          pendingSubmissions: data.pending_submissions || 0,
          nextDeadline: data.next_deadline || null,
          recentSubmissions: data.recent_submissions?.map(sub => ({
            id: sub.id,
            exercice: {
              id: sub.exercice.id,
              titre: sub.exercice.titre,
              date_limite: sub.exercice.date_limite
            },
            note: sub.note,
            date_soumission: sub.date_soumission,
            en_retard: sub.en_retard,
            correction: {
              est_validee: sub.correction?.est_validee || false,
              feedback: sub.correction?.feedback || null
            }
          })) || []
        });
      } catch (err) {
        console.error("Erreur de chargement:", err);
        setError("Impossible de charger les données. Veuillez réessayer.");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [navigate]);

  // Fonctions utilitaires
  const formatDate = (dateString) => {
    if (!dateString) return "Aucune échéance";
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric', 
      month: 'short', 
      year: 'numeric',
      hour: '2-digit', 
      minute: '2-digit'
    });
  };

  const daysUntilDeadline = (deadline) => {
    if (!deadline) return null;
    const now = new Date();
    const dueDate = new Date(deadline);
    const diffTime = Math.max(0, dueDate - now); // Évite les valeurs négatives
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  // Affichage pendant le chargement
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 mt-16 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">Chargement de vos données...</p>
      </div>
    );
  }

  // Affichage en cas d'erreur
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 mt-16 text-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <strong className="font-bold">Erreur ! </strong>
          <span className="block sm:inline">{error}</span>
          <button 
            onClick={() => window.location.reload()}
            className="mt-2 px-4 py-1 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  // Affichage principal
  return (
    <div className="container mx-auto px-4 py-8 space-y-8 mt-16">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Tableau de bord étudiant</h1>
        <p className="mt-2 text-gray-600">Suivez votre progression et vos soumissions</p>
      </header>

      {/* Cartes de statistiques */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Exercices complétés */}
        <div 
          className="bg-white p-6 rounded-lg shadow-md cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => navigate('/exercises')}
        >
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Exercices complétés</h2>
            <CheckCircle className="h-6 w-6 text-green-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {stats.completedExercises}/{stats.totalExercises}
          </p>
          <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
            <div 
              className="bg-green-500 h-2.5 rounded-full" 
              style={{ 
                width: `${stats.totalExercises > 0 
                  ? (stats.completedExercises / stats.totalExercises) * 100 
                  : 0}%` 
              }}
            ></div>
          </div>
          <p className="mt-1 text-sm text-gray-600">
            {stats.totalExercises > 0 
              ? `${Math.round((stats.completedExercises / stats.totalExercises) * 100)}% complété` 
              : 'Aucun exercice disponible'}
          </p>
        </div>

        {/* Score moyen */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Score moyen</h2>
            <BarChart className="h-6 w-6 text-blue-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {stats.averageScore.toFixed(1)}/20
          </p>
          <div className="flex items-center mt-1">
            <TrendingUp className="h-4 w-4 text-blue-500 mr-1" />
            <p className="text-sm text-gray-600">
              {stats.averageScore > 0 
                ? `+${((stats.averageScore - 10) / 10 * 100).toFixed(1)}% vs moyenne classe` 
                : 'Données en cours de calcul'}
            </p>
          </div>
        </div>

        {/* Prochaine échéance */}
        <div 
          className="bg-white p-6 rounded-lg shadow-md cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => navigate('/exercises')}
        >
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Prochaine échéance</h2>
            <Clock className="h-6 w-6 text-orange-500" />
          </div>
          {stats.nextDeadline ? (
            <>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {daysUntilDeadline(stats.nextDeadline)} jour(s)
              </p>
              <p className="mt-1 text-sm text-gray-600">
                {formatDate(stats.nextDeadline)}
              </p>
            </>
          ) : (
            <p className="mt-2 text-gray-600">Aucune échéance prochaine</p>
          )}
        </div>

        {/* Soumissions en attente */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">En attente de correction</h2>
            <AlertCircle className="h-6 w-6 text-yellow-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {stats.pendingSubmissions}
          </p>
          <p className="mt-1 text-sm text-gray-600">
            {stats.pendingSubmissions > 0 
              ? 'Corrections en cours' 
              : 'Toutes vos soumissions sont corrigées'}
          </p>
        </div>
      </div>

      {/* Soumissions récentes */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Soumissions récentes</h2>
          <button 
            onClick={() => navigate('/submissions')}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Voir tout →
          </button>
        </div>
        
        {stats.recentSubmissions.length > 0 ? (
          <div className="space-y-4">
            {stats.recentSubmissions.map((submission) => (
              <div 
                key={submission.id} 
                className={`flex items-center justify-between p-4 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors ${
                  submission.en_retard ? 'bg-red-50' : 'bg-gray-50'
                }`}
                onClick={() => navigate(`/submission/${submission.id}`)}
              >
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-900 truncate">
                    {submission.exercice.titre}
                  </h3>
                  <div className="flex items-center mt-1 space-x-4 text-sm text-gray-600">
                    <span>Soumis le {formatDate(submission.date_soumission)}</span>
                    {submission.en_retard && (
                      <span className="text-red-500 flex items-center">
                        <Clock className="h-3 w-3 mr-1" /> En retard
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center ml-4">
                  {submission.correction?.est_validee ? (
                    <span className="font-semibold px-3 py-1 rounded-full bg-green-100 text-green-800">
                      {submission.note}/20
                    </span>
                  ) : (
                    <span className="font-semibold px-3 py-1 rounded-full bg-yellow-100 text-yellow-800">
                      En cours
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-gray-600">Aucune soumission récente</p>
            <button
              onClick={() => navigate('/exercises')}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Voir les exercices disponibles
            </button>
          </div>
        )}
      </div>

      {/* Suggestions d'amélioration */}
      {stats.recentSubmissions.some(s => s.correction?.feedback) && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Suggestions d'amélioration</h2>
          <div className="space-y-3">
            {stats.recentSubmissions
              .filter(s => s.correction?.feedback)
              .slice(0, 2)
              .map((submission) => (
                <div key={`feedback-${submission.id}`} className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-medium text-gray-900">{submission.exercice.titre}</h3>
                  <p className="mt-1 text-sm text-gray-600">{submission.correction.feedback}</p>
                  <button 
                    onClick={() => navigate(`/submission/${submission.id}`)}
                    className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Voir les détails →
                  </button>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;