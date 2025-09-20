import React from 'react';
import { cn } from '../../lib/utils';

interface ErrorMessageProps {
  error: Error | null;
  onRetry?: () => void;
  className?: string;
  title?: string;
  showIcon?: boolean;
  variant?: 'default' | 'minimal' | 'detailed';
}

// Helper function to get user-friendly error messages
const getUserFriendlyMessage = (error: Error): { title: string; message: string; suggestion: string } => {
  const errorMessage = error.message.toLowerCase();
  
  if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
    return {
      title: 'Connection Problem',
      message: 'Unable to connect to the server',
      suggestion: 'Please check your internet connection and try again'
    };
  }
  
  if (errorMessage.includes('404') || errorMessage.includes('not found')) {
    return {
      title: 'Data Not Found',
      message: 'The requested data could not be found',
      suggestion: 'This might be a temporary issue. Please try again in a moment'
    };
  }
  
  if (errorMessage.includes('500') || errorMessage.includes('internal server')) {
    return {
      title: 'Server Error',
      message: 'The server encountered an unexpected error',
      suggestion: 'Our team has been notified. Please try again in a few minutes'
    };
  }
  
  if (errorMessage.includes('timeout')) {
    return {
      title: 'Request Timeout',
      message: 'The request took too long to complete',
      suggestion: 'The server might be busy. Please try again'
    };
  }
  
  if (errorMessage.includes('400') || errorMessage.includes('bad request')) {
    return {
      title: 'Invalid Request',
      message: 'There was a problem with the request',
      suggestion: 'Please check your filters and try again'
    };
  }
  
  // Default fallback
  return {
    title: 'Something went wrong',
    message: error.message || 'An unexpected error occurred',
    suggestion: 'Please try again or contact support if the problem persists'
  };
};

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ 
  error, 
  onRetry, 
  className,
  title,
  showIcon = true,
  variant = 'default'
}) => {
  if (!error) return null;

  const friendlyError = getUserFriendlyMessage(error);
  const displayTitle = title || friendlyError.title;

  const baseClasses = 'rounded-xl border border-red-200 bg-red-50 p-4';
  const variantClasses = {
    default: 'p-6',
    minimal: 'p-4',
    detailed: 'p-6'
  };

  return (
    <div className={cn(
      baseClasses,
      variantClasses[variant],
      className
    )}>
      <div className="flex items-start gap-3">
        {showIcon && (
          <div className="flex-shrink-0">
            <svg 
              className="w-5 h-5 text-red-600 mt-0.5" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
              />
            </svg>
          </div>
        )}
        
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-red-800 mb-1">
            {displayTitle}
          </h3>
          
          {variant !== 'minimal' && (
            <p className="text-sm text-red-700 mb-2">
              {friendlyError.message}
            </p>
          )}
          
          {variant === 'detailed' && (
            <p className="text-xs text-red-600 mb-3">
              {friendlyError.suggestion}
            </p>
          )}
          
          {process.env.NODE_ENV === 'development' && variant === 'detailed' && (
            <details className="mt-2">
              <summary className="text-xs text-red-600 cursor-pointer hover:text-red-800">
                Technical Details
              </summary>
              <pre className="mt-1 text-xs text-red-600 bg-red-100 p-2 rounded overflow-auto max-h-20">
                {error.message}
              </pre>
            </details>
          )}
        </div>
        
        {onRetry && (
          <div className="flex-shrink-0">
            <button
              onClick={onRetry}
              className="px-3 py-1.5 text-xs bg-[#459B63] text-white rounded-lg hover:bg-[#3a8354] transition-colors font-medium"
              aria-label="Retry loading data"
            >
              Retry
            </button>
          </div>
        )}
      </div>
    </div>
  );
};