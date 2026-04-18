// frontend/src/components/Navbar.jsx

import { Link, useLocation } from 'react-router-dom';
import { Brain, Activity } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();

  return (
    <nav className="bg-white border-b shadow-sm">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 font-bold text-xl text-blue-600">
            <Brain className="w-6 h-6" />
            <span>MedAI Correlator</span>
          </Link>
          <div className="flex items-center gap-6 text-sm text-gray-600">
            <Link to="/" className={`hover:text-blue-600 ${location.pathname === '/' ? 'text-blue-600 font-medium' : ''}`}>
              Dashboard
            </Link>
            <Link to="/demo" className={`hover:text-blue-600 ${location.pathname === '/demo' ? 'text-blue-600 font-medium' : ''}`}>
              Demo
            </Link>
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
              🔒 HIPAA Compliant
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
}
