import React from 'react';
import { BarChart, CheckCircle, Clock } from 'lucide-react';

function Dashboard() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-8 mt-16">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Tableau de bord étudiant</h1>
        <p className="mt-2 text-gray-600">Suivez votre progression et vos soumissions</p>
      </header>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Exercices complétés</h2>
            <CheckCircle className="h-6 w-6 text-green-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-gray-900">12</p>
          <p className="mt-1 text-sm text-gray-600">Sur 15 exercices au total</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Score moyen</h2>
            <BarChart className="h-6 w-6 text-blue-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-gray-900">85%</p>
          <p className="mt-1 text-sm text-gray-600">Basé sur toutes les soumissions</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Prochaine échéance</h2>
            <Clock className="h-6 w-6 text-orange-500" />
          </div>
          <p className="mt-2 text-3xl font-bold text-gray-900">2 jours</p>
          <p className="mt-1 text-sm text-gray-600">Exercice d'optimisation SQL</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Soumissions récentes</h2>
        <div className="space-y-4">
          {[1, 2, 3].map((item) => (
            <div key={item} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-medium text-gray-900">Exercice de normalisation de base de données</h3>
                <p className="text-sm text-gray-600">Soumis il y a 2 jours</p>
              </div>
              <div className="flex items-center">
                <span className="text-green-600 font-semibold">18/20</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;