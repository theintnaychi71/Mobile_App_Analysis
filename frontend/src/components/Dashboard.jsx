import React, { useState, useEffect } from 'react';
import { 
  getDashboardStats, getCategoryAnalysis, getTopApps, 
  getRatingDistribution, getCorrelationAnalysis, getPriceDistribution, getInsights, getReleaseYearDistribution,
  getFilterOptions, getTopDevelopers, getContentRatingDistribution, getInstallDistribution
} from '../api/api';
import { 
  Smartphone, TrendingUp, Users, Download, Star, 
  PieChart, BarChart3, RefreshCw, Filter, ArrowUpRight,
  Package, DollarSign, Activity, ScatterChart as ScatterChartIcon, Trophy, Award, Calendar, AlertCircle
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
  const [ratingDistribution, setRatingDistribution] = useState([]);
  const [correlationData, setCorrelationData] = useState(null);
  const [priceDistribution, setPriceDistribution] = useState(null);
  const [releaseYearDistribution, setReleaseYearDistribution] = useState([]);
  const [insights, setInsights] = useState([]);
  const [installDistribution, setInstallDistribution] = useState([]);
  
  const [filters, setFilters] = useState({ category: 'All', type: 'All', contentRating: 'All' });
  const [filterOptions, setFilterOptions] = useState({ categories: ['All'], types: ['All', 'Free', 'Paid'], contentRatings: ['All'] });
  
  const [topDevelopers, setTopDevelopers] = useState([]);
  const [contentRatingData, setContentRatingData] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const loadFilterOptions = async () => {
      try {
        const options = await getFilterOptions();
        setFilterOptions({
          categories: ['All', ...options.categories],
          types: ['All', 'Free', 'Paid'],
          contentRatings: ['All', ...options.content_ratings]
        });
      } catch (err) {
        console.error('Error loading filter options:', err);
      }
    };
    loadFilterOptions();
  }, []);

  useEffect(() => {
    fetchData();
  }, [filters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [statsData, categoryAnalysis] = await Promise.all([
        getDashboardStats(filters),
        getCategoryAnalysis(filters)
      ]);
      
      setStats(statsData);
      setCategoryData(categoryAnalysis);
      
      setTimeout(async () => {
        try {
          const [
            topAppsData,
            topDevelopersData,
            contentRatingDistData,
            ratingDistData,
            correlationAnalysisData,
            priceDistData,
            releaseYearData,
            insightsData,
            installDistData
          ] = await Promise.all([
            getTopApps('installs', 50, filters),
            getTopDevelopers('installs', filters),
            getContentRatingDistribution(filters),
            getRatingDistribution(filters),
            getCorrelationAnalysis(filters),
            getPriceDistribution(filters),
            getReleaseYearDistribution(filters),
            getInsights(filters),
            getInstallDistribution(filters)
          ]);
          setTopApps(topAppsData);
          setTopDevelopers(topDevelopersData);
          setContentRatingData(contentRatingDistData);
          setRatingDistribution(ratingDistData);
          setCorrelationData(correlationAnalysisData);
          setPriceDistribution(priceDistData);
          setReleaseYearDistribution(releaseYearData || []);
          setInsights(insightsData);
          setInstallDistribution(installDistData);
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
            <button onClick={fetchData} className="bg-google-blue hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors">
              Retry
            </button>
          </div>
          <p className="text-gray-400 text-sm">Make sure the Flask API is running on http://localhost:5001</p>
        </div>
      </div>
    );
  }

  const pieData = [
    { name: 'Free', value: stats?.free_apps || 0, color: '#0F9D58' },
    { name: 'Paid', value: (stats?.total_apps || 0) - (stats?.free_apps || 0), color: '#4285F4' }
  ];

  const ratingDistChart = ratingDistribution.length > 0 ? ratingDistribution : [
    { range: '5.0', count: 0 },
    { range: '4.0-4.9', count: 0 },
    { range: '3.0-3.9', count: 0 },
    { range: '2.0-2.9', count: 0 },
    { range: '1.0-1.9', count: 0 },
    { range: '0-0.9', count: 0 }
  ];

  // ✅ DYNAMIC: Uses API data based on active filters, falls back to empty state if not loaded
  const installTiers = installDistribution.length > 0 ? installDistribution : [
    { tier: '10M+', count: 0 },
    { tier: '1M-10M', count: 0 },
    { tier: '100K-1M', count: 0 },
    { tier: '10K-100K', count: 0 },
    { tier: '<10K', count: 0 }
  ];

  // ✅ Scatter data for installs-based plots.
  // Uses backend scatter_data if it includes installs, otherwise falls back to topApps.
  const scatterBase = correlationData?.scatter_data || [];
  const installsScatterData = scatterBase.some(p => typeof p.installs === 'number')
    ? scatterBase
    : topApps;

  return (
    <div className="pt-20 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
            <p className="text-gray-400">Mobile App Market Analysis Overview</p>
          </div>
          <button onClick={fetchData} className="mt-4 md:mt-0 flex items-center space-x-2 bg-play-surface hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-colors border border-gray-700">
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>

        {/* Global Filters */}
        <div className="bg-play-surface border border-gray-700 rounded-xl p-4 mb-8">
          <div className="flex flex-col md:flex-row md:items-end gap-4">
            <div className="flex-1">
              <label className="block text-xs font-medium text-gray-400 mb-1">Category</label>
              <select 
                value={filters.category} 
                onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))} 
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:ring-2 focus:ring-google-blue focus:border-transparent"
              >
                {filterOptions.categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-xs font-medium text-gray-400 mb-1">Type</label>
              <select 
                value={filters.type} 
                onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))} 
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:ring-2 focus:ring-google-blue focus:border-transparent"
              >
                {filterOptions.types.map(type => <option key={type} value={type}>{type}</option>)}
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-xs font-medium text-gray-400 mb-1">Content Rating</label>
              <select 
                value={filters.contentRating} 
                onChange={(e) => setFilters(prev => ({ ...prev, contentRating: e.target.value }))} 
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:ring-2 focus:ring-google-blue focus:border-transparent"
              >
                {filterOptions.contentRatings.map(rating => <option key={rating} value={rating}>{rating}</option>)}
              </select>
            </div>
            <button 
              onClick={() => setFilters({ category: 'All', type: 'All', contentRating: 'All' })} 
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-4 mb-8 border-b border-gray-700 pb-4">
          {['overview', 'apps', 'correlations', 'pricing', 'trends'].map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === tab ? 'bg-google-blue text-white' : 'bg-play-surface text-gray-400 hover:text-white'}`}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard icon={<Package className="w-6 h-6" />} label="Total Apps" value={stats.total_apps.toLocaleString()} color="google-green" trend={`+${stats.total_categories} categories`} />
            <StatCard icon={<Star className="w-6 h-6" />} label="Avg Rating" value={`${stats.avg_rating}/5.0`} color="google-yellow" trend="User satisfaction" />
            <StatCard icon={<Download className="w-6 h-6" />} label="Total Installs" value={formatNumber(stats.total_installs)} color="google-blue" trend="Market reach" />
            <StatCard icon={<DollarSign className="w-6 h-6" />} label="Free Apps" value={`${stats.free_percentage}%`} color="google-red" trend={`${stats.free_apps.toLocaleString()} apps`} />
          </div>
        )}

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Charts Row 1 - DYNAMIC GRID BASED ON CATEGORY FILTER */}
            <div className={`grid gap-6 mb-8 ${filters.category === 'All' ? 'lg:grid-cols-3' : 'lg:grid-cols-2'}`}>
              
              {/* CONDITIONALLY RENDERED: Only shows when Category is 'All' */}
              {filters.category === 'All' && stats?.top_categories && (
               <ChartCard title="Top Categories by App Count" icon={<BarChart3 className="w-5 h-5" />}>
                  <ResponsiveContainer width="100%" height={380}>
                    <BarChart 
                      data={stats.top_categories.slice(0, 10)}
                      margin={{ top: 10, right: 10, left: -20, bottom: 80 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis 
                        dataKey="name" 
                        stroke="#9CA3AF" 
                        fontSize={11} 
                        tick={{ fill: '#9CA3AF' }}
                        interval={0}
                        angle={-90}
                        textAnchor="end"
                        dy={5}
                      />
                      <YAxis stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} 
                        itemStyle={{ color: '#fff' }} 
                      />
                      <Bar dataKey="count" fill="#4285F4" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
              )}

              <ChartCard title="Content Rating Breakdown" icon={<Users className="w-5 h-5" />}>
                <ResponsiveContainer width="100%" height={350}>
                  <RechartsPieChart>
                    <Pie
                      data={contentRatingData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="count"
                      nameKey="rating"
                    >
                      {contentRatingData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                    <Legend verticalAlign="bottom" height={36} wrapperStyle={{ color: '#9CA3AF' }} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard title="Free vs Paid Apps Distribution" icon={<PieChart className="w-5 h-5" />}>
                <ResponsiveContainer width="100%" height={350}>
                  <RechartsPieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={5} dataKey="value">
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                    <Legend verticalAlign="bottom" height={36} wrapperStyle={{ color: '#9CA3AF' }} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            {/* Charts Row 2 */}
            <div className="grid lg:grid-cols-2 gap-6 mb-8">
              <ChartCard title="Rating Distribution" icon={<Star className="w-5 h-5" />}>
                <ResponsiveContainer width="100%" height={350}>
                  <AreaChart data={ratingDistChart}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="range" stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                    <YAxis stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                    <Area type="monotone" dataKey="count" stroke="#F4B400" fill="#F4B400" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard title="Install Distribution by Tier" icon={<Download className="w-5 h-5" />}>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={installTiers} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis type="number" stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                    <YAxis type="category" dataKey="tier" stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} width={70} />
                    <Tooltip contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                    <Bar dataKey="count" fill="#0F9D58" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            <ChartCard title="Category Analysis" icon={<Activity className="w-5 h-5" />}>
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
                        <td className="text-right py-3 px-4"><span className="inline-flex items-center"><Star className="w-4 h-4 text-google-yellow mr-1" />{cat.avg_rating}</span></td>
                        <td className="text-right py-3 px-4 text-gray-400">{formatNumber(cat.total_installs)}</td>
                        <td className="text-right py-3 px-4 text-gray-400">{formatNumber(cat.avg_installs)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </ChartCard>

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

        {/* ✅ Apps Tab — natural, clean leaderboard list (uses existing topApps data, no new API) */}
        {activeTab === 'apps' && (
          <>
            <div className="mb-8">
              <ChartCard title="Top 15 Apps by Installs" icon={<Trophy className="w-5 h-5" />}>
                {/* Column headers (desktop only) */}
                <div className="hidden md:flex items-center gap-4 px-4 pb-3 mb-2 border-b border-gray-700/60 text-xs font-medium uppercase tracking-wider text-gray-500">
                  <span className="w-8 text-center">#</span>
                  <span className="w-10"></span>
                  <span className="flex-1">App</span>
                  <span className="w-16 text-right">Rating</span>
                  <span className="w-20 text-right">Installs</span>
                  <span className="w-16 text-center">Type</span>
                </div>

                <div className="space-y-2">
                  {topApps.slice(0, 15).map((app, index) => {
                    const rank = index + 1;
                    const rankClass =
                      rank === 1 ? 'bg-google-yellow/20 text-google-yellow' :
                      rank === 2 ? 'bg-gray-400/20 text-gray-300' :
                      rank === 3 ? 'bg-orange-600/20 text-orange-400' :
                      'bg-gray-700/40 text-gray-400';

                    return (
                      <div
                        key={`${app.name}-${index}`}
                        className="flex items-center gap-4 px-4 py-3 rounded-xl bg-gray-800/30 border border-gray-700/40 hover:bg-gray-800/60 hover:border-google-blue/40 transition-colors"
                      >
                        {/* Rank */}
                        <span className={`w-8 h-8 shrink-0 rounded-lg flex items-center justify-center text-sm font-bold ${rankClass}`}>
                          {rank}
                        </span>

                        {/* App initial avatar */}
                        <span
                          className="w-10 h-10 shrink-0 rounded-xl flex items-center justify-center text-white font-bold"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        >
                          {app.name?.charAt(0).toUpperCase()}
                        </span>

                        {/* Name + category */}
                        <span className="flex-1 min-w-0">
                          <p className="text-white font-medium truncate" title={app.name}>{app.name}</p>
                          <p className="text-xs text-gray-400 truncate">{app.category}</p>
                        </span>

                        {/* Rating */}
                        <span className="hidden md:inline-flex w-16 shrink-0 items-center justify-end text-sm text-gray-300">
                          <Star className="w-4 h-4 text-google-yellow mr-1" />
                          {app.rating}
                        </span>

                        {/* Installs */}
                        <span className="inline-flex w-20 shrink-0 items-center justify-end text-sm font-semibold text-google-blue">
                          {formatNumber(app.installs)}
                        </span>

                        {/* Type badge */}
                        <span className="hidden md:inline-flex w-16 shrink-0 justify-center">
                          <span className={`px-2 py-0.5 rounded-full text-xs ${
                            app.type === 'Free' ? 'bg-google-green/20 text-google-green' : 'bg-google-blue/20 text-google-blue'
                          }`}>
                            {app.type}
                          </span>
                        </span>
                      </div>
                    );
                  })}

                  {topApps.length === 0 && (
                    <p className="text-center text-gray-500 py-8">No app data available for the selected filters.</p>
                  )}
                </div>
              </ChartCard>
            </div>

            <ChartCard title="Top 10 Developers by Total Installs" icon={<Award className="w-5 h-5" />}>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={topDevelopers} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis type="number" stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} tickFormatter={(value) => formatNumber(value)} />
                  <YAxis type="category" dataKey="developer" stroke="#9CA3AF" fontSize={11} tick={{ fill: '#9CA3AF' }} width={120} />
                  <Tooltip contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} formatter={(value) => formatNumber(value)} />
                  <Bar dataKey="total_installs" fill="#9C27B0" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </>
        )}

        {/* Correlations Tab */}
        {activeTab === 'correlations' && correlationData && (
          <>
            <div className="grid lg:grid-cols-3 gap-6 mb-8">
              <CorrelationCard title="Rating vs Reviews" value={correlationData.correlations.rating_reviews} description="Correlation between app ratings and review counts" color="google-blue" />
              <CorrelationCard title="Rating vs Installs" value={correlationData.correlations.rating_installs} description="Correlation between app ratings and install counts" color="google-green" />
              <CorrelationCard title="Reviews vs Installs" value={correlationData.correlations.reviews_installs} description="Correlation between review counts and install counts" color="google-yellow" />
            </div>

            <div className="space-y-6">
              {/* Rating vs Reviews Scatter Plot */}
              <ChartCard title="Rating vs Reviews Scatter Plot" icon={<ScatterChartIcon className="w-5 h-5" />}>
                <ResponsiveContainer width="100%" height={400}>
                  <ScatterChart data={correlationData.scatter_data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis type="number" dataKey="rating" name="Rating" domain={[0, 5]} stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                    <YAxis type="number" dataKey="reviews" name="Reviews" stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} tickFormatter={(value) => formatNumber(value)} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} formatter={(value, name) => [name === 'Rating' ? value.toFixed(2) : formatNumber(value), name]} />
                    <Scatter fill="#4285F4" />
                  </ScatterChart>
                </ResponsiveContainer>
                <CorrelationInsight value={correlationData.correlations.rating_reviews} xName="rating" yName="review count" />
                <p className="text-center text-gray-400 text-sm mt-4">Sample size: {correlationData.sample_size} apps from {correlationData.total_analyzed} total</p>
              </ChartCard>

              <div className="grid lg:grid-cols-2 gap-6">
                {/* Rating vs Installs Scatter Plot */}
                <ChartCard title="Rating vs Installs Scatter Plot" icon={<ScatterChartIcon className="w-5 h-5" />}>
                  <ResponsiveContainer width="100%" height={400}>
                    <ScatterChart data={installsScatterData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis type="number" dataKey="rating" name="Rating" domain={[0, 5]} stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                      <YAxis type="number" dataKey="installs" name="Installs" stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} tickFormatter={(value) => formatNumber(value)} />
                      <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} formatter={(value, name) => [name === 'Rating' ? value.toFixed(2) : formatNumber(value), name]} />
                      <Scatter fill="#0F9D58" />
                    </ScatterChart>
                  </ResponsiveContainer>
                  <CorrelationInsight value={correlationData.correlations.rating_installs} xName="rating" yName="install count" />
                </ChartCard>

                {/* Reviews vs Installs Scatter Plot */}
                <ChartCard title="Reviews vs Installs Scatter Plot" icon={<ScatterChartIcon className="w-5 h-5" />}>
                  <ResponsiveContainer width="100%" height={400}>
                    <ScatterChart data={installsScatterData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis type="number" dataKey="reviews" name="Reviews" stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                      <YAxis type="number" dataKey="installs" name="Installs" stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} tickFormatter={(value) => formatNumber(value)} />
                      <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} formatter={(value, name) => [name === 'Rating' ? value.toFixed(2) : formatNumber(value), name]} />
                      <Scatter fill="#F4B400" />
                    </ScatterChart>
                  </ResponsiveContainer>
                  <CorrelationInsight value={correlationData.correlations.reviews_installs} xName="review count" yName="install count" />
                </ChartCard>
              </div>
            </div>
          </>
        )}

        {/* Pricing Tab */}
        {activeTab === 'pricing' && priceDistribution && (
          <>
            <div className="grid lg:grid-cols-2 gap-6 mb-8">
              <ChartCard title="App Count by Price Range" icon={<DollarSign className="w-5 h-5" />}>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={priceDistribution.app_count}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="price" stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                    <YAxis stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                    <Bar dataKey="count" fill="#0F9D58" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard title="Install Distribution by Price Range" icon={<Download className="w-5 h-5" />}>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={priceDistribution.install_distribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="price" stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                    <YAxis stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} tickFormatter={(value) => formatNumber(value)} />
                    <Tooltip contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} formatter={(value) => formatNumber(value)} />
                    <Bar dataKey="installs" fill="#F4B400" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            <InsightCard title="Pricing Strategy Insight" icon={<DollarSign className="w-5 h-5 text-google-blue" />} insight="Free apps dominate the market in both count and installs. Paid apps in the $1-5 range show the best balance between app count and user adoption." />
          </>
        )}

        {/* Trends Tab */}
        {activeTab === 'trends' && (
          <div className="space-y-6">
            {releaseYearDistribution && releaseYearDistribution.length > 0 ? (
              <>
                <ChartCard title="Apps Released by Year" icon={<TrendingUp className="w-5 h-5" />}>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={releaseYearDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="year" stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                      <YAxis stroke="#9CA3AF" fontSize={12} tick={{ fill: '#9CA3AF' }} />
                      <Tooltip contentStyle={{ backgroundColor: '#1F1F1F', border: '1px solid #374151', borderRadius: '8px' }} itemStyle={{ color: '#fff' }} />
                      <Bar dataKey="count" fill="#4285F4" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>

                <div className="grid md:grid-cols-2 gap-6">
                  <InsightCard 
                    title="Peak Release Year" 
                    icon={<Trophy className="w-5 h-5 text-google-green" />} 
                    insight={`The year ${releaseYearDistribution.reduce((max, item) => item.count > max.count ? item : max).year} had the most app releases.`} 
                  />
                  <InsightCard 
                    title="Market Growth Trend" 
                    icon={<TrendingUp className="w-5 h-5 text-google-blue" />} 
                    insight={`App releases span from ${releaseYearDistribution[0]?.year || 'N/A'} to ${releaseYearDistribution[releaseYearDistribution.length - 1]?.year || 'N/A'}, showing the evolution of the mobile app market over time.`} 
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="card p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white">Total Years Tracked</h3>
                      <Calendar className="w-5 h-5 text-google-blue" />
                    </div>
                    <p className="text-3xl font-bold text-white">{releaseYearDistribution.length}</p>
                    <p className="text-sm text-gray-400 mt-1">Years of app data</p>
                  </div>

                  <div className="card p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white">Average Apps/Year</h3>
                      <BarChart3 className="w-5 h-5 text-google-green" />
                    </div>
                    <p className="text-3xl font-bold text-white">
                      {Math.round(releaseYearDistribution.reduce((sum, item) => sum + item.count, 0) / releaseYearDistribution.length).toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-400 mt-1">Apps per year</p>
                  </div>

                  <div className="card p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white">Most Recent Year</h3>
                      <ArrowUpRight className="w-5 h-5 text-google-yellow" />
                    </div>
                    <p className="text-3xl font-bold text-white">{releaseYearDistribution[releaseYearDistribution.length - 1]?.year || 'N/A'}</p>
                    <p className="text-sm text-gray-400 mt-1">
                      {releaseYearDistribution[releaseYearDistribution.length - 1]?.count.toLocaleString() || 0} apps
                    </p>
                  </div>
                </div>
              </>
            ) : (
              <div className="card p-12 text-center">
                <AlertCircle className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No Release Year Data Available</h3>
                <p className="text-gray-400 max-w-md mx-auto">
                  The "Released" field is missing or empty in your dataset. 
                  Please ensure your MongoDB documents include a <code className="bg-gray-800 px-2 py-1 rounded text-google-blue">Released</code> or <code className="bg-gray-800 px-2 py-1 rounded text-google-blue">Last Updated</code> field with date values.
                </p>
                <button 
                  onClick={fetchData} 
                  className="mt-6 bg-google-blue hover:bg-blue-600 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                >
                  Retry Loading Data
                </button>
              </div>
            )}
          </div>
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
      <div className={`${colorClasses[color]} inline-flex p-3 rounded-lg mb-4`}>{icon}</div>
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

// Auto-generated analysis text under each scatter plot
const CorrelationInsight = ({ value, xName, yName }) => {
  const abs = Math.abs(value);
  const positive = value >= 0;

  let strength, boxClasses;
  if (abs >= 0.7)      { strength = 'Strong';     boxClasses = 'border-google-green bg-google-green/10'; }
  else if (abs >= 0.4) { strength = 'Moderate';   boxClasses = 'border-google-blue bg-google-blue/10'; }
  else if (abs >= 0.2) { strength = 'Weak';       boxClasses = 'border-google-yellow bg-google-yellow/10'; }
  else                 { strength = 'Negligible'; boxClasses = 'border-gray-600 bg-gray-800/40'; }

  const label = abs < 0.2
    ? 'Negligible correlation'
    : `${strength} ${positive ? 'positive' : 'negative'} correlation`;

  let sentence;
  if (abs < 0.2) {
    sentence = `a high ${xName} does not reliably mean a high ${yName} — the two metrics move almost independently.`;
  } else if (positive) {
    sentence = `the higher the ${xName}, the higher the ${yName} tends to be.`;
  } else {
    sentence = `the higher the ${xName}, the lower the ${yName} tends to be.`;
  }

  return (
    <div className={`mt-4 border-l-4 rounded-r-lg p-4 ${boxClasses}`}>
      <p className="text-sm text-gray-300">
        <span className="font-semibold text-white">Analysis — {label} (r = {value.toFixed(3)}): </span>
        In general, {sentence}
      </p>
    </div>
  );
};

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
        <div className={`text-4xl font-bold ${colorClasses[color].split(' ')[1]} mb-2`}>{value.toFixed(3)}</div>
        <p className="text-gray-400 text-sm">{description}</p>
      </div>
    </div>
  );
};

export default Dashboard;