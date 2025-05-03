import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';

export default function DarkModeToggle() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Vérifier le localStorage et les préférences système
    const savedMode = localStorage.getItem('darkMode');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedMode === 'true' || (savedMode === null && systemPrefersDark)) {
      enableDarkMode();
    }
  }, []);

  const enableDarkMode = () => {
    document.documentElement.classList.add('dark');
    setIsDark(true);
    localStorage.setItem('darkMode', 'true');
  };

  const disableDarkMode = () => {
    document.documentElement.classList.remove('dark');
    setIsDark(false);
    localStorage.setItem('darkMode', 'false');
  };

  const toggleDarkMode = () => {
    if (document.documentElement.classList.contains('dark')) {
      disableDarkMode();
    } else {
      enableDarkMode();
    }
  };

  return (
    <button
      onClick={toggleDarkMode}
      className="flex items-center gap-2 p-2 rounded-md bg-neutralSilver dark:bg-darkBg text-neutralDGrey dark:text-darkText hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-300"
      aria-label={isDark ? 'Passer en mode clair' : 'Passer en mode sombre'}
    >
      {isDark ? (
        <>
          <Sun className="w-5 h-5" />
          <span className="hidden sm:inline">Mode clair</span>
        </>
      ) : (
        <>
          <Moon className="w-5 h-5" />
          <span className="hidden sm:inline">Mode sombre</span>
        </>
      )}
    </button>
  );
}