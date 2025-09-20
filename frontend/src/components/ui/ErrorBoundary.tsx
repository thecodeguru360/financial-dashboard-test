import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetOnPropsChange?: boolean;
  resetKeys?: Array<string | number>;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
  prevResetKeys?: Array<string | number>;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public static getDerivedStateFromProps(props: Props, state: State): State | null {
    const { resetKeys } = props;
    const { prevResetKeys, hasError } = state;

    // Reset error state if resetKeys have changed
    if (hasError && resetKeys && prevResetKeys) {
      if (resetKeys.some((key, idx) => key !== prevResetKeys[idx])) {
        return {
          hasError: false,
          error: undefined,
          errorInfo: undefined,
          prevResetKeys: resetKeys,
        };
      }
    }

    // Update prevResetKeys if they've changed
    if (resetKeys && (!prevResetKeys || resetKeys.some((key, idx) => key !== prevResetKeys[idx]))) {
      return {
        ...state,
        prevResetKeys: resetKeys,
      };
    }

    return null;
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Store error info for debugging
    this.setState({ errorInfo });
    
    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  private handleRetry = () => {
    this.setState({ 
      hasError: false, 
      error: undefined, 
      errorInfo: undefined 
    });
  };

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const isDevelopment = process.env.NODE_ENV === 'development';

      return (
        <div className="flex flex-col items-center justify-center p-8 text-center min-h-[300px]">
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 max-w-lg w-full">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-red-100 rounded-full">
              <svg 
                className="w-6 h-6 text-red-600" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" 
                />
              </svg>
            </div>
            
            <h2 className="text-lg font-semibold text-red-800 mb-2">
              Chart Error
            </h2>
            
            <p className="text-sm text-red-700 mb-4">
              {this.state.error?.message || 'An unexpected error occurred while rendering this chart'}
            </p>

            {isDevelopment && this.state.errorInfo && (
              <details className="mb-4 text-left">
                <summary className="text-xs text-red-600 cursor-pointer hover:text-red-800">
                  Technical Details (Development)
                </summary>
                <pre className="mt-2 text-xs text-red-600 bg-red-100 p-2 rounded overflow-auto max-h-32">
                  {this.state.error?.stack}
                </pre>
              </details>
            )}
            
            <div className="flex gap-2 justify-center">
              <button
                onClick={this.handleRetry}
                className="px-4 py-2 bg-[#459B63] text-white rounded-lg hover:bg-[#3a8354] transition-colors text-sm font-medium"
              >
                Try Again
              </button>
              <button
                onClick={this.handleReload}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}