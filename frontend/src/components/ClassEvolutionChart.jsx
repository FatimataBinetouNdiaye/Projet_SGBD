// components/ClassEvolutionChart.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

function ClassEvolutionChart({ classId }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    if (!classId) return;
    const fetchEvolution = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://127.0.0.1:8000/api/professor/class/evolution/', {
            headers: { Authorization: `Bearer ${token}` }
          });
          
        setData(response.data);
      } catch (error) {
        console.error("Erreur lors de la récupération de l'évolution de la classe :", error);
      }
    };
    fetchEvolution();
  }, [classId]);

  if (!data || data.length === 0) {
    return <p className="text-gray-500 text-sm">Pas de données disponibles pour cette classe.</p>;
  }

  return (
    <div className="mt-4 bg-gray-50 p-4 rounded border">
      <h3 className="text-md font-semibold mb-2">Évolution des notes</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="exercice" />
          <YAxis domain={[0, 20]} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="note_moyenne" stroke="#10b981" strokeWidth={2} name="Note Moyenne" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ClassEvolutionChart;
