import axios from 'axios';

const API_BASE = '/api';
const API_KEY = 'dev-key-12345'; // Should be from env in production

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'X-API-Key': API_KEY
  }
});

export const kpisAPI = {
  list: () => api.get('/kpis'),
  create: (data) => api.post('/kpis', data)
};

export const goalsAPI = {
  create: (data) => api.post('/goals', data)
};

export const reportsAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/reports/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};

export const analysisAPI = {
  analyze: (data) => api.post('/analyze', data)
};

export default api;
