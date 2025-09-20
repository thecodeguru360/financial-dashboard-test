import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { FilterProvider, useFilters } from '../../../providers/FilterProvider';

// Test component that uses the filter context
const TestComponent: React.FC = () => {
  const { filters, updateFilters, resetFilters } = useFilters();
  
  return (
    <div>
      <div data-testid="start-date">{filters.start_date || 'No start date'}</div>
      <div data-testid="end-date">{filters.end_date || 'No end date'}</div>
      <div data-testid="property-ids">
        {filters.property_ids ? filters.property_ids.join(',') : 'No properties'}
      </div>
      <button
        onClick={() => updateFilters({ start_date: '2024-01-01' })}
        data-testid="set-start-date"
      >
        Set Start Date
      </button>
      <button
        onClick={() => updateFilters({ property_ids: [1, 2, 3] })}
        data-testid="set-properties"
      >
        Set Properties
      </button>
      <button onClick={resetFilters} data-testid="reset">
        Reset
      </button>
    </div>
  );
};

describe('FilterProvider', () => {
  const renderWithProvider = () => {
    return render(
      <FilterProvider>
        <TestComponent />
      </FilterProvider>
    );
  };

  it('should provide default filter values', () => {
    renderWithProvider();
    
    expect(screen.getByTestId('start-date')).toHaveTextContent('No start date');
    expect(screen.getByTestId('end-date')).toHaveTextContent('No end date');
    expect(screen.getByTestId('property-ids')).toHaveTextContent('No properties');
  });

  it('should update filters correctly', () => {
    renderWithProvider();
    
    fireEvent.click(screen.getByTestId('set-start-date'));
    expect(screen.getByTestId('start-date')).toHaveTextContent('2024-01-01');
    
    fireEvent.click(screen.getByTestId('set-properties'));
    expect(screen.getByTestId('property-ids')).toHaveTextContent('1,2,3');
  });

  it('should reset filters correctly', () => {
    renderWithProvider();
    
    // Set some filters
    fireEvent.click(screen.getByTestId('set-start-date'));
    fireEvent.click(screen.getByTestId('set-properties'));
    
    // Verify they are set
    expect(screen.getByTestId('start-date')).toHaveTextContent('2024-01-01');
    expect(screen.getByTestId('property-ids')).toHaveTextContent('1,2,3');
    
    // Reset and verify
    fireEvent.click(screen.getByTestId('reset'));
    expect(screen.getByTestId('start-date')).toHaveTextContent('No start date');
    expect(screen.getByTestId('property-ids')).toHaveTextContent('No properties');
  });

  it('should throw error when used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => {
      render(<TestComponent />);
    }).toThrow('useFilters must be used within a FilterProvider');
    
    consoleSpy.mockRestore();
  });
});