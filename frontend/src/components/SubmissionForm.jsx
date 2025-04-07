import React, { useState, useEffect } from 'react';
import { Upload, X, CheckCircle } from 'lucide-react';
import axios from 'axios';

function SubmissionForm() {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [selectedExerciseId, setSelectedExerciseId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchExercises = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8000/api/exercices/actifs/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.data && Array.isArray(response.data.data)) {
          setExercises(response.data.data);
        } else {
          setError('Format de données inattendu');
        }
      } catch (err) {
        setError(err.message || "Erreur de connexion au serveur");
      } finally {
        setLoading(false);
      }
    };

    fetchExercises();
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    if (!file || !selectedExerciseId) {
      setError('Veuillez sélectionner un exercice et un fichier');
      setIsSubmitting(false);
      return;
    }

    const formData = new FormData();
    formData.append('exercice', selectedExerciseId);
    formData.append('fichier_pdf', file);
    formData.append('nom_original', file.name);
    formData.append('taille_fichier', file.size.toString());

    try {
      const res = await axios.post('http://localhost:8000/api/soumissions/', formData, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setSuccessMessage('Votre solution a été soumise avec succès !');
      setError(null);
      setFile(null);
      setSelectedExerciseId('');
      
      setTimeout(() => setSuccessMessage(null), 5000);
      
    } catch (err) {
      console.error('Erreur:', {
        status: err.response?.status,
        data: err.response?.data,
        config: err.config
      });
      setError(err.response?.data?.detail || "Erreur lors de la soumission");
      setSuccessMessage(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 mt-16">
      <div className="max-w-2xl mx-auto space-y-8">
        <header className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Soumettre votre solution</h1>
          <p className="mt-2 text-gray-600">Téléchargez votre solution au format PDF</p>
        </header>

        {successMessage && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative">
            {successMessage}
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <label className="block text-sm font-medium text-gray-700">
              Sélectionner l'exercice*
            </label>
            
            {loading ? (
              <div className="text-center py-4">
                <p>Chargement des exercices...</p>
              </div>
            ) : exercises.length > 0 ? (
              <select
                value={selectedExerciseId}
                onChange={(e) => setSelectedExerciseId(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                required
                disabled={isSubmitting}
              >
                <option value="">-- Sélectionnez un exercice --</option>
                {exercises.map((exercise) => (
                  <option key={exercise.id} value={exercise.id}>
                    {exercise.titre} (Date limite: {new Date(exercise.date_limite).toLocaleDateString()})
                  </option>
                ))}
              </select>
            ) : (
              <div className="text-center py-4">
                <p>Aucun exercice disponible pour le moment</p>
              </div>
            )}
          </div>

          <div
            className={`relative border-2 border-dashed rounded-lg p-8 text-center ${
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="flex items-center justify-center space-x-4">
                <CheckCircle className="h-8 w-8 text-green-500" />
                <div className="text-left">
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="text-red-500 hover:text-red-700"
                  disabled={isSubmitting}
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div>
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer rounded-md font-medium text-blue-600 hover:text-blue-500"
                  >
                    <span>Télécharger un fichier</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept=".pdf"
                      onChange={handleChange}
                      disabled={isSubmitting}
                    />
                  </label>
                  <p className="text-gray-500">ou glisser-déposer</p>
                </div>
                <p className="text-sm text-gray-500">PDF jusqu'à 10MB</p>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={!file || !selectedExerciseId || isSubmitting}
            className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
              (!file || !selectedExerciseId || isSubmitting)
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
            }`}
          >
            {isSubmitting ? 'Envoi en cours...' : 'Soumettre la solution'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default SubmissionForm;