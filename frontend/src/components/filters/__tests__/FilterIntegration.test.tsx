import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FilterProvider, useFilters } from '../../../providers/FilterProvider';
import { useRevenueTimeline } from '../../../hooks/useApiQueries';

// Mock the API hook
const mockUseRevenueTimeline = jest.fn();
jest.mock('../../../hooks/useApiQueries', () => ({
  useRevenueTimeline: () => mockUseRevenueTimeline(),
}));

// Test component that uses both filters and API hooks
const TestIntegrationComponent: React.FC = () => {
  const { filters, updateFilters } = useFilters();
  const { data, isLoading } = useRevenueTimeline(filters);
  
  return (
    <div>
      <div data-testid="filters">
        Start: {filters.start_date || 'None'} | End: {filters.end_date || 'None'} | Properties: {filters.property_ids?.join(',') || 'None'}
      </div>
      <button
        onClick={() => updateFilters({ start_date: '2024-01-01', end_date: '2024-12-31' })}
        data-testid="set-date-range"
      >
        Set Date Range
      </button>
      <button
        onClick={() => updateFilters({ property_ids: [1, 2] })}
        data-testid="set-properties"
      >
        Set Properties
      </button>
      <div data-testid="api-status">
        {isLoading ? 'Loading' : 'Loaded'}
      </div>
      <div data-testid="api-data">
        {data ? JSON.stringify(data) : 'No data'}
      </div>
    </div>
  );
};

describe('Filter Integration', () => {
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
          <TestIntegrationComponent />
        </FilterProvider>
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
    mockUseRevenueTimeline.mockReturnValue({
      data: { data: [{ date: '2024-01-01', total_revenue: 1000 }] },
      isLoading: false,
    });
  });

  it('should pass filters to API hooks', () => {
    renderWithProviders();
    
    // Initial state
    expect(screen.getByTestId('filters')).toHaveTextContent('Start: None | End: None | Properties: None');
    
    // Update date range
    fireEvent.click(screen.getByTestId('set-date-range'));
    expect(screen.getByTestId('filters')).toHaveTextContent('Start: 2024-01-01 | End: 2024-12-31 | Properties: None');
    
    // Update properties
    fireEvent.click(screen.getByTestId('set-properties'));
    expect(screen.getByTestId('filters')).toHaveTextContent('Start: 2024-01-01 | End: 2024-12-31 | Properties: 1,2');
  });

  it('should display API data correctly', () => {
    renderWithProviders();
    
    expect(screen.getByTestId('api-status')).toHaveTextContent('Loaded');
    expect(screen.getByTestId('api-data')).toHaveTextContent('{"data":[{"date":"2024-01-01","total_revenue":1000}]}');
  });

  it('should handle loading state', () => {
    mockUseRevenueTimeline.mockReturnValue({
      data: null,
      isLoading: true,
    });

    renderWithProviders();
    
    expect(screen.getByTestId('api-status')).toHaveTextContent('Loading');
    expect(screen.getByTestId('api-data')).toHaveTextContent('No data');
  });
});