import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Smartphone, BarChart3, Home, TrendingUp } from 'lucide-react';
import HomePage from './components/HomePage';
import Dashboard from './components/Dashboard';
import Prediction from './components/Prediction';

function App() {
  return (
    <Router>
      <AppLayout />
    </Router>
  );
}

function AppLayout() {
  const location = useLocation();
  const isPredictionPage = location.pathname === '/predict';

  return (
      <div className="min-h-screen bg-play-dark">
        {!isPredictionPage && <Navbar />}
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/predict" element={<Prediction />} />
        </Routes>
      </div>
  );
}

function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration- ${
      scrolled ? 'bg-play-dark/95 backdrop-blur-md shadow-lg' : 'bg-play-dark'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <div className="bg-gradient-to-br from-google-green to-google-blue p-2 rounded-lg">
              <Smartphone className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-google-green to-google-blue bg-clip-text text-transparent">
              App Market Analysis
            </span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-8">
            <NavLink to="/" icon={<Home className="w-4 h-4" />}>
              Home
            </NavLink>
            <NavLink to="/dashboard" icon={<BarChart3 className="w-4 h-4" />}>
              Dashboard
            </NavLink>
            <NavLink to="/predict" icon={<TrendingUp className="w-4 h-4" />}>
              Predict
            </NavLink>
          </div>

          <Link
            to="/dashboard"
            className="bg-google-blue hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center space-x-2"
          >
            <TrendingUp className="w-4 h-4" />
            <span>Explore Data</span>
          </Link>
        </div>
      </div>
    </nav>
  );
}

function NavLink({ to, children, icon }) {
  return (
    <Link
      to={to}
      className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors duration-200"
    >
      {icon}
      <span>{children}</span>
    </Link>
  );
}

export default App;
