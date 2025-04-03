import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Users, Book, Plus, Eye, Edit, Trash, X, Upload } from 'lucide-react';

function TeacherDashboard() {
  // Couleurs du thème avec brandPrimary verte
  const colors = {
    brandPrimary: '#4CAF4F',
    brandPrimaryLight: '#81C784',
    brandPrimaryLighter: '#C8E6C9',
    brandPrimaryDark: '#388E3C',
    success: '#4CAF4F',
    warning: '#FFC107',
    danger: '#F44336',
    info: '#2196F3',
    lightBg: '#E8F5E9',
    darkText: '#263238',
    lightText: '#607D8B'
  };

  const [exercises, setExercises] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const [newExercise, setNewExercise] = useState({
    titre: '',
    description: '',
    difficulte: 'Moyenne',
    deadline: '',
  });
  const [stats, setStats] = useState({
    totalStudents: 0,
    totalExercises: 0,
    averageScore: 0,
  });
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    try {
      const exercisesResponse = await axios.get('http://127.0.0.1:8000/api/exercices/');
      const statsResponse = await axios.get('http://127.0.0.1:8000/api/stats/');

      setExercises(exercisesResponse.data);
      setStats(statsResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Erreur lors de la récupération des données');
    }
  }

  async function handleCreateExercise(e) {
    e.preventDefault();
    setError('');

    try {
      const formData = new FormData();
      formData.append('titre', newExercise.titre);
      formData.append('description', newExercise.description);
      formData.append('difficulte', newExercise.difficulte);
      formData.append('deadline', newExercise.deadline);
      if (pdfFile) {
        formData.append('fichier_pdf', pdfFile);
      }

      const response = await axios.post('http://127.0.0.1:8000/api/exercices/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setShowModal(false);
      setNewExercise({
        titre: '',
        description: '',
        difficulte: 'Moyenne',
        deadline: '',
      });
      setPdfFile(null);
      fetchData();
    } catch (error) {
      console.error('Error creating exercise:', error);
      setError('Erreur lors de la création de l\'exercice');
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setPdfFile(file);
    } else {
      setError('Veuillez sélectionner un fichier PDF');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Tableau de bord professeur</h1>
          <p className="mt-2 text-gray-600">Gérez vos exercices et suivez les progrès des étudiants</p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Étudiants inscrits</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalStudents}</p>
                <p className="text-xs text-green-500 mt-1">+5% ce mois</p>
              </div>
              <div className="p-3 rounded-full" style={{ backgroundColor: colors.lightBg }}>
                <Users className="h-6 w-6" style={{ color: colors.brandPrimary }} />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Exercices créés</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalExercises}</p>
                <p className="text-xs text-green-500 mt-1">+2 cette semaine</p>
              </div>
              <div className="p-3 rounded-full" style={{ backgroundColor: colors.lightBg }}>
                <Book className="h-6 w-6" style={{ color: colors.brandPrimary }} />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Score moyen</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stats.averageScore.toFixed(1)}%</p>
                <p className="text-xs text-green-500 mt-1">+3% vs dernier mois</p>
              </div>
              <div className="p-3 rounded-full" style={{ backgroundColor: colors.lightBg }}>
                <BarChart className="h-6 w-6" style={{ color: colors.brandPrimary }} />
              </div>
            </div>
          </div>
        </div>

        {/* Exercises Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
            <div>
              <h2 className="text-xl font-bold text-gray-900">Exercices</h2>
              <p className="text-sm text-gray-500 mt-1">Liste de tous vos exercices assignés</p>
            </div>
            <button 
              onClick={() => setShowModal(true)}
              className="flex items-center px-4 py-2 rounded-xl hover:shadow-md transition-all"
              style={{ 
                backgroundColor: colors.brandPrimary, 
                color: 'white',
                '&:hover': {
                  backgroundColor: colors.brandPrimaryDark
                }
              }}
            >
              <Plus className="h-4 w-4 mr-2" />
              Nouvel exercice
            </button>
          </div>

          <div className="overflow-x-auto rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Titre</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Difficulté</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date limite</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Professeur</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {exercises.map((exercise) => (
                  <tr key={exercise.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{exercise.titre}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                        exercise.difficulte === 'Facile' ? 'bg-green-100 text-green-800' :
                        exercise.difficulte === 'Moyenne' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {exercise.difficulte}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                      {new Date(exercise.deadline).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                      {exercise.professeur.username}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex space-x-3">
                        <button 
                          className="p-1.5 rounded-lg hover:bg-gray-100"
                          title="Voir"
                        >
                          <Eye className="h-4 w-4 text-gray-600" />
                        </button>
                        <button 
                          className="p-1.5 rounded-lg hover:bg-gray-100"
                          title="Modifier"
                        >
                          <Edit className="h-4 w-4 text-gray-600" />
                        </button>
                        <button 
                          className="p-1.5 rounded-lg hover:bg-gray-100"
                          title="Supprimer"
                        >
                          <Trash className="h-4 w-4 text-gray-600" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Create Exercise Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-gray-900">Créer un nouvel exercice</h3>
                <button 
                  onClick={() => setShowModal(false)} 
                  className="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <form onSubmit={handleCreateExercise} className="space-y-4">
                <div>
                  <label htmlFor="titre" className="block text-sm font-medium text-gray-700 mb-1">
                    Titre
                  </label>
                  <input
                    type="text"
                    id="titre"
                    value={newExercise.titre}
                    onChange={(e) => setNewExercise({...newExercise, titre: e.target.value})}
                    className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 focus:ring-offset-1 focus:ring-green-500 focus:border-green-500"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    id="description"
                    value={newExercise.description}
                    onChange={(e) => setNewExercise({...newExercise, description: e.target.value})}
                    rows={4}
                    className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 focus:ring-offset-1 focus:ring-green-500 focus:border-green-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="difficulte" className="block text-sm font-medium text-gray-700 mb-1">
                      Difficulté
                    </label>
                    <select
                      id="difficulte"
                      value={newExercise.difficulte}
                      onChange={(e) => setNewExercise({...newExercise, difficulte: e.target.value})}
                      className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 focus:ring-offset-1 focus:ring-green-500 focus:border-green-500"
                    >
                      <option>Facile</option>
                      <option>Moyenne</option>
                      <option>Difficile</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="deadline" className="block text-sm font-medium text-gray-700 mb-1">
                      Date limite
                    </label>
                    <input
                      type="datetime-local"
                      id="deadline"
                      value={newExercise.deadline}
                      onChange={(e) => setNewExercise({...newExercise, deadline: e.target.value})}
                      className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:ring-2 focus:ring-offset-1 focus:ring-green-500 focus:border-green-500"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="pdf" className="block text-sm font-medium text-gray-700 mb-1">
                    Fichier PDF
                  </label>
                  <div className="mt-1">
                    <label className="w-full flex flex-col items-center px-4 py-6 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-green-500 hover:bg-green-50 transition-all">
                      <Upload className="h-8 w-8 mb-2" style={{ color: colors.brandPrimary }} />
                      <p className="text-sm text-center">
                        {pdfFile ? (
                          <span className="font-medium">{pdfFile.name}</span>
                        ) : (
                          <>
                            <span className="font-medium" style={{ color: colors.brandPrimary }}>Cliquez pour télécharger</span>
                            <span className="block text-xs text-gray-500 mt-1">ou glissez-déposez un fichier PDF</span>
                          </>
                        )}
                      </p>
                      <input
                        type="file"
                        id="pdf"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="sr-only"
                      />
                    </label>
                  </div>
                </div>

                {error && <p className="text-red-500 text-sm">{error}</p>}

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-lg hover:shadow-md transition-all"
                    style={{ 
                      backgroundColor: colors.brandPrimary, 
                      color: 'white',
                      '&:hover': {
                        backgroundColor: colors.brandPrimaryDark
                      }
                    }}
                  >
                    Créer l'exercice
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default TeacherDashboard;