import React from 'react';
import { UseQueryResult } from '@tanstack/react-query';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorBoundary } from './ErrorBoundary';
import { ChartSkeleton } from './SkeletonLoader';
import { ChartEmptyState } from './EmptyState';
import { ChartErrorFallback } from './ErrorFallback';
import { cn } from '../../lib/utils';

interface ChartWrapperProps<T> {
  query: UseQueryResult<T, Error>;
  children: (data: T) => React.ReactNode;
  title?: string;
  className?: string;
  minHeight?: string;
  loadingVariant?: 'spinner' | 'skeleton';
  skeletonVariant?: 'line' | 'bar' | 'mixed';
  emptyStateProps?: {
    title?: string;
    description?: string;
    action?: {
      label: string;
      onClick: () => void;
    };
  };
  errorFallbackProps?: {
    title?: string;
    description?: string;
    showDetails?: boolean;
  };
  // Function to check if data is empty
  isEmpty?: (data: T) => boolean;
}

// Default empty check function
const defaultIsEmpty = <T,>(data: T): boolean => {
  if (!data) return true;
  if (Array.isArray(data)) return data.length === 0;
  if (typeof data === 'object' && data !== null) {
    // Check if it's an object with a 'data' property (common API response pattern)
    if ('data' in data && Array.isArray((data as any).data)) {
      return (data as any).data.length === 0;
    }
    // Check if object has any properties
    return Object.keys(data).length === 0;
  }
  return false;
};

export function ChartWrapper<T>({ 
  query, 
  children, 
  title, 
  className,
  minHeight = 'min-h-[300px]',
  loadingVariant = 'skeleton',
  skeletonVariant = 'line',
  emptyStateProps,
  errorFallbackProps,
  isEmpty = defaultIsEmpty
}: ChartWrapperProps<T>) {
  const { data, isLoading, error, refetch, isRefetching } = query;

  return (
    <div className={cn(
      'rounded-xl border border-[#F1F1F1] bg-white p-6 shadow-sm hover:shadow-md transition-shadow duration-200',
      minHeight,
      className
    )}>
      {title && (
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#F1F1F1]">
          <h3 className="text-lg font-semibold text-gray-900">
            {title}
          </h3>
          {isRefetching && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <LoadingSpinner size="sm" />
              <span>Updating...</span>
            </div>
          )}
        </div>
      )}
      
      <ErrorBoundary
        resetKeys={[query.dataUpdatedAt]} // Reset error boundary when data updates
        fallback={
          <ChartErrorFallback
            error={new Error('Chart rendering failed')}
            resetError={() => window.location.reload()}
            title={errorFallbackProps?.title}
            description={errorFallbackProps?.description}
            showDetails={errorFallbackProps?.showDetails}
          />
        }
      >
        {isLoading && (
          <div className="w-full">
            {loadingVariant === 'skeleton' ? (
              <ChartSkeleton variant={skeletonVariant} />
            ) : (
              <div className="flex items-center justify-center h-full min-h-[300px]">
                <div className="text-center">
                  <LoadingSpinner size="lg" className="mb-3" />
                  <p className="text-sm text-gray-600">Loading chart data...</p>
                </div>
              </div>
            )}
          </div>
        )}
        
        {error && !isLoading && (
          <ChartErrorFallback
            error={error}
            resetError={() => refetch()}
            title={errorFallbackProps?.title}
            description={errorFallbackProps?.description}
            showDetails={errorFallbackProps?.showDetails}
          />
        )}
        
        {data && !isLoading && !error && isEmpty(data) && (
          <ChartEmptyState
            title={emptyStateProps?.title}
            description={emptyStateProps?.description}
            action={emptyStateProps?.action}
          />
        )}
        
        {data && !isLoading && !error && !isEmpty(data) && (
          <div className="w-full">
            {children(data)}
          </div>
        )}
      </ErrorBoundary>
    </div>
  );
}