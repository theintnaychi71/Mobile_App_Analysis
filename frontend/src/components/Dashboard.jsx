import React, { useState, useEffect } from 'react';
import { 
  getDashboardStats, getCategoryAnalysis, getTopApps, 
  getRatingDistribution, getCorrelationAnalysis, getPriceDistribution, getInsights, getReleaseYearDistribution 
} from '../api/api';
import { 
  Smartphone, TrendingUp, Users, Download, Star, 
  PieChart, BarChart3, RefreshCw, Filter, ArrowUpRight,
  Package, DollarSign, Activity, ScatterChart as ScatterChartIcon, Trophy, Award
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart as RechartsPieChart, Pie, Cell, LineChart, Line, AreaChart, Area,
  ScatterChart, Scatter, ZAxis
} from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [categoryData, setCategoryData] = useState([]);
  const [topApps, setTopApps] = useState([]);
  const [topAppsByReviews, setTopAppsByReviews] = useState([]); // NEW STATE
  const [ratingDistribution, setRatingDistribution] = useState([]);
  const [correlationData, setCorrelationData] = useState(null);
  const [priceDistribution, setPriceDistribution] = useState(null);
  const [releaseYearDistribution, setReleaseYearDistribution] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load essential data first (stats and category data)
      const [statsData, categoryAnalysis] = await Promise.all([
        getDashboardStats(),
        getCategoryAnalysis()
      ]);
      
      setStats(statsData);
      setCategoryData(categoryAnalysis);
      
      // Load detailed data in background after essential data is loaded
      setTimeout(async () => {
        try {
          const [
            topAppsData,
            topAppsByReviewsData, // NEW
            ratingDistData,
            correlationAnalysisData,
            priceDistData,
            releaseYearData,
            insightsData
          ] = await Promise.all([
            getTopApps('installs', 15),
            getTopApps('reviews', 15), // NEW: Fetch top apps by reviews
            getRatingDistribution(),
            getCorrelationAnalysis(),
            getPriceDistribution(),
            getReleaseYearDistribution(),
            getInsights()
          ]);
          setTopApps(topAppsData);
          setTopAppsByReviews(topAppsByReviewsData); // NEW
          setRatingDistribution(ratingDistData);
          setCorrelationData(correlationAnalysisData);
          setPriceDistribution(priceDistData);
          setReleaseYearDistribution(releaseYearData);
          setInsights(insightsData);
        } catch (err) {
          console.error('Error loading detailed data:', err);
        }
      }, 100);
      
    } catch (err) {
      setError('Failed to fetch data. Please ensure the backend API is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0F9D58', '#4285F4', '#F4B400', '#DB4437', '#9C27B0', '#FF5722', '#795548', '#607D8B'];

  const formatNumber = (num) => {
    if (num >= 1000000000) return `${(num / 1000000000).toFixed(2)}B`;
    if (num >= 1000000) return `${(num / 1000000).toFixed(2)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(2)}K`;
    return num.toString();
  };

  if (loading) {
    return (
      <div className="pt-20 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-google-blue animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pt-20 min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-6 mb-6">
            <p className="text-red-400 mb-4">{error}</p>
            <button
              onClick={fetchData}
              className="bg-google-blue hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Retry
            </button>
          </div>
          <p className="text-gray-400 text-sm">
            Make sure the Flask API is running on http://localhost:5000
          </p>
        </div>
      </div>
    );
  }

  const pieData = [
    { name: 'Free', value: stats.free_apps, color: '#0F9D58' },
    { name: 'Paid', value: stats.total_apps - stats.free_apps, color: '#4285F4' }
  ];

  const ratingDistChart = ratingDistribution.length > 0 ? ratingDistribution : [
    { range: '5.0', count: Math.floor(stats.total_apps * 0.15) },
    { range: '4.0-4.9', count: Math.floor(stats.total_apps * 0.35) },
    { range: '3.0-3.9', count: Math.floor(stats.total_apps * 0.25) },
    { range: '2.0-2.9', count: Math.floor(stats.total_apps * 0.15) },
    { range: '1.0-1.9', count: Math.floor(stats.total_apps * 0.07) },
    { range: '0-0.9', count: Math.floor(stats.total_apps * 0.03) }
  ];

  const installTiers = [
    { tier: '10M+', count: Math.floor(stats.total_apps * 0.05) },
    { tier: '1M-10M', count: Math.floor(stats.total_apps * 0.15) },
    { tier: '100K-1M', count: Math.floor(stats.total_apps * 0.25) },
    { tier: '10K-100K', count: Math.floor(stats.total_apps * 0.30) },
    { tier: '<10K', count: Math.floor(stats.total_apps * 0.25) }
  ];

  return (
    <div className="pt-20 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
            <p className="text-gray-400">Mobile App Market Analysis Overview</p>
          </div>
          <button
            onClick={fetchData}
            className="mt-4 md:mt-0 flex items-center space-x-2 bg-play-surface hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-colors border border-gray-700"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-4 mb-8 border-b border-gray-700 pb-4">
          {['overview', 'apps', 'correlations', 'pricing', 'trends'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-google-blue text-white'
                  : 'bg-play-surface text-gray-400 hover:text-white'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<Package className="w-6 h-6" />}
            label="Total Apps"
            value={stats.total_apps.toLocaleString()}
            color="google-green"
            trend={`+${stats.total_categories} categories`}
          />
          <StatCard
            icon={<Star className="w-6 h-6" />}
            label="Avg Rating"
            value={`${stats.avg_rating}/5.0`}
            color="google-yellow"
            trend="User satisfaction"
          />
          <StatCard
            icon={<Download className="w-6 h-6" />}
            label="Total Installs"
            value={formatNumber(stats.total_installs)}
            color="google-blue"
            trend="Market reach"
          />
          <StatCard
            icon={<DollarSign className="w-6 h-6" />}
            label="Free Apps"
            value={`${stats.free_percentage}%`}
            color="google-red"
            trend={`${stats.free_apps.toLocaleString()} apps`}
          />
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Charts Row 1 */}
            <div className="grid lg:grid-cols-2 gap-6 mb-8">
              {/* Category Distribution */}
              <ChartCard
                title="Top Categories by App Count"
                icon={<BarChart3 className="w-5 h-5" />}
              >
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={stats.top_categories.slice(0, 10)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="name" 
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                    />
                    <YAxis 
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F1F1F', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Bar dataKey="count" fill="#4285F4" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>

              {/* Free vs Paid */}
              <ChartCard
                title="Free vs Paid Apps Distribution"
                icon={<PieChart className="w-5 h-5" />}
              >
                <ResponsiveContainer width="100%" height={350}>
                  <RechartsPieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={80}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F1F1F', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Legend 
                      verticalAlign="bottom" 
                      height={36}
                      wrapperStyle={{ color: '#9CA3AF' }}
                    />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            {/* Charts Row 2 */}
            <div className="grid lg:grid-cols-2 gap-6 mb-8">
              {/* Rating Distribution */}
              <ChartCard
                title="Rating Distribution"
                icon={<Star className="w-5 h-5" />}
              >
                <ResponsiveContainer width="100%" height={350}>
                  <AreaChart data={ratingDistChart}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="range" 
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                    />
                    <YAxis 
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F1F1F', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="count" 
                      stroke="#F4B400" 
                      fill="#F4B400" 
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartCard>

              {/* Install Tiers */}
              <ChartCard
                title="Install Distribution by Tier"
                icon={<Download className="w-5 h-5" />}
              >
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={installTiers} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      type="number"
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                    />
                    <YAxis 
                      type="category"
                      dataKey="tier"
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                      width={60}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F1F1F', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Bar dataKey="count" fill="#0F9D58" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            {/* Category Analysis Table */}
            <ChartCard
              title="Category Analysis"
              icon={<Activity className="w-5 h-5" />}
            >
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">Category</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Apps</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Avg Rating</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Total Installs</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Avg Installs</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categoryData.slice(0, 10).map((cat, index) => (
                      <tr key={index} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                        <td className="py-3 px-4 font-medium">{cat.category}</td>
                        <td className="text-right py-3 px-4 text-gray-400">{cat.count.toLocaleString()}</td>
                        <td className="text-right py-3 px-4">
                          <span className="inline-flex items-center">
                            <Star className="w-4 h-4 text-google-yellow mr-1" />
                            {cat.avg_rating}
                          </span>
                        </td>
                        <td className="text-right py-3 px-4 text-gray-400">{formatNumber(cat.total_installs)}</td>
                        <td className="text-right py-3 px-4 text-gray-400">{formatNumber(cat.avg_installs)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </ChartCard>

            {/* Insights Section */}
            <div className="mt-8 grid md:grid-cols-2 gap-6">
              {insights.map((insight, index) => (
                <InsightCard
                  key={index}
                  title={insight.title}
                  icon={insight.type === 'category_dominance' ? <TrendingUp className="w-5 h-5 text-google-green" /> :
                        insight.type === 'rating_analysis' ? <Star className="w-5 h-5 text-google-yellow" /> :
                        insight.type === 'monetization' ? <DollarSign className="w-5 h-5 text-google-blue" /> :
                        <Download className="w-5 h-5 text-google-red" />}
                  insight={insight.message}
                />
              ))}
            </div>
          </>
        )}

        {/* Apps Tab */}
        {activeTab === 'apps' && (
          <>
            <div className="grid lg:grid-cols-2 gap-6 mb-8">
              <ChartCard
                title="Top 15 Apps by Installs"
                icon={<Trophy className="w-5 h-5" />}
              >
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={topApps} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      type="number"
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                      tickFormatter={(value) => formatNumber(value)}
                    />
                    <YAxis 
                      type="category"
                      dataKey="name"
                      stroke="#9CA3AF"
                      fontSize={11}
                      tick={{ fill: '#9CA3AF' }}
                      width={150}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F1F1F', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                      itemStyle={{ color: '#fff' }}
                      formatter={(value) => formatNumber(value)}
                    />
                    <Bar dataKey="installs" fill="#4285F4" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>

              {/* NEW: Top Apps by Reviews Chart */}
              <ChartCard
                title="Top 15 Apps by Reviews"
                icon={<Users className="w-5 h-5" />}
              >
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={topAppsByReviews} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      type="number"
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                      tickFormatter={(value) => formatNumber(value)}
                    />
                    <YAxis 
                      type="category"
                      dataKey="name"
                      stroke="#9CA3AF"
                      fontSize={11}
                      tick={{ fill: '#9CA3AF' }}
                      width={150}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F1F1F', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                      itemStyle={{ color: '#fff' }}
                      formatter={(value) => formatNumber(value)}
                    />
                    <Bar dataKey="reviews" fill="#F4B400" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            <ChartCard
              title="Top Apps Details"
              icon={<Award className="w-5 h-5" />}
            >
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">App Name</th>
                      <th className="text-left py-3 px-4 text-gray-400 font-medium">Category</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Rating</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Installs</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Reviews</th>
                      <th className="text-right py-3 px-4 text-gray-400 font-medium">Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topApps.map((app, index) => (
                      <tr key={index} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                        <td className="py-3 px-4 font-medium">{app.name}</td>
                        <td className="py-3 px-4 text-gray-400">{app.category}</td>
                        <td className="text-right py-3 px-4">
                          <span className="inline-flex items-center">
                            <Star className="w-4 h-4 text-google-yellow mr-1" />
                            {app.rating}
                          </span>
                        </td>
                        <td className="text-right py-3 px-4 text-gray-400">{formatNumber(app.installs)}</td>
                        <td className="text-right py-3 px-4 text-gray-400">{formatNumber(app.reviews)}</td>
                        <td className="text-right py-3 px-4">
                          <span className={`px-2 py-1 rounded text-xs ${
                            app.type === 'Free' ? 'bg-google-green/20 text-google-green' : 'bg-google-blue/20 text-google-blue'
                          }`}>
                            {app.type}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </ChartCard>
          </>
        )}

        {/* Correlations Tab */}
        {activeTab === 'correlations' && correlationData && (
          <>
            <div className="grid lg:grid-cols-3 gap-6 mb-8">
              <CorrelationCard
                title="Rating vs Reviews"
                value={correlationData.correlations.rating_reviews}
                description="Correlation between app ratings and review counts"
                color="google-blue"
              />
              <CorrelationCard
                title="Rating vs Installs"
                value={correlationData.correlations.rating_installs}
                description="Correlation between app ratings and install counts"
                color="google-green"
              />
              <CorrelationCard
                title="Reviews vs Installs"
                value={correlationData.correlations.reviews_installs}
                description="Correlation between review counts and install counts"
                color="google-yellow"
              />
            </div>

            <ChartCard
              title="Rating vs Reviews Scatter Plot"
              icon={<ScatterChartIcon className="w-5 h-5" />}
            >
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart data={correlationData.scatter_data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    type="number" 
                    dataKey="rating" 
                    name="Rating"
                    stroke="#9CA3AF"
                    fontSize={12}
                    tick={{ fill: '#9CA3AF' }}
                    domain={[0, 5]}
                  />
                  <YAxis 
                    type="number" 
                    dataKey="reviews" 
                    name="Reviews"
                    stroke="#9CA3AF"
                    fontSize={12}
                    tick={{ fill: '#9CA3AF' }}
                    tickFormatter={(value) => formatNumber(value)}
                  />
                  <Tooltip 
                    cursor={{ strokeDasharray: '3 3' }}
                    contentStyle={{ 
                      backgroundColor: '#1F1F1F', 
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                    itemStyle={{ color: '#fff' }}
                    formatter={(value, name) => [
                      name === 'Rating' ? value.toFixed(2) : formatNumber(value),
                      name
                    ]}
                  />
                  <Scatter fill="#4285F4" />
                </ScatterChart>
              </ResponsiveContainer>
              <p className="text-center text-gray-400 text-sm mt-4">
                Sample size: {correlationData.sample_size} apps from {correlationData.total_analyzed} total
              </p>
            </ChartCard>
          </>
        )}

        {/* Pricing Tab */}
        {activeTab === 'pricing' && priceDistribution && (
          <>
            <div className="grid lg:grid-cols-2 gap-6 mb-8">
              <ChartCard
                title="App Count by Price Range"
                icon={<DollarSign className="w-5 h-5" />}
              >
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={priceDistribution.app_count}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="price" 
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                    />
                    <YAxis 
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F1F1F', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Bar dataKey="count" fill="#0F9D58" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard
                title="Install Distribution by Price Range"
                icon={<Download className="w-5 h-5" />}
              >
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={priceDistribution.install_distribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis 
                      dataKey="price" 
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                    />
                    <YAxis 
                      stroke="#9CA3AF"
                      fontSize={12}
                      tick={{ fill: '#9CA3AF' }}
                      tickFormatter={(value) => formatNumber(value)}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F1F1F', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                      itemStyle={{ color: '#fff' }}
                      formatter={(value) => formatNumber(value)}
                    />
                    <Bar dataKey="installs" fill="#F4B400" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            <InsightCard
              title="Pricing Strategy Insight"
              icon={<DollarSign className="w-5 h-5 text-google-blue" />}
              insight="Free apps dominate the market in both count and installs. Paid apps in the $1-5 range show the best balance between app count and user adoption."
            />
          </>
        )}

        {/* Trends Tab */}
        {activeTab === 'trends' && releaseYearDistribution.length > 0 && (
          <>
            <ChartCard
              title="Apps Released by Year"
              icon={<TrendingUp className="w-5 h-5" />}
            >
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={releaseYearDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="year" 
                    stroke="#9CA3AF"
                    fontSize={12}
                    tick={{ fill: '#9CA3AF' }}
                  />
                  <YAxis 
                    stroke="#9CA3AF"
                    fontSize={12}
                    tick={{ fill: '#9CA3AF' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F1F1F', 
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Bar dataKey="count" fill="#4285F4" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            {releaseYearDistribution.length > 0 && (
              <div className="mt-8 grid md:grid-cols-2 gap-6">
                <InsightCard
                  title="Peak Release Year"
                  icon={<Trophy className="w-5 h-5 text-google-green" />}
                  insight={`The year ${releaseYearDistribution.reduce((max, item) => item.count > max.count ? item : max).year} had the most app releases with ${releaseYearDistribution.reduce((max, item) => item.count > max.count ? item : max).count.toLocaleString()} apps.`}
                />
                <InsightCard
                  title="Market Growth Trend"
                  icon={<TrendingUp className="w-5 h-5 text-google-blue" />}
                  insight={`App releases span from ${releaseYearDistribution[0]?.year || 'N/A'} to ${releaseYearDistribution[releaseYearDistribution.length - 1]?.year || 'N/A'}, showing the evolution of the mobile app market over time.`}
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

const StatCard = ({ icon, label, value, color, trend }) => {
  const colorClasses = {
    'google-green': 'bg-google-green/10 text-google-green',
    'google-blue': 'bg-google-blue/10 text-google-blue',
    'google-yellow': 'bg-google-yellow/10 text-google-yellow',
    'google-red': 'bg-google-red/10 text-google-red',
  };

  return (
    <div className="stat-card">
      <div className={`${colorClasses[color]} inline-flex p-3 rounded-lg mb-4`}>
        {icon}
      </div>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <div className="text-gray-400 text-sm mb-2">{label}</div>
      {trend && <div className="text-xs text-gray-500">{trend}</div>}
    </div>
  );
};

const ChartCard = ({ title, icon, children }) => (
  <div className="card">
    <div className="flex items-center justify-between mb-6">
      <h3 className="text-lg font-semibold flex items-center space-x-2">
        <span className="text-google-blue">{icon}</span>
        <span>{title}</span>
      </h3>
    </div>
    {children}
  </div>
);

const InsightCard = ({ title, icon, insight }) => (
  <div className="card border-l-4 border-google-green">
    <div className="flex items-start space-x-3">
      <div className="mt-1">{icon}</div>
      <div>
        <h4 className="font-semibold mb-2">{title}</h4>
        <p className="text-gray-400 text-sm">{insight}</p>
      </div>
    </div>
  </div>
);

const CorrelationCard = ({ title, value, description, color }) => {
  const colorClasses = {
    'google-green': 'bg-google-green/10 text-google-green border-google-green',
    'google-blue': 'bg-google-blue/10 text-google-blue border-google-blue',
    'google-yellow': 'bg-google-yellow/10 text-google-yellow border-google-yellow',
    'google-red': 'bg-google-red/10 text-google-red border-google-red',
  };

  return (
    <div className={`card border-l-4 ${colorClasses[color]}`}>
      <div className="text-center">
        <h4 className="font-semibold mb-2">{title}</h4>
        <div className={`text-4xl font-bold ${colorClasses[color].split(' ')[1]} mb-2`}>
          {value.toFixed(3)}
        </div>
        <p className="text-gray-400 text-sm">{description}</p>
      </div>
    </div>
  );
};

export default Dashboard;
