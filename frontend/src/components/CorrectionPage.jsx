import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { MessageSquareText, FileCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
const CorrectionPage = () => {
  const [corrections, setCorrections] = useState([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("token");
      
      if (!token) {
        navigate('/connexion');
        return;
      }

      try {
        // 1. Récupérer l'utilisateur connecté
        const userResponse = await axios.get(
          "http://127.0.0.1:8000/api/utilisateur-connecte/",
          { headers: { Authorization: `Bearer ${token}` } }
        );

        console.log("Utilisateur:", userResponse.data);

        // 2. Vérification du rôle (version robuste)
        const isEtudiant = userResponse.data.role === 'ET' || 
                         userResponse.data.is_etudiant ||
                         userResponse.data.groups?.includes('ETUDIANT');

        if (!isEtudiant) {
          setError("Accès réservé aux étudiants");
          setIsLoading(false);
          return;
        }

        // 3. Récupération des corrections avec le bon paramètre
        const response = await axios.get(
          `http://127.0.0.1:8000/api/corrections/?etudiant=${userResponse.data.id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        console.log("Corrections reçues:", response.data);

        // 4. Transformation des données pour correspondre au frontend
        const formattedCorrections = response.data.map(corr => ({
          ...corr,
          date_soumission: corr.date_soumission || corr.soumission?.date_soumission,
          plagiarism_report: corr.plagiarism_report || {},
          soumission: {
            ...corr.soumission,
            exercice: {
              titre: corr.exercice_titre || 'Titre inconnu'
            }
          }
        }));

        setCorrections(formattedCorrections);

      } catch (err) {
        console.error("Erreur API:", {
          message: err.message,
          status: err.response?.status,
          data: err.response?.data
        });
        setError(err.response?.data?.detail || "Erreur de chargement");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  return (
    <div className="space-y-8 p-6 mt-16">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Mes corrections</h1>
        <p className="mt-2 text-gray-600">
          Consultez vos notes et les retours générés par l'IA pour chaque soumission
        </p>
      </header>

      {error && (
        <div className="bg-red-100 text-red-700 p-4 rounded">{error}</div>
      )}

      <div className="grid gap-6">
        {corrections.map((correction) => (
          <div
            key={correction.id}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <div className="p-2 bg-green-100 rounded-lg">
                  <FileCheck className="h-6 w-6 text-green-700" />
                </div>
                <div className="flex-1">
                <h2 className="text-xl font-semibold text-gray-900">
  {correction.soumission?.exercice?.titre || 'Titre inconnu'}
</h2>
<p className="mt-1 text-gray-600">
  Soumis le{' '}
  {correction.date_soumission
    ? format(
        new Date(correction.date_soumission),
        'dd MMMM yyyy',
        { locale: fr }
      )
    : 'Date inconnue'}
</p>

                  <div className="mt-2 text-sm text-gray-700 space-y-1">
                    <p>
                      <strong>Note :</strong> {correction.note}/20
                    </p>
                    <p>
                      <strong>Feedback IA :</strong>{' '}
                      {correction.feedback || 'Non précisé'}
                    </p>
                    <p>
                      <strong>Points forts :</strong>{' '}
                      {correction.points_forts || 'Non précisé'}
                    </p>
                    <p>
                      <strong>Points faibles :</strong>{' '}
                      {correction.points_faibles || 'Non précisé'}
                    </p>
                  </div>

                  {correction.commentaire_professeur && (
                    <div className="mt-4 p-3 bg-blue-50 border-l-4 border-blue-500">
                      <p className="text-sm text-blue-800">
                        <strong>Commentaire du professeur :</strong>{' '}
                        {correction.commentaire_professeur}
                      </p>
                    </div>
                  )}

                  {/* ← Nouveau : Rapport de plagiat */}
                  
                  {correction.plagiarism_report && (
  <div className="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-500 rounded">
    <h3 className="flex items-center text-yellow-700 font-semibold mb-2">
      <MessageSquareText className="h-5 w-5 mr-2" />
      {correction.est_plagiat ? (
        `Plagiat détecté (${(correction.plagiarism_score * 100).toFixed(1)}%)`
      ) : (
        "Aucun plagiat détecté"
      )}
    </h3>

    {correction.plagiarism_report.comparisons && (
      <div className="mt-3 space-y-3">
        <h4 className="font-medium">Comparaisons effectuées:</h4>
        {correction.plagiarism_report.comparisons.map((comparison, index) => (
          <div key={index} className={`p-3 rounded ${comparison.is_plagiarism ? 'bg-red-50' : 'bg-gray-50'}`}>
            <div className="flex justify-between">
              <span className="font-medium">
                {comparison.student_name || 'Étudiant inconnu'}
              </span>
              <span className={`font-semibold ${comparison.is_plagiarism ? 'text-red-600' : 'text-gray-600'}`}>
                {(comparison.similarity_score * 100).toFixed(1)}%
              </span>
            </div>
            
            {comparison.details && (
              <div className="mt-2 text-sm text-gray-600 grid grid-cols-2 gap-2">
                <div>
                  <span className="font-medium">Cosinus:</span> {comparison.details.cosine.toFixed(3)}
                </div>
                <div>
                  <span className="font-medium">Jaccard:</span> {comparison.details.jaccard.toFixed(3)}
                </div>
              </div>
            )}

            <div className="mt-1 text-xs text-gray-500">
              Date: {new Date(comparison.date).toLocaleDateString('fr-FR')}
            </div>
          </div>
        ))}
      </div>
    )}

    {correction.plagiarism_report.summary && (
      <div className="mt-4 pt-4 border-t border-yellow-200">
        <h4 className="font-medium">Résumé:</h4>
        <ul className="mt-2 text-sm space-y-1">
          <li>Nombre de comparaisons: {correction.plagiarism_report.summary.total_compared}</li>
          <li>Similarité maximale: {(correction.plagiarism_report.summary.max_similarity * 100).toFixed(1)}%</li>
          <li>Seuil de détection: {(correction.plagiarism_report.metadata?.threshold * 100 || 0).toFixed(1)}%</li>
        </ul>
      </div>
    )}
  </div>
)}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CorrectionPage;
