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
import { useRevenueByProperty } from '../../hooks/useApiQueries';
import { useFilters } from '../../providers/FilterProvider';
import { PropertyRevenue } from '../../types/api';

interface RevenueByPropertyChartProps {
  className?: string;
  sortBy?: 'name' | 'revenue';
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

  const revenue = payload[0]?.value || 0;

  return (
    <div className="bg-white border border-[#F1F1F1] rounded-xl p-3 shadow-lg">
      <p className="font-medium text-gray-900">{label}</p>
      <p className="text-sm text-gray-600">
        Total Revenue: <span className="font-medium" style={{ color: '#459B63' }}>
          ${revenue.toLocaleString('en-US', { 
            minimumFractionDigits: 2, 
            maximumFractionDigits: 2 
          })}
        </span>
      </p>
    </div>
  );
};

// Format and sort data for the chart
const formatChartData = (
  data: PropertyRevenue, 
  sortBy: 'name' | 'revenue' = 'revenue',
  sortOrder: 'asc' | 'desc' = 'desc'
) => {
  const formatted = data.data.map(item => ({
    property_name: item.property_name,
    revenue: item.total_revenue,
    property_id: item.property_id,
    // Truncate long property names for display
    displayName: item.property_name.length > 15 
      ? `${item.property_name.substring(0, 15)}...` 
      : item.property_name,
  }));

  // Sort the data
  return formatted.sort((a, b) => {
    let comparison = 0;
    
    if (sortBy === 'name') {
      comparison = a.property_name.localeCompare(b.property_name);
    } else {
      comparison = a.revenue - b.revenue;
    }
    
    return sortOrder === 'asc' ? comparison : -comparison;
  });
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

// Custom label formatter for bars
const CustomLabel = (props: any) => {
  const { x, y, width, value } = props;
  
  // Only show labels for larger bars to avoid clutter
  if (value < 1000) return null;
  
  return (
    <text
      x={x + width / 2}
      y={y - 5}
      fill="#6B7280"
      textAnchor="middle"
      fontSize={10}
    >
      ${value >= 1000 ? `${(value / 1000).toFixed(0)}K` : value.toFixed(0)}
    </text>
  );
};

export const RevenueByPropertyChart: React.FC<RevenueByPropertyChartProps> = ({ 
  className,
  sortBy = 'revenue',
  sortOrder = 'desc'
}) => {
  const { filters } = useFilters();
  const query = useRevenueByProperty(filters);

  const chartData = useMemo(() => {
    if (!query.data) return [];
    return formatChartData(query.data, sortBy, sortOrder);
  }, [query.data, sortBy, sortOrder]);

  return (
    <ChartWrapper
      query={query}
      title="Revenue by Property"
      className={className}
      minHeight="min-h-[400px]"
      skeletonVariant="bar"
      errorFallbackProps={{
        title: "Property Revenue Chart Error",
        description: "Unable to load revenue by property data. Please check your connection and try again.",
        showDetails: true
      }}
    >
      {(data) => (
        <div className="w-full h-[350px]" role="img" aria-label="Revenue by property chart">
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
                wrapperStyle={{ paddingTop: '20px', color: '#6B7280' }}
                iconType="rect"
              />
              <Bar
                dataKey="revenue"
                name="Total Revenue"
                fill="#459B63"
                radius={[4, 4, 0, 0]}
                label={<CustomLabel />}
              />
            </BarChart>
          </ResponsiveContainer>
          
          {/* Screen reader accessible data table */}
          <div className="sr-only">
            <table>
              <caption>Revenue by property data</caption>
              <thead>
                <tr>
                  <th>Property Name</th>
                  <th>Total Revenue</th>
                </tr>
              </thead>
              <tbody>
                {chartData.map((item, index) => (
                  <tr key={index}>
                    <td>{item.property_name}</td>
                    <td>
                      ${item.revenue.toLocaleString('en-US', { 
                        minimumFractionDigits: 2, 
                        maximumFractionDigits: 2 
                      })}
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