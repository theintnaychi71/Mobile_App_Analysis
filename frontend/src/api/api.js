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

export const healthCheck = async () => {
  try {
    const response = await axios.get('http://localhost:5000/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};
