import React from 'react';
import { cn } from '../../lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className,
  variant = 'rectangular',
  width,
  height,
  animation = 'pulse'
}) => {
  const baseClasses = 'bg-gray-200';
  
  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg'
  };
  
  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-pulse', // Could implement wave animation with CSS
    none: ''
  };

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        animationClasses[animation],
        className
      )}
      style={style}
      role="status"
      aria-label="Loading content"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};

// Chart skeleton component with different variants
export const ChartSkeleton: React.FC<{ 
  className?: string;
  variant?: 'line' | 'bar' | 'mixed';
}> = ({ className, variant = 'line' }) => {
  return (
    <div className={cn('space-y-4', className)} role="status" aria-label="Loading chart">
      {/* Chart area skeleton */}
      <div className="space-y-3">
        {/* Y-axis labels */}
        <div className="flex items-end justify-between h-64">
          <div className="flex flex-col justify-between h-full py-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} variant="text" width={30} height={12} />
            ))}
          </div>
          
          {/* Chart bars/lines area */}
          <div className="flex-1 mx-4 h-full bg-gray-100 rounded-lg relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-pulse opacity-50" />
            
            {/* Render different skeleton based on chart type */}
            {variant === 'line' && (
              <div className="h-full p-4 relative">
                {/* Simulated line chart path */}
                <svg className="w-full h-full">
                  <path
                    d="M 20 180 Q 80 120 140 160 T 260 100 T 380 140"
                    stroke="#D1D5DB"
                    strokeWidth="3"
                    fill="none"
                    className="animate-pulse"
                  />
                  {/* Data points */}
                  {[20, 80, 140, 200, 260, 320, 380].map((x, i) => (
                    <circle
                      key={i}
                      cx={x}
                      cy={120 + Math.sin(i) * 40}
                      r="4"
                      fill="#D1D5DB"
                      className="animate-pulse"
                    />
                  ))}
                </svg>
              </div>
            )}
            
            {variant === 'bar' && (
              <div className="flex items-end justify-around h-full p-4">
                {Array.from({ length: 8 }).map((_, i) => (
                  <Skeleton 
                    key={i} 
                    variant="rectangular" 
                    width={20} 
                    height={Math.random() * 150 + 50}
                    className="bg-gray-300"
                  />
                ))}
              </div>
            )}
            
            {variant === 'mixed' && (
              <div className="h-full p-4 relative">
                {/* Bars */}
                <div className="flex items-end justify-around h-full absolute inset-4">
                  {Array.from({ length: 6 }).map((_, i) => (
                    <Skeleton 
                      key={i} 
                      variant="rectangular" 
                      width={15} 
                      height={Math.random() * 100 + 30}
                      className="bg-gray-300"
                    />
                  ))}
                </div>
                {/* Line overlay */}
                <svg className="w-full h-full absolute inset-4">
                  <path
                    d="M 20 150 Q 80 100 140 130 T 260 80 T 320 110"
                    stroke="#D1D5DB"
                    strokeWidth="2"
                    fill="none"
                    className="animate-pulse"
                  />
                </svg>
              </div>
            )}
          </div>
        </div>
        
        {/* X-axis labels */}
        <div className="flex justify-around ml-12">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} variant="text" width={40} height={12} />
          ))}
        </div>
      </div>
      
      <span className="sr-only">Loading chart data...</span>
    </div>
  );
};

// Table skeleton component
export const TableSkeleton: React.FC<{ 
  rows?: number; 
  columns?: number; 
  className?: string;
}> = ({ 
  rows = 5, 
  columns = 3, 
  className 
}) => {
  return (
    <div className={cn('space-y-3', className)} role="status" aria-label="Loading table">
      {/* Header row */}
      <div className="flex gap-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} variant="text" height={16} width="100%" className="flex-1" />
        ))}
      </div>
      
      {/* Data rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton 
              key={colIndex} 
              variant="text" 
              height={14} 
              width="100%" 
              className="flex-1" 
            />
          ))}
        </div>
      ))}
      
      <span className="sr-only">Loading table data...</span>
    </div>
  );
};

// Card skeleton component
export const CardSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div 
      className={cn(
        'rounded-xl border border-[#F1F1F1] bg-white p-6 space-y-4',
        className
      )}
      role="status" 
      aria-label="Loading card content"
    >
      {/* Title */}
      <Skeleton variant="text" height={20} width="60%" />
      
      {/* Content area */}
      <div className="space-y-3">
        <Skeleton variant="rectangular" height={200} width="100%" />
        <div className="flex justify-between">
          <Skeleton variant="text" height={14} width="30%" />
          <Skeleton variant="text" height={14} width="20%" />
        </div>
      </div>
      
      <span className="sr-only">Loading card content...</span>
    </div>
  );
};

// Dashboard skeleton for full page loading
export const DashboardSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('min-h-screen bg-[#FAFAFA]', className)} role="status" aria-label="Loading dashboard">
      {/* Header skeleton */}
      <div className="bg-white border-b border-[#F1F1F1] p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <Skeleton variant="text" height={32} width={300} />
              <Skeleton variant="text" height={16} width={200} />
            </div>
            <div className="flex gap-4">
              <Skeleton variant="rectangular" height={40} width={200} />
              <Skeleton variant="rectangular" height={40} width={150} />
            </div>
          </div>
        </div>
      </div>
      
      {/* Main content skeleton */}
      <div className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Revenue section */}
        <div className="space-y-4">
          <Skeleton variant="text" height={24} width={200} />
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <CardSkeleton />
            <CardSkeleton />
          </div>
        </div>
        
        {/* Other sections */}
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="space-y-4">
            <Skeleton variant="text" height={24} width={250} />
            <CardSkeleton />
          </div>
        ))}
      </div>
      
      <span className="sr-only">Loading dashboard...</span>
    </div>
  );
};

// Statistics skeleton for lead time stats
export const StatsSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('space-y-4', className)} role="status" aria-label="Loading statistics">
      <div className="grid grid-cols-2 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="text-center space-y-2">
            <Skeleton variant="text" height={12} width="60%" className="mx-auto" />
            <Skeleton variant="text" height={24} width="80%" className="mx-auto" />
          </div>
        ))}
      </div>
      <span className="sr-only">Loading statistics...</span>
    </div>
  );
};