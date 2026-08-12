import React, { useState, useEffect } from 'react';
import { Smartphone, TrendingUp, Star, DollarSign, Users, BarChart3, Calculator, CheckCircle, AlertCircle, Target, Zap, Map, Printer, ArrowLeft, Sparkles, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import { predictAppSuccess } from '../api/api';

const FALLBACK_CATEGORIES = [
  'GAME', 'SOCIAL', 'EDUCATION', 'PRODUCTIVITY', 'HEALTH_AND_FITNESS',
  'FINANCE', 'LIFESTYLE', 'ENTERTAINMENT', 'COMMUNICATION', 'TRAVEL_AND_LOCAL'
];
const FALLBACK_CONTENT_RATINGS = ['Everyone', 'Everyone 10+', 'Teen', 'Mature 17+'];

const Prediction = () => {
  const [formData, setFormData] = useState({
    appName: '',
    category: 'GAME',
    rating: 4.0,
    reviews: 1000,
    installs: 10000,
    isFree: true,
    price: 0,
    developer: '',
    contentRating: 'Everyone'
  });

  const [categories, setCategories] = useState(FALLBACK_CATEGORIES);
  const [contentRatings, setContentRatings] = useState(FALLBACK_CONTENT_RATINGS);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadOptions = async () => {
      try {
        const res = await fetch('http://localhost:5001/api/filter-options');
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const options = await res.json();
        if (Array.isArray(options.categories) && options.categories.length > 0) {
          setCategories(options.categories);
          setFormData(prev => ({ ...prev, category: options.categories.includes(prev.category) ? prev.category : options.categories[0] }));
        }
        if (Array.isArray(options.content_ratings) && options.content_ratings.length > 0) {
          setContentRatings(options.content_ratings);
          setFormData(prev => ({ ...prev, contentRating: options.content_ratings.includes(prev.contentRating) ? prev.contentRating : options.content_ratings[0] }));
        }
      } catch (err) {
        console.error('Using fallback categories:', err);
      }
    };
    loadOptions();
  }, []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (name === 'rating' || name === 'reviews' || name === 'installs' || name === 'price') ? parseFloat(value) || 0 : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const result = await predictAppSuccess(formData);
      setPrediction(result);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to predict app success. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getSuccessLevel = (score) => {
    if (score >= 80) return { label: 'MARKET LEADER', color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/20', printColor: '#10b981' };
    if (score >= 60) return { label: 'STRONG CONTENDER', color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20', printColor: '#eab308' };
    if (score >= 40) return { label: 'GROWING APP', color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/20', printColor: '#f97316' };
    return { label: 'NEEDS IMPROVEMENT', color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20', printColor: '#ef4444' };
  };

  // ===== Print-only stylesheet =====
  const printStyles = `
    @media print {
      @page { margin: 0.6in; size: A4; }
      body { background: white !important; }
      .print-header { display: flex !important; }
      .print-footer { display: block !important; }
      .no-print { display: none !important; }
      .print-break-before { page-break-before: always; }
      .print-break-avoid { page-break-inside: avoid; }
      
      .print-container { background: white !important; color: #111 !important; padding: 0 !important; max-width: 100% !important; }
      .print-section { background: white !important; border: 1px solid #e5e7eb !important; color: #111 !important; }
      .print-section-title { color: #111 !important; border-bottom: 2px solid #111 !important; padding-bottom: 4px !important; margin-bottom: 12px !important; }
      
      .print-text { color: #111 !important; }
      .print-text-muted { color: #555 !important; }
      .print-text-white { color: #111 !important; }
      
      .print-banner {
        background: #f9fafb !important;
        border: 2px solid #111 !important;
        color: #111 !important;
      }
      .print-score-value { font-size: 64px !important; font-weight: 800 !important; }
      
      .print-card {
        background: white !important;
        border: 1px solid #d1d5db !important;
        padding: 12px !important;
        border-radius: 4px !important;
        page-break-inside: avoid;
      }
      .print-card-label { color: #555 !important; font-size: 11px !important; text-transform: uppercase !important; letter-spacing: 0.05em !important; margin-bottom: 4px !important; }
      .print-card-value { color: #111 !important; font-size: 14px !important; font-weight: 600 !important; }
      
      .print-progress {
        background: #e5e7eb !important;
        height: 8px !important;
        border-radius: 4px !important;
        overflow: hidden !important;
        margin-top: 6px !important;
      }
      .print-progress-bar { height: 100%; }
      
      .print-table { width: 100%; border-collapse: collapse; }
      .print-table th {
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #111;
        padding: 8px 12px;
        font-size: 12px;
        color: #111;
      }
      .print-table td {
        border-bottom: 1px solid #e5e7eb;
        padding: 8px 12px;
        font-size: 13px;
        color: #333;
      }
      
      .print-risk {
        border-left: 4px solid #ef4444;
        padding: 8px 12px;
        margin-bottom: 8px;
        background: #fef2f2 !important;
      }
      .print-opp {
        border-left: 4px solid #10b981;
        padding: 8px 12px;
        margin-bottom: 8px;
        background: #f0fdf4 !important;
      }
      
      .print-rec-item {
        padding: 6px 0;
        border-bottom: 1px dotted #d1d5db;
        color: #333 !important;
      }
      .print-rec-num {
        display: inline-block;
        width: 22px;
        height: 22px;
        background: #111;
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 22px;
        font-size: 11px;
        margin-right: 8px;
      }
      
      .print-roadmap-item {
        border: 1px solid #d1d5db;
        padding: 10px;
        margin-bottom: 8px;
        page-break-inside: avoid;
      }
      .print-roadmap-priority {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 10px;
        font-weight: 700;
        margin-right: 8px;
        text-transform: uppercase;
      }
    }
  `;

  // Helper components — screen version
  const SuccessFactorCard = ({ icon: Icon, label, value, score, maxScore = 100, color }) => (
    <div className="group p-5 rounded-2xl border border-white/10 bg-slate-900/70 shadow-xl shadow-black/10 transition duration-300 hover:-translate-y-1 hover:border-white/20">
      <div className="flex items-start space-x-3 mb-3">
        <div className={`p-2 rounded-lg ${color}`}><Icon className="w-5 h-5" /></div>
        <div className="flex-1">
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-lg font-semibold text-white">{value}</p>
        </div>
      </div>
      <div className="mt-3">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Score</span>
          <span>{score}/{maxScore}</span>
        </div>
        <div className="w-full bg-white/10 rounded-full h-2">
          <div className="h-2 rounded-full transition-all duration-500 bg-current" style={{ width: `${Math.min(100, (score / maxScore) * 100)}%` }} />
        </div>
      </div>
    </div>
  );

  const BenchmarkCard = ({ label, yours, categoryAvg, marketAvg, percentile }) => (
    <div className="p-5 rounded-2xl bg-slate-900/70 border border-white/10 shadow-xl shadow-black/10">
      <p className="text-sm font-medium text-gray-300 mb-3">{label}</p>
      <div className="space-y-2">
        <div className="flex justify-between"><span className="text-sm text-gray-500">Your App</span><span className="text-lg font-bold text-white">{typeof yours === 'number' ? yours.toLocaleString() : yours}</span></div>
        <div className="flex justify-between"><span className="text-sm text-gray-500">Category Avg</span><span className="text-sm text-gray-400">{typeof categoryAvg === 'number' ? categoryAvg.toLocaleString() : categoryAvg}</span></div>
        <div className="flex justify-between"><span className="text-sm text-gray-500">Market Avg</span><span className="text-sm text-gray-400">{typeof marketAvg === 'number' ? marketAvg.toLocaleString() : marketAvg}</span></div>
    <div className="pt-3 border-t border-white/10">
          <div className="flex justify-between">
            <span className="text-xs text-gray-500">Percentile</span>
            <span className={`text-sm font-semibold ${percentile >= 75 ? 'text-green-400' : percentile >= 50 ? 'text-yellow-400' : 'text-orange-400'}`}>Top {100 - percentile}%</span>
          </div>
        </div>
      </div>
    </div>
  );

  // ===== PRINT-ONLY helper components =====
  const PrintScoreCard = ({ label, value, score, maxScore, color }) => (
    <div className="print-card">
      <div className="print-card-label">{label}</div>
      <div className="print-card-value">{value}</div>
      <div className="print-progress">
        <div className="print-progress-bar" style={{ width: `${(score / maxScore) * 100}%`, background: color }} />
      </div>
      <div style={{ fontSize: 11, color: '#666', marginTop: 4 }}>{score}/{maxScore} points</div>
    </div>
  );

  const PrintBenchmark = ({ label, yours, categoryAvg, marketAvg, percentile }) => (
    <div className="print-card" style={{ flex: 1, minWidth: 180 }}>
      <div className="print-card-label">{label}</div>
      <table style={{ width: '100%', fontSize: 13, marginTop: 6 }}>
        <tbody>
          <tr><td style={{ color: '#555', padding: '2px 0' }}>Your App</td><td style={{ textAlign: 'right', fontWeight: 700, color: '#111' }}>{typeof yours === 'number' ? yours.toLocaleString() : yours}</td></tr>
          <tr><td style={{ color: '#555', padding: '2px 0' }}>Category Avg</td><td style={{ textAlign: 'right', color: '#333' }}>{typeof categoryAvg === 'number' ? categoryAvg.toLocaleString() : categoryAvg}</td></tr>
          <tr><td style={{ color: '#555', padding: '2px 0' }}>Market Avg</td><td style={{ textAlign: 'right', color: '#333' }}>{typeof marketAvg === 'number' ? marketAvg.toLocaleString() : marketAvg}</td></tr>
          <tr><td style={{ color: '#555', padding: '2px 0' }}>Percentile</td><td style={{ textAlign: 'right', fontWeight: 600, color: '#111' }}>Top {100 - percentile}%</td></tr>
        </tbody>
      </table>
    </div>
  );

  if (prediction) {
    const { successScore, probability, marketPosition, positionDescription, factors, benchmarks, risks, opportunities, roadmap, recommendation } = prediction;
    const successLevel = getSuccessLevel(successScore);
    const generatedDate = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    const generatedTime = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

    return (
      <>
        <style>{printStyles}</style>
        <div className="min-h-screen overflow-hidden bg-[#07111f] print-container">
          <div className="absolute inset-x-0 top-0 h-[34rem] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-500/20 via-indigo-500/10 to-transparent pointer-events-none print:hidden" />
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-7 sm:py-10 print:px-0 print:py-0">

            {/* ===== PRINT-ONLY HEADER ===== */}
            <div className="print-header hidden" style={{ borderBottom: '3px solid #111', paddingBottom: 16, marginBottom: 20 }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 11, color: '#666', textTransform: 'uppercase', letterSpacing: '0.1em' }}>App Success Report</div>
                <div style={{ fontSize: 28, fontWeight: 800, color: '#111', marginTop: 4 }}>{formData.appName || 'Untitled App'}</div>
                <div style={{ fontSize: 13, color: '#555', marginTop: 4 }}>
                  Category: <strong>{formData.category}</strong> &nbsp;•&nbsp; Model: <strong>{formData.isFree ? 'Free' : `Paid ($${formData.price})`}</strong>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 11, color: '#666' }}>Generated</div>
                <div style={{ fontSize: 13, fontWeight: 600, color: '#111' }}>{generatedDate}</div>
                <div style={{ fontSize: 12, color: '#555' }}>{generatedTime}</div>
              </div>
            </div>

            {/* ===== SCREEN-ONLY BACK BUTTON ===== */}
            <Link to="/" className="no-print mb-8 inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-gray-300 transition hover:bg-white/10 hover:text-white">
              <ArrowLeft className="w-4 h-4" />
              <span>Back to home</span>
            </Link>

            {/* Title */}
            <div className="mb-10 rounded-3xl border border-white/10 bg-white/[0.03] p-7 text-center shadow-2xl shadow-black/20 no-print sm:p-10">
              <div className="mb-3 flex items-center justify-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-blue-300"><Sparkles className="h-4 w-4" /> Intelligence report</div>
              <h1 className="text-4xl sm:text-5xl font-bold mb-4">
                <span className="bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">App Success Analysis</span>
              </h1>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                {formData.appName} — Comprehensive market analysis and success prediction
              </p>
            </div>

            {/* ===== SCORE BANNER ===== */}
            <div className={`relative overflow-hidden rounded-3xl p-7 sm:p-10 print:p-6 ${successLevel.bg} ${successLevel.border} border mb-8 shadow-2xl shadow-black/30 print-banner print-break-avoid`}>
              <div className="absolute -right-20 -top-24 h-72 w-72 rounded-full bg-white/10 blur-3xl print:hidden" />
              <div className="absolute -bottom-28 right-1/3 h-56 w-56 rounded-full bg-blue-400/10 blur-3xl print:hidden" />
              <div className="relative z-10 flex flex-col md:flex-row print:flex-row items-center justify-between gap-6">
                <div className="text-center md:text-left print:text-left">
                  <div className="no-print">
                    <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-bold uppercase tracking-wider text-white"><ShieldCheck className="h-4 w-4" /> {marketPosition}</div>
                    <h2 className="text-3xl font-bold mb-2 text-white print-text-white">Your success outlook</h2>
                    <p className="text-gray-300 mb-4 print-text-muted">{positionDescription}</p>
                  </div>
                  <div className="hidden print:block" style={{ marginBottom: 8 }}>
                    <div style={{ fontSize: 14, fontWeight: 700, color: successLevel.printColor, textTransform: 'uppercase', letterSpacing: '0.1em' }}>{marketPosition}</div>
                    <div style={{ fontSize: 13, color: '#555' }}>{positionDescription}</div>
                  </div>
                  <div className="flex items-center gap-8 print:gap-6">
                    <div>
                      <div className="text-5xl sm:text-6xl print-score-value font-bold">
                        <span className={`${successLevel.color} print:hidden`}>{successScore}%</span>
                        <span className="hidden print:inline" style={{ color: successLevel.printColor }}>{successScore}%</span>
                      </div>
                      <div className="text-sm text-gray-400 mt-1 print-text-muted">Success Score</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-white print-text-white">{(probability * 100).toFixed(1)}%</div>
                      <div className="text-sm text-gray-400 print-text-muted">Probability</div>
                    </div>
                  </div>
                </div>
                <div className="w-full md:w-64 no-print">
                  <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-5 backdrop-blur-sm">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-gray-400">Progress to 100%</span>
                      <span className={successLevel.color}>{successScore}%</span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-3">
                      <div className={`h-3 rounded-full transition-all duration-1000 ${successLevel.color.replace('text-', 'bg-')}`} style={{ width: `${successScore}%` }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* ===== FACTORS — screen version ===== */}
            <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8 print:hidden">
              <SuccessFactorCard icon={Star} label="Quality Score" value={factors?.ratingImpact || 'N/A'} score={factors?.qualityScore || 0} maxScore={25} color="bg-yellow-500/10 text-yellow-400" />
              <SuccessFactorCard icon={TrendingUp} label="Market Performance" value={factors?.categoryPosition || 'N/A'} score={factors?.marketScore || 0} maxScore={30} color="bg-green-500/10 text-green-400" />
              <SuccessFactorCard icon={Users} label="User Engagement" value={factors?.engagementPotential || 'N/A'} score={factors?.engagementScore || 0} maxScore={20} color="bg-blue-500/10 text-blue-400" />
              <SuccessFactorCard icon={DollarSign} label="Monetization" value={factors?.revenuePotential || 'N/A'} score={factors?.monetizationScore || 0} maxScore={15} color="bg-purple-500/10 text-purple-400" />
              <SuccessFactorCard icon={Target} label="Competitive Position" value={factors?.competitionLevel || 'N/A'} score={factors?.competitiveScore || 0} maxScore={10} color="bg-orange-500/10 text-orange-400" />
            </div>

            {/* ===== FACTORS — print version ===== */}
            <div className="hidden print:block mb-8">
              <h3 className="print-section-title" style={{ fontSize: 16, fontWeight: 700 }}>Score Breakdown</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10 }}>
                <PrintScoreCard label="Quality" value={factors?.ratingImpact || 'N/A'} score={factors?.qualityScore || 0} maxScore={25} color="#eab308" />
                <PrintScoreCard label="Market" value={factors?.categoryPosition || 'N/A'} score={factors?.marketScore || 0} maxScore={30} color="#10b981" />
                <PrintScoreCard label="Engagement" value={factors?.engagementPotential || 'N/A'} score={factors?.engagementScore || 0} maxScore={20} color="#3b82f6" />
                <PrintScoreCard label="Monetization" value={factors?.revenuePotential || 'N/A'} score={factors?.monetizationScore || 0} maxScore={15} color="#a855f7" />
                <PrintScoreCard label="Competitive" value={factors?.competitionLevel || 'N/A'} score={factors?.competitiveScore || 0} maxScore={10} color="#f97316" />
              </div>
            </div>

            {/* ===== BENCHMARKS ===== */}
            <div className="grid lg:grid-cols-3 gap-6 mb-8 print:hidden">
              <BenchmarkCard label="⭐ Rating Benchmark" yours={benchmarks?.rating?.yours} categoryAvg={benchmarks?.rating?.category_avg} marketAvg={benchmarks?.rating?.market_avg} percentile={benchmarks?.rating?.percentile} />
              <BenchmarkCard label="📥 Installs Benchmark" yours={benchmarks?.installs?.yours} categoryAvg={benchmarks?.installs?.category_avg} marketAvg={benchmarks?.installs?.market_avg} percentile={benchmarks?.installs?.percentile} />
              <BenchmarkCard label="💬 Reviews Benchmark" yours={benchmarks?.reviews?.yours} categoryAvg={benchmarks?.reviews?.category_avg} marketAvg={benchmarks?.reviews?.market_avg} percentile={benchmarks?.reviews?.percentile} />
            </div>

            <div className="hidden print:block mb-8 print-break-avoid">
              <h3 className="print-section-title" style={{ fontSize: 16, fontWeight: 700 }}>Market Benchmarks</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
                <PrintBenchmark label="⭐ Rating" yours={benchmarks?.rating?.yours} categoryAvg={benchmarks?.rating?.category_avg} marketAvg={benchmarks?.rating?.market_avg} percentile={benchmarks?.rating?.percentile} />
                <PrintBenchmark label="📥 Installs" yours={benchmarks?.installs?.yours} categoryAvg={benchmarks?.installs?.category_avg} marketAvg={benchmarks?.installs?.market_avg} percentile={benchmarks?.installs?.percentile} />
                <PrintBenchmark label="💬 Reviews" yours={benchmarks?.reviews?.yours} categoryAvg={benchmarks?.reviews?.category_avg} marketAvg={benchmarks?.reviews?.market_avg} percentile={benchmarks?.reviews?.percentile} />
              </div>
            </div>

            {/* ===== RISKS & OPPORTUNITIES (screen) ===== */}
            <div className="grid lg:grid-cols-2 gap-6 mb-8 print:hidden">
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2"><AlertCircle className="w-6 h-6 text-red-400" /><span>Risk Factors</span></h3>
                <div className="space-y-3">
                  {risks && risks.length > 0 ? risks.map((risk, index) => (
                    <div key={index} className="p-3 bg-red-500/5 border border-red-500/20 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${risk.severity === 'High' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}`}>{risk.severity}</span>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-white">{risk.issue}</p>
                          <p className="text-xs text-gray-400 mt-1">{risk.impact}</p>
                        </div>
                      </div>
                    </div>
                  )) : <p className="text-gray-400 italic text-center py-4">No significant risks identified</p>}
                </div>
              </div>
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2"><Zap className="w-6 h-6 text-green-400" /><span>Growth Opportunities</span></h3>
                <div className="space-y-3">
                  {opportunities && opportunities.length > 0 ? opportunities.map((opp, index) => (
                    <div key={index} className="p-3 bg-green-500/5 border border-green-500/20 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${opp.potential === 'High' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'}`}>{opp.potential}</span>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-white">{opp.area}</p>
                          <p className="text-xs text-gray-400 mt-1">{opp.action}</p>
                        </div>
                      </div>
                    </div>
                  )) : <p className="text-gray-400 italic text-center py-4">No major opportunities identified</p>}
                </div>
              </div>
            </div>

            {/* ===== RISKS & OPPORTUNITIES (print) ===== */}
            <div className="hidden print:block mb-8 print-break-avoid">
              <h3 className="print-section-title" style={{ fontSize: 16, fontWeight: 700 }}>Risk & Opportunity Analysis</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#ef4444', marginBottom: 8 }}>⚠ RISKS</div>
                  {risks && risks.length > 0 ? risks.map((r, i) => (
                    <div key={i} className="print-risk">
                      <div style={{ fontWeight: 600, fontSize: 13 }}>[{r.severity}] {r.issue}</div>
                      <div style={{ fontSize: 12, color: '#666', marginTop: 2 }}>{r.impact}</div>
                    </div>
                  )) : <div style={{ color: '#888', fontSize: 13 }}>No significant risks.</div>}
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#10b981', marginBottom: 8 }}>✓ OPPORTUNITIES</div>
                  {opportunities && opportunities.length > 0 ? opportunities.map((o, i) => (
                    <div key={i} className="print-opp">
                      <div style={{ fontWeight: 600, fontSize: 13 }}>[{o.potential}] {o.area}</div>
                      <div style={{ fontSize: 12, color: '#666', marginTop: 2 }}>{o.action}</div>
                    </div>
                  )) : <div style={{ color: '#888', fontSize: 13 }}>No major opportunities.</div>}
                </div>
              </div>
            </div>

            {/* ===== ROADMAP ===== */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700 mb-8 print:hidden">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2"><Map className="w-6 h-6 text-blue-400" /><span>Success Roadmap</span></h3>
              <div className="space-y-4">
                {roadmap && roadmap.map((item, index) => (
                  <div key={index} className="p-4 bg-gray-900/50 rounded-xl border border-gray-700">
                    <div className="flex items-start space-x-3">
                      <div className={`px-3 py-1 rounded-full text-xs font-semibold ${item.priority === 'Critical' ? 'bg-red-500/20 text-red-400' : item.priority === 'High' ? 'bg-orange-500/20 text-orange-400' : item.priority === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-blue-500/20 text-blue-400'}`}>{item.priority}</div>
                      <div className="flex-1">
                        <h4 className="text-lg font-semibold text-white mb-2">{item.milestone}</h4>
                        <div className="space-y-1 mb-2">{item.actions.map((action, i) => (<div key={i} className="flex items-start space-x-2 text-sm text-gray-300"><span className="text-google-blue mt-1">•</span><span>{action}</span></div>))}</div>
                        <p className="text-xs text-gray-500">Impact: {item.impact}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="hidden print:block mb-8 print-break-avoid">
              <h3 className="print-section-title" style={{ fontSize: 16, fontWeight: 700 }}>Success Roadmap</h3>
              {roadmap && roadmap.map((item, i) => (
                <div key={i} className="print-roadmap-item">
                  <span className="print-roadmap-priority" style={{
                    background: item.priority === 'Critical' ? '#fee2e2' : item.priority === 'High' ? '#ffedd5' : item.priority === 'Medium' ? '#fef9c3' : '#dbeafe',
                    color: item.priority === 'Critical' ? '#b91c1c' : item.priority === 'High' ? '#c2410c' : item.priority === 'Medium' ? '#a16207' : '#1e40af'
                  }}>{item.priority}</span>
                  <strong style={{ fontSize: 14 }}>{item.milestone}</strong>
                  <div style={{ fontSize: 12, color: '#333', marginTop: 4 }}>
                    {item.actions.map((a, j) => (<div key={j}>• {a}</div>))}
                  </div>
                  <div style={{ fontSize: 11, color: '#666', marginTop: 4, fontStyle: 'italic' }}>Expected impact: {item.impact}</div>
                </div>
              ))}
            </div>

            {/* ===== RECOMMENDATIONS ===== */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-700 mb-8 print:hidden">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2"><CheckCircle className="w-6 h-6 text-green-400" /><span>Key Recommendations</span></h3>
              <div className="space-y-3">
                {recommendation?.recommendations?.map((rec, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="mt-1 min-w-[24px] h-6 w-6 rounded-full bg-green-500/20 flex items-center justify-center">
                      <span className="text-green-400 text-xs font-bold">{index + 1}</span>
                    </div>
                    <p className="text-gray-300">{rec}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="hidden print:block mb-8 print-break-avoid">
              <h3 className="print-section-title" style={{ fontSize: 16, fontWeight: 700 }}>Key Recommendations</h3>
              {recommendation?.recommendations?.map((rec, i) => (
                <div key={i} className="print-rec-item">
                  <span className="print-rec-num">{i + 1}</span>
                  <span style={{ fontSize: 13 }}>{rec}</span>
                </div>
              ))}
            </div>

            {/* ===== SCREEN ACTION BUTTONS ===== */}
            <div className="no-print flex flex-col sm:flex-row gap-4 justify-center">
              <button onClick={() => setPrediction(null)} className="px-8 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-xl transition-all duration-200 font-medium">
                Analyze Another App
              </button>
              <button onClick={() => window.print()} className="px-8 py-3 bg-google-blue hover:bg-blue-600 text-white rounded-xl transition-all duration-200 font-medium flex items-center justify-center space-x-2">
                <Printer className="w-5 h-5" />
                <span>Save Report (PDF)</span>
              </button>
            </div>

            {/* ===== PRINT FOOTER ===== */}
            <div className="print-footer hidden" style={{ borderTop: '1px solid #d1d5db', marginTop: 30, paddingTop: 12, fontSize: 10, color: '#888', display: 'flex', justifyContent: 'space-between' }}>
              <div>App Success Predictor • Generated by Market Analysis Dashboard</div>
              <div>{formData.appName} — {generatedDate} • Page 1</div>
            </div>
          </div>
        </div>
      </>
    );
  }

  // ===== FORM VIEW (unchanged) =====
  return (
    <div className="min-h-screen overflow-hidden bg-[#07111f]">
      <div className="absolute inset-x-0 top-0 h-[32rem] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-500/20 via-indigo-500/10 to-transparent pointer-events-none" />
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-14">
        <div className="text-center mb-12">
          <Link to="/" className="mb-8 inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-gray-300 transition hover:bg-white/10 hover:text-white"><ArrowLeft className="h-4 w-4" /> Back to home</Link>
          <div className="mb-4 flex items-center justify-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-blue-300"><Sparkles className="h-4 w-4" /> App intelligence</div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">Predict Your App's Success</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">Enter your app details and our AI algorithm will analyze its potential for success</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <form onSubmit={handleSubmit} className="rounded-3xl border border-white/10 bg-slate-900/70 p-6 shadow-2xl shadow-black/30 backdrop-blur-xl sm:p-8">
              <h2 className="text-2xl font-semibold text-white mb-6 flex items-center space-x-3">
                <Smartphone className="w-6 h-6 text-google-blue" /><span>App Details</span>
              </h2>

              <div className="grid sm:grid-cols-2 gap-6 mb-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">App Name</label>
                  <input type="text" name="appName" value={formData.appName} onChange={handleInputChange} placeholder="e.g., My Awesome App" className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl focus:ring-2 focus:ring-google-blue focus:border-transparent text-white placeholder-gray-600 transition-all" required />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Developer Name</label>
                  <input type="text" name="developer" value={formData.developer} onChange={handleInputChange} placeholder="e.g., Your Company" className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl focus:ring-2 focus:ring-google-blue focus:border-transparent text-white placeholder-gray-600 transition-all" />
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-6 mb-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Category </label>
                  <select name="category" value={formData.category} onChange={handleInputChange} className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl focus:ring-2 focus:ring-google-blue focus:border-transparent text-white transition-all">
                    {categories.map(cat => (<option key={cat} value={cat}>{cat}</option>))}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Content Rating </label>
                  <select name="contentRating" value={formData.contentRating} onChange={handleInputChange} className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl focus:ring-2 focus:ring-google-blue focus:border-transparent text-white transition-all">
                    {contentRatings.map(rating => (<option key={rating} value={rating}>{rating}</option>))}
                  </select>
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-6 mb-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Expected Rating ⭐ <span className="text-xs text-gray-500 ml-2">(0-5)</span></label>
                  <input type="number" name="rating" value={formData.rating} onChange={handleInputChange} min="0" max="5" step="0.1" className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl focus:ring-2 focus:ring-google-blue focus:border-transparent text-white transition-all" required />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">Initial Reviews <span className="text-xs text-gray-500 ml-2">(0-5000+)</span></label>
                  <input type="number" name="reviews" value={formData.reviews} onChange={handleInputChange} min="0" className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl focus:ring-2 focus:ring-google-blue focus:border-transparent text-white transition-all" required />
                </div>
              </div>

              <div className="space-y-2 mb-6">
                <label className="text-sm font-medium text-gray-300">Expected Installs <span className="text-xs text-gray-500 ml-2">(0-10M+)</span></label>
                <input type="number" name="installs" value={formData.installs} onChange={handleInputChange} min="0" className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl focus:ring-2 focus:ring-google-blue focus:border-transparent text-white transition-all" required />
              </div>

              <div className="space-y-4 mb-6 p-6 bg-gray-900/50 rounded-xl border border-gray-700">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <div className="relative">
                    <input type="checkbox" name="isFree" checked={formData.isFree} onChange={handleInputChange} className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-google-blue rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-google-green"></div>
                  </div>
                  <span className="text-white font-medium">App will be Free</span>
                </label>
                {!formData.isFree && (
                  <div className="space-y-2 pl-14">
                    <label className="text-sm font-medium text-gray-300">Price ($)</label>
                    <input type="number" name="price" value={formData.price} onChange={handleInputChange} min="0" step="0.99" className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:ring-2 focus:ring-google-blue focus:border-transparent text-white transition-all" />
                  </div>
                )}
              </div>

              {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6">
                  <div className="flex items-center space-x-3"><AlertCircle className="w-5 h-5 text-red-400" /><p className="text-red-400">{error}</p></div>
                </div>
              )}

              <button type="submit" disabled={loading} className="w-full bg-gradient-to-r from-google-green to-google-blue hover:from-green-600 hover:to-blue-600 text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 transform hover:scale-[1.02] hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3">
                {loading ? (<div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin" />) : (<><Calculator className="w-5 h-5" /><span>Predict App Success</span></>)}
              </button>
            </form>
          </div>

          <div className="space-y-6">
            <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-6 shadow-xl shadow-black/20 backdrop-blur-xl">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2"><BarChart3 className="w-6 h-6 text-google-yellow" /><span>Success Factors</span></h3>
              <div className="space-y-4">
                <div className="flex items-start space-x-3"><div className="w-2 h-2 mt-2 rounded-full bg-google-green" /><div><p className="text-sm font-medium text-white">Category Demand</p><p className="text-xs text-gray-400">High-demand categories increase visibility</p></div></div>
                <div className="flex items-start space-x-3"><div className="w-2 h-2 mt-2 rounded-full bg-google-blue" /><div><p className="text-sm font-medium text-white">User Ratings</p><p className="text-xs text-gray-400">4.5+ ratings significantly boost success</p></div></div>
                <div className="flex items-start space-x-3"><div className="w-2 h-2 mt-2 rounded-full bg-google-yellow" /><div><p className="text-sm font-medium text-white">Install Velocity</p><p className="text-xs text-gray-400">Rapid early adoption predicts long-term success</p></div></div>
                <div className="flex items-start space-x-3"><div className="w-2 h-2 mt-2 rounded-full bg-google-red" /><div><p className="text-sm font-medium text-white">Competition Level</p><p className="text-xs text-gray-400">Moderate competition is often ideal</p></div></div>
              </div>
            </div>
            <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 p-6 shadow-xl shadow-black/20 backdrop-blur-xl">
              <h3 className="text-lg font-semibold text-white mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm"><span className="text-gray-400">Average App Rating</span><span className="text-white">4.2/5.0</span></div>
                <div className="flex justify-between text-sm"><span className="text-gray-400">Free Apps</span><span className="text-google-green">85%</span></div>
                <div className="flex justify-between text-sm"><span className="text-gray-400">Avg Installs</span><span className="text-white">~500K</span></div>
                <div className="flex justify-between text-sm"><span className="text-gray-400">Success Rate</span><span className="text-google-blue">~35%</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Prediction;
