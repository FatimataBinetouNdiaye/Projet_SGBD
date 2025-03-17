import React from 'react';
import { Github, Mail, Lock, User } from 'lucide-react';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom'; // Pour la navigation

function Login() {
  const navigate = useNavigate(); // Hook pour la navigation

  // Gérer la réponse de Google
  const handleGoogleSuccess = (credentialResponse) => {
    console.log('Google Login Success:', credentialResponse);
    // Ici, vous pouvez envoyer le token à votre backend pour vérification
  };

  const handleGoogleError = () => {
    console.log('Google Login Failed');
  };

  return (
    <GoogleOAuthProvider clientId="VOTRE_CLIENT_ID_GOOGLE"> {/* Remplacez par votre Client ID */}
      <div className="container mx-auto px-4 py-8 mt-16">
        <div className="max-w-md mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Bienvenue</h1>
            <p className="mt-2 text-gray-600">Connectez-vous à votre compte pour continuer</p>
          </div>

          <div className="bg-white p-8 rounded-lg shadow-md">
            <form className="space-y-6">
              {/* Champ Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Adresse email
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="email"
                    id="email"
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-brandPrimary focus:border-brandPrimary"
                    placeholder="Entrez votre email"
                  />
                </div>
              </div>

              {/* Champ Mot de passe */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Mot de passe
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="password"
                    id="password"
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-brandPrimary focus:border-brandPrimary"
                    placeholder="Entrez votre mot de passe"
                  />
                </div>
                <div className="mt-2 text-right">
                  <a href="#" className="text-sm text-brandPrimary hover:text-brandPrimary/80">
                    Mot de passe oublié ?
                  </a>
                </div>
              </div>

              {/* Bouton de connexion */}
              <button
                type="submit"
                className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-brandPrimary hover:bg-brandPrimary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brandPrimary transition-all duration-200"
              >
                <User className="h-5 w-5 mr-2" />
                Se connecter
              </button>
            </form>

            {/* Séparateur "Ou continuer avec" */}
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Ou continuer avec</span>
                </div>
              </div>

              {/* Boutons de connexion tiers */}
              <div className="mt-6 grid grid-cols-2 gap-3">
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={handleGoogleError}
                  useOneTap
                  theme=""
                  size="medium"
                  shape="rectangular"
                  text="signin_with"
                />
                <button
                  className="w-full inline-flex justify-center items-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 transition-all duration-200"
                  onClick={() => console.log('Email login')}
                >
                  <Mail className="h-5 w-5 mr-2" />
                  Email
                </button>
              </div>
            </div>

            {/* Lien "Créer un compte" */}
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Vous n'avez pas de compte ?{' '}
                <button
                  onClick={() => navigate('/signup')} // Redirige vers la page d'inscription
                  className="font-medium text-brandPrimary hover:text-brandPrimary/80"
                >
                  Créer un compte
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </GoogleOAuthProvider>
  );
}

export default Login;