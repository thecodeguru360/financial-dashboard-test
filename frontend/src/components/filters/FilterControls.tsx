import React from 'react';
import { DateRange } from 'react-day-picker';
import { RotateCcw } from 'lucide-react';

import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { DateRangePicker } from './DateRangePicker';
import { PropertyMultiSelect } from './PropertyMultiSelect';
import { useFilters } from '../../providers/FilterProvider';
import { useProperties } from '../../hooks/useApiQueries';

interface FilterControlsProps {
  className?: string;
}

export const FilterControls: React.FC<FilterControlsProps> = ({ className }) => {
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
    <div className={`space-y-4 ${className || ''}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Filters</h3>
        {hasActiveFilters && (
          <Button
            variant="outline"
            size="sm"
            onClick={resetFilters}
            className="h-8 px-2 lg:px-3"
          >
            <RotateCcw className="mr-2 h-4 w-4" />
            Reset
          </Button>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Date Range Filter */}
        <div className="space-y-2">
          <Label htmlFor="date-range">Date Range</Label>
          <DateRangePicker
            value={dateRange}
            onChange={handleDateRangeChange}
            placeholder="Select date range"
            className="w-full"
          />
        </div>

        {/* Property Filter */}
        <div className="space-y-2">
          <Label htmlFor="properties">Properties</Label>
          <PropertyMultiSelect
            properties={properties}
            selectedIds={filters.property_ids || []}
            onChange={handlePropertyChange}
            placeholder="All properties"
            className="w-full"
            isLoading={isLoadingProperties}
          />
        </div>
      </div>

      {/* Active filters summary */}
      {hasActiveFilters && (
        <div className="text-sm text-muted-foreground">
          <span>Active filters: </span>
          {filters.start_date && filters.end_date && (
            <span className="inline-block bg-secondary px-2 py-1 rounded mr-2">
              {filters.start_date} to {filters.end_date}
            </span>
          )}
          {filters.property_ids && filters.property_ids.length > 0 && (
            <span className="inline-block bg-secondary px-2 py-1 rounded mr-2">
              {filters.property_ids.length} {filters.property_ids.length === 1 ? 'property' : 'properties'}
            </span>
          )}
        </div>
      )}
    </div>
  );
};