import { useCallback } from 'react';
import { reportError } from '../lib/errorReporting';

interface ErrorHandlerOptions {
  logError?: boolean;
  onError?: (error: Error) => void;
}

interface ErrorInfo {
  type: 'network' | 'server' | 'client' | 'unknown';
  statusCode?: number;
  message: string;
  originalError: Error;
}

export const useErrorHandler = (options: ErrorHandlerOptions = {}) => {
  const { logError = true, onError } = options;

  const categorizeError = useCallback((error: Error): ErrorInfo => {
    const message = error.message.toLowerCase();
    
    // Network errors - enhanced detection
    if (
      message.includes('network') || 
      message.includes('fetch') || 
      message.includes('connection') ||
      message.includes('failed to fetch') ||
      message.includes('networkerror') ||
      message.includes('cors') ||
      error.name === 'NetworkError' ||
      (error.name === 'TypeError' && message.includes('fetch'))
    ) {
      return {
        type: 'network',
        message: 'Unable to connect to the server. Please check your internet connection.',
        originalError: error
      };
    }
    
    // Server errors (5xx)
    if (message.includes('500') || message.includes('502') || message.includes('503') || message.includes('504') || message.includes('internal server')) {
      const statusMatch = message.match(/(\d{3})/);
      return {
        type: 'server',
        statusCode: statusMatch ? parseInt(statusMatch[1]) : 500,
        message: 'The server encountered an error. Please try again in a few minutes.',
        originalError: error
      };
    }
    
    // Client errors (4xx)
    if (message.includes('400') || message.includes('401') || message.includes('403') || message.includes('404') || message.includes('bad request')) {
      const statusMatch = message.match(/(\d{3})/);
      const statusCode = statusMatch ? parseInt(statusMatch[1]) : 400;
      
      let userMessage = 'There was a problem with your request.';
      if (statusCode === 404) {
        userMessage = 'The requested data was not found.';
      } else if (statusCode === 401) {
        userMessage = 'You are not authorized to access this data.';
      } else if (statusCode === 403) {
        userMessage = 'Access to this resource is forbidden.';
      }
      
      return {
        type: 'client',
        statusCode,
        message: userMessage,
        originalError: error
      };
    }
    
    // Timeout errors
    if (message.includes('timeout') || message.includes('aborted')) {
      return {
        type: 'network',
        message: 'The request timed out. Please try again.',
        originalError: error
      };
    }
    
    // Default to unknown
    return {
      type: 'unknown',
      message: error.message || 'An unexpected error occurred',
      originalError: error
    };
  }, []);

  const handleError = useCallback((error: Error, context?: any) => {
    const errorInfo = categorizeError(error);
    
    // Log error if enabled
    if (logError) {
      console.error('Error handled:', {
        type: errorInfo.type,
        statusCode: errorInfo.statusCode,
        message: errorInfo.message,
        originalError: error,
        stack: error.stack,
        timestamp: new Date().toISOString(),
        context
      });
    }
    
    // Report error to error reporting service
    reportError(error, {
      errorType: errorInfo.type,
      statusCode: errorInfo.statusCode,
      ...context
    });
    
    // Call custom error handler if provided
    if (onError) {
      onError(error);
    }
    
    return errorInfo;
  }, [categorizeError, logError, onError]);

  const createRetryHandler = useCallback((retryFn: () => void, maxRetries = 3) => {
    let retryCount = 0;
    
    return () => {
      if (retryCount < maxRetries) {
        retryCount++;
        console.log(`Retrying... (${retryCount}/${maxRetries})`);
        retryFn();
      } else {
        console.warn('Max retries reached');
      }
    };
  }, []);

  return {
    handleError,
    categorizeError,
    createRetryHandler
  };
};

// Hook specifically for API query errors
export const useApiErrorHandler = () => {
  const { handleError } = useErrorHandler({
    logError: true
  });

  const handleQueryError = useCallback((error: Error, queryKey: readonly string[], filters?: any) => {
    const errorInfo = handleError(error, {
      component: 'API',
      action: 'query',
      queryKey,
      filters
    });
    
    // Additional logging for API queries
    console.error(`API Query Error [${queryKey.join('.')}]:`, {
      ...errorInfo,
      queryKey,
      filters,
      timestamp: new Date().toISOString()
    });
    
    return errorInfo;
  }, [handleError]);

  return {
    handleQueryError,
    handleError
  };
};