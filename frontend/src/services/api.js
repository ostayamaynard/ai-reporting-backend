import axios from 'axios';

const API_BASE = '/api';

// Try to get API key from localStorage, fallback to default
const getApiKey = () => {
  return localStorage.getItem('api_key') || 'dev-key-12345';
};

const api = axios.create({
  baseURL: API_BASE
});

// Add interceptor to include API key in every request
api.interceptors.request.use((config) => {
  config.headers['X-API-Key'] = getApiKey();
  return config;
});

export const kpisAPI = {
  list: () => api.get('/kpis'),
  create: (data) => api.post('/kpis', data)
};

export const goalsAPI = {
  create: (data) => api.post('/goals', data)
};

export const reportsAPI = {
  list: () => api.get('/reports'),
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/reports/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  getData: (reportId) => api.get(`/reports/${reportId}/data`),
  getReport: (reportId) => api.get(`/reports/${reportId}`)
};

export const analysisAPI = {
  analyze: (data) => api.post('/analyze', data),
  chat: (data) => api.post('/chat', data)
};

export const settingsAPI = {
  setApiKey: (key) => localStorage.setItem('api_key', key),
  getApiKey: () => getApiKey(),
  clearApiKey: () => localStorage.removeItem('api_key')
};

export default api;
