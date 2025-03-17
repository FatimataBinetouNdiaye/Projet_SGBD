import React, { useState, useEffect } from 'react';
import icon from '/src/assets/icon.png';
import { Link as ScrollLink } from 'react-scroll';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { FaBars, FaXmark } from 'react-icons/fa6';
import { Database, Upload, LayoutDashboard } from 'lucide-react';

const Navbar = () => {
  const [isMenuOpen, setMenuOpen] = useState(false);
  const [isSticky, setIsSticky] = useState(false);
  const location = useLocation(); // Permet de savoir sur quelle page on est

  const toggleMenu = () => setMenuOpen(!isMenuOpen);

  useEffect(() => {
    const handleScroll = () => setIsSticky(window.scrollY > 100);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={`w-full fixed top-0 left-0 right-0 bg-white md:bg-transparent`}>
      <nav className={`py-4 lg:px-14 px-4 ${isSticky ? 'sticky top-0 left-0 right-0 border-b bg-white duration-300' : ''}`}>
        <div className="flex justify-between items-center text-base gap-8">
          <RouterLink to="/" className="text-2xl font-semibold flex items-center space-x-3">
            <img src={icon} alt="non disponible" className="w-10 inline-block items-center" />
            <span className="text-[#263238]">Platforme Intelligente</span>
          </RouterLink>

          {/* Navigation */}
          <ul className="md:flex space-x-12 hidden">
            {location.pathname === "/" ? (
              <>
                <li>
                  <ScrollLink to="Accueil" spy={true} smooth={true} offset={-100} className="block text-base text-gray-900 hover:text-brandPrimary first:font-medium">
                    Accueil
                  </ScrollLink>
                </li>
                <li>
                  <ScrollLink to="Exercices" spy={true} smooth={true} offset={-100} className="block text-base text-gray-900 hover:text-brandPrimary first:font-medium">
                     A propos
                  </ScrollLink>
                </li>
              </>
            ) : (
              <li>
                <RouterLink to="/" className="block text-base text-gray-900 hover:text-brandPrimary first:font-medium">
                  Accueil
                </RouterLink>
              </li>
            )}
            <li>
              <RouterLink to="/exercices" className="block text-base text-gray-900 hover:text-brandPrimary first:font-medium">
                <Database className="inline-block w-5 h-5 mr-2" /> Liste des Exercices
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/soumettre" className="block text-base text-gray-900 hover:text-brandPrimary first:font-medium">
                <Upload className="inline-block w-5 h-5 mr-2" /> Soumettre
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/tableau-de-bord" className="block text-base text-gray-900 hover:text-brandPrimary first:font-medium">
                <LayoutDashboard className="inline-block w-5 h-5 mr-2" /> Tableau de bord
              </RouterLink>
            </li>
          </ul>

          {/* Boutons Connexion & Inscription */}
          <div className="space-x-12 hidden lg:flex items-center">
            <RouterLink to="/login" className="text-brandPrimary hover:text-gray-900">Login</RouterLink>
            <button className="bg-brandPrimary text-white py-2 px-4 transition-all duration-300 rounded hover:bg-neutralDGrey">
              <RouterLink to="/signup"> Sign up </RouterLink>
            </button>
          </div>

          {/* Bouton Menu Mobile */}
          <div className="md:hidden">
            <button onClick={toggleMenu} className="focus:outline-none focus:text-gray-500">
              {isMenuOpen ? <FaXmark className="h-6 w-6 text-neutralDGrey" /> : <FaBars className="h-6 w-6 text-neutralDGrey" />}
            </button>
          </div>
        </div>

        {/* Menu Mobile */}
        {isMenuOpen && (
          <div className="space-y-4 px-4 mt-16 py-7 bg-brandPrimary fixed top-0 right-0 left-0">
            {location.pathname === "/" ? (
              <>
                <ScrollLink to="Accueil" spy={true} smooth={true} offset={-100} className="block text-base text-white hover:text-brandPrimary first:font-medium" onClick={toggleMenu}>
                  Accueil
                </ScrollLink>
                <ScrollLink to="Exercices" spy={true} smooth={true} offset={-100} className="block text-base text-white hover:text-brandPrimary first:font-medium" onClick={toggleMenu}>
                   A propos
                </ScrollLink>
              </>
            ) : (
              <RouterLink to="/" className="block text-base text-white hover:text-brandPrimary first:font-medium" onClick={toggleMenu}>
                Accueil
              </RouterLink>
            )}
            <RouterLink to="/exercices" className="block text-base text-white hover:text-brandPrimary first:font-medium" onClick={toggleMenu}>
              <Database className="inline-block w-5 h-5 mr-2" /> Liste des Exercices
            </RouterLink>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Navbar;
