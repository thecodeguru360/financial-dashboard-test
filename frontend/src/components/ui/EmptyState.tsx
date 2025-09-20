import React from 'react';
import { cn } from '../../lib/utils';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
  variant?: 'default' | 'chart' | 'table' | 'search';
}

// Default icons for different variants
const getDefaultIcon = (variant: string) => {
  switch (variant) {
    case 'chart':
      return (
        <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      );
    case 'table':
      return (
        <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 10h18M3 14h18m-9-4v8m-7 0V4a1 1 0 011-1h16a1 1 0 011 1v16a1 1 0 01-1 1H4a1 1 0 01-1-1z" />
        </svg>
      );
    case 'search':
      return (
        <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      );
    default:
      return (
        <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      );
  }
};

// Default messages for different variants
const getDefaultMessages = (variant: string) => {
  switch (variant) {
    case 'chart':
      return {
        title: 'No Data Available',
        description: 'There is no data to display for the selected filters. Try adjusting your date range or property selection.'
      };
    case 'table':
      return {
        title: 'No Records Found',
        description: 'No records match your current filters. Try broadening your search criteria.'
      };
    case 'search':
      return {
        title: 'No Results Found',
        description: 'Your search didn\'t return any results. Try different keywords or filters.'
      };
    default:
      return {
        title: 'No Data Available',
        description: 'There is currently no data to display.'
      };
  }
};

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  action,
  className,
  variant = 'default'
}) => {
  const defaultMessages = getDefaultMessages(variant);
  const displayTitle = title || defaultMessages.title;
  const displayDescription = description || defaultMessages.description;
  const displayIcon = icon || getDefaultIcon(variant);

  return (
    <div 
      className={cn(
        'flex flex-col items-center justify-center text-center p-8 min-h-[300px]',
        className
      )}
      role="status"
      aria-label="No data available"
    >
      <div className="mb-4">
        {displayIcon}
      </div>
      
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        {displayTitle}
      </h3>
      
      <p className="text-sm text-gray-600 mb-6 max-w-md">
        {displayDescription}
      </p>
      
      {action && (
        <button
          onClick={action.onClick}
          className="px-4 py-2 bg-[#459B63] text-white rounded-lg hover:bg-[#3a8354] transition-colors text-sm font-medium"
        >
          {action.label}
        </button>
      )}
    </div>
  );
};

// Specialized empty state components
export const ChartEmptyState: React.FC<Omit<EmptyStateProps, 'variant'>> = (props) => (
  <EmptyState {...props} variant="chart" />
);

export const TableEmptyState: React.FC<Omit<EmptyStateProps, 'variant'>> = (props) => (
  <EmptyState {...props} variant="table" />
);

export const SearchEmptyState: React.FC<Omit<EmptyStateProps, 'variant'>> = (props) => (
  <EmptyState {...props} variant="search" />
);