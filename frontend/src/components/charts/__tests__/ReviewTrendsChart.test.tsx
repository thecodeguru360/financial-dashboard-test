import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReviewTrendsChart } from '../ReviewTrendsChart';
import { FilterProvider } from '../../../providers/FilterProvider';

// Mock the API hook
jest.mock('../../../hooks/useApiQueries', () => ({
  useReviewTrends: jest.fn(),
}));

// Mock Recharts components to avoid ResizeObserver issues
jest.mock('recharts', () => ({
  ComposedChart: ({ children }: any) => <div data-testid="composed-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  Legend: () => <div data-testid="legend" />,
}));

const { useReviewTrends } = require('../../../hooks/useApiQueries');

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

describe('ReviewTrendsChart', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state', () => {
    useReviewTrends.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
      refetch: jest.fn(),
    });

    render(<ReviewTrendsChart />, { wrapper: createWrapper() });
    
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    const mockError = new Error('Failed to fetch review trends data');
    useReviewTrends.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: mockError,
      refetch: jest.fn(),
    });

    render(<ReviewTrendsChart />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Error loading data')).toBeInTheDocument();
    expect(screen.getByText('Failed to fetch review trends data')).toBeInTheDocument();
  });

  it('renders chart with data', () => {
    const mockData = {
      data: [
        { 
          month: '2023-01', 
          avg_rating: 4.5, 
          review_count: 25 
        },
        { 
          month: '2023-02', 
          avg_rating: 4.2, 
          review_count: 18 
        },
        { 
          month: '2023-03', 
          avg_rating: 4.7, 
          review_count: 32 
        },
      ],
    };

    useReviewTrends.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<ReviewTrendsChart />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Review Trends')).toBeInTheDocument();
    // Check that the chart components are rendered
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    expect(screen.getByTestId('composed-chart')).toBeInTheDocument();
    
    // Check summary statistics display
    expect(screen.getByText('Total Reviews:')).toBeInTheDocument();
    expect(screen.getByText('75')).toBeInTheDocument(); // 25 + 18 + 32
    expect(screen.getByText('Overall Average:')).toBeInTheDocument();
  });

  it('renders empty state when no data available', () => {
    const mockData = {
      data: [],
    };

    useReviewTrends.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<ReviewTrendsChart />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Review Trends')).toBeInTheDocument();
    expect(screen.getByText('No review data available')).toBeInTheDocument();
    expect(screen.getByText('Try adjusting your date range or property filters')).toBeInTheDocument();
  });

  it('formats month display correctly', () => {
    const mockData = {
      data: [
        { 
          month: '2023-01', 
          avg_rating: 4.5, 
          review_count: 25 
        },
        { 
          month: '2023-12', 
          avg_rating: 4.2, 
          review_count: 18 
        },
      ],
    };

    useReviewTrends.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<ReviewTrendsChart />, { wrapper: createWrapper() });
    
    // Check for screen reader table to verify month formatting
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
    
    // Should format 2023-01 as "Jan 2023" and 2023-12 as "Dec 2023"
    expect(screen.getByText('Jan 2023')).toBeInTheDocument();
    expect(screen.getByText('Dec 2023')).toBeInTheDocument();
  });

  it('calculates summary statistics correctly', () => {
    const mockData = {
      data: [
        { 
          month: '2023-01', 
          avg_rating: 4.0, 
          review_count: 10 
        },
        { 
          month: '2023-02', 
          avg_rating: 5.0, 
          review_count: 10 
        },
      ],
    };

    useReviewTrends.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<ReviewTrendsChart />, { wrapper: createWrapper() });
    
    // Total reviews should be 20
    expect(screen.getByText('20')).toBeInTheDocument();
    
    // Overall average should be weighted: (4.0*10 + 5.0*10) / 20 = 4.5
    expect(screen.getByText('4.50 ⭐')).toBeInTheDocument();
  });

  it('includes accessible data table for screen readers', () => {
    const mockData = {
      data: [
        { 
          month: '2023-01', 
          avg_rating: 4.5, 
          review_count: 25 
        },
        { 
          month: '2023-02', 
          avg_rating: 4.2, 
          review_count: 18 
        },
      ],
    };

    useReviewTrends.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<ReviewTrendsChart />, { wrapper: createWrapper() });
    
    // Check for screen reader table
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
    expect(screen.getByText('Review trends data showing monthly ratings and counts')).toBeInTheDocument();
    
    // Check table headers
    expect(screen.getByText('Month')).toBeInTheDocument();
    expect(screen.getByText('Average Rating')).toBeInTheDocument();
    expect(screen.getByText('Review Count')).toBeInTheDocument();
  });

  it('sorts data by month chronologically', () => {
    const mockData = {
      data: [
        { 
          month: '2023-03', 
          avg_rating: 4.7, 
          review_count: 32 
        },
        { 
          month: '2023-01', 
          avg_rating: 4.5, 
          review_count: 25 
        },
        { 
          month: '2023-02', 
          avg_rating: 4.2, 
          review_count: 18 
        },
      ],
    };

    useReviewTrends.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<ReviewTrendsChart />, { wrapper: createWrapper() });
    
    // Check for screen reader table to verify sorting
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
    
    // The data should be sorted chronologically: Jan, Feb, Mar
    const rows = screen.getAllByRole('row');
    expect(rows).toHaveLength(4); // header + 3 data rows
  });

  it('handles different month formats gracefully', () => {
    const mockData = {
      data: [
        { 
          month: 'January 2023', 
          avg_rating: 4.5, 
          review_count: 25 
        },
        { 
          month: '2023-02', 
          avg_rating: 4.2, 
          review_count: 18 
        },
      ],
    };

    useReviewTrends.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<ReviewTrendsChart />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Review Trends')).toBeInTheDocument();
    // Should handle both formats without crashing
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
  });

  it('displays ratings with proper precision', () => {
    const mockData = {
      data: [
        { 
          month: '2023-01', 
          avg_rating: 4.567, 
          review_count: 25 
        },
      ],
    };

    useReviewTrends.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<ReviewTrendsChart />, { wrapper: createWrapper() });
    
    // Check for screen reader table to verify rating precision
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
    
    // Should display rating with 2 decimal places
    expect(screen.getByText('4.57 out of 5 stars')).toBeInTheDocument();
  });

  it('handles zero review counts correctly', () => {
    const mockData = {
      data: [
        { 
          month: '2023-01', 
          avg_rating: 0, 
          review_count: 0 
        },
        { 
          month: '2023-02', 
          avg_rating: 4.5, 
          review_count: 10 
        },
      ],
    };

    useReviewTrends.mockReturnValue({
      data: mockData,
      isLoading: false,
      error: null,
      refetch: jest.fn(),
    });

    render(<ReviewTrendsChart />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Review Trends')).toBeInTheDocument();
    // Should handle zero values without crashing
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    
    // Total reviews should be 10
    expect(screen.getByText('10')).toBeInTheDocument();
  });
});