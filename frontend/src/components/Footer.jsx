import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Twitter, Instagram, Linkedin, Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  const [email, setEmail] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Email soumis:", email);
  };

  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="container mx-auto px-4">
        {/* Grille du footer */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Section 1 : Logo et description */}
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Plateforme Intelligente</h2>
            <p className="text-gray-400">
              Une solution innovante pour l'évaluation et l'amélioration des performances académiques.
            </p>
            {/* Icônes des réseaux sociaux */}
            <div className="flex space-x-4">
              <a href="#" aria-label="Facebook" className="text-gray-400 hover:text-white">
                <Facebook className="h-6 w-6" />
              </a>
              <a href="#" aria-label="Twitter" className="text-gray-400 hover:text-white">
                <Twitter className="h-6 w-6" />
              </a>
              <a href="#" aria-label="Instagram" className="text-gray-400 hover:text-white">
                <Instagram className="h-6 w-6" />
              </a>
              <a href="#" aria-label="LinkedIn" className="text-gray-400 hover:text-white">
                <Linkedin className="h-6 w-6" />
              </a>
            </div>
          </div>

          {/* Section 2 : Liens rapides */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Liens rapides</h3>
            <ul className="space-y-2">
              <li><Link to="/" className="text-gray-400 hover:text-white">Accueil</Link></li>
              <li><Link to="/apropos" className="text-gray-400 hover:text-white">À propos</Link></li>
              <li><Link to="/fonctionnalites" className="text-gray-400 hover:text-white">Fonctionnalités</Link></li>
              <li><Link to="/contact" className="text-gray-400 hover:text-white">Contact</Link></li>
            </ul>
          </div>

          {/* Section 3 : Newsletter */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Newsletter</h3>
            <p className="text-gray-400">
              Abonnez-vous à notre newsletter pour recevoir les dernières mises à jour.
            </p>
            <form className="flex space-x-2" onSubmit={handleSubmit}>
              <input
                type="email"
                placeholder="Votre email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-brandPrimary"
                required
              />
              <button
                type="submit"
                className="bg-brandPrimary text-white px-4 py-2 rounded-lg hover:bg-brandPrimaryDark transition-all"
              >
                S'abonner
              </button>
            </form>
          </div>

          {/* Section 4 : Contact */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Contact</h3>
            <ul className="space-y-2">
              <li className="flex items-center space-x-2">
                <Mail className="h-5 w-5 text-gray-400" />
                <a href="mailto:fatoubintoundiaye704@gmail.com" className="text-gray-400 hover:text-white">
                  fatoubintoundiaye704@gmail.com
                </a>
              </li>
              <li className="flex items-center space-x-2">
                <Phone className="h-5 w-5 text-gray-400" />
                <a href="tel:+1234567890" className="text-gray-400 hover:text-white">
                  +221 785901973
                </a>
              </li>
              <li className="flex items-center space-x-2">
                <MapPin className="h-5 w-5 text-gray-400" />
                <span className="text-gray-400">Ouakam,Dakar,Sénégal</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Section du copyright */}
        <div className="border-t border-gray-800 mt-8 pt-8 text-center">
          <p className="text-gray-400">
            &copy; {new Date().getFullYear()} Platforme Intelligente. Tous droits réservés.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
