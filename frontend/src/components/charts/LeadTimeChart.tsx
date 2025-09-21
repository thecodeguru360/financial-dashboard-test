import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { ChartWrapper } from '../ui/ChartWrapper';
import { useLeadTimes } from '../../hooks/useApiQueries';
import { useFilters } from '../../providers/FilterProvider';
import { LeadTimeData } from '../../types/api';
import { formatNumber } from '../../lib/utils';

interface LeadTimeChartProps {
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

  const leadTimeDays = label;
  const count = payload[0]?.value || 0;

  return (
    <div className="bg-white border border-[#F1F1F1] rounded-xl p-3 shadow-lg ">
      <p className="font-medium text-gray-900">
        {leadTimeDays} {leadTimeDays === 1 ? 'day' : 'days'} lead time
      </p>
      <p className="text-sm text-gray-600">
        Bookings: <span className="font-medium" style={{ color: '#459B63' }}>
          {count} {count === 1 ? 'booking' : 'bookings'}
        </span>
      </p>
    </div>
  );
};

// Format data for the histogram chart
const formatChartData = (data: LeadTimeData | undefined) => {
  if (!data || !Array.isArray(data.data)) return [];
  return data.data.map(item => ({
    lead_time_days: item.lead_time_days,
    count: item.count,
    // Add color coding based on lead time ranges
    color: item.lead_time_days <= 7 ? 'hsl(var(--destructive))' : 
           item.lead_time_days <= 30 ? 'hsl(var(--warning))' : 
           'hsl(var(--primary))',
  })).sort((a, b) => a.lead_time_days - b.lead_time_days);
};

// Custom tick formatter for X-axis
const formatDaysTick = (value: number) => {
  if (value === 0) return '0';
  if (value <= 7) return `${value}d`;
  if (value <= 30) return `${value}d`;
  if (value >= 365) return `${Math.round(value / 365)}y`;
  if (value >= 30) return `${Math.round(value / 30)}m`;
  return `${value}d`;
};

// Custom tick formatter for Y-axis
const formatCountTick = (value: number) => {
  if (value >= 1000) {
    return `${(value / 1000).toFixed(0)}K`;
  }
  return value.toString();
};

// Statistics table component
const LeadTimeStatsTable: React.FC<{ stats: LeadTimeData['stats'] | undefined }> = ({ stats }) => {
  if (!stats) return null;
  
  return (
    <div className="bg-muted/30 rounded-lg p-4">
      <h4 className="text-sm font-medium text-foreground mb-3">Key Metrics</h4>
      <div className="space-y-3">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-700">
            {formatNumber(stats.median_days)}
          </div>
          <div className="text-xs text-muted-foreground">
            Median Days
          </div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-700">
            {formatNumber(stats.p90_days)}
          </div>
          <div className="text-xs text-muted-foreground">
            90th Percentile
          </div>
        </div>
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-700">
            {formatNumber(stats.total_bookings)}
          </div>
          <div className="text-xs text-muted-foreground">
            Total Bookings
          </div>
        </div>
      </div>
    </div>
  );
};

