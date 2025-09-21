import React, { useEffect } from 'react';
import { QueryProvider } from './providers/QueryProvider';
import { FilterProvider } from './providers/FilterProvider';
import { GlobalErrorBoundary } from './components/ui/GlobalErrorBoundary';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import { NetworkStatus } from './components/ui/NetworkStatus';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { DashboardSection } from './components/layout/DashboardSection';
import { RevenueTimelineChart, RevenueByPropertyChart, LostIncomeChart, ReviewTrendsChart, LeadTimeChart } from './components/charts';
import { KPIDashboard } from './components/kpis';
import { setupGlobalErrorHandling } from './lib/errorReporting';

function App() {
  // Set up global error handling
  useEffect(() => {
    setupGlobalErrorHandling();
  }, []);

  return (
    <GlobalErrorBoundary>
      <QueryProvider>
        <FilterProvider>
          <ErrorBoundary>
            <NetworkStatus />
            <DashboardLayout>
              {/* Key Performance Indicators Section */}
              <DashboardSection
                id="kpis"
                title="Key Performance Indicators"
                description="Overview of your portfolio's key metrics and financial performance"
              >
                <KPIDashboard />
              </DashboardSection>

              {/* Revenue Analytics Section */}
              <DashboardSection
                id="revenue"
                title="Revenue Analytics"
                description="Track financial performance and identify revenue trends across your portfolio"
              >
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                  <RevenueTimelineChart />
                  <RevenueByPropertyChart />
                </div>
              </DashboardSection>

              {/* Maintenance Impact Section */}
              <DashboardSection
                id="maintenance"
                title="Maintenance Impact"
                description="Analyze the financial impact of maintenance blocks on your revenue"
              >
                <div className="grid grid-cols-1 gap-6">
                  <LostIncomeChart />
                </div>
              </DashboardSection>

              {/* Review Trends Section */}
              <DashboardSection
                id="reviews"
                title="Review Trends"
                description="Monitor guest satisfaction and service quality over time"
              >
                <div className="grid grid-cols-1 gap-6">
                  <ReviewTrendsChart />
                </div>
              </DashboardSection>

              {/* Lead Time Analysis Section */}
              <DashboardSection
                id="leadtime"
                title="Lead Time Analysis"
                description="Understand guest booking patterns and optimize pricing strategies"
              >
                <div className="grid grid-cols-1 gap-6">
                  <LeadTimeChart />
                </div>
              </DashboardSection>
            </DashboardLayout>
          </ErrorBoundary>
        </FilterProvider>
      </QueryProvider>
    </GlobalErrorBoundary>
  );
}

export default App;
