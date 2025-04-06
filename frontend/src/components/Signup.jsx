import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, User, Lock, Hash, CheckCircle, ArrowRight, Loader2 } from 'lucide-react';
import axios from 'axios';
import { GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from "jwt-decode";

function Signup() {
  // Couleurs du thème
  const colors = {
    brandPrimary: '#4CAF4F', // Vert
    brandPrimaryLight: '#81C784',
    brandPrimaryDark: '#388E3C',
    brandPrimaryLighter: '#C8E6C9',
    lightBg: '#F5F5F5',
    darkText: '#263238',
    lightText: '#607D8B'
  };

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    matricule: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'ET'
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [success, setSuccess] = useState(false);
  const [countdown, setCountdown] = useState(5);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    // Validations
    if (formData.password !== formData.confirmPassword) {
      setError("Les mots de passe ne correspondent pas");
      setIsSubmitting(false);
      return;
    }

    if (formData.password.length < 6) {
      setError("Le mot de passe doit contenir au moins 6 caractères");
      setIsSubmitting(false);
      return;
    }

    if (!formData.matricule) {
      setError("Le matricule est obligatoire");
      setIsSubmitting(false);
      return;
    }

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/signup/', {
        first_name: formData.firstName,
        last_name: formData.lastName,
        matricule: formData.matricule,
        email: formData.email,
        password: formData.password,
        role: formData.role
      });
      
      if (response.status === 201) {
        setSuccess(true);
        // Compte à rebours pour la redirection
        const timer = setInterval(() => {
          setCountdown(prev => prev - 1);
        }, 1000);
        
        setTimeout(() => {
          clearInterval(timer);
          navigate('/login');
        }, 5000);
      }
    } catch (error) {
      console.error('Erreur d\'inscription:', error);
      setError(error.response?.data?.message || 
              error.response?.data?.detail || 
              "Une erreur est survenue lors de l'inscription");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleSignup = async (credentialResponse) => {
    setIsSubmitting(true);
    setError(null);
  
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/google-auth/', {
        token: credentialResponse.credential,
        role: formData.role
      });
  
      if (response.data.access_token) {
        setSuccess(true);
        const timer = setInterval(() => {
          setCountdown(prev => prev - 1);
        }, 1000);
        
        setTimeout(() => {
          clearInterval(timer);
          navigate('/');
        }, 5000);
      }
    } catch (error) {
      console.error('Erreur inscription Google:', error);
      setError(error.response?.data?.error || "Échec de l'inscription avec Google");
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    return () => {
      clearInterval();
    };
  }, []);

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-16 pb-8" style={{ backgroundColor: colors.lightBg }}>
        <div className="max-w-md w-full bg-white p-10 rounded-xl shadow-lg text-center">
          <CheckCircle className="h-16 w-16 mx-auto mb-4" style={{ color: colors.brandPrimary }} />
          <h2 className="text-2xl font-bold mb-2" style={{ color: colors.darkText }}>Inscription réussie !</h2>
          <p className="mb-6" style={{ color: colors.lightText }}>
            Vous allez être redirigé vers la page de connexion dans {countdown} seconde{countdown > 1 ? 's' : ''}
          </p>
          <Link 
            to="/login" 
            className="font-medium hover:underline"
            style={{ color: colors.brandPrimary }}
          >
            Cliquez ici si la redirection ne fonctionne pas
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center pt-16 pb-8" style={{ backgroundColor: colors.lightBg }}>
      <div className="max-w-md w-full p-8 rounded-xl shadow-lg" style={{ backgroundColor: 'white' }}>
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold" style={{ color: colors.darkText }}>Créer un compte</h1>
          <p className="mt-2" style={{ color: colors.lightText }}>Rejoignez notre communauté d'apprenants</p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-md text-sm" style={{ backgroundColor: '#FEE2E2', color: '#B91C1C' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>
                Prénom*
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5" style={{ color: colors.lightText }} />
                </div>
                <input
                  type="text"
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  className="block w-full pl-10 py-2.5 rounded-lg border focus:outline-none focus:ring-2 focus:ring-offset-2"
                  style={{
                    borderColor: colors.brandPrimaryLighter,
                    '&:focus': {
                      borderColor: colors.brandPrimary,
                      ringColor: colors.brandPrimaryLight
                    }
                  }}
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="lastName" className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>
                Nom*
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5" style={{ color: colors.lightText }} />
                </div>
                <input
                  type="text"
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  className={`block w-full pl-10 py-2.5 rounded-lg border focus:outline-none focus:ring-2 focus:ring-offset-2 border-[${colors.brandPrimaryLighter}] focus:border-[${colors.brandPrimary}] focus:ring-[${colors.brandPrimaryLight}]`}
                  required
                />
              </div>
            </div>
          </div>

          <div>
            <label htmlFor="matricule" className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>
              Matricule*
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Hash className="h-5 w-5" style={{ color: colors.lightText }} />
              </div>
              <input
                type="text"
                id="matricule"
                name="matricule"
                value={formData.matricule}
                onChange={handleChange}
                className={`block w-full pl-10 py-2.5 rounded-lg border focus:outline-none focus:ring-2 focus:ring-offset-2 border-[${colors.brandPrimaryLighter}] focus:border-[${colors.brandPrimary}] focus:ring-[${colors.brandPrimaryLight}]`}
                placeholder="Votre matricule"
                required
              />
            </div>
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>
              Adresse email*
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail className="h-5 w-5" style={{ color: colors.lightText }} />
              </div>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={`block w-full pl-10 py-2.5 rounded-lg border focus:outline-none focus:ring-2 focus:ring-offset-2 border-[${colors.brandPrimaryLighter}] focus:border-[${colors.brandPrimary}] focus:ring-[${colors.brandPrimaryLight}]`}
                placeholder="vous@exemple.com"
                required
              />
            </div>
          </div>

          <div>
            <label htmlFor="role" className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>
              Vous êtes*
            </label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              className={`block w-full py-2.5 rounded-lg border focus:outline-none focus:ring-2 focus:ring-offset-2 border-[${colors.brandPrimaryLighter}] focus:border-[${colors.brandPrimary}] focus:ring-[${colors.brandPrimaryLight}]`}
              required
            >
              <option value="ET">Étudiant</option>
              <option value="PR">Professeur</option>
            </select>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>
              Mot de passe*
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5" style={{ color: colors.lightText }} />
              </div>
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={`block w-full pl-10 pr-10 py-2.5 rounded-lg border focus:outline-none focus:ring-2 focus:ring-offset-2 border-[${colors.brandPrimaryLighter}] focus:border-[${colors.brandPrimary}] focus:ring-[${colors.brandPrimaryLight}]`}
                placeholder="••••••••"
                required
                minLength="6"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5" style={{ color: colors.lightText }} />
                ) : (
                  <Eye className="h-5 w-5" style={{ color: colors.lightText }} />
                )}
              </button>
            </div>
            <p className="mt-1 text-xs" style={{ color: colors.lightText }}>Minimum 6 caractères</p>
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1" style={{ color: colors.darkText }}>
              Confirmer mot de passe*
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5" style={{ color: colors.lightText }} />
              </div>
              <input
                type={showConfirmPassword ? "text" : "password"}
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className={`block w-full pl-10 pr-10 py-2.5 rounded-lg border focus:outline-none focus:ring-2 focus:ring-offset-2 border-[${colors.brandPrimaryLighter}] focus:border-[${colors.brandPrimary}] focus:ring-[${colors.brandPrimaryLight}]`}
                placeholder="••••••••"
                required
                minLength="6"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-5 w-5" style={{ color: colors.lightText }} />
                ) : (
                  <Eye className="h-5 w-5" style={{ color: colors.lightText }} />
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full flex justify-center items-center py-3 px-4 rounded-lg shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200 ${
              isSubmitting ? 'opacity-70 cursor-not-allowed' : 'hover:bg-[#388E3C]'
            }`}
            style={{
              backgroundColor: colors.brandPrimary,
              focusRingColor: colors.brandPrimaryLight
            }}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="animate-spin mr-2 h-5 w-5" />
                Enregistrement...
              </>
            ) : (
              <>
                <span className="mr-2">S'inscrire</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </form>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t" style={{ borderColor: colors.brandPrimaryLighter }}></div>
          </div>
          <div className="relative flex justify-center">
            <span className="px-2 bg-white text-sm" style={{ color: colors.lightText }}>
              Ou continuer avec
            </span>
          </div>
        </div>

        <div className="flex justify-center">
          <GoogleLogin
            onSuccess={handleGoogleSignup}
            onError={() => setError("Échec de la connexion avec Google")}
            shape="pill"
            size="large"
            text="signup_with"
            locale="fr"
          />
        </div>

        <div className="mt-6 text-center text-sm" style={{ color: colors.lightText }}>
          Déjà un compte ?{' '}
          <Link 
            to="/login" 
            className="font-medium hover:underline"
            style={{ color: colors.brandPrimary }}
          >
            Connectez-vous
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Signup;