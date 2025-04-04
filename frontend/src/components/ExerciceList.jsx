import React, { useState, useEffect } from 'react';
import { FileText, Clock, ArrowRight, Search } from 'lucide-react';
import axios from 'axios';

const ExerciceList = () => {
  const [exercises, setExercises] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDifficulty, setFilterDifficulty] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const exercisesPerPage = 5;
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem("token"); // 🔑 Corrigé ici : "token" et non "access_token"
    console.log("Token récupéré:", token);

    if (!token) {
      setError("Aucun token trouvé. Veuillez vous reconnecter.");
      return;
    }

    axios
      .get("http://127.0.0.1:8000/api/exercices/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((response) => {
        setExercises(response.data);
      })
      .catch((error) => {
        console.error("Erreur lors de la récupération des exercices :", error);
        setError("Erreur lors du chargement des exercices.");
      });
  }, []);

  const getDifficulty = (ponderation) => {
    if (typeof ponderation === 'number') return computeLevel(ponderation);
    
    if (typeof ponderation === 'object' && Object.keys(ponderation).length > 0) {
      const total = Object.values(ponderation).reduce((sum, val) => sum + parseInt(val || 0), 0);
      return computeLevel(total / Object.keys(ponderation).length); // moyenne
    }
  
    return 'Inconnue';
  };
  
  const computeLevel = (p) => {
    if (isNaN(p)) return 'Inconnue';
    if (p < 30) return 'Easy';
    if (p < 70) return 'Medium';
    return 'Hard';
  };
  
  

  const filteredExercises = exercises.filter((exercise) => {
    const matchesSearch =
      exercise.titre.toLowerCase().includes(searchTerm.toLowerCase()) ||
      exercise.description.toLowerCase().includes(searchTerm.toLowerCase());
    const difficulty = getDifficulty(exercise.ponderation);
    const matchesDifficulty = filterDifficulty === 'all' || difficulty === filterDifficulty;
    return matchesSearch && matchesDifficulty;
  });

  const indexOfLastExercise = currentPage * exercisesPerPage;
  const indexOfFirstExercise = indexOfLastExercise - exercisesPerPage;
  const currentExercises = filteredExercises.slice(indexOfFirstExercise, indexOfLastExercise);
  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <div className="space-y-8 p-6 mt-16">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Exercices Disponibles</h1>
        <p className="mt-2 text-gray-600">
          Effectuez ces exercices pour améliorer vos compétences en bases de données
        </p>
      </header>

      {/* Affichage erreur */}
      {error && (
        <div className="bg-red-100 text-red-700 p-4 rounded">
          {error}
        </div>
      )}

      <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0 md:space-x-4">
        <div className="relative w-full md:w-1/2">
          <input
            type="text"
            placeholder="Rechercher un exercice..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-brandPrimary"
          />
          <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
        </div>
        <select
          value={filterDifficulty}
          onChange={(e) => setFilterDifficulty(e.target.value)}
          className="w-full md:w-1/4 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-brandPrimary"
        >
          <option value="all">Tous les niveaux</option>
          <option value="Easy">Facile</option>
          <option value="Medium">Moyen</option>
          <option value="Hard">Difficile</option>
        </select>
      </div>

      <div className="grid gap-6">
        {currentExercises.map((exercise) => {
          const difficulty = getDifficulty(exercise.ponderation);
          return (
            <div key={exercise.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <FileText className="h-6 w-6 text-brandPrimary" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">{exercise.titre}</h2>
                    <p className="mt-1 text-gray-600">{exercise.description}</p>
                    <div className="mt-2 flex items-center space-x-4">
                      <div className="flex items-center text-sm text-gray-500">
                        <Clock className="h-4 w-4 mr-1" />
                        <span>
                          À rendre avant{' '}
                          {exercise.date_limite
                            ? new Date(exercise.date_limite).toLocaleString()
                            : '—'}
                        </span>
                      </div>
                      <span
                        className={`px-2 py-1 text-sm rounded-full ${
                          difficulty === 'Easy'
                            ? 'bg-green-100 text-green-800'
                            : difficulty === 'Medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : difficulty === 'Hard'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {difficulty}
                      </span>
                    </div>
                  </div>
                </div>
                <button className="flex items-center text-blue-600 hover:text-blue-700">
                  <span className="mr-1">Commencer</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Pagination */}
      <div className="flex justify-center space-x-2">
        {Array.from({ length: Math.ceil(filteredExercises.length / exercisesPerPage) }, (_, i) => (
          <button
            key={i + 1}
            onClick={() => paginate(i + 1)}
            className={`px-4 py-2 rounded-lg ${
              currentPage === i + 1
                ? 'bg-brandPrimary text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {i + 1}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ExerciceList;
