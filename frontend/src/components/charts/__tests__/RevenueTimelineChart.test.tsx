import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RevenueTimelineChart } from '../RevenueTimelineChart';
import { FilterProvider } from '../../../providers/FilterProvider';

// Mock the API hook
jest.mock('../../../hooks/useApiQueries', () => ({
  useRevenueTimeline: jest.fn(),
}));

const { useRevenueTimeline } = require('../../../hooks/useApiQueries');

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

describe('RevenueTimelineChart', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state', () => {
    useRevenueTimeline.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
      refetch: jest.fn(),
    });

    render(<RevenueTimelineChart />, { wrapper: createWrapper() });
    
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    const mockError = new Error('Failed to fetch data');
    useRevenueTimeline.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: mockError,
      refetch: jest.fn(),
    });

    render(<RevenueTimelineChart />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Error loading data')).toBeInTheDocument();
    expect(screen.getByText('Failed to fetch data')).toBeInTheDocument();
  });

  it('renders chart with data', () => {
    const mockData = {
      data: [
        { date: '2024-01-01', total_revenue: 1000 },
        { date: '2024-01-02', total_revenue: 1500 },
        { date: '2024-01-03', total_revenue: 1200 },
      ],
    };

    useRevenueTimeline.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<RevenueTimelineChart />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Revenue Timeline')).toBeInTheDocument();
    // Check that the chart container is rendered
    expect(screen.getByRole('img', { name: 'Revenue timeline chart' })).toBeInTheDocument();
  });

  it('includes accessible data table for screen readers', () => {
    const mockData = {
      data: [
        { date: '2024-01-01', total_revenue: 1000 },
        { date: '2024-01-02', total_revenue: 1500 },
      ],
    };

    useRevenueTimeline.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<RevenueTimelineChart />, { wrapper: createWrapper() });
    
    // Check for screen reader table
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
    expect(screen.getByText('Revenue timeline data')).toBeInTheDocument();
  });
});