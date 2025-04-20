import { StrictMode } from 'react'
import './index.css'
import ReactDOM from 'react-dom/client';
import React from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';

import App from './App.jsx'
import { AuthProvider } from './context/AuthContext';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId="380403399725-mipoiq1l59ca8fl6eq1o2rpe4f3iv0ro.apps.googleusercontent.com">
      <App />
      </GoogleOAuthProvider>
  </React.StrictMode>
);