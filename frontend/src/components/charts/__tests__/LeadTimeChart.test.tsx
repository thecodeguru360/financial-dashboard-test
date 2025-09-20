import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LeadTimeChart } from '../LeadTimeChart';
import { FilterProvider } from '../../../providers/FilterProvider';
import { useLeadTimes } from '../../../hooks/useApiQueries';
import { LeadTimeData } from '../../../types/api';

// Mock the API hook
jest.mock('../../../hooks/useApiQueries');
const mockUseLeadTimes = useLeadTimes as jest.MockedFunction<typeof useLeadTimes>;

// Mock Recharts components
jest.mock('recharts', () => ({
  ...jest.requireActual('recharts'),
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Cell: () => <div data-testid="cell" />,
}));

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <FilterProvider>
        {children}
      </FilterProvider>
    </QueryClientProvider>
  );
};

// Mock data
const mockLeadTimeData: LeadTimeData = {
  stats: {
    median_days: 14,
    p90_days: 45,
    distribution: [5, 10, 15, 20, 8, 6, 4, 2, 1],
  },
  data: [
    { lead_time_days: 1, count: 5 },
    { lead_time_days: 7, count: 10 },
    { lead_time_days: 14, count: 15 },
    { lead_time_days: 21, count: 20 },
    { lead_time_days: 30, count: 8 },
    { lead_time_days: 45, count: 6 },
    { lead_time_days: 60, count: 4 },
    { lead_time_days: 90, count: 2 },
    { lead_time_days: 120, count: 1 },
  ],
};

describe('LeadTimeChart', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state correctly', () => {
    mockUseLeadTimes.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
      isError: false,
    } as any);

    render(
      <TestWrapper>
        <LeadTimeChart />
      </TestWrapper>
    );

    expect(screen.getByRole('status', { name: 'Loading' })).toBeInTheDocument();
  });

  it('renders error state correctly', () => {
    const mockError = new Error('Failed to fetch lead time data');
    mockUseLeadTimes.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: mockError,
      isError: true,
    } as any);

    render(
      <TestWrapper>
        <LeadTimeChart />
      </TestWrapper>
    );

    expect(screen.getByText('Error loading data')).toBeInTheDocument();
    expect(screen.getByText('Failed to fetch lead time data')).toBeInTheDocument();
  });

  it('renders chart with data correctly', async () => {
    mockUseLeadTimes.mockReturnValue({
      data: mockLeadTimeData,
      isLoading: false,
      error: null,
      isError: false,
    } as any);

    render(
      <TestWrapper>
        <LeadTimeChart />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Booking Lead Time Analysis')).toBeInTheDocument();
    });

    // Check statistics table
    expect(screen.getByText('Lead Time Statistics')).toBeInTheDocument();
    expect(screen.getByText('14')).toBeInTheDocument(); // Median
    expect(screen.getByText('45')).toBeInTheDocument(); // P90
    expect(screen.getByText('Median Days')).toBeInTheDocument();
    expect(screen.getByText('90th Percentile')).toBeInTheDocument();

    // Check summary stats
    expect(screen.getByText('Total Bookings:')).toBeInTheDocument();
    expect(screen.getByText('Average Lead Time:')).toBeInTheDocument();

    // Check legend
    expect(screen.getByText('≤ 7 days (Last minute)')).toBeInTheDocument();
    expect(screen.getByText('8-30 days (Short term)')).toBeInTheDocument();
    expect(screen.getByText('> 30 days (Long term)')).toBeInTheDocument();

    // Check chart components
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    expect(screen.getByTestId('bar')).toBeInTheDocument();
  });

  it('renders empty state when no data available', () => {
    mockUseLeadTimes.mockReturnValue({
      data: { stats: { median_days: 0, p90_days: 0, distribution: [] }, data: [] },
      isLoading: false,
      error: null,
      isError: false,
    } as any);

    render(
      <TestWrapper>
        <LeadTimeChart />
      </TestWrapper>
    );

    expect(screen.getByText('No lead time data available')).toBeInTheDocument();
    expect(screen.getByText('Try adjusting your date range or property filters')).toBeInTheDocument();
  });

  it('applies custom className correctly', () => {
    mockUseLeadTimes.mockReturnValue({
      data: mockLeadTimeData,
      isLoading: false,
      error: null,
      isError: false,
    } as any);

    const { container } = render(
      <TestWrapper>
        <LeadTimeChart className="custom-class" />
      </TestWrapper>
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('includes accessibility features', async () => {
    mockUseLeadTimes.mockReturnValue({
      data: mockLeadTimeData,
      isLoading: false,
      error: null,
      isError: false,
    } as any);

    render(
      <TestWrapper>
        <LeadTimeChart />
      </TestWrapper>
    );

    await waitFor(() => {
      // Check ARIA label
      const chartContainer = screen.getByRole('img');
      expect(chartContainer).toHaveAttribute(
        'aria-label',
        'Lead time distribution histogram showing booking patterns'
      );
    });

    // Check screen reader table
    const table = screen.getByRole('table', { hidden: true });
    expect(table).toBeInTheDocument();
    
    const caption = screen.getByText('Lead time distribution data showing booking patterns by advance booking days', { selector: 'caption' });
    expect(caption).toBeInTheDocument();

    // Check table headers
    expect(screen.getByText('Lead Time (Days)', { selector: 'th' })).toBeInTheDocument();
    expect(screen.getByText('Number of Bookings', { selector: 'th' })).toBeInTheDocument();
    expect(screen.getByText('Category', { selector: 'th' })).toBeInTheDocument();
  });

  it('calculates summary statistics correctly', async () => {
    mockUseLeadTimes.mockReturnValue({
      data: mockLeadTimeData,
      isLoading: false,
      error: null,
      isError: false,
    } as any);

    render(
      <TestWrapper>
        <LeadTimeChart />
      </TestWrapper>
    );

    await waitFor(() => {
      // Total bookings should be sum of all counts: 5+10+15+20+8+6+4+2+1 = 71
      expect(screen.getByText('71')).toBeInTheDocument();
      
      // Average should be calculated correctly
      // (1*5 + 7*10 + 14*15 + 21*20 + 30*8 + 45*6 + 60*4 + 90*2 + 120*1) / 71
      const expectedAvg = (1*5 + 7*10 + 14*15 + 21*20 + 30*8 + 45*6 + 60*4 + 90*2 + 120*1) / 71;
      expect(screen.getByText(`${expectedAvg.toFixed(1)} days`)).toBeInTheDocument();
    });
  });

  it('handles edge cases in data formatting', async () => {
    const edgeCaseData: LeadTimeData = {
      stats: {
        median_days: 0,
        p90_days: 365,
        distribution: [],
      },
      data: [
        { lead_time_days: 0, count: 1 },
        { lead_time_days: 365, count: 1 },
      ],
    };

    mockUseLeadTimes.mockReturnValue({
      data: edgeCaseData,
      isLoading: false,
      error: null,
      isError: false,
    } as any);

    render(
      <TestWrapper>
        <LeadTimeChart />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('0')).toBeInTheDocument(); // Median
      expect(screen.getByText('365')).toBeInTheDocument(); // P90
    });
  });

  it('uses correct color coding for lead time categories', async () => {
    mockUseLeadTimes.mockReturnValue({
      data: mockLeadTimeData,
      isLoading: false,
      error: null,
      isError: false,
    } as any);

    render(
      <TestWrapper>
        <LeadTimeChart />
      </TestWrapper>
    );

    await waitFor(() => {
      // Check that legend items are present (color coding is tested through visual elements)
      expect(screen.getByText('≤ 7 days (Last minute)')).toBeInTheDocument();
      expect(screen.getByText('8-30 days (Short term)')).toBeInTheDocument();
      expect(screen.getByText('> 30 days (Long term)')).toBeInTheDocument();
    });
  });
});