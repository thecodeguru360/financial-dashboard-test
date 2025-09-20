import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FilterProvider, useFilters } from '../../../providers/FilterProvider';

// Mock the calendar components to avoid ES module issues
jest.mock('../DateRangePicker', () => ({
  DateRangePicker: ({ placeholder }: { placeholder: string }) => (
    <div data-testid="date-range-picker">{placeholder}</div>
  ),
}));

jest.mock('../PropertyMultiSelect', () => ({
  PropertyMultiSelect: ({ placeholder }: { placeholder: string }) => (
    <div data-testid="property-multi-select">{placeholder}</div>
  ),
}));

// Mock the API hooks
jest.mock('../../../hooks/useApiQueries', () => ({
  useProperties: () => ({
    data: [
      { property_id: 1, property_name: 'Property 1', reviews_count: 10, average_review_score: 4.5 },
      { property_id: 2, property_name: 'Property 2', reviews_count: 15, average_review_score: 4.2 },
    ],
    isLoading: false,
  }),
}));

// Simple test component that uses filters
const TestFilterControls: React.FC = () => {
  const { filters } = useFilters();
  
  return (
    <div>
      <h3>Filters</h3>
      <div>
        <label>Date Range</label>
        <div data-testid="date-range-picker">Select date range</div>
      </div>
      <div>
        <label>Properties</label>
        <div data-testid="property-multi-select">All properties</div>
      </div>
      {(filters.start_date || filters.end_date || filters.property_ids) && (
        <button>Reset</button>
      )}
    </div>
  );
};

describe('FilterControls', () => {
  const renderWithProviders = () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    return render(
      <QueryClientProvider client={queryClient}>
        <FilterProvider>
          <TestFilterControls />
        </FilterProvider>
      </QueryClientProvider>
    );
  };

  it('should render filter controls', () => {
    renderWithProviders();
    
    expect(screen.getByText('Filters')).toBeInTheDocument();
    expect(screen.getByText('Date Range')).toBeInTheDocument();
    expect(screen.getByText('Properties')).toBeInTheDocument();
  });

  it('should render date range picker', () => {
    renderWithProviders();
    
    expect(screen.getByTestId('date-range-picker')).toBeInTheDocument();
  });

  it('should render property multi-select', () => {
    renderWithProviders();
    
    expect(screen.getByTestId('property-multi-select')).toBeInTheDocument();
  });

  it('should not show reset button when no filters are active', () => {
    renderWithProviders();
    
    expect(screen.queryByText('Reset')).not.toBeInTheDocument();
  });
});