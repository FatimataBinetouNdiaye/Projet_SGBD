import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { FileText, Clock, Check, Edit, User, ChevronDown, ChevronUp } from 'lucide-react';

function StudentSubmissions() {
    const { studentId } = useParams();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState(null);
    const [formData, setFormData] = useState({
        note: '',
        feedback: '',
        points_forts: '',
        points_faibles: '',
        commentaire_professeur: '',
    });

    // Palette de couleurs
    const colors = {
        brandPrimary: '#4CAF4F',
        brandPrimaryLight: '#81C784',
        brandPrimaryLighter: '#C8E6C9',
        brandPrimaryDark: '#388E3C',
        textDark: '#263238',
        textLight: '#607D8B',
        bgLight: '#F5F7FA',
        success: '#4CAF4F',
        warning: '#FFC107',
        danger: '#F44336'
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get(
                    `http://127.0.0.1:8000/api/professor/students/${studentId}/submissions/`,
                    { headers: { Authorization: `Bearer ${token}` } }
                );
                setData(response.data);
            } catch (error) {
                console.error("Error:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [studentId]);

    const handleViewDetails = async (submission) => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(
                `http://127.0.0.1:8000/api/submissions/${submission.id}/pdf/`,
                {
                    responseType: 'blob',
                    headers: { Authorization: `Bearer ${token}` }
                }
            );
            const fileURL = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
            window.open(fileURL, '_blank');
        } catch (error) {
            console.error("Erreur lors de l'ouverture du PDF :", error);
        }
    };

    const handleEdit = (submission) => {
        setEditingId(submission.id);
        setFormData({
            note: submission.note || '',
            feedback: submission.feedback || '',
            points_forts: submission.points_forts || '',
            points_faibles: submission.points_faibles || '',
            commentaire_professeur: submission.commentaire_professeur || '',
        });
    };

    const handleChange = (e) => {
        setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const handleUpdate = async (submissionId) => {
        try {
            const token = localStorage.getItem('token');
            await axios.patch(
                `http://127.0.0.1:8000/api/corrections/${submissionId}/update/`,
                formData,
                { headers: { Authorization: `Bearer ${token}` } }
            );
            // Mettre à jour les données locales après la modification
            setData(prev => ({
                ...prev,
                soumissions: prev.soumissions.map(s => 
                    s.id === submissionId ? { 
                        ...s, 
                        ...formData,
                        note: parseFloat(formData.note) 
                    } : s
                )
            }));
            setEditingId(null);
        } catch (err) {
            console.error("Erreur lors de la mise à jour :", err);
        }
    };

    if (loading) return (
        <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2" style={{ borderColor: colors.brandPrimary }}></div>
        </div>
    );

    return (
        <div className="container mx-auto px-4 py-8 pt-20"> 
            {data && (
                <div className="space-y-6">
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center justify-center h-14 w-14 rounded-full" style={{ backgroundColor: colors.brandPrimaryLighter }}>
                            <User className="h-6 w-6" style={{ color: colors.brandPrimary }} />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold" style={{ color: colors.textDark }}>
                                {data.etudiant.nom_complet}
                            </h1>
                            <p className="text-sm" style={{ color: colors.textLight }}>Matricule: {data.etudiant.matricule}</p>
                        </div>
                    </div>

                    <div className="bg-white rounded-xl shadow-md overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead>
                                    <tr style={{ backgroundColor: colors.brandPrimaryLighter }}>
                                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: colors.textDark }}>Exercice</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: colors.textDark }}>Date</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: colors.textDark }}>Statut</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: colors.textDark }}>Note</th>
                                        <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider" style={{ color: colors.textDark }}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {data.soumissions.map(soumission => (
                                        <React.Fragment key={soumission.id}>
                                            <tr className="hover:bg-gray-50 transition-colors duration-150">
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <div className="text-sm font-medium" style={{ color: colors.textDark }}>
                                                        {soumission.exercice}
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <div className="text-sm" style={{ color: colors.textDark }}>
                                                        {new Date(soumission.date_soumission).toLocaleDateString()}
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    {soumission.statut === 'Corrigé' ? (
                                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" style={{ backgroundColor: colors.brandPrimaryLighter, color: colors.brandPrimary }}>
                                                            <Check className="h-3 w-3 mr-1" /> Corrigé
                                                        </span>
                                                    ) : (
                                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" style={{ backgroundColor: '#FFF3CD', color: colors.warning }}>
                                                            <Clock className="h-3 w-3 mr-1" /> En attente
                                                        </span>
                                                    )}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <div className="text-sm font-medium" style={{ color: soumission.note !== null ? (soumission.note >= 10 ? colors.success : colors.danger) : colors.textLight }}>
                                                        {soumission.note !== null ? `${soumission.note}/20` : '-'}
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-right space-x-2">
                                                    <button
                                                        onClick={() => handleViewDetails(soumission)}
                                                        className="inline-flex items-center px-3 py-1 rounded-md text-sm transition-colors duration-200"
                                                        style={{ 
                                                            backgroundColor: colors.brandPrimaryLighter,
                                                            color: colors.brandPrimary
                                                        }}
                                                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.brandPrimaryLight}
                                                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.brandPrimaryLighter}
                                                    >
                                                        <FileText className="h-4 w-4 mr-1" /> Détails
                                                    </button>
                                                    {soumission.statut === 'Corrigé' && (
                                                        <button
                                                            onClick={() => handleEdit(soumission)}
                                                            className="inline-flex items-center px-3 py-1 rounded-md text-sm transition-colors duration-200"
                                                            style={{ 
                                                                backgroundColor: '#E8F5E9',
                                                                color: colors.brandPrimaryDark
                                                            }}
                                                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.brandPrimaryLighter}
                                                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#E8F5E9'}
                                                        >
                                                            <Edit className="h-4 w-4 mr-1" /> Modifier
                                                        </button>
                                                    )}
                                                </td>
                                            </tr>
                                            {editingId === soumission.id && (
                                                <tr>
                                                    <td colSpan="5" className="px-6 py-4 bg-gray-50">
                                                        <div className="space-y-4 p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
                                                            <h3 className="text-lg font-semibold flex items-center" style={{ color: colors.textDark }}>
                                                                <span className="w-2 h-5 rounded-full mr-2" style={{ backgroundColor: colors.brandPrimary }}></span>
                                                                Modifier la correction
                                                            </h3>
                                                            
                                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                                <div>
                                                                    <label className="block text-sm font-medium mb-1" style={{ color: colors.textDark }}>Note /20</label>
                                                                    <input
                                                                        type="number"
                                                                        name="note"
                                                                        min="0"
                                                                        max="20"
                                                                        step="0.5"
                                                                        value={formData.note}
                                                                        onChange={handleChange}
                                                                        className="w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-offset-2 focus:ring-opacity-50"
                                                                        style={{ 
                                                                            borderColor: colors.brandPrimaryLight,
                                                                            focusRing: colors.brandPrimary 
                                                                        }}
                                                                    />
                                                                </div>
                                                            </div>
                                                            
                                                            <div>
                                                                <label className="block text-sm font-medium mb-1" style={{ color: colors.textDark }}>Feedback</label>
                                                                <textarea
                                                                    name="feedback"
                                                                    value={formData.feedback}
                                                                    onChange={handleChange}
                                                                    rows={3}
                                                                    className="w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-offset-2 focus:ring-opacity-50"
                                                                    style={{ 
                                                                        borderColor: colors.brandPrimaryLight,
                                                                        focusRing: colors.brandPrimary 
                                                                    }}
                                                                />
                                                            </div>
                                                            
                                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                                <div>
                                                                    <label className="block text-sm font-medium mb-1" style={{ color: colors.textDark }}>Points forts</label>
                                                                    <textarea
                                                                        name="points_forts"
                                                                        value={formData.points_forts}
                                                                        onChange={handleChange}
                                                                        rows={2}
                                                                        className="w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-offset-2 focus:ring-opacity-50"
                                                                        style={{ 
                                                                            borderColor: colors.brandPrimaryLight,
                                                                            focusRing: colors.brandPrimary 
                                                                        }}
                                                                    />
                                                                </div>
                                                                <div>
                                                                    <label className="block text-sm font-medium mb-1" style={{ color: colors.textDark }}>Points faibles</label>
                                                                    <textarea
                                                                        name="points_faibles"
                                                                        value={formData.points_faibles}
                                                                        onChange={handleChange}
                                                                        rows={2}
                                                                        className="w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-offset-2 focus:ring-opacity-50"
                                                                        style={{ 
                                                                            borderColor: colors.brandPrimaryLight,
                                                                            focusRing: colors.brandPrimary 
                                                                        }}
                                                                    />
                                                                </div>
                                                            </div>
                                                            
                                                            <div>
                                                                <label className="block text-sm font-medium mb-1" style={{ color: colors.textDark }}>Commentaire du professeur</label>
                                                                <textarea
                                                                    name="commentaire_professeur"
                                                                    value={formData.commentaire_professeur}
                                                                    onChange={handleChange}
                                                                    rows={2}
                                                                    className="w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-offset-2 focus:ring-opacity-50"
                                                                    style={{ 
                                                                        borderColor: colors.brandPrimaryLight,
                                                                        focusRing: colors.brandPrimary 
                                                                    }}
                                                                />
                                                            </div>
                                                            
                                                            <div className="flex justify-end space-x-3 pt-2">
                                                                <button
                                                                    onClick={() => setEditingId(null)}
                                                                    className="px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
                                                                    style={{ 
                                                                        backgroundColor: '#F5F5F5',
                                                                        color: colors.textDark
                                                                    }}
                                                                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#EEEEEE'}
                                                                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#F5F5F5'}
                                                                >
                                                                    Annuler
                                                                </button>
                                                                <button
                                                                    onClick={() => handleUpdate(soumission.id)}
                                                                    className="px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors duration-200"
                                                                    style={{ backgroundColor: colors.brandPrimary }}
                                                                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.brandPrimaryDark}
                                                                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.brandPrimary}
                                                                >
                                                                    Enregistrer
                                                                </button>
                                                            </div>
                                                        </div>
                                                    </td>
                                                </tr>
                                            )}
                                        </React.Fragment>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default StudentSubmissions;