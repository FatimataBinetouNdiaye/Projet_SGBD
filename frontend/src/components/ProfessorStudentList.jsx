import React, { useState, useEffect } from 'react';
import { Users, ChevronDown, ChevronUp, FileText, User } from 'lucide-react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Link as RouterLink } from 'react-router-dom';
import ClassEvolutionChart from './ClassEvolutionChart';

function ProfessorStudentList() {
    const [classes, setClasses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedClass, setExpandedClass] = useState(null);
    const navigate = useNavigate();

    // Palette de couleurs
    const colors = {
        brandPrimary: '#4CAF4F',
        brandPrimaryLight: '#81C784',
        brandPrimaryLighter: '#C8E6C9',
        textDark: '#263238',
        textLight: '#607D8B',
        bgLight: '#F5F7FA'
    };

    useEffect(() => {
        const fetchClasses = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('http://127.0.0.1:8000/api/professor/classes/', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setClasses(response.data);
            } catch (error) {
                if (error.response?.status === 403) {
                    navigate('/unauthorized');
                }
            } finally {
                setLoading(false);
            }
        };
        fetchClasses();
    }, [navigate]);

    const toggleClass = (classId) => {
        setExpandedClass(expandedClass === classId ? null : classId);
    };

    if (loading) return (
        <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2" style={{ borderColor: colors.brandPrimary }}></div>
        </div>
    );

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex items-center mb-8">
                <Users className="h-8 w-8 mr-3" style={{ color: colors.brandPrimary }} />
                <h1 className="text-3xl font-bold" style={{ color: colors.textDark }}>Mes Classes</h1>
            </div>
            
            <div className="space-y-6">
                {classes.map(classe => (
                    <div key={classe.id} className="bg-white rounded-xl shadow-md overflow-hidden transition-all duration-200 hover:shadow-lg">
                        <div 
                            className="flex justify-between items-center p-5 cursor-pointer"
                            style={{ backgroundColor: colors.brandPrimaryLighter }}
                            onClick={() => toggleClass(classe.id)}
                        >
                            <div className="flex items-center">
                                <div className="mr-3 flex items-center justify-center h-10 w-10 rounded-full" style={{ backgroundColor: colors.brandPrimary }}>
                                    <span className="text-white font-semibold">{classe.nom.charAt(0)}</span>
                                </div>
                                <h2 className="font-semibold text-xl" style={{ color: colors.textDark }}>{classe.nom}</h2>
                            </div>
                            {expandedClass === classe.id ? 
                                <ChevronUp className="h-6 w-6" style={{ color: colors.brandPrimary }} /> : 
                                <ChevronDown className="h-6 w-6" style={{ color: colors.brandPrimary }} />}
                        </div>
                        
                        {expandedClass === classe.id && (
                            <div className="p-5">
                                <div className="overflow-x-auto rounded-lg border border-gray-200">
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead style={{ backgroundColor: colors.brandPrimaryLighter }}>
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: colors.textDark }}>Étudiant</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: colors.textDark }}>Informations</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: colors.textDark }}>Soumissions</th>
                                                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider" style={{ color: colors.textDark }}>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-200">
                                            {classe.etudiants.map(etudiant => (
                                                <tr key={etudiant.id} className="hover:bg-gray-50 transition-colors duration-150">
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="flex items-center">
                                                            <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center mr-3">
                                                                <User className="h-5 w-5 text-gray-500" />
                                                            </div>
                                                            <div>
                                                                <div className="text-sm font-medium" style={{ color: colors.textDark }}>{etudiant.prenom} {etudiant.nom}</div>
                                                                <div className="text-sm" style={{ color: colors.textLight }}>{etudiant.matricule}</div>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="text-sm" style={{ color: colors.textDark }}>{etudiant.email}</div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="flex items-center">
                                                            <FileText className="h-4 w-4 mr-1" style={{ color: colors.brandPrimary }} />
                                                            <span className="text-sm font-medium" style={{ color: colors.brandPrimary }}>
                                                                {etudiant.soumissions_count || 0} soumission(s)
                                                            </span>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-right">
                                                        <RouterLink 
                                                            to={`/soumissions/etudiant/${etudiant.id}`}
                                                            className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium transition-colors duration-200"
                                                            style={{ 
                                                                backgroundColor: colors.brandPrimaryLighter,
                                                                color: colors.brandPrimary
                                                            }}
                                                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = colors.brandPrimaryLight}
                                                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = colors.brandPrimaryLighter}
                                                        >
                                                            Voir détails
                                                        </RouterLink>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>

                                {expandedClass === classe.id && (
                                    <div className="mt-8">
                                        <h3 className="text-lg font-semibold mb-4 flex items-center" style={{ color: colors.textDark }}>
                                            <span className="w-2 h-5 rounded-full mr-2" style={{ backgroundColor: colors.brandPrimary }}></span>
                                            Évolution de la classe
                                        </h3>
                                        <div className="bg-white p-4 rounded-lg border border-gray-200">
                                            <ClassEvolutionChart classId={classe.id} />
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ProfessorStudentList;