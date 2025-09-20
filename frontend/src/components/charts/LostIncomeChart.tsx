import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { ChartWrapper } from '../ui/ChartWrapper';
import { useMaintenanceLostIncome } from '../../hooks/useApiQueries';
import { useFilters } from '../../providers/FilterProvider';
import { LostIncomeData } from '../../types/api';
import { formatCurrency, formatNumber } from '../../lib/utils';

interface LostIncomeChartProps {
  className?: string;
  sortBy?: 'name' | 'lost_income' | 'blocked_days';
  sortOrder?: 'asc' | 'desc';
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

  const lostIncome = payload[0]?.payload?.lost_income;
  const blockedDays = payload[0]?.payload?.blocked_days;

  return (
    <div className="bg-white border border-[#F1F1F1] rounded-xl p-3 shadow-lg">
      <p className="font-medium text-gray-900">{label}</p>
      <div className="space-y-1 text-sm">
        <p className="text-gray-600">
          Lost Income: <span className="font-medium" style={{ color: '#DC2626' }}>
            ${formatCurrency(lostIncome)}
          </span>
        </p>
        <p className="text-gray-600">
          Blocked Days: <span className="font-medium" style={{ color: '#EA580C' }}>
            {formatNumber(blockedDays)} {blockedDays === 1 ? 'day' : 'days'}
          </span>
        </p>
        <p className="text-xs text-gray-600">
          Avg Daily Loss: ${formatCurrency(blockedDays > 0 ? (lostIncome || 0) / (blockedDays || 1) : 0)}
        </p>
      </div>
    </div>
  );
};

// Format and sort data for the chart
const formatChartData = (
  data: LostIncomeData, 
  sortBy: 'name' | 'lost_income' | 'blocked_days' = 'lost_income',
  sortOrder: 'asc' | 'desc' = 'desc'
) => {
  const formatted = data.data.map(item => ({
    property_name: item.property_name,
    lost_income: item.lost_income,
    blocked_days: item.blocked_days,
    property_id: item.property_id,
    // Truncate long property names for display
    displayName: item.property_name.length > 15 
      ? `${item.property_name.substring(0, 15)}...` 
      : item.property_name,
  }));

  // Sort the data
  return formatted.sort((a, b) => {
    let comparison = 0;
    
    switch (sortBy) {
      case 'name':
        comparison = a.property_name.localeCompare(b.property_name);
        break;
      case 'blocked_days':
        comparison = a.blocked_days - b.blocked_days;
        break;
      case 'lost_income':
      default:
        comparison = a.lost_income - b.lost_income;
        break;
    }
    
    return sortOrder === 'asc' ? comparison : -comparison;
  });
};

// Custom tick formatter for Y-axis
const formatYAxisTick = (value: number) => {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  } else if (value >= 1000) {
    return `${(value / 1000).toFixed(0)}K`;
  }
  return `${value.toFixed(0)}`;
};

// Custom label formatter for bars
const CustomLabel = (props: any) => {
  const { x, y, width, value } = props;
  
  // Only show labels for larger bars to avoid clutter
  if (value < 100) return null;
  
  return (
    <text
      x={x + width / 2}
      y={y - 5}
      fill="hsl(var(--muted-foreground))"
      textAnchor="middle"
      fontSize={10}
    >
      ${value >= 1000 ? `${(value / 1000).toFixed(0)}K` : value.toFixed(0)}
    </text>
  );
};

export const LostIncomeChart: React.FC<LostIncomeChartProps> = ({ 
  className,
  sortBy = 'lost_income',
  sortOrder = 'desc'
}) => {
  const { filters } = useFilters();
  const query = useMaintenanceLostIncome(filters);

  const chartData = useMemo(() => {
    if (!query.data) return [];
    return formatChartData(query.data, sortBy, sortOrder);
  }, [query.data, sortBy, sortOrder]);

  const hasData = chartData.length > 0;
  const totalLostIncome = useMemo(() => {
    return chartData.reduce((sum, item) => sum + item.lost_income, 0);
  }, [chartData]);

  return (
    <ChartWrapper
      query={query}
      title="Maintenance Lost Income"
      className={className}
      minHeight="min-h-[400px]"
      skeletonVariant="bar"
      errorFallbackProps={{
        title: "Maintenance Impact Chart Error",
        description: "Unable to load maintenance lost income data. This may be due to a server issue or data processing problem.",
        showDetails: true
      }}
    >
      {() => (
        <div className="w-full h-[350px]" role="img" aria-label="Lost income due to maintenance by property chart">
          {hasData ? (
            <>
              <div className="mb-4 text-center">
                <p className="text-sm text-muted-foreground">
                  Total Lost Income: <span className="font-semibold text-destructive">
                    ${formatCurrency(totalLostIncome)}
                  </span>
                </p>
              </div>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartData}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 60, // Extra space for rotated labels
                  }}
                >
                  <CartesianGrid 
                    strokeDasharray="3 3" 
                    stroke="#F1F1F1"
                  />
                  <XAxis
                    dataKey="displayName"
                    tick={{ fontSize: 10, fill: '#6B7280' }}
                    axisLine={{ stroke: '#F1F1F1' }}
                    tickLine={{ stroke: '#F1F1F1' }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    interval={0}
                  />
                  <YAxis
                    tickFormatter={formatYAxisTick}
                    tick={{ fontSize: 12, fill: '#6B7280' }}
                    axisLine={{ stroke: '#F1F1F1' }}
                    tickLine={{ stroke: '#F1F1F1' }}
                  />
                  <Tooltip 
                    content={<CustomTooltip />}
                    cursor={{ fill: '#F5F5F5', opacity: 0.5 }}
                  />
                  <Legend 
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="rect"
                  />
                  <Bar
                    dataKey="lost_income"
                    name="Lost Income"
                    fill="#DC2626"
                    radius={[4, 4, 0, 0]}
                    label={<CustomLabel />}
                  />
                </BarChart>
              </ResponsiveContainer>
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <p className="text-muted-foreground">No maintenance data available</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Try adjusting your date range or property filters
                </p>
              </div>
            </div>
          )}
          
          {/* Screen reader accessible data table */}
          <div className="sr-only">
            <table>
              <caption>Lost income due to maintenance by property</caption>
              <thead>
                <tr>
                  <th>Property Name</th>
                  <th>Lost Income</th>
                  <th>Blocked Days</th>
                  <th>Average Daily Loss</th>
                </tr>
              </thead>
              <tbody>
                {chartData.map((item, index) => (
                  <tr key={index}>
                    <td>{item.property_name}</td>
                    <td>
                      ${formatCurrency(item.lost_income)}
                    </td>
                    <td>{item.blocked_days} {item.blocked_days === 1 ? 'day' : 'days'}</td>
                    <td>
                      ${formatCurrency(item.blocked_days > 0 ? (item.lost_income || 0) / (item.blocked_days || 1) : 0)}
                    </td>
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