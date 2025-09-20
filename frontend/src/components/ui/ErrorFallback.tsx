import React from 'react';
import { cn } from '../../lib/utils';

interface ErrorFallbackProps {
  error?: Error | null;
  resetError?: () => void;
  className?: string;
  variant?: 'chart' | 'page' | 'section' | 'minimal';
  title?: string;
  description?: string;
  showReload?: boolean;
  showRetry?: boolean;
  showDetails?: boolean;
}

// Get appropriate icon for error type
const getErrorIcon = (variant: string) => {
  switch (variant) {
    case 'chart':
      return (
        <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      );
    case 'page':
      return (
        <svg className="w-12 h-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      );
    default:
      return (
        <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
  }
};

// Get default messages based on variant
const getDefaultMessages = (variant: string, error?: Error | null) => {
  const isNetworkError = error?.message.toLowerCase().includes('network') || 
                        error?.message.toLowerCase().includes('fetch') ||
                        error?.message.toLowerCase().includes('connection');
  
  const isServerError = error?.message.toLowerCase().includes('500') ||
                       error?.message.toLowerCase().includes('server');

  switch (variant) {
    case 'chart':
      if (isNetworkError) {
        return {
          title: 'Connection Error',
          description: 'Unable to load chart data. Please check your internet connection and try again.'
        };
      }
      if (isServerError) {
        return {
          title: 'Server Error',
          description: 'The server is experiencing issues. Please try again in a few minutes.'
        };
      }
      return {
        title: 'Chart Error',
        description: 'Unable to display this chart. There may be an issue with the data or chart configuration.'
      };
    
    case 'page':
      return {
        title: 'Application Error',
        description: 'The application encountered an unexpected error. We apologize for the inconvenience.'
      };
    
    case 'section':
      return {
        title: 'Section Error',
        description: 'This section could not be loaded. Please try refreshing the page.'
      };
    
    default:
      return {
        title: 'Error',
        description: 'Something went wrong. Please try again.'
      };
  }
};

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetError,
  className,
  variant = 'minimal',
  title,
  description,
  showReload = true,
  showRetry = true,
  showDetails = false
}) => {
  const defaultMessages = getDefaultMessages(variant, error);
  const displayTitle = title || defaultMessages.title;
  const displayDescription = description || defaultMessages.description;
  const isDevelopment = process.env.NODE_ENV === 'development';

  const handleReload = () => {
    window.location.reload();
  };

  const handleRetry = () => {
    if (resetError) {
      resetError();
    } else {
      window.location.reload();
    }
  };

  // Variant-specific styling
  const getVariantStyles = () => {
    switch (variant) {
      case 'page':
        return {
          container: 'min-h-screen bg-[#FAFAFA] flex items-center justify-center p-4',
          content: 'max-w-md w-full bg-white rounded-xl border border-[#F1F1F1] p-8 text-center shadow-lg',
          icon: 'flex items-center justify-center w-16 h-16 mx-auto mb-6 bg-red-100 rounded-full',
          title: 'text-2xl font-bold text-gray-900 mb-4',
          description: 'text-gray-600 mb-6'
        };
      
      case 'chart':
        return {
          container: 'flex items-center justify-center p-8 min-h-[300px]',
          content: 'max-w-sm w-full text-center',
          icon: 'flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-red-100 rounded-full',
          title: 'text-lg font-semibold text-gray-900 mb-2',
          description: 'text-sm text-gray-600 mb-4'
        };
      
      case 'section':
        return {
          container: 'flex items-center justify-center p-6 min-h-[200px] bg-red-50 rounded-xl border border-red-200',
          content: 'max-w-sm w-full text-center',
          icon: 'flex items-center justify-center w-10 h-10 mx-auto mb-3 bg-red-100 rounded-full',
          title: 'text-base font-medium text-gray-900 mb-2',
          description: 'text-sm text-gray-600 mb-3'
        };
      
      default: // minimal
        return {
          container: 'flex items-center gap-3 p-4 bg-red-50 rounded-lg border border-red-200',
          content: 'flex-1',
          icon: 'flex-shrink-0',
          title: 'text-sm font-medium text-red-800',
          description: 'text-xs text-red-700 mt-1'
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <div className={cn(styles.container, className)} role="alert" aria-live="assertive">
      <div className={styles.content}>
        {variant !== 'minimal' && (
          <div className={styles.icon}>
            {getErrorIcon(variant)}
          </div>
        )}
        
        <div className={variant === 'minimal' ? 'flex items-start gap-3' : ''}>
          {variant === 'minimal' && (
            <div className={styles.icon}>
              {getErrorIcon(variant)}
            </div>
          )}
          
          <div className={variant === 'minimal' ? 'flex-1 min-w-0' : ''}>
            <h3 className={styles.title}>
              {displayTitle}
            </h3>
            
            <p className={styles.description}>
              {displayDescription}
            </p>
            
            {/* Development error details */}
            {isDevelopment && showDetails && error && variant !== 'minimal' && (
              <details className="mb-4 text-left">
                <summary className="text-xs text-red-600 cursor-pointer hover:text-red-800 mb-2">
                  Technical Details (Development)
                </summary>
                <div className="bg-red-50 rounded p-3 space-y-2">
                  <div>
                    <p className="text-xs font-medium text-red-700">Error:</p>
                    <p className="text-xs text-red-600 font-mono">{error.message}</p>
                  </div>
                  {error.stack && (
                    <div>
                      <p className="text-xs font-medium text-red-700">Stack:</p>
                      <pre className="text-xs text-red-600 font-mono overflow-auto max-h-32 whitespace-pre-wrap">
                        {error.stack}
                      </pre>
                    </div>
                  )}
                </div>
              </details>
            )}
            
            {/* Action buttons */}
            {(showRetry || showReload) && variant !== 'minimal' && (
              <div className="flex gap-2 justify-center">
                {showRetry && resetError && (
                  <button
                    onClick={handleRetry}
                    className="px-4 py-2 bg-[#459B63] text-white rounded-lg hover:bg-[#3a8354] transition-colors text-sm font-medium"
                    aria-label="Retry loading"
                  >
                    Try Again
                  </button>
                )}
                
                {showReload && (
                  <button
                    onClick={handleReload}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
                    aria-label="Reload page"
                  >
                    Reload Page
                  </button>
                )}
              </div>
            )}
          </div>
          
          {/* Minimal variant action button */}
          {variant === 'minimal' && showRetry && resetError && (
            <div className="flex-shrink-0">
              <button
                onClick={handleRetry}
                className="px-3 py-1.5 text-xs bg-[#459B63] text-white rounded-lg hover:bg-[#3a8354] transition-colors font-medium"
                aria-label="Retry"
              >
                Retry
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Specialized error fallback components
export const ChartErrorFallback: React.FC<Omit<ErrorFallbackProps, 'variant'>> = (props) => (
  <ErrorFallback {...props} variant="chart" showDetails={true} />
);

export const PageErrorFallback: React.FC<Omit<ErrorFallbackProps, 'variant'>> = (props) => (
  <ErrorFallback {...props} variant="page" showDetails={true} />
);

export const SectionErrorFallback: React.FC<Omit<ErrorFallbackProps, 'variant'>> = (props) => (
  <ErrorFallback {...props} variant="section" />
);

export const MinimalErrorFallback: React.FC<Omit<ErrorFallbackProps, 'variant'>> = (props) => (
  <ErrorFallback {...props} variant="minimal" showReload={false} />
);