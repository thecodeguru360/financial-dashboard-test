import React from 'react';
import { QueryClient, QueryClientProvider, QueryCache, MutationCache } from '@tanstack/react-query';

// Global error handler for queries
const handleQueryError = (error: Error) => {
  console.error('Global Query Error:', {
    message: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString()
  });
  
  // You could add global error reporting here
  // e.g., send to error tracking service
};

// Global error handler for mutations
const handleMutationError = (error: Error) => {
  console.error('Global Mutation Error:', {
    message: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString()
  });
};

// Create a client with enhanced error handling
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleQueryError,
  }),
  mutationCache: new MutationCache({
    onError: handleMutationError,
  }),
  defaultOptions: {
    queries: {
      // Global defaults for all queries
      staleTime: 2 * 60 * 1000, // 2 minutes
      retry: (failureCount, error) => {
        // Don't retry on client errors (4xx)
        if (error instanceof Error) {
          const message = error.message.toLowerCase();
          if (message.includes('400') || message.includes('401') || 
              message.includes('403') || message.includes('404')) {
            return false;
          }
        }
        
        // Retry up to 3 times for other errors
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      // Network mode configuration
      networkMode: 'online',
    },
    mutations: {
      retry: (failureCount, error) => {
        // Don't retry mutations on client errors
        if (error instanceof Error) {
          const message = error.message.toLowerCase();
          if (message.includes('400') || message.includes('401') || 
              message.includes('403') || message.includes('404')) {
            return false;
          }
        }
        return failureCount < 2;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
});

interface QueryProviderProps {
  children: React.ReactNode;
}

export const QueryProvider: React.FC<QueryProviderProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};