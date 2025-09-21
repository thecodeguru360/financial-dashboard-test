import React from 'react';
import { useKPIs } from '../../hooks/useApiQueries';
import { useFilters } from '../../providers/FilterProvider';
import { KPICard } from './KPICard';
import { ErrorMessage } from '../ui/ErrorMessage';

export function KPIDashboard() {
  const { filters } = useFilters();
  const { data: kpiData, isLoading, error } = useKPIs(filters);

  if (error) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <ErrorMessage 
          error={error}
          title="Failed to load KPI data"
          variant="detailed"
        />
      </div>
    );
  }

  // Show loading state for all KPI cards
  if (isLoading || !kpiData) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, index) => (
          <KPICard 
            key={index}
            kpi={{
              name: '',
              value: 0,
              unit: '',
              description: ''
            }}
            isLoading={true}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {kpiData.data.map((kpi) => (
        <KPICard 
          key={kpi.name}
          kpi={kpi}
        />
      ))}
    </div>
  );
}