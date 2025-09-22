import { ApiFilters } from '../types/api';

// API base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Helper function to build query parameters
export const buildQueryParams = (filters: ApiFilters): string => {
  const params = new URLSearchParams();
  
  if (filters.start_date) {
    params.append('start_date', filters.start_date);
  }
  
  if (filters.end_date) {
    params.append('end_date', filters.end_date);
  }
  
  if (filters.property_ids && filters.property_ids.length > 0) {
    params.append('property_ids', filters.property_ids.join(','));
  }
  
  return params.toString();
};

// Generic fetch function with enhanced error handling
export const apiRequest = async <T>(endpoint: string, filters?: ApiFilters): Promise<T> => {
  const queryParams = filters ? buildQueryParams(filters) : '';
  const url = `${API_BASE_URL}${endpoint}${queryParams ? `?${queryParams}` : ''}`;
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        // If we can't parse the error response, create a generic one
        errorData = { 
          detail: `HTTP ${response.status}: ${response.statusText}`,
          status_code: response.status 
        };
      }
      
      // Create more descriptive error messages based on status code
      let errorMessage = errorData.detail || `Request failed with status ${response.status}`;
      
      if (response.status >= 500) {
        errorMessage = `Server error (${response.status}): ${errorData.detail || 'The server encountered an internal error'}`;
      } else if (response.status === 404) {
        errorMessage = `Not found (404): ${errorData.detail || 'The requested resource was not found'}`;
      } else if (response.status === 401) {
        errorMessage = `Unauthorized (401): ${errorData.detail || 'Authentication required'}`;
      } else if (response.status === 403) {
        errorMessage = `Forbidden (403): ${errorData.detail || 'Access denied'}`;
      } else if (response.status === 400) {
        errorMessage = `Bad request (400): ${errorData.detail || 'Invalid request parameters'}`;
      }
      
      const error = new Error(errorMessage);
      (error as any).status = response.status;
      (error as any).statusText = response.statusText;
      throw error;
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      // Handle specific error types
      if (error.name === 'AbortError') {
        throw new Error('Request timeout: The server took too long to respond');
      }
      
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        throw new Error('Network error: Unable to connect to the server. Please check your internet connection.');
      }
      
      throw error;
    }
    
    throw new Error('An unexpected error occurred while making the request');
  }
};

// API endpoint constants
export const API_ENDPOINTS = {
  PROPERTIES: '/api/properties',
  REVENUE_TIMELINE: '/api/revenue/timeline',
  REVENUE_BY_PROPERTY: '/api/revenue/by-property',
  MAINTENANCE_LOST_INCOME: '/api/maintenance/lost-income',
  REVIEW_TRENDS: '/api/reviews/trends',
  LEAD_TIMES: '/api/bookings/lead-times',
  KPIS: '/api/kpis',
} as const;