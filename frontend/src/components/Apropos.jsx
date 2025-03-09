import React from 'react';
import { Brain, BarChart, BookOpen } from 'lucide-react'; // Importez les icônes nécessaires

const Apropos = () => {
  return (
    <div className="py-12 bg-gray-50">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">Nos Fonctionnalités</h2>
        {/* Grille des fonctionnalités */}
        <div className="grid md:grid-cols-3 gap-8">
          {/* Carte Évaluation par IA */}
          <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:border-brandPrimary hover:border-4 hover:shadow-lg transition-all duration-300">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <Brain className="h-6 w-6 text-brandPrimary" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Évaluation par IA</h3>
            <p className="text-gray-600">
              Correction automatique intelligente de vos exercices avec des retours détaillés
            </p>
          </div>

          {/* Carte Suivi personnalisé */}
          <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:border-brandPrimary  hover:border-4 hover:shadow-lg transition-all duration-300">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <BarChart className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Suivi personnalisé</h3>
            <p className="text-gray-600">
              Visualisez votre progression et identifiez vos points d'amélioration
            </p>
          </div>

          {/* Carte Exercices variés */}
          <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:border-brandPrimary  hover:border-4 hover:shadow-lg transition-all duration-300">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <BookOpen className="h-6 w-6 text-brandPrimary" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Exercices variés</h3>
            <p className="text-gray-600">
              Une large bibliothèque d'exercices couvrant tous les aspects des bases de données
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Apropos;