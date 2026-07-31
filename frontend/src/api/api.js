import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getDashboardStats = async () => {
  try {
    const response = await api.get('/dashboard/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    throw error;
  }
};

export const getCategoryAnalysis = async (category = 'All') => {
  try {
    const response = await api.get(`/category-analysis?category=${category}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching category analysis:', error);
    throw error;
  }
};

export const getTopApps = async (metric = 'installs', limit = 20) => {
  try {
    const response = await api.get(`/top-apps?metric=${metric}&limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching top apps:', error);
    throw error;
  }
};

export const getRatingDistribution = async () => {
  try {
    const response = await api.get('/rating-distribution');
    return response.data;
  } catch (error) {
    console.error('Error fetching rating distribution:', error);
    throw error;
  }
};

export const getCorrelationAnalysis = async () => {
  try {
    const response = await api.get('/correlation-analysis');
    return response.data;
  } catch (error) {
    console.error('Error fetching correlation analysis:', error);
    throw error;
  }
};

export const getPriceDistribution = async () => {
  try {
    const response = await api.get('/price-distribution');
    return response.data;
  } catch (error) {
    console.error('Error fetching price distribution:', error);
    throw error;
  }
};

export const getInsights = async () => {
  try {
    const response = await api.get('/insights');
    return response.data;
  } catch (error) {
    console.error('Error fetching insights:', error);
    throw error;
  }
};

export const getReleaseYearDistribution = async () => {
  try {
    const response = await api.get('/release-year-distribution');
    return response.data;
  } catch (error) {
    console.error('Error fetching release year distribution:', error);
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await axios.get('http://localhost:5000/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};
