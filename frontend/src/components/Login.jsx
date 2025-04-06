import React, { useState } from 'react';
import axios from 'axios';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from "jwt-decode";

function Login() {
  // Couleurs du thème
  const colors = {
    brandPrimary: '#4CAF4F', // Vert - Couleur principale
    brandPrimaryLight: '#81C784', // Vert clair
    brandPrimaryLighter: '#C8E6C9', // Vert très clair
    brandPrimaryDark: '#388E3C', // Vert foncé
    lightBg: '#F5F5F5', // Fond clair
    darkText: '#263238', // Texte foncé
    lightText: '#607D8B' // Texte clair
  };

  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    role: 'ET'
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState({
    email: '',
    password: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    if (name === 'email') {
      setFormErrors({
        ...formErrors,
        email: !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? 'Email invalide' : ''
      });
    }
    if (name === 'password') {
      setFormErrors({
        ...formErrors,
        password: value.length < 6 ? 'Minimum 6 caractères' : ''
      });
    }
  };

  const validateForm = () => {
    const errors = {};
    if (!formData.email) errors.email = 'Email requis';
    if (!formData.password) errors.password = 'Mot de passe requis';
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleLoginSuccess = async (accessToken) => {
    try {
      localStorage.setItem("token", accessToken);
      
      const userResponse = await axios.get("http://127.0.0.1:8000/api/utilisateur-connecte/", {
        headers: {
          Authorization: `Bearer ${accessToken}`
        }
      });

      const userData = {
        id: userResponse.data.id,
        email: userResponse.data.email,
        nom: userResponse.data.nom,
        prenom: userResponse.data.prenom,
        role: userResponse.data.role,
        photo: userResponse.data.photo_profil || null
      };

      localStorage.setItem("user", JSON.stringify(userData));

      const redirectPath = userData.role === 'PR' ? "/dashboard/prof" : "/tableau-de-bord";
      navigate(redirectPath);
    } catch (error) {
      console.error("Erreur après connexion:", error);
      setError("Erreur lors de la récupération des données utilisateur");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/token/", {
        email: formData.email,
        password: formData.password
      });

      await handleLoginSuccess(response.data.access);

    } catch (error) {
      console.error("Erreur de connexion:", error);
      
      if (error.response) {
        switch (error.response.status) {
          case 401: setError("Identifiants incorrects"); break;
          case 400: setError("Données de connexion invalides"); break;
          case 500: setError("Erreur serveur - Veuillez réessayer plus tard"); break;
          default: setError("Erreur de connexion");
        }
      } else if (error.request) {
        setError("Pas de réponse du serveur");
      } else {
        setError("Erreur de configuration");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLoginSuccess = async (credentialResponse) => {
    setIsLoading(true);
    setError('');
    
    try {
      const decoded = jwtDecode(credentialResponse.credential);

      const response = await axios.post("http://127.0.0.1:8000/api/google-auth/", {
        token: credentialResponse.credential,
        role: formData.role
      });

      await handleLoginSuccess(response.data.access);
      
    } catch (error) {
      console.error("Erreur de connexion Google:", error);
      setError("Erreur lors de la connexion avec Google");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLoginFailure = () => {
    setError("Échec de la connexion avec Google");
  };

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: colors.lightBg }}>
      <div className="max-w-md w-full space-y-8 p-10 rounded-xl shadow-lg" style={{ backgroundColor: 'white' }}>
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold" style={{ color: colors.darkText }}>
            Connexion
          </h2>
          <p className="mt-2 text-sm" style={{ color: colors.lightText }}>
            Accédez à votre espace {formData.role === 'ET' ? 'étudiant' : 'professeur'}
          </p>
        </div>

        {error && (
          <div className="rounded-md p-4" style={{ backgroundColor: '#FEE2E2', color: '#B91C1C' }}>
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium">{error}</h3>
              </div>
            </div>
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium" style={{ color: colors.darkText }}>
                Adresse email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={formData.email}
                onChange={handleChange}
                className={`appearance-none relative block w-full px-3 py-3 border ${formErrors.email ? 'border-red-300' : 'border-gray-300'} rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 sm:text-sm`}
                style={{
                  borderColor: formErrors.email ? '#FCA5A5' : colors.brandPrimaryLighter,
                  focusBorderColor: colors.brandPrimary,
                  focusRingColor: colors.brandPrimaryLight
                }}
                placeholder="email@exemple.com"
              />
              {formErrors.email && (
                <p className="mt-1 text-sm" style={{ color: '#DC2626' }}>
                  {formErrors.email}
                </p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium" style={{ color: colors.darkText }}>
                Mot de passe
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className={`appearance-none relative block w-full px-3 py-3 border ${formErrors.password ? 'border-red-300' : 'border-gray-300'} rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 sm:text-sm`}
                  style={{
                    borderColor: formErrors.password ? '#FCA5A5' : colors.brandPrimaryLighter,
                    focusBorderColor: colors.brandPrimary,
                    focusRingColor: colors.brandPrimaryLight
                  }}
                  placeholder="••••••••"
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
              {formErrors.password && (
                <p className="mt-1 text-sm" style={{ color: '#DC2626' }}>
                  {formErrors.password}
                </p>
              )}
            </div>

            <div>
              <label htmlFor="role" className="block text-sm font-medium" style={{ color: colors.darkText }}>
                Type de compte
              </label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="mt-1 block w-full pl-3 pr-10 py-3 text-base border rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 sm:text-sm"
                style={{
                  borderColor: colors.brandPrimaryLighter,
                  focusBorderColor: colors.brandPrimary,
                  focusRingColor: colors.brandPrimaryLight
                }}
              >
                <option value="ET">Étudiant</option>
                <option value="PR">Professeur</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 rounded"
                style={{
                  color: colors.brandPrimary,
                  borderColor: colors.brandPrimaryLight,
                  focusRingColor: colors.brandPrimary
                }}
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm" style={{ color: colors.darkText }}>
                Se souvenir de moi
              </label>
            </div>

            <div className="text-sm">
              <RouterLink 
                to="/mot-de-passe-oublie" 
                className="font-medium hover:underline"
                style={{ color: colors.brandPrimary }}
              >
                Mot de passe oublié ?
              </RouterLink>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200"
              style={{
                backgroundColor: colors.brandPrimary,
                hoverBackgroundColor: colors.brandPrimaryDark,
                focusRingColor: colors.brandPrimaryLight,
                disabledOpacity: '0.7'
              }}
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin mr-2 h-5 w-5" />
                  Connexion en cours...
                </>
              ) : (
                <>
                  <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                    <svg className="h-5 w-5" style={{ color: colors.brandPrimaryLighter }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                    </svg>
                  </span>
                  Se connecter
                </>
              )}
            </button>
          </div>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t" style={{ borderColor: colors.brandPrimaryLighter }}></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white" style={{ color: colors.lightText }}>
              Ou continuer avec
            </span>
          </div>
        </div>

        <div className="flex justify-center">
          <GoogleLogin
            onSuccess={handleGoogleLoginSuccess}
            onError={handleGoogleLoginFailure}
            shape="pill"
            size="large"
            text="continue_with"
            locale="fr"
            theme="filled_blue" // Vous pouvez personnaliser ceci si nécessaire
          />
        </div>

        <div className="text-center text-sm" style={{ color: colors.lightText }}>
          Pas encore de compte ?{' '}
          <RouterLink 
            to="/signup" 
            className="font-medium hover:underline"
            style={{ color: colors.brandPrimary }}
          >
            S'inscrire
          </RouterLink>
        </div>
      </div>
    </div>
  );
}

export default Login;