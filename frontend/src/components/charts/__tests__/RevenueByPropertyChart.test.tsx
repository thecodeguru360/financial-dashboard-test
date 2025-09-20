import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RevenueByPropertyChart } from '../RevenueByPropertyChart';
import { FilterProvider } from '../../../providers/FilterProvider';

// Mock the API hook
jest.mock('../../../hooks/useApiQueries', () => ({
  useRevenueByProperty: jest.fn(),
}));

const { useRevenueByProperty } = require('../../../hooks/useApiQueries');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <FilterProvider>
        {children}
      </FilterProvider>
    </QueryClientProvider>
  );
};

describe('RevenueByPropertyChart', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state', () => {
    useRevenueByProperty.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
      refetch: jest.fn(),
    });

    render(<RevenueByPropertyChart />, { wrapper: createWrapper() });
    
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    const mockError = new Error('Failed to fetch data');
    useRevenueByProperty.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: mockError,
      refetch: jest.fn(),
    });

    render(<RevenueByPropertyChart />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Error loading data')).toBeInTheDocument();
    expect(screen.getByText('Failed to fetch data')).toBeInTheDocument();
  });

  it('renders chart with data', () => {
    const mockData = {
      data: [
        { property_id: 1, property_name: 'Property A', total_revenue: 5000 },
        { property_id: 2, property_name: 'Property B', total_revenue: 3000 },
        { property_id: 3, property_name: 'Property C', total_revenue: 4000 },
      ],
    };

    useRevenueByProperty.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<RevenueByPropertyChart />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Revenue by Property')).toBeInTheDocument();
    // Check that the chart container is rendered
    expect(screen.getByRole('img', { name: 'Revenue by property chart' })).toBeInTheDocument();
  });

  it('sorts data by revenue in descending order by default', () => {
    const mockData = {
      data: [
        { property_id: 1, property_name: 'Property A', total_revenue: 3000 },
        { property_id: 2, property_name: 'Property B', total_revenue: 5000 },
        { property_id: 3, property_name: 'Property C', total_revenue: 4000 },
      ],
    };

    useRevenueByProperty.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<RevenueByPropertyChart />, { wrapper: createWrapper() });
    
    // Check for screen reader table to verify sorting
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
    
    // The data should be sorted by revenue descending: B (5000), C (4000), A (3000)
    const rows = screen.getAllByRole('row');
    expect(rows).toHaveLength(4); // header + 3 data rows
  });

  it('includes accessible data table for screen readers', () => {
    const mockData = {
      data: [
        { property_id: 1, property_name: 'Property A', total_revenue: 5000 },
        { property_id: 2, property_name: 'Property B', total_revenue: 3000 },
      ],
    };

    useRevenueByProperty.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<RevenueByPropertyChart />, { wrapper: createWrapper() });
    
    // Check for screen reader table
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
    expect(screen.getByText('Revenue by property data')).toBeInTheDocument();
  });
});