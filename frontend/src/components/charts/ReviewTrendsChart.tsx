import React, { useMemo } from 'react';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { ChartWrapper } from '../ui/ChartWrapper';
import { useReviewTrends } from '../../hooks/useApiQueries';
import { useFilters } from '../../providers/FilterProvider';
import { ReviewTrendsData } from '../../types/api';

interface ReviewTrendsChartProps {
  className?: string;
}

// Custom tooltip component for better accessibility and formatting
const CustomTooltip = ({ 
  active, 
  payload, 
  label 
}: any) => {
  if (!active || !payload || !payload.length) {
    return null;
  }

  const month = label;
  const avgRating = payload.find((p: any) => p.dataKey === 'avg_rating')?.value || 0;
  const reviewCount = payload.find((p: any) => p.dataKey === 'review_count')?.value || 0;

  return (
    <div className="bg-white border border-[#F1F1F1] rounded-xl p-3 shadow-lg">
      <p className="font-medium text-gray-900">{month}</p>
      <div className="space-y-1 text-sm">
        <p className="text-gray-600">
          Average Rating: <span className="font-medium" style={{ color: '#459B63' }}>
            {avgRating.toFixed(2)} ⭐
          </span>
        </p>
        <p className="text-gray-600">
          Review Count: <span className="font-medium text-gray-700">
            {reviewCount} {reviewCount === 1 ? 'review' : 'reviews'}
          </span>
        </p>
      </div>
    </div>
  );
};

// Format data for the chart
const formatChartData = (data: ReviewTrendsData) => {
  return data.data.map(item => {
    // Parse the month string (assuming format like "2023-01" or "January 2023")
    let displayMonth: string;
    try {
      // Try parsing as YYYY-MM format first
      if (item.month.match(/^\d{4}-\d{2}$/)) {
        displayMonth = format(parseISO(`${item.month}-01`), 'MMM yyyy');
      } else {
        // Fallback to using the month as-is
        displayMonth = item.month;
      }
    } catch {
      displayMonth = item.month;
    }

    return {
      month: displayMonth,
      avg_rating: item.avg_rating,
      review_count: item.review_count,
      // Store original month for sorting
      originalMonth: item.month,
    };
  }).sort((a, b) => {
    // Sort by original month string
    return a.originalMonth.localeCompare(b.originalMonth);
  });
};

// Custom tick formatter for rating Y-axis (left)
const formatRatingTick = (value: number) => {
  return value.toFixed(1);
};

// Custom tick formatter for count Y-axis (right)
const formatCountTick = (value: number) => {
  if (value >= 1000) {
    return `${(value / 1000).toFixed(0)}K`;
  }
  return value.toString();
};

export const ReviewTrendsChart: React.FC<ReviewTrendsChartProps> = ({ 
  className 
}) => {
  const { filters } = useFilters();
  const query = useReviewTrends(filters);

  const chartData = useMemo(() => {
    if (!query.data) return [];
    return formatChartData(query.data);
  }, [query.data]);

  const hasData = chartData.length > 0;
  
  // Calculate summary statistics
  const summaryStats = useMemo(() => {
    if (!hasData) return null;
    
    const totalReviews = chartData.reduce((sum, item) => sum + item.review_count, 0);
    const avgRating = chartData.reduce((sum, item, _, arr) => {
      return sum + (item.avg_rating * item.review_count) / totalReviews;
    }, 0);
    
    return {
      totalReviews,
      avgRating: totalReviews > 0 ? avgRating : 0,
    };
  }, [chartData, hasData]);

  return (
    <ChartWrapper
      query={query}
      title="Review Trends"
      className={className}
      minHeight="min-h-[400px]"
      skeletonVariant="mixed"
      errorFallbackProps={{
        title: "Review Trends Chart Error",
        description: "Unable to load review trends data. This could be due to a data processing issue or server problem.",
        showDetails: true
      }}
    >
      {() => (
        <div className="w-full h-[350px]" role="img" aria-label="Review trends chart showing ratings and review counts over time">
          {hasData ? (
            <>
              {summaryStats && (
                <div className="mb-4 text-center">
                  <div className="flex justify-center gap-6 text-sm text-muted-foreground">
                    <span>
                      Total Reviews: <span className="font-semibold text-secondary">
                        {summaryStats.totalReviews.toLocaleString()}
                      </span>
                    </span>
                    <span>
                      Overall Average: <span className="font-semibold text-primary">
                        {summaryStats.avgRating.toFixed(2)} ⭐
                      </span>
                    </span>
                  </div>
                </div>
              )}
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart
                  data={chartData}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 20,
                  }}
                >
                  <CartesianGrid 
                    strokeDasharray="3 3" 
                    stroke="#F1F1F1"
                  />
                  <XAxis
                    dataKey="month"
                    tick={{ fontSize: 11, fill: '#6B7280' }}
                    axisLine={{ stroke: '#F1F1F1' }}
                    tickLine={{ stroke: '#F1F1F1' }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                    interval={0}
                  />
                  {/* Left Y-axis for ratings */}
                  <YAxis
                    yAxisId="rating"
                    orientation="left"
                    domain={[0, 5]}
                    tickFormatter={formatRatingTick}
                    tick={{ fontSize: 12, fill: '#6B7280' }}
                    axisLine={{ stroke: '#F1F1F1' }}
                    tickLine={{ stroke: '#F1F1F1' }}
                    label={{ 
                      value: 'Average Rating', 
                      angle: -90, 
                      position: 'insideLeft',
                      style: { textAnchor: 'middle', fill: '#6B7280' }
                    }}
                  />
                  {/* Right Y-axis for counts */}
                  <YAxis
                    yAxisId="count"
                    orientation="right"
                    tickFormatter={formatCountTick}
                    tick={{ fontSize: 12, fill: '#6B7280' }}
                    axisLine={{ stroke: '#F1F1F1' }}
                    tickLine={{ stroke: '#F1F1F1' }}
                    label={{ 
                      value: 'Review Count', 
                      angle: 90, 
                      position: 'insideRight',
                      style: { textAnchor: 'middle', fill: '#6B7280' }
                    }}
                  />
                  <Tooltip 
                    content={<CustomTooltip />}
                    cursor={{ fill: '#F5F5F5', opacity: 0.5 }}
                  />
                  <Legend 
                    wrapperStyle={{ paddingTop: '20px', color: '#6B7280' }}
                    iconType="rect"
                  />
                  {/* Bar chart for review counts */}
                  <Bar
                    yAxisId="count"
                    dataKey="review_count"
                    name="Review Count"
                    fill="#F5F5F5"
                    fillOpacity={0.8}
                    radius={[2, 2, 0, 0]}
                  />
                  {/* Line chart for average ratings */}
                  <Line
                    yAxisId="rating"
                    type="monotone"
                    dataKey="avg_rating"
                    name="Average Rating"
                    stroke="#459B63"
                    strokeWidth={3}
                    dot={{ 
                      fill: '#459B63', 
                      strokeWidth: 2, 
                      r: 5 
                    }}
                    activeDot={{ 
                      r: 7, 
                      stroke: '#459B63',
                      strokeWidth: 2,
                      fill: '#FAFAFA'
                    }}
                    connectNulls={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <p className="text-muted-foreground">No review data available</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Try adjusting your date range or property filters
                </p>
              </div>
            </div>
          )}
          
          {/* Screen reader accessible data table */}
          <div className="sr-only">
            <table>
              <caption>Review trends data showing monthly ratings and counts</caption>
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Average Rating</th>
                  <th>Review Count</th>
                </tr>
              </thead>
              <tbody>
                {chartData.map((item, index) => (
                  <tr key={index}>
                    <td>{item.month}</td>
                    <td>{item.avg_rating.toFixed(2)} out of 5 stars</td>
                    <td>{item.review_count} {item.review_count === 1 ? 'review' : 'reviews'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </ChartWrapper>
  );
};