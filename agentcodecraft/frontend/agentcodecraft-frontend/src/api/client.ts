import axios from 'axios';

// Read backend base URL from Vite env, default to localhost:8000
const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: apiBaseURL,
  withCredentials: false,
});

// Optional: simple request/response logging in dev
if (import.meta.env.DEV) {
  apiClient.interceptors.request.use((config) => {
    // eslint-disable-next-line no-console
    console.log('[API] →', config.method?.toUpperCase(), config.url, config.params || '', config.data || '');
    return config;
  });

  apiClient.interceptors.response.use(
    (response) => {
      // eslint-disable-next-line no-console
      console.log('[API] ←', response.status, response.config.url, response.data);
      return response;
    },
    (error) => {
      // eslint-disable-next-line no-console
      console.error('[API] ✖', error.response?.status, error.config?.url, error.response?.data);
      throw error;
    }
  );
}