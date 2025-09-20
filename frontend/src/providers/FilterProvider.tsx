import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ApiFilters } from '../types/api';

interface FilterContextType {
  filters: ApiFilters;
  updateFilters: (newFilters: Partial<ApiFilters>) => void;
  resetFilters: () => void;
}

const FilterContext = createContext<FilterContextType | undefined>(undefined);

interface FilterProviderProps {
  children: ReactNode;
}

const defaultFilters: ApiFilters = {
  start_date: undefined,
  end_date: undefined,
  property_ids: undefined,
};

export const FilterProvider: React.FC<FilterProviderProps> = ({ children }) => {
  const [filters, setFilters] = useState<ApiFilters>(defaultFilters);

  const updateFilters = (newFilters: Partial<ApiFilters>) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters,
    }));
  };

  const resetFilters = () => {
    setFilters(defaultFilters);
  };

  const value: FilterContextType = {
    filters,
    updateFilters,
    resetFilters,
  };

  return (
    <FilterContext.Provider value={value}>
      {children}
    </FilterContext.Provider>
  );
};

export const useFilters = (): FilterContextType => {
  const context = useContext(FilterContext);
  if (context === undefined) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};