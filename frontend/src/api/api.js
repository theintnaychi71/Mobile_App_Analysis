import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const buildFilterQuery = (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.category && filters.category !== 'All') {
    params.append('category', filters.category);
  }
  if (filters.type && filters.type !== 'All') {
    params.append('type', filters.type);
  }
  const contentRatingVal = filters.contentRating || filters.content_rating;
  if (contentRatingVal && contentRatingVal !== 'All') {
    params.append('content_rating', contentRatingVal);
  }
  return params.toString();
};

export const getFilterOptions = async () => {
  try {
    const response = await api.get('/filter-options');
    return response.data;
  } catch (error) {
    console.error('Error fetching filter options:', error);
    throw error;
  }
};

export const getDashboardStats = async (filters = {}) => {
  try {
    const query = buildFilterQuery(filters);
    const url = query ? `/dashboard/stats?${query}` : '/dashboard/stats';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    throw error;
  }
};

export const getCategoryAnalysis = async (filters = {}) => {
  try {
    const query = buildFilterQuery(filters);
    const url = query ? `/category-analysis?${query}` : '/category-analysis';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching category analysis:', error);
    throw error;
  }
};

export const getTopApps = async (metric = 'installs', limit = 20, filters = {}) => {
  try {
    const query = buildFilterQuery(filters);
    let url = `/top-apps?metric=${metric}&limit=${limit}`;
    if (query) url += `&${query}`;
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching top apps:', error);
    throw error;
  }
};

export const getTopDevelopers = async (sortBy = 'installs', filters = {}) => {
  try {
    const query = buildFilterQuery(filters);
    let url = `/top-developers?sortBy=${sortBy}`;
    if (query) url += `&${query}`;
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching top developers:', error);
    throw error;
  }
};

export const getContentRatingDistribution = async (filters = {}) => {
  try {
    const query = buildFilterQuery(filters);
    const url = query ? `/content-rating-distribution?${query}` : '/content-rating-distribution';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching content rating distribution:', error);
    throw error;
  }
};

export const getRatingDistribution = async (filters = {}) => {
  try {
    const query = buildFilterQuery(filters);
    const url = query ? `/rating-distribution?${query}` : '/rating-distribution';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching rating distribution:', error);
    throw error;
  }
};

export const getPriceDistribution = async (filters = {}) => {
  try {
    const query = buildFilterQuery(filters);
    const url = query ? `/price-distribution?${query}` : '/price-distribution';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching price distribution:', error);
    throw error;
  }
};

export const getInsights = async (filters = {}) => {
  try {
    const query = buildFilterQuery(filters);
    const url = query ? `/insights?${query}` : '/insights';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching insights:', error);
    throw error;
  }
};

export const getReleaseYearDistribution = async (filters = {}) => {
  try {
    const query = buildFilterQuery(filters);
    const url = query ? `/release-year-distribution?${query}` : '/release-year-distribution';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching release year distribution:', error);
    throw error;
  }
};

// ✅ NEW: Fetch install distribution dynamically based on filters
export const getInstallDistribution = async (filters = {}) => {
  try {
    const query = buildFilterQuery(filters);
    const url = query ? `/install-distribution?${query}` : '/install-distribution';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error fetching install distribution:', error);
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await axios.get('http://localhost:5001/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

// App Success Prediction API
export const predictAppSuccess = async (appData) => {
  try {
    const response = await api.post('/predict', appData);
    return response.data;
  } catch (error) {
    console.error('Error predicting app success:', error);
    throw error;
  }
};
