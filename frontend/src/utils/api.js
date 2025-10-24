import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const searchAPI = {
  semanticSearch: (question) => api.post('/search', { question }),
};

export const eventsAPI = {
  getAll: () => api.get('/events'),
  getById: (id) => api.get(`/events/${id}`),
  search: (filters) => api.post('/events/search', filters),
};

export const locationsAPI = {
  getAll: () => api.get('/locations'),
  getById: (id) => api.get(`/locations/${id}`),
  getAvailable: () => api.get('/locations/available'),
  search: (filters) => api.post('/locations/search', filters),
};

export const usersAPI = {
  getAll: () => api.get('/users'),
  getById: (id) => api.get(`/users/${id}`),
  getOrganizers: () => api.get('/users/organizers'),
  getByRole: (role) => api.get(`/users/role/${role}`),
};

export default api;