import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiRequest, API_ENDPOINTS } from '../lib/api';
import { useApiErrorHandler } from './useErrorHandler';
import {
  Property,
  PropertiesResponse,
  RevenueTimeline,
  PropertyRevenue,
  LostIncomeData,
  ReviewTrendsData,
  LeadTimeData,
  KPIResponse,
  ApiFilters,
} from '../types/api';

// Query keys for React Query
export const QUERY_KEYS = {
  PROPERTIES: ['properties'],
  REVENUE_TIMELINE: ['revenue', 'timeline'],
  REVENUE_BY_PROPERTY: ['revenue', 'by-property'],
  MAINTENANCE_LOST_INCOME: ['maintenance', 'lost-income'],
  REVIEW_TRENDS: ['reviews', 'trends'],
  LEAD_TIMES: ['bookings', 'lead-times'],
  KPIS: ['kpis'],
} as const;

// Enhanced retry function with better error handling
const createRetryFunction = (queryKey: readonly string[]) => {
  return (failureCount: number, error: Error) => {
    const errorMessage = error.message.toLowerCase();
    
    // Don't retry on client errors (4xx) - these are usually permanent
    if (
      errorMessage.includes('400') || 
      errorMessage.includes('401') || 
      errorMessage.includes('403') || 
      errorMessage.includes('404') ||
      errorMessage.includes('bad request') ||
      errorMessage.includes('unauthorized') ||
      errorMessage.includes('forbidden') ||
      errorMessage.includes('not found')
    ) {
      console.warn(`Not retrying client error for ${queryKey.join('.')}: ${error.message}`);
      return false;
    }
    
    // Don't retry on certain network errors that are unlikely to resolve quickly
    if (
      errorMessage.includes('cors') ||
      errorMessage.includes('blocked') ||
      error.name === 'SecurityError'
    ) {
      console.warn(`Not retrying security/CORS error for ${queryKey.join('.')}: ${error.message}`);
      return false;
    }
    
    // Retry up to 3 times for network and server errors
    if (failureCount < 3) {
      const retryableErrors = [
        'network', 'fetch', 'connection', 'timeout', 'aborted',
        '500', '502', '503', '504', 'internal server', 'bad gateway',
        'service unavailable', 'gateway timeout'
      ];
      
      const isRetryable = retryableErrors.some(pattern => errorMessage.includes(pattern));
      
      if (isRetryable || error.name === 'NetworkError' || error.name === 'TypeError') {
        console.log(`Retrying ${queryKey.join('.')} (attempt ${failureCount + 1}/3) - ${error.message}`);
        return true;
      }
    }
    
    console.warn(`Max retries reached or non-retryable error for ${queryKey.join('.')}: ${error.message}`);
    return false;
  };
};

// Hook for fetching properties list
export const useProperties = (): UseQueryResult<Property[], Error> => {
  const { handleQueryError } = useApiErrorHandler();
  
  return useQuery({
    queryKey: QUERY_KEYS.PROPERTIES,
    queryFn: async () => {
      try {
        const response = await apiRequest<PropertiesResponse>(API_ENDPOINTS.PROPERTIES);
        return response.data;
      } catch (error) {
        handleQueryError(error as Error, QUERY_KEYS.PROPERTIES);
        throw error;
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: createRetryFunction([...QUERY_KEYS.PROPERTIES]),
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
  });
};

// Hook for fetching revenue timeline
export const useRevenueTimeline = (
  filters: ApiFilters
): UseQueryResult<RevenueTimeline, Error> => {
  const { handleQueryError } = useApiErrorHandler();
  const queryKey = [...QUERY_KEYS.REVENUE_TIMELINE, filters];
  
  return useQuery({
    queryKey,
    queryFn: async () => {
      try {
        return await apiRequest<RevenueTimeline>(API_ENDPOINTS.REVENUE_TIMELINE, filters);
      } catch (error) {
        handleQueryError(error as Error, [...QUERY_KEYS.REVENUE_TIMELINE], filters);
        throw error;
      }
    },
    enabled: true, // Always enabled, filters can be empty
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: createRetryFunction([...QUERY_KEYS.REVENUE_TIMELINE]),
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

// Hook for fetching revenue by property
export const useRevenueByProperty = (
  filters: ApiFilters
): UseQueryResult<PropertyRevenue, Error> => {
  const { handleQueryError } = useApiErrorHandler();
  const queryKey = [...QUERY_KEYS.REVENUE_BY_PROPERTY, filters];
  
  return useQuery({
    queryKey,
    queryFn: async () => {
      try {
        return await apiRequest<PropertyRevenue>(API_ENDPOINTS.REVENUE_BY_PROPERTY, filters);
      } catch (error) {
        handleQueryError(error as Error, [...QUERY_KEYS.REVENUE_BY_PROPERTY], filters);
        throw error;
      }
    },
    enabled: true,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: createRetryFunction([...QUERY_KEYS.REVENUE_BY_PROPERTY]),
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

// Hook for fetching maintenance lost income
export const useMaintenanceLostIncome = (
  filters: ApiFilters
): UseQueryResult<LostIncomeData, Error> => {
  const { handleQueryError } = useApiErrorHandler();
  const queryKey = [...QUERY_KEYS.MAINTENANCE_LOST_INCOME, filters];
  
  return useQuery({
    queryKey,
    queryFn: async () => {
      try {
        return await apiRequest<LostIncomeData>(API_ENDPOINTS.MAINTENANCE_LOST_INCOME, filters);
      } catch (error) {
        handleQueryError(error as Error, [...QUERY_KEYS.MAINTENANCE_LOST_INCOME], filters);
        throw error;
      }
    },
    enabled: true,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: createRetryFunction([...QUERY_KEYS.MAINTENANCE_LOST_INCOME]),
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

// Hook for fetching review trends
export const useReviewTrends = (
  filters: ApiFilters
): UseQueryResult<ReviewTrendsData, Error> => {
  const { handleQueryError } = useApiErrorHandler();
  const queryKey = [...QUERY_KEYS.REVIEW_TRENDS, filters];
  
  return useQuery({
    queryKey,
    queryFn: async () => {
      try {
        return await apiRequest<ReviewTrendsData>(API_ENDPOINTS.REVIEW_TRENDS, filters);
      } catch (error) {
        handleQueryError(error as Error, [...QUERY_KEYS.REVIEW_TRENDS], filters);
        throw error;
      }
    },
    enabled: true,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: createRetryFunction([...QUERY_KEYS.REVIEW_TRENDS]),
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

// Hook for fetching lead time data
export const useLeadTimes = (
  filters: ApiFilters
): UseQueryResult<LeadTimeData, Error> => {
  const { handleQueryError } = useApiErrorHandler();
  const queryKey = [...QUERY_KEYS.LEAD_TIMES, filters];
  
  return useQuery({
    queryKey,
    queryFn: async () => {
      try {
        return await apiRequest<LeadTimeData>(API_ENDPOINTS.LEAD_TIMES, filters);
      } catch (error) {
        handleQueryError(error as Error, [...QUERY_KEYS.LEAD_TIMES], filters);
        throw error;
      }
    },
    enabled: true,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: createRetryFunction([...QUERY_KEYS.LEAD_TIMES]),
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

// Hook for fetching KPIs
export const useKPIs = (
  filters: ApiFilters
): UseQueryResult<KPIResponse, Error> => {
  const { handleQueryError } = useApiErrorHandler();
  const queryKey = [...QUERY_KEYS.KPIS, filters];
  
  return useQuery({
    queryKey,
    queryFn: async () => {
      try {
        return await apiRequest<KPIResponse>(API_ENDPOINTS.KPIS, filters);
      } catch (error) {
        handleQueryError(error as Error, [...QUERY_KEYS.KPIS], filters);
        throw error;
      }
    },
    enabled: true,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: createRetryFunction([...QUERY_KEYS.KPIS]),
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};