export const LeadTimeChart: React.FC<LeadTimeChartProps> = ({ 
  className 
}) => {
  const { filters } = useFilters();
  const query = useLeadTimes(filters);

  const chartData = useMemo(() => {
    return formatChartData(query.data);
  }, [query.data]);

  const hasData = chartData.length > 0;
  
  // Calculate summary statistics
  const summaryStats = useMemo(() => {
    if (!hasData || !query.data) return null;
    
    const totalBookings = chartData.reduce((sum, item) => sum + item.count, 0);
    const avgLeadTime = chartData.reduce((sum, item) => {
      return sum + (item.lead_time_days * item.count);
    }, 0) / totalBookings;
    
    return {
      totalBookings,
      avgLeadTime: totalBookings > 0 ? avgLeadTime : 0,
    };
  }, [chartData, hasData, query.data]);

  return (
    <ChartWrapper
      query={query}
      title="Booking Lead Time Analysis"
      className={className}
      minHeight="min-h-[500px]"
      skeletonVariant="bar"
      errorFallbackProps={{
        title: "Lead Time Analysis Error",
        description: "Unable to load booking lead time data. This may be due to a calculation error or data availability issue.",
        showDetails: true
      }}
    >
      {() => (
        <div className="w-full min-h-[500px]" role="img" aria-label="Lead time distribution histogram showing booking patterns">
          {hasData && query.data ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[450px]">
              {/* Left Column - Booking Lead Stats */}
              <div className="lg:col-span-1 space-y-4">
                {/* Statistics Table */}
                <LeadTimeStatsTable stats={query.data?.stats} />
                
                {/* Summary Stats */}
                {summaryStats && (
                  <div className="bg-muted/30 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-foreground mb-3">Summary</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Total Bookings:</span>
                        <span className="font-semibold text-primary">
                          {formatNumber(summaryStats.totalBookings)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Average Lead Time:</span>
                        <span className="font-semibold text-gray-700">
                          {summaryStats.avgLeadTime.toFixed(1)} days
                        </span>
                      </div>
                    </div>
                  </div>
                )}


              </div>

              {/* Right Column - Histogram Chart (Wider) */}
              <div className="lg:col-span-2 h-full">

                                {/* Legend */}
                <div className="bg-muted/30 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-foreground mb-3">Categories</h4>
                 
                  <div className="flex gap-4 text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded" style={{ backgroundColor: 'hsl(var(--destructive))' }}></div>
                      <span className="text-muted-foreground">≤ 7 days (Last minute)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded" style={{ backgroundColor: 'hsl(var(--warning))' }}></div>
                      <span className="text-muted-foreground">8-30 days (Short term)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded" style={{ backgroundColor: 'hsl(var(--primary))' }}></div>
                      <span className="text-muted-foreground">&gt; 30 days (Long term)</span>
                    </div>
                  
                  </div>
                </div>

                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={chartData}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 60,
                    }}
                  >
                    <CartesianGrid 
                      strokeDasharray="3 3" 
                      stroke="#F1F1F1"
                    />
                    <XAxis
                      dataKey="lead_time_days"
                      tick={{ fontSize: 11, fill: '#6B7280' }}
                      axisLine={{ stroke: '#F1F1F1' }}
                      tickLine={{ stroke: '#F1F1F1' }}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                      tickFormatter={formatDaysTick}
                      label={{ 
                        value: 'Lead Time (Days)', 
                        position: 'insideBottom', 
                        offset: -10,
                        style: { textAnchor: 'middle', fill: '#6B7280' }
                      }}
                    />
                    <YAxis
                      tickFormatter={formatCountTick}
                      tick={{ fontSize: 12, fill: '#6B7280' }}
                      axisLine={{ stroke: '#F1F1F1' }}
                      tickLine={{ stroke: '#F1F1F1' }}
                      label={{ 
                        value: 'Number of Bookings', 
                        angle: -90, 
                        position: 'insideLeft',
                        style: { textAnchor: 'middle', fill: '#6B7280' }
                      }}
                    />
                    <Tooltip 
                      content={<CustomTooltip />}
                      cursor={{ fill: '#F5F5F5', opacity: 0.5 }}
                    />
                    <Bar
                      dataKey="count"
                      radius={[2, 2, 0, 0]}
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-[450px]">
              <div className="text-center">
                <p className="text-muted-foreground">No lead time data available</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Try adjusting your date range or property filters
                </p>
              </div>
            </div>
          )}
          
          {/* Screen reader accessible data table */}
          <div className="sr-only">
            <table>
              <caption>Lead time distribution data showing booking patterns by advance booking days</caption>
              <thead>
                <tr>
                  <th>Lead Time (Days)</th>
                  <th>Number of Bookings</th>
                  <th>Category</th>
                </tr>
              </thead>
              <tbody>
                {chartData.map((item, index) => (
                  <tr key={index}>
                    <td>{item.lead_time_days} {item.lead_time_days === 1 ? 'day' : 'days'}</td>
                    <td>{item.count} {item.count === 1 ? 'booking' : 'bookings'}</td>
                    <td>
                      {item.lead_time_days <= 7 ? 'Last minute' : 
                       item.lead_time_days <= 30 ? 'Short term' : 
                       'Long term'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {query.data && (
              <div>
                <h4>Summary Statistics</h4>
                <p>Median lead time: {query.data.stats.median_days.toFixed(0)} days</p>
                <p>90th percentile lead time: {query.data.stats.p90_days.toFixed(0)} days</p>
              </div>
            )}
          </div>
        </div>
      )}
    </ChartWrapper>
  );
};