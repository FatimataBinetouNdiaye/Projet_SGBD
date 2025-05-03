import React, { useState, useEffect } from 'react';
import { BarChart, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { format, differenceInDays } from 'date-fns';
import { fr } from 'date-fns/locale';
import { useNavigate } from 'react-router-dom';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler 
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function Dashboard() {
  const colors = {
    brandPrimary: '#4CAF4F',
    brandPrimaryLight: '#81C784',
    brandPrimaryLighter: '#C8E6C9',
    brandPrimaryDark: '#388E3C',
    brandDanger: '#F44336'
  };
  
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState({
    stats: { 
      completed: 0, 
      total: 0, 
      average_score: 0, 
      next_deadline: null,
      unsubmitted_count: 0,
      late_submissions: 0
    },
    all_submissions: [],
    recent_submissions: []
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://127.0.0.1:8000/api/student/dashboard/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        setDashboardData({
          stats: response.data.stats,
          all_submissions: response.data.all_submissions,
          recent_submissions: response.data.recent_submissions
        });
        
      } catch (err) {
        if (err.response?.status === 401) {
          localStorage.removeItem('token');
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

  const prepareChartData = () => {
    const correctedSubmissions = dashboardData.all_submissions
      .filter(sub => sub.correction?.note !== undefined)
      .sort((a, b) => new Date(a.submission_date) - new Date(b.submission_date));

    const labels = correctedSubmissions.map((_, index) => `Soumission ${index + 1}`);
    const data = correctedSubmissions.map(sub => sub.correction.note);

    return {
      labels,
      datasets: [{
        label: 'Notes',
        data,
        borderColor: colors.brandPrimaryDark,
        backgroundColor: colors.brandPrimaryLighter,
        tension: 0.3,
        fill: true,
        pointBackgroundColor: colors.brandPrimary,
        pointBorderColor: '#fff',
        pointRadius: 5,
        pointHoverRadius: 7,
        borderWidth: 2
      }]
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: 'Évolution des notes',
        font: { size: 16 }
      },
      tooltip: {
        callbacks: {
          title: (context) => {
            const submission = dashboardData.all_submissions
              .filter(sub => sub.correction?.note !== undefined)
              .sort((a, b) => new Date(a.submission_date) - new Date(b.submission_date))
              [context[0].dataIndex];
            return submission.exercise_title;
          },
          label: (context) => {
            const submission = dashboardData.all_submissions
              .filter(sub => sub.correction?.note !== undefined)
              .sort((a, b) => new Date(a.submission_date) - new Date(b.submission_date))
              [context.dataIndex];
            return [
              `Note: ${context.raw}/20`,
              `Date: ${format(new Date(submission.submission_date), 'dd MMM yyyy', { locale: fr })}`,
              submission.en_retard ? '⚠ En retard' : 'À temps'
            ];
          }
        }
      }
    },
    scales: {
      y: {
        min: 0,
        max: 20,
        ticks: { stepSize: 2 },
        title: { display: true, text: 'Note (/20)' }
      },
      x: {
        title: { display: true, text: 'Historique des soumissions' }
      }
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>;
  }

  if (error) {
    return <div className="bg-red-50 border-l-4 border-red-500 p-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <AlertCircle className="h-5 w-5 text-red-500" />
        </div>
        <div className="ml-3">
          <p className="text-sm text-red-700">
            Erreur: {error}. <button 
              onClick={() => window.location.reload()} 
              className="font-medium underline text-red-700 hover:text-red-600"
            >
              Réessayer
            </button>
          </p>
        </div>
      </div>
    </div>;
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Tableau de bord étudiant</h1>
        <p className="mt-2 text-gray-600">Votre progression académique complète</p>
      </header>

      {/* Statistiques */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Exercices complétés</h2>
            <CheckCircle className="h-6 w-6 text-green-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {dashboardData.stats.completed}/{dashboardData.stats.total}
          </p>
          <p className="mt-1 text-sm text-gray-600">
            {dashboardData.stats.unsubmitted_count} non soumis
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Moyenne générale</h2>
            <BarChart className="h-6 w-6 text-green-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-gray-900">
            {dashboardData.stats.average_score.toFixed(1)}/20
          </p>
          <p className="mt-1 text-sm text-gray-600">
            Basé sur {dashboardData.stats.completed} corrections
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Prochaine échéance</h2>
            <Clock className="h-6 w-6 text-green-500" />
          </div>
          {dashboardData.stats.next_deadline ? (
            <>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {dashboardData.stats.next_deadline.days_left} jours
              </p>
              <p className="mt-1 text-sm text-gray-600 truncate">
                {dashboardData.stats.next_deadline.title}
              </p>
            </>
          ) : (
            <p className="mt-2 text-gray-600">Aucune échéance à venir</p>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Retards</h2>
            <AlertCircle className="h-6 w-6 text-red-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-red-600">
            {dashboardData.stats.late_submissions}
          </p>
          <p className="mt-1 text-sm text-gray-600">
            Soumissions en retard
          </p>
        </div>
      </div>

      {/* Graphique d'évolution */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Évolution de vos notes</h2>
        {dashboardData.all_submissions.filter(sub => sub.correction?.note !== undefined).length > 1 ? (
          <div className="h-80">
            <Line data={prepareChartData()} options={chartOptions} />
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            {dashboardData.all_submissions.length === 0 
              ? "Aucune soumission disponible" 
              : "Pas assez de données pour afficher la progression (minimum 2 notes requises)"}
          </div>
        )}
      </div>

      {/* Toutes les soumissions */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Historique complet des soumissions</h2>
          <span className="text-sm text-gray-500">
            {dashboardData.all_submissions.length} soumissions au total
          </span>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exercice</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Note</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dashboardData.all_submissions
                .slice((pagination.page - 1) * pagination.pageSize, pagination.page * pagination.pageSize)
                .map((submission, index) => (
                  <tr 
                    key={index} 
                    className={`hover:bg-gray-50 cursor-pointer ${submission.en_retard ? 'bg-red-50' : ''}`}
                    onClick={() => navigate(`/submissions/${submission.id}`)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {submission.exercise_title}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {format(new Date(submission.submission_date), 'dd MMM yyyy', { locale: fr })}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {submission.correction ? (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          Corrigé
                        </span>
                      ) : (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                          En attente
                        </span>
                      )}
                      {submission.en_retard && (
                        <span className="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                          Retard
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {submission.correction ? (
                        <span className={`font-semibold ${submission.correction.note >= 10 ? 'text-green-600' : 'text-red-600'}`}>
                          {submission.correction.note}/20
                        </span>
                      ) : '-'}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {dashboardData.all_submissions.length > pagination.pageSize && (
          <div className="flex items-center justify-between mt-4">
            <button 
              onClick={() => setPagination({...pagination, page: Math.max(1, pagination.page - 1)})}
              disabled={pagination.page === 1}
              className="px-4 py-2 border rounded-md disabled:opacity-50"
            >
              Précédent
            </button>
            <span className="text-sm text-gray-700">
              Page {pagination.page} sur {Math.ceil(dashboardData.all_submissions.length / pagination.pageSize)}
            </span>
            <button 
              onClick={() => setPagination({...pagination, page: pagination.page + 1})}
              disabled={pagination.page * pagination.pageSize >= dashboardData.all_submissions.length}
              className="px-4 py-2 border rounded-md disabled:opacity-50"
            >
              Suivant
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;