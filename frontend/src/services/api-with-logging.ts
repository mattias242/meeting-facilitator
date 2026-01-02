/** API service with logging integration. */

import axios from 'axios';
import logger from '../utils/logger';

// Create axios instance with logging
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    const startTime = Date.now();
    config.metadata = { startTime };
    
    logger.debug('API Request Started', {
      method: config.method?.toUpperCase(),
      url: config.url,
      data: config.data,
    });
    
    return config;
  },
  (error) => {
    logger.error('API Request Error', {
      error: error.message,
      config: error.config,
    });
    return Promise.reject(error);
  }
);

// Response interceptor for logging
api.interceptors.response.use(
  (response) => {
    const duration = Date.now() - (response.config.metadata?.startTime || Date.now());
    
    logger.apiRequest(
      response.config.method?.toUpperCase() || 'UNKNOWN',
      response.config.url || 'UNKNOWN',
      response.status,
      duration
    );
    
    return response;
  },
  (error) => {
    const duration = Date.now() - (error.config?.metadata?.startTime || Date.now());
    const status = error.response?.status;
    
    logger.apiRequest(
      error.config?.method?.toUpperCase() || 'UNKNOWN',
      error.config?.url || 'UNKNOWN',
      status,
      duration,
      error.message
    );
    
    return Promise.reject(error);
  }
);

export default api;
