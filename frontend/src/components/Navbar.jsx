import React, { useState, useEffect } from 'react';
import axios from 'axios';
import icon from '/src/assets/icon.png';
import { Link as ScrollLink } from 'react-scroll';
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';
import { FaBars, FaXmark } from 'react-icons/fa6';
import { Database, Upload, LayoutDashboard, LogOut, User, Settings } from 'lucide-react';
import './Navbar.css'; // Fichier CSS séparé
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext'; // adapte selon ton chemin


const Navbar = () => {
  const [isMenuOpen, setMenuOpen] = useState(false);
  const [isSticky, setIsSticky] = useState(false);
  const { user, setUser, logout } = useContext(AuthContext);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  
  const toggleMenu = () => setMenuOpen(!isMenuOpen);
  const toggleDropdown = () => setDropdownOpen(!dropdownOpen);

  useEffect(() => {
    const handleScroll = () => setIsSticky(window.scrollY > 100);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const response = await axios.get('http://127.0.0.1:8000/api/utilisateur-connecte/', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setUser(response.data);
      } catch (error) {
        console.error("Erreur de chargement utilisateur", error);
        handleLogout();
      }
    };

    fetchUser();
  }, [location.pathname]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("role");
    setUser(null);
    setDropdownOpen(false);
    setMenuOpen(false);
    navigate("/login");
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownOpen && !event.target.closest('.dropdown-container')) {
        setDropdownOpen(false);
      }
      if (isMenuOpen && !event.target.closest('.mobile-menu-container')) {
        setMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [dropdownOpen, isMenuOpen]);

  return (
    <header className="navbar-header">
      <nav className={`navbar-nav ${isSticky ? 'sticky-nav' : ''}`}>
        <div className="nav-container">
          <RouterLink to="/" className="logo-link">
            <img src={icon} alt="icon" className="logo-img" />
            <span className="logo-text">Platforme Intelligente</span>
          </RouterLink>

          <ul className="desktop-menu">
            {location.pathname === "/" ? (
              <>
                <li>
                  <ScrollLink 
                    to="Accueil" 
                    spy smooth 
                    offset={-100} 
                    className="nav-link"
                  >
                    Accueil
                  </ScrollLink>
                </li>
                <li>
                  <ScrollLink 
                    to="Exercices" 
                    spy smooth 
                    offset={-100} 
                    className="nav-link"
                  >
                    À propos
                  </ScrollLink>
                </li>
              </>
            ) : (
              <li>
                <RouterLink to="/" className="nav-link">Accueil</RouterLink>
              </li>
            )}

            {user && (
              <>
                <li>
                  <RouterLink to="/soumettre" className="nav-link">
                    <Upload className="link-icon" /> Soumettre
                  </RouterLink>
                </li>
                <li>
                  <RouterLink 
                    to={user.role === 'PR' ? "/dashboard/prof" : "/tableau-de-bord"} 
                    className="nav-link"
                  >
                    <LayoutDashboard className="link-icon" /> Dashboard
                  </RouterLink>
                </li>
                <li>
                  <RouterLink to="/exercices" className="nav-link">
                    <Database className="link-icon" /> Exercices
                  </RouterLink>
                </li>
              </>
            )}
          </ul>

          <div className="auth-section">
            {user ? (
              <div className="dropdown-container">
                <button 
                  onClick={toggleDropdown}
                  className="profile-button"
                >
                  <img
                    src={user.photo_profil || "https://via.placeholder.com/40"}
                    alt="Profil"
                    className="profile-img"
                  />
                </button>
                
                {dropdownOpen && (
                  <div className="dropdown-menu">
                    <RouterLink 
                      to="/profil"
                      className="dropdown-item"
                      onClick={() => setDropdownOpen(false)}
                    >
                      <User className="dropdown-icon" /> Mon Profil
                    </RouterLink>
                    <RouterLink 
                      to="/parametres"
                      className="dropdown-item"
                      onClick={() => setDropdownOpen(false)}
                    >
                      <Settings className="dropdown-icon" /> Paramètres
                    </RouterLink>
                    <button onClick={logout}>Déconnexion</button>

                  </div>
                )}
              </div>
            ) : (
              <>
                <RouterLink 
                  to="/login" 
                  className="login-link"
                >
                  Connexion
                </RouterLink>
                <RouterLink 
                  to="/signup" 
                  className="signup-link"
                >
                  Inscription
                </RouterLink>
              </>
            )}
          </div>

          <div className="mobile-menu-container">
            <button 
              onClick={toggleMenu}
              className="menu-toggle"
              aria-label="Toggle menu"
            >
              {isMenuOpen ? <FaXmark className="menu-icon" /> : <FaBars className="menu-icon" />}
            </button>
          </div>
        </div>

        {isMenuOpen && (
          <div className="mobile-menu">
            <ul>
              <li>
                {location.pathname === "/" ? (
                  <ScrollLink 
                    to="Accueil" 
                    spy smooth 
                    offset={-100} 
                    onClick={() => setMenuOpen(false)}
                    className="mobile-link"
                  >
                    Accueil
                  </ScrollLink>
                ) : (
                  <RouterLink 
                    to="/" 
                    onClick={() => setMenuOpen(false)}
                    className="mobile-link"
                  >
                    Accueil
                  </RouterLink>
                )}
              </li>

              {location.pathname === "/" && (
                <li>
                  <ScrollLink 
                    to="Exercices" 
                    spy smooth 
                    offset={-100} 
                    onClick={() => setMenuOpen(false)}
                    className="mobile-link"
                  >
                    À propos
                  </ScrollLink>
                </li>
              )}

              {user && (
                <>
                  <li>
                    <RouterLink 
                      to="/soumettre" 
                      onClick={() => setMenuOpen(false)}
                      className="mobile-link"
                    >
                      <Upload className="mobile-icon" /> Soumettre
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink 
                      to={user.role === 'PR' ? "/dashboard/prof" : "/tableau-de-bord"} 
                      onClick={() => setMenuOpen(false)}
                      className="mobile-link"
                    >
                      <LayoutDashboard className="mobile-icon" /> Dashboard
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink 
                      to="/exercices" 
                      onClick={() => setMenuOpen(false)}
                      className="mobile-link"
                    >
                      <Database className="mobile-icon" /> Exercices
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink 
                      to="/profil" 
                      onClick={() => setMenuOpen(false)}
                      className="mobile-link"
                    >
                      <User className="mobile-icon" /> Mon Profil
                    </RouterLink>
                  </li>
                </>
              )}

              <li className="mobile-auth">
                {user ? (
                  <button
                    onClick={handleLogout}
                    className="mobile-logout"
                  >
                    <LogOut className="mobile-icon" /> Déconnexion
                  </button>
                ) : (
                  <div className="mobile-auth-buttons">
                    <RouterLink 
                      to="/login" 
                      onClick={() => setMenuOpen(false)}
                      className="mobile-login"
                    >
                      Connexion
                    </RouterLink>
                    <RouterLink 
                      to="/signup" 
                      onClick={() => setMenuOpen(false)}
                      className="mobile-signup"
                    >
                      Inscription
                    </RouterLink>
                  </div>
                )}
              </li>
            </ul>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Navbar;