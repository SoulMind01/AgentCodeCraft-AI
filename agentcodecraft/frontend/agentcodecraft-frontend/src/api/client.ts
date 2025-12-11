import axios from 'axios';

const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: apiBaseURL,
  withCredentials: false,
});

// Add auth headers here if needed
apiClient.interceptors.request.use((config) => {
  // const token = localStorage.getItem('token');
  // if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});