import React from 'react';
import { DateRange } from 'react-day-picker';
import { RotateCcw } from 'lucide-react';

import { Button } from '../ui/button';
import { DateRangePicker } from './DateRangePicker';
import { PropertyMultiSelect } from './PropertyMultiSelect';
import { useFilters } from '../../providers/FilterProvider';
import { useProperties } from '../../hooks/useApiQueries';

interface HeaderFilterControlsProps {
  className?: string;
}

export const HeaderFilterControls: React.FC<HeaderFilterControlsProps> = ({ className }) => {
  const { filters, updateFilters, resetFilters } = useFilters();
  const { data: properties = [], isLoading: isLoadingProperties } = useProperties();

  // Convert API filters to DateRange format
  const dateRange: DateRange | undefined = filters.start_date || filters.end_date
    ? {
        from: filters.start_date ? new Date(filters.start_date) : undefined,
        to: filters.end_date ? new Date(filters.end_date) : undefined,
      }
    : undefined;

  // Handle date range changes
  const handleDateRangeChange = (range: DateRange | undefined) => {
    updateFilters({
      start_date: range?.from ? range.from.toISOString().split('T')[0] : undefined,
      end_date: range?.to ? range.to.toISOString().split('T')[0] : undefined,
    });
  };

  // Handle property selection changes
  const handlePropertyChange = (selectedIds: number[]) => {
    updateFilters({
      property_ids: selectedIds.length > 0 ? selectedIds : undefined,
    });
  };

  // Check if any filters are active
  const hasActiveFilters = Boolean(
    filters.start_date || 
    filters.end_date || 
    (filters.property_ids && filters.property_ids.length > 0)
  );

  return (
    <div className={`flex items-center space-x-3 ${className || ''}`}>
      {/* Date Range Filter */}
      <DateRangePicker
        value={dateRange}
        onChange={handleDateRangeChange}
        placeholder="Select date range"
        className="w-48"
      />

      {/* Property Filter */}
      <PropertyMultiSelect
        properties={properties}
        selectedIds={filters.property_ids || []}
        onChange={handlePropertyChange}
        placeholder="All properties"
        className="w-48"
        isLoading={isLoadingProperties}
      />

      {/* Reset Button */}
      {hasActiveFilters && (
        <Button
          variant="outline"
          size="sm"
          onClick={resetFilters}
          className="h-9 px-3"
          title="Reset all filters"
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
};