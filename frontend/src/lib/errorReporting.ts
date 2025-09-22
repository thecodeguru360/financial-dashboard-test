// Error reporting and logging utilities

interface ErrorReport {
  message: string;
  stack?: string;
  url: string;
  timestamp: string;
  userAgent: string;
  userId?: string;
  sessionId?: string;
  additionalContext?: Record<string, any>;
}

interface ErrorContext {
  component?: string;
  action?: string;
  filters?: any;
  queryKey?: string[];
  [key: string]: any;
}

class ErrorReporter {
  private sessionId: string;
  private userId?: string;

  constructor() {
    this.sessionId = this.generateSessionId();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  setUserId(userId: string) {
    this.userId = userId;
  }

  reportError(error: Error, context?: ErrorContext) {
    const report: ErrorReport = {
      message: error.message,
      stack: error.stack,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      sessionId: this.sessionId,
      userId: this.userId,
      additionalContext: context
    };

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.group('🚨 Error Report');
      console.error('Error:', error);
      console.log('Context:', context);
      console.log('Full Report:', report);
      console.groupEnd();
    }

    // In production, you would send this to your error reporting service
    // Examples: Sentry, LogRocket, Bugsnag, etc.
    this.sendToErrorService(report);

    return report;
  }

  private async sendToErrorService(report: ErrorReport) {
    // This is where you would integrate with your error reporting service
    // For now, we'll just store it locally for development
    
    try {
      // Example: Send to Sentry
      // Sentry.captureException(new Error(report.message), {
      //   contexts: {
      //     report: report
      //   }
      // });

      // Example: Send to custom endpoint
      // await fetch('/api/errors', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(report)
      // });

      // For development: store in localStorage
      if (process.env.NODE_ENV === 'development') {
        const existingErrors = JSON.parse(localStorage.getItem('errorReports') || '[]');
        existingErrors.push(report);
        
        // Keep only last 50 errors
        if (existingErrors.length > 50) {
          existingErrors.splice(0, existingErrors.length - 50);
        }
        
        localStorage.setItem('errorReports', JSON.stringify(existingErrors));
      }
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  }

  // Get stored error reports (for development)
  getStoredErrors(): ErrorReport[] {
    try {
      return JSON.parse(localStorage.getItem('errorReports') || '[]');
    } catch {
      return [];
    }
  }

  // Clear stored error reports
  clearStoredErrors() {
    localStorage.removeItem('errorReports');
  }
}

// Create singleton instance
export const errorReporter = new ErrorReporter();

// Convenience function for reporting errors with context
export const reportError = (error: Error, context?: ErrorContext) => {
  return errorReporter.reportError(error, context);
};

// Hook for error reporting in React components
export const useErrorReporting = () => {
  const reportComponentError = (error: Error, componentName: string, additionalContext?: any) => {
    return reportError(error, {
      component: componentName,
      ...additionalContext
    });
  };

  const reportApiError = (error: Error, queryKey: string[], filters?: any) => {
    return reportError(error, {
      component: 'API',
      action: 'query',
      queryKey,
      filters
    });
  };

  const reportChartError = (error: Error, chartType: string, data?: any) => {
    return reportError(error, {
      component: 'Chart',
      action: 'render',
      chartType,
      dataSize: Array.isArray(data) ? data.length : 'unknown'
    });
  };

  return {
    reportComponentError,
    reportApiError,
    reportChartError,
    reportError
  };
};

// Global error handler for unhandled errors
export const setupGlobalErrorHandling = () => {
  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    reportError(new Error(`Unhandled Promise Rejection: ${event.reason}`), {
      component: 'Global',
      action: 'unhandledRejection'
    });
  });

  // Handle uncaught errors
  window.addEventListener('error', (event) => {
    reportError(new Error(event.message), {
      component: 'Global',
      action: 'uncaughtError',
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno
    });
  });
};