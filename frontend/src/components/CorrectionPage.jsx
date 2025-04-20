import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { MessageSquareText, FileCheck } from 'lucide-react';

const CorrectionPage = () => {
  const [corrections, setCorrections] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem("token");
    console.log("✅ Token récupéré:", token);

    if (!token) {
      setError("Aucun token trouvé. Veuillez vous reconnecter.");
      return;
    }

    axios
      .get("http://127.0.0.1:8000/api/corrections/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((response) => {
        console.log("📦 Corrections reçues:", response.data);
        setCorrections(response.data);
      })
      .catch((error) => {
        console.error("❌ Erreur lors de la récupération des corrections :", error);
        setError("Erreur lors du chargement des corrections.");
      });
  }, []);

  return (
    <div className="space-y-8 p-6 mt-16">
      <div className="text-center text-green-600 text-lg">✅ CorrectionPage chargé</div>

      <header className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Mes corrections</h1>
        <p className="mt-2 text-gray-600">
          Consultez vos notes et les retours générés par l'IA pour chaque soumission
        </p>
      </header>

      {/* Affichage erreur */}
      {error && (
        <div className="bg-red-100 text-red-700 p-4 rounded">
          {error}
        </div>
      )}

      {/* Affichage brut JSON pour debug */}
      <pre className="bg-gray-100 text-sm p-4 rounded overflow-auto">
        {JSON.stringify(corrections, null, 2)}
      </pre>

      <div className="grid gap-6">
        {corrections.map((correction) => (
          <div key={correction.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <div className="p-2 bg-green-100 rounded-lg">
                  <FileCheck className="h-6 w-6 text-green-700" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    {correction.soumission?.exercice_title || 'Titre inconnu'}
                  </h2>
                  <p className="mt-1 text-gray-600">
                    Soumis le {correction.soumission?.date_soumission ? format(new Date(correction.soumission.date_soumission), 'dd MMMM yyyy', { locale: fr }) : 'Date inconnue'}
                  </p>
                  <div className="mt-2 text-sm text-gray-700">
                    <p><strong>Note :</strong> {correction.note}/20</p>
                    <p><strong>Feedback IA :</strong> {correction.feedback || 'Non précisé'}</p>
                    <p><strong>Points forts :</strong> {correction.points_forts || 'Non précisé'}</p>
                    <p><strong>Points faibles :</strong> {correction.points_faibles || 'Non précisé'}</p>
                  </div>

                  {correction.commentaire_professeur && (
                    <div className="mt-4 p-3 bg-blue-50 border-l-4 border-blue-500">
                      <p className="text-sm text-blue-800">
                        <strong>Commentaire du professeur :</strong> {correction.commentaire_professeur}
                      </p>
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