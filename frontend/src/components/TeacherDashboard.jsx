import React, { useState, useEffect, useRef, useCallback  } from 'react';
import axios from 'axios';
import { Plus, Eye, Edit, Trash, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const TeacherDashboard = () => {
  // Couleurs du thème
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

  // États
  const [exercises, setExercises] = useState([]);
  const [classes, setClasses] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const [modeleCorrectionFile, setModeleCorrectionFile] = useState(null);
  const [error, setError] = useState('');
  const [isEditMode, setIsEditMode] = useState(false);
  const [editId, setEditId] = useState(null);
  const navigate = useNavigate();

  const initialExerciseState = {
    titre: '',
    description: '',
    difficulte: 'Moyenne',
    deadline: '',
    consignes: '',
    classe: '',
    est_publie: false
  };

  const [newExercise, setNewExercise] = useState(initialExerciseState);

  // Chargement des données initiales
  const hasNavigatedRef = useRef(false);

  const loadData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
  
      const headers = { Authorization: `Bearer ${token}` };
      
      // Récupérer les exercices du professeur connecté
      const exercisesRes = await axios.get('http://127.0.0.1:8000/api/exercices/', { headers });
      const classesRes = await axios.get('http://127.0.0.1:8000/api/classes/', { headers });
  
      setExercises(exercisesRes.data);
      setClasses(classesRes.data);
    } catch (error) {
      console.error("Erreur:", error);
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      }
    }
  }, [navigate]);
  // 2. Utilisez cette fonction dans un useEffect simplifié
  useEffect(() => {
    if (!hasNavigatedRef.current) {
      loadData();
      hasNavigatedRef.current = true;
    }
  }, [loadData]);

  // Gestion des fichiers
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setPdfFile(file);
      setError('');
    } else {
      setError('Veuillez sélectionner un fichier PDF valide');
      e.target.value = '';
    }
  };

  const handleCorrectionFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setModeleCorrectionFile(file);
      setError('');
    }
  };

  const handleCreateOrUpdateExercise = async (e) => {
    e.preventDefault();
    setError('');
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
  
    const formData = new FormData();
    formData.append('titre', newExercise.titre);
    formData.append('description', newExercise.description);
    formData.append('consignes', newExercise.consignes);
    formData.append('difficulte', newExercise.difficulte); // Ajout du champ difficulté
    formData.append('date_limite', new Date(newExercise.deadline).toISOString()); // Correction du nom et format
    
    formData.append('est_publie', newExercise.est_publie);
    if (newExercise.classe) formData.append('classe', newExercise.classe);
    
    const difficulteToPonderation = {
      'Facile': { score: 20 },
      'Moyenne': { score: 50 },
      'Difficile': { score: 80 }
    };
    formData.append('ponderation', JSON.stringify(difficulteToPonderation[newExercise.difficulte]));
    
    if (pdfFile) formData.append('fichier_consigne', pdfFile);
    if (modeleCorrectionFile) formData.append('modele_correction', modeleCorrectionFile);
  
    try {
      const headers = {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`
      };
  
      if (isEditMode && editId) {
        await axios.put(`http://127.0.0.1:8000/api/exercices/${editId}/`, formData, { headers });
      } else {
        await axios.post('http://127.0.0.1:8000/api/exercices/', formData, { headers });
      }
  
      resetForm();
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'envoi du formulaire');
    }
  };
  
  // Dans la fonction openEditModal, corrigez la date :
  const openEditModal = (exercise) => {
    setNewExercise({
      titre: exercise.titre,
      description: exercise.description,
      difficulte: exercise.difficulte || 'Moyenne',
      deadline: exercise.date_limite ? formatDateForInput(exercise.date_limite) : '',
      consignes: exercise.consignes,
      classe: exercise.classe?.id || '',
      est_publie: exercise.est_publie
    });
    setEditId(exercise.id);
    setIsEditMode(true);
    setShowModal(true);
  };
  
  // Ajoutez cette fonction utilitaire pour formater la date
  const formatDateForInput = (dateString) => {
    const date = new Date(dateString);
    date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return date.toISOString().slice(0, 16);
  };

  const resetForm = () => {
    setShowModal(false);
    setNewExercise(initialExerciseState);
    setPdfFile(null);
    setModeleCorrectionFile(null);
    setIsEditMode(false);
    setEditId(null);
  };

  

  const handleDeleteExercise = async (id) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer cet exercice ?")) return;
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      await axios.delete(`http://127.0.0.1:8000/api/exercices/${id}/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Mettre à jour la liste après suppression
      const headers = { Authorization: `Bearer ${token}` };
      const exercisesRes = await axios.get('http://127.0.0.1:8000/api/exercices/', { headers });
      setExercises(exercisesRes.data);
    } catch (err) {
      console.error('Erreur lors de la suppression:', err);
    }
  };

  return (
    <div className="bg-gray-50 p-8 min-h-screen px-8 pt-24">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Tableau de bord professeur</h1>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center px-4 py-2 rounded-lg text-white"
            style={{ backgroundColor: colors.brandPrimary }}
          >
            <Plus className="h-4 w-4 mr-2" />
            Nouvel exercice
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Titre</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Difficulté</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date limite</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {exercises.map((ex) => (
                <tr key={ex.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{ex.titre}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      ex.difficulte === 'Facile' ? 'bg-green-100 text-green-800' :
                      ex.difficulte === 'Difficile' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {ex.difficulte}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
  {ex.date_limite ? new Date(ex.date_limite).toLocaleDateString() : 'Non définie'}
</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button className="text-blue-500 hover:text-blue-700">
                        <Eye className="h-5 w-5" />
                      </button>
                      <button 
                        onClick={() => openEditModal(ex)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        <Edit className="h-5 w-5" />
                      </button>
                      <button 
                        onClick={() => handleDeleteExercise(ex.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash className="h-5 w-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Modal de création/édition */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full">
              <div className="flex justify-between items-center border-b p-4">
                <h3 className="text-xl font-bold">
                  {isEditMode ? 'Modifier un exercice' : 'Créer un nouvel exercice'}
                </h3>
                <button onClick={resetForm} className="text-gray-500 hover:text-gray-700">
                  <X className="h-6 w-6" />
                </button>
              </div>
              <form onSubmit={handleCreateOrUpdateExercise} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Titre*</label>
                  <input
                    type="text"
                    value={newExercise.titre}
                    onChange={(e) => setNewExercise({...newExercise, titre: e.target.value})}
                    className="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description*</label>
                  <textarea
                    value={newExercise.description}
                    onChange={(e) => setNewExercise({...newExercise, description: e.target.value})}
                    className="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                    rows={4}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Consignes*</label>
                  <textarea
                    value={newExercise.consignes}
                    onChange={(e) => setNewExercise({...newExercise, consignes: e.target.value})}
                    className="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                    rows={2}
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Difficulté*</label>
                    <select
                      value={newExercise.difficulte}
                      onChange={(e) => setNewExercise({...newExercise, difficulte: e.target.value})}
                      className="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                      required
                    >
                      <option value="Facile">Facile</option>
                      <option value="Moyenne">Moyenne</option>
                      <option value="Difficile">Difficile</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Classe</label>
                    <select
                      value={newExercise.classe}
                      onChange={(e) => setNewExercise({...newExercise, classe: e.target.value})}
                      className="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="">Sélectionnez une classe</option>
                      {classes.map(classe => (
                        <option key={classe.id} value={classe.id}>{classe.nom}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date limite*</label>
                  <input
                    type="datetime-local"
                    value={newExercise.deadline}
                    onChange={(e) => setNewExercise({...newExercise, deadline: e.target.value})}
                    className="w-full rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Fichier PDF</label>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Modèle de correction
                    {modeleCorrectionFile && (
                      <span className="ml-2 text-green-600">(Fichier sélectionné)</span>
                    )}
                  </label>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleCorrectionFileChange}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="publish"
                    checked={newExercise.est_publie}
                    onChange={(e) => setNewExercise({...newExercise, est_publie: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="publish" className="ml-2 block text-sm text-gray-900">
                    Publier immédiatement
                  </label>
                </div>

                {error && (
                  <div className="p-4 text-sm text-red-700 bg-red-100 rounded-lg">
                    {error}
                  </div>
                )}

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={resetForm}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-lg text-white"
                    style={{ backgroundColor: colors.brandPrimary }}
                  >
                    {isEditMode ? 'Mettre à jour' : 'Créer'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherDashboard;