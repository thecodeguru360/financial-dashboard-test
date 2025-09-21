import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { ChartWrapper } from '../ui/ChartWrapper';
import { useRevenueTimeline } from '../../hooks/useApiQueries';
import { useFilters } from '../../providers/FilterProvider';
import { RevenueTimeline } from '../../types/api';
import { formatCurrency } from '../../lib/utils';

interface RevenueTimelineChartProps {
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

  const date = label ? format(parseISO(label), 'MMM dd, yyyy') : '';
  const revenue = payload[0]?.value || 0;

  return (
    <div className="bg-white border border-[#F1F1F1] rounded-xl p-3 shadow-lg">
      <p className="font-medium text-gray-900">{date}</p>
      <p className="text-sm text-gray-600">
        Revenue: <span className="font-medium" style={{ color: '#459B63' }}>
          ${formatCurrency(revenue)}
        </span>
      </p>
    </div>
  );
};

// Format data for the chart
const formatChartData = (data: RevenueTimeline) => {
  return data.data.map(item => ({
    date: item.date,
    revenue: item.total_revenue,
    // Format date for display
    displayDate: format(parseISO(item.date), 'MMM dd'),
  }));
};

// Custom tick formatter for X-axis
const formatXAxisTick = (tickItem: string) => {
  try {
    return format(parseISO(tickItem), 'MMM dd');
  } catch {
    return tickItem;
  }
};

// Custom tick formatter for Y-axis
const formatYAxisTick = (value: number) => {
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(1)}M`;
  } else if (value >= 1000) {
    return `$${(value / 1000).toFixed(0)}K`;
  }
  return `$${value.toFixed(0)}`;
};

export const RevenueTimelineChart: React.FC<RevenueTimelineChartProps> = ({ 
  className 
}) => {
  const { filters } = useFilters();
  const query = useRevenueTimeline(filters);

  return (
    <ChartWrapper
      query={query}
      title="Revenue Timeline"
      className={className}
      minHeight="min-h-[400px]"
      skeletonVariant="line"
      errorFallbackProps={{
        title: "Revenue Chart Error",
        description: "Unable to load revenue timeline data. This could be due to a network issue or server problem.",
        showDetails: true
      }}
    >
      {(data) => {
        const chartData = formatChartData(data);
        
        return (
          <div className="w-full h-[350px]" role="img" aria-label="Revenue timeline chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
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
                  dataKey="date"
                  tickFormatter={formatXAxisTick}
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  axisLine={{ stroke: '#F1F1F1' }}
                  tickLine={{ stroke: '#F1F1F1' }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  tickFormatter={formatYAxisTick}
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  axisLine={{ stroke: '#F1F1F1' }}
                  tickLine={{ stroke: '#F1F1F1' }}
                />
                <Tooltip 
                  content={<CustomTooltip />}
                  cursor={{ stroke: '#459B63', strokeWidth: 2 }}
                />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#459B63"
                  strokeWidth={1}
                  dot={false}
                  activeDot={{ 
                    r: 6, 
                    stroke: '#459B63',
                    strokeWidth: 2,
                    fill: '#FAFAFA'
                  }}
                  connectNulls={false}
                />
              </LineChart>
            </ResponsiveContainer>
            
            {/* Screen reader accessible data table */}
            <div className="sr-only">
              <table>
                <caption>Revenue timeline data</caption>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {chartData.map((item, index) => (
                    <tr key={index}>
                      <td>{format(parseISO(item.date), 'MMMM dd, yyyy')}</td>
                      <td>
                        ${formatCurrency(item.revenue)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      }}
    </ChartWrapper>
  );
};