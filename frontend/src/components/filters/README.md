# Filter Components

This directory contains the filtering system components for the Financial Dashboard.

## Components

### FilterProvider
Context provider that manages filter state across the application.

**Usage:**
```tsx
import { FilterProvider } from './providers/FilterProvider';

<FilterProvider>
  <App />
</FilterProvider>
```

### useFilters Hook
Hook to access and modify filter state.

**Usage:**
```tsx
import { useFilters } from './providers/FilterProvider';

const { filters, updateFilters, resetFilters } = useFilters();
```

### DateRangePicker
Component for selecting date ranges with validation.

**Props:**
- `value?: DateRange` - Current selected date range
- `onChange: (range: DateRange | undefined) => void` - Callback when range changes
- `placeholder?: string` - Placeholder text
- `className?: string` - Additional CSS classes

**Usage:**
```tsx
import { DateRangePicker } from './components/filters/DateRangePicker';

<DateRangePicker
  value={dateRange}
  onChange={handleDateRangeChange}
  placeholder="Select date range"
/>
```

### PropertyMultiSelect
Multi-select component for choosing properties with search functionality.

**Props:**
- `properties: Property[]` - Array of available properties
- `selectedIds: number[]` - Array of selected property IDs
- `onChange: (selectedIds: number[]) => void` - Callback when selection changes
- `placeholder?: string` - Placeholder text
- `className?: string` - Additional CSS classes
- `isLoading?: boolean` - Loading state

**Features:**
- Search functionality
- Select all/deselect all
- Individual property selection
- Loading state support

**Usage:**
```tsx
import { PropertyMultiSelect } from './components/filters/PropertyMultiSelect';

<PropertyMultiSelect
  properties={properties}
  selectedIds={selectedPropertyIds}
  onChange={handlePropertyChange}
  placeholder="All properties"
  isLoading={isLoadingProperties}
/>
```

### FilterControls
Complete filter interface combining date range and property selection.

**Props:**
- `className?: string` - Additional CSS classes

**Features:**
- Date range selection
- Property multi-select
- Reset functionality
- Active filter summary
- Responsive design

**Usage:**
```tsx
import { FilterControls } from './components/filters/FilterControls';

<FilterControls />
```

## Integration with API Hooks

The filter system integrates seamlessly with the API hooks:

```tsx
import { useFilters } from './providers/FilterProvider';
import { useRevenueTimeline } from './hooks/useApiQueries';

const MyComponent = () => {
  const { filters } = useFilters();
  const { data, isLoading } = useRevenueTimeline(filters);
  
  // Component renders with filtered data
};
```

## Filter State Structure

```typescript
interface ApiFilters {
  start_date?: string;     // YYYY-MM-DD format
  end_date?: string;       // YYYY-MM-DD format
  property_ids?: number[]; // Array of property IDs
}
```

## Requirements Satisfied

This implementation satisfies the following requirements:

- **5.1**: Date range picker for filtering all analytics
- **5.2**: Multi-select property filter
- **5.3**: Filter changes update all charts within 2 seconds (via React Query)
- **5.4**: Clear axis titles, legends, and tooltips (in individual chart components)
- **5.5**: Detailed tooltips on hover (in individual chart components)
- **5.6**: Accessibility standards for color contrast and screen readers

## Testing

The filter components include comprehensive tests:

- Unit tests for FilterProvider context
- Integration tests for filter state management
- Component tests for UI interactions
- Mock tests for API integration

Run tests with:
```bash
npm test -- --testPathPattern=filters
```