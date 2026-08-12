import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Smartphone, TrendingUp, PieChart, BarChart3, Users, Download, Star, Shield, RefreshCw } from 'lucide-react';
import { getDashboardStats } from '../api/api';

const HomePage = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000000) return `${(num / 1000000000).toFixed(1)}B+`;
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M+`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K+`;
    return num.toString();
  };
  return (
    <div className="pt-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-google-green/10 via-transparent to-google-blue/10" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="text-center">
            <div className="inline-flex items-center space-x-2 bg-play-surface rounded-full px-4 py-2 mb-8">
              <Smartphone className="w-5 h-5 text-google-green" />
              <span className="text-sm text-gray-300">Mobile App Market Intelligence</span>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
                Discover Insights from
              </span>
              <br />
              <span className="bg-gradient-to-r from-google-green to-google-blue bg-clip-text text-transparent">
                Mobile App Data
              </span>
            </h1>
            
            <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-10">
              Analyze {loading ? 'thousands' : stats?.total_apps?.toLocaleString() || 'thousands'} of mobile applications across {loading ? '50+' : stats?.total_categories || '50+'} categories, ratings, installs, and pricing models. 
              Make data-driven decisions for your next app venture.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/dashboard"
                className="w-full sm:w-auto bg-google-blue hover:bg-blue-600 text-white font-medium py-3 px-8 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
              >
                <TrendingUp className="w-5 h-5" />
                <span>Explore Dashboard</span>
              </Link>
              <Link
                to="/predict"
                className="w-full sm:w-auto bg-gradient-to-r from-google-green to-google-blue hover:from-green-600 hover:to-blue-600 text-white font-medium py-3 px-8 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
              >
                <Smartphone className="w-5 h-5" />
                <span>Predict Success</span>
              </Link>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto bg-play-surface hover:bg-gray-700 text-white font-medium py-3 px-8 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 border border-gray-700"
              >
                <span>View on GitHub</span>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-play-surface/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-white">Live Statistics</h3>
            <button
              onClick={fetchStats}
              className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="text-sm">Refresh</span>
            </button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <StatCard 
              icon={<Download className="w-8 h-8 text-google-green" />} 
              label="Apps Analyzed" 
              value={loading ? '...' : stats?.total_apps?.toLocaleString() || 'N/A'} 
            />
            <StatCard 
              icon={<Users className="w-8 h-8 text-google-blue" />} 
              label="Categories" 
              value={loading ? '...' : stats?.total_categories || 'N/A'} 
            />
            <StatCard 
              icon={<Star className="w-8 h-8 text-google-yellow" />} 
              label="Avg Rating" 
              value={loading ? '...' : `${stats?.avg_rating?.toFixed(1) || 'N/A'}/5.0`} 
            />
            <StatCard 
              icon={<Shield className="w-8 h-8 text-google-red" />} 
              label="Total Installs" 
              value={loading ? '...' : formatNumber(stats?.total_installs || 0)} 
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Powerful Analytics Features
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Comprehensive tools to understand the mobile app market landscape
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<BarChart3 className="w-8 h-8" />}
              title="Category Analysis"
              description="Explore app distribution across 50+ categories from Games to Education"
              color="google-green"
            />
            <FeatureCard
              icon={<PieChart className="w-8 h-8" />}
              title="Market Share"
              description="Understand free vs paid app distribution and market dominance"
              color="google-blue"
            />
            <FeatureCard
              icon={<Star className="w-8 h-8" />}
              title="Rating Insights"
              description="Analyze user satisfaction patterns and rating distributions"
              color="google-yellow"
            />
            <FeatureCard
              icon={<TrendingUp className="w-8 h-8" />}
              title="Success Prediction"
              description="AI-powered prediction for your app's potential success"
              color="google-green"
            />
            <FeatureCard
              icon={<Users className="w-8 h-8" />}
              title="User Engagement"
              description="Correlate reviews, ratings, and installs for engagement metrics"
              color="google-green"
            />
            <FeatureCard
              icon={<Smartphone className="w-8 h-8" />}
              title="App Comparison"
              description="Compare apps side-by-side across multiple metrics"
              color="google-blue"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-google-green/20 to-google-blue/20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">
            Ready to Explore the Data?
          </h2>
          <p className="text-gray-400 text-lg mb-10">
            Dive into our interactive dashboard and discover actionable insights from thousands of mobile applications.
          </p>
          <Link
            to="/dashboard"
            className="inline-flex items-center space-x-2 bg-google-blue hover:bg-blue-600 text-white font-medium py-4 px-8 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <BarChart3 className="w-5 h-5" />
            <span>Launch Dashboard</span>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-gray-400">
            <p className="mb-2">🎓 University Fourth Year Project | Mobile App Market Analysis Dashboard | 2026</p>
            <p className="text-sm">Built with React, Tailwind CSS, and Flask</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

const StatCard = ({ icon, label, value }) => (
  <div className="stat-card text-center">
    <div className="flex justify-center mb-4">{icon}</div>
    <div className="text-3xl font-bold text-white mb-2">{value}</div>
    <div className="text-gray-400">{label}</div>
  </div>
);

const FeatureCard = ({ icon, title, description, color }) => {
  const colorClasses = {
    'google-green': 'text-google-green',
    'google-blue': 'text-google-blue',
    'google-yellow': 'text-google-yellow',
    'google-red': 'text-google-red',
  };

  return (
    <div className="card hover:scale-105 transition-transform duration-300">
      <div className={`${colorClasses[color]} mb-4`}>{icon}</div>
      <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
};

export default HomePage;
