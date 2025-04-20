import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { useNavigate } from 'react-router-dom';

function CorrectionList() {
  const [corrections, setCorrections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    axios.get('http://127.0.0.1:8000/api/corrections/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then(response => {
        setCorrections(response.data);
      })
      .catch(err => {
        setError('Impossible de récupérer les corrections');
        console.error(err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [navigate]);

  if (loading) {
    return <div className="text-center mt-12">Chargement...</div>;
  }

  if (error) {
    return <div className="text-center text-red-500 mt-12">{error}</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8">Mes corrections</h1>
      {corrections.length === 0 ? (
        <p className="text-center text-gray-600">Aucune correction disponible pour le moment.</p>
      ) : (
        <div className="space-y-6">
          {corrections.map((correction, index) => (
            <div key={index} className="p-6 bg-white shadow rounded-lg border">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                {correction.soumission.exercice_title || 'Exercice'}
              </h2>
              <p className="text-sm text-gray-500 mb-2">
                Soumis le {format(new Date(correction.soumission.date_soumission), 'dd MMMM yyyy', { locale: fr })}
              </p>
              <p className="text-lg font-bold">
                Note : <span className={correction.note >= 10 ? 'text-green-600' : 'text-red-600'}>
                  {correction.note}/20
                </span>
              </p>
              <div className="mt-4 space-y-2 text-sm text-gray-700">
                <p><strong>Feedback :</strong> {correction.feedback || 'Aucun feedback généré.'}</p>
                <p><strong>Points forts :</strong> {correction.points_forts || 'Non précisé.'}</p>
                <p><strong>Points faibles :</strong> {correction.points_faibles || 'Non précisé.'}</p>
              </div>
              {correction.commentaire_professeur && (
                <div className="mt-4 p-3 bg-gray-50 border-l-4 border-blue-500">
                  <p className="text-sm text-blue-800"><strong>Commentaire du professeur :</strong> {correction.commentaire_professeur}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default CorrectionList;
