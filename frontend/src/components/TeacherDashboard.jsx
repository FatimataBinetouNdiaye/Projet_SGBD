import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Plus, Eye, Edit, Trash, X, ChevronUp, User, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';



const TeacherDashboard = () => {
  // Palette de couleurs verte
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
    lightText: '#607D8B',
    bgLight: '#F5F7FA'
  };

  // États
  const [exercises, setExercises] = useState([]);
  const [classes, setClasses] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const [modeleCorrectionFile, setModeleCorrectionFile] = useState(null);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isEditMode, setIsEditMode] = useState(false);
  const [editId, setEditId] = useState(null);
  const [activeSection, setActiveSection] = useState('info');
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [teacherData, setTeacherData] = useState(null);
  const navigate = useNavigate();
  const formRef = useRef(null);

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

  // Chargement des données
  const loadTeacherData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const headers = { Authorization: `Bearer ${token}` };
      
      // Récupération des données du professeur
      const teacherRes = await axios.get('http://127.0.0.1:8000/api/professors/me/', { headers });
      setTeacherData(teacherRes.data);

      // Récupération des exercices et classes
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

  useEffect(() => {
    loadTeacherData();
  }, [loadTeacherData]);

   // Gestion du scroll dans le modal
   useEffect(() => {
    if (!showModal || !formRef.current) return;

    const handleScroll = () => {
      const formContent = formRef.current;
      setShowScrollTop(formContent.scrollTop > 200);

      const sections = ['info', 'details', 'files', 'publish'];
      const scrollPosition = formContent.scrollTop + 100;

      for (const section of sections) {
        const element = document.getElementById(`section-${section}`);
        if (element && element.offsetTop <= scrollPosition && 
            element.offsetTop + element.offsetHeight > scrollPosition) {
          setActiveSection(section);
          break;
        }
      }
    };

    formRef.current.addEventListener('scroll', handleScroll);
    return () => {
      if (formRef.current) {
        formRef.current.removeEventListener('scroll', handleScroll);
      }
    };
  }, [showModal]);

  const scrollToTop = () => {
    if (formRef.current) {
      formRef.current.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }
  };

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

  // Création/mise à jour d'un exercice
  const handleCreateOrUpdateExercise = async (e) => {
    e.preventDefault();
    setError('');
    const token = localStorage.getItem('token');
    
    const formData = new FormData();
    formData.append('titre', newExercise.titre);
    formData.append('description', newExercise.description);
    formData.append('consignes', newExercise.consignes);
    if (pdfFile) formData.append('fichier_pdf', pdfFile);
    formData.append('difficulte', newExercise.difficulte);
    const deadlineDate = new Date(newExercise.deadline);
    if (!isNaN(deadlineDate.getTime())) {
      formData.append('date_limite', deadlineDate.toISOString());
    }
    
    formData.append('est_publie', newExercise.est_publie);
    if (newExercise.classe) formData.append('classe', newExercise.classe);
    
    if (modeleCorrectionFile) formData.append('modele_correction', modeleCorrectionFile);

    try {
      const headers = {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`
      };

      if (isEditMode && editId) {
        console.log("isEditMode:", isEditMode, "editId:", editId);

        await axios.patch(`http://127.0.0.1:8000/api/exercices/${editId}/`, formData, { headers });
        setSuccessMessage('✅ Les modifications ont été faites avec succès.');
      } else {
        await axios.post('http://127.0.0.1:8000/api/exercices/', formData, { headers });
        setSuccessMessage('✅ Exercice créé avec succès.');
      }
      
      setTimeout(() => setSuccessMessage(''), 3000);
      resetForm();
      loadTeacherData();
    } catch (err) {
      console.error("Erreur complète:", err); // 👈 pour tout voir
      console.error("Détails:", err.response?.data); // 👈 plus ciblé
      setError(
        err.response?.data?.detail ||
        JSON.stringify(err.response?.data) || 
        'Erreur lors de l\'envoi du formulaire'
      );
    }
    
  };

  // Édition d'un exercice
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
    setActiveSection('info');
  };

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
    setActiveSection('info');
  };

  // Suppression d'un exercice
  const handleDeleteExercise = async (id) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer cet exercice ?")) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://127.0.0.1:8000/api/exercices/${id}/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSuccessMessage('Exercice supprimé avec succès');
      setTimeout(() => setSuccessMessage(''), 3000);
      loadTeacherData();
    } catch (err) {
      setError('Erreur lors de la suppression');
    }
  };

  const scrollToSection = (section) => {
    setActiveSection(section);
    const element = document.getElementById(`section-${section}`);
    if (element && formRef.current) {
      formRef.current.scrollTo({
        top: element.offsetTop - 80,
        behavior: 'smooth'
      });
    }
  };
  return (
    <div className="min-h-screen" style={{ backgroundColor: colors.bgLight }}>
      {/* Carte simplifiée */}
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-20">
  <div className="bg-white rounded-lg shadow p-4">
    <div className="flex items-center space-x-3">
      <div className="flex items-center justify-center h-8 w-8 rounded-full" 
           style={{ backgroundColor: colors.brandPrimaryLighter }}>
        <User className="h-4 w-4" style={{ color: colors.brandPrimary }} />
      </div>
      <div>
      <h1 className="text-x1 font-semibold" style={{ color: colors.darkText }}>
          {teacherData ? `${teacherData.first_name} ${teacherData.last_name}` : 'Tableau de bord'}
        </h1>
        <p className="text-xs" style={{ color: colors.lightText }}>Professeur</p>
      </div>
    </div>
  </div>
</div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Section de bienvenue */}
        <div className="mb-8 p-6 rounded-xl shadow-sm  " style={{ backgroundColor: colors.lightBg }}>
          <h2 className="text-2xl font-bold mb-2" style={{ color: colors.brandPrimaryDark }}>
            Tableau de bord professeur
          </h2>
          <p style={{ color: colors.lightText }}>
            {teacherData && `Bienvenue ${teacherData.first_name}, gérez vos exercices ici.`}
          </p>
        </div>

        {/* Messages d'alerte */}
        {successMessage && (
          <div className="mb-4 p-3 rounded-md" style={{ backgroundColor: colors.brandPrimaryLighter, color: colors.brandPrimaryDark }}>
            {successMessage}
          </div>
        )}
        {error && (
          <div className="mb-4 p-3 rounded-md" style={{ backgroundColor: '#FFEBEE', color: colors.danger }}>
            {error}
          </div>
        )}

        {/* Bouton d'action principal */}
        <div className="flex justify-end mb-8">
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center px-5 py-3 rounded-lg text-white shadow-md hover:shadow-lg transition-all"
            style={{ 
              backgroundColor: colors.brandPrimary,
              '&:hover': { backgroundColor: colors.brandPrimaryDark }
            }}
          >
            <Plus className="h-5 w-5 mr-2" />
            Nouvel exercice
          </button>
        </div>

        {/* Tableau des exercices - version améliorée */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="p-4 border-b border-gray-200 flex justify-between items-center">
            <div>
              <h3 className="text-lg font-medium" style={{ color: colors.darkText }}>Vos exercices</h3>
              <p className="text-sm" style={{ color: colors.lightText }}>{exercises.length} exercice(s) au total</p>
            </div>
          </div>
          
          {exercises.length === 0 ? (
            <div className="p-8 text-center">
              <p style={{ color: colors.lightText }}>Vous n'avez pas encore créé d'exercices</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: colors.lightText }}>Titre</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: colors.lightText }}>Difficulté</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: colors.lightText }}>Date limite</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: colors.lightText }}>Statut</th>
                    <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider" style={{ color: colors.lightText }}>Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {exercises.map((ex) => (
                    <tr key={ex.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium" style={{ color: colors.darkText }}>{ex.titre}</div>
                        <div className="text-sm mt-1" style={{ color: colors.lightText }}>{ex.description.substring(0, 60)}...</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          ex.difficulte === 'Facile' ? 'bg-green-100 text-green-800' :
                          ex.difficulte === 'Difficile' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {ex.difficulte}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm" style={{ color: colors.darkText }}>
                          {ex.date_limite ? new Date(ex.date_limite).toLocaleDateString('fr-FR') : 'Non définie'}
                        </div>
                        {ex.date_limite && (
                          <div className="text-xs mt-1" style={{ color: colors.lightText }}>
                            {new Date(ex.date_limite).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {ex.est_publie ? (
                          <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                            Publié
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                            Brouillon
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end space-x-2">
                          <button 
                            onClick={() => openEditModal(ex)}
                            className="p-2 rounded-full hover:bg-gray-100"
                            title="Modifier"
                          >
                            <Edit className="h-5 w-5" style={{ color: colors.brandPrimary }} />
                          </button>
                          <button 
                            onClick={() => handleDeleteExercise(ex.id)}
                            className="p-2 rounded-full hover:bg-gray-100"
                            title="Supprimer"
                          >
                            <Trash className="h-5 w-5" style={{ color: colors.danger }} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal de création/édition - version améliorée */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 pt-20">
            <div className="bg-white rounded-xl shadow-xl max-w-5xl w-full flex flex-col md:flex-row" style={{ maxHeight: 'calc(100vh - 8rem)' }}>
              {/* Barre de navigation verticale */}
              <div className="w-full md:w-56 p-4 border-b md:border-b-0 md:border-r" style={{ backgroundColor: colors.lightBg }}>
                <h4 className="font-medium mb-4 sticky top-0 py-2" style={{ backgroundColor: colors.lightBg, color: colors.darkText }}>
                  Navigation
                </h4>
                <nav className="flex md:flex-col space-x-2 md:space-x-0 md:space-y-2 overflow-x-auto md:overflow-x-visible pb-2 md:pb-0">
                  <button 
                    type="button"
                    onClick={() => scrollToSection('info')}
                    className={`px-3 py-2 text-sm rounded whitespace-nowrap ${
                      activeSection === 'info' 
                        ? 'bg-white shadow-sm font-medium' 
                        : 'hover:bg-white'
                    }`}
                    style={{ 
                      color: activeSection === 'info' ? colors.brandPrimaryDark : colors.darkText,
                      backgroundColor: activeSection === 'info' ? 'white' : 'transparent'
                    }}
                  >
                    Informations de base
                  </button>
                  <button 
                    type="button"
                    onClick={() => scrollToSection('details')}
                    className={`px-3 py-2 text-sm rounded whitespace-nowrap ${
                      activeSection === 'details' 
                        ? 'bg-white shadow-sm font-medium' 
                        : 'hover:bg-white'
                    }`}
                    style={{ 
                      color: activeSection === 'details' ? colors.brandPrimaryDark : colors.darkText,
                      backgroundColor: activeSection === 'details' ? 'white' : 'transparent'
                    }}
                  >
                    Détails
                  </button>
                  <button 
                    type="button"
                    onClick={() => scrollToSection('files')}
                    className={`px-3 py-2 text-sm rounded whitespace-nowrap ${
                      activeSection === 'files' 
                        ? 'bg-white shadow-sm font-medium' 
                        : 'hover:bg-white'
                    }`}
                    style={{ 
                      color: activeSection === 'files' ? colors.brandPrimaryDark : colors.darkText,
                      backgroundColor: activeSection === 'files' ? 'white' : 'transparent'
                    }}
                  >
                    Fichiers
                  </button>
                  <button 
                    type="button"
                    onClick={() => scrollToSection('publish')}
                    className={`px-3 py-2 text-sm rounded whitespace-nowrap ${
                      activeSection === 'publish' 
                        ? 'bg-white shadow-sm font-medium' 
                        : 'hover:bg-white'
                    }`}
                    style={{ 
                      color: activeSection === 'publish' ? colors.brandPrimaryDark : colors.darkText,
                      backgroundColor: activeSection === 'publish' ? 'white' : 'transparent'
                    }}
                  >
                    Publication
                  </button>
                </nav>
              </div>

              {/* Contenu principal avec scroll */}
              <div className="flex-1 flex flex-col">
                {/* En-tête fixe */}
                <div className="sticky top-0 bg-white z-10 px-6 py-4 border-b flex justify-between items-center">
                  <h3 className="text-xl font-bold" style={{ color: colors.darkText }}>
                    {isEditMode ? 'Modifier un exercice' : 'Créer un nouvel exercice'}
                  </h3>
                  <button onClick={resetForm} style={{ color: colors.lightText }} className="hover:text-gray-700">
                    <X className="h-6 w-6" />
                  </button>
                </div>

                {/* Contenu scrollable */}
                <div 
                  ref={formRef}
                  className="flex-1 overflow-y-auto p-6"
                >
                  <form onSubmit={handleCreateOrUpdateExercise} className="space-y-6">
                    {/* Section Informations de base */}
                    <section 
                      id="section-info" 
                      className="scroll-mt-20 pb-6 mb-6 border-b border-gray-100"
                    >
                      <h4 className="font-medium text-lg mb-4" style={{ color: colors.darkText }}>
                        Informations de base
                      </h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>Titre*</label>
                          <input
                            type="text"
                            value={newExercise.titre}
                            onChange={(e) => setNewExercise({...newExercise, titre: e.target.value})}
                            className="w-full rounded-lg border-gray-300 focus:border-green-500 focus:ring-green-500 px-3 py-2"
                            required
                            style={{ borderColor: colors.brandPrimaryLight }}
                            placeholder="Titre de l'exercice"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>Description*</label>
                          <textarea
                            value={newExercise.description}
                            onChange={(e) => setNewExercise({...newExercise, description: e.target.value})}
                            className="w-full rounded-lg border-gray-300 focus:border-green-500 focus:ring-green-500 px-3 py-2"
                            rows={3}
                            required
                            style={{ borderColor: colors.brandPrimaryLight }}
                            placeholder="Description détaillée de l'exercice"
                          />
                        </div>
                      </div>
                    </section>

                    {/* Section Détails de l'exercice */}
                    <section 
                      id="section-details" 
                      className="scroll-mt-20 pb-6 mb-6 border-b border-gray-100"
                    >
                      <h4 className="font-medium text-lg mb-4" style={{ color: colors.darkText }}>
                        Détails de l'exercice
                      </h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>Consignes*</label>
                          <textarea
                            value={newExercise.consignes}
                            onChange={(e) => setNewExercise({...newExercise, consignes: e.target.value})}
                            className="w-full rounded-lg border-gray-300 focus:border-green-500 focus:ring-green-500 px-3 py-2"
                            rows={3}
                            required
                            style={{ borderColor: colors.brandPrimaryLight }}
                            placeholder="Consignes pour les étudiants"
                          />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>Difficulté*</label>
                            <select
                              value={newExercise.difficulte}
                              onChange={(e) => setNewExercise({...newExercise, difficulte: e.target.value})}
                              className="w-full rounded-lg border-gray-300 focus:border-green-500 focus:ring-green-500 px-3 py-2"
                              required
                              style={{ borderColor: colors.brandPrimaryLight }}
                            >
                              <option value="Facile">Facile</option>
                              <option value="Moyenne">Moyenne</option>
                              <option value="Difficile">Difficile</option>
                            </select>
                          </div>

                          <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>Classe</label>
                            <select
                              value={newExercise.classe}
                              onChange={(e) => setNewExercise({...newExercise, classe: e.target.value})}
                              className="w-full rounded-lg border-gray-300 focus:border-green-500 focus:ring-green-500 px-3 py-2"
                              style={{ borderColor: colors.brandPrimaryLight }}
                            >
                              <option value="">Sélectionnez une classe</option>
                              {classes.map(classe => (
                                <option key={classe.id} value={classe.id}>{classe.nom}</option>
                              ))}
                            </select>
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>Date limite*</label>
                          <input
                            type="datetime-local"
                            value={newExercise.deadline}
                            onChange={(e) => setNewExercise({...newExercise, deadline: e.target.value})}
                            className="w-full rounded-lg border-gray-300 focus:border-green-500 focus:ring-green-500 px-3 py-2"
                            required
                            style={{ borderColor: colors.brandPrimaryLight }}
                          />
                        </div>
                      </div>
                    </section>

                    {/* Section Fichiers joints */}
                    <section 
                      id="section-files" 
                      className="scroll-mt-20 pb-6 mb-6 border-b border-gray-100"
                    >
                      <h4 className="font-medium text-lg mb-4" style={{ color: colors.darkText }}>
                        Fichiers joints
                      </h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>Fichier PDF*</label>
                          <div className="flex items-center">
                            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer hover:bg-gray-50">
                              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                <svg className="w-8 h-8 mb-4" style={{ color: colors.brandPrimary }} aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                                </svg>
                                <p className="mb-2 text-sm" style={{ color: colors.lightText }}>
                                  <span className="font-semibold">Cliquez pour uploader</span> ou glissez-déposez
                                </p>
                                <p className="text-xs" style={{ color: colors.lightText }}>PDF (MAX. 10MB)</p>
                              </div>
                              <input 
                                type="file" 
                                accept=".pdf" 
                                onChange={handleFileChange} 
                                className="hidden" 
                                required
                              />
                            </label>
                          </div>
                          {pdfFile && (
                            <div className="mt-2 text-sm flex items-center" style={{ color: colors.brandPrimary }}>
                              <svg className="w-4 h-4 mr-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 20">
                                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 18a.969.969 0 0 0 .933 1h12.134A.97.97 0 0 0 15 18M1 7V5.828a2 2 0 0 1 .586-1.414l2.828-2.828A2 2 0 0 1 5.828 1h8.239A.97.97 0 0 1 15 2v5M6 1v4a1 1 0 0 1-1 1H1m0 9v-5h1.5a1.5 1.5 0 1 1 0 3H1m12-3v-5h1.375a1.125 1.125 0 0 1 0 2.25H13Zm-9-3h1.5a1.5 1.5 0 1 1 0 3H4"/>
                              </svg>
                              {pdfFile.name}
                            </div>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>
                            Modèle de correction (optionnel)
                          </label>
                          <div className="flex items-center">
                            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer hover:bg-gray-50">
                              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                <svg className="w-8 h-8 mb-4" style={{ color: colors.brandPrimary }} aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                                </svg>
                                <p className="mb-2 text-sm" style={{ color: colors.lightText }}>
                                  <span className="font-semibold">Cliquez pour uploader</span> ou glissez-déposez
                                </p>
                                <p className="text-xs" style={{ color: colors.lightText }}>PDF, DOC, DOCX (MAX. 10MB)</p>
                              </div>
                              <input 
                                type="file" 
                                accept=".pdf,.doc,.docx" 
                                onChange={handleCorrectionFileChange} 
                                className="hidden" 
                              />
                            </label>
                          </div>
                          {modeleCorrectionFile && (
                            <div className="mt-2 text-sm flex items-center" style={{ color: colors.brandPrimary }}>
                              <svg className="w-4 h-4 mr-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 20">
                                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 18a.969.969 0 0 0 .933 1h12.134A.97.97 0 0 0 15 18M1 7V5.828a2 2 0 0 1 .586-1.414l2.828-2.828A2 2 0 0 1 5.828 1h8.239A.97.97 0 0 1 15 2v5M6 1v4a1 1 0 0 1-1 1H1m0 9v-5h1.5a1.5 1.5 0 1 1 0 3H1m12-3v-5h1.375a1.125 1.125 0 0 1 0 2.25H13Zm-9-3h1.5a1.5 1.5 0 1 1 0 3H4"/>
                              </svg>
                              {modeleCorrectionFile.name}
                            </div>
                          )}
                        </div>
                      </div>
                    </section>

                    {/* Section Publication */}
                    <section 
                      id="section-publish" 
                      className="scroll-mt-20"
                    >
                      <h4 className="font-medium text-lg mb-4" style={{ color: colors.darkText }}>
                        Publication
                      </h4>
                      <div className="flex items-center">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={newExercise.est_publie} 
                            onChange={(e) => setNewExercise({...newExercise, est_publie: e.target.checked})}
                            className="sr-only peer" 
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                          <span className="ml-3 text-sm font-medium" style={{ color: colors.darkText }}>
                            {newExercise.est_publie ? 'Publié' : 'Brouillon'}
                          </span>
                        </label>
                      </div>
                      <p className="mt-2 text-sm" style={{ color: colors.lightText }}>
                        {newExercise.est_publie 
                          ? 'Cet exercice sera visible par les étudiants immédiatement' 
                          : 'Cet exercice ne sera pas visible par les étudiants'}
                      </p>
                    </section>

                    {error && (
                      <div className="p-4 text-sm rounded-lg" style={{ backgroundColor: '#FFEBEE', color: colors.danger }}>
                        {error}
                      </div>
                    )}

                    <div className="flex justify-end space-x-3 pt-6">
                      <button
                        type="button"
                        onClick={resetForm}
                        className="px-4 py-2 rounded-lg text-sm font-medium border border-gray-300"
                        style={{ 
                          color: colors.darkText,
                          '&:hover': { backgroundColor: '#F5F5F5' }
                        }}
                      >
                        Annuler
                      </button>
                      <button
                        type="submit"
                        className="px-4 py-2 rounded-lg text-white text-sm font-medium shadow-sm hover:shadow-md transition-all"
                        style={{ backgroundColor: colors.brandPrimary }}
                      >
                        {isEditMode ? 'Mettre à jour' : 'Créer l\'exercice'}
                      </button>
                    </div>
                  </form>
                </div>

                {/* Bouton de retour en haut */}
                {showScrollTop && (
                  <button
                    onClick={scrollToTop}
                    className="fixed right-8 bottom-8 p-3 rounded-full shadow-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                    style={{ backgroundColor: 'white' }}
                    aria-label="Remonter en haut"
                  >
                    <ChevronUp className="h-5 w-5" style={{ color: colors.brandPrimary }} />
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default TeacherDashboard